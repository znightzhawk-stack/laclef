#!/usr/bin/env python3
import datetime as dt, json, os, pathlib, sys, urllib.request, urllib.error
ROOT=pathlib.Path(__file__).resolve().parents[1]
NOW=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))); DAY=NOW.strftime("%Y-%m-%d")
KEY=os.environ.get("GEMINI_API_KEY","").strip()
MODEL=os.environ.get("GEMINI_MODEL","").strip() or "gemini-2.5-flash"
def read(p, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default
def write(p, obj):
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def call(prompt):
    if not KEY: raise RuntimeError("GEMINI_API_KEY secret is missing")
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"
    body={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.25,"responseMimeType":"application/json"}}
    req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=90) as r: data=json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Gemini API HTTP {e.code}: {e.read().decode(errors='replace')[:1000]}")
    try: return json.loads(data["candidates"][0]["content"]["parts"][0]["text"])
    except Exception as e: raise RuntimeError("Gemini 응답이 JSON 형식이 아닙니다. 모델 ID/응답을 확인하세요.") from e
def main():
    plan=read(ROOT/"config/company-plan.json",{})
    board=read(ROOT/"tasks/task-board.json",{"tasks":[]})
    tasks=board.get("tasks",[])
    if not tasks: raise RuntimeError("tasks/task-board.json에 업무가 없습니다.")
    status={"date":DAY,"updated_at":NOW.isoformat(),"run_id":os.getenv("GITHUB_RUN_ID",""),"repository":os.getenv("GITHUB_REPOSITORY",""),"model":MODEL,"overall_status":"running","progress":10,"departments":[
      {"id":"planning","name":"기획부","status":"running","progress":25,"message":"업무 후보 검토"},
      {"id":"analysis","name":"분석부","status":"queued","progress":0,"message":"기획 결과 대기"},
      {"id":"reporting","name":"보고부","status":"queued","progress":0,"message":"분석 결과 대기"},
      {"id":"executive","name":"총괄실","status":"queued","progress":0,"message":"최종 확인 대기"}],"report_path":None,"selected_tasks":[],"next_tasks":[],"error":None}
    write(ROOT/"reports/office-status.json",status); write(ROOT/"docs/office-status.json",status)
    prompt=f"""날짜 {DAY}. 회사 계획: {json.dumps(plan,ensure_ascii=False)}. 업무 보드: {json.dumps(tasks,ensure_ascii=False)}.
기획부는 오늘의 핵심 업무 3개를 현재 보드에서 우선 선정하고, 분석부는 우선순위(1~5)·기대효과·난이도·리스크를 평가, 보고부는 한국어 Markdown 보고서를 작성, 총괄실은 완료 여부와 다음 업무 1~3개를 기록하라.
내부 기획만 수행하고 외부 조사나 외부 시스템 변경은 하지 마라. 확인하지 않은 사실을 검증했다고 쓰지 말고, 실제 실행되지 않은 일을 완료했다고 주장하지 마라.
반드시 JSON만 출력: {{"selected_tasks":[{{"id":"PILOT-001","title":"업무명","department":"planning","priority":1,"expected_effect":"효과","difficulty":"낮음","risk":"리스크"}}],"department_summary":{{"planning":"요약","analysis":"요약","reporting":"요약","executive":"요약"}},"report_markdown":"# 보고서 전체 내용","next_tasks":[{{"id":"NEXT-001","title":"후속 업무","department":"planning","priority":2,"description":"설명"}}],"overall_status":"completed","completion_note":"완료 여부와 검토 필요 사항"}}"""
    try:
        out=call(prompt); selected=out.get("selected_tasks",[]); nxt=out.get("next_tasks",[]); report=out.get("report_markdown","")
        if not isinstance(selected,list) or not isinstance(nxt,list) or not report.strip(): raise RuntimeError("모델 결과에 필수 필드가 없습니다.")
        rp=ROOT/f"reports/office-{DAY}.md"; rp.parent.mkdir(parents=True,exist_ok=True); rp.write_text(report.rstrip()+"\n",encoding="utf-8")
        ids={str(x.get("id","")) for x in selected}
        for t in tasks:
            if t.get("id") in ids: t.update({"status":"completed","completed_at":NOW.isoformat(),"last_run_id":os.getenv("GITHUB_RUN_ID","")})
        known={str(t.get("id","")) for t in tasks}
        for i,t in enumerate(nxt,1):
            tid=str(t.get("id") or f"NEXT-{DAY.replace('-','')}-{i:02d}")
            if tid not in known:
                tasks.append({"id":tid,"title":str(t.get("title","후속 업무")),"department":t.get("department","planning"),"status":"queued","priority":int(t.get("priority",3) or 3),"description":str(t.get("description","")),"created_by":"ai-office-pilot","created_at":NOW.isoformat()}); known.add(tid)
        board.update({"updated_at":NOW.isoformat(),"tasks":tasks}); write(ROOT/"tasks/task-board.json",board)
        summary=out.get("department_summary",{})
        status.update({"overall_status":out.get("overall_status","needs_review"),"progress":100 if out.get("overall_status")=="completed" else 90,
          "departments":[{"id":k,"name":n,"status":"completed","progress":100,"message":str(summary.get(k,"결과 기록"))[:400]} for k,n in [("planning","기획부"),("analysis","분석부"),("reporting","보고부"),("executive","총괄실")]],
          "report_path":f"reports/office-{DAY}.md","selected_tasks":selected,"next_tasks":nxt,"completion_note":out.get("completion_note","")})
        write(ROOT/"reports/office-status.json",status); write(ROOT/"docs/office-status.json",status)
        print(f"Created reports/office-{DAY}.md and updated task board.")
    except Exception as e:
        status.update({"overall_status":"error","progress":0,"error":str(e),"departments":[{"id":"planning","name":"기획부","status":"error","progress":0,"message":"실행 실패"},{"id":"analysis","name":"분석부","status":"blocked","progress":0,"message":"앞 단계 실패"},{"id":"reporting","name":"보고부","status":"blocked","progress":0,"message":"앞 단계 실패"},{"id":"executive","name":"총괄실","status":"blocked","progress":0,"message":"오류 기록"}]})
        write(ROOT/"reports/office-status.json",status); write(ROOT/"docs/office-status.json",status); raise
if __name__=="__main__":
    try: main()
    except Exception as e: print(f"AI Office Pilot failed: {e}",file=sys.stderr); sys.exit(1)
