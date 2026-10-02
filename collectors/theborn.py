"""더본코리아 외식 브랜드 — 보도자료에서 신제품과 출시일만 뽑는다.

**먼저 알아야 할 것: 더본코리아 브랜드 사이트에는 신제품 신호가 없다.**
2026-10-02 에 현재 운영 중인 대표 브랜드 20개를 전부 열어 실측했고, 상품 목록을
긁을 수 있는 곳은 많지만 **'이게 새 상품이다'라고 말해주는 자리가 어디에도 없다.**
그래서 메뉴판을 긁는 어댑터는 만들지 않는다. 자세한 근거는 아래 §2.

남은 경로는 본사 보도자료 하나뿐이고, 이건 오뚜기·오리온·GS25 와 **같은 종류의
소스**다. 그래서 그 셋의 규칙을 그대로 가져와 더본 제목 버릇에 맞게 조인다.

**이 모듈은 브랜드가 18개다.** 한 목록에서 브랜드를 가려내는 구조라 파일을 쪼갤
수 없다(본아이에프 선례). 그래서 BRAND 상수 대신 BRANDS 목록을 내보낸다.
대표 브랜드 20개에서 **빽다방**(collectors/cafe_paikdabang.py)과
**한신포차**(collectors/hanshinpocha.py)를 뺀 수다. 둘은 자기 사이트에 쓸 만한
신호가 있어 따로 있고, 한 브랜드를 두 어댑터에 걸치면 같은 키가 두 번 들어간다
(collect.main 은 어댑터 사이 중복을 걸러주지 않는다).

─────────────────────────────────────────────────────────────────────────────
§1. 수집 경로. 2026-10-02 실측.

  목록  GET https://www.theborn.co.kr/theborn-notice/news-or-media/?npage=N
        9건/페이지, 24페이지(211건, 2013-02-08~2026-09-22). SSR 이라 브라우저 불필요.
        쿠키·토큰·리퍼러 없이 열린다.
  ⚠️ 목록 li 안에 **기사 본문이 통째로 들어 있다.** `<p class="max-lines">` 는
     CSS(-webkit-line-clamp)로 두 줄만 보이게 자를 뿐 HTML 에는 전문이 있다.
     그래서 상세 페이지를 따로 받지 않는다(오리온은 제목이 잘려서 상세를 받아야
     했는데 여기는 제목도 본문도 안 잘린다). 요청이 4~5회로 끝난다.
  ⚠️ '미디어' 탭(/theborn-notice/media/)은 `.ne_med` 가 **0건**이다. 빈 탭이고
     npage 목록은 뉴스 전용이다. 둘을 합칠 걱정은 없다.

날짜는 목록의 게시일(`2026.09.22`)을 released_at 에 그대로 쓴다. GS25·오리온과
같은 근거다 — 브랜드가 '출시한다'고 낸 글이고 그 글의 날짜다.
⚠️ 본문에 `📌출시일 : 9/3(목)` 처럼 실제 출시일이 적힌 경우가 있다(롤링파스타
   2026-09-10 기사, 게시일보다 7일 이르다). 그래도 안 쓴다 — 창에 들어온 6건 중
   1건에만 있고, 연도가 안 적혀 있어 우리가 연도를 채워 넣어야 한다. 날짜를
   지어내지 않는다는 이 레포 방침에 걸린다. 7일 오차를 안고 게시일을 쓴다.

§2. 브랜드 사이트를 왜 안 긁는가 (2026-10-02 실측, 20개 전수).

  브랜드가 어디에 사는지부터 갈린다.
    · 자체 도메인 10개 — 역전우동0410·빽다방·롤링파스타·한신포차·백스비어·
      새마을식당·리춘시장·원조쌈밥집·돌배기집·미정국수0410.
      대부분 WordPress 4.7~4.9 고 메뉴가 SSR 이다.
      ⚠️ 리춘시장(licun8888.com)은 사실상 죽었다 — https 는 인증서 호스트명이
         안 맞고 `https://licun8888.com` 은 paikdabang.com 으로 떨어진다.
    · theborn.co.kr 내부 페이지 10개 — 빽보이피자·홍콩반점0410·제순식당·고투웍·
      홍콩분식·본가·인생설렁탕·막이오름·연돈볼카츠·성성식당.
      `#menu_list .item` 한 셀렉터로 전부 파싱된다(10개 합쳐 메뉴 158건).
  긁는 것 자체는 어느 쪽도 쉽다. 문제는 **신제품 신호가 0** 이라는 것이다.
    - NEW 배지가 없다. 'new' 문자열이 걸리는 자리를 전부 열어 봤는데 전부 가짜였다:
      CSS 클래스, `<!-- NEW SLIDE -->` 주석, `<title>한신메뉴</title>`(한신포차),
      그리고 성성식당의 이미지 **파일명** `05_이태리찜닭_new.jpg` 등 4건
      (2017/06 업로드분이고 카드 마크업은 다른 상품과 완전히 같다).
    - '신메뉴' 전용 탭/카테고리가 없다. 빽다방의 /menu/menu_new/ 같은 자리가
      어느 브랜드에도 없다. 섹션 제목을 전수로 떠도 `식사류/요리류`·`피자 PIZZA`·
      `계절메뉴` 뿐이고 '신메뉴' 섹션은 없다. 막이오름 `계절메뉴` 가 그나마
      가까운데 그 안 4건의 업로드 연월이 2023/03 과 2025/10 로 갈린다.
    - 상품별 날짜 필드가 없다. `#menu_list` 안에 쓰이는 속성이 class·id·src·alt
      넷뿐이고 `data-*` 가 하나도 없다. 가격도 전 건 빈 값이다.
  날짜 비슷한 것 셋을 쳐 봤고 **셋 다 가짜이거나 모자라서 버렸다**:
    ① 이미지 HTTP `Last-Modified` — **가짜다.** 업로드 경로와 어긋난다. 실측:
       /uploads/2025/12/꼬치어묵우동-1.jpg → 2026-02-27,
       /uploads/2026/07/치킨가라아게정식-1.jpg → 2026-10-01,
       /uploads/2018/04/08_야채튀김우동.jpg → 2025-03-27.
       서버 파일 mtime 이 재저장·이관으로 덮인 값이라 상품과 무관하다.
    ② `/wp-content/uploads/YYYY/MM/` 경로 — 연·월뿐이고 '일'이 없다. 없는 날짜를
       1일로 채우면 그건 우리가 지어낸 값이다(cafe_paikdabang.py 가 같은 이유로
       같은 신호를 버렸다).
    ③ WP REST `/wp-json/wp/v2/media` 의 `date` — 열리기는 하는데 **못 믿는다.**
       udon0410 은 `x-wp-total: 349` 인데 실제로 31건만 돌려주고 page=5 에서 400 이
       난다. 그 31건 중 6건은 date 와 업로드 경로의 연월이 아예 다르다
       (/uploads/2022/06/21_불오뎅.jpg → 2025-03-27). 현행 메뉴 이미지(2026/10)는
       응답에 아예 없다.
       theborn.co.kr 쪽은 아예 막혀 있다 — `/wp-json/wp/v2/types` 가
       post·page·attachment 셋뿐이라 브랜드 글의 커스텀 타입(`theborn_brand`)이
       REST 에 등록돼 있지 않다(`/wp-json/wp/v2/theborn_brand` → 404
       `rest_no_route`). 그 글에 붙은 첨부도 같이 가려져서
       `/wp-json/wp/v2/media?search=…` 가 `X-WP-Total: 2` 를 주면서 본문은 빈
       배열이다. sitemap 도 없다(/sitemap.xml·/wp-sitemap.xml 전부 404 폴백).
  결론: 브랜드 사이트는 **신제품 소스로 구조적으로 불가**다. 메뉴판을 통째로
  긁어 올리는 건 이 서비스의 용건이 아니다.
  🔴 **매장찾기 API(`theborndb.theborn.co.kr/wp-json/api/...`)는 쓰지 마라.**
     그 호스트의 robots.txt 가 `User-agent: * / Disallow: /` 다. 브랜드 ID 목록을
     주긴 하지만 상품도 날짜도 없고, 애초에 전 경로 금지다.

§3. 제목 → 브랜드·상품명.

  브랜드는 ALIAS 표로 가려낸다. **닫힌 집합이다** — 표에 없는 이름이 나오면 그 글은
  그냥 넘어간다. 이게 중요하다. 새 브랜드를 알아서 집어 오면 base.BRANDS 에 없는
  브랜드가 되어 `kind()` 가 KeyError 를 던지고, collect 는 어댑터 단위로 잡으므로
  **18개 브랜드가 통째로 실패한다.** 새 브랜드가 생기면 사람이 ALIAS·BRANDS 양쪽에
  넣는다.

  상품명은 두 갈래로 뽑는다(2026-10-02, 211건 전수 대조).
    ⓐ `N종` 이 제목에 있으면 **여럿**이다. `N종(A, B, …)` 꼴 괄호 목록을 제목에서
       먼저, 없으면 본문에서 찾고 **쉼표로 쪼갠 개수가 N 과 정확히 같을 때만** 쓴다.
       이 개수 일치가 이 어댑터에서 제일 센 자기검증이다. 실제로 걸러낸 예:
       빽보이피자 카카오프렌즈 기사는 본문에 `2종(치즈포텐 스테이크 피자, 오븐
       치즈김치볶음밥)` 과 `3종(▲피자박스 춘식 ▲배볼록 춘식 ▲피자파티 라춘)`
       두 개가 있는데, N=2 라서 굿즈 쪽이 자동으로 탈락한다.
       괄호 목록이 없으면 **본문 따옴표가 정확히 N개일 때만** 그걸 쓴다. 전수에서
       이 폴백이 걸린 건 빽보이피자 '신메뉴 3종 출시'(2025-12-17) 한 건뿐이고
       3개 전부 맞았다. 나머지 기사는 따옴표가 5~12개라 개수 불일치로 탈락한다.
    ⓑ `N종` 이 없으면 **하나**다. 제목의 마지막 따옴표 안을 쓴다.

  ⚠️ **'협업'·'콜라보'를 제목 금지어로 두면 안 된다.** 처음에 그렇게 짰다가
     역전우동 신메뉴 3건(열탄제육덮밥·구운어묵튀김우동·간장양념구이 덮밥)이
     통째로 날아갔다. 더본은 콜라보 신메뉴를 자주 낸다. 대신 GS25 선례대로
     **위치**로 가른다 — 따옴표 **뒤**에 협업어가 오면 따옴표 안은 제휴 상대지
     상품이 아니다.
       "역전우동, 장호준 셰프와 두번째 협업 '구운어묵튀김우동' 출시" → 뒤가 '출시' → 상품
       "빽보이피자, 피자업계 최초 '카카오프렌즈'와 협업 신메뉴 출시" → 뒤가 '와 협업' → 버림
  ⚠️ `_SKIP` 에 '한정 전국 판매'를 넣었다. 홍콩반점 '팔도 홍콩반점 N화 ○○편'
     시리즈(부대찌개짬뽕·돼지국밥짬뽕·애호박찌개짬뽕)가 그 꼴인데, 2주만 파는
     지역 한정 기획이고 제목이 '출시'가 아니라 '판매'다. 진짜 신상이긴 하지만
     행사성이 강해 담지 않는다. 같은 이유로 '출시 기념 … 할인 프로모션' 류도 뺀다
     (연돈 수제튀김 도시락 7종 2026-09-22, 홍콩반점 슈림프 투움바 짬뽕 2025-12-15).
     못 믿을 걸 담느니 놓치는 쪽이다.

§4. 수확량. 211건 전수에 돌려 22개 기사·32개 상품을 집었고 **32건 전부 눈으로
    대조했다(오집 0건)**. 기본 창(DAYS=300)에서는 6개 기사·10개 상품, 5개 브랜드
    (롤링파스타·새마을식당·역전우동0410·연돈볼카츠·빽보이피자)다. GS25 11건·
    오뚜기 15건·오리온 10건과 같은 급이다. 본사가 보도자료를 낼 만큼 민 상품만
    잡히고, 그래서 날짜가 정확하다.
    ⚠️ 등록은 18개 브랜드지만 실제로 상품이 나오는 브랜드는 그중 일부다. 보도자료가
    없는 브랜드(제순식당·고투웍·홍콩분식·성성식당 등)는 0건이 정상이다.

§5. 브랜드 목록을 어떻게 확정했나. `theborn.co.kr/brand/` 아래 세 축을 전부 떴다
    (셀렉터 `ul.brand_list > li.item`, 2026-10-02).
      대표 20 / 글로벌 9 / 테스트 1.
    ⚠️ li 에 텍스트도 img alt 도 없다. 브랜드명은 **링크 대상 페이지의 <title>**
       로만 알 수 있다(로고 파일명은 `logo.png`·`Untitled-2.png` 처럼 쓸모없는 게 섞여 있다).
    여기 등록한 18개는 **대표 20개 - 빽다방 - 한신포차**다(둘은 자기 어댑터가
    있다). 글로벌·테스트 축은 뺐다:
      · 글로벌 9개 — 7개가 대표 브랜드와 겹치는 해외용 사본이고, 5개는 메뉴가
        0건("등록된 메뉴가 없습니다")이다. 겹치지 않는 둘(백's 비빔밥·백철판)은
        대표 목록에도 창업센터 목록에도 없어 국내 운영 근거가 없다.
      · 테스트 1개(원키친) — `/brand/test/` 소속이고 창업안내·매장찾기 링크가
        아예 없다. 테스트 브랜드는 담지 않는다.
    ⚠️ 슬러그가 헷갈린다. 국내 홍콩반점은 `홍콩반점2`(하이픈 없음), 글로벌은
       `홍콩반점-2`(하이픈)다. 하이픈 쪽은 메뉴가 0건이라 예전 조사가 이걸 보고
       "홍콩반점은 메뉴가 없다"고 적어 뒀는데 **틀린 기록이다.**
    운영 상태 참고(보도자료 수집에는 영향 없음): 창업센터(start.theborn.co.kr)
    네비게이션이 세는 현행 가맹 모집 브랜드는 18개이고 **성성식당·홍콩분식**이
    빠져 있다(매장은 있고 모집만 없는 것으로 보인다).

robots: https://www.theborn.co.kr/robots.txt → 200, text/plain, 전문 23바이트.
        `User-agent: *` / `Allow: /`. 금지 경로가 하나도 없다. 이미지
        (/wp-content/uploads/)도 허용이라 오리온·GS25 와 달리 이미지 URL 을
        담는 데 제약이 없다.
약관: 푸터 법적 링크가 `/agreement/` 하나뿐이고 그건 **개인정보처리방침**이다.
      웹사이트 이용약관 페이지가 없다. 크롤러·스크래퍼·복제 금지 조항을 찾지
      못했다(2026-10-02 전문 확인).
"""
import html
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

