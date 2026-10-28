import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY", "")
TASK = os.environ.get("OFFICE_TASK", "").strip()

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPORTS = ROOT / "reports"


def main():
    if not API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY secret이 없습니다. "
            "GitHub 저장소의 Settings에서 확인하세요."
        )

    if not TASK:
        raise RuntimeError("업무 지시가 비어 있습니다.")

    client = genai.Client(api_key=API_KEY)

    prompt = f"""
당신은 기업의 AI 기획실입니다.
아래 업무 지시를 한국어로 분석하고 실행 가능한 결과를 작성하세요.

반드시 다음 항목을 포함하세요.
1. 업무 요약
2. 핵심 분석 및 확인이 필요한 사실
3. 실행 과제와 우선순위
4. 담당 부서 제안
5. 위험요인 및 후속 조치

근거가 없는 사실이나 완료하지 않은 작업을 사실처럼 표현하지 마세요.
실제 외부 시스템에 접근하거나 업무를 실행하지 못했다면 그 한계를 밝혀주세요.

업무 지시:
{TASK}
"""

    # 서버 과부하(503) 대응: 1순위 최신 모델과 2순위 안정형 백업 모델 지정
    target_models = ['gemini-3.8-flash', 'gemini-1.5-pro']
    response = None
    last_exception = None

    for model_name in target_models:
        success = False
        for attempt in range(3):  # 각 모델별 최대 3번 재시도
            try:
                print(f"시도 중: {model_name} (시도 횟수 {attempt + 1}/3)")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and response.text:
                    success = True
                    break
            except Exception as exc:
                last_exception = exc
                print(f"경고: {model_name} 호출 중 일시적 오류 발생. 3초 후 재시도합니다... ({exc})")
                time.sleep(3 * (attempt + 1))  # 점진적으로 대기 시간 증가
        
        if success:
            break

    if not response or not response.text:
        raise RuntimeError(
            f"모든 모델 호출 실패 (서버 과부하 또는 네트워크 에러): {last_exception}"
        )

    report_text = response.text.strip()

    DOCS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now = datetime.now(timezone.utc).isoformat()

    report_path = REPORTS / f"office-{today}.md"
    report_path.write_text(
        f"# AI Office 업무보고서\n\n"
        f"- 생성일(UTC): {now}\n\n"
        f"## 입력된 업무 지시\n\n{TASK}\n\n"
        f"## Gemini 분석 결과\n\n{report_text}\n",
        encoding="utf-8",
    )

    status = {
        "updated_at": now,
        "status": "completed",
        "latest_report": f"../reports/office-{today}.md",
        "task": TASK,
        "summary": report_text[:500],
        "departments": [
            {"name": "기획부", "status": "검토 필요"},
            {"name": "분석부", "status": "검토 필요"},
            {"name": "보고부", "status": "보고서 생성"},
            {"name": "총괄실", "status": "결과 검토 필요"}
        ]
    }

    status_path = DOCS / "office-status.json"
    status_path.write_text(
        json.dumps(status, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"보고서 생성 완료: {report_path.relative_to(ROOT)}")
    print(f"상태 데이터 생성 완료: {status_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
