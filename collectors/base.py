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
# 빵집·빙수·아이스크림·도넛은 '외식'이 아니라 카페로 묶는다. 한국에서는
# 끼니가 아니라 커피 옆에서 먹는 것이고, 사용자가 찾는 자리도 거기다.
BRANDS = {
    "메가MGC커피": (CAFE, "커피"),
    "스타벅스":    (CAFE, "커피"),
    "이디야커피":  (CAFE, "커피"),
    "설빙":        (CAFE, "빙수"),
    "빽다방":      (CAFE, "커피"),
    "커피빈":      (CAFE, "커피"),
    "폴바셋":      (CAFE, "커피"),
    "CU":         (CVS, ""),
    "세븐일레븐":  (CVS, ""),
    "이마트24":    (CVS, ""),
    "GS25":       (CVS, ""),
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
    "롯데칠성음료": (MAKER, "음료"),
    # 직영몰이라 남의 브랜드도 판다. 그래도 '제조사' 로 두는 건 1단 '가공식품' 이
    # 누가 만들었나가 아니라 무엇이냐 축이기 때문이다(TAXONOMY §3). 세부분류를
    # '음료' 가 아니라 '냉동식품' 으로 둔 근거는 collectors/fredit.py docstring.
    "hy프레딧":    (MAKER, "냉동식품"),
    "아워홈":      (MAKER, "냉동식품"),
    "동서식품":    (MAKER, "커피"),
    "샘표":        (MAKER, "조미료"),
    "배스킨라빈스": (CAFE, "아이스크림"),
    "던킨":        (CAFE, "도넛"),
    "이삭토스트":  (FRANCHISE, "분식"),
    "파리바게뜨":  (CAFE, "베이커리"),
    "나폴레옹과자점": (CAFE, "베이커리"),
    "브레댄코":    (CAFE, "베이커리"),
    "홍루이젠":    (CAFE, "베이커리"),
    "노티드":      (CAFE, "베이커리"),
    "삼송빵집":    (CAFE, "베이커리"),
    "본죽":        (FRANCHISE, "한식"),
    "본죽&비빔밥":  (FRANCHISE, "한식"),
    "본도시락":    (FRANCHISE, "도시락"),
    "본설렁탕":    (FRANCHISE, "한식"),
    "본우리반상":  (FRANCHISE, "한식"),
    "멘지":        (FRANCHISE, "한식"),
    "본흑염소·능이삼계탕": (FRANCHISE, "한식"),
    "이지브루잉커피": (CAFE, "커피"),
    "요거프레소":  (CAFE, "커피"),
    "매머드커피":  (CAFE, "커피"),
    "더벤티":      (CAFE, "커피"),
    "컴포즈커피":  (CAFE, "커피"),
    "할리스":      (CAFE, "커피"),
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
    #   동서식품   — 약관 제13조 ② "동서식품을 이용함으로써 얻은 정보를 사전승낙
    #               없이 복제·전송·출판·배포… 영리목적으로 이용하여서는 안 됩니다".
    #               크롤러·스크래퍼 금지 조항은 없다. 제2조가 '이용자' 를 회원으로
    #               정의하고 '영리목적' 단서가 붙어 그대로 걸리는지는 애매하다.
    #   샘표      — 같은 성격의 복제·배포 제한. 단 그 조항이 '새미네부엌 커뮤니티'
    #               절 안에 있어 보도자료실에 걸리는지 애매하다. 크롤러 금지 없음.
    #
    # 등록하지 않는 곳:
    #   롯데리아 — lotteeatz.com/robots.txt 가 알려진 봇 티어 외 모든 UA 를
    #              Disallow: / 로 차단한다. 뚫으려면 UA 를 위장해야 하는데,
    #              그건 대법원 2021도1533 이 정보통신망 침입죄 근거로 든 행위다.
    #   빕스     — robots.txt 가 Googlebot·NaverBot 외 전면 차단
    #
    # GS25 는 2026-10-01 에 등록했다. 상품 목록은 여전히 수집 불가다 —
    # gs25.gsretail.com 이 전 경로 본사 SPA 로 리다이렉트되고, 앱(우리동네GS)의 웹 짝인
    # m.woodongs.com 에도 상품 라우트가 없다. 대신 본사 보도자료에서 오뚜기·오리온과
    # 같은 방식으로 신제품만 뽑는다. 자세한 근거는 collectors/gs25.py docstring 참고.
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
    # 상품 목록 페이지가 없는 브랜드다. 기사별 상세 주소가 Item.url 로 붙으므로
    # 이건 폴백일 뿐이다. 브랜드 소개(/brand/gs25)보다 보도자료 목록이 용건에 가깝다.
    "GS25":        "https://www.gsretail.com/news/press-releases",
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
    # 상품별 주소는 롯데칠성몰(mall.) 이라 Item.url 로 따로 붙는다. 이건 폴백이다.
    "롯데칠성음료": "https://company.lottechilsung.co.kr/kor/product/newprdt/list.do",
    # 상품별 주소(/product/detail?prdId=)가 Item.url 로 붙으므로 이건 폴백이다.
    "hy프레딧":    "https://m.fredit.co.kr/product/main-tab-menu?keyword=main&ctgId=C10000001001",
    # 아워홈·샘표는 상품 목록 페이지가 없어 보도자료를 폴백으로 쓴다(GS25 선례).
    # 동서식품은 상품 목록이 있고 어댑터도 그쪽을 읽는다.
    "아워홈":      "https://www.ourhome.co.kr/front/newsboardlist.do",
    "동서식품":    "https://www.dongsuh.co.kr/product/list/1",
    "샘표":        "https://www.sempio.com/news/press-release",
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
    # 편의점은 category 가 '신상품'·'행사 상품' 같은 판매채널이라 분류로는 못 가른다.
    # 아래는 전체 데이터에 대고 식품 오탐 0 을 확인하고 넣은 것들이다.
    "키친타올", "마스크팩", "폼클렌저", "클렌져", "면도기", "면도날",
    "화장지", "오버나이트", "간편유심", "토퍼", "립테라피", "로션", "위생",
    "브레스스프레이",
    # 생활용품 제조사명. 그 이름이 붙은 건 먹는 게 아니다.
    "리스테린", "페브리즈", "질레트", "센카", "니베아", "존슨", "다우니",
)
# 넣으면 안 되는 단어들. 한국어는 단어 경계가 없어서 우연히 걸린다.
#   보틀  → 빅보틀팝·보틀캔디 (과자)
#   모자  → 분모자 = 당면. 로제분모자볶이·분모자 로제 떡볶이
#   케이스 → 드립백 커피 틴케이스 세트
#   타올  → 롯데)로케타올리베라스750ml = 와인 ('로케타 올리베라스')
#   매트  → 패트와매트반반바 (아이스크림)
#   핸디  → 복숭아 가득 핸디 젤리 (스타벅스). 텀블러류는 '텀블러' 로 이미 잡힌다
#   티슈  → 던킨 '티슈 브레드'
#   렌즈  → '글로렌즈)골든고비라거', 이디야 '사과당근클렌즈주스'
#   피지  → 스타벅스 '리버 피치 피지오'·'쿨 라임 피지오' (음료)
#   가위  → 한가위보름달만찬·풍성한가위정찬도시락. '주방 가위' 로 붙여야 한다
#   빨대  → 메가 '빨대 텀블러'. 어차피 '텀블러' 가 잡는다
#   면도  → '짜장면도시락'·'라면도시락'. 편의점 이름은 띄어쓰기가 없어서 걸린다
#   찜기  → '소갈비찜기획상품'. 편의점이 '기획팩·기획상품' 을 아주 흔히 쓴다
#   스프레이 → '식용유 스프레이'·'휘핑 스프레이크림'. 먹는 스프레이가 실재한다
#   유심  → '두유심플'·'우유심쿵'
# 위 넷은 지금 데이터엔 오탐이 없지만 앞으로 날 자리다. 좁혀서 넣었고
# 좁히면서 잃은 건 0건이다(면도→면도기·면도날 4건 그대로).
#
# ⚠️ 리스테린·페브리즈 같은 브랜드명을 넣은 건 이 목록만의 예외다.
# ALCOHOL_WORDS 에서는 '하이트' 를 "제조사명이라 음료도 걸린다" 며 일부러 뺐다.
# 비식품 쪽은 이 회사들이 식품을 안 만들어서 안전한 것뿐이니, 한쪽 선례를
# 들고 다른 쪽에 적용하지 마라.
# 새 단어를 넣기 전에 전체 데이터에 대고 식품 오탐이 0인지 먼저 세라.


