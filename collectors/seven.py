"""세븐일레븐.

목록은 두 군데서 긁는다. 둘은 신제품 근거의 질이 정반대다.
- Fresh Food(도시락·김밥·샌드위치): `dosirakNewMoreAjax.asp` 가 목록 전체를
  통째로 다시 그려주는 구조라 넉넉한 크기로 한 번만 부르면 끝난다.
  **여기에만 상품별 '신상품' 배지가 있다.** 이게 이 브랜드의 유일한 신제품 근거다.
- 신상품 탭(pTab=8): `presentList.asp` 가 첫 13건을, `listMoreAjax.asp` 가 나머지를
  HTML 조각으로 준다. 이름과 달리 신제품 근거가 못 된다(아래).
PB 전용 탭(pTab=5, 7-Select)도 같은 방식으로 붙지만 신제품 목록이 아니라 뺐다.
POST 만으로 서버가 완성된 HTML 을 돌려주므로 브라우저 불필요. 인코딩은 UTF-8.

## Fresh Food 의 '신상품' 배지가 진짜인 이유 (2026-10-01 실측)

`bestdosirakList.asp` 를 열면 페이지 안에 **"신상품 - 새로운 푸드를 만나보세요!"**
라는 섹션 제목(`h4.tit_2depth`)이 있고 그 아래 10건이 깔린다. 사람이 고른 매대다.
전체 목록(`dosirakNewMoreAjax.asp`, 136건)에서 배지를 세어보면:
  - 136건 중 **11건**만 '신상품' 이다(8%). 정적 페이지의 10건은 이 11건의 부분집합이다.
  - 나머지 배지는 '인기' 5건·'단체' 4건. **행사 배지(1+1·2+1·할인·증정)는 0건이다.**
    Fresh Food 목록 전체에 행사 배지가 한 개도 없다 — 행사 매대가 아니다.
  - 11건은 복가득담은한상도시락·치폴레치킨버거·BELT샌드처럼 실제로 갓 나온 것들이다.
즉 이 배지는 목록 전체에 깔리는 장식이 아니라 **상품별로 선별해서 붙는 표시**다.
그래서 Fresh Food 는 배지가 붙은 것만 is_new=True 로 올리고, 나머지는 is_new=None
(모름)으로 둔다. 목록 전체를 신상으로 미는 구조가 아니다.

## 신상품 탭(pTab=8)을 is_new 근거로 쓰지 않는 이유 (2026-10-01 실측)

이전 판은 '탭 이름이 신상품이니 거기서 온 76건은 전부 is_new=True' 로 뒀다.
그건 메뉴판 한 판을 통째로 신상으로 미는 구조이고, 실측으로 틀렸다.
  - **76건 중 행사 배지가 안 붙은 건 0건이다.** 1+1·2+1·할인이 전부 하나씩 달려 있다.
    "행사 라벨이 붙은 걸 신상으로 올리지 않는다"는 이 레포 규칙에 정면으로 걸린다.
  - 내용물이 수십 년 된 제품이다. 해태)연양갱·마즈)스니커즈·마즈)트윅스·
    롯데)말랑카우·크라운)땅콩캬라멜이 '신상품' 배지를 달고 올라온다.
  - 상품코드(`fncGoView('061235')`)가 오름차순으로 깔리는데 1페이지가 061235~119073,
    2페이지가 122665~138xxx 다. 즉 1페이지 13건이 목록에서 **가장 오래된** 축이다.
  - 이미지 경로(`/upload/product/<바코드>/...`)는 타임스탬프가 아니라 바코드다.
    (경로 자체도 robots.txt 의 `Disallow: /upload/` 라 우리가 두드릴 자리가 아니다.
     표시용으로 주소만 넘기고 HEAD 조차 보내지 않는다.)
  - 배지가 뒷페이지에 없는 건 상품이 구상품이라서가 아니라 `listMoreAjax.asp` 가
    신상품 배지를 아예 렌더하지 않기 때문이다. `intCurrPage=1` 로 같은 13건을
    다시 받아보면 **똑같은 13건이 배지만 빠진 채** 돌아온다. 즉 배지는 상품별
    표시가 아니라 탭 전체에 찍히는 장식이다 — Fresh Food 쪽과 정반대다.
  - `presentList.asp` 는 `intCurrPage` 를 무시한다(2·3 을 줘도 같은 13건).
그래서 이 탭은 is_new=None 으로 두고, 행사 배지가 붙은 건 promo 로 내보낸다.
사이트 메뉴 구조도 이 판단과 맞는다 — 이 탭은 `7prodList.asp`("PB상품/신상품")가
`pTab=5`(7-Select)로 POST 해서 들어가는 **PB·매대 묶음**이지 출시 목록이 아니다.

## 없는 것 (찾아봤고 없었다, 2026-10-01)

- **등록일·출시일**: 목록에도 상세에도 없다. `presentView.asp` 를 두 상품(138004,
  061235)에 대해 받아 날짜 문자열을 전부 뽑아보면 두 응답이 **완전히 같은 집합**
  (2024-02-07·2024-04-01·2026-10-01·2026-10-15·2026-10-31·2027-02-06·2027-12-31)
  이다. 상품별 값이 아니라 개인정보방침 개정일·진행 이벤트 기간 같은 페이지 상용구다.
  `dosirakNewMoreAjax.asp` 응답에도 날짜 문자열이 0건이다.
- **다른 신상품 경로**: `/product/` 아래 전 페이지를 훑었다. `hitProductList.asp`·
  `salecouponList.asp` 는 pTab 폼만 있는 빈 껍데기(5.7KB)고, `7cafe.asp`·
  `thanksgiving.asp` 는 상품 카드가 0건인 안내 페이지다.
- **보도자료**: 세븐일레븐은 GS25·오뚜기처럼 쓸 보도자료 소스가 없다.
  `7-eleven.co.kr` 에 뉴스 메뉴 자체가 없고, 공지사항(`noticeList.asp`)은 최근 10건이
  전부 시스템 점검·개인정보방침·이사회 운영 안내다. 운영사 사이트 `koreaseven.com`
  은 DNS 가 해석되지 않는다(NXDOMAIN).
그래서 released_at·uploaded_at 은 비운다. desc 도 비운다 — 상세의 설명란은 상품명을
그대로 반복할 뿐이라 상세를 긁을 이유가 없다.
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

# 상품별 신제품 배지. Fresh Food 에서만 선별해서 붙는다(136건 중 11건).
# 신상품 탭(pTab=8)에도 같은 글자가 찍히지만 그쪽은 탭 전체 장식이라 안 믿는다.
NEW_TAG = "신상품"

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


def _cards(html: str, category: str, is_new: bool | None, view: str,
           badge_is_new: bool = False) -> list[Item]:
    """목록 페이지든 더보기 조각이든 같은 카드 마크업을 쓴다.

    badge_is_new 를 켜면 상품별 '신상품' 배지를 신제품 근거로 읽는다(Fresh Food 전용).
    끄면 배지를 무시하고 호출자가 준 is_new 를 그대로 쓴다(신상품 탭). 두 목록에서
    같은 글자가 전혀 다른 의미라 한 함수에서 플래그로 가른다 — 근거는 docstring.
    """
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

        tags = [t for t in (x.text().strip() for x in li.css("ul.tag_list_01 li")) if t]
        # 화면엔 NEW 배지를 collect 가 따로 그린다. 같은 뜻을 두 번 찍지 않게 뺀다.
        labels = [t for t in tags if t != NEW_TAG]

        # Fresh Food 는 배지가 상품별로 선별돼 붙으므로 그게 곧 신제품 근거다.
        # 신상품 탭은 배지가 탭 전체 장식이라(그리고 뒷페이지엔 아예 안 그려진다)
        # 무시하고 호출자가 준 값을 쓴다.
        new = ((NEW_TAG in tags) or None) if badge_is_new else is_new

        # 상품코드는 목록 카드 안에 이미 있다. 상세를 열어보지 않고 주소만 조립한다.
        pcd = _pcd(li)

        out.append(Item(
            brand=BRAND,
            name=name,
            image="" if not src or src.startswith(PLACEHOLDER) else BASE + src,
            labels=labels,
            category=category,
            is_new=new,
            # 신제품 근거가 있으면 행사 배지는 도입 행사로 보고 넘긴다.
            promo=new is not True and any(t in PROMO_TAGS for t in labels),
            url=f"{BASE}{view}?pCd={pcd}" if pcd else "",
        ))
    return out


def _promo_tab(c: httpx.Client) -> list[Item]:
    """pTab=8. 이름은 '신상품' 이지만 신제품 근거가 아니라 매대다(docstring 참고).

    is_new=None 으로 두고 행사 배지만 promo 로 올린다. 76건 전부 행사 배지가
    붙어 있어 사실상 전량이 promo 가 되는데, 그게 이 탭의 실체다.
    """
    items = _cards(_post(c, "/product/presentList.asp", {"pTab": TAB_NEW}),
                   "신상품", None, VIEW_NEW)
    # 조용히 0건이 되는 게 제일 나쁘다. 첫 화면은 반드시 와야 한다.
    if not items:
        raise ValueError(
            "세븐일레븐 presentList.asp?pTab=8 에서 카드가 0건이다. "
            "ul#listUl / .pic_product / .infowrap .name 셀렉터나 pTab 코드가 "
            "바뀌었는지 확인하라")

    # 더보기는 2페이지부터. 서버가 첫 13건을 건너뛴 위치에서 잘라준다.
    for page in range(2, MAX_PAGES + 2):
        got = _cards(_post(c, "/product/listMoreAjax.asp", {
            "intPageSize": PAGE_SIZE, "intCurrPage": page,
            "cateCd1": "", "cateCd2": "", "cateCd3": "", "pTab": TAB_NEW}),
            "신상품", None, VIEW_NEW)
        items += got
        if len(got) < PAGE_SIZE:              # 덜 왔으면 마지막 페이지
            break
    return items


def _fresh_food(c: httpx.Client) -> list[Item]:
    """Fresh Food. 요청한 건수만큼 목록을 처음부터 다시 그려준다.

    이 브랜드의 유일한 신제품 근거가 여기 있다. 목록 전체가 신상인 게 아니라
    상품별로 '신상품' 배지가 선별돼 붙는다(2026-10-01 실측 136건 중 11건).
    배지가 없는 건 is_new=None(모름)이다.
    """
    items: list[Item] = []
    size = PAGE_SIZE
    for _ in range(MAX_PAGES):
        items = _cards(_post(c, "/product/dosirakNewMoreAjax.asp",
                             {"intPageSize": size, "pTab": ""}),
                       "Fresh Food", None, VIEW_FF, badge_is_new=True)
        if len(items) < size:                 # 요청한 것보다 적게 왔으면 다 받은 것
            break
        size = min(size * 2, MAX_PAGE_SIZE)                             # 딱 맞게 왔으면 잘렸을 수 있으니 넓혀서 다시
    if not items:
        raise ValueError(
            "세븐일레븐 dosirakNewMoreAjax.asp 에서 카드가 0건이다. "
            "Fresh Food 목록 주소나 카드 셀렉터가 바뀌었는지 확인하라")
    return items


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        fresh = _fresh_food(c)
        # 신제품 근거가 있는 쪽을 먼저 담는다. 같은 상품이 양쪽에 있으면
        # Fresh Food 의 상품별 배지가 이겨야 한다(현재 겹침 0건이지만 순서로 못박는다).
        for it in fresh + _promo_tab(c):
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)

    # 배지가 통째로 사라지면(마크업 개편) 조용히 신제품 0건이 된다. 세어서 드러낸다.
    # 0건 자체는 '이번 주 신상이 없다'일 수도 있어 예외로 올리진 않는다 — 대신
    # 태그가 아예 한 개도 안 읽히면 그건 셀렉터가 깨진 것이라 예외로 올린다.
    n_new = sum(1 for it in fresh if it.is_new is True)
    if not any(it.labels for it in fresh):
        raise ValueError(
            f"세븐일레븐 Fresh Food {len(fresh)}건에서 태그가 한 개도 안 읽혔다. "
            "ul.tag_list_01 li 가 바뀌었는지 확인하라 "
            "(2026-10-01 실측: 136건 중 신상품 11·인기 5·단체 4)")
    print(f"  세븐일레븐 Fresh Food {len(fresh)}건 중 신상품 {n_new}건 "
          f"/ 행사매대(pTab=8) {len(items) - len(fresh)}건")
    return items
