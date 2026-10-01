"""할리스(HOLLYS).

⚠️ **이용약관이 상업적 이용을 금지한다.** 폴바셋·이마트24·도미노피자와 같은 종류의
건이라 운영자 방침("약관만 금지면 수집하되 기록")에 따라 어댑터는 만들되 여기 남긴다.
2026-09-30 `hollys.co.kr/customer/policy/serviceTerms.do` 본문이다.

  제15조(게시물의 저작권과 소유권) 2. 회원은 서비스를 이용하여 얻은 정보를 회원의
  비영리적인 이용 이외의 목적으로 복제, 출판, 방송 등에 사용하거나 제3자에게
  판매하는 등 상업적으로 사용할 수 없습니다.

  제18조 … 9) 회사의 서비스 정보를 이용하여 얻은 정보를 회사의 사전 승낙없이
  복제 또는 유통시키거나 상업적으로 이용하는 경우

주어가 '회원'이고 우리는 로그인 없는 비회원이라 CRAWLING-POLICY.md §4 의 browsewrap
논점이 그대로 걸리지만, 그 §4 의 결론은 '다투지 않는다'다. **삭제 요청이 오면
즉시 내린다.** robots.txt 는 우리를 막지 않는다 — 2026-09-30 재확인, **200**,
`User-agent: *` 에 `Disallow: /membership` 과 `Disallow: /myHollys` 둘뿐이고
우리가 때리는 /menu/*.do 는 걸리지 않는다. (403 이었다면 RFC 9309 상 전면 금지라
수집하면 안 된다. 상태코드를 확인했다.)

조사에서 '신호 확인 안 됨'으로 남은 브랜드라 직접 찾아봤다. 2026-09-30 실측 결론:
**HTML 에는 상품 단위 신제품 신호가 없다.**
  - NEW 배지 없음. 페이지 전체에서 'NEW'·'신메뉴' 문자열이 0건이다.
  - 신메뉴 전용 페이지·탭 없음. 메뉴 nav 가 espresso/hollyccino/signature/juice/
    tea/bakery/bean/md 8개 카테고리뿐이다.
  - 날짜 텍스트 0건. 상세 블록에 출시일이 없다.
  - 유일하게 비슷한 게 icon_seasolan_menu.gif('시즌 메뉴' 아이콘)인데 시즌이지
    신제품이 아니다. labels 에 '시즌메뉴'로 넣되 is_new 근거로는 쓰지 않는다.

그런데 **상품 이미지 자체에 NEW 배지가 합성돼 있다**(2026-10-01, docs/IMAGE-BADGES.md §1).
좌상단에 빨간 사각형 `NEW` 가 고정 크기·고정 위치로 박힌다. HTML 에 흔적이 없으니
픽셀로 읽는 수밖에 없고, 그게 이 브랜드의 **유일한 신상 신호**다. 아래 _has_badge 가
그 일을 한다. 라벨 '시즌메뉴'는 MD 굿즈(춘식 키링·담요)에도 붙어 신상 판정에 못 쓴다.
배지를 못 읽은 상품은 **None(모름)** 으로 둔다. 근거 없이 False 로 내리지 않는다.

날짜는 이미지 파일명의 업로드 타임스탬프(menuEtc_202608200959255100.png)뿐이다.
**uploaded_at 까지만 쓰고 released_at 에는 절대 넣지 않는다.** 실측한 분포가
메가(173건 중 81건이 2024-06)와 같은 일괄 재업로드 모양이다 — 2025-04 한 달에
전체의 1/3 가까이 몰려 있다. 그 날 다 출시됐을 리 없다.

수집 구조: 카테고리 8장이면 끝이다(8요청). 페이징도 AJAX 도 없고, 상품 상세가
목록과 같은 페이지 안에 숨은 div(.menu_view01#menuView1_<id>)로 전부 들어 있어서
상세를 따로 받을 필요가 없다. desc·영문명·ICE/HOT 까지 한 번에 나온다.
브라우저 불필요. 여기에 배지 판정용 이미지 요청이 더해지는데, 이건 이전 수집분을
재사용해 새로 생기거나 그림이 바뀐 것만 받는다(_fill_is_new).

url 은 카테고리 페이지다. 상품 단위 URL 이 사실상 없다 — onMenuChange(id) 가
같은 페이지 안에서 div 를 토글할 뿐이다. /menu/menuShare.do?div=etc&idx=..&menuDiv=..
가 상품별로 있긴 한데 열어 보면 og:title 만 박힌 빈 페이지고 JS 로 카테고리
페이지로 다시 튕긴다(2026-09-30 실측). 중간에 튕기느니 곧장 보낸다.
"""
import io
import re
import time
from urllib.parse import quote

