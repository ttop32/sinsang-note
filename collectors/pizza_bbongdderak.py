"""뽕뜨락피자. 등록 담당자에게: **(FRANCHISE, "피자")**.

공정위 `피자` 가맹점 50개. 이름값에 비해 가맹점이 적지만 인지도가 있어서
미조사 88곳 중 먼저 열었다. 사이트는 그누보드5 고 메뉴가 **게시판 하나**
(`bo_table=11`, 갤러리 스킨 `menu_10`)에 통째로 들어 있다.

```
GET https://www.bbongdderak.com/bbs/board.php?bo_table=11&page=N
  page=1  60건 / page=2  8건 / page=3  0건   → 전체 68건 (2026-10-08 실측)
```

`http://www.bbongdderak.com` 으로 걸면 https 로 리다이렉트된다. 인증서는 멀쩡해서
`certs/` 에 더할 게 없다.

## 세부분류 — 떡볶이·파스타가 섞여 있지만 `피자` 다

`뽕떡`(뽕뜨락떡볶이) 15건과 파스타·튀김이 `사이드` 에 들어 있다. 브랜드 자체가
피자집이고 공정위 등록도 `피자` 라 세부분류는 `피자` 하나로 둔다. 상품 쪽
구분은 `category` 에 그대로 담는다.

## 배지 — `.gallery_icon p.new` **3/68 (4.4%)**. `p.best` 를 같이 세면 안 된다

2026-10-08 전수 68건을 세었다:

```
배지 없음        50건 (73.5%)
p.best  BEST    15건 (22.1%)   ← 🔴 추천 표시다. 신제품이 아니다
p.new   NEW      3건 ( 4.4%)   ← ✅ 이것만 is_new
```

**① 종류 전수.** 위 셋이 전부다 — 카드 68장의 `.gallery_icon p` 를 하나도 빼지 않고
셌고 `hot`·`recommend`·`시그니처` 류는 raw 검색 **0회**다. 둘이 **같은
`div.gallery_icon` 안에 `p` 로 나란히** 들어 있어서 `.gallery_icon p` 로 세면
**18건(26%)** 이 된다. 얌샘김밥 `prBadge` 에 BEST/HOT/COOL 이 섞여 있던 것과
같은 자리다. **클래스가 `new` 인 것만 본다.**

BEST 15건은 모모스테키·쓰리고·베이컨포테이토·스파이시쉬림프처럼 **10년 가까이 파는
간판**이다. 이걸 신상으로 올렸으면 메뉴판 4분의 1이 신제품이 됐다.

**② 주석·숨김이 아니다.** 피자마루는 `<span class="new">` 가 카드 81장 **전부**에
있었는데 100% HTML 주석 안이라 실제로는 0/81 이었다. raw HTML 에서 직접 셌다:

```
class="new"     주석 안 0회 / 전체  3회      ← 주석에 숨은 게 없다
class="best"    주석 안 0회 / 전체 15회
gallery_icon    주석 안 0회 / 전체 74회  (= 상품 68 + CSS 규칙 3줄 × 2페이지)
```

CSS 도 확인했다. 숨기는 규칙이 없다:

```
.gallery_icon        {position:absolute; left:0px; bottom:0px; z-index:0; width:100%;}
.gallery_icon p.new  {height:25px; background:#ff1f33; color:#fff; ... font-weight:700;}
```

**③ 배지 3건의 이름을 눈으로 읽었다.** `프리미엄웨스틴피자`·`트러플머쉬룸피자`·
`빠삭후라이드`. 클래식 기본 메뉴(`페페로니`·`불고기`·`슈프림콤비`·`콰트로`·`멜팅치즈`)
는 **하나도 안 붙어 있다.** 다만 셋 중 하나가 묵었다 — 바로 아래 ⚠️ 를 보라.

안 붙은 50건은 `False` 가 아니라 **`None`** 이다. 운영자가 손으로 켜는 표시라
'안 켰다'가 '신제품이 아니다'를 뜻하지 않는다(피자스쿨과 같은 선).

## 🔴 날짜가 **없다**. 그래서 배지만으로 간다

목록에도 상세에도 등록일이 없다. 그누보드 `wr_datetime` 을 스킨이 아예 안 찍고,
`rss.php?bo_table=11` 은 **파라미터를 무시하고 이벤트 게시판(31번)을 돌려준다**
(`<title>뽕뜨락피자 > 진행중인이벤트</title>`). `bbs/rss.php` 는
`RSS 보기가 금지되어 있습니다` 40바이트다.

`released_at`·`uploaded_at` 을 둘 다 비우고 `is_new` 만 준다. `rules.is_fresh`
가 이 경우 `first_seen` + `STALE` 로 수명을 끊어 준다(설빙·빽다방과 같은 경로).

⚠️ **NEW 3건 중 1건은 묵었다.** 상세 본문의 에디터 이미지 경로로 확인했다
(2026-10-08 실측):

```
wr_id=151 프리미엄웨스틴피자  /data/editor/2610/  …_1790817944_… → 2026-10-01  ✅ 일주일 전
wr_id=150 트러플머쉬룸피자    /data/editor/2610/                 → 2026-10-01  ✅
wr_id=136 빠삭후라이드        /data/editor/2104/                 → 2021-04     🔴 4년 반 묵음
```

설빙 `인절미설빙` 과 같은 '내려놓는 걸 잊은 배지'다. **그래도 이 날짜를
`released_at` 에 넣지 않는다** — 함정 7(피자마루에서 2020-08-21 등록 피자 3종의
파일명이 2025-03-17 이었다). 사진만 갈아도 올라가는 값이라 신호가 아니다.
여기선 '배지가 믿을 만한가' 를 **사람이 판단하는 근거로만** 썼고 코드는 안 읽는다.
빠삭후라이드는 합류 첫 `STALE` 일 동안 한 번 올라왔다가 내려간다.

## 분류 — `sca` 5칸. 합이 정확히 전체와 같다

```
클래식 17 · 사이드 24 · 뽕떡 15 · 더하기 6 · 러블리 6   = 68  ✅ 전체와 일치
```

분류 없는 상품이 하나도 없다. 그래서 **전체 목록을 기준으로 삼고** `sca` 는
분류를 붙이는 용도로만 돌린다. 둘이 어긋나면(분류가 늘거나 상품이 분류에서
빠지면) 가드가 잡는다. `sca` 값은 페이지에서 찾는다 — 박아두면 조용히 어긋난다.
⚠️ 같은 nav 에 이벤트 게시판의 `진행중`·`종료` 도 `sca=` 로 걸려 있는데
`bo_table=11` 에선 0건이라 자연히 지나간다.

## 나머지

  - 이미지는 목록이 `thumb-…_263x195.jpg` 를 준다. `thumb-` 와 `_263x195` 를
    떼면 원본이 나온다 — 표본 10건을 직접 받아 **10/10 image 200** 을 확인했다.
    못 떼면 썸네일을 그대로 쓴다(빈손으로 두지 않는다).
  - 설명은 `.gallery_text` 에 있고 끝이 `…` 로 잘려 있다. 그대로 넣는다.
    **전건은 아니다 — 2026-10-08 실측 44/68(65%)만 차고 나머지는 빈 값**
    (콜라·피클·소스처럼 설명이 없는 것들). 그래서 desc 바닥 가드는 안 둔다.
  - `뽕피 Set 1~3`·`뽕치 Set 1~2`·`뽕파 Set 1~2` 는 세트지만 본품 이름이
    따로 없어서 `rules.drop_sets()` 가 남긴다. 세트 자체가 상품인 쪽이라
    맞는 동작이고, 어차피 배지가 없어 화면엔 안 오른다.
  - 상품명 68건을 전부 눈으로 읽었다. 주류·비식품은 없다(콜라·사이다·
    피클·소스까지 전부 먹는 것이다).
"""
import re
import time
import urllib.parse

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "뽕뜨락피자"
ROOT = "https://www.bbongdderak.com"
BOARD = ROOT + "/bbs/board.php"
BO_TABLE = "11"          # 메뉴 게시판
DELAY = 1.5
MAX_PAGES = 6            # 폭주 방지. 2026-10-08 실측은 2페이지다.

