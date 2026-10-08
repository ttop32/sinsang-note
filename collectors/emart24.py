"""이마트24.

/goods/list 는 헤더만 있는 껍데기라 쓸모없다. 실제 목록은 상품 3개 섹션
(행사 상품 / 차별화 상품 / Fresh Food)이 각각 서버렌더로 뿌린다. 브라우저 불필요.
섹션당 전체는 수십 페이지라 신상만 보는 이 사이트 용도에 맞춰 앞쪽만 긁는다.

신제품 날짜는 **이미지의 Last-Modified** 로 얻는다. 2026-10-01 실측:
  - 이미지는 전건(981/981) msave.emart24.co.kr 에 있고, 그중 980건이 Last-Modified
    를 준다(값이 없는 1건은 'AE)필스너우르켈캔맥주500ML*4'). 서로 다른 날짜가
    343개이고 범위가 2020-04-06 ~ 2026-09-29 다. 일괄 재업로드로 한 날에 몰린
    흔적이 없다 — 상품별로 따로 찍힌 진짜 타임스탬프다.
  - 이게 '등록 시점'이라는 근거 두 가지를 실측했다.
    ① align=RECENT 정렬이 실제로 이 mtime 내림차순이다. pl 1~10페이지의
       (최소, 최대) 날짜가 1p 09/02~09/22, 2p 08/18~09/02, 3p 08/03~08/20,
       … 10p 05/21~07/09 로 페이지 단위로는 단조롭게 내려간다(페이지 안에서는
       ±2주쯤 섞인다. 같은 날 올린 것끼리는 순서가 없다).
       옛 주석의 "RECENT 가 등록 최신순이라는 근거가 어디에도 없다"는 이걸로 풀렸다.
    ② 신세계그룹 뉴스룸 보도자료와 대조했다(WP REST:
       www.shinsegaegroupnewsroom.com/wp-json/wp/v2/posts?search=...).
         성수310)우유사르르생크림빵   mtime 07-22 / 출시 PR 07-23  (1일)
         성수310)로열밀크티펫350ml   mtime 08-19 / 출시 PR 08-27  (8일)
         박은영 중화풍 3종           mtime 09-02·09-07 / PR 09-10 (3~8일)
         화이트)New꼬모말보로소비뇽블랑 mtime 09-22 / PR 10-01     (9일)
       전부 mtime 이 출시 보도자료보다 0~9일 **앞선다**. 사진을 먼저 올리고
       며칠 뒤 출시를 알리는 순서라 등록일로 보는 게 맞다.
  - 다만 출시일 그 자체는 아니다(브랜드가 '출시일'이라고 준 값이 아니라 파일
    타임스탬프다). 그래서 released_at 이 아니라 uploaded_at 에 넣는다.
  - 파일명은 바코드다(8800323763185.JPG). 거기엔 타임스탬프가 없다.
    ETag("0-8aa4-6ab2208c")의 끝자리가 mtime 의 16진수라 Last-Modified 와 같은 정보다.
  - 981건 HEAD 가 9초다(커넥션 재사용). 따로 조이지 않고 전건을 찍는다.

NEW 뱃지는 **있긴 한데 낡았다**. ⚠️ 옛 주석의 "전 섹션·전 페이지에서 항상
style=opacity:0" 은 틀렸다 — 180건만 보고 쓴 문장이다. 981건 전수에서 opacity
없이 켜진 NEW 가 7건 있다(전부 차별화 상품, 전부 비행사):
  옐로우)백미밥180g / 응급실)치즈쏘옥떡볶이300g·매콤직화곱창100g·직화무뼈닭발80g·
  쫄깃직화껍데기220g / 포차24)매콤껍데기200g·머릿고기165g
그런데 이 7건의 이미지 mtime 이 전부 2025-11-19~20 이고 RECENT 정렬 18~19페이지에
있다. 10개월 묵은, MD 가 끄지 않은 표식이다. 그래서 뱃지는 켜져 있으면 그대로
is_new=True 로 올리되(브랜드가 한 말이니 숨기지 않는다) 날짜가 거부하게 둔다 —
collect.is_fresh 가 '배지는 믿되 날짜가 있으면 그쪽을 따른다'로 이미 처리한다.
뱃지가 꺼져 있을 때는 is_new=False 가 아니라 None 이다. False 로 두면 is_fresh 가
released_at 만 보게 되는데 이 브랜드는 released_at 이 없어서 전건이 화면에서 사라진다.

## 상품 분류는 `base_category_seq` 에 있다 (2026-10-01 실측)

예전엔 category 에 섹션 이름('차별화 상품')을 넣었다. 그건 판매채널이지 분류가
아니라서 '도시락끼리 모아보기'가 안 됐다. 목록 URL 의 `base_category_seq` 가
진짜 상품 분류 축이고, **섹션마다 축이 다르다.**
  - `/goods/ff` → 41 도시락 · 42 김밥 · 43 햄버거 · 45 주먹밥 · 46 샌드위치 ·
    47 즉석식. 상품 분류 그 자체다. 172건을 6개로 전수 분해했고 겹침 0,
    분류 밖 2건(목록이 크롤 중에 움직여서 생긴 레이스)뿐이다.
  - `/goods/event` → 1 간편식사 · 2 과자 · 3 생활용품 · 5 음료. 거칠다.
    (간편식사에 피스타치오·샤인머스켓·스프가 섞여 있다.) 그래도 섹션 이름보다는
    낫고, **생활용품 272건이 base.NONFOOD_CATEGORIES 에 걸려 굿즈로 빠진다** —
    전에는 '행사 상품'이라 하나도 안 걸렸다.
  - `/goods/pl` → **상품 분류 축이 없다.** 나오는 건 PB 브랜드 20종
    (단독판매·성수310·포차24·조선호텔·구황작물·CHEF'S LINE UP …)이다.
    브라우저로도 열어 확인했다 — 검색창 아래 칩이 전부 PB 브랜드다.
`base_category_seq` 는 **섹션을 넘지 않는다**. pl 에 41(도시락)·1(간편식사)을
넣으면 전부 0건이다(10개 값 전수 확인). 그래서 pl 전용 상품은 분류를 못 받는다:
pl 513건 중 ff·event 에도 있어서 분류가 붙는 건 175건이고 **338건은 빈다.**
이름으로 지어내지 않는다(옐로우 PB 하나에 백미밥·초콜릿·고구마칩·파르페가 다 있다).
사이트가 안 주는 것이라 "없다"가 실측 결론이다.

같은 상품이 섹션을 넘나든다. 분류는 **정밀한 쪽이 이긴다**(ff > event > 없음).
전에는 먼저 만난 섹션이 이겨서 ff 상품 146건이 '차별화 상품'을 달고 있었다.

없는 것들(여기 또 뒤지지 말라고 적어둔다). 2026-10-01 실측:
  - **신상품 전용 탭·메뉴가 없다.** /sitemap 을 전부 폈다. 상품 메뉴는
    /goods/{event,pl,ff} 셋뿐이다. 필터도 신상품이 아니다 — 행사 섹션은
    1+1 / 2+1 / 3+1 / 세일 / 골라담기다(그건 `category_seq`,
    분류는 `base_category_seq` 로 파라미터가 아예 다르다).
    정렬 셀렉트도 없다. 페이지 전체에서 align 은 RECENT 한 값만 나온다.
  - m.emart24.co.kr 은 같은 사이트다(경로 동일). 별도 모바일 API 가 없다.
  - /goods/special 이 마크업에 있다(2026-08-18 '추석 선물 특선'으로 추가된 흔적).
    지금 열면 200 이지만 카드 0건에 타이틀이 '브랜드 가치'로 떨어지는 빈 껍데기다.
    시즌이 끝나 비워둔 자리라 수집원이 못 된다.
  - **상세 페이지가 없다.** 상품명이 여전히 <a href="#none"> 이다. 그래서
    Item.url 을 비워 둔다(base.SITES 의 브랜드 목록 페이지로 폴백).
  - **XHR 이 없다.** 브라우저로 /goods/pl 을 열어 네트워크를 봤다. 요청 37건이
    전부 HTML 문서 + css/png/js + 이미지다. 상품 JSON 은 한 건도 없다.
    Thymeleaf 서버렌더다(주석에 th:href 가 그대로 남아 있다). 스크립트 4개 중
    ajax/fetch 를 쓰는 건 toolbox.js 뿐인데 범용 파일 업로드·다운로드 헬퍼다.
  - 목록 HTML 에 등록일·출시일 필드가 없다. 날짜처럼 보이는 문자열은 개발자가
    남긴 HTML 주석이다("2026-05-07 [개선] 홈페이지 컨텐츠 및 ui 수정" 류).

행사 상품 섹션은 통째로 행사 매대다(필터가 1+1/2+1/3+1/세일/골라담기뿐). 여기서 온 건
promo 로 표시한다. 화면 상위가 전부 이마트24 2+1 로 덮였던 게 바로 이 섹션이다.
mtime 이 최근이어도 promo 면 is_fresh 가 버린다 — WINDOW=60 기준으로 98건이
창 안에 들어오지만 그중 비행사는 62건이고, 화면에 오르는 건 그 62건뿐이다.

가격(.price, 예: "1,700 원")도 같이 내려오지만 Item 에 담을 자리가 없어 버린다.
"""
import re
import time
from email.utils import parsedate_to_datetime

