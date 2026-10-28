import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

API_KEY = os.environ.get("GEMINI_API_KEY", "")
# 외부 환경변수의 간섭을 받지 않도록 안정적인 모델명으로 강제 고정합니다.
MODEL = "gemini-1.5-flash"
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

    DOCS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now = datetime.now(timezone.utc).isoformat()

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

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.3
        }
    }

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{MODEL}:generateContent?key={API_KEY}"
    )

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Gemini API 요청 실패 (HTTP {exc.code}): {detail[:1500]}"
        ) from exc

    candidates = result.get("candidates", [])
    if not candidates:
        raise RuntimeError(
            "Gemini가 결과를 반환하지 않았습니다. API 응답을 확인하세요."
        )

    parts = candidates[0].get("content", {}).get("parts", [])
    report_text = "\n".join(
        part.get("text", "") for part in parts if part.get("text")
    ).strip()

    if not report_text:
        raise RuntimeError("Gemini 응답에 보고서 본문이 없습니다.")

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
