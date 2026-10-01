#!/usr/bin/env python3
"""수집 → data/products.json 갱신 → docs/index.html 생성.

신제품 판정은 '어제 없던 키가 오늘 있으면 신규'. 첫 실행은 전부 신규가 아니라,
브랜드가 알려주는 uploaded_at 을 first_seen 으로 쓴다(메가는 이미지 파일명에 들어있음).
"""
import collections
import inspect
import json
import pathlib
from datetime import date, datetime, timezone

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
from collectors import dongsuh, fredit, gs25, lottechilsung, ourhome, sempio
import rules
from web import home

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
            lottechilsung, fredit, ourhome,             # 제조사(음료·냉동식품)
            dongsuh, sempio,                            # 제조사(커피·조미료)
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
# 급감 가드를 켜는 최소 규모. 메뉴가 서너 개뿐인 브랜드는 하나만 빠져도 30% 가
# 줄어서 매번 가드에 걸린다 — 배스킨라빈스가 3 → 2건으로 걸렸고 어댑터는
# 멀쩡했다. 비율 가드는 숫자가 어느 정도 있어야 뜻이 있다.
FLOOR_MIN = 10

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
            if before >= FLOOR_MIN and len(items) < before * FLOOR:
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
        # 이전 수집분은 to_dict() 를 안 거쳐서 파생값이 낡았거나 아예 없다.
        # 단어 목록을 고쳐도 하필 그날 수집이 실패한 브랜드만 옛 판정을 들고
        # 있게 되고, 필드가 없으면 거짓으로 읽혀 샴푸가 식품 목록에 섞인다.
        # 실제로 385행이 그 상태였다. 수집이 실패한 날에만 터지는데 그날은
        # 아무도 화면을 안 본다.
        #
        # 계산을 여기 베껴 적지 마라. 전에 그렇게 했다가 image 정규화 하나를
        # 빠뜨려서, 같은 종류의 버그를 고치는 커밋 안에서 같은 버그를 다시 냈다.
        base.derive(c, stored=True)   # 어댑터 뜻이 아니라 옛 판정이다
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

    rules.untrust_bulk_dates(rows)                   # 사이트 개편 재발행분을 날짜에서 뺀다
    rules.undupe_display(rows)                       # 다듬다 같아진 이름은 원본으로
    fresh = rules.pick(rows, today)                  # 홈 목록(브랜드 상한 적용)
    # 페이지는 상한 없이 만든다. 상한에 걸린 것도 /b/<브랜드>/ 와 검색으로 닿아야 한다.
    listed = rules.pick(rows, today, cap=False)
    listed_goods = rules.pick(rows, today, goods=True, cap=False)
    # 세는 기준과 카드에 찍는 날짜가 같아야 한다. 전에는 카운터만 기준선을 빼서
    # "오늘 3건" 이라고 써놓고 오늘 날짜 카드가 92장 떴다.
    # rules.shown_date 는 브랜드가 준 날짜를 그대로 쓰고, 날짜가 없는 기준선 상품만
    # 비운다 — 기준선이 막아야 할 건 '우리가 처음 본 날'이라는 추측이지
    # 브랜드가 직접 찍어준 날짜가 아니다.
    new_today = [r for r in fresh if rules.shown_date(r) == today]
    shown = min(len(fresh), rules.SHOW) if rules.SHOW else len(fresh)
    print(f"총 {len(rows)}건 / 신제품 {len(listed)}건 (홈 {shown}장,"
          f" 오늘 {len(new_today)}건) / 굿즈 {len(listed_goods)}건 / 사라짐 {len(gone)}건")
    home.render(fresh, new_today, total=len(listed))

    # 개별 페이지·sitemap·아이콘. web.seo 가 collect 를 import 하므로 여기서 늦게 부른다.
    from web import assets, pages, seo
    docs = OUT.parent
    paths = pages.build(listed, rows, docs, goods=listed_goods)
    seo.build(fresh, paths, docs)
    assets.build(docs)
    print(f"→ 개별 페이지 {len(paths)}장 + sitemap·feed·아이콘")

    # 데이터는 위에서 이미 썼다. 실패한 어댑터가 있으면 여기서 죽어 Actions 가 빨갛게 뜬다.
    # (워크플로의 커밋 스텝은 if: always() 라 부분 결과는 반영된다.)
    if errors:
        raise SystemExit("어댑터 실패:\n" + "\n".join(errors))



if __name__ == "__main__":
    main()