SITE = "https://www.theborn.co.kr"
LIST = SITE + "/theborn-notice/news-or-media/"
MAX_PAGES = 8        # 한 페이지 9건. 폭주 방지 상한(DAYS=300 이면 보통 4페이지에서 끝난다).
DAYS = 300
DELAY = 2.0          # robots 에 Crawl-delay 는 없다. 요청이 4~5회뿐이라 여유를 둔다.

# 기사 제목이 쓰는 이름 → 레지스트리에 등록된 브랜드명.
# **닫힌 집합이다.** 여기 없는 브랜드는 집지 않는다(§3 참고).
# 한 제목에 여러 브랜드가 나오면 **먼저 나온 쪽**이 주인공이다
# ("빽보이피자, 홍콩반점과 협업 …" → 빽보이피자).
ALIAS = {
    "역전우동0410": "역전우동0410", "역전우동": "역전우동0410",
    "홍콩반점0410": "홍콩반점0410", "홍콩반점": "홍콩반점0410",
    "미정국수0410": "미정국수0410", "미정국수": "미정국수0410",
    # 연돈볼카츠와 연돈튀김덮밥은 같은 브랜드의 두 간판이다. 보도자료가 둘을
    # 섞어 쓰고 2026-09-22 기사는 '연돈튀김덮밥/연돈볼카츠' 로 병기한다.
    "연돈볼카츠": "연돈볼카츠", "연돈튀김덮밥": "연돈볼카츠",
    "빽보이피자": "빽보이피자", "롤링파스타": "롤링파스타",
    "새마을식당": "새마을식당",
    # 한신포차는 일부러 넣지 않는다. 자기 사이트가 상품별 날짜를 줘서
    # collectors/hanshinpocha.py 가 따로 맡는다. 두 어댑터가 같은 브랜드를
    # 뱉으면 collect 가 같은 키를 두 번 담는다.
    "리춘시장": "리춘시장", "막이오름": "막이오름",
    "인생설렁탕": "인생설렁탕", "돌배기집": "돌배기집",
    "제순식당": "제순식당", "고투웍": "고투웍", "홍콩분식": "홍콩분식",
    "성성식당": "성성식당", "본가": "본가",
    # 자기 사이트(paiksbeer.com)가 전부 '백스비어' 로 쓴다. 'ㅃ' 표기는 못 봤지만
    # 더본의 다른 브랜드가 전부 '빽' 이라 오타가 날 자리라 둘 다 받는다.
    "백스비어": "백스비어", "빽스비어": "백스비어",
    # 자기 사이트 og:title 과 창업센터 네비게이션이 '원조쌈밥집' 이다
    # (og 는 '백종원의 원조쌈밥집'). 대표브랜드 목록의 로고 파일명만 '쌈밥' 이다.
    "원조쌈밥집": "원조쌈밥집", "쌈밥집": "원조쌈밥집",
    # 빽다방은 일부러 넣지 않는다(cafe_paikdabang.py 담당).
}

