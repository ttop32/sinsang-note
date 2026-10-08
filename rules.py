"""무엇을 신상으로 볼 것인가. 화면에 올릴지 말지를 정하는 규칙만 모았다.

수집(collect.py)도 쓰고 화면 생성(web/*)도 쓴다. 전에는 collect.py 안에
수집·판정·분류·홈렌더가 같이 있어서 web/pages.py 와 web/seo.py 가 collect 를
거꾸로 import 했고, 순환을 피하려고 함수 안에서 import 하는 자리가 세 군데
있었다. 판정은 아래쪽 모듈이라 아무도 import 하지 않는다 — 여기서 끊는다.

규칙을 두 벌로 두지 마라. 이 레포에서 제일 자주 난 결함이 '같은 규칙이 두
곳에 있고 한 곳만 고침' 이다.
"""
import collections
import re
from datetime import date, timedelta

from collectors import base


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
# 브랜드당 상한. 40 이었을 때 세븐일레븐·팔도·스시로 셋이 300장 중 120장을
# 먹어서 58곳을 수집하는데 화면에는 23곳만 떴다. 12 로 내리면 46곳이 뜨고
# 후보가 329건이라 화면 300장과 거의 같아진다 — 상한이 가리는 양도 줄어든다.
# 팔도 라면 46종·스시로 '이달의 한정메뉴' 46종처럼 한 브랜드가 비슷한 걸
# 수십 개 올리는 경우를 막는 장치지, 그 브랜드를 벌주는 게 아니다.
# 전체는 /b/<브랜드>/ 에서 볼 수 있다.
PER_BRAND = 0

# 첫 화면에 그리는 최대 개수. 전량(2,600건+)을 한 장에 그리면 1MB 를 넘어가고
# 브랜드가 늘수록 감당이 안 된다. 이 사이트의 용건은 '신제품'이라 최신순 앞쪽이
# 대부분의 가치를 갖는다. 전량은 data/products.json 에 그대로 남는다.
# 홈에 그릴 카드 수. 0 이면 제한 없음.
# 전에 300 으로 잘랐는데 "전체 1,237건" 이라고 써놓고 300장만 보여주는 게
# 사용자한테 거짓말로 읽혔다. 다 그린다 — 이미지가 지연 로딩이라 첫 화면
# 비용은 거의 같고, 끝까지 내려본 사람에게 나머지를 숨길 이유가 없다.
SHOW = 0


# 일괄 재발행 판정. 한 브랜드가 같은 날짜에 이만큼 몰아서 올렸으면 그건 출시일이
# 아니라 사이트 개편·재등록 자국이다.
BULK_MIN = 20          # 이보다 적게 몰린 건 그냥 같은 날 나온 것일 수 있다
BULK_RATIO = 10        # 그 브랜드의 평소 묶음 크기의 몇 배를 이상치로 볼 것인가


def undupe_display(rows: list) -> int:
    """다듬은 이름이 같아진 것들은 원본으로 되돌린다. 되돌린 건수를 돌려준다.

    규격을 떼다 보면 서로 다른 상품이 같은 이름이 된다 —
    팔도 '이천햅쌀 비락식혜 1.5L' 과 '이천햅쌀 비락식혜' 가 둘 다
    '이천햅쌀 비락식혜' 가 돼서 카드가 두 장 나란히 떴다. 파리바게뜨
    '버터 크라상 파이 (8개입)' 과 '(낱개)' 도 같다.

    이건 display_name 혼자서는 못 푼다 — 다른 상품을 봐야 알 수 있다.
    겹치면 그 브랜드 안에서 겹친 것들만 원본으로 돌린다. 읽기 좋은 이름보다
    구별되는 이름이 먼저다.
    """
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        d = r.get("display")
        if d:
            per[r["brand"]][d].append(r)
    back = 0
    for brand, groups in per.items():
        for disp, items in groups.items():
            if len(items) < 2:
                continue
            if len({i["name"] for i in items}) < 2:
                continue              # 원본까지 같으면 되돌려도 소용없다
            for i in items:
                i["display"] = i["name"]
                back += 1
    if back:
        print(f"   이름이 겹쳐 원본으로 되돌린 것 {back}건")
    return back


