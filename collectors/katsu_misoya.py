"""미소야. 가맹점 180개 — 돈까스 업종 2위.

공정위 업종 분류는 '일식'이지만 실제는 돈카츠 전문점이다(FRANCHISE-MASTER §7-4 가
경고한 그 자리). 이 프로젝트에서는 돈까스를 전부 `일식` 세부분류로 보내므로 결과는 같다.

아임웹(imweb)이고 `/menu` **1요청(1.3MB)에 전 메뉴가 SSR** 로 들어온다. 브라우저 불필요.
조사 문서 두 개가 이 브랜드를 두고 정면으로 갈렸는데(CANDIDATES-ASIAN 은 '상품 0건',
CANDIDATES-WESTERN 은 '상품 57건'), **2026-10-02 재실측 결과 후자가 맞다.**
렌더 텍스트만 보면 카테고리명밖에 안 보이는데, 상품은 갤러리 위젯의
`div#caption_<n>`(화면에서 `display:none`) 안에 들어 있다.

마크업은 두 조각이 `<n>` 으로 짝지어진다.
  <div id="caption_25766631" style="display:none"><h4>로스카츠</h4><p>담백한 육즙가득 등심…</p></div>
  <div id="gal_item_25766631" style="background-image: url(https://cdn.imweb.me/thumbnail/20230830/….png)">
**둘 다 있어야 상품으로 본다.** 캡션만 있고 이미지가 없는 3건(`신선합니다`·`맛있습니다`·
`건강합니다`)은 브랜드 소개 문구지 상품이 아닌데, 이 '둘 다' 조건이 그걸 정확히 걸러낸다.
60 캡션 → 57 상품.

**신제품 신호는 이미지 CDN 경로의 날짜뿐이다.** NEW 배지도 '신메뉴' 카테고리도 없다.
`cdn.imweb.me/thumbnail/YYYYMMDD/…` 의 YYYYMMDD 가 상품마다 갈린다(2026-10-02).

  20230830 32건   20231010 6건   20251113 5건   20230927 4건   20231005 3건
  20251127 3건    20260330 2건   20231019 1건   20260331 1건

2023년에 몰아 올린 위에 2025-11·2026-03 이 얹혀 있다. 증분 업로드가 실제로 돈다는 뜻이다.
**`uploaded_at` 까지만이다 — `released_at` 로 올리지 않는다**(본아이에프 선례).
`is_new` 는 비운다(None).

⚠️ **이 날짜를 믿기 전에 교차검증을 했다.** 같은 아임웹인 쑝쑝돈까스에서 조사 문서가
"당일 날짜 4건 = 증분 업로드 증거"라고 적었는데, 실제로 그 4건은 **로고 파일**이었고
날짜는 CDN 이 썸네일을 다시 만들 때마다 바뀌는 값이었다(2026-09-30 → 2026-10-01 로
이동). 미소야도 로고가 `thumbnail/20260812/` 로 잡히는데, 위의 '캡션+갤러리 이미지'
조건이 로고를 애초에 상품으로 세지 않는다. 날짜를 세려면 **상품에 붙은 것만** 세라.

카테고리는 상품에 필드로 안 붙어 있다. 대신 **페이지 자신의 네비게이션**이
`/menu/#<섹션id>` 로 KATSU·UDON·SOBA·RICE BOWL·HOT POT·SUSHI·ADD ON 을 가리킨다.
그 앵커들의 문서상 위치를 재서, 상품보다 앞에 있는 마지막 앵커의 라벨을 붙인다.
라벨 목록을 코드에 적어두지 않고 페이지에서 읽는 이유는, 브랜드가 분류를 바꾸면
우리 표가 조용히 낡기 때문이다. `since2000`(브랜드 소개 앵커)은 상품 앞에 오지 않아
실제로는 아무 상품에도 붙지 않지만, 혹시 붙더라도 카테고리일 뿐 판정에 쓰지 않는다.
⚠️ 앵커는 **제목 섹션**을 가리키고 갤러리는 그 다음 섹션이라, 경계가 한 칸 어긋나면
분류가 밀린다. 실제로 HOT POT 앵커 뒤에 덮밥류가 섞여 들어온다. 분류는 참고값이고
신제품 판정에는 쓰지 않으므로 그대로 둔다.

가격은 **사이트 어디에도 없다.** 상품 상세 페이지도 없어서 Item.url 은 SITES 폴백으로
떨어진다. desc(구성 설명)는 캡션의 `<p>` 에 있고 `<br>` 이 섞여 들어와 한 줄로 턴다.

robots.txt: `Allow: /` + `/site_join`·`/login`·`/logout.cm`·`/shop_cart`·`/?mode*`·
`/admin` Disallow. `/menu` 와 cdn 이미지는 허용 범위다.
이용약관: `/?mode=policy` 인데 **robots 가 `/?mode*` 를 막아 받지 않았다.**
확인하지 못했다는 뜻이지 금지 조항이 없다는 뜻이 아니다(쑝쑝돈까스·백소정과 같은 상황).
"""
import html as _html
import re


