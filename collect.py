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
from collectors import (bakery_breadnco, bakery_hongruijen, bakery_knotted,
                        bakery_napoleon, bakery_samsong, burger_mcdonalds,
                        maker_orion, maker_ottogi, maker_paldo)
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
from collectors import gs25

# GS25 는 상품 카탈로그를 긁을 수 없다 — gs25.gsretail.com 은 전 경로가 본사
# 브랜드 페이지로 리다이렉트되는 SPA 껍데기고, 카탈로그는 '우리동네GS' 앱 전용이다.
# 대신 본사 보도자료에서 출시 기사만 추린다. 오뚜기·오리온과 같은 종류의 소스라
# 수집량도 같은 급(연 10건 안팎)이고 편의점 3사와 비교할 물량이 아니다.
ADAPTERS = [mega, starbucks, ediya, cafe_sulbing, cafe_paikdabang,   # 카페
            cafe_coffeebean, cafe_paulbassett, cafe_yogerpresso,
            cafe_mammoth, cafe_theventi, cafe_compose, cafe_hollys,
            cu, seven, emart24, gs25,                                # 편의점
            burger_momstouch, burger_burgerking, burger_frankburger, # 햄버거
            burger_mcdonalds,
            maker_ottogi, maker_paldo, maker_orion,                  # 제조사(과자·라면)
            chicken_bbq, chicken_bhc, chicken_kyochon, chicken_goobne,  # 치킨
            pizza_pizzahut, pizza_mrpizza, pizza_papajohns, pizza_domino,  # 피자
            dessert_baskinrobbins, cafe_dunkin,                      # 디저트
            toast_isaac, snack_kimbabcheonguk, snack_barunkim,       # 분식
            snack_jaws, snack_myungrang,
            bakery_parisbaguette, bakery_napoleon, bakery_breadnco,  # 베이커리
            bakery_hongruijen, bakery_knotted, bakery_samsong,
            bon_if,                        # 본아이에프 8브랜드(한식·도시락·카페)
            sushi_sushiro, sandwich_eggdrop, sandwich_subway,        # 일식·샌드위치
            salad_salady]                                            # 샐러드
# 롯데리아·빕스·GS25 는 뺀다. 사유는 base.BRANDS 주석 참고.

# 전일 대비 이 비율 밑으로 떨어지면 부분수집으로 보고 실패 처리한다.
# 셀렉터가 하나 깨지면 예외가 아니라 '조용한 부분수집'으로 끝나는 게 이 프로젝트의
# 최대 리스크다. 0건 가드만으로는 절반이 날아가도 통과한다.
FLOOR = 0.7

# 브랜드가 신제품이라고 표시해주지 않는 곳은 날짜로 판단한다. 이 기간 안이면 신제품.
# 21일은 너무 좁았다(113건). 60일이면 225건이고, 카페·프랜차이즈는 시즌 단위로
# 신메뉴를 내놓아서 두 달치를 보는 게 실제 출시 주기에 맞는다.
WINDOW = 60

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

    fresh = pick(rows, today)
    goods = pick(rows, today, goods=True)      # 굿즈는 버리지 않고 따로 모은다
    # 기준선은 '오늘'에서 뺀다. 브랜드가 합류하거나 수집 범위가 넓어진 날에는
    # 그 브랜드의 신메뉴 목록 전체가 처음 보이는 거라 first_seen 이 오늘이 된다.
    # 목록에는 올리되(브랜드가 신메뉴라고 말하니까) "오늘 N건"으로 세지는 않는다.
    # 세면 어댑터를 붙일 때마다 오늘 신상이 수십 건씩 뛴다.
    new_today = [r for r in fresh if _when(r) == today and not r.get("baseline")]
    print(f"총 {len(rows)}건 / 신제품 {len(fresh)}건 (오늘 {len(new_today)}건)"
          f" / 굿즈 {len(goods)}건 / 사라짐 {len(gone)}건")
    render(fresh, new_today)

    # 개별 페이지·sitemap·아이콘. web.seo 가 collect 를 import 하므로 여기서 늦게 부른다.
    from web import assets, pages, seo
    docs = OUT.parent
    paths = pages.build(fresh, rows, docs, goods=goods)
    seo.build(fresh, paths, docs)
    assets.build(docs)
    print(f"→ 개별 페이지 {len(paths)}장 + sitemap·feed·아이콘")

    # 데이터는 위에서 이미 썼다. 실패한 어댑터가 있으면 여기서 죽어 Actions 가 빨갛게 뜬다.
    # (워크플로의 커밋 스텝은 if: always() 라 부분 결과는 반영된다.)
    if errors:
        raise SystemExit("어댑터 실패:\n" + "\n".join(errors))


