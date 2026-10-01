from dataclasses import dataclass, asdict, field
import re
import time

import httpx

# 공개 봇이니 신원을 밝힌다. 브라우저를 위장하면 사이트 운영자가 우리를 식별하거나
# 연락하거나 선별 차단할 방법이 없다. robots.txt 의 UA별 규칙에도 매칭되지 않는다.
UA = "sinsang-note/1.0 (+https://github.com/ttop32/sinsang-note)"


# 괄호 안이 '같은 상품의 사이즈·온도 표기'일 때만 턴다.
# 예전엔 괄호를 통째로 지웠는데 그러면 맛·종류 변형까지 합쳐져 상품이 사라졌다.
# 미스터피자 '더블치즈(씬)' 9건이 클래식에 흡수됐고, bhc 크리스피번 3종과
# 파파존스 파스타 3종도 각각 1건이 됐다.
_SIZE = re.compile(
    r"^(L|M|S|XL|EX|대|중|소|Mini|Regular|Large|HOT|ICE|ICED|아이스|핫|"
    r"\d+\s*(ml|mL|L|g|G|kg|인분|개입|P|입))$", re.I)


def make_key(brand: str, name: str) -> str:
    """중복 판정 키. 사이즈·온도 표기만 털고 나머지 괄호 내용은 남긴다."""
    def drop(m):
        inner = m.group(1).strip()
        return "" if _SIZE.match(inner) else m.group(0)
    n = re.sub(r"\(([^)]*)\)", drop, name)
    n = re.sub(r"\s+", "", n)
    return f"{brand}:{n}"


# 브랜드 유형. 화면에서 이 축으로 나눠 보여준다.
CVS = "편의점"
CAFE = "카페"
FRANCHISE = "프랜차이즈"
MAKER = "제조사"     # 편의점에 상품을 넣는 식품 제조사. 보도자료가 출시일을 준다

# 브랜드 → (유형, 세부분류). 어댑터가 각자 선언하면 표기가 어긋나므로 여기 한 곳에 둔다.
# 세부분류는 프랜차이즈에서만 쓴다(햄버거/피자/치킨).
BRANDS = {
    "메가MGC커피": (CAFE, ""),
    "스타벅스":    (CAFE, ""),
    "이디야커피":  (CAFE, ""),
    "설빙":        (CAFE, ""),
    "빽다방":      (CAFE, ""),
    "커피빈":      (CAFE, ""),
    "폴바셋":      (CAFE, ""),
    "CU":         (CVS, ""),
    "세븐일레븐":  (CVS, ""),
    "이마트24":    (CVS, ""),
    "맘스터치":    (FRANCHISE, "햄버거"),
    "버거킹":      (FRANCHISE, "햄버거"),
    "BBQ":        (FRANCHISE, "치킨"),
    "bhc치킨":     (FRANCHISE, "치킨"),
    "교촌치킨":    (FRANCHISE, "치킨"),
    "피자헛":      (FRANCHISE, "피자"),
    "미스터피자":  (FRANCHISE, "피자"),
    "파파존스":    (FRANCHISE, "피자"),
    "도미노피자":  (FRANCHISE, "피자"),
    "굽네치킨":    (FRANCHISE, "치킨"),
    "프랭크버거":  (FRANCHISE, "햄버거"),
    "맥도날드":    (FRANCHISE, "햄버거"),
    "오뚜기":      (MAKER, "라면"),
    "팔도":        (MAKER, "라면"),
    "오리온":      (MAKER, "과자"),
    "배스킨라빈스": (FRANCHISE, "디저트"),
    "던킨":        (FRANCHISE, "디저트"),
    "이삭토스트":  (FRANCHISE, "분식"),
    "파리바게뜨":  (FRANCHISE, "베이커리"),
    "나폴레옹과자점": (FRANCHISE, "베이커리"),
    "브레댄코":    (FRANCHISE, "베이커리"),
    "홍루이젠":    (FRANCHISE, "베이커리"),
    "노티드":      (FRANCHISE, "베이커리"),
    "삼송빵집":    (FRANCHISE, "베이커리"),
    "본죽":        (FRANCHISE, "한식"),
    "본죽&비빔밥":  (FRANCHISE, "한식"),
    "본도시락":    (FRANCHISE, "도시락"),
    "본설렁탕":    (FRANCHISE, "한식"),
    "본우리반상":  (FRANCHISE, "한식"),
    "멘지":        (FRANCHISE, "한식"),
    "본흑염소·능이삼계탕": (FRANCHISE, "한식"),
    "이지브루잉커피": (CAFE, ""),
    "요거프레소":  (CAFE, ""),
    "매머드커피":  (CAFE, ""),
    "더벤티":      (CAFE, ""),
    "컴포즈커피":  (CAFE, ""),
    "할리스":      (CAFE, ""),
    "김밥천국":    (FRANCHISE, "분식"),
    "바르다김선생": (FRANCHISE, "분식"),
    "죠스떡볶이":  (FRANCHISE, "분식"),
    "명랑핫도그":  (FRANCHISE, "분식"),
    "스시로":      (FRANCHISE, "일식"),
    "에그드랍":    (FRANCHISE, "샌드위치"),
    "써브웨이":    (FRANCHISE, "샌드위치"),
    "샐러디":      (FRANCHISE, "샐러드"),
    # 아래 셋은 robots.txt 는 허용하지만 이용약관이 수집·복제를 금지한다.
    # 운영자 판단으로 수집하되, 삭제 요청이 오면 다투지 말고 즉시 내린다.
    #   이마트24  — 약관 제8조 ⑧ "크롤러, 매크로 프로그램, 스파이더, 스크래퍼 등… 수집"
    #   도미노피자 — 푸터 "사전 서면동의 없이 정보·콘텐츠를 상업적 목적으로 스크래핑"
    #   폴바셋    — 약관 v9.0 "사전 승낙 없이 복제 또는 유통하거나 상업적으로 이용"
    #
    # 등록하지 않는 곳:
    #   롯데리아 — lotteeatz.com/robots.txt 가 알려진 봇 티어 외 모든 UA 를
    #              Disallow: / 로 차단한다. 뚫으려면 UA 를 위장해야 하는데,
    #              그건 대법원 2021도1533 이 정보통신망 침입죄 근거로 든 행위다.
    #   빕스     — robots.txt 가 Googlebot·NaverBot 외 전면 차단
    #   GS25     — 사이트 자체가 폐쇄(앱 전용 이관) robots.txt 는 /goods/ 를 허용하지만 사이트 푸터가
    # "사전 서면동의 없이 정보·콘텐츠를 상업적 목적으로 스크래핑" 을 금지한다.
    # 이마트24(약관 제8조 ⑧)와 같은 종류의 건이라 사용자 판단이 필요하다.
    # 롯데리아는 등록하지 않는다. lotteeatz.com/robots.txt 가 알려진 봇 티어 외
    # 모든 UA 를 Disallow: / 로 막는다. 우리 UA 는 어느 티어에도 없어 전 경로 금지다.
    # 다른 호스트로 우회하는 건 신원을 밝히는 이 프로젝트 방침에 어긋난다.
}


