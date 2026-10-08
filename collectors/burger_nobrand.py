"""노브랜드버거 — 신세계푸드 브랜드 홈 **1요청**에 전체 메뉴가 다 있다.

`www.nobrandburger.com` 은 `https://www.shinsegaefood.com/nobrandburger/index.sf`
로 리다이렉트된다. 그 한 장이 647KB SSR 이고 메뉴 55건이 통째로 들어 있다.
브라우저·API·토큰 전부 불필요. 요청 1회.

⚠️ **TLS 를 verify=False 로 우회하지 않는다.** 앞선 조사 메모에는 두 호스트가
`CERTIFICATE_VERIFY_FAILED` 라 적혀 있었는데 2026-10-02 실측에서는 **재현되지
않는다.** 인증서가 2026-08-05 에 갱신됐고 체인이 완전하다(GlobalSign GCC R46
OV TLS CA 2025 → Root R46 → Root R3, `openssl s_client` 로 확인). `base.client()`
기본값(verify=True)으로 6회 연속 200 이다. `www.nobrandburger.com` 으로 걸어도
같은 곳으로 떨어지며 검증을 통과한다. 다시 깨지면 그때 `verify=False` 가 아니라
먼저 체인을 확인해라 — `notes/CANDIDATES-PIZZA-FASTFOOD.md` §5-5 방침이다.

## 상품은 속성에 들어 있다

카드가 `<a>` 가 아니라 JS 모달 버튼이고, 데이터는 버튼의 data-* 에 있다.

    <li class="menu_item new">
      <button class="menu_anch" onclick="openPop('popup-menu', this)"
        data-name="버크셔K 카츠</br>Berkshire K Katsu"
        data-img="2026/07/29/버크셔K카츠_단품_06.홈페이지(보정본).png"
        data-story='…설명…'>

`data-name` 은 **한글명과 영문명이 `</br>` 로 붙어 있다.** 그대로 쓰면 상품명에
영문이 들러붙으니 끊어서 `name` / `name_en` 으로 나눈다(구분자가 `</br>`·`<br/>`
둘 다 나온다 — 한 카드 안에서 섞인다). `data-story` 에는 `<br />` 과 색상
`<span>` 이 섞여 있어 태그를 벗긴다.

이미지 실주소는 `https://www.shinsegaefood.com/uimages/` + `data-img` 다. 파일명이
한글이라 퍼센트 인코딩해서 넣는다(인코딩 없이도 서버는 받지만, 우리 HTML 에
그대로 박히는 주소라 인코딩된 쪽이 안전하다). 2026-10-02 실측 200/157KB.

## 신제품 신호 — `li` 의 `new` 클래스다

🔎 **대문자 'NEW' 로 세면 0건이 나온다.** 이 페이지에는 `NEW`·`icon_new`·
`badge` 문자열이 한 번도 안 나오고, '신메뉴' 는 **파일명 한 곳**
(`신메뉴_06.홈페이지_주스_(1).png`)에만 있다. 신호는 소문자 클래스다.

55건의 `li.menu_item` 클래스 분포(2026-10-02 전수) —
`menu_item` 41 · **`menu_item new` 8** · `menu_item best` 5 · `menu_item kids` 1.

## 교차검증 — new 8건이 업로드일 상위 8건과 정확히 겹친다

`data-img` 경로 앞이 `YYYY/MM/DD` 라 상품마다 업로드일이 나온다. 55건을 날짜로
세웠더니 `new` 8건이 **전부 최신 구간**에 있었다.

| 날짜 | new | 상품 |
|---|---|---|
| 2026-08-13 | ✅ | 풀드포크 샐러드 · 아보카도 새우 샐러드 |
| 2026-07-29 | ✅ | 버크셔K 카츠 · 버크셔K 카츠 어니언 |
| 2026-07-28 | ✅ | 데일리 치킨 |
| 2026-06-30 | ✅ | 메이플 고구마 · 슈크림 츄러스 · 아이스 슈 |
| 2026-06-30 | ❌ | 크런치 새우볼 · 치즈스틱 ← 같은 날인데 배지가 없다 |
| 2026-06-12 이전 | ❌ | 나머지 45건 전부 |

`new` 가 붙은 것 중 2026-06-30 보다 오래된 건 **0건**이다. 배지와 날짜가
서로를 받쳐준다. 같은 2026-06-30 안에서도 3건만 붙은 걸 보면 배지는 날짜보다
세밀하게 관리되고 있다 — 일괄로 찍고 방치한 게 아니다.

⚠️ 날짜는 `released_at` 이 아니라 `uploaded_at` 이다. 2025-05-07 에 20건이
몰려 있는데 그건 사이트 개편 때의 일괄 재업로드다(`rules.untrust_bulk_dates`
가 알아서 무효화한다 — 그 브랜드 중앙값 2건의 10배를 넘는다).

배지 없는 카드는 `is_new=None` 이다. False 가 아니다 — 이 템플릿에는
'여긴 신메뉴 아님' 을 명시하는 표시가 없다(프랭크버거 `icon_none` 과 다르다).

## 담지 않는 것

상품별 주소가 없다. 카드가 `openPop('popup-menu', this)` 로 같은 페이지에
모달을 띄울 뿐이라 가리킬 URL 자체가 존재하지 않는다. `url` 은 비우고
`base.SITES` 폴백에 맡긴다. 가격은 페이지에 없다.

═══════════════════════════════════════════════════════════════════════════
## 두 번째 소스 — 신세계그룹 뉴스룸 (WP REST). 2026-10-08 합류

메뉴판은 **지금 파는 것**만 준다. 출시일이 없고(이미지 업로드일이 전부),
야구장 한정·시즌 한정처럼 메뉴판에 안 오르고 끝나는 상품은 아예 안 보인다.
노브랜드 버거를 운영하는 신세계푸드가 그룹 뉴스룸(WordPress)에 보도자료를
올리는데, 거긴 공개 REST API 가 키·쿠키 없이 열려 있다(2026-10-08 실측 200).

  GET https://shinsegaegroupnewsroom.com/wp-json/wp/v2/posts
      ?categories=11          보도자료 카테고리
      &search=노브랜드 버거    x-wp-total: 225
      &per_page=100&page=N
      &_fields=id,date,link,title,content

⚠️ **`date` 를 쓴다. `modified` 금지.** 받아 온 100건 중 **67건(67%)** 이 두
   값의 날짜가 다르고 최대 **716일**까지 벌어진다. `modified` 를 쓰면 2024년
   기사가 올해 신상이 된다(이 레포 공통 함정, 피자스쿨 2015년 치즈피자 사고).

**일괄 등록 흔적 — 없다.** 300일 창 51건이 **49개 서로 다른 날짜**에 있고 한
날짜 최대 2건이다. → 보도자료 건은 `released_at` 을 쓴다.
(메뉴판 쪽은 그대로 `uploaded_at` 이다. 2025-05-07 에 20건이 몰린 사이트
 개편 일괄 재업로드라 `rules.untrust_bulk_dates` 에 맡긴다 — 위 §교차검증.)

### 남의 브랜드 거르기 — 뉴스룸은 **그룹 전체** 신문이다

`search=노브랜드 버거` 에도 신세계푸드(비버거)·SSG닷컴·이마트·신세계그룹
기사가 섞여 온다. 두 관문을 둔다 —
  ① 제목 관문: 제목에 `노브랜드 버거`(띄어쓰기 자유) 또는 `NBB` 가 있어야 한다.
     300일 창 51건 중 **7건 탈락** — ‘스꾸하우스’ 팝업 2건, SSG닷컴 프로모션,
     이마트 고유가 지원금, 신세계그룹 랜쇼페 2건, 신세계푸드 두초크.
  ② 본문 머리 관문: 본문 앞 `NEWS_LEAD`(300)자 안에 `노브랜드` 가 나와야 한다.
     ①을 통과한 44건은 전부 통과했다(0건 탈락). 그래도 둔다 — 사촌 어댑터
     maker_shinsegaefood 에서 같은 관문이 실제로 1건을 잡았고, 제목 버릇이
     바뀌면 ①만으로는 모자란다. ⚠️ **'본문에 있다' 만으로는 못 거른다**:
     신세계푸드 스무디 팝업 기사도 본문 1,009자 뒤에 '노브랜드' 가 나온다.

### 제목이 시끄럽다 — GS25 계보의 '마지막 따옴표' 규칙을 쓴다

    “버거 먹고 캐릭터 굿즈 모으고”…노브랜드 버거, 게임 ‘애니모’ 협업 버거팩 출시
    ‘가성비 헤비급 버거’ 통했다…노브랜드 버거, ‘어메이징 더블 치즈’ 정식 출시
쌍따옴표 헤드라인을 지우고(`_HEAD`), **브랜드명 뒤부터만** 본다. 그러면 남는
홑따옴표는 상품명이다. 상품을 따옴표로 특정 못 하는 기사는 통째로 버린다
(`collectors/gs25.py` 와 같은 판단 — 억지로 '신메뉴 2종' 을 쓰지 않는다).
⚠️ 자르기 **전에** 제목 전체로 `_PR_SKIP` 을 돌린다. GS25 는 자르고 나서 봐서
   브랜드명 앞의 매출·돌파가 안 걸리는 구멍을 안고 있다고 적어 놨다.
⚠️ `인기`·`증가`·`확대`·`가격` 은 `_PR_SKIP` 이 아니라 `_PR_TAIL`(동사 뒤)에
   둔다. 사촌 어댑터가 2026-10-03 에 같은 이동을 하고 근거를 남겼다. 실증:
     노브랜드 버거, 랜더스무디 **인기** 잇는다…야구장 얼먹 디저트 ‘랜더슈’ 출시
   `인기` 를 제목 전체로 보면 이 진짜 신제품이 조용히 죽는다.
⚠️ `메뉴` 를 '따옴표~동사 사이' 금칙어로 두면 안 된다. `신메뉴` 에 걸려서
     신세계푸드 노브랜드 버거, 야구장 인기 간식 ‘레몬 크림 새우’ **신메뉴**로 출시
   가 죽는다(실측). 협업 기사는 `협업`·`컬래버` 가 이미 `_PR_SKIP` 에서 잡는다.

### 중복 — 메뉴판 이름이 정본이다. ⚠️ `make_key` 가 못 잡는 쌍이 있다

메뉴판 55건과 보도자료 7건의 이름을 **눈으로 대조**했다. 겹치는 5건 중 **3건은
`base.make_key()` 로 안 잡힌다** — 메뉴판이 `NBB ` 접두를 달고 있어서다:

  | 보도자료에서 뽑은 이름 | 메뉴판 정본        | make_key 로 잡히나 |
  |---|---|---|
  | 버크셔K 카츠       | 버크셔K 카츠           | ✅ 같다 |
  | 레몬 크림 새우     | 레몬 크림 새우         | ✅ 같다 |
  | 어메이징 더블 치즈 | **NBB** 어메이징 더블 치즈 | ❌ 못 잡는다 |
  | 어메이징 불고기    | **NBB** 어메이징 불고기    | ❌ |
  | 어메이징 더블 살사 | **NBB** 어메이징 더블 살사 | ❌ |

`NBB` 는 메뉴판 카테고리 이름이기도 하다(`NBB 어메이징` 칸). 보도자료는 그
접두 없이 쓴다. 그래서 **이 어댑터 안에서만** 쓰는 `_dupe_key()` 로 `NBB`
접두와 공백·중점·괄호를 털어 비교한다(`base.py` 는 손대지 않는다 —
`make_key` 를 바꾸면 전 브랜드가 영향을 받는다).
⚠️ `_dupe_key` 는 **보도자료 건을 거를 때만** 쓴다. 메뉴판 55건끼리의 중복
   판정에는 안 쓴다 — 접두를 털다가 메뉴판 항목끼리 충돌하면 건수가 준다.
   (현재 55건은 털어도 충돌 0건이지만, 규칙으로 막아 둔다.)

### 실측 결과 (2026-10-08, 300일 창)

  뉴스룸 51건 → 제목관문 44 → 본문관문 44 → `_pr_pick` 7건 →
  메뉴판과 겹치는 **5건 제거**(위 표) → 새로 **2건**.
    2026-07-02  랜더슈          야구장 한정 디저트. 메뉴판에 없다
    2025-12-30  고스트페퍼 버거  시즌 한정. 지금은 내려가 메뉴판에 없다
  합계 **55 → 57건.**
  ⚠️ 2건 다 메뉴판에 없는 '한정' 상품이다. 이게 이 소스를 붙인 이유다 —
     메뉴판만 보면 왔다 간 상품은 영영 안 보인다.
  ⚠️ `‘고스트페퍼 버거’ 2종` 처럼 `N종` 이 붙은 제목은 따옴표 안 이름을 그대로
     쓴다(라인 이름이지만 실재하는 상품명이다). 사촌 어댑터
     maker_shinsegaefood 의 `_COUNT_TAIL` 과 같은 판단이다.

robots: https://shinsegaegroupnewsroom.com/robots.txt — 200 / 133B / text/plain.
        `User-agent: *` / `Allow: /` / `Disallow: /*action=download_media_library_as_zip*`.
        `/wp-json/` 은 금지 목록에 없다.
        ⚠️ 사진 호스트 `images.shinsegaegroupnewsroom.com` 의 robots.txt 는
           **403(S3 AccessDenied XML)** 이다 — 404 가 아니다. robots 파일이 없는
           것으로 보고 본 도메인 방침을 따른다.
"""
import certifi
import html as htmllib
import pathlib
import ssl
import re
import time
from datetime import date, timedelta
from urllib.parse import quote

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "노브랜드버거"
ROOT = "https://www.shinsegaefood.com"
MENU_URL = ROOT + "/nobrandburger/index.sf"
IMG_BASE = ROOT + "/uimages/"
MAX_ITEMS = 300      # 폭주 방지. 현재 55건.