def untrust_bulk_dates(rows: list) -> int:
    """일괄 재발행 날짜를 지운다. 지운 건수를 돌려준다.

    파리바게뜨가 2026-08-26 에 98건, 08-28 에 67건을 같은 날짜로 달고 들어왔다.
    소보루빵·카스테라·단팥빵 같은 상시 품목이고 사이트 개편 때 재발행된 것이다.
    어댑터가 그걸 알고 released_at 대신 uploaded_at 에 넣어 '약하게' 쓰려 했는데,
    is_fresh 는 둘을 같은 자격으로 봐서 방어가 아무 일도 안 했다. 그래서 홈
    1,237장 중 312장(25%)이 파리바게뜨 메뉴판이 됐다.

    평평한 임계값은 못 쓴다 — CU 는 이미지 등록이 주 단위 배치라 한 날짜에
    45~78건이 정상이다. 그 브랜드의 **평소 묶음 크기(중앙값)** 와 비교해야
    이상치가 갈린다. CU 는 중앙값이 12라 120건부터 걸리고, 파리바게뜨는
    중앙값이 2라 20건부터 걸린다.
    """
    import statistics
    per = collections.defaultdict(collections.Counter)
    for r in rows:
        if r.get("uploaded_at"):
            per[r["brand"]][r["uploaded_at"]] += 1
    bad = set()
    for brand, c in per.items():
        sizes = list(c.values())
        if len(sizes) < 3:
            continue                      # 날짜가 몇 개 없으면 이상치를 못 가린다
        med = statistics.median(sizes)
        for dt, n in c.items():
            if n >= BULK_MIN and med and n >= BULK_RATIO * med:
                bad.add((brand, dt))
    gone = 0
    for r in rows:
        if (r["brand"], r.get("uploaded_at")) in bad:
            r["uploaded_at"] = ""
            gone += 1
    if bad:
        top = sorted(bad, key=lambda x: -per[x[0]][x[1]])[:3]
        print(f"   일괄 재발행 날짜 {len(bad)}묶음 {gone}건 무효화: "
              + ", ".join(f"{b} {d}({per[b][d]})" for b, d in top))
    return gone


def pick(rows: list, today: str, *, goods: bool = False,
         cap: bool = True) -> list:
    """신제품 목록. 고르고·정렬하고·변형을 묶는 순서가 식품과 굿즈 모두 같아야
    한다. 전에는 이 네 줄이 호출부에 펼쳐져 있어서 한쪽만 고치면 어긋났다.

    cap 은 브랜드별 상한이다. 홈 한 장에 한 브랜드가 도배되는 걸 막는 장치라
    목록 화면에만 쓴다. 상세·브랜드·유형 페이지는 상한 없이 만든다 — 상한은
    '한 화면에 몇 장을 보여줄까' 의 문제지 그 상품의 페이지가 있으면 안 된다는
    뜻이 아니다. 섞어 쓰면 상한을 내릴 때마다 검색 유입 경로가 같이 사라진다.
    """
    out = [r for r in rows if is_fresh(r, today, goods=goods)]
    out.sort(key=lambda r: (_when(r), r["brand"]), reverse=True)
    out = drop_sets(merge_variants(out), rows)
    return cap_per_brand(out) if cap else out


# 같은 상품의 단품·세트·라지세트가 따로 올라온다. 버거킹만 12개 그룹 36건이라
# 화면이 같은 버거로 도배된다. 표시할 때만 묶고 데이터는 전부 남긴다.
_VARIANT = re.compile(
    r"\s*[\[(]?\s*(라지\s*세트|L\s*세트|더블\s*PICK\s*세트|세트|콤보|단품)\s*[\])]?\s*$")

