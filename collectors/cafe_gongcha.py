"""공차(Gong Cha).

도메인부터 틀렸었다. 1차 조사가 `gongcha.co.kr` / `www.gongcha.co.kr` /
`gongchakorea.co.kr` 세 호스트를 때려 **전부 ConnectTimeout** 으로 '수집 불가'
판정을 냈는데, 셋 다 공차코리아의 **본 사이트가 아니다**(2026-10-03 재실측).
  gongcha.co.kr        443 이 ConnectTimeout. http 로는 200 이지만 515바이트짜리
                       '공차넷 고객 채널방' 안내 페이지다. 메뉴가 없다.
  www.gongcha.co.kr    위와 같은 문서.
  gongchakorea.co.kr   https·http 둘 다 ConnectTimeout. (메일 도메인으로만 산다 —
                       푸터의 고객센터 주소가 gongchakorea@gongchakorea.co.kr 이다.)
정답은 **gong-cha.co.kr**(하이픈) 이다. TLS 체인 정상, SSR, 쿠키·세션 불필요.
푸터에 `(주)공차코리아 대표이사 고희경 / 사업자등록번호 214-88-84534` 가 박혀 있어
공식 사이트가 맞다. 호스트 이름만 보고 끊으면 안 되는 사례다(탐앤탐스와 같다).

루트(`/`)는 유튜브 배경 영상에 '가맹문의 / 브랜드 소개' 두 칸짜리 스플래시다.
본체는 `/brand` 이하이고 메뉴는 두 갈래다.
  /brand/menu/product?category=<코드>   상품 카탈로그. 탭 9개, 합계 121건
  /brand/menu/new_menu                  '신메뉴' 면

⚠️ **신메뉴 면은 상품 목록이 아니다.** 캠페인 **포스터 5장**짜리 스와이퍼고,
각 슬라이드가 `/brand/menu/new_menu_detail?seq=31..35` 로 간다. 상세를 열어도
`<img src="/upload/new/<md5>.jpg">` **그림 한 장뿐**이다 — 상품명도, 가격도,
날짜도, alt 텍스트도 없다(alt="메뉴" 가 전부). 그림 안에 글자가 합성돼 있지만
컴포즈커피처럼 '배지 색 비율' 로 셀 수 있는 종류가 아니라 OCR 이 필요하다.
그래서 이 면은 **읽지 않는다.**

신제품 신호를 찾아본 결과 — **쓸 수 있는 게 없다.**

1. 탭 `001001` 이 "New 시즌 메뉴" 다. 주석 처리된 설명문까지 있다
   ("당신의 입맛을 사로잡을 신상! 가장 먼저 즐겨보세요!"). 그래서 이걸
   is_new 로 쓰려다 **세어 보고 접었다.**
     - 전체 121건 중 **52건(43.0%)** 이 이 탭이다. 탐앤탐스 17.6%·블루샥 4.3%
       와 자릿수가 다르다. 버거킹 31% 보다도 높다.
     - 탭 안이 13개 '시리즈' 로 묶여 있는데 **1년 반치 시즌 라인업이 통째로
       쌓여 있다.** 반례가 또렷하다 —
         · `저당 밀크티 시리즈` **16종**(no=1103~1118). 상설 저당 라인이다.
         · `더블 Matcha 시리즈` 4종 중 no=**1073·1074·1075** 로 이 탭에서
           **가장 오래된 id** 다. 상설 메뉴판의 `밀크티` 탭 최신 id(606)
           보다는 새롭지만, 신상이라 부를 물건이 아니다.
         · `브라운슈가 시그니처`·`시그니처 시리즈`·`빙수 쉐이크` 도 같은 처지다.
     설빙(시그니처 배지와 NEW 배지를 섞어 세어 2013년 인절미설빙이 신상이 된
     건)과 똑같은 함정이다. **탭 이름을 배지로 쓰지 않는다.**
2. 상품 카드에 배지 마크업이 없다. `<div class="figure">` 안에 `<img>` 앞으로
   빈 줄(조건부 슬롯)이 있지만 **9개 탭 121건 전부 비어 있다** — 버거운버거의
   `<span class="bub-card-new" hidden>` 과 달리 아예 아무것도 안 들어간다.
   페이지의 `new`/`New` 문자열은 전부 CSS 클래스·탭 코드다.
3. **날짜가 어디에도 없다.** 목록·상세·영양정보 어느 쪽에도 `20\\d\\d` 패턴이
   0건이다. 이미지 파일명은 md5 라 탐앤탐스식 타임스탬프도 못 쓴다.
   이미지 Last-Modified 는 쓰지 않는다(컴포즈커피 149건 일괄 선례).
4. 게시판 두 개를 확인했지만 둘 다 상품이 아니다.
     /brand/content/noticelist   32건. 운영 공지(앱 리뉴얼·결제수단·컵보증금).
                                 신메뉴 출시 글이 없다.
     /brand/content/eventlist    548건. 전부 카드사 할인·콜라보 프로모션이다.
                                 '빙수 쉐이크 보이스 키링 프로모션' 같은 것들로,
                                 상품으로 넣으면 왓더버거 1+1 글과 같은 사고가 난다.

그래서 **is_new·released_at·uploaded_at 을 전부 비운다.** 없는 신호를 지어내는
대신 collect 의 '어제 없던 게 오늘 있다' diff 에 맡긴다(Item docstring 의
마지막 경로). 합류 첫날은 121건이 통째로 baseline 이라 화면에 0건이고, 그 뒤
공차가 상품을 올리면 그날 잡힌다. `no` 가 등록 순 증가 id(최신 1149)라 순서로는
보이지만 날짜가 아니라서 정렬에도 안 쓴다.

요청은 **9회**다. 탭 목록을 페이지에서 긁어 쓰므로 탭이 늘어도 따라간다.
상세(`product_detail`)에 설명문이 있지만 121회를 더 때려야 해서 받지 않는다 —
목록이 이름·사진·상품별 주소를 다 준다. desc 는 비운다.

카테고리는 탭 이름을 그대로 넣는다. `no` 기준으로는 121건이 전부 단일 탭이라
겹치는 게 없어 보이지만, **같은 상품이 다른 no 로 두 탭에 들어간 게 1건** 있다
(`허니 자몽 블랙티` — 베스트셀러 no=584 / 프룻티&모어 no=551). no 로 접으면
못 잡으니 make_key 로 접는다. 그래서 수집량은 121 이 아니라 **120건**이다.

robots.txt(2026-10-03, 200): `user-agent: *` 에 `disallow: /thdadmin/` 과
`disallow: /upload/` 두 줄뿐이다. 우리가 때리는 `/brand/menu/` 는 안 걸린다.
`/upload/` 는 이미지 경로인데 **주소만 적어 보낼 뿐 받지 않는다**(배지 판정이
없어서 받을 이유가 없다).
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "공차"
# ⚠️ `www.` 를 빼면 안 된다. apex(`gong-cha.co.kr`)는 **A 레코드가 없다** —
# 2026-10-08 실측에서 자기 자신을 가리키는 CNAME 만 있어 DNS 가 안 풀리고
# `nodename nor servname provided` 로 죽는다. `www.gong-cha.co.kr` 은 200 이다.
# 그리고 `gongcha.co.kr`(하이픈 없는 쪽)은 공차가 아니다 — 다른 주소로
# 풀리고 ConnectTimeout 이다. 도메인을 줄여 적지 마라.
SITE = "https://www.gong-cha.co.kr"
LIST_URL = f"{SITE}/brand/menu/product"
DETAIL_URL = f"{SITE}/brand/menu/product_detail"
FIRST_CATEGORY = "001001"     # 탭 목록을 긁어올 출발점
MAX_CATEGORIES = 20           # 폭주 방지. 현재 9개.
DELAY = 2.0

# 탭 `<li><a data-cate="001006">밀크티</a></li>`. 첫 탭만 href 로 오고 나머지는
# data-cate 라 둘 다 본다. href 쪽은 `/brand/menu/product?category=001001` 모양이다.
_TAB = re.compile(r'<li[^>]*>\s*<a[^>]*?(?:data-cate="(\d+)"|href="[^"]*category=(\d+)[^"]*")'
                  r'[^>]*>(.*?)</a>', re.S)

# 상품 상세 주소. 목록이 주는 href 에는 `&scroll=y` 가 묻어 있어 그대로 두면
# 카드 링크에 스크롤 상태가 새어 나간다. category·no 만 뽑아 다시 짠다.
_NO = re.compile(r"category=(\d+)&no=(\d+)")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(src: str) -> str:
    if not src:
        return ""
    return src if src.startswith("http") else SITE + src


def _tabs(html: str) -> list:
    """(코드, 탭이름) 목록. 페이지가 주는 순서를 그대로 쓴다."""
    out, seen = [], set()
    for m in _TAB.finditer(html):
        code = m.group(1) or m.group(2)
        name = _clean(re.sub(r"<[^>]+>", "", m.group(3)))
        if code and code not in seen:
            seen.add(code)
            out.append((code, name))
    return out[:MAX_CATEGORIES]


def _cards(html: str, cat_name: str) -> list:
    items = []
    for a in HTMLParser(html).css("#product_list li a"):
        p = a.css_first(".text-a p")
        name = _clean(p.text()) if p else ""
        if not name:
            continue
        img = a.css_first("img")
        m = _NO.search(a.attributes.get("href", ""))
        items.append(Item(
            brand=BRAND,
            name=name,
            image=_abs(img.attributes.get("src", "") if img else ""),
            category=cat_name,
            # is_new 를 안 채운다(None). 탭 이름이 'New 시즌 메뉴' 라고
            # 43% 에 배지를 다는 건 설빙·퀴즈노스와 같은 사고다 — docstring 참고.
            url=f"{DETAIL_URL}?category={m.group(1)}&no={m.group(2)}" if m else "",
        ))
    return items


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST_URL, params={"category": FIRST_CATEGORY}))
        r.raise_for_status()
        tabs = _tabs(r.text)
        if not tabs:
            raise RuntimeError("공차 메뉴 탭을 못 찾았다 — 카탈로그 구조가 바뀌었다")

        pages = {FIRST_CATEGORY: r.text}
        for code, _name in tabs:
            if code in pages:
                continue
            time.sleep(DELAY)
            rr = base.retry(lambda code=code: c.get(LIST_URL, params={"category": code}))
            rr.raise_for_status()
            pages[code] = rr.text

    for code, name in tabs:
        for it in _cards(pages.get(code, ""), name):
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)

    # 9개 탭을 다 받으면 120건 안팎이다. 크게 모자라면 셀렉터가 깨진 것이다.
    if len(items) < 80:
        raise RuntimeError(f"공차 {len(items)}건 — 메뉴 목록 구조가 바뀌었을 수 있다")
    return items
