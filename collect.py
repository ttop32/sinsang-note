#!/usr/bin/env python3
"""수집 → data/products.json 갱신 → docs/index.html 생성.

신제품 판정은 '어제 없던 키가 오늘 있으면 신규'. 첫 실행은 전부 신규가 아니라,
브랜드가 알려주는 uploaded_at 을 first_seen 으로 쓴다(메가는 이미지 파일명에 들어있음).
"""
import collections
import html
import inspect
import json
import pathlib
import re
from datetime import date, datetime, timedelta, timezone

from collectors import (bakery_parisbaguette, base, bon_if, cafe_yogerpresso,
                        snack_barunkim, snack_jaws, snack_kimbabcheonguk,
                        snack_myungrang)
from collectors import (cafe_compose, cafe_hollys, cafe_mammoth, cafe_theventi,
                        salad_salady, sandwich_eggdrop, sandwich_subway,
                        sushi_sushiro)
from collectors import (burger_burgerking, burger_frankburger, burger_momstouch,
                        cafe_coffeebean, cafe_paulbassett, cafe_yogerpresso,
            cafe_mammoth, cafe_theventi, cafe_compose, cafe_hollys, cafe_dunkin, cafe_paikdabang,
                        cafe_paulbassett,
                        cafe_sulbing, chicken_bbq, chicken_goobne,
                        dessert_baskinrobbins, emart24,
                        chicken_bhc, chicken_kyochon, cu, ediya,
                        mega, pizza_domino, pizza_mrpizza, pizza_papajohns,
                        pizza_pizzahut,
                        seven, starbucks, toast_isaac)

# GS25 는 제외. gs25.gsretail.com/gscvs/* 가 기업 소개 페이지로 301 되고
# 상품 카탈로그는 '우리동네GS' 앱 전용으로 옮겨가 공개 웹 소스가 없다.
ADAPTERS = [mega, starbucks, ediya, cafe_sulbing, cafe_paikdabang,   # 카페
            cafe_coffeebean, cafe_paulbassett, cafe_yogerpresso,
            cafe_mammoth, cafe_theventi, cafe_compose, cafe_hollys,
            cu, seven, emart24,                                      # 편의점
            burger_momstouch, burger_burgerking, burger_frankburger, # 햄버거
            chicken_bbq, chicken_bhc, chicken_kyochon, chicken_goobne,  # 치킨
            pizza_pizzahut, pizza_mrpizza, pizza_papajohns, pizza_domino,  # 피자
            dessert_baskinrobbins, cafe_dunkin,                      # 디저트
            toast_isaac, snack_kimbabcheonguk, snack_barunkim,       # 분식
            snack_jaws, snack_myungrang,
            bakery_parisbaguette,                                    # 베이커리
            bon_if,                        # 본아이에프 8브랜드(한식·도시락·카페)
            sushi_sushiro, sandwich_eggdrop, sandwich_subway,        # 일식·샌드위치
            salad_salady]                                            # 샐러드
# 롯데리아·빕스·GS25 는 뺀다. 사유는 base.BRANDS 주석 참고.

# 전일 대비 이 비율 밑으로 떨어지면 부분수집으로 보고 실패 처리한다.
# 셀렉터가 하나 깨지면 예외가 아니라 '조용한 부분수집'으로 끝나는 게 이 프로젝트의
# 최대 리스크다. 0건 가드만으로는 절반이 날아가도 통과한다.
FLOOR = 0.7

# 브랜드가 신제품이라고 표시해주지 않는 곳은 날짜로 판단한다. 이 기간 안이면 신제품.
WINDOW = 21

# 브랜드가 NEW 배지를 안 내리는 경우가 있다. 이디야는 2017년 상품에, 버거킹은
# 전체의 31%에 배지가 붙어 있다. 배지를 믿되 날짜가 이만큼 지났으면 신제품이
# 아니라고 본다. WINDOW 보다 넉넉한 건 배지를 몇 달 달아두는 게 흔해서다.
STALE = 90

# 브랜드 하나가 화면을 덮지 못하게 하는 상한. CU 는 NEW 배지 유지 기간이 길어
# 666건이 한꺼번에 올라오고, 그러면 이마트24 가 상위 300건을 덮던 문제가 재발한다.
PER_BRAND = 40

