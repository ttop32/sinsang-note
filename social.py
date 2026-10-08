"""브랜드 공식 SNS. 브랜드 페이지의 바깥 링크로 쓴다.

왜 여기 따로 두나 — `collectors/base.py` 의 `SITES` 옆에 붙이는 게 자연스러워
보이지만, 저건 수집이 쓰는 표고 이건 화면만 쓰는 표다. 그리고 지금 여러 작업이
`base.BRANDS` 를 동시에 고치는 중이라 같은 파일에 넣으면 서로 덮어쓴다.

⚠️ **핸들을 이름에서 유추하지 마라.** 20개를 찍어봤더니 8개는 없는 계정, 4개는
남의 개인 계정이었다(`ediya_coffee`→윤소연, `bhc_chicken`→임방환,
`bbq_chicken`→Jazhari Johnson, `orionworld`→Ajay Kaundal). 남의 개인 계정을
브랜드 공식인 양 걸면 그 사람이 실제로 피해를 본다.

여기 있는 것은 전부 **브랜드 공식 홈페이지가 스스로 가리키는 링크**에서 따서
**비로그인으로 열어 확인**한 것이다. 근거와 조사 방법은 `notes/INSTAGRAM.md`.
공식 사이트가 안 가리키면 **없는 것으로 둔다** — 추측해서 채우지 않는다.

조사하면서 걸린 함정(핸들을 추가할 때 다시 밟기 쉽다):
  · 공식 사이트가 가리켜도 계정이 죽어 있을 수 있다(바르다김선생). 열어봐야 한다.
  · HTML 주석 안에 옛 링크가 남아 있다(커피빈). 정규식으로 긁으면 그걸 집는다.
  · 아이콘만 있고 주소가 빈 경우가 있다(김밥천국 `http://instagram.com/`).
  · 언더바 개수·점과 언더바 구분이 다 함정이다(`ediya.coffee` ≠ `ediya_coffee`).
  · 영상 임베드는 채널 주인을 증명하지 못한다. 처갓집양념치킨 메인의 배경 영상은
    남의 개인 채널(김재훈) 것이었다. 채널을 열어 그 브랜드 것인지 봐야 한다.
  · 사이트가 가리키는 게 본사·창업자 채널일 수 있다. 더본코리아 홈페이지가 거는
    유튜브는 백종원 개인 채널이라 브랜드 링크로 쓰지 않았다.

인스타 조사일 2026-10-01, 유튜브 조사일과 인스타 보강일 2026-10-02.
유튜브 근거는 `notes/YOUTUBE.md`.

2026-10-08 보강 — 브랜드가 171곳에서 217곳으로 늘면서 생긴 빈칸 121곳을 다시 훑어
인스타 32곳·유튜브 15곳을 채웠다. 근거와 못 찾은 사유는 `notes/SOCIAL-LINKS-2026-10-08.md`.
그때 새로 밟은 함정:
  · `schema.org` `sameAs` 가 죽은 계정·남의 계정을 가리키고 푸터 쪽이 맞는 경우가 있다
    (쥬씨 `juicyjuice_official`→팔로워 6 / 카페인중독 `caffeine_addiction`→팔로워 2).
  · 같은 브랜드라도 인스타 핸들과 유튜브 핸들이 다르다. 한쪽을 복사하면 안 된다
    (우지커피 `oozy.coffee_official` vs `oozycoffee`, 카페051 `cafe_051_official` vs `cafe051_official`).
  · 유튜브 한글 핸들은 사이트가 퍼센트 인코딩으로 걸어둔다. 여기엔 한글 그대로 적는다.
"""

