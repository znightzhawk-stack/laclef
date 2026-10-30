import datetime
import glob
import json
import os
import urllib.request


def generate_executive_report():
  api_key = os.environ.get("GEMINI_API_KEY")
  prompt = "(주)큐에이치앤씨 이기석 팀장을 위한 엔터프라이즈급 경영 및 포트폴리오 전략 보고서를 작성해주세요. 미국 증시(NVDA, AVGO, ALAB) 및 부동산 개발 사업 현황 포함."

  report_text = ""
  if api_key:
    try:
      # 표준 urllib를 사용해 외부 패키지 의존성 없이 Gemini REST API 호출
      url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
      headers = {"Content-Type": "application/json"}
      data = {"contents": [{"parts": [{"text": prompt}]}]}
      req = urllib.request.Request(
          url,
          data=json.dumps(data).encode("utf-8"),
          headers=headers,
          method="POST",
      )
      with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
        report_text = (
            result.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )
    except Exception as e:
      print(f"API call notice: {e}")

  # API 호출 실패 또는 키가 없을 시 기관용 기본 템플릿 적용
  if not report_text:
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    report_text = f"""# LACLEF EXECUTIVE QUANTITATIVE REPORT
- **Date:** {today_str}
- **Author:** 이기석 회사 ((앤드원홀딩스(주))

## 1. MACRO & US EQUITY PORTFOLIO STRATEGY (AI INFRASTRUCTURE)
- **Core Holdings:** NVIDIA (NVDA), Broadcom (AVGO), Astera Labs (ALAB)
- **Analysis:** AI 하드웨어 밸류체인 내 독점적 해자를 지닌 핵심 종목군으로, Q3 실적 시즌 및 데이터센터 인프라 수급 확장에 따른 모멘텀 유지.

## 2. REAL ESTATE DEVELOPMENT PROJECT STATUS
- **Sokcho I-Park Suite:** 성과보수 및 프로모션 장소제공 계약 관리 완료, 현장 운영 점검.
- **Ulsan Samsan-dong Project:** 608세대 공동주택 개발 타당성 및 분양가 모델 검토 지속.
"""

  os.makedirs("reports", exist_ok=True)
  today_str = datetime.datetime.now().strftime("%Y-%m-%d")
  filename = f"reports/office-{today_str}.md"
  with open(filename, "w", encoding="utf-8") as f:
    f.write(report_text)
  print(f"Successfully generated: {filename}")


def update_static_dashboard():
  reports_dir = "reports"
  os.makedirs(reports_dir, exist_ok=True)
  report_files = sorted(
      glob.glob(os.path.join(reports_dir, "*.md")), reverse=True
  )

  list_items = ""
  for filepath in report_files:
    filename = os.path.basename(filepath)
    list_items += f"""
        <li style="margin-bottom: 12px; padding: 15px; background: #1e293b; border-radius: 8px; border-left: 4px solid #3b82f6;">
            <a href="reports/{filename}" target="_blank" style="color: #60a5fa; font-weight: bold; text-decoration: none; font-size: 1.1rem;">📄 {filename}</a>
            <p style="color: #94a3b8; margin: 5px 0 0 0; font-size: 0.9rem;">앤드원홀딩스(주) 엔터프라이즈급 타당성 및 포트폴리오 분석 보고서</p>
        </li>
        """

  html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LACLEF Executive Command Center</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 40px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        h1 {{ color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 15px; margin-top: 0; }}
        ul {{ list-style: none; padding: 0; }}
        .footer {{ margin-top: 30px; text-align: center; color: #64748b; font-size: 0.85rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏢 LACLEF Executive Command Center</h1>
        <p style="color: #94a3b8;">앤드원홀딩스(주) 실시간 부동산 개발 및 글로벌 포트폴리오 관제실</p>
        <hr style="border: 0; border-top: 1px solid #334155; margin: 20px 0;">
        
        <h2>📊 생성된 정밀 분석 보고서 목록</h2>
        <ul>
            {list_items if list_items else '<p style="color: #94a3b8;">아직 생성된 보고서가 없습니다.</p>'}
        </ul>
        
        <div class="footer">
            System Status: <strong>ONLINE (Zero-Dependency Mode)</strong> • Powered by Python Stdlib
        </div>
    </div>
</body>
</html>
"""

  with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
  print("Successfully updated static index.html.")


def main():
  print("Starting LACLEF workflow...")
  generate_executive_report()
  update_static_dashboard()
  print("Workflow completed successfully.")


if __name__ == "__main__":
  main()
