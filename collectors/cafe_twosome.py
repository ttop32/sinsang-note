"""투썸플레이스(TWOSOME PLACE).

notes/CANDIDATES-CAFE2.md §2 가 '불가'로 접었던 브랜드다. 그 판정의 전제는
**www 하나뿐**이었다 — www.twosome.co.kr 은 CloudFront WAF 가 우리 UA 를 403 으로
막고(2026-10-02 재확인, robots.txt 조차 403), 뚫는 유일한 길이 브라우저 UA 위장이라
접었다. 위장은 지금도 하지 않는다.

**그런데 모바일 호스트는 WAF 뒤에 있지 않다.**

  dig m.twosome.co.kr  → 211.115.119.191   (www 는 CloudFront 18.64.8.x)
  GET https://m.twosome.co.kr/  → 302 → mo.twosome.co.kr, **우리 UA 로 200**

같은 회사의 같은 메뉴 데이터인데 앞단만 다르다. 호스트를 바꾼 것일 뿐
UA 는 base.UA 그대로 보낸다. 위장이 아니다.

mo.twosome.co.kr/robots.txt 는 `User-agent: * / Disallow: /` 다. 운영자 승인 아래
무시한다(이 레포의 롯데리아·엔제리너스와 같은 취급). 삭제 요청이 오면 즉시 내린다.

## 엔드포인트

메뉴 목록 페이지(/mn/menuInfoList.do)는 껍데기고 실제 데이터는 XHR 이다.

  POST https://mo.twosome.co.kr/mn/menuInfoListAjax.json
       pageNum=1&grtCd=<대분류>&midCd=
  → {"queryCode":1000, "fetchResultListSet":[{MENU_CD, MENU_NM, EN_MENU_NM,
      MENU_IMG, GRT_NM, MID_NM, BADG_CD, BADG_NM, TOTAL_COUNT, NEXT_PAGE}, ...]}

대분류는 목록 페이지의 탭에서 읽는다(NEW / 1 커피·음료 / 4 홀케이크 / 2 디저트 /
3 푸드 / 5 상품). 현재는 카테고리당 1페이지에 전건이 오고 NEXT_PAGE 가 0 이다
(최대 90건). 그래도 NEXT_PAGE 를 따라가게 짰다 — 품목이 늘면 서버가 쪼갠다.

## 신제품 신호: BADG_NM 이 'New' 인가

⚠️ **aria-label 이나 탭 이름을 믿으면 안 된다.** 교차검증한 것을 적는다
(2026-10-02, 전 카테고리 324행 / 중복 제거 318품목).

  - NEW 탭이 주는 6건과, 일반 카테고리에서 BADG_NM='New' 인 6건이
    **MENU_CD 집합까지 정확히 일치한다.** 세븐일레븐처럼 '신상품 탭이 다른
    엔드포인트라 뱃지가 빠지는' 경우가 아니다.
  - 배지는 신상 전용이 아니다 — 같은 자리에 BADG_NM='Best' 가 7건 있다.
    즉 '전부 New' 가 아니고, 문자열로 갈라야 한다.
  - 비율이 **6/318 = 1.9%** 다. 이디야(2017년 상품)·버거킹(31%)처럼 배지를
    안 내리는 브랜드가 아니다.

그래서 is_new 는 **BADG_NM 이 'New'** 일 때만 True 고, 목록에 실린 나머지는
False 다(배지가 없음을 확인한 것이므로). NEW 탭은 같은 걸 한 번 더 주는 셈이라
읽지 않는다 — 요청만 늘고 중복만 생긴다.

## 날짜

브랜드가 출시일을 주지 않는다. 상세(/mn/menuInfoDetail.do)에도 없다 —
거기 보이는 2025.10.13·2021.06.16 은 전부 **소스 주석**이다.

쓸 수 있는 건 이미지 파일명의 업로드 시각뿐이다.
  10193792_01_01_**20260831**025202.jpg → 2026-08-31
**uploaded_at 까지만 쓰고 released_at 에는 넣지 않는다.** 다만 할리스·메가와 달리
일괄 재업로드 자국은 없다 — 324건의 월 분포가 2025-11 2 / 2025-12 13 / 2026-01 15 /
… / 2026-06 35 / 2026-09 28 로 고르게 퍼져 있다(최다 달이 전체의 11%). 54건은
파일명에 시각이 없어 빈값이다.

## 그 밖에

- '상품 > 카페용품' 70건은 트래블백·선풍기·키링 같은 MD 다. base.is_nonfood 가
  '에코백'·'키링'은 잡지만 '트래블백'·'피규어 선풍기'는 못 잡는다. 분류로
  확실하게 nonfood 를 찍는다.
- url 은 mo. 호스트의 상세다. www 쪽 같은 경로는 우리가 열어볼 수 없어
  살아 있는지 확인할 방법이 없다 — 확인한 주소만 쓴다.
- desc·온도 라벨은 목록에 없고 상세에만 있다. 상세가 1건당 37KB 라 전건
  받으면 12MB 다. **신상으로 판정한 것만** 받는다(현재 6건).
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "투썸플레이스"
SITE = "https://mo.twosome.co.kr"
LIST_URL = f"{SITE}/mn/menuInfoList.do"
AJAX_URL = f"{SITE}/mn/menuInfoListAjax.json"
DETAIL_URL = f"{SITE}/mn/menuInfoDetail.do"

# 대분류. 'NEW' 탭은 일부러 뺐다 — 배지와 결과가 같아서 중복만 만든다(docstring).
CATEGORIES = ["1", "4", "2", "3", "5"]
DELAY = 2.0
MAX_PAGES = 20       # 폭주 방지. 현재 카테고리당 1페이지.
MAX_DETAILS = 30     # 상세를 받을 상한. 현재 신상 6건.

NONFOOD_MIDS = {"카페용품"}


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _uploaded_at(img: str) -> str:
    """이미지 파일명 끝의 업로드 시각(..._20260831025202.jpg)을 날짜로."""
    m = re.search(r"_(\d{4})(\d{2})(\d{2})\d{6}\.", img or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def _detail(c, menu_cd: str) -> tuple:
    """상세에서 (desc, labels). 실패하면 조용히 빈 값으로 둔다."""
    r = base.retry(lambda: c.get(DETAIL_URL, params={"menuCd": menu_cd}))
    r.raise_for_status()
    doc = HTMLParser(r.text)

    # ⚠️ `p.desc` 를 셀렉터로 쓰면 **빈 문자열이 나온다.** 마크업이
    # `<p class="desc"><p>설명 첫 줄</p><p>둘째 줄</p></p>` 인데 <p> 는 <p> 를
    # 품을 수 없어서 파서가 바깥 것을 먼저 닫아 버린다. 설명은 형제로 밀려난다.
    # 그래서 한 단계 위(dd)를 통째로 읽는다.
    desc = ""
    dd = doc.css_first(".menu-detail-info-title dd")
    if dd:
        # '※ 알레르기 유발요인 …' 은 설명이 아니라 고지사항이다.
        desc = _clean(dd.text()).split("※")[0].strip()

    labels = []
    for a in doc.css(".hot_n_iced a"):
        t = _clean(a.text())
        if t.startswith("핫") and "HOT" not in labels:
            labels.append("HOT")
        elif t.startswith("아이스") and "ICE" not in labels:
            labels.append("ICE")
    return desc, labels


def _page(c, grt: str, page: int) -> list:
    def go():
        return c.post(AJAX_URL, data={"pageNum": str(page), "grtCd": grt, "midCd": ""})
    r = base.retry(go)
    r.raise_for_status()
    d = r.json()
    # 서버가 자기 오류를 200 + queryCode 로 알려준다. 조용한 0건으로 흘리지 않는다.
    if d.get("queryCode") != 1000:
        raise RuntimeError(f"투썸 {grt} p{page}: {d.get('queryCode')} {d.get('queryMessage')}")
    return d.get("fetchResultListSet") or []


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client(headers={"Referer": LIST_URL}) as c:
        first = True
        for grt in CATEGORIES:
            page = 1
            while page and page <= MAX_PAGES:
                if not first:
                    time.sleep(DELAY)
                first = False
                rows = _page(c, grt, page)
                if not rows:
                    break
                for x in rows:
                    name = _clean(x.get("MENU_NM"))
                    if not name:
                        continue
                    img = x.get("MENU_IMG") or ""
                    mid = _clean(x.get("MID_NM"))
                    it = Item(
                        brand=BRAND,
                        name=name,
                        name_en=_clean(x.get("EN_MENU_NM")),
                        image=(SITE + img) if img.startswith("/") else img,
                        category=mid or _clean(x.get("GRT_NM")),
                        uploaded_at=_uploaded_at(img),
                        # 배지 문자열로만 가른다. 'Best' 가 같은 자리에 온다.
                        is_new=(x.get("BADG_NM") == "New"),
                        nonfood=mid in NONFOOD_MIDS,
                        url=f"{DETAIL_URL}?menuCd={x.get('MENU_CD')}",
                    )
                    if it.key in seen:      # 같은 상품이 두 카테고리에 걸쳐 있다
                        continue
                    seen.add(it.key)
                    items.append(it)
                nxt = rows[0].get("NEXT_PAGE") or 0
                page = int(nxt) if nxt else 0

        # 목록이 통째로 비면 조용한 0건 수집이 된다. 예외로 올려 드러낸다.
        if not items:
            raise RuntimeError("투썸플레이스 0건 — WAF 나 엔드포인트가 바뀌었을 수 있다")

        for it in [i for i in items if i.is_new][:MAX_DETAILS]:
            time.sleep(DELAY)
            cd = it.url.rsplit("=", 1)[-1]
            it.desc, it.labels = _detail(c, cd)

    return items