def is_nonfood(name: str, category: str = "") -> bool:
    """굿즈·생활용품인가. 카페 MD, 편의점 생활용품, 콜라보 굿즈가 여기 걸린다."""
    return category in NONFOOD_CATEGORIES or any(w in name for w in NONFOOD_WORDS)


# 주류. 청소년보호법상 주류 광고는 연령 확인 없는 공개 페이지에 올릴 게 아니고,
# "오늘 뭐 새로 나왔나" 보러 온 사람이 찾는 것도 아니다. 비식품과 같은 방식으로
# 본 목록에서 뺀다. 데이터에는 남겨둔다 — 나중에 연령 확인을 붙이면 살릴 수 있다.
ALCOHOL_CATEGORIES = {"주류"}

# 이마트24 는 상품명 앞에 주종을 붙인다("레드)베어풋카베르네소비뇽750ml").
# 이름 단어보다 이게 정확하다. 세븐일레븐은 제조사를 붙여서("롯데)옐로우테일…")
# 접두로는 못 가르고, 그쪽은 아래 포도품종 단어로 잡는다.
# 실측해서 주종인 것만 넣었다 — '옐로우)' 는 과자, '포차24)' 는 안주다.
ALCOHOL_PREFIXES = ("레드", "화이트", "로제", "스파클링", "샴페인",
                    "위스키", "사케", "칵테일", "보드카", "럼", "리커")

