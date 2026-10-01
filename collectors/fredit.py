"""hy 프레딧 — hy(한국야쿠르트) 직영몰의 '신제품' 탭.

`notes/CANDIDATES-DIRECT2.md` §2-1 이 채택한 소스다. 그 문서가 남긴 미확인 두 개
(등록일 유무 · 비식품/외부브랜드 혼입)를 2026-10-01 실측으로 닫은 결과를 여기 적는다.

수집 경로. 화면 HTML 은 쓸 수 없다:
  - `/product/main-tab-menu?keyword=main&ctgId=C10000001001` 은 1.65MB SSR 인데
    **렌더된 `<div id="__layout">` 안에 상품 카드가 한 장도 없다.** 상품명이 있는
    자리는 `window.__NUXT__` 페이로드(JS IIFE, 변수 치환 압축)와 `ld+json` 블록
    둘뿐이다. 조사 문서가 '상품명 SSR 포함'이라고 적은 건 그 두 블록을 본 것이다.
    `ld+json` 은 파싱은 쉬운데 **1페이지 20건뿐**이고 배지·분류가 없다.
  - `?page=2`·`?currentPage=2`·`?pageSize=200` 은 전부 1페이지를 되돌려준다(실측).
    즉 SSR 로는 159건에 닿을 방법이 없다.
그래서 화면이 쓰는 JSON API 를 그대로 쓴다. 쿠키·로그인·토큰 없이 열린다
(브라우저는 `fredit-token` JWT 를 같이 보내지만 빼고도 같은 응답이 온다. 확인함).

  GET /api/freditProduct/v01/tabMenuProducts/{ctgId}            ← 신제품 전량
  GET /api/freditProduct/v01/tabMenuProducts/{ctgId}/{subCtgId} ← 분류별
  GET /api/freditProduct/v01/mainTopMenuProductPageInfo/{ctgId}  ← 분류 11종 목록

⚠️ **페이징이 쿼리스트링이 아니라 `rest-api-header` 헤더다.** 값은 JSON 문자열
`{"currentPage":1,"pageSize":100,"prdOrderGbn":"20"}` 이다. 이 헤더를 빼면
**200 OK 에 `totalRecords:0`, `body:[]` 가 온다 — 예외가 안 난다.** 이 레포가 가장
여러 번 데인 '조용한 0건' 모양 그대로라, 아래 `_page()` 가 건수를 직접 검산한다.

⚠️ 그리고 **`currentPage` 의 보폭이 `pageSize` 와 무관하게 20 으로 고정이다.**
실측(2026-10-01): `pageSize=100` 으로 `currentPage` 를 1→2 로 올리면 101번째가 아니라
**21번째** 행부터 온다. 즉 `offset = (currentPage-1) × 20`, 창 크기만 `pageSize` 다.
순진하게 1,2,3 으로 올리면 80건씩 겹쳐서 받는다(그래서 159건짜리를 200건 받았다).
`_STRIDE` 로 `pageSize // 20` 만큼 건너뛴다. 그래서 `PAGE_SIZE` 는 20의 배수여야 한다.

날짜 — **없다. 찾아봤고 없다.**
  - 목록 행의 키 88개 전수를 떴다. 등록일·출시일 성격의 필드가 없다
    (`dispClDtm` 은 전건 null, `orderTime`·`time` 도 null).
  - 상세(`/product/detail?prdId=`)도 같다. 상세 응답 전체에서 날짜꼴 문자열을
    정규식으로 긁으면 이미지 경로의 `20260928`·`20260929` 뿐이다.
  - `robots.txt` 가 가리키는 `sitemap.xml` 도 봤다. `<lastmod>` 가 2,894개 URL 에
    **딱 3가지 값**(2026-08-12 1,967 / 2026-07-08 622 / 2026-06-10 305)이다.
    사이트맵 생성 배치 날짜지 상품 날짜가 아니다.
그래서 `released_at` 은 비운다. 대신 이미지 경로의 타임스탬프를 `uploaded_at` 에
넣는다 — 롯데칠성·신라호텔과 같은 성격이고 §9-8 이 요구하는 자리다. 두 꼴이 있다:
    /prdimg/20260929/001/...        (82건)  디렉터리가 날짜
    /prdimg/71827/71827_thumb_1790556531598.jpg (77건)  epoch 밀리초
전 159건이 둘 중 하나로 날짜가 나온다(결손 0).

**이게 업로드 시각인데 왜 믿을 만한가** — 메가MGC 때(173건 중 81건이 2024-06 한 달에
몰린 일괄 재업로드)와 달리, 여기선 **API 가 돌려주는 순서와 이 날짜가 같이 움직인다.**
인접 158쌍 중 날짜가 거꾸로 가는 곳이 13쌍(8%)뿐이다. 하루 최대 쏠림도 24건으로,
입점사 한 곳의 SKU 등록 묶음이지 사이트 전체 재업로드가 아니다. 그래도 **출시일이
아니라 등록 시각의 대리값**이다. `released_at` 으로 올리면 거짓말이 된다.

**'신제품' 탭이 1년치 보관함인가 — 아니다.** 브레댄코가 'new' 분류에 1년치를 쌓아둔
전례가 있어 먼저 쟀다. 159건의 위 날짜가 **2026-07-01 ~ 2026-09-29** 안에 전부 들어온다
(수집일 2026-10-01). 더 오래된 게 한 건도 없고 경계가 월초에 딱 떨어진다 —
대략 3개월 롤링 창이다. 우리 화면 기준(`collect.WINDOW` 60일)보다 길 뿐 영구 보관함이
아니다. 그래서 `is_new=True` 로 두고, 60일보다 오래된 건 `uploaded_at` 으로
`collect.is_fresh()` 가 알아서 떨군다(실측 159 → 식품 98 → 창 안 75 → 세트 제외 64).

비식품 — **단어가 아니라 브랜드가 준 분류로 가른다.**
조사 문서는 `NONFOOD_WORDS` 에 `찜기`·`조리도구`·`주방 가위`·`플레이팅팬` 을 보태라고
적었는데, 그 전에 이 탭이 **분류를 직접 준다**는 걸 찾았다. 신제품 탭 아래 11분류 중
`뷰티`·`생활 · 주방용품`·`반려동물` 이 비식품 축이다. 둘을 같이 재 봤다(2026-10-01):

    브랜드 분류로 잡히는 비식품   56건  (+ 반려동물 5건)  = 61
    NONFOOD_WORDS 로 잡히는 것                            = 24   ← 37건이 분류로만 잡힌다

분류로만 잡히는 37건: 실리만 찜기·조리도구·플레이팅팬 12종, 바겐슈타이거 수저·트레이·
믹싱볼 4종, 피죤 3종, 에코버 섬유유연제·얼룩제거제·세정제 3종, 바스틀리·해피얼쓰
티슈·타월 5종, 폴프랜즈 풋커버 3종, 에콜린 앰플, hyFredit 실리콘 지퍼백, 펫푸드 5종 …
반대로 **분류가 식품이라는데 단어가 비식품이라고 한 건 0건**이다. 둘이 충돌하지 않으니
`to_dict()` 의 OR 결합이 안전하고, 어느 쪽이 늘거나 줄어도 이 어댑터는 안 흔들린다.

⚠️ **위 24 라는 숫자는 `NONFOOD_WORDS` 가 바뀔 때마다 움직인다.** 2026-10-01 하루 안에
`찜기`·`조리도구`·`주방 가위`·`플레이팅팬`·`키친타월` 이 들어왔다가(24→37) 다시 빠졌다(37→24).
빠질 때 이 159건을 다시 셌는데 **13건이 전부 `nonfood=True` 를 유지했다** — 단어가 아니라
분류가 받치고 있었기 때문이다. 숫자가 아니라 **"분류 신호 단독으로 61건을 다 받는다"**
가 이 블록에서 변하지 않는 사실이다.
그래서 **`NONFOOD_WORDS` 는 이 어댑터 때문에 건드릴 필요가 없고**,
`Item.nonfood=True` 로 어댑터가 직접 표시한다.
(분류가 섞이는 상품 — 식품 분류와 비식품 분류를 둘 다 가진 것 — 은 159건 중 0건이라
"비식품 분류만 가진 것"으로 안전하게 가를 수 있다. 1건(`브이푸드 포스파티딜세린`)은
어느 분류에도 안 들어가는데, hy 자사 건강식품이라 식품으로 둔다.)

반려동물 5건(애니몬다 펫푸드)도 `nonfood=True` 로 둔다. 먹긴 먹는데 **사람이 먹는 게
아니라서** '오늘 새로 나온 먹거리' 목록에 섞이면 안 된다. 굿즈와 같은 처리라
데이터에는 남고 목록만 갈린다. 판단이 갈릴 수 있는 자리니 `_NONFOOD_CTG` 한 줄이다.

외부 브랜드 — **그대로 올린다. 거르지 않는다.** 159건 중 hy 자사 상품은 8건 안팎이고
(쿠퍼스·슈퍼100·하루야채·하이브루·브이푸드·발휘) 나머지는 전부 입점·수입 브랜드다.
  ① 등록하는 브랜드명이 `hy프레딧` — **제조사 이름이 아니라 파는 곳 이름**이다.
     카드가 "hy 가 만들었다"고 말하지 않는다. 1단 분류 `가공식품` 도
     `notes/TAXONOMY.md` §3 이 못박았듯 '누가 만들었나'가 아니라 '무엇이냐' 축이다.
  ② 이 레포는 CU·세븐일레븐·이마트24·GS25 를 이미 같은 계약으로 다룬다 —
     남이 만든 상품을 '그 채널의 신상품'으로 올린다. 직영몰도 같은 자리다.
  ③ 걸러내면 남는 게 8건이고, **냉동식품 25건이 전부 사라진다**(아래). 이 어댑터를
     붙이는 이유 자체가 없어진다.
⚠️ 다만 브랜드 축이 거친 건 사실이다. '청년떡집 크림떡'을 찾는 사람이 `hy프레딧`
   아래에서 찾지는 않는다. 상품명에 제조사가 그대로 들어 있어 검색으로는 닿는다.

분류(`base.BRANDS`) — `냉동식품` 으로 제안한다. 신제품 159건의 분류 분포 실측:

    생활 · 주방용품 52 | 식재료 · 반찬 43 | 베이커리 · 간식 35 | 뷰티 14
    달걀 · 정육 · 수산 14 | 건강 · 기능식품 13 | 발효유 · 유제품 11
    커피 · 차 5 | 반려동물 5 | 생수 · 주스 · 음료 2 | 국 · 탕 · 밀키트 0

⚠️ **`음료` 는 여기서 안 나온다 — 2건뿐이다.** 조사 문서가 hy 를 음료 축 후보로 올렸고
`notes/TAXONOMY.md` §7-2 도 그렇게 적었는데, 실제로 열어 보니 음료는 롯데칠성 몫이다.
대신 상품명이 `[택배배송/냉동]` 으로 시작하는 **냉동식품이 25건**이고(브랜드가 직접
붙인 표기라 셀 수 있다) 이게 수집원이 없던 바로 그 축이다. 식품 98건 중 25건이라
전부를 설명하지는 못한다 — 브랜드 단위 세부분류의 구조적 한계다(오뚜기=`라면` 과 같다).
`냉동식품` 은 `collect.SUBS` 에 있다(TAXONOMY §7-2 가 예고한 대로 들어갔다).

⚠️ **화면 40칸 경고.** `collect.PER_BRAND` 가 40인데 위 실측대로면 합류 첫날
식품 64건이 신상 판정을 받는다. 날짜(60일 창)와 비식품 분류로 159→64 까지는 좁혔지만
그래도 상한을 넘는다. 더 좁힐 브랜드 근거가 없다 — `bdgCnn` 배지는 159건 중
`N` 6건·`B` 1건뿐이라 탭 안에서 의미가 없고, 입점/직배송을 가르는 `prdSpCd`
(`20` 직배송 75 / `10` 택배 84)로 좁히면 **냉동식품 25건이 전부 택배 쪽이라 같이 날아간다.**
남은 손잡이는 `collect.PER_BRAND` 쪽이다. 팔도가 이미 상한을 다 쓰고 있어 둘째가 된다.

참고로 **7월분 30건은 날짜 게이트에서 자동으로 떨어진다**(WINDOW 60일, cutoff 2026-08-02).
is_fresh 통과 129건 = 9월 83 + 8월 46. 위 '보관함인가' 질문이 어느 쪽으로 판명나든
`released_at` 이 아니라 `uploaded_at` 에 넣었기 때문에 화면에는 최근 두 달치만 나간다.

robots: `m.fredit.co.kr/robots.txt` → 200 `text/plain` 263B. `User-agent: *` 에
        Disallow 6줄(로그인·비회원주문조회·검색결과·장바구니 3종)뿐이다.
        `/api/`·`/product/` 는 금지가 아니다. `Crawl-delay` 없음 — 그래도
        한 번에 14요청이라 `DELAY` 를 둔다.
약관: 확인하지 못했다(SPA 라 초기 HTML 에 약관 본문이 없다). `notes/CRAWLING-POLICY.md` §4
      와 같은 상태다. 보수적으로 간격을 두는 것으로 대신한다.
"""
import json
import re
import time
from datetime import datetime, timedelta, timezone

