"""본아이에프 8개 브랜드.

www.bonif.co.kr 의 메뉴 화면은 jsrender 템플릿뿐이라 HTML 에 상품이 없다. 대신
/static/js/common/api/menu.js 가 내부 API 주소를 그대로 노출한다. 그 API 가 쿠키·토큰·
리퍼러 없이 열려서 그쪽만 쓴다. 브라우저 불필요. 2026-09-30 실측.

  GET api.bonif.co.kr/brand/v1/menu?brdCd=<코드>      상품 전량 (페이징 없음)
  GET api.bonif.co.kr/brand/v1/category?brdCd=<코드>  카테고리 이름

**이 모듈은 브랜드가 8개다.** 한 API 에 brdCd 만 바꾸면 8개 브랜드가 모두 나오기에
파일을 쪼개지 않았다. 그래서 BRAND 상수 대신 BRANDS 목록을 내보낸다.
브랜드당 2요청, 전부 합쳐 16요청에 445건(2026-09-30)이다.

**상품마다 newYn Y/N 이 있다.** 이 프로젝트에서 is_new 를 True 와 False 양쪽으로
확정할 수 있는 몇 안 되는 소스다. 445건 중 Y 가 73건, N 이 372건이고 빈 값은 없었다.

**출시일은 없다.** 응답의 regDt/updDt 는 브랜드 레코드에 하나씩 붙은 것이고 상품에는
날짜 필드가 아예 없다. /brand/v1/menu/detail 도 실측했는데 태그 29종 어디에도 상품
날짜가 없었다(있는 건 allergyText·originText·menuFeature 뿐이고, 상세는 1건에 180KB라
전량 호출은 애초에 못 한다). 그래서 released_at 은 비운다.
uploaded_at 은 cmdtListImg 파일명 앞의 날짜(20260923_...)로 채운다. 상품 출시일이
아니라 이미지 업로드 날짜라 released_at 에 넣지 않는다.

브랜드 코드-이름은 www 헤더 네비게이션의 /brand/intro?brdCd= 링크와 API 응답의
brdNm 을 맞춰 확인했다. 조사 문서의 추정 순서와 달리 **BF101 이 본죽, BF102 가
본죽&비빔밥**이다(둘이 뒤바뀌어 있었다). BF114 만 두 이름이 엇갈린다 — 네비게이션
라벨은 '이지 브레드&커피'인데 API brdNm 과 상세 페이지 <title> 은 '이지브루잉커피'다.
데이터가 스스로 말하는 쪽을 택했다.

응답은 기본 XML 이지만 Accept: application/json 을 주면 JSON 으로 온다(실측).
파싱이 단순해지므로 JSON 을 쓴다.

가격(cmdtPrice)·열량·알레르기 정보가 API 에 있지만 Item 에 자리가 없어 버린다.
할인 필드(cmdtSalePrice)는 445건 전부 정가와 같거나 0이라 promo 는 전부 False 다.
"""
import html
import json
import re
import time

from . import base
from .base import Item

API = "https://api.bonif.co.kr/brand/v1"
SITE = "https://www.bonif.co.kr/brand/menu/detail"
IMG_ROOT = "https://cdn.bonif.co.kr/cmdt"
DELAY = 1.2  # 요청 간격(초)

# 브랜드 코드 → 브랜드명. 코드는 www 헤더 네비게이션에 박혀 있는 8개가 전부다.
CODES = {
    "BF101": "본죽",
    "BF102": "본죽&비빔밥",
    "BF104": "본도시락",
    "BF105": "본설렁탕",
    "BF107": "본우리반상",
    "BF111": "멘지",
    "BF113": "본흑염소·능이삼계탕",
    "BF114": "이지브루잉커피",
}

# 레지스트리가 등록할 브랜드명. 이 모듈이 뱉는 Item.brand 는 전부 이 안에 있다.
BRANDS = list(CODES.values())

# 매운맛 단계. 화면에는 고추 아이콘으로만 나오고 글자가 없어서 우리가 이름을 붙인다.
SPICY = {"1": "매운맛1", "2": "매운맛2", "3": "매운맛3"}


def _get(c, path: str, code: str) -> dict:
    r = base.retry(lambda: c.get(f"{API}/{path}", params={"brdCd": code}))
    r.raise_for_status()
    time.sleep(DELAY)
    # 응답에 BOM 이 붙는 걸 본 적은 없지만 헤더가 charset 을 두 번 말하는 서버라
    # utf-8-sig 로 벗겨두면 손해가 없다.
    return json.loads(r.content.decode("utf-8-sig"))


def _clean(s: str) -> str:
    """subExp 는 445건 중 124건에 <br> 이 섞여 들어온다. 태그를 털고 한 줄로 만든다."""
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", s or "")).split())


def _uploaded_at(img: str) -> str:
    """이미지 파일명 앞의 업로드 날짜(20260923_wK4_...)를 날짜로.

    released_at 에는 넣지 않는다. 브랜드가 말하는 출시일이 아니라 이미지를 올린
    날짜고, 실제로 사이트 개편 때 몰린 흔적이 있다(BF114 는 74건 중 32건이 2025-05).
    """
    m = re.match(r"(\d{4})(\d{2})(\d{2})_", img or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client(headers={"Accept": "application/json"}) as c:
        for code, brand in CODES.items():
            data = _get(c, "menu", code)["data"]

            # 응답이 말하는 브랜드명이 우리 표와 다르면 조용히 넘기지 않는다.
            # 브랜드명이 바뀌면 레지스트리 등록이 어긋나므로 드러나야 한다.
            said = (data.get("brand") or {}).get("brdNm") or ""
            if said and said != brand:
                raise RuntimeError(f"{code} 브랜드명이 바뀌었다: {brand} → {said}")

            cats = {x["cmdtCateIdx"]: x["cateNm"]
                    for x in _get(c, "category", code)["data"]["categoryList"]}

            for m in data.get("menuList") or []:
                name = _clean(m.get("cmdtNm"))
                if not name:
                    continue
                img = m.get("cmdtListImg") or ""
                new = m.get("newYn")
                it = Item(
                    brand=brand,
                    name=name,
                    desc=_clean(m.get("subExp")),
                    image=f"{IMG_ROOT}/{img}" if img else "",
                    labels=[SPICY[m["spicyCd"]]] if m.get("spicyCd") in SPICY else [],
                    category=cats.get(m.get("cmdtCateIdx"), ""),
                    uploaded_at=_uploaded_at(img),
                    is_new=True if new == "Y" else False if new == "N" else None,
                    url=f"{SITE}?brdCd={code}&cmdtIdx={m['cmdtIdx']}",
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)
    return items