# 첫 화면에 그리는 최대 개수. 전량(2,600건+)을 한 장에 그리면 1MB 를 넘어가고
# 브랜드가 늘수록 감당이 안 된다. 이 사이트의 용건은 '신제품'이라 최신순 앞쪽이
# 대부분의 가치를 갖는다. 전량은 data/products.json 에 그대로 남는다.
SHOW = 300

# 브랜드 하나에서 하루에 이만큼 넘게 새로 등장하면 신제품 출시가 아니라
# 우리 쪽이 바뀐 것으로 본다(수집 범위 상향, 파서 개선, 중복 키 규칙 변경).
# 그런 건 기준선으로 넣어 '오늘 신규'를 오염시키지 않는다.
# 실제로 이디야 169건·이마트24 590건이 이 경로였고, 키 규칙을 바꾼 날에는
# 미스터피자 '더블치즈(씬)' 처럼 합쳐져 있던 변형이 갈라져 10건씩 튀었다.
# 한 브랜드가 하루에 8종 넘게 내놓는 일은 실제로는 거의 없다.
SURGE = 8

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data" / "products.json"
OUT = ROOT / "docs" / "index.html"
ROOT_PATH = "/sinsang-note/"
SITE = "신상노트"
TAGLINE = "편의점·카페·프랜차이즈 신제품 모아보기"


def brands_of(mod) -> list:
    """어댑터가 담당하는 브랜드 이름들.

    대부분은 BRAND 하나지만 본아이에프처럼 한 API 로 여러 브랜드를 가져오는
    어댑터는 BRANDS 리스트를 내놓는다. 실패 시 이전분 유지·급감 가드가
    브랜드 단위로 동작해야 해서 여기서 통일한다.
    """
    if hasattr(mod, "BRANDS"):
        return list(mod.BRANDS)
    return [mod.BRAND]


def load_previous() -> dict:
    if not DATA.exists():
        return {}
    # 저장된 key 를 그대로 쓰지 않고 이름에서 다시 계산한다. key 규칙이 바뀌어도
    # 이전 수집분이 그대로 매칭돼 first_seen 이력이 끊기지 않는다.
    out = {}
    for p in json.loads(DATA.read_text(encoding="utf-8"))["products"]:
        k = base.make_key(p["brand"], p["name"])
        p["key"] = k
        out[k] = p
    return out


