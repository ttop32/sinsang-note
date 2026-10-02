"""푸라닭.

공정위 등록 가맹점 715개로 치킨 업종 13위. '치킨, 요리가 되다' 를 내건
프리미엄 라인이라 신제품 회전이 빠른 편이다.

puradakchicken.com 은 옛날 ASP 사이트다. 목록이 서버에서 그대로 렌더돼 나오고
쿠키·세션·브라우저가 필요 없다. 응답은 UTF-8.

⚠️ 최상위 `/` 는 글자 여섯 개짜리 스플래시라 쓸 게 없다. 메뉴판은 /menu/product.asp 다.

분류 탭은 GNB 의 javascript:link02xx() 로 숨어 있어서 /common/js/link.js 를 봐야
주소가 나온다(2026-10-02 실측).
    전체메뉴      product.asp            88건
    치킨 메뉴     product.asp?sermode=0  54건
    사이드 메뉴   product.asp?sermode=1  34건
    나만의 레시피  recipe.asp
    메뉴별 정보   menuInfo.asp
54 + 34 = 88 로 두 분류가 전체를 정확히 반 가른다. 그래서 전체 페이지 대신
sermode=0·1 두 쪽을 훑는다 — 요청 수는 같은데(합쳐서 8페이지) 분류를 공짜로 얻는다.

제외한 것:
  - **나만의 레시피(recipe.asp)** 는 상품이 아니다. 들어가 보면 '고추마요 카나페',
    '치킨고추마요덮밥' 같은 **집에서 해 먹는 요리법 글 4건**이다. 푸라닭이 파는
    물건이 아니라 블로그 글이라 담지 않는다.
  - 메뉴별 정보(menuInfo.asp)는 영양성분표지 상품 목록이 아니다.
  - '베스트 메뉴'(sermode=0 의 옛 주소) 탭은 GNB 에서 주석 처리돼 사라졌다.
    살아 있었어도 BEST 는 NEW 가 아니라 안 썼을 것이다.

🔴 신제품 신호 = **상품별 NEW 배지.** notes/CANDIDATES-CHICKEN.md 의 2026-09-30
조사에는 '푸라닭은 신제품 신호 없음' 이라고 적혀 있는데 **그건 틀렸다.**
2026-10-02 실측으로 배지가 실재한다.
    <img src="../images/menu/img_new.png" class="best" alt="NEW메뉴">
88건 중 6건에만 붙어 있다(마마치 3종 + 쿼터레그 3종). 전건에 찍히는 장식이 아니라
브랜드가 고른 선별 배지다. 그래서 배지가 있으면 is_new=True 로 본다.
배지가 **없는 것은 False 가 아니라 None** 이다 — 안 붙었다는 게 오래됐다는 증거는
못 된다(BBQ 의 `is_new=is_new or None` 과 같은 태도).

🔴 같은 자리에 비슷하게 생긴 배지가 셋 더 있는데 **전부 신제품과 무관하다.**
alt 를 읽어보면 정체가 분명하다 — 매운맛 단계다.
    img_hot01.png  alt="약간 매운맛"   6건
    img_hot02.png  alt="매운맛"       1건
    img_hot03.png  alt="아주 매운맛"   7건
(BEST 배지는 아니다. 이 사이트엔 BEST 배지가 아예 없다.) 파일명이 `img_hot` 으로
시작한다는 이유로 신제품·인기상품으로 넘기면 안 된다. 그래서 신제품 판정은
**파일명에 `img_new` 가 들어갈 때만** 켜고, 매운맛 단계는 alt 그대로 labels 에 담는다.

두 번째 신호 = **이미지의 Last-Modified.** 88건이 31개 날짜로 흩어져 있고
(2020-07-31 사이트 개설분 11건이 가장 큰 덩어리, 나머지는 길어야 7건) 일괄 업로드
흔적이 없다. 더구나 NEW 배지 6건의 Last-Modified 가 2026-08-13 ×3 · 2026-06-25 ×3
으로 **전체에서 가장 최신 두 날짜와 정확히 겹친다** — 두 신호가 서로를 검증한다.
BBQ·교촌과 같은 자리인 uploaded_at 에 넣는다. 어디까지나 파일 업로드 시각이지
브랜드가 말한 출시일이 아니므로 released_at 은 비운다.

⚠️ 이미지 경로에 대괄호와 한글이 그대로 들어 있다
(`/upload/menu/[400-400]씬후라이드_쿼터레그.png`). HEAD 를 칠 때는 quote() 로
퍼센트 인코딩하고, Item.image 에는 원본 경로를 그대로 둔다(브라우저가 알아서 쓴다).

⚠️ 페이지 번호를 끝 너머로 넘기면(page=9, 10 …) 404 가 아니라 **마지막 페이지를
그대로 다시 돌려준다.** 그래서 '새로 들어온 게 0건이면 멈춘다' 로 끊고,
MAX_PAGES 로 한 번 더 막는다.

목록 카드의 href 는 `view.asp?idx=238&page=1&sermode=&sermode2=&serdiv=` 인데
뒤쪽 빈 파라미터는 목록 복귀용이라 상품과 무관하다. idx 만 떼어 깔끔한
`/menu/view.asp?idx=238` 로 조립한다(실제로 그 상품 상세가 열리는 걸 확인했다).

⚠️ **주문 채널(배달/홀/포장)은 labels 에 담지 않는다.** 카드에 `div.g_circle
p.circle` 로 들어 있어서 한때 labels 로 옮겼는데, **88건 전부가 셋 다 달고 있어서**
목록의 모든 카드에 "배달 홀 포장" 이 똑같이 찍혔다. base.shown_labels() 는 행사·NEW
중복만 걸러서 이걸 안 막는다. 다른 어댑터가 labels 에 넣는 건 NEW·BEST·한정·매운맛
처럼 **상품끼리 갈리는** 표시뿐이다. 전건에 붙는 건 라벨이 아니라 배경이다.

가격은 목록에 없고 상세에만 있다. Item 에 자리가 없어 받지 않는다.
세트·행사·이벤트 공지는 이 목록에 없다. '윙콤보'·'플래터'·'내.완.반' 은 구성 자체가
하나의 상품이고 할인이 아니라서 promo 는 전건 False 다. 세트 변형을 접는 건
collect.drop_sets() 담당이라 여기서 손대지 않는다.
"""
import re
import time
from email.utils import parsedate_to_datetime
from urllib.parse import quote

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "푸라닭"
SITE = "https://www.puradakchicken.com"
MENU = SITE + "/menu/"

