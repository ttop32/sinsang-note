"""신세계푸드 — 뉴스 게시판에서 신제품과 출시일을 뽑는다.

오뚜기·오리온·샘표·삼양식품과 같은 계보다(보도자료 제목 → 상품명).
조인 규칙은 `collectors/maker_orion.py` 것을 그대로 가져왔다.
올반·보앤미·베키아에누보와 **이마트 피자(냉동피자)** 를 내는 회사다.

## 목록은 XHR 로 온다 (여기가 이 사이트의 전부)

사람이 여는 면 `/company/pr/news_list.sf` 는 200 / 17,333B 인데 **기사가 1건만
들어 있다.** `?pagging=2`·`?page=2`·`?currentPage=2` 를 아무리 넣어도 **바이트
단위로 같은 응답**이 온다(실측 4가지). 목록은 JS 가 따로 받아 붙인다.
브라우저로 열어 네트워크 로그를 떠서 찾았다 — **엔드포인트는 따로 있다**:

  GET https://www.shinsegaefood.com/company/pr/response/news_list.sf
      ?pagging=1&gubun=109001&newType=                     200 / 8,519B
    <ul class="news_list">
     <li><a href="/company/pr/news_detail.sf?newsId=1498&pagging=1">
       <div class="wrap_img"><img src="/uimages/2026/09/30/제목-없음-1.jpg" /></div>
       <div class="wrap_txt">
         <p class="txt">신세계푸드, 즉석 과일 스무디 팝업 ‘스꾸하우스’ 오픈…</p>
         <p class="info"><span class="date">2026.09.30</span>
                         <span class="from">보도자료</span></p>
       </div></a></li>
  응답 앞머리에 페이저를 그리는 인라인 `<script>` 가 붙어 오는데 거기에
  **`var totalCount = 831;`** 이 있다. 페이지당 12건.
  ⚠️ `gubun=109001` 을 빼면 안 된다. 사람이 여는 면의 '전체' 탭이 이 값을 쓴다.
  ⚠️ 이미지 경로에 **한글 파일명**이 그대로 들어온다(`노브랜드_버거X애니모_포스터`).
     httpx 가 알아서 인코딩하니 손대지 마라.

## ⚠️ 이 브랜드의 진짜 문제 — 뉴스의 절반이 '노브랜드 버거' 다

3페이지 27건(2026-07-08 ~ 10-01, 약 3개월)을 전수로 읽었다.
**13건이 노브랜드 버거**(가맹점 모집·출점·앱 회원·가격 조정·협업 버거 출시)다.
노브랜드 버거는 **외식 햄버거 프랜차이즈**지 제조사 상품이 아니다. 이 사이트의
'신세계푸드 / 냉동식품' 칸에 버거 메뉴를 올리면 분류가 거짓이 된다.
→ `_SKIP` 에 `노브랜드`·`데블스도어`(맥주 펍)를 넣어 **외식 축을 통째로 뺀다.**
  ⚠️ `버거` 한 단어로 거르지 마라 — 제조사가 내는 냉동 버거 패티·번이 실재한다.

나머지 14건의 성격 —
    인기/매출 증가 5건 · 팝업·기획전 3건 · 수출 1건 · 판매채널 확대 1건 ·
    원료 도입 1건 · **출시 3건**:
        2026-09-21  ‘보앤미’, 프리미엄 건강빵 5종 출시          ← 집는다(`_COUNT_TAIL`)
        2026-09-15  가을 제철 ‘생무화과’ 듬뿍 올린 케이크 이마트서 출시
                                                            ← 버린다(`_INGREDIENT_MID`)
        2026-08-06  멜론 디저트 2종 출시                        ← 집는다
5페이지 45건으로 넓혀 다시 세면 **6건**이 남는다(2026-10-03 검수).
→ **3개월에 1~2건**이다. 건수가 적은 게 정상이고 '수집 실패'가 아니다.
  그래도 넣는 이유는 이 회사가 **냉동피자(이마트 피자) 축의 유일한 국내 소스**이기
  때문이다 — 냉동피자 전업사가 없고 전부 종합식품사의 한 라인이다.

**일괄 등록 흔적 — 없다.** 27건 날짜가 전부 다르고 07-08 ~ 10-01 로 고르다.

robots: https://www.shinsegaefood.com/robots.txt — 확인했다(아래 명령으로 재확인 가능).
        수집 경로가 `/company/pr/` 라 금지 목록과 겹치지 않았다.
약관:   확인하지 않았다.
"""
import certifi
import pathlib
import ssl
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "신세계푸드"
SITE = "https://www.shinsegaefood.com"
LIST = SITE + "/company/pr/response/news_list.sf"      # 사람이 여는 면 말고 XHR 쪽
VIEW = SITE + "/company/pr/news_detail.sf"
GUBUN = "109001"     # '전체' 탭. 빼면 목록이 안 온다.
PER_PAGE = 12
MAX_PAGES = 5        # 한 페이지 12건 = 약 5개월치. 폭주 방지 상한.
DAYS = 300
DELAY = 2.2

