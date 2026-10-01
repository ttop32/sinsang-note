"""샘표 — 보도자료에서 신제품과 출시일을 뽑는다.

오뚜기·오리온·GS25·동서식품과 같은 종류의 소스다. 그 계보의 규칙을 그대로 가져와
샘표 제목 버릇에 맞게 조인다. 조사한 브랜드 중 **출시 기사 밀도가 제일 높다** —
1페이지 12건 중 '출시'가 든 기사가 5~6건이다.

수집 경로. 2026-10-01 실측:
  - `/news/press-release` 가 **완전한 SSR** 이다. 45KB 원본 HTML 에 한 줄로
    카테고리·썸네일·제목·날짜가 다 들어 있다. JS 도 XHR 도 필요 없다.

        <div class="item">
          <span class="category blind">press</span>
          <a href="/news/view/1634" class="item-a block">
            <div class="item-thumb"><img src="/image/KU/HV/2026090811220200….jpg"></div>
            <div class="item-cont"><h3 class="h">샘표, … ‘양조간장 801’ 출시</h3></div>
            <div class="item-footer"><span class="date">2026.08.19</span></div>
          </a>
        </div>

  - 한 페이지 12건, **58페이지**. 2페이지부터는 주소가 달라진다:
      1페이지 = `/news/press-release`
      n페이지 = `/news/press/{n-1}`   (2페이지가 `/news/press/1`. 0부터 센다)
    1페이지를 `/news/press/0` 으로 요청하지 말고 그냥 원래 주소를 쓴다.
  - 상세는 `/news/view/{id}`. 목록의 `a.item-a` href 를 그대로 쓴다.
  - 날짜는 **일 단위**(`2026.08.19`)로 한 줄에 같이 온다. 상세를 받을 필요가 없다.

⚠️ **빈 `div.item` 이 페이지마다 3개씩 들어 있다.** 레이아웃 채움용인지 템플릿
   잔재인지는 모르겠으나 `a`·`h3`·`.date` 가 전부 없다. 세 개가 다 있을 때만 받는다.
   `len(d.css("div.item"))` 를 건수로 쓰면 12 가 아니라 15 가 나온다.

⚠️ **썸네일 파일명에 타임스탬프가 들어 있다** (`/image/KU/HV/20260908112202…`).
   전부 2026-09-08 로 같다 — 사이트 이관 때 한꺼번에 올라간 자국이지 기사 날짜가
   아니다(위 예시의 기사 날짜는 2026-08-19 다). notes/CANDIDATES-DIRECT2.md §6-2 가
   경고한 그 함정이다. **파일명에서 날짜를 줍지 마라.** `.date` 가 바로 옆에 있다.

**브랜드 축**: 한 피드에 샘표 본체 말고도 `차오차이`·`폰타나`·`질러`·`순작`·
`티아시아`·`새미네부엌`·`백년동안`·`연두` 가 섞인다. 전부 **샘표 자체 브랜드**라
`BRAND = "샘표"` 로 귀속해도 틀리지 않는다. hy프레딧처럼 남의 브랜드 상품을 파는
구조가 아니다(notes/CANDIDATES-DIRECT2.md §6-2 와 다른 상황이다).
`desc` 에서만 앞머리 브랜드명을 턴다.

신제품 판정 근거는 배지가 아니라 **기사 자체**다. 브랜드가 '출시'라고 낸 기사라서
is_new=True 로 둔다(같은 계보 전부와 같은 근거).

2026-10-01 에 10페이지 120건(2025-07-03 ~ 2026-09-08, 약 430일)을 받아 제목을
전수로 눈으로 훑고 조인 규칙을 맞췄다. 샘표 제목에서 확인한 함정:
  ① **상품 두 개를 따옴표 두 쌍으로 나란히 쓴다. 구분자가 없다.** 실측 4건:
       "샘표, ‘조선LA갈비양념’ ’조선고추장제육양념’ 출시"
       "샘표, ‘조선 갈비양념’ ‘조선 불고기양념’ 출시"
       "샘표 순작, ‘진쌍화차’ ‘진생강차’ 출시"
       "차오차이, 수타식 ‘직화 짜장면’ ‘유니 짜장면’ 출시"
     오뚜기의 `_TRAIL_SEP` 은 `·`·`,` 같은 **구분자**를 보는데 여기엔 공백뿐이라
     안 걸린다. 그냥 두면 둘 중 하나만(또는 첫 번째 것만) 상품으로 올라간다.
     더 나쁜 건 1번 예시다 — 두 번째 여는 부호가 `’`(U+2019) 라 `_SINGLE` 이
     쌍으로 못 읽고 **앞 상품 하나만** 집는다. 오뚜기 '칡냉면·쫄냉면' 과 같은 자국이다.
     → `_NEXT_QUOTE`(닫는 따옴표 바로 뒤에 또 따옴표가 열린다) 와
       '마지막 두 따옴표 사이가 공백뿐' 검사, 둘로 막는다. 4건 다 버려진다.
  ② '2종'·'4종' 기사가 잦다(제로슈거 드레싱 4종, 저당 디핑 소스 2종, 저당 장류
     4종, 저당 고기양념 2종, 아몬드&피넛 스프레드 2종). 오뚜기의 `\\d+종` 이 먹는다.
  ③ **'선보여' 가 상품이 아닌 데 쓰인다.** 실측 1건:
       "샘표, 창립 80주년 기념 ‘아트팩토리 프로젝트’ 선보여"   ← 미술 프로젝트
     `_SKIP` 에 '프로젝트' 한 단어를 더해 잡았다.

**_VERB 는 계보 그대로 두되 '제안'·'첫 선' 은 넣지 않았다.** GS25 는 실측으로
'제안'을 넣어 2건을 얻었는데, 샘표에서 '제안'을 쓰는 기사 5건은 **전부 레시피·
식생활 홍보**다("요리 소스 제안", "건강한 식생활 제안", "저당 테이블 제안",
"백숙삼계탕 육수 제안", "봄나물 요리법 제안"). 넓히면 5건이 통째로 오집된다.
반대로 계보의 '선봬·선보여·선보인다·론칭' 은 **오늘 데이터에서 얻는 게 0건**이고
(샘표는 거의 항상 '출시'를 쓴다) 유일하게 걸린 1건이 위 함정 ③ 이다. 그래도 지우지
않았다 — 같은 계보 5개 파일이 같은 _VERB 를 쓰고, 막은 건 _VERB 가 아니라 _SKIP 이다.

조인 결과 120건 중 **28건**이 남는다. 28건 전부 제목을 눈으로 대조했다(오집 0건).
최근 300일로 좁히면 **21건**이다. 월 4~6건으로, 보도자료형 중에서는 수집량이 가장
많다(동서식품 월 1~2건, GS25 연 10건 안팎).
버린 쪽도 전수로 훑었다. '출시/선보/론칭' 이 든 41건 중 13건을 버리는데
— 묶음 기사 5건(②), 상품 둘 1건(①, 나머지 3건은 300일 창 밖), 상품명에 `·`·`&` 1건,
따옴표가 아예 없는 2건("샘표, 홍게간장 출시", "폰타나, 제로 드레싱 발사믹 출시"),
'출시 기념 라이브' 1건, 나머지가 ③ 류다.
⚠️ **따옴표 없는 2건은 진짜 신제품인데 놓친다.** 상품명을 특정할 수 없어 버린다 —
   "홍게간장 출시" 에서 '홍게간장' 을 따 오려면 조사·수식어를 가르는 규칙이
   필요한데, 그건 못 믿을 걸 담는 쪽이라 놓치는 쪽을 골랐다(계보 전체의 방침이다).

**비식품은 어댑터에서 따로 표시하지 않는다.** 실측 1건
"샘표 질러, 'BEST 육포X키캡 키링 세트’ 한정 출시" 는 상품명에 '키링' 이 들어 있어
`base.is_nonfood()` 가 이름만으로 잡는다(확인함 → True). 동서식품의 '카누 바리스타
오아시스'(커피 머신)처럼 **이름만으로는 알 수 없는** 경우가 샘표엔 없어서
`_NONFOOD_TITLE` 을 두지 않았다. 새로 생기면 collectors/dongsuh.py 를 베껴라.

robots: `https://www.sempio.com/robots.txt` → **404 인데 본문이 HTML 이다**
        (`text/html`, 1,839B, 에러 페이지). 0바이트 404(= 규칙 부재, 오뚜기·아워홈)와
        다르다. 규칙을 읽을 수 없으므로 판정 불가로 보고 **간격을 보수적으로 잡았다**
        (DELAY=5.0, 이 레포 기본 2.2 의 두 배 이상).
        notes/CANDIDATES-DIRECT2.md §5-4·§7-⑤ 가 요구한 처리다.
약관: **있다. 그리고 복제·배포 제한 조항이 있다.** 푸터 →
      `https://member.sempio.com/legal/terms-and-condition` (40.8KB).
      「(새미네부엌 커뮤니티 서비스)… 웹사이트 방문자는 해당 홈페이지에 있는 정보를
      회사의 사전 승낙없이 복제, 송신, 출판, 배포, 방송 등 영리목적으로 이용하거나
      제3자가 이용하도록 해서는 안됩니다」
      크롤러·스크래퍼·매크로를 금지하는 조항은 **없다**(해당 단어 0회).
      조항이 '새미네부엌 커뮤니티' 절 안에 있고 '영리목적' 을 단서로 달고 있어
      보도자료실에 그대로 걸리는지는 애매하다. base.py 의 이마트24·도미노피자·폴바셋
      주석과 같은 성격이라 **BRANDS 등록 시 같은 블록에 적는 것을 권한다**
      (판단은 운영자 몫이다).
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "샘표"
SITE = "https://www.sempio.com"
LIST = SITE + "/news/press-release"   # 1페이지. 2페이지부터는 /news/press/{n-1}
PAGE_SIZE = 12       # 한 페이지 12건(빈 div.item 3개는 세지 않는다)
MAX_PAGES = 10       # 폭주 방지 상한. 300일 창은 7페이지면 덮인다.
DAYS = 300           # 이보다 오래된 보도자료는 신제품 섹션에 쓸모가 없다.
DELAY = 5.0          # robots 를 읽을 수 없다(HTML). 기본 2.2 보다 보수적으로 잡는다.

# --- 제목 → 상품명 (maker_ottogi 와 같은 규칙 + 샘표 함정 보강) ---------------
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_MULTI = re.compile(r"\d+\s*종")
_TRAIL_SEP = re.compile(r"^\s*[·∙,、/]")
# 함정 ① — 닫는 따옴표 바로 뒤에 또 따옴표가 열리면 상품이 하나가 아니다.
# 여는 부호로 `’`(U+2019) 를 쓰는 제목이 있어서 닫는 부호까지 전부 넣는다.
_NEXT_QUOTE = re.compile(r"^\s*[‘’'`]")

# 기사 자체가 신제품 기사가 아닌 경우. '출시'가 들어 있어도 버린다.
# '프로젝트' 하나가 샘표 실측 추가분이다(함정 ③ — '아트팩토리 프로젝트' 선보여).
# 나머지는 maker_ottogi 와 같다. 샘표의 비(非)상품 기사는 대부분 쿠킹클래스·봉사·
# 수상·MOU 인데 전부 _VERB 가 없어서 알아서 빠진다 — 단어를 더 넣어도 하는 일이 없다.
_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원", "프로젝트")
# 따옴표와 '출시' 사이에 이게 끼면 따옴표 안은 상품명이 아니라 제휴 상대다.
# ⚠️ 일부러 따옴표 '뒤쪽'만 본다. head 전체로 넓히지 마라 —
#    notes/QA-REPORT.md §2-6 이 시험하고 기각한 해법이다(GS25 채택분 2건이 죽는다).
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
# '출시' 뒤에 실적 문구가 붙으면 그 날짜는 출시일이 아니라 기사 작성일이다.
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")

# 기존 제품의 테마/에디션 패키지 기사. notes/QA-REPORT.md §2-6 이 세 브랜드 채택분
# 전수에 돌려 통과시킨 규칙 그대로다(틀린 2건만 버리고 맞는 9건은 전부 살았다).
# ⚠️ 샘표 120건에서는 빼도 결과가 같다 — 그런 기사가 아직 안 나왔을 뿐이다.
#    같은 계보 5개 파일이 같은 블록을 들고 있고, 이게 막는 꼴("‘A’ 테마 ‘B’ 출시")은
#    기존 제품을 신제품으로 올리는 가장 비싼 오집이다. 그대로 둔다.
_REPACK_HEAD = ("에디션", "라벨")                            # “…” 헤드라인 안
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")    # 따옴표와 따옴표 사이

# desc 앞머리에서 털 브랜드명. 전부 샘표 자체 브랜드다(위 '브랜드 축' 참고).
# 쉼표가 있을 때만 턴다 — "차오차이 ‘어향가지소스’ 출시" 처럼 쉼표가 없는 제목은
# 자르면 상품명까지 날아간다.
_DESC_HEAD = re.compile(
    r"^\s*(?:샘표|차오차이|폰타나|질러|순작|티아시아|새미네부엌|백년동안|연두|김치앳홈)"
    r"[^,]{0,12},\s*")


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열.

    "드레싱 4종 출시"처럼 기사 하나에 상품이 여럿이면 버린다. 억지로 '드레싱 4종'을
    상품명으로 쓰지 않는다. 따옴표 두 쌍이 나란히 붙은 것도 같은 이유로 버린다.
    """
    t = " ".join(title.split())
    # “…” 홍보 헤드라인 안에 에디션/라벨이 있으면 기존 제품의 패키지 기사다.
    if any(w in m.group(1) for m in _HEAD.finditer(t) for w in _REPACK_HEAD):
        return ""
    body = _HEAD.sub(" ", t)
    if any(w in body for w in _SKIP) or _MULTI.search(body):
        return ""
    # ‘A’ 테마 ‘B’ 꼴 — 마지막 두 따옴표 사이가 테마/에디션이면 B 는 기존 제품이다.
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
    if not quoted or any(w in head[quoted.end():] for w in _BETWEEN):
        return ""
    rest = head[quoted.end():]
    # 닫는 따옴표 바로 뒤가 구분자거나 또 다른 따옴표면 상품이 더 이어진다(함정 ①).
    if _TRAIL_SEP.match(rest) or _NEXT_QUOTE.match(rest):
        return ""
    # ‘A’ ‘B’ 꼴 — 마지막 두 따옴표 사이가 공백뿐이면 나란히 쓴 두 상품이다(함정 ①).
    hq = list(_SINGLE.finditer(head))
    if len(hq) >= 2 and not head[hq[-2].end():hq[-1].start()].strip():
        return ""
    name = quoted.group(1).strip(" ,·∙")
    if len(name) < 2 or any(c in name for c in "·∙&?"):
        return ""
    return name