# 레지스트리가 등록할 브랜드명. 이 모듈이 뱉는 Item.brand 는 전부 이 안에 있다.
BRANDS = sorted(set(ALIAS.values()))

_VERB = re.compile(r"(출시|선보|선봬|론칭)")

# 상품 기사가 아닌 것. 제목만 보고 끊는다.
# '기념' 은 안 넣는다 — "출시 기념 할인" 은 '할인' 이 이미 잡고, 넣으면
# "5주년 기념 신메뉴 '버터갈릭파스타'" 같은 진짜 신상이 같이 죽는다.
_SKIP = ("할인", "프로모션", "이벤트", "행사", "쿠폰", "증정", "경품", "당첨",
         "캠페인", "안내", "1+1", "무료", "가격 조정", "판매 매장",
         "한정 판매", "한정 전국 판매", "챌린지", "ON AIR", "광고",
         "상륙", "지원", "사용", "가맹", "채용", "수상", "매출", "기부", "1주년")

# 따옴표 **뒤**에 이게 오면 따옴표 안은 제휴 상대지 상품이 아니다(§3 ⚠️).
_PARTNER = ("협업", "콜라보", "컬래버", "제휴", "와 ", "과 ")

# 홑·쌍따옴표를 다 받는다. 더본 보도자료는 ‘ ’ ' " “ ” 가 섞여 나오고,
# 닫는 따옴표를 여는 따옴표로 잘못 쓴 기사도 있다(빽보이피자 2025-12-17).
_QUOTE = re.compile(r"[‘'`“\"]([^’‘'`”\"]{2,30})[’‘'`”\"]")
# `2종(A, B)` · `신메뉴 3종 (A, B, C)`
_NPAREN = re.compile(r"(\d+)\s*종\s*\(([^)]{3,120})\)")
_NJONG = re.compile(r"(\d+)\s*종")