import httpx
from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "이마트24"
URL = "https://emart24.co.kr/goods/{section}"
PROMO_SECTIONS = {"event"}   # 행사 매대. 신제품이 아니라 행사라서 실린 상품들이다.
MAX_PAGES = 25  # 분류당 상한. 8 로는 세 섹션 모두 상한을 소진해 뒤쪽이 통째로 잘렸다.
DELAY = 0.4     # 연속 호출 간격(초)

# 행사 섹션은 분류 하나가 수백 건이다(간편식사 596 · 음료 600+ · 생활용품 272 ·
# 과자 196, 2026-10-01 실측). 전부 promo 라 화면엔 한 건도 안 오르는데 25페이지씩
# 네 번 긁으면 수집량이 3배가 된다. align=RECENT 라 앞쪽이 최신이므로 분류마다
# 최신 7페이지(140건)씩만 본다 — 합이 560건으로 섹션 통짜로 긁던 때(500건)와
# 비슷하면서 네 분류에 고르게 퍼진다.
EVENT_MAX_PAGES = 7

# `base_category_seq` → 이마트24가 쓰는 분류 이름. 섹션마다 축이 다르다.
# 이 표는 아래 _check_nav() 가 매 수집마다 사이트 메뉴와 대조한다.
FF_CATEGORIES = {"41": "도시락", "42": "김밥", "43": "햄버거",
                 "45": "주먹밥", "46": "샌드위치", "47": "즉석식"}
