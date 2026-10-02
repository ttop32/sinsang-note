"""담꾹((주)디엔에프씨).

가맹점 266개로 공정위 `한식` 업종 중위권이다(2025년도 정보공개서, 2024년 말 기준).
매장에서 데워 내는 밀키트형 한식 프랜차이즈다.

`/recipe/menus/` 한 장이 전체 메뉴를 SSR 로 담는다. 쿠키·세션·JS 불필요.
`?cate_indx=` 로 거르는 분류가 셋이고(1 신메뉴 / 2 인기메뉴 / 3 시즌메뉴) 인자를
빼면 전체다. **총 4요청에 44건**(2026-10-02 실측).

신제품 신호가 둘인데, 이 프로젝트에서 **둘이 가장 깨끗하게 맞아떨어진 사례**다.

  is_new  `?cate_indx=1` 이 '신메뉴' 전용 분류다. 전체 44건 중 8건이 여기 실린다.
  uploaded_at  썸네일 파일명이 `YYMMDD_<일련번호>.jpg` 다.
          `260721_755.jpg` → 2026-07-21. 44건 **전부** 파싱되고 미래 날짜가 하나도
          없다(최대 2026-07-21, 조사일 2026-10-02). 범위는 2022-08-23 ~ 2026-07-21.

  🔵 **교차검증 — 신메뉴 8건이 파일명 날짜 최신 8건과 정확히 같은 집합이다.**
          2026-07-21 3건 + 2026-04-22 1건 + 2026-01-27 4건 = 8건이고, 이게
          `cate_indx=1` 목록과 한 건도 어긋나지 않는다. 브랜드가 손으로 고른
          분류와, 그 분류를 모르는 파일명 날짜가 **독립적으로 같은 답**을 냈다.
          세븐일레븐 '신상품' 탭처럼 분류만 다르고 목록은 같은 가짜가 아니다 —
          전체 44건을 돌려주는 경로가 따로 있고 거기서 8건만 골라낸 것이다.
          (덤으로 모달 id `lp_NN` 도 오래된 것일수록 작다. lp_97 이 최신,
           lp_1 이 2022-08-23 자 부대찌개다. 세 번째 축도 어긋나지 않는다.)

  🔵 **Last-Modified 로 한 번 더 받아봤다**(8건 표본). 파일명과 헤더가 같다 —
          `260422_711.jpg`→2026-04-22, `260127_700.jpg`→2026-01-27,
          `251112_644.jpg`→2025-11-12, `250402_555.jpg`→2025-04-02,
          `230904_39.jpg`→2023-09-04, `220823_19.jpg`→2022-08-23. 8건 중 6건이
          초 단위까지 같은 날이고, `260721_755.jpg` 는 하루 뒤(07-22 업로드),
          `220823_1-1.jpg` 는 2022-10-25 다. 뒤 둘은 **같은 이름으로 사진만 다시
          올린 경우**라 헤더가 밀린 것이다. 그래서 어댑터는 **파일명 쪽을 쓴다** —
          재업로드에 흔들리지 않고, HEAD 요청 44번을 아낀다.

**released_at 에는 넣지 않는다.** 브랜드가 "출시일"이라고 말한 값이 아니라 사진을
올린 날짜다(본아이에프 cmdtListImg·한솥 imagePath·원앤원과 같은 처분).
특히 2022-08-23 에 15건이 몰려 있는데 이건 사이트를 처음 만들 때 통째로 올린
흔적이지 그 15종이 그날 나왔다는 뜻이 아니다 — 큰맘할매순대국 2025-12-22 와 같은
자리다. **최근 날짜는 믿을 만하고 2022-08-23 은 사이트 구축일**로 읽어야 한다.

`is_new` 는 **True 와 False 양쪽으로 쓴다.** 한 요청이 전체 메뉴를 다 돌려주고
그 안에서 브랜드가 8건만 따로 골라 담은 구조라 '안 담긴 건 신상이 아니다'로 읽어도
무리가 없다(에그드랍 category=NEW, 폴바셋 newIcon, 큰맘할매순대국 tab-new 와 같은
처분). 신메뉴 분류가 **인기메뉴·시즌메뉴와 한 건도 겹치지 않는 것**도 브랜드가
이 셋을 배타적으로 관리한다는 뜻이라 신뢰를 더한다(인기∩시즌은 4건 겹친다).

`category` 는 비운다. 이 사이트의 분류 셋은 전부 판매 전략(신메뉴·인기·시즌)이지
음식 종류가 아니다. 억지로 넣으면 다른 브랜드의 '순대국'·'돈까스' 와 같은 칸에
'인기메뉴' 가 들어간다. 대신 인기·시즌은 `labels` 로 화면에 남긴다.

`desc` 는 **일부러 비운다.** 모달(`openmodal('lp_97')`)에 글이 있긴 한데 상품 설명이
아니라 매장용 **조리법**이다("냉동상태의 묵은지 고등어조림을 흐르는 물에 담그거나
전날 냉장고에서 완전히 해동한다" / "중불로 줄여 약 10~15분간 끓여준다"). 이걸
상품 설명 자리에 넣으면 카드가 이상해진다. 한 줄 소개는 사이트 어디에도 없다.

`Item.url` 도 비운다. 모달이 주소를 갖지 않는다 — `openmodal()` 이 숨은 div 를
JS 로 띄울 뿐이라 `#lp_97` 로 들어가도 아무 일도 일어나지 않는다. `base.site()` 의
메뉴 페이지로 떨어뜨린다(큰맘할매순대국과 같은 처분).

가격은 사이트에 없다. 이미지는 `dnfcm1.cafe24.com` 에 https 로 올라가 있다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "담꾹"
URL = "https://www.damgguk.com/recipe/menus/"
DELAY = 1.4          # 요청 간격(초). 전부 4요청이다.

# cate_indx → 분류명. 빈 키가 '전체'다. 전체를 먼저 받아 목록을 만들고
# 나머지 셋으로 표시만 덧칠한다.
NEW_CATE = "1"
CATES = {
    NEW_CATE: "신메뉴",
    "2": "인기메뉴",
    "3": "시즌메뉴",
}

# 썸네일 파일명 앞의 YYMMDD. `260721_755.jpg` · `221129_hambak.jpg` 둘 다 잡는다.
_STAMP = re.compile(r"^(\d{2})(\d{2})(\d{2})_")
# 카드가 여는 모달 id. 이 사이트에서 상품을 가리키는 유일한 안정 키다.
_LPID = re.compile(r"openmodal\('([^']+)'\)")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _uploaded_at(src: str) -> str:
    """썸네일 파일명 앞 YYMMDD 를 날짜로. 안 읽히면 비운다(날짜는 지어내지 않는다).

    출시일이 아니라 사진을 올린 날짜다 — docstring 의 유보 사항을 읽어라.
    """
    m = _STAMP.match((src or "").rsplit("/", 1)[-1])
    if not m:
        return ""
    y, mo, d = (int(g) for g in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"20{y:02d}-{mo:02d}-{d:02d}"


def _cards(c, cate: str) -> list:
    """(모달id, 상품명, 썸네일 URL) 목록. cate 가 빈 문자열이면 전체."""
    r = base.retry(lambda: c.get(URL, params=({"cate_indx": cate} if cate else {})))
    r.raise_for_status()
    time.sleep(DELAY)

    out = []
    for a in HTMLParser(r.text).css("section.products a[onclick]"):
        m = _LPID.search(a.attributes.get("onclick", "") or "")
        name = a.css_first("div")
        img = a.css_first("img")
        if not m or not name:
            continue
        out.append((m.group(1), _clean(name.text()),
                    img.attributes.get("src", "") if img else ""))
    return out


def fetch() -> list[Item]:
    with base.client() as c:
        everything = _cards(c, "")
        if not everything:
            raise RuntimeError("담꾹 전체 메뉴: 상품 0건 — 셀렉터가 깨졌을 수 있다")

        # 분류별 모달 id 집합. 전체 목록에 덧칠할 표시로만 쓴다.
        tagged: dict = {}
        for cate, label in CATES.items():
            ids = {lp for lp, _, _ in _cards(c, cate)}
            if cate == NEW_CATE and not ids:
                raise RuntimeError("담꾹 신메뉴 분류: 상품 0건 — 구조가 바뀌었다")
            tagged[label] = ids

    new_ids = tagged["신메뉴"]
    items: list[Item] = []
    seen: set = set()
    for lp, name, src in everything:
        if not name:
            continue
        key = base.make_key(BRAND, name)
        if key in seen:
            continue
        seen.add(key)
        items.append(Item(
            brand=BRAND,
            name=name,
            image=src,
            # 신메뉴는 is_new 로 가므로 라벨에서 뺀다. 인기·시즌만 화면에 남긴다.
            labels=[l for l in ("인기메뉴", "시즌메뉴") if lp in tagged[l]],
            # 분류 셋이 전부 판매 전략이라 음식 종류 칸에는 넣지 않는다(docstring).
            category="",
            # 사진 올린 날짜. 출시일이 아니다(docstring 참고).
            uploaded_at=_uploaded_at(src),
            # 전체 목록이 따로 있고 거기서 8건을 골라낸 구조라 False 도 쓴다.
            is_new=lp in new_ids,
            # 1+1·할인 행사가 이 사이트에 없다.
            promo=False,
        ))
    return items