ALCOHOL_WORDS = (
    "맥주", "비어", "라거", "에일", "IPA", "흑맥주", "발포주",
    "위스키", "하이볼", "칵테일", "소주", "보드카", "샴페인", "데낄라", "브랜디",
    "하이네켄", "기네스", "칭따오", "버드와이저",
    # 포도품종·와인용어. 와인은 이름에 '와인' 이 안 들어가는 게 보통이라
    # 품종으로 잡아야 한다(세븐일레븐 '롯데)옐로우테일오로라팩(쉬라)').
    "와인", "까버네", "까베르네", "카베르네", "쇼비뇽", "소비뇽",
    "샤르도네", "샤도네이", "피노누아", "메를로", "모스카토", "쉬라", "시라즈",
    "리슬링", "산지오베제", "말벡",
    "까르미네르",
    # 주종도 품종도 이름에 없는 것들. 제품명으로 잡을 수밖에 없고 이 목록은
    # 늘어난다 — 구조적 한계다. '클라우드' 는 할리스 '미니저그 (클라우드크림)'
    # 이 걸려서 편의점 제조사 접두 뒤에 오는 경우로 좁혔다.
    "옐로우테일", ")클라우드", "한맥", "카스아이스", "칼스버그", "삿포로",
    "더드래프트", "크로넨버그", "쇼쿠사이", "효케츠", "파울라너",
    "바이젠", "츄하이", "필스너", "스타우트",
    "라들러", "에비스", "써머스비", "상그리아", "브룻", "스텔라퓨어", "크루저",
    ")페로니",   # '페로니' 로는 피자헛 '페페로니 러버' 를 문다
)

# 뒤에 무엇이 오느냐로 갈리는 것들. 단순 포함으로는 못 가른다.
_ALCOHOL_RE = re.compile(r"막걸리(?!향|맛|풍미)")
# 넣으면 안 되는 단어들. 전체 데이터에 대고 센 결과다.
#   막걸리 → 스타벅스 '막걸리향 크림 콜드 브루' = 커피. 2건 전부 오탐
#   사케  → '사케라또 아포가토'(스타벅스), 사케동. 접두 '사케)' 로만 잡는다
#   카스  → 카스테라 28건
#   테라  → 카스테라, 프론테라
#   럼    → 브라운쿠키크럼블, 블루베리플럼주스. 접두 '럼)' 로만 잡는다
#   사와  → 사사사와플크림샌드
#   청주  → 청주식돼지김치짜글이
#   하이트 → 제조사명이라 '하이트)무알콜레몬유자' 같은 음료도 걸린다
#   스텔라 → 카스텔라 19건 (빽다방 생크림 카스텔라·던킨 카스텔라 도넛)
#   코젤  → 츄파춥스게코젤리
#   기린  → 기린오후의차밀크티
#   몰트  → 스타벅스 '콜드 브루 몰트'
#   블랑  → 지금은 전건 술이지만 2글자라 언제든 식품을 문다. 크로넨버그로 잡는다
# 새 단어를 넣기 전에 전체 데이터에 대고 식품 오탐이 0인지 먼저 세라.

