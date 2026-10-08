"""피자헛.

사이트가 Angular SPA 라 어느 경로를 받아도 12KB짜리 빈 껍데기만 온다(HTML 스크랩 불가).
대신 목록을 채우는 /api/menu/* 가 쿠키·토큰 없이 그냥 열린다. 그래서 JSON 만 받는다.
브라우저 불필요.

매장별 API 라 storeCd 가 필요한데, 사이트 자신이 매장 미선택 상태에서 쓰는 기본값이
'0996' 이다(main 번들의 getReadStore() 기본 반환값). 그걸 그대로 쓴다.
피자 목록만은 /api/menu/pizza/all/DELIVERY 로 매장 없이 받아진다.

신제품 신호가 두 개 다 있다. 2026-09-30 실측:
  - badge 필드에 NEW / BEST / NOTHING 이 온다. NEW 가 브랜드의 신제품 표시다.
  - saleStartDate 가 실제 판매 시작일이다(UTC 로 오고 KST 자정에 해당). 92건 중
    피자 외 전부에 들어있고, 피자는 사이즈(items[]) 쪽에 들어있다. 가장 강한 신호.
badge 는 손으로 관리해서 낡는다. '화이트 트러플 머쉬룸' 은 2025-09-22 출시인데 아직
NEW 고, 2026-04 출시한 파스타는 NOTHING 이다. 그래서 NEW 는 True 로 올리되,
NOTHING·BEST 를 False 로 뒤집지는 않는다(배지 없음 = 신제품 아님, 이 아니다).
신제품 판정은 released_at 을 기준으로 하는 게 맞다.

세트·콤보는 lclass 가 'S' 로 와서 그대로 promo 로 찍는다(파스타헛 [세트]/[콤보] 24건).
핫딜·1+1(/menu/hotdeal, /menu/oneplusone)은 통째로 행사라 아예 받지 않는다.
DIY 하프앤하프(list/halfnhalf)와 세트(list/set)도 뺀다. 상품이 아니라 조합 화면이고
상품 이미지가 아예 없다. 치킨(list/chicken)은 sideAndBeverage 에 전부 들어있어 안 받는다.

이미지는 API 에 없다(image·thumb 가 전부 null). 번들의 getMenuImage() 를 따라가면
<CDN>/img/menu/<코드>_<사이즈>.png 인데, 어떤 코드·사이즈를 쓰는지가 분류마다 달라서
후보를 순서대로 HEAD 로 찔러 첫 200 을 쓴다. 파스타헛 세트/콤보 등 일부는 어느
후보도 없어서 빈 값으로 남는다(실측 92건 중 30건쯤).

상품 페이지는 /menu/pizza/all/<digitalKey> 다. 번들의 goNavigate() 가 상품을 누를 때
기본으로 타는 경로(["/menu/pizza/", type, rpstMenuCd])이고, type 자리에 목록을 받은
'all' 을 넣으면 피자·파스타·사이드·플랫츠·세트가 전부 그 상품 화면으로 뜬다(실측).
digitalKey 는 이미 받은 응답에 있어 추가 요청은 없다. Angular SPA 라 HTML 만 받으면
어느 주소든 같은 껍데기가 오니, 검증은 브라우저 렌더로 했다.

가격은 JSON 에 있지만(price/memberDlv 등) Item 에 자리가 없어 버린다.
"""
import time
from datetime import datetime, timedelta, timezone

from . import base
from .base import Item

BRAND = "피자헛"
SITE = "https://www.pizzahut.co.kr"
API = SITE + "/api"
STORE = "0996"          # 사이트가 매장 미선택 시 쓰는 기본 매장 코드
IMG_ROOT = "https://akamai.pizzahut.co.kr/2020pizzahut-prod/public/img/menu/"
KST = timezone(timedelta(hours=9))
DELAY = 0.1             # 요청 간격(초). 이미지 확인 HEAD 가 100여 회라 반드시 둔다.