# 브랜드 → 인스타그램 핸들. 없는 곳은 아예 안 적는다(빈 문자열도 두지 않는다).
INSTAGRAM = {
    "33떡볶이":             "33tteokbokki",
    "60계":               "60chicken",
    "BBQ":               "bbq_offi",
    "CJ제일제당":            "cjcheiljedang",
    "CU":                "cu_official",
    "GS25":              "gs25_official",
    "KFC":               "kfc_korea",
    "bhc치킨":             "bhc_chicken_official",
    # 브랜드 전용이 아니라 hy 법인 계정이다. 쇼핑몰 운영 주체라 걸어 두되, 브랜드 계정이 생기면 바꾼다.
    "hy프레딧":             "hy.official.kr",
    "가마치통닭":             "gamachi_official",
    "공차":                "gongcha_korea",
    "교촌치킨":              "kyochon_official",
    "국수나무":              "noodletree_official",
    # 언더바 세 개.
    "굽네치킨":              "the___goobster",
    "김가네":               "gimgane_official",
    "김밥킹":               "gimbapking_official",
    "꾸브라꼬숯불치킨":          "kkubeu_home",
    "나폴레옹과자점":           "napoleon.bakery",
    "네네치킨":              "nenechicken_official",
    # 공식 사이트 schema.org 에 적힌 norangtongdak486 은 삭제된 계정이다.
    "노랑통닭":              "norangtongdak_official",
    "노브랜드버거":            "nobrandburger.official",
    "노티드":               "cafeknotted_kr",
    "농심":                "nongshim",
    "누구나홀딱반한닭":          "nuguna_banhandak",
    "달롱도르":              "dallondor_official",
    "달리는커피":             "dalcu_korea",
    # 브랜드 전용이 아니라 대상그룹 법인 계정이다. 공식 사이트 `sameAs` 가 가리키는 건 이것뿐.
    "대상":                "daesang_news",
    "더벤티":               "theventi_official",
    "던킨":                "dunkin_kr",
    "도미노피자":             "dominostory",
    "동경에서먹었던규동":         "tokyokyudong",
    # 브랜드 계정이 아니라 자사몰(동원몰) 계정이다. 공식 사이트 푸터가 가리키는 건 이것뿐.
    "동원F&B":             "dongwonmall",
    "두찜":                "twozzim",
    "디저트39":             "dessert39_official",
    # 공식 사이트는 ttangttangchicken_official 도 같이 걸어두는데 그쪽은 삭제된 계정이다.
    "땅땅치킨":              "ttangttang.chicken_new",
    "떡군이네떡볶이":           "tteokgoonene",
    "또래오래":              "toreore_official",
    "뚜레쥬르":              "touslesjours_kr",
    "라홍방마라탕":            "lahongbang_official",
    "롯데리아":              "lotteria_kr",
    "롯데웰푸드":             "lottewellfood_food",
    # 사이트가 "음료 인스타그램"이라고 이름 붙인 계정. 처음처럼·새로 같은 주류 계정은 따로 있다.
    "롯데칠성음료":            "lottechilsung",
    "마왕족발":              "mawang_official",
    "맘스터치":              "momstouch.love",
    "매머드커피":             "mmthcoffee",
    # 핸들 끝에 언더바가 붙는다.
    "매스커피":              "masscoffee_",
    "매일유업":              "freshmaeil",
    "맥도날드":              "mcdonalds_kr",
    "메가MGC커피":           "mega.mgc.coffee_official",
    "멕시카나":              "mexicana_official",
    "멘지":                "ramen_menji",
    # 핸들 끝에 언더바가 붙고 중간에 `.com` 이 들어간다. 도메인이 아니라 핸들이다.
    "면사랑":               "noodlelovers.com_",
    "명랑핫도그":             "myungranghotdog_official",
    # 핸들 끝에 언더바가 붙는다. 빼면 다른 계정이다.
    "미스터피자":             "mrpizza_official_",
    "미카도스시":             "mikadosushi_official",
    "바른치킨":              "barunchicken_official",
    "배스킨라빈스":            "baskinrobbinskorea",
    "백소정":               "baeksojeong_official",
    "백억커피":              "10billioncoffee",
    "버거운버거":             "burgerunburger_official",
    "버거킹":               "burgerkingkorea",
    # 공식 사이트 메뉴에 걸린 bobae__official 은 삭제된 계정이다. 이게 산 쪽.
    "보배반점":              "bobaebanjum_kr",
    "본도시락":              "bondosirak_official",
    "본설렁탕":              "bonseol_official",
    "본우리반상":             "bonwoori_official",
    "본죽":                "bonjukofficial",
    # 본죽과 같은 계정을 쓴다. 같은 회사의 자매 브랜드다.
    "본죽&비빔밥":            "bonjukofficial",
    "부어치킨":              "boor_chicken",
    "브라운돈까스":            "browntonkatsu",
    "브레댄코":              "breadnco_kr",
    "빙그레":               "binggraekorea",
    "빙동댕":               "bing_dong_daeng",
    "빨라쪼":               "palazzo_kr",
    "빽다방":               "paikscoffee_official",
    # 사조대림 전용이 아니라 모회사 사조그룹 계정이다. 사조 사이트가 가리키는 건 이것뿐.
    "사조대림":              "sajogroup",
    "삼송빵집":              "samsong_bakery",
    "삼양식품":              "samyangfoods",
    "삼첩분식":              "samcheop__official",
    "샐러디":               "saladykorea",
    "샘표":                "sempio.official",
    "세븐일레븐":             "7elevenkorea",
    "소림마라":              "sorimmara_official",
    "쉐이크쉑":              "shakeshackkr",
    "쉬즈베이글":             "shes_bagel_official",
    "스시로":               "sushiro_korea",
    "스쿨푸드":              "schoolfood_official",
    "스타벅스":              "starbuckskorea",
    "슬로우캘리":             "slowcali_official",
    "신세계푸드":             "shinsegaefood.official",
    "싸다김밥":              "ssadagb_official",
    "써브웨이":              "subwaykorea",
    "쏘자토스트":             "ssojatoast_official",
    "아웃백스테이크하우스":        "outbackkorea",
    "아워홈":               "ourhome.delicious",
    "얌샘김밥":              "yumsem_official",
    "에그드랍":              "eggdrop.official",
    # 팔로워 15명·게시물 3개뿐이다. 공식 사이트가 가리키고 이름도 맞아 넣었다.
    "에밀리아젤라또":           "emiliagelato_official",
    "엽기떡볶이":             "yupdduk_official",
    "오뚜기":               "otoki_daily",
    "오리온":               "orion_world",
    "왓더버거":              "what_the_burger",
    "요거프레소":             "yogerpresso_official",
    # 점과 언더바가 섞인다. 유튜브 핸들(`oozycoffee`)과 모양이 다르다.
    "우지커피":              "oozy.coffee_official",
    "원할머니보쌈족발":          "wongrandma",
    # 공식 사이트는 케이터링 계정(eupcheonri_catering)만 직접 건다. 이건 사이트가 가리키는
    # 공식 유튜브(소개에 공식 도메인을 되걸어 확인됨)가 자기 소개에 적어둔 본계정이다.
    "읍천리382":            "eupcheonri_official",
    "이디야커피":             "ediya.coffee",
    "이마트24":             "emart24_official",
    "이삭토스트":             "isaactoast.official",
    "이지브루잉커피":           "easybrewingcoffee",
    "자담치킨":              "jadamchicken_official",
    # 언더바 두 개.
    "죠스떡볶이":             "jaws__official",
    # 공식 사이트 schema.org 의 juicyjuice_official 은 팔로워 6명짜리 남의 계정이다. 푸터 링크가 산 쪽.
    "쥬씨":                "newjuicy_kr",
    "지미존스":              "jimmyjohns_korea",
    # 계정 주체가 운영사 (주)고구려푸드다. 소개에 짬뽕10101 이 BRAND.1 로 적혀 있다.
    "짬뽕10101":           "goguryeofood_official",
    "짬뽕관":               "jjambbonggwan",
    # 푸터는 쥬씨와 공용인 juicychayam_official(`쥬씨&차얌`) 도 거는데, schema.org 가 선언한 차얌 전용 계정이 이것.
    "차얌":                "chayamkr",
    "참토스트":              "charmtoast_official",
    "처갓집양념치킨":           "cheogajip_go",
    "춘리마라탕":             "chunlimalatang_official",
    # 공식 사이트가 schema.org 에 적어둔 chickenplus 는 팔로워 12명짜리 남의 개인 계정이다.
    "치킨플러스":             "chickenplus__official",
    "카페051":             "cafe_051_official",
    "카페만월경":             "manwolgyung_official",
    "카페베네":              "caffebene_official",
    # 공식 사이트 schema.org 의 caffeine_addiction 은 팔로워 2명짜리 빈 계정이다. 푸터 버튼이 가리키는 이쪽이 공식.
    "카페인중독":             "caffeinism_company",
    "커피베이":              "coffeebay_official",
    # 공식 사이트 주석 안에 죽은 계정(coffeebeankorea)이 같이 있었다. 이게 산 쪽이다.
    "커피빈":               "coffeebean_kr",
    "컴포즈커피":             "compose_coffee",
    "쿠우쿠우":              "qooqoo_official",
    "퀴즈노스":              "quiznoskorea",
    "크라운제과":             "crownsns",
    "탐앤탐스":              "tomntoms_coffee",
    "탕화쿵푸마라탕":           "tanghuokungfu_korea",
    "태리로제떡볶이":           "terryroze_official",
    "텐퍼센트커피":            "tenpercent.coffee",
    "토마토도시락":            "tomatodosirak_official",
    "투썸플레이스":            "atwosomeplace_official",
    "파리바게뜨":             "parisbaguette_kr",
    "파스쿠찌":              "pascucci_kr",
    "파파존스":              "papajohnskr",
    # https 인증서가 깨져 있어 http 로만 열린다.
    "팔공티":               "palgongtea.official",
    "팔도":                "paldofood",
    "페리카나":              "pelicana1982",
    "포케올데이":             "pokeallday_official",
    "폴바셋":               "paulbassettkorea",
    "푸라닭":               "puradak_official",
    "풀무원":               "pulmuone",
    # 핸들 끝에 언더바가 붙는다.
    "프랭크버거":             "frankburger_official_",
    "피자마루":              "pizzamaru_official",
    "피자스쿨":              "pizzaschool_official",
    "피자헛":               "pizzahutkorea",
    # 계정 이름은 `하림자연실록`. 소개가 하림 공식이라고 밝힌다.
    "하림":                "harim_natural",
    "하이트진로음료":           "hitejinrobeverage_official",
    "한솥":                "hansot_official",
    "할리스":               "official_hollys",
    "해태제과식품":            "haitai_co",
    "호식이두마리치킨":          "hosigi1999",
    "홍루이젠":              "hungruichenkorea",
    "홍익돈까스":             "hongikdonkatsu_official",
    "홍짜장":               "2026_hongjjajang_official",
    "후라이드 참 잘하는집":       "good__fried",
}

