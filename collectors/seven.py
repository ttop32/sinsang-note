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

## 상품 분류는 Fresh Food 의 하위 탭에 있다 (2026-10-01 실측)

예전엔 category 에 'Fresh Food'(탭 이름)·'신상품'(매대 이름)을 넣었다. 둘 다
판매채널이라 '도시락끼리 모아보기'가 안 됐다. `bestdosirakList.asp` 안에
하위 탭이 셋 있고(`ul.tab_layer04`), 같은 `dosirakNewMoreAjax.asp` 에 pTab 으로
넘기면 서버가 그대로 걸러준다.
  - `pTab=mini`    → 도시락/조리면   32건
  - `pTab=noodle`  → 삼각김밥/김밥   60건
  - `pTab=d_group` → 샌드위치/햄버거 44건
**탭 이름(mini·noodle)과 내용이 안 맞는다** — noodle 이 면이 아니라 김밥이다.
코드가 아니라 화면 글자를 믿어야 한다. 셋은 전체(136건)를 정확히 나눠 가진다:
32+60+44=136, 겹침 0, 전체에만 있고 어느 탭에도 없는 상품 0.

화면용 이름으로는 이렇게 옮긴다.
  - mini → **도시락**. 라벨이 '도시락/조리면' 인데 32건에 면류가 한 건도 없다.
    대신 닭강정·닭껍질튀김·백순대볶음처럼 즉석조리 쪽에 가까운 게 5건쯤 섞인다.
    세븐일레븐이 자기 도시락 매대에 올린 것이라 그 말을 그대로 따른다.
  - noodle → **김밥**. 김밥·삼각김밥·유부초밥·무스비가 전부 여기다. 한 식구다.
  - d_group → 라벨이 '샌드위치/햄버거' 로 **두 분류를 붙여놓은 이름**이라
    이름에 '버거'가 있으면 햄버거, 아니면 샌드위치로 가른다. 라벨을 읽는 것이지
    분류를 지어내는 게 아니다. 44건을 눈으로 확인했고 애매한 건 2건이다
    (롯데)미트피자핫도그 · 롯데)K길거리토스트 → 샌드위치로 간다).

신상품 탭(pTab=8)에는 **분류 축이 없다.** presentList.asp 의 hidden 폼에
cateCd1·cateCd2·cateCd3 가 있지만 값이 전부 비어 있고 고르는 메뉴가 없다
(페이지의 탭 목록은 '7-Select'·'신상품' 둘뿐, select 요소 0개, fncCate 류 함수 0개).
그래서 category 를 비운다. 어차피 전건이 promo 라 화면엔 안 오른다.

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

# Fresh Food 하위 탭. {pTab 값: (화면 글자, 화면용 분류)}.
# 화면 글자는 bestdosirakList.asp 의 ul.tab_layer04 에 있는 그대로이고,
# 매 수집마다 _check_tabs() 가 그 메뉴와 대조한다. 코드 이름(mini·noodle)은
# 내용과 안 맞으니 믿지 마라 — noodle 이 면이 아니라 김밥이다(docstring 참고).
# 값이 None 인 탭은 라벨이 두 분류를 붙여놓은 것이라 _split() 이 갈라준다.
FF_TABS = {
    "mini": ("도시락/조리면", "도시락"),
    "noodle": ("삼각김밥/김밥", "김밥"),
    "d_group": ("샌드위치/햄버거", None),
}
FF_LIST = "/product/bestdosirakList.asp"   # 탭 메뉴가 있는 정적 페이지


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


def _check_tabs(c: httpx.Client) -> None:
    """Fresh Food 하위 탭이 그대로인지 매 수집마다 대조한다.

    분류가 전적으로 이 탭에 달려 있다. 사이트가 탭을 갈아끼우면 목록은 멀쩡히
    오는데 분류만 통째로 틀려진다 — 눈에 안 띄는 고장이라 여기서 드러낸다.
    """
    r = c.get(BASE + FF_LIST)
    r.raise_for_status()
    time.sleep(DELAY)
    found = {}
    for a in HTMLParser(r.text).css("a"):
        m = re.search(r"[?&]pTab=([A-Za-z0-9_]+)", a.attributes.get("href") or "")
        if m:
            found[m.group(1)] = " ".join(a.text().split())
    want = {k: label for k, (label, _) in FF_TABS.items()}
    if found != want:
        raise ValueError(
            f"세븐일레븐 Fresh Food 하위 탭이 달라졌다. 기대 {want} / 실제 {found} "
            f"— {FF_LIST} 의 ul.tab_layer04 를 보고 FF_TABS 를 고쳐라")


