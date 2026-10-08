"""카페051((주)공오일, 부산 지역번호 051 에서 온 이름).

대문(cafe051.com/)은 레이아웃 이름이 'opening' 인 창업유치 스플래시라 본문이
없다. 본체는 /new2025 이하이고 **Rhymix(XE 계열) SSR** 이다 — 컴포즈커피와 같은
엔진이라 브라우저가 필요 없다. 내비 BRAND > MENU 가 /board16 이고 거기가
게시판 갤러리 스킨으로 된 메뉴판이다(2026-10-03 실측).

  /index.php?mid=board16&page=1   100건
  /index.php?mid=board16&page=2    90건   → 합계 190건, page=3 은 0건
  /board16/<document_srl>          상품 상세

`listStyle=list`·`listStyle=webzine` 은 서버가 무시한다(둘 다 갤러리 그대로,
날짜 0건). 날짜 칸을 띄우는 스킨 옵션이 없다.

## 신상 신호 — 둘을 교차검증했다

**① 썸네일에 합성된 NEW 배지.** 마크업에는 신호가 하나도 없다 —
`NEW`·`신메뉴`·`신상`·`badge`·`label` 문자열이 전 페이지에 **0건**이고, 분류도
COFFEE / Non-coffee / Beverage / Blended / CAN DRINK / 10oz / Desserts 7개뿐이라
신메뉴 칸이 없다. 그런데 **썸네일 그림 좌상단에 흰 원 테두리 + NEW 글자가
합성돼 있다.** 컴포즈커피와 같은 함정이고 같은 방법으로 푼다.

컴포즈는 우하 사분면 노랑(#FFD800) 비율이었지만 여기는 **좌상단 1/3 의 흰색
비율**이다. 190장 전수 실측(2026-10-03):

      0.0000   157장   배경이 흰색이 아니고 배지도 없는 것
      0.0179 ~ 0.0184  **3장**   ← 배지. 우베라떼·설향 우베라떼·우베 밀크쉐이크
      0.9248 ~ 1.0000   30장   디저트. **배경이 통째로 순백**이라 1.0 에 붙는다

양쪽으로 다 벌어져 있다(0 ↔ 0.0179, 0.0184 ↔ 0.9248). 그래서 하한뿐 아니라
**상한도 둔다** — 흰 배경 접시 사진 30장을 배지로 세면 전체의 17% 가 가짜
신상이 된다. 그 30장은 좌상단을 전부 받아 눈으로 확인했고 배지가 한 장도 없다.

⚠️ **한계를 적어 둔다.** 배지가 흰색이라 흰 배경 상품(디저트)에 붙으면 우리는
못 본다. 틀리는 방향이 '놓침' 이지 '상시 메뉴를 신상으로 올림' 이 아니라서
그대로 둔다(컴포즈 `_has_badge` 와 같은 원칙).

**② 상세의 `og:article:published_time`.** 목록에는 날짜가 없지만 상세 페이지
`<meta property="og:article:published_time">` 이 등록 시각을 준다. 배지 3건의
날짜가 전부 **2026-08-25**(39일 전)이고, 배지가 없는 바로 다음 묶음은
2026-06-16 이다. 두 신호가 어긋나지 않는다 — 배지 3건 = 최신 3건이다.

⚠️ **썸네일 URL 의 `?t=` 는 날짜가 아니다.** Rhymix 썸네일 캐시의 mtime 이라
썸네일을 다시 만들면 갱신된다. 5건을 og 와 대조했더니 2건이 어긋났다 —
`고흥 유자 에이드` 는 t 가 2026-07-13 인데 실제 등록일은 **2025-08-28** 이다
(11개월 차). t 로 날짜를 세면 2026-07-15 에 21건이 몰리는 가짜 묶음이 나온다.
쓰지 마라.

## document_srl 은 썸네일 경로에서 캔다

카드의 `<a>` 가 `javascript:void(0)` 이라 상세 주소가 마크업에 없다. 대신
썸네일이 `/files/thumbnails/101/150/600x600.crop.jpg` 인데 이건 Rhymix 의
`getNumberingPath()` 가 document_srl 을 뒤에서부터 3자리씩 끊어 만든 경로다.
뒤집어 이으면 150101 이고 /board16/150101 이 실제로 열린다(검증했다).

목록이 srl 내림차순이고 srl 순서와 등록일 순서가 일치해서(150101=2026-08-25,
148500=2026-06-16, 143034=2025-11-20, 141042=2025-08-28) **앞에서부터만** 상세를
받으면 된다. DETAIL_DAYS 보다 오래된 게 나오면 멈춘다 — 190건을 전부 받으면
6분이 걸리고 그 대부분이 rules.WINDOW(60일) 밖이라 쓸 데가 없다.

## 안 하는 것

- **분류(category)를 안 채운다.** 전체 목록에는 분류가 안 실리고, 받으려면
  카테고리 7면을 따로 돌아야 한다. 받아봐야 `COFFEE`·`Desserts` 같은 영문이고
  taxonomy 표에도 없다. 컴포즈커피와 같은 판단이다.
- /board11·/board12(공지·뉴스로 보이는 게시판)는 **둘 다 글이 0건**이다.
  사이트 RSS(/rss)는 제휴문의 게시판 하나뿐이고 스팸이 섞여 있다.
  board16 전용 피드(/board16/rss)는 "피드 기능이 잠겨 있습니다" 다.

robots.txt 는 cafe051.com 에 없다(404). 간격은 2초.
"""
import io
import re
import time
from datetime import date, timedelta

