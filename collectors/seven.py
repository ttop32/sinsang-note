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

신제품 판정은 '배지'가 아니라 '탭'을 근거로 한다. 2026-09-30 실측:
  - presentList.asp?pTab=8 의 탭 이름이 그대로 '신상품'이고, 첫 화면 13건은
    13건 모두 '신상품' 배지를 달고 있다(일부만 붙는 게 아니었다).
  - 배지가 뒷페이지에 없는 건 listMoreAjax.asp 가 행사 배지(1+1·2+1·할인·증정)만
    그리고 신상품 배지는 아예 렌더하지 않기 때문이다. 상품이 구상품이라서가 아니다.
  - listMoreAjax.asp 가 pTab 을 정말 타는지 확인했다. pTab=8 / 5 / "" 로 같은
    페이지를 부르면 결과가 전부 다르다. 즉 뒷페이지도 신상품 탭의 연속이다.
그래서 이 탭에서 온 상품은 is_new=True 로 둔다. Fresh Food 는 신상품 탭이 아니라
식품 카테고리 목록이므로 is_new=None(모름)이다.

행사 배지를 promo 로 올릴지는 근거가 있느냐로 가른다. 신상품 탭 99건 중 86건이
1+1·2+1 을 달고 있는데, 이건 갓 나온 상품에 붙는 도입 행사지 '행사라서 실린 상품'이
아니다. 브랜드가 신상품이라고 말한 걸 행사 배지를 이유로 지우면 이 브랜드 신제품이
87% 사라진다. 그래서 신상품 탭은 promo 를 세우지 않고 배지는 labels 로만 남긴다.
반대로 Fresh Food 는 신제품이라는 근거가 없으므로, 행사 배지가 붙은 건 행사 상품으로
본다(근거 없는 상품을 행사 배지만 믿고 신상인 척 내보내지 않는다).