def _split(name: str) -> str:
    """'샌드위치/햄버거' 탭을 라벨대로 둘로 가른다.

    분류를 지어내는 게 아니라 **두 분류를 붙여놓은 라벨을 읽는** 것이다.
    세븐일레븐이 이미 "이 44건은 샌드위치 아니면 햄버거다" 라고 말해줬고,
    둘 중 어느 쪽인지만 이름에서 고른다. 2026-10-01 실측 44건 전수 확인:
    '버거'가 들어간 18건은 전부 버거, 나머지는 샌드·샌드위치·토스트·핫도그다.
    애매한 2건(미트피자핫도그·K길거리토스트)은 샌드위치로 간다.

    ⚠️ **세븐일레븐이 상품명을 잘라서 준다.** '삼립)메가불고기스테이크갈릭버'
    처럼 '버거'의 끝 글자가 날아간 게 있다(목록 .name 도 img alt 도 똑같이
    잘려 있어 온전한 이름을 주는 자리가 없다). 그래서 '버'로 끝나는 것도
    버거로 본다 — 211건 전수에서 '버'로 끝나는 건 그 한 건뿐이고
    샌드위치 쪽엔 하나도 없다.
    """
    return "햄버거" if "버거" in name or name.endswith("버") else "샌드위치"


def _cards(html: str, category: str | None, is_new: bool | None, view: str,
           badge_is_new: bool = False) -> list[Item]:
    """목록 페이지든 더보기 조각이든 같은 카드 마크업을 쓴다.

    badge_is_new 를 켜면 상품별 '신상품' 배지를 신제품 근거로 읽는다(Fresh Food 전용).
    끄면 배지를 무시하고 호출자가 준 is_new 를 그대로 쓴다(신상품 탭). 두 목록에서
    같은 글자가 전혀 다른 의미라 한 함수에서 플래그로 가른다 — 근거는 docstring.

    category 가 None 이면 '샌드위치/햄버거' 처럼 두 분류를 붙여놓은 탭이라
    _split() 이 이름으로 가른다. 빈 문자열이면 분류 축이 없는 목록이다(신상품 탭).
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
            category=_split(name) if category is None else category,
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
    # 분류 축이 없는 매대라 category 를 비운다(모듈 docstring 참고).
    items = _cards(_post(c, "/product/presentList.asp", {"pTab": TAB_NEW}),
                   "", None, VIEW_NEW)
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
            "", None, VIEW_NEW)
        items += got
        if len(got) < PAGE_SIZE:              # 덜 왔으면 마지막 페이지
            break
    return items


def _ff_tab(c: httpx.Client, p_tab: str, category: str | None) -> list[Item]:
    """Fresh Food 한 탭. 요청한 건수만큼 목록을 처음부터 다시 그려준다."""
    items: list[Item] = []
    size = PAGE_SIZE
    for _ in range(MAX_PAGES):
        items = _cards(_post(c, "/product/dosirakNewMoreAjax.asp",
                             {"intPageSize": size, "pTab": p_tab}),
                       category, None, VIEW_FF, badge_is_new=True)
        if len(items) < size:                 # 요청한 것보다 적게 왔으면 다 받은 것
            break
        size = min(size * 2, MAX_PAGE_SIZE)   # 딱 맞게 왔으면 잘렸을 수 있으니 넓혀서 다시
    return items


def _fresh_food(c: httpx.Client) -> list[Item]:
    """Fresh Food. 하위 탭(도시락·김밥·샌드위치/햄버거)별로 나눠 받는다.

    이 브랜드의 유일한 신제품 근거가 여기 있다. 목록 전체가 신상인 게 아니라
    상품별로 '신상품' 배지가 선별돼 붙는다(2026-10-01 실측 136건 중 11건).
    배지가 없는 건 is_new=None(모름)이다.

    분류를 얻으려고 탭을 나눈 것이지 건수를 늘리려는 게 아니다. 세 탭은 전체
    목록을 정확히 나눠 가진다(32+60+44=136, 겹침 0). 그래도 혹시 탭 어디에도
    없는 상품이 생기면 통짜 목록 쪽이 더 많아지므로, 아래 fetch() 가 센다.
    """
    _check_tabs(c)
    items: list[Item] = []
    seen = set()
    for p_tab, (label, category) in FF_TABS.items():
        got = _ff_tab(c, p_tab, category)
        # 조용히 0건이 되는 게 제일 나쁘다. 세 탭 다 수십 건짜리 목록이다.
        if not got:
            raise ValueError(
                f"세븐일레븐 Fresh Food 탭 pTab={p_tab}({label}) 에서 카드가 0건이다 "
                f"(2026-10-01 실측 mini 32 · noodle 60 · d_group 44). "
                f"dosirakNewMoreAjax.asp 의 pTab 값이나 카드 셀렉터를 확인하라")
        for it in got:
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)

    # 탭을 나눠 받으면서 상품을 흘리지 않았는지 통짜 목록과 대조한다.
    # 지금은 세 탭이 전체를 정확히 덮지만(136=32+60+44), 사이트가 네 번째 분류를
    # 만들면 그 상품들이 **조용히 사라진다**. 그 고장은 화면에서 안 보인다.
    whole = _ff_tab(c, "", "")
    lost = [it.name for it in whole if it.key not in seen]
    if lost:
        raise ValueError(
            f"세븐일레븐 Fresh Food 통짜 목록 {len(whole)}건 중 {len(lost)}건이 "
            f"어느 하위 탭에도 없다(예: {lost[:5]}). {FF_LIST} 에 탭이 늘었는지 "
            f"확인하고 FF_TABS 에 더해라")
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