import httpx
from PIL import Image
from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "할리스"
SITE = "https://www.hollys.co.kr"
CATEGORIES = ["espresso", "hollyccino", "signature", "juice",
              "tea", "bakery", "bean", "md"]
DELAY = 2.0

# 이미지 NEW 배지 검출. 수치 근거는 docs/IMAGE-BADGES.md §1(샘플 25장)이고,
# 2026-10-01 에 전수 240장으로 다시 재 봤다. 좌상단 빨강 비율이
#   0.0 쪽 206건(203건이 정확히 0.000, 나머지 3건도 최대 0.008)
#   0.2018~0.2019  34건  (배지 크기·위치가 고정이라 소수 4자리까지 같다)
# 둘로만 갈린다. 그 사이에 값이 하나도 없어서 임계를 어디에 둬도 결과가 같다.
#
# ⚠️ 저 0.2018 은 _has_badge 의 전처리 순서(알파 합성 → 360px 축소 → 30% 박스)를
#    그대로 밟았을 때의 값이다. 순서가 조금만 달라도 숫자가 움직인다 — 검수자가
#    알파 합성을 건너뛰고(투명부가 검게 깔린다) 같은 배지를 재니 0.2249 가 나왔다.
#    배지 테두리가 흰 배경에 섞이느냐 검은 배경에 섞이느냐의 차이다. 재현이 안 된다고
#    검출이 깨진 게 아니니 전처리부터 맞춰 보라는 뜻이다. 어느 쪽이든 0.0 쪽과는
#    20배 이상 떨어져 있어 판정(0.05)은 흔들리지 않는다.
BADGE_BOX = 0.30     # 좌상단 꼭짓점 박스 비율. **사분면(1/4)으로 재면 안 된다** —
                     # 빨간 MD 텀블러가 TL_red 0.113 으로 진짜 배지(0.072)를 앞질러
                     # 순위가 뒤집힌다. 꼭짓점 박스로 재면 그 텀블러들이 0.000 이다.
BADGE_RED = 0.05     # 판정 임계. 0.0 과 0.202 사이라 어디에 둬도 되는 수준의 마진이다.
BADGE_MIN_PX = 80    # 깨진 초소형 썸네일(미스터피자 33×27 사례)은 로고가 화면을 채워
                     # 네 꼭짓점이 동시에 붉어진다. 판정하지 않고 모름으로 둔다.
IMG_TIMEOUT = 10.0   # 이미지 1장당 상한. 느린 한 장이 수집 전체를 잡아두면 안 된다.
IMG_DELAY = 0.1      # 첫 수집은 240장을 연속으로 두드린다. 간격을 둔다.
IMG_FAIL_MIN = 5     # 과반 실패 가드를 켜는 최소 표본. 아래 _fill_is_new 참고 —
                     # 캐시가 더워지면 하루에 1~3장만 받으므로, 표본 조건이 없으면
                     # 그 한 장이 타임아웃 난 날 브랜드가 통째로 실패 처리된다.


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _text(node) -> str:
    """<br> 로 줄을 나눈 이름이 섞여 있다('블랙아리아<br>아메리카노').
    그냥 text() 를 쓰면 단어가 붙어 버려서 <br> 를 공백으로 바꾼 뒤 읽는다."""
    if not node:
        return ""
    return _clean(HTMLParser(re.sub(r"<br\s*/?>", " ", node.html or "")).text())


def _abs(src: str) -> str:
    if not src:
        return ""
    if src.startswith("//"):
        return "https:" + src
    return src if src.startswith("http") else SITE + src


def _uploaded_at(img_url: str) -> str:
    """이미지 파일명의 업로드 타임스탬프(menuEtc_202608200959255100)를 날짜로.

    released_at 에는 넣지 않는다. 브랜드가 말하는 출시일이 아니라 파일 업로드
    시각이고, 실제로 2025-04 한 달에 뭉쳐 있다(이미지 일괄 재업로드 흔적).
    """
    m = re.search(r"_(\d{4})(\d{2})(\d{2})\d{10}\.", img_url)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def _labels(doc, idx: str, seasonal: bool) -> list:
    """영양정보 표의 행 머리(HOT/ICED)가 이 상품의 제공 온도다."""
    out = []
    table = doc.css_first(f"#menuView2_{idx}")
    for th in table.css("tbody th") if table else []:
        t = _clean(th.text()).upper()
        if t in ("HOT", "ICE", "ICED") and t not in out:
            out.append(t)
    if seasonal:
        out.append("시즌메뉴")
    return out