# 상품 상세 페이지가 없는 브랜드를 위한 폴백. 카드를 누르면 최소한 그 브랜드
# 메뉴 페이지로는 가야 한다. 트래픽을 브랜드로 돌려주는 게 이 링크의 목적이다.
SITES = {
    "메가MGC커피":  "https://www.mega-mgccoffee.com/menu/",
    "스타벅스":     "https://www.starbucks.co.kr/menu/drink_list.do",
    "이디야커피":   "https://www.ediya.com/contents/drink.html",
    "설빙":         "https://sulbing.com/menu/",
    "빽다방":       "https://paikdabang.com/menu/menu_new/",
    "커피빈":       "https://www.coffeebeankorea.com/menu/list.asp",
    "CU":          "https://cu.bgfretail.com/product/product.do",
    "세븐일레븐":   "https://www.7-eleven.co.kr/product/presentList.asp",
    "맘스터치":     "https://www.momstouch.co.kr/menu/new.php",
    "버거킹":       "https://www.burgerking.co.kr/menu/main",   # 해시 라우팅 아님(history 모드)
    "프랭크버거":   "https://www.frankburger.co.kr/html/menu_1.html",
    "BBQ":         "https://bbq.co.kr/categories/17",   # /menu 는 404. Next.js 라 카테고리 경로를 쓴다
    "bhc치킨":      "https://www.bhc.co.kr/menu/chicken.asp",
    "교촌치킨":     "https://www.kyochon.com/menu/chicken.asp",
    # /menu/new_p 의 _p 는 AJAX 조각 경로라 사람이 열면 에러 JSON 이 뜬다.
    "굽네치킨":     "https://www.goobne.co.kr/menu/menu_list",
    "피자헛":       "https://www.pizzahut.co.kr/menu",
    "미스터피자":   "https://www.mrpizza.co.kr/bbs/board.php?bo_table=menu",
    "파파존스":     "https://pji.co.kr/menu/pizza",
    "배스킨라빈스": "https://www.baskinrobbins.co.kr/menu/fom.php",
    "던킨":         "https://www.dunkindonuts.co.kr/menu",
    "이삭토스트":   "https://www.isaac-toast.co.kr/menu/menu.php",
    "이마트24":     "https://emart24.co.kr/goods/pl",
    "도미노피자":   "https://www.dominos.co.kr/goods/list",
    "폴바셋":       "https://www.baristapaulbassett.co.kr/menu/List.pb",
    "파리바게뜨":   "https://www.paris.co.kr/products/",
    "나폴레옹과자점": "https://napoleonbakery.co.kr/h/b/napoleon/products",
    "브레댄코":     "https://www.breadnco.kr/portfolio-category/new/",
    "홍루이젠":     "https://www.hongruizhen.com/goods/goods_list.php?cateCd=001",
    "노티드":       "http://www.knottedstore.com/menu",   # TLS 2026-09-06 만료 → http
    "삼송빵집":     "https://ssbnc.kr/doc/menu0.php",
    "본죽":         "https://www.bonif.co.kr/brand/menu?brdCd=BF101",
    "본죽&비빔밥":   "https://www.bonif.co.kr/brand/menu?brdCd=BF102",
    "본도시락":     "https://www.bonif.co.kr/brand/menu?brdCd=BF104",
    "본설렁탕":     "https://www.bonif.co.kr/brand/menu?brdCd=BF105",
    "본우리반상":   "https://www.bonif.co.kr/brand/menu?brdCd=BF107",
    "멘지":         "https://www.bonif.co.kr/brand/menu?brdCd=BF111",
    "본흑염소·능이삼계탕": "https://www.bonif.co.kr/brand/menu?brdCd=BF113",
    "이지브루잉커피": "https://www.bonif.co.kr/brand/menu?brdCd=BF114",
    "요거프레소":   "https://yogerpresso.co.kr/menu/menu-new.html",
    "김밥천국":     "https://kimbab1009.com/31",
    "바르다김선생": "https://teacherkim.co.kr/menu/list.html?bs=004001",
    "죠스떡볶이":   "https://jawsfood.co.kr/menu/menu.html",
    "명랑핫도그":   "https://myungranghotdog.com/menu/new",
    "매머드커피":   "https://mmthcoffee.com/sub/menu/new_list.php",
    "더벤티":       "https://theventi.co.kr/new2022/menu/all.html",
    "컴포즈커피":   "https://composecoffee.com/index1",
    "할리스":       "https://www.hollys.co.kr/menu/espresso.do",
    "스시로":       "https://www.sushiro.co.kr/pm",
    "에그드랍":     "http://www.eggdrop.co.kr/menu/list.php?category=NEW",
    "써브웨이":     "https://www.subway.co.kr/menuList/sandwich",
    "샐러디":       "https://salady.com/menu/list_1",
    "맥도날드":     "https://www.mcdonalds.co.kr/kor/menu/burger",
    "오뚜기":       "https://www.otoki.com/pr/news?searchNewsCategory=PRESS",
    "팔도":         "https://www.paldofood.co.kr/product/noodle",
    "오리온":       "https://www.orionworld.com/board/list/87",
}