EVENT_CATEGORIES = {"1": "간편식사", "2": "과자", "3": "생활용품", "5": "음료"}

# 섹션 → (분류 축, 정밀도). 정밀도가 높은 쪽이 중복 상품의 분류를 가져간다.
# pl 은 축이 None 이다 — 사이트가 상품 분류를 안 준다(모듈 docstring 참고).
SECTIONS = {
    "event": (EVENT_CATEGORIES, 1),
    "pl": (None, 0),
    "ff": (FF_CATEGORIES, 2),
}

# 브랜드마다 다른 말을 쓰는 걸 화면용 한 가지 이름으로 모은다.
# 주먹밥(삼각김밥)은 김밥과 같은 칩으로 묶는다 — 따로 두면 35건·25건으로
# 쪼개지는데 "김밥끼리 모아보기" 하는 사람이 둘을 구분해 찾지 않는다.
# '간편식사'는 이마트24 행사 섹션이 쓰는 이름 그대로 둔다. 거친 묶음이라
# (피스타치오·샤인머스켓·스프가 같이 들어 있다) 더 좁은 이름을 붙일 근거가 없다.
# ⚠️ '생활용품' 은 base.NONFOOD_CATEGORIES 가 읽는 값이다. 바꾸지 마라.
CATEGORY_NAMES = {
    "도시락": "도시락", "김밥": "김밥", "주먹밥": "김밥", "햄버거": "햄버거",
    "샌드위치": "샌드위치", "즉석식": "즉석식",
    "간편식사": "간편식사", "과자": "과자", "음료": "음료", "생활용품": "생활용품",
}


def _labels(card) -> list:
    """켜져 있는 뱃지만. 혜택(2+1, 1+1, 세일)과 NEW 가 같은 자리에 그려진다.

    NEW 는 대개 opacity:0 으로 꺼져 있지만 항상은 아니다(981건 중 7건이 켜져 있다).
    꺼진 걸 걸러내는 게 이 함수의 일이고, 켜진 NEW 는 그대로 통과시켜
    _is_new() 가 집어가게 둔다.
    """
    out = []
    tit = card.css_first(".itemTit")
    if not tit:
        return out
    for span in tit.css("span"):
        # "opacity: 0" 문자열 비교는 공백 없는 opacity:0 이나 0.0 을 놓친다.
        style = (span.attributes.get("style") or "").replace(" ", "")
        if "opacity:0" in style:
            continue
        text = " ".join(span.text().split())
        if text:
            out.append(text)
    return out


