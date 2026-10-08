"""앤티앤스(Auntie Anne's) — 프레즐.

`CANDIDATES-BAKERY.md` §3 이 **"규칙상 허용인데 의도는 정반대다"** 로 접은 곳이다.
robots 에 `User-agent: *` 그룹이 **아예 없고** 대신 GPTBot·ChatGPT-User·CCBot·
ClaudeBot·Amazonbot 등 AI·데이터 봇 수십 종을 하나씩 `Disallow: /` 한다. 우리 UA 는
목록에 없어 규칙상으론 통과였지만, 브랜드 의사표시로 보고 붙이지 않았다.
**2026-10-02 운영자가 robots 무시를 승인**해서 다시 연다. 2026-10-08 실측.

## 경로

1차가 "홈이 8KB 스플래시"라고 남긴 그대로다. `https://www.auntieannes.co.kr/` 는
7,992바이트 '브랜드 홈페이지 / 창업 홈페이지' 갈림길이고 **본체는 `/main.html`** 이다.
워드프레스(Enfold 테마)인데 상품은 커스텀 테이블이라 REST 로는 안 나온다.

  GET /product-all/?cate=all   **한 장에 전부 있다** (143KB)
  GET /menu-new                NEW 만. ⚠️ **상품명이 안 들어 있다** — §아래

`?cate=all` 한 장이면 끝난다. `classic/stick/hotdog/deep/ade/coffee` 카테고리별 URL 도
있지만 받을 이유가 없다.

## 한 페이지 안에 영역이 **셋**이다. 섞으면 안 된다

```
.new-wrap02 .avia-image-container        신제품 10건  ← href 에 &type=new
.grid-entry .grid-entry-title             베스트  4건  ← 카테고리와 중복이다. 안 쓴다
.menu-list(6칸) .grid-entry               전 메뉴 48건
     클래식 프레즐 6 · 스틱 프레즐 8 · 핫도그 프레즐 3 · 딥 4 · 에이드 12 · 커피 15
```

⚠️ **신제품 영역과 나머지는 마크업이 아예 다르다.**
- 신제품: 이름이 **`<img alt="베이컨 피자">`** 에만 있다. 제목 태그가 없다.
- 전 메뉴: 이름이 `<h3 class="entry-content-header"><span>Original Pretzel</span>
  오리지널 프레즐</h3>` 이고 **`img alt` 는 `sweetpotato_creamcheese_stick-list` 라는
  엉뚱한 고정 문자열**이다(테마 더미값). alt 를 믿고 긁으면 48건이 전부 같은 이름이 된다.

`/menu-new` 는 따로 받지 않는다. 같은 10건인데 거기선 alt 까지 더미로 채워져 있어
**상품명을 하나도 못 뽑는다.** `?cate=all` 의 신제품 영역이 유일하게 이름을 준다.

## 신제품 신호 — **전 메뉴 48건 중 10건 (20.8%)**

```
베이컨 피자 · 할라피뇨 피자 · 페퍼로니 피자 · 치즈피자          2026-09-23
파인애플/자몽/청포도 오렌지에이드                              2026-04-30
고구마 크림치즈 스틱 · 아몬드 ~ · 베이컨 치즈 ~                 2025-08-29
```

🔴 **하이오커피와 같은 '1년치 바구니'다.** 2025-08 부터 2026-09 까지 세 묶음이 그대로
쌓여 있다 — 고구마 크림치즈 스틱은 **13개월 전** 것이다. 신제품 탭이 있다는 사실만으로
`is_new=True` 를 올리면 작년 상품이 오늘 신상으로 뜬다.
**그래서 날짜가 반드시 붙어야 하고, 걸러내는 건 `collect` 의 60일 창에 맡긴다.**
날짜를 비우면 `is_new=True` 가 창 검사를 통째로 건너뛴다(함정 #5).

## 날짜 — 이미지 URL 의 캐시버스터 epoch. **`released_at` 이 아니다**

썸네일이 `/pds/menu/70_s?1790128850` 꼴이고 쿼리가 **유닉스 초**다.

컴포즈커피(2026-06-16 149건)·블루샥처럼 **이미지 Last-Modified 가 배포 시각이라 가짜**
였던 전례가 있어서 의심하고 분포를 봤는데, 여기는 진짜다 —
- 전 메뉴 48건 중 다수가 `1731985109 / 1731985188 / 1731985252 / 1731985345` 처럼
  **2024-11-19 에 몇십 초 간격**으로 찍혀 있다. 사이트 구축 때 한 번에 올린 것이다.
- 신제품 10건만 `2025-08-29`·`2026-04-30`·`2026-09-23` 로 **묶음별로 따로** 찍힌다.
배포 시각이면 전건이 같은 값이어야 하는데 레코드마다 다르고 묶음 경계와 맞는다.

그래도 사진 올린 시각이지 브랜드가 "출시일"이라고 말한 값이 아니다. 2024-11-19 덩어리는
일괄 등록이기도 하다. **`uploaded_at` 에만 넣는다**(`rules.untrust_bulk_dates()` 가
보는 자리).

상세는 `/product-detail/index.html?s_type=<A|C|E|G|I|K>&p_no=<n>` 이다.

등록 제안: 유형 **`CAFE`**, 세부분류 `베이커리`.
⚠️ `FRANCHISE` 로 넣으면 1단 탭이 '카페'가 아니라 '외식'으로 간다.
"""
import re
from datetime import datetime, timezone

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "앤티앤스"
SITE = "https://www.auntieannes.co.kr"
LIST = SITE + "/product-all/?cate=all"