# (sermode 값, 화면상 분류). 둘이 합쳐 전체 목록과 같다.
LISTS = [("0", "치킨"), ("1", "사이드")]

MAX_PAGES = 20    # 폭주 방지. 현재 분류당 5·3페이지.
DELAY = 0.3       # 목록 요청 간격(초)
IMG_DELAY = 0.15  # 이미지 HEAD 간격(초)

_IDX = re.compile(r"idx=(\d+)")


def _badges(node) -> tuple:
    """카드의 배지들을 (is_new, labels) 로.

    같은 `div.min_area` 안에 NEW 배지와 매운맛 단계 배지가 섞여 있다.
    `img_new` 만 신제품이고 `img_hot01/02/03` 은 맵기다(alt 가 '약간 매운맛' 등).
    """
    is_new, labels = False, []
    for img in node.css("div.min_area img"):
        src = img.attributes.get("src", "") or ""
        alt = " ".join((img.attributes.get("alt", "") or "").split())
        if "img_new" in src:
            is_new = True
            labels.append("NEW")
        elif alt:
            labels.append(alt)   # '약간 매운맛' / '매운맛' / '아주 매운맛'
    return is_new, labels


def _uploaded_at(client, img_url: str) -> str:
    """이미지의 Last-Modified 를 날짜로. 실패하면 조용히 비운다.

    경로에 대괄호·한글이 있어 그대로 보내면 서버가 못 알아듣는다. 인코딩해서 친다.
    """
    if not img_url:
        return ""
    try:
        lm = client.head(quote(img_url, safe=":/")).headers.get("last-modified", "")
        return parsedate_to_datetime(lm).date().isoformat() if lm else ""
    except Exception:
        return ""


