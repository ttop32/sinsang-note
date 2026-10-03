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
# 아이스크림·빙수 전수 조사(2026-10-03). 공정위 `아이스크림/빙수`(K1) 가맹점 수
# 순위를 위에서부터 훑었다. 순위표와 불가 사유는 notes/CANDIDATES-ICECREAM-BINGSU.md.
from collectors import dessert_palazzo, dessert_yoajung
# 햄버거·카페 전수 조사 2차(2026-10-02). 공정위 패스트푸드·커피·음료 업종의
# 가맹점 수 순위를 위에서부터 훑어 아직 없던 곳만 붙였다.
# 순위표와 불가 사유는 notes/CANDIDATES-BURGER-CAFE3.md.
# 롯데리아는 1차에서 robots 로 접었던 곳이다 — 운영자 판단으로 무시하되 UA 는
# 위장하지 않고, 주문 플로우가 아니라 브랜드 메뉴 면(/brand/ria)만 읽는다.
from collectors import (burger_burgerunburger, burger_fiveguys,
                        burger_lotteria, burger_nobrand, burger_shakeshack,
                        burger_whattheburger, cafe_blushaak,
                        cafe_cafe051, cafe_caffebene, cafe_eupcheonri,
                        cafe_gongcha, cafe_oozy, cafe_palgongtea,
                        cafe_caffeine, cafe_dalcu, cafe_hasamdong,
                        cafe_juicy, cafe_masscoffee, cafe_pascucci,
                        cafe_projectb, cafe_tenpercent, cafe_tomntoms,
                        toast_ssoja)
# 과자·음료 제조사 2차(2026-10-02). 매출 순위 기준 전수 조사에서 나왔다 —
# 근거와 순위표는 notes/MAKER-SNACK-DRINK.md, 브랜드별 함정은 각 docstring.
from collectors import (maker_binggrae, maker_crown, maker_dongwonfnb,
                        maker_haitai, maker_hitejinrobev, maker_lottewellfood,
                        maker_maeil, maker_pulmuone, maker_sajo, maker_samyang)
# 라면·냉동식품·냉동피자 전수 조사(2026-10-02). 순위표는
# notes/CANDIDATES-RAMEN-FROZEN.md. 농심·CJ 는 1차가 robots 로 접었던 곳이다.
from collectors import (maker_cj, maker_daesang, maker_lavelee,
                        maker_myunsarang, maker_nongshim, maker_shinsegaefood)
# SPC삼립. 같은 라운드에서 파일만 만들어진 채 등록이 빠져 있었다 — 2차가
# `/brand/bakery` 한 경로만 보고 "신제품 신호 없음" 으로 접었는데 보도자료
# JSON API 가 열려 있고 출시 밀도가 이번 조사 1위(120건 중 81건)다.
from collectors import maker_spcsamlip
# 주류. 성인 인증 게이트가 없는 유일한 곳이다(notes/CANDIDATES-ALCOHOL.md).
from collectors import cafe_angelinus, cafe_twosome
from collectors import cafe_baekeok, cafe_dessert39
from collectors import maker_harim
# 카페·디저트·분식 중위권 14곳. 배선 가드가 잡아낸 미등록분.
from collectors import (cafe_bombom,
                        cafe_coffeebay,
                        cafe_hio,
                        cafe_manwolkyung,
                        dessert_bingdongdaeng,
                        dessert_dallondor,
                        dessert_emiliagelato,
                        dessert_taraequeen,
                        snack_33tteok,
                        snack_chickgimbap,
                        snack_gimbapking,
                        snack_morak,
                        snack_terryroze,
                        snack_tteokgoon)
from collectors import alcohol_hitejinro
# 한식 중위권. 공정위 가맹점 수 188~603위 구간(notes/CANDIDATES-KATSU-JPN-KOR.md).
from collectors import (korean_damgguk, korean_obongzip, korean_twozzim,
                        korean_yoogane)
# 치킨 2차. 공정위 가맹점 수 상위에서 신제품 신호가 확인된 곳들
# (근거는 notes/CANDIDATES-CHICKEN2.md).
from collectors import (chicken_60chicken, chicken_barun, chicken_boor,
                        chicken_cheogajip,
                        chicken_chickenplus, chicken_hoocham, chicken_jadam,
                        chicken_gamachi, chicken_kkubeurakko, chicken_mexicana,
                        chicken_hosigi, chicken_nene, chicken_norang,
                        chicken_nuguna,
                        chicken_pelicana, chicken_puradak, chicken_toreore,
                        chicken_ttangttang)
