"""세븐일레븐.

신상품은 카테고리별 asp 페이지가 아니라 /product/presentList.asp 의 탭에 있다.
(/product/hitProductList.asp 를 열면 pTab=8 로 POST 재전송하는 빈 폼만 돌아온다.)
POST 만으로 서버가 완성된 HTML 을 돌려주므로 브라우저 불필요. 인코딩은 UTF-8.

목록은 두 군데서 긁는다.
- 신상품 탭(pTab=8): 첫 화면 13건은 presentList.asp 가 그리고, 나머지는
  listMoreAjax.asp 가 HTML 조각으로 준다. 첫 화면의 intPageSize 는 먹지 않는다.
- Fresh Food(도시락·김밥·샌드위치): dosirakNewMoreAjax.asp 가 목록 전체를
  통째로 다시 그려주는 구조라 넉넉한 크기로 한 번만 부르면 끝난다.
PB 전용 탭(pTab=5, 7-Select)도 같은 방식으로 붙지만 신제품 목록이 아니라 뺐다.

주의 두 가지.
- listMoreAjax.asp 는 '신상품' 배지를 안 그린다(PB·1+1·할인은 그린다).
  그래서 배지가 살아있는 첫 화면을 먼저 담고 뒷페이지를 덧붙인다.
- 상품 설명 필드가 사이트 어디에도 없다. 상세 페이지(presentView.asp)의 설명란도
  상품명을 그대로 반복할 뿐이라 상세를 긁을 이유가 없다. 그래서 desc 는 빈 값이다.
  가격은 목록에 있지만 Item 계약에 없어서 버린다.
"""
import time
import httpx
from selectolax.parser import HTMLParser

from .base import Item

BRAND = "세븐일레븐"
BASE = "https://www.7-eleven.co.kr"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")
TAB_NEW = "8"          # presentList.asp 의 신상품 탭
PAGE_SIZE = 200        # 더보기 한 번에 받는 건수. 현재 두 목록 다 한 번이면 덮인다.
MAX_PAGES = 15         # 폭주 방지. 현재 섹션당 1~2회.
DELAY = 1.0            # 낡은 ASP 서버라 몰아치지 않는다
PLACEHOLDER = "/front/img/product/"   # 사진 없는 상품에 물려주는 디폴트 이미지 경로


def _post(c: httpx.Client, path: str, data: dict) -> str:
    r = c.post(BASE + path, data=data)
    r.raise_for_status()
    time.sleep(DELAY)
    return r.text


def _cards(html: str, category: str) -> list[Item]:
    """목록 페이지든 더보기 조각이든 같은 카드 마크업을 쓴다."""
    tree = HTMLParser(html)
    root = tree.css_first("ul#listUl") or tree.body
    out = []
    for li in root.css("li"):
        pic = li.css_first(".pic_product")
        if pic is None:                       # 섹션 제목·MORE 버튼·태그 li
            continue

        img = pic.css_first("img")
        src = (img.attributes.get("src") or "") if img else ""
        name_node = pic.css_first(".infowrap .name")
        name = " ".join(name_node.text().split()) if name_node else ""
        if not name and img:
            name = " ".join((img.attributes.get("alt") or "").split())
        if not name or name == "디폴트 이미지":
            continue

        out.append(Item(
            brand=BRAND,
            name=name,
            image="" if not src or src.startswith(PLACEHOLDER) else BASE + src,
            labels=[t.text().strip() for t in li.css("ul.tag_list_01 li") if t.text().strip()],
            category=category,
        ))
    return out


def _new_products(c: httpx.Client) -> list[Item]:
    """신상품 탭. 첫 화면(배지 있음) + 더보기 페이지."""
    items = _cards(_post(c, "/product/presentList.asp", {"pTab": TAB_NEW}), "신상품")

    # 더보기는 2페이지부터. 서버가 첫 13건을 건너뛴 위치에서 잘라준다.
    for page in range(2, MAX_PAGES + 2):
        got = _cards(_post(c, "/product/listMoreAjax.asp", {
            "intPageSize": PAGE_SIZE, "intCurrPage": page,
            "cateCd1": "", "cateCd2": "", "cateCd3": "", "pTab": TAB_NEW}), "신상품")
        items += got
        if len(got) < PAGE_SIZE:              # 덜 왔으면 마지막 페이지
            break
    return items


def _fresh_food(c: httpx.Client) -> list[Item]:
    """Fresh Food. 요청한 건수만큼 목록을 처음부터 다시 그려준다."""
    items: list[Item] = []
    size = PAGE_SIZE
    for _ in range(MAX_PAGES):
        items = _cards(_post(c, "/product/dosirakNewMoreAjax.asp",
                             {"intPageSize": size, "pTab": ""}), "Fresh Food")
        if len(items) < size:                 # 요청한 것보다 적게 왔으면 다 받은 것
            break
        size *= 2                             # 딱 맞게 왔으면 잘렸을 수 있으니 넓혀서 다시
    return items


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with httpx.Client(headers={"User-Agent": UA}, timeout=30, follow_redirects=True) as c:
        # 신상품을 먼저 담아야 같은 상품이 Fresh Food 에도 있을 때 배지를 안 잃는다
        for it in _new_products(c) + _fresh_food(c):
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)
    return items
