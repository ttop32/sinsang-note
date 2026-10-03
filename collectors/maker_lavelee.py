r"""라벨리(Lavelee) — 빙과 전업 제조사. 언론보도 게시판의 '출시' 기사를 읽는다.

**아이스크림 제조사 축**이다(프랜차이즈가 아니다). 국내 빙과 시장은
롯데웰푸드(39.8%)·빙그레(28.1%)·해태아이스크림(14.6%) 셋이 83%를 먹고,
그 아래 **빙과 전업사는 (주)서주와 (주)라벨리 둘뿐**이다.
라벨리 총매출 **365.7억**(사람인 기업정보). 전남 화순 본사, 1996년 설립.
군납·PB 생산이 큰 회사라 자사 브랜드 신제품은 많지 않다.
`brand_sub` 는 `아이스크림`.

⚠️ 같은 축의 (주)서주(총매출 584.8억, `seoju.kr`)는 **구조적 불가**다 —
   제품 페이지가 180개 가까이 있는데 등록일도 NEW 배지도 없고(`/bar1`·`/cone1`
   같은 고정 슬러그), 공지사항(`/notice`·`/companynotice`)은 "게시물이 없습니다".

## ⚠️ 지금 이 어댑터는 **0건을 돌려준다. 그게 맞다.**

언론보도 게시판이 **전체 4건**이고 그중 상품 기사는 **1건(2025-01-06)** 이다.
`DAYS=400` 창 밖이라 오늘 기준 0건이다. `collectors/theborn.py` 가 보도자료
없는 브랜드에 0건을 돌려주는 것과 같다 — '고장' 으로 읽지 마라.
게시판 자체가 안 읽히면 그건 따로 `raise` 한다(아래 가드).

## 두 게시판을 다 열어 보고 '언론보도' 를 골랐다

  GET https://lavelee.co.kr/news/            (라벨리 News) 200 / 75,450B
    전체 7건. 전부 **행사·영상 소개**다 — '몽골 라벨리 홍보행사'(2025/05/29),
    '떠먹는요거트볼 일본방송 영상'(2025/01/16), '…생산과정'(2021/06/25 ×4).
    상품 출시 글이 **0건**이라 안 쓴다.
  GET https://lavelee.co.kr/media-coverage/  (언론보도)   200 / 76,838B  ← **쓰는 경로**
    전체 4건:
```
2026/04/10  광주상의, 지역 기업에 라벨리 빙과류 간식 지원       ← 상품 아님
2025/01/06  라벨리 아이스크림, 일본 세븐일레븐에서 선보여        ← 수출 소식
2025/01/06  “즐겨먹던 콘칩과자를 아이스크림으로” 라벨리
            ‘빅 아이스 콘칩’ 출시                            ✔ 유일한 상품
2025/01/06  라벨리 팥빙수                                   ← 제목에 동사가 없다
```
    게시판은 **살아 있다**(최신 글 2026-04-10). 상품 기사만 뜸하다.

## 마크업 — 워드프레스 KBoard 갤러리 스킨. 완전 SSR

    <div class="kboard-gallery-item">
      <a href="/media-coverage/?uid=1506246056&mod=document&pageid=1">
        <div class="kboard-gallery-thumbnail">
          <img src="https://lavelee.co.kr/wp-content/uploads/kboard_thumbnails/
                    11/202501/677b28859cb418158849-220x155.jpg">
          <div class="kboard-gallery-username">2025/01/06 by. laveleeadmin</div>
        </div>
        <div class="kboard-gallery-title">“즐겨먹던 콘칩과자를 …” 라벨리
            ‘빅 아이스 콘칩’ 출시</div>
      </a></div>
  선택자: `.kboard-gallery-item` → `.kboard-gallery-title`(제목) ·
          `.kboard-gallery-username`(`YYYY/MM/DD by. …`) · `img`(썸네일) · `a`(링크).
  ⚠️ 날짜 칸 클래스 이름이 `username` 이다. **작성자 칸이 아니라 날짜 칸**이다
     (스킨이 둘을 한 줄에 합쳐 놨다). 이름만 보고 건너뛰면 날짜를 통째로 놓친다.
  목록 날짜가 `YYYY/MM/DD` 로 완전해서 **상세를 받지 않는다**(요청 1회).

  사진은 **https 절대 URL** 이라 그대로 쓴다. 다만 썸네일이 220×155 로 작아서
  파일명의 `-220x155` 를 떼면 원본이 나온다(실측: 썸네일 11,370B → 원본 53,949B,
  둘 다 200 / image/jpeg). 원본을 쓴다.

## 제목 → 상품명

오리온 `_pick` 계보다. `“…”` 홍보 헤드라인을 지우고, 마지막 `출시` 앞의
`‘…’` 작은따옴표 안을 상품명으로 본다. 따옴표가 없으면 버린다
(`라벨리 팥빙수` 처럼 동사도 따옴표도 없는 제목이 실재한다).

날짜가 `2025/01/06` 에 3건 몰려 있다 = **게시판을 만들면서 과거 기사를 한꺼번에
옮긴 흔적**이다. 그래서 `released_at` 이 아니라 **`uploaded_at`** 에 넣는다
(롯데웰푸드·요아정과 같은 판단).

robots: https://lavelee.co.kr/robots.txt → 200 / 67B.
        `User-agent: *` / `Disallow: /wp-admin/` / `Allow: /wp-admin/admin-ajax.php`
        뿐이다. **우리가 받는 `/media-coverage/` 는 허용**이다. `Crawl-delay` 없음.
약관:   확인하지 않았다.
"""
import re
from datetime import date, timedelta
from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "라벨리"