def _page(client, sermode: str, page: int) -> list:
    r = base.retry(
        lambda: client.get(f"{MENU}product.asp?sermode={sermode}&page={page}"))
    r.raise_for_status()
    return HTMLParser(r.text).css("div.photo_list ul.list > li")


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    new_badges = 0
    with base.client() as c:
        for sermode, category in LISTS:
            for page in range(1, MAX_PAGES + 1):
                time.sleep(DELAY)
                cards = _page(c, sermode, page)
                if not cards:
                    break
                added = 0
                for card in cards:
                    title = card.css_first("p.title")
                    name = " ".join(title.text().split()) if title else ""
                    if not name:
                        continue

                    en = card.css_first("p.txt")
                    thumb = card.css_first("div.thumb img")
                    src = thumb.attributes.get("src", "") if thumb else ""
                    link = card.css_first("a[href^='view.asp?idx=']")
                    idx = _IDX.search(link.attributes.get("href", "")) if link else None
                    is_new, labels = _badges(card)
                    if is_new:
                        new_badges += 1

                    it = Item(
                        brand=BRAND,
                        name=name,
                        name_en=" ".join(en.text().split()) if en else "",
                        image=SITE + src if src.startswith("/") else src,
                        labels=labels,
                        category=category,
                        # 배지가 없다고 '신제품 아님'은 아니다. 모르면 None.
                        is_new=is_new or None,
                        # 할인·행사 표시가 없는 사이트다. 세트·콤보는 promo 가 아니라
                        # collect.drop_sets() 가 이름으로 거른다.
                        promo=False,
                        url=f"{MENU}view.asp?idx={idx.group(1)}" if idx else "",
                    )
                    if it.key in seen:
                        continue
                    seen.add(it.key)
                    items.append(it)
                    added += 1

                # 끝 너머 페이지는 404 가 아니라 마지막 페이지를 다시 준다.
                # 새로 들어온 게 없으면 거기가 끝이다.
                if not added:
                    break

        # 비어 있으면 셀렉터가 깨진 것이다. 조용히 [] 를 돌려주는 건 이 레포에서
        # 가장 나쁜 실패다 — 이유를 말하고 죽는다.
        if not items:
            raise RuntimeError("메뉴 목록이 비었다 — 셀렉터가 깨졌을 가능성")

        # 🔴 배지만 사라지는 경로를 막는다. 파일명이 `img_new.png` 에서 한 글자만
        # 바뀌어도 `_badges()` 는 그걸 매운맛 배지로 흘려보내고(alt 로 떨어진다)
        # is_new 가 전건 None 이 된다. 그때도 건수는 88 그대로라 collect.py 의
        # 0건 가드도 FLOOR 도 통과하고 "푸라닭은 신제품이 없다"가 조용히 굳는다.
        # 네네치킨·또래오래·노랑통닭과 같은 처분이다. 브랜드가 정말로 NEW 를 다
        # 내린 날에도 터지는데, 그 오탐은 감수한다.
        if not new_badges:
            raise RuntimeError(
                "푸라닭 NEW 배지가 0건 — 'div.min_area img[src*=img_new]' 가 "
                "안 걸린다. 이 브랜드의 신제품 신호라, 날아가도 건수는 그대로여서 "
                "아무도 못 알아챈다")

        for it in items:
            time.sleep(IMG_DELAY)
            it.uploaded_at = _uploaded_at(c, it.image)

    # 두 번째 신호(이미지 Last-Modified)도 같은 이유로 지킨다. 이미지 호스트가
    # 헤더를 끊거나 경로가 바뀌면 HEAD 가 전건 조용히 실패해 날짜가 통째로
    # 사라진다 — 가마치통닭·노랑통닭과 같은 가드다(실측 88/88 이 날짜를 받는다).
    dated = sum(1 for it in items if it.uploaded_at)
    if dated * 2 < len(items):
        raise RuntimeError(
            f"푸라닭 업로드일 {len(items)}건 중 {dated}건만 붙었다 — 이미지 "
            f"Last-Modified 가 끊겼거나 경로가 바뀌었을 가능성")
    return items