# 같은 상품을 주문 방식·크기·부위로 쪼개 올리는 것들. 묶을 때만 턴다
# (화면 이름은 display_name 이 따로 만든다).
#   미스터피자 '피치 세트 M(배달)'·'L(배달)'·'M(포장)'·'L(포장)' = 카드 4장
#   맘스터치   '싱글피자N치킨세트 (순살)'·'(뼈)'
_CHANNEL = re.compile(r"\s*[\[(]\s*(배달|포장|매장|홀|테이크아웃|순살|뼈)\s*[\])]\s*$")
_SIZE_TAIL = re.compile(r"\s+(?:[SML]|라지|미디엄|스몰|대|중|소)\s*$")


def base_name(name: str) -> str:
    """'몬스터 맥시멈3 라지세트' → '몬스터 맥시멈3'. 접미가 겹쳐 붙어도 다 턴다."""
    prev = None
    while prev != name:
        prev = name
        name = _CHANNEL.sub("", name).strip()
        name = _VARIANT.sub("", name).strip()
        name = _SIZE_TAIL.sub("", name).strip()
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


def drop_sets(rows: list, universe: list = None) -> list:
    """본품 없는 세트·콤보는 뺀다.

    세트는 두 종류다. '몬스터 맥시멈3 세트'처럼 본품이 따로 있는 변형은
    구성·할인이지 신제품이 아니다. 반면 '학화 호도 먼치킨 세트(5개입)'처럼
    세트 자체가 하나의 상품인 것도 있다.

    전에는 이름에 '세트'·'콤보' 가 들었다는 이유로 전부 뺐다. 그래서 신제품
    24건이 사라졌고 그중 17건은 본품 이름이 데이터 어디에도 없었다. 목록에서만
    빠지는 게 아니라 상세 페이지 자체가 안 생겨 검색으로도 못 닿는다.

    universe 는 본품을 찾을 범위다(보통 수집한 전체). 안 주면 rows 안에서 찾는다.
    """
    if universe is None:
        universe = rows
    # 본품은 '실제로 그 이름으로 존재하는 상품' 이어야 한다. 가공한 이름을
    # 모아두면 세트끼리 서로를 본품으로 쳐서 전부 지워진다.
    # 띄어쓰기·괄호는 브랜드마다 들쭉날쭉이라 지우고 비교한다.
    names = {}
    for r in universe:
        names.setdefault(r["brand"], set()).add(_flat(r["name"]))
    out = []
    for r in rows:
        base = _flat(_set_base(r["name"]))
        # 본품이 실제로 있을 때만 뺀다. 이름에 '세트' 가 들었다는 이유로 전부
        # 빼면 '학화 호도 먼치킨 세트(5개입)'·'러스크 어소트먼트 세트' 처럼
        # 그 자체가 상품인 것까지 사라지고, 상세 페이지도 안 생겨 검색으로도
        # 못 닿는다. 조용히 지워지는 쪽이라 더 나쁘다.
        if _SET.search(r["name"]) and base and base != _flat(r["name"]) \
                and base in names.get(r["brand"], ()):
            continue
        out.append(r)
    return out


_SET = re.compile(r"세트|콤보")

# 이름에서 세트 표기를 떼어 본품 이름 후보를 만든다.
_SET_TAIL = re.compile(
    r"\s*[\[(]?\s*(?:라지\s*)?(?:세트|콤보)\s*[\])]?\s*(?:\(.*\))?\s*$")


def _flat(name: str) -> str:
    """띄어쓰기·괄호를 지운 비교용 이름. '피치 세트 M(배달)' → '피치세트M배달'."""
    return re.sub(r"[\s()\[\]（）]", "", name)


def _set_base(name: str) -> str:
    """'불고기버거 세트' → '불고기버거'. 뗄 게 없으면 원래 이름을 돌려준다."""
    prev = None
    while prev != name:
        prev = name
        name = _SET_TAIL.sub("", name).strip()
    return name

def cap_per_brand(rows: list) -> list:
    """브랜드별 상한. 0 이면 상한 없음.

    한때 40, 그다음 12 였는데 운영자가 풀라고 했다. 상한이 있으면 화면 숫자와
    실제 건수가 갈라지고, 그 차이를 설명하는 문장을 푸터에 계속 덧붙이게 된다.
    다 보여주고 고르는 건 사용자가 한다.
    """
    if not PER_BRAND:
        return rows
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