MIN_ITEMS = 50           # 2026-10-08 실측 68건
# 🔴 이 값은 복붙하면 안 된다. 다른 어댑터는 1/3 인데 여기는 **0.15** 다 —
#    이 브랜드만 같은 자리에 경쟁 배지(`p.best` 15건)가 있어서다.
#    `NEW_SEL` 이 `.gallery_icon p` 로 넓어지면 18/68 = **26.5%** 가 되는데
#    1/3(33.3%)이면 그게 **그냥 통과한다** — 가드가 자기가 막겠다고 적은 사고를
#    못 잡는 셈이다. 실측 4.4% 와 사고 26.5% 사이에 선을 긋는다.
#    0.15 → 10건까지 통과(배지를 몇 개 더 켜도 안 터짐), 11건부터 터진다.
BADGE_MAX_RATIO = 0.15   # 2026-10-08 실측 3/68 = 4.4% (BEST 혼입 시 26.5%)
CAT_MIN_RATIO = 0.9      # 실측은 68/68 = 100%

# 🔴 'p.new' 만 신제품이다. 같은 .gallery_icon 안의 'p.best' 15건은 추천 표시다.
NEW_SEL = ".gallery_icon p.new"
_THUMB = re.compile(r"/thumb-")
_SIZED = re.compile(r"_\d+x\d+(\.\w+)$")


def _cards(html: str) -> list:
    return HTMLParser(html).css("ul.board_gallery > li")


def _wr_id(li) -> str:
    a = li.css_first(".gallery_subject a")
    m = re.search(r"wr_id=(\d+)", a.attributes.get("href") or "") if a is not None else None
    return m.group(1) if m else ""


