"""모스버거. 등록 담당자에게: **(FRANCHISE, "햄버거")**.

일본 모스버거와 미디어윌의 합작 (주)모스버거코리아다. 공정위 `패스트푸드` 가맹점
7개로 작지만 인지도가 높아서 먼저 열었다.

⚠️ **도메인이 `mosburger.co.kr` 이 아니다.** 공식은 `http://www.moskorea.kr` 다
(프차몰 정보공개서·푸터 사업자등록번호 220-88-26499 로 확인). https 는 열려 있지
않아 http 로 간다.

사이트는 `superboard` 라는 국산 CMS 고, 메뉴도 게시판 스킨(`skin/product/basic`)이다.

## 🔴 `신메뉴` 탭(`ca_id=01`)은 포스터 1장이다 — 긁을 게 없다

```
GET /menu/list?ca_id=01   16,265B   ul.listType1 0건   prdtTotalCount='0'
  → 본문이 <img src="/superboard/data/editor/2608/2026081721...">  포스터 한 장
```
`ca_id=05`(모스의 아침)도 0건이다. 돈까스클럽·101번지남산과 같은 칸이라
**'신메뉴 탭에 있다'를 신제품 신호로 쓰지 않는다.** 카테고리는 nav 에서 찾아
전부 도는데(id 를 박으면 사이트가 칸을 늘릴 때 조용히 어긋난다), 빈 칸은
자연히 0건으로 지나간다. 다만 `신메뉴` 는 **맨 뒤로 돌린다** — 나중에 이 칸이
채워지면 버거·사이드와 같은 상품이 겹치는데, 그때 `category` 가 '신메뉴' 라는
판매 구좌로 덮이면 안 된다(먼저 본 것을 남기므로 진짜 분류가 이긴다).

## 🔴 `ca_id` 없이 `/menu/list` 를 받으면 안 된다 — 상품 아닌 행이 끼어 있다

`ca_id` 를 빼면 한 쪽에 **55건**이 온다. 칸별 합(54건)보다 하나 많다. 그 하나가
2026-10-08 실측:

```
idx=213  "하와이안베이컨치즈버거 출시"   배지 있음   ← 어느 칸에도 안 들어 있다
```

상품이 아니라 **출시 공지 배너**가 상품 테이블(`sp_product`)에 들어앉은 것이다.
분류가 없어서 칸별 목록에는 안 뜨고 전체 목록에만 뜬다. 긁으면
`하와이안베이컨치즈버거 출시` 라는 이름의 가짜 상품이 배지를 달고 올라간다.

**그래서 이 어댑터는 반드시 칸(`ca_id`)별로 돈다.** 요청이 늘더라도 전체 목록
한 방으로 바꾸지 마라. (사람이 여는 `SITES` 링크는 전체 목록이어도 상관없다.)

## 🔴 배지 — 같은 상품이 자리마다 다르다. **목록 페이지만 믿는다**

배지 요소는 `div.iconBox img[src="/images/icon-new.png"]` 하나인데 세 자리에서
비율이 딴판이다. 2026-10-08 전수 실측:

```
카테고리 목록 /menu/list?ca_id=NN        4 / 54  (7.4%)   ← ✅ 이것만 쓴다
상세 ?viewMode=view&idx=NN 본문          4 / 4   (표본 8건 중 목록과 일치)
상세의 '다른메뉴보기' 블록               14 / 14 (100%)   ← 🔴 조건 없이 찍는다
```

`다른메뉴보기` 는 **1972년부터 있는 간판 `모스버거`(idx 75)와 `와규치즈버거`
(idx 28)에도 배지를 달아 준다.** 템플릿이 무조건 렌더하는 것이고 퀴즈노스
66/66 과 같은 자리다. 거기서 긁었으면 메뉴판 54건이 통째로 신상이 됐다.
그래서 이 어댑터는 **상세 페이지를 아예 받지 않는다.**

⚠️ **`alt` 값으로 판정하면 안 된다.** 같은 배지의 `alt` 가 목록에선 `기간한정`,
상세 본문에선 `HIT` 고 파일명은 `icon-new` 다. 셋이 서로 다르니 어느 하나를
믿을 근거가 없다. 목록 페이지에 **요소가 있느냐만** 본다.

**① 종류 전수.** 목록 4칸의 `.iconBox img` 를 전부 세었더니
`('icon-new.png','기간한정','limit')` **4건**과 '없음' 50건, 두 가지뿐이다.
사이트가 쓰는 `icon-*` 파일을 raw 로 훑어도 **`icon-new.png` 하나**다
(`icon-best`·`icon-hot` **0회**). 뽕뜨락처럼 BEST 가 섞여 있지 않다.
`div.iconBox` 자체가 raw 에 **4번만** 나온다 — 배지 없는 카드엔 아예 안 그려진다.

**② 주석·숨김이 아니다.** 피자마루는 `<span class="new">` 가 카드 81장 전부에
있었는데 100% 주석 안이라 0/81 이었다. 여기선 `iconBox`·`icon-new.png` 가
**주석 안 0회 / 전체 4회**다. `display:none` 은 쪽당 2회(6칸 합 12회) 나오지만 **전부 배지와 무관한
자리**다(`#lnb > li:last-child` 네비 규칙과 smartlog 추적 픽셀).

**③ 배지 4건의 이름을 눈으로 읽었다.**
`하와이안베이컨치즈버거` · `하와이안베이컨치즈버거 세트` · `감자치즈고로케` ·
`저당수박에이드`. **1972년부터 있는 간판은 하나도 안 붙어 있다** —
`모스버거`(idx 75) · `모스치즈버거` · `와규치즈버거`(idx 28) · `코카콜라` ·
`후렌치후라이` 전부 `None` 이다. 마왕족발처럼 수년째 켜둔 배지가 아니다.
⚠️ 다만 `저당수박에이드` 는 10월에 수박 에이드다. `기간한정` 이라 곧 썩는 쪽이고
(함정 8) `endDate` 가 사이트에 없다 — `first_seen`+`STALE` 에 맡긴다.

배지 4건은 전체에서 **`idx` 가 가장 큰 넷**이다(226·227·228·229).
`idx` 는 `sp_product` 의 기본키라 등록 순서고, 배지와 순서가 서로를 받쳐 준다.
안 붙은 50건은 `False` 가 아니라 **`None`** 이다 — 운영자가 손으로 켜는
표시라 '안 켰다'가 '신제품이 아니다'를 뜻하지 않는다(피자스쿨·파파존스와 같은 선).

## ✅ 날짜 — 메뉴엔 없다. `모스소식` 게시판의 `<상품명> 출시!` 글에서 가져온다

메뉴는 목록에도 상세에도 등록일 필드가 **없다**. 대신 `/board/news` 가 진짜
출시 공지를 2021년부터 쌓아 두고 있다(일반글 26건 = 10+10+6, 4페이지는 0행이라
루프가 거기서 멈춘다). 2026-10-08 실측:

```
26.08.17 <하와이안베이컨치즈버거> 출시!   26.07.01 <허브앤치즈피쉬버거> 출시!
26.01.18 <데리야끼버거, 더블데리야끼버거> 출시!   25.10.12 <와규블랙올리브치즈버거>출시!
25.06.30 <어메이징크런치버거> 출시!      24.12.23 <더블베이컨치즈버거>출시!
24.09.02 <아메리켄 쉬림프 치즈버거>출시!  24.05.26 <크런치 치킨버거>출시!
24.01.08 <스노우 모스버거> 출시!        23.08.06 <그릴드 통 치킨버거> 출시!
23.05.10 <어메이징 쉬림프버거> 출시!     23.03.05 <매쉬드 포테이토치즈버거>출시!
22.12.12 <유즈코쇼 와규치즈버거>출시!    22.09.22 <BBQ 풀드포크버거> 출시!
22.07.25 <핫 썸머 치킨버거> 출시!       22.05.03 <쿠스쿠스 새우카츠버거> 출시!
22.03.02 <토마토바질버거>출시!          21.10.18 <매쉬드크림와규버거>출시!
```

### 왜 `uploaded_at` 이 아니라 `released_at` 인가

파리바게뜨 312장 사고 때문에 이걸 따져야 한다. 셋 다 통과한다:

1. **브랜드가 "출시"라고 말한 값이다.** 글 제목이 `<하와이안베이컨치즈버거> 출시!`
   다. 사진 올린 날도, 메뉴판 등록일도, 가격 개정일도 아니다. 출시를 알리려고
   쓴 글이고 그 글의 작성일이다. (`모스소식` 26건 중 출시 글이 아닌 8건은
   매장 GRAND OPENING·연휴 영업시간·안전보건 공지인데 `출시` 가 없어 빠진다.)
2. **일괄 묶음이 없다.** 5년에 걸쳐 18건이고 **한 날 최대 1건**이다. 파리바게뜨는
   하루 98건·67건이었고 제일제면소는 22건 중 9건이 하루였다. 여긴 그 모양이 아니다.
   게시판을 통째로 옮겨 심으면 날짜가 뭉치는데, 그걸 `_launches` 뒤 가드가 잡는다.
3. **내용이 연도와 맞는다.** 2021 매쉬드크림와규, 2022 쿠스쿠스·유즈코쇼,
   2023 매쉬드포테이토, 2024 크런치치킨, 2026 데리야끼·하와이안. 역순이 없다.

### 붙는 건 6건뿐이고, 배지와는 1건만 겹친다 (2026-10-08 실측)

```
released_at 6건   하와이안베이컨치즈버거 2026-08-17 · 데리야끼버거 2026-01-18 ·
                  더블데리야끼버거 2026-01-18 · 와규블랙올리브치즈버거 2025-10-12 ·
                  크런치치킨버거 2024-05-26 · 더블베이컨치즈버거 2024-12-23
is_new=True 4건   하와이안베이컨치즈버거(+세트) · 감자치즈고로케 · 저당수박에이드
겹침 1건          하와이안베이컨치즈버거  ← 배지와 날짜가 서로를 받쳐 준다
```

6건 중 **60일 창에 드는 건 하와이안베이컨치즈버거 하나**(52일 전)다. 나머지 5건은
1~2년 전이라 날짜가 있어도 화면에 안 오른다 — 그게 맞는 동작이다. 이름이 정확히
같아야 붙이므로 나머지 48건은 날짜가 빈 채로 나가고, 근거가 없으니 역시 안 오른다.

⚠️ **이름이 정확히 같을 때만 붙인다.** 게시판 이름과 메뉴 이름이 띄어쓰기만
다른 건 붙지만(`크런치 치킨버거` → `크런치치킨버거`), `쿠스쿠스 새우카츠버거`
와 메뉴의 `새우카츠버거` 는 **안 붙인다.** 부분일치를 허용하면 `모스버거` 가
`스노우 모스버거`(2024-01-08)에 걸려 1972년 간판 상품이 신상이 된다. 못 붙은
건 날짜 없이 두는 게 정직하다 — 54건 중 6건만 붙고 나머지는 빈 채로 나가며,
근거가 없으니 `rules.is_fresh` 가 화면에 안 올린다.

⚠️ 한 상품이 두 글에 나오면 **가장 이른 날짜로 고정**한다(피자마루 `치즈 폭탄
피자` 가 2020년 메뉴인데 2025년 신상이 됐던 사고). 지금은 겹치는 이름이 없지만
재출시 공지가 올라오면 바로 겹친다.

## 나머지

  - 세트 15건은 그대로 내보낸다. 어댑터가 세트를 판단하지 말라는 게
    `Item.promo` 주석의 지시고, `rules` 가 알아서 턴다. **실측으로 확인했다** —
    `하와이안베이컨치즈버거 세트` 도 배지가 붙어 올라가지만
    `rules.base_name("하와이안베이컨치즈버거 세트")` 가 `'하와이안베이컨치즈버거'`
    를 돌려주므로 `merge_variants` 가 단품과 한 그룹으로 묶고 **더 짧은 단품을
    대표로** 남긴다. 화면에 오르는 건 단품 하나뿐이고, 날짜(2026-08-17)도
    단품 쪽에 있다. 세트가 혼자 남는 경우도 없다(60일이 지나면 둘 다 빠진다).
  - ⚠️ `모스너겟(5조각)`·`(10조각)`, `통새우너겟(3조각)` 처럼 `(N조각)` 변형이
    있는데 `rules`·`base` 어디에도 '조각' 을 터는 규칙이 없어 따로 올라간다.
    **여기선 배지가 하나도 안 붙어 화면에 안 뜨므로 건드리지 않았다.**
    (러브레터는 `치즈인 순살치킨 (4조각/10조각)` 둘 다 배지가 붙어서 그쪽
    어댑터 안에서 합쳤다. 공용 `base._SIZE` 는 양쪽 다 안 건드렸다.)
  - 이미지는 목록 카드의 썸네일이고 54/54 전건 절대 URL 이다.
    ⚠️ **등록 담당자에게: 이미지가 http 전용이다.** `base.derive()` 가 http 주소를
    `image` 에서 `image_src` 로 옮기므로 `to_dict()` 뒤 `image` 는 **54/54 빈
    문자열**이 된다. `rules.mirror_images` 가 돌아야 카드에 사진이 뜬다
    (에그드랍·퀴즈노스·쉐이크쉑·스쿨푸드와 같은 칸이다). 어댑터의 이미지 가드는
    derive 전 값을 보므로 정상 통과한다.
  - 설명(`desc`)은 상세 페이지에만 있는데, 상세에는 위의 깨진 배지 블록이
    같이 붙어 있고 54번을 더 받아야 한다. 가맹점 7개짜리 브랜드에 요청을
    54번 더 쏘지 않는다. 영문명은 목록 카드(`div.en`)에 있어서 그건 넣는다.
  - ⚠️ 상세 페이지가 **SQL 쿼리문을 본문에 그대로 인쇄한다**(`select product.*
    ... from sp_product ...`). 디버그 출력이 운영에 남은 것으로 보인다. 더
    찔러보지 않았고 수집에도 안 쓴다. notes 에 적어 뒀다.
  - 상품명 54건을 전부 눈으로 읽었다. 주류·비식품은 없다.
"""
import collections
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "모스버거"
ROOT = "http://www.moskorea.kr"      # ⚠️ https 아님, mosburger.co.kr 아님
MENU = ROOT + "/menu/list"
NEWS = ROOT + "/board/news"
DELAY = 1.5
MAX_PAGES = 10       # 폭주 방지. 2026-10-08 실측은 메뉴 6칸 + 소식 4페이지다.

