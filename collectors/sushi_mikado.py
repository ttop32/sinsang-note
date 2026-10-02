"""미카도스시(올바른에프앤비) — 메뉴 게시판의 등록일과 '신메뉴' 본문.

www.mikadosushi.co.kr 은 그누보드다. 메뉴가 갤러리 게시판(bo_table=menu) 한 개에
들어 있고 상품 1건이 글 1건이다. 쿠키·세션 없이 열리고 브라우저도 필요 없다.
(mikadosushi.kr 도 같은 회사 도메인인데 그쪽은 창업 랜딩 한 장이라 상품이 없다.
 본문 링크가 전부 인스타그램·네이버로 나간다. 그래서 .co.kr 을 쓴다.)

2026-10-02 실측, 전량 98건:
  - 목록 `?bo_table=menu` 는 페이지당 16건, 7페이지. `sca=` 로 6개 분류
    (초밥·롤군함·튀김우동·디저트·곁들임·포장배달)로도 나뉘지만 **합이 63건이라
    분류가 안 붙은 글이 35건 있다.** 그래서 분류를 돌지 않고 sca 없이 전량을 받는다.
  - `sst=wr_datetime&sod=desc` 가 먹는다. 최신순으로 받아 오래된 글이 나오면
    끊을 수 있어서 상세 요청이 98번에서 30번 아래로 준다.
  - **목록에는 날짜가 없다.** 날짜·본문은 상세(`&wr_id=`)에만 있다.
  - RSS(`/bbs/rss.php?bo_table=menu`)는 "RSS 보기가 금지되어 있습니다" 를 돌려줘
    못 쓴다. 날짜를 싸게 긁는 길이 없어 상세를 하나씩 받는 수밖에 없다.

신제품 신호:
  is_new   **상세 본문이 "2025년 12월 신메뉴" 라고 직접 말한다.** 이게 이 브랜드의
           유일한 신제품 신호다. 2026-10-02 기준 7건(wr_id 135~141)이 여기 걸리고
           전부 등록일이 2025-11-04 로 같다. 신호가 가짜가 아닌지 교차검증했다 —
           그 7건은 **최신순 정렬에서도 맨 앞 7건**이라 날짜와 본문이 서로를
           뒷받침한다. 본문에 '신메뉴'가 없는 나머지 91건은 본문이 상품명을 그대로
           반복할 뿐이라(`계란마요구이` → "계란마요구이") 아무 말도 안 하는 것이다.
           그래서 False 로 뒤집지 않고 None 으로 둔다(피자헛·이삭토스트와 같은 선).
  released_at  **비운다.** 위 7건의 본문은 "2025년 12월 신메뉴"라 **달**만 말하고
           등록일은 2025-11-04 다. 즉 등록일은 출시보다 한 달 앞선 값이고, 달만
           있는 쪽은 날짜를 지어내야 쓸 수 있다. 둘 다 출시일이 아니라서 비운다.
  uploaded_at  게시글 등록일(`#bo_v_info .if_date` 의 `작성일:25-11-04`)을 담는다.
           ⚠️ 등록일이 곧 출시일인 게시판이 아니다. 2025-09-23~25 사흘에 20건이
           몰려 있는데(wr_id 115~134) 이건 사이트 개편 때 메뉴를 다시 올린
           흔적이다 — 그 20건은 `광어초밥`·`연어초밥` 같은 상설 메뉴다.
           본아이에프와 같은 이유로 released_at 이 아니라 uploaded_at 에 둔다.

**그래서 이 어댑터가 '신상'이라고 말하는 건 is_new=True 7건뿐이다.** 그 7건은
2025-11-04 등록분이라 지금(2026-10-02) 기준으로 11개월 됐다. 화면에 오르지
않는 게 정상이고, 다음 신메뉴가 올라오면 그때 잡힌다.

가격은 사이트 어디에도 없다. name_en 자리에 쓸 영문명도 없다(목록의 `<p>` 는
전건 `MIKADO SUSHI` 라는 고정 문구다).

robots.txt: `User-agent: *` / `Allow: /` — 전면 허용.
약관: 사이트에 약관·법적고지 페이지 자체가 없다(2026-10-02 실측, 푸터는
      사업자정보와 /adm 링크뿐).
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "미카도스시"
SITE = "https://www.mikadosushi.co.kr"
LIST = SITE + "/bbs/board.php"
BO = "menu"
PAGE_SIZE = 16
MAX_PAGES = 10     # 폭주 방지. 현재 7페이지.
# 이 일수보다 오래된 글이 나오면 멈춘다. 최신순 정렬이라 그 뒤는 더 오래됐다.
# 400 으로 둔 근거: 실측 경계가 2025-09-23(≈374일) 다음이 2022-10-17 로 뚝
# 떨어진다. 2025년분은 전부 받고 2022년 뭉치는 건드리지 않는 자리다.
DAYS = 400
DELAY = 1.2

# 본문이 신제품이라고 말하는 표현. '2025년 12월 신메뉴 계란마요구이' 꼴이다.
_SAYS_NEW = re.compile(r"신메뉴|신상품|신제품")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _uploaded_at(s: str) -> str:
    """'작성일:25-11-04' → '2025-11-04'. 날짜로 안 읽히면 빈 문자열."""
    m = re.search(r"(\d{2})-(\d{2})-(\d{2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"20{y:02d}-{mo:02d}-{d:02d}"


def _ids(html: str) -> list:
    """목록에서 (wr_id, 상품명). 최신순 정렬된 순서를 그대로 지킨다."""
    out = []
    for li in HTMLParser(html).css("#gall_ul > li"):
        a = li.css_first("a.bo_tit")
        if not a:
            continue
        m = re.search(r"wr_id=(\d+)", a.attributes.get("href", ""))
        name = a.css_first("strong")
        if m and name:
            out.append((m.group(1), _clean(name.text())))
    return out


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    items: list[Item] = []
    seen_id, seen_key = set(), set()
    stop = False
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if stop:
                break
            r = base.retry(lambda: c.get(LIST, params={
                "bo_table": BO, "sst": "wr_datetime", "sod": "desc", "page": page}))
            r.raise_for_status()
            rows = _ids(r.text)
            if not rows:
                if page == 1:
                    raise RuntimeError("미카도스시 메뉴 게시판: 0건 — 셀렉터가 깨졌을 수 있다")
                break
            # 범위를 넘긴 page 가 1페이지를 되돌려주는 게시판이 흔하다(메가 선례).
            if all(w in seen_id for w, _ in rows):
                break
            time.sleep(DELAY)

            for wid, listed in rows:
                if wid in seen_id:
                    continue
                seen_id.add(wid)
                d = base.retry(lambda: c.get(LIST, params={"bo_table": BO, "wr_id": wid}))
                d.raise_for_status()
                time.sleep(DELAY)
                doc = HTMLParser(d.text)
                when = _uploaded_at(
                    doc.css_first("#bo_v_info .if_date").text()
                    if doc.css_first("#bo_v_info .if_date") else "")
                if not when:
                    raise RuntimeError(f"미카도스시 wr_id={wid}: 작성일을 못 읽었다")
                if when < floor:
                    # 최신순이라 여기부터는 전부 더 오래됐다. 남은 요청을 아낀다.
                    stop = True
                    break

                tit = doc.css_first(".bo_v_tit")
                con = doc.css_first("#bo_v_con")
                cat = doc.css_first(".bo_v_cate")
                name = _clean(tit.text()) if tit else listed
                body = _clean(con.text()) if con else ""
                img = ""
                for n in doc.css("#bo_v_atc img"):
                    src = n.attributes.get("src", "")
                    if "/data/file/menu/" in src:
                        img = src if src.startswith("http") else SITE + src
                        break

                it = Item(
                    brand=BRAND,
                    name=name,
                    # 본문이 상품명을 그대로 반복하는 글이 대부분이라 그때는 버린다.
                    desc="" if body.replace(" ", "") == name.replace(" ", "") else body,
                    image=img,
                    category=_clean(cat.text()) if cat else "",
                    uploaded_at=when,
                    # 본문이 '신메뉴'라고 말할 때만 True. 안 말하면 '아님'이 아니라 '모름'.
                    is_new=True if _SAYS_NEW.search(body) else None,
                    url=f"{LIST}?bo_table={BO}&wr_id={wid}",
                )
                if it.key in seen_key:
                    continue
                seen_key.add(it.key)
                items.append(it)

            if len(rows) < PAGE_SIZE:
                break
    return items