def main() -> None:
    today = date.today().isoformat()
    prev = load_previous()
    known_brands = {p["brand"] for p in prev.values()}

    products, errors, failed_brands = [], [], []
    for mod in ADAPTERS:
        names = brands_of(mod)
        label = names[0] if len(names) == 1 else f"{mod.__name__.split('.')[-1]}({len(names)}종)"
        try:
            # 이전 수집 결과를 받아 재요청을 줄일 수 있는 어댑터에만 넘긴다(CU 등).
            if "known" in inspect.signature(mod.fetch).parameters:
                items = mod.fetch(known=prev)
            else:
                items = mod.fetch()
            if not items:
                raise RuntimeError("0건 수집 — 파서가 깨졌을 가능성")
            before = sum(1 for p in prev.values() if p["brand"] in names)
            if before and len(items) < before * FLOOR:
                raise RuntimeError(
                    f"수집량 급감 {before} → {len(items)}건 — 부분수집 의심")
            print(f"{label}: {len(items)}건")
            products += items
        except Exception as e:                      # 한 브랜드가 죽어도 나머지는 살린다
            errors.append(f"{label}: {e}")
            failed_brands += names
            print(f"!! {label} 실패: {e}")


    rows = []

    # 실패한 브랜드는 이전 수집분을 그대로 유지한다. 해외 러너에서 국내 사이트가
    # 간헐적으로 DNS 실패하거나 타임아웃 나는데, 그때마다 그 브랜드가 통째로
    # '사라짐' 처리되면 데이터가 깎이고 되돌릴 수 없다.
    carried = [p for p in prev.values() if p["brand"] in failed_brands]
    for c in carried:
        # 이전 수집분은 레지스트리 값이 없을 수 있다(계약이 나중에 늘었다).
        c["brand_type"], c["brand_sub"] = base.kind(c["brand"])
    if carried:
        print(f"   실패 브랜드 이전분 유지: {len(carried)}건")
    rows += carried

    for it in products:
        d = it.to_dict()
        old = prev.get(d["key"])
        if old:
            d["first_seen"] = old.get("first_seen", today)
            d["baseline"] = old.get("baseline", False)
        elif d["brand"] not in known_brands:
            # 브랜드가 막 합류했다. 이건 신제품이 아니라 그 브랜드 메뉴판 전체다.
            # 날짜를 알려주는 브랜드는 소급하고, 나머지는 오늘로 두되 baseline 으로 표시해
            # '오늘 신규' 집계와 화면 배지에서 빼놓는다.
            d["first_seen"] = d.get("uploaded_at") or today
            d["baseline"] = True
        elif d.get("uploaded_at") and d["uploaded_at"] < today:
            # 브랜드가 알려준 등록일이 과거다. 우리가 늦게 발견했을 뿐 신제품이 아니다.
            # (수집기 버그를 고쳐 누락분이 한꺼번에 들어올 때 이 경로를 탄다.)
            d["first_seen"] = d["uploaded_at"]
            d["baseline"] = False
        else:
            d["first_seen"] = today                            # 진짜 신규
            d["baseline"] = False
        rows.append(d)

    # 브랜드별로 오늘 새로 등장한 게 급증이면 수집 범위 변경으로 보고 기준선 처리
    surged = {b for b, n in collections.Counter(
        r["brand"] for r in rows if r["first_seen"] == today and not r["baseline"]
    ).items() if n > SURGE}
    for r in rows:
        if r["brand"] in surged and r["first_seen"] == today and not r["baseline"]:
            r["baseline"] = True
    if surged:
        print(f"   수집범위 변경으로 판단해 기준선 처리: {', '.join(sorted(surged))}")

    rows.sort(key=lambda r: (r["first_seen"], r.get("uploaded_at", "")), reverse=True)
    gone = [k for k in prev if k not in {r["key"] for r in rows}]

    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(
        {"updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "count": len(rows), "products": rows},
        ensure_ascii=False, indent=1), encoding="utf-8")

    fresh = [r for r in rows if is_fresh(r, today)]
    fresh.sort(key=lambda r: (_when(r), r["brand"]), reverse=True)
    fresh = cap_per_brand(drop_sets(merge_variants(fresh)))
    new_today = [r for r in fresh if _when(r) == today]
    print(f"총 {len(rows)}건 / 신제품 {len(fresh)}건 (오늘 {len(new_today)}건) / 사라짐 {len(gone)}건")
    render(fresh, new_today)

    # 개별 페이지·sitemap·아이콘. web.seo 가 collect 를 import 하므로 여기서 늦게 부른다.
    from web import assets, pages, seo
    docs = OUT.parent
    paths = pages.build(fresh, rows, docs)
    seo.build(fresh, paths, docs)
    assets.build(docs)
    print(f"→ 개별 페이지 {len(paths)}장 + sitemap·feed·아이콘")

    # 데이터는 위에서 이미 썼다. 실패한 어댑터가 있으면 여기서 죽어 Actions 가 빨갛게 뜬다.
    # (워크플로의 커밋 스텝은 if: always() 라 부분 결과는 반영된다.)
    if errors:
        raise SystemExit("어댑터 실패:\n" + "\n".join(errors))


# 같은 상품의 단품·세트·라지세트가 따로 올라온다. 버거킹만 12개 그룹 36건이라
# 화면이 같은 버거로 도배된다. 표시할 때만 묶고 데이터는 전부 남긴다.
_VARIANT = re.compile(
    r"\s*[\[(]?\s*(라지\s*세트|L\s*세트|더블\s*PICK\s*세트|세트|콤보|단품)\s*[\])]?\s*$")


def base_name(name: str) -> str:
    """'몬스터 맥시멈3 라지세트' → '몬스터 맥시멈3'. 접미가 겹쳐 붙어도 다 턴다."""
    prev = None
    while prev != name:
        prev = name
        name = _VARIANT.sub("", name).strip()
    return name


def merge_variants(rows: list) -> list:
    """변형을 하나로. 대표는 이름이 가장 짧은 것 — 세트가 아니라 본품이다."""
    rep: dict = {}
    for r in rows:
        k = (r["brand"], base_name(r["name"]))
        if k not in rep or len(r["name"]) < len(rep[k]["name"]):
            rep[k] = r
    keep = {id(v) for v in rep.values()}
    return [r for r in rows if id(r) in keep]