from . import base
from .base import Item

BRAND = "hy프레딧"
SITE = "https://m.fredit.co.kr"
API = SITE + "/api/freditProduct/v01"
NEW_CTG = "C10000001001"                 # '신제품' 탭. <title>신제품 | hy프레딧</title>
LIST_URL = "https://m.fredit.co.kr/product/main-tab-menu?keyword=main&ctgId=" + NEW_CTG
DETAIL = SITE + "/product/detail?prdId="

PAGE_SIZE = 100    # pageSize=500 도 먹지만, 서버가 조용히 상한을 걸어도 버티게 돌린다
_OFFSET_STEP = 20  # 서버가 쓰는 offset 단위. pageSize 와 무관하게 고정이다(docstring).
_STRIDE = PAGE_SIZE // _OFFSET_STEP      # currentPage 를 이만큼씩 올려야 안 겹친다
MAX_PAGES = 20     # 폭주 방지. 현재 159건 = 2페이지.
ORDER = "20"       # rest-api-header 의 prdOrderGbn. 화면이 보내는 값 그대로다.
DELAY = 0.3        # Crawl-delay 가 없다. 약관을 못 읽었으니 우리가 보수적으로 둔다.

# 비식품 축. 브랜드가 신제품 탭 아래에 직접 걸어 둔 분류 이름이다.
# 이름 단어(NONFOOD_WORDS)보다 정확해서 여기서 끝낸다 — 모듈 docstring 참고.
# '반려동물'은 먹는 것이긴 한데 사람이 먹는 게 아니라 같이 뺀다.
_NONFOOD_CTG = {"뷰티", "생활 · 주방용품", "반려동물"}