def _date(s: str) -> str:
    """'2026.08.19' → '2026-08-19'. 월·일 범위를 검증한다.

    범위를 안 보면 UUID 조각(`2026/06/92`)이 날짜로 둔갑한다(다른 브랜드에서 실측).
    """
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})\s*$", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _abs(path: str) -> str:
    path = (path or "").strip()
    if not path:
        return ""
    return path if path.startswith("http") else SITE + path


def _rows(html: str) -> list[tuple]:
    """목록 HTML → (날짜, 제목, 상세주소, 이미지주소) 목록.

    빈 `div.item` 이 페이지마다 3개씩 섞여 있다. 셋 다 있을 때만 받는다.
    """
    out = []
    for node in HTMLParser(html).css("div.item"):
        a = node.css_first("a.item-a")
        h = node.css_first("h3.h")
        d = node.css_first(".item-footer .date")
        if not (a and h and d):
            continue
        img = node.css_first(".item-thumb img")
        out.append((
            _date(d.text(strip=True)),
            " ".join(h.text().split()),
            _abs(a.attributes.get("href") or ""),
            # ⚠️ 파일명의 숫자는 기사 날짜가 아니다. 날짜는 위 .date 에서만 읽는다.
            _abs((img.attributes.get("src") or "") if img else ""),
        ))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            # 1페이지만 주소가 다르다. 2페이지가 /news/press/1 이다(0부터 센다).
            url = LIST if page == 1 else f"{SITE}/news/press/{page - 1}"
            r = base.retry(lambda: c.get(url))
            r.raise_for_status()
            rows = _rows(r.text)

            # 셀렉터가 바뀌면 조용히 0건이 되는 게 제일 나쁘다. 1페이지는 반드시
            # 기사가 와야 한다(58페이지짜리 아카이브다). 안 오면 드러낸다.
            if page == 1 and not rows:
                raise ValueError(
                    f"샘표 보도자료 1페이지가 비었다. {url} → {len(r.content)}B, "
                    f"div.item {len(HTMLParser(r.text).css('div.item'))}개 — "
                    f"목록 셀렉터(div.item / a.item-a / h3.h / .item-footer .date)가 "
                    f"바뀌었는지 확인하라")
            if not rows:
                break

            for released, title, url_view, image in rows:
                if released and released < floor:
                    continue
                name = _pick(title)
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    # 기사 제목이 그대로 설명이 된다. 앞의 브랜드명만 턴다.
                    desc=_DESC_HEAD.sub("", title),
                    image=image,
                    released_at=released,
                    is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                    url=url_view,
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            # 목록은 날짜 내림차순이지만(120건 전수 확인) 같은 계보대로 기사 하나가
            # 오래됐다고 끊지 않는다. 페이지에서 가장 새 기사까지 기준일보다
            # 오래됐을 때만 멈춘다.
            fresh = [d for d, _, _, _ in rows if d]
            if fresh and max(fresh) < floor:
                break
            if len(rows) < PAGE_SIZE:
                break
    return items