# (분류명, 경로). 분류명은 엔드포인트가 뜻하는 그대로다. 겹치는 상품은 key 로 지운다.
SOURCES = (
    ("피자",      "/menu/pizza/all/DELIVERY"),
    ("사이드·음료", f"/menu/{STORE}/list/sideAndBeverage"),
    ("플랫츠",     f"/menu/{STORE}/list/npanflatzz"),
)


def _clean(s) -> str:
    return " ".join((s or "").split())


def _released_at(row: dict) -> str:
    """saleStartDate 를 KST 날짜로. 피자는 사이즈별로 있어서 가장 이른 걸 쓴다."""
    stamps = [row.get("saleStartDate")] + [i.get("saleStartDate")
                                           for i in row.get("items") or []]
    stamps = [s for s in stamps if s]
    if not stamps:
        return ""
    # strptime 은 마이크로초가 없으면 죽는다. fromisoformat 이 둘 다 받는다.
    dt = datetime.fromisoformat(min(stamps))
    return dt.astimezone(KST).strftime("%Y-%m-%d")


def _image_candidates(row: dict) -> list[str]:
    """분류마다 쓰는 코드·사이즈가 달라서 실측으로 정한 우선순위."""
    dk, mc = row.get("digitalKey") or "", row.get("menuCd") or ""
    mclass, sclass = row.get("mclass"), row.get("sclass")
    if mclass == "SD" and sclass == "AT":     # 사이드·치킨은 menuCd + s
        order = [f"{mc}_s", f"{dk}_s", f"{dk}_l"]
    elif mclass == "SD":                      # 파스타 등은 digitalKey + l
        order = [f"{dk}_l", f"{dk}_s", f"{mc}_s"]
    else:                                     # 피자·플랫츠·음료는 digitalKey + s
        order = [f"{dk}_s", f"{mc}_s", f"{dk}_l"]
    return [IMG_ROOT + n + ".png" for n in order if not n.startswith("_")]


def _image(c, row: dict, cache: dict) -> str:
    dk = row.get("digitalKey") or ""
    if dk in cache:
        return cache[dk]
    url = ""
    for cand in _image_candidates(row):
        try:
            if c.head(cand).status_code == 200:
                url = cand
                break
        except Exception:
            pass
        time.sleep(DELAY)
    cache[dk] = url
    return url


def fetch() -> list[Item]:
    items: list[Item] = []
    seen, img_cache = set(), {}
    headers = {"Referer": "https://www.pizzahut.co.kr/menu"}
    with base.client(headers=headers) as c:
        for category, path in SOURCES:
            r = base.retry(lambda: c.get(API + path))
            r.raise_for_status()
            time.sleep(DELAY)

            for row in r.json():
                name = _clean(row.get("rpstName"))
                if not name:
                    continue
                badge = row.get("badge")
                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en=_clean((row.get("items") or [{}])[0].get("nameEn")
                                   or row.get("nameEn")),
                    desc=_clean(row.get("rpstDesc")),
                    labels=[badge] if badge in ("NEW", "BEST") else [],
                    category=category,
                    released_at=_released_at(row),
                    # NEW 만 신제품 표시로 읽는다. NOTHING·BEST 는 '아니다' 가 아니라
                    # '모른다' 다. 위 주석의 배지 노후화 참고.
                    is_new=True if badge == "NEW" else None,
                    url=(f"{SITE}/menu/pizza/all/{row['digitalKey']}"
                         if row.get("digitalKey") else ""),
                    # lclass=="S" 는 세트·콤보다. collect.drop_sets() 가 이름으로
                    # 거르므로 promo 로 찍지 않는다. 그러면 신메뉴 세트가 이중으로
                    # 잘린다(2026-04 출시 파스타 17건이 그랬다).
                    promo=False,
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                it.image = _image(c, row, img_cache)
                items.append(it)
    return items
