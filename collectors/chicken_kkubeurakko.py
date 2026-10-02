"""꾸브라꼬숯불치킨.

공정위 등록 가맹점 250개로 치킨 업종 23위. WordPress 사이트고 메뉴가 SSR 이다.
쿠키·세션 없이 열리고 브라우저도 불필요하다.

⚠️ **최상위 `kkubeurakko.com` 은 브랜드/창업 두 칸짜리 포털 스플래시**다(렌더 텍스트
473자). 홈을 받고 "JS 렌더라 불가" 로 넘기면 안 된다 — 메뉴는 따로 있다.
⚠️ 도메인 철자가 짐작으로는 안 나온다. `kkubrakko.com` 이 아니라 **`kkubeurakko.com`** 이다.

메뉴 페이지는 넷이다. 경로가 `menu-1 … menu-4` 라 이름이 없어서 분류는 각 페이지의
`<title>`("숯불 치킨 메뉴 - 꾸브라꼬 숯불치킨")에서 앞부분을 떼어 쓴다.
경로가 바뀌면 `/wp-json/wp/v2/pages` 로 다시 찾을 수 있다 — WordPress REST 가 열려 있다.
2026-10-02 실측: 숯불 치킨 메뉴 10 / 후라이드 메뉴 3 / 세트 메뉴 6 / 사이드 메뉴 15 = 34건.

🔴 **상품명이 `alt` 속성에 들어 있다.** 텍스트 노드가 아예 없어서 다른 길이 없다.
이게 이 어댑터의 가장 약한 고리다. 이 레포는 `alt` 때문에 이미 한 번 데였다 —
자담치킨 뿌슐랭 포스터의 alt 가 `치즈핑 치킨 포스터` 로 **틀려** 있었다
(collectors/chicken_jadam.py 참고). 그래서 여기서는 **파일명과 대조해서** 확인했다:
`트러플꾸브 ↔ truffle-kkub.png`, `저당양념꾸브 ↔ menu2026-1.png`,
`까르보꾸브 ↔ m1.png`, `취향존중 두마리세트 ↔ set-1.png`, `흑미치즈볼 ↔ side-2.png` —
분류별 접두(m/set/side)와 번호가 목록 순서와 맞고 어긋나는 건 없었다(2026-10-02).
alt 가 깨지는 날을 대비해 이름이 하나도 안 나오면 터뜨린다.

🔴 **아이콘·로고를 걸러야 한다.** 같은 정규식에 `ico-kakao.svg`(alt=카카오상담),
`ico-instagram.svg`, `ico-naver.svg`, `ico-facebook.svg`, `fixed-logo.svg`
(alt=꾸브라꼬숯불치킨) 5건이 같이 걸린다. 전부 `.svg` 라 **확장자로 거른다**
(상품 이미지는 전건 `.png`). 안 거르면 '카카오상담'·'페이스북' 이 상품으로 올라간다.
실측 39건 → 걸러서 **34건**이다.

⚠️ PC·모바일 블록이 같은 상품을 두 번 그린다(원본 66건). 이미지 경로로 중복을 턴다.

신제품 신호:
  is_new  **없다.** NEW 배지도 신메뉴 탭도 없다. 전건 None 으로 둔다.
          메뉴판 전체를 신상으로 찍지 않는다.
  released_at  없다. 출시일을 적어주는 자리가 없다. 비운다.
  uploaded_at  이미지의 Last-Modified.
          업로드 경로가 `/wp-content/uploads/2026/08/` 처럼 **월까지만** 알려주는데,
          거기서 날짜를 만들면 일(日)을 지어내는 셈이라 쓰지 않았다. 대신 HEAD 로
          진짜 날짜를 받는다 — 2026-10-02 실측으로 경로 월과 어긋나지 않는다
          (2026/08 → 2026-08-11, 2026/02 → 2026-02-27, 2025/07 → 2025-07-30,
          2025/08 → 2025-08-19). 34요청이면 감당할 만하다.
          ⚠️ 다만 **강한 신호는 아니다.** 34건이 사실상 네 덩어리다
          (2025-07 10건, 2025-08 22건, 2026-02 1건, 2026-08 1건). 새로 나온 두 건
          (저당양념꾸브·트러플꾸브)을 가려내는 데는 쓸 만하고, 덩어리 안의 선후는
          못 가린다. 업로드 시각이지 출시일이 아니므로 released_at 에는 안 넣는다.

상품별 상세 페이지가 없다. url 은 그 상품이 실린 메뉴 페이지까지만 채운다.
가격은 페이지에 없다. 세트 메뉴 6건은 그대로 싣고 promo 는 전건 False 다
(할인·행사 표시 없음, 세트 변형은 rules.drop_sets() 담당).
robots.txt 는 워드프레스 기본이다(`/wp-admin` 등만 Disallow). 메뉴 경로는 허용 범위다.
"""
import re
import time
from email.utils import parsedate_to_datetime

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "꾸브라꼬숯불치킨"
SITE = "https://kkubeurakko.com"
PAGES = ["/menu-1/", "/menu-2/", "/menu-3/", "/menu-4/"]

