"""STACKBEAN(스택빈) — 커피 프랜차이즈. 상품 번호가 곧 등록 시각이다. **(CAFE, "커피")**

등록 담당자에게: `(CAFE, "커피")` · SITES `http://stackbean.co.kr/product/list.php?ca_id=10`   (⚠️ http — https 자체서명)

공정위 `커피` 가맹점 5+ 중 **가맹점 5개**(프차몰 실측). `notes/CANDIDATES-CAFE6.md` 긴 꼬리에서 찾았다. 2026-10-14 실측.

## 경로 — 상위 칸 4개 × 페이징

```
GET http://stackbean.co.kr/product/list.php?ca_id=<칸>&page=N        한 쪽 8개
    10 NEW / HEALTHY 26건(4쪽) · 20 커피 25건(4쪽) · 30 음료 39건(5쪽) · 40 디저트 16건(2쪽)
```
⚠️ **홈 메뉴 링크(10·2010·3020·4010)만 따라가면 상품의 47%(49/105)밖에 못 받는다** — 2010·3020·4010 은 각 묶음의
**첫 하위 탭**이고, 목록 안에 하위 탭(2030 콜드브루·2040 시그니처·3030 티·3040 에이드·4020~4040 디저트·마카롱·샌드위치,
탭에 없는 2020 디카페인·3010 대용량)이 더 있다(검수 실측). 그래서 **상위 칸 20·30·40** 을 받는다 — 하위 탭의 합집합이다.
쪽 수는 목록의 `ul.paging a[href*="page="]` 가 알려 준다(함정 ⑦). 칸마다 실측 건수의 70% 밑이면 터뜨린다
(1쪽만 받히면 8+8+8+8=32건이라 전체 하한만으로는 못 잡는다 — 검수 재현).
카드 = `div.sub02_list li` → `.txt_wrap p`(상품명) · `img`(`/product/data/item/<번호>/…`). 상세 페이지는 없다(링크가 `#`).
`30` 칸의 **대용량 변형**(`1.1L 아이스 아메리카노`·`MAX 식혜` 등 8건)은 같은 음료의 크기라 뺀다.

## 신호 — 상품 번호(10자리) = **상품 레코드를 만든 유닉스 시각**

```
/product/data/item/1763430099/1763430099_l1.jpg     1763430099 = 2025-11-18 10:41 KST  (뱅쇼)
```
이 사이트는 영카트가 아니라 `GnCommon` 기반 자체 솔루션인데, 번호=생성 시각이 실측으로 성립한다(검수):
- 이미지 49장의 `Last-Modified` 가 **49/49 번호와 같거나 15초~34분 뒤**다(번호=폼 연 시각, 파일=저장 시각). 반례 0.
- 2025-08-21·11-18 묶음 **22/22쌍**에서 다음 상품 번호가 앞 상품의 파일 저장 시각보다 1초~3분 뒤 — 하나씩 손으로 올렸다.
- **사진을 갈아도 번호는 안 움직인다** — 일반 칸 23건 사진이 2025-01-15 에 일괄 교체됐는데 번호는 2022~2024 그대로다.
  사진 날짜를 썼다면 23건이 틀린 날짜를 받았다. 그래서 사진 날짜보다 강하다.
그래도 상품을 **지우고 다시 만들면 새 번호**를 받는다 → `released_at` 이 아니라 `uploaded_at` 에 넣는다.

## 🔴 재등록 — 새 번호를 단 옛 상품. **막는 것 하나, 못 막는 것 하나**

1. **막는다 — NEW 칸 밖의 새 번호.** 2025년에 만든 26건은 **전부 `NEW / HEALTHY`(10) 칸**에 있고 일반 칸에는 하나도 없다
   (2022~2024 번호만). 이 브랜드는 새 상품을 10 칸에 올린다. 그래서 **최근 60일 번호인데 10 칸에 없는 상품은 재등록으로 보고
   날짜를 버린다**(날짜를 잃으면 화면에 안 오른다). 일반 칸 상품을 지웠다 다시 만들어 원래 칸에 넣는 경우가 여기서 걸린다.
2. **못 막는다 — 10 칸으로 돌아오는 시즌 메뉴.** 겨울 메뉴(뱅쇼·샹그리아 스파클링, 2025-11-18)를 봄에 지웠다가 다음 겨울에
   새로 만들어 10 칸에 넣으면 **새 번호 + NEW 칸**이라 진짜 신상과 구별할 축이 사이트에 없다. 지운 옛 레코드가 남지 않으니
   이름 대조도 안 된다(2024 겨울 번호가 하나도 안 남아 있어 이 브랜드가 그렇게 하는지조차 확인 못 했다).
   같은 이름이 옛 번호와 새 번호로 **동시에** 있으면 이른 쪽을 쓴다(지우지 않고 새로 만든 경우만 막힌다 — 실측 겹침 0건).

## 하루 묶음(2025-08-21 19건) — 진짜 라인인지 재등록인지 **사이트 안에서는 못 가른다**

2025-08-21 의 19건은 **프로틴 12 + 시트러스 7**(오렌지 클래식·레몬브라이트·라임 릴렉서 등) 새 라인이고, 14:08~16:02 에 하나씩 올렸다.
105개 전체에서 같은 이름의 옛 번호가 0건이라 재등록 근거는 없다. 하지만 **앞으로 오는 하루 묶음**을 가를 축은 위 1(10 칸 여부)뿐이다 —
10 칸에 한꺼번에 다시 올린 옛 메뉴는 못 가른다. 최근 60일 비율 가드(0.5)는 **절반 넘는 통째 재등록**만 잡는다
(0.3 이면 08-21 같은 정상 라인 출시 19/49 에 터진다). 묶음 크기 중앙값 3 · `BULK_MIN 20` 이라 `untrust_bulk_dates` 도 19건은 안 지운다.

## 오늘(2026-10-14) 화면 — 0건이 정상

가장 최근 등록이 2025-11-18(뱅쇼·샹그리아 스파클링·고구마라떼·달밤라떼·밤구마). 11개월째 새 등록이 없다.
`뱅쇼`·`샹그리아` 는 카페 메뉴(무알콜)이고 `base.is_alcohol` 도 0건이다.
"""
import re
import time
from datetime import date, datetime, timedelta, timezone

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "STACKBEAN"

