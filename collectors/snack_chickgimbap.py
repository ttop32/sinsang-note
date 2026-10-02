"""병아리김밥 — 메뉴 섹션에서 이름 앞에 붙은 `new ` 접두를 센다.

엔와이앤컴퍼니㈜(745-86-01902, 서울 강서 공항대로44길 66 NY빌딩 401호,
대표 윤동연). 공정위 `기타 외식` 78개점(2024년 말). 꼬마김밥 전문점이다.
도메인은 **`chickgimbap.com`**(푸터에 `www.chickgimbap.com` 과
사업자등록번호가 같이 찍혀 있어 대조했다). 검색으로는 안 나오고
인스타 `@chickgimbap_official` 의 linktr.ee 를 거쳐 찾았다.
2026-10-02 실측 200 / 80KB / UTF-8 / 완전 SSR. gnuboard 테마 위에 얹은
한 장짜리 창업 랜딩이다.

⚠️ **루트가 인트로 게이트다.** 브라우저로 열면 `구경해 볼래? / 입장하기`
노란 전면 레이어가 먼저 뜬다. 다만 **서버 302 도 JS 리다이렉트도 아니고
본문 위에 덮인 레이어**라, 우리가 받는 HTML 에는 메뉴가 그대로 들어 있다.
게이트를 보고 "못 읽는 사이트"로 접지 마라(반대로, 게이트가 있다고 본문이
없는 것도 아니다).

robots.txt 는 **404** 다(200/빈 파일이 아니라 아예 없다).
`<meta name="robots" content="index,follow">` 는 본문에 있다.
이용약관 문서는 푸터에 모달로 있는데 **내용이 비어 있다** —
`해당 홈페이지에 맞는 회원가입약관을 입력합니다.` 라는 테마 자리표시자
그대로다. 즉 "약관에 금지 조항이 없다"가 아니라 **"약관이 작성돼 있지
않다"**. 삭제 요청이 오면 다투지 말고 즉시 내린다.

## ⭐ 배지 비율 — 45건 중 new 6 (13.3%)

| 분류 | 건수 | new |
|---|---:|---:|
| 꼬마김밥 메뉴 | 13 | 2 |
| 도시락&세트 메뉴 | 12 | 1 |
| 유부초밥 메뉴 | 6 | 1 |
| 사이드 메뉴 | 14 | 2 |
| **합계** | **45** | **6** |

전수도 0건도 아니다. 붙은 이름은 **참치김치 반뚱이김밥 · 유부 반뚱이김밥 ·
병아리 로마콤보 · 병아리 유부초밥(3pcs) · 연불냉국수 · 로제크림우동**.
간판인 `병아리 김밥` 과 대표 사이드 `학교앞 떡볶이`·`순살 닭강정` 에는
안 붙어 있다 — 섹션 장식이 아니다. 브랜드도 랜딩에 `1년 2회 메뉴 리뉴얼로
꾸준한 신메뉴판매` 라고 적어 뒀고, 6건이라는 수가 거기 맞는다.

## ⚠️ 배지가 **요소가 아니라 상품명 문자열의 일부**다

이게 이 사이트의 함정이다. 싸다김밥은 글자가 아니라 그림이었고,
수유리우동집은 전수로 깔린 div 였는데, 여기는 **아예 마크업이 없다.**

    <li class="swiper-slide">
      <img src="/data/file/menu/252b…jpg" alt="">
      <h6>new 참치김치 반뚱이김밥</h6>   ← innerHTML 이 딱 이 글자다
    </li>

`class`·`data-*`·별도 `<span>` 이 하나도 없다. 운영자가 관리자 화면에서
상품명 앞에 `new ` 를 타자로 쳐 넣은 것이다. 화면에도 그대로 글자로 보인다
(브라우저 실측: 45건 전부 `offsetParent !== null`, 그중 6건이 `new` 로 시작).
그래서 **판정 기준이 문자열 접두사**고, `is_new` 를 세울 때 그 접두를
이름에서 떼어내야 한다. 운영자가 `New`·`NEW` 로 쓸 수도 있어 대소문자를
무시하고, 뒤에 공백이 없는 `new메뉴` 같은 말까지 걸리지 않게 **경계를 둔다.**

⚠️ 원본을 `NEW` 로 grep 하면 **0건**이다(전부 소문자). 대문자만 보고
"신호 없음"으로 적으면 틀린다.

## 날짜는 비운다
이 사이트에는 게시판이 없다(공지·보도자료·소식 전부 없음. 창업 문의 폼뿐).
`new` 6건의 이미지가 `252b6951…_` 로 시작하는 같은 업로드 묶음이고
나머지는 `05006d73…_` 인데, **`모듬 튀김` 이 `252b…` 인데도 `new` 가
아니다** — 같은 날 올린 그림이라고 다 신상이 아니라는 반례다(김가네·
김밥킹에 적어 둔 것과 같은 종류). 파일명에 날짜도 없다.
`released_at`·`uploaded_at` 둘 다 **비운다. 지어내지 않는다.**

## 상품별 주소가 없다
GNB 가 `javascript:void(0)` + `data-url="include_main.php#sec10"` 으로
섹션을 끼워 넣는 방식이라 상품 상세가 없다. 본문 자체에
`<section id="sec10">` 이 있으므로 전 상품을 `/#sec10` 으로 보낸다.
요청 **1회**로 끝난다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "병아리김밥"
ROOT = "https://chickgimbap.com"
MENU_URL = ROOT + "/#sec10"     # 상품별 주소가 없다(위 docstring)
DELAY = 2.5                     # robots 가 없다. 1요청뿐이라 여유를 둔다.
MIN_ITEMS = 20                  # 실측 45. 절반도 못 찾으면 구조가 바뀐 것이다.

# 이름 앞에 타자로 박아 둔 신상 표시. 대소문자 무시, 뒤에 공백/구두점이
# 와야 걸린다(`new메뉴` 같은 단어가 통째로 걸리는 걸 막는다).
_NEW = re.compile(r"^new\b[\s:·-]*", re.I)


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(ROOT))
        r.raise_for_status()
        time.sleep(DELAY)

        sec = HTMLParser(r.text).css_first("#sec10")
        if sec is None:
            raise RuntimeError(
                f"[{BRAND}] 메뉴 섹션(#sec10)을 못 찾았다 — "
                f"랜딩 구조가 바뀌었다")

        for box in sec.css("div.menu-box"):
            h4 = box.css_first("h4")
            # '꼬마김밥 메뉴' → '꼬마김밥'. 분류를 못 읽으면 비운다.
            category = (" ".join(h4.text().split()).replace("메뉴", "").strip()
                        if h4 else "")
            for li in box.css("li.swiper-slide"):
                h6 = li.css_first("h6")
                if h6 is None:
                    continue
                raw = " ".join(h6.text().split())
                if not raw:
                    continue
                name = _NEW.sub("", raw).strip()
                if not name:
                    # 'new' 만 들어 있는 카드는 상품이 아니다.
                    continue
                img = li.css_first("img")
                src = img.attributes.get("src", "") if img else ""
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=ROOT + src if src.startswith("/") else src,
                    category=category,
                    # 접두가 붙은 것만 True. 없으면 '아니다'가 아니라 '모른다'.
                    is_new=True if raw != name else None,
                    url=MENU_URL,
                )
                if it.key in keys:
                    continue
                keys.add(it.key)
                items.append(it)

    if len(items) < MIN_ITEMS:
        raise RuntimeError(
            f"[{BRAND}] 상품이 {len(items)}건뿐이다(실측 45) — "
            f"선택자가 깨졌는지 확인해야 한다")

    # 신호가 이름 접두 하나뿐이다. 운영자가 접두를 떼면 건수는 45 그대로라
    # collect 의 0건·급감 가드에 안 걸리고 조용히 '신상 없는 브랜드'가 된다.
    if items and not any(i.is_new for i in items):
        print(f"[{BRAND}] 이름 앞 'new' 접두가 0건이다 — 운영자가 뗀 건지 "
              f"선택자가 깨진 건지 확인해야 한다")
    return items
