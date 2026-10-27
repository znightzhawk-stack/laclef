# Laclef AI Office Pilot

## 기존 설정 보존
- 기존 `.github/workflows/daily-report.yml`을 수정하지 않습니다.
- 기존 `docs/index.html`을 덮어쓰지 않습니다.
- 새 파일 `ai-office-pilot.yml`, `scripts/ai_office_pilot.py`, `docs/office-dashboard.html`을 추가합니다.
- 새 workflow는 수동 실행과 매일 09:30 KST 예약 실행을 지원합니다.

## 적용
1. 저장소 https://github.com/znighthawk-stack/laclef 에서 Add file → Upload files를 누릅니다.
2. 압축을 풀고 내부 경로 그대로 파일들을 업로드합니다. 숨김 경로 `.github/workflows/`도 포함합니다.
3. 기존 `GEMINI_API_KEY` secret이 Settings → Secrets and variables → Actions에 있는지 확인합니다. 키 값은 공유하지 마세요.
4. 기존 daily-report.yml이 사용하는 Gemini 모델 ID가 `gemini-2.5-flash`와 다르면 Settings → Secrets and variables → Actions → Variables에 `GEMINI_MODEL`을 만들고 기존 파일의 정확한 모델 ID를 입력합니다.
5. Actions → AI Office Pilot → Run workflow로 수동 실행합니다.
6. 초록색 완료 후 `reports/office-YYYY-MM-DD.md`, `reports/office-status.json`, `tasks/task-board.json`을 확인합니다. 실패하면 실행 로그의 오류 메시지를 확인합니다.
7. 새 화면은 `docs/office-dashboard.html`입니다. 브라우저에서 호스팅하려면 GitHub Pages가 필요합니다. 기존 3D 대시보드는 이 패키지에서 덮어쓰지 않습니다.

## 기능 범위
한 번의 Gemini API 호출에서 부서 역할을 순서대로 수행하는 파일럿입니다. 네 개의 독립 AI 에이전트가 상호 대화하는 구조는 아니며, 외부 웹 조사·메일 발송·외부 업무 시스템 변경도 하지 않습니다. 모델이 제안한 업무는 보드에 대기 상태로 기록합니다.
Workflow는 결과 파일 커밋을 위해 `contents: write` 권한을 사용합니다. Gemini 사용량과 무료 한도는 Google의 현재 조건에 따릅니다.