# 상품이 들어 있지 않은 칸. 지금은 포스터 1장뿐이라 0건으로 지나가지만,
# 나중에 채워져도 '신메뉴' 라는 판매 구좌가 진짜 분류를 덮으면 안 되므로
# 맨 뒤로 돌린다(먼저 본 분류가 남는다).
LAST_CAT = "신메뉴"

# `<상품명> 출시!` 에서 이름만. 꺾쇠 안을 집고 쉼표로 쪼갠다.
_LAUNCH = re.compile(r"[<〈＜]([^>〉＞]+)[>〉＞]")
# ⚠️ '재출시' 는 일부러 뺀다. 재출시 공지는 **그 이름으로 더 오래된 출시 글이
#    게시판에 이미 있을 때만** 안전하다(아래 '가장 이른 날짜' 가 막아 준다).
#    1972년 간판 `모스버거` 처럼 게시판 개설(2021) 이전 상품에 `<모스버거> 재출시!`
#    가 올라오면 비교 대상이 없어 그 날짜가 그대로 붙고 간판이 신상이 된다.
#    재출시는 신제품이 아니므로 아예 안 읽는 쪽이 맞다.
_IS_LAUNCH = re.compile(r"(?<!재)출시")
_YYMMDD = re.compile(r"(\d{2})\.(\d{2})\.(\d{2})")

