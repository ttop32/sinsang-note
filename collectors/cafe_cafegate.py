"""카페게이트 — (카페, 커피).

공정위 `커피` 업종 가맹점 **146개**(2024년 말, 프차몰 순위 30위). 커피와 샌드위치를
같이 파는 브랜드고, 베이커리 칸에 샌드위치·베이글·붕어빵이 들어 있다. 그래도 유형은
`CAFE` 다 — base.BRANDS 맨 위 규칙("빵집·빙수·아이스크림·도넛은 카페로 묶는다")과
같은 자리고, 세부분류는 `커피`.

아임웹(imweb)이다. **첫 화면만 보고 접으면 안 되는 곳이었다.** `https://www.cafegate.co.kr`
루트는 본문 텍스트가 413자뿐(JS 렌더)이라 "수집 불가" 로 보이는데, `sitemap.xml`
(robots 가 직접 가리킨다)에 경로 53개가 전부 적혀 있고 그 아래는 **정적 SSR** 이다.
컴포즈커피·네네치킨 선례와 같은 함정이다.

## 긁는 자리 — 메뉴 6칸 (2026-10-08 실측, 내비 순서 그대로)

```
/new           신메뉴          10건  ★ 브랜드가 직접 가른 칸
/coffee        커피&콜드브루   19건
/S_latte       논커피라떼      11건
/fra_smoothie  프라페&스무디   12건
/tea_ade       티&에이드       20건
/dessert       베이커리        23건
                              합계 95건 / 6요청
```
⚠️ sitemap 에 있는 **`/menu` 는 긁지 않는다.** `/coffee` 와 **같은 19건**이다
   (옛 경로가 남은 것). 넣으면 요청만 늘고 결과는 같다.

상품은 아임웹 갤러리 위젯이다 — `div.item_gallary` 안에
`div[id^=caption_]` 에 `<h4>` 상품명 · `<p>` 설명이 들어 있고, 이미지는
`._img_wrap` 의 `background-image: url(...)` 이다.
⚠️ `/new` 에는 **캡션이 없는 포스터 배너가 38건 섞여 있다**(행사 안내 이미지).
   `<h4>` 가 비면 버린다. 안 버리면 이름 없는 카드가 38장 생긴다.

## 신제품 신호 — 상품명 접두 `[NEW]`. **95건 중 10건 (10.5%)**

```
[NEW] 10건  전부 /new 칸                       ← 나머지 5칸은 0건
그 외 85건  접두 없음
```
브랜드가 선별해서 붙이는 접두다. 배지가 요소가 아니라 **상품명 문자열 안**에
들어 있는 모양이라 셀렉터로는 안 잡힌다(병아리김밥 `<h6>new …</h6>` 와 같은 자리).
`[NEW]` 는 이름에서 떼고 `is_new` 로 옮긴다 — 안 떼면 카드에 `[NEW]올데이 딥 라떼`
라고 찍힌다.

### 🔴 `/new` 칸 밖 85건은 `is_new=False` — **의도적으로 영구 제외한다**

`rules.is_fresh` 의 `is_new is False` 분기는 `released_at` 을 요구하는데 이
브랜드는 `released_at` 을 주지 않는다. 즉 **95건 중 85건은 어떤 날짜가 붙어도
화면에 영원히 안 나온다.** 더플레이스가 이 길로 영구 0건이 됐던 그 분기다.
여기서는 **알고 그렇게 둔다.** 근거 —

- 접두는 "아무 말 안 함" 이 아니라 **브랜드가 가른 표시**다. 리터럴 `[NEW]` 가
  6페이지 전체에서 **정확히 20회**(상품 10개 × 캡션 div + 라이트박스 title)고
  나머지 5칸에는 **0회**다. 같은 사이트가 같은 방식으로 10건에만 붙였다.
- 그러니 나머지 85건은 `None`(모름)이 아니라 `False`(브랜드가 상시 메뉴라고
  말함)가 맞다. 도미노 선례와 같은 자리다.
- `None` 으로 바꾸면 `uploaded_at` 이 살아나는데 **그 값을 믿으면 안 된다.**
  imweb 썸네일 경로 날짜는 사진을 다시 올리면 따라 움직인다(아래 §날짜의
  `자스민 밀크티` 한 카드 안 2종 날짜). 도미노 2026-09-14 재업로드 9건에
  2020년부터 팔던 슈퍼디럭스가 섞인 사고가 정확히 그 경로다.
- 그래서 이 브랜드가 화면에 올릴 수 있는 최대치는 **`[NEW]` 10건으로 구조적으로
  묶여 있다.** 메뉴판 전체가 신상으로 새는 경로가 닫혀 있다는 뜻이기도 하다.

85건을 버리면서도 받아 오는 이유는 **배지 비율의 분모**이기 때문이다. 아래
`NEW_MAX_RATIO` 가드가 그 분모로 "신메뉴 칸이 메뉴판을 삼켰는지"를 잡는다.

## 날짜 — 이미지 CDN 경로의 `YYYYMMDD`. **`uploaded_at` 에만 넣는다**

이미지가 `https://cdn.imweb.me/thumbnail/20260907/<해시>.png` 다.

🔴 **이미지 시각은 가짜일 때가 많아서(컴포즈 149건 일괄·블루샥 배포시각·쑝쑝돈까스
CDN 재생성) 분포를 먼저 쟀다.** 2026-10-08 실측 —

```
/new 10건의 묶음      공지사항(/notice)의 출시 공지                       차
20260907 × 4건   ←→   2026-09-10 "더 완벽해진 시그니처 신메뉴 4종 출시"   -3일
20260602 × 2건   ←→   2026-06-05 "아이스크림 신메뉴 2종 출시"             -3일
20260803 × 4건   ←→   2026-08-18 "자스민 음료 4종 출시"                   -15일
```
**건수는 세 묶음 다 맞는다(4·2·4).** 날짜는 **이미지 쪽이 3~15일 먼저**고 공지보다
늦은 적은 없다 — 포스터를 올려 두고 며칠 뒤 공지를 쓰는 순서라 방향은 맞다.
⚠️ 다만 **"묶음 경계가 공지와 그대로 맞는다"고 쓰면 과장이다.** 2026-08-03 은
   공지판에 실재하는 날짜이긴 한데 **다른 상품 공지**(#57 에너지 음료 3종, 그
   3종은 메뉴 6칸에 없다)라서 우연일 수 있다. 맞춰진 건 건수와 순서뿐이다.

배포 시각은 아니다 — 날짜가 16종이고 2023-05-14 ~ 2026-09-07 로 흩어져 있다.
옛 메뉴는 옛 날짜를 그대로 들고 있다(아메리카노 20230514). 앤티앤스·송사부와
같은 '진짜' 쪽이다.

⚠️ **한 카드 안에서 날짜가 갈리는 경우가 있다.** `/new` 10장 중 `자스민 밀크티`
   한 장만 배경 이미지가 `20260803`, 같은 카드의 라이트박스 이미지가 `20260827`
   (24일 차)이다. 나머지 9장은 한 가지뿐이다. 어댑터는 **배경 이미지 쪽**을
   쓴다(같은 묶음 4건이 한 날짜로 모이는 쪽). 즉 이 값은 '사진을 올린 날' 이지
   상품의 날짜가 아니다.

그래서 브랜드가 "출시일" 이라고 말한 값이 아니므로 **`released_at` 은 비우고
`uploaded_at` 에만** 넣는다(파리바게뜨 312장 선례).

🟡 **대가가 있다.** 자스민 4종은 실제 출시가 2026-08-18(51일 전)이라 60일 창
   안인데 이미지 날짜 08-03(66일 전) 때문에 떨어진다 — `[NEW]` 10건 중 오늘
   화면에 오르는 건 4건뿐이다. 창 밖으로 **일찍 떨어지는** 방향이라 가짜 신상이
   뜨는 사고보다는 낫다고 보고 그대로 둔다. 고치려면 `/notice` 를 1요청 더 받아
   묶음에 출시일을 붙이면 된다(위 표가 그 작업을 손으로 한 것이다). 아래
   §공지사항의 "못 쓴다" 는 **상품명으로 못 쓴다**는 뜻이지 날짜로 못 쓴다는
   뜻이 아니다.

⚠️ `uploaded_at` 최대 묶음이 **2023-06-19 에 32건**이다. 사이트를 처음 만들며
   한꺼번에 올린 자국으로 보인다(커피·논커피·티에이드·프라페·베이커리 다섯 칸에
   걸쳐 있다). 전부 `is_new=False` 라 화면에는 영향이 없고, `released_at` 에는
   들어가지 않는다. `rules.untrust_bulk_dates()` 는 `BULK_MIN=20` 은 넘지만
   중앙값 기준 비율에서 안 걸리므로 **아래 로컬 가드가 유일한 방어**다.

## 공지사항은 수집하지 않는다

`/notice`(공지사항)·`/press`(보도자료)·`/event` 에 날짜가 붙은 출시 공지가 있고
위에서 날짜 검증에 썼지만, 글 제목이 상품명이 아니라 기사 제목
("찬바람 불 때 생각나는 길거리토스트 2종 재출시")이라 Item.name 으로 못 쓴다.
상품 단위는 메뉴 6칸이 이미 정확히 준다. **'재출시' 가 섞여 있다는 것도 이유다** —
2026-10-01 자 두 건이 전부 재출시고, 그건 신상이 아니다.

## desc 가 칸마다 다르다

`/new` 의 `<p>` 는 한글 소개문이고, 나머지 5칸의 `<p>` 는 **영문 상품명**이다
(`Lemon Americano`). 그래서 `/new` 는 `desc`, 나머지는 `name_en` 에 넣는다.
섞으면 카드 설명에 영문 이름만 찍힌다.

## 그 밖

- 상품 상세 페이지가 없다(갤러리 라이트박스). `Item.url` 은 그 상품이 있는
  **칸 주소**로 둔다.
- 굿즈 칸이 없다. 95건 전부 먹는 것이다.
- 술 없음.
- robots(200, 233B): `User-agent: * / Allow: /` 에 Disallow 7줄이 로그인·장바구니·
  관리자·`/?mode*` 다. 우리가 때리는 6경로는 어디에도 안 걸린다. sitemap 도 적혀 있다.

등록 제안: 유형 `CAFE`, 세부분류 `커피`
          SITES `https://cafegate.co.kr/new`
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "카페게이트"
SITE = "https://cafegate.co.kr"
DELAY = 2.0

# 내비 순서 그대로. 첫 칸이 브랜드가 가른 '신메뉴' 다.
# ⚠️ sitemap 의 `/menu` 는 `/coffee` 와 같은 19건이라 넣지 않는다.
# 🔴 **순서를 바꾸지 마라(알파벳순 정리 금지).** `seen` 이 칸을 가로질러
#    공유되고 **먼저 본 쪽이 이긴다.** 지금은 `/new` 10건이 다른 5칸과 이름이
#    하나도 안 겹쳐서(2026-10-08 실측) 무해하지만, 겹치는 날 `/new` 가 뒤로
#    밀리면 `is_new=True` 가 조용히 `False` 로 바뀐다.
NEW_PATH = "new"
PAGES = {
    "new": "신메뉴",
    "coffee": "커피&콜드브루",
    "S_latte": "논커피라떼",
    "fra_smoothie": "프라페&스무디",
    "tea_ade": "티&에이드",
    "dessert": "베이커리",
}

MIN_ITEMS = 60        # 2026-10-08 실측 95건
MIN_PER_PAGE = 5      # 가장 작은 칸(신메뉴)이 원시 10장
# 신메뉴 비율 상한. 2026-10-08 실측 10/95 = 10.5% 다.
# 레포 관례는 '절반'(하이오 `len(items)//2`, 퀴즈노스 66/66 사고)인데 여기선
# **0.25 로 조인다** — 화면에 오를 수 있는 게 `[NEW]` 10건뿐이라 그 수가 두 배
# 넘게 뛰면 그 자체가 사고다. 절반(47건)에 두면 `/new` 가 40건이 돼도 안 걸린다.
NEW_MAX_RATIO = 0.25
# 업로드일 종류의 하한. 전건이 한 날이면 imweb 이 썸네일을 일괄 재생성한 것이다
# (컴포즈 2026-06-16 149건 선례). rules.untrust_bulk_dates() 는 여길 못 잡는다.
MIN_DATE_KINDS = 5    # 2026-10-08 실측 16종

_NEW_PREFIX = re.compile(r"^\s*\[\s*NEW\s*\]\s*", re.I)
_CDN_DATE = re.compile(r"cdn\.imweb\.me/thumbnail/(\d{4})(\d{2})(\d{2})/")
_BG_URL = re.compile(r"url\((['\"]?)(https?://[^)'\"]+)\1\)")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _image(card) -> str:
    """`._img_wrap` 의 background-image. 비면 data-bg 를 본다."""
    node = card.css_first("._img_wrap")
    if not node:
        return ""
    # ⚠️ selectolax 의 .attributes.get(k, "") 는 **값 없는 속성에 None** 을 준다.
    #    태리로제떡볶이 56건이 그렇게 증발했다. or "" 로 받는다.
    for raw in (node.attributes.get("style") or "", node.attributes.get("data-bg") or ""):
        m = _BG_URL.search(raw)
        if m:
            return m.group(2)
    return ""


def _uploaded_at(img: str) -> str:
    m = _CDN_DATE.search(img or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()

    with base.client(headers={"Referer": SITE + "/"}) as c:
        for i, (path, label) in enumerate(PAGES.items()):
            if i:
                time.sleep(DELAY)
            url = f"{SITE}/{path}"
            r = base.retry(lambda: c.get(url))
            r.raise_for_status()
            cards = HTMLParser(r.text).css(".item_gallary")
            if not cards:
                raise RuntimeError(
                    f"{BRAND} {label}({path}): 갤러리 항목 0건 — "
                    f"아임웹 위젯 마크업(.item_gallary)이 바뀌었을 수 있다")

            got = 0
            for card in cards:
                cap = card.css_first("[id^=caption_]")
                if not cap:
                    continue
                h = cap.css_first("h4")
                raw = _clean(h.text() if h else "")
                # 캡션 없는 포스터 배너. /new 에만 38건 섞여 있다.
                if not raw:
                    continue
                is_new = bool(_NEW_PREFIX.match(raw))
                name = _NEW_PREFIX.sub("", raw)
                if not name:
                    continue
                p = cap.css_first("p")
                text = _clean(p.text() if p else "")
                img = _image(card)
                it = Item(
                    brand=BRAND,
                    name=name,
                    # /new 의 <p> 는 한글 소개문, 나머지 5칸은 영문 상품명이다.
                    desc=text if path == NEW_PATH else "",
                    name_en="" if path == NEW_PATH else text,
                    image=img,
                    category=label,
                    # 이미지 CDN 경로의 날짜. 출시일이 아니므로 released_at 은 비운다.
                    uploaded_at=_uploaded_at(img),
                    is_new=is_new,
                    url=url,
                )
                got += 1
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)

            # ⚠️ `got` 은 **중복 제거 전** 숫자다(같은 상품이 추천 칸과 본 칸에
            #    두 번 걸린다). 아래 실측값도 중복 제거 전으로 적어야 터졌을 때
            #    사람이 비교할 수 있다 — 중복 제거 후는 10/19/11/12/20/23 이다.
            if got < MIN_PER_PAGE:
                raise RuntimeError(
                    f"{BRAND} {label}({path}): 캡션이 붙은 카드가 {got}장뿐이다 — "
                    f"2026-10-08 실측(중복 제거 전)은 신메뉴 10 / 커피 23 / "
                    f"논커피라떼 14 / 프라페 15 / 티에이드 23 / 베이커리 25 였다")

    if len(items) < MIN_ITEMS:
        raise RuntimeError(
            f"{BRAND}: 상품 {len(items)}건 — 2026-10-08 실측은 95건이었다. "
            f"칸이 빠졌거나 캡션 구조가 바뀌었는지 확인하라")

    new = sum(1 for i in items if i.is_new)
    if not new:
        raise RuntimeError(
            f"{BRAND}: `[NEW]` 접두가 0건이다 — 배지가 상품명 문자열 안에 있는 "
            f"브랜드라 접두 표기가 바뀌면 조용히 0건이 된다(2026-10-08 실측 10건)")
    if new > len(items) * NEW_MAX_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {new}건이 `[NEW]` 다 — 2026-10-08 실측은 "
            f"10/95(10.5%)였다. 메뉴판이 통째로 신상으로 올라간다")

    dated = sum(1 for i in items if i.uploaded_at)
    if dated < len(items) * 0.9:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 날짜를 {dated}건밖에 못 읽었다 — "
            f"이미지가 cdn.imweb.me/thumbnail/<날짜>/ 경로를 벗어났다. "
            f"날짜를 비우면 60일 창을 건너뛴다")

    noimg = sum(1 for i in items if not i.image)
    if noimg > len(items) * 0.1:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {noimg}건에 이미지가 없다 — "
            f"`._img_wrap` 의 background-image 가 바뀌었을 수 있다")

    # imweb 이 썸네일을 일괄 재생성하면 95건이 한 날짜가 된다. 그러면 메뉴판
    # 전체가 최근 날짜를 들게 되는데, `rules.untrust_bulk_dates()` 는 날짜
    # 종류가 적을수록 오히려 안 걸린다. 여기서 직접 받는다.
    kinds = len({i.uploaded_at for i in items if i.uploaded_at})
    if kinds < MIN_DATE_KINDS:
        raise RuntimeError(
            f"{BRAND}: 업로드일이 {kinds}종뿐이다 — 2026-10-08 실측은 16종"
            f"(2023-05-14 ~ 2026-09-07)이었다. 썸네일이 일괄 재생성됐는지 확인하라")
    return items
