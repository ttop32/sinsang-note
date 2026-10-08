"""뚜레쥬르.

1차(`CANDIDATES-BAKERY.md` §뚜레쥬르)에서 **robots 전면 차단**으로 접었던 곳이다.

```
## disallow all other bots
User-agent: *
Disallow: /
## Google
User-agent: Googlebot
Allow: /$
Allow: /product
```

**2026-10-02 운영자가 robots 무시를 승인**해서 다시 연다. 1차가 "사이트에 제품 > NEW
카테고리가 있지만 붙이면 안 된다"고 적어둔 그 NEW 카테고리가 이 어댑터의 소스다.

EUC-KR ASP 다. `r.text` 로 읽으면 상품명이 통째로 깨지니 `r.content.decode("euc-kr")`
로 직접 벗긴다(`china_tanghuo` 와 같은 처리). 전부 SSR, 브라우저 불필요. 2026-10-08 실측.

## 경로를 찾은 방법

사이트 내비가 전부 `javascript:showMenuInfo('010101','U')` 라 HTML 만 봐서는 경로가
안 나온다. 메뉴 트리는 **`/inc/js/menu.js` 안에 JSON 으로 통째로** 들어 있다
(`"nm":"신제품","link":"/product/new.asp"`). 여기서 두 장을 골랐다.

  GET /product/new.asp      신제품 — 최신 묶음 1건. 2026-10-08 현재 **11건**
  GET /product/result.asp   제품 검색결과(검색어 없음) = **전 카탈로그 442건 한 장**

`/product/list.asp?ref=<n>&cg_num=<m>` 쪽 카테고리 페이지는 **15건씩 끊긴다**
(빵·케이크·델리·음료·디저트&스낵·선물 전부 15). 6칸을 페이징까지 돌면 30요청이 넘는데
`result.asp` 한 장이 442건을 다 주므로 그쪽을 쓴다.

## 신제품 신호 — `/product/new.asp` 는 **신제품 캠페인 전용 페이지**다

`new.asp` 는 '그때그때의 신제품 묶음' 한 건을 보여준다. 지금 걸린 건 `seq=231`
**"26 추석"** 이고 상품 11건이다. 페이지 안 `.new_list` 에 **과거 묶음 24페이지 분량**
(`new.asp?seq=230 26 올디스타코 콜라보`, `seq=229 26 여름시즌` …)이 링크로 나열된다.
즉 **브랜드가 직접 끊어 올리는 신제품 공지 시리즈**지, 상시 메뉴가 쌓이는 탭이 아니다.

소스 자체가 신제품 전용 목록이라 **여기 11건은 100% `is_new=True` 가 정상**이다
(퀴즈노스 66/66 과 겉모양은 같지만 성격이 반대다 — 저쪽은 메뉴판 전체에 NEW 가 붙은
것이었다). 전 카탈로그 442건과의 비율로 보면 **11/442 = 2.5%** 다.

마크업의 `<span class="lb_new">New</span>` 는 **주석 처리돼 있다**(노티드 41개와 같다).
배지를 세면 안 되고, 페이지 자체가 신호다.

**하이오커피 함정 점검** — 저쪽은 '신메뉴' 40건이 1년치 바구니라 10월에 쌍화차와
컵빙수가 공존했다. 여기 11건은 사진 날짜가 **2026-09-04 ~ 2026-09-18 한 달 안**이고
품목도 추석 선물세트·가을 롤케이크로 서로 모순이 없다. 바구니가 아니다.

```
쌀맛나는 케이크              2026-09-16
흑임자 롤케이크              2026-09-04
디카페인커피 헤이즐넛 롤케이크   2026-09-04
웨이퍼 샌드 선물세트          2026-09-08
갓샌드 세트                 2026-09-18
한아름 약과 세트             2026-09-18
삼색 모나카 세트             2026-09-04
뚜당케(뚜레쥬르 당근 케이크)    2026-09-18
딸기 웨이퍼 샌드             2026-09-08
요거트 웨이퍼 샌드            2026-09-08
블루베리 요거트 웨이퍼 샌드      2026-09-08
```

11건 중 8건은 전 카탈로그에도 그대로 있다. 겹치는 게 흠이 아니다 — 빵집은 신제품이
곧바로 상시 메뉴로 들어간다. 나머지 3건(선물세트류)은 `result.asp` 에 아직 없다.

## 날짜 — 이미지 파일명. **`released_at` 이 아니다**

`/data/product/2026-9-16_event(1).jpg` 꼴이라 앞이 날짜다. **월·일에 0 이 안 붙는다**
(`2026-9-4`), 정규식에 두 자리를 강제하면 통째로 놓친다.

전 카탈로그 442건의 월별 분포는 고르다 — `2026-10` 3 / `2026-09` 17 / `2026-08` 26 /
`2026-07` 14 / `2026-06` 20 … 파리바게뜨 312장이나 아웃백 `20250422` 28건 같은 일괄
재업로드 봉우리가 없다. 그래도 **브랜드가 "출시일"이라고 말한 값이 아니라 사진 올린
날짜**라서 `uploaded_at` 에만 넣는다. `rules.untrust_bulk_dates()` 가 보는 자리도 거기다.

## 나머지 필드

  img[alt]        상품명. ⚠️ `.name` 은 **12자에서 잘린다**(`더 고소한 호두 아몬드 케...`).
                  alt 에 전체가 들어 있으니 alt 를 쓰고 `.name` 은 폴백이다.
  .txt_shape      카테고리(`Cake`/`Drink`/`Dessert`/`Gift`). new.asp 에는 없다
  .desc           설명. 줄바꿈이 들어 있어 공백으로 접는다
  viewDetail(5586)  → /product/detail.asp?gubun=new&prod_num=5586 (실측 200)

등록 제안: 유형 **`CAFE`**, 세부분류 `베이커리`.
⚠️ `FRANCHISE` 로 넣으면 1단 탭이 '카페'가 아니라 '외식'으로 간다.

⚠️ **CJ푸드빌 계열 중복 주의.** 모회사 `cjfoodville.co.kr` 에는 상품 목록이 없다
(§`notes/RECHECK-ROBOTS-DINING.md` 참고). 빕스도 자기 사이트를 쓴다. 겹치지 않는다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "뚜레쥬르"
SITE = "https://www.tlj.co.kr"
NEW = SITE + "/product/new.asp"        # 신제품 캠페인 최신 1건
ALL = SITE + "/product/result.asp"     # 전 카탈로그 442건
VIEW = SITE + "/product/detail.asp?gubun=new&prod_num={}"
DELAY = 1.6

# `/data/product/2026-9-16_event(1).jpg`. ⚠️ 월·일에 0 이 안 붙는다.
_UPLOADED = re.compile(r"/data/product/(\d{4})-(\d{1,2})-(\d{1,2})[_.]")
_PDT = re.compile(r"viewDetail\(\s*'?(\d+)'?\s*\)")


def _euckr(r) -> str:
    """EUC-KR ASP. r.text 로 읽으면 상품명이 통째로 깨진다."""
    return r.content.decode("euc-kr", "replace")


def _uploaded_at(src: str) -> str:
    m = _UPLOADED.search(src or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _rows(html: str) -> list:
    """`li.item_wrap` → (이름, 카테고리, 이미지경로, 설명, prod_num)."""
    out = []
    for li in HTMLParser(html).css("li.item_wrap"):
        img = li.css_first(".img img")
        # selectolax 는 값 없는 속성에 None 을 준다. 기본값이 안 먹는다.
        alt = " ".join((img.attributes.get("alt") or "").split()) if img else ""
        src = (img.attributes.get("src") or "") if img else ""
        nm = li.css_first(".name")
        # ⚠️ .name 은 12자에서 잘린다. alt 가 전체 이름이다.
        name = alt or (" ".join(nm.text().split()) if nm else "")
        if not name:
            continue
        shape = li.css_first(".txt_shape")
        desc = li.css_first(".over .desc")
        pdt = _PDT.search(li.html or "")
        out.append((
            name,
            " ".join(shape.text().split()) if shape else "",
            src,
            " ".join(desc.text().split()) if desc else "",
            pdt.group(1) if pdt else "",
        ))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()

    with base.client() as c:
        r = base.retry(lambda: c.get(NEW))
        r.raise_for_status()
        new_rows = _rows(_euckr(r))
        # 신제품 묶음이 통째로 비면 캠페인이 갈리는 중이거나 마크업이 바뀐 것이다.
        # 조용히 0건으로 넘기지 않는다 — 급감 가드에도 안 걸린다.
        if not new_rows:
            raise RuntimeError(
                f"{NEW}: 신제품 0건 — 'li.item_wrap' 이 비었다. 2026-10-08 실측은 "
                f"11건(seq=231 '26 추석')이었다")

        time.sleep(DELAY)
        rr = base.retry(lambda: c.get(ALL))
        rr.raise_for_status()
        all_rows = _rows(_euckr(rr))
        if not all_rows:
            raise RuntimeError(
                f"{ALL}: 전 카탈로그 0건 — 'li.item_wrap' 이 비었다. "
                f"2026-10-08 실측은 442건이었다")

        # 신제품을 먼저 넣는다. 같은 상품이 카탈로그에도 있어서(11건 중 8건)
        # 순서를 바꾸면 is_new=False 쪽이 이긴다.
        for rows, is_new in ((new_rows, True), (all_rows, False)):
            for name, shape, src, desc, pdt in rows:
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=desc,
                    image=SITE + src if src.startswith("/") else src,
                    category=shape,
                    # 사진 파일명의 날짜다. 브랜드가 말한 출시일이 아니라
                    # released_at 에 넣지 않는다 — 모듈 주석 참고.
                    uploaded_at=_uploaded_at(src),
                    is_new=is_new,
                    url=VIEW.format(pdt) if pdt else "",
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

    new_count = sum(1 for i in items if i.is_new)
    if new_count > len(items) * 0.5:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {new_count}건이 신제품이다 — 2026-10-08 "
            f"실측은 442건 중 11건(2.5%)이었다. result.asp 가 전 카탈로그를 주지 "
            f"않으면 메뉴판이 통째로 신상으로 올라간다")
    dated = sum(1 for i in items if i.uploaded_at)
    if dated < len(items) * 0.9:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 날짜를 {dated}건밖에 못 읽었다 — "
            f"'/data/product/YYYY-M-D_' 규칙이 바뀌었다(⚠️ 월·일에 0 이 안 붙는다). "
            f"날짜를 비우면 60일 창을 건너뛴다")
    return items
