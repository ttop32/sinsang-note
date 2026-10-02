"""두찜(두마리찜닭, (주)기영에프앤비).

가맹점 603개로 공정위 `한식` 업종 상위권이다(2025년도 정보공개서, 2024년 말 기준).

⚠️ **도메인을 헷갈리지 마라. `doochim.com` 은 두찜이 아니다.**
2026-10-02 실측으로 `doochim.com` / `www.doochim.com` 은 두찜과 무관한 한의원
사이트에 떨어진다. 그마저도 **침해당한 워드프레스**라 응답 본문에 파일 업로드
웹셸("Priv8 Uploader")이 그대로 노출된다. 어떤 이유로도 이 호스트에 요청을 보내지
마라. 두찜 공식 도메인은 **`twozzim.com`** 이다(창업 사이트는 `start-twozzim.com`).

메뉴는 `/bbs/content.php?co_id=menu` **한 장**에 전부 들어 있다. 그누보드이고
탭 다섯 개(BEST·블랙&크림·레드·사이드·토핑추가)가 전부 같은 HTML 안의
`ul.menu_bbs` 다섯 덩어리다. 쿠키·세션·JS 불필요. **1요청에 59칸, 중복을 턴 54건**
(2026-10-02 실측). BEST 탭 5건은 다른 탭에 겹쳐 실린 것이라 중복으로 빠진다.

⚠️ **탭마다 마크업이 다르다.** 앞 세 탭은 상품명이 `<a>` 안에 있고 상세 링크
(`bbs/board.php?bo_table=menu&wr_id=N`)가 걸리는데, 사이드·토핑추가 35건은
`ul.menus_box_txt_ul1` 의 **직접 텍스트**이고 링크가 없다. `.menus_box_txt_ul1 a`
로만 집으면 그 35건을 통째로 놓친다(처음에 19건만 나왔던 게 이 때문이다).
그래서 ul 의 텍스트를 읽고 링크는 있으면 쓴다.

**신제품 배지가 없다.** 썸네일 위 배지(`.menus_box_img span`)는 `BEST` 5건뿐이고
`NEW` 는 54건 어디에도 없다. 원앤원처럼 주석으로 숨겨둔 자리도 없다.
그래서 `is_new` 는 전부 None(모름)이다.

  uploaded_at  **이미지의 `Last-Modified` 헤더**로 채운다. 파일명이 전부
          해시(`thumb-<32hex>_<8>_<40hex>_500x0.png`)라 날짜가 박혀 있지 않아서
          헤더 말고는 길이 없다. 54건 전부 200 과 Last-Modified 를 돌려준다.
          분포는 —
            2024-01-26 10건  찜닭 본진 일괄 등록
            2024-03-18  1건  불닭로제찜닭
            2025-02-11 31건  사이드·토핑추가 일괄 등록
            2025-04-30  1건  실비한우곱찜닭
            2025-05-14  1건  닭볶음탕
            2025-06-19  2건  옛날통닭·모치치
            2025-10-21  1건  매운갈비찜닭
            2026-01-19  1건  곤드레까만볶음밥
            2026-02-25  4건  한우대창맵닭발·묵은지찜닭·한우대창마라닭발·묵은지김치볶음밥
            2026-07-07  2건  로제칼낙지찜닭·칼낙지찜닭
          ⚠️ **2024-01-26 과 2025-02-11 두 무더기는 일괄 등록이다.** 54건 중
          41건이 거기 몰려 있다. 사이트를 손볼 때 사진을 통째로 올린 흔적이지 그
          41종이 그날 나왔다는 뜻이 아니다(큰맘할매순대국 2025-12-22, 유가네
          2020-07-07, 오봉집 2025-12-22 와 같은 자리). **따로 떨어진 13건만
          '그 뒤에 추가됐다'로 읽어야 한다.**

  🔵 **교차검증 — 공지 게시판이 날짜 순서를 확인해 준다.**
          `/bbs/board.php?bo_table=news` 에 신메뉴 글이 상품명을 따옴표로 달고
          올라온다. 최신순으로
            두찜 신메뉴 "매운갈비찜닭" 출시
            신메뉴 '실비한우곱찜닭' 출시
            멕시칸 풍미 가득 신메뉴 '타코라구요찜닭' 출시!
            신메뉴 '불닭로제찜닭' 소개
            신메뉴 '양구 펀치볼 시래기 찜닭' 출시!
          이고, 이미지 날짜가 매운갈비찜닭 2025-10-21 > 실비한우곱찜닭 2025-04-30 >
          불닭로제찜닭 2024-03-18 로 **게시판 순서와 같은 차례**다. 게시판을 모르는
          Last-Modified 가 게시판과 같은 답을 냈다. (타코라구요찜닭은 지금 메뉴에
          없다 — 단종된 모양이다.)
          게시판 자체를 소스로 쓰지 않은 이유는 목록에 날짜가 안 찍히고, 54건짜리
          메뉴판이 이미 있어 굳이 제목에서 상품명을 뜯어낼 필요가 없어서다.

  🔵 **세 번째 축 — 상세 글번호(`wr_id`)도 같은 차례다.** 링크가 걸린 19건을
          wr_id 오름차순으로 세우면 이미지 날짜가 거의 그대로 비감소한다
          (…30~48 → 2024-01-26, 52 → 2024-03-18, 66 → 2025-04-30,
           72 → 2025-10-21, 75~77 → 2026-02-25, 81~82 → 2026-07-07).
          **어긋나는 건 딱 1건, `닭볶음탕`(wr_id 27, 2025-05-14)이다.** 번호는
          제일 낮은데 날짜만 최근인 건 **오래된 글의 사진만 나중에 갈아끼운**
          경우다 — Last-Modified 가 '상품이 생긴 날'이 아니라 '파일을 마지막으로
          쓴 날'이라는 이 값의 성질이 그대로 드러난 사례다. 그래서 released_at
          으로 승격시키지 않는다. 다만 19건 중 18건이 맞는다는 건 이 값이
          대체로는 등록 순서를 따라간다는 뜻이기도 하다.

**released_at 에는 넣지 않는다.** 브랜드가 "출시일"이라고 말한 값이 아니라 사진을
올린 시각이다(본아이에프·한솥·원앤원과 같은 처분). 상품 상세(`wr_id`)도 받아
확인했는데 그누보드 작성일을 테마가 찍지 않아 날짜 항목이 아예 없다. 지어내지
않고 비운다.

이 브랜드는 `is_new` 가 없어 **합류 첫날에는 신제품을 하나도 못 내놓는다.**
그 대신 `collect.py` 가 uploaded_at 을 first_seen 으로 소급해 기준선으로 깔아두므로,
다음에 올라오는 새 메뉴부터 날짜와 함께 잡힌다. 그게 정직하다(원앤원 선례).

사이드의 세트 5종(튀김·납작·롱롱·둥근·나홀로세트)은 promo 로 찍지 않는다. 할인
행사가 아니라 구성 메뉴고, 거르는 건 `collect.drop_sets()` 담당이다(이삭토스트 선례).

이미지 HEAD 는 URL 단위로 캐시한다. 지금은 54건에 고유 이미지 54장이라 절감이
0이지만, 같은 사진을 두 탭이 공유해도 요청이 안 늘게 둔다. 총 요청 1 + 54 = 55회.

가격은 사이트에 없다. `토핑추가` 탭 15건은 사리·치즈 같은 추가 선택지라 단독
상품으로 보기 애매하지만, 브랜드가 메뉴판에 올린 것이고 '분모자'·'푸주' 처럼
신상이 나올 수 있는 자리라 그대로 둔다.
"""
import re
import time
from email.utils import parsedate_to_datetime

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "두찜"
HOST = "https://twozzim.com"
MENU_URL = HOST + "/bbs/content.php?co_id=menu"
DELAY = 0.7          # 이미지 HEAD 간격(초)
MAX_HEADS = 120      # 폭주 방지. 현재 54건.

