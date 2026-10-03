"""요아정(요거트 아이스크림의 정석) — 공지사항 게시판의 '출시' 기사를 읽는다.

이 업종에서 **배스킨라빈스·설빙 다음으로 큰 브랜드**다. 공정위
`아이스크림/빙수`(K1) 에 같은 사업자가 두 줄로 올라 있다(2024년 말):
```
카페요아정              372개   (주)요아정
요거트아이스크림의 정석   187개   미확인
```
**둘은 같은 회사다.** 사업자등록번호가 `696-86-02195` 로 똑같다 —
옛 사이트(yoajung.imweb.me)는 `주식회사 트릴리언즈`, 현 사이트
(yoajung.co.kr)는 `주식회사 요아정` 으로 상호만 바뀌었다. 그래서
브랜드를 **하나(`요아정`)로 합쳐** 등록한다. 두 줄로 넣으면 같은 상품이
두 번 올라간다. `brand_sub` 는 `아이스크림`(요거트 아이스크림)이다.

## ⚠️ 지금 이 어댑터는 **0건을 돌려준다. 그게 맞다.**

게시판이 살아는 있는데 **최신 상품 글이 2025-02-10 이다**(19개월 정지).
`DAYS=400` 창 밖이라 오늘 기준 수집은 0건이다. 0건을 '고장'으로 읽지 마라 —
`collectors/theborn.py` 가 보도자료 없는 브랜드에 0건을 돌려주는 것과 같다.
게시판 선택자가 깨지면 그건 따로 `raise` 한다(아래 가드).

## 쓸 수 없는 경로부터 (여기서 시간 버리지 마라)

  GET https://yoajung.co.kr/bbs/content.php?co_id=menustore   200 / 2,108,659B
    '메뉴&매장'. 2MB 중 대부분이 **매장 목록 JSON**(`wr_datetime` 이 잔뜩 보이지만
    전부 **점포** 등록일이다 — 상품 날짜가 아니다. 숫자만 보고 속지 마라).
    메뉴 쪽은 **영양성분 계산기**다. 상품마다 `data-kcal`·`data-sugar`·
    `data-allergy` 는 있는데 **등록일도 NEW 배지도 없다.** 사진 파일명도
    해시(`…_FY3uDP9Q_f26c34e8….png`)라 epoch 가 없다(농심식 교차검증 불가).
    → 메뉴판 전체를 '신상' 으로 넣을 수 없다.
  GET https://yoajung.co.kr/bbs/board.php?bo_table=main_events  200 / 26,401B
    이벤트 게시판. 2026-09-22 'SKT Young Week' **1건**뿐이고 상품이 아니다.
  https://yoajung.imweb.me/Notice (6건·최신 2023-08-10) · /32 News (3건·최신
    2023-02-17) — **옛 사이트**다. 상품 출시 글이 0건이고 3년째 멈춰 있다.

## 쓰는 경로

  GET https://yoajung.co.kr/bbs/board.php?bo_table=main_port   200 / 40,444B
    그누보드5 공지사항. 완전 SSR. 2026-10-03 현재 **전체 14건**(1페이지).
    <td class="td_subject"><a href="…&wr_id=12">[요아정 소식] 요아정, 신제품
        '파베 생초콜릿' 2종 출시</a></td>
  ⚠️ **목록의 날짜 칸을 믿지 마라.** 목록은 `MM-DD` 만 찍고(그누보드 기본),
     맨 윗줄 공지는 `07-22` 로 보이는데 상세를 열면 `작성일 25-02-10 12:44` 다.
     목록 날짜와 실제 작성일이 **다르다.** 그래서 이 어댑터는 **상세의
     `작성일 YY-MM-DD` 를 받아 쓴다**(2000년대로 펴서 `20YY-MM-DD`).

  실측 전수(상세에서 받은 작성일):
```
14 [요아정 X 로스트아크] … 프로모션 참여 매장        25-02-10  ← 프로모션
13 압구정 로데오에 '요아정 하우스' 오픈…             25-02-10  ← 매장 오픈
12 요아정, 신제품 '파베 생초콜릿' 2종 출시            25-02-10  ← 'N종' → 버림
11 요아정, 웰니스 … '저당 요거트 아이스크림' 출시     25-02-10  ✔ 유일한 상품
10 …요아정 아이스크림 100개 기부…                   25-01-02  ← 기부
 8 요아정XTWS(투어스) 콜라보 메뉴 2종 출시…          25-01-02  ← 콜라보+N종 → 버림
 3 …수험생을 위한 11월 이달의 메뉴 2종 할인 이벤트…   24-11-14  ← 할인
 1 [OPEN] 요아정 홈페이지 리뉴얼                     24-02-27  ← 리뉴얼
```
`작성일` 이 `25-02-10` 에 4건, `25-01-02` 에 7건 몰려 있다 = **보도자료를
한꺼번에 퍼 나른 일괄 등록**이다. 그래서 이 날짜는 `released_at` 이 아니라
**`uploaded_at`** 에 넣는다(롯데웰푸드가 같은 판단을 했다). 기사 본문은
실제 출시일을 따로 말한다("1월 13일 새롭게 선보였다") — 하지만 본문에서
날짜를 캐내는 건 이 레포의 다른 어댑터가 하지 않는 일이라 하지 않는다.

robots: https://yoajung.co.kr/robots.txt → 200 / 22B.
        `User-agent:*` + `Allow: /` — **전면 허용**이다. `Crawl-delay` 없음.
약관:   확인하지 않았다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "요아정"

# 신제품 글 게시판이 유일한 소스라 **0건인 날이 정상**이다. 조사 시점에도
# 창 안 글이 없었다. collect 의 0건 가드를 끄되 로그에는 한 줄 찍힌다
# — 사유는 collect.py 의 ALLOW_EMPTY 주석 참고.
ALLOW_EMPTY = True
SITE = "https://yoajung.co.kr"
LIST = SITE + "/bbs/board.php?bo_table=main_port"
VIEW = LIST + "&wr_id="
DELAY = 2.2
DAYS = 400
MAX_DETAILS = 12

# --- 제목 → 상품명. maker_orion `_pick` 계보 -------------------------------
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|선보일|론칭|공개)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_MULTI = re.compile(r"\d+\s*종")      # 'N종' 은 하나를 특정 못 한다 → 버린다
_LEAD = re.compile(r"^\s*\[[^\]]*\]\s*")      # '[요아정 소식]' 접두
_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출",
         "영업이익", "협약", "체결", "후원", "기부", "공모", "박람회", "팝업",
         "캠페인", "앰배서더", "간담회", "개최", "참여", "참가", "전개", "지원",
         "리뉴얼", "실적", "가맹", "창업", "모집", "오픈", "행사", "이벤트",
         "할인", "증정", "프로모션", "웨이팅", "기록", "계약")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "에디션", "테마")


def _pick(title: str) -> str:
    t = _LEAD.sub("", " ".join(title.split()))
    body = _HEAD.sub(" ", t)
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


# 상세의 '작성일25-02-10 12:31'. 그누보드5 기본 표기다.
_WROTE = re.compile(r"작성일\s*(\d{2})-(\d{2})-(\d{2})")


def _wrote_at(html: str) -> str:
    """상세의 `작성일 YY-MM-DD` → 'YYYY-MM-DD'. 못 읽으면 빈 문자열."""
    txt = " ".join(HTMLParser(html).text().split())
    m = _WROTE.search(txt)
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"20{y:02d}-{mo:02d}-{d:02d}"


def _image(html: str) -> str:
    for img in HTMLParser(html).css("#bo_v_atc img, #bo_v_con img, .view_content img"):
        src = (img.attributes.get("src") or "").strip()
        if src.startswith("https://"):
            return src
    return ""


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()
        doc = HTMLParser(r.text)
        links = [a for a in doc.css("a")
                 if "bo_table=main_port" in (a.attributes.get("href") or "")
                 and "wr_id=" in (a.attributes.get("href") or "")]

        # 글이 한 줄도 안 읽히면 그누보드 스킨이 바뀐 것이다. 조용히 넘기지 않는다.
        if not links:
            raise ValueError(
                f"요아정 공지 목록에서 글 링크를 하나도 못 찾았다. {r.url} → "
                f"{len(r.content)}B — 'bo_table=main_port&wr_id=' 링크 꼴이 "
                f"바뀌었는지 확인하라")

        # 같은 글이 PC/모바일 스킨에 두 번 나올 수 있다. wr_id 로 중복을 턴다.
        cand = {}
        for a in links:
            href = a.attributes.get("href") or ""
            m = re.search(r"wr_id=(\d+)", href)
            title = " ".join(a.text().split())
            if not m or not title:
                continue
            cand.setdefault(m.group(1), title)

        # 제목만으로 상품 글이 아닌 게 분명하면 상세를 받지 않는다(요청 절약).
        picked = [(wid, t, _pick(t)) for wid, t in cand.items()]
        picked = [p for p in picked if p[2]]
        picked.sort(key=lambda p: int(p[0]), reverse=True)

        for wid, title, name in picked[:MAX_DETAILS]:
            time.sleep(DELAY)
            rr = base.retry(lambda wid=wid: c.get(VIEW + wid))
            rr.raise_for_status()
            # ⚠️ 목록 날짜 칸은 실제 작성일과 다르다. 상세에서 받는다.
            wrote = _wrote_at(rr.text)
            if not wrote or wrote < floor:
                continue
            it = Item(
                brand=BRAND,
                name=name,
                desc=_LEAD.sub("", " ".join(title.split())),
                image=_image(rr.text),
                # 25-02-10 에 4건, 25-01-02 에 7건이 몰린 일괄 등록이다.
                # 출시일이 아니라 등록 시각이므로 released_at 에 넣지 않는다.
                uploaded_at=wrote,
                is_new=True,
                url=VIEW + wid,
            )
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)
    return items