MIN_ITEMS = 40          # 2026-10-08 실측 54건
# 2026-10-08 실측: 출시 글 18건에서 이름 19개(데리야끼 글 하나가 이름 둘).
# 세는 단위는 **이름** 이다.
MIN_LAUNCHES = 8
MIN_FILLED_CATS = 4     # 상품이 든 칸 수. 실측 4칸(버거·세트·사이드·음료&디저트)
BADGE_MAX_RATIO = 1 / 3  # 2026-10-08 실측 4/54 = 7.4%


def _norm(s: str) -> str:
    """비교용 이름. 공백만 턴다. 부분일치는 쓰지 않으니 이걸로 충분하다."""
    return re.sub(r"\s+", "", s or "").lower()


NAV_CA = "02"           # nav 를 읽으려고 아무 칸이나 하나 받는다


def _cats(c, cache: dict) -> list:
    """nav 에서 (ca_id, 칸 이름). id 를 박으면 칸이 늘 때 조용히 어긋난다.

    받은 본문은 `cache` 에 넣어 아래 수집 루프가 다시 안 받게 한다.
    """
    r = base.retry(lambda: c.get(MENU, params={"ca_id": NAV_CA}))
    r.raise_for_status()
    cache[NAV_CA] = r.text
    nav = HTMLParser(r.text).css_first("li.menu ul")
    out = []
    for a in (nav.css("a") if nav is not None else []):
        m = re.search(r"ca_id=(\w+)", a.attributes.get("href") or "")
        if m and m.group(1) not in [x[0] for x in out]:
            out.append((m.group(1), " ".join(a.text().split())))
    # '신메뉴' 는 맨 뒤로 (docstring 참고)
    out.sort(key=lambda x: x[1] == LAST_CAT)
    return out


