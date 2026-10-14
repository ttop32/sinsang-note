"""카페16온스(CAFE 16OZ COFFEE) — 부산 기반 커피 프랜차이즈. **(CAFE, "커피")**

등록 담당자에게: `(CAFE, "커피")` · SITES `https://cafe16oz.com/bbs/m01.php`

공정위 `커피` 289곳(가맹점 5+) 중 **98위(가맹점 31개)**. `notes/CANDIDATES-CAFE5.md` §6
"다음 후보 2순위". 2026-10-14 실측.

## 경로 — `메뉴소개 > 신메뉴` 한 장. 손으로 짠 정적 HTML 이다

```
GET https://cafe16oz.com/bbs/m01.php    34KB   카드 4장
```
카드는 `div.menu.sample_image` → `h5`(한글명) · `p`(영문명) · `img`(`/img/<파일>.png`).
그누보드 껍데기 위에 **하드코딩된 페이지**라 페이징·목록 API 가 없다.
```
리치 아이스티     LYCHEE ICETEA         /img/LYCHEE-ICETEA.png
리치 에이드       LYCHEE ADE            /img/LYCHEE-ADE.png
리치 캐모마일     LYCHEE CHAMOMILE      /img/LYCHEE-CHAMOMILE.png
블랙시크릿라떼    Black Secret Latt     /img/coffee23.png
```
`전메뉴`(`/bbs/m02.php`, 카드 24장)는 배지·날짜 없는 메뉴판이라 읽지 않는다.
없는 경로는 정직하게 404 다(`/bbs/m09.php` → 404 / 209B) — soft-404 사이트가 아니다.

## 신제품 신호 — 브랜드 전용 '신메뉴' 칸 + 이미지 파일의 `Last-Modified`

상품 단위로 떨어지는 신메뉴 칸이다(CAFE5 의 74곳 중 이런 곳은 드물었다). 다만 **날짜가 없다**.
이미지가 정적 파일이라 `HEAD` 의 `Last-Modified` 가 곧 그 파일을 서버에 올린 시각이다:
```
LYCHEE-ICETEA.png      Thu, 15 Jan 2026 04:48:27 GMT
LYCHEE-ADE.png         Thu, 15 Jan 2026 04:51:10 GMT     ← 셋이 13분 안에 하나씩
LYCHEE-CHAMOMILE.png   Thu, 15 Jan 2026 05:00:58 GMT
coffee23.png           Thu, 27 Nov 2025 01:05:04 GMT
(대조) logo.png        Wed, 03 Sep 2025 00:37:48 GMT     ← 사이트를 연 날
(대조) coffee01.png    Wed, 10 Sep 2025 10:43:11 GMT     ← 전메뉴 첫 장
```
초 단위로 갈리고 사이트 오픈일(로고)과 다르다 — 배포 시각이 아니라 하나씩 올린 것이다.
그래도 '파일을 올린 날'이지 출시일이 아니라 `uploaded_at` 에만 넣는다(함정 ⑤).

🔴 **정적 파일 날짜의 약점 — 사진을 한꺼번에 다시 올리면 전부 그날이 된다.** 실제 선례가 있다:
전메뉴(`m02`) 이미지 21장이 **2025-09-10 10:43·10:56 두 번**에 몰려 올라갔고 그날 `logo.png` 는
09-03 그대로였다(검수 실측) — **로고 하나로는 일괄 업로드를 못 가린다.** 그래서 **전메뉴의 `/img` 파일
(신메뉴 카드 파일 제외) + 로고를 대조 묶음으로 전부 `HEAD` 한다**(실측 24장). 카드 사진의 시각 **±2시간 안에
대조 파일이 3개 이상** 있으면 일괄 업로드로 보고 그 카드의 날짜를 버린다(날짜를 잃으면 `is_new` 도 안 준다).
날짜가 아니라 **시각 차**로 비교하는 건 재배포가 KST 자정을 넘길 때 날짜 비교가 갈리기 때문이다.
실측: 리치 3종(01-15 13:48~14:00 KST)·블랙시크릿라떼(11-27) 주변 대조 파일 **0개** → 날짜 유지.
⚠️ **남는 구멍** — `coffee23.png`(블랙시크릿라떼)는 전메뉴와 **같은 파일**이라 그 사진 **한 장만** 갈면
옛 상품 1건이 60일 동안 신상으로 뜬다. 낱장 교체는 대조로 못 가린다. 그래서 대조 묶음에서 카드 파일을 뺀다
(빼지 않으면 자기 자신과 겹쳐 셈이 틀어진다). 카드 수는 원문의 `sample_image` 등장 횟수와 맞춘다.

배지 비율: 칸 전체가 '신메뉴' 라 **4/4 (100%)**. 100% 는 신제품 전용 칸이면 정상이고(뚜레쥬르·
에밀리아젤라또 선례), 날짜가 이 칸을 걸러 준다 — `is_new=True` 여도 `rules.is_fresh()` 는
날짜가 있으면 날짜를 따른다. 날짜를 못 읽으면 `is_new` 를 주지 않는다(함정 ④).
⚠️ 이 칸은 **새 상품이 올라와도 옛 상품을 바로 안 내린다**(지금 9개월 묵은 리치 3종이 그대로다).
그래서 배지가 아니라 날짜가 판정을 해야 한다.

## 오늘(2026-10-14) 화면 — 0건이 정상

가장 최근 파일이 2026-01-15(9개월 전). 다음 신메뉴 이미지가 올라오면 그날 잡힌다.
"""
import re
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "카페16온스"
SITE = "https://cafe16oz.com"
URL = SITE + "/bbs/m01.php"
ALL = SITE + "/bbs/m02.php"          # 전메뉴 — 대조 파일 묶음(읽기만, 상품으로 안 쓴다)
DELAY = 0.7

