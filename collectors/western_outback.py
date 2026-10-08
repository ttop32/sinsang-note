"""아웃백스테이크하우스.

`CANDIDATES-WESTERN.md` 에서 **"이 카테고리 기술적으로 최고인데 약관이 막는다"** 로
접혔던 곳이다. 막은 건 robots 가 아니라 이용약관 제10조 ④(자동 접속 프로그램·
일체의 크롤링 금지)였고, **2026-10-02 운영자가 약관 무시를 승인**해서 다시 연다.
robots 자체는 원래 열려 있었다 — `.do` 두 개(`/qkO3DtBJHg0se.do`,
`/A0RG7SrkDWpB.do`)만 막고 나머지는 `Allow: /` 다.

전부 SSR 이다. 브라우저 불필요. 2026-10-08 실측.

## 경로

  GET /menu/productList.do?cateIdx=<n>&menuIdx=43     카테고리별 상품 목록
  GET /menu/productView.do?cateIdx=<n>&pdtIdx=<id>&menuIdx=43   상품 상세

**cateIdx 를 박지 않는다.** 목록 페이지의 좌측 내비에 `/menu/main.do?menuIdx=43&
cateIdx=<n>` 링크가 전 카테고리 분량 들어 있어서, 아무 한 장을 받아 거기서 긁어낸다.
`BLACK LABEL AUTUMN EDITION` 처럼 **계절마다 통째로 갈리는 칸**이 있어서 상수로
적어두면 다음 시즌에 조용히 빈다.

2026-10-08 실측 13칸 중 상품 목록이 있는 건 9칸이다. 나머지 넷은 `productList.do`
가 아닌 다른 화면으로 떨어진다 — `BEVERAGES & ALCOHOL`·`SIDES & ADD ON MATES`·
`DESSERTS` 는 `productContents.do`(편집기로 올린 포스터 `.webp` 두 장뿐, 상품
데이터가 없다), `SIZZLING BONE-IN STEAK` 는 `productView.do`(단일 상품 상세)다.
**이 넷은 0건이 정상이라 칸마다 raise 하지 않고 합계로만 가드한다.**

`WINES` 는 아예 받지 않는다. 17건 전부 술이다(하우스 와인 Red/White, 울프 블라스
빌야라 쉬라즈 …). 요청 하나 아끼고 `base.is_alcohol` 에 기대지 않는다.

## 신제품 신호 — NEW 배지. **원시 110건 중 17건(15.5%) → fetch() 62건 중 12건**

```html
<span class="p-icon" …><img src="/asset/images/icon/icon_new.png" alt="NEW"/></span>
```

⚠️ `.p-icon` 이 **있다는 것만으로 세면 안 된다.** 설빙이 정확히 그 사고였다
(`span.flag` 안에 `icon_signature.png` 6 / `icon_new.png` 1). 여기도 같은 자리를
쓰는 배지가 여러 종일 수 있으므로 **파일명이 `icon_new` 인지 본다.**

2026-10-08 전수 — 분모가 '메뉴판 전체'인데 배지가 15.5% 에만 붙는다. 켜고 끄는
배지라는 뜻이다. **퀴즈노스(66건 전부 NEW)·얌샘김밥(BEST/HOT 을 존재만 세서 41건
전부)과 반대 경우고, 하이오커피처럼 '신메뉴 전용 탭'도 아니다.** 신제품 전용
목록이 아니라 일반 메뉴판에 선택적으로 붙은 배지다.

```
cate=24 LUNCH SET                      19건 NEW=5
cate=26 DELIVERY                       46건 NEW=3
cate=52 BLACK LABEL AUTUMN EDITION      1건 NEW=0
cate=54 APPETIZERS & SALADS             7건 NEW=1
cate=57 SPECIAL STEAKS & BACK RIBS      7건 NEW=2
cate=59 PASTA & RICE                    9건 NEW=3
cate=64 EASY PICK                       3건 NEW=3
cate=69 BLACK LABEL SIZZLING EDITION    1건 NEW=0
                                      110건 NEW=17 (15.5%)
```

⚠️ **위 110·17 은 칸을 돌며 센 원시 수치고, `fetch()` 가 돌려주는 건 62건/NEW 12건**이다.
같은 상품이 여러 칸에 중복으로 걸려 있어 `base.make_key` 로 접히기 때문이다(아래 참고).
비율을 재검증할 때 분모를 헷갈리지 마라 — **원시 17/110 = 15.5%, 산출 12/62 = 19.4%.**

배지가 없는 나머지는 `is_new=False` 로 내보낸다. 브랜드가 직접 켜고 끄는 배지라
'모름'이 아니라 '아니라고 확인된 것'이다.

## 날짜 — 이미지 경로의 업로드 일자. **`released_at` 이 아니다**

썸네일이 `/upload/product/20260901/20260901003719551073.png` 꼴이라 앞 8자리가
날짜다. 110건 전건에서 뽑힌다.

그런데 **일괄 재업로드 덩어리가 보인다** — `20250422` 28건, `20250616` 15건,
`20260308` 10건, `20240714` 9건, `20260901` 9건. 하루에 신제품 28종이 나온 게
아니라 사진을 한꺼번에 다시 올린 것이다. 파리바게뜨 312장과 같은 함정이라
**`uploaded_at` 에만 넣는다.** `rules.untrust_bulk_dates()` 가 `uploaded_at` 만
보기 때문에 여기 넣어야 가드가 걸린다. 브랜드가 "출시일"이라고 말한 값이 아니므로
`released_at` 은 끝까지 비운다.

날짜가 전건 안 뽑히면 업로드 경로 규칙이 바뀐 것이라 raise 한다. 날짜를 비운 채
`is_new=True` 를 올리면 60일 창을 통째로 건너뛴다.

## 나머지 필드

  .ko-name                    상품명
  .en-title                   영문명 (`SIZZLING CHEESE BOMB BOLOGNESE PASTA`)
  .info                       설명 한 줄
  onclick="fnPdtView('N', 10470)"  → pdtIdx. 상세 URL 을 여기서 만든다
                              (`fnPdtView` 본체는 외부 JS 라 페이지에 없다.
                               URL 꼴은 내비가 쓰는 productView.do 로 실측 확인)

`EASY PICK` 3건은 `듀얼 PICK (2인)`·`시그니처 PICK (3인)`·`테이스티 PICK (4인)`
으로 사실상 세트다. **여기서 거르지 않는다** — 세트 판정은 `collect.drop_sets()`
가 이름으로 한다. 어댑터마다 세트 기준을 달리 잡다가 신메뉴 세트가 잘린 전례가 있다.

등록 제안: 유형 `FRANCHISE`, 세부분류 `양식`.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "아웃백스테이크하우스"
SITE = "https://www.outback.co.kr"
MENU_IDX = 43
LIST = SITE + "/menu/productList.do?cateIdx={}&menuIdx=" + str(MENU_IDX)
VIEW = SITE + "/menu/productView.do?cateIdx={}&pdtIdx={}&menuIdx=" + str(MENU_IDX)
SEED_CATE = 26           # 내비를 긁어올 아무 한 장. DELIVERY 가 제일 크다
SEED = LIST.format(SEED_CATE)
DELAY = 1.5

# 술만 들어 있는 칸. 17건 전부 와인이라 요청 자체를 보내지 않는다.
SKIP_CATES = {38}

# 내비의 카테고리 링크. `/menu/main.do?menuIdx=43&cateIdx=24` 꼴이다.
_CATE = re.compile(r"/menu/main\.do\?menuIdx=\d+&cateIdx=(\d+)")
# 썸네일 경로의 업로드 일자. `/upload/product/20260901/…`
_UPLOADED = re.compile(r"/upload/product/(\d{4})(\d{2})(\d{2})/")
# `fnPdtView('N', 10470)` 의 상품 번호
_PDT = re.compile(r"fnPdtView\(\s*'[^']*'\s*,\s*(\d+)\s*\)")


def _text(node, sel: str) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _cates(html: str) -> list:
    """내비에서 cateIdx 를 순서대로 뽑는다. 중복은 턴다.

    ⚠️ **지금 보고 있는 칸은 내비에 번호가 없다.** 활성 항목만
    `<li class='actived'><a href="#">` 라서 정규식에 안 걸린다. 그래서
    SEED 의 cateIdx 를 손으로 넣어 준다 — 이걸 빠뜨려서 DELIVERY 46건이
    통째로 빠진 적이 있다(실행 결과 110 → 31건).
    """
    out = [SEED_CATE]
    for n in _CATE.findall(html):
        i = int(n)
        if i not in out and i not in SKIP_CATES:
            out.append(i)
    return out


def _is_new(cell) -> bool:
    """NEW 배지인가.

    `.p-icon` 이 있다는 것만으로는 안 된다 — 설빙이 `span.flag` 안에
    `icon_signature.png` 를 섞어 두고 있었고 존재만 세서 2013년 메뉴가
    신상이 됐다. 배지 **그림 파일명**을 본다.
    """
    for img in cell.css(".p-icon img"):
        # selectolax 는 값 없는 속성에 None 을 준다. 기본값이 안 먹는다.
        if "icon_new" in (img.attributes.get("src") or ""):
            return True
    return False


def _uploaded_at(src: str) -> str:
    m = _UPLOADED.search(src or "")
    return "-".join(m.groups()) if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = {}

    with base.client() as c:
        r = base.retry(lambda: c.get(SEED))
        r.raise_for_status()
        cates = _cates(r.text)
        if not cates:
            raise RuntimeError(
                f"{SEED}: 내비에서 cateIdx 를 하나도 못 찾았다 — "
                f"'/menu/main.do?menuIdx=..&cateIdx=..' 링크 꼴이 바뀌었는지 확인하라")

        for cate in cates:
            time.sleep(DELAY)
            url = LIST.format(cate)
            rr = base.retry(lambda url=url: c.get(url))
            rr.raise_for_status()

            # 칸마다 raise 하지 않는다. 포스터(productContents.do)·단일 상세
            # (productView.do)로 떨어지는 칸이 넷 있고 거기는 0건이 정상이다.
            doc = HTMLParser(rr.text)
            # 카테고리 이름은 빵부스러기 마지막 칸에서 받는다. 섹션 제목
            # (.menu-list-title)은 DELIVERY 한 장에만 9개가 있어서 셀과
            # 짝지으려면 문서 순서를 직접 걸어야 하는데, 그만한 값이 없다.
            crumbs = [" ".join(x.text().split()) for x in doc.css("ul.location li")]
            cate_name = crumbs[-1] if crumbs else ""

            for cell in doc.css(".menu-list-cell"):
                name = _text(cell, ".ko-name")
                if not name:
                    continue
                img = cell.css_first(".btn-menu-list-thumb img")
                src = (img.attributes.get("src") or "") if img else ""
                uploaded = _uploaded_at(src)
                is_new = _is_new(cell)

                pdt = _PDT.search(cell.html or "")
                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en=_text(cell, ".en-title"),
                    desc=_text(cell, ".info"),
                    image=SITE + src if src.startswith("/") else src,
                    category=cate_name,
                    # 사진 올린 날짜다. 20250422 에 28건이 몰린 일괄 재업로드가
                    # 섞여 있어 released_at 에 넣지 않는다 — 모듈 주석 참고.
                    uploaded_at=uploaded,
                    is_new=is_new,
                    url=VIEW.format(cate, pdt.group(1)) if pdt else "",
                )
                # ⚠️ 같은 상품이 여러 칸에 걸려 있고 **칸마다 배지가 다르다.**
                # 2026-10-08 실측: `트리플 갈릭 스트립` 은 LUNCH SET·SPECIAL
                # STEAKS 에서 NEW 인데 DELIVERY 에서는 아니고, `마라 투움바
                # 파스타` 는 PASTA & RICE 에서만 NEW 다. 먼저 본 것만 남기면
                # DELIVERY 를 먼저 도는 탓에 둘 다 신상에서 빠진다.
                # 한 칸이라도 NEW 라고 하면 그쪽으로 바꿔 단다.
                prev = seen.get(it.key)
                if prev is None:
                    seen[it.key] = it
                    items.append(it)
                elif is_new and not prev.is_new:
                    items[items.index(prev)] = it
                    seen[it.key] = it

    if not items:
        raise RuntimeError(
            f"{BRAND}: 상품 0건 — '.menu-list-cell / .ko-name' 셀렉터가 깨졌다 "
            f"(카테고리 {len(cates)}칸을 돌았다)")
    new_count = sum(1 for i in items if i.is_new)
    if not new_count:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 NEW 배지 0건 — 2026-10-08 실측은 "
            f"중복을 턴 뒤 12건이었다. '.p-icon img[src*=icon_new]' 가 "
            f"바뀌었는지 확인하라")
    dated = sum(1 for i in items if i.uploaded_at)
    if dated < len(items) * 0.9:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 날짜를 {dated}건밖에 못 읽었다 — "
            f"썸네일 경로 '/upload/product/YYYYMMDD/' 규칙이 바뀌었다. "
            f"날짜를 비우면 60일 창을 건너뛴다")
    return items