# 이미지 경로의 업로드 타임스탬프 두 꼴. released_at 이 아니라 uploaded_at 이다.
_IMG_DAY = re.compile(r"/prdimg/(\d{4})(\d{2})(\d{2})/")
_IMG_EPOCH = re.compile(r"_thumb_(\d{13})\.")
# 한국 사이트가 찍은 시각이다. 러너가 UTC 면 fromtimestamp 가 하루를 당겨서
# 저녁 업로드분이 전날로 찍힌다. 그래서 KST 로 고정한다.
_KST = timezone(timedelta(hours=9))


def _hdr(page: int) -> dict:
    """페이징은 쿼리가 아니라 이 헤더다. 빠뜨리면 200 OK 에 0건이 온다."""
    return {"rest-api-header": json.dumps(
        {"currentPage": page, "pageSize": PAGE_SIZE, "prdOrderGbn": ORDER},
        ensure_ascii=False)}


def _body(client, path: str, page: int = 1) -> tuple:
    """한 페이지. (행 목록, 전체건수). 응답이 성공코드가 아니면 그대로 올린다."""
    r = client.get(API + path, headers=_hdr(page))
    r.raise_for_status()
    time.sleep(DELAY)
    j = r.json()
    if j.get("resultCode") != "0000":
        raise RuntimeError(f"{path} 응답코드 {j.get('resultCode')} "
                           f"{j.get('resultMessage')!r} — API 계약이 바뀌었다")
    return j.get("body") or [], (j.get("header") or {}).get("totalRecords", 0)