MIN_ITEMS = 2          # 실측 4. 이 칸은 옛 상품을 안 내리므로 1장만 남는 건 구조가 깨진 것이다
MAX_ITEMS = 30
BULK_WINDOW = timedelta(hours=2)   # 이 시간 안에 다른 사이트 파일이 몰려 있으면 일괄 업로드
BULK_MIN = 3                       # 실측: 정상 2026-01-15·2025-11-27 은 0개, 2025-09-10 일괄은 21장
MIN_CONTROLS = 10                  # 실측 전메뉴 이미지 24장(카드 파일 제외 23)
_KST = timezone(timedelta(hours=9))
_IMG = re.compile(r'<img[^>]+src="(/img/[^"]+)"')


def _lm(c, url: str) -> datetime | None:
    """HEAD Last-Modified → aware datetime. 못 읽으면 None."""
    try:
        h = base.retry(lambda: c.head(url))
    except Exception:
        return None
    lm = h.headers.get("last-modified") if h.status_code == 200 else None
    if not lm:
        return None
    try:
        return parsedate_to_datetime(lm)
    except (TypeError, ValueError):
        return None


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(URL))
        r.raise_for_status()
        cards = []
        for card in HTMLParser(r.text).css("div.menu.sample_image"):
            h5 = card.css_first("h5")
            name = " ".join(h5.text().split()) if h5 else ""
            if not name:
                continue
            en = card.css_first("p")
            img = card.css_first("img")
            src = (img.attributes.get("src") or "") if img else ""
            if src.startswith("/"):
                src = SITE + src
            cards.append((name, " ".join(en.text().split()) if en else "", src))
        # 카드 클래스가 일부만 바뀌면 남은 카드만 조용히 나간다 — 원문 개수와 맞춘다.
        raw_cards = r.text.count("sample_image")
        if not MIN_ITEMS <= len(cards) <= MAX_ITEMS or len(cards) != raw_cards:
            raise RuntimeError(
                f"{BRAND}: 신메뉴 카드 {len(cards)}장 / 원문 'sample_image' {raw_cards}회 — "
                f"2026-10-14 실측은 4/4 였다. 'div.menu.sample_image > h5' 가 깨졌는지 확인하라")
        card_files = {src.rsplit("/", 1)[-1] for _, _, src in cards}

        # 대조 파일 — 전메뉴의 /img 파일 중 신메뉴 카드가 아닌 것 + 로고.
        time.sleep(DELAY)
        a = base.retry(lambda: c.get(ALL))
        a.raise_for_status()
        controls = sorted({u for u in _IMG.findall(a.text)
                           if u.rsplit("/", 1)[-1] not in card_files} | {"/img/logo.png"})
        stamps = []
        for u in controls:
            time.sleep(DELAY)
            t = _lm(c, SITE + u)
            if t:
                stamps.append(t)
        dated = []
        for name, en, src in cards:
            time.sleep(DELAY)
            dated.append((name, en, src, _lm(c, src) if src else None))

    if len(stamps) < MIN_CONTROLS:
        raise RuntimeError(f"{BRAND}: 대조 파일 날짜를 {len(stamps)}개만 읽었다(실측 24) — "
                           f"일괄 업로드를 가릴 수 없으니 멈춘다")
    if not any(t for *_, t in dated):
        raise RuntimeError(f"{BRAND}: 신메뉴 이미지 {len(dated)}장 모두 Last-Modified 를 "
                           f"못 읽었다. 실측은 4/4 였다")

    items: list[Item] = []
    seen = set()
    for name, en, src, t in dated:
        d = ""
        if t:
            near = sum(1 for x in stamps if abs(x - t) <= BULK_WINDOW)
            # 다른 사이트 파일이 같은 시간대에 몰려 있으면 일괄 업로드다. 날짜를 버린다.
            if near < BULK_MIN:
                d = t.astimezone(_KST).date().isoformat()
        it = Item(brand=BRAND, name=name, name_en=en, image=src,
                  uploaded_at=d,
                  # 칸 전체가 '신메뉴' 다. 날짜를 못 믿으면 주지 않는다(함정 ④).
                  is_new=True if d else None,
                  url=URL)
        if it.key not in seen:
            seen.add(it.key)
            items.append(it)
    return items
