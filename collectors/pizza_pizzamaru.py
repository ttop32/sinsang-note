"""피자마루. 등록 담당자에게: **(FRANCHISE, "피자")**.

가맹점 498개로 공정위 `피자`(I1) 2위다. 완전 SSR 이라 카테고리 10장만 받으면
이름·설명·가격·이미지가 전부 첫 HTML 에 들어온다. http·https 둘 다 200 이고
apex·www 둘 다 열린다. https 를 쓴다.

🔴 **앞선 조사의 "신메뉴 전용 페이지 + '신제품순' 정렬" 은 둘 다 신호가 아니다.**
2026-10-08 에 네 갈래로 검증했고 넷 다 떨어졌다. 그래서 이 어댑터는
`/menu/10`(신메뉴)을 **신상 근거로 쓰지 않는다.**

  ① 겹침 — `/menu/10` 9건 중 3건(아메리칸체다 피자 · BBQ치폴레 피자 · 레드콘
     피자)이 상설 카테고리 `/menu/26`(골드&바이트)에 **같은 이름으로 또 있다.**
     도우만 다른 같은 제품이라 상품 id 는 다르다. 신메뉴 칸에 올려둔 채
     상설 라인에도 넣어 파는 중이라는 뜻이다.
  ② 날짜 모순 — `/menu/10` 9건의 등록 시각이 **2024-11-12 ~ 2026-10-01, 23개월에
     걸쳐 있다.** 하이오커피(10월에 쌍화차와 컵빙수 공존)와 같은 '1년치 바구니'
     인데 폭이 그보다 두 배다. 계절도 어긋난다 — 겨울 한정(2025-12 불닭
     치즈폭탄피자 세트)·여름 한정(2026-05 닭꼬치 4종 세트·혼밥박스)·가을 한정
     (2026-10 피자설기 3종)이 한 화면에 같이 있다. 9건 중 5건이 `[기간한정판매]`
     ·`[한정판매]`·`세트` 다.
  ③ '신제품순' 정렬 — **존재하지 않는다.** 그 블록은 10개 카테고리 전부에서
     `<!-- ... -->` 주석 안에 있고 `<a href="">` 로 링크도 비어 있다. 주석을
     걷어내면 '신제품순' 글자가 0회다(10/10 페이지 실측). 정렬 쿼리파라미터도 없다.
  ④ NEW 배지 — **0건이다.** `<span class="new">`·`<span class="best">` 가 카드
     81개 **전부**에 들어 있지만 **81건 100% 가 주석 안**이다. 주석을 걷어내면
     살아있는 배지가 0개다. 배지 비율로 적으면 `0/81 (0%)` 이다.
     (설빙 사고의 반대 꼴이다 — 거기선 존재만 세서 늙은 배지를 신상으로 읽었고,
      여기선 마크업만 보면 전건이 NEW 로 보인다.)

## 그래도 어댑터를 만드는 이유 — 상품마다 진짜 등록 시각이 있다

메뉴판을 통째로 긁어 '전부 신상'으로 만들 셈이면 안 만드는 게 낫다. 여기는
그게 아니다. **상품 id 가 유닉스 시각이다.**

  /product/17908222007644 → 앞 10자리 1790822200 → 2026-10-01 11:36
  /product/15980189507337 → 앞 10자리 1598018950 → 2020-08-21 23:09

같은 값이 이미지 파일명에도 따로 찍힌다(`/d_fileinfo/img/01` + `YYYYMMDDHHMMSS`).
두 소스가 81건 전부에서 분 단위로 맞는다. 바깥 근거와도 맞는다 — 공지사항
`/company/09/` 의 출시 글과 대조했다(2026-10-08 실측):

  공지 `맵단짠 완벽조합! 레드콘 피자 출시!!`      2025-04-03 ↔ id 2025-04-02 09:40
  공지 `여기가 미국⁉ 아메리칸체다피자 출시`        2024-11-28 ↔ id 2024-11-12 13:40
  공지 `1인피자(8인치) 판매 매장 리스트`           2025-11-12 ↔ id 2025-11-14 11:04
  공지 `피자설기 판매매장 안내`                    2026-10-07 ↔ id 2026-10-01 11:36

⚠️ **이미지 파일명 쪽은 쓰지 않는다.** 사진을 갈아끼우면 날짜가 따라 올라간다 —
2020-08-21 에 등록된 이탈리안 치즈 피자·꿀고구마 피자·투움바 피자의 파일명이
2025-03-17 로 찍혀 있다(그날 7장을 한꺼번에 교체했다). 도미노 20260914 사고와
같은 함정이다. 상품 id 는 기본키라 사진을 바꿔도 안 움직인다.

⚠️ **`released_at` 이 아니라 `uploaded_at` 에 넣는다.** CMS 행 생성 시각이지
브랜드가 발표한 출시일이 아니고, 한 번 일괄 등록 자국이 있다 — 81건 중
**2020-08-21 밤 21:33~23:38 에 20건(25%)** 이 몰려 있다(지금 사이트를 세운 날이다.
푸터는 COPYRIGHT © 2015 지만 그 20건이 전부 그 밤에 찍혔다). `uploaded_at` 에
두면 `rules.untrust_bulk_dates()` 가 그런 묶음을 한 번 더 걸러준다.
2020년이라 60일 창에는 어차피 안 닿지만, 다음 개편 때를 위한 자리다.

날짜 분포(2026-10-08 실측, 81건):
  2020-08-21 20 · 2023-06-13 11 · 2026-05-18 6 · 1인피자 2025-11-14 5 ·
  2021-07-20~23 3 · 2022-03-03 2 · 2023-02-21 3 · 2024-07-03 3 · 2024-11-12 3 ·
  2025-04-02~03 4 · 2026-01-19 3 · 2026-10-01 3 · 나머지는 1~2건씩
몰린 세 날(2020-08-21 사이트 개장 · 2023-06-13 퍼스널 라인 신설 ·
2025-11-14 1인피자 라인 신설)은 전부 **라인 단위 출시**라 거짓은 아니다.

## 나머지

  - `is_new` 는 전건 None 이다. 배지가 없고(위 ④) 신메뉴 칸도 못 믿으니
    '모른다'가 정직하다. 판정은 `uploaded_at` 과 60일 창이 한다.
  - 카테고리 10개를 다 받고 `/menu/10`(신메뉴)만 **맨 뒤로 돌린다.** 이름이
    겹칠 때 Item.key 중복 제거가 앞엣것을 남기므로, 상설 카테고리 이름
    (골드&바이트 등)이 `category` 에 들어가고 '신메뉴' 라는 선반 이름이
    상품에 눌러붙지 않는다. 그래도 신메뉴 칸만 가진 4건(피자설기 3종 ·
    혼밥박스)은 거기서만 들어오므로 빼지 않는다.
  - 🔴 **이름이 겹치면 날짜는 제일 이른 것을 남긴다.** 카드 81개가 이름으로는
    62개고, 11개가 카테고리를 걸친다. 같은 제품을 도우 라인별로 따로 등록해서
    **옛 제품이 새 id 를 받는다** — `치즈 폭탄 피자` 는 시카고 라인에
    2021-07-06 에 있었는데 1인피자(8인치) 라인이 생긴 2025-11-14 에 또 등록됐고,
    `페퍼로니 치즈 폭탄 피자` 는 2020-08-21 → 2025-11-14 다. 카테고리 순서대로
    앞엣것을 남기면 2020년 메뉴가 2025년 신상이 된다. 가장 이른 날짜가
    '그 이름이 처음 생긴 때'라 그쪽을 쓴다.
  - `<li class="soldout">` 가 41건 붙는데 **품절이 아니다.** 설명이 전부
    `※일부 매장 한정 판매` 이고 품절 오버레이(`.sold_t`) 마크업은 안 들어온다.
    온라인 주문 대상이 아니라는 표시로 보여 거르지 않는다.
  - 설명은 `p.t2` 인데 전 상품 공통 안내문이 붙어 있다(`(본 사진은 이미지컷…)`
    73건 · `(본 가격은 포장…)` 62건 · `※일부 매장 한정 판매` 15건). 떼고 넣는다.
  - 가격(`p.t3`)은 Item 에 자리가 없어 버린다. 영문명은 사이트에 없다.
  - 상세 `/product/<id>` 는 날짜가 없고 원산지 표만 길다(118KB). 받지 않는다.
  - 주류·비식품은 없다. 상품 81건을 전부 눈으로 읽었다.
  - ⚠️ 이용약관 제9조가 복제·상업적 이용을 금지한다. 운영자가 2026-10-02 에
    robots·약관 제약 무시를 승인했다. 삭제 요청이 오면 즉시 내린다
    (이마트24·도미노피자와 같은 칸).
"""
import datetime
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "피자마루"
ROOT = "https://www.pizzamaru.co.kr"
DELAY = 1.5     # 요청 간격(초). 10회뿐이라 넉넉히 둔다.