# 일부러 배선하지 않는다(2026-10-14). 지우지 않고 두는 이유는 사이트가 바뀌면
# 한 줄로 되살릴 수 있어서다 — collect.parked() 가 이 사유를 찍는다.
PARKED = ("신상 신호가 상품 등록 시각(번호)뿐이라 시즌 메뉴를 NEW 칸에 다시 만들면 "
          "옛 메뉴가 통째로 신상으로 뜬다. 겨울 5종을 오늘 번호로 바꿔 시뮬레이션하면 "
          "노출 5건이고, 지운 옛 레코드가 안 남아 이름 대조도 못 한다. 못 막아서 안 붙인다")
SITE = "http://stackbean.co.kr"
LIST = SITE + "/product/list.php?ca_id={}&page={}"
NEW_CA = "10"
# (상위 칸, 2026-10-14 실측 건수). 홈 링크는 하위 탭 하나씩만 가리켜서 상위 칸을 직접 적는다.
CATEGORIES = [("10", 26), ("20", 25), ("30", 39), ("40", 16)]
CAT_MIN_RATIO = 0.7
DELAY = 1.2
MAX_PAGES = 12
MIN_ITEMS = 70          # 실측 대용량 8건 빼고 98건
MAX_ITEMS = 400
DATED_MIN_RATIO = 0.9
FRESH_MAX_RATIO = 0.5   # 2025-08-21 라인 출시 19건 선례 — 0.3 이면 정상 출시에 터진다
WINDOW = 60

_PAGE = re.compile(r"[?&]page=(\d+)")
_ITID = re.compile(r"/data/item/(\d{10})/")
_SIZE_VARIANT = re.compile(r"^(?:1\.1L|MAX)\s")
_KST = timezone(timedelta(hours=9))


