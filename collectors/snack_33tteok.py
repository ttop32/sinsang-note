"""33떡볶이&꼬마김밥.

(주)성백F&S(860-81-02199, 이호성 / 본사 강원 홍천) 운영. 공정위 업종이 `분식`이
아니라 **`기타 외식`** 이라 분식 TOP30 에는 안 나온다 — 183개점(2024년 말)으로
떡볶이 축 7위다. `CANDIDATES-SNACK2.md` 가 "도메인 미특정"으로 남겨 둔 건이다.

## 도메인이 둘인데 **하나는 창업 랜딩이다**

| 도메인 | 정체 | 바이트 |
|---|---|---:|
| **`33success100.co.kr`** | ✅ 브랜드 사이트(gnuboard). 메뉴·커뮤니티·미디어 | 30KB |
| `success100.co.kr` | ❌ 창업 모집 랜딩 한 장(Cloudflare). 내비가 전부 `#con02` 앵커 | 787KB |
| `33떡볶이꼬마김밥.com` | 브랜드 사이트로 연결(푸터 링크) | — |

둘 다 `<title>` 에 `33떡볶이꼬마김밥` 이 들어 있어서 제목만 보면 못 가른다
(용우동 §5-2 의 변종이다). **내비를 보면 갈린다** — 랜딩 쪽은 내비 전체가
`#con02`·`#con03` 같은 한 장짜리 앵커고, 상품 목록이 없다.

robots.txt: **200 / 21바이트 / `User-agent:* / Allow: /`**. 전부 https, SSR, UTF-8.
이용약관은 푸터에 없다(개인정보처리방침만). **"약관을 확인하지 못했다"** 상태다.

## ⚠️ 이 사이트는 **아직 덜 채워져 있다 — `test` 더미 글이 살아 있다**

- 공지사항 2건이 전부 제목 `test`(작성일 `25-09-19`)
- 이벤트 1건이 `이벤트 제목 test`
- FAQ 1건이 `질문 test / 답변 test`
- **미디어(33일보) 2건 중 1건이 `언론사 test / 제목 test / 날짜 test`**

개인정보처리방침 시행일이 2024-12-24 이니 새로 만든 사이트다. 태리로제(같은
제작사 VWEB)에는 `{{시행일}}` 치환자가 그대로 남아 있었다. **같은 제작사
사이트를 만나면 더미와 치환자를 먼저 의심해라.** 아래 필터가 그걸 거른다.

## 두 소스를 합친다 — 메뉴에서 상품, 33일보에서 신상 판정

**① 메뉴 — `/bbs/content.php?co_id=menu` 한 장(53KB)에 5개 탭이 전부 들어 있다.**
삼첩분식과 같은 구조다(탭 버튼 수 = 상품묶음 수).

    <div class="ccon02_btnwrap"><p class="ccon02_btn">떡볶이</p> … </div>
    <div class="ccon02_con on">
      <div class="ccon02_con_box" data-name="국물떡볶이"
           data-content="진한 특제 소스와 쫄깃한 밀떡, 부드러운 어묵이…"
           data-photo="https://33success100.co.kr/data/file/main_menu/….png">

2026-10-02 실측 **떡볶이 6 · 꼬마김밥 6 · 식사류 7 · 사이드 3 · 세트메뉴 5 = 27건.**

## ⭐ 메뉴에는 배지가 **0/27** 이다. 신상 신호는 보도자료에만 있다

메뉴 페이지 원본에 `NEW`·`new`·`신메뉴`·`신상`·`BEST` 가 **전부 0건**이다
(주석 안에도 없다). 상품 카드에 배지 슬롯 자체가 없다. 싸다김밥처럼 그림 안에
글자가 합성돼 있는 것도 아니다 — `data-photo` 는 상품 사진 한 장뿐이다.

**② 33일보(`co_id=media`) — 유효한 보도자료가 딱 1건 있다.**

    <p class="econ02_con_tt01">신아일보</p>
    <p class="econ02_con_tt02">33떡볶이&꼬마김밥, '김치볶음밥·새우볶음밥·제육덮밥'
                               식사류 신메뉴 3종 출시</p>
    <p class="econ02_con_tt03">1주전</p>

**전체 2건 중 1건이 `test` 더미**라 실제 유효 보도자료는 1건이다.

### 제목의 **따옴표 안**에서만 상품명을 꺼낸다

제목이 `'김치볶음밥·새우볶음밥·제육덮밥'` 처럼 **상품명을 작은따옴표로 묶고
가운뎃점으로 나열**한다. 그래서 따옴표 구간을 꺼내 `·` 로 쪼갠 뒤
**메뉴의 상품명과 정확히 같을 때만** `is_new` 를 올린다. 삼첩분식에서 쓴
'이름 일치' 방어와 같다 — 느슨하게 맞추면 `식사류 신메뉴 3종` 같은 꾸밈말이
상품에 붙는다.

2026-10-02 실측 결과 **3개 중 1개(`제육덮밥`)만 메뉴에 있다.** 나머지 둘
(`김치볶음밥`·`새우볶음밥`)은 **아직 메뉴 페이지에 안 올라와 있다.** 없는 것을
억지로 만들어 넣지 않는다 — 올라오는 날 자동으로 붙는다.

### ⚠️ 날짜를 못 쓴다 — `1주전` 이다

`econ02_con_tt03` 이 상대 날짜(`1주전`)다. 같은 사이트의 공지 게시판은
`25-09-19` 꼴 절대 날짜를 쓰는데, 이 섹션은 최근 글을 상대 표기로 낸다.
"1주전"을 오늘 기준으로 역산해서 넣으면 **매일 실행할 때마다 값이 달라진다.**
그래서 **절대 날짜가 보일 때만 받고 아니면 비운다**(`YY-MM-DD`·`YYYY-MM-DD` 둘 다 허용).
이미지 경로(`/data/file/main_menu/<해시>…`)에도 날짜가 없다.

상품별 주소는 **없다.** 카드가 `data-*` 를 들고 있는 JS 슬라이드라 href 가 없다.
`url` 을 비워 `base.SITES` 폴백에 맡긴다. 가격은 사이트에 없다. 전부 https 다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "33떡볶이"
ROOT = "https://33success100.co.kr"
CONTENT = ROOT + "/bbs/content.php"
DELAY = 2.5

# 두 소스의 이름을 맞추는 키. 공백과 꾸밈말을 턴다(삼첩분식과 같은 규칙).
_NOISE = re.compile(r"신메뉴|출시|\s+")
# 제목의 따옴표 구간. 한글 사이트라 홑따옴표가 전각('…')으로 들어온다.
_QUOTED = re.compile(r"[‘'\"“]([^’'\"”]{2,80})[’'\"”]")
# 절대 날짜만 받는다. '1주전' 같은 상대 표기는 버린다(위 docstring 참고).
_DATE = re.compile(r"(?:(20)?(\d{2}))[-.](\d{2})[-.](\d{2})")
# 더미 글. 사이트가 아직 덜 채워져 있다(위 docstring 참고).
_DUMMY = ("test", "TEST")
# 출시 글이 아닌 것. 이름 일치가 1차 방어고 이건 두 번째 그물이다.
_EVENT = ("이벤트", "할인", "증정", "기념", "당첨", "박람회", "오픈", "호점")


def _norm(name: str) -> str:
    return _NOISE.sub("", name or "")


def _press(c) -> tuple[set, dict]:
    """33일보 → (신상으로 볼 정규화 이름 집합, {이름: 날짜}).

    제목의 따옴표 안을 `·` 로 쪼갠 것만 상품명으로 본다. 날짜는 절대 표기일
    때만 채운다.
    """
    r = base.retry(lambda: c.get(CONTENT, params={"co_id": "media"}))
    r.raise_for_status()
    time.sleep(DELAY)

    names, dates = set(), {}
    for box in HTMLParser(r.text).css(".econ02_con_box"):
        tit = box.css_first(".econ02_con_tt02")
        if not tit:
            continue
        title = " ".join(tit.text().split())
        if not title or any(d in title for d in _DUMMY):
            continue                       # test 더미
        if "신메뉴" not in title and "출시" not in title:
            continue
        if any(w in title for w in _EVENT):
            continue

        dat = box.css_first(".econ02_con_tt03")
        raw = " ".join(dat.text().split()) if dat else ""
        m = _DATE.search(raw) if raw and not any(d in raw for d in _DUMMY) else None
        day = f"{m.group(1) or '20'}{m.group(2)}-{m.group(3)}-{m.group(4)}" if m else ""

        for q in _QUOTED.findall(title):
            for part in q.split("·"):
                key = _norm(part)
                if not key:
                    continue
                names.add(key)
                if day:
                    dates[key] = day
    return names, dates


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        new_names, dates = _press(c)

        r = base.retry(lambda: c.get(CONTENT, params={"co_id": "menu"}))
        r.raise_for_status()
        time.sleep(DELAY)

    doc = HTMLParser(r.text)
    tabs = [" ".join(b.text().split()) for b in doc.css(".ccon02_btnwrap .ccon02_btn")]
    groups = doc.css(".ccon02_con")
    if not groups or len(tabs) != len(groups):
        # 탭과 묶음이 안 맞으면 어느 묶음이 어느 분류인지 알 수 없다.
        # 조용히 넘기지 않는다(삼첩분식과 같은 처분).
        raise ValueError(f"{BRAND}: 탭 {len(tabs)}개 ≠ 상품묶음 {len(groups)}개")

    for i, group in enumerate(groups):
        for box in group.css(".ccon02_con_box"):
            a = box.attributes
            name = " ".join((a.get("data-name") or "").split())
            if not name:
                continue
            key = _norm(name)
            it = Item(
                brand=BRAND,
                name=name,
                desc=" ".join((a.get("data-content") or "").split()),
                image=a.get("data-photo", ""),
                category=tabs[i],
                # 보도자료가 절대 날짜를 줄 때만 찬다. '1주전' 은 안 쓴다.
                released_at=dates.get(key, ""),
                # 보도자료 따옴표 안에 이름이 있는 상품만 True.
                # 없음은 '아니다'가 아니라 '모른다'다.
                is_new=True if key in new_names else None,
                # 상품별 주소가 없다(JS 슬라이드).
                url="",
            )
            if it.key in keys:
                continue
            keys.add(it.key)
            items.append(it)

    # 이 브랜드의 신호는 보도자료 1건뿐이다. 그 섹션이 갈리거나 더미만 남으면
    # 건수는 27 그대로라 collect 의 0건·급감 가드에 안 걸린다. 로그에 남긴다.
    if items and not any(i.is_new for i in items):
        print(f"[{BRAND}] 보도자료에서 신상으로 짚어낸 상품이 0건이다 — "
              f"33일보 섹션 구조나 제목 표기를 확인해야 한다")
    return items