# 브랜드 → 유튜브 핸들(`@` 뒤). 인스타와 같은 규칙으로 모았다.
# 본아이에프 8개 브랜드(본죽·본도시락·멘지 …)는 전부 같은 `Bonif_` 를 쓴다 —
# 브랜드별 채널이 없고 본사 채널 하나에 브랜드별 영상이 같이 올라온다.
YOUTUBE = {
    "33떡볶이":             "33tteokbokki",
    "60계":               "60gye",
    "BBQ":               "bbq_offi",
    # 채널 이름은 `제당슈만`. 푸터가 "유튜브 공식 채널"로 거는 쪽이다.
    "CJ제일제당":            "CJCheilJedangOfficial",
    "CU":                "cu.official",
    "GS25":              "official_GS25",
    "KFC":               "kfckorea.official",
    "bhc치킨":             "bhcchicken",
    # 인스타와 같이 hy 법인 채널이다. 핸들에 한글이 들어간다.
    "hy프레딧":             "hy.한국야쿠르트",
    "가마치통닭":             "GAMACHI",
    "교촌치킨":              "KYOCHON-TV",
    "국수나무":              "noodles_tree",
    "굽네치킨":              "goobne",
    "김가네":               "김가네-j5r",
    "네네치킨":              "네네치킨OFFICIAL",
    "노랑통닭":              "norang_tongdak",
    "농심":                "nongshim",
    "누구나홀딱반한닭":          "Nuguna_banhandak",
    # 채널 이름은 `대상그룹 DAESANG 디튜브`. 인스타와 같이 법인 채널이다.
    "대상":                "DTUBE",
    "더벤티":               "theventi_official",
    "던킨":                "DunkinDonutsKorea",
    "도미노피자":             "dominostory3082",
    "동경에서먹었던규동":         "tokyogyudong",
    "동원F&B":             "DongwonFnB",
    "두찜":                "twozzim_official",
    "디저트39":             "dessert39_official",
    "땅땅치킨":              "ttangttangchicken",
    "또래오래":              "toreore9292",
    "라홍방마라탕":            "lahongbang_official",
    # 채널 이름은 `리아버거가게`.
    "롯데리아":              "lotteriakorea",
    # 사이트가 "음료 공식 유튜브"라고 이름 붙인 채널. 주류·칠성레이블 채널은 따로 있다.
    "롯데칠성음료":            "Lotte7star",
    "맘스터치":              "momstouch6549",
    "매일유업":              "maeili2mo",
    "메가MGC커피":           "megamgccoffee",
    "멘지":                "Bonif_",
    "면사랑":               "noodlelovers.official",
    "명랑핫도그":             "myungranghotdog",
    "모토이시":              "모토이시창업톡톡",
    "미소야":               "misoya_official",
    "미스터피자":             "mrpizza15770077",
    # 사이트가 @user-gk9it3zs2f·@바른치킨-t6l 도 같이 거는데 둘 다 없는 채널이다.
    "바른치킨":              "barunchicken_official",
    "배스킨라빈스":            "baskinrobbinskorea",
    "백소정":               "baeksojeong",
    "백억커피":              "10billioncoffee",
    "버거킹":               "burgerking_korea",
    "보배반점":              "bobaebanjum",
    "본도시락":              "Bonif_",
    "본설렁탕":              "Bonif_",
    "본우리반상":             "Bonif_",
    "본죽":                "Bonif_",
    "본죽&비빔밥":            "Bonif_",
    "본흑염소·능이삼계탕":        "Bonif_",
    "부어치킨":              "부어치킨-j4k",
    "브라운돈까스":            "브라운돈까스-l3y",
    # 사이트가 Global 채널로 따로 적은 @OMG_omyguide 가 아니라 국내 채널 쪽이다.
    "빙그레":               "official.binggrae",
    # 한글 핸들. 사이트는 퍼센트 인코딩된 주소로 걸어둔다.
    "빙동댕":               "빙동댕빙수",
    "삼송빵집":              "ssbnc",
    "삼양식품":              "samyangfoods",
    "샐러디":               "saladykorea",
    "샘표":                "sempioKorea",
    "세븐일레븐":             "7elevenkorea",
    "쉐이크쉑":              "SHAKESHACKKOREA",
    "스시로":               "Sushiro_korea",
    "스타벅스":              "starbuckskorea",
    "슬로우캘리":             "Slowcali_official",
    # 채널 이름은 `스프TV`.
    "신세계푸드":             "SHINSEGAEFOOD.OFFICIAL",
    "싸다김밥":              "ssadagb",
    "써브웨이":              "Subwaykr",
    "아웃백스테이크하우스":        "outbackkorea",
    # 핸들 끝에 마침표가 하나 더 붙는다. 빼면 다른 주소가 된다.
    "아워홈":               "ourhome.official.",
    "애플꼬마김밥":            "애플꼬마김밥",
    "얌샘김밥":              "yumsem",
    "에그드랍":              "eggdrop.official",
    # 채널 이름은 `동대문엽기떡볶이`. 소개가 yupdduk.com 과 공식 인스타를 되건다.
    "엽기떡볶이":             "yupdduk_official",
    "오뚜기":               "otoki_daily",
    "오리온":               "ORIONworld",
    "요거프레소":             "yogerpresso_official",
    "우지커피":              "oozycoffee",
    "원할머니보쌈족발":          "wongrandma1975",
    "읍천리382":            "eupcheonri_official",
    "이디야커피":             "ediyacoffee",
    "이마트24":             "emart24_official",
    "이지브루잉커피":           "Bonif_",
    "자담치킨":              "jadamchicken_official",
    # 사이트는 옛 `channel/UC2e5…` 주소로 건다. 소개가 `쥬씨 유튜브 공식계정`.
    "쥬씨":                "juicy_kr_official",
    "지미존스":              "jimmyjohns_korea",
    # 계정 주체가 운영사 (주)고구려푸드다. 소개에 짬뽕10101 이 BRAND.1 로 적혀 있다.
    "짬뽕10101":           "goguryeofood",
    "짬뽕관":               "jjambbonggwan",
    # 채널 이름은 `공오일`. 소개가 `카페051 공식 유튜브 채널`이라고 밝힌다. 인스타 핸들(cafe_051_official)과 언더바가 다르다.
    "카페051":             "cafe051_official",
    # 소개가 공식 도메인 cafewhale.com 과 공식 인스타를 되건다.
    "카페만월경":             "manwolgyung",
    # 사이트는 `channel/UCQ7…` 주소로 건다. 핸들에 숫자가 붙는다.
    "카페베네":              "caffebene4373",
    # 채널 이름이 브랜드명과 다르다. 커피빈 공식 사이트 푸터가 가리키는 채널이 이것뿐이다.
    "커피빈":               "커피빈유통실험실",
    "쿠우쿠우":              "qooqoo_official",
    "퀴즈노스":              "quiznoskorea2559",
    "탕화쿵푸마라탕":           "tanghuokungfu",
    "토마토도시락":            "tomatodosirak_official",
    "투썸플레이스":            "a_twosome_place",
    "파리바게뜨":             "loveparisbaguette",
    # 채널 이름은 `파스쿠찌_유튜브점`.
    "파스쿠찌":              "pascucci_kr",
    "파파존스":              "파파존스-z8d",
    "팔도":                "paldofood6295",
    "페리카나":              "pelicanachicken",
    "포케올데이":             "pokeallday",
    # 채널 이름이 운영사(엠즈씨드)다. 소개에 폴 바셋 공식 채널이라고 적혀 있다.
    "폴바셋":               "paulbassett2407",
    "푸라닭":               "PURADAK",
    # 뉴스룸(SITES 주소)의 SNS 블록은 통째로 주석 처리돼 있다. 산 링크는 본사 사이트 pulmuone.co.kr 쪽.
    "풀무원":               "pulmuone.official",
    "프랭크버거":             "Frankburger_official",
    # 한글 핸들. 사이트는 옛 `user/pizzamaru` 주소로 건다.
    "피자마루":              "공식채널피자마루",
    "피자헛":               "enjoypizzahut",
    # 언더바 두 개.
    "하림":                "Harim__TV",
    "하이트진로":             "hitevideo",
    "하이트진로음료":           "hitejinrobeverage",
    "한솥":                "한솥도시락-e2r",
    "해태제과식품":            "Haitaico",
    "호식이두마리치킨":          "호식이두마리치킨-m3w",
    "홍루이젠":              "hungruichen",
    "후라이드 참 잘하는집":       "hoocham.official",
}


def instagram(brand: str) -> str:
    """공식 인스타 주소. 없으면 빈 문자열."""
    handle = INSTAGRAM.get(brand)
    return f"https://www.instagram.com/{handle}/" if handle else ""


def youtube(brand: str) -> str:
    """공식 유튜브 주소. 없으면 빈 문자열."""
    handle = YOUTUBE.get(brand)
    return f"https://www.youtube.com/@{handle}" if handle else ""


def links(brand: str) -> list:
    """브랜드 페이지에 걸 바깥 SNS 링크. (이름, 주소) 목록, 없으면 빈 목록."""
    out = []
    if url := instagram(brand):
        out.append(("인스타그램", url))
    if url := youtube(brand):
        out.append(("유튜브", url))
    return out