def _launches(c) -> dict:
    """정규화한 상품명 → 출시일(YYYY-MM-DD). 겹치면 **가장 이른 날**을 남긴다."""
    dates: dict[str, str] = {}
    page = 1
    while page <= MAX_PAGES:
        r = base.retry(lambda: c.get(NEWS, params={"page": page}))
        r.raise_for_status()
        # 공지글(tr.tr_notice)은 매 페이지 위에 다시 붙는다. 일반글만 센다.
        rows = [tr for tr in HTMLParser(r.text).css("#sb-list tbody tr")
                if "tr_notice" not in (tr.attributes.get("class") or "")]
        if not rows:
            break
        for tr in rows:
            sbj, dt = tr.css_first("td.sbj a"), tr.css_first("td.date")
            if sbj is None or dt is None:
                continue
            title = " ".join(sbj.text().split())
            if not _IS_LAUNCH.search(title):
                continue          # 매장 오픈·연휴 공지
            m = _YYMMDD.search(" ".join(dt.text().split()))
            if not m:
                continue
            day = f"20{m.group(1)}-{m.group(2)}-{m.group(3)}"
            for chunk in _LAUNCH.findall(title):
                for nm in chunk.split(","):     # '<데리야끼버거, 더블데리야끼버거>'
                    k = _norm(nm)
                    # 재출시 공지가 올라오면 같은 이름이 두 번 나온다.
                    # 늦은 쪽을 쓰면 옛 상품이 신상이 된다(피자마루 사고).
                    if k and (k not in dates or day < dates[k]):
                        dates[k] = day
        page += 1
        time.sleep(DELAY)
    return dates