def shown_date(r: dict) -> str:
    """카드에 찍을 날짜. 모르면 빈 문자열이다.

    기준선(brand 가 막 합류했거나 수집 범위가 넓어진 날 한꺼번에 들어온 것)에
    first_seen 밖에 없으면 그건 '우리가 오늘 처음 봤다' 일 뿐 출시일이 아니다.
    그걸 그대로 찍어서 "오늘 3건" 이라고 써놓고 오늘 날짜 카드가 92장 뜨고 있었다.
    숫자를 맞추는 게 아니라 모르는 날짜를 안 쓰는 쪽이 맞다.
    """
    stamped = r.get("released_at") or r.get("uploaded_at")
    if stamped:
        return stamped
    return "" if r.get("baseline") else r.get("first_seen", "")


def is_fresh(r: dict, today: str, *, goods: bool = False) -> bool:
    """화면에 올릴 신제품인가.

    사용자 요구는 '그날 새로 올라온 것만'이다. 전체 메뉴판은 필요 없다.
    브랜드가 신제품이라고 말해주면 그걸 믿고, 아니면 날짜가 최근인지 본다.
    아무 근거도 없으면 올리지 않는다 — 카탈로그를 신상인 척 내보내는 게
    이 서비스에서 제일 큰 거짓말이다.
    """
    # 맨 앞이어야 한다. 아래 is_new 분기가 먼저 return 해버리면 브랜드 신메뉴
    # 페이지에 올라온 굿즈(매머드 키링·볼펜 등)가 그대로 통과한다.
    # 주류는 한동안 여기서 통째로 뺐다. 국민건강증진법 제8조의2 제1항이
    # 주류 광고의 **주체**를 제조·판매·수입업자로 제한해서, 우리 같은 제3자는
    # 연령 확인을 붙여도 그 제한을 못 피한다는 판단이었다. 운영자가 세 번
    # 요청해서 넣는 쪽으로 뒤집는다 — 판단은 운영자 몫이다.
    # 되돌릴 조건: 업계·당국에서 '제3자 신제품 소식'을 광고로 보는 해석이
    # 나오거나, 브랜드 쪽에서 내려달라는 요청이 오면 이 줄을 되살린다.
    #     if r.get("alcohol"): return False
    # 굿즈는 버리는 게 아니라 따로 모은다. 신제품 판정 근거(아래)는 식품과 똑같이
    # 적용하고, 어느 쪽 목록에 넣을지만 여기서 가른다.
    if bool(r.get("nonfood")) != goods:
        return False
    # 다만 '굿즈' 는 카페·외식 브랜드가 내는 기념품이다 — 텀블러·키링·인형·볼펜.
    # 편의점·제조사가 파는 전동칫솔·세제·스타킹·콘돔·핫팩은 먹는 게 아닌 건
    # 맞지만 굿즈가 아니다. 그걸 '굿즈' 라고 불러놓으면 화면이 이상해진다.
    # 분류 이름이 내용을 설명하지 못하면 그건 분류가 아니다. 그래서 그쪽은
    # 굿즈 목록에도 안 올린다 — 신상노트는 먹는 것과 그 브랜드 굿즈를 모은다.
    if goods and r.get("brand_type") not in ("카페", "프랜차이즈"):
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
        # 날짜도 없고 붙은 라벨이 행사뿐이면 배지를 믿지 않는다. 세븐일레븐의
        # '신상품' 탭에 해태 연양갱·스니커즈·트윅스가 2+1 을 달고 올라온다 —
        # 수십 년 된 제품이다. 그 탭은 신상품이 아니라 행사 매대에 가깝다.
        # 사용자가 처음 지적한 게 정확히 이거였다("신상이 아니라 2+1 행사 상품").
        if any(l in base.PROMO_LABELS for l in r.get("labels", [])):
            return False
        # 그 외에는 배지를 믿는다. 브랜드가 자기 신메뉴 목록에 올려놓은
        # 것이라 합류 첫날이어도 신제품이 맞다.
        # (기준선이라고 막았더니 빽다방 신메뉴 11건·설빙 NEW 14건이 통째로
        #  사라졌다. 기준선 가드는 아무 근거가 없는 diff 경로에만 쓴다.)
        #
        # 다만 영원히는 아니다. 날짜가 없으면 브랜드가 배지를 내릴 때까지
        # 계속 신상으로 남는데, 설빙 '인절미설빙'(2013년 간판)처럼 몇 년째
        # 배지가 달린 것도 있다. 우리가 처음 본 지 STALE 일이 지났으면 그만
        # 내린다. STALE 은 여태 정의만 돼 있고 아무 데서도 안 읽혔다.
        seen = r.get("first_seen", "")
        return not seen or seen >= (d0 - timedelta(days=STALE)).isoformat()

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


