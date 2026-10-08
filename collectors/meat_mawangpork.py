"""마왕족발((주)콜라겐랩).

레지스트리 등록값 — `base.BRANDS`: `"마왕족발": (FRANCHISE, "한식")`,
`base.SITES`: `"마왕족발": "https://mawangpork.com/html/menu_1.html"`.
(족발·보쌈이라 `taxonomy.SUBS` 에서는 `한식` 이다. 두찜·오봉집·원할머니와 같은 칸.)

가맹점 231개다(공정위 2025년도 정보공개서, 2024년 말 기준). 족발 업종에서
`MEAT` 조사가 훑은 브랜드 중 **살아 있는 NEW 배지를 가진 유일한 곳**이다.

⚠️ **도메인을 헷갈리지 마라. `mawangjokbal.com` 은 NXDOMAIN 이다.**
공식 도메인은 **`mawangpork.com`** 이고, 푸터 신원도 맞는다 —
`(주)콜라겐랩 박근준 사업자등록번호 224-86-00575`. 공정위 마스터의 가맹본부와
일치한다(하남돼지집과 같은 제작사 템플릿이다. 둘 다 푸터가 `Designed By view3.net`).

  GET mawangpork.com/html/menu_1.html?sca=<탭>

정적처럼 보이는 `.html` 인데 실제로는 PHP 가 받는다. 쿠키·세션 불필요.
**3요청에 29건**(2026-10-08 실측).

  ⚠️ **탭 세 개를 다 받아야 한다. `menu_1.html` 만 받으면 10건이다.**
  화면 탭(`ul.menu_tab a[data-sca]`)은 클릭하면 같은 URL 에 `sca` 를 POST 해서
  `.menu_list` 만 갈아끼우는 ajax 다. 같은 값을 **GET 쿼리로 줘도 똑같이** 온다
  (실측 확인). 그래서 평범한 GET 세 번으로 끝낸다.
      sca=2 메인메뉴 10 · sca=3 세트메뉴 8 · sca=4 사이드메뉴 11
  `sca=5` 는 0건이다(탭이 셋뿐이다).

  ⚠️ **`menu_2.html` ~ `menu_7.html` 은 쓰지 마라. 전부 200 이지만 내용이 없다.**
  `menu_2~5` 는 `메인 메뉴`·`세트 메뉴`·`사이드 메뉴`·`싱글도시락` 이라는 제목만
  남은 구버전 게시판이고 본문이 **「게시물이 없습니다」** 다. `menu_6`·`menu_7` 은
  사이트 **홈페이지**가 그대로 떨어지는 soft-404 다. 넷 다 `p.m_txt` 0건이라
  셀렉터로는 조용히 빈 리스트가 되고, 길이만 보면 14~26KB 라 성공처럼 보인다.
  **200 을 성공으로 읽으면 안 되는 자리의 교과서다.**

  is_new  🟢 **`<ul class="option">` 안의 `<li>New</li>` 배지.** 이 레포에서
          드물게 **켜고 끄는** 배지다. **29건 중 5건(17%)** 에만 붙어 있고
          나머지 24건은 `<ul class="option">` 이 **빈 채로** 온다. 자리만 있고
          전건에 켜져 있는 장식(퀴즈노스 NEW 66/66)과는 다르다.
            메인메뉴 2/10  청양매운족발 · 바삭소금구이
            세트메뉴 1/8   내맘대로세트
            사이드   2/11  쭈꾸미볶음 · 로제떡볶이

          **다른 배지는 섞여 있지 않다.** 29건에서 나온 배지 문자열은 `New`
          하나뿐이고, `menu_1.css` 의 `.option li` 도 빨간 원 **한 벌**이라
          `Best`/`Hot` 용 변형 클래스가 아예 없다. 얌샘김밥(BEST 19·HOT 8·COOL 6)
          이나 설빙(`icon_signature.png` 를 존재만 세서 2013년 메뉴가 신상이 됐다)
          같은 섞임은 여기 없다. 그래도 **문자열이 `NEW` 일 때만** True 로 올린다 —
          관리자가 이 칸에 자유 텍스트를 넣는 구조라 언젠가 `Best` 가 들어오면
          그건 `labels` 로만 흘러가고 신제품 판정에는 닿지 않아야 한다.

          🔴 **배지는 오래 켜져 있다. 날짜 없이 쓰면 안 된다.** 5건 중 2건이
          2024년 사진이고, 그중 `쭈꾸미볶음` 은 공지사항에 **2023.12.22
          「히든 별미 메뉴 쭈꾸미 볶음 출시!」** 로 올라온 상품이다. **2년 가까이
          배지가 켜진 채다.** 그래서 `uploaded_at` 을 반드시 같이 채운다 —
          `rules.is_fresh()` 가 `is_new is True` 라도 날짜가 있으면 날짜를 먼저
          보기 때문에(`stamped >= cutoff`) 이 2건이 신상으로 새지 않는다.
          배지만 믿고 날짜를 비우면 설빙 '인절미설빙' 자리로 직행한다.

          배지가 없는 24건은 `False` 가 아니라 **None** 이다(죠스떡볶이 선례).
          이 사이트가 "신제품 아님"이라고 말한 적은 없고, `is_new=False` 는
          `released_at` 없이는 `is_fresh` 에서 영구 탈락이라 **나중에 배지 없이
          조용히 추가되는 메뉴까지 diff 경로에서 막아버린다.**

  uploaded_at  **이미지 업로드 경로에 날짜가 박힌다.** `MEAT` 조사가 못 찾은
          값이다. `background-image` 의 CDN 주소가
          `/upload/menu_01/2026_03_31/admin_1vRj3_2026_03_31_12_23_12.png`
          → 2026-03-31. 폴더와 파일명에 **같은 날짜가 두 번** 들어가 서로를
          검증한다. 29건 전부 파싱되고 **미래 날짜가 하나도 없다**
          (최대 2026-03-31, 조사일 2026-10-08). 분포는 —
            2020-07-31  3건  마왕통구이·패밀리세트·악마세트
            2021-05-13  2건  천사세트·파인애플 샤베트
            2022-07-15  1건  마왕세트
            2023-01-26  7건  보쌈구이·불족발·갈릭족발·당면냉채족발·반반세트·
                             족발볶음밥·쟁반국수
            2023-02-02  6건  불보쌈·미니족구이·마왕국수·비빔국수·열무국수·껍데기볶음
            2023-11-27  2건  김치전·감자전·마라볶음밥
            2024-06-03  1건  로제떡볶이
            2024-06-12  4건  클래식족발·쭈꾸미볶음·마왕통구이 쭈꾸미세트·
                             클래식족발 쭈꾸미세트
            2026-03-31  3건  청양매운족발·바삭소금구이·내맘대로세트

  🔵 **교차검증 — 공지사항이 이 날짜의 정체를 세 번 짚어준다.**
          `/board/index.php?board=notice_01` 은 목록에 `등록일` 을 찍는다(5쪽 43건).
          ① **2020.07.31 「마왕족발 공식 홈페이지가 새로운 모습으로 리뉴얼
             되었습니다」** ↔ 사진 2020-07-31 **3건**. **사이트 개편일이다.**
          ② **2023.01.26 「마왕족발 신메뉴 [마라통구이] 출시!」** ↔ 사진
             2023-01-26 **7건**. 그런데 그 7건은 불족발·갈릭족발처럼 **원래
             있던 메뉴**고 정작 마라통구이는 지금 메뉴판에 없다(단종). 즉 그날은
             **사진 일괄 교체일**이지 7종의 출시일이 아니다. 2023-02-02 6건도 같다.
          ③ **2023.12.22 「히든 별미 메뉴 쭈꾸미 볶음 출시!」** ↔ 쭈꾸미볶음
             사진은 **2024-06-12**. 출시보다 **반년 늦다.**
          세 번 다 "이 날짜는 상품이 나온 날이 아니라 사진을 올린 날"로 떨어진다.

  **released_at 은 못 채운다.** 목록에도 상세 팝업에도 날짜 항목이 없다.
          위 ①②③ 때문에 사진 날짜를 출시일로 승격시키지도 않는다(본아이에프·
          한솥·원앤원·오봉집·두찜과 같은 처분). 29건 중 **16건이 2023-01-26·
          02-02 두 무더기**에 몰려 있다 — `rules.untrust_bulk_dates()` 는
          `BULK_MIN=20` 이라 이 규모를 안 건드리지만, **읽을 때는 '그 뒤로는
          안 바뀌었다' 정도로만 읽어야 한다.**

  ⛔ **서버 `Last-Modified` 는 쓰지 마라. 위조돼 있다.** `MEAT` §4 가 적어둔
          대로이고 2026-10-08 에 다시 쟀다. 일곱 페이지를 1.3초 간격으로 받으니
          `01:12:47`·`:48`·`:49`·`:51`… 로 **요청 시각을 그대로 따라왔다.**
          두찜처럼 이미지 HEAD 로 날짜를 캐는 길이 이 사이트에서는 막혀 있다.
          그래서 경로에 박힌 날짜 말고는 쓸 게 없다.

desc 는 상세 팝업에서 가져온다. 목록 카드에는 상품명뿐이고, 카드를 누르면
`POST /resource/menu.php {idx:<data-idx>}` 가 조각 HTML 을 돌려준다. 알레르기
정보도 같이 오지만 지금은 설명만 쓴다. 29요청이 늘어나는 건 사실이라 **실패해도
수집을 멈추지 않는다** — desc 는 신제품 신호가 아니다(두찜의 HEAD 와 같은 처분).
상세에 날짜·가격은 없다. 가격은 사이트 어디에도 없다.

세트메뉴 탭 8건(`마왕세트`·`천사세트`·`반반세트`·`내맘대로세트`·`패밀리세트`·
`악마세트`·`마왕통구이 쭈꾸미세트`·`클래식족발 쭈꾸미세트`)은 promo 로 찍지
않는다. 할인 행사가 아니라 구성 메뉴고, 거르는 건 `collect.drop_sets()`
담당이다(이삭토스트 선례). **행사 상품은 메뉴판에 아예 안 섞인다** — 쿠팡이츠
5천원 할인, 서울장수 콜라보 같은 건 전부 `/board/index.php?board=event_01`
게시판에만 있고 메뉴 탭에는 올라오지 않는다. 상품명 29개를 눈으로 읽어 확인했다.

robots 는 `User-agent: *` / `Allow:/` 21바이트다.

`Item.url` 은 분류 탭까지 건다. 상세가 POST 라 상품마다 걸 주소가 없다.
"""
import re
import time
from datetime import date

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "마왕족발"
HOST = "https://mawangpork.com"
MENU_URL = HOST + "/html/menu_1.html"
DETAIL_URL = HOST + "/resource/menu.php"
DELAY = 1.4          # 요청 간격(초)