def site(brand: str) -> str:
    """브랜드 메뉴 페이지. 등록이 안 됐으면 빈 문자열(링크를 안 건다)."""
    return SITES.get(brand, "")


# 먹는 게 아닌 것들. 브랜드가 분류로 알려주는 경우가 가장 정확하고, 없으면 이름을 본다.
# 이름 단어는 좁게 잡는다 — '보틀'·'케이스' 를 넣었더니 '보틀캔디'·'빅보틀팝'·
# '드립백 커피 틴케이스' 같은 실제 식품이 걸렸다.
NONFOOD_CATEGORIES = {"MD상품", "생활용품"}
NONFOOD_WORDS = (
    "텀블러", "머그", "키링", "파우치", "볼펜", "피규어", "무드등",
    "에코백", "담요", "인형", "칫솔", "치약", "바디밤", "가그린", "스타킹", "양말",
    "립밤", "클렌징", "핸드크림", "샴푸", "앞치마", "쇼핑백", "보냉백", "보온병",
    "우산", "슬리퍼", "방향제", "콘돔", "마스크3", "손소독", "굿즈", "가방", "세제",
)
# 넣으면 안 되는 단어들. 한국어는 단어 경계가 없어서 우연히 걸린다.
#   보틀  → 빅보틀팝·보틀캔디 (과자)
#   모자  → 분모자 = 당면. 로제분모자볶이·분모자 로제 떡볶이
#   케이스 → 드립백 커피 틴케이스 세트
#   타올  → 롯데)로케타올리베라스750ml = 와인 ('로케타 올리베라스')
#   매트  → 패트와매트반반바 (아이스크림)
#   핸디  → 복숭아 가득 핸디 젤리 (스타벅스). 텀블러류는 '텀블러' 로 이미 잡힌다
# 새 단어를 넣기 전에 전체 데이터에 대고 식품 오탐이 0인지 먼저 세라.