# ── 죽은 사진 걸러내기 ────────────────────────────────────────────────
# 주소가 있다고 사진이 뜨는 건 아니다. 2026-10-02 전수 실측에서 1,044장 중
# 7장이 깨져 있었다 — 홍루이젠 4장은 CDN 이 404(본문은 HTML 70바이트)를
# 돌려주고, 롯데칠성 3장은 서버가 중간 인증서를 안 보내 TLS 체인이 끊긴다.
# 둘 다 브라우저에서도 똑같이 안 열린다.
#
# derive() 가 http:// 를 지우는 것과 같은 취지다 — 빈 네모가 뜨느니 사진 없는
# 카드로 그린다. 다만 여기선 주소를 버리지 않고 image_src 에 넣어 둔다.
# 그래야 서버가 고쳐졌을 때 다음 실행에서 되살아난다(한 번 빈 칸이 되면
# 영영 못 돌아오는 게 더 나쁘다).
IMG_WORKERS = 12      # 동시 요청 수. 1,035장에 30초쯤 걸린다.
IMG_TIMEOUT = 20
IMG_MIN = 500         # 이보다 작으면 사진이 아니라 에러 페이지다

# 우리가 받아 둔 미러를 알아보는 표식(아래 MIRROR_DIR 와 짝이다).
MIRROR_MARK = "/i/"

# ⚠️ 브라우저가 보내는 것을 똑같이 보내야 한다. 그냥 받으면 200 인데 우리
# 도메인에서 부르면 막는 곳이 있다 — 가마치통닭이 Referer 를 붙이자 403 이
# 됐다(핫링크 차단). 레퍼러 없이 재고 "멀쩡하다" 고 하면 화면에선 깨진다.
IMG_HEADERS = {"Referer": "https://ttop32.github.io/",
               "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"}

# Content-Type 으로 판정하면 안 된다. 탐앤탐스·커피베이는 **진짜 PNG 를
# application/octet-stream 으로** 보낸다 — 타입만 보면 멀쩡한 사진 400여 장을
# 숨긴다. 브라우저는 내용을 보고 그린다. 우리도 앞 몇 바이트를 본다.
_MAGIC = ((b"\x89PNG", "png"), (b"\xff\xd8", "jpeg"), (b"GIF8", "gif"),
          (b"BM", "bmp"), (b"\x00\x00\x01\x00", "ico"))

# ⚠️ AVIF 를 빠뜨렸다가 멀쩡한 사진을 떨어뜨렸다. 빙동댕(Wix CDN)이 우리가
# 보내는 `Accept: image/avif` 를 보고 avif 로 내려준다 — 즉 **우리가 요청한
# 형식인데 우리가 모른다고 버린 것**이다. 최신 형식은 앞으로도 늘어난다.
_BMFF = {b"avif", b"avis", b"heic", b"heix", b"hevc", b"mif1", b"msf1"}


