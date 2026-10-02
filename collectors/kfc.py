"""KFC 코리아 — 브랜드가 직접 운영하는 '신메뉴' 면만 읽는다.

www.kfckorea.com 은 Vue SSR 이다. 상품 카탈로그(/allmenu)는 **클라이언트에서
XHR 로 채워져서 HTML 에 0건**이지만(`__INITIAL_COMPONENTS_STATE__` 가 `[null,null]`),
신메뉴 면(/promotion/newMenu)은 **서버가 데이터를 통째로 박아서 내려준다.**
그래서 그 한 면만 받는다. 브라우저 불필요, 요청 1회, 인증·토큰·리퍼러 없음.

  GET https://www.kfckorea.com/promotion/newMenu
      → HTML 안에 `window.__INITIAL_COMPONENTS_STATE__ = [null,{"listData":{...}}];`

신제품 신호 — 2026-10-02 실측. **브랜드가 자기 데이터에 유형을 적어 둔다.**
  event_type       "A805"
  event_type_nm    "신제품"
이게 이 어댑터의 근거 전부다. 배지를 우리가 해석하는 게 아니라 KFC 가 레코드에
'신제품'이라고 써 둔 것이다.

🔎 **가짜 신호인지 교차검증했다.** 같은 CMS 의 다른 면을 받아 비교했다:
  /promotion/promotionList/1  → 5건, event_type_nm 이 **전건 "행사"**.
      '치킨나이트 1+1', '10AM~2PM은 켚런치 타임!', '오리지널 딥버켓!',
      '매일 밤 9시~밤 10시까지 치킨 1+1!', '신규 회원 가입 혜택'
  /promotion/newMenu          → 1건, event_type_nm "신제품". 위 5건과 **겹치지 않는다.**
  /promotion/promotionEndList, /promotion/promotionOffshop → 이 면들엔 event 행이 없다.
세븐일레븐 '신상품' 탭처럼 같은 목록을 다른 주소로 다시 부르는 구조가 아니다.
행사와 신제품이 **다른 레코드**로 분리돼 있고 1+1·할인은 전부 '행사' 쪽에 있다.

날짜도 레코드가 준다. 둘 다 쓴다.
  event_show_str_date  "2026-09-08 04:00:00"  → released_at (판매 시작일)
  event_reg_dt         "2026-09-03 16:25:31"  → uploaded_at (KFC 가 글을 올린 시각)
  event_date           "9/8(화)~11/9(목)"     ← 연도가 없다. 쓰지 않는다.
본문(event_web_explan)의 "1. 판매 기간 : 26년 9월 8일 (화) ~ …" 도 같은 날짜라
교차로 맞는다. released_at 이 '출시일'이 아니라 '판매 시작일'인 건 맞지만, 신메뉴
면의 레코드라 그 둘이 같다고 본다.

상품명은 본문의 `2. 출시 메뉴 : 갓쏘이 치킨, 갓쏘이 통다리` 줄에서 뽑는다.
**event_title 은 쓰지 않는다** — "달콤짭짤의 갓벽한 밸런스! 갓쏘이치킨" 처럼
홍보 헤드라인이고, 이벤트 1건이 상품 2개를 담는 경우가 실제로 있다(지금이 그렇다).
이 줄을 못 찾으면 **예외로 올린다.** 조용히 0건이 되거나 헤드라인을 상품명으로
집는 것보다, 포맷이 바뀐 걸 드러내는 쪽이 낫다(이 레포의 조용한 부분수집 방침).

⚠️ **유보 — '신제품' 이 꼭 '처음 나온 것'은 아니다.** 지금 올라온 갓쏘이치킨은
   목록 이미지 아트웍에 **"RETURN"** 이라고 찍혀 있다(2026-09-03 업로드분 실측).
   재출시인데 KFC 가 자기 신메뉴 면에 '신제품'으로 올린 것이다. 브랜드가 그렇게
   말한 걸 근거 없이 뒤집지는 않지만(계약: 모르면 None, 아니라고 확인돼야 False),
   스시로 '이달의 한정메뉴'와 같은 종류의 유보가 여기에도 있다. 글자로는
   재출시인지 알 수 없다 — RETURN 은 이미지 안에만 있다.

⚠️ 수확량이 작다. 이 면은 **지금 판매 중인 신메뉴만** 보여준다(event_progress_yn=Y).
   2026-10-02 현재 1건(상품 2개)이다. 종료된 신제품을 돌려주는 목록은 없다
   (/promotion/promotionEndList 는 행사 전용이고 event 행이 0건이다).
   이벤트별 상세는 열리지만(아래 DETAIL), 지난 건을 찾으려면 event_index 를
   훑어야 해서 안 한다 — 스캐닝이고, 종료된 신메뉴는 지금 못 사는 상품이다.

이미지는 목록 썸네일(event_web_list_img)을 쓴다. 660×278 가로 배너라 카드에 맞는다.
상세 이미지(event_web_img)는 1070×1783 세로 전단이라 카드에서 못 쓴다.
경로가 `/event/...` 로만 와서 앞에 `/nas` 를 붙여야 실제 파일이다(IMG 상수).
`/nas/kfcimg/...`·`/kfcs_api_img/...` 는 전부 404 다 — 번들의 다른 상수에 속으면 안 된다.

url 은 이벤트 상세다. 경로 가운데의 `017fdaa1659d8d21b7070863d61f02ad` 는 우리가
지어낸 게 아니라 클라이언트 번들(/assets/client.js)의 라우트 정의에 그대로 박힌
문자열이다(`{path:"017fdaa1659d8d21b7070863d61f02ad/:sq", component:NewPromotionView}`).
실제로 열어 확인했다 — /1126 은 '달콤짭짤의 갓벽한 밸런스! 갓쏘이치킨' 이 렌더되고
없는 번호(/999999)는 빈 셸이 온다. ⚠️ 난독화된 라우트라 언젠가 바뀔 수 있다.
바뀌면 카드 링크가 빈 셸로 떨어진다(404 는 아니다). SITES 폴백으로 되돌리면 된다.

가격은 어느 응답에도 없다. 영양정보도 없다(/menu/allergy 는 이미지 한 장이다).

robots: https://www.kfckorea.com/robots.txt 는 **404 가 아니라 200 HTML** 이다.
        SPA catch-all 이 2,021바이트짜리 셸을 돌려준다(content-type 이 없고 본문이
        `<!doctype html>` 로 시작한다). 즉 robots.txt 가 **없다.** 허용도 금지도
        아니라 요청을 1회로 줄이고 간격을 길게 잡는다(죠스떡볶이 선례).
약관: /site/terms 도 같은 셸(200, 2,021바이트)이라 **본문을 확인하지 못했다.**
      푸터에 '사이트 이용약관' 링크는 있으나 클라이언트에서 그려져 초기 HTML 에
      없다. CRAWLING-POLICY.md §4 와 같은 칸이다. 붙이기 전에 사람이 봐야 한다.
"""
import html
import json
import re