# (sca 값, 분류명). 메뉴 페이지 상단 탭 `ul.menu_tab a` 의 data-sca 에서 그대로
# 옮겼다. 2026-10-08 실측. sca 를 안 주면 첫 탭(메인메뉴)만 온다.
TABS = (
    ("2", "메인메뉴"),
    ("3", "세트메뉴"),
    ("4", "사이드메뉴"),
)

MIN_ITEMS = 20       # 29건에서 이 아래로 떨어지면 탭이 깨진 것이다
MAX_ITEMS = 150      # 폭주 방지
MAX_DETAIL = 150     # 상세 요청 상한

# background-image 안의 주소.
_BG_URL = re.compile(r"url\(\s*['\"]?(.*?)['\"]?\s*\)")
# 업로드 경로의 날짜. `/upload/menu_01/2026_03_31/<파일명>` 의 폴더 쪽을 읽는다.
# 파일명에도 같은 날짜가 또 들어 있지만 폴더가 더 짧고 형식이 고정이다.
_PATH_DATE = re.compile(r"/(\d{4})_(\d{2})_(\d{2})/[^/]+$")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _uploaded_at(url: str) -> str:
    """업로드 경로의 날짜. 출시일이 아니라서 released_at 엔 안 넣는다.

    날짜로 안 읽히거나 미래면 지어내지 않고 비운다(읍천리 선례).
    """
    m = _PATH_DATE.search(url or "")
    if not m:
        return ""
    try:
        d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return ""
    return d.isoformat() if d <= date.today() else ""