def _is_image(blob: bytes) -> bool:
    if any(blob.startswith(m) for m, _ in _MAGIC):
        return True
    # 컨테이너 꼴 둘. RIFF/WEBP 와 ISO BMFF(avif·heic). 앞 네 바이트는 상자
    # 길이라 종류는 4~12 바이트에 있다.
    if blob[:4] == b"RIFF" and blob[8:12] == b"WEBP":
        return True
    if blob[4:8] == b"ftyp" and blob[8:12] in _BMFF:
        return True
    head = blob[:400].lstrip()
    return head.startswith(b"<svg") or b"<svg" in head[:200]


def verify_images(rows: list) -> tuple:
    """화면에 올릴 사진이 실제로 열리는지 확인한다. (고친 수, 되살린 수).

    브라우저와 같은 조건으로 본다 — 인증서 검증을 켜고, 통째로 받아서
    Content-Type 과 크기를 확인한다. 404 를 200 처럼 흘려보내는 CDN 이 있어서
    상태코드만 보면 안 되고, HTML 에러 페이지를 사진으로 세면 안 된다.
    """
    import concurrent.futures as cf

    import httpx

    # 🔴 우리가 받아 둔 미러는 확인하지 않는다. 아직 푸시 전이라 그 주소는
    # 404 다 — 확인하면 **방금 받은 걸 스스로 지운다.** 실제로 그 순서로
    # 돌렸더니 미러 12장이 전부 감춰졌다. 디스크에 파일이 있는지로 족하다.
    todo = {}
    for r in rows:
        url = r.get("image") or r.get("image_src") or ""
        if url and MIRROR_MARK not in url:
            todo.setdefault(url, []).append(r)
    if not todo:
        return 0, 0

    def live(url: str) -> bool:
        try:
            with httpx.Client(timeout=IMG_TIMEOUT, follow_redirects=True,
                              headers={"User-Agent": base.UA, **IMG_HEADERS}) as c:
                resp = c.get(url)
                return (resp.status_code < 400 and len(resp.content) >= IMG_MIN
                        and _is_image(resp.content))
        except Exception:
            return False

    with cf.ThreadPoolExecutor(IMG_WORKERS) as ex:
        ok = dict(zip(todo, ex.map(live, todo)))

    hid = back = 0
    for url, group in todo.items():
        # 🔴 http 는 살아 있어도 되살리지 않는다. 브라우저가 혼합 콘텐츠로
        # 막으니 화면에선 어차피 안 보이고, 되살려 놓으면 `image` 가 차서
        # **미러가 할 일이 없어진다**(실제로 그 순서로 미러가 0장이 됐다).
        # http 는 mirror_images 담당이다 — 받아서 우리 쪽에 두는 게 답이다.
        live_https = ok[url] and not url.startswith("http://")
        for r in group:
            if live_https:
                if not r.get("image"):
                    r["image"], back = url, back + 1
                r.pop("image_src", None)
            elif ok[url]:
                # 살아 있는 http. image 는 비워 두고 주소만 남긴다.
                r["image_src"], r["image"] = url, ""
            elif r.get("image"):
                r["image_src"], r["image"] = url, ""
                hid += 1
    return hid, back


# ── 날짜 없이 신상으로 들어온 것 ────────────────────────────────────
# `is_new=True` 인데 released_at·uploaded_at 이 둘 다 비면 is_fresh 가 60일
# 창을 건너뛴다. 날짜를 안 주는 브랜드(팔도·커피빈·컴포즈·빽다방 — 전부 0%)
# 한테는 그게 설계대로다. 그 브랜드들은 first_seen 과 baseline 으로 가린다.
#
# 문제는 **평소엔 날짜를 주는 브랜드가 한 건만 비워 보낼 때**다. 그러면 창이
# 통째로 열린다. 실제로 농심 `농심라면큰사발면`(1975년 제품의 2025-01 복각)이
# 그 길로 화면에 올라와 있었다. 날짜를 비우는 게 안전한 쪽이 아니라 **창을
# 우회하는 길**이었던 것이다.
#
# 지우지는 않는다. 지금 걸리는 건 CU 행사 132건뿐이고 그건 이미 행사 규칙이
# 막고 있다 — 여기서 또 지우면 효과는 0인데 '조용히 사라지는' 위험만 는다.
# 그건 이 레포에서 두 번째로 자주 난 사고다. 찾아서 찍기만 한다.
DATED_BRAND = 0.7     # 이 비율 넘게 날짜를 주면 '날짜를 주는 브랜드'로 본다
DATED_MIN = 10        # 그 판단을 할 최소 표본