def drop_sets(rows: list) -> list:
    """본품 없는 세트·콤보는 뺀다.

    세트는 두 종류다. '몬스터 맥시멈3 세트'처럼 본품이 따로 있는 변형은
    merge_variants 가 본품으로 묶는다. 여기서 걸리는 건 '싱글피자N버거세트'
    처럼 본품이 없는 조합 상품인데, 이건 신제품이 아니라 구성·할인이다.
    """
    return [r for r in rows if not _SET.search(r["name"])]


_SET = re.compile(r"세트|콤보")

# 카드에 안 보일 행사 라벨
PROMO_LABELS = {"1+1", "2+1", "3+1", "1 + 1", "2 + 1", "3 + 1",
                "할인", "증정", "세일", "특가"}

# 브랜드가 준 NEW 계열 라벨. 우리 NEW 뱃지와 겹쳐 두 번 뜬다.
DUP_LABELS = {"NEW", "New", "new", "신메뉴", "신상품", "신제품"}


def cap_per_brand(rows: list) -> list:
    """브랜드별 상한을 적용한다. 날짜순으로 이미 정렬돼 있어 최근 것부터 남는다."""
    seen = collections.Counter()
    out = []
    for r in rows:
        if seen[r["brand"]] < PER_BRAND:
            seen[r["brand"]] += 1
            out.append(r)
    return out


def _when(r: dict) -> str:
    """이 상품이 '언제 것'인가. 브랜드가 준 날짜를 우선하고 없으면 우리가 처음 본 날."""
    return r.get("released_at") or r.get("uploaded_at") or r.get("first_seen", "")


def is_fresh(r: dict, today: str) -> bool:
    """화면에 올릴 신제품인가.

    사용자 요구는 '그날 새로 올라온 것만'이다. 전체 메뉴판은 필요 없다.
    브랜드가 신제품이라고 말해주면 그걸 믿고, 아니면 날짜가 최근인지 본다.
    아무 근거도 없으면 올리지 않는다 — 카탈로그를 신상인 척 내보내는 게
    이 서비스에서 제일 큰 거짓말이다.
    """
    d0 = date.fromisoformat(today)
    cutoff = (d0 - timedelta(days=WINDOW)).isoformat()
    stamped = r.get("released_at") or r.get("uploaded_at")

    # 신제품 근거가 먼저다. 갓 나온 상품이 도입 행사를 하는 건 당연하고,
    # promo 를 먼저 보면 그런 상품이 통째로 잘린다(CU 신제품 107건).
    # promo 는 '신제품 근거 없이 행사라서 목록에 실린 것'을 거르는 용도다.
    if r.get("is_new") is True:
        # 배지는 믿되 날짜가 있으면 그쪽을 따른다. 배지만 보고 넘기면 화면이
        # "최근 21일"이라고 써놓고 3개월 전 상품을 보여주게 된다(94건이 그랬다).
        if stamped:
            return stamped >= cutoff
        # 날짜가 없으면 기준선인지 본다. 이 검사를 빠뜨려서 합류 첫날 쌓은
        # 메뉴판이 통째로 '오늘 신상'으로 나갔다(300장 중 265장).
        return not r.get("baseline")

    if r.get("promo"):
        return False                      # 행사라서 실린 상품. 신제품 근거가 없다.

    # 어댑터가 promo 를 안 채워도 라벨이 행사면 같은 취급한다. 단 브랜드가
    # 날짜를 준 경우는 '신제품 + 도입행사'일 수 있으니 날짜 판정에 맡긴다.
    if not stamped and any(l in PROMO_LABELS for l in r.get("labels", [])):
        return False

    # 브랜드가 '신제품 아님'이라고 말했으면 이미지 업로드 시각으로 뒤집지 않는다.
    # 사이트 개편 때 이미지를 일괄 재업로드하면 옛 상품이 최근 날짜를 갖는다.
    # 도미노 2026-09-14 업로드분 9건에 2020년부터 팔던 슈퍼디럭스가 들어있다.
    if r.get("is_new") is False:
        rel = r.get("released_at")
        return bool(rel) and rel >= cutoff

    # 브랜드가 준 날짜가 최근이면 신제품이다. 우리가 그 브랜드를 언제 붙였는지와 무관하다.
    # (기준선이라고 빼면 합류 직전에 나온 진짜 신메뉴까지 사라진다.)
    if stamped:
        return stamped >= cutoff

    # 날짜를 안 주는 브랜드는 '어제 없던 게 오늘 있다'로만 판단한다.
    # 합류 시 쌓은 기준선은 그 판단의 출발점이라 신제품이 아니다.
    if r.get("baseline"):
        return False
    return r.get("first_seen", "") >= cutoff


