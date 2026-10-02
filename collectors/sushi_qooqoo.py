"""쿠우쿠우 — 보도자료 스크랩 게시판에서 신메뉴와 그 상품명을 뽑는다.

**초밥뷔페라 '상품 목록'이 아예 없다.** 2026-10-02 실측으로 확인한 구조다.

  /page/?pid=Sushi-roll · Hotdish · Instant · Dessert
      상설 메뉴를 쉼표로 늘어놓은 소개문 한 덩어리다("광어초밥, 연어초밥,
      육회초밥, …"). 상품 단위 마크업도, 날짜도, NEW 표시도 없다.
  /page/?pid=newMenu  ← '신메뉴 소개'
      **이미지 4장이 전부다.** `newmenu_260615_1.png` ~ `_4.png` 가 `<li><img>`
      로 나란히 붙어 있고 alt 도 캡션도 없다. 상품명이 픽셀 안에만 있어서
      긁을 것이 없다. 파일명의 `260615` 를 날짜로 쓰지 않는다는 건 이 레포
      방침이고(메가·할리스·스시로 선례), 애초에 상품명이 없으니 소용도 없다.

그래서 **메뉴 화면이 아니라 공지사항(bo_table=notice)** 을 읽는다. 이름은
공지사항이지만 실제 내용물은 **자사 보도자료 스크랩**이다 — 매체명을 대괄호로
머리에 달고(`[신아일보] …`) 기사 전문을 본문에 그대로 옮겨 둔다. 2026-10-02
기준 7페이지(105건)를 훑어 전부 눈으로 확인했고, 그중 신메뉴 기사는 날짜·
상품명·사진을 모두 갖고 있다. 오리온·GS25 보도자료 어댑터와 같은 칸이다.

신제품 신호:
  is_new       채택된 건은 전부 True. 브랜드가 "신메뉴 … 출시"라고 낸 기사만
               고르기 때문이다. 아래 _pick 참고.
  released_at  게시판 등록일(`td-date`, `2026.08.25`)을 쓴다.
               ⚠️ **유보**: 이건 스크랩을 올린 날이지 출시일이 아니다. 실측하면
               기사 입력일(2026.08.19)보다 뒤고, 기사가 말하는 실제 판매 시작일
               (8월 15일)보다는 열흘 뒤다. 즉 **항상 실제 출시일보다 늦다.**
               본문에서 날짜를 캐낼 수도 있지만 표기가 매체마다 달라
               ('입력 2026.08.19 15:10' / '승인' / '작성일' / '2026-07-01 12:31:44')
               안정적이지 않다. 구조화된 필드 하나를 쓰는 쪽을 택했다.

상품명 뽑기가 이 어댑터의 전부다. 기사 본문이 상품을 적는 방식이 셋이고
**셋 다 섞여 나온다.** 실측해서 신뢰도 순으로 줄을 세웠다.

  ① ▲ 글머리표 (wr_id=783, 12월 신메뉴 19종)
     "▲치즈타코야끼초밥 ▲치즈시로미야끼초밥(고단백) ▲火끈우삼겹직화롤 …"
     가장 깨끗하다. 있으면 이것만 쓴다.
  ② ‘…’ 작은따옴표 (wr_id=851·836·820)
     "‘옥수수 팬케이크’와 ‘단고단고 인절미 팬케이크’를 전국 매장에서"
     상품명이 맞을 때도 있지만 **콘셉트 문구도 같은 따옴표에 들어간다** —
     ‘푸드파티’, ‘키즈 피크닉’, ‘얼큰함’, ‘치즈의 풍미’,
     ‘숲의 기운을 담다 - 자연이 전하는 건강한 에너지’. 그래서 ① 이 없을 때만
     쓰고 _is_concept 로 한 번 더 거른다.
  ③ 평문 (wr_id=830·779)
     "샐러드 메뉴로는 시트러스 푸룬 샐러드와 구운 버섯 샐러드를 마련했다."
     **구분할 방법이 없다.** 억지로 자르면 '메뉴로는'·'마련했다' 같은 게
     상품이 된다. 이런 기사는 **0건으로 넘긴다.** 실제로 wr_id=830
     ('푸드파티' 정기 신메뉴)은 이 어댑터가 한 건도 못 가져온다.
     같은 출시를 다른 매체가 ①·② 로 쓴 기사가 함께 올라오는 일이 잦아
     (12월 신메뉴는 779·780·781·783 네 건) 실제 손실은 보이는 것보다 작다.

**같은 출시를 여러 매체가 쓴 중복은 Item.key 로 접힌다.** base.make_key 가
공백을 털기 때문에 ‘쿠웅이 찐빵’(779 본문)과 ▲쿠웅이찐빵(783 본문)이 같은
키가 된다 — 노린 게 아니라 확인한 것이다.

**쿠우쿠우 블루레일은 뺀다.** 같은 회사의 회전초밥 서브브랜드고 보도자료도
섞여 들어오는데(wr_id=806·807·808·831·832) 우리 레지스트리에 등록된 브랜드가
아니다. 남의 브랜드 상품을 쿠우쿠우 이름으로 올릴 수는 없다. 제목에
'블루레일'이 있으면 거른다.

⚠️ 2026-10-02 수집분 27건 중 1건이 깨진 이름으로 들어온다 — `치즈케이쿠아이`.
   원문이 `▲치즈케이쿠아이 스크림`(치즈케이크 아이스크림)으로 **글머리표 안에
   오타 공백**이 있어서다. 소스의 오타이지 파싱 실패가 아니라 손대지 않았다.
   공백을 메우려면 '글머리표 뒤 두 번째 단어도 이름일 수 있다'는 규칙이
   필요한데, 그러면 `▲홍초火닭갈비 등`의 '등'까지 이름에 붙는다.

이미지는 본문 첫 `/data/editor/…` 이미지를 쓴다. https 로 열리고, robots.txt 가
404(=제한 없음)라 금지 경로 문제도 없다. 다만 기사 대표사진이라 상품 1건의
사진이 아니라 **그 출시분 전체를 찍은 한 장**인 경우가 많다. 같은 출시에서 뽑은
여러 상품이 같은 사진을 공유한다. 게시판이 링크를 `https://host:443/…` 로
내는 자리가 있어 기본 포트는 떼고 담는다.

이용약관: 없다. 2026-10-02 실측 — 푸터에 약관·개인정보 링크가 없고 전역
네비게이션(브랜드이야기/메뉴안내/매장찾기/창업/고객지원) 어디에도 없다.
robots.txt 는 404. 그래서 요청 간격을 넉넉히 둔다.

desc 는 비운다. 본문이 기사 전문이라 그대로 담으면 남의 기사를 통째로
싣는 꼴이 된다(CRAWLING-POLICY §3-① 에서 제일 큰 리스크로 꼽은 항목).
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "쿠우쿠우"
SITE = "https://www.qooqoo.co.kr"
LIST = SITE + "/bbs/board.php"
BO = "notice"          # 이름은 공지사항이지만 내용물은 보도자료 스크랩이다
DAYS = 300             # 이 범위 밖 글은 상세를 받지 않는다(오리온과 같은 상한)
MAX_PAGES = 10         # 폭주 방지. 한 페이지 15건, 300일이면 6페이지쯤.
DELAY = 2.2            # 요청 간격(초). robots·약관이 없는 사이트라 보수적으로.

# 제목 선별. '메뉴'를 내놓았다고 말하는 기사만 통과시킨다.
# 둘 다 필요하다 — _NOUN 만 보면 '메뉴 개편'·'메뉴 구성'이 들어오고,
# _VERB 만 보면 '414석 대형 프리미엄 뷔페 선보여'(매장 기사)가 들어온다.
_NOUN = ("신메뉴", "메뉴")
_VERB = ("출시", "선보")
# 위 둘을 통과하고도 상품 기사가 아닌 것들. 전부 실측에서 걸린 제목이다.
#   교육   — '2026년 1차 정기 신메뉴 집체교육 실시'
#   경연·성료·시상 — '제1회 가맹점 신메뉴 경연대회 성료'
#   블루레일 — 서브브랜드(위 docstring 참고)
_SKIP = ("블루레일", "교육", "경연", "시상", "성료", "수상", "간담회", "미팅",
         "리뉴얼", "오픈", "개점", "협약", "MOU", "이벤트", "프로모션",
         "할인", "증정", "모집", "채용", "매출", "실적")

# ① 글머리표. 뒤에 오는 첫 덩어리만 본다.
_BULLET = re.compile(r"[▲△■]\s*([^\s▲△■]{2,30})")
# ② 작은따옴표. 곧은 따옴표도 쓰는 매체가 있어 둘 다 받는다.
_QUOTED = re.compile(r"[‘'']([^’''“”]{2,28})[’'']")

# ② 에서 상품이 아닌 걸 거르는 말들. 따옴표 **뒤 30자 안**에 이게 있으면
# 그 따옴표는 상품명이 아니라 그 출시의 콘셉트·모티브다.
#   "‘키즈 피크닉’을 콘셉트로 한 신메뉴 6종"
#   "‘얼큰함’과 ‘치즈의 풍미’를 핵심 콘셉트로 한"
#   "마스코트 ‘쿠웅이’를 모티브로 해"
_CONCEPT_AFTER = ("콘셉트", "컨셉", "모티브", "주제", "테마", "핵심")
# 말끝이 이러면 상품명이 아니라 상태·느낌을 적은 말이다('얼큰함'·'화려함').
_CONCEPT_TAIL = ("함", "움", "임", "듯", "다", "요", "죠", "까")

# `▲치즈버거롤이 새롭게 등장해` — 글머리표 run 의 마지막 항목에는 조사가 붙는다.
# 조사를 늘 떼면 '떡볶이'·'쿠웅이' 같은 진짜 이름이 깎이므로, **뒤따르는 말이
# 서술어일 때만** 뗀다. 실측에서 걸린 건 '새롭게'·'마련됐다' 둘이고 나머지는
# 같은 자리에 올 법한 말을 미리 넣어 둔 것이다.
_JOSA = "이가은는을를"
_PREDICATE = ("새롭게", "추가", "마련", "등장", "포함", "구성", "준비",
              "선보", "출시", "제공", "올랐", "더했", "대거")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _date(s: str) -> str:
    """'2026.08.25' → '2026-08-25'. 월·일 범위를 검증한다."""
    m = re.search(r"(20\d{2})[-.](\d{1,2})[-.](\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _wanted(title: str) -> bool:
    """이 제목이 신메뉴 출시 기사인가."""
    t = _clean(title)
    if any(w in t for w in _SKIP):
        return False
    return any(w in t for w in _NOUN) and any(w in t for w in _VERB)


def _strip_josa(tok: str, after: str) -> str:
    """글머리표 끝에 붙은 조사만 뗀다. 뒤에 서술어가 올 때만."""
    if len(tok) >= 4 and tok[-1] in _JOSA and any(
            after.lstrip().startswith(w) for w in _PREDICATE):
        return tok[:-1]
    return tok


def _by_bullet(body: str) -> list:
    out = []
    for m in _BULLET.finditer(body):
        tok = _strip_josa(m.group(1), body[m.end():m.end() + 12])
        tok = tok.strip(" ,·∙")
        if len(tok) >= 2:
            out.append(tok)
    return out


def _is_concept(name: str, after: str, title: str) -> bool:
    """따옴표 안이 상품명이 아니라 콘셉트 문구인가."""
    if name in title:                       # 제목에 이미 나온 건 그 기사의 콘셉트다
        return True
    if any(w in after for w in _CONCEPT_AFTER):
        return True
    if name.endswith(_CONCEPT_TAIL):
        return True
    # '치즈의 풍미' 같은 소유격 구절. 상품명에 '의 ' 가 들어가는 일은 없었다.
    return "의 " in name or " - " in name or "–" in name


def _by_quote(body: str, title: str) -> list:
    out = []
    for m in _QUOTED.finditer(body):
        name = m.group(1).strip(" ,·∙")
        if len(name) < 2 or _is_concept(name, body[m.end():m.end() + 30], title):
            continue
        out.append(name)
    return out


def _names(body: str, title: str) -> list:
    """본문에서 상품명들. 글머리표가 있으면 그것만, 없으면 따옴표."""
    names = _by_bullet(body) or _by_quote(body, title)
    seen, out = set(), []
    for n in names:
        flat = n.replace(" ", "")
        if flat not in seen:
            seen.add(flat)
            out.append(n)
    return out


def _rows(html: str) -> list:
    """(등록일, wr_id, 제목). 고정 공지도 섞여 있어 날짜가 없으면 버린다."""
    out = []
    for tr in HTMLParser(html).css("tr"):
        a, d = tr.css_first(".td-subject a"), tr.css_first(".td-date")
        if not (a and d):
            continue
        m = re.search(r"wr_id=(\d+)", a.attributes.get("href", ""))
        when = _date(d.text())
        if m and when:
            out.append((when, m.group(1), _clean(a.text())))
    return out


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    cand, seen_id = [], set()
    with base.client(verify=False) as c:
        for page in range(1, MAX_PAGES + 1):
            r = base.retry(lambda: c.get(LIST, params={"bo_table": BO, "page": page}))
            r.raise_for_status()
            rows = _rows(r.text)
            if not rows:
                if page == 1:
                    raise RuntimeError("쿠우쿠우 공지사항: 0건 — 셀렉터가 깨졌을 수 있다")
                break
            # 범위를 넘긴 page 가 1페이지를 되돌려주는 게시판이 흔하다. 전부 본 글이면 종료.
            if all(w in seen_id for _, w, _ in rows):
                break
            fresh = False
            for when, wid, title in rows:
                if wid in seen_id:
                    continue
                seen_id.add(wid)
                # 1페이지 맨 위에 2019년 고정 공지가 붙어 있다. 그것 때문에
                # 페이지를 끊으면 안 되므로, 끊는 판단은 '고정 아닌 글'로만 한다.
                if when >= floor:
                    fresh = True
                    if _wanted(title):
                        cand.append((when, wid, title))
            time.sleep(DELAY)
            if not fresh:
                break

        items: list[Item] = []
        seen = set()
        for when, wid, title in cand:
            time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"bo_table": BO, "wr_id": wid}))
            r.raise_for_status()
            doc = HTMLParser(r.text)
            atc = doc.css_first(".board-view-atc")
            if atc is None:
                raise RuntimeError(f"쿠우쿠우 wr_id={wid}: 본문(.board-view-atc)이 없다")
            body = _clean(atc.text())
            img = ""
            for n in atc.css("img"):
                src = n.attributes.get("src", "")
                if "/data/editor/" in src:
                    img = src if src.startswith("http") else SITE + src
                    img = img.replace("https://www.qooqoo.co.kr:443/", SITE + "/")
                    break
            for name in _names(body, title):
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=img,
                    released_at=when,
                    is_new=True,     # 브랜드가 '신메뉴 … 출시'라고 낸 기사다
                    url=f"{LIST}?bo_table={BO}&wr_id={wid}",
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)
    return items