def undated_new(rows: list) -> list:
    """날짜를 주는 브랜드가 날짜 없이 보낸 is_new. (브랜드, 보유율, 건수) 목록."""
    cover = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        c = cover[r.get("brand", "")]
        c[0] += 1
        if r.get("released_at") or r.get("uploaded_at"):
            c[1] += 1
    hit = collections.Counter()
    for r in rows:
        total, dated = cover[r.get("brand", "")]
        if (r.get("is_new") and not (r.get("released_at") or r.get("uploaded_at"))
                and total >= DATED_MIN and dated / total >= DATED_BRAND):
            hit[(r["brand"], f"{dated}/{total}")] += 1
    return [(b, cov, n) for (b, cov), n in hit.most_common()]


# ── 합류 첫날 배지 하나로만 올라온 것 ──────────────────────────────
# `is_fresh` 는 `is_new is True` 를 맨 위에서 받아서 **baseline 검사를
# 건너뛴다.** 브랜드가 붙인 배지를 믿는다는 뜻인데, 그 배지가 '이번 달 신상'
# 이 아니라 **1년치가 쌓인 바구니**면 합류 첫날 그게 통째로 올라온다.
#
# 하이오커피가 그랬다. '신메뉴' 전용 카테고리 40건이 다른 탭과 하나도 안
# 겹쳐서 믿을 만해 보였는데, 10월에 쌍화차·유자생강차(겨울)와 컵빙수·
# 수박주스(여름)가 같이 들어 있었다. 날짜가 없어 60일 창도 못 쓰고,
# STALE 은 first_seen 기준이라 합류 후 90일간 안 걸린다.
#
# 자동으로 지우지 않는다 — 같은 모양인 컴포즈 16건·설빙 4건은 눈으로 확인한
# 진짜 신상이다. 기계가 가를 수 없으니 **사람이 보게 찍기만** 한다.
# `baseline` 은 합류 첫날 묶음에만 붙으니 이 경고는 새로 들어온 브랜드에만
# 뜬다. 즉 "새 브랜드를 붙였으면 이 목록을 한 번 보라" 는 뜻이다.
BADGE_ONLY_MIN = 10   # 이보다 많으면 눈으로 볼 값어치가 있다


def badge_only(rows: list) -> list:
    """합류 첫날 배지만으로 올라온 카드. (브랜드, 건수) 목록, 많은 순."""
    hit = collections.Counter(
        r["brand"] for r in rows
        if r.get("is_new") and r.get("baseline")
        and not (r.get("released_at") or r.get("uploaded_at")))
    return [(b, n) for b, n in hit.most_common() if n >= BADGE_ONLY_MIN]


# ── 브라우저가 못 받는 사진을 우리 쪽에 둔다 ──────────────────────
# 우리 페이지는 https 인데 사진이 http 뿐인 브랜드가 있다. 혼합 콘텐츠라
# 브라우저가 막고, 그 호스트들은 https 를 아예 안 연다(ConnectError) —
# 주소만 바꿔선 안 된다. 에그드랍·퀴즈노스·쉐이크쉑·스쿨푸드가 그렇다.
#
# 그래서 빌드할 때 받아서 docs/i/ 에 둔다. 정적 호스팅이라 프록시를 돌릴 수
# 없고, 남의 프록시(images.weserv.nl 같은 것)에 태우면 우리 트래픽이 그쪽을
# 지나간다. 받아 두는 쪽이 단순하고 우리가 통제한다.
#
# **화면에 올라간 것만** 받는다. 전량을 받으면 레포가 매일 불어난다.
# 안 쓰는 파일은 매번 지운다 — 60일 창 밖으로 나간 상품의 사진은 필요 없다.
# 400px WebP 로 줄인다. 카드가 400×400 으로 그린다.
MIRROR_DIR = "i"
MIRROR_PX = 400
MIRROR_Q = 72


