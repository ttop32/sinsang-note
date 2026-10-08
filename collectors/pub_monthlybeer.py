"""월간맥주 — 맥주 프랜차이즈. (프랜차이즈, 안주)

삼정프랜차이즈(김부성, 광주 동구 의재로136번길 2-11) 운영.
공정위 `주점` 등록 500개 중 **가맹점 60개**(2026-10-08 프차몰 실측).

## 🔴 이 어댑터가 뒤집는 것 — "주점은 메뉴가 이미지뿐이라 불가"

`CANDIDATES-CAFE2.md` §8-6 이 투다리·청담동말자싸롱·생활맥주 **3곳**을 보고
업종 500개를 통째로 접었고, 그 판정이 `COVERAGE-SUMMARY.md`·`CRAWLING-POLICY.md`
§6-4·`ROADMAP.md` 로 퍼졌다. 2026-10-08 에 **26곳을 다시 열었고 8곳이 상품명을
텍스트로 준다**(`notes/CANDIDATES-PUB-RETAIL-DRINK.md` §2). 여기는 그중
**신상 신호까지 있는 유일한 곳**이다.

## 경로 — 카테고리 10칸을 돌면 끝난다

    GET https://www.monthlybeer.co.kr/product/list?ca_id=<01..10>[&page=N]

카테고리 이름은 **페이지가 스스로 알려준다** — 내비게이션의
`a[href*="product/list?ca_id="]` 가 `01 피자/파스타 … 10 스낵류` 를 준다.
그래서 여기에 칸 이름을 적어 두지 않는다(적어 두면 사이트가 바꿀 때 어긋난다).

⚠️ **페이징 파라미터를 목록 마크업에서 읽었다.** `div.paging` 의 링크는
`/_subpage/kor/product/list.php?…&page=N` 라는 **다른 경로**를 가리킨다.
그런데 `/product/list?ca_id=01&page=2` 로도 똑같이 동작한다(실측 확인).
한화갤러리아 때처럼 "같은 바이트 = 페이징 없음" 으로 단정하지 않고
**링크를 먼저 읽은** 결과다(함정 8).

전체 목록(`/product/list`, ca_id 없음)은 9쪽 68건이고, 칸별 합(7+7+11+7+9+8+1+2+6+10)도
**정확히 68** 이다. 칸별로 도는 쪽을 택한 건 `category` 를 같이 얻기 위해서다.

## ⭐ 신상 신호 — **상품명 앞의 `[NEW]` 말머리**

배지가 별도 요소가 아니다. `span.tit` 안에 **글자로** 들어 있다.

**2026-10-08 실측 — 68건 중 `[NEW]` 7건 (10.3%)**

```
[NEW] 크레이지핫치킨 패스츄리피자   (피자/파스타)
[NEW] 숙주산더미탕수육             (튀김류)
[NEW] 우삼겹표고계란전             (튀김류)
[NEW] 갈릭버터치즈통감자           (튀김류)
[NEW] 칼칼고추장찌개               (탕류)
[NEW] 꼬지어묵김치우동             (탕류)
[NEW] 허니고구마프라이             (스낵류)
```

⚠️ **대괄호 말머리를 세면 안 된다 — 같은 자리에 다른 말머리가 또 있다.**
`[상하키친] 트러플크림 파스타`·`[상하키친] 레몬크림새우`·`[상하키친] 마늘깐풍기`
**3건**이 공동 브랜드 표시로 붙어 있다. 설빙 `span.flag` 에 시그니처 배지가
섞였던 사고와 같은 자리다. 그래서 **`[NEW]` 문자열만** 본다.
`[상하키친]` 은 브랜드가 쓰는 상품명의 일부라 이름에 그대로 남긴다.

⚠️ **`[NEW]` 가 아닌 61건을 `is_new=False` 로 두지 않는다.** 말머리는
"이건 신상이다" 만 말하고 "이건 신상이 아니다" 는 말하지 않는다. `False` 로
두면 날짜가 전혀 없는 이 브랜드는 `rules.is_fresh` 의 `is_new is False` 분기가
`released_at` 을 요구해 **61건이 영구히 안 나온다**(더플레이스 사고). `None` 이면
diff 경로로 떨어져 나중에 메뉴가 늘 때 잡힌다. 얌샘김밥과 같은 처분이다.

## 날짜가 하나도 없다

목록에도 상세에도 등록일이 없고, 이미지 파일명은
`<숫자>_<랜덤>_<sha1>.png` 라 epoch 도 없다(농심처럼 파일명에서 뽑을 수 없다).
`released_at`·`uploaded_at` 둘 다 **비운다.** 억지로 오늘 날짜를 넣으면
메뉴판 전체가 60일 창에 들어온다(함정 5 의 반대 방향 사고).
`is_new=True` 7건은 `rules.is_fresh` 가 `first_seen` + STALE 로 걷어간다.

## 술은 안 들어 있다 — 그래도 막아 둔다

카테고리 10칸이 전부 음식이다(`주류`·`맥주`·`하이볼` 칸이 없다). 68건을 눈으로
읽었고 술은 0건이다. 다만 **주점이라 언제든 생길 수 있어서** 칸 이름에 술이
들어가면 건너뛴다(`_ALCOHOL_CATES`). 호맥은 `[NEW]` 3건 중 2건이 맥주였다.

## 이미지

`div.tmb` 의 `style="background-image:url('…')"` 에서 뽑는다. 주소가
`https://www.monthlybeer.co.kr:443/superboard/…` 로 **포트가 박혀서** 온다.
:443 을 붙인 쪽과 뗀 쪽이 같은 바이트(91,472B PNG)라 떼고 쓴다.

## robots.txt — 200 / 298B. **우리에게 해당하는 규칙이 없다**

`Googlebot-Image`·`bingbot`·`ZoominfoBot`·`SemrushBot`·`DotBot`·`AhrefsBot` 이
`Disallow: /`, `Yeti`·`NaverBot` 이 `Allow: /`. **`User-agent: *` 그룹이 아예 없다.**
`sinsang-note/1.0` 은 어느 그룹에도 안 걸린다. UA 위장은 하지 않는다.

## 이용약관 — **읽었다.** `/doc/policy` (200 / 43,761B)

LNB 서브메뉴의 `<li><a href="/doc/policy">이용약관</a></li>` 한 줄이 주석 처리돼
있어서 처음엔 "약관 없음"으로 봤는데 **틀렸다.** 푸터의 `약관 및 정책` 링크가
살아 있고 같은 주소가 **약관 전문**을 준다(제1장 총칙 제1조(목적)…).

- **크롤링·로봇·스크래핑을 금지하는 문구는 없다**(`크롤`·`스크래` 전수 0건).
- 다만 회원 금지행위에 이런 조항이 있다 — "회사의 서비스에 게시된 정보를
  변경하거나 서비스를 이용하여 얻은 정보를 회사의 사전 승낙 없이 영리 또는
  비영리의 목적으로 복제, 출판, 방송 등에 사용하거나 제3자에게 제공하는 행위".
  제1조가 적용 범위를 **"회원으로 가입하고 이를 이용함에 있어"** 로 한정하고
  우리는 로그인하지 않는 비로그인 수집이라 문면상 바로 걸리지는 않는다.
  **판단은 운영자 몫이다** — 할리스·폴바셋을 뺀 조항과 같은 종류다.
  삭제 요청이 오면 즉시 내린다.

등록 제안: 유형 `FRANCHISE`, 세부분류 `안주`
          SITES `https://www.monthlybeer.co.kr/product/list`
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "월간맥주"
SITE = "https://www.monthlybeer.co.kr"
LIST = SITE + "/product/list"
DELAY = 1.5
MAX_PAGES = 6     # 2026-10-08 실측 최대 칸이 11건(1쪽 8건)이라 2쪽이다. 폭주 방지.
                  # ⚠️ 상한에 닿으면 raise 한다 — 조용히 잘리면 안 된다.
MIN_CATES = 8     # 실측 10칸
# 실측 68건. 전엔 50 이었는데 **한 칸(최대 11건)이 통째로 사라져도 안 걸려서**
# 60 으로 올렸다. 아래 전체 목록 쪽수 교차검증이 같은 구멍을 한 겹 더 막는다.
MIN_ITEMS = 60
PER_PAGE = 8      # 전체 목록 한 쪽 건수. 쪽수 × 이 값으로 총계를 가늠한다
MAX_NEW_RATIO = 0.5   # 실측 7/68 = 10.3%. 절반을 넘으면 말머리를 남발한 것이다

# 🔴 술이 든 칸은 버린다. 2026-10-08 현재 이런 칸은 없지만 주점이라 언제든 생긴다.
_ALCOHOL_CATES = ("주류", "맥주", "소주", "와인", "하이볼", "사케", "칵테일")

# `span.tit` 맨 앞의 신상 말머리. ⚠️ `[상하키친]` 같은 다른 말머리가 같은 자리에
# 3건 있다. 대괄호를 통째로 털면 공동 브랜드 표시까지 지워진다.
_NEW_PREFIX = re.compile(r"^\[\s*NEW\s*\]\s*", re.I)

# `background-image:url('…')` 안의 주소. 따옴표가 있을 수도 없을 수도 있다.
_BG_URL = re.compile(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _image(li) -> str:
    tmb = li.css_first(".tmb")
    if tmb is None:
        return ""
    # ⚠️ selectolax 는 값 없는 속성에 None 을 준다(태리로제떡볶이 56건 증발).
    style = tmb.attributes.get("style") or ""
    m = _BG_URL.search(style)
    if not m:
        return ""
    # 사이트가 `https://host:443/…` 로 포트를 박아 준다. 떼도 같은 바이트다.
    return m.group(1).strip().replace("//www.monthlybeer.co.kr:443/",
                                      "//www.monthlybeer.co.kr/")


def _cates(doc) -> list[tuple[str, str]]:
    """내비게이션이 알려주는 (ca_id, 칸 이름). 칸 이름을 코드에 적지 않는다."""
    out, seen = [], set()
    for a in doc.css('a[href*="ca_id="]'):
        href = a.attributes.get("href") or ""
        m = re.search(r"ca_id=(\d+)", href)
        name = _clean(a.text())
        if not m or not name or m.group(1) in seen:
            continue
        seen.add(m.group(1))
        out.append((m.group(1), name))
    return out


def _page(c, ca_id: str, page: int) -> tuple[HTMLParser, list]:
    """상품 한 쪽. `ca_id` 가 빈 문자열이면 칸을 안 가린 전체 목록이다."""
    q = f"?ca_id={ca_id}" if ca_id else "?ca_id="
    url = LIST + q + (f"&page={page}" if page > 1 else "")
    r = base.retry(lambda: c.get(url))
    r.raise_for_status()
    doc = HTMLParser(r.text)
    return doc, doc.css("ul.prdt-list > li")


def _last_page(doc) -> int:
    """`div.paging` 이 말하는 마지막 쪽 번호. 총계 교차검증에 쓴다.

    칸별로 돌다 보면 **페이징이 조용히 죽어도 아무 소리가 안 난다** — 서버가
    `&page=N` 을 무시하거나 2쪽을 200 에러페이지로 주면 2쪽에 있던 6건이
    소리 없이 빠진다(2026-10-08 기준 튀김류 3·탕류 1·스낵류 2). 그걸 잡으려고
    칸을 안 가린 전체 목록의 쪽수를 같이 읽어 둔다. 1요청이면 된다.
    """
    nums = [int(a.text().strip()) for a in doc.css(".paging a")
            if a.text().strip().isdigit()]
    return max(nums) if nums else 0


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    skipped: list[str] = []

    with base.client(headers={"Referer": SITE + "/"}) as c:
        # 칸을 안 가린 전체 목록 1쪽. 여기서 ① 카테고리 목록과 ② 전체 쪽수를
        # 같이 얻는다. 전엔 `ca_id=01` 1쪽을 받아 놓고 루프에서 또 받아
        # **같은 요청을 두 번** 보냈다.
        doc, _ = _page(c, "", 1)
        cates = _cates(doc)
        last_page = _last_page(doc)
        if len(cates) < MIN_CATES:
            raise RuntimeError(
                f"{BRAND}: 카테고리가 {len(cates)}칸이다 — 2026-10-08 실측은 10칸"
                f"(피자/파스타 … 스낵류)이었다. 내비게이션 마크업이 바뀌었는지, "
                f"ca_id 링크 선택자가 어긋났는지 확인하라. 받은 값: {cates}")

        for ca_id, cname in cates:
            # 🔴 술 칸은 수집하지 않는다(주점이라 언제든 생긴다).
            if any(w in cname for w in _ALCOHOL_CATES):
                skipped.append(cname)
                continue
            for page in range(1, MAX_PAGES + 1):
                time.sleep(DELAY)
                _, rows = _page(c, ca_id, page)
                if not rows:
                    # ⚠️ "빈 쪽 = 끝" 과 "1쪽부터 깨짐" 을 구별한다. 실측상
                    # 1쪽이 0건인 칸은 없다(제일 작은 샐러드류도 1건). 1쪽이
                    # 비면 그 칸이 통째로 조용히 사라지는 것이라 드러낸다 —
                    # 가장 비싼 손실이다(튀김류 한 칸에 NEW 가 3건 있다).
                    if page == 1:
                        raise RuntimeError(
                            f"{BRAND}: `{cname}`(ca_id={ca_id}) 1쪽이 0건이다 — "
                            f"2026-10-08 실측은 모든 칸이 1건 이상이었다. 그 "
                            f"주소가 200 에러페이지를 주는지 확인하라")
                    break        # 2쪽 이후의 빈 쪽은 정상적인 끝이다.
                if page == MAX_PAGES:
                    # 상한에 닿았다는 건 더 있는데 안 받았다는 뜻일 수 있다.
                    raise RuntimeError(
                        f"{BRAND}: `{cname}`(ca_id={ca_id})가 상한 "
                        f"{MAX_PAGES}쪽에 닿았다 — 2026-10-08 실측 최대 칸은 "
                        f"11건(2쪽)이었다. 칸이 커졌으면 MAX_PAGES 를 올려라")
                for li in rows:
                    tit = li.css_first(".tit")
                    if tit is None:
                        continue
                    raw = _clean(tit.text())
                    if not raw:
                        continue
                    # ⚠️ `[NEW]` 만 턴다. `[상하키친]` 은 상품명의 일부다.
                    name = _NEW_PREFIX.sub("", raw)
                    flagged = name != raw
                    txt = li.css_first(".txt")
                    it = Item(
                        brand=BRAND,
                        name=name,
                        desc=_clean(txt.text()) if txt is not None else "",
                        image=_image(li),
                        category=cname,
                        # 날짜가 사이트 어디에도 없다. 비워 둔다(docstring §날짜).
                        # 말머리가 없는 건 '신상이 아니다' 가 아니라 '모른다' 다.
                        is_new=True if flagged else None,
                        # 상품별 페이지가 없다(li 에 a 가 없다). 칸 목록으로 보낸다.
                        url=f"{LIST}?ca_id={ca_id}",
                    )
                    if it.key in seen:
                        continue
                    seen.add(it.key)
                    items.append(it)

    if skipped:
        print(f"[{BRAND}] 술로 보이는 카테고리를 건너뛰었다: {skipped}")

    if len(items) < MIN_ITEMS:
        raise RuntimeError(
            f"{BRAND}: 상품 {len(items)}건 — 2026-10-08 실측은 68건이었다. "
            f"`ul.prdt-list > li` 선택자나 페이징(`&page=N`)이 바뀌었는지 확인하라")

    new_count = sum(1 for i in items if i.is_new)
    if new_count == 0:
        raise RuntimeError(
            f"{BRAND}: `[NEW]` 말머리가 0건이다 — 2026-10-08 실측은 68건 중 7건"
            f"(10.3%)이었다. 이 브랜드는 날짜가 전혀 없어서 **말머리가 유일한 "
            f"신상 신호**다. 0건이면 어댑터가 조용히 아무것도 못 내놓는다. "
            f"브랜드가 표기를 바꿨는지(예: `NEW ` 공백형·`[신메뉴]`) 확인하라")
    if new_count > len(items) * MAX_NEW_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {new_count}건이 `[NEW]` 다"
            f"(기대 {MAX_NEW_RATIO:.0%} 이하, 2026-10-08 실측 7/68=10.3%). "
            f"메뉴판이 통째로 신상으로 올라간다 — 개편으로 말머리를 일괄로 "
            f"붙였는지 확인하라")

    # 칸별 합 ↔ 전체 목록 쪽수 교차검증. 페이징이 조용히 죽는 걸 잡는다.
    # 전체 목록은 한 쪽 8건이라 마지막 쪽이 N 이면 총계는 (N-1)*8+1 ~ N*8 이다
    # (2026-10-08 실측: 9쪽 → 65~72, 실제 68).
    if last_page:
        lo, hi = (last_page - 1) * PER_PAGE + 1, last_page * PER_PAGE
        if not lo <= len(items) <= hi:
            raise RuntimeError(
                f"{BRAND}: 칸별로 모은 {len(items)}건이 전체 목록이 말하는 "
                f"{lo}~{hi}건({last_page}쪽 × {PER_PAGE}건) 밖이다 — 칸 하나가 "
                f"통째로 빠졌거나 `&page=N` 이 무시됐는지 확인하라")
    else:
        print(f"[{BRAND}] 전체 목록에서 쪽수를 못 읽었다(`div.paging`) — "
              f"총계 교차검증을 건너뛴다")

    imaged = sum(1 for i in items if i.image)
    if imaged < len(items) * 0.9:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 사진을 {imaged}건밖에 못 읽었다 — "
            f"`div.tmb` 의 `background-image:url(...)` 모양이 바뀌었는지 확인하라")
    return items