from . import base
from .base import Item

BRAND = "KFC"
SITE = "https://www.kfckorea.com"
NEW_MENU = SITE + "/promotion/newMenu"
IMG = SITE + "/nas"
DETAIL = SITE + "/promotion/017fdaa1659d8d21b7070863d61f02ad/{sq}"

NEW_TYPE = "A805"      # event_type_nm "신제품". 행사는 다른 코드다(위 교차검증).

# `window.__INITIAL_COMPONENTS_STATE__ = [ ... ];` 다음 줄이 VUEX 상태라 거기서 끊는다.
_STATE = re.compile(
    r"window\.__INITIAL_COMPONENTS_STATE__\s*=\s*(\[.*?\])\s*;\s*"
    r"\n?\s*window\.__INITIAL_VUEX_STATE__", re.S)

# 본문의 `2. 출시 메뉴 : 갓쏘이 치킨, 갓쏘이 통다리` 줄.
_MENU_LINE = re.compile(r"출시\s*메뉴\s*[:：]\s*(.+)")

_BLOCK = re.compile(r"</\s*(?:div|p|br|li)\s*>", re.I)
_TAG = re.compile(r"<[^>]+>")

# 상품명이 아닌 것. 설명 문구가 같은 줄에 섞여 들어오면 여기서 걸린다.
_BAD_WORD = ("출시", "판매", "채널", "기간", "할인", "쿠폰", "원")