def pick(rows: list, today: str, *, goods: bool = False) -> list:
    """화면에 올릴 목록. 고르고·정렬하고·변형을 묶는 순서가 식품과 굿즈 모두 같아야
    한다. 전에는 이 네 줄이 호출부에 펼쳐져 있어서 한쪽만 고치면 어긋났다."""
    out = [r for r in rows if is_fresh(r, today, goods=goods)]
    out.sort(key=lambda r: (_when(r), r["brand"]), reverse=True)
    return cap_per_brand(drop_sets(merge_variants(out)))


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


def is_fresh(r: dict, today: str, *, goods: bool = False) -> bool:
    """화면에 올릴 신제품인가.

    사용자 요구는 '그날 새로 올라온 것만'이다. 전체 메뉴판은 필요 없다.
    브랜드가 신제품이라고 말해주면 그걸 믿고, 아니면 날짜가 최근인지 본다.
    아무 근거도 없으면 올리지 않는다 — 카탈로그를 신상인 척 내보내는 게
    이 서비스에서 제일 큰 거짓말이다.
    """
    # 맨 앞이어야 한다. 아래 is_new 분기가 먼저 return 해버리면 브랜드 신메뉴
    # 페이지에 올라온 굿즈(매머드 키링·볼펜 등)가 그대로 통과한다.
    if r.get("alcohol"):
        return False                      # 술. 연령 확인 없이 내보낼 게 아니다.
    # 굿즈는 버리는 게 아니라 따로 모은다. 신제품 판정 근거(아래)는 식품과 똑같이
    # 적용하고, 어느 쪽 목록에 넣을지만 여기서 가른다.
    if bool(r.get("nonfood")) != goods:
        return False
    d0 = date.fromisoformat(today)
    cutoff = (d0 - timedelta(days=WINDOW)).isoformat()
    stamped = r.get("released_at") or r.get("uploaded_at")

    # 신제품 근거가 먼저다. 갓 나온 상품이 도입 행사를 하는 건 당연하고,
    # promo 를 먼저 보면 그런 상품이 통째로 잘린다(CU 신제품 107건).
    # promo 는 '신제품 근거 없이 행사라서 목록에 실린 것'을 거르는 용도다.
    if r.get("is_new") is True:
        # 배지는 믿되 날짜가 있으면 그쪽을 따른다. 배지만 보고 넘기면 화면이
        # "최근 60일"이라고 써놓고 반년 전 상품을 보여주게 된다.
        if stamped:
            return stamped >= cutoff
        # 날짜가 없으면 배지를 그대로 믿는다. 브랜드가 자기 신메뉴 목록에
        # 올려놓은 것이라 합류 첫날이어도 신제품이 맞다.
        # (기준선이라고 막았더니 빽다방 신메뉴 11건·설빙 NEW 14건이 통째로
        #  사라졌다. 기준선 가드는 아무 근거가 없는 diff 경로에만 쓴다.)
        return True

    if r.get("promo"):
        return False                      # 행사라서 실린 상품. 신제품 근거가 없다.

    # 어댑터가 promo 를 안 채워도 라벨이 행사면 같은 취급한다. 단 브랜드가
    # 날짜를 준 경우는 '신제품 + 도입행사'일 수 있으니 날짜 판정에 맡긴다.
    if not stamped and any(l in base.PROMO_LABELS for l in r.get("labels", [])):
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
/* 푸터의 분류·업체 목록. 업체가 50곳 넘어서 그냥 흘리면 푸터가 화면을 덮는다. */
.fl{margin:10px 0;line-height:2}
.fl b{display:block;font-weight:600;color:var(--fg);margin-bottom:2px}
.fl a{margin-right:2px}
.bn{font-size:10px;color:var(--mut);margin:0 8px 0 2px}