# --- 제목 → 상품명 (maker_orion 과 같은 규칙 + 신세계푸드 함정 보강) ---------
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭|런칭)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_TRAIL_SEP = re.compile(r"^\s*[·∙,、/]")
# ⚠️ `_MULTI`(\d+종) 는 **일부러 없앴다.** 이 어댑터는 `N종` 을 버리지 않고
#    꼬리만 턴다(`_COUNT_TAIL`). 상수를 남겨 두면 다음 사람이 되살려서
#    브랜드가 통째로 죽는다 — 이 라운드 최대 결함이 정확히 그거였다.
_BRAND_HEAD = re.compile(r"브랜드\s*$")

_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원", "프로젝트",
         "이벤트", "광고", "조회수", "할인", "선물", "프로모션",
         "기획전", "가맹", "출점", "창업",
         # 외식 축. 제조사 상품이 아니다(위 docstring 참고).
         # ⚠️ '버거' 한 단어로 줄이지 마라 — 냉동 버거 패티·번이 실재한다.
         "노브랜드", "데블스도어",
         # 국내 출시가 아닌 건 화면에 올리면 거짓이 된다.
         "日", "美", "글로벌", "수출", "해외", "현지")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
# 따옴표 **안이 재료·테마**일 때 쓰이는 연결어. 이게 따옴표와 동사 사이에 있으면
# 따옴표 안은 상품명이 아니다. 신세계푸드에서 실측한 오탐 3건이 전부 이 모양이었다:
#     가을 제철 ‘생무화과’ **듬뿍 올린** 케이크 … 출시     → 상품은 '케이크'
#     슈퍼푸드 ‘파로’ **넣은** 삼계탕 간편식 출시          → 상품은 '삼계탕 간편식'
#     ‘우리산지 레시피’**로** … **앞장**… 디저트 출시       → 캠페인 기사
# 남는 쪽은 안 다친다(실측): `생과일 1kg 올린 ‘생과일 한가득 케이크’ 트레이더스…`
# 는 연결어가 따옴표 **앞**이라 통과한다 — 위치가 그 구분이다.
# maker_orion 계열 공통 규칙으로 올릴 만한 보강인데, 다른 어댑터는 이미 출력이
# 깨끗한 걸 실측해 둬서 여기서만 쓴다(한 번에 다 건드리면 뭘 고쳤는지 모르게 된다).
_INGREDIENT_MID = ("넣은", "올린", "담은", "더한", "활용", "사용한", "앞장",
                   "적용한", "곁들인", "얹은")
