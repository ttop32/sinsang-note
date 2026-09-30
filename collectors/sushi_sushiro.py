"""스시로(스시로한국).

/pm '이달의 한정메뉴' 한 축만 받는다. SSR 이고 브라우저 불필요.
카드가 전부 data 속성으로 구조화돼 있어(`data-menu-name-ko/-ja/-price/-image`)
파싱 실패 위험이 이 브랜드군에서 가장 낮다.

2026-09-30 실측:
  - `/pm?page=1..6` 총 46건(8·8·8·8·8·6). page=7 을 넣으면 서버가 6페이지를
    그대로 되돌려주므로 범위 초과는 '전부 기존 키'로 걸러 끊는다(메가 선례).
  - 조사 문서는 카드를 `<article class="new-menu-card">` 라고 적었는데 실제로는
    `<div class="card ... menu-card menu-modal-trigger">` 다. data 속성은 그대로라
    태그·클래스가 아니라 `[data-menu-name-ko]` 로 잡는다.
  - 그랜드메뉴(/gm)는 받지 않는다. 상시 메뉴라 신제품 신호가 없다.

신제품 신호:
  is_new  전건 True. `/pm` 은 "이달에만 즐길 수 있는 한정 메뉴" 전용 페이지고
          카드의 data-menu-group 도 전건 '이달의 한정메뉴' 다.
          배스킨라빈스 '이달의 맛'과 같은 성격으로 다룬다.
          ⚠️ 유보: '이 달에 파는 것'이지 '이 달에 처음 나온 것'이 아니다.
          매달 갈리는 건 맞지만 지난 시즌 재등장 품목이 섞일 수 있다.
  released_at  비운다. 페이지 어디에도 날짜 텍스트가 없다.
          유일한 월 표시는 배너 이미지 파일명(`ad/homepage/pm_wide/2609_wide.jpg`
          → 2026-09)인데, 이건 상품별 출시일이 아니라 배너 한 장의 이름이다.
          파일명을 날짜로 쓰지 않는다는 이 레포 방침(메가·할리스 선례)에 그대로 걸린다.
  uploaded_at  비운다. 상품 이미지 파일명이 `002232.jpg` 같은 일련번호라 시각이 없다.

url 은 비운다. 카드를 누르면 같은 페이지의 모달이 열릴 뿐 상품별 URL 이 없다.
(base.SITES 에 '스시로' 를 넣어 두면 카드가 /pm 으로 떨어진다. 등록은 레지스트리 몫이다.)

name_en 에는 일본어명(data-menu-name-ja)을 담는다. 영문명이 아예 없고,
이 브랜드에서 한글명 다음으로 브랜드가 직접 주는 이름이 이것뿐이다.

이용약관: 없다. 2026-09-30 실측 — 푸터 링크가 브랜드스토리·이달의 한정메뉴·
그랜드메뉴·테이크아웃/배달안내·전국매장안내·SNS 뿐이고 약관·개인정보 링크가 하나도 없다.
`/terms` `/privacy` `/policy` `/agreement` 도 전부 404(JSON 본문)다.
robots.txt 도 404 라 제한 없음. 그래서 요청 간격을 넉넉히 둔다.

가격(data-menu-price, 예: "5,000")도 같이 오지만 Item 에 자리가 없어 버린다.
"""
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "스시로"
HOST = "https://www.sushiro.co.kr"
PM_PATH = "/pm"
MAX_PAGES = 20   # 폭주 방지. 현재 6페이지.
DELAY = 2.0      # 요청 간격(초). robots 가 없는 사이트라 보수적으로 둔다.


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            r = base.retry(lambda: c.get(HOST + PM_PATH, params={"page": page}))
            r.raise_for_status()
            cards = HTMLParser(r.text).css("[data-menu-name-ko]")
            if not cards:
                # 1페이지가 비면 셀렉터가 깨진 것이다. 조용한 0건 수집을 막는다.
                if page == 1:
                    raise RuntimeError("스시로 /pm: 상품 0건 — 셀렉터가 깨졌을 수 있다")
                break

            parsed = []
            for card in cards:
                a = card.attributes
                name = _clean(a.get("data-menu-name-ko", ""))
                if not name:
                    continue
                parsed.append(Item(
                    brand=BRAND,
                    name=name,
                    name_en=_clean(a.get("data-menu-name-ja", "")),
                    image=a.get("data-menu-image", "") or "",
                    category=_clean(a.get("data-menu-group", "")),
                    is_new=True,
                ))

            # 범위를 넘긴 page 는 서버가 마지막 페이지를 되돌려준다. 전부 기존 키면 종료.
            if not parsed or all(it.key in seen for it in parsed):
                break

            for it in parsed:
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            time.sleep(DELAY)
    return items
