import os
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY", "")
TASK = os.environ.get("OFFICE_TASK", "").strip()

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPORTS = ROOT / "reports"
INDEX_PATH = ROOT / "index.html"


def generate_dashboard_html():
    """대시보드 HTML을 루트에 자동으로 생성/갱신하는 함수"""
    html_content = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LACLEF | AI Group Executive Command</title>
<meta name="description" content="AI 그룹회사 통합 대시보드와 미니어처 아이소메트릭 사무실">
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<style>
:root {
    --bg: #030712;
    --surface: #0b1120;
    --surface-glass: rgba(15, 23, 42, 0.75);
    --border: rgba(51, 65, 85, 0.6);
    --border-bright: rgba(56, 189, 248, 0.4);
    --text: #f8fafc;
    --muted: #94a3b8;
    --cyan: #38bdf8;
    --indigo: #818cf8;
    --emerald: #34d399;
    --amber: #fbbf24;
    --rose: #fb7185;
}
* { box-sizing: border-box; }
body {
    margin: 0;
    background-color: var(--bg);
    background-image: 
        radial-gradient(circle at 15% 15%, rgba(56, 189, 248, 0.06) 0%, transparent 40%),
        radial-gradient(circle at 85% 85%, rgba(129, 140, 248, 0.05) 0%, transparent 40%);
    color: var(--text);
    font: 13.5px/1.5 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    letter-spacing: -0.01em;
}
button { font: inherit; cursor: pointer; transition: all 0.2s ease; }

header {
    display: flex; justify-content: space-between; align-items: center; gap: 16px;
    padding: 16px 32px; border-bottom: 1px solid var(--border);
    background: rgba(3, 7, 18, 0.85); position: sticky; top: 0; z-index: 50; backdrop-filter: blur(16px);
}
.brand { display: flex; align-items: center; gap: 14px; }
.logo {
    width: 40px; height: 40px; display: grid; place-items: center;
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.15), rgba(129, 140, 248, 0.15));
    border: 1px solid var(--border-bright); border-radius: 12px; color: var(--cyan);
    font-weight: 800; font-size: 16px; box-shadow: 0 0 20px rgba(56, 189, 248, 0.15);
}
.brand h1 { font-size: 14px; letter-spacing: 0.12em; margin: 0; font-weight: 700; }
.brand small { display: block; color: var(--muted); font-size: 10px; letter-spacing: 0.1em; margin-top: 2px; }
.header-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.chip {
    padding: 6px 12px; border: 1px solid var(--border); border-radius: 9999px;
    color: var(--muted); font-size: 11px; font-weight: 500; background: var(--surface); display: flex; align-items: center;
}
.chip.good { color: var(--emerald); border-color: rgba(52, 211, 153, 0.3); background: rgba(52, 211, 153, 0.05); }
.led { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--emerald); margin-right: 6px; box-shadow: 0 0 8px var(--emerald); }