from PIL import Image

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "카페051"
SITE = "https://cafe051.com"
LIST_URL = f"{SITE}/index.php"
BOARD = "board16"
MAX_PAGES = 6        # 폭주 방지. 현재 2페이지(100+90).
DELAY = 2.0

# 상세를 받아 날짜를 채울 범위. rules.WINDOW 가 60일이라 넉넉히 두 배 반을 본다.
# 목록이 srl 내림차순이고 srl 순서 = 등록 순서라 앞에서부터 받다가 끊으면 된다.
DETAIL_DAYS = 150
MAX_DETAILS = 50     # 폭주 방지. 현재 이 창에 드는 건 10건 안팎이다.

# 썸네일 좌상단에 합성된 NEW 배지(위 docstring §①).
_BADGE_LO = 0.005    # 실측 간격 0.0000 ↔ 0.0179 사이
_BADGE_HI = 0.50     # 실측 간격 0.0184 ↔ 0.9248 사이. 흰 배경 디저트 30장을 막는다
_WHITE_MIN = 238     # 채널 최솟값. JPEG 압축 때문에 255 로는 안 잡힌다
_WHITE_SPREAD = 12   # 채널 간 편차. 색 있는 밝은 면(크림·우유)을 흰색으로 안 센다

_PUBLISHED = re.compile(
    r'og:article:published_time"\s+content="(\d{4}-\d{2}-\d{2})')
_THUMB_SRL = re.compile(r"/files/thumbnails/((?:\d{3}/)+)")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(src: str) -> str:
    if not src:
        return ""
    return src if src.startswith("http") else SITE + src


def _srl(src: str) -> int:
    """썸네일 경로에서 document_srl 을 되살린다. Rhymix getNumberingPath 의 역이다.

    `/files/thumbnails/101/150/600x600.crop.jpg` → 150101.
    """
    m = _THUMB_SRL.match(src or "")
    if not m:
        return 0
    chunks = m.group(1).rstrip("/").split("/")
    return int("".join(reversed(chunks)))


def _labels(li) -> list:
    """ICED / HOT. 목록 카드의 .ml_info 가 용량과 함께 들고 있다."""
    out = []
    for node in li.css(".ml-iced-title, .ml-hot-title"):
        t = _clean(node.text()).upper()
        if t:
            out.append(t)
    return out


def _white_ratio(im, box) -> float:
    px = list(im.crop(box).getdata())
    if not px:
        return 0.0
    hit = sum(1 for r, g, b in px
              if min(r, g, b) >= _WHITE_MIN and max(r, g, b) - min(r, g, b) <= _WHITE_SPREAD)
    return hit / len(px)