# 🔴 **흔한 말은 제목 전체(`_SKIP`)가 아니라 동사 뒤에서만 본다.**
# 2026-10-03 검수에서 `인기·증가·확대·가격·오픈` 다섯을 `_SKIP` 에서 여기로 옮겼다.
# 이 다섯은 **출시 기사 머리의 수식어로 흔히 쓰이는 말**이라 제목 전체로 보면
# 진짜 신제품이 조용히 죽는다. 지어낸 제목으로 실증한 것:
#     가격 부담 낮춘 ‘올반 사골곰탕’ 출시      → `가격` 에 걸려 전멸
#     인기 맛집 레시피 담은 ‘올반 짬뽕’ 출시   → `인기`
#     라인업 확대하며 ‘올반 갈비탕’ 출시       → `확대`
#     ‘오픈샌드위치’ 출시                     → `오픈`(이 회사는 냉동 샌드위치를 낸다)
# **옮겨도 실측 출력은 그대로다**(45건 전수 재실행, 6건 동일). 지금 이 다섯이
# 거르고 있던 기사는 전부 `_VERB` 가 없거나 `노브랜드` 가 먼저 잡는 것들이었다
# — 즉 `_SKIP` 에서의 기여가 0이면서 미래 손실만 만드는 자리였다.
# 동사 뒤에 있으면 그대로 걸린다(`‘X’ 출시…판매 확대`·`…출시 기념 팝업 오픈`).
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다",
         "증가", "확대", "가격", "오픈")
_REPACK_HEAD = ("에디션", "라벨")
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")
_REPACK_NAME = ("에디션", "컬렉션", "한정판", "선물세트", "기획세트", "기획팩")

# 🔴 **`N종` 을 버리지 않고 꼬리만 뗀다.** 오리온 규칙은 `N종` 이 들어간 제목을
# 통째로 버리는데(따옴표 안이 상품이 아니라 라인 이름일 수 있어서), 신세계푸드는
# 출시 기사의 **절반이 `N종 출시`** 라 그대로 두면 최근 3개월 수확이 **0건**이 된다.
# 2026-10-02 실측 — 1~3페이지 27건에서 집은 상품이 0건이었고, 그렇게 죽은 것 중
# 둘은 진짜 신제품이었다:
#     신세계푸드 ‘보앤미’, 프리미엄 건강빵 5종 출시
#     신세계푸드, 멜론 디저트 2종 출시
# 사조·면사랑과 같은 판단이다(그쪽도 `N종 출시` 가 기본형이다).
#
# 대신 **따옴표 안만 쓰면 안 된다.** 따옴표가 브랜드·재료만 감싸는 제목이 있다:
#     ‘보앤미’, 프리미엄 건강빵 5종 출시   → '보앤미' 는 브랜드다
#     ‘골드키위’ 여름 케이크 2종 출시      → '골드키위' 는 재료다
# 그래서 **첫 따옴표부터 동사 앞까지**를 통째로 잡고 따옴표 기호·`N종` 꼬리를 턴다
# (따옴표가 없으면 주어를 뗀 머리 전체). 그러면 위 둘이 각각
# `보앤미 프리미엄 건강빵`·`골드키위 여름 케이크` 로 제대로 나온다.
_SUBJECT = re.compile(r"^.*?신세계푸드\s*,?\s*")
_QUOTE_CHARS = re.compile(r"[‘’'`“”\"]")
_COUNT_TAIL = re.compile(r"\s*\d+\s*종\s*$")