nav{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);
margin:12px -16px 0;padding:10px 16px;overflow-x:auto;-webkit-overflow-scrolling:touch;
scrollbar-width:none}
nav::-webkit-scrollbar{display:none}
.tw{display:flex;gap:6px;width:max-content}
.t{appearance:none;-webkit-appearance:none;border:1px solid var(--line);background:var(--chip);
color:var(--fg);font:inherit;font-size:14px;line-height:1;padding:0 10px;border-radius:999px;
cursor:pointer;white-space:nowrap;min-height:40px;display:inline-flex;align-items:center;gap:6px}
.t.on{background:var(--accent);border-color:var(--accent);color:#fff}
.t .n{font-size:12px;opacity:.7}
/* 2단은 가로로 흐른다. 외식이 7칩 500px 이라 375px 화면에서는 뒤가 잘리는데,
   스크롤 막대를 숨겨놔서 더 있다는 걸 알 수가 없었다. 오른쪽 끝에 그라데이션을
   깔아 "뒤에 더 있다" 를 보여준다. 끝까지 밀면 사라진다(아래 스크립트). */
.subnav{margin:0 -16px;padding:8px 16px;overflow-x:auto;scrollbar-width:none;
border-bottom:1px solid var(--line);position:relative}
.subnav::-webkit-scrollbar{display:none}
.subwrap{position:relative}
.subwrap::after{content:"";position:absolute;right:0;top:0;bottom:1px;width:36px;
pointer-events:none;opacity:0;transition:opacity .15s;
background:linear-gradient(90deg,transparent,var(--bg) 70%)}
.subwrap.more::after{opacity:1}
.t.s{min-height:34px;font-size:13px;padding:0 12px;background:transparent}
.t.s.on{background:var(--fg);border-color:var(--fg);color:var(--bg)}

a.c{text-decoration:none;color:inherit;transition:border-color .15s}
a.c:hover,a.c:focus-visible{border-color:var(--accent)}
.c[hidden]{display:none}
/* .t 가 display:inline-flex 라 브라우저 기본 [hidden]{display:none} 을 이긴다.
   카드(.c)에서 같은 사고가 났을 때 그쪽만 고치고 칩은 놔뒀다 — 그래서 2단
   칩이 지금껏 한 번도 안 숨겨졌고, 카페를 골라도 치킨·피자 칩이 남아 있었다. */
.t[hidden]{display:none}          /* .c 의 display:flex 가 브라우저 기본 [hidden] 을 덮는다 */
.c img{height:auto}               /* width/height 속성만으론 세로로 늘어난다 */
.go{display:block;padding:0 11px 12px;font-size:11px;color:var(--accent);font-weight:600}
.en{margin:0;font-size:11px;color:var(--mut)}
"""

# 1단 탭. 375px 가용폭이 343px 인데 건수 배지를 달면 4탭도 이미 352px 로 넘친다
# (건수가 2자리이던 시절 재놓은 "4개가 상한"이 3자리가 되면서 깨졌다).
# 배지를 떼면 5탭 291px 로 들어가고, 6탭은 344px 라 한 픽셀 차로 안 된다.
# 건수는 칩을 누르면 바로 아래 #cnt 가 말해주고 푸터가 총계를 적는다.
PRIMARY = [("전체", ""), ("편의점", "편의점"), ("카페", "카페"),
           ("외식", "외식"), ("가공식품", "가공식품")]

# 2단(세부). brand_sub 값이다. 화면에는 건수 많은 순으로 깔리고(아래 render),
# 이 순서는 건수가 같을 때만 쓴다. 전에는 선언 순서 그대로 깔려서 2위인
# 일식 40건이 8번째로 밀려 375px 화면 밖에 있었다.
SUBS = ["커피", "베이커리", "아이스크림", "빙수", "도넛",
        "과자", "라면", "햄버거", "피자", "치킨",
        "분식", "한식", "도시락", "일식", "샌드위치", "샐러드"]

# web/pages.py 가 유형 페이지(/c/...)를 만들 때 쓰는 목록. 1단+2단을 합친다.
SECTIONS = ([("전체", "")]
            + [(k, k) for k in ["편의점", "카페", "외식", "가공식품"] + SUBS])


def primary_of(r: dict) -> str:
    """대분류. 프랜차이즈는 전부 '외식' 으로 묶는다."""
    t = r.get("brand_type", "")
    if t == "프랜차이즈":
        return "외식"
    # 과자·라면·음료·냉동식품. 나머지 셋은 "어디서 파나" 축인데 이것만 "무엇인가"
    # 축이다. 신라면 툼바는 편의점에서도 마트에서도 사니 "어디서" 로는 못 넣는다.
    if t == "제조사":
        return "가공식품"
    return t


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
                   for l in base.shown_labels(r.get("labels")))
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
    # 숫자는 화면에 실제로 있는 것만 센다. len(rows) 를 쓰면 SHOW 가 자른 뒤에도
    # 483건이라고 써서, 끝까지 내려도 300장뿐인 화면이 거짓말을 한다.
    shown = rows[:SHOW]
    more = len(rows) - len(shown)
    pcount = collections.Counter(primary_of(r) for r in shown)
    scount = collections.Counter(r.get("brand_sub", "") for r in shown if r.get("brand_sub"))

    tabs = "".join(
        f'<button class="t{" on" if i == 0 else ""}" data-f="{html.escape(key)}"'
        f' aria-pressed="{"true" if i == 0 else "false"}">'
        f'{html.escape(label)}</button>'
        for i, (label, key) in enumerate(PRIMARY)
        if not key or pcount.get(key))
    # 건수 많은 순. 가로로 흐르는 줄이라 화면 안에 드는 건 앞의 네댓 개뿐이고,
    # 선언 순서대로 깔면 제일 볼 게 많은 분류가 화면 밖으로 밀린다.
    subs = "".join(
        f'<button class="t s" data-s="{html.escape(k)}" aria-pressed="false">'
        f'{html.escape(k)}<span class="n">{scount[k]}</span></button>'
        for k in sorted((k for k in SUBS if scount.get(k)),
                        key=lambda k: (-scount[k], SUBS.index(k))))

    updated = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    # 홈에서 /c/ 로 나가는 길이 하나도 없었다. SHOW 가 자른 분량과, 홈 칩에
    # 안 뜨는 분류(화면 300장 안에 한 건도 없는 유형)가 여기서만 닿는다.
    from web import theme as _t
    kinds = [k for _, k in SECTIONS if k and any(
        primary_of(r) == k or r.get("brand_sub") == k or r.get("brand_type") == k
        for r in rows)]
    klinks = " · ".join(
        f'<a href="{ROOT_PATH}{_t.kind_path(k)}">{html.escape(k)}</a>' for k in kinds)
    klinks += f' · <a href="{ROOT_PATH}{_t.kind_path("굿즈")}">굿즈</a>'
    # 업체별로도 찾는다. /b/ 는 만들어만 놓고 사이트 어디서도 링크하지 않아
    # 사이트맵으로만 닿을 수 있었다. 건수 많은 순, 이름순은 동점일 때만.
    bcount = collections.Counter(r["brand"] for r in rows)
    blinks = " · ".join(
        f'<a href="{ROOT_PATH}{_t.brand_path(b)}">{html.escape(b)}</a>'
        f'<span class="bn">{n}</span>'
        for b, n in sorted(bcount.items(), key=lambda kv: (-kv[1], kv[0])))
    count = (f"최근 {WINDOW}일 신제품 {len(rows)}건 — 이 화면에 최신 {len(shown)}장"
             if more else f"최근 {WINDOW}일 신제품 {len(shown)}건")
    lead = (f"오늘 {len(new_today)}건" if new_today
            else f"최근 {WINDOW}일 신제품 {len(shown)}건")
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
<div class="subwrap" id="subwrap" hidden><div class="subnav" id="subnav"><div class="tw">{subs}</div></div></div>
<p id="cnt" class="cnt" role="status" aria-live="polite"></p>
<main class="g" id="g">
{body}
<p class="empty" id="noresult" hidden>찾는 제품이 없습니다.<br>다른 말로 검색해 보세요.</p>
</main>
<footer>마지막 갱신 {updated} · {count}
<div class="fl"><b>분류</b> {klinks}</div>
<div class="fl"><b>업체</b> {blinks}</div>
{theme.NOTICE}</footer>
</div>
<script>
const g = document.getElementById('g'), q = document.getElementById('q'),
      cnt = document.getElementById('cnt'), sortBtn = document.getElementById('sort'),
      subnav = document.getElementById('subnav'),
      subwrap = document.getElementById('subwrap'),
      empty = document.getElementById('noresult');
const cards = [...g.querySelectorAll('.c')];
const priBtns = [...document.querySelectorAll('nav .t')];
const subBtns = [...subnav.querySelectorAll('.t.s')];

cards.forEach((c, i) => {{
  c.dataset.i = i;                                  // 원래 순서(최신순)
  // 카드 안 UI 문구("브랜드에서 보기")까지 색인하면 그 말로 전건이 걸린다.
  c.dataset.q = [c.querySelector('h2'), c.querySelector('.en'),
                 c.querySelector('.br'), c.querySelector('.d')]
      .filter(Boolean).map(n => n.textContent).join(' ').toLowerCase();
  c.dataset.b = (c.querySelector('.br') || {{}}).textContent || '';
}});

let kind = '', sub = '', words = [];

function apply() {{
  let n = 0;
  for (const c of cards) {{
    const ok = (!kind || c.dataset.p === kind)
            && (!sub  || c.dataset.s === sub)
            // 통째로 찾으면 '얼큰 우동'·'바닐라 라떼' 가 0건이 된다. 상품명은
            // 붙여 쓰는데(얼큰우동) 사람은 띄어서 친다. 낱말마다 따로 본다.
            && words.every(w => c.dataset.q.includes(w));
    c.hidden = !ok;
    if (ok) n++;
  }}
  const filtering = kind || sub || words.length;
  cnt.textContent = filtering ? n + '건' : '';
  empty.hidden = n > 0;
  if (!n) showEmpty();
}}

// 0건일 때 무엇 때문인지 말해준다. 전에는 탭 조합 탓인데도 "다른 말로
// 검색해 보세요" 라고 해서 엉뚱한 쪽을 가리켰다.
function showEmpty() {{
  const on = [];
  if (kind) on.push(kind);
  if (sub) on.push(sub);
  if (words.length) on.push('\u2018' + words.join(' ') + '\u2019');
  empty.innerHTML = on.length
    ? on.join(' + ') + ' 에 해당하는 제품이 없습니다.'
      + '<br><button type="button" class="t" id="reset">조건 모두 지우기</button>'
    : '찾는 제품이 없습니다.<br>다른 말로 검색해 보세요.';
}}

function resetAll() {{
  kind = ''; sub = ''; words = []; q.value = '';
  priBtns.forEach((t, i) => {{
    t.classList.toggle('on', i === 0);
    t.setAttribute('aria-pressed', i === 0);
  }});
  subBtns.forEach(x => {{ x.classList.remove('on'); x.setAttribute('aria-pressed', 'false'); }});
  syncSub(); apply();
}}

document.addEventListener('click', e => {{
  if (e.target.id === 'reset') resetAll();
}});

function syncSub() {{
  // 그 대분류에 실제로 있는 세부만 남긴다. 하나도 없으면 2단 줄을 숨긴다.
  let any = false;
  for (const b of subBtns) {{
    const has = cards.some(c => c.dataset.s === b.dataset.s
                             && (!kind || c.dataset.p === kind));
    b.hidden = !has;
    if (has) any = true;
  }}
  subwrap.hidden = !any;
  subnav.scrollLeft = 0;
  hint();
}}

// 2단이 가로로 넘치면 오른쪽에 그라데이션을 켠다. 스크롤 막대를 숨겨놔서
// 더 있다는 걸 알 수가 없었다. 끝까지 밀면 끈다.
function hint() {{
  const left = subnav.scrollWidth - subnav.clientWidth - subnav.scrollLeft;
  subwrap.classList.toggle('more', left > 4);
}}
subnav.addEventListener('scroll', hint, {{passive: true}});
addEventListener('resize', hint);

document.querySelector('nav').addEventListener('click', e => {{
  const b = e.target.closest('.t'); if (!b) return;
  priBtns.forEach(t => {{
    const on = t === b;
    t.classList.toggle('on', on); t.setAttribute('aria-pressed', on);
  }});
  kind = b.dataset.f;
  sub = '';                                         // 대분류를 바꾸면 세부는 초기화
  subBtns.forEach(x => {{ x.classList.remove('on'); x.setAttribute('aria-pressed', 'false'); }});
  syncSub(); apply();
}});

subnav.addEventListener('click', e => {{
  const b = e.target.closest('.t.s'); if (!b) return;
  const off = b.classList.contains('on');           // 다시 누르면 해제
  subBtns.forEach(x => {{
    const on = !off && x === b;
    x.classList.toggle('on', on); x.setAttribute('aria-pressed', on);
  }});
  sub = off ? '' : b.dataset.s;
  apply();
}});

let timer;
q.addEventListener('input', () => {{
  clearTimeout(timer);
  timer = setTimeout(() => {{
    words = q.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    apply();
  }}, 150);
}});

sortBtn.addEventListener('click', () => {{
  const byDate = sortBtn.dataset.s === 'date';
  sortBtn.dataset.s = byDate ? 'brand' : 'date';
  sortBtn.textContent = byDate ? '브랜드순' : '최신순';
  [...cards].sort((a, b) => byDate
    ? (a.dataset.b.localeCompare(b.dataset.b, 'ko') || a.dataset.i - b.dataset.i)
    : (a.dataset.i - b.dataset.i)).forEach(c => g.appendChild(c));
}});

syncSub();
</script>
</body></html>"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc, encoding="utf-8")
    print(f"→ {OUT.relative_to(ROOT)} ({len(doc)//1024}KB)")


if __name__ == "__main__":
    main()