NEW_CLASS = "new"    # li.menu_item 에 붙는 소문자 클래스 (위 docstring)

# data-name 의 한·영 구분자. 한 페이지 안에 `</br>` 와 `<br />` 가 섞여 있다.
_BR = re.compile(r"<\s*/?\s*br\s*/?\s*>", re.I)
_TAG = re.compile(r"<[^>]+>")
_IMG_DATE = re.compile(r"^(\d{4})/(\d{2})/(\d{2})/")

# --- 두 번째 소스: 신세계그룹 뉴스룸 (공개 WP REST). docstring §두 번째 소스 ---
NEWS_SITE = "https://shinsegaegroupnewsroom.com"
NEWS_API = NEWS_SITE + "/wp-json/wp/v2/posts"
NEWS_CAT = 11              # '보도자료' 카테고리
NEWS_Q = "노브랜드 버거"    # 전문검색. 그룹 전체 신문이라 이것만 믿으면 안 된다
NEWS_FIELDS = "id,date,link,title,content"
NEWS_PER_PAGE = 100        # WP REST 상한
NEWS_MAX_PAGES = 3         # 폭주 방지 상한. 300일 창은 1페이지로 덮인다(실측)
NEWS_LEAD = 300            # 본문 머리 관문. 여기까지 '노브랜드' 가 나와야 한다
NEWS_DAYS = 300            # 이보다 오래된 보도자료는 신제품 섹션에 쓸모가 없다
NEWS_DELAY = 1.5