# 무알콜 표기가 있으면 주류가 아니다. '아사히스타일프리캔맥주' 처럼 이름에
# 맥주가 들어가도 술이 아닌 것들이 있다.
NONALCOHOL_MARKS = ("무알콜", "논알콜", "넌알콜", "비알콜",
                    "무알코올", "논알코올", "넌알코올")

# 도수 0.0 표기. 이 검사는 맨 앞에서 즉시 False 를 돌려주므로 오탐이 나면
# 술이 그대로 화면에 올라간다 — 방향이 반대인 유일한 규칙이다. 그냥 "0.0" 을
# 넣으면 '…10.0g' 같은 용량 표기에 걸려 주류 필터가 통째로 꺼진다.
_ZERO_ABV = re.compile(r"(?<!\d)0\.0(?!\d)")


# 제조사 자사 주류 브랜드. 이름만으로는 못 가르고 그 회사 상품일 때만 술이다.
# '클라우드' 를 전역 단어로 넣으면 노티드 '밀크 클라우드'·'티라미수 클라우드'
# 와 할리스 '미니저그 (클라우드크림)' 을 문다. 브랜드를 묶으면 그게 안 걸린다.
# 편의점이 파는 같은 제품은 제조사 접두가 붙어("롯데)클라우드…") 따로 잡힌다.
ALCOHOL_BY_BRAND = {
    # 값은 정규식이다. '새로' 는 2글자라 그냥 넣으면 '새로나온…' 을 문다
    # (브랜드 안으로 좁혀도 그렇다). 뒤에 한글이 붙으면 다른 말이므로 끊는다.
    "롯데칠성음료": (r"클라우드", r"처음처럼", r"새로(?![가-힣])", r"백화수복",
                 r"스카치블루", r"순하리", r"청하", r"설중매", r"마주앙",
                 r"충전소", r"별빛"),
}


def is_alcohol(name: str, category: str = "", brand: str = "") -> bool:
    """술인가. 무알콜 표기가 있으면 이름에 '맥주' 가 들어가도 술이 아니다."""
    if any(m in name for m in NONALCOHOL_MARKS) or _ZERO_ABV.search(name):
        return False
    if category in ALCOHOL_CATEGORIES:
        return True
    if any(re.search(w, name) for w in ALCOHOL_BY_BRAND.get(brand, ())):
        return True
    if _ALCOHOL_RE.search(name):
        return True
    head = name.split(")", 1)[0] if ")" in name else ""
    return head in ALCOHOL_PREFIXES or any(w in name for w in ALCOHOL_WORDS)


# 카드에 안 찍는 라벨. 정본은 여기다 — 홈(collect.card)과 하위 페이지
# (web/pages)가 각자 적어두면 한쪽만 고쳐진다. 실제로 그랬다: 홈만 고쳐져
# 상세·브랜드·유형 페이지 548장에 'NEW NEW' 중복이 1,024건 남아 있었다.
#
# 행사 라벨은 편의점이 신상품에 도입 행사를 거의 항상 붙여서(세븐일레븐
# 신상품 탭 91건 전부) 그대로 두면 신상 목록이 할인 목록처럼 읽힌다.
# 행사 정보 자체는 data/products.json 에 남는다.
PROMO_LABELS = {"1+1", "2+1", "3+1", "1 + 1", "2 + 1", "3 + 1",
                "할인", "증정", "세일", "특가"}

# NEW 배지를 이미 그리므로 같은 뜻의 라벨은 겹쳐 찍지 않는다.
#
# 목록으로 적지 않고 규칙으로 센다. 전에 {"NEW","신메뉴",…} 로 열거했다가
# 삼송빵집의 'NEW MENU' 를 놓쳐 'NEW NEW MENU' 가 나란히 떴다. 브랜드마다
# 띄어쓰기·대소문자·꼬리말이 제각각이라 열거하면 반드시 빠뜨린다.
_DUP_HEADS = ("NEW", "신메뉴", "신상품", "신제품", "출시")