# `ul.menu_bbs` 등장 순서 = 화면 탭 순서. BEST 는 다른 탭의 재탕이라
# 분류명으로 쓰지 않고(중복 제거로 빠진다) 나머지만 category 에 들어간다.
TABS = ("BEST", "블랙&크림", "레드", "사이드", "토핑추가")
BEST_TAB = "BEST"


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _uploaded_at(c, src: str, cache: dict) -> str:
    """이미지 Last-Modified 를 날짜로. 못 읽으면 비운다(날짜는 지어내지 않는다).

    출시일이 아니라 사진을 올린 시각이다 — docstring 의 유보 사항을 읽어라.
    GMT 로 오지만 KST 로 돌리지 않는다(큰맘할매순대국과 같은 처분) — 날짜만
    쓰는데 한 칸 틀릴 수 있는 건 GMT 15:00 이후 파일뿐이고, 그걸 맞추자고
    서버가 어느 시간대로 내보내는지에 대한 가정을 하나 더 들이지 않는다.
    """
    if not src:
        return ""
    if src in cache:
        return cache[src]
    if len(cache) >= MAX_HEADS:
        return ""
    out = ""
    try:
        r = base.retry(lambda: c.head(src))
        lm = r.headers.get("last-modified", "")
        if lm:
            out = parsedate_to_datetime(lm).date().isoformat()
    except Exception:
        out = ""
    cache[src] = out
    time.sleep(DELAY)
    return out


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(MENU_URL))
        r.raise_for_status()

        groups = HTMLParser(r.text).css("ul.menu_bbs")
        if not groups:
            raise RuntimeError("두찜: 메뉴 탭 0개 — 셀렉터가 깨졌을 수 있다")

        items: list[Item] = []
        seen: set = set()
        stamps: dict = {}
        for i, group in enumerate(groups):
            category = TABS[i] if i < len(TABS) else ""
            cards = group.css(".menus_box")
            if not cards:
                raise RuntimeError(
                    f"두찜 {category or i}번 탭: 상품 0건 — 구조가 바뀌었다")

            for card in cards:
                # ⚠️ ul 의 텍스트를 읽는다. 뒤쪽 두 탭은 <a> 가 없다(docstring).
                head = card.css_first(".menus_box_txt_ul1")
                name = _clean(head.text()) if head else ""
                if not name:
                    continue
                key = base.make_key(BRAND, name)
                if key in seen:
                    continue
                seen.add(key)

                desc = card.css_first(".menus_box_txt_ul2")
                img = card.css_first(".menus_box_img img")
                src = img.attributes.get("src", "") if img else ""
                badge = card.css_first(".menus_box_img span")
                link = head.css_first("a") if head else None
                href = link.attributes.get("href", "") if link else ""

                items.append(Item(
                    brand=BRAND,
                    name=name,
                    desc=_clean(desc.text()) if desc else "",
                    image=src,
                    # BEST 뿐이다. NEW 는 이 사이트에 없다(docstring).
                    labels=[_clean(badge.text())] if badge and badge.text().strip()
                           else [],
                    # BEST 탭은 재탕이라 분류로 쓰지 않는다. 다만 BEST 탭에서
                    # 먼저 만난 5건은 여기로 떨어지므로 비워 둔다.
                    category="" if category == BEST_TAB else category,
                    uploaded_at=_uploaded_at(c, src, stamps),
                    # 이 사이트에는 신제품 배지가 없다. 모름을 모름으로 둔다.
                    is_new=None,
                    # 1+1·할인 행사가 이 사이트에 없다. 사이드 세트는 promo 가 아니다.
                    promo=False,
                    url=href,
                ))
    return items
