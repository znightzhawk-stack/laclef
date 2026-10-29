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
.empty { color: var(--muted); font-size