def _page(client, path: str) -> list:
    """전량. 받은 건수가 서버가 말한 totalRecords 와 다르면 예외를 던진다.

    rest-api-header 를 서버가 무시하게 되면 totalRecords 0 · body [] 가 200 으로
    온다. 그게 이 레포가 제일 여러 번 당한 '조용한 0건'이라 건수를 직접 검산한다.
    """
    rows, total = _body(client, path)
    for n in range(1, MAX_PAGES):
        if len(rows) >= total:
            break
        more, _ = _body(client, path, 1 + n * _STRIDE)
        if not more:
            break
        rows += more
    if len(rows) != total:
        raise RuntimeError(f"{path} 건수 불일치 — 서버 {total}건 / 받은 {len(rows)}건. "
                           f"페이징(rest-api-header)이 안 먹고 있다")
    return rows


def _categories(client) -> dict:
    """prdId → 브랜드가 건 분류 이름들. 비식품 판정의 근거다."""
    r = client.get(f"{API}/mainTopMenuProductPageInfo/{NEW_CTG}", headers=_hdr(1))
    r.raise_for_status()
    time.sleep(DELAY)
    subs = ((r.json().get("body") or {}).get("subCategorys")) or []
    if not subs:
        raise RuntimeError("신제품 탭의 하위 분류가 0개 — 비식품을 가를 근거가 사라졌다")

    out: dict = {}
    for s in subs:
        cid, name = s.get("ctgId"), (s.get("ctgNm") or "").strip()
        if not cid or not name:
            continue
        for row in _page(client, f"/tabMenuProducts/{NEW_CTG}/{cid}"):
            out.setdefault(row["prdId"], set()).add(name)
    return out


