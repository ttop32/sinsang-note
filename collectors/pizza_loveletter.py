"""피자와 치킨의 러브레터. 등록 담당자에게: **(FRANCHISE, "피자")**.

(주)디에스푸드가 2004년부터 하는 피자+치킨 세트 브랜드. 공정위 `피자` 가맹점 44개.
사이트는 손으로 짠 PHP 고 메뉴가 `kind` 3칸에 나뉘어 있다.

```
GET http://loveletterds.com/menu/2200_menu.php?kind=N     ← 본문. 한 쪽에 최대 15건
GET http://loveletterds.com/menu/menu_list.php?kind=N&page=P  ← 16번째부터 붙이는 ajax
```

⚠️ **https 가 없다.** `https://loveletterds.com` 은 붙지 않는다. http 로 간다.
⚠️ 도메인이 `loveletter.co.kr` 류가 아니라 **`loveletterds.com`**(디에스푸드)이다.

## 🔴 ajax 엔드포인트만 긁으면 조용히 모자란다 — 여기서 걸릴 뻔했다

처음에 `menu_list.php?kind=1&page=0` 만 받고 **6건**으로 셌다. 그런데 본문 페이지의
`var p_total` 은 **14** 다. `page=0` 은 15건짜리 쪽수 계산에서 엉뚱한 조각을 주고
`page=1` 부터는 빈 응답이다:

```
menu_list.php?kind=1&page=0  →  6건   ← 이것만 보면 6건이 '전부' 로 보인다
menu_list.php?kind=1&page=1  →  0건
2200_menu.php?kind=1         → 14건   ← 진짜 전부. p_total=14 와 일치
```

**본문 페이지를 기준으로 삼고, `p_total` 이 본문 건수보다 많을 때만 ajax 로
뒷장을 붙인다.** 실측(2026-10-08) `kind=3` 이 `p_total=19` 인데 본문에 15건이라
`page=1` 로 4건을 더 받는다. 200 이 왔다고 다 받은 게 아니다(함정 9).

세 칸 합 **41건**. 칸 이름은 페이지에서 찾는다 — 박아두면 조용히 어긋난다.

```
kind=1 피자          14건
kind=2 치킨           8건
kind=3 세트&사이드     19건
```

## 배지 — `span.new` **5/41 (12.2%)** (2026-10-08 전수 실측. 조각 합친 뒤 4/40)

```
no=120  치즈인 순살치킨 (4조각)   NEW
no=119  치즈인 순살치킨 (10조각)  NEW
no=117  양념치킨 피자            NEW
no=116  감튀마운틴피자           NEW
no=112  요거트 치즐러 치킨        NEW
나머지 36건 배지 없음
```

**① 종류 전수.** 카드 41장의 `span[class]` 를 전부 세었더니 `('new eng','NEW')` 5건과
'없음' 36건, **두 가지뿐**이다. `class="best`·`class="hot` 은 raw 검색 **0회**다.
뽕뜨락은 같은 자리에 BEST 15건이, 얌샘김밥은 BEST/HOT/COOL 이 섞여 있었다 — 여긴 아니다.

**② 주석·숨김이 아니다.** 피자마루는 `<span class="new">` 가 카드 81장 **전부**에
있었는데 100% HTML 주석 안이라 실제로는 0/81 이었다. raw 에서 직접 셌다:

```
class="new eng"   주석 안 0회 / 전체 8회      ← 주석에 숨은 게 없다
display:none      5회, 전부 배지와 무관한 자리(모달 껍데기·네비)
```

**③ 🔴 raw 8회 중 3회는 상품이 아니다 — 숨은 더미다.**

```
<div class="thumbs" style="background-image:url(../images/dummy/menu1.png)">
  <dl class="info"><dt><span class="name">하와이안베이컨치즈볼 피자</span>
                   <span class="new eng">NEW</span></dt>
```

`#viwmenu` 모달의 빈 껍데기에 **`하와이안베이컨치즈볼 피자` 라는 가짜 상품**이
`images/dummy/menu1.png` 와 함께 박혀 있고 `kind` 3칸에 한 번씩 나온다(3 = 8 − 5).
`span.new` 만 보고 긁으면 **있지도 않은 상품이 매일 신상으로 올라간다.** 막는 건 두 겹인데
**일차 방어선은 이름 셀렉터 `h4.name` 이다** — 더미의 이름은 `span.name` 이라 이름이
안 뽑히고 그대로 버려진다. 이차가 `funView(kind,no)` 를 단 `li` 만 고르는 카드 필터다.
(검수에서 확인: `funView` 필터만 떼면 더미는 여전히 `h4.name` 에서 걸러진다. 둘이
**동시에** 무너져야 샌다.) 그래서 `_DUMMY` 가드는 마지막 그물이지 일차가 아니다.

**④ 배지 5건의 이름을 눈으로 읽었다.** 전부 최근 것이고 기본 메뉴가 하나도 없다.
2021년부터 있는 `후라이드치킨`·`양념치킨`·`치즈(多)피자`·`페퍼로니폭탄피자`·
`슈퍼슈프림피자` 는 **전부 배지가 없다.** 마왕족발처럼 수년째 켜둔 배지가 아니다.
⚠️ 2021년 `양념치킨`(배지 없음)과 2026년 `양념치킨 피자`(배지 있음)는 이름이 달라
`make_key` 에서 안 겹친다 — 겹쳤으면 옛 치킨이 신상이 됐다(피자마루 사고 자리).

배지 5건은 상품 id `no` 가 큰 쪽에 몰려 있다(120·119·117·116·112 / 최댓값 120).
안 붙은 36건은 `False` 가 아니라 **`None`** 이다(피자스쿨·뽕뜨락과 같은 선).

## 🔴 `(N조각)` 은 크기 변형이다 — 여기서 합친다

`치즈인 순살치킨 (10조각)`(치킨 칸, no=119)과 `(4조각)`(세트&사이드 칸, no=120)이
**둘 다 NEW 를 달고 따로 올라온다.** 같은 치킨이 화면에 두 장 뜬다.

`rules.merge_variants` 가 이걸 못 턴다. 2026-10-08 실측:

```
rules.base_name("하와이안베이컨치즈버거 세트") → '하와이안베이컨치즈버거'   ← 세트는 턴다
rules.base_name("치즈인 순살치킨 (10조각)")   → '치즈인 순살치킨 (10조각)'  ← 조각은 못 턴다
```

`rules._SIZE_TAIL` 은 `S|M|L|라지|미디엄|스몰|대|중|소` 만, `base.make_key` 의
`_SIZE` 는 `ml|L|g|kg|인분|개입|P|입` 만 안다. **양쪽 다 '조각' 이 없다.**
`조각` 은 `인분`·`개입` 과 같은 크기 표기지 다른 상품이 아니다(피자마루에서
8인치 1인피자 5건을 '크기 변형이지 신제품이 아니다'로 걷어낸 선례와 같은 자리).

🔴 **`collectors/base.py` 의 `_SIZE` 는 건드리지 않았다.** 전 어댑터에 영향이
가는 공용 규칙이고 내 구간이 아니다. 이 파일 안에서만 `_merge_pieces()` 로 묶는다.
**41건 → 40건, NEW 5 → 4.** `base._SIZE` 에 `조각` 이 없다는 사실 자체는
`notes/CANDIDATES-PIZZA3-FASTFOOD2.md` 에 '다음 사람이 볼 것' 으로 적어 뒀다
(모스버거에도 `모스너겟(5조각)`·`(10조각)` 쌍이 있는데 거긴 배지가 없어 안 뜬다).

대표는 **브랜드 나열 순에서 먼저 나온 쪽**이다(= `치킨` 칸의 10조각). 날짜는
**이른 쪽**을 남기고(피자마루 사고), 배지는 변형 중 하나라도 붙어 있으면 살린다.

## 🔴 날짜가 **없다**

목록에도 `menu_view.php` 상세에도 등록일이 없다. `released_at`·`uploaded_at` 을
비우고 `is_new` 만 준다 — `rules.is_fresh` 가 `first_seen` + `STALE` 로 수명을
끊는다(설빙·빽다방 경로).

⚠️ **공지 게시판은 못 쓴다.** `/community/3301_notice_list.php` 에 `[신메뉴 출시]`
글이 timestamp 까지 달려 10건 있는데 **2024-11-15 에서 멈췄다.** 지금 NEW 가 붙은
5건은 거기 하나도 없다. 날짜를 가져다 붙일 데가 없다는 뜻이다(모스버거는 같은
모양의 게시판이 살아 있어서 쓸 수 있었다 — 여긴 아니다).

⚠️ **이미지 파일명을 날짜로 쓰지 않는다.** 경로가 `260916_040200_master_….png`
꼴이라 `YYMMDD_HHMMSS` 가 그대로 박혀 있고, NEW 5건이 260916·260916·260916·
260430·251210 으로 꽤 그럴듯하다. 그래도 **안 쓴다** — 함정 7(피자마루에서
2020-08-21 등록 상품의 파일명이 2025-03-17 이었다). 사진만 갈아도 올라간다.
여기서도 `버팔로윙`·`버팔로봉`(260430)이 NEW 없이 같은 날짜를 달고 있어서
파일명이 '출시'가 아니라 '업로드'라는 게 드러난다.

## 나머지

  - 이미지는 목록이 `background-image:url(../../upload/menu/…)` 로 준다.
    `../` 를 털고 루트에 붙이면 `http://loveletterds.com/upload/menu/…` 이고
    직접 받아 **image/png 200** 을 확인했다.
    ⚠️ **등록 담당자에게: 이 브랜드는 이미지가 http 전용이다.** `base.derive()` 가
    http 주소를 `image` 에서 `image_src` 로 옮기므로 `to_dict()` 뒤 `image` 는
    **40/40 빈 문자열**이 된다. `rules.mirror_images` 가 돌아야 카드에 사진이 뜬다
    (`rules.py` 가 열거한 에그드랍·퀴즈노스·쉐이크쉑·스쿨푸드와 같은 칸이다).
    어댑터의 이미지 가드는 derive 전 값을 보므로 정상 통과한다.
  - 설명은 `menu_view.php?kind=&no=` 상세에만 있다. 41번을 더 받아야 해서
    넣지 않았다(가맹점 44개짜리 브랜드다). 이름·이미지·분류·배지로 충분하다.
  - `…세트` 10건은 그대로 내보낸다. 본품이 있는 것은 `rules.drop_sets()` 가 턴다.
  - 상품명 41건(합병 후 40건)을 전부 눈으로 읽었다. 주류·비식품은 없다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "피자와치킨의러브레터"
ROOT = "http://loveletterds.com"          # ⚠️ https 없음
MAIN = ROOT + "/menu/2200_menu.php"
AJAX = ROOT + "/menu/menu_list.php"
DELAY = 1.5
MAX_PAGES = 5            # 폭주 방지. 2026-10-08 실측은 칸당 ajax 1쪽 이하다.

MIN_ITEMS = 31           # 2026-10-08 실측 40건(조각 변형 합친 뒤)
BADGE_MAX_RATIO = 1 / 3  # 2026-10-08 실측 4/40 = 10.0%

# 🔴 '(N조각)' 은 크기 변형이지 다른 상품이 아니다. `rules.merge_variants` 가
#    이걸 못 턴다 — `rules._SIZE_TAIL` 은 S/M/L·대중소만, `base.make_key` 의
#    `_SIZE` 는 ml·g·인분·개입·P·입만 안다. **'조각' 이 양쪽 목록에 다 없다.**
#    그래서 `치즈인 순살치킨 (10조각)`(치킨 칸)과 `(4조각)`(세트&사이드 칸)이
#    **둘 다 NEW 를 달고 따로 올라간다** — 화면에 같은 치킨이 두 장 뜬다.
#    버거킹 12그룹 36건을 `merge_variants` 가 묶는 것과 같은 자리라 여기서 묶는다.
#    ⚠️ `collectors/base.py` 의 `_SIZE` 는 **건드리지 않는다** — 전 어댑터에
#       영향이 가는 공용 규칙이고 내 구간이 아니다. 이 파일 안에서만 처리한다.
_PIECES = re.compile(r"\s*\(\s*\d+\s*조각\s*\)\s*$")

# 배지 셀렉터. 뽕뜨락·만월경과 같이 상수로 올려 두고 에러 메시지도 이걸 찍는다.
NEW_SEL = "span.new"
MERGE_MAX_RATIO = 0.15   # 2026-10-08 실측 1/41 = 2.4%. 과합병 방지 바닥

_VIEW = re.compile(r"funView\((\d+),\s*(\d+)\)")
# 🔴 모달 껍데기에 박힌 가짜 상품('하와이안베이컨치즈볼 피자')이 쓰는 이미지.
#    그게 목록으로 새면 없는 상품이 매일 신상으로 올라간다(docstring ③).
_DUMMY = re.compile(r"/images/dummy/")
_TOTAL = re.compile(r"p_total\s*=\s*(\d+)")
_BG = re.compile(r"url\(\s*['\"]?(.*?)['\"]?\s*\)")
_UP = re.compile(r"^(?:\.\./)+")


def _products(html: str) -> list:
    """(상품명, li) 목록. **이름이 실제로 뽑힌 것만** 센다.

    `p_total` 과 대조하는 기준이라 '카드처럼 생긴 노드' 가 아니라 '상품' 이어야
    한다(docstring 참고). 더미 모달은 이름이 `span.name` 이라 여기서도 안 걸린다
    — `h4.name` 이 사실상 일차 방어선이고, `funView` 필터가 이차다.
    """
    out = []
    for li in _cards(html):
        nm = li.css_first("h4.name")
        name = " ".join(nm.text().split()) if nm is not None else ""
        if name:
            out.append((name, li))
    return out


def _merge_pieces(items: list) -> list:
    """`(N조각)` 크기 변형을 한 건으로. 대표는 **브랜드가 먼저 내놓은 쪽**.

    `rules.merge_variants` 는 '대표는 이름이 가장 짧은 것' 인데, 그 규칙은
    `X` 와 `X 세트` 중 본품을 고르려고 있는 것이다. 여기선 둘 다 본품이라
    (`4조각`·`10조각`) 글자 수로 고르면 엉뚱해진다 — 짧은 `(4조각)` 이 이기면
    치킨이 `세트&사이드` 칸 상품으로 올라간다. 그래서 **`kind` 순서(브랜드가
    1 피자 → 2 치킨 → 3 세트&사이드 로 늘어놓은 순)에서 먼저 나온 쪽**을 대표로
    둔다. 치킨은 `치킨` 칸 것이 남는다.

    ⚠️ 날짜는 **가장 이른 것**을 남긴다. 늦은 쪽을 쓰면 옛 제품이 새 신상이
       된다(피자마루 `치즈 폭탄 피자` 가 2020년 메뉴인데 2025년 신상이 된 사고).
       지금 이 브랜드는 날짜가 전건 비어 있지만, 날짜가 생겨도 안 깨지게 둔다.
    ⚠️ 배지는 변형 중 **하나라도 붙어 있으면** 살린다. 4조각에만 NEW 가 붙고
       10조각엔 안 붙는 식으로 갈리면 안 되고, 어차피 같은 상품이다.
    """
    rep: dict = {}
    order: list = []
    for it in items:
        key = (_PIECES.sub("", it.name).strip() or it.name)
        if key not in rep:
            rep[key] = it
            order.append(key)
            continue
        # 대표는 먼저 본 것(= 브랜드 나열 순). 날짜는 이른 쪽, 배지는 붙은 쪽.
        cur = rep[key]
        dates = [d for d in (cur.released_at, it.released_at) if d]
        cur.released_at = min(dates) if dates else ""
        cur.is_new = True if (cur.is_new or it.is_new) else None
    return [rep[k] for k in order]


def _kinds(c) -> list:
    """(kind, 칸 이름). 페이지에서 찾는다 — 박아두면 칸이 바뀔 때 어긋난다."""
    r = base.retry(lambda: c.get(MAIN, params={"kind": 1}))
    r.raise_for_status()
    out = []
    for a in HTMLParser(r.text).css("a[href*='kind=']"):
        h = a.attributes.get("href") or ""
        if "&no=" in h:                   # 상품 바로가기. 칸 nav 가 아니다
            continue
        m = re.search(r"kind=(\d+)", h)
        name = " ".join(a.text().split())
        if m and name and m.group(1) not in [k for k, _ in out]:
            out.append((m.group(1), name))
    return out


def _cards(html: str) -> list:
    """funView(kind,no) 를 단 li 만. 네비·푸터의 li 는 걸리지 않는다."""
    return [li for li in HTMLParser(html).css("li")
            if li.css_first("a[onclick*='funView']") is not None]


def _image(li) -> str:
    th = li.css_first(".thumbs")
    m = _BG.search((th.attributes.get("style") or "")) if th is not None else None
    if not m or not m.group(1):
        return ""
    # '../../upload/menu/x.png' → 'http://loveletterds.com/upload/menu/x.png'
    return ROOT + "/" + _UP.sub("", m.group(1).strip())


def fetch() -> list[Item]:
    items: list[Item] = []
    seen: set[str] = set()
    badged = 0

    with base.client() as c:
        kinds = _kinds(c)
        if not kinds:
            raise RuntimeError(
                f"{BRAND}: 메뉴 칸(kind)을 하나도 못 읽었다 — 'a[href*=kind=]' 가 바뀌었다")
        for kind, cat in kinds:
            time.sleep(DELAY)
            r = base.retry(lambda: c.get(MAIN, params={"kind": kind}))
            r.raise_for_status()
            m = _TOTAL.search(r.text)
            if not m:
                raise RuntimeError(
                    f"{BRAND}: kind={kind}({cat}) 에서 p_total 을 못 찾았다. "
                    "이 값이 없으면 몇 건을 덜 받았는지 알 수 없다")
            want = int(m.group(1))
            # 🔴 `p_total` 과 맞춰야 하는 건 **이름까지 뽑힌 상품 수**다.
            #    카드 노드 수로 재면 안 된다 — 카드 고르기가 느슨해져 네비·푸터
            #    `li` 까지 세면(kind=3 본문의 날 li 는 50개다) `50 >= 19` 가 되어
            #    **ajax 뒷장을 아예 안 받고** 상품 4건이 말없이 사라진다.
            #    `MIN_ITEMS` 바닥에도 안 걸린다. 그래서 파싱 결과로 센다.
            parsed = _products(r.text)
            page = 1
            while len(parsed) < want and page <= MAX_PAGES:
                time.sleep(DELAY)
                rr = base.retry(lambda: c.get(AJAX, params={"kind": kind, "page": page}))
                rr.raise_for_status()
                more = _products(rr.text)
                if not more:
                    break
                parsed += more
                page += 1
            if len(parsed) < want:
                raise RuntimeError(
                    f"{BRAND}: kind={kind}({cat}) 가 p_total={want} 인데 이름이 "
                    f"뽑힌 상품은 {len(parsed)}건뿐이다. ajax 쪽수 규칙이나 "
                    "'h4.name' 이 바뀌었다 — 모자란 채로 내보내면 급감 가드에도 안 걸린다")

            for name, li in parsed:
                a = li.css_first("a[onclick*='funView']")
                mv = _VIEW.search(a.attributes.get("onclick") or "") if a is not None else None
                is_new = li.css_first(NEW_SEL) is not None
                badged += is_new
                no = mv.group(2) if mv else ""
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=_image(li),
                    category=cat,
                    # 사이트 어디에도 날짜가 없다. 이미지 파일명의 YYMMDD 는
                    # 업로드일이라 안 쓴다(함정 7, docstring 참고).
                    is_new=True if is_new else None,
                    url=f"{MAIN}?kind={kind}&no={no}" if no else f"{MAIN}?kind={kind}",
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

    raw_n = len(items)
    items = _merge_pieces(items)
    # 🔸 배지 수를 **합병 뒤 기준으로 다시 센다.** 합병 전 5건을 합병 후 40건과
    #    비교하면 분자·분모가 다른 단계라 메시지 숫자가 한 칸 어긋난다.
    badged = sum(1 for i in items if i.is_new)

    if len(items) < MIN_ITEMS:
        raise RuntimeError(
            f"{BRAND}: 상품 {len(items)}건 — 2026-10-08 실측은 40건이었다 "
            f"(칸별 14/8/19 = 41건에서 조각 변형 1건 합침). "
            f"본 칸: {[c for _, c in kinds]}")

    # 조각 정규식이 너무 넓어지면 서로 다른 상품이 한 장으로 뭉친다.
    if raw_n - len(items) > raw_n * MERGE_MAX_RATIO:
        raise RuntimeError(
            f"{BRAND}: 조각 변형을 합치면서 {raw_n}건이 {len(items)}건이 됐다 "
            f"(기대 {MERGE_MAX_RATIO:.0%} 이하, 2026-10-08 실측 1/41=2.4%). "
            "_PIECES 가 너무 넓어져 다른 상품까지 묶고 있는지 보라")

    if not any(i.image for i in items):
        raise RuntimeError(f"{BRAND}: 이미지가 0건 — '.thumbs' 의 background-image 가 바뀌었다")

    # 🔴 모달 껍데기의 가짜 상품이 목록에 샜는지. 지금은 `funView` 를 단 li 만
    #    세서 안 걸리지만, 카드 선택이 느슨해지면 '하와이안베이컨치즈볼 피자'
    #    (있지도 않은 상품)가 NEW 를 달고 매일 올라간다(docstring ③).
    fake = [i.name for i in items if _DUMMY.search(i.image)]
    if fake:
        raise RuntimeError(
            f"{BRAND}: 모달 껍데기의 더미 상품이 목록에 섞였다 {fake} — "
            "카드 선택이 'funView 를 단 li' 보다 느슨해졌다. 실제로 파는 상품이 아니다")

    # 🔴 날짜가 없는 브랜드라 배지가 유일한 근거다. 양쪽을 다 막는다.
    if badged > len(items) * BADGE_MAX_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {badged}건에 NEW 가 붙었다 "
            f"(기대 {BADGE_MAX_RATIO:.0%} 이하, 2026-10-08 실측 "
            f"4/40=10.0% — 합병 전 5/41=12.2%). "
            "템플릿이 배지를 무조건 찍게 바뀌었는지 보라")
    if badged == 0:
        raise RuntimeError(
            f"{BRAND}: NEW 배지가 0건이다 — 2026-10-08 실측은 4건이었다"
            f"(합병 전 5건). '{NEW_SEL}' 가 바뀌었다면 날짜가 없어 "
            "신제품을 영영 못 집는다")
    return items
