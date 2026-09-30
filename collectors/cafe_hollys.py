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
**상품 단위 신제품 신호가 없다.**
  - NEW 배지 없음. 페이지 전체에서 'NEW'·'신메뉴' 문자열이 0건이다.
  - 신메뉴 전용 페이지·탭 없음. 메뉴 nav 가 espresso/hollyccino/signature/juice/
    tea/bakery/bean/md 8개 카테고리뿐이다.
  - 날짜 텍스트 0건. 상세 블록에 출시일이 없다.
  - 유일하게 비슷한 게 icon_seasolan_menu.gif('시즌 메뉴' 아이콘)인데 시즌이지
    신제품이 아니다. labels 에 '시즌메뉴'로 넣되 is_new 근거로는 쓰지 않는다.
그래서 is_new 는 **전건 None(모름)** 이다. 근거 없이 False 로 내리지 않는다.

날짜는 이미지 파일명의 업로드 타임스탬프(menuEtc_202608200959255100.png)뿐이다.
**uploaded_at 까지만 쓰고 released_at 에는 절대 넣지 않는다.** 실측한 분포가
메가(173건 중 81건이 2024-06)와 같은 일괄 재업로드 모양이다 — 2025-04 한 달에
전체의 1/3 가까이 몰려 있다. 그 날 다 출시됐을 리 없다.

수집 구조: 카테고리 8장이면 끝이다(8요청). 페이징도 AJAX 도 없고, 상품 상세가
목록과 같은 페이지 안에 숨은 div(.menu_view01#menuView1_<id>)로 전부 들어 있어서
상세를 따로 받을 필요가 없다. desc·영문명·ICE/HOT 까지 한 번에 나온다.
브라우저 불필요.

url 은 카테고리 페이지다. 상품 단위 URL 이 사실상 없다 — onMenuChange(id) 가
같은 페이지 안에서 div 를 토글할 뿐이다. /menu/menuShare.do?div=etc&idx=..&menuDiv=..
가 상품별로 있긴 한데 열어 보면 og:title 만 박힌 빈 페이지고 JS 로 카테고리
페이지로 다시 튕긴다(2026-09-30 실측). 중간에 튕기느니 곧장 보낸다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "할리스"
SITE = "https://www.hollys.co.kr"
CATEGORIES = ["espresso", "hollyccino", "signature", "juice",
              "tea", "bakery", "bean", "md"]
DELAY = 2.0


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


def fetch() -> list[Item]:
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
    return items
