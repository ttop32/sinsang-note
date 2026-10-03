"""카페인중독 — 메뉴 카드의 이미지 업로드일을 날짜로 쓴다.

(주)어딕션컴퍼니(옛 중독컴퍼니). **도메인 찾는 데가 제일 오래 걸린다** —
흔히 추측하는 `cafeinjungdok.com`·`caffeineaddiction.co.kr`·`cafeinjungdok.co.kr`·
`caffeineaddiction.kr`·`addictioncompany.co.kr` 은 전부 NXDOMAIN 이고,
`addiction.co.kr` 은 한국중독정신의학회라는 **남의 사이트**다. 실제 공식 사이트는
한글 도메인 `카페인중독.com`(퓨니코드 `xn--iq1bo78ac9at1k9mh.com`) 이다.
`caffein-addiction.imweb.me` 도 살아 있지만 그쪽은 창업상담 랜딩이라 상품이 없다.

아임웹(imweb) SSR 이고 경로가 숫자다. 상품이 있는 면은 이렇다(2026-10-03 실측).

    /29  디저트·와플 23   /52 크로플 12   /31 베이커리 36   /33 떡볶이 5
    /65  음료 2          /979821801 커피 31   /1373078117 티 12
    /40  에이드 7        /41 스무디 21        /70 제주 한정 4

⚠️ 내비에 `/56`(디저트)과 `/29`(와플)이 따로 걸려 있지만 **`/56` 은 `/29` 로
리다이렉트된다.** 둘 다 읽으면 같은 23건을 두 번 받는다. `/29` 하나만 쓴다.

카드 구조는 우지커피와 같은 아임웹 기본형이다 — `div.item_container._item_container`
안에 `p.title`(상품명) + `span.body`(설명) + `div.img_wrap[data-src]`(이미지).
여기서도 **`p.title` 텍스트에 `span.body` 가 중첩돼 딸려 나온다.** 꼬리를 뗀다.

## 신상 신호 — 배지가 없다. 날짜가 신호다

NEW 배지도, 신메뉴 전용 면도 없다. 내비의 `/86`(새로운 메뉴)는 이미지 몇 장과
상담 입력폼뿐이고 상품 카드가 0건이다. `/28`(메뉴)은 51칸이 전부
`img_wrap._img_wrap.no_content` **포스터 한 장**이고 `p.title` 이 빈 문자열이라
이름을 못 얻는다(우지커피 `/Vision` 과 같은 모양).

쓸 수 있는 건 카드 이미지 CDN 경로의 `/YYYYMMDD/` 다. **그런데 이건 기본적으로
못 믿는 값이라 먼저 분포부터 셌다**(컴포즈커피 Last-Modified 149건 한 날,
파리바게뜨 98건 한 날 같은 전례가 있다). 151종의 분포가 이렇게 갈린다.

    20251015  65건 (43%)  ← 아메리카노·카페라떼·카페모카·얼그레이·캐모마일…
    20200731   8건        ← 2020년 묶음
    20200720   7건        ← 2020년 묶음
    20261001   3건  호박인절미 떡플 / 카스테라인절미 떡플 / 옛맛 인절미 떡플
    20260904   4건  산더미 라면땅(달콤·매콤) / 에그마요·참치마요 벽돌샌드위치
    20260825   3건  저당 꿀사과·꿀배·꿀유자 요구르트
    20260707   6건  팩빙수 2종 / 버켓 빙수 4종
    20260610   2건  꿀 수박 컵빙수 / 꿀 수박 우유화채
    20260520   4건  말차몬드 와플 / 딸기나무숲 라떼 / 숙성 말차 라떼 / 코코 말차 클라우드
    …(이하 1~4건짜리 날짜가 20개 더)

**43%짜리 한 날(2025-10-15)은 카탈로그 통째 재업로드**다 — 그 날에 걸린 65건이
전부 아메리카노·카페라떼·얼그레이 같은 상시 메뉴고, 신상이 하나도 없다.
반면 나머지 날짜는 **3~6건씩 묶인 계절 신메뉴**다. 한 묶음이 한 번의 출시고,
그 묶음 안이 전부 같은 테마다(인절미 떡플 3종, 저당 요구르트 3종, 빙수 6종).

사이트가 그걸 또 한 번 확인해 준다 — `/28` 의 포스터 51장(이름은 없지만 날짜는
있다)의 업로드일이 `20261001 · 20260825 · 20260720 · 20260707 · 20260626 ·
20260326 · 20260312 · 20251219 · 20251209 …` 로 **카드 날짜와 같은 날에 찍힌다.**
신메뉴를 낼 때 포스터와 상품 카드를 같이 올리는 운영이다. 반대로 20251015 에는
포스터가 한 장도 없다 — 그 날은 출시가 아니라 사이트 작업이었다는 뜻이다.

그래서 **일괄 재업로드일(전체의 30%를 넘는 날짜)의 uploaded_at 은 비운다.**
날짜를 박아두지 않고 매번 센다. 현재 걸리는 건 20251015 하나다.
(`rules.untrust_bulk_dates` 가 수집 뒤에 같은 일을 한 번 더 하지만, 그쪽은
브랜드별 중앙값 기준이라 기준이 다르다. 어댑터가 먼저 아는 건 어댑터가 턴다.)

`is_new` 는 **채우지 않는다(None).** 브랜드가 신제품이라고 말한 적이 없고,
우리가 읽은 건 업로드일뿐이다. 날짜가 `uploaded_at` 에 들어가므로
`rules.is_fresh` 의 날짜 분기가 최근 것만 골라낸다. 배지가 없는데 전건에
`is_new=True` 를 찍는 게 이 서비스에서 제일 하면 안 되는 일이다.

`released_at` 이 아니라 `uploaded_at` 인 이유도 같다 — 브랜드가 "며칠 출시"라고
말한 게 아니라 우리가 CDN 경로에서 읽어낸 업로드일이다.

## 담지 않는 것

`/23`(언론보도)·`/44`(공지사항) 게시판은 읽지 않는다. 20건을 훑어보니
'9월 성공창업설명회 성료', '상생 정책', '이노비즈 인증' 같은 **가맹 영업·수상
기사**가 대부분이고 상품 출시 기사가 드물다. 메뉴 카드 쪽이 날짜도 상품도
더 정확해서 보도자료를 겹쳐 읽을 이유가 없다(우지커피는 반대로 메뉴 카드에
쓸 날짜가 없어서 보도자료로 갔다 — 브랜드마다 답이 다르다).

상품 상세 페이지가 없어 `Item.url` 은 비우고 SITES 폴백에 맡긴다.
이미지는 `cdn.imweb.me` https 라 `base.derive()` 가 지우지 않는다. 요청은 10회다.

robots.txt: 200/0바이트(빈 파일)라 금지 규칙이 없다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "카페인중독"
# 한글 도메인 카페인중독.com 의 퓨니코드.
ROOT = "https://xn--iq1bo78ac9at1k9mh.com"

# 경로 → 화면에 쓸 분류. 내비 이름 그대로다.
# ⚠️ /56(디저트)은 /29 로 리다이렉트된다. 넣으면 23건을 두 번 받는다(docstring).
MENU_PATHS = {
    "/29": "디저트",
    "/52": "크로플",
    "/31": "베이커리",
    "/33": "떡볶이",
    "/65": "음료",
    "/979821801": "커피",
    "/1373078117": "티",
    "/40": "에이드",
    "/41": "스무디",
    "/70": "제주 한정",
}

DELAY = 2.0
MIN_ITEMS = 100          # 이보다 적으면 선택자가 깨진 것이다(실측 151)
MAX_ITEMS = 600          # 폭주 방지
# 한 업로드일이 전체의 이 비율을 넘으면 일괄 재업로드로 보고 날짜를 비운다.
# 실측 2025-10-15 가 43%, 그 다음이 5% 대라 사이가 넓게 벌어진다.
_BULK_SHARE = 0.30

_CDN_DAY = re.compile(r"/(\d{8})/")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _card(con) -> tuple:
    """카드에서 (상품명, 설명, 이미지, 업로드일 YYYYMMDD).

    `p.title` 이 `span.body` 를 품고 있어 꼬리를 떼야 상품명이 된다. 안 떼면
    이름이 `호박인절미 떡플쫄깃한 인절미에…` 가 된다(우지커피와 같은 함정).
    """
    t = con.css_first("p.title")
    b = con.css_first("span.body")
    iw = con.css_first("div.img_wrap")
    full = _clean(t.text()) if t is not None else ""
    body = _clean(b.text()) if b is not None else ""
    name = full[:len(full) - len(body)].strip() if body and full.endswith(body) else full
    src = iw.attributes.get("data-src", "") if iw is not None else ""
    m = _CDN_DAY.search(src or "")
    return name, body, src, (m.group(1) if m else "")


def fetch() -> list[Item]:
    rows = []
    seen = set()
    with base.client() as c:
        for path, label in MENU_PATHS.items():
            r = base.retry(lambda: c.get(ROOT + path))
            r.raise_for_status()
            time.sleep(DELAY)
            for con in HTMLParser(r.text).css("div.item_container._item_container"):
                name, desc, src, day = _card(con)
                if not name:
                    continue           # 포스터 칸(no_content)은 이름이 없다
                key = name.replace(" ", "")
                if key in seen:
                    continue
                seen.add(key)
                rows.append((name, desc, src, day, label))

    if len(rows) < MIN_ITEMS:
        raise RuntimeError(f"카페인중독 {len(rows)}건 — item_container 선택자가 "
                           "깨졌거나 메뉴 경로가 바뀌었다")
    if len(rows) > MAX_ITEMS:
        raise RuntimeError(f"카페인중독 {len(rows)}건 — 메뉴 경로가 늘어났다. 확인 필요")

    # 일괄 재업로드일을 센다. 박아두지 않고 매번 센다(docstring §신상 신호).
    tally = {}
    for _n, _d, _s, day, _l in rows:
        if day:
            tally[day] = tally.get(day, 0) + 1
    bulk = {d for d, n in tally.items() if n / len(rows) > _BULK_SHARE}

    items = []
    for name, desc, src, day, label in rows:
        stamped = "" if (not day or day in bulk) else f"{day[:4]}-{day[4:6]}-{day[6:]}"
        items.append(Item(
            brand=BRAND,
            name=name,
            desc=desc,
            image=src,
            category=label,
            uploaded_at=stamped,
            # 브랜드가 신제품이라고 말한 적이 없다. 날짜로만 판정한다(docstring).
            is_new=None,
        ))
    items.sort(key=lambda i: i.uploaded_at, reverse=True)
    return items