def _uploaded_at(img: str) -> str:
    """이미지 경로의 업로드 시각. 출시일이 아니므로 released_at 에는 넣지 않는다."""
    m = _IMG_DAY.search(img)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = _IMG_EPOCH.search(img)
    if m:
        return datetime.fromtimestamp(int(m.group(1)) / 1000, _KST).strftime("%Y-%m-%d")
    return ""


def fetch() -> list[Item]:
    headers = {"Accept": "application/json", "Referer": LIST_URL}
    with base.client(headers=headers) as c:
        rows = _page(c, f"/tabMenuProducts/{NEW_CTG}")
        if not rows:
            raise RuntimeError("신제품 0건 — 파서가 깨졌을 가능성")
        cats = _categories(c)

    # 분류가 날아가면 치약·찜기가 조용히 식품 목록으로 올라간다. 실측 커버리지는
    # 159건 중 158건(99%)이라, 절반 밑으로 떨어지면 응답 구조가 바뀐 것이다.
    if len(cats) * 2 < len(rows):
        raise RuntimeError(f"분류를 받은 상품이 {len(cats)}/{len(rows)}건뿐 — "
                           f"비식품 판정이 무력해진다")

    items: list[Item] = []
    dated = 0
    for row in rows:
        name = " ".join((row.get("prdNm") or "").split())
        prd = row.get("prdId")
        if not name or not prd:
            continue
        mine = cats.get(prd, set())
        img = row.get("webPrdImageUrl") or ""
        day = _uploaded_at(row.get("prdImgFlNm") or img)
        dated += bool(day)
        items.append(Item(
            brand=BRAND,
            name=name,
            image=img,          # s3image.fredit.co.kr 절대주소. 인코딩은 web/seo.py 몫이다
            # 브랜드가 건 분류를 그대로 남긴다. 한 상품이 두 분류에 걸리는 게
            # 159건 중 36건이라 ' / ' 로 잇는다. 쓰이는 곳은 상세 페이지 '카테고리'
            # 줄과 JSON-LD 뿐이고(web/pages.py·web/seo.py), 분기에는 안 쓰인다.
            # ⚠️ 이어 붙인 값이라 base.NONFOOD_CATEGORIES 의 정확일치에는 안 걸린다.
            #    비식품 판정은 아래 nonfood 가 직접 하므로 지금은 무해하지만,
            #    다른 코드가 category 로 분기하게 되면 여기부터 봐야 한다.
            category=" / ".join(sorted(mine)),
            uploaded_at=day,
            released_at="",     # 어디에도 없다. 모듈 docstring 참고.
            # 브랜드가 '신제품' 탭에 올려놓은 것이다. 그 탭이 3개월 롤링 창이라
            # (영구 보관함이 아니라) 배지를 그대로 믿는다. 60일 컷은 uploaded_at 이 한다.
            is_new=True,
            # 분류가 전부 비식품 축일 때만 비식품이다. 식품 분류를 하나라도
            # 가지면 식품으로 둔다(실측 혼재 0건).
            nonfood=bool(mine) and mine <= _NONFOOD_CTG,
            url=DETAIL + str(prd),
        ))

    # 날짜가 사라지면 is_fresh 가 전건을 통과시켜 3개월치가 영구히 신상으로 뜬다.
    # 브레댄코에서 실제로 난 사고라 조용히 넘기지 않는다.
    if dated * 2 < len(items):
        raise RuntimeError(f"이미지 타임스탬프를 {dated}/{len(items)}건에서만 읽었다 — "
                           f"경로 규칙이 바뀌었다")
    return items