from . import base
from .base import Item

BRAND = "미소야"
URL = "https://www.misoya.co.kr/menu"

# 상품 캡션(화면에선 숨김). <h4> 이름 + <p> 구성 설명.
_CAPTION = re.compile(
    r'<div id="caption_(\d+)"[^>]*>\s*<h4>(.*?)</h4>\s*(?:<p>(.*?)</p>)?', re.S)
# 같은 번호의 갤러리 타일. 썸네일이 style 의 background-image 에 들어 있다.
_GAL = re.compile(
    r'id="gal_item_(\d+)"[^>]*background-image:\s*url\('
    r'(https://cdn\.imweb\.me/thumbnail/(\d{8})/[^)\s]+?)\)')
# 네비게이션이 거는 메뉴 섹션 앵커.
_NAV = re.compile(r'href="/menu/#(s[0-9a-f]+)"[^>]*>(.*?)</a>', re.S)


def _clean(s: str) -> str:
    """태그를 털고 엔티티를 풀어 한 줄로. desc 에 <br> 이 자주 섞인다."""
    return " ".join(_html.unescape(re.sub(r"<[^>]*>", " ", s or "")).split())


def _uploaded_at(yyyymmdd: str) -> str:
    return f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:]}"


def _category_at(anchors: list, pos: int) -> str:
    """상품보다 앞에 있는 마지막 네비 앵커의 라벨. 없으면 빈 문자열."""
    label = ""
    for apos, name in anchors:
        if apos > pos:
            break
        label = name
    return label


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(URL))
        r.raise_for_status()
    page = r.text

    # 네비가 가리키는 섹션 id → 라벨. 그 섹션이 문서 어디에 있는지도 같이 잰다.
    anchors = []
    for m in _NAV.finditer(page):
        label = _clean(m.group(2))
        pos = page.find(f'id="{m.group(1)}"')
        if label and pos >= 0:
            anchors.append((pos, label))
    anchors.sort()

    gal = {m.group(1): (m.group(2), m.group(3)) for m in _GAL.finditer(page)}
    if not gal:
        raise RuntimeError("미소야: 갤러리 타일 0건 — 셀렉터가 깨졌다")

    items: list[Item] = []
    seen = set()
    for m in _CAPTION.finditer(page):
        no = m.group(1)
        # 캡션만 있고 짝이 되는 갤러리 타일이 없으면 상품이 아니다(브랜드 소개 문구).
        if no not in gal:
            continue
        name = _clean(m.group(2))
        if not name:
            continue
        image, ymd = gal[no]
        it = Item(
            brand=BRAND,
            name=name,
            desc=_clean(m.group(3)),
            image=image,
            category=_category_at(anchors, m.start()),
            # 이미지 올린 날이지 출시일이 아니다. released_at 으로 올리지 않는다.
            uploaded_at=_uploaded_at(ymd),
            # NEW 배지도 신메뉴 칸도 없다. 모름은 모름으로 둔다.
            is_new=None,
        )
        # 같은 상품이 두 섹션에 겹쳐 실린다 — 57 타일 중 3쌍(콜드냉멘·소바 샐러드
        # 로스카츠·통살생선카츠)이 그래서 54건이 된다.
        # **먼저 만난 쪽(= 문서 앞, 날짜가 이른 쪽)을 남긴다.** 이삭토스트는 목록이
        # 최신순이라 뒤를 남겼는데 여기는 반대 이유다 — 통살생선카츠가 KATSU 에
        # 2023-08-30, ADD ON 에 2026-03-31 로 두 번 실려 있다. 늦은 쪽을 택하면
        # 사이드 사진을 다시 올렸다는 이유로 3년 된 상품이 신상으로 올라간다.
        if it.key in seen:
            continue
        seen.add(it.key)
        items.append(it)

    if not items:
        raise RuntimeError("미소야: 상품 0건 — 캡션·갤러리 짝짓기가 깨졌다")
    return items
