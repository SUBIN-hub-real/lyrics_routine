"""가사 일과 — 오늘의 목록을 만들어 data/days.json 에 추가한다.

GitHub Actions(.github/workflows/daily.yml)에서 ANTHROPIC_API_KEY 가 있을 때만 돈다.
오늘 날짜(한국 시간)의 항목이 이미 있으면 아무것도 하지 않는다.
"""
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import anthropic

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "days.json"
MODEL = os.environ.get("GASA_MODEL", "claude-sonnet-5")

PROMPT = """당신은 작사 공부 루틴 페이지 '가사 일과'의 {today} 목록을 만듭니다.
사용자는 가사 쓰는 능력을 기르려고 매일 이 목록을 봅니다. 확인하지 못한 사실은 쓰지 마세요.

이미 나온 것(다시 쓰지 말 것):
- 곡: {used_songs}
- 시: {used_poems}
- 팁 제목: {used_tips}

## 곡 (아침 2, 밤 2)
- 웹 검색으로 찾아서 고르세요. 가사가 좋은 한국어 곡. 장르를 넓게(인디 록/포크/모던록, 싱어송라이터, 발라드, R&B/소울, 시티팝, 밴드, 7080·90 가요, OST, 재즈 보컬, 국악 크로스오버, 가사 평이 좋은 아이돌 곡, 최근 1~2년 인디 신곡 등). 네 곡의 장르와 시대가 겹치지 않게, 적어도 한 곡은 인디 씬 곡.
- 제외: 가사가 지나치게 빽빽한 랩 중심 힙합, 가사가 거의 없는 일렉트로닉.
- 아침은 밝거나 담백한 곡, 밤은 차분하거나 깊은 곡.
- 가수와 제목이 실제로 맞는지 검색으로 확인한 곡만.
- 가사는 한 줄도 인용하지 마세요. why(가사에서 배울 점, 1~2문장)와 task(들으며 할 일, 1문장)를 본인 말로.

## 시 (2편)
- 보통 1편은 현대시(1950년대 이후 시인, 폭넓게), 1편은 저작권이 끝난 작품(1929년 이전 발표 한국 시 또는 고시조·고려가요).
- 현대시: text 를 넣지 마세요(인용 금지). links 에 {{"label":"네이버에서 전문 찾기","url":"https://search.naver.com/search.naver?query=<시인 제목 전문 URL인코딩>"}} 와 검색으로 확인한 수록 시집의 출판사·서점 페이지. source 에는 확인한 시집·연도만.
- 저작권 만료 작품: text 에 전문(현대어 표기, 줄바꿈 \\n). 확실히 아는 작품만. links 는 [].
- note: 운율·반복·행갈이·소리에서 작사가가 배울 점, 1~2문장.
- era: "modern" 또는 "classic".

## 팁 1개
tip: {{"h": 제목, "p": 설명 2~3문장, "x": 오늘의 연습 1~2문장}}. 가능하면 오늘의 곡·시와 연결.

## 출력
마지막에 아래 형태의 JSON 하나만 ```json 코드 블록으로 출력하세요.
{{"date":"{today}","morning":[{{"title":"","artist":"","genre":"","why":"","task":""}},{{...}}],"night":[{{...}},{{...}}],"poems":[{{"era":"","title":"","poet":"","source":"","text":"","note":"","links":[]}},{{...}}],"tip":{{"h":"","p":"","x":""}}}}
"""


def main() -> int:
    now = dt.datetime.now(ZoneInfo("Asia/Seoul"))
    today = now.date().isoformat()
    data = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else {"days": []}
    days = data.get("days", [])
    if any(d.get("date") == today for d in days):
        print(f"{today} 항목이 이미 있어요. 건너뜁니다.")
        return 0

    used_songs = ", ".join(f"{s['artist']} - {s['title']}" for d in days for s in d.get("morning", []) + d.get("night", [])) or "없음"
    used_poems = ", ".join(f"{p['poet']} - {p['title']}" for d in days for p in d.get("poems", [])) or "없음"
    used_tips = ", ".join(d.get("tip", {}).get("h", "") for d in days) or "없음"

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 12}],
        messages=[{"role": "user", "content": PROMPT.format(
            today=today, used_songs=used_songs, used_poems=used_poems, used_tips=used_tips)}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    m = re.findall(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    if not m:
        print("모델 응답에서 JSON을 찾지 못했어요:\n" + text[-2000:], file=sys.stderr)
        return 1
    entry = json.loads(m[-1])
    entry["date"] = today
    entry["created_at"] = now.isoformat(timespec="seconds")
    for p in entry.get("poems", []):
        if p.get("era") == "modern":
            p.pop("text", None)
    assert len(entry.get("morning", [])) == 2 and len(entry.get("night", [])) == 2, "곡 개수가 맞지 않아요"
    assert len(entry.get("poems", [])) == 2, "시 개수가 맞지 않아요"

    days.append(entry)
    data["days"] = days
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    songs = [f"{s['title']}({s['artist']})" for s in entry["morning"] + entry["night"]]
    print(f"{today} 추가: " + ", ".join(songs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