# (경로번호, 내비게이션 표기). 순서가 의미를 갖는다 — 신메뉴(10)를 맨 뒤에 두어야
# 이름이 겹치는 상품이 상설 카테고리 이름을 갖는다(docstring §나머지).
CATEGORIES = (
    ("11", "클래식"),
    ("32", "1인피자(8인치)"),
    ("13", "몬스터"),
    ("26", "골드&바이트"),
    ("12", "프리미엄"),
    ("27", "시카고&치즈폭탄"),
    ("31", "퍼스널(마루업)"),
    ("14", "투탑박스"),
    ("15", "사이드 및 기타"),
    ("10", "신메뉴"),
)

CARD = ".prd_lst.menu_lst li"

# 상품 id 앞 10자리가 유닉스 시각이다. 뒤 4자리는 같은 초 안의 일련번호다.
_PID = re.compile(r"/product/(\d{14})")
# 사람이 만든 사이트라 id 길이가 달라질 수 있다. 상식 밖 시각은 버린다.
EPOCH_MIN = 1420070400   # 2015-01-01. 푸터 저작권 표기가 2015 다
EPOCH_SLACK = 86400      # 미래 하루까지는 봐준다(서버 시계 차이)

# 전 상품에 붙는 공통 안내문. 설명이 아니라 매장 운영 고지다.
_NOISE = re.compile(r"^(※|\(본 가격|\(본 사진|\(매장별 판매)")