# `/pds/menu/70_s?1790128850` 의 쿼리는 유닉스 초다.
_STAMP = re.compile(r"\?(\d{9,11})(?:$|&)")
# 테마가 넣어 둔 더미 alt. 전 메뉴 48건이 전부 이 값이라 이름으로 쓰면 안 된다.
_DUMMY_ALT = "sweetpotato_creamcheese_stick-list"


def _abs(src: str) -> str:
    src = (src or "").strip()
    if not src:
        return ""
    return SITE + src if src.startswith("/") else src


def _href(a) -> str:
    # selectolax 는 값 없는 속성에 None 을 준다. 기본값이 안 먹는다.
    h = (a.attributes.get("href") or "") if a else ""
    return SITE + "/product-detail/" + h.split("product-detail/", 1)[1] \
        if "product-detail/" in h else h


def _uploaded_at(src: str) -> str:
    m = _STAMP.search(src or "")
    if not m:
        return ""
    try:
        ts = datetime.fromtimestamp(int(m.group(1)), tz=timezone.utc)
    except (ValueError, OSError, OverflowError):
        return ""
    # 2000년 이전·먼 미래는 캐시버스터가 아니라 다른 값이다
    if not (2000 <= ts.year <= datetime.now(timezone.utc).year + 1):
        return ""
    return ts.date().isoformat()


def _new_rows(doc) -> list:
    """신제품 영역. 이름이 `img alt` 에만 있다."""
    out = []
    for box in doc.css(".new-wrap02 .avia-image-container"):
        img = box.css_first("img")
        alt = " ".join((img.attributes.get("alt") or "").split()) if img else ""
        if not alt or alt == _DUMMY_ALT:
            continue
        out.append((alt, "", "", _abs(img.attributes.get("src") or ""),
                    _href(box.css_first("a")),
                    _uploaded_at(img.attributes.get("src") or "")))
    return out


def _all_rows(doc) -> list:
    """카테고리 6칸. 이름은 `h3.entry-content-header` 고 alt 는 더미다."""
    out = []
    for sec in doc.css(".menu-list"):
        cate = sec.css_first(".product-cate")
        cate = " ".join(cate.text().split()) if cate else ""
        for e in sec.css(".grid-entry"):
            head = e.css_first("h3.entry-content-header")
            if not head:
                continue
            en = head.css_first("span")
            name_en = " ".join(en.text().split()) if en else ""
            full = " ".join(head.text().split())
            # <span>영문</span> 뒤가 국문이다. 영문을 떼어 낸 나머지를 쓴다.
            name = full[len(name_en):].strip() if name_en and full.startswith(name_en) else full
            if not name:
                continue
            img = e.css_first("img")
            src = (img.attributes.get("src") or "") if img else ""
            out.append((name, name_en, cate, _abs(src),
                        _href(e.css_first("a")), _uploaded_at(src)))
    return out


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()
        doc = HTMLParser(r.text)

    new_rows = _new_rows(doc)
    all_rows = _all_rows(doc)
    if not all_rows:
        raise RuntimeError(
            f"{LIST}: 전 메뉴 0건 — '.menu-list .grid-entry h3.entry-content-header' "
            f"가 깨졌다. 2026-10-08 실측은 6칸 48건이었다")
    if not new_rows:
        raise RuntimeError(
            f"{LIST}: 신제품 0건 — '.new-wrap02 .avia-image-container' 가 깨졌거나 "
            f"alt 가 더미('{_DUMMY_ALT}')로 바뀌었다. 2026-10-08 실측은 10건이었다")

    items: list[Item] = []
    seen = set()
    # 신제품을 먼저 넣는다. 같은 상품이 카테고리에도 있어서 순서를 바꾸면
    # is_new=False 쪽이 이긴다.
    for rows, is_new in ((new_rows, True), (all_rows, False)):
        for name, name_en, cate, image, url, uploaded in rows:
            it = Item(
                brand=BRAND,
                name=name,
                name_en=name_en,
                image=image,
                category=cate,
                # 사진 캐시버스터의 epoch 다. 2024-11-19 에 몰린 사이트 구축
                # 일괄 등록이 섞여 있어 released_at 에 넣지 않는다.
                uploaded_at=uploaded,
                is_new=is_new,
                url=url,
            )
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)

    new_count = sum(1 for i in items if i.is_new)
    if new_count > len(items) * 0.5:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {new_count}건이 신제품이다 — 2026-10-08 "
            f"실측은 48건 중 10건(20.8%)이었다. 카테고리 영역을 못 읽은 것 아닌지 보라")
    dated = sum(1 for i in items if i.uploaded_at)
    if dated < len(items) * 0.9:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 날짜를 {dated}건밖에 못 읽었다 — 썸네일의 "
            f"'?<유닉스초>' 캐시버스터가 사라졌다. 신제품 탭이 1년치 바구니라 "
            f"**날짜 없이는 작년 상품이 신상으로 뜬다**")
    return items