def _has_badge(c, url: str) -> bool:
    """썸네일 좌상단에 NEW 배지가 합성돼 있는가.

    못 받거나 못 읽으면 False 다 — 배지가 없는 쪽으로 틀리는 게 안전하다.
    여기서 틀려서 True 가 되면 상시 메뉴가 신상으로 올라간다.
    """
    if not url:
        return False
    try:
        im = Image.open(io.BytesIO(base.retry(lambda: c.get(url)).content)).convert("RGB")
    except Exception:
        return False
    w, h = im.size
    return _BADGE_LO <= _white_ratio(im, (0, 0, w // 3, h // 3)) <= _BADGE_HI


def _published(c, srl: int) -> str:
    """상세의 og:article:published_time (YYYY-MM-DD). 없으면 빈 문자열."""
    r = base.retry(lambda: c.get(f"{SITE}/{BOARD}/{srl}"))
    r.raise_for_status()
    m = _PUBLISHED.search(r.text)
    return m.group(1) if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()

    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST_URL, params={"mid": BOARD, "page": page}))
            r.raise_for_status()
            cards = HTMLParser(r.text).css("ul.gallery > li")
            if not cards:
                break

            parsed = []
            for li in cards:
                node = li.css_first(".ko_title") or li.css_first(".thum_title")
                name = _clean(node.text()) if node else ""
                if not name:
                    continue
                img = li.css_first("img")
                src = img.attributes.get("src", "") if img else ""
                srl = _srl(src)
                en = li.css_first(".en_title")
                ex = li.css_first(".explanation")
                parsed.append((srl, Item(
                    brand=BRAND,
                    name=name,
                    name_en=_clean(en.text()) if en else "",
                    desc=_clean(ex.text()) if ex else "",
                    image=_abs(src),
                    labels=_labels(li),
                    url=f"{SITE}/{BOARD}/{srl}" if srl else "",
                )))

            # 범위를 넘긴 page 를 서버가 1페이지로 되돌려주는 경우를 막는다
            if not parsed or all(it.key in seen for _, it in parsed):
                break
            for srl, it in parsed:
                if it.key not in seen:
                    seen.add(it.key)
                    items.append((srl, it))

    # 목록이 통째로 비면 조용한 0건 수집이 된다. 예외로 올려 드러낸다.
    if len(items) < 50:
        raise RuntimeError(f"카페051 {len(items)}건 — 갤러리 구조가 바뀌었을 수 있다")

    # 상세에서 등록일. srl 내림차순으로 앞에서부터 받다가 창을 벗어나면 끊는다.
    cutoff = (date.today() - timedelta(days=DETAIL_DAYS)).isoformat()
    dated = 0
    with base.client() as c:
        for srl, it in sorted(items, key=lambda p: -p[0])[:MAX_DETAILS]:
            if not srl:
                continue
            time.sleep(DELAY)
            day = _published(c, srl)
            if not day:
                continue
            it.released_at = day
            dated += 1
            if day < cutoff:
                break
    if not dated:
        raise RuntimeError("카페051 상세에서 등록일을 한 건도 못 읽었다 "
                           "— og:article:published_time 이 사라졌을 수 있다")

    # 썸네일을 받아 배지를 본다. 목록을 다 모은 뒤에 한 번만 돈다.
    # 배지 0건은 '오늘 신상이 없다'일 수도 있어서 실패로 보지 않는다. 다만
    # 그림을 **한 장도 못 읽으면** 그건 우리 쪽 고장이다.
    read = 0
    with base.client() as c:
        for _, it in items:
            if not it.image:
                continue
            read += 1
            if _has_badge(c, it.image):
                it.is_new = True
    if items and read == 0:
        raise RuntimeError("카페051 썸네일을 한 장도 못 읽었다 "
                           "— 이미지 주소가 바뀌었을 수 있다")

    return [it for _, it in items]
