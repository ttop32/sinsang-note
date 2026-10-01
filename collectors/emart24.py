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
import time
from email.utils import parsedate_to_datetime

import httpx
from selectolax.parser import HTMLParser

from . import base
from .base import UA, Item

BRAND = "이마트24"
URL = "https://emart24.co.kr/goods/{section}"
SECTIONS = {"event": "행사 상품", "pl": "차별화 상품", "ff": "Fresh Food"}
PROMO_SECTIONS = {"event"}   # 행사 매대. 신제품이 아니라 행사라서 실린 상품들이다.
MAX_PAGES = 25  # 섹션당 상한. 8 로는 세 섹션 모두 상한을 소진해 뒤쪽이 통째로 잘렸다.
DELAY = 0.4     # 연속 호출 간격(초)


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


def fetch() -> list[Item]:
    items: list[Item] = []
    by_key: dict = {}
    stamps: dict = {}
    with base.client() as c:
        for section, category in SECTIONS.items():
            promo = section in PROMO_SECTIONS
            for page in range(1, MAX_PAGES + 1):
                time.sleep(DELAY)
                r = c.get(URL.format(section=section),
                          params={"search": "", "page": page,
                                  "category_seq": "", "align": "RECENT"})
                r.raise_for_status()
                cards = HTMLParser(r.text).css("section.itemList .itemWrap")
                # 마크업이 바뀌어 조용히 0건이 되는 게 제일 나쁘다. 1페이지는
                # 반드시 카드가 와야 한다(세 섹션 다 수백 건짜리 목록이다).
                if page == 1 and not cards:
                    raise ValueError(
                        f"이마트24 /goods/{section} 1페이지에 카드가 0건이다. "
                        f"응답 {len(r.text)}바이트 — section.itemList .itemWrap "
                        f"셀렉터나 섹션 주소가 바뀌었는지 확인하라")
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
                for it in parsed:
                    old = by_key.get(it.key)
                    if old is None:
                        by_key[it.key] = it
                        items.append(it)
                    elif it.promo:
                        old.promo = True

    # 날짜는 전적으로 이미지 CDN 의 Last-Modified 에 기대고 있다. 그게 통째로
    # 끊기면(헤더 제거·호스트 교체) 날짜 0건인 채로 조용히 돌아가 화면이 빈다.
    # 실측 980/981 이라 '거의 전부'가 정상이고, 한 자리라도 깨지면 드러낸다.
    dated = sum(1 for it in items if it.uploaded_at)
    if items and dated < len(items) // 2:
        raise ValueError(
            f"이마트24 이미지 Last-Modified 가 {len(items)}건 중 {dated}건뿐이다. "
            f"이 브랜드는 날짜 신호가 이것 하나라 이대로면 화면이 빈다 — "
            f"이미지 호스트(msave.emart24.co.kr)나 응답 헤더가 바뀌었는지 확인하라")
    return items
