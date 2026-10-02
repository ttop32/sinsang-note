"""크라운제과 — 보도자료에서 신제품과 출시일을 뽑고, 신제품 카테고리에서 사진만 얹는다.

오뚜기·오리온·샘표·해태제과식품과 같은 계보다(보도자료 제목 → 상품명).
조인 규칙은 `collectors/maker_orion.py` 것을 그대로 가져왔다.

**왜 두 경로를 쓰나.** 크라운은 신제품 전용 카테고리와 보도자료를 둘 다 가지고
있는데 **한쪽엔 날짜가 없고 한쪽엔 사진이 없다.**

  ⓐ 제품 카탈로그    `GET /product/index?searchCateCd=<코드>`      200 / 21~27KB
     카테고리 5개 합쳐 약 130KB. 제품 사진이 `/upload/system/product/…` 로
     붙어 있다. **날짜가 없고, 수십 년 된 상품이 그대로 들어 있다.**
  ⓑ 보도자료 검색    `POST /sns/news  searchText=출시`            200 / 2,334,980B
     총 520건 중 '출시' 75건. `<td class="cnt">2026-08-25</td>` 로 **날짜를 준다.**
     **사진은 `data:image/jpeg;base64,…` 인라인이라 쓸 수 없다.**

→ **날짜와 상품명은 ⓑ 가, 사진은 ⓐ 가 준다.** 이름을 공백 없이 맞춰 이어 붙인다
  (보도자료 `‘초코츄러스’` ↔ 카탈로그 `초코 츄러스`. 띄어쓰기만 다르다).
  ⓐ 에만 있고 보도자료가 없는 상품은 **날짜가 없으므로 올리지 않는다.**
  카탈로그의 '신제품' 탭은 사람이 손으로 관리하는 배지라, 날짜 없이 그대로 믿으면
  해태 `productNewIconYn`(2024년 상품이 아직 true)과 같은 사고가 난다.

⚠️⚠️ **대역폭 — 이게 이 브랜드의 진짜 비용이고, 설계를 지배한다.**
  썸네일이 전부 `data:image/jpeg;base64,…` 인라인이라 **한 행에 1~3MB** 가 붙는다
  (base64 를 들어내면 10.8MB 본문이 21,244B 로 줄어든다).
  **목록을 통째로 받으면 1페이지 10,821,476B · 2페이지 1.65MB · 3페이지 1.51MB
  = 300일 창에 약 14MB** 다. 이 레포에서 가장 비싼 어댑터였다.

  → **서버 검색으로 바꿔서 5,697,564B(−59%)로 줄였다. 수집 결과는 5건 그대로다.**
    `theForm` 에 `searchText` 가 있다. ⚠️ **POST 로만 먹는다** — 같은 값을 GET
    으로 보내면 **200 에 0건(18,655B)** 이 와서 "검색 기능이 없다" 로 읽기 딱 좋다.
    동사별 실측(2026-10-02, 1페이지):

      출시  2,334,980B / 총 75건 / 10행 (2025-11-19 ~ 2026-07-31)
      론칭  3,184,185B / 총  1건 /  1행 (빅콘)
      런칭     18,609B / 총  0건
      선봬     18,940B / 총  1건 (2005년 기사)
      선보     19,275B / 총  2건 (2010년 기사)
      카탈로그(사진) 5종 합계 121,575B
      ─────────────────────────────── 합계 5,697,564B

    **'출시' 1페이지가 8개월을 덮는다**(필터링되어 행당 날짜 간격이 넓어진다).
    그래서 `MAX_PAGES = 1` 이면 충분하다 — 통짜 목록이 3페이지 필요하던 창을
    1페이지로 덮는다.

  → **더 줄일 방법은 없다. 세 가지를 다 재 보고 적는다.**
    ① **더 가벼운 엔드포인트** — 없다. `sitemap.xml`·`/rss`·`/sns/news/rss` 전부
       404(1,986B 공용 에러 페이지). `m.crown.co.kr` 은 www 와 같은 IP 인데
       인증서가 호스트명 불일치라 못 쓴다. 보도자료의 `searchCateCd`(제품뉴스)는
       **셀렉트가 주석 처리돼 죽어 있다**(아래 참고).
    ② **스트리밍 조기 중단** — 효과가 거의 없다. 행이 이미지와 **번갈아** 놓여
       있고 **날짜 `<td>` 가 자기 행 이미지 뒤**에 온다. 통짜 1페이지에서 행이
       끝나는 지점을 재 보면 0.3MB · 3.1MB · 6.4MB · 9.6MB … 로 흩어져 있고,
       '론칭' 결과는 **단 1행인데 날짜가 바이트 99.9% 지점**(3,180,550/3,184,185)
       이다. 그래도 **폭주 방지로는 쓴다** — `MAX_BYTES` 로 한 요청을 끊는다.
    ③ **파싱 전에 base64 털기** — 한다(`_DATAURI`). 전송량은 안 줄지만 파서에
       10.8MB 대신 21KB 를 넘기게 되어 메모리·시간이 준다.
    → 남은 비용의 대부분은 **'론칭' 3.18MB 한 요청**이고, 그게 `빅콘` 1건을
      가져온다. 빼면 2.5MB 가 되지만 진짜 신제품을 잃는다. 안 뺀다.

  → **`data:` 썸네일은 절대 Item.image 에 담지 마라.** `base.derive()` 는
    `http://` 만 버리므로 `data:` 는 그대로 통과해 products.json 에 수백 KB 짜리
    문자열이 박힌다.

⚠️ **이미지 파일명의 `YYMMDD` 를 날짜로 쓰지 마라.**
     /upload/system/product/…_260416 초코 츄러스1.7k 입체이미지 (2).jpg
   파일명은 **260416** 인데 보도자료 출시일은 **2026-06-16** 이다 — 두 달 차다.
   디자인 시안 날짜지 출시일이 아니다. (해태는 반대로 파일명이 하루 **늦다**.
   롯데칠성 어댑터의 "이미지 경로 = 업로드 시각" 규칙을 여기 복사하면 틀린다.)

⚠️ **상세 주소는 진짜로 있다.** 다른 제조사와 달리 404 가 제대로 돌아온다 —
     /sns/news/view?idx=88278      200 / 119,659B   (상세는 base64 1장뿐이라 가볍다)
     /product/view?idx=393         200 /  23,209B
     /product/index/view?idx=393   404 /   1,986B   ← 없는 경로는 404 를 준다
   그래서 보도자료 상세를 Item.url 로 붙인다. 다만 **상세는 열지 않는다** —
   목록에 제목·날짜가 다 있다.
   ⚠️ **상세로 목록을 대신할 생각도 버려라.** 상세 하단에 이전/다음 글 idx 가
      `onclick="view('88277')"` 로 있어서 체인을 걸을 수는 있는데, **상세도 본문
      사진이 인라인 base64 라 건당 0.3~3.3MB** 다(실측 3홉 6,457,351B). 검색보다
      비싸다. 위 §대역폭 ①에 포함해 기각한 안이다.

⚠️ **숨은 탭을 `href` 로는 못 찾는다.** 신제품 카테고리 탭이
   `<a href="javascript:searchCate('1478063307');">` 라서 링크 수집에 안 걸린다
   (1차 조사가 놓친 이유다). `searchCateCd` 를 **GET 쿼리로 넣으면 그대로 열린다**
   — POST 폼인데 GET 도 받는다. 카테고리 코드 실측:
     1478063307 신제품 · all 전체 · 1478063272 비스킷 · 1478063299 케이크 ·
     1478063302 스낵 · 1478063306 캔디/초콜릿
⚠️ **보도자료의 `searchCateCd` 는 안 먹는다.** 목록 HTML 에 `0 기업뉴스 /
   1 제품뉴스 / 2 공지사항` 셀렉트가 **주석 처리된 채** 남아 있다. 실제로
   `?searchCateCd=1` 을 보내면 **200 에 0건**이 온다(18,618B, `<tr>` 헤더만).
   "0건이면 파라미터를 의심해라"의 반대 사례다 — 여기선 파라미터가 죽은 것이다.
   제품뉴스만 받을 방법은 없고, 제목으로 걸러야 한다.

**이 보도자료는 절반이 지주(크라운해태)의 메세나 기사다.** 30건 중 15건이
국악·조각·창신제·한음영재·디스크골프·눈꽃축제·도서출간이다.
**주어가 가르는 축이 또렷하다** — `크라운해태…` 로 시작하면 지주(버린다),
`크라운제과`·`크라운 <브랜드>` 면 제품이다. 키워드 역필터보다 이쪽이 정확해서
`_HOLDING` 으로 제목 머리를 먼저 본다.

**크라운에서 새로 보탠 조인 규칙 2개** (3페이지 30건 제목을 전수로 훑고 맞췄다):
  ① **따옴표 안이 '에디션' 이면 기존 제품의 한정판이다.** 계보의 `_REPACK_HEAD`
     는 “…” 헤드라인 안만 보는데 크라운은 상품명 자리에 그대로 쓴다 —
     `‘쿠크다스 우베에디션’ 출시`. `_REPACK_NAME` 으로 이름 자체를 본다.
  ② **따옴표 밖에 '에디션' 이 있어도 한정판이다.** `크라운 키커바, MZ 스페셜
     에디션 ‘피스타치오’ 출시` · `찐감자 스낵 어썸, 4번째 에디션 ‘체다치즈’ 출시`.
     둘 다 **따옴표 안은 맛 이름뿐**이고 상품은 기존 라인이다.
     → `_REPACK_MID`(계보) 를 '따옴표 둘 사이' 가 아니라 **따옴표 앞 전체**로도
       한 번 더 본다. 크라운에서만 넓힌 것이고 그 이유를 여기 적어 둔다.

조인 결과 3페이지 30건(2025-12-03 ~ 2026-10-01) 중 **최근 300일에서 5건**이
남는다. 전수로 눈을 대고 센 손실도 적어 둔다 — 버리는 진짜 신제품:
  · `크라운제과, 상큼한 여름 제철 과일 ‘살구 에디션’ 2종 출시`  (에디션 + 2종)
  · `크라운 빅파이, … 로컬 푸드 에디션 3탄 출격`                (에디션 + 따옴표 없음)
  · `크라운 신짱, '가마솥 누룽지'로 세번째 출격!`                (`출시` 동사 없음)
  · `크라운 버터와플, 프리미엄 에디션 이즈니생메르 와플 출시`     (에디션 + 따옴표 없음)
  전부 **에디션/따옴표 없음** 이라 계보 방침대로 놓치는 쪽을 골랐다.

robots: `https://www.crown.co.kr/robots.txt` → **404 + HTML 1,986B**
        (`<title>크라운제과</title>` 사이트 공용 에러 페이지). 0바이트 404
        (= 규칙 부재) 와 다르다 — 규칙을 읽을 수 없는 **'판정 불가'** 다
        (notes/CANDIDATES-MAKER.md §②). 운영자 판단으로 수집한다.
        위 `/product/index/view` 404 와 같은 페이지라 "robots 자리에 에러
        페이지가 온다"가 확정된다.
약관:   확인하지 않았다.
"""
import re
import time
from datetime import date, timedelta
from urllib.parse import quote

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "크라운제과"
SITE = "https://www.crown.co.kr"
NEWS = SITE + "/sns/news"                      # 보도자료 목록
PRODUCT = SITE + "/product/index"              # 제품 카탈로그(사진 전용)
# 카테고리 코드 전부 실측. ⚠️ `all` 은 이름과 달리 전체가 아니다 — 스낵 12건만
# 온다(26,776B). 그래서 코드를 하나씩 돈다. 다섯 번 합쳐 약 130KB 다.
# **이 카탈로그는 사진만 쓴다.** 신상 판정·날짜는 보도자료가 한다(위 docstring).
PRODUCT_CATES = ("1478063307",   # 신제품
                 "1478063272",   # 비스킷
                 "1478063299",   # 케이크
                 "1478063302",   # 스낵
                 "1478063306")   # 캔디/초콜릿