def _desc(c, idx: str, cache: dict) -> str:
    """상세 팝업의 설명. 못 받으면 비운다 — desc 는 신제품 신호가 아니다."""
    if not idx:
        return ""
    if idx in cache:
        return cache[idx]
    if len(cache) >= MAX_DETAIL:
        return ""
    out = ""
    try:
        r = base.retry(lambda: c.post(DETAIL_URL, data={"idx": idx}))
        r.raise_for_status()
        p = HTMLParser(r.text).css_first(".menu_popup .pop_list li")
        out = _clean(p.text()) if p else ""
    except Exception:
        out = ""
    cache[idx] = out
    time.sleep(DELAY)
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen: set = set()
    descs: dict = {}
    with base.client(headers={"Referer": MENU_URL}) as c:
        for sca, category in TABS:
            r = base.retry(lambda: c.get(MENU_URL, params={"sca": sca}))
            r.raise_for_status()
            time.sleep(DELAY)

            cards = HTMLParser(r.text).css("ul.main_list > li")
            if not cards:
                # menu_2~7 처럼 200 인데 빈 껍데기일 수 있다(docstring).
                raise RuntimeError(
                    f"{BRAND} {category}(sca={sca}): 상품 0건 — "
                    "ul.main_list 가 비었다(탭 ajax 가 바뀌었을 수 있다)")

            for card in cards:
                n = card.css_first("p.m_txt")
                name = _clean(n.text()) if n else ""
                if not name:
                    continue
                key = base.make_key(BRAND, name)
                if key in seen:
                    continue
                seen.add(key)
                if len(items) >= MAX_ITEMS:
                    raise RuntimeError(f"{BRAND}: 상품이 {MAX_ITEMS}건을 넘었다")

                # ⚠️ (attributes.get(k) or "") 로 읽는다. selectolax 는 값 없는
                # 속성에 None 을 주고 기본값이 안 먹는다.
                img = card.css_first(".list_img")
                style = (img.attributes.get("style") or "") if img else ""
                m = _BG_URL.search(style)
                image = m.group(1).strip() if m else ""

                # 빈 <ul class="option"> 이 기본값이다. 켜진 카드에만 <li> 가 있다.
                badges = [_clean(b.text()) for b in card.css("ul.option li")]
                badges = [b for b in badges if b]

                items.append(Item(
                    brand=BRAND,
                    name=name,
                    desc=_desc(c, card.attributes.get("data-idx") or "", descs),
                    image=image,
                    # 지금은 New 뿐이다. 다른 말이 들어오면 라벨로만 보이고
                    # 신제품 판정에는 닿지 않는다(docstring).
                    labels=badges,
                    category=category,
                    # 사진 올린 날짜. 출시일이 아니다(docstring 의 교차검증 ①②③).
                    uploaded_at=_uploaded_at(image),
                    # 문자열이 NEW 일 때만 True. 없으면 False 가 아니라 모름이다.
                    is_new=True if any(b.upper() == "NEW" for b in badges) else None,
                    # 1+1·할인 행사는 이벤트 게시판에만 있다. 세트는 promo 가 아니다.
                    promo=False,
                    url=f"{MENU_URL}?sca={sca}",
                ))

    if len(items) < MIN_ITEMS:
        raise RuntimeError(
            f"{BRAND} {len(items)}건 — 평소 29건이다. 탭 하나가 비었을 수 있다")

    badged = [i for i in items if i.is_new]
    if not badged:
        raise RuntimeError(
            f"{BRAND}: NEW 배지 0건 — 이 브랜드의 유일한 신제품 신호가 사라졌다")
    if len(badged) == len(items):
        # 전건에 켜져 있으면 신호가 아니라 장식이다(퀴즈노스 66/66 선례).
        raise RuntimeError(
            f"{BRAND}: NEW 배지가 {len(items)}건 전부다 — 장식으로 바뀌었다")

    if not any(i.uploaded_at for i in items):
        raise RuntimeError(
            f"{BRAND}: 업로드 날짜를 한 건도 못 읽었다 — /upload/ 경로가 바뀌었다")

    return items