def fetch() -> list[Item]:
    items: list[Item] = []
    seen: set[str] = set()
    badged = 0

    per_cat: dict = {}          # 칸별 건수. 칸이 통째로 사라지는 걸 잡는다
    with base.client() as c:
        launched = _launches(c)
        time.sleep(DELAY)
        cache: dict = {}
        cats = _cats(c, cache)
        if not cats:
            raise RuntimeError(
                f"{BRAND}: 메뉴 카테고리를 nav 에서 하나도 못 읽었다 — "
                "'li.menu ul' 구조가 바뀌었다")
        for ca_id, cat in cats:
            html = cache.get(ca_id)
            if html is None:
                time.sleep(DELAY)
                r = base.retry(lambda: c.get(MENU, params={"ca_id": ca_id}))
                r.raise_for_status()
                html = r.text
            # ⚠️ 'ul.listType1' 은 상세의 '다른메뉴보기' 에도 쓰이는 클래스다.
            #    목록 페이지만 받으므로 여기 걸리는 건 진짜 목록뿐이다.
            cards = HTMLParser(html).css("ul.listType1 > li")
            per_cat[cat] = len(cards)
            for li in cards:
                ko = li.css_first(".ko")
                name = " ".join(ko.text().split()) if ko is not None else ""
                if not name:
                    continue
                en = li.css_first(".en")
                img = li.css_first(".imgBox img")
                a = li.css_first("a.link")
                href = a.attributes.get("href") or "" if a is not None else ""
                idx = re.search(r"idx=(\d+)", href)
                # 배지는 목록 페이지에만 있는 이 요소 하나다. alt 는 자리마다
                # 달라서(기간한정/HIT) 값으로 판정하지 않고 유무만 본다.
                has_badge = li.css_first(".iconBox img") is not None
                badged += has_badge
                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en=" ".join(en.text().split()) if en is not None else "",
                    image=(img.attributes.get("src") or "") if img is not None else "",
                    category=cat,
                    # 이름이 정확히 같은 출시 공지가 있을 때만. 부분일치는
                    # '모스버거'가 '스노우 모스버거'에 걸려서 안 쓴다.
                    released_at=launched.get(_norm(name), ""),
                    # 배지가 없는 건 '신제품이 아니다'가 아니라 '모른다'다.
                    is_new=True if has_badge else None,
                    url=(f"{ROOT}/menu/list?viewMode=view&ca_id={ca_id}"
                         f"&idx={idx.group(1)}" if idx else f"{MENU}?ca_id={ca_id}"),
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

    if len(items) < MIN_ITEMS:
        raise RuntimeError(
            f"{BRAND}: 상품 {len(items)}건 — 2026-10-08 실측은 54건이었다. "
            f"'ul.listType1 > li' 가 바뀌었거나 칸을 덜 돌았다 "
            f"(칸별: {per_cat})")

    # 🔴 칸 하나가 통째로 사라지면 MIN_ITEMS 만으로는 못 잡는다. 실측 54건에
    #    바닥이 40이라 12건짜리 '사이드'·'음료&디저트' 가 빠져도 42건으로 통과한다.
    #    칸별 0건을 일괄로 막을 수는 없다 — '신메뉴'·'모스의 아침' 은 **정상적으로**
    #    0건이다(포스터 1장). 그래서 '상품이 든 칸 수' 에 바닥을 둔다.
    filled = sum(1 for n in per_cat.values() if n)
    if filled < MIN_FILLED_CATS:
        raise RuntimeError(
            f"{BRAND}: 상품이 든 칸이 {filled}개뿐이다 "
            f"(기대 {MIN_FILLED_CATS}개, 2026-10-08 실측 버거15·세트15·사이드12·"
            f"음료&디저트12). 칸 하나가 통째로 빠졌다 — 칸별: {per_cat}")

    if not any(i.image for i in items):
        raise RuntimeError(f"{BRAND}: 이미지가 0건 — '.imgBox img' 가 바뀌었다")

    # 🔴 이 가드가 이 어댑터의 핵심이다. 목록 템플릿이 상세의 '다른메뉴보기'
    #    처럼 배지를 무조건 찍게 바뀌면 메뉴판 54건이 통째로 신상이 된다.
    #    2026-10-08 실측은 4/54(7.4%)다.
    if badged > len(items) * BADGE_MAX_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {badged}건에 배지가 붙었다 "
            f"(기대 {BADGE_MAX_RATIO:.0%} 이하, 2026-10-08 실측 4/54=7.4%). "
            "목록 템플릿이 상세의 '다른메뉴보기'처럼 무조건 찍게 바뀌었는지 보라")
    if badged == 0:
        raise RuntimeError(
            f"{BRAND}: 배지가 0건이다 — 2026-10-08 실측은 4건이었다. "
            "'.iconBox img' 가 바뀌었다면 신제품을 영영 못 집는다")

    if len(launched) < MIN_LAUNCHES:
        raise RuntimeError(
            f"{BRAND}: 모스소식에서 출시 상품명을 {len(launched)}개밖에 못 읽었다 "
            f"— 2026-10-08 실측은 글 18건에서 이름 19개였다(데리야끼 글 하나가 "
            "이름 둘). 게시판 표 구조나 '<상품명>' 표기가 바뀌었다. "
            "날짜를 잃으면 60일 창을 건너뛴다")

    # 출시 공지가 한 날짜에 몰리면 게시판을 옮겨 심은 것이다. 그대로 두면
    # 이름이 맞는 상품이 전부 같은 날 신상이 된다. 실측 최대 묶음은 1건이다.
    days = collections.Counter(launched.values())
    top, n = days.most_common(1)[0]
    if n > max(3, len(launched) / 3):
        raise RuntimeError(
            f"{BRAND}: 출시 공지 {len(launched)}건 중 {n}건이 {top} 한 날에 "
            "몰렸다 — 게시판 일괄 이관으로 보인다. released_at 으로 쓰면 안 된다")
    return items