def _is_dup(label: str) -> bool:
    """우리 NEW 배지와 같은 뜻인가. 'NEW MENU'·'new'·'신 메뉴' 를 다 잡는다."""
    flat = label.replace(" ", "").upper()
    return any(flat.startswith(h.replace(" ", "").upper()) for h in _DUP_HEADS)


def shown_labels(labels) -> list:
    """카드에 찍을 라벨만 남긴다. 홈·상세·브랜드·유형 전부 이걸 쓴다."""
    return [l for l in (labels or [])
            if l and l not in PROMO_LABELS and not _is_dup(l)]


# ── 표시용 이름 ────────────────────────────────────────────────────────
#
# 편의점 상품명은 POS 에 박힌 문자열 그대로다 — `CJ)얼큰우동221g(큰컵)`,
# `롯데)말랑카우밀크79g`. 사람이 읽기도 어렵고 유튜브에 검색도 안 된다.
#
# 🔴 **원본 name 은 절대 바꾸지 않는다.** make_key() 가 name 으로 키를 만들고
# 그 키에 first_seen 이력이 매달려 있다. 이름을 건드리면 전 상품의 키가 바뀌어
# "어제 없던 게 오늘 있다" 가 전건 참이 되고 이력이 통째로 끊긴다.
# 그래서 원본은 그대로 두고 **표시용 이름을 따로** 만든다(derive 가 d["display"]).

# 제조사·납품사 접두. 떼도 되는 것만 들어간다.
#
# 가르는 기준은 추측이 아니라 실측이다 — **둘 이상의 편의점 체인에 같은 접두가
# 나타나면 제조사**다. 제조사는 모든 체인에 납품하지만 PB·자체 라인은 그 체인에만
# 있다. data/products.json 7,005건으로 세어 32개가 나왔고 전건을 눈으로 확인했다.
# 반대로 한 체인에만 있는 접두(`포차24)` 이마트24 30건, `성수310)` 53건,
# `405)` CU 18건, `PBICK)` 22건)는 PB 브랜드라 떼면 상품명을 잃는다 — 안 뗀다.
#
# ⚠️ 정확히 일치할 때만 뗀다. 부분일치로 하면 `하이트진로)`·`롯데리아)` 가
# `하이트)`·`롯데)` 로 걸려서 회사가 다른데도 떨어진다.
# ⚠️ 새 접두를 넣기 전에 전체 데이터에 돌려 상품명이 깎이지 않는지 먼저 세라.
MAKER_PREFIXES = {
    "CJ", "HK", "그린", "널담", "농심", "대상", "동원", "롯데", "리뉴", "마즈",
    "매일", "바세린", "바프", "빙그레", "삼립", "샘표", "서주", "스위트", "엠즈",
    "오뚜기", "오비", "유한", "제니코", "카브루", "코카", "크라운", "티젠", "피지",
    "하겐", "하림", "하이트", "해태",
}

# 선두 대괄호. 숫자뿐이면(나폴레옹과자점 `[123] Love you more` 등 83건) 버리고,
# 말이 들어 있으면(`[파란라벨]`·`[프로틴]`·`[고기곱빼기]`) 괄호만 벗겨 남긴다.
# 통째로 버리면 `[프로틴]닭가슴살` 에서 라인 구분이 사라진다.
_LEAD_BRACKET = re.compile(r"^\[([^\[\]]*)\]\s*")

# `제조사)` 접두. 여는 괄호를 품으면 안 된다 — `디카페인카페모카(H)` 의 `(H)` 가
# 접두로 걸려 이름 앞 10글자가 통째로 날아간다(빽다방·브레댄코 349건이 그랬다).
_PREFIX = re.compile(r"^([^()\[\]\s]{1,10})\)\s*")

