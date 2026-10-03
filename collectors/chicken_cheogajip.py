"""처갓집양념치킨.

공정위 등록 가맹점 1,254개로 치킨 업종 4위다. BBQ·bhc·교촌 다음 자리라
치킨 분류를 채우려면 빠질 수 없다.

cheogajip.co.kr 은 그누보드 게시판을 메뉴판으로 쓴다. 메뉴판 주소가
/bbs/board.php?bo_table=allmenu 인 것도 그래서다. 서버에서 다 렌더돼 나오고
쿠키·세션·브라우저가 필요 없다. 응답은 UTF-8.

분류는 sca 쿼리 파라미터로 거른다(한마리메뉴·반반메뉴·다리.날개메뉴·반마리메뉴·
사이드메뉴). 그런데 **전체 페이지가 이미 다섯 분류를 전부 담고 있고**, 카드마다
`<!-- <p class="bo_cate_link">한마리메뉴</p> -->` 주석으로 자기 분류를 들고 있다.
그래서 요청 한 번으로 끝낸다 — sca 페이지를 따로 5번 긁는 것보다 가볍고,
분류 결과도 같다(32건 전부 주석이 붙어 있는 걸 2026-10-02 에 확인했다).
주석이라 셀렉터로는 못 잡아서 `li.gall_li` 의 원본 HTML 에 정규식을 댄다.
주석이 사라지면 category 만 비고 상품은 그대로 나온다 — 그 정도면 감수할 만하다.

⚠️ **카드는 32장인데 상품은 30건이 정상이다.** `치킨치즈볼 골드`·`치킨치즈볼 레드`
   가 각각 **글자까지 똑같이 두 번** 올라와 있어서 `seen` 이 뒤엣것을 버린다
   (2026-10-02 실측). 가마치통닭의 47 → 45 와 같은 사정이다. 32 가 안 나온다고
   파서를 의심하지 마라.

🔴 **상세 페이지가 없다.** 카드 어디에도 `<a>` 가 없어서 눌러도 아무 데도 안 간다
(2026-10-02 실측). 그래서 url 은 비우고 base.SITES 의 브랜드 메뉴판 폴백에 맡긴다.

신제품 신호 — **NEW 배지가 없다.** 사이트 어디에도 신메뉴 탭·신메뉴 배지·출시일이
없다. 그래서 `is_new` 는 전건 None 으로 둔다. 전체 메뉴를 신제품이라 찍지 않는다.
신제품 판정은 collect.py 의 '어제 없던 키가 오늘 있다' diff 에 맡긴다.

대신 **이미지의 Last-Modified** 를 uploaded_at 으로 넣는다. 믿는 근거는
그누보드가 작성일을 HTML 주석에 남겨놓는다는 점이다
(`<span class="gall_subject">작성일 </span>05-28`). 가장 최신인 미트칠리
양념치킨은 주석 작성일 05-28 과 이미지 Last-Modified 2026-05-28 이 월·일까지
정확히 맞고, 2023-04-27 묶음 5건도 작성일 04-27 과 맞는다. CDN 이 일괄로 찍어준
시각이 아니라 게시판에 올린 시각이라는 뜻이다. 주석에는 연도가 없어서
(MM-DD 뿐) 작성일 자체는 단독으로 못 쓰고, 교차검증 재료로만 쓴다.

⚠️ 다만 **강한 신호는 아니다.** 2026-10-02 실측 32건 분포 —
    2026-05-28 / 2026-03-17 / 2025-07-24 / 2024-07-19 / 2023-04-27 ×5
    그리고 **2023-02-16 에 23건(72%)이 몰려 있다.**
뒤쪽 덩어리는 사이트 이관분으로 보인다(BBQ 의 2026-04-30 과 같은 모양). 그리고
작성일 주석과 Last-Modified 가 어긋나는 것도 있다(K-마라 05-14 vs 03-17,
꼬꼬뱅 09-12 vs 2025-07-24) — 이미지를 나중에 갈아끼운 것으로 보인다.
즉 최근 올라온 몇 건을 가려내는 데는 쓸 만하고, 이관 덩어리 안의 선후를 가리는
데는 못 쓴다. BBQ·교촌과 같은 쓰임새다 — 기준선 소급용이지 출시일이 아니다.
출시일이 아니므로 released_at 에는 절대 넣지 않는다.

게시물 번호(span.sound_only)가 46, 45, 44 … 로 내려간다. 대체로 최신순 정렬이라는
뜻이지 날짜는 아니다. 순서를 날짜로 바꿔 쓰지 않는다.

버리는 것들:
  - 가격(`p.menuprice`, '19,000원+4,000원' 형태의 부위 추가금). Item 에 자리가 없다.
  - 반마리메뉴 분류는 sca 목록에는 있지만 전체 페이지에 실린 상품이 0건이다.
  - 세트·행사·이벤트 공지는 애초에 이 게시판에 없다. 전부 단품이다.
    '후라이드 + 치즈슈프림양념' 류 반반메뉴는 세트가 아니라 맛 조합이라 그대로 담고
    (교촌 '반반…[간장+레드]' 선례), promo 는 전건 False 로 둔다. 이 브랜드엔
    할인·행사 표시가 없다. 세트 변형 처리는 collect.drop_sets() 담당이다.

robots: https://cheogajip.co.kr/robots.txt 는 200 이고 `User-agent: *` / `Allow: /`
        두 줄이 전부다(2026-10-03 실측, 22B). Disallow 가 없어 우리 경로
        `/bbs/board.php` 는 허용 범위다.
"""
import re
import time
from email.utils import parsedate_to_datetime

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "처갓집양념치킨"
SITE = "https://cheogajip.co.kr"
MENU = SITE + "/bbs/board.php?bo_table=allmenu"