main { max-width: 1400px; margin: auto; padding: 32px 24px; display: grid; gap: 24px; }
.hero { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.eyebrow { font-size: 11px; letter-spacing: 0.2em; color: var(--cyan); text-transform: uppercase; font-weight: 600; margin-bottom: 6px; }
.hero h2 { font-size: clamp(24px, 2.5vw, 32px); margin: 0; font-weight: 700; letter-spacing: -0.02em; }
.hero p { color: var(--muted); margin: 6px 0 0; font-size: 14px; }
.actions { display: flex; gap: 10px; flex-wrap: wrap; }
.btn {
    border: 1px solid var(--border); background: var(--surface); color: var(--text);
    padding: 8px 16px; border-radius: 10px; font-size: 12px; font-weight: 500;
}
.btn.primary { border-color: rgba(56, 189, 248, 0.4); background: rgba(56, 189, 248, 0.1); color: #bae6fd; }
.btn:hover { border-color: var(--muted); background: rgba(255, 255, 255, 0.04); }
.btn.primary:hover { background: rgba(56, 189, 248, 0.18); }

.notice {
    border: 1px solid rgba(251, 191, 36, 0.25); background: rgba(251, 191, 36, 0.05);
    color: #fde68a; border-radius: 12px; padding: 12px 18px; font-size: 12.5px; display: flex; align-items: center; gap: 10px;
}

.metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.metric, .panel {
    border: 1px solid var(--border); background: var(--surface-glass); border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); backdrop-filter: blur(12px);
}
.metric { padding: 20px; }
.metric .label { color: var(--muted); font-size: 12px; font-weight: 500; }
.metric .value { font-size: 28px; font-weight: 700; margin: 8px 0 4px; letter-spacing: -0.02em; }
.metric .foot { font-size: 11px; color: var(--muted); }
.metric .value.cyan { color: var(--cyan); text-shadow: 0 0 20px rgba(56, 189, 248, 0.3); }
.metric .value.green { color: var(--emerald); text-shadow: 0 0 20px rgba(52, 211, 153, 0.3); }

.layout { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(320px, 0.9fr); gap: 20px; }
.panel-head { padding: 18px 22px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.panel-head h3 { font-size: 14px; margin: 0; font-weight: 600; letter-spacing: -0.01em; }
.panel-head p { font-size: 11.5px; color: var(--muted); margin: 3px 0 0; }
.panel-body { padding: 20px 22px; }
.tiny { font-size: 11px; color: var(--muted); }
.tag { font-size: 10.5px; border: 1px solid var(--border); padding: 4px 10px; border-radius: 9999px; color: var(--muted); white-space: nowrap; font-weight: 500; background: rgba(255, 255, 255, 0.02); }
.tag.demo { color: var(--amber); border-color: rgba(251, 191, 36, 0.3); background: rgba(251, 191, 36, 0.05); }
.tag.live { color: var(--emerald); border-color: rgba(52, 211, 153, 0.3); background: rgba(52, 211, 153, 0.05); }

.office-wrap { overflow: hidden; position: relative; min-height: 380px; background: radial-gradient(circle at center, #0f172a 0%, #030712 75%); border-radius: 0 0 16px 16px; padding: 12px; }
.office-top { display: flex; justify-content: space-between; align-items: center; margin: 0 8px 12px; }
.office-stage { height: 340px; display: grid; place-items: center; perspective: 1200px; overflow: hidden; }
.iso {
    width: min(540px, 95%); aspect-ratio: 1.45; position: relative;
    transform: rotateX(54deg) rotateZ(-45deg) scale(0.78); transform-style: preserve-3d;
    transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1); filter: drop-shadow(0 25px 35px rgba(0,0,0,0.6));
}
.iso.spin { transform: rotateX(54deg) rotateZ(315deg) scale(0.78); }
.floor {
    position: absolute; inset: 0; background: linear-gradient(135deg, #0b1329, #060a17);
    border: 2px solid rgba(56, 189, 248, 0.25); box-shadow: inset 0 0 0 12px #040711, 0 0 0 1px rgba(56, 189, 248, 0.1);
    transform: translateZ(0); background-image: linear-gradient(rgba(56, 189, 248, 0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(56, 189, 248, 0.04) 1px, transparent 1px);
    background-size: 32px 32px;
}
.room {
    position: absolute; width: 42%; height: 42%; border: 2px solid rgba(56, 189, 248, 0.35);
    background: rgba(15, 23, 42, 0.85); transform-style: preserve-3d; box-shadow: 8px 8px 0 rgba(2, 6, 23, 0.6); transition: all 0.2s;
}
.room:hover { border-color: var(--cyan); background: rgba(30, 41, 59, 0.9); }
.room:before, .room:after { content: ""; position: absolute; background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(56, 189, 248, 0.2); }
.room:before { width: 100%; height: 24px; left: 0; top: -24px; transform: skewY(-35deg); transform-origin: bottom; background: rgba(30, 58, 95, 0.4); }
.room:after { height: 100%; width: 24px; right: -24px; top: 0; transform: skewX(-35deg); transform-origin: left; background: rgba(15, 30, 53, 0.4); }
.room button { position: absolute; inset: 0; border: 0; background: transparent; cursor: pointer; z-index: 2; }
.room .roomname {
    position: absolute; inset: 0; display: grid; place-items: center; text-align: center; color: #e0f2fe; font-weight: 700; font-size: 11.5px;
    transform: rotateZ(45deg) rotateX(-54deg) translateZ(20px); text-shadow: 0 0 12px rgba(56, 189, 248, 0.5); pointer-events: none;
}
.room .desk {
    position: absolute; width: 34%; height: 20%; left: 33%; top: 35%; background: #1e293b; border: 1px solid rgba(148, 163, 184, 0.3);
    transform: translateZ(18px); box-shadow: 0 0 10px rgba(56, 189, 248, 0.15);
}
.room .desk:after { content: ""; position: absolute; width: 20%; height: 50%; left: 40%; top: 25%; background: var(--cyan); box-shadow: 0 0 10px var(--cyan); }
.room.plan { left: 4%; top: 4%; border-color: rgba(56, 189, 248, 0.5); }
.room.dev { right: 4%; top: 4%; border-color: rgba(129, 140, 248, 0.5); }
.room.market { left: 4%; bottom: 4%; border-color: rgba(52, 211, 153, 0.5); }
.room.finance { right: 4%; bottom: 4%; border-color: rgba(251, 191, 36, 0.5); }

.core {
    position: absolute; left: 38%; top: 38%; width: 24%; height: 24%; background: rgba(15, 23, 42, 0.95);
    border: 2px solid var(--cyan); box-shadow: 0 0 30px rgba(56, 189, 248, 0.25); transform: translateZ(26px);
    display: grid; place-items: center; color: var(--cyan); font-size: 11px; font-weight: 800; text-align: center; letter-spacing: 0.1em;
}
.core span { transform: rotateZ(45deg) rotateX(-54deg); }
.office-legend { display: flex; gap: 12px; flex-wrap: wrap; padding: 0 12px 8px; }
.dept-dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: 6px; box-shadow: 0 0 6px currentColor; }

.dept-list { display: grid; gap: 10px; }
.dept {
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
    padding: 12px 14px; border: 1px solid var(--border); border-radius: 12px; background: rgba(15, 23, 42, 0.5); transition: all 0.2s;
}
.dept:hover { border-color: rgba(56, 189, 248, 0.3); background: rgba(15, 23, 42, 0.8); }
.dept strong { display: block; font-size: 12.5px; font-weight: 600; }
.dept small { display: block; color: var(--muted); font-size: 11px; margin-top: 3px; }
.dept button {
    border: 1px solid var(--border); border-radius: 8px; padding: 6px 12px;
    background: var(--surface); color: var(--text); font-size: 11.5px; font-weight: 500;
}
.dept button:hover { background: rgba(56, 189, 248, 0.1); border-color: var(--cyan); color: var(--cyan); }
.status { font-size: 10.5px; color: var(--amber); font-weight: 500; margin-bottom: 2px; }
.status.ok { color: var(--emerald); }

.bottom { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.bar-row { display: grid; grid-template-columns: 100px 1fr 36px; align-items: center; gap: 12px; margin: 14px 0; font-size: 11.5px; }
.bar { height: 8px; border-radius: 9999px; background: rgba(255, 255, 255, 0.05); overflow: hidden; border: 1px solid var(--border); }
.bar i { display: block; height: 100%; background: linear-gradient(90deg, #38bdf8, #818cf8); border-radius: 9999px; }
.feed { display: grid; gap: 10px; }
.feed-item { display: flex; gap: 12px; align-items: flex-start; padding-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.04); }
.feed-item:last-child { border: 0; padding-bottom: 0; }
.feed-icon {
    width: 28px; height: 28px; border: 1px solid var(--border); border-radius: 8px;
    display: grid; place-items: center; color: var(--cyan); flex-shrink: 0; background: rgba(56, 189, 248, 0.05);
}
.feed-item strong { font-size: 12px; display: block; font-weight: 600; }
.feed-item p { font-size: 11.5px; color: var(--muted); margin: 3px 0 0; }

.reports { display: grid; gap: 8px; }
.report {
    display: flex; justify-content: space-between; align-items: center; gap: 12px;
    padding: 12px 14px; background: rgba(15, 23, 42, 0.5); border: 1px solid var(--border); border-radius: 10px; transition: all 0.2s;
}
.report:hover { border-color: rgba(56, 189, 248, 0.3); background: rgba(15, 23, 42, 0.8); }
.report a { color: #e0f2fe; text-decoration: none; font-size: 12.5px; overflow-wrap: anywhere; font-weight: 500; }
.report a:hover { color: var(--cyan); text-decoration: underline; }
.empty { color: var(--muted); font-size: 12.5px; padding: 16px 0; text-align: center; }
.footer { color: var(--muted); font-size: 11px; text-align: center; padding: 10px 0 24px; letter-spacing: 0.02em; }

#modal {
    position: fixed; inset: 0; background: rgba(3, 7, 18, 0.8); backdrop-filter: blur(8px);
    display: none; align-items: center; justify-content: center; padding: 20px; z-index: 100;
}
#modal.open { display: flex; }
.modal-card {
    max-width: 560px; width: 100%; border: 1px solid var(--border-bright); border-radius: 20px;
    background: #0b1120; padding: 24px; box-shadow: 0 25px 60px rgba(0,0,0,0.6);
}
.modal-card h3 { margin: 0 0 8px; font-size: 18px; font-weight: 700; }
.modal-card p { color: var(--muted); font-size: 13px; line-height: 1.6; }
.modal-card button { float: right; margin-top: 10px; }

@media(max-width: 900px) {
    .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .layout, .bottom { grid-template-columns: 1fr; }
    .office-stage { height: 280px; }
    .iso { transform: rotateX(54deg) rotateZ(-45deg) scale(0.62); }
    .iso.spin { transform: rotateX(54deg) rotateZ(315deg) scale(0.62); }
}
</style>
</head>
<body>
<header>
  <div class="brand">
    <div class="logo">L</div>
    <div><h1>LACLEF <span style="color:var(--cyan)">/ AI GROUP</span></h1><small>EXECUTIVE COMMAND CENTER</small></div>
  </div>
  <div class="header-right">
    <span id="sourceChip" class="chip">데이터 연결 확인 중</span>
    <span class="chip good"><i class="led"></i>WEB ONLINE</span>
    <span class="chip" id="clock">--:--:-- KST</span>
  </div>
</header>
<main>
  <section class="hero">
    <div>
      <div class="eyebrow">AI COMPANY OPERATIONS</div>
      <h2>그룹 통합 관제실</h2>
      <p>부서별 업무 흐름 · 자동화 실행 · 경영 보고서를 한 화면에서 실시간으로 관제합니다.</p>
    </div>
    <div class="actions">
      <button class="btn" id="rotateBtn">3D 공간 회전</button>
      <button class="btn primary" id="refreshBtn">데이터 새로고침</button>
    </div>
  </section>

  <div class="notice" id="dataNotice">
    <span>💡</span>
    <div>GitHub 저장소 및 Actions 연동 상태를 실시간으로 확인하며, 최신 AI 리포트와 부서별 현황을 불러옵니다.</div>
  </div>

  <section class="metrics">
    <div class="metric">
      <div class="label">부서 공간</div>
      <div class="value cyan">04</div>
      <div class="foot">기획 · 사업개발 · 마케팅 · 재무</div>
    </div>
    <div class="metric">
      <div class="label">저장된 보고서</div>
      <div class="value" id="reportCount">--</div>
      <div class="foot" id="reportCountFoot">GitHub 연결 확인 중</div>
    </div>
    <div class="metric">
      <div class="label">최근 워크플로 실행</div>
      <div class="value" id="runState">확인 중</div>
      <div class="foot" id="runDate">실행 이력 조회 중</div>
    </div>
    <div class="metric">
      <div class="label">시스템 모드</div>
      <div class="value green" id="modeValue">DEMO</div>
      <div class="foot" id="modeFoot">연결 전에는 예시 데이터 표시</div>
    </div>
  </section>

  <section class="layout">
    <div class="panel">
      <div class="panel-head">
        <div>
          <h3>미니어처 아이소메트릭 사무실</h3>
          <p>부서를 클릭하면 역할과 상세 연결 상태를 확인할 수 있습니다.</p>
        </div>
        <span class="tag">INTERACTIVE 3D VIEW</span>
      </div>
      <div class="office-wrap">
        <div class="office-top">
          <span class="tiny">VIRTUAL FLOOR · LEVEL 01</span>
          <span class="tiny">클릭 가능한 부서 공간</span>
        </div>
        <div class="office-stage">
          <div class="iso" id="iso">
            <div class="floor"></div>
            <div class="room plan"><button data-dept="planning" aria-label="기획실"></button><div class="desk"></div><div class="roomname">기획실</div></div>
            <div class="room dev"><button data-dept="development" aria-label="사업개발실"></button><div class="desk"></div><div class="roomname">사업개발실</div></div>
            <div class="room market"><button data-dept="marketing" aria-label="마케팅실"></button><div class="desk"></div><div class="roomname">마케팅실</div></div>
            <div class="room finance"><button data-dept="finance" aria-label="재무·리스크실"></button><div class="desk"></div><div class="roomname">재무·리스크실</div></div>
            <div class="core"><span>AI CORE</span></div>
          </div>
        </div>
        <div class="office-legend">
          <span class="tiny"><i class="dept-dot" style="color:var(--cyan)"></i>기획실</span>
          <span class="tiny"><i class="dept-dot" style="color:var(--indigo)"></i>사업개발실</span>
          <span class="tiny"><i class="dept-dot" style="color:var(--emerald)"></i>마케팅실</span>
          <span class="tiny"><i class="dept-dot" style="color:var(--amber)"></i>재무·리스크실</span>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-head">
        <div>
          <h3 id="deptTitle">부서별 운영 현황</h3>
          <p>그룹사 주요 부문별 AI 연동 및 실행 상태</p>
        </div>
        <span class="tag demo" id="deptTag">현황</span>
      </div>
      <div class="panel-body">
        <div class="dept-list" id="deptList"></div>
        <div style="margin-top:16px;border-top:1px solid var(--border);padding-top:14px">
          <div class="tiny">선택한 부서</div>
          <h3 id="selectedName" style="margin:6px 0; font-size:15px;">기획실</h3>
          <p id="selectedDesc" style="margin:0;color:var(--muted);font-size:12px">경영 요약, 일일 업무보고, 실행 우선순위 관리</p>
          <div id="selectedData" class="tiny" style="margin-top:10px;color:var(--text);background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;border:1px solid var(--border);">부서를 선택하여 상세 정보를 확인하세요.</div>
        </div>
      </div>
    </div>
  </section>

  <section class="bottom">
    <div class="panel">
      <div class="panel-head">
        <div>
          <h3>부서별 자동화 준비도</h3>
          <p>현재 구축 및 연동 진척도 지표</p>
        </div>
        <span class="tag demo">진척도</span>
      </div>
      <div class="panel-body" id="bars"></div>
    </div>
    <div class="panel">
      <div class="panel-head">
        <div>
          <h3>시스템 이벤트</h3>
          <p>브라우저 연결 및 데이터 조회 로그</p>
        </div>
        <span class="tag" id="eventTag">LOCAL</span>
      </div>
      <div class="panel-body">
        <div class="feed" id="feed"></div>
      </div>
    </div>
  </section>

  <section class="panel">
    <div class="panel-head">
      <div>
        <h3>최근 AI 일일 및 타당성 검토 보고서</h3>
        <p>GitHub 저장소 reports 폴더에 생성된 실무 보고서 목록</p>
      </div>
      <span class="tag" id="reportsTag">연결 확인 중</span>
    </div>
    <div class="panel-body">
      <div class="reports" id="reports"></div>
    </div>
  </section>

  <div class="footer">LACLEF AI GROUP · Executive Command Center · Secure Static Portal</div>
</main>

<div id="modal">
  <div class="modal-card">
    <button class="btn" id="closeModal">닫기</button>
    <h3 id="modalTitle">부서</h3>
    <p id="modalText"></p>
    <div class="tiny" style="margin-top:16px;padding:10px;background:rgba(56,189,248,0.05);border:1px solid rgba(56,189,248,0.2);border-radius:8px;color:#bae6fd;">
      실행 버튼을 통해 언제든지 실무 분석 리포트를 생성할 수 있습니다.
    </div>
  </div>
</div>

<script>
const OWNER = "znighthawk-stack";
const REPO = "laclef";
const BRANCH = "main";

const departments = [
  {id: "planning", name: "기획실", desc: "경영 요약 · 일일 보고서 · 실행 우선순위", color: "var(--cyan)", state: "기반 구축", detail: "GitHub Actions 기반 AI 일일 보고서 자동 생성 및 그룹사 총괄 기획 파이프라인이 연동되어 있습니다."},
  {id: "development", name: "사업개발실", desc: "부동산 시행 · 타당성 검토 · 수지분석", color: "var(--indigo)", state: "활성화됨", detail: "부동산 개발 시행 타당성, 토지비 역산, 용적률 산출 및 PF 리스크 검토 리포트 자동 생성 기능이 탑재되어 있습니다."},
  {id: "marketing", name: "마케팅실", desc: "캠페인 기획 · 고객 유입 · 전환 분석", color: "var(--emerald)", state: "구축 예정", detail: "마케팅 실적 및 분양/광고 캠페인 데이터 연동을 통한 성과 분석 모듈입니다."},
  {id: "finance", name: "재무·리스크실", desc: "예산 관리 · 현금흐름(Cash Flow) · 계약 검토", color: "var(--amber)", state: "구축 예정", detail: "재무제표, 자금 조달 구조 및 계약서 독소조항 방어 검토를 위한 전문 분석 모듈입니다."}
];

const $ = function(id) { return document.getElementById(id); };

function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function(match) {
        if (match === '&') return '&';
        if (match === '<') return '<';
        if (match === '>') return '>';
        if (match === '"') return '"';
        if (match === "'") return ''';
        return match;
    });
}

function addEvent(title, desc) {
  const feed = $("feed");
  const item = document.createElement("div");
  item.className = "feed-item";
  item.innerHTML = '<div class="feed-icon">◆</div><div><strong>' + escapeHtml(title) + '</strong><p>' + escapeHtml(desc) + '</p></div>';
  feed.prepend(item);
  while(feed.children.length > 5) {
    feed.lastChild.remove();
  }
}

function renderDepartments() {
  $("deptList").innerHTML = departments.map(function(d) {
    var isOk = (d.id === "planning" || d.id === "development") ? "ok" : "";
    return '<div class="dept"><div><strong><i class="dept-dot" style="color:' + d.color + '"></i>' + d.name + '</strong><small>' + d.desc + '</small></div><div style="text-align:right"><div class="status ' + isOk + '">' + d.state + '</div><button data-open="' + d.id + '">상세보기</button></div></div>';
  }).join("");
}

function selectDept(id) {
  const d = departments.find(function(x) { return x.id === id; });
  if (!d) return;
  $("selectedName").textContent = d.name;
  $("selectedDesc").textContent = d.desc;
  $("selectedData").textContent = d.detail;
  $("modalTitle").textContent = d.name;
  $("modalText").textContent = d.detail;
  $("modal").classList.add("open");
}

function renderBars() {
  const vals = [["기획실", 90], ["사업개발실", 85], ["마케팅실", 30], ["재무·리스크실", 25]];
  $("bars").innerHTML = vals.map(function(v) {
    return '<div class="bar-row"><span>' + v[0] + '</span><div class="bar"><i style="width:' + v[1] + '%"></i></div><b>' + v[1] + '%</b></div>';
  }).join("");
}

async function getJson(url) {
  const r = await fetch(url, {headers: {"Accept": "application/vnd.github+json"}, cache: "no-store"});
  if (!r.ok) throw new Error("HTTP " + r.status);
  return r.json();
}

function reportUrl(path) {
  return "https://github.com/" + OWNER + "/" + REPO + "/blob/" + BRANCH + "/" + path.split("/").map(encodeURIComponent).join("/");
}

async function loadReports() {
 const container = $("reports");
 try {
  const files = await getJson("https://api.github.com/repos/" + OWNER + "/" + REPO + "/contents/reports?ref=" + BRANCH);
  if (!Array.isArray(files)) throw new Error("reports 폴더를 읽을 수 없습니다.");
  const md = files.filter(function(f) { return f.type === "file" && f.name.endsWith(".md"); }).sort(function(a,b) { return b.name.localeCompare(a.name); }).slice(0,8);
  $("reportCount").textContent = files.filter(function(f) { return f.type === "file" && f.name.endsWith(".md"); }).length;
  $("reportCountFoot").textContent = "GitHub 저장소 연동됨";
  $("modeValue").textContent = "LIVE";
  $("modeValue").className = "value green";
  $("modeFoot").textContent = "실제 데이터 동기화 완료";
  $("sourceChip").textContent = "GitHub 라이브 연동";
  $("sourceChip").className = "chip good";
  $("dataNotice").innerHTML = '<span>✨</span><div>GitHub 저장소와 성공적으로 동기화되었습니다. 최신 타당성 검토 및 그룹사 리포트를 즉시 조회하실 수 있습니다.</div>';
  $("reportsTag").textContent = "실제 파일 목록";
  $("reportsTag").className = "tag live";
  container.innerHTML = "";
  if (!md.length) {
    container.innerHTML = '<div class="empty">reports 폴더에 생성된 보고서가 없습니다. Actions에서 워크플로를 실행해 주세요.</div>';
    return;
  }
  md.forEach(function(f) {
    const el = document.createElement("div");
    el.className = "report";
    const a = document.createElement("a");
    a.href = reportUrl(f.path);
    a.target = "_blank";
    a.rel = "noopener";
    a.textContent = f.name;
    const t = document.createElement("span");
    t.className = "tag live";
    t.textContent = "리포트 파일";
    el.append(a, t);
    container.append(el);
  });
  addEvent("보고서 목록 동기화 성공", md.length + "개 파일 로드 완료");
 } catch(e) {
  $("reportCount").textContent = "확인 중";
  $("reportCountFoot").textContent = "API 제한 또는 비공개 저장소";
  $("modeValue").textContent = "DEMO";
  $("modeValue").className = "value";
  $("modeFoot").textContent = "예시 데이터 모드";
  $("sourceChip").textContent = "오프라인/스탠바이";
  $("sourceChip").className = "chip";
  $("reportsTag").textContent = "연결 대기";
  $("reportsTag").className = "tag demo";
  container.innerHTML = '<div class="empty">저장소 보고서 목록을 가져오는 중이거나 API 접근이 제한되었습니다. Actions 실행 후 새로고침을 확인해 주세요.</div>';
  addEvent("저장소 연동 대기", e.message);
 }
}

async function loadRuns() {
 try {
  const d = await getJson("https://api.github.com/repos/" + OWNER + "/" + REPO + "/actions/runs?per_page=1");
  const r = d.workflow_runs && d.workflow_runs[0];
  if (!r) throw new Error("워크플로 실행 이력 없음");
  const success = r.conclusion === "success";
  $("runState").textContent = r.status === "in_progress" ? "실행 중" : success ? "성공" : r.conclusion || r.status;
  $("runState").className = "value " + (success ? "green" : "");
  $("runDate").textContent = new Date(r.updated_at).toLocaleString("ko-KR", {timeZone: "Asia/Seoul"}) + " · " + r.name;
  $("eventTag").textContent = "GitHub Actions";
  addEvent("최근 워크플로 상태", r.name + " (" + (r.conclusion || r.status) + ")");
 } catch(e) {
  $("runState").textContent = "대기 중";
  $("runDate").textContent = "워크플로 이력 확인 필요";
  addEvent("워크플로 미조회", e.message);
 }
}

function refresh() {
  addEvent("대시보드 새로고침", "GitHub 데이터 및 Actions 상태를 다시 조회합니다.");
  loadReports();
  loadRuns();
}

function clock() {
  $("clock").textContent = new Date().toLocaleTimeString("ko-KR", {timeZone: "Asia/Seoul", hour12: false}) + " KST";
}

document.addEventListener("click", function(e) {
  const b = e.target.closest("[data-dept],[data-open]");
  if (b) selectDept(b.dataset.dept || b.dataset.open);
});

$("closeModal").onclick = function() { $("modal").classList.remove("open"); };
$("modal").onclick = function(e) { if (e.target.id === "modal") $("modal").classList.remove("open"); };
$("rotateBtn").onclick = function() {
  $("iso").classList.toggle("spin");
  addEvent("가상 사무실 시점 변경", "아이소메트릭 3D 공간을 회전했습니다.");
};
$("refreshBtn").onclick = refresh;

renderDepartments();
renderBars();
clock();
setInterval(clock, 1000);
addEvent("통합 관제실 가동", "웹 대시보드가 성공적으로 로드되었습니다.");
refresh();
</script>
</body>
</html>
"""
    INDEX_PATH.write_text(html_content, encoding="utf-8")
    print("index.html 자동 생성 완료")


def main():
    if not API_KEY:
        raise RuntimeError("GEMINI_API_KEY secret이 없습니다.")
    if not TASK:
        raise RuntimeError("업무 지시가 비어 있습니다.")

    client = genai.Client(api_key=API_KEY)

    prompt = f"""
당신은 월가 기관투자자 리서치 센터 및 글로벌 디벨로퍼 그룹사의 수석 데이터/전략 애널리스트입니다.
대표님께서 내리신 아래의 업무 지시에 대해, 단순한 서술형 글이 아니라 **엔지니어링 수치, KPI 스코어카드, 정량적 데이터 테이블, 리스크 매트릭스**가 촘촘히 박힌 '엔터프라이즈급 정밀 분석 보고서'를 작성하세요.

반드시 다음 양식과 요소를 마크다운 테이블 및 블록 형태로 포함하세요:

1. **[EXECUTIVE KPI SCORECARD]** (핵심 지표 요약 테이블)
   - 프로젝트 명칭 / 목표 수익률(IRR/ROE) / 예상 총사업비(CAPEX) / 리스크 등급 (A~D) / 종합 판정
2. **[QUANTITATIVE METRICS & FINANCIAL BREAKDOWN]** (정량적 수치 분석 및 자금/원가 구조 테이블)
   - 항목별 추정 금액, 비중(%), 평당 단가, 민감도 분석 수치 등을 마크다운 테이블(`| 항목 | 금액 | 비중 | 비고 |`)로 반드시 상세히 시각화
3. **[ENGINEERING & TECHNICAL FEASIBILITY]** (부문별 공학적/구조적 검토 지표)
   - 용적률, 건폐율, 주차대수 산정, 하중 및 설계 가설계(Mass Study) 지표
4. **[RISK MATRIX & MITIGATION PROTOCOL]** (리스크 매트릭스)
   - 리스크 요인 / 발생 확률 (High/Med/Low) / 영향도 / 방어 조항 및 대응 프로토콜

업무 지시:
{TASK}
"""

    # 💡 530/503 트래픽 폭주(High Demand) 장애 대응용 자동 폴백 모델 순회 로직
    models_to_try = ['gemini-3.8-flash', 'gemini-2.5-flash', 'gemini-1.5-flash']
    response = None
    last_error = None

    for m in models_to_try:
        try:
            print(f"Trying model: {m}")
            response = client.models.generate_content(model=m, contents=prompt)
            if response and response.text:
                print(f"Success with model: {m}")
                break
        except Exception as e:
            print(f"Model {m} encountered an error: {e}")
            last_error = e
            continue

    if not response or not response.text:
        raise RuntimeError(f"모든 AI 모델 호출이 실패했습니다. (마지막 에러: {last_error})")

    report_text = response.text.strip()

    DOCS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    KST = timezone(timedelta(hours=9))
    today = datetime.now(KST).strftime("%Y-%m-%d")
    now_kst = datetime.now(KST).isoformat()

    report_filename = f"office-{today}.md"
    report_path = REPORTS / report_filename
    report_path.write_text(
        f"# [LACLEF EXECUTIVE QUANTITATIVE REPORT]\n\n"
        f"- **생성일시(KST):** {now_kst}\n"
        f"- **지시 사항:** {TASK}\n"
        f"- **분석 모드:** 엔지니어링 지표 및 KPI 스코어카드 통합 엔진\n\n"
        f"---\n\n{report_text}\n",
        encoding="utf-8",
    )

    status = {
        "updated_at": now_kst,
        "status": "completed",
        "latest_report": f"reports/{report_filename}",
        "task": TASK,
        "summary": report_text[:600] + "...",
        "full_report_content": report_text,
        "departments": [
            {"name": "기획실", "status": "정량 KPI 및 스코어카드 산출 완료"},
            {"name": "사업개발실", "status": "공학적 가설계 및 수지 테이블 연동 완료"},
            {"name": "마케팅실", "status": "시장 흡수율 및 민감도 분석 완료"},
            {"name": "재무·리스크실", "status": "리스크 매트릭스 및 방어 조항 검토 완료"}
        ]
    }

    status_path = DOCS / "office-status.json"
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")

    generate_dashboard_html()

    print(f"지표 중심의 엔지니어링 보고서 및 대시보드 갱신 완료")


if __name__ == "__main__":
    main()
