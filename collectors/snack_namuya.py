"""국수나무 — 소식 게시판에서 신메뉴와 출시일을 뽑는다.

(주)해피브릿지에프앤씨(298-86-02026) · (주)에이치비에스(445-88-02233) 공동 운영.
공정위 `분식` 236개점. 도메인은 **`namuya.co.kr`** 이다(`guksunamu` 아님 —
로마자 표기를 추측하면 또 틀린다. '나무야'를 쓴다).

robots.txt: **200 / 21바이트 / `User-agent: * / Allow:/`**. 전부 https, SSR.
이용약관 문서는 푸터에 없다(개인정보처리방침·이메일무단수집거부만).

## 메뉴 페이지가 아니라 소식 게시판을 쓰는 이유

메뉴(`/food/food.php?cat_no=1~7` — 정식·생면·면·밥·돈까스·시즌메뉴·곁들임)는
SSR 로 깔끔하게 나오는데 **신상 구분이 하나도 없다.** NEW 배지도, 신메뉴
카테고리도, 날짜도 없다. 소스에 달린 주석이 구조를 그대로 말해 준다 —
`<!-- 상세페이지는 따로 없으며, 마우스가 올라갔을 때 설명글이 나타납니다. -->`.

반면 소식 게시판은 **제목에 `[신메뉴]` 접두가 붙고 날짜가 연도까지 온다.**

    <a href="/news/news.php?boardid=news&mode=view&idx=10" class="news-item">
      <span class="num">6</span>
      <div class="tit">[신메뉴] 직화제육덮밥 &amp; 직화제육면 출시</div>
      <div class="date">2026-10-01</div>

gnuboard 가 아니라 자체 게시판이라 **목록에 연도가 다 찍힌다**(슬로우캘리처럼
상세를 열어 연도를 확인할 필요가 없다). 2026-10-02 실측 전체 8건 중 `[신메뉴]`
5건이고, **최신이 2026-10-01 — 이 조사에서 본 분식 게시판 중 가장 신선하다.**

| 날짜 | 제목 | 판정 |
|---|---|---|
| 2026-10-01 | `[신메뉴] 직화제육덮밥 & 직화제육면 출시` | 담는다 |
| 2026-07-10 | `[신메뉴] 국수나무x셰프들의오픈런 콜라보 메뉴 3종 출시` | 담는다 |
| 2026-07-10 | `[신메뉴] 산더미 애호박국수 출시` | 담는다 |
| 2026-06-04 | `[신메뉴] 맑은고기국수 출시` | 담는다 |
| 2026-06-04 | `[신메뉴] 깨마니비빔막국수 & 돈므라이스 출시` | 담는다 |
| 2026-06-04 | `브랜드 홈페이지 리뉴얼 오픈 안내` · `공지` 2건 | 접두가 없어 안 걸린다 |

⚠️ **2026-06-04 세 건은 홈페이지를 새로 열면서 한꺼번에 올린 글이다**(같은 날
`브랜드 홈페이지 리뉴얼 오픈 안내` 가 같이 있다). 그 날짜는 글을 올린 날이지
상품이 나온 날이 아닐 수 있다. 그래도 `released_at` 에 넣는 건, 브랜드가
그 날짜로 공표한 값이고 우리가 더 나은 값을 만들 수 없기 때문이다. **한 날짜에
여러 건이 몰리면 이관일을 의심해라**(얌샘 2023-11-23 62건, 우리할매떡볶이
보도자료 12건이 전부 2024-01-04·12 였던 것과 같은 자국).

## 이름을 제목에서 뽑는 규칙 — 쪼개지 않는다

`[신메뉴]` 접두와 꼬리의 `출시` 만 턴다. `직화제육덮밥 & 직화제육면` 처럼
두 상품이 한 글에 들어 있어도 **쪼개지 않는다.** 본문이 이미지 한 장이라
개별 상품명을 확인할 길이 없고, 쪼개면 이름을 지어내게 된다
(슬로우캘리와 같은 처분. `notes/CANDIDATES-BAKERY.md` 의 '시리즈 단위' 참고).
`콜라보 메뉴 3종` 같은 묶음도 그대로 둔다.

## 이미지는 상세에서 한 장씩 가져온다
목록에는 썸네일이 없다. 상세 본문이 이미지 한 장(`/uploaded/webedit/2610/….jpg`)
뿐이라 그걸 쓴다. 담는 글만 상세를 받으므로 요청은 `1 + 담는 글 수` 다.
⚠️ 경로의 `2610` 은 연·월(2026-10)인데 **글 날짜가 바로 옆 목록에 있으므로
파일 경로에서 날짜를 줍지 않는다**(샘표에서 같은 실수를 경고해 뒀다).

`is_new` 는 전부 True — 브랜드가 `[신메뉴]` 라고 붙인 글만 담기 때문이다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "국수나무"
ROOT = "https://www.namuya.co.kr"
LIST = ROOT + "/news/news.php"
DELAY = 2.5
MAX_POSTS = 30   # 폭주 방지. 현재 전체 8건, 담는 건 5건이다.

PREFIX = "[신메뉴]"
_TAG = re.compile(r"^\s*\[[^\]]*\]\s*")
_TAIL = re.compile(r"\s*출시\s*[!！.]*\s*$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _pick(title: str) -> str:
    """제목에서 상품 이름. 접두와 꼬리의 '출시' 만 턴다(위 docstring 참고)."""
    return _TAIL.sub("", _TAG.sub("", title)).strip()


def _image(c, href: str) -> str:
    """상세 본문의 첫 이미지. 목록에는 썸네일이 없다."""
    r = base.retry(lambda: c.get(href))
    r.raise_for_status()
    time.sleep(DELAY)

    for n in HTMLParser(r.text).css("img"):
        src = n.attributes.get("src", "")
        if "/uploaded/" in src:
            return ROOT + src if src.startswith("/") else src
    return ""


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()
        time.sleep(DELAY)

        posts = []
        for a in HTMLParser(r.text).css("a.news-item"):
            tit = a.css_first(".tit")
            dat = a.css_first(".date")
            href = a.attributes.get("href", "")
            if not (tit and dat and href):
                continue
            title = " ".join(tit.text().split())
            date = " ".join(dat.text().split())
            if title.startswith(PREFIX) and _DATE.match(date):
                posts.append((title, date, href))

        for title, date, href in posts[:MAX_POSTS]:
            name = _pick(title)
            if not name:
                continue
            it = Item(
                brand=BRAND,
                name=name,
                desc=_TAG.sub("", title),
                image=_image(c, ROOT + href if href.startswith("/") else href),
                released_at=date,
                is_new=True,     # 브랜드가 '[신메뉴]' 로 올린 글만 담는다
                url=ROOT + href if href.startswith("/") else href,
            )
            if it.key in keys:
                continue
            keys.add(it.key)
            items.append(it)
    return items
