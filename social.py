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

조사일 2026-10-01. 유튜브는 아직 조사 전이다.
"""

# 브랜드 → 인스타그램 핸들. 없는 곳은 아예 안 적는다(빈 문자열도 두지 않는다).
INSTAGRAM = {
    "BBQ":               "bbq_offi",
    "CU":                "cu_official",
    "GS25":              "gs25_official",
    "bhc치킨":             "bhc_chicken_official",
    # 브랜드 전용이 아니라 hy 법인 계정이다. 쇼핑몰 운영 주체라 걸어 두되, 브랜드 계정이 생기면 바꾼다.
    "hy프레딧":             "hy.official.kr",
    "교촌치킨":              "kyochon_official",
    # 언더바 세 개.
    "굽네치킨":              "the___goobster",
    "나폴레옹과자점":           "napoleon.bakery",
    "노티드":               "cafeknotted_kr",
    "더벤티":               "theventi_official",
    "던킨":                "dunkin_kr",
    "도미노피자":             "dominostory",
    "맘스터치":              "momstouch.love",
    "매머드커피":             "mmthcoffee",
    "맥도날드":              "mcdonalds_kr",
    "메가MGC커피":           "mega.mgc.coffee_official",
    "멘지":                "ramen_menji",
    "명랑핫도그":             "myungranghotdog_official",
    # 핸들 끝에 언더바가 붙는다. 빼면 다른 계정이다.
    "미스터피자":             "mrpizza_official_",
    "배스킨라빈스":            "baskinrobbinskorea",
    "버거킹":               "burgerkingkorea",
    "본도시락":              "bondosirak_official",
    "본설렁탕":              "bonseol_official",
    "본우리반상":             "bonwoori_official",
    "본죽":                "bonjukofficial",
    # 본죽과 같은 계정을 쓴다. 같은 회사의 자매 브랜드다.
    "본죽&비빔밥":            "bonjukofficial",
    "브레댄코":              "breadnco_kr",
    "빽다방":               "paikscoffee_official",
    "삼송빵집":              "samsong_bakery",
    "샐러디":               "saladykorea",
    "세븐일레븐":             "7elevenkorea",
    "스시로":               "sushiro_korea",
    "스타벅스":              "starbuckskorea",
    "써브웨이":              "subwaykorea",
    "에그드랍":              "eggdrop.official",
    "오뚜기":               "otoki_daily",
    "오리온":               "orion_world",
    "요거프레소":             "yogerpresso_official",
    "이디야커피":             "ediya.coffee",
    "이마트24":             "emart24_official",
    "이삭토스트":             "isaactoast.official",
    "이지브루잉커피":           "easybrewingcoffee",
    # 언더바 두 개.
    "죠스떡볶이":             "jaws__official",
    # 공식 사이트 주석 안에 죽은 계정(coffeebeankorea)이 같이 있었다. 이게 산 쪽이다.
    "커피빈":               "coffeebean_kr",
    "컴포즈커피":             "compose_coffee",
    "파리바게뜨":             "parisbaguette_kr",
    "파파존스":              "papajohnskr",
    "팔도":                "paldofood",
    "폴바셋":               "paulbassettkorea",
    # 핸들 끝에 언더바가 붙는다.
    "프랭크버거":             "frankburger_official_",
    "피자헛":               "pizzahutkorea",
    "할리스":               "official_hollys",
    "홍루이젠":              "hungruichenkorea",
}


def instagram(brand: str) -> str:
    """공식 인스타 주소. 없으면 빈 문자열."""
    handle = INSTAGRAM.get(brand)
    return f"https://www.instagram.com/{handle}/" if handle else ""


def links(brand: str) -> list:
    """브랜드 페이지에 걸 바깥 SNS 링크. (이름, 주소) 목록, 없으면 빈 목록."""
    out = []
    if url := instagram(brand):
        out.append(("인스타그램", url))
    return out