_TAGS = re.compile(r"<[^>]+>")
_FIRST_IMG = re.compile(r'<img[^>]+src="([^"]+)"', re.I)
# 제목 관문. 띄어쓰기가 들쭉날쭉이고 'NBB' 로만 쓰는 제목도 있다.
_IS_NBB = re.compile(r"노브랜드\s*버거|NBB")

# --- 보도자료 제목 → 상품명 (collectors/gs25.py 계보 + 노브랜드 함정 보강) ----
_PR_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭|런칭)")
_PR_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_PR_HEAD = re.compile(r"[“”\"]([^“”\"]*)[“”\"]")
# 브랜드명(주어)까지 떼고 그 뒤만 본다. 앞은 홍보 헤드라인이다.
_PR_SUBJECT = re.compile(r"^.*?[‘’'\"]?노브랜드\s*버거[’'\"]?\s*,?\s*")
_PR_TRAIL_SEP = re.compile(r"^\s*[·∙,、/]")
# 기사 자체가 신제품 기사가 아닌 경우. '출시'가 들어 있어도 버린다.
# ⚠️ `인기`·`증가`·`확대`·`가격` 은 여기 두지 마라 — `_PR_TAIL` 로 간다(위 docstring).
_PR_SKIP = ("가맹", "출점", "창업", "점포", "회원", "돌파", "누적", "완판",
            "매출", "영업이익", "성료", "수상", "선정", "채용", "협약", "체결",
            "후원", "기부", "추모", "공모", "발대식", "심포지엄", "박람회",
            "팝업", "캠페인", "발탁", "앰배서더", "재단", "경연", "시상",
            "간담회", "개최", "스폰서", "리뉴얼", "실적", "매진", "진행",
            "참가", "참여", "전개", "지원", "프로젝트", "이벤트", "광고",
            "할인", "선물", "프로모션", "기획전", "페스티벌", "서포터즈",
            "모집", "인하", "인상", "진출", "기념",
            # 협업·컬래버 기사는 상품이 아니라 제휴 상대를 따옴표에 넣는다.
            #   노브랜드 버거, 게임 ‘애니모’ **협업** 버거팩 출시   ← '애니모'는 게임
            #   … ‘무쇠팔’ **협업** 메뉴 출시                      ← '무쇠팔'은 셰프
            "협업", "컬래버", "콜라보",
            # 국내 출시가 아닌 건 화면에 올리면 거짓이 된다.
            "수출", "해외", "글로벌", "日", "美")
