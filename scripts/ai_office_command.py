import os
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY", "")
TASK = os.environ.get("OFFICE_TASK", "").strip()

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPORTS = ROOT / "reports"


def main():
    if not API_KEY:
        raise RuntimeError("GEMINI_API_KEY secret이 없습니다. GitHub 저장소 Settings를 확인하세요.")
    if not TASK:
        raise RuntimeError("업무 지시가 비어 있습니다.")

    client = genai.Client(api_key=API_KEY)

    # 디벨로퍼 전용 프롬프트 (수지분석, 토지비 역산, 민감도 분석, 독소조항 방어)
    prompt = f"""
당신은 대한민국 최고 수준의 부동산 개발(시행) PF 전문 수석 애널리스트이자 AI 기획실장입니다.
아래 업무 지시에 대해, 두루뭉술한 템플릿이 아닌 **실제 부지 매입 여부와 PF 조달 결정을 내리기 위한 디벨로퍼 레벨의 심층 타당성 검토 보고서**를 작성하세요.

반드시 다음 5가지 핵심 요소를 상세한 수치 시뮬레이션과 함께 포함하여 마크다운 형식으로 작성하세요.

1. 개발 개요 및 건축 가설계(Mass Study) 역산
   - 용도지역(준주거/상업지역 가정)별 최대 용적률 적용 연면적 추정.
   - 호실 구성(소형 원룸 vs 투룸 아파텔 MD Mix) 및 주차대수(서울시 조례 기준) 충족 검토.
2. 추정 수지분석표 (Cash Flow & P&L 구조)
   - [A] 총분양수입 (예상 평당 분양가 및 분양가율 적용 총액)
   - [B] 총사업비 구성: 토지비, 건축공사비(평당 단가 산정), 부대비용(설계/감리/마케팅 등 총매출의 6~8%), 금융비용(브릿지론/본PF 이자)
   - [C] 시행이익 및 자기자본수익률(IRR/ROE) 추정 (목표 마진율 제시)
3. 토지가격 역산 (Residual Land Value / Hurdle Price)
   - 목표 시행이익률을 역산하여, 현 분양가 및 공사비 조건에서 **우리가 이 땅을 평당 얼마 이하로 매입해야 사업성이 성립하는지(마지노선 매입가)** 도출.
4. 민감도 분석 (Sensitivity Analysis)
   - 분양가 5% 하락 시 및 공사비 10% 상승 시 시행 이익 및 손익분기점 변동 시뮬레이션.
5. 핵심 리스크 및 계약 방어 조항 (Legal & Risk Mitigation)
   - 본PF 조달 실패 리스크 대응 (시공사 책임준공 및 채무인수 조건).
   - 토지 매매계약 특약 가이드 ('인허가 불허 시 계약 무효 및 계약금 반환', '매도인 책임 명도 완료 조건').

업무 지시:
{TASK}
"""

    target_models = ['gemini-3.8-flash', 'gemini-1.5-pro']
    response = None
    last_exception = None

    for model_name in target_models:
        success = False
        for attempt in range(3):
            try:
                print(f"AI 분석 시도: {model_name} (시도 {attempt + 1}/3)")
                response = client.models.generate_content(model=model_name, contents=prompt)
                if response and response.text:
                    success = True
                    break
            except Exception as exc:
                last_exception = exc
                print(f"일시적 오류 발생. 3초 후 재시도... ({exc})")
                time.sleep(3 * (attempt + 1))
        if success:
            break

    if not response or not response.text:
        raise RuntimeError(f"모든 모델 호출 실패: {last_exception}")

    report_text = response.text.strip()

    DOCS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    KST = timezone(timedelta(hours=9))
    today = datetime.now(KST).strftime("%Y-%m-%d")
    now_kst = datetime.now(KST).isoformat()

    report_filename = f"office-{today}.md"
    report_path = REPORTS / report_filename
    report_path.write_text(
        f"# [디벨로퍼 타당성 검토 보고서]\n\n"
        f"- 생성일시(KST): {now_kst}\n"
        f"- 대상 업무: {TASK}\n\n"
        f"---\n\n{report_text}\n",
        encoding="utf-8",
    )

    # 대시보드 연동용 상태 JSON
    status = {
        "updated_at": now_kst,
        "status": "completed",
        "latest_report": f"reports/{report_filename}",
        "task": TASK,
        "summary": report_text[:600] + "...",
        "full_report_content": report_text,
        "departments": [
            {"name": "개발사업부", "status": "가설계 및 용적률 역산 완료"},
            {"name": "재무PF팀", "status": "수지분석 및 토지비 한계가(Hurdle Price) 산출 완료"},
            {"name": "분양마케팅부", "status": "적정 분양가 및 민감도 분석 완료"},
            {"name": "법무대관실", "status": "계약 특약 및 리스크 방어 조항 검토 완료"}
        ]
    }

    status_path = DOCS / "office-status.json"
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"보고서 생성 완료: {report_path}")
    print(f"상태 데이터 갱신 완료: {status_path}")


if __name__ == "__main__":
    main()