# 상품명이 아닌 것들. 따옴표 안이 상품명이 아닌 경우가 실제로 많다.
_BAD_WORD = ("신메뉴", "메뉴", "세트", "할인", "프로모션", "이벤트", "출시")
# 두 상품을 한 따옴표에 묶은 것·굿즈 글머리표. 오리온의 `·∙&?` 규칙과 같은 취지다.
_BAD_CHAR = "•·∙&?▲"

_DATE = re.compile(r"(20\d{2})\.(\d{1,2})\.(\d{1,2})")


def _clean(s: str) -> str:
    """제목에 <br> 이 박혀 있다. 태그를 털고 한 줄로 만든다."""
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", s or "")).split())


def _date(s: str) -> str:
    """'2026.09.22' → '2026-09-22'. 월·일 범위를 검증한다."""
    m = _DATE.search(s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _brand(title: str) -> tuple:
    """제목이 말하는 (브랜드, 제목에 쓰인 표기). 표에 없으면 ("", "")."""
    hits = [(title.index(k), -len(k), k) for k in ALIAS if k in title]
    if not hits:
        return "", ""
    said = min(hits)[2]
    return ALIAS[said], said


def _desc(title: str, said: str) -> str:
    """카드 설명. 기사 제목에서 앞머리의 회사명·브랜드명만 턴다.

    쉼표까지 자르는 식으로 하면 안 된다 — "롤링파스타 5,000원파스타 '레드페퍼
    오일파스타' 출시" 에서 `5,000` 의 쉼표가 먼저 걸려 설명이 '000원파스타…' 가 됐다.
    브랜드 표기만 정확히 떼고 뒤에 붙은 구두점을 턴다.
    """
    s = re.sub(r"^\s*더본코리아\s*", "", title)
    if s.startswith(said):
        s = s[len(said):]
    return s.lstrip(" ,·-–—") or title


def _name(s: str) -> str:
    """상품명으로 쓸 수 있으면 다듬어서, 아니면 빈 문자열."""
    n = (s or "").strip(" ,·∙'\"‘’“”")
    if not (2 <= len(n) <= 30):
        return ""
    if any(w in n for w in _BAD_WORD) or any(c in n for c in _BAD_CHAR):
        return ""
    if _NJONG.search(n):          # '여름 신메뉴 2종' 처럼 개수 표현이 남은 것
        return ""
    return n


def _pick(title: str, body: str) -> list:
    """기사 하나에서 상품명들을 뽑는다. 특정 못 하면 빈 목록(§3)."""
    if not _VERB.search(title) or any(w in title for w in _SKIP):
        return []

    m = _NJONG.search(title)
    if m:                                   # ⓐ 여럿
        n = int(m.group(1))
        if not (2 <= n <= 9):               # '3화'·'10종' 류는 상품 목록이 아니다
            return []
        for src in (title, body):
            for said, listed in _NPAREN.findall(src):
                if int(said) != n:
                    continue
                parts = [_name(x) for x in re.split(r"[,·∙/]", listed)]
                if len(parts) == n and all(parts):
                    return parts
        # 괄호 목록이 없을 때만. 개수가 정확히 N 일 때만 믿는다.
        quoted = [_name(x) for x in _QUOTE.findall(body)]
        if len(quoted) == n and all(quoted):
            return quoted
        return []

    quotes = list(_QUOTE.finditer(title))   # ⓑ 하나
    if not quotes:
        return []
    last = quotes[-1]
    if any(w in title[last.end():] for w in _PARTNER):
        return []
    one = _name(last.group(1))
    return [one] if one else []


def _rows(page_html: str) -> list:
    """목록 페이지의 기사들. (제목, 본문, 날짜, 링크, 이미지)."""
    out = []
    box = HTMLParser(page_html).css_first(".ne_med")
    if box is None:
        raise RuntimeError("`.ne_med` 목록 컨테이너가 없다 — 마크업이 바뀌었다")
    for li in box.css("li"):
        a = li.css_first("div p a")
        if a is None:
            continue
        body = li.css_first("p.max-lines")
        # 날짜는 div 안 마지막 <p> 다. 자리를 세지 않고 날짜꼴인 p 를 찾는다.
        stamped = [p for p in li.css("div > p") if _DATE.search(p.text() or "")]
        img = li.css_first("a img")
        out.append((
            _clean(a.html),
            " ".join((body.text() if body else "").split()),
            _date(stamped[-1].text()) if stamped else "",
            a.attributes.get("href", ""),
            img.attributes.get("src", "") if img else "",
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
            r = base.retry(lambda: c.get(LIST, params={"npage": page}))
            r.raise_for_status()
            rows = _rows(r.text)
            # 1페이지가 비는 건 '기사가 없다'가 아니라 파서가 깨진 것이다.
            # 더본 보도자료는 2013년부터 211건짜리 아카이브다. 조용히 넘기지 않는다.
            if page == 1 and not rows:
                raise RuntimeError(
                    "더본코리아 보도자료 1페이지가 0건 — 목록 마크업이 바뀌었다")
            if not rows:
                break

            for title, body, released, url, image in rows:
                if released and released < floor:
                    continue
                brand, said = _brand(title)
                if not brand:
                    continue
                for name in _pick(title, body):
                    it = Item(
                        brand=brand,
                        name=name,
                        # 기사 제목이 그대로 설명이 된다. 앞의 브랜드명만 턴다.
                        desc=_desc(title, said),
                        image=image,
                        released_at=released,
                        is_new=True,       # 브랜드가 '출시'라고 낸 기사다
                        url=url,
                    )
                    if it.key not in seen:
                        seen.add(it.key)
                        items.append(it)

            # 목록은 게시일 내림차순이다(211건 전수 확인). 그래도 오리온·GS25 와
            # 같이 '페이지에서 가장 새 기사까지 오래됐을 때'만 끊는다.
            fresh = [d for _, _, d, _, _ in rows if d]
            if fresh and max(fresh) < floor:
                break
    return items