# 더본코리아 외식 브랜드(보도자료 18 + 한신포차)와 KFC(브랜드 신메뉴 면).
from collectors import hanshinpocha, kfc, theborn
# 분식 2차. 공정위 '분식' 업종 가맹점 수 상위에서 신제품 신호가 확인된 곳들.
# 김밥·떡볶이·우동을 따로 떼지 않고 전부 '분식' 한 칸에 넣는다(공정위 업종과 같다).
# salad_* 둘은 같은 조사에서 나온 샐러드 축이다. 근거는 notes/CANDIDATES-SNACK2.md.
from collectors import (salad_pokeallday, salad_slowcali,
                        snack_applefood, snack_gimgane,
                        snack_namuya, snack_samcheop, snack_schoolfood,
                        snack_ssada, snack_yumsem)
# 돈까스·일식·한식·샌드위치 2차. 공정위 가맹점 수 상위를 전수로 훑어 신제품
# 신호가 실재하는 곳만 골랐다. 근거는 notes/CANDIDATES-KATSU-JPN-KOR.md.
# 돈까스는 공정위 업종이 일식·서양식·기타외식·분식으로 흩어져 있어 전부
# '일식' 한 칸에 모았다(사유는 base.BRANDS 주석).
from collectors import (japan_motoishi, japan_tokyogyudong, katsu_baeksojeong,
                        katsu_brown, katsu_ginzaryoko, katsu_haruensoku,
                        katsu_hongik, katsu_misoya, korean_hansot,
                        korean_keunmam, korean_wonandone, sandwich_itsand,
                        sandwich_jimmyjohns, sandwich_quiznos,
                        sandwich_shesbagel, sushi_mikado, sushi_qooqoo,
                        toast_charmtoast)
# 중식. 공정위 `중식` 업종 가맹점 수 전수(99개 브랜드)를 훑어 신제품 신호가
# 실재하는 곳만 골랐다. 근거와 순위표는 notes/CANDIDATES-CHINESE.md.
# ⚠️ 이 업종은 **메뉴판을 긁지 않는다.** 상위권 다수가 마라탕 브랜드인데
#    그쪽 메뉴 페이지는 상품이 아니라 탕에 넣는 재료 목록이다. 그래서
#    대부분 보도자료·공지 게시판에서 날짜와 함께 뽑는다(GS25 와 같은 방식).
#    브랜드당 연 1~4건이라 0건이 '수집 실패'가 아니다.
#    더본코리아 계열(홍콩반점0410·리춘시장·고투웍)은 theborn 담당이라 뺐다.
from collectors import (china_bobae, china_chunli, china_hongjjajang,
                        china_jjambbong10101, china_jjambbonggwan,
                        china_lahongbang, china_mimigwan, china_samsammara,
                        china_sorimmara, china_tanghuo)
import rules
import taxonomy
from web import home

