"""스타벅스 코리아.

drink_list.do / food_list.do 는 목록 자리를 빈 <ul> 로 내려보내고 jQuery 템플릿으로
채우는 구조라 HTML 을 긁어도 상품이 0건이다. 실제 데이터는 카테고리별 정적 JSON
/upload/json/menu/<카테고리코드>.js 이고, 쿠키·세션·리퍼러 없이 그냥 받아진다.
그래서 목록 페이지는 건너뛰고 JSON 만 카테고리 수만큼 직접 받는다. 브라우저 불필요.

영문명(product_ENGNM)은 이 JSON 에선 전부 빈 값이고 상세 페이지
drink_view.do?product_cd= 의 인라인 drinkData 에만 들어있다. 상품당 1회 요청(300건
이상, 건당 140KB)이라 비용이 안 맞아서 받지 않고 빈 값으로 둔다.
가격은 어느 경로에도 없다.
"""
import json
import re
import time
import httpx

from . import base
from .base import UA, Item

BRAND = "스타벅스"
# 2026-09-30 현재 www 서브도메인의 DNS 레코드가 사라졌다(외부 네트워크에서도 ENOTFOUND).
# 어느 쪽이 살아나도 자동으로 붙도록 후보를 순회한다.
HOSTS = ("https://www.starbucks.co.kr", "https://starbucks.co.kr")
JSON_PATH = "/upload/json/menu/{code}.js"
MAX_CATEGORIES = 40  # 폭주 방지. CATEGORIES 가 고정 리터럴이라 지금은 걸릴 일이 없다.
DELAY = 0.5          # 요청 간격(초)

# 목록 페이지 getCateCodeCng() 의 코드 ↔ 분류 체크박스 라벨.
# 앞 10개가 음료(drink_list.do), 뒤 7개가 푸드(food_list.do).
# 푸드의 '기타 푸드'(W0000123)는 사이트에서 주석 처리돼 있어 뺐다.
CATEGORIES = [
    ("W0000171", "콜드 브루 커피"),
    ("W0000060", "브루드 커피"),
    ("W0000003", "에스프레소"),
    ("W0000004", "프라푸치노"),
    ("W0000005", "블렌디드"),
    ("W0000422", "스타벅스 리프레셔"),
    ("W0000061", "스타벅스 피지오"),
    ("W0000075", "티(티바나)"),
    ("W0000053", "기타 제조 음료"),
    ("W0000062", "스타벅스 주스(병음료)"),
    ("W0000013", "브레드"),
    ("W0000032", "케이크"),
    ("W0000033", "샌드위치 & 샐러드"),
    ("W0000054", "따뜻한 푸드"),
    ("W0000055", "과일 & 요거트"),
    ("W0000056", "스낵 & 미니 디저트"),
    ("W0000064", "아이스크림"),
]


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _image(row: dict) -> str:
    """템플릿과 동일하게 www → image 로 바꾼 호스트에 파일 경로를 붙인다."""
    host = row.get("img_UPLOAD_PATH") or ""
    path = row.get("file_PATH") or ""
    return host.replace("www", "image", 1) + path if path else ""


def _uploaded_at(row: dict) -> str:
    """new_SDATE(20260928) = 출시일. 없는 상품도 있어서 그 땐 빈 값."""
    d = row.get("new_SDATE") or ""
    return f"{d[:4]}-{d[4:6]}-{d[6:]}" if re.fullmatch(r"\d{8}", d) else ""


def _labels(row: dict) -> list:
    """목록 템플릿이 붙이는 마크와 같은 기준."""
    out = []
    if row.get("newicon") == "Y":
        out.append("NEW")
    if row.get("sell_CAT") == "1":
        out.append("시즌 한정")
    if row.get("sold_OUT") == "Y":
        out.append("SOLD OUT")
    return out


def _live_host(c) -> str:
    """JSON 을 실제로 돌려주는 호스트를 고른다. 전부 죽었으면 마지막 오류를 올린다.

    apex(starbucks.co.kr)는 DNS 제공업체의 빈 파킹 페이지를 200 으로 준다.
    상태코드만 보면 살아있다고 오판하므로 JSON 파싱까지 확인한다.
    """
    last = None
    probe = JSON_PATH.format(code=CATEGORIES[0][0])
    for h in HOSTS:
        try:
            r = c.get(h + probe)
            r.raise_for_status()
            json.loads(r.text)
            return h
        except Exception as e:                       # 연결 실패·DNS·HTTP·비 JSON 전부
            last = f"{h} → {type(e).__name__}"
    raise RuntimeError(f"스타벅스 호스트 전부 사용 불가 ({last})") from None


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        host = _live_host(c)
        for code, label in CATEGORIES[:MAX_CATEGORIES]:
            r = base.retry(lambda: c.get(host + JSON_PATH.format(code=code)))
            r.raise_for_status()
            # 무효한 카테고리 코드에 스타벅스는 404 가 아니라 200 + HTML 오류페이지를 준다.
            # 조용히 넘기면 그 카테고리가 통째로 증발하므로 예외로 올려 수집을 실패시킨다.
            try:
                rows = json.loads(r.text).get("list", [])
            except json.JSONDecodeError:
                raise RuntimeError(
                    f"{code}({label}): JSON 이 아닌 응답. 카테고리 코드가 폐기됐을 수 있다") from None

            for row in rows:
                name = _clean(row.get("product_NM"))
                if not name:
                    continue
                # cate_NAME 이 브랜드가 준 소분류. '기타'는 정보가 없어 대분류로 대체.
                cate = _clean(row.get("cate_NAME"))
                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en=_clean(row.get("product_ENGNM")),
                    desc=_clean(row.get("content")),
                    image=_image(row),
                    labels=_labels(row),
                    category=cate if cate and cate != "기타" else label,
                    uploaded_at=_uploaded_at(row),
                )
                if it.key not in seen:        # 같은 상품이 두 카테고리에 걸쳐 있다
                    seen.add(it.key)
                    items.append(it)

            time.sleep(DELAY)
    return items