# 🔴 **목록을 통째로 받지 않는다. 검색으로 서버에서 걸러 받는다**(아래 §대역폭).
# `theForm` 에 `searchText` 가 있는데 **POST 로만 먹는다** — GET 으로 보내면
# 200 에 0건(18,655B)이 와서 "검색이 없다" 로 읽기 딱 좋다.
# 동사별 실측(2026-10-02, 1페이지):
#     출시  2,334,980B / 총 75건 / 10행 (2025-11-19 ~ 2026-07-31)
#     론칭  3,184,185B / 총  1건 /  1행 (빅콘. ⚠️썸네일 하나가 3MB다)
#     런칭     18,609B / 총  0건
#     선봬     18,940B / 총  1건 (2005년 기사)
#     선보     19,275B / 총  2건 (2010년 기사)
# `_VERB` 와 같은 낱말을 쓴다 — 서버 검색과 `_pick` 의 동사 집합이 어긋나면
# 조용히 빠지는 기사가 생긴다. 새 동사를 `_VERB` 에 넣으면 여기도 넣어라.
_SEARCH_TERMS = ("출시", "론칭", "런칭", "선봬", "선보")
MAX_PAGES = 1        # '출시' 1페이지가 이미 8개월을 덮는다(2025-11-19 ~).
# 한 요청이 가져올 수 있는 최대 바이트. 썸네일이 전부 인라인 base64 라 한 행에
# 1~3MB 가 붙는다. 넘치면 거기서 끊고 받은 데까지만 판다 — 잘린 마지막 행은
# `a.tit` 나 세 번째 `<td>` 가 없어서 저절로 버려진다.
MAX_BYTES = 6_000_000
DAYS = 300
DELAY = 2.2