def _img_url(src: str) -> str:
    """이미지 주소에서 규격 위반 문자(공백·따옴표·한글)만 퍼센트 인코딩한다.

    할리스 주소는 전부 ASCII 라 지금 이 함수가 바꾸는 건 없다. 그래도 거쳐 가는
    이유는 **한글이 그대로 들어간 이미지 주소가 데이터에 948행** 있어서다
    (파리바게뜨 508·빽다방 299·교촌치킨 68·맥도날드 46·써브웨이 11·BBQ 6·팔도 10).
    이 코드가 그쪽으로 옮겨갈 때 같은 데를 밟지 않게 처음부터 통과시킨다.

    2026-10-01 에 7개 브랜드 각 1장씩 실제로 때려보고 적는다. 터지는 건
    **클라이언트 문제**지 서버 문제가 아니다.
      httpx(우리 base.client) 원본 그대로 → 7/7 200. 알아서 인코딩해 보낸다.
      urllib(조사 스크립트)   원본 그대로 → 7/7 실패(UnicodeEncodeError,
                                            써브웨이만 InvalidURL).
    즉 docs/IMAGE-BADGES.md §E 의 '빽다방 25장 전멸'은 urllib 함정이다. 지금
    당장은 httpx 가 막아주지만 그 동작에 기대고 싶지 않다 — 클라이언트를 바꾸거나
    조사 스크립트를 재활용하는 순간 바로 터지고, 명시적으로 인코딩해 두면 어느
    쪽이든 같은 바이트가 나간다.

    safe 목록은 **web/seo.py 의 _URL_SAFE 와 같은 규칙**이다. 그쪽 주석에 왜
    이래야 하는지가 적혀 있다 — 요약하면 둘을 반드시 남겨야 한다.
      %    이미 인코딩된 주소를 또 인코딩하면 %25 가 겹친다(커피빈 %2520 사고).
           이 규칙 덕에 두 번 통과시켜도 결과가 같다(멱등).
      [ ]  스타벅스가 `.../[9200000007173]_2026….jpg` 형태로 서빙 중이라
           인코딩하면 404 가 난다.
    collectors/ 가 web/ 을 import 하면 의존 방향이 거꾸로라 규칙만 베꼈다.
    공용 함수로 올리려면 base.py 와 web/seo.py 를 같이 손봐야 한다(운영자 판단).
    """
    return quote(str(src or ""), safe=":/?#[]@!$&'()*+,;=-._~%")