def _itid_date(src: str) -> str:
    m = _ITID.search(src or "")
    if not m:
        return ""
    d = datetime.fromtimestamp(int(m.group(1)), _KST).date()
    return d.isoformat() if date(2015, 1, 1) <= d <= date.today() + timedelta(days=1) else ""


def fetch() -> list[Item]:
    found: dict = {}          # key → dict(item, cats)
    per_cat: dict = {}
    with base.client() as c:
        for ca, expect in CATEGORIES:
            last, p, n = 1, 1, 0
            while p <= min(last, MAX_PAGES):
                time.sleep(DELAY)
                r = base.retry(lambda ca=ca, p=p: c.get(LIST.format(ca, p)))
                r.raise_for_status()
                t = HTMLParser(r.text)
                pages = [int(x) for a in t.css("ul.paging a") for x in _PAGE.findall(a.attributes.get("href") or "")]
                last = max([last] + pages)
                for li in t.css("div.sub02_list li"):
                    nm = li.css_first(".txt_wrap p")
                    img = li.css_first("img")
                    name = " ".join(nm.text().split()) if nm else ""
                    src = (img.attributes.get("src") or "") if img else ""
                    if not name:
                        continue
                    n += 1
                    if _SIZE_VARIANT.match(name) or base.is_alcohol(name, "", BRAND):
                        continue
                    it = Item(brand=BRAND, name=name,
                              image=SITE + src if src.startswith("/") else src,
                              uploaded_at=_itid_date(src),
                              url=SITE + f"/product/list.php?ca_id={ca}")
                    cur = found.get(it.key)
                    if cur is None:
                        found[it.key] = dict(item=it, cats={ca})
                        continue
                    cur["cats"].add(ca)
                    # 같은 이름이 옛 번호·새 번호로 동시에 있으면 이른 쪽(안전한 방향)
                    if it.uploaded_at and it.uploaded_at < (cur["item"].uploaded_at or "9"):
                        cur["item"].uploaded_at = it.uploaded_at
                p += 1
            per_cat[ca] = n
            if n < expect * CAT_MIN_RATIO:
                raise RuntimeError(f"{BRAND}: 칸 {ca} {n}건 — 실측 {expect}건. 페이징(`page=`)이나 "
                                   f"'div.sub02_list li' 가 깨졌다. 여기까지: {per_cat}")

    cutoff = (date.today() - timedelta(days=WINDOW)).isoformat()
    items: list[Item] = []
    regs = []
    for v in found.values():
        it = v["item"]
        # 재등록 막기 — 새 상품은 NEW 칸에 올라온다(2025년 26건 전부). 최근 번호인데 NEW 칸에
        # 없으면 옛 상품을 지웠다 다시 만든 것으로 보고 날짜를 버린다(모듈 주석 §재등록 1).
        if it.uploaded_at and it.uploaded_at >= cutoff and NEW_CA not in v["cats"]:
            regs.append(it.name)
            it.uploaded_at = ""
        items.append(it)
    if regs:
        print(f"{BRAND}: NEW 칸 밖의 최근 번호 {len(regs)}건 — 재등록으로 보고 날짜를 버렸다: {regs[:10]}")

    if not MIN_ITEMS <= len(items) <= MAX_ITEMS:
        raise RuntimeError(f"{BRAND}: 상품 {len(items)}건 — 실측 98건. 칸별: {per_cat}")
    dated = sum(1 for i in items if i.uploaded_at)
    if dated < (len(items) - len(regs)) * DATED_MIN_RATIO:
        raise RuntimeError(f"{BRAND}: {len(items)}건 중 등록 시각 {dated}건 — 이미지 경로가 "
                           f"'/data/item/<10자리>/' 꼴이 아니게 됐다")
    fresh = sum(1 for i in items if i.uploaded_at >= cutoff)
    if fresh > len(items) * FRESH_MAX_RATIO:
        raise RuntimeError(f"{BRAND}: {fresh}/{len(items)} 건이 최근 {WINDOW}일 등록 — 상품을 일괄 재등록했는지 보라")
    return items
