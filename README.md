# 가사 일과

작사 실력을 기르기 위한 매일 루틴 페이지입니다. 매일 아침 새로 고른 한국어 노래 네 곡(아침 2 · 밤 2), 운율이 좋은 시 두 편, 작사 팁 하나가 올라옵니다.

- 노래: 인디, 포크, 발라드, R&B, 시티팝, 7080·90 가요, OST 등 장르를 섞어서 고릅니다. 가사가 지나치게 빽빽한 힙합과 가사가 거의 없는 일렉트로닉은 뺍니다. 가사 전문은 저작권 때문에 싣지 않고 유튜브와 네이버 가사 검색으로 연결합니다.
- 시: 저작권이 끝난 작품(1929년 이전 발표작, 고시조)은 전문을 싣고, 현대시는 전문을 볼 수 있는 곳으로 연결합니다.
- 오늘 이후의 목록은 보이지 않고, 지난 날짜는 위쪽 '지난 날'에서 다시 볼 수 있습니다.

## 구조

| 파일 | 역할 |
| --- | --- |
| `index.html` | 페이지. `data/days.json`을 읽어 그리는 정적 페이지 |
| `data/days.json` | 날짜별 목록. `{"days": [...]}` |
| `manifest.webmanifest`, `icon*` | 폰 홈 화면에 앱처럼 추가할 때 쓰는 정보 |
| `scripts/generate.py` | (선택) Anthropic API로 오늘 목록을 만드는 스크립트 |
| `.github/workflows/daily.yml` | (선택) 위 스크립트를 매일 06:40(KST)에 돌리는 예비 작업 |

## 매일 목록이 올라오는 방식

1. 기본: Claude 예약 작업이 매일 06:00(KST)쯤 곡과 시를 찾아 `data/days.json`에 추가하고 커밋합니다.
2. 예비(선택): 저장소 **Settings → Secrets and variables → Actions**에 `ANTHROPIC_API_KEY`를 넣으면, 06:40에 그날 목록이 아직 없을 때만 GitHub Actions가 대신 만듭니다. API 사용료가 나갑니다. 키가 없으면 이 작업은 아무것도 하지 않습니다.

## 데이터 형식

```json
{
  "date": "2026-09-23",
  "morning": [{"title": "", "artist": "", "genre": "", "why": "", "task": "", "youtube": "(선택)", "lyrics": "(선택)"}],
  "night":   [...],
  "poems":   [{"era": "classic|modern", "title": "", "poet": "", "source": "", "text": "(classic만)", "note": "", "links": [{"label": "", "url": ""}]}],
  "tip":     {"h": "", "p": "", "x": ""}
}
```