def is_nonfood(name: str, category: str = "") -> bool:
    """굿즈·생활용품인가. 카페 MD, 편의점 생활용품, 콜라보 굿즈가 여기 걸린다."""
    return category in NONFOOD_CATEGORIES or any(w in name for w in NONFOOD_WORDS)


def kind(brand: str) -> tuple:
    """등록되지 않은 브랜드는 조용히 넘기지 않고 드러낸다."""
    if brand not in BRANDS:
        raise KeyError(f"BRANDS 에 없는 브랜드: {brand}")
    return BRANDS[brand]


@dataclass
class Item:
    """브랜드 어댑터가 공통으로 뱉는 상품 1건.

    이 서비스의 용건은 '신제품'이다. 전체 카탈로그가 아니다.
    어댑터는 아래 세 신호로 신제품 여부를 최대한 알려줘야 한다.
      released_at  브랜드가 출시일/등록일을 알려주면 채운다. 가장 강한 신호.
      is_new       브랜드가 NEW 배지 등으로 신제품이라 표시하면 True.
                   신제품이 아니라고 확인되면 False. 알 수 없으면 None.
      promo        1+1·2+1 같은 행사/할인 상품. 신제품이 아니므로 화면에서 뺀다.
                   세트·콤보는 여기 쓰지 마라. collect.drop_sets() 가 이름으로
                   거른다. 어댑터마다 세트 기준이 달라져 신메뉴 세트가 잘렸다.
    셋 다 비어 있으면 '어제 없던 게 오늘 있다'는 diff 로만 판정하게 되고,
    그 브랜드는 합류 첫날엔 신제품을 하나도 못 내놓는다. 그래도 그게 정직하다.
    """
    brand: str
    name: str
    name_en: str = ""
    desc: str = ""
    image: str = ""
    labels: list = field(default_factory=list)   # ICE / HOT 등
    category: str = ""
    uploaded_at: str = ""                        # 브랜드가 알려주면 채움 (YYYY-MM-DD)
    released_at: str = ""                        # 출시일/등록일. uploaded_at 보다 강한 신호
    is_new: bool | None = None                   # 브랜드가 신제품이라 표시했는가
    promo: bool = False                          # 행사/할인 상품 (신제품 아님)
    nonfood: bool = False                        # 굿즈·생활용품. 먹는 게 아니라 따로 관리한다
    url: str = ""                                # 브랜드 사이트의 이 상품 페이지.
                                                 # 없으면 SITES 의 브랜드 메뉴 URL 로 떨어진다
    brand_type: str = ""                         # 레지스트리에서 채운다. 어댑터는 비워둔다
    brand_sub: str = ""                          # 프랜차이즈 세부분류(햄버거/피자/치킨)

    @property
    def key(self) -> str:
        return make_key(self.brand, self.name)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["key"] = self.key
        d["brand_type"], d["brand_sub"] = kind(self.brand)
        d["url"] = self.url or site(self.brand)
        # 어댑터가 따로 표시하지 않았으면 이름·분류로 판정한다.
        d["nonfood"] = self.nonfood or is_nonfood(self.name, self.category)
        return d


# 해외 러너에서 국내 사이트는 간헐적으로 연결 실패·타임아웃이 난다.
# 연결 단계 재시도는 transport 가 맡고, 읽기 타임아웃은 retry() 로 감싼다.
def client(**kw) -> httpx.Client:
    # 어댑터가 Referer 같은 헤더를 더할 수 있게 UA 위에 덮어쓴다.
    headers = {"User-Agent": UA} | dict(kw.pop("headers", {}))
    kw.setdefault("timeout", httpx.Timeout(30.0, connect=15.0))
    # verify 는 transport 에 넘겨야 한다. httpx.Client(transport=..., verify=...) 는
    # transport 가 있으면 verify 를 조용히 무시한다. 이걸 모르고 구형 TLS 사이트
    # 4곳(또래오래·노랑통닭·훌랄라·지코바)이 '연결 불가'로 잘못 판정됐다.
    verify = kw.pop("verify", True)
    return httpx.Client(headers=headers, follow_redirects=True,
                        transport=httpx.HTTPTransport(retries=3, verify=verify), **kw)


def retry(fn, tries: int = 3, delay: float = 2.0):
    """일시적 오류는 간격을 늘려가며 다시 시도한다. 끝까지 실패하면 그대로 올린다."""
    for i in range(tries):
        try:
            return fn()
        except (httpx.TransportError, httpx.HTTPStatusError):
            if i == tries - 1:
                raise
            time.sleep(delay * (i + 1))
