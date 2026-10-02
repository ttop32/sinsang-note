"""한신포차(더본코리아).

더본코리아 브랜드 중 **유일하게 상품별 날짜를 주는 곳**이다. 나머지 18개 브랜드는
신제품 신호도 날짜도 없어서 본사 보도자료로만 다룬다(collectors/theborn.py §2).
그래서 이 브랜드만 theborn.py 의 ALIAS 에서 빼고 따로 둔다 — 두 어댑터가 같은
브랜드를 뱉으면 collect 가 같은 키를 두 번 담는다(어댑터 사이 중복은 안 걸러준다).

수집 경로. 2026-10-02 실측. 브라우저 불필요, 총 7요청.

  ① GET https://hanshinpocha.com/menu/
     탭 4개가 **한 페이지에 다 들어 있다**(133KB). `.tabs li[data-tab]` 순서와
     `.menu_wrap` 순서가 1:1 이라 카테고리는 그 자리에서 붙인다.
       대표 메뉴 3 / 안주 메뉴 33 / 탕·찌개 메뉴 6 / 하이볼·칵테일 메뉴 10 = 52건
     카드 `.inner` 안에 `.menu_tit`(이름)·`.desc`(설명)·`.thumb img`(이미지).
     `.price` 는 전건 `<!--  -->` 라 가격은 없다.

  ② GET https://hanshinpocha.com/feed/?post_type=post_menu&paged=1..6
     **여기가 핵심이다.** 메뉴가 `post_menu` 라는 커스텀 포스트 타입인데
     `/wp-json/wp/v2/types` 에는 post·page·attachment 뿐이라 REST 로는 안 열린다
     (`/wp-json/wp/v2/post_menu` → 404). sitemap 도 전부 404다.
     그런데 **RSS 피드는 post_type 쿼리로 CPT 를 그대로 열어준다.** 10건씩
     6페이지(10·10·10·10·10·2 = 52건), paged=7 은 404 로 끊긴다.

  ③ 제목으로 ①과 ②를 잇는다. **52건이 빠짐없이 1:1 로 붙는다**(양쪽 missing 0).
     ⚠️ 피드 제목에 `&#038;` 같은 엔티티가 들어오므로 html.unescape 가 필수다
        ('오징어부추전&초무침').

날짜 — `pubDate` 를 **uploaded_at** 에 넣는다. released_at 이 아니다.
  이건 '그 메뉴가 메뉴판에 오른 날'이지 브랜드가 말한 출시일이 아니다.
  본아이에프가 이미지 파일명 날짜를 uploaded_at 에만 넣은 것과 같은 자리다.
  🔎 **교차검증했다(2026-10-02).** 52건 전부에 대해 pubDate 의 연·월과 그 상품
     이미지의 `/wp-content/uploads/YYYY/MM/` 를 맞춰 봤다.
       일치 51 / 불일치 1 / 피드 누락 0
     불일치 1건은 '한신 무뼈닭발'(pubDate 2017-12, 이미지 2021/12)인데
     2017년 상품의 사진만 2021년에 바꾼 것으로 설명이 된다.
     같은 대조를 미정국수0410 에 돌리면 25건 중 24건이 어긋난다(2018년 간판
     메뉴 20여 장이 2026-01-15 20분 사이에 재등록돼 있다). 그래서 그쪽은 버리고
     여기 것만 쓴다. **'날짜가 있다'와 '그 날짜가 상품 날짜다'는 다른 말이다.**
  ⚠️ 그래도 일괄 등록 흔적은 있다. 2026-06-15 에 14건이 10분 간격으로 찍혀 있다.
     이건 재등록이 아니라 **진짜 메뉴 증설**로 보인다 — 그 14건의 이미지가 전부
     `/uploads/2026/06/` 이고 이름도 전부 그때 처음 보이는 것들이다(갑오징어구이·
     반건조노가리구이·딸기주물럭 등). 2025-04~05 에도 비슷한 묶음이 있다.
     rules.untrust_bulk_dates() 가 uploaded_at 을 보고 이상치를 지우는데,
     BULK_MIN 이 20 이라 14건짜리 묶음은 안 걸린다. 걸릴 만큼 큰 묶음이 오면
     그때는 자동으로 무효화된다 — 그 안전망에 기대려고 released_at 이 아니라
     uploaded_at 에 넣는 것이다.

is_new 는 None 이다. 배지가 없다.
  🔎 `/menu/` 에서 '신메뉴'가 3번 잡히는데 **전부 `한신메뉴`의 부분일치**다
     (`<title>한신메뉴</title>` 와 PC·모바일 네비게이션 링크). 'new' 2건도
     `new Date()` 와 패밀리사이트 링크 `newmaul.com` 이다. 배지 요소·클래스는
     하나도 없다. 신제품 판정은 uploaded_at 과 collect 의 어제 대비 diff 가 맡는다.

url 은 비운다. 피드가 상품별 permalink(`/post_menu/<slug>/`)를 주긴 하는데
**열어 보면 빈 껍데기다** — 2026-10-02 '갑오징어구이' 상세를 받아 보니 제목만
<title> 에 있고 본문에 상품 이미지도 설명도 없다(uploads 이미지 0장, 본문이
브랜드 소개 문구와 푸터뿐). 눌렀을 때 아무것도 없는 페이지로 보내느니
base.SITES 폴백(/menu/)이 낫다.

⚠️ 주류가 섞여 있다. 하이볼·칵테일 탭 10건과 안주 탭 일부가 base.is_alcohol() 에
   걸려 본 목록에서 빠진다. 데이터에는 남으므로 어댑터가 따로 거르지 않는다.

robots: https://hanshinpocha.com/robots.txt → 200, text/plain, 3줄.
        `User-agent: *` / `Disallow: /wp-admin/` / `Allow: /wp-admin/admin-ajax.php`.
        우리가 쓰는 `/menu/` 도 `/feed/` 도 금지 대상이 아니다.
약관: 없다. 푸터에 약관·개인정보 링크가 하나도 없고 `/terms/`·`/privacy/`·
      `/policy/` 가 전부 404 다(2026-10-02 실측). 수집 금지 문구를 찾지 못했다.
"""
import html
import re
import time
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "한신포차"
SITE = "https://hanshinpocha.com"
MENU = SITE + "/menu/"
FEED = SITE + "/feed/"
POST_TYPE = "post_menu"
KST = timezone(timedelta(hours=9))
MAX_PAGES = 10       # 한 페이지 10건. 폭주 방지 상한(현재 6페이지에서 끝난다).
DELAY = 1.5


