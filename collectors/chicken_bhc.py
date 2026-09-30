"""bhc치킨.

bhc.co.kr 도 Next.js(App Router)라 HTML 에는 상품이 없고, 화면은 같은 도메인의
/api/v1/web/* 을 클라이언트에서 받아 채운다. 쿠키·세션 없이 열린다. 브라우저 불필요.

신제품 신호가 셋 다 있는 드문 브랜드다.
  - '신메뉴'(cateIdx=22) 전용 카테고리가 따로 있고,
  - 모든 상품에 isNew(Y/N) 플래그가 붙어 있으며,
  - 이미지 파일명이 20260709_093529_… 라 업로드 시각이 그대로 박혀 있다.
신메뉴 카테고리는 isNew=Y 의 부분집합이라(3건 ⊂ 13건) 판정은 isNew 로 하고,
카테고리는 그냥 목록 소스 중 하나로 같이 훑는다.

출시일을 직접 알려주는 필드는 없어서 released_at 은 비우고, 파일명 타임스탬프는
mega.py 와 같은 의미의 uploaded_at 으로 넣는다.

⚠️ 상품별 페이지가 없다. 2026-09-30 실측: 목록 화면에서 상품을 눌러도 주소는
그대로고 카드가 제자리에서 펼쳐질 뿐이다(앵커·해시도 없다). productCd 로 열 수 있는
건 JSON 을 뱉는 /api/v1/web/products/{productCd} 뿐이라 링크로 쓰면 안 된다.
그래서 url 은 사람이 보는 분류 페이지 /menu/{cateIdx} 까지만 채운다. 상품 하나를
집어주진 못해도, 그 상품이 실제로 실려 있는 페이지이고 base.SITES 폴백(치킨 분류)보다
가깝다.

가격은 상세(/products/{productCd})에만 있고 Item 에 자리가 없어 받지 않는다.
"""
import re
import time

from . import base
from .base import Item

BRAND = "bhc치킨"
SITE = "https://www.bhc.co.kr"
API = SITE + "/api/v1/web"
MAX_CATEGORIES = 40  # 폭주 방지. 현재 대/소 합쳐 18개.
DELAY = 0.25         # 요청 간격(초)


def _uploaded_at(img_url: str) -> str:
    """이미지 파일명 앞의 업로드 타임스탬프(20260709_093529)를 날짜로."""
    m = re.search(r"/(\d{4})(\d{2})(\d{2})_\d{6}_", img_url or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def _body(client, path: str):
    r = base.retry(lambda: client.get(f"{API}{path}"))
    r.raise_for_status()
    return r.json().get("body") or []


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        # 소분류는 현재 전부 0건을 돌려주지만, 상품이 그리로 옮겨가도 놓치지 않게 같이 본다.
        cats = []
        for top in _body(c, "/categories/list"):
            cats.append((top["cateIdx"], top["cateNm"]))
            for sub in top.get("subCateList") or []:
                cats.append((sub["cateIdx"], sub["cateNm"]))

        for cid, cname in cats[:MAX_CATEGORIES]:
            time.sleep(DELAY)
            for p in _body(c, f"/categories/{cid}/products"):
                name = " ".join((p.get("productNm") or "").split())
                if not name:
                    continue
                labels = []
                if p.get("isNew") == "Y":
                    labels.append("NEW")
                if p.get("isBest") == "Y":
                    labels.append("BEST")
                if p.get("isLimited") == "Y":
                    labels.append("한정")

                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=" ".join((p.get("description") or "").split()),
                    image=p.get("mainImg") or "",
                    labels=labels,
                    category=cname,
                    uploaded_at=_uploaded_at(p.get("mainImg") or ""),
                    is_new=p.get("isNew") == "Y",
                    # 상품별 주소가 없어 분류 페이지까지만. 위 ⚠️ 참고.
                    url=f"{SITE}/menu/{cid}",
                    # 버거 세트와 '치킨(반)+라이스+콜라' 조합은 구성 상품이라 신제품이 아니다
                    # 세트는 promo 가 아니다. collect.drop_sets() 가 이름으로 거른다.
                    # promo 는 할인·행사 전용인데 bhc 는 그런 표시가 없다.
                    promo=False,
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
    return items