def _pages(c, params: dict) -> list:
    """게시판을 끝까지. 빈 페이지가 나오면 멈춘다."""
    out, page = [], 1
    while page <= MAX_PAGES:
        r = base.retry(lambda: c.get(BOARD, params=dict(params, page=page)))
        r.raise_for_status()
        lis = _cards(r.text)
        if not lis:
            break
        out += lis
        page += 1
        time.sleep(DELAY)
    return out


def _scas(c) -> list:
    """분류 값을 페이지에서 찾는다. 박아두면 사이트가 분류를 바꿀 때 어긋난다."""
    r = base.retry(lambda: c.get(BOARD, params={"bo_table": BO_TABLE}))
    r.raise_for_status()
    out = []
    for a in HTMLParser(r.text).css("a[href*='sca=']"):
        m = re.search(r"sca=([^&\"']+)", a.attributes.get("href") or "")
        if m:
            v = urllib.parse.unquote(m.group(1))
            if v and v not in out:
                out.append(v)
    return out


def _image(li) -> str:
    """원본 주소. 못 만들면 썸네일 그대로 — 빈손으로 두지 않는다."""
    img = li.css_first("img.image")
    src = (img.attributes.get("src") or "") if img is not None else ""
    if not src or "/thumb-" not in src:
        return src
    return _SIZED.sub(r"\1", _THUMB.sub("/", src))


def fetch() -> list[Item]:
    with base.client() as c:
        # 전체 목록이 기준이다. 분류별 합이 여기 못 미치면 가드가 잡는다.
        cards = _pages(c, {"bo_table": BO_TABLE})
        cat_of: dict[str, str] = {}
        for sca in _scas(c):
            time.sleep(DELAY)
            for li in _pages(c, {"bo_table": BO_TABLE, "sca": sca}):
                wid = _wr_id(li)
                if wid:
                    cat_of.setdefault(wid, sca)

    items: list[Item] = []
    seen: set[str] = set()
    badged = 0
    for li in cards:
        sub = li.css_first(".gallery_subject a")
        name = " ".join(sub.text().split()) if sub is not None else ""
        if not name:
            continue
        wid = _wr_id(li)
        desc = li.css_first(".gallery_text")
        # 🔴 'p.new' 만. '.gallery_icon p' 로 세면 BEST 15건이 딸려 온다.
        is_new = li.css_first(NEW_SEL) is not None
        badged += is_new
        it = Item(
            brand=BRAND,
            name=name,
            desc=" ".join(desc.text().split()) if desc is not None else "",
            image=_image(li),
            category=cat_of.get(wid, ""),
            # 날짜가 사이트 어디에도 없다. 에디터 이미지 파일명의 유닉스 시각은
            # 사진만 갈아도 올라가서 안 쓴다(함정 7, 피자마루 선례).
            is_new=True if is_new else None,
            url=f"{BOARD}?bo_table={BO_TABLE}&wr_id={wid}" if wid else BOARD,
        )
        if it.key not in seen:
            seen.add(it.key)
            items.append(it)

    if len(items) < MIN_ITEMS:
        raise RuntimeError(
            f"{BRAND}: 상품 {len(items)}건 — 2026-10-08 실측은 68건이었다. "
            "'ul.board_gallery > li' 가 바뀌었거나 페이지를 덜 돌았다")

    if not any(i.image for i in items):
        raise RuntimeError(f"{BRAND}: 이미지가 0건 — 'img.image' 가 바뀌었다")

    # 🔴 이 어댑터의 핵심 가드. 'p.new' 가 'p' 로 넓어지거나 스킨이 배지를
    #    무조건 찍게 바뀌면 간판 메뉴 68건이 통째로 신상이 된다.
    #    2026-10-08 실측 3/68 = 4.4% (BEST 를 같이 세면 18/68 = 26%).
    if badged > len(items) * BADGE_MAX_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {badged}건에 NEW 가 붙었다 "
            f"(기대 {BADGE_MAX_RATIO:.0%} 이하, 2026-10-08 실측 3/68=4.4%). "
            "'p.best' 15건까지 같이 세고 있는지 보라 — 그러면 18/68=26.5% 가 된다")
    if badged == 0:
        raise RuntimeError(
            f"{BRAND}: NEW 배지가 0건이다 — 2026-10-08 실측은 3건이었다. "
            f"'{NEW_SEL}' 가 바뀌었다면 날짜가 없는 브랜드라 신제품을 영영 못 집는다")

    # 분류는 68/68 이 채워지는 게 정상이다. 분류 페이지가 비면 category 가
    # 조용히 빈 채로 나가므로 바닥을 둔다.
    tagged = sum(1 for i in items if i.category)
    if tagged < len(items) * CAT_MIN_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 분류를 {tagged}건밖에 못 붙였다 "
            f"(2026-10-08 실측 68/68). 'sca' 목록이나 분류 이름이 바뀌었다")
    return items