def mirror_images(rows: list, docs, base_url: str) -> tuple:
    """http 로만 열리는 사진을 받아 docs/i/ 에 둔다. (받은 수, 지운 수).

    `image` 가 비고 `image_src` 가 http 인 행만 본다. 성공하면 `image` 에
    우리 주소를 넣는다 — 그 뒤로는 평범한 사진과 똑같이 다뤄진다.

    ⚠️ 상대 경로를 쓰면 안 된다. 홈은 docs/ 에 있지만 상세는 docs/p/<...>/
    라 한 칸 아래다. og:image 는 아예 절대 주소라야 크롤러가 읽는다.
    그래서 base_url 을 받아 **전체 주소**로 적는다(https 라 derive 도 안 지운다).
    base_url 은 collect 가 web.theme.BASE_URL 을 넘긴다 — rules 가 web 을
    import 하면 지금 한 방향으로 정리해 둔 의존이 다시 엉킨다.
    """
    import hashlib
    import io
    import concurrent.futures as cf

    import httpx
    from PIL import Image

    out = docs / MIRROR_DIR
    out.mkdir(parents=True, exist_ok=True)
    todo = {}
    for r in rows:
        src = r.get("image_src") or ""
        if not r.get("image") and src.startswith("http://"):
            todo.setdefault(src, []).append(r)

    def grab(url: str):
        name = hashlib.sha1(url.encode()).hexdigest()[:16] + ".webp"
        dest = out / name
        if dest.exists():
            return url, name
        try:
            with httpx.Client(timeout=IMG_TIMEOUT, follow_redirects=True,
                              headers={"User-Agent": base.UA, **IMG_HEADERS}) as c:
                blob = c.get(url).content
            if len(blob) < IMG_MIN or not _is_image(blob):
                return url, ""
            im = Image.open(io.BytesIO(blob))
            im = im.convert("RGB") if im.mode not in ("RGB", "L") else im
            im.thumbnail((MIRROR_PX, MIRROR_PX))
            im.save(dest, "WEBP", quality=MIRROR_Q, method=4)
        except Exception:
            return url, ""
        return url, name

    got = {}
    if todo:
        with cf.ThreadPoolExecutor(IMG_WORKERS) as ex:
            got = dict(ex.map(grab, todo))

    used, n = set(), 0
    for url, group in todo.items():
        if not got.get(url):
            continue
        used.add(got[url])
        for r in group:
            r["image"] = f"{base_url.rstrip('/')}/{MIRROR_DIR}/{got[url]}"
            n += 1

    # 안 쓰는 파일은 지운다. 안 그러면 레포가 매일 불어난다.
    #
    # 🔴 그런데 **받기에 실패한 날 전부 지우면 안 된다.** 2026-10-03 에 넣은
    # 26장이 다음 날 수집(10-04)에서 통째로 사라졌다. 러너가 해외 IP 라 그
    # http 호스트들에 못 닿았고, `used` 가 비니까 기존 파일이 전부 "안 쓰는
    # 것" 으로 보여 지워진 것이다. **네트워크 실패가 영구 삭제로 이어졌다.**
    #
    # 받을 게 있었는데 **하나도 못 받았으면 그날은 안 지운다.** 사진이 잠깐
    # 안 보이는 것과 영영 사라지는 것은 다르다 — 이 레포에서 두 번째로 자주
    # 난 사고가 '조용히 사라지는 것' 이다.
    gone = 0
    if todo and not used:
        print(f"   ! 사진 {len(todo)}장을 하나도 못 받았다 — 기존 미러를 "
              "지우지 않는다(네트워크 문제일 때 영구 삭제를 막는다)")
        return n, 0
    for f in out.glob("*.webp"):
        if f.name not in used:
            f.unlink()
            gone += 1
    return n, gone