CSS_EXTRA = """
/* 홈 전용. 공통 토큰·카드·그리드는 web/theme.py CSS 가 정의한다. */
.skip{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.skip:focus{position:fixed;left:16px;top:8px;width:auto;height:auto;z-index:9;
background:var(--accent);color:#fff;padding:8px 12px;border-radius:8px;text-decoration:none}

.tools{display:flex;gap:8px;margin-top:14px}
#q{flex:1;min-width:0;font:inherit;font-size:15px;padding:10px 14px;border-radius:999px;
border:1px solid var(--line);background:var(--chip);color:var(--fg);min-height:42px;
-webkit-appearance:none;appearance:none}
#q::placeholder{color:var(--mut)}
#q:focus{outline:none;border-color:var(--accent)}
#sort{flex:none}
.cnt{margin:10px 0 0;font-size:12px;color:var(--mut);min-height:16px}

nav{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);
margin:12px -16px 0;padding:10px 16px;overflow-x:auto;-webkit-overflow-scrolling:touch;
scrollbar-width:none}
nav::-webkit-scrollbar{display:none}
.tw{display:flex;gap:6px;width:max-content}
.t{appearance:none;-webkit-appearance:none;border:1px solid var(--line);background:var(--chip);
color:var(--fg);font:inherit;font-size:14px;line-height:1;padding:0 14px;border-radius:999px;
cursor:pointer;white-space:nowrap;min-height:40px;display:inline-flex;align-items:center;gap:6px}
.t.on{background:var(--accent);border-color:var(--accent);color:#fff}
.t .n{font-size:12px;opacity:.7}
.subnav{margin:0 -16px;padding:8px 16px;overflow-x:auto;scrollbar-width:none;
border-bottom:1px solid var(--line)}
.subnav::-webkit-scrollbar{display:none}
.t.s{min-height:34px;font-size:13px;padding:0 12px;background:transparent}
.t.s.on{background:var(--fg);border-color:var(--fg);color:var(--bg)}

a.c{text-decoration:none;color:inherit;transition:border-color .15s}
a.c:hover,a.c:focus-visible{border-color:var(--accent)}
.c[hidden]{display:none}          /* .c 의 display:flex 가 브라우저 기본 [hidden] 을 덮는다 */
.c img{height:auto}               /* width/height 속성만으론 세로로 늘어난다 */
.go{display:block;padding:0 11px 12px;font-size:11px;color:var(--accent);font-weight:600}
.en{margin:0;font-size:11px;color:var(--mut)}
"""

# 1단 탭. 375px 화면에서는 탭이 몇 개든 4개까지만 보인다(칩 폭 실측). 그래서
# 대분류는 4개로 묶고 세부 분류는 2단에서 고르게 한다.
PRIMARY = [("전체", ""), ("편의점", "편의점"), ("카페", "카페"), ("외식", "외식")]

# 2단(세부). brand_sub 값이다. 프랜차이즈에만 있다.
SUBS = ["햄버거", "피자", "치킨", "베이커리", "디저트", "분식",
        "한식", "도시락", "일식", "샌드위치", "샐러드"]

# web/pages.py 가 유형 페이지(/c/...)를 만들 때 쓰는 목록. 1단+2단을 합친다.
SECTIONS = [("전체", "")] + [(k, k) for k in ["편의점", "카페"] + SUBS]


def primary_of(r: dict) -> str:
    """대분류. 프랜차이즈는 전부 '외식' 으로 묶는다."""
    t = r.get("brand_type", "")
    return "외식" if t == "프랜차이즈" else t