# 신제품 글 게시판이 유일한 소스라 **0건인 날이 정상**이다. 조사 시점에도
# 창 안 글이 없었다. collect 의 0건 가드를 끄되 로그에는 한 줄 찍힌다
# — 사유는 collect.py 의 ALLOW_EMPTY 주석 참고.
ALLOW_EMPTY = True
SITE = "https://lavelee.co.kr"
LIST = SITE + "/media-coverage/"
DELAY = 2.2
DAYS = 400       # 상품 기사가 연 1건 남짓이다. 300일로 자르면 게시판 상태를 못 본다.

_VERB = re.compile(r"(출시|선봬|선보여|선보인다|선보일|론칭)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_MULTI = re.compile(r"\d+\s*종")
_SKIP = ("지원", "기부", "후원", "협약", "체결", "수상", "선정", "채용", "매출",
         "영업이익", "박람회", "팝업", "캠페인", "간담회", "개최", "참여",
         "참가", "전개", "리뉴얼", "실적", "모집", "행사", "이벤트", "할인",
         "완판", "돌파", "누적", "성료", "방송", "영상", "생산과정")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "에디션", "테마")
# 썸네일 꼬리. 떼면 원본이 나온다.
_THUMB = re.compile(r"-\d{2,4}x\d{2,4}(?=\.[A-Za-z]{3,4}$)")


def _pick(title: str) -> str:
    t = " ".join(title.split())
    body = _HEAD.sub(" ", t)                  # “…” 는 홍보 헤드라인이다
    if any(w in body for w in _SKIP) or _MULTI.search(body):
        return ""
    verb = None
    for m in _VERB.finditer(body):
        verb = m
    if not verb:
        return ""
    head = body[:verb.start()]
    quoted = None
    for m in _SINGLE.finditer(head):
        quoted = m
    if not quoted or any(w in head[quoted.end():] for w in _BETWEEN):
        return ""
    name = quoted.group(1).strip(" ,·∙")
    if len(name) < 2 or any(ch in name for ch in "·∙&?"):
        return ""
    return name


def _date(s: str) -> str:
    """'2025/01/06 by. laveleeadmin' → '2025-01-06'."""
    m = re.search(r"(20\d{2})[/.-](\d{1,2})[/.-](\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()
        rows = HTMLParser(r.text).css(".kboard-gallery-item")

        # 게시판이 통째로 안 읽히면 KBoard 스킨이 바뀐 것이다.
        if not rows:
            raise ValueError(
                f"라벨리 언론보도 목록이 비었다. {r.url} → {len(r.content)}B — "
                f"선택자(.kboard-gallery-item / .kboard-gallery-title / "
                f".kboard-gallery-username)가 바뀌었는지 확인하라")

        dated = 0
        for it_el in rows:
            t_el = it_el.css_first(".kboard-gallery-title")
            # ⚠️ 클래스 이름이 username 인데 실제로는 날짜 칸이다.
            d_el = it_el.css_first(".kboard-gallery-username")
            if not t_el:
                continue
            title = " ".join(t_el.text().split())
            when = _date(d_el.text() if d_el else "")
            if when:
                dated += 1
            if not when or when < floor:
                continue
            name = _pick(title)
            if not name:
                continue
            img_el = it_el.css_first("img")
            src = (img_el.attributes.get("src") or "").strip() if img_el else ""
            if src and "/kboard_thumbnails/" in src:
                src = _THUMB.sub("", src)          # 220x155 썸네일 → 원본
            a = it_el.css_first("a")
            href = (a.attributes.get("href") or "").strip() if a else ""
            item = Item(
                brand=BRAND,
                name=name,
                desc=title,
                image=src if src.startswith("https://") else "",
                # 2025/01/06 에 3건이 몰린 일괄 이관이라 출시일로 쓰지 않는다.
                uploaded_at=when,
                is_new=True,
                url=urljoin(SITE, href) if href else LIST,
            )
            if item.key not in seen:
                seen.add(item.key)
                items.append(item)

        # 날짜를 한 건도 못 읽었으면 전건이 조용히 떨어진다. 터뜨린다.
        if rows and not dated:
            raise ValueError(
                f"라벨리 언론보도 {len(rows)}건에서 날짜를 하나도 못 읽었다. "
                f".kboard-gallery-username 의 'YYYY/MM/DD' 꼴이 바뀌었는지 확인하라")
    return items