MAX_ITEMS = 200   # 폭주 방지. 현재 32건.
DELAY = 0.3       # 목록 요청 간격(초)
IMG_DELAY = 0.15  # 이미지 HEAD 간격(초)

# 분류가 주석 안에 들어 있다. 셀렉터로는 못 잡아서 원본 HTML 을 본다.
_CATE = re.compile(r'class="bo_cate_link"\s*>\s*([^<]+?)\s*<')


def _name(node) -> str:
    """`li.gall_text_href` 안에서 `<hr class="subjectunder">` **앞**의 맨 텍스트.

    이름이 태그에 안 싸여 있어서 text() 로 통째로 뽑으면 설명·해시태그·가격이
    전부 딸려 온다. hr 을 만나면 끊는다.
    """
    parts = []
    for n in node.iter(include_text=True):
        if n.tag == "hr":
            break
        if n.tag == "-text":
            parts.append(n.text_content or "")
    return " ".join("".join(parts).split())


def _desc(node) -> str:
    """`<h3>` 안 첫 `<p>`. 단 `p.menuprice` 는 가격이라 설명이 아니다.

    반반메뉴 3건은 설명 `<p>` 가 아예 없어서 첫 `<p>` 가 가격이다.
    거르지 않으면 '19,000원+3,000원' 이 상품 설명으로 올라간다.
    """
    for p in node.css("h3 > p"):
        if "menuprice" not in (p.attributes.get("class") or ""):
            return " ".join(p.text().split())
    return ""


def _uploaded_at(client, img_url: str) -> str:
    """이미지의 Last-Modified 를 날짜로. 실패하면 조용히 비운다."""
    if not img_url:
        return ""
    try:
        lm = client.head(img_url).headers.get("last-modified", "")
        return parsedate_to_datetime(lm).date().isoformat() if lm else ""
    except Exception:
        return ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        time.sleep(DELAY)
        r = base.retry(lambda: c.get(MENU))
        r.raise_for_status()
        cards = HTMLParser(r.text).css("li.gall_li")

        # 비어 있으면 셀렉터가 깨진 것이다. 조용히 []를 돌려주면 collect.py 의
        # 0건 가드가 '브랜드 수집 실패' 로 잡아주긴 하지만, 그 전에 여기서
        # 이유를 말하고 죽는 쪽이 고치기 쉽다.
        if not cards:
            raise RuntimeError("메뉴 카드가 비었다 — 셀렉터가 깨졌을 가능성")

        for card in cards[:MAX_ITEMS]:
            text_node = card.css_first("li.gall_text_href")
            if text_node is None:
                continue
            name = _name(text_node)
            if not name:
                continue

            img = card.css_first("li.gall_href img")
            src = img.attributes.get("src", "") if img else ""
            cate = _CATE.search(card.html or "")
            # 해시태그는 부위·수량 선택지다('#한마리'·'#순살'·'#9개').
            # 사이즈·온도 라벨과 같은 성격이라 labels 로 옮긴다.
            tags = [t for li in card.css("ul.menutag li")
                    if (t := " ".join(li.text().split()).lstrip("#"))]

            it = Item(
                brand=BRAND,
                name=name,
                desc=_desc(text_node),
                image=src,                       # 이미 절대 https 주소다
                labels=tags,
                category=cate.group(1) if cate else "",
                # NEW 배지도 신메뉴 탭도 출시일도 없는 사이트다. 모르는 건
                # 모른다고 둔다 — 전건 True 도 전건 False 도 거짓말이다.
                is_new=None,
                # 할인·행사 표시가 없다. 세트는 promo 가 아니다
                # (collect.drop_sets() 가 이름으로 거른다).
                promo=False,
                # 상품 상세 페이지가 없다(<a> 자체가 없음). base.SITES 폴백에 맡긴다.
                url="",
            )
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)

        if not items:
            raise RuntimeError("카드는 있는데 상품 이름이 하나도 안 나왔다 — "
                               "셀렉터가 깨졌을 가능성")

        for it in items:
            time.sleep(IMG_DELAY)
            it.uploaded_at = _uploaded_at(c, it.image)

    # 🔴 '건수는 멀쩡한데 날짜만 사라진' 상태를 막는다. 이미지 호스트가
    # Last-Modified 를 끊거나 경로가 바뀌면 HEAD 가 전건 조용히 실패하는데,
    # 건수는 그대로라 collect.py 의 0건 가드도 FLOOR 도 통과한다. BBQ 의
    # _head_guard·가마치통닭·노랑통닭과 같은 처분이다(실측 30/30 이 날짜를 받는다).
    dated = sum(1 for it in items if it.uploaded_at)
    if dated * 2 < len(items):
        raise RuntimeError(
            f"처갓집양념치킨 업로드일 {len(items)}건 중 {dated}건만 붙었다 — 이미지 "
            f"Last-Modified 가 끊겼거나 경로가 바뀌었을 가능성. 이 브랜드는 "
            f"NEW 배지도 신메뉴 탭도 없어서 이게 유일한 날짜 신호다")
    return items