def card(r: dict) -> str:
    e = html.escape
    sub = r.get("brand_sub", "")
    pri = primary_of(r)
    img = (f'<img loading="lazy" decoding="async" width="400" height="400"'
           f' src="{e(r["image"])}" alt="{e(r["brand"])} {e(r["name"])}">'
           if r.get("image") else '<div class="ph" aria-hidden="true"></div>')
    badge = '<span class="lb">NEW</span>' if r.get("is_new") else ""
    # 1+1·2+1 은 뺀다. 편의점은 신상품에 도입 행사를 거의 항상 붙여서(세븐일레븐
    # 신상품 탭 91건 전부) 그대로 두면 신상 목록이 할인 목록처럼 읽힌다.
    # 행사 정보 자체는 data/products.json 과 상세 페이지에 남는다.
    tags = "".join(f'<span class="lb lb2">{e(l)}</span>'
                   for l in r.get("labels", [])
                   if l and l not in PROMO_LABELS and l not in DUP_LABELS)
    # 카드를 누르면 브랜드의 그 상품 페이지로 간다. 우리가 정보를 붙들지 않고
    # 트래픽을 브랜드로 돌려주는 구조여야 한다.
    #
    # 다만 상품 페이지가 아예 없는 브랜드가 있다(메가·빽다방·프랭크버거·이마트24
    # — 카드에 href 가 없고 같은 페이지 모달로 뜬다). 그런 곳을 메뉴판으로
    # 보내면 사용자가 그 제품을 다시 찾아야 한다. 차라리 우리 상세 페이지로
    # 보낸다. 사진·설명·날짜가 다 있고 거기서 브랜드로 한 번 더 나갈 수 있다.
    url, external = r.get("url", ""), True
    if not url or url == base.site(r["brand"]):
        from web import theme
        url, external = ROOT_PATH + theme.product_path(r), False
    # 영문명은 화면 보조이자 검색 대상이다("Latte" 로 검색해도 걸리게)
    en = f'<p class="en">{e(r["name_en"])}</p>' if r.get("name_en") else ""
    inner = (f'{img}<div class="b"><div class="m">{badge}{tags}'
             f'<span class="br">{e(r["brand"])}</span></div>'
             f'<h2>{e(r["name"])}</h2>{en}'
             f'<p class="d">{e(r.get("desc", ""))}</p>'
             f'<time datetime="{e(_when(r))}">{e(_when(r))}</time></div>')
    # 외부(브랜드)로 나갈 때만 새 탭 + nofollow. 우리 상세는 같은 탭.
    attrs = ' target="_blank" rel="noopener nofollow"' if external else ""
    go = "브랜드에서 보기" if external else "자세히 보기"
    return (f'<a class="c" data-p="{e(pri)}" data-s="{e(sub)}" href="{e(url)}"{attrs}>{inner}'
            f'<span class="go">{go} &rarr;</span></a>')