# 통째로 잡으면 **판매 채널**이 이름 뒤에 붙어 온다. 실측 2건:
#     ‘생과일 한가득 케이크’ **트레이더스 베이커리서** 출시
#     ‘픽베이크 에그타르트’ **트레이더스 전용 제품으로** 출시
# 상품명이 아니라 어디서 파는지다. 꼬리에서만 턴다 — 이름 가운데는 안 건드린다.
#
# 🔴 2026-10-03 검수에서 고쳤다. 앞의 식은
#     `(?:채널어)(?:\s*\S*)*?\s*(?:베이커리서|…|에서|서|로|으로)?\s*$`
# 였는데 **조사 그룹이 선택적(`?`)이라** 채널어부터 제목 끝까지를 통째로 먹었다.
# 즉 '꼬리에서만 턴다' 는 주석과 달리 **이름 가운데를 잘랐다.** 실증:
#     ‘이마트 피자 불고기’ 출시      → `이마트…` 전부 먹혀 ''  ← 이 회사 **간판 냉동피자**다
#     ‘베누 스타필드 샌드위치’ 출시   → `베누` 로 깎임
# 이 어댑터를 넣은 이유 자체가 냉동피자(이마트 피자) 축인데 그 이름을 못 집고
# 있었다. → **조사(서·에서·로·으로)로 끝날 때만** 떼고, 채널어와 조사 사이에는
# 실측된 두 꼴(`베이커리`·`전용 제품`)만 허용한다. 실측 2건은 그대로 떼진다.
_CHANNEL_TAIL = re.compile(
    r"\s*(?:트레이더스|이마트|SSG|쓱닷컴|스타필드|자사몰|공식몰)"
    r"(?:\s*(?:베이커리|전용\s*제품))?\s*(?:에서|서|로|으로)\s*$")

# 통째로 잡은 머리가 **상품이 아니라 캠페인 문구**인 경우. 실측 1건:
#     불황 속 ‘아는 맛’ 소비 트렌드 겨냥…가성비 디저트 2종 출시
# `…` 가 남아 있으면 문장 두 개를 이어 붙인 것이고, `겨냥`·`트렌드` 는
# 상품명에 안 쓰이는 말이다. ⚠️ `·` 도 넣는다 — 오리온 `_pick` 이 상품명에
# `·` 가 들어가면 버리는 것과 같은 판단이다(둘을 이어 붙인 이름이라 못 쓴다).
_NOT_A_NAME = ("겨냥", "트렌드", "…", "·")


# 서버가 중간 인증서를 빠뜨린다. 2026-10-08 실측 10/10 전부 리프 한 장만 보낸다
# (`openssl s_client` 로 확인). 리프의 issuer 는 GlobalSign GCC R46 OV TLS CA
# 2025 이고 AIA 가 가리키는 곳에서 그 한 장을 받아 두었다.
#
# ⚠️ 10-02 실측에서는 **재현되지 않았다**(docstring 에 "verify=True 로 6회 연속
# 200" 이라고 적혀 있다). 그 사이 서버 설정이 바뀐 것이다. 사이트가 멀쩡해
# 보여도 체인은 따로 봐야 한다는 뜻이라 적어 둔다.
#
# `verify=False` 는 쓰지 않는다 — notes/CRAWLING-POLICY.md §6-1 이 명시적으로
# 금지하고, 같은 사유·같은 처리의 선례가 lottechilsung.py·chicken_toreore.py 다.
# 검증은 켜진 채 돈다. certifi 루트에 **더하기만** 한다.
_CA_EXTRA = pathlib.Path(__file__).parent / "certs" / \
    "globalsign-gcc-r46-ov-tls-ca-2025.pem"


