"""요거프레소.

/menu/menu-new.html 한 장이 신메뉴 아카이브다. SSR, UTF-8, 브라우저 불필요, 1요청.
robots.txt 는 `User-agent: * / Allow: /` 전체 허용(2026-09-30 재확인).

⚠️ 이용약관(/policy/term.html)이 이 브랜드 것이 아니다. 홈페이지 제작사가
**도메인 등록 서비스 약관 템플릿**을 그대로 붙여놨다("추가 도메인 등록시 개인정보
자동 입력" 따위). 명랑핫도그와 본문이 완전히 같다. 크롤링 금지 조항은 없지만,
이 문서가 브랜드의 의사표시라고 보기 어렵다는 점을 감안해야 한다.

신제품 신호 — 2026-09-30 실측. 69슬라이드, 2021-01 까지 누적.
  - 슬라이드 캡션이 '2026년 7월 유자레몬 샤베트' 처럼 **출시 연월 + 상품명**이다.
    2자리 연도('25년 8월')와 4자리 연도('2026년 7월')가 섞여 있다.
  - released_at 에 **그 달 1일**을 넣는다. 배스킨라빈스가 이미 쓰는 방식이고
    같은 근거다. 판단 근거를 남겨 둔다:
      · 달은 우리가 추정한 게 아니라 브랜드가 글자로 써 준 값이다.
      · Item.released_at 은 YYYY-MM-DD 문자열 한 자리뿐이라 '월 정밀도'를
        표현할 자리가 없다. 비워 두면 이 브랜드의 제일 강한 신호가 통째로 날아가고,
        합류 첫날 신제품이 0건이 된다.
      · 오차는 최대 한 달이고 **미래로는 절대 벗어나지 않는다**(항상 그 달 1일).
      · 대안인 이미지 타임스탬프는 실제로 틀린다 — '25년 8월 믹스요거트쉐이크'의
        이미지가 2026-04 업로드다. 그건 출시일이 아니라 업로드 시각이라 uploaded_at 이다.
    **일자는 사실이 아니라 자리채움이다.** 화면에서 '몇 일'로 읽히면 안 된다.
  - 이미지 경로가 연월을 교차검증해 주긴 하는데 **정확히 일치하지는 않는다.**
    폴더가 출시 한 달 전인 경우가 흔하고(2026년 6월 신메뉴 → /202605/),
    한참 뒤에 다시 올린 것도 있다(25년 8월 → /202604/). 그래서 경로는
    uploaded_at 으로만 쓰고 released_at 판정에는 쓰지 않는다.
  - 캡션 앞머리의 분류어가 '신메뉴' 하나가 아니다. **'리뉴얼'·'한정메뉴'**도 있고
    아예 없는 것도 있다. 리뉴얼은 브랜드가 기존 메뉴를 고쳤다고 말한 것이므로
    is_new=False 로 내린다(근거가 있는 False 다). 나머지는 신메뉴 아카이브에
    올라와 있다는 사실을 근거로 True.

**항목이 개별 SKU 가 아니라 시리즈 단위인 경우가 많다**('아이스컵빙수 시리즈',
'쫀득베이글 3종'). 이름을 쪼개지 않고 브랜드가 쓴 그대로 둔다.
2024-04 이전 슬라이드는 캡션이 '2023년 12월 신메뉴' 처럼 **분류어뿐이라 상품명이 없다.**
그런 건 상품이 아니므로 버린다(69건 중 41건).

상품 상세 페이지가 없다(링크가 전부 href="#none"). url 은 비워 둔다.
가격 정보는 사이트 어디에도 없다.
"""
import re
import time
from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "요거프레소"
ROOT = "https://yogerpresso.co.kr"
URL = ROOT + "/menu/menu-new.html"
CATEGORY = "신메뉴"
DELAY = 2.0   # robots 에 Crawl-delay 는 없다. 1요청뿐이라 여유를 둔다.

# 캡션 앞머리: '2026년 7월' 또는 '25년 8월'
_WHEN = re.compile(r"^(\d{2,4})\s*년\s*(\d{1,2})\s*월\s*")
# 연월 뒤에 오는 분류어. 상품명에서 떼어 labels 로 옮긴다.
_KIND = re.compile(r"^(신메뉴|리뉴얼|한정메뉴)\s*")


def _caption(txt: str) -> tuple:
    """'2026년 7월 신메뉴 레트로 미숫가루' → ('2026-07-01', '신메뉴', '레트로 미숫가루').

    연월을 못 읽으면 전부 빈 값으로 돌려준다(그런 슬라이드는 지금 없다).
    """
    m = _WHEN.match(txt)
    if not m:
        return "", "", txt
    year, month = int(m.group(1)), int(m.group(2))
    if year < 100:
        year += 2000                      # '25년' → 2025년
    if not 1 <= month <= 12:
        return "", "", txt
    rest = txt[m.end():].strip()
    k = _KIND.match(rest)
    kind = k.group(1) if k else ""
    return f"{year:04d}-{month:02d}-01", kind, rest[k.end():].strip() if k else rest


def _uploaded_at(img_url: str) -> str:
    """파일명 꼬리의 업로드 타임스탬프(_20260706091120.png)를 날짜로."""
    m = re.search(r"_(\d{4})(\d{2})(\d{2})\d{6}\.\w+$", img_url)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(URL))
        r.raise_for_status()
        time.sleep(DELAY)

        # 썸네일 슬라이더(.view-slide-thumb)가 같은 69건을 한 벌 더 갖고 있다.
        # 큰 슬라이더만 본다.
        for slide in HTMLParser(r.text).css(".view-slide-big .swiper-slide"):
            cap = slide.css_first("p.txt")
            if not cap:
                continue
            released, kind, name = _caption(" ".join(cap.text().split()))
            if not name:
                continue          # '2023년 12월 신메뉴' 처럼 상품명이 없는 옛 슬라이드
            img = slide.css_first("img")
            src = img.attributes.get("src", "") if img else ""
            it = Item(
                brand=BRAND,
                name=name,
                image=urljoin(ROOT, src) if src else "",
                labels=[kind] if kind else [],
                category=CATEGORY,
                uploaded_at=_uploaded_at(src),
                released_at=released,
                # 리뉴얼은 브랜드가 '기존 메뉴를 고쳤다'고 말한 것이라 False.
                is_new=False if kind == "리뉴얼" else True,
            )
            if it.key in keys:
                continue          # 같은 이름이 두 슬라이드로 올라온 경우가 있다
            keys.add(it.key)
            items.append(it)
    return items