# 용량·규격 단위. 숫자가 **바로 앞에 붙어** 있을 때만 단위로 본다.
#   - 사이에 공백을 허용하면 `포차24 매콤껍데기` 의 `24 매` 가 걸린다.
#   - 맨 앞이면 이름 자체다 — `5G_국대급시너지도시락` 의 `5G`.
#   - 앞이 숫자·쉼표면 가격이다 — `롯데)3,900매콤닭껍질튀김` 의 `900매`.
#   - 뒤에 영문·숫자가 오면 단위가 아니다 — `자이언트X3_…`, `초BIG!…`.
# `개`·`구`·`포`는 뺐다. `8포션`·`6구`·`12개월` 처럼 말의 일부로 걸린다
# (`개입` 은 남긴다 — 그건 단위가 맞다).
_UNIT = r"(?:kg|개입|ml|인분|g|l|t|p|입|매)"
_SPEC = re.compile(r"(?<=.)(?<![\d,.])\d+(?:\.\d+)?" + _UNIT + r"(?![A-Za-z0-9])", re.I)

# `*6`·`*4입` 같은 묶음 표기. `x`·`X` 는 넣지 않는다 — `자이언트X3` 이 걸린다.
_MULT = re.compile(r"\s*[*×]\s*\d+\s*(?:개입|입|매|p)?(?![A-Za-z0-9가-힣])", re.I)

# 괄호 안이 규격뿐인 것. `(6입)`·`(355ml)` 과 POS 입수코드 `(12)`·`(36)`.
_SPEC_PAREN = re.compile(r"\s*\(\s*(?:[*×]?\s*)?\d+(?:\.\d+)?\s*" + _UNIT + r"?\s*\)", re.I)

# 끝에 붙은 보조 괄호 앞에만 공백을 넣는다. `카스테라(초코)` → `카스테라 (초코)`.
# 이름 중간은 건드리지 않는다 — `소프트(모닝)롤` 을 쪼개면 더 읽기 나쁘다.
_TAIL_PAREN = re.compile(r"(?<=\S)\(([^()]*)\)\s*$")


def _sub_outside_parens(rx, s: str) -> str:
    """괄호 **밖**에서만 치환한다. 괄호 안은 통째로 두거나 통째로 버린다.

    괄호 안에서 용량만 빼면 껍데기가 남아 더 흉해진다 — hy프레딧
    `…도라지 캔디(1.2g x 50정) 2통` 이 `…캔디( x 50정) 2통` 이 됐었다.
    """
    spans = [m.span() for m in re.finditer(r"\([^()]*\)", s)]
    def rep(m):
        return m.group(0) if any(a <= m.start() < b for a, b in spans) else " "
    return rx.sub(rep, s)


def _drop_unmatched_parens(s: str) -> str:
    """짝 없는 괄호만 공백으로 바꾼다. 안의 글자는 안 버린다.

    편의점 이름은 괄호가 열리고 안 닫힌 게 흔하다(`…하몽맛45g(`,
    `바닐라라떼300ml(컵`). 여는 괄호에서 잘라버리면 `스키틀즈젤리(후르츠요거트`
    의 맛 이름이 사라진다 — 글자는 남기고 괄호만 없앤다.
    """
    depth, out = 0, []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            if depth == 0:
                out.append(" ")
                continue
            depth -= 1
        out.append(ch)
    if depth:                       # 안 닫힌 여는 괄호를 뒤에서부터 지운다
        left, rev = depth, []
        for ch in reversed(out):
            if ch == "(" and left:
                rev.append(" ")
                left -= 1
            else:
                rev.append(ch)
        out = list(reversed(rev))
    return "".join(out)


