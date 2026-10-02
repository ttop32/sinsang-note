"""에밀리아젤라또 — 공지사항의 **`[신메뉴]` 글**에서 상품명과 출시일을 뽑는다.

공정위 `아이스크림/빙수`(K1) 가맹점 수 **16개**(2024년 말, 공정위 표기는
`에밀리아(emilia)`, 가맹본부 에밀리아코리아(주)). 이탈리아 볼로냐산 젤라또
완제품을 직수입해 파는 브랜드라 `brand_sub` 는 `아이스크림` 이다.

가맹점 수는 16개로 작지만 **신제품 신호가 이 업종에서 가장 깨끗하다** —
공지 제목이 `[신메뉴] "<상품명>" … 출시 안내` 라는 고정 꼴이고 날짜가 완전하다.
"작은 프랜차이즈는 자체 웹이 없다"는 통념의 반례라 표에 남겨 둘 값이 있다.

## 두 경로를 다 열어 보고 공지 쪽을 골랐다

  GET https://www.emiliagelato.co.kr/19  (메뉴·젤라또)  200 / 345,372B
    돌체바닐라·딸기·초콜릿·레몬·헤이즐넛… **상시 20여 가지 맛 카탈로그**다.
    NEW 배지도 등록일도 없다 → 전부 신상으로 넣을 수 없다. 안 쓴다.
  GET https://www.emiliagelato.co.kr/29  (에밀리아소식·공지사항)  200 / 310,564B
    ← **쓰는 경로.** 완전 SSR 이다.

## 마크업 (2026-10-02 실측)

    <table class="board-table-1" data-pagesize="10" data-bid="tzdlrf">
      <tbody class="board-tbody">
        <tr class="board-tbody-tr" id="QJqgB4" data-type="nm">
          <td class="board-tbody-item-count">28</td>
          <td class="board-tbody-item-title">
              <div>[신메뉴] "피스타치오 카다이프 스프레드" 토핑 출시 안내</div></td>
          <td class="board-tbody-item-date">2026-03-02</td>
        </tr>
  선택자: `table.board-table-1 tbody.board-tbody tr` →
          `.board-tbody-item-title div`(제목) · `.board-tbody-item-date`(날짜).
  날짜는 `YYYY-MM-DD` 로 완전하다. **상세 링크가 없다** — 본문은
  `data-toggle="modal"` 자바스크립트 모달이라 글마다 URL 이 없다.
  그래서 `Item.url` 은 목록 URL 로 두고, **사진은 받지 않는다**
  (목록에 썸네일이 없고 모달 본문은 JS 전용이다. maker_samyang 과 같은 처지다).
  페이지는 1·2·3 세 장인데 1장(10건)이 2025-03 ~ 2026-06 을 덮어서 1장만 받는다.

## 제목 → 상품명

상품명은 **큰따옴표** 안에 있다. 한 글에 두 개가 들어오는 경우가 실재한다
(`신메뉴 젤라또 "바닐라&쿠키", "바닐라&비스킷" 출시 안내` → 2건).
따옴표가 없으면 **버린다** — `[신메뉴] 새로운 맛 2가지 출시 안내` 처럼
무엇이 나왔는지 제목만으로 특정할 수 없는 글이 있고, 거기서 지어내면 안 된다.

⚠️ 오리온 `_pick` 은 상품명에 `&` 가 있으면 버리는데(홍보 문구 오인 방지)
   **여기서는 `&` 가 진짜 상품명의 일부다**(`바닐라&쿠키`). 그 규칙을 그대로
   옮겨 왔다가 2건이 조용히 사라진다. 이 어댑터는 `&` 를 허용한다.

## 실측 — 공지 10건 중 신메뉴 글 6건(60%), 뽑힌 상품 6건

```
30  [박람회] 2026년 창업 박람회 참가 (세택)                2026-06-15  ← 버림
29  [박람회] 2026 창업 박람회 참가 안내                    2026-04-22  ← 버림
28  [신메뉴] "피스타치오 카다이프 스프레드" 토핑 출시 안내     2026-03-02  ✔
27  [신메뉴] "바닐라체리" 맛 출시 안내                      2026-02-23  ✔
26  [신메뉴] 토핑 "미니 와플 콘" 안내                       2026-02-19  ✔
25  [신메뉴] 새로운 맛 2가지 출시 안내                      2025-10-01  ← 따옴표 없음
24  신메뉴 젤라또 "바닐라&쿠키", "바닐라&비스킷" 출시 안내     2025-08-05  ✔✔
23  신메뉴 젤라또 "스트라치아텔라" "바닐라&망고칩" 출시 안내    2025-06-07  ✔✔
22  2025 카페&베이커리페어 참가 안내                       2025-05-20  ← 버림
21  젤라또 콘 출시 안내                                   2025-03-08  ← 따옴표 없음
```
**날짜가 10건 모두 다른 날이다.** 일괄 등록 흔적이 없다(컴포즈 149건이 하루에
몰린 것과 반대 모양). 가장 최근 신메뉴가 2026-03-02 이라 화면의 신상 창(60일)
에는 지금 당장 오르지 않는다 — 그래도 `released_at` 이 정확해서 넣을 값이 있다.

'신메뉴' 표시가 10건 중 0건이 되면 제목 꼴이 바뀐 것이므로 `fetch()` 끝에서
터뜨린다(100% 가 되는 쪽도 막는다 — 그건 공지 전체가 신메뉴로 뒤집힌 것이다).

robots: https://www.emiliagelato.co.kr/robots.txt → 200 / 318B.
        `User-agent: *` 하나뿐이고 `Disallow:` 가 `/module/site/`·`/module/form/`·
        `/module/member/`·`/oauth/`·`/policy_*`·`/mypage`·`/join`·`/login`·
        `/order`·`/cart`·**`/13`**·**`/15`** 다. 우리가 받는 **`/29` 는 금지
        목록에 없다 = 명시적으로 허용**이다. `Crawl-delay` 선언 없음.
약관:   확인하지 않았다.
"""
import re

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "에밀리아젤라또"
SITE = "https://www.emiliagelato.co.kr"
LIST = SITE + "/29"          # 에밀리아소식(공지사항)
DELAY = 2.2
MAX_PAGES = 1                # 1장(10건)이 2025-03 ~ 2026-06 을 덮는다