# 동사 뒤에 이게 붙으면 그 날짜는 출시일이 아니라 실적 기사 작성일이다.
_PR_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록",
            "연다", "쏜다", "증가", "확대", "가격")
# 따옴표와 동사 사이에 끼면 따옴표 안은 상품명이 아니다.
# ⚠️ `메뉴` 를 넣지 마라 — `신메뉴로 출시` 에 걸려 진짜 신제품이 죽는다(위 docstring).
_PR_BETWEEN = ("브랜드", "에디션", "테마", "시리즈", "전용 앱")
# 이름 자체가 상품이 아니라 묶음·행사인 경우.
#   ‘어메이징 더블 랜쇼페 **에디션**’ 출시   ‘**투게더팩**’ 출시(가정의 달 묶음)
#   ‘5K 런치**타임**’  ‘어메이징 NBB **데이**’  ‘와페모 **페스티벌**’
_PR_NOT_A_NAME = ("에디션", "시리즈", "세트", "콤보", "팩", "페스티벌",
                  "데이", "타임", "한정판", "기획")

# 중복 판정용 정규화. **이 어댑터 안에서만** 쓴다(base.py 는 손대지 않는다).
# 메뉴판은 `NBB 어메이징 더블 치즈`, 보도자료는 `어메이징 더블 치즈` 다.
_NBB_PREFIX = re.compile(r"^\s*(?:NBB|엔비비)\s+", re.I)
_FLAT = re.compile(r"[\s·∙・()（）\[\]]")


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