# 한 날짜에 전체의 이만큼이 몰리면 사이트를 다시 세워 전 상품이 '오늘 등록'이
# 된 것이다. 건수는 그대로라 collect.py 의 0건·급감 가드에 안 걸린다.
# 지금 최대 묶음은 2020-08-21 의 20/81(25%)이다.
BULK_SHARE = 1 / 2


def _uploaded_at(href: str) -> str:
    """상품 id 앞 10자리(유닉스 시각)를 날짜로. 범위 밖이면 빈 값."""
    m = _PID.search(href)
    if not m:
        return ""
    epoch = int(m.group(1)[:10])
    now = int(time.time())
    if not EPOCH_MIN <= epoch <= now + EPOCH_SLACK:
        return ""
    return datetime.date.fromtimestamp(epoch).isoformat()


def _desc(li) -> str:
    """p.t2 에서 전 상품 공통 안내문을 뺀 설명."""
    node = li.css_first("p.t2")
    if node is None:
        return ""
    html = node.html or ""
    out = []
    for raw in re.split(r"<br\s*/?>", html):
        line = " ".join(HTMLParser(raw).text().split())
        if line and not _NOISE.match(line):
            out.append(line)
    return " ".join(out)


def _cards(html: str, category: str) -> list[Item]:
    items = []
    for li in HTMLParser(html).css(CARD):
        link = li.css_first("a[href*='/product/']")
        title = li.css_first("p.t1")
        if link is None or title is None:
            continue
        name = " ".join(title.text().split())
        if not name:
            continue
        # ⚠️ attributes.get(k, "") 은 값 없는 속성에 None 을 준다. or "" 로 받는다.
        href = link.attributes.get("href") or ""
        img = li.css_first(".img img")
        src = (img.attributes.get("src") or "") if img else ""
        items.append(Item(
            brand=BRAND,
            name=name,
            desc=_desc(li),
            image=ROOT + src if src.startswith("/") else src,
            category=category,
            # 상품 id 에 박힌 등록 시각. 출시일이 아니라 CMS 등록이라 uploaded_at 이다.
            uploaded_at=_uploaded_at(href),
            # 배지가 0건이고 '신메뉴' 칸도 못 믿는다. 모른다고 두는 게 정직하다.
            is_new=None,
            url=ROOT + href if href.startswith("/") else href,
        ))
    return items


def fetch() -> list[Item]:
    items: list[Item] = []
    seen: dict[str, Item] = {}
    with base.client() as c:
        for cid, category in CATEGORIES:
            r = base.retry(lambda: c.get(f"{ROOT}/menu/{cid}/"))
            r.raise_for_status()
            page = _cards(r.text, category)
            if not page:
                raise RuntimeError(f"피자마루 /menu/{cid}({category}) 가 0건 "
                                   "— 카드 셀렉터나 경로가 바뀌었다")
            for it in page:
                old = seen.get(it.key)
                if old is None:
                    seen[it.key] = it
                    items.append(it)
                # 같은 이름이 다른 도우 라인에 또 등록돼 있다. 날짜만 이른 쪽으로
                # 내린다 — 안 그러면 2020년 메뉴가 2025년 신상이 된다(docstring).
                elif it.uploaded_at and (not old.uploaded_at
                                         or it.uploaded_at < old.uploaded_at):
                    old.uploaded_at = it.uploaded_at
            time.sleep(DELAY)

    if not items:
        raise RuntimeError("피자마루 수집 0건 — 메뉴 경로가 바뀌었다")
    dated = [it for it in items if it.uploaded_at]
    # 이 브랜드는 날짜가 유일한 신상 근거다. 상품 id 모양이 바뀌면 전건 날짜가
    # 사라지는데, 건수는 그대로라 급감 가드에 안 걸리고 조용히 아무것도 안 낸다.
    if len(dated) < len(items) * 0.9:
        raise RuntimeError(f"피자마루 상품 id 날짜가 {len(dated)}/{len(items)}건뿐 "
                           "— /product/<유닉스시각> 꼴이 바뀌었다")
    top = max({it.uploaded_at for it in dated},
              key=lambda d: sum(1 for x in dated if x.uploaded_at == d))
    n = sum(1 for x in dated if x.uploaded_at == top)
    if n > len(dated) * BULK_SHARE:
        raise RuntimeError(
            f"피자마루 등록일이 {top} 한 날짜에 {n}/{len(dated)}건 몰렸다 "
            "— 사이트 재구축 일괄등록으로 보인다. 날짜로 쓰면 안 된다")
    return items
