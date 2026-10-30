import datetime
import glob
import os
import google.generativeai as genai


def generate_executive_report(custom_prompt=""):
  api_key = os.environ.get("GEMINI_API_KEY")
  if api_key:
    genai.configure(api_key=api_key)

  model_name = "gemini-3.8-flash"
  prompt = (
      custom_prompt
      if custom_prompt
      else "엔터프라이즈급 경영 및 포트폴리오 전략 보고서를 작성해주세요."
  )

  report_text = ""
  try:
    if api_key:
      model = genai.GenerativeModel(model_name)
      response = model.generate_content(prompt)
      report_text = response.text
    else:
      raise Exception("GEMINI_API_KEY not found.")
  except Exception as e:
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    report_text = f"# LACLEF EXECUTIVE REPORT\n- **Date:** {today_str}\n\n## 1. Status\n- Generated via fallback template.\n"

  os.makedirs("reports", exist_ok=True)
  today_str = datetime.datetime.now().strftime("%Y-%m-%d")
  filename = f"reports/office-{today_str}.md"

  with open(filename, "w", encoding="utf-8") as f:
    f.write(report_text)
  print(f"Generated: {filename}")


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
            <p style="color: #94a3b8; margin: 5px 0 0 0; font-size: 0.9rem;">LACLEF Executive Report</p>
        </li>
        """

  html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>LACLEF Executive Command Center</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 40px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 12px; }}
        h1 {{ color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 15px; }}
        ul {{ list-style: none; padding: 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏢 LACLEF Executive Command Center</h1>
        <h2>📊 보고서 목록</h2>
        <ul>
            {list_items if list_items else '<p>보고서 없음</p>'}
        </ul>
    </div>
</body>
</html>
"""

  with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
  print("Dashboard updated.")


def main():
  # 원하시는 프롬프트를 파라미터에 넣거나 공란으로 두시면 됩니다.
  user_prompt = os.environ.get("CUSTOM_PROMPT", "")
  generate_executive_report(user_prompt)
  update_static_dashboard()


if __name__ == "__main__":
  main()
