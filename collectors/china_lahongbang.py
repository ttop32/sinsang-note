"""라홍방마라탕 — 그누보드 '언론 기사' 게시판에서 신메뉴와 출시일을 뽑는다.

공정위 `중식` 업종 가맹점 수 **8위**(129개, 2024년 말). (주)라홍에프앤비.

**메뉴 페이지는 쓸 수 없다.** `/page.php?p_id=menu` 는 마라탕에 넣는 재료와 상시
메뉴를 이미지로 깔아놓은 한 장짜리 페이지다. NEW 배지도 날짜도 없다. 탕화쿵푸·
춘리마라탕과 같은 사정이다 — 마라탕집 메뉴판은 재료 바구니라 카탈로그가 아니다.

남은 경로는 보도자료고, 이건 GS25·오뚜기·오리온과 **같은 종류의 소스**다.

수집 경로. 2026-10-02 실측:
  - 그누보드5다. 게시판 4개 중 `news`(언론 기사, 134건)만 쓴다.
    `notice`(공지사항)·`promotion`(프로모션)·`franchise`(매장안내)는 각각
    창업 안내·할인 행사·지점 목록이라 상품이 없다.
  - 목록 `/bbs/board.php?bo_table=news&page=N`. SSR 이고 **제목이 안 잘린다**.\n    ⚠️ **페이징이 사실상 없다** — 1페이지에 134건이 전부 들어오고 `page=2` 는\n    0건이다. MAX_PAGES 는 글이 늘어나 페이징이 켜질 때를 대비한 상한일 뿐이다.
  - ⚠️ **목록의 날짜가 `06-17` 처럼 월·일뿐이다.** 그누보드가 올해 글은 연도를
    떼고 보여준다. 연도를 추측해 채우면 안 되므로 **상세의 `작성일 26-06-17 10:07`**
    을 쓴다. 상세는 어차피 교차검증 때문에 받는다.
  - `/bbs/rss.php?bo_table=news` 는 **"RSS 보기가 금지되어 있습니다"**(18바이트)다.
    관리자가 꺼둔 것이라 목록 HTML 말고는 길이 없다.

신제품 판정 근거는 **기사 자체**다. 브랜드가 '신메뉴 … 출시' 라고 낸 글이라
is_new=True 로 둔다(GS25·오뚜기·오리온과 같은 근거).

상품명은 제목·본문을 **교차검증**해서만 뽑는다(탕화쿵푸·춘리·보배반점과 같은 규칙).
  ① 본문에서 ‘…’ 로 인용된 이름을 모으고
  ② 그중 **제목에도 글자 그대로 있는 것만** 채택한다.
이 게시판은 134건 중 **100건 넘게 매장 오픈 기사**다("완도점 개점", "도쿄 기치죠지점
신규 오픈"). 따옴표 안이 '인계점'·'기치죠지점'·'2026 창업 프로모션' 같은 비상품이라
교차검증이 꼭 필요하다. 지점명은 _NOT_PRODUCT 의 '점' 으로도 한 번 더 걸린다.

⚠️ **같은 제품 기사가 여러 매체로 중복 등재된다.** 고래사어묵 협업 HMR '마라탕
   한그릇' 은 05-12 / 05-20 / 05-29 / 06-08 네 번 올라온다. base.make_key() 가
   이름으로 묶지만 어댑터에서도 한 번 더 턴다. **가장 오래된 날짜가 남게** 목록을
   뒤에서부터(=오래된 쪽부터) 담는다 — 출시일은 첫 보도 날짜가 맞다.
⚠️ '마라탕 한그릇' 은 매장 메뉴가 아니라 고래사어묵과 함께 낸 HMR 이다. 보배반점
   '크림짬뽕' 과 같은 성격이고, 같은 이유로 담는다(그쪽 docstring 참고).

robots: `www.lahongbang.com/robots.txt` → 200, text/plain.
        `User-agent: *` / `Allow: /` / `Disallow: /adm/` / `Disallow: /install/`.
        우리가 쓰는 `/bbs/board.php` 는 **허용**이다.
약관: 푸터에 개인정보처리방침만 있고 **이용약관 페이지가 없다**. 수집·복제를
      금지하는 문구는 찾지 못했다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "라홍방마라탕"
SITE = "https://www.lahongbang.com"
LIST = SITE + "/bbs/board.php"
BO_TABLE = "news"
MAX_PAGES = 3        # 지금은 1페이지에 134건이 다 온다(위 docstring 참고).\n                     # 페이징이 켜질 때를 대비한 상한이다.
DAYS = 540           # 중식은 신메뉴가 연 1~4건이라 300일이면 브랜드 페이지가 빈다.
                     # 화면 노출은 rules.WINDOW(60일)가 따로 자르므로 넓혀도
                     # '오래된 게 신상으로 뜨는' 일은 없다(짬뽕관 어댑터와 맞췄다).
DELAY = 2.2

# 상품 기사인가. 이 말이 없으면 상세를 받지 않는다.
_LAUNCH = re.compile(r"(출시|선봬|선보|론칭|신메뉴|신제품)")

# 상품 기사가 아닌데 위 동사를 쓰는 것들. 실측 제목 134건으로 뽑았다.
_SKIP = ("오픈", "개점", "진출", "확대", "박람회", "성료", "상담", "프로모션",
         "할인", "기부", "봉사", "나눔", "대출", "지원", "수상", "선정", "성료")

_QUOTED = re.compile(r"[‘'`]([^’'`\n]{2,40})[’'`]")

# 따옴표 안이 상품이 아닌 것들. '점' 이 지점명을 통째로 잡는다.
#
# ⚠️ **브랜드명 자체가 따옴표 안에 들어온다.** 기사가 "마라탕 프랜차이즈
#    '라홍방마라탕'이 …" 라고 쓰고, 제목에도 브랜드명이 있으니 교차검증을 그대로
#    통과한다(실측: '라홍방마라탕' 이 상품으로 올라왔다). 브랜드명을 넣어 막는다.
# ⚠️ 협업 제품은 본문이 두 이름을 ' x ' 로 이어 부른다 —
#    '고래사 x 라홍방 마라탕 한그릇'. 같은 제품의 다른 표기라 중복이 되므로
#    협업 접두가 붙은 쪽을 버리고 짧은 쪽('마라탕 한그릇')만 남긴다.
_NOT_PRODUCT = ("프로모션", "브랜드", "프랜차이즈", "박람회", "이벤트",
                "캠페인", "협약", "지원", "라홍방", "라홍")

# 지점명. `"점"` 을 _NOT_PRODUCT 에 넣으면 부분일치라 '점보마라탕'·'점보만두'
# 같은 실존 작명을 죽인다(라화쿵부가 실제로 '3KG 점보마라탕' 을 판다).
# 지점명은 항상 '…점' 으로 **끝나므로** 끝자리로만 본다.
_BRANCH = re.compile(r"점$")

_COLLAB = re.compile(r"\s[xX×]\s")

# 상세의 작성일. 그누보드는 두 자리 연도로 쓴다 — '26-06-17 10:07'.
_WROTE = re.compile(r"작성일\s*(\d{2})-(\d{2})-(\d{2})")


def _text(node) -> str:
    return " ".join(node.text().split()) if node else ""


def _date(s: str) -> str:
    """'2026-06-17' → 같은 문자열. 월·일 범위를 검증한다.

    그누보드가 두 자리 연도만 주는 자리라(`작성일 26-06-17`) 우리가 `20` 을 붙여
    만든다. 그 값이 `2099-99-99` 같은 쓰레기여도 그대로 released_at 에 들어가면
    정렬과 60일 창 판정이 통째로 깨진다. 다른 중식 어댑터와 같은 검증을 건다.
    """
    m = re.search(r"(20\d{2})-(\d{1,2})-(\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    return f"{y:04d}-{mo:02d}-{d:02d}" if 1 <= mo <= 12 and 1 <= d <= 31 else ""


def _rows(html: str) -> list:
    """목록 한 페이지 → [(wr_id, 제목)]. 날짜는 월·일뿐이라 여기서 안 읽는다."""
    out = []
    for tr in HTMLParser(html).css("tr"):
        a = tr.css_first(".bo_tit a")
        if not a:
            continue
        m = re.search(r"wr_id=(\d+)", a.attributes.get("href", ""))
        title = _text(a)
        if m and title:
            out.append((m.group(1), title))
    return out


def _names(title: str, body: str) -> list:
    """제목과 본문을 교차검증해 상품명을 뽑는다. 못 고르면 빈 목록."""
    t = " ".join(title.split())
    if any(w in t for w in _SKIP) or not _LAUNCH.search(t):
        return []
    flat = t.replace(" ", "")
    out, seen = [], set()
    for m in _QUOTED.finditer(body):
        name = m.group(1).strip(" ,·∙")
        # 협업 제품은 본문이 '고래사 x 라홍방 마라탕 한그릇' 처럼 길게 부른다.
        # 두 상품을 '·' 로 묶은 것과 구분이 안 되므로 묶음 기호가 있으면 버린다.
        if len(name) < 2 or any(c in name for c in "·∙&?") or _COLLAB.search(name):
            continue
        if any(w in name for w in _NOT_PRODUCT) or _BRANCH.search(name):
            continue
        if name.replace(" ", "") not in flat or name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def _image(doc) -> str:
    """본문 이미지. 그누보드 에디터가 올린 /data/editor/ 만 쓴다."""
    for n in doc.css("img"):
        src = n.attributes.get("src", "")
        if src.startswith("https://") and "/data/editor/" in src:
            return src
    return ""


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    cand = []
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"bo_table": BO_TABLE,
                                                       "page": page}))
            r.raise_for_status()
            rows = _rows(r.text)
            # 1페이지가 비면 마크업이 바뀐 것이다. 조용히 빈 목록을 돌려주지 않는다.
            if not rows:
                if page == 1:
                    raise RuntimeError(f"{LIST} 1페이지에서 글을 못 찾았다. 마크업을 확인해라")
                break
            for wr_id, title in rows:
                if any(w in title for w in _SKIP) or not _LAUNCH.search(title):
                    continue
                cand.append((wr_id, title))

        # 같은 제품이 여러 날짜로 중복 등재된다. 오래된 글(=작은 wr_id)부터 담아
        # 첫 보도 날짜가 released_at 으로 남게 한다(docstring 참고).
        cand.sort(key=lambda x: int(x[0]))

        items: list[Item] = []
        seen = set()
        for wr_id, title in cand:
            time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"bo_table": BO_TABLE,
                                                       "wr_id": wr_id}))
            r.raise_for_status()
            doc = HTMLParser(r.text)
            for s in doc.css("script,style"):
                s.decompose()
            body = " ".join(doc.text().split())
            m = _WROTE.search(body)
            if not m:
                continue
            when = _date(f"20{m.group(1)}-{m.group(2)}-{m.group(3)}")
            if not when:
                continue
            if when < floor:
                continue
            img = _image(doc)
            url = f"{LIST}?bo_table={BO_TABLE}&wr_id={wr_id}"
            for name in _names(title, body):
                it = Item(brand=BRAND, name=name, image=img,
                          released_at=when, is_new=True, url=url)
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
    return items
