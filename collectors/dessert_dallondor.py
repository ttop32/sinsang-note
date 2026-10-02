"""달롱도르 — 자체 사이트 **뉴스 게시판**의 '출시' 기사에서 신제품을 뽑는다.

공정위 `아이스크림/빙수`(K1) 가맹점 수 **84개**로 배스킨라빈스(1,706)·설빙(576)·
카페요아정(372)·요거트아이스크림의정석(187) 다음 5위다(2024년 말,
notes/FRANCHISE-MASTER.md §디저트/아이스크림). 가맹본부 (주)화이트빌.
요거트 아이스크림이 주력이라 `brand_sub` 는 `아이스크림` 이다(눈꽃빙수도 판다).

오리온·사조 계보다 — **보도자료 제목에서 상품명을 뽑고 등록일을 출시일로 쓴다.**

## 메뉴판은 안 쓴다 (두 경로를 다 열어 보고 내린 판정)

  GET https://dallondor.com/menu/list.php?cat_no=2   200 / 42,580B
    요거트 아이스크림 카탈로그다. **NEW 배지도 등록일도 없다.**
    (probe 에서 잡힌 `new` 4건은 전부 내비의 `/notice/news.php` 링크였다 —
     배지가 아니다. 문자열만 세고 넘어가면 이렇게 속는다.)
    cat_no 는 2(요거트 아이스크림)·4·8… 로 분류가 갈리는데 어느 쪽도 같다.
  → 메뉴판 전체를 '신상'으로 넣을 수 없다. 뉴스 게시판만 쓴다.

## 쓰는 경로

  GET https://dallondor.com/notice/news.php    200 / 34,141B    완전 SSR
    <div class="board-list"><table><tbody>
      <tr>
        <td><span class="label">공지</span></td>            ← 공지는 상품이 아니다
        <td class="subject"><a href="/notice/news.php?boardid=news&mode=view&idx=7"
            title="달롱도르, 겨울 시즌 한정 ‘해피 케이크 시리즈’ 출시">…</a></td>
        <td>달롱도르</td>
        <td>2025-12-05</td>      ← 4번째 td = 등록일. `YYYY-MM-DD` 로 완전하다
        <td>361</td>
      </tr>
  선택자: `.board-list table tbody tr` → `td.subject a`(제목·링크) · `td`[3](날짜).
  ⚠️ 같은 글이 PC 표(`.board-list`)와 모바일 목록(`.board-list-m`)에 **두 번** 있다.
     `.board-list` 로 한정하지 않으면 전건이 2배로 들어온다.
  상세(`…&mode=view&idx=N`)의 본문 첫 그림이 기사 사진이다:
     `/uploaded/webedit/2512/912582a2…png` → 절대 https 로 올려 쓴다.

## 실측 — 게시판이 **얇고, 지금은 멈춰 있다**

2026-10-02 현재 **전체 4건**이 전부다(페이지네이션 없음).
```
공지  [공지] 달롱도르 요거트 아이스크림 영양성분 안내     2025-08-12   ← 공지
 3    달롱도르, 겨울 시즌 한정 ‘해피 케이크 시리즈’ 출시   2025-12-05   ← 상품
 2    달롱도르, 가을을 담은 요거트 아이스크림 신메뉴 5종 출시 2025-09-30  ← 'N종'
 1    …한양대 에리카 워터밤 행사 참여…                  2025-09-05   ← 행사
```
**최신 글이 2025-12-05 다. 10개월째 새 글이 없다.** 그래서 `DAYS` 를 오리온의
300일이 아니라 **400일**로 잡았다 — 연 3~4건짜리 게시판이라 300일로 자르면
지금 당장 0건이 되고, 그러면 게시판이 살아 있는지 죽었는지도 구분이 안 된다.
화면의 신상 창(60일)에는 어차피 안 오르니 데이터가 부풀 걱정은 없다.

'N종' 기사는 **일부러 버린다**(오리온 `_MULTI` 와 같은 규칙). 제목만으로는
5종 중 무엇인지 특정할 수 없어서 지어내게 된다. 그래서 실수집은 **1건**이다.
0건이 아니라 1건인 게 맞다 — 이 브랜드는 원래 이만큼만 낸다.

robots: https://dallondor.com/robots.txt → 200 / 4,386B.
        Googlebot·Yeti·NaverBot·Daumoa·bingbot·Slurp·Baiduspider·YandexBot·
        DuckDuckBot·facebookexternalhit·Twitterbot·LinkedInBot 등 **명명된 봇만**
        `Allow: /` + `Crawl-delay: 1` 이고, 끝에 "나쁜 봇들 및 기타 모든 봇 차단"
        절이 있다. 우리 UA 는 명명 목록에 없으니 **형식상 차단**이다.
        운영자 판단으로 수집하되 UA 위장은 하지 않고(`base.UA`), 선언된
        `Crawl-delay: 1` 보다 넉넉한 2.2초를 쓴다. 삭제 요청이 오면 즉시 내린다.
약관:   확인하지 않았다.
"""
import re
import time
from datetime import date, timedelta
from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "달롱도르"
SITE = "https://dallondor.com"
LIST = SITE + "/notice/news.php"
DELAY = 2.2
DAYS = 400      # 연 3~4건짜리 게시판이다. 300일로 자르면 지금 당장 0건이 된다.
MAX_DETAILS = 10    # 상세 요청 상한. 폭주 방지.