def _has_badge(data: bytes) -> bool:
    """좌상단에 빨간 NEW 배지가 합성돼 있는가. 판정할 수 없으면 ValueError.

    투명 PNG 는 흰 배경에 먼저 합성한다(바로 RGB 로 바꾸면 투명부가 검게 깔려
    색 비율이 달라진다). 긴 변 360px 로 줄인 뒤 좌상단 꼭짓점 박스에서
    고채도 빨강 픽셀 비율을 센다.

    색 기준은 **Pillow HSV(H·S·V 모두 0-255)** 다. 0-360/0-100 스케일로 읽으면
    docs/IMAGE-BADGES.md 의 수치가 재현되지 않는다.

    ⚠️ 이 판정은 **할리스 전용**이다. 같은 자리에 다른 뜻의 배지를 쓰는 브랜드가
    있다(컴포즈 노란 별 = NEW/베스트/콤보, 메가 `ONLY ICE`). 범용 헬퍼로 올려
    아무 브랜드에나 돌리면 신상이 아닌 걸 신상으로 잡는다.
    """
    im = Image.open(io.BytesIO(data))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        im = Image.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, 255)), im)
    im = im.convert("RGB")
    if im.width < BADGE_MIN_PX or im.height < BADGE_MIN_PX:
        raise ValueError(f"이미지가 너무 작다 ({im.width}x{im.height})")
    im.thumbnail((360, 360))
    box = im.crop((0, 0, int(im.width * BADGE_BOX), int(im.height * BADGE_BOX)))
    # HSV 바이트열을 직접 훑는다. getdata() 는 Pillow 14 에서 사라진다.
    raw = box.convert("HSV").tobytes()
    red = sum(1 for i in range(0, len(raw), 3)
              if raw[i + 1] >= 150 and raw[i + 2] >= 120
              and (raw[i] <= 10 or raw[i] >= 245))
    return red / (len(raw) // 3) >= BADGE_RED


def _fill_is_new(client, items: list, known: dict) -> None:
    """상품 이미지를 받아 NEW 배지를 읽고 is_new 를 채운다.

    240장을 매 수집마다 다시 받으면 CI 가 그만큼 느려진다. 이전 수집분에 같은
    키가 있고 **이미지 주소까지 그대로면** 그때 내린 판정을 재사용한다. 주소가
    바뀌었으면 배지가 붙거나 떨어진 것일 수 있으니 다시 받는다. 이전 판정이
    None(모름)인 것도 다시 받는다 — 그게 지난번 실패분의 재시도 경로다.

    못 받은 한 장 때문에 수집 전체를 죽이지 않는다. 그 상품만 is_new 를 None 으로
    두고 넘어간다(화면에서는 신제품이 아닌 것과 똑같이 취급된다). False 로 내리면
    '배지 없음을 확인했다'는 뜻이 되고 그 오판이 캐시에 박혀 다시 확인하지도 않는다.
    다만 **과반이 실패하면 예외로 올린다.** 조용히 전부 '신상 아님'이 되면 할리스가
    통째로 사라지는데, 이 프로젝트가 가장 여러 번 데인 게 그런 조용한 실패다.
    """
    done: dict = {}          # 이미지 주소 → 판정. 같은 그림을 두 번 받지 않는다
    tried = failed = 0
    for it in items:
        if not it.image:
            continue
        old = known.get(it.key)
        if old and old.get("image") == it.image and old.get("is_new") is not None:
            it.is_new = old["is_new"]
            continue
        if it.image in done:
            it.is_new = done[it.image]
            continue
        tried += 1
        try:
            r = client.get(_img_url(it.image), timeout=IMG_TIMEOUT)
            r.raise_for_status()
            it.is_new = _has_badge(r.content)
            done[it.image] = it.is_new
        except (httpx.HTTPError, OSError, ValueError) as e:
            failed += 1
            print(f"  할리스 이미지 실패: {it.name} — {type(e).__name__}: {e}")
        time.sleep(IMG_DELAY)

    # 과반 실패는 '배지 판정이 통째로 깨졌다'는 뜻이라 예외로 올린다. 단 표본이
    # IMG_FAIL_MIN 보다 적으면 비율을 믿지 않는다. 캐시가 더워지면 tried 가 그날
    # 신규 상품 수(보통 1~3건)로 떨어지는데, 그때 한 장만 타임아웃 나도 1/1=100%가
    # 되어 collect.py 가 할리스 238건을 통째로 실패 처리해 버린다(이전분 carry).
    # 신상 한 건 못 읽은 대가로 브랜드 전체가 멈추는 건 막으려던 사고의 반대편이다.
    if tried >= IMG_FAIL_MIN and failed * 2 > tried:
        raise RuntimeError(
            f"할리스 이미지 {tried}건 중 {failed}건 실패 — 배지 판정이 통째로 깨졌다")
    print(f"  할리스 배지 판정 {tried}건 (캐시 {len(items) - tried}건)")


def fetch(known: dict | None = None) -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        for i, cat in enumerate(CATEGORIES):
            if i:
                time.sleep(DELAY)
            url = f"{SITE}/menu/{cat}.do"
            r = base.retry(lambda: c.get(url))
            r.raise_for_status()
            doc = HTMLParser(r.text)
            blocks = doc.css("div.menu_view01")
            # 카테고리가 통째로 비면 조용한 부분수집이 된다. 예외로 올려 드러낸다.
            if not blocks:
                raise RuntimeError(f"할리스 {cat}: 상품 0건 — 셀렉터가 깨졌을 수 있다")

            h2 = doc.css_first("h2.h2menu")
            category = _clean(h2.text()) if h2 else cat.upper()

            for b in blocks:
                idx = (b.attributes.get("id", "") or "").replace("menuView1_", "")
                detail = b.css_first(".menu_detail")
                if not detail:
                    continue
                # <p><span>국문명</span> 영문명</p> 구조다.
                p = detail.css_first("p")
                name = _text(p.css_first("span")) if p else ""
                if not name:
                    continue
                name_en = _text(p).replace(name, "", 1).strip() if p else ""
                img = b.css_first("img")
                src = _abs(img.attributes.get("src", "") if img else "")
                info = detail.css_first("p.menu_info")
                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en=name_en,
                    desc=_text(info),
                    image=src,
                    labels=_labels(doc, idx, bool(b.css_first("img[src*='icon_seasolan_menu']"))),
                    category=category,
                    uploaded_at=_uploaded_at(src),
                    url=url,
                )
                if it.key in seen:            # 같은 상품이 두 카테고리에 걸쳐 있다
                    continue
                seen.add(it.key)
                items.append(it)

        # is_new 는 HTML 이 아니라 이미지에서 나온다. 목록을 다 모은 뒤 한 번에 판정한다.
        _fill_is_new(c, items, known or {})
    return items