출시일·등록일은 목록·상세 어디에도 없다. 상세(presentView.asp)의 날짜는 진행중인
이벤트의 행사 기간(2026-09-01 ~ 2026-09-30)이지 상품 출시일이 아니라 쓰지 않는다.
상품 설명 필드도 사이트 어디에도 없다. 상세의 설명란은 상품명을 그대로 반복할 뿐이라
상세를 긁을 이유가 없다. 그래서 desc 는 빈 값이다.
다만 상세 주소는 목록 카드의 fncGoView('062598') 에서 그대로 나오므로, 긁지는 않고
Item.url 로만 넘긴다(신상품 탭 → presentView.asp, Fresh Food → bestdosirakView.asp).
원래는 hidden 폼 POST 지만 GET 으로도 같은 화면이 나오는 걸 확인했다.
가격은 목록에 있지만 Item 계약에 없어서 버린다.
"""
import re
import time
import httpx
from selectolax.parser import HTMLParser

from . import base
from .base import UA, Item

BRAND = "세븐일레븐"
BASE = "https://www.7-eleven.co.kr"
TAB_NEW = "8"          # presentList.asp 의 신상품 탭
PAGE_SIZE = 200        # 더보기 한 번에 받는 건수. 현재 두 목록 다 한 번이면 덮인다.
MAX_PAGES = 15         # 폭주 방지. 현재 섹션당 1~2회.
MAX_PAGE_SIZE = 1000   # 배증 상한. 낡은 ASP 서버에 비상식적인 크기를 요구하지 않는다.
DELAY = 1.0            # 낡은 ASP 서버라 몰아치지 않는다
PLACEHOLDER = "/front/img/product/"   # 사진 없는 상품에 물려주는 디폴트 이미지 경로

# 행사 배지. 이게 붙었다고 구상품인 건 아니고, '신제품 근거가 없을 때'에만 행사로 본다.
PROMO_TAGS = {"1+1", "2+1", "할인", "증정", "세일"}

# 상세 페이지. 목록마다 상세가 따로다(신상품 탭 ↔ Fresh Food).
# 원래는 pCd 를 hidden 폼에 넣어 POST 하지만 GET 으로도 같은 화면이 나온다(2026-09-30 실측).
VIEW_NEW = "/product/presentView.asp"
VIEW_FF = "/product/bestdosirakView.asp"


def _post(c: httpx.Client, path: str, data: dict) -> str:
    r = c.post(BASE + path, data=data)
    r.raise_for_status()
    time.sleep(DELAY)
    return r.text


def _pcd(li) -> str:
    """상품코드. 상세 링크가 a 태그가 아니라 fncGoView('128106') 로만 붙어 있다."""
    a = li.css_first("a.btn_product_01")
    m = re.search(r"fncGoView\('(\d+)'\)", a.attributes.get("href", "") or "") if a else None
    return m.group(1) if m else ""


def _cards(html: str, category: str, is_new: bool | None, view: str) -> list[Item]:
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

        # '신상품' 배지는 첫 화면에만 그려지고 더보기 AJAX 응답엔 없다. 같은 탭인데
        # 앞 13건만 배지가 붙어 화면이 일관성을 잃으므로 labels 에선 빼고,
        # 신제품 여부는 배지 대신 탭(is_new 인자)으로 판정한다.
        labels = [t for t in (x.text().strip() for x in li.css("ul.tag_list_01 li"))
                  if t and t != "신상품"]

        # 상품코드는 목록 카드 안에 이미 있다. 상세를 열어보지 않고 주소만 조립한다.
        pcd = _pcd(li)

        out.append(Item(
            brand=BRAND,
            name=name,
            image="" if not src or src.startswith(PLACEHOLDER) else BASE + src,
            labels=labels,
            category=category,
            is_new=is_new,
            # 신제품 근거가 있으면 행사 배지는 도입 행사로 보고 넘긴다.
            promo=is_new is not True and any(t in PROMO_TAGS for t in labels),
            url=f"{BASE}{view}?pCd={pcd}" if pcd else "",
        ))
    return out


def _new_products(c: httpx.Client) -> list[Item]:
    """신상품 탭. 탭 자체가 신상품이라 여기서 온 건 전부 is_new=True."""
    items = _cards(_post(c, "/product/presentList.asp", {"pTab": TAB_NEW}),
                   "신상품", True, VIEW_NEW)

    # 더보기는 2페이지부터. 서버가 첫 13건을 건너뛴 위치에서 잘라준다.
    for page in range(2, MAX_PAGES + 2):
        got = _cards(_post(c, "/product/listMoreAjax.asp", {
            "intPageSize": PAGE_SIZE, "intCurrPage": page,
            "cateCd1": "", "cateCd2": "", "cateCd3": "", "pTab": TAB_NEW}),
            "신상품", True, VIEW_NEW)
        items += got
        if len(got) < PAGE_SIZE:              # 덜 왔으면 마지막 페이지
            break
    return items


def _fresh_food(c: httpx.Client) -> list[Item]:
    """Fresh Food. 요청한 건수만큼 목록을 처음부터 다시 그려준다.

    신상품 탭이 아니라 식품 카테고리 목록이라 신제품 여부를 알 수 없다(is_new=None).
    """
    items: list[Item] = []
    size = PAGE_SIZE
    for _ in range(MAX_PAGES):
        items = _cards(_post(c, "/product/dosirakNewMoreAjax.asp",
                             {"intPageSize": size, "pTab": ""}), "Fresh Food", None, VIEW_FF)
        if len(items) < size:                 # 요청한 것보다 적게 왔으면 다 받은 것
            break
        size = min(size * 2, MAX_PAGE_SIZE)                             # 딱 맞게 왔으면 잘렸을 수 있으니 넓혀서 다시
    return items


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        # 신상품을 먼저 담아야 같은 상품이 Fresh Food 에도 있을 때 is_new 를 안 잃는다
        for it in _new_products(c) + _fresh_food(c):
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)
    return items