def _is_new(labels: list):
    """켜진 NEW 뱃지 → True, 없으면 None(모름). **False 를 쓰면 안 된다.**

    collect.is_fresh 는 is_new 가 False 면 released_at 만 보는데, 이 브랜드는
    released_at 이 없다(출시일을 주는 곳이 아예 없다). False 로 두는 순간
    uploaded_at 을 들고 와도 전건이 화면에서 잘린다.
    """
    return True if any(l.upper() == "NEW" for l in labels) else None


def _uploaded_at(client, img_url: str, cache: dict) -> str:
    """이미지의 Last-Modified 를 날짜로. 실패하면 조용히 비운다.

    섹션끼리 같은 상품이 겹쳐서 같은 주소를 두 번 찍는 일이 있다. 캐시해 둔다.
    """
    if not img_url:
        return ""
    if img_url in cache:
        return cache[img_url]
    try:
        lm = client.head(img_url).headers.get("last-modified", "")
        out = parsedate_to_datetime(lm).date().isoformat() if lm else ""
    except (httpx.HTTPError, TypeError, ValueError):
        out = ""
    cache[img_url] = out
    return out


def _nav_categories(html: str) -> dict:
    """섹션 페이지가 선언한 분류 메뉴. {base_category_seq: 이름}.

    행사 섹션은 혜택 필터(1+1·2+1·세일·골라담기)도 같은 모양의 ul 로 그린다.
    그쪽은 `category_seq` 쪽에 값이 들어가는데, **분류를 고른 상태로 열면 혜택
    링크가 base_category_seq 를 그대로 물고 온다**(예: 간편식사 페이지에서
    골라담기 = category_seq=12&base_category_seq=1). 그래서 'base_category_seq 가
    있는 링크'로 잡으면 골라담기가 간편식사를 덮어쓴다 — 실제로 그렇게 깨졌다.
    분류 링크는 category_seq 가 **빈 값**이라는 점으로 가른다.
    """
    out = {}
    for a in HTMLParser(html).css("a"):
        m = re.search(r"[?&]category_seq=&base_category_seq=(\d+)",
                      a.attributes.get("href") or "")
        if m:
            out[m.group(1)] = " ".join(a.text().split())
    return out


def _check_nav(section: str, html: str, expected: dict) -> None:
    """사이트가 분류를 바꾸면 조용히 넘기지 않는다.

    이 어댑터의 분류는 전적으로 base_category_seq 표에 기대고 있다. 사이트가
    코드를 갈아끼우면 목록은 멀쩡히 오는데 분류만 통째로 틀려진다(또는 0건이
    되어 칩이 사라진다). 눈에 안 띄는 고장이라 수집 때마다 대조한다.
    """
    nav = _nav_categories(html)
    if nav != expected:
        # 사라진 분류만 보면 안 된다. 분류가 **늘었을 때**는 그 분류 상품이
        # 조용히 통째로 빠지는데(우리 표에 없으니 안 긁는다) 화면에선
        # '그 칩이 원래 없었나' 로만 보인다.
        raise ValueError(
            f"이마트24 /goods/{section} 의 분류 메뉴가 달라졌다. "
            f"기대 {expected} / 실제 {nav} — 빠진 것 "
            f"{ {k: v for k, v in expected.items() if nav.get(k) != v} } / 늘어난 것 "
            f"{ {k: v for k, v in nav.items() if expected.get(k) != v} }. "
            f"FF_CATEGORIES·EVENT_CATEGORIES 와 CATEGORY_NAMES 를 사이트에 맞춰 고쳐라")