MAX_ITEMS = 200   # 폭주 방지. 현재 34건.
DELAY = 0.5       # 목록 요청 간격(초)
IMG_DELAY = 0.15  # 이미지 HEAD 간격(초)

# 업로드 폴더 안의 이미지 + 바로 뒤의 alt. 상품명이 alt 에만 있다.
_ITEM = re.compile(
    r'src="(/wp-content/uploads/\d{4}/\d{2}/[^"]+)"[^>]*alt="([^"]{1,30})"')


def _uploaded_at(client, img_url: str) -> str:
    """이미지의 Last-Modified 를 날짜로. 실패하면 조용히 비운다."""
    if not img_url:
        return ""
    try:
        lm = client.head(img_url).headers.get("last-modified", "")
        return parsedate_to_datetime(lm).date().isoformat() if lm else ""
    except Exception:
        return ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    seen_img = set()
    with base.client() as c:
        for path in PAGES:
            time.sleep(DELAY)
            r = base.retry(lambda p=path: c.get(SITE + p))
            r.raise_for_status()
            doc = HTMLParser(r.text)
            title = doc.css_first("title")
            # "숯불 치킨 메뉴 - 꾸브라꼬 숯불치킨" → "숯불 치킨 메뉴"
            cate = (title.text().split(" - ")[0].strip() if title else "")

            for img, alt in _ITEM.findall(r.text):
                # 아이콘·로고는 전부 svg 다. 상품 이미지는 전건 png.
                if img.lower().endswith(".svg"):
                    continue
                if img in seen_img:        # PC·모바일 블록 중복
                    continue
                seen_img.add(img)
                name = " ".join(alt.split())
                if not name:
                    continue

                it = Item(
                    brand=BRAND,
                    name=name,
                    image=SITE + img,
                    category=cate,
                    # NEW 배지도 신메뉴 탭도 없다. 모르는 건 모른다고 둔다.
                    is_new=None,
                    promo=False,
                    url=SITE + path,
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
                if len(items) >= MAX_ITEMS:
                    break

        # 이름이 alt 에만 있는 구조라 alt 가 사라지면 조용히 0건이 된다.
        if not items:
            raise RuntimeError("상품이 하나도 안 나왔다 — alt 가 사라졌거나 "
                               "셀렉터가 깨졌을 가능성")

        for it in items:
            time.sleep(IMG_DELAY)
            it.uploaded_at = _uploaded_at(c, it.image)

    # 🔴 '건수는 멀쩡한데 날짜만 사라진' 상태를 막는다. 이미지 호스트가
    # Last-Modified 를 끊거나 경로가 바뀌면 HEAD 가 전건 조용히 실패하는데,
    # 건수는 그대로라 collect.py 의 0건 가드도 FLOOR 도 통과한다. BBQ 의
    # _head_guard·가마치통닭·노랑통닭과 같은 처분이다(실측 34/34 가 날짜를 받는다).
    dated = sum(1 for it in items if it.uploaded_at)
    if dated * 2 < len(items):
        raise RuntimeError(
            f"꾸브라꼬숯불치킨 업로드일 {len(items)}건 중 {dated}건만 붙었다 — 이미지 "
            f"Last-Modified 가 끊겼거나 경로가 바뀌었을 가능성. 이 브랜드는 "
            f"NEW 배지도 신메뉴 탭도 없어서 이게 유일한 신호다")
    return items
