"""탕화쿵푸마라탕 — 보도자료(NEWS 게시판)에서 신메뉴와 출시일을 뽑는다.

공정위 `중식` 업종 가맹점 수 **1위**(492개, 2024년 말). 한국탕화쿵푸(주).

**메뉴 페이지는 쓸 수 없다.** `/default/brand/menu/menu.php` 를 받아 보면 2026-10-02
현재 상품이 아니라 **마라탕에 넣는 재료 72종**이 나온다("고구마 당면 / 넓적옥수수면 /
청경채 / 팽이버섯 …"). 마라탕집은 '상품'이라는 단위가 재료 바구니라 메뉴판이 곧
카탈로그가 아니다. 날짜도 NEW 배지도 없다. 긁으면 재료 72개가 전부 '신상' 으로
올라간다 — 이 서비스에서 제일 하면 안 되는 짓이다. 그래서 메뉴 페이지는 안 본다.

남은 경로는 보도자료 하나뿐이고, 이건 GS25·오뚜기·오리온과 **같은 종류의 소스**다.
그 셋의 규칙을 그대로 가져와 이 사이트의 버릇에 맞게 조인다.

수집 경로. 2026-10-02 실측:
  - NEWS 목록 `/default/brand/tidings/news.php?com_board_id=13&com_board_page=N`.
    쿠키·토큰 없이 SSR 로 열린다. 한 페이지 5건, 9페이지(=45건, 2024-09~).
  - **인코딩이 EUC-KR 이다.** 헤더가 charset 을 안 주고 httpx 는 utf-8 로 읽어서
    제목이 통째로 깨진다(`��ȭ��Ǫ`). `r.content.decode("euc-kr")` 로 직접 벗긴다.
  - 목록 한 줄이 `<dl>` 이고 `dd.webzine_subject` / `webzine_description` /
    `webzine_dateof_write` 가 각각 제목·본문요약·작성일자다.
  - ⚠️ **목록 제목은 30자쯤에서 `..` 로 잘린다.** 실측:
      `탕화쿵푸마라탕, 크림새우·연근완자튀김·연근후라이..`
    상품명이 잘려 나가므로 목록만으로는 상품명을 못 뽑는다(오리온과 같은 함정).
    그래서 후보만 목록에서 고르고 **상세를 받아 온전한 제목**을 쓴다.
    상세는 `?com_board_basic=read_form&com_board_idx=NN&com_board_id=13`.

공지사항 게시판(`/default/brand/tidings/board.php`)도 받아 봤다. **글이 1건**이고
그 1건이 "홈페이지가 새롭게 개편되었습니다"(2025-06-12)다. 상품 신호가 없어 안 본다.

신제품 판정 근거는 '배지'가 아니라 **기사 자체**다. 브랜드가 '출시·선보였다'고 낸
기사라서 is_new=True 로 둔다(GS25·오뚜기·오리온과 같은 근거).

**상품명은 제목과 본문을 교차검증해서만 뽑는다.** 이 사이트 고유의 사정이 있다 —
한 기사가 상품 여럿을 묶어 낸다. 실측:
  제목 `탕화쿵푸마라탕, 크림새우·연근완자튀김·연근후라이 사이드 메뉴 3종 출시`
  본문 `‘크림새우’는 … ‘연근완자튀김’은 … ‘연근후라이’는 …`
오리온·오뚜기는 `\\d+종` 을 만나면 통째로 버리는데(제목만으로는 상품을 못 가르니까),
여기서는 **본문이 상품마다 ‘…’ 로 이름을 따로 불러준다.** 그래서
  ① 본문에서 ‘…’ 로 인용된 이름을 모으고
  ② 그중 **제목에도 글자 그대로 들어 있는 것만** 상품으로 채택한다
는 2중 검증을 쓴다. 한쪽에만 있는 건 버린다 — 본문 인용에는 ‘지구의 날’·‘루미네스’
같은 행사명이 섞이고, 제목 인용에는 ‘가맹하고 싶은 프랜차이즈’ 같은 평가명이 섞인다.
둘 다 통과하는 건 2026-10-02 기준 사이드 3종뿐이었고, 전건 본문을 눈으로 읽어
실제로 그 상품을 가리키는지 확인했다(오집 0건).

수집량은 적다. 45건 중 상품 기사는 **연 2건 안팎**이다(사이드 3종 2026-08-03,
요거트월드 협업 만우절 한정 메뉴 2026-04-01). 나머지는 전부 매장 오픈·축제 스폰서·
봉사활동·창업박람회·MOU 다. 그래도 날짜가 정확하고 브랜드가 직접 '출시'라고 말한
건이라 신뢰도는 높다. 가맹점 492개짜리 1위 브랜드를 아예 비워두는 것보다 낫다.

🔴 **이 사이트는 Cafe24 일일 트래픽 한도에 자주 걸린다.** 한도를 넘기면 상태코드
   **200** 으로 "Access is temporarily restricted" 안내 페이지가 온다(15KB).
   `_get()` 이 그걸 잡아 전용 메시지로 터뜨린다 — 자세한 건 그 docstring 참고.

robots: `tanghuokungfu.co.kr/robots.txt` → **404 인데 본문이 HTML** 이다(사이트
        공통 오류 페이지). 파일이 없는 것이므로 제한은 없다. 단 허용도 아니라서
        요청 간격을 2.5초로 길게 잡는다(죠스떡볶이 선례).
약관: 푸터에 개인정보처리방침·이메일무단수집거부만 있고 **이용약관 페이지가 없다**.
      수집·복제를 금지하는 문구는 찾지 못했다(스시로와 같은 칸).
⚠️ 기사 이미지는 원 매체 CDN(`cdn.e2news.com/news/photo/...`)을 그대로 가리킨다.
   브랜드 서버가 아니라 언론사 서버라 깨질 수 있다. https 인 것만 담는다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "탕화쿵푸마라탕"
SITE = "https://tanghuokungfu.co.kr"
NEWS = SITE + "/default/brand/tidings/news.php"
BOARD_ID = "13"      # NEWS 게시판. 공지사항은 다른 php 파일이라 id 를 안 쓴다
# 한 페이지 5건, 전체 9페이지(45건). DAYS(540일)를 덮으려면 4페이지로는 모자란다
# — 월 1.8건 꼴이라 20건이면 1년이 안 된다. 전체가 45건뿐이라 다 받아도 9요청이다.
# ⚠️ 좁게 잡으면 `when < floor` 전에 루프가 끝나 **경고 없이** 창 안 글을 놓친다.
MAX_PAGES = 9
DAYS = 540           # 중식은 신메뉴가 연 1~4건이라 300일이면 브랜드 페이지가 빈다.
                     # 화면 노출은 rules.WINDOW(60일)가 따로 자르므로 넓혀도
                     # '오래된 게 신상으로 뜨는' 일은 없다(짬뽕관 어댑터와 맞췄다).
DELAY = 2.5          # robots.txt 가 없다. 허용도 금지도 아니니 간격을 길게 잡는다

# Cafe24 일일 트래픽 한도 차단 페이지의 표식. 상태코드가 200 이라 본문으로만 안다.
# 한글이 EUC-KR 로 깨져 오는 자리라 영문 문장을 쓴다(그쪽은 안 깨진다).
_BLOCKED = "Access is temporarily restricted"

# 목록 단계 1차 거르기. 잘린 제목·요약에서도 판정이 안 뒤집히는 말만 넣는다.
# 본판정은 상세의 온전한 제목으로 _names() 가 한다.
_PRESCREEN = ("봉사활동", "기부", "장학", "스폰서", "박람회", "MOU", "업무협약",
              "직영점 오픈", "성료", "채용", "매출", "주주총회")

# 상품 기사인가. 이 말이 없으면 상세를 받지 않는다.
_LAUNCH = re.compile(r"(출시|선봬|선보|론칭|신메뉴|한정 ?메뉴|새롭게)")

# 상품 기사가 아닌데 위 동사를 쓰는 것들. 오리온 _SKIP 과 같은 취지다.
_SKIP = ("가맹하고 싶은", "프랜차이즈 평가", "상위 3%", "착한가게", "세스코",
         "창업박람회", "이벤트 성료", "조감도", "청소년 전용", "금융 서비스")

# 본문·제목의 홑따옴표. 한국 기사는 ‘ ’ 와 ' 를 섞어 쓴다.
_QUOTED = re.compile(r"[‘'`]([^’'`\n]{2,30})[’'`]")

# 따옴표 안이 상품이 아닌 것들. 본문 인용에 섞여 들어온다.
_NOT_PRODUCT = ("축제", "대동제", "지구의 날", "데이", "이벤트", "캠페인", "협약",
                "프랜차이즈", "브랜드", "기념", "서비스", "보너스", "마을")

# 지점명. `"점"` 을 _NOT_PRODUCT 에 넣으면 부분일치라 '점보마라탕'·'점보만두'
# 같은 실존 작명을 죽인다(라화쿵부가 실제로 '3KG 점보마라탕' 을 판다).
# 지점명은 항상 '…점' 으로 **끝나므로** 끝자리로만 본다.
_BRANCH = re.compile(r"점$")


def _text(node) -> str:
    return " ".join(node.text().split()) if node else ""


def _date(s: str) -> str:
    """'2026-08-03' → 같은 문자열. 월·일 범위를 검증한다."""
    m = re.search(r"(20\d{2})-(\d{1,2})-(\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _get(c, params: dict) -> str:
    """EUC-KR 페이지를 받아 문자열로. 헤더가 charset 을 안 줘서 직접 벗긴다.

    🔴 **일일 트래픽 한도 차단을 여기서 잡는다.** 이 사이트는 Cafe24 호스팅이고
    한도를 넘기면 **상태코드 200 으로** 차단 안내 페이지를 돌려준다
    ("This site is currently unavailable" / "Access is temporarily restricted.
    Please try again shortly, or from tomorrow onward"). 15KB 짜리라 크기로도
    구분이 안 되고, raise_for_status() 로도 안 걸린다. 그대로 두면 파싱이 0행을
    내놓고 "마크업이 바뀌었다"는 엉뚱한 메시지가 뜬다 — 2026-10-02 실제로 그랬다.
    (`notes/CANDIDATES-WESTERN.md` 가 2026-09-30 에 이 브랜드를 '확인 못 함' 으로
     남긴 것도 같은 차단이었다. 같은 함정에 두 번 걸린 셈이다.)

    사유가 다르면 대응도 다르다 — 마크업 변경은 코드를 고쳐야 하고, 트래픽 차단은
    내일 다시 돌리면 된다. 그래서 메시지를 갈라 둔다. collect 는 어느 쪽이든
    이 브랜드만 실패로 두고 이전 수집분을 유지한다.
    """
    r = base.retry(lambda: c.get(NEWS, params=params))
    r.raise_for_status()
    html = r.content.decode("euc-kr", "replace")
    if _BLOCKED in html:
        raise RuntimeError(
            "탕화쿵푸: Cafe24 일일 트래픽 한도에 걸렸다(200 으로 차단 안내가 온다). "
            "마크업 문제가 아니다. 내일 다시 돌려라")
    return html


def _rows(html: str) -> list:
    """목록 한 페이지 → [(작성일, 글번호, 잘린제목, 본문요약)]."""
    out = []
    for dl in HTMLParser(html).css("dl"):
        title = _text(dl.css_first("dd.webzine_subject .obj_value"))
        when = _date(_text(dl.css_first("dd.webzine_dateof_write .obj_value")))
        desc = _text(dl.css_first("dd.webzine_description .obj_value"))
        a = dl.css_first("a")
        idx = re.search(r"com_board_idx=(\d+)", a.attributes.get("href", "")) if a else None
        if title and when and idx:
            out.append((when, idx.group(1), title, desc))
    return out


def _names(title: str, body: str) -> list:
    """제목과 본문을 교차검증해 상품명을 뽑는다. 못 고르면 빈 목록.

    본문이 ‘…’ 로 부른 이름 중 **제목에도 글자 그대로 있는 것**만 남긴다.
    한쪽에만 있는 건 행사명·평가명이라 버린다(docstring 참고).
    """
    t = " ".join(title.split())
    if any(w in t for w in _SKIP) or not _LAUNCH.search(t):
        return []
    flat = t.replace(" ", "")
    out, seen = [], set()
    for m in _QUOTED.finditer(body):
        name = m.group(1).strip(" ,·∙")
        # 두 상품을 '·' 로 묶은 한 덩어리는 버린다. 본문이 각각을 따로 부르므로
        # 개별 상품은 이 반복에서 따로 잡힌다(보배반점에서 실제로 터진 오집이다).
        if len(name) < 2 or any(ch in name for ch in "·∙&?"):
            continue
        if any(w in name for w in _NOT_PRODUCT) or _BRANCH.search(name):
            continue
        if name.replace(" ", "") not in flat:   # 제목이 같은 이름을 부르지 않으면 버린다
            continue
        if name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def _image(doc) -> str:
    """기사 본문 이미지.

    ⚠️ 문서 전체에서 첫 https 이미지를 집으면 안 된다. 지금은 사이트 UI 가 전부
    `/default/img/...`·`/bizdemo.../img/...` 라 우연히 비껴가지만, 레이아웃이
    바뀌면 로고가 상품 사진으로 붙는다. 그래서 **본문 영역으로 먼저 좁히고**
    (`dd.webzine_description` 안이 기사 본문이다) 거기서 못 찾을 때만 문서
    전체를 보되, 경로에 `/img/` 가 든 사이트 이미지는 계속 뺀다.
    다른 중식 어댑터도 전부 본문 컨테이너로 좁힌다(삼삼마라 `.board_view`,
    미미관 `.board_txt_area`, 라홍방 `/data/editor/`).
    """
    for scope in ("dd.webzine_description img", "img"):
        for n in doc.css(scope):
            src = n.attributes.get("src", "")
            if src.startswith("https://") and "/img/" not in src:
                return src
    return ""


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    cand, stop = [], False
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            rows = _rows(_get(c, {"com_board_id": BOARD_ID, "com_board_page": page}))
            # 1페이지가 비면 마크업이 바뀐 것이다. 조용히 빈 목록을 돌려주지 않는다.
            if not rows:
                if page == 1:
                    raise RuntimeError(f"{NEWS} 1페이지에서 글을 못 찾았다. 마크업을 확인해라")
                break
            for when, idx, short, desc in rows:
                if when < floor:
                    stop = True
                    continue
                if any(w in short or w in desc for w in _PRESCREEN):
                    continue
                if not _LAUNCH.search(short + " " + desc):
                    continue
                cand.append((when, idx))
            if stop:
                break

        items: list[Item] = []
        seen = set()
        for when, idx in cand:
            time.sleep(DELAY)
            html = _get(c, {"com_board_id": BOARD_ID,
                            "com_board_basic": "read_form", "com_board_idx": idx})
            doc = HTMLParser(html)
            for s in doc.css("script,style"):
                s.decompose()
            body = " ".join(doc.text().split())
            # 상세의 온전한 제목. '제목' 라벨 다음 '작성자' 앞까지가 제목이다.
            m = re.search(r"제목\s+(.+?)\s+작성자", body)
            if not m:
                continue
            title = m.group(1)
            img = _image(doc)
            url = f"{NEWS}?com_board_basic=read_form&com_board_idx={idx}&com_board_id={BOARD_ID}"
            for name in _names(title, body):
                it = Item(brand=BRAND, name=name, image=img,
                          category="사이드" if "사이드" in title else "",
                          released_at=when, is_new=True, url=url)
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
    return items