def _clean(s: str) -> str:
    return " ".join(_TAG.sub(" ", s or "").replace("&nbsp;", " ").split())


def _split_name(data_name: str) -> tuple:
    """`한글명</br>English Name` → (한글명, 영문명). 영문이 없으면 뒤는 빈 값."""
    parts = [p.strip() for p in _BR.split(data_name or "") if p.strip()]
    parts = [_clean(p) for p in parts]
    parts = [p for p in parts if p]
    if not parts:
        return "", ""
    if len(parts) == 1:
        # `주스 / Juice` 처럼 슬래시로 붙여 둔 것도 있다. 뒤가 라틴문자뿐이면 영문명이다.
        head, sep, tail = parts[0].partition(" / ")
        if sep and re.fullmatch(r"[A-Za-z0-9 &'().,\-]+", tail):
            return head.strip(), tail.strip()
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def _image(data_img: str) -> str:
    """`2026/07/29/버크셔K카츠….png` → 절대 주소. 파일명이 한글이라 인코딩한다."""
    if not data_img:
        return ""
    return IMG_BASE + quote(data_img.strip(), safe="/")


def _uploaded_at(data_img: str) -> str:
    m = _IMG_DATE.match((data_img or "").strip())
    return "-".join(m.groups()) if m else ""


def _dupe_key(name: str) -> str:
    """중복 비교용 이름. `NBB` 접두와 공백·중점·괄호를 턴다.

    `base.make_key()` 는 공백만 털기 때문에 `NBB 어메이징 더블 치즈`(메뉴판)와
    `어메이징 더블 치즈`(보도자료)를 다른 상품으로 본다. 실측 3쌍이 그랬다.
    ⚠️ 보도자료 건을 거를 때만 쓴다. 메뉴판끼리의 판정에는 쓰지 않는다.
    """
    return _FLAT.sub("", _NBB_PREFIX.sub("", name or ""))