# 지주 기사. 제목 머리가 이거면 제품 기사가 아니다(국악·조각·도서·창신제).
_HOLDING = re.compile(r"^\s*크라운해태")

# 인라인 썸네일. 파싱 전에 털어낸다 — 본문의 99.8% 가 이것이라 그냥 파서에
# 넘기면 메모리와 시간을 다 여기에 쓴다(10.8MB → 들어내면 21KB).
_DATAURI = re.compile(r"data:image/[a-zA-Z0-9.+-]+;base64,[A-Za-z0-9+/=]+")

# --- 제목 → 상품명 (maker_orion 과 같은 규칙 + 크라운 함정 보강) --------------
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭|런칭)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_MULTI = re.compile(r"\d+\s*종")
_TRAIL_SEP = re.compile(r"^\s*[·∙,、/]")
_NEXT_QUOTE = re.compile(r"^\s*[‘’'`]")

_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원", "프로젝트",
         # 크라운 실측 추가분. 지주의 메세나·행사 축이다.
         # ⚠️ `조각` 두 글자로 넣지 마라 — '조각케이크'·'조각치즈' 같은 상품명을
         #    문다. 메세나 기사는 전부 주어가 '크라운해태' 라 `_HOLDING` 이
         #    이미 잡으므로, 여기선 좁은 형태만 둔다.
         "국악", "조각전", "조각가", "창신제", "한음", "공연", "축제", "대회", "출간",
         # 국내 출시가 아닌 건 화면에 올리면 거짓이 된다.
         "日", "美", "글로벌", "수출", "해외")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")