# GS25 는 상품 카탈로그를 긁을 수 없다 — gs25.gsretail.com 은 전 경로가 본사
# 브랜드 페이지로 리다이렉트되는 SPA 껍데기고, 카탈로그는 '우리동네GS' 앱 전용이다.
# 대신 본사 보도자료에서 출시 기사만 추린다. 오뚜기·오리온과 같은 종류의 소스라
# 수집량도 같은 급(연 10건 안팎)이고 편의점 3사와 비교할 물량이 아니다.
ADAPTERS = [mega, starbucks, ediya, cafe_sulbing, cafe_paikdabang,   # 카페
            cafe_coffeebean, cafe_paulbassett, cafe_yogerpresso,
            cafe_mammoth, cafe_theventi, cafe_compose, cafe_hollys,
            cafe_twosome, cafe_angelinus,
            cu, seven, emart24, gs25,                                # 편의점
            burger_momstouch, burger_burgerking, burger_frankburger, # 햄버거
            burger_mcdonalds,
            burger_lotteria, burger_nobrand, burger_whattheburger,   # 햄버거 2차
            burger_shakeshack, burger_fiveguys, burger_burgerunburger,
            cafe_tomntoms, cafe_blushaak, cafe_gongcha, cafe_cafe051,  # 카페 2차
            cafe_oozy, cafe_palgongtea, cafe_pascucci, cafe_tenpercent,
            cafe_caffebene, cafe_eupcheonri, cafe_caffeine,
            cafe_hasamdong, cafe_dalcu, cafe_juicy, cafe_masscoffee,
            cafe_projectb,                     # 프로젝트비 2브랜드(고망고·차얌)
            maker_ottogi, maker_paldo, maker_orion,                  # 제조사(과자·라면)
            lottechilsung, fredit, ourhome,             # 제조사(음료·냉동식품)
            dongsuh, sempio,                            # 제조사(커피·조미료)
            # 과자·음료 제조사 2차. 전부 보도자료형(오리온 계보)이다.
            maker_haitai, maker_crown, maker_lottewellfood,   # 과자
            maker_samyang,                                    # 라면·스낵
            maker_binggrae, maker_maeil, maker_hitejinrobev,  # 음료
            maker_pulmuone, maker_dongwonfnb, maker_sajo,     # 냉동·간편식
            # 라면·냉동식품·냉동피자 전수 조사분. 농심만 신제품 면(배지+이미지
            # epoch)이고 나머지 둘은 보도자료형이다.
            maker_nongshim,                                   # 라면
            maker_cj, maker_shinsegaefood,                    # 냉동·간편식·냉동피자
            maker_myunsarang,                                 # 냉동면·생면·육수
            maker_daesang,                                    # 장류·소스·조미료
            maker_lavelee,                                    # 빙과 전업(아이스크림)
            maker_spcsamlip,                                  # 베이커리(양산빵)
            alcohol_hitejinro,                          # 제조사(주류)
            maker_harim,                                # 제조사(육가공·식재료)
            cafe_baekeok, cafe_dessert39,               # 카페·디저트
            cafe_bombom, cafe_coffeebay, cafe_hio,      # 카페 중위권
            cafe_manwolkyung,
            dessert_bingdongdaeng, dessert_dallondor,   # 디저트·빙수
            dessert_emiliagelato, dessert_taraequeen,
            snack_33tteok, snack_chickgimbap,           # 분식 중위권
            snack_gimbapking, snack_morak,
            snack_terryroze, snack_tteokgoon,
            korean_twozzim, korean_damgguk,             # 한식 중위권
            korean_yoogane, korean_obongzip,
            chicken_bbq, chicken_bhc, chicken_kyochon, chicken_goobne,  # 치킨
            chicken_cheogajip, chicken_puradak, chicken_jadam,
            chicken_toreore, chicken_boor, chicken_ttangttang,
            chicken_pelicana, chicken_barun, chicken_nuguna, chicken_hoocham,
            chicken_kkubeurakko, chicken_chickenplus,
            chicken_mexicana, chicken_hosigi, chicken_60chicken,
            chicken_nene, chicken_gamachi, chicken_norang,
            pizza_pizzahut, pizza_mrpizza, pizza_papajohns, pizza_domino,  # 피자
            dessert_baskinrobbins, cafe_dunkin,                      # 디저트
            # 아이스크림·빙수 전수 조사분(공정위 K1 가맹점 수 상위).
            dessert_yoajung, dessert_palazzo,
            toast_isaac, snack_kimbabcheonguk, snack_barunkim,       # 분식
            snack_jaws, snack_myungrang,
            snack_yumsem, snack_gimgane, snack_schoolfood,  # 분식 2차
            snack_samcheop, snack_namuya, snack_applefood, snack_ssada,
            salad_slowcali, salad_pokeallday,               # 샐러드 2차
            bakery_parisbaguette, bakery_napoleon, bakery_breadnco,  # 베이커리
            bakery_hongruijen, bakery_knotted, bakery_samsong,
            bon_if,                        # 본아이에프 8브랜드(한식·도시락·카페)
            # 더본코리아 18브랜드. 브랜드 메뉴 사이트에는 신제품 신호가 없어서
            # 본사 보도자료만 읽는다(GS25 와 같은 종류의 소스, 사유는
            # collectors/theborn.py docstring §2). 빽다방은 cafe_paikdabang 담당.
            theborn, kfc,
            # 한신포차만 자기 사이트가 상품별 날짜를 준다(RSS pubDate).
            # 그래서 theborn 에서 빼고 따로 둔다 — 겹치면 키가 두 번 담긴다.
            hanshinpocha,
            sushi_sushiro, sandwich_eggdrop, sandwich_subway,        # 일식·샌드위치
            sandwich_quiznos, sandwich_shesbagel, sandwich_itsand,   # 샌드위치 2차
            sandwich_jimmyjohns, toast_charmtoast, toast_ssoja,
            katsu_baeksojeong, katsu_misoya, katsu_ginzaryoko,       # 돈까스(→일식)
            katsu_haruensoku, katsu_hongik, katsu_brown,
            sushi_qooqoo, sushi_mikado,                              # 일식 2차
            japan_motoishi, japan_tokyogyudong,
            korean_hansot, korean_keunmam, korean_wonandone,         # 한식 2차
            # 중식. 보도자료·공지 게시판형 5 + 메뉴 NEW 배지형 1(소림마라).
            # 소림마라는 배지가 2023년에 멈춰 있어 화면에 0건이 정상이다
            # (사유는 collectors/china_sorimmara.py docstring).
            china_tanghuo, china_chunli, china_bobae,
            china_sorimmara, china_lahongbang, china_jjambbonggwan,
            china_hongjjajang, china_mimigwan, china_jjambbong10101,
            china_samsammara,
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


def orphans() -> list:
    """어댑터 파일은 있는데 배선이 빠진 곳. (모듈, 사유) 목록.

    새 브랜드 하나를 붙이려면 **네 곳**을 고쳐야 한다 — 위의 import, 아래
    ADAPTERS, base.BRANDS, base.SITES. 하나만 빠뜨리면 파일이 멀쩡히 있는데
    아무 일도 안 일어나고, 아무도 모른다.

    실제로 한 날에 세 번 났다. SPC삼립은 파일·docstring·검증이 다 돼 있는데
    세 곳 어디에도 없어서 죽은 채로 방치돼 있었고, 한식 4곳(두찜·담꾹·유가네·
    오봉집)과 커피 2곳(투썸플레이스·엔제리너스)은 손으로 찾아 붙였다.

    배선을 자동으로 만들지 않고 찾아내기만 하는 이유는, 어느 어댑터를 켤지는
    사람이 정하는 게 맞아서다(롯데리아·빕스처럼 일부러 끈 것이 있다).
    """
    import importlib
    out = []
    live = {id(m) for m in ADAPTERS}
    for f in sorted((ROOT / "collectors").glob("*.py")):
        name = f.stem
        if name in ("base", "__init__"):
            continue
        try:
            mod = importlib.import_module(f"collectors.{name}")
        except Exception as e:
            out.append((name, f"import 실패 — {type(e).__name__}: {e}"))
            continue
        names = getattr(mod, "BRANDS", None) or (
            [mod.BRAND] if hasattr(mod, "BRAND") else [])
        if not names:
            continue
        for b in names:
            if b not in base.BRANDS:
                out.append((name, f"base.BRANDS 에 '{b}' 없음"))
            elif not base.SITES.get(b):
                out.append((name, f"base.SITES 에 '{b}' 없음"))
        if id(mod) not in live:
            out.append((name, "ADAPTERS 목록에 없음 — 수집이 안 돈다"))
    return out


def main() -> None:
    # 배선이 빠진 어댑터부터 찍는다. 죽어 있는 걸 모르는 게 제일 나쁘다.
    # 죽이지는 않는다 — 작업 중인 파일 하나 때문에 그날 수집 전체가 멎으면
    # 그게 더 큰 손해다. 대신 맨 앞과 맨 뒤 두 번 찍어서 묻히지 않게 한다.
    lost = orphans()
    for name, why in lost:
        print(f"!! collectors/{name}.py — {why}")

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
    # 주소가 있다고 사진이 뜨는 건 아니다. 화면에 올릴 것만 실제로 때려 본다
    # (전수 1,044장 중 7장이 404·끊긴 TLS 체인이었다). 자세한 건 rules 쪽 주석.
    hid, back = rules.verify_images(rules.pick(rows, today, cap=False)
                                    + rules.pick(rows, today, goods=True, cap=False))
    if hid or back:
        print(f"   사진 안 열리는 것 {hid}장 감춤 / 되살아난 것 {back}장")

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
    # 업체가 분류를 새로 만들거나 이름을 바꾸면 그 상품들이 brand_sub 로 조용히
    # 떨어진다. hy프레딧이 통째로 '냉동식품' 이 된 경로가 그거였다. 세어서 찍는다.
    for brand, cat, n in taxonomy.unmapped(rows):
        print(f"   ! {brand} 의 분류 '{cat}' 를 아직 안 옮겼다 ({n}건)")

    # 날짜를 주는 브랜드가 날짜 없이 보낸 신상. 그 길로 들어오면 60일 창이
    # 통째로 열린다 — 농심이 1975년 제품의 복각을 그렇게 올렸다. 자세한 건
    # rules.undated_new 주석.
    for brand, cover, n in rules.undated_new(rows):
        print(f"   ! {brand} 는 날짜를 {cover} 주는데 {n}건을 날짜 없이 "
              "신상으로 보냈다 — 60일 창을 건너뛴다")

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
    if lost:
        print(f"!! 배선이 빠진 어댑터 {len(lost)}건 — 위 '!!' 줄 참고")
    if errors:
        raise SystemExit("어댑터 실패:\n" + "\n".join(errors))



if __name__ == "__main__":
    main()