def _plain(fragment: str) -> str:
    """WP 가 주는 HTML 조각 → 공백 정리된 평문."""
    return " ".join(htmllib.unescape(_TAGS.sub(" ", fragment or "")).split())


def _news_date(s: str) -> str:
    """'2026-07-02T09:10:00' → '2026-07-02'. 월·일 범위를 검증한다.

    범위를 안 보면 UUID 조각이 날짜로 둔갑한다(다른 브랜드에서 실측).
    """
    m = re.match(r"^\s*(20\d{2})-(\d{1,2})-(\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _pr_pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열.

    '신메뉴 2종 출시'처럼 기사 하나에 상품이 여럿이고 이름이 따옴표에 없으면
    버린다. 억지로 '신메뉴 2종'을 상품명으로 쓰지 않는다.
    """
    t = " ".join(title.split())
    body = _PR_HEAD.sub(" ", t)
    # ⚠️ 브랜드명 뒤로 자르기 **전에** 제목 전체로 본다(GS25 의 알려진 구멍 봉합).
    if any(w in body for w in _PR_SKIP):
        return ""
    b = _PR_SUBJECT.search(body)
    if b:
        body = body[b.end():]
    verb = None
    for m in _PR_VERB.finditer(body):
        verb = m
    if not verb or any(w in body[verb.end():] for w in _PR_TAIL):
        return ""
    head = body[:verb.start()]
    quoted = None
    for m in _PR_SINGLE.finditer(head):
        quoted = m
    if not quoted or any(w in head[quoted.end():] for w in _PR_BETWEEN):
        return ""
    # 닫는 따옴표 바로 뒤가 구분자면 상품이 더 이어진다.
    if _PR_TRAIL_SEP.match(head[quoted.end():]):
        return ""
    name = quoted.group(1).strip(" ,·∙")
    if len(name) < 2 or any(c in name for c in "·∙&?"):
        return ""
    if any(w in name for w in _PR_NOT_A_NAME):
        return ""
    return name


def _press_rows(rows: list, floor: str) -> list:
    """뉴스룸 응답 행 → (released, name, desc, image, url). 관문 통과분만."""
    out = []
    for row in rows:
        released = _news_date(row.get("date") or "")   # ⚠️ modified 가 아니다
        if not released or released < floor:
            continue
        title = _plain((row.get("title") or {}).get("rendered"))
        # ① 제목 관문 — 그룹 전체 신문이라 주어가 노브랜드 버거여야 한다.
        if not _IS_NBB.search(title):
            continue
        body = _plain((row.get("content") or {}).get("rendered"))
        # ② 본문 머리 관문 — 지나가는 언급과 주어를 가른다.
        pos = body.find("노브랜드")
        if pos < 0 or pos > NEWS_LEAD:
            continue
        name = _pr_pick(title)
        if not name:
            continue
        img = _FIRST_IMG.search((row.get("content") or {}).get("rendered") or "")
        out.append((released, name, title,
                    img.group(1) if img else "",
                    row.get("link") or NEWS_SITE))
    return out


def fetch() -> list[Item]:
    with base.client(verify=_ssl_context()) as c:
        r = base.retry(lambda: c.get(MENU_URL))
        r.raise_for_status()

    doc = HTMLParser(r.text)
    groups = doc.css(".menu_group")
    if not groups:
        raise RuntimeError(f"{MENU_URL}: .menu_group 이 0개다(마크업이 바뀌었다)")

    items: list[Item] = []
    seen = set()
    for g in groups:
        title = g.css_first(".menu_group_title")
        category = " ".join(title.text().split()) if title else ""
        for li in g.css("li.menu_item"):
            btn = li.css_first("[data-name]")
            if btn is None:
                continue
            name, name_en = _split_name(btn.attributes.get("data-name"))
            if not name:
                continue
            data_img = btn.attributes.get("data-img") or ""
            is_new = NEW_CLASS in (li.attributes.get("class") or "").split()
            it = Item(
                brand=BRAND,
                name=name,
                name_en=name_en,
                desc=_clean(btn.attributes.get("data-story")),
                image=_image(data_img),
                category=category,
                uploaded_at=_uploaded_at(data_img),
                is_new=True if is_new else None,
            )
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)
            if len(items) > MAX_ITEMS:
                raise RuntimeError(f"{BRAND}: 상품이 {MAX_ITEMS}건을 넘었다")

    if not items:
        raise RuntimeError(f"{MENU_URL}: data-name 에서 상품을 하나도 못 뽑았다")

    # ── 두 번째 소스: 신세계그룹 뉴스룸 보도자료 ─────────────────────────
    # 메뉴판을 **먼저** 돌린 뒤에 온다. 메뉴판 이름이 정본이고(`NBB 어메이징 …`
    # 처럼 접두가 붙은 정규 표기), 보도자료 이름은 그 변형이라 겹치면 버린다.
    # 겹침 판정은 `it.key` 와 `_dupe_key()` 둘 다 본다 — docstring §중복 표 참고.
    menu_norm = {_dupe_key(it.name) for it in items}
    floor = (date.today() - timedelta(days=NEWS_DAYS)).isoformat()
    with base.client() as c:
        for page in range(1, NEWS_MAX_PAGES + 1):
            if page > 1:
                time.sleep(NEWS_DELAY)
            r = base.retry(lambda: c.get(NEWS_API, params={
                "categories": NEWS_CAT, "search": NEWS_Q,
                "per_page": NEWS_PER_PAGE, "page": page,
                "_fields": NEWS_FIELDS}))
            r.raise_for_status()
            rows = r.json()

            # 225건짜리 아카이브다. 1페이지가 비면 카테고리 번호나 검색어,
            # 또는 WP REST 자체가 닫힌 것이다. 조용히 0건이 되게 두지 않는다.
            if page == 1 and not rows:
                raise RuntimeError(
                    f"신세계그룹 뉴스룸 1페이지가 비었다. {r.url} → "
                    f"{len(r.content)}B x-wp-total={r.headers.get('x-wp-total')!r} — "
                    f"categories={NEWS_CAT}(보도자료)·search={NEWS_Q} 나 "
                    f"/wp-json/wp/v2/posts 공개 여부가 바뀌었는지 확인하라")
            if not rows:
                break

            for released, name, desc, img, link in _press_rows(rows, floor):
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=desc,
                    image=img,
                    # 날짜가 49개로 흩어져 있다(한 날짜 최대 2건). 일괄 등록이
                    # 아니라서 메뉴판처럼 uploaded_at 으로 강등하지 않는다.
                    released_at=released,
                    is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                    url=link,
                )
                if it.key in seen or _dupe_key(name) in menu_norm:
                    continue
                seen.add(it.key)
                menu_norm.add(_dupe_key(name))
                items.append(it)

            fresh = [_news_date(row.get("date") or "") for row in rows]
            fresh = [d for d in fresh if d]
            if fresh and max(fresh) < floor:
                break
    return items
