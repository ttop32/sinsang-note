"""삼삼마라 — 아임웹 공지사항 게시판에서 신메뉴와 출시일을 뽑는다.

공정위 `중식` 업종 가맹점 수 **94위**(5개, 2024년 말). 한글 도메인 `삼삼마라.com`
(= `xn--oi2bo7bt0ja.com`). 꼬리 구간인데도 담은 이유는 **신호가 깨끗해서**다 —
브랜드가 직접 쓴 공지에 `[공지] 삼삼마라 신메뉴 ‘바질크림새우’ 출시 안내`
(2026-04-08) 처럼 제목·날짜·본문이 다 갖춰져 있다. 41~99위에서 이런 건 여기뿐이다.

⚠️ **가맹점 5개짜리 브랜드다.** 노출 가치가 낮다고 판단되면 base.BRANDS 에서 빼라.
   어댑터는 그대로 두면 되고, 뺀다고 다른 데가 깨지지 않는다.

수집 경로. 2026-10-02 실측:
  - 아임웹(imweb)이다. 공지 게시판이 `/20` 이고 쿠키 없이 SSR 로 열린다.
    목록 한 줄이 `<ul class="li_body">` 이고 `a.list_text_title span`(제목),
    `li.time`(날짜 `2026-04-08`, title 속성에 시각까지)이 들어 있다.
    현재 44건, 5페이지(10/10/10/10/4). **제목이 안 잘린다.**
  - 상세는 `/20/?bmode=view&idx=<번호>&t=board`.

🔴 **본문은 ‘…’ 가 아니라 `[…]` 로 상품을 부른다.**
   제목: `신메뉴 ‘바질크림새우’ 출시 안내`
   본문: `… 새로운 미식 경험, [바질크림새우]를 드디어 …`
   다른 중식 어댑터(탕화쿵푸·춘리·보배반점·라홍방)는 본문의 ‘…’ 만 봤는데
   여기서는 그러면 0건이 된다. 그래서 **본문 쪽은 ‘…’ 와 […] 둘 다 읽는다.**
   교차검증 원칙(제목에도 같은 이름이 글자 그대로 있어야 채택)은 그대로다.
   ⚠️ 본문에는 `'초록빛 유혹'` 같은 홍보 문구도 따옴표로 들어온다. 제목에 없으니
      교차검증에서 저절로 떨어진다 — 그게 이 규칙을 쓰는 이유다.

⚠️ **이미지는 `.board_view` 안에서만 집는다.** 상세의 `<img>` 는 12개인데
   그중 11개가 사이트 공통 이미지(`cdn.imweb.me/thumbnail/…` 네비 로고,
   창업절차 아이콘)다. 문서 전체에서 첫 https 이미지를 집으면 로고가 붙는다.
   글 본문 컨테이너 `.board_view` 로 좁히면 글에 딸린 사진 1장만 남는다
   (실측: `cdn.imweb.me/upload/S2023111450954400f023a/6b174ea224c0a.jpg`).

신제품 판정 근거는 **공지 자체**다. 브랜드가 '신메뉴 … 출시' 라고 쓴 글이라
is_new=True 로 둔다. 날짜는 게시판 등록일이라 released_at 에 넣는다.

수집량은 **연 2건**이다(2026-09-10 치즈 분모자, 2026-04-08 바질크림새우).
36건 중 나머지는 위생검사 결과·운영시간 변경·매장 오픈 공지라 상품이 아니다.

robots: `삼삼마라.com/robots.txt` → 200, text/plain. 아임웹 공통 규칙이다.
        `User-agent: *` / `Allow: /` 에 `/site_join`·`/login`·`/shop_cart`·
        `/?mode*`·`/admin` 만 Disallow. 우리가 쓰는 `/20` 은 허용이다.
        ⚠️ `/?mode*` 는 파이썬 robotparser 가 못 읽는 패턴이다(쿼리 와일드카드를
        quote 해버린다). 우리는 그 경로를 안 쓰니 문제되지 않는다.
약관: 게시판 아래에 개인정보처리방침이 길게 붙어 있다. 수집·복제를 금지하는
      이용약관은 찾지 못했다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "삼삼마라"
SITE = "https://xn--oi2bo7bt0ja.com"     # 삼삼마라.com
BOARD = SITE + "/20"
MAX_PAGES = 2        # 한 페이지 10건. 2페이지면 1년 반쯤 된다
DAYS = 540           # 중식은 신메뉴가 연 1~4건이라 300일이면 브랜드 페이지가 빈다.
                     # 화면 노출은 rules.WINDOW(60일)가 따로 자르므로 넓혀도
                     # '오래된 게 신상으로 뜨는' 일은 없다(짬뽕관 어댑터와 맞췄다).
DELAY = 2.2

_LAUNCH = re.compile(r"(출시|선봬|선보|론칭|신메뉴|신제품)")

# 상품 공지가 아닌데 위 동사를 쓰는 것들.
_SKIP = ("운영시간", "불검출", "위생", "휴무", "오픈", "채용", "이벤트", "점검")

# 본문은 ‘…’ 와 […] 를 섞어 쓴다(docstring 참고). 제목은 ‘…’ 만 쓴다.
_QUOTED = re.compile(r"[‘'`\[]([^’'`\[\]\n]{2,30})[’'`\]]")

_NOT_PRODUCT = ("삼삼마라", "공지", "브랜드", "프랜차이즈", "본점", "매장", "이벤트")


def _text(node) -> str:
    return " ".join(node.text().split()) if node else ""


def _date(s: str) -> str:
    m = re.search(r"(20\d{2})-(\d{1,2})-(\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    return f"{y:04d}-{mo:02d}-{d:02d}" if 1 <= mo <= 12 and 1 <= d <= 31 else ""


def _rows(html: str) -> list:
    """목록 한 페이지 → [(날짜, 글번호, 제목)]."""
    out = []
    for ul in HTMLParser(html).css("ul.li_body"):
        a = ul.css_first("a.list_text_title")
        if not a:
            continue
        m = re.search(r"idx=(\d+)", a.attributes.get("href", ""))
        title = _text(a)
        when = _date(_text(ul.css_first("li.time")))
        if m and title and when:
            out.append((when, m.group(1), title))
    return out


def _image(doc) -> str:
    """글 본문(.board_view) 안의 첫 이미지. 사이트 공통 이미지를 피한다."""
    for n in doc.css(".board_view img"):
        src = n.attributes.get("src") or n.attributes.get("data-src") or ""
        if src.startswith("https://"):
            return src
    return ""


def _names(title: str, body: str) -> list:
    """제목과 본문을 교차검증해 상품명을 뽑는다. 못 고르면 빈 목록."""
    t = " ".join(title.split()).replace("[공지]", " ")
    if any(w in t for w in _SKIP) or not _LAUNCH.search(t):
        return []
    flat = t.replace(" ", "")
    out, seen = [], set()
    for m in _QUOTED.finditer(body):
        name = m.group(1).strip(" ,·∙")
        if len(name) < 2 or any(c in name for c in "·∙&?"):
            continue
        if any(w in name for w in _NOT_PRODUCT):
            continue
        if name.replace(" ", "") not in flat or name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    cand = []
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(BOARD, params={"page": page}))
            r.raise_for_status()
            rows = _rows(r.text)
            # 1페이지가 비면 마크업이 바뀐 것이다. 조용히 빈 목록을 돌려주지 않는다.
            if not rows:
                if page == 1:
                    raise RuntimeError(f"{BOARD} 1페이지에서 글을 못 찾았다. 마크업을 확인해라")
                break
            for when, idx, title in rows:
                if when < floor:
                    continue
                flat = title.replace("[공지]", " ")
                if any(w in flat for w in _SKIP) or not _LAUNCH.search(flat):
                    continue
                cand.append((when, idx, title))

        items: list[Item] = []
        seen = set()
        for when, idx, title in cand:
            time.sleep(DELAY)
            url = f"{BOARD}/?bmode=view&idx={idx}&t=board"
            r = base.retry(lambda: c.get(url))
            r.raise_for_status()
            doc = HTMLParser(r.text)
            for s in doc.css("script,style"):
                s.decompose()
            body = " ".join(doc.text().split())
            img = _image(doc)
            for name in _names(title, body):
                it = Item(brand=BRAND, name=name, image=img,
                          released_at=when, is_new=True, url=url)
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
    return items