def _clean(s: str) -> str:
    return " ".join(html.unescape(s or "").split())


def _cards(page: str) -> list:
    """(카테고리, 이름, 설명, 이미지). 탭 순서와 `.menu_wrap` 순서가 1:1 이다."""
    doc = HTMLParser(page)
    tabs = [_clean(t.text()) for t in doc.css(".tabs li")]
    wraps = doc.css(".menu_wrap")
    if not wraps:
        raise RuntimeError("`.menu_wrap` 이 없다 — 메뉴 페이지 마크업이 바뀌었다")
    # 탭 이름이 모자라면 카테고리만 비우고 상품은 살린다. 탭이 늘어났을 뿐인데
    # 브랜드를 통째로 죽일 일은 아니다.
    if len(tabs) != len(wraps):
        tabs = tabs + [""] * len(wraps)

    out = []
    for label, wrap in zip(tabs, wraps):
        inners = wrap.css(".inner")
        if not inners:
            raise RuntimeError(f"탭 '{label}' 의 상품이 0건 — 셀렉터가 깨졌을 수 있다")
        for card in inners:
            tit = card.css_first(".menu_tit")
            if tit is None:
                continue
            img = card.css_first(".thumb img")
            desc = card.css_first(".desc")
            out.append((label, _clean(tit.text()),
                        _clean(desc.text()) if desc else "",
                        img.attributes.get("src", "") if img else ""))
    return out


def _dates(c) -> dict:
    """상품명 → 게시일(YYYY-MM-DD). RSS 가 CPT 를 열어주는 유일한 경로다."""
    out = {}
    for page in range(1, MAX_PAGES + 1):
        if page > 1:
            time.sleep(DELAY)
        r = base.retry(lambda: c.get(FEED, params={"post_type": POST_TYPE,
                                                   "paged": page}))
        if r.status_code == 404:        # 마지막 페이지 다음은 404 로 끊긴다
            break
        r.raise_for_status()
        items = re.findall(r"<item>(.*?)</item>", r.text, re.S)
        if not items:
            break
        for it in items:
            t = re.search(r"<title>(.*?)</title>", it, re.S)
            d = re.search(r"<pubDate>(.*?)</pubDate>", it)
            if not (t and d):
                continue
            name = _clean(re.sub(r"<!\[CDATA\[|\]\]>", "", t.group(1)))
            when = _kst(d.group(1))
            if when:
                out[name] = when
    return out


def _kst(stamp: str) -> str:
    """RSS pubDate → 한국 날짜(YYYY-MM-DD). 못 읽으면 빈 문자열.

    피드는 `Mon, 15 Jun 2026 00:21:21 +0000` 처럼 UTC 로 온다. 러너 시간대가
    UTC 일 수 있으므로 KST 로 **고정**해서 바꾼다. astimezone() 에 맡기면
    러너에 따라 날짜가 하루씩 어긋난다(이 레포는 GitHub Actions 에서 돈다).
    """
    try:
        when = parsedate_to_datetime(stamp)
    except (TypeError, ValueError):
        return ""
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when.astimezone(KST).strftime("%Y-%m-%d")


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(MENU))
        r.raise_for_status()
        cards = _cards(r.text)
        if not cards:
            raise RuntimeError("메뉴 0건 — 셀렉터가 깨졌다")
        time.sleep(DELAY)
        dates = _dates(c)

    # 피드가 통째로 비면 날짜가 전부 사라진다. 조용히 날짜 없는 52건이 되느니
    # 드러낸다 — 이 어댑터를 따로 만든 이유가 날짜이기 때문이다.
    if not dates:
        raise RuntimeError(
            f"{POST_TYPE} 피드에서 날짜를 한 건도 못 받았다 — "
            f"post_type 쿼리가 막혔거나 피드가 꺼졌다")

    items: list[Item] = []
    seen = set()
    matched = 0
    for label, name, desc, image in cards:
        when = dates.get(name, "")
        matched += bool(when)
        it = Item(
            brand=BRAND,
            name=name,
            desc=desc,
            image=image,
            category=label,
            uploaded_at=when,        # 출시일이 아니라 메뉴판 등록일이다(docstring)
            # 배지가 없다. '신메뉴' 문자열은 전부 '한신메뉴'의 부분일치였다.
            is_new=None,
        )
        if it.key not in seen:
            seen.add(it.key)
            items.append(it)

    # 2026-10-02 실측은 52/52 였다. 제목 표기가 한쪽만 바뀌면 조인이 조용히
    # 깨지는데, 그러면 날짜 없는 메뉴판이 되어 이 어댑터의 뜻이 사라진다.
    if matched < len(items) * 0.8:
        raise RuntimeError(
            f"메뉴 {len(items)}건 중 날짜가 붙은 건 {matched}건뿐 — "
            f"제목 조인이 깨졌다(피드 {len(dates)}건)")
    return items