def render(rows: list, new_today: list) -> None:
    shown = rows[:SHOW]                 # 숫자는 실제로 그리는 것만 세야 맞는다
    pcount = collections.Counter(primary_of(r) for r in shown)
    scount = collections.Counter(r.get("brand_sub", "") for r in shown if r.get("brand_sub"))

    tabs = "".join(
        f'<button class="t{" on" if i == 0 else ""}" data-f="{html.escape(key)}"'
        f' aria-pressed="{"true" if i == 0 else "false"}">'
        f'{html.escape(label)}<span class="n">{len(shown) if not key else pcount.get(key, 0)}</span>'
        f'</button>'
        for i, (label, key) in enumerate(PRIMARY)
        if not key or pcount.get(key))
    subs = "".join(
        f'<button class="t s" data-s="{html.escape(k)}" aria-pressed="false">'
        f'{html.escape(k)}<span class="n">{scount[k]}</span></button>'
        for k in SUBS if scount.get(k))

    updated = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    lead = (f"오늘 {len(new_today)}건" if new_today
            else f"최근 {WINDOW}일 신제품 {len(rows)}건")
    from web import theme
    top = next((r for r in rows if r.get("image")), None)
    _head = theme.head(
        f"{SITE} — {TAGLINE}",
        f"{TAGLINE}. 편의점·카페·햄버거·피자·치킨·베이커리 신제품을 매일 자동으로 모읍니다.",
        "/", image=(top or {}).get("image", ""),
        extra=CSS_EXTRA)

    body = "\n".join(card(r) for r in shown) or (
        '<p class="empty">아직 새로 올라온 제품이 없습니다.<br>'
        '매일 아침 다시 확인합니다.</p>')

    doc = f"""<!doctype html><html lang="ko"><head>
{_head}
</head><body><div class="w">
<a class="skip" href="#g">본문으로 건너뛰기</a>
<header><h1>{SITE}</h1><p class="sub">{TAGLINE}</p><p class="lead">{lead}</p></header>
<div class="tools">
  <input id="q" type="search" placeholder="상품·브랜드 검색" aria-label="상품 또는 브랜드 검색"
         autocomplete="off" enterkeyhint="search">
  <button id="sort" class="t" data-s="date" aria-label="정렬 바꾸기">최신순</button>
</div>
<nav aria-label="분류"><div class="tw">{tabs}</div></nav>
<div class="subnav" id="subnav" hidden><div class="tw">{subs}</div></div>
<p id="cnt" class="cnt" role="status" aria-live="polite"></p>
<main class="g" id="g">
{body}
<p class="empty" id="noresult" hidden>찾는 제품이 없습니다.<br>다른 말로 검색해 보세요.</p>
</main>
<footer>마지막 갱신 {updated} · 최근 {WINDOW}일 신제품 {len(rows)}건<br>
상품 정보와 이미지의 저작권은 각 브랜드에 있습니다.</footer>
</div>
<script>
const g = document.getElementById('g'), q = document.getElementById('q'),
      cnt = document.getElementById('cnt'), sortBtn = document.getElementById('sort');
const cards = [...g.querySelectorAll('.c')];
const empty = document.getElementById('noresult');
cards.forEach((c, i) => {{
  c.dataset.i = i;                                    // 원래 순서(최신순)를 기억
  // 카드 안의 UI 문구("브랜드에서 보기")까지 색인되면 그 말로 검색했을 때
  // 전건이 걸린다. 상품명·영문명·브랜드·설명만 넣는다.
  c.dataset.q = [c.querySelector('h2'), c.querySelector('.en'),
                 c.querySelector('.br'), c.querySelector('.d')]
      .filter(Boolean).map(n => n.textContent).join(' ').toLowerCase();
  c.dataset.b = (c.querySelector('.br') || {{}}).textContent || '';
}});
let kind = '', term = '';

function apply() {{
  let n = 0;
  for (const c of cards) {{
    const ok = (!kind || c.dataset.g === kind) && (!term || c.dataset.q.includes(term));
    c.hidden = !ok;
    if (ok) n++;
  }}
  cnt.textContent = (kind || term) ? n + '건' : '';
}}

document.querySelector('nav').addEventListener('click', e => {{
  const b = e.target.closest('.t'); if (!b) return;
  document.querySelectorAll('nav .t').forEach(t => {{
    const on = t === b; t.classList.toggle('on', on); t.setAttribute('aria-pressed', on);
  }});
  kind = b.dataset.f;
  sub = '';                                    // 대분류를 바꾸면 세부는 초기화
  subBtns.forEach(x => {{ x.classList.remove('on'); x.setAttribute('aria-pressed', 'false'); }});
  syncSub(); apply();
}});

subnav.addEventListener('click', e => {{
  const b = e.target.closest('.t.s'); if (!b) return;
  const off = b.classList.contains('on');     // 다시 누르면 해제
  subBtns.forEach(x => {{
    const on = !off && x === b;
    x.classList.toggle('on', on); x.setAttribute('aria-pressed', on);
  }});
  sub = off ? '' : b.dataset.s;
  apply();
}});

syncSub();

let timer;
q.addEventListener('input', () => {{
  clearTimeout(timer);
  timer = setTimeout(() => {{ term = q.value.trim().toLowerCase(); apply(); }}, 150);
}});

sortBtn.addEventListener('click', () => {{
  const byDate = sortBtn.dataset.s === 'date';
  sortBtn.dataset.s = byDate ? 'brand' : 'date';
  sortBtn.textContent = byDate ? '브랜드순' : '최신순';
  const sorted = [...cards].sort((a, b) => byDate
    ? (a.dataset.b.localeCompare(b.dataset.b, 'ko') || a.dataset.i - b.dataset.i)
    : (a.dataset.i - b.dataset.i));
  sorted.forEach(c => g.appendChild(c));
}});
</script>
</body></html>"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc, encoding="utf-8")
    print(f"→ {OUT.relative_to(ROOT)} ({len(doc)//1024}KB)")


if __name__ == "__main__":
    main()