def fetch() -> list[Item]:
    items: list[Item] = []
    by_key: dict = {}
    rank_of: dict = {}      # key → 지금 담긴 분류의 정밀도
    stamps: dict = {}
    checked: set = set()
    with base.client() as c:
        for section, (cats, rank) in SECTIONS.items():
            promo = section in PROMO_SECTIONS
            limit = EVENT_MAX_PAGES if section == "event" else MAX_PAGES
            # 분류 축이 없는 섹션(pl)은 한 번만, 있는 섹션은 분류별로 훑는다.
            streams = list(cats.items()) if cats else [("", "")]
            for seq, raw_category in streams:
                category = CATEGORY_NAMES[raw_category] if raw_category else ""
                for page in range(1, limit + 1):
                    time.sleep(DELAY)
                    r = c.get(URL.format(section=section),
                              params={"search": "", "page": page,
                                      "category_seq": "", "base_category_seq": seq,
                                      "align": "RECENT"})
                    r.raise_for_status()
                    if section not in checked:
                        checked.add(section)
                        if cats:
                            _check_nav(section, r.text, cats)
                    cards = HTMLParser(r.text).css("section.itemList .itemWrap")
                    # 마크업이 바뀌어 조용히 0건이 되는 게 제일 나쁘다. 1페이지는
                    # 반드시 카드가 와야 한다(2026-10-01 실측으로 분류별 최소가
                    # ff/햄버거 19건이다 — 1페이지가 비는 분류는 없다).
                    if page == 1 and not cards:
                        raise ValueError(
                            f"이마트24 /goods/{section}"
                            f"{f'?base_category_seq={seq}({raw_category})' if seq else ''} "
                            f"1페이지에 카드가 0건이다. 응답 {len(r.text)}바이트 — "
                            f"section.itemList .itemWrap 셀렉터나 분류 코드가 "
                            f"바뀌었는지 확인하라")
                    if not cards:
                        break   # 범위를 넘긴 page 는 빈 목록을 돌려준다

                    parsed = []
                    for card in cards:
                        name_node = card.css_first(".itemtitle a")
                        name = " ".join(name_node.text().split()) if name_node else ""
                        if not name:
                            continue
                        img_node = card.css_first(".itemSpImg img")
                        image = img_node.attributes.get("src", "") if img_node else ""
                        labels = _labels(card)
                        parsed.append(Item(
                            brand=BRAND,
                            name=name,
                            image=image,
                            labels=labels,
                            category=category,
                            promo=promo,
                            # 등록 시점. 출시일이 아니라 사진이 올라간 날이다(위 docstring).
                            uploaded_at=_uploaded_at(c, image, stamps),
                            is_new=_is_new(labels),
                        ))

                    # 섹션끼리 상품이 겹친다(FF 상품이 차별화/행사에도 뜬다).
                    # 중복이라고 페이지를 끊으면 뒤 섹션이 통째로 날아가므로 그냥 건너뛰기만 한다.
                    # 다만 행사 매대에도 걸린 상품은 어느 섹션에서 먼저 만났든 행사 상품이므로
                    # promo 만은 살려서 합친다(섹션 순서에 따라 표시가 뒤집히지 않게).
                    # 분류도 같은 이유로 합친다 — 먼저 만난 섹션이 아니라 **더 정밀한
                    # 축**이 이긴다. 전에는 pl 을 먼저 만나는 바람에 Fresh Food 상품
                    # 146건이 '차별화 상품'(판매채널)을 달고 있었다.
                    for it in parsed:
                        old = by_key.get(it.key)
                        if old is None:
                            by_key[it.key] = it
                            rank_of[it.key] = rank if category else -1
                            items.append(it)
                            continue
                        if it.promo:
                            old.promo = True
                        if category and rank > rank_of.get(it.key, -1):
                            old.category = category
                            rank_of[it.key] = rank

    # 날짜는 전적으로 이미지 CDN 의 Last-Modified 에 기대고 있다. 그게 통째로
    # 끊기면(헤더 제거·호스트 교체) 날짜 0건인 채로 조용히 돌아가 화면이 빈다.
    # 실측 980/981 이라 '거의 전부'가 정상이고, 한 자리라도 깨지면 드러낸다.
    dated = sum(1 for it in items if it.uploaded_at)
    if items and dated < len(items) // 2:
        raise ValueError(
            f"이마트24 이미지 Last-Modified 가 {len(items)}건 중 {dated}건뿐이다. "
            f"이 브랜드는 날짜 신호가 이것 하나라 이대로면 화면이 빈다 — "
            f"이미지 호스트(msave.emart24.co.kr)나 응답 헤더가 바뀌었는지 확인하라")

    # 분류가 조용히 비면 화면에서 칩이 사라진다. 메뉴 대조(_check_nav)를 통과했는데도
    # 분류가 안 붙었다면 목록 자체가 비어 돌아온 것이다.
    # 2026-10-01 실측: Fresh Food 172건 + 행사 분류 4종이 붙어 전체의 과반이 넘는다.
    # pl 전용 상품(338건)은 사이트에 분류가 없어서 원래 비는 자리다.
    tagged = sum(1 for it in items if it.category)
    if items and not tagged:
        raise ValueError(
            f"이마트24 {len(items)}건 전부 분류가 비었다. base_category_seq 로 "
            f"거른 목록이 통째로 안 온다는 뜻이다 — 분류 코드가 바뀌었는지 확인하라")
    print(f"  이마트24 분류 {tagged}/{len(items)}건 "
          f"(차별화 전용 상품은 사이트에 분류가 없다)")
    return items