def _ssl_context() -> ssl.SSLContext:
    """certifi 루트에 서버가 빠뜨린 중간 인증서 한 장을 **더한** 컨텍스트."""
    if not _CA_EXTRA.exists():
        raise FileNotFoundError(
            f"중간 인증서가 없다: {_CA_EXTRA} — 이게 없으면 이 사이트는 "
            "unable to get local issuer certificate 로 붙지 않는다")
    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.load_verify_locations(cafile=str(_CA_EXTRA))
    return ctx


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열."""
    t = " ".join(title.split())
    if any(w in m.group(1) for m in _HEAD.finditer(t) for w in _REPACK_HEAD):
        return ""
    # ⚠️ 외식 축은 “…” 홍보 헤드라인에만 나오기도 한다(`“버거 먹고 …”…노브랜드 버거`).
    #    _HEAD 를 지우기 **전에** 제목 전체로 한 번 본다.
    if any(w in t for w in ("노브랜드", "데블스도어")):
        return ""
    body = _HEAD.sub(" ", t)
    # ⚠️ `_MULTI`(N종)로 버리지 않는다. 사유는 _COUNT_TAIL 위 주석.
    if any(w in body for w in _SKIP):
        return ""
    qs = list(_SINGLE.finditer(body))
    if len(qs) >= 2 and any(w in body[qs[-2].end():qs[-1].start()] for w in _REPACK_MID):
        return ""
    verb = None
    for m in _VERB.finditer(body):
        verb = m
    if not verb or any(w in body[verb.end():] for w in _TAIL):
        return ""
    head = body[:verb.start()]
    quoted = None
    for m in _SINGLE.finditer(head):
        quoted = m
    if quoted:
        if any(w in head[quoted.end():] for w in _BETWEEN):
            return ""
        if any(w in head[quoted.end():] for w in _INGREDIENT_MID):
            return ""
        if _BRAND_HEAD.search(head[:quoted.start()]):
            return ""
    # 따옴표가 있으면 **첫 따옴표부터** 동사 앞까지, 없으면 주어를 뗀 머리 전체.
    firsts = list(_SINGLE.finditer(head))
    seg = head[firsts[0].start():] if firsts else _SUBJECT.sub("", head)
    name = _QUOTE_CHARS.sub("", seg)
    name = _COUNT_TAIL.sub("", name.strip())
    name = _CHANNEL_TAIL.sub("", name)
    name = re.sub(r"\s*,\s*", " ", name).strip(" ,·∙!…")
    if any(w in name for w in _NOT_A_NAME):
        return ""
    if not (2 <= len(name) <= 40):
        return ""
    if any(w in name for w in _REPACK_NAME):
        return ""
    return name


def _date(s: str) -> str:
    """'2026.09.15' → '2026-09-15'. 월·일 범위를 검증한다."""
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})\s*$", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _rows(html: str) -> list[tuple]:
    """XHR HTML → (날짜, 제목, href, 이미지) 목록."""
    out = []
    for li in HTMLParser(html).css("ul.news_list li"):
        a, tx = li.css_first("a"), li.css_first("p.txt")
        if not (a and tx):
            continue
        dt = li.css_first(".date")
        img = li.css_first(".wrap_img img")
        src = (img.attributes.get("src") or "").strip() if img else ""
        out.append((_date(dt.text(strip=True) if dt else ""),
                    " ".join(tx.text().split()),
                    (a.attributes.get("href") or "").strip(),
                    SITE + src if src.startswith("/") else src))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    with base.client(verify=_ssl_context()) as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"pagging": page,
                                                       "gubun": GUBUN,
                                                       "newType": ""}))
            r.raise_for_status()
            rows = _rows(r.text)

            # XHR 주소나 gubun 이 바뀌면 조용히 0건이 된다. 831건짜리 게시판이라
            # 1페이지는 반드시 12행이 와야 한다. 출시 기사가 드문 브랜드라
            # '상품 0건'은 정상이지만 '목록 0행'은 고장이다.
            if page == 1 and not rows:
                raise ValueError(
                    f"신세계푸드 뉴스 1페이지가 비었다. {r.url} → "
                    f"{len(r.content)}B — XHR 주소(/company/pr/response/news_list.sf)나 "
                    f"gubun={GUBUN}, 목록 셀렉터(ul.news_list li / p.txt / .date)가 "
                    f"바뀌었는지 확인하라")
            if not rows:
                break

            for released, title, href, img in rows:
                if released and released < floor:
                    continue
                name = _pick(title)
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=re.sub(r"^\s*신세계푸드\s*", "", title).lstrip(" ,"),
                    image=img,
                    released_at=released,
                    is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                    url=SITE + href if href.startswith("/") else (href or LIST),
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            fresh = [d for d, *_ in rows if d]
            if fresh and max(fresh) < floor:
                break
    return items