def _text(s: str) -> str:
    """HTML 본문을 줄 단위 평문으로. 블록 태그를 줄바꿈으로 바꾼 뒤 태그를 턴다.

    전부 공백으로 바꾸면 `1. 판매 기간 … 2. 출시 메뉴 … 3. 출시 채널 …` 이
    한 줄이 되어 '출시 메뉴' 줄이 어디서 끝나는지 알 수 없다.
    """
    s = _BLOCK.sub("\n", s or "")
    s = html.unescape(_TAG.sub("", s)).replace("\xa0", " ")
    return "\n".join(" ".join(line.split()) for line in s.split("\n"))


def _date(s: str) -> str:
    """'2026-09-08 04:00:00' → '2026-09-08'. 날짜꼴이 아니면 빈 문자열."""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", (s or "").strip())
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _names(explan: str) -> list:
    """`출시 메뉴 : A, B` 줄에서 상품명들. 못 찾으면 빈 목록."""
    for line in _text(explan).split("\n"):
        m = _MENU_LINE.search(line)
        if not m:
            continue
        out = []
        for part in re.split(r"[,/·]", m.group(1)):
            n = part.strip(" .·")
            if 2 <= len(n) <= 30 and not any(w in n for w in _BAD_WORD):
                out.append(n)
        if out:
            return out
    return []


def _state(page: str) -> list:
    m = _STATE.search(page)
    if not m:
        raise RuntimeError(
            "__INITIAL_COMPONENTS_STATE__ 를 못 찾았다 — SSR 이 꺼졌거나 변수명이 바뀌었다")
    return json.loads(m.group(1))


def _rows(state: list) -> list:
    for part in state:
        if isinstance(part, dict) and isinstance(part.get("listData"), dict):
            return part["listData"].get("rows") or []
    raise RuntimeError(f"listData 가 없다 — 응답 모양이 바뀌었다(요소 {len(state)}개)")


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(NEW_MENU))
        r.raise_for_status()
        rows = _rows(_state(r.text))

    # 신메뉴 면이 통째로 비는 건 '신제품이 없다'일 수도 있지만, 파서가 깨진
    # 경우와 구분이 안 된다. 0건은 collect 가 어차피 실패로 잡으므로 여기서
    # 사유를 분명히 적어 올린다.
    if not rows:
        raise RuntimeError("KFC 신메뉴 목록이 0건 — 응답 스키마나 노출 조건이 바뀌었는지 확인하라")

    for row in rows:
        if (row.get("event_type") or "") != NEW_TYPE:
            # 신메뉴 면에 행사 레코드가 섞여 들어오면 드러나야 한다.
            raise RuntimeError(
                f"신메뉴 면에 '{row.get('event_type_nm')}'({row.get('event_type')}) "
                f"레코드가 섞였다: {row.get('event_title')!r}")
        names = _names(row.get("event_web_explan") or "")
        if not names:
            raise RuntimeError(
                f"'출시 메뉴 :' 줄을 못 찾았다(event_index={row.get('event_index')}, "
                f"title={row.get('event_title')!r}) — 본문 서식이 바뀌었다")
        image = row.get("event_web_list_img") or row.get("event_web_img") or ""
        sq = row.get("event_index")
        for name in names:
            it = Item(
                brand=BRAND,
                name=name,
                # 이벤트 제목이 그 상품의 홍보 문구다. 설명으로는 그대로 쓸 만하다.
                desc=" ".join((row.get("event_title") or "").split()),
                image=IMG + image if image else "",
                released_at=_date(row.get("event_show_str_date")),
                uploaded_at=_date(row.get("event_reg_dt")),
                is_new=True,        # KFC 가 레코드에 '신제품'이라고 적어 뒀다
                url=DETAIL.format(sq=sq) if sq else "",
            )
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)
    return items