# 신메뉴 글 표시. `[신메뉴] …` 과 접두 없는 `신메뉴 젤라또 …` 둘 다 실재한다.
_NEWMARK = re.compile(r"\[?\s*신메뉴\s*\]?")
# 상품명은 큰따옴표 안. 스마트 따옴표(“ ”)도 받는다.
_QUOTED = re.compile(r"[\"“]([^\"”]{2,40})[\"”]")
# 상품 글이 아닌 것. 박람회·페어·창업설명회 등.
_SKIP = ("박람회", "페어", "창업", "모집", "채용", "휴무", "공사", "가격",
         "인상", "이벤트", "행사", "할인", "리뉴얼", "수상", "협약", "기부")


def _date(s: str) -> str:
    m = re.search(r"(20\d{2})[-.](\d{1,2})[-.](\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _names(title: str) -> list[str]:
    """제목에서 큰따옴표 안의 상품명을 전부 뽑는다. 없으면 빈 리스트."""
    t = " ".join(title.split())
    if not _NEWMARK.search(t) or any(w in t for w in _SKIP):
        return []
    out = []
    for m in _QUOTED.finditer(t):
        # ⚠️ '&' 를 거르지 마라. '바닐라&쿠키' 가 진짜 상품명이다.
        nm = m.group(1).strip(" ,·∙")
        if len(nm) >= 2 and nm not in out:
            out.append(nm)
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    rows_n = marked_n = 0
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()
        rows = HTMLParser(r.text).css(
            "table.board-table-1 tbody.board-tbody tr")

        if not rows:
            raise ValueError(
                f"에밀리아 공지 목록이 비었다. {r.url} → {len(r.content)}B — "
                f"선택자(table.board-table-1 tbody.board-tbody tr)가 "
                f"바뀌었는지 확인하라")

        for tr in rows:
            tt = tr.css_first(".board-tbody-item-title")
            dt = tr.css_first(".board-tbody-item-date")
            if not tt:
                continue
            rows_n += 1
            title = " ".join(tt.text().split())
            released = _date(dt.text() if dt else "")
            if _NEWMARK.search(title):
                marked_n += 1
            for name in _names(title):
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=title,
                    released_at=released,
                    # 브랜드가 '[신메뉴]' 라고 직접 붙인 글이다.
                    is_new=True,
                    url=LIST,      # 글마다 URL 이 없다(모달). 목록으로 떨어뜨린다
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

    # ── 신호 비율 가드 ────────────────────────────────────────────────
    # 신호는 '있다'가 아니라 '전체의 몇 %냐'로 믿는다. 2026-10-02 실측
    # 10건 중 6건(60%)이 신메뉴 글이다. 0% 면 제목 꼴이 바뀐 것이고,
    # 100% 면 공지 전체가 신메뉴로 뒤집혀 신호 구실을 못 하는 것이다.
    if rows_n and marked_n == 0:
        raise ValueError(
            f"에밀리아 공지 {rows_n}건 중 '신메뉴' 글이 0건이다. 제목 꼴"
            f"('[신메뉴] \"상품명\" … 출시 안내')이 바뀌었는지 확인하라")
    if rows_n >= 5 and marked_n == rows_n:
        raise ValueError(
            f"에밀리아 공지 {rows_n}건이 **전부** '신메뉴' 글이다. 그러면 신호가"
            f" 아니라 장식이다 — 게시판이 바뀌었는지 확인하라"
            f"(퀴즈노스 선례: NEW 가 66건 전부)")
    return items
