r"""빨라쪼(Palazzo Del Freddo) — 브랜드가 직접 켜고 끄는 **'신제품/신메뉴' 목록**.

공정위 `아이스크림/빙수`(K1) 가맹점 수 **15개**(2024년 말, 공정위 영업표지는
`빨라쪼 델 프레도`, 가맹본부 ㈜빨라쪼). 1880년 로마에서 시작한 이탈리아 젤라또
브랜드를 **해태제과가 들여와 운영**한다(사이트 푸터가 `haitai Confectionery &
Food. Co.LTD`). `brand_sub` 는 `아이스크림`(젤라또)이다.

⚠️ `collectors/maker_haitai.py`(해태제과식품 과자 보도자료)와 **겹치지 않는다.**
   저쪽은 제과 보도자료, 이쪽은 가맹 브랜드의 메뉴 공지다. 상품이 섞이지 않는다.
⚠️ 같은 ㈜빨라쪼 가 운영하는 **지파시(G.Fassi, 9개)** 는 별도 사이트
   `http://www.gfassi.com` 인데 **한 장짜리 소개 페이지**(14,911B)에 게시판도
   메뉴 목록도 없다(링크가 페이스북·인스타그램·영양성분 PDF 셋뿐) → 구조적 불가.

## 사이트가 해시뱅(`#!`) SPA 다 — HTML 만 받으면 빈 껍데기다

  GET http://www.ipalazzo.com/menu/            200 / 10,830B
    본문이 `'신제품/신메뉴'` 글자 하나뿐이다. 목록이 없다.
브라우저로 열어 `performance.getEntriesByType('resource')` 를 찍어 XHR 를 찾았다
(maker_shinsegaefood 가 쓴 그 방법). 하나뿐이다:

  GET http://www.ipalazzo.com/menu/ajax/new.aspx          200 / 9,436B
    <select name="menu_new_list">
      <option value="108" selected>리뉴얼 젤라또 프레도 출시!</option>
      <option value="107">2026 여름 음료 출시!</option>
      … (2026-10-03 실측 **93개**. 2015년쯤부터의 전체 아카이브다)
    <div class="menu-new-attach"><img src="/upload/20260624/빨라쪼 프레도 리뉴얼 포스터(작은파일).png">

  **상세는 `?idx=N`** 이다. `seq`·`no`·`id`·`code`·`num` 은 전부 무시되고
  최신(108)이 그대로 돌아온다 — **파라미터 이름을 틀리면 조용히 같은 글을
  93번 받게 된다.** `selected="selected"` 가 요청한 idx 로 바뀌는지로 확인한다.

## 날짜 — 첨부 그림의 **업로드 폴더명** `/upload/YYYYMMDD/`

목록에도 상세에도 날짜 칸이 없다. 대신 포스터 경로가 날짜 폴더다.
`released_at` 이 아니라 **`uploaded_at`** 에 넣는다(mega·농심과 같은 판단).

**일괄 업로드인가 — 아니다.** 최신 14건 실측(2026-10-03):
```
108 리뉴얼 젤라또 프레도 출시!   2026-06-24   ← '리뉴얼' 이라 버린다
107 2026 여름 음료 출시!        2026-06-16
106 2026 컵빙수 출시!           2026-05-27
105 베이커리 출시!              2026-05-27   ← 이름이 '베이커리' 라 버린다
104 쑥 음료 출시!               2026-05-12
103 거문도 해풍쑥 젤라또 출시!   2026-05-12
102 딸기 시즌 메뉴 출시!        2026-02-25
101 고르곤졸라 치즈 젤라또 출시! 2026-02-10
100 2025 크리스마스 케이크 출시! 2025-12-08
 99 델리 메뉴 출시!             2025-11-26
 98 유자 한라봉 젤라또 출시!     2025-11-26
 97 젤라또 보틀 케이크 출시!     2025-09-26
 96 프로바이오 요고라또 출시!    2025-09-04
 95 찰현미 젤라또 출시!         2025-08-27
```
13개월에 걸쳐 흩어져 있고 **idx 순서와 날짜 순서가 정확히 일치한다**(단조 감소).
컴포즈(149건이 하루)·롯데웰푸드(7개 날짜에 54건) 같은 일괄 재업로드 모양이
아니다. idx 가 날짜순이라 **오래된 게 나오면 거기서 멈춘다** — 93건을 다 받지 않는다.

## 제목 → 상품명 · **'시즌 라인업 공지' 는 상품이 아니다**

제목이 `<상품명> 출시!` 고정 꼴이라 꼬리를 떼면 된다. 따옴표가 없다.
그런데 **제목의 절반쯤은 상품 하나가 아니라 그 시즌 메뉴 묶음 공지**다.
처음에 꼬리만 떼고 다 넣었다가 아래 넷이 상품으로 올라갔다 — 전부 잘못이다:
```
2026 여름 음료 / 2026 컵빙수 / 딸기 시즌 메뉴 / 2025 크리스마스 케이크
```
카드에 '2026 여름 음료' 를 띄우면 눌러 본 사람이 "이게 무슨 상품이지" 가 된다.
이 레포 규칙이 "세트·이벤트 공지를 상품으로 넣지 마라" 다. 그래서 버린다:
  - `리뉴얼` — 기존 상품의 리뉴얼은 신상이 아니다(운영자 규칙).
  - 이벤트·프로모션·할인·안내·휴무 류.
  - **연도 접두** (`^20\d\d`) — `2026 여름 음료`·`2025 크리스마스 케이크`.
  - **일반명사로 끝나는 묶음 이름** (`…메뉴`·`…음료`·`…시즌`·`…라인업`·`…시리즈`)
    — `딸기 시즌 메뉴`·`델리 메뉴`·`쑥 음료`.
  - `N종` 이 든 제목 — 하나를 특정할 수 없다(오리온 `_MULTI` 와 같은 규칙).
  - **이름이 통째로 일반명사 한 덩어리**인 글(`베이커리`·`젤라또`·`디저트`).
    ⚠️ **부분일치로 거르지 마라** — `젤라또 보틀 케이크` 가 '케이크' 에 걸려
    사라진다. 이 레포가 `카스`→`카스테라` 28건으로 데인 그 함정이다.
    **접두는 정규식, 꼬리는 `endswith`, 일반명사는 완전일치**로만 본다.

### 묶음 공지 안의 개별 상품명은 **캐내지 않는다**

상세의 `.menu-new-content` 에 개별 상품이 적혀 있는 글도 있다. 그런데 꼴이
글마다 다르다(2026-10-03 실측):
```
idx 107 (2026 여름 음료)      content = ''        ← 아예 비어 있다. 포스터 그림뿐
idx 106 (2026 컵빙수)         content = ''        ← 비어 있다
idx 102 (딸기 시즌 메뉴)       '🍓 딸기 라떼\n입안 가득…\n🍵 딸기 그린티 라떼\n…'
                                                 ← 상품마다 앞에 이모지가 붙는다
idx 100 (2025 크리스마스 케이크) '🎄✨ 빨라쪼만의 … 🎄\n메리 초코 트리\n초콜라또…
                                 \n⛄️ 화이트 스노우 빌리지\n…'
                                                 ← 첫 상품엔 이모지가 **없다**
```
머리글에도 이모지가 붙고(`🍓 Strawberry Season in PALAZZO 🍓`), 상품 표시가
일관되지 않는다. 여기서 규칙을 세우면 머리글을 상품으로 만들거나 상품을
놓친다 — **지어내느니 버린다**(이 레포 원칙: "없으면 지어내지 말고 비워라").
빨라쪼가 상세를 정형화하면 그때 다시 본다.

## 쓸 수 있었지만 안 쓴 경로

  GET http://www.ipalazzo.com/notice/ajax/list.aspx  (새소식) 200 / 5,562B
    `<div class="date">2025-01-09</div>` 로 날짜가 깔끔한데 **최신 글이
    2025-01-09 다**(21개월 정지). 신제품 목록(2026-06)보다 훨씬 낡았다.
  GET http://www.ipalazzo.com/press/ajax/list.aspx   (보도자료) 200 / 5,924B
    최신 2025-11-24. 역시 신제품 목록보다 낡다. 같은 상품이 두 경로로
    들어오면 중복이 되므로 **한 경로만 쓴다**(더 최신인 신제품 목록).

## 사진 — **받지 않는다**

포스터는 `http://www.ipalazzo.com/upload/…png` 로 **https 가 없다.**
`https://www.ipalazzo.com/...` 와 `https://ipalazzo.com/...` 둘 다 IIS 404
(315B, `text/html; charset=us-ascii`)를 돌려준다. 같은 경로를 http 로 받으면
`200 / 830,983B / image/png` 다. `base.derive()` 가 http 이미지를 버리므로
애초에 담지 않는다. maker_samyang 과 같은 처지다.

robots: http://www.ipalazzo.com/robots.txt → **404**(1,238B 짜리 사이트 404 페이지).
        https 쪽은 IIS 404(315B). **robots 가 없다** = 허용도 금지도 아니다.
        그래서 간격을 넉넉히(2.5초) 두고 요청 수를 `MAX_DETAILS` 로 묶는다.
약관:   확인하지 않았다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "빨라쪼"
SITE = "http://www.ipalazzo.com"
MENU = SITE + "/menu/"
AJAX = SITE + "/menu/ajax/new.aspx"
DELAY = 2.5          # robots 가 없는 사이트다. 간격을 길게 잡는다.
DAYS = 300
MAX_DETAILS = 20     # idx 가 날짜순이라 보통 10건 안쪽에서 멈춘다. 폭주 방지 상한.

_TAIL = re.compile(r"\s*출시\s*[!！.]*\s*$")
_STAMP = re.compile(r"/upload/(\d{8})/")

# 상품 글이 아닌 것. 제목에 들어 있으면 버린다.
_SKIP = ("리뉴얼", "이벤트", "프로모션", "할인", "증정", "안내", "휴무", "공지",
         "가격", "인상", "채용", "모집", "가맹", "창업", "박람회", "수상",
         "기부", "협약", "당첨", "응모")
_MULTI = re.compile(r"\d+\s*종")          # 'N종' 은 하나를 특정 못 한다

# 시즌 라인업 공지. 연도로 시작하면 그 해 메뉴 묶음이다.
#   2026 여름 음료 · 2026 컵빙수 · 2025 크리스마스 케이크
_SEASON_HEAD = re.compile(r"^20\d{2}\b")
# 일반명사로 끝나면 상품 하나가 아니라 묶음이다. **꼬리(endswith)로만** 본다 —
# 부분일치로 바꾸면 '젤라또 보틀 케이크' 가 날아간다.
_BUNDLE_TAIL = ("메뉴", "음료", "시즌", "라인업", "시리즈", "세트", "컬렉션")

# ⚠️ **완전일치로만** 거른다(위와 같은 이유).
_GENERIC = {"베이커리", "음료", "메뉴", "신메뉴", "케이크", "젤라또",
            "디저트", "커피", "빙수", "라떼", "토핑"}


def _name(title: str) -> str:
    """제목 → 상품명. 묶음 공지면 빈 문자열(= 버린다)."""
    t = " ".join(title.split())
    if any(w in t for w in _SKIP) or _MULTI.search(t):
        return ""
    nm = _TAIL.sub("", t).strip(" !！.·")
    if len(nm) < 2 or nm in _GENERIC:
        return ""
    if _SEASON_HEAD.match(nm):
        return ""                      # '2026 여름 음료' 같은 시즌 묶음
    if nm.endswith(_BUNDLE_TAIL):
        return ""                      # '딸기 시즌 메뉴'·'쑥 음료'·'델리 메뉴'
    return nm


def _uploaded(html: str) -> str:
    """첨부 그림 경로의 `/upload/YYYYMMDD/` → 'YYYY-MM-DD'."""
    m = _STAMP.search(html or "")
    if not m:
        return ""
    s = m.group(1)
    y, mo, d = int(s[:4]), int(s[4:6]), int(s[6:])
    if not (2010 <= y <= date.today().year + 1 and 1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    items: list[Item] = []
    seen = set()
    with base.client(headers={"Referer": MENU}) as c:
        r = base.retry(lambda: c.get(AJAX))
        r.raise_for_status()
        opts = [(o.attributes.get("value") or "", " ".join(o.text().split()))
                for o in HTMLParser(r.text).css("select[name=menu_new_list] option")]
        opts = [(v, t) for v, t in opts if v.isdigit() and t]

        # 목록이 통째로 안 읽히면 ajax 응답 꼴이 바뀐 것이다. 조용히 넘기지 않는다.
        if not opts:
            raise ValueError(
                f"빨라쪼 신제품 목록이 비었다. {AJAX} → {len(r.content)}B — "
                f"select[name=menu_new_list] option 구조가 바뀌었는지 확인하라")

        # idx 내림차순 = 최신순. 오래된 게 나오면 거기서 멈춘다.
        opts.sort(key=lambda p: int(p[0]), reverse=True)
        stale = fetched = 0
        for idx, title in opts[:MAX_DETAILS]:
            time.sleep(DELAY)
            rr = base.retry(lambda idx=idx: c.get(AJAX, params={"idx": idx}))
            rr.raise_for_status()
            fetched += 1
            # ⚠️ 파라미터 이름이 틀리면 서버가 최신 글을 그대로 돌려준다.
            #    요청한 idx 가 선택돼 있는지로 확인한다.
            sel = HTMLParser(rr.text).css_first(
                "select[name=menu_new_list] option[selected]")
            got = (sel.attributes.get("value") or "") if sel else ""
            if got and got != idx:
                raise ValueError(
                    f"빨라쪼 상세가 idx={idx} 를 무시하고 idx={got} 를 돌려줬다. "
                    f"쿼리 파라미터 이름(`idx`)이 바뀌었는지 확인하라 — "
                    f"그대로 두면 같은 글을 {len(opts)}번 받는다")
            up = _uploaded(rr.text)
            if not up:
                continue                 # 포스터가 없는 옛 글. 날짜를 지어내지 않는다
            if up < floor:
                stale += 1
                break                    # idx 순 = 날짜순이라 여기부터는 다 옛글
            nm = _name(title)
            if not nm:
                continue
            it = Item(
                brand=BRAND,
                name=nm,
                desc=" ".join(title.split()),
                # 포스터가 http 전용이라 담지 않는다(docstring §사진).
                image="",
                uploaded_at=up,
                # 브랜드가 직접 관리하는 '신제품/신메뉴' 목록이다.
                is_new=True,
                url=f"{MENU}#!new/{idx}",
            )
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)

        # 받아본 글 전부에서 날짜를 못 읽었다면 `/upload/YYYYMMDD/` 꼴이
        # 바뀐 것이다. 그러면 전건이 조용히 사라진다 — 터뜨린다.
        if fetched and not items and not stale:
            raise ValueError(
                f"빨라쪼 신제품 {fetched}건에서 날짜를 하나도 못 읽었다. "
                f"포스터 경로의 `/upload/YYYYMMDD/` 꼴이 바뀌었는지 확인하라")
    return items
