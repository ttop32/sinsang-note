"""애플꼬마김밥 — 언론보도 게시판에서 신제품과 출시일을 뽑는다.

주식회사 애플푸드(884-81-01497, 세종). 공정위 `분식` 105개점.
도메인은 **`apple-food.co.kr`**(브랜드명 로마자가 아니라 회사명이다).
gnuboard + Tailwind 테마. 전부 SSR·https.

## 메뉴 게시판에는 신상 구분이 없다

`/bbs/board.php?bo_table=menu` 가 200 / 90KB 로 상품명과 한 줄 설명까지
깔끔하게 내려준다(`애플꼬마김밥 5줄`·`모둠꼬마김밥 8줄`·`참치꼬마김밥 4줄` …).
수집 난이도만 보면 제일 쉬운 축인데 **신상을 가를 게 하나도 없다.**
2026-10-02 실측 — `data-*` 속성은 `data-cfasync`·`data-cfemail`·`data-page`
셋뿐(전부 Cloudflare·페이징용이고 상품 플래그가 아니다), `sca=` 분류 파라미터
0건, 대소문자 무시하고 센 `new` 토큰 1건(테마 문자열). 수유리우동집처럼
숨겨진 전수 배지가 있는 것도 아니라 **아예 없는 쪽**이다.

그래서 언론보도 게시판을 쓴다. 거기엔 날짜가 연도까지 찍힌다.

## ⚠️ 이 게시판은 대부분 매장 오픈 소식이다. 역필터가 본체다

2026-10-02 실측 — 총 25건(2페이지). 1페이지 15건을 전수로 훑으면 이렇다.

    애플꼬마김밥 “김해삼계점 신규 오픈으로 150호점 돌파 눈앞”      2026-07-02
    애플꼬마김밥, 147호점 루원시티점 오픈                          2026-06-12
    애플꼬마김밥, 대구안지랑역점 오픈                              2026-05-26
    애플꼬마김밥, 여름 한정 신메뉴 ‘냉쫄면’ 출시                   2026-05-04  ← 이것만 상품
    애플꼬마김밥, 145호점 '평택점' 오픈                            2026-04-21
    … 자양점 꼬마김밥 1,000줄 기부 / 김천김밥축제 부스 매출 1위 …

**15건 중 상품 글이 1건이다.** 쥬씨(`notes/CANDIDATES-THIN.md` §3-9)와 같은
밀도이고, 거기 적힌 "역필터(`출시|신메뉴` ∧ ¬`오픈|점`)가 필수고 월 1건 미만을
각오해야 한다"가 그대로 적용된다. **연 1~2건을 각오하고 붙인다.**
게시판 자체는 살아 있다(최신 2026-07-02).

역필터는 두 겹이다.
  ① 제목에 `출시` 또는 `신메뉴` 가 있어야 한다
  ② `오픈`·`호점`·`기부`·`축제`·`달성`·`박람회`·`이벤트`·`돌파` 가 있으면 뺀다
②가 없으면 `"김해삼계점 신규 오픈으로 150호점 돌파 눈앞"` 이 ①을 통과하지
않는데도(출시·신메뉴 없음) 안심할 수 없다 — 본사가 "신메뉴 출시 기념 오픈
이벤트" 같은 제목을 쓰면 ①만으로는 통과한다. 미리 막아 둔다.

이름은 제목에서 **따옴표 안**을 먼저 찾는다(`‘냉쫄면’`). 따옴표가 없으면
브랜드명 접두와 꾸밈말을 턴 나머지를 쓴다. 못 뽑으면 그 글은 버린다 —
제목 통째로 상품명이 되면 카드에 `애플꼬마김밥, 여름 한정 신메뉴 … 출시` 가
찍힌다(오뚜기·샘표 보도자료 어댑터와 같은 처리).

`released_at` 은 목록의 날짜다. 브랜드가 그날 출시를 알린 글이므로 출시일로
쓴다. 목록에 **연도가 다 찍혀 있어** 상세를 열 필요가 없다(슬로우캘리처럼
`MM-DD` 만 주는 gnuboard 테마와 다르다). 썸네일도 목록에 있어 요청이 1~2회면
끝난다. `is_new` 는 전부 True — 브랜드가 '출시'라고 낸 글만 담기 때문이다.

robots.txt: **200 / 1,248바이트인데 지시문이 한 줄도 없다.** 전부 Cloudflare 의
`content-signals` 설명 주석이고 `User-agent`·`Disallow`·`Allow` 가 아예 없다.
크롤러 규칙으로는 **무제한**이지만, 그 주석이 `ai-train`·`ai-input` 에 대한
EU 저작권지침 제4조 권리유보 문구를 담고 있다. 우리는 모델을 학습시키지 않고
신제품 소식을 색인하는 쪽이라 거기 걸리지 않는다고 본다 — 다만 **"규칙이
없다"와 "아무 말도 없다"는 다르다**는 걸 적어 둔다. 삭제 요청이 오면 다투지
말고 즉시 내린다. 이용약관 문서는 푸터에 없다(개인정보처리방침만).
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "애플꼬마김밥"
ROOT = "https://apple-food.co.kr"
LIST = ROOT + "/bbs/board.php"
BO_TABLE = "news"
PAGE_SIZE = 15   # 한 페이지 15건. 이보다 적게 오면 다음 장이 없다.
MAX_PAGES = 6    # 폭주 방지. 현재 2페이지(25건).
DELAY = 2.5

# ① 있어야 하는 말 ② 있으면 안 되는 말. 근거는 위 docstring 의 15건 전수 표.
_RELEASE = ("출시", "신메뉴")
_NOT_PRODUCT = ("오픈", "호점", "기부", "축제", "달성", "박람회", "이벤트", "돌파")

# 제목 안의 따옴표. 한국 보도자료는 ‘ ’ 를 쓰고 가끔 ' ' · " " 도 섞인다.
_QUOTED = re.compile(r"[‘'\"“]([^’'\"”]{2,30})[’'\"”]")
_HEAD = re.compile(rf"^\s*{BRAND}\s*[,.]?\s*")
_NOISE = re.compile(r"(여름|겨울|봄|가을)?\s*한정\s*|신메뉴\s*|\s*출시.*$")


def _is_product(title: str) -> bool:
    return (any(w in title for w in _RELEASE)
            and not any(w in title for w in _NOT_PRODUCT))


def _href(card) -> str:
    """그 글의 상세 주소.

    ⚠️ 원본 HTML 에서는 카드가 `<a href="…wr_id=45">` 안에 들어 있는데
    **파서를 거치면 그 `<a>` 가 조상에서 사라진다.** 테마가 그 안에 '수정하기'
    `<a>` 를 하나 더 넣어 뒀고, HTML5 파서는 중첩된 `<a>` 를 허용하지 않아
    바깥 `<a>` 를 끊어 올리기 때문이다. 그래서 `card.parent` 를 타고
    올라가면 `div.col-span-…` 이 나오고 주소를 못 찾는다(실제로 전 카드가
    빈 주소였다). **감싼 칸 안에서 `wr_id` 가 든 링크를 찾는 쪽으로 간다.**
    """
    box = card.parent
    if box is None:
        return ""
    for n in box.css("a[href]"):
        href = n.attributes.get("href", "")
        if "wr_id=" in href:
            # 테마가 `&w=u`(gnuboard 수정 모드)를 붙여 둔다. 비회원이 열어도
            # 지금은 글이 그대로 보이지만, 사람에게 내보내는 주소에 수정 모드를
            # 달아 둘 이유가 없다. 떼고 내보낸다(둘 다 같은 48,072바이트 실측).
            return href.replace("&w=u", "")
    return ""


def _pick(title: str) -> str:
    """제목에서 상품 이름. 못 뽑으면 빈 문자열(그 글은 버린다)."""
    m = _QUOTED.search(title)
    if m:
        return m.group(1).strip()
    return _NOISE.sub("", _HEAD.sub("", title)).strip()


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            r = base.retry(lambda: c.get(LIST, params={"bo_table": BO_TABLE,
                                                       "page": page}))
            r.raise_for_status()
            time.sleep(DELAY)

            cards = HTMLParser(r.text).css("div.news-card")
            for card in cards:
                subj = card.css_first(".news-subject")
                if not subj:
                    continue
                title = " ".join(subj.text().split())
                if not _is_product(title):
                    continue
                name = _pick(title)
                if not name:
                    continue
                # 카드 안 첫 날짜. 목록에 연도까지 찍혀 있다.
                m = re.search(r"\d{4}-\d{2}-\d{2}",
                              " ".join(card.text().split()))
                img = card.css_first("figure img")
                href = _href(card)
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=title,
                    image=img.attributes.get("src", "") if img else "",
                    released_at=m.group(0) if m else "",
                    is_new=True,     # 브랜드가 '출시'라고 낸 글만 담는다
                    url=href,
                )
                if it.key in keys:
                    continue
                keys.add(it.key)
                items.append(it)

            # 꽉 차지 않은 페이지면 다음 장이 없다.
            if len(cards) < PAGE_SIZE:
                break
    return items