# --- 제목 → 상품명. maker_orion `_pick` 과 같은 규칙이다 --------------------
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|선보일|론칭|공개)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_MULTI = re.compile(r"\d+\s*종")        # 'N종' 은 하나를 특정 못 한다 → 버린다
# 상품이 아닌 글. 수상·팝업·캠페인·실적·채용·협약·기부·완판·리뉴얼·가맹점 모집.
_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "공모", "발대식", "박람회",
         "팝업", "캠페인", "앰배서더", "경연", "시상", "간담회", "개최", "참여",
         "참가", "전개", "지원", "리뉴얼", "실적", "가맹", "창업", "모집",
         "오픈", "행사", "이벤트", "할인", "증정", "영양성분")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "에디션", "테마")


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 특정 못 하면 빈 문자열."""
    t = " ".join(title.split())
    body = _HEAD.sub(" ", t)                      # “…” 는 홍보 헤드라인이다
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
    """'2025-12-05' → '2025-12-05'. 월·일 범위를 검증한다."""
    m = re.search(r"(20\d{2})[-.](\d{1,2})[-.](\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _image(html: str) -> str:
    """상세 본문의 첫 에디터 그림. 없으면 빈 문자열."""
    for img in HTMLParser(html).css("img"):
        src = (img.attributes.get("src") or "").strip()
        if "/uploaded/" in src:
            return urljoin(SITE, src)
    return ""


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()
        doc = HTMLParser(r.text)
        # ⚠️ `.board-list` 로 한정한다. 같은 글이 `.board-list-m`(모바일)에도 있다.
        rows = doc.css(".board-list table tbody tr")

        # 게시판 자체가 비면 고장이다. 조용히 0건을 돌려주지 않는다.
        if not rows:
            raise ValueError(
                f"달롱도르 뉴스 목록이 비었다. {r.url} → {len(r.content)}B — "
                f"선택자(.board-list table tbody tr / td.subject a)가 "
                f"바뀌었는지 확인하라")

        picked = []
        for tr in rows:
            a = tr.css_first("td.subject a")
            if not a:
                continue
            # '공지' 라벨이 붙은 줄은 상품 기사가 아니다(영양성분 안내 등).
            if tr.css_first("span.label"):
                continue
            tds = tr.css("td")
            released = _date(tds[3].text()) if len(tds) > 3 else ""
            if not released or released < floor:
                continue
            title = " ".join((a.attributes.get("title") or a.text()).split())
            name = _pick(title)
            if not name:
                continue
            picked.append((name, title, released,
                           urljoin(SITE, a.attributes.get("href") or "")))

        for name, title, released, href in picked[:MAX_DETAILS]:
            img = ""
            if href:
                time.sleep(DELAY)
                try:
                    rr = base.retry(lambda href=href: c.get(href))
                    rr.raise_for_status()
                    img = _image(rr.text)
                except Exception:
                    img = ""        # 사진은 없어도 된다. 기사 자체는 유효하다
            it = Item(
                brand=BRAND,
                name=name,
                desc=title,
                image=img,
                released_at=released,
                is_new=True,
                url=href or LIST,
            )
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)
    return items