def display_name(name: str) -> str:
    """화면·검색어에 쓸 이름. 원본은 그대로 두고 읽을 수 있는 쪽만 만든다.

    `CJ)얼큰우동221g(큰컵)` → `얼큰우동 (큰컵)`
    `롯데)말랑카우밀크79g`   → `말랑카우밀크`
    `포차24)맥반석오징어`    → `포차24 맥반석오징어`   (PB 브랜드라 안 뗀다)

    ⚠️ 사이즈·온도 괄호(`(HOT)`·`(L)`·`(R)`)는 **남긴다.** 빽다방
    `아메리카노(HOT)`/`(ICED)` 와 이디야 `(L)`/`(EX)` 가 128건 있는데, 떼면
    목록에 같은 이름의 카드가 둘씩 뜬다. 변형을 접는 건 별개 작업이다.

    정리한 결과가 2글자 이하로 줄면 **원본을 그대로 돌려준다** — 복구 불가로
    보고 손대지 않는 쪽이 안전하다(`면)2`·`CJ)맛밤80g` 등 12건).
    """
    src = (name or "").strip()
    if not src:
        return name or ""
    s = src

    m = _LEAD_BRACKET.match(s)
    if m:
        inner, rest = m.group(1).strip(), s[m.end():]
        s = rest if (not inner or inner.isdigit()) else f"{inner} {rest}"

    m = _PREFIX.match(s)
    if m:
        head, rest = m.group(1), s[m.end():]
        # 1글자 접두는 CU 의 분류 코드다 — `도)`=도시락 `김)`=김밥 `샌)`=샌드위치
        # `햄)`·`샐)`·`면)`·`삼)`·`주)`·`랩)`·`핫)`. 전건 확인했고 상품명이 아니다.
        # 나머지는 떼지 않고 괄호만 벗긴다. 글자를 하나도 안 잃는 쪽이다.
        s = rest if (head in MAKER_PREFIXES or len(head) == 1) else f"{head} {rest}"

    s = _SPEC_PAREN.sub(" ", s)        # 괄호 안이 규격뿐이면 괄호째 버린다
    s = _sub_outside_parens(_MULT, s)
    s = _sub_outside_parens(_SPEC, s)
    s = re.sub(r"\(\s*\)", " ", s)
    s = _drop_unmatched_parens(s)
    s = _TAIL_PAREN.sub(r" (\1)", s)
    s = re.sub(r"\s+", " ", s).strip(" ·,/")
    return s if len(s.replace(" ", "")) >= 3 else src


def derive(d: dict) -> dict:
    """레지스트리·판정에서 나오는 값들을 채운다. 제자리에서 고치고 그대로 돌려준다.

    여기가 정본이어야 한다. 수집한 상품은 Item.to_dict() 로 들어오지만, 수집이
    실패한 브랜드의 이전분은 그 경로를 안 거쳐서 collect 가 따로 채워야 한다.
    전에 그 두 자리에 같은 계산을 각자 적어뒀더니 한쪽에만 image 정규화가 빠져서,
    수집이 실패한 브랜드만 http 이미지를 들고 들어와 카드가 빈 네모가 됐다.
    필드를 하나 더 늘릴 때 여기만 고치면 되게 둔다.
    """
    d["brand_type"], d["brand_sub"] = kind(d["brand"])
    d["url"] = d.get("url") or site(d["brand"])
    # 표시용 이름. 원본 name 은 건드리지 않는다(위 display_name 주석 참고).
    # 위의 nonfood·alcohol 과 달리 **매번 다시 계산한다** — 규칙을 고치면
    # 수집이 실패해 이월된 행도 같이 따라오게 하려는 것이다. 재료가 name
    # 하나뿐이라 다시 계산해도 잃을 값이 없다.
    d["display"] = display_name(d["name"])
    # 어댑터가 따로 표시하지 않았으면 이름·분류로 판정한다.
    #
    # ⚠️ 이 두 줄은 한 방향으로만 움직인다(True 가 박히면 안 내려간다).
    # 수집 성공분은 매번 어댑터가 준 값(보통 False)에서 다시 계산하니 괜찮지만,
    # 수집 실패해서 이월된 행은 이미 파생된 값이라 **단어를 빼도 안 풀린다.**
    # "단어를 뺐는데 왜 아직 굿즈로 있지?" 가 나오면 여기가 답이다.
    # 지금 데이터는 깨끗하다(저장값 vs 재계산 불일치 0건).
    cat = d.get("category", "")
    d["nonfood"] = bool(d.get("nonfood")) or is_nonfood(d["name"], cat)
    d["alcohol"] = bool(d.get("alcohol")) or is_alcohol(d["name"], cat, d["brand"])
    # 우리 페이지는 https 라 http 이미지는 브라우저가 막는다(혼합 콘텐츠).
    # 빈 네모가 뜨느니 사진 없는 카드로 그리는 게 낫다. 에그드랍 73건이
    # 그랬다 — 인증서가 2025-05-27 에 만료돼 https 로는 아예 안 열린다.
    if (d.get("image") or "").startswith("http://"):
        d["image"] = ""
    return d


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
    alcohol: bool = False                        # 술. 연령 확인이 없으니 본 목록에서 뺀다
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
        return derive(d)


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