_REPACK_HEAD = ("에디션", "라벨")
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")
_REPACK_NAME = ("에디션", "컬렉션", "한정판", "선물세트", "기획팩")


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열."""
    t = " ".join(title.split())
    if _HOLDING.match(t):
        return ""
    if any(w in m.group(1) for m in _HEAD.finditer(t) for w in _REPACK_HEAD):
        return ""
    body = _HEAD.sub(" ", t)
    if any(w in body for w in _SKIP) or _MULTI.search(body):
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
    if not quoted or any(w in head[quoted.end():] for w in _BETWEEN):
        return ""
    # 크라운 보강 ② — 따옴표 '앞' 에 에디션/한정판이 있으면 기존 라인의 변형이다.
    # 계보는 따옴표 둘 사이만 보는데 크라운은 따옴표가 하나뿐인 제목에서 쓴다.
    if any(w in head[:quoted.start()] for w in _REPACK_MID):
        return ""
    rest = head[quoted.end():]
    if _TRAIL_SEP.match(rest) or _NEXT_QUOTE.match(rest):
        return ""
    hq = list(_SINGLE.finditer(head))
    if len(hq) >= 2 and not head[hq[-2].end():hq[-1].start()].strip():
        return ""
    name = quoted.group(1).strip(" ,·∙")
    if len(name) < 2 or any(c in name for c in "·∙&?!"):
        return ""
    # 크라운 보강 ① — 이름 자체가 에디션이면 기존 제품의 한정판이다.
    if any(w in name for w in _REPACK_NAME):
        return ""
    return name


def _date(s: str) -> str:
    """'2026-08-25' → 그대로. 월·일 범위를 검증한다."""
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})\s*$", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _flat(s: str) -> str:
    """이름 맞춤용. 보도자료 ‘초코츄러스’ ↔ 카탈로그 '초코 츄러스' 는 띄어쓰기만 다르다."""
    return re.sub(r"\s+", "", s or "")


def _abs_image(src: str) -> str:
    """상품 사진 주소. 파일명에 한글·공백이 들어 있어 퍼센트 인코딩이 필요하다.

    ⚠️ **`/upload/` 로 시작하는 것만 받는다.** 그러지 않으면 `li.item` 안의 첫
       `<img>` 가 **'NEW' 배지 아이콘**(`/resources/image/web/common/img_tag_new.png?2`)
       이라 상품 사진 대신 배지가 담긴다. 2026-10-02 에 실제로 그렇게 나가서
       5건 중 3건의 이미지가 404 로 돌아왔다(아래 `?2` 함정과 겹쳐서).
    ⚠️ **쿼리(`?2`)를 인코딩하면 안 된다.** `quote()` 에 통째로 넘기면 `?` 가
       `%3F` 가 돼 서버가 파일명의 일부로 읽고 404 를 준다. 경로만 인코딩한다.
    ⚠️ `data:` 로 시작하면 버린다. 보도자료 썸네일이 전부 인라인 base64 인데
       `base.derive()` 는 `http://` 만 거르므로 여기서 막지 않으면 수백 KB 짜리
       문자열이 products.json 에 박힌다.
    """
    src = (src or "").strip()
    if not src or src.startswith("data:"):
        return ""
    if src.startswith("http"):
        return src if src.startswith("https://") else ""
    if not src.startswith("/upload/"):
        return ""          # NEW 배지·레이아웃 아이콘. 상품 사진이 아니다.
    path, sep, query = src.partition("?")
    return SITE + quote(path) + (sep + query if sep else "")


def _product_images(c) -> dict:
    """제품 카탈로그에서 {공백없는상품명: 사진주소} 를 만든다.

    **사진 전용이다.** 여기엔 수십 년 된 상품(죠리퐁·콘초·카라멜콘 땅콩…)이 그대로
    들어 있어서 신상 판정에는 못 쓴다. 상품명이 보도자료와 겹칠 때만 사진을 얹는다.
    """
    out = {}
    for i, cate in enumerate(PRODUCT_CATES):
        if i:
            time.sleep(DELAY)
        r = base.retry(lambda: c.get(PRODUCT, params={"searchCateCd": cate}))
        r.raise_for_status()
        for node in HTMLParser(r.text).css("li.item"):
            strong = node.css_first("strong")
            if not strong:
                continue
            name = " ".join(strong.text().split())
            # 첫 img 가 'NEW' 배지일 수 있다. 상품 사진(/upload/)을 찾아 쓴다.
            url = ""
            for img in node.css("img"):
                url = _abs_image(img.attributes.get("src") or "")
                if url:
                    break
            if name and url:
                out.setdefault(_flat(name), url)
    if not out:
        raise ValueError(
            f"크라운 제품 카탈로그가 비었다. {PRODUCT}?searchCateCd={PRODUCT_CATES[0]} "
            f"— li.item / strong / img 셀렉터가 바뀌었는지 확인하라")
    return out


def _rows(html: str) -> list[tuple]:
    """보도자료 목록 → (날짜, 제목, idx) 목록.

    ⚠️ 썸네일(`<img src="data:image/jpeg;base64,…">`)은 읽지도 않는다.
    """
    out = []
    for tr in HTMLParser(html).css("tr"):
        a = tr.css_first("a.tit")
        tds = tr.css("td")
        if not a or len(tds) < 3:
            continue
        onclick = a.attributes.get("onclick") or ""
        m = re.search(r"view\('(\d+)'\)", onclick)
        if not m:
            continue
        out.append((_date(tds[2].text(strip=True)),
                    " ".join(a.text().split()),
                    m.group(1)))
    return out


def _search(c, term: str, page: int) -> tuple:
    """보도자료를 `term` 으로 검색해 (행 목록, 받은 바이트) 를 돌려준다.

    ⚠️ **POST 여야 한다.** 같은 파라미터를 GET 으로 보내면 200 에 0건이 온다.
    ⚠️ 스트리밍으로 받아 `MAX_BYTES` 에서 끊는다. 썸네일이 인라인 base64 라
       한 행에 1~3MB 가 붙어서, 상한이 없으면 한 요청이 10MB 를 넘는다.
    """
    data = {"currentPageNo": str(page), "searchText": term,
            "tcate": "event", "idx": "", "searchRegion": ""}

    def once():
        buf = bytearray()
        with c.stream("POST", NEWS, data=data) as r:
            r.raise_for_status()
            for chunk in r.iter_bytes():
                buf += chunk
                if len(buf) >= MAX_BYTES:
                    break
        return bytes(buf)

    raw = base.retry(once)
    html = _DATAURI.sub("", raw.decode("utf-8", "replace"))
    return _rows(html), len(raw)


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    seen_idx = set()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    hits = 0          # 검색이 실제로 돌아갔는지(아래 가드)
    with base.client() as c:
        images = _product_images(c)
        for term in _SEARCH_TERMS:
            for page in range(1, MAX_PAGES + 1):
                time.sleep(DELAY)
                rows, _ = _search(c, term, page)
                hits += len(rows)
                if not rows:
                    break

                for released, title, idx in rows:
                    if idx in seen_idx:
                        continue
                    seen_idx.add(idx)
                    if released and released < floor:
                        continue
                    name = _pick(title)
                    if not name:
                        continue
                    it = Item(
                        brand=BRAND,
                        name=name,
                        # 기사 제목이 그대로 설명이 된다. 앞의 회사명만 턴다.
                        desc=re.sub(r"^\s*크라운(제과)?[^,]{0,12},\s*", "", title),
                        image=images.get(_flat(name), ""),
                        released_at=released,
                        is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                        url=f"{NEWS}/view?idx={idx}",
                    )
                    if it.key not in seen:
                        seen.add(it.key)
                        items.append(it)

                fresh = [d for d, _, _ in rows if d]
                if fresh and max(fresh) < floor:
                    break

    # 검색이 통째로 죽으면(POST 가 GET 으로 바뀌거나 필드명이 바뀌면) 200 에
    # 0건이 조용히 온다. 520건짜리 게시판에서 '출시' 가 75건이니 0 은 있을 수 없다.
    if not hits:
        raise ValueError(
            f"크라운 보도자료 검색이 0행이다. POST {NEWS} searchText="
            f"{'/'.join(_SEARCH_TERMS)} — POST 가 아니거나(GET 은 조용히 0건이다) "
            f"폼 필드명(searchText/currentPageNo/tcate)이 바뀌었는지 확인하라")
    return items
