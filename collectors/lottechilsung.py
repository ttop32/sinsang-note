"""롯데칠성음료 — 회사 홈페이지의 '신제품' 전용 페이지 한 장.

`/kor/product/newprdt/list.do` 가 SSR 이고 페이지네이션이 없다. 요청 1회로 끝난다.
2026-10-01 실측 (원본 78,906B, `<title>신제품 | 롯데칠성음료</title>`):

    <div class="pdListD"><div class="list">
        <p class="tit">펩시 엑스트라 피즈</p>
        <p class="txt"><p class="txt">오래 즐기고 싶은 너만의 짜릿함</p></p>
        <p class="img"><img src="/image/2026/9/202609220615531610.png" alt="" /></p>
        <p class="bg" style="background:#184BC2"></p>
        <a href="javascript:" data-url="https://mall.lottechilsung.co.kr/product-detail?productNo=133584523"
           class="btn" data-seq="340">롯데칠성몰에서 구매하기</a>
    </div> … 18건</div>

⚠️ `p.txt` 가 **중첩**돼 있다. HTML 은 p 안에 p 를 못 넣어서 파서가 앞을 닫아버리고,
   `css("p.txt")` 의 첫 노드가 **빈 문자열**로 나온다. 비지 않은 첫 노드를 써야 한다.

상품 주소는 `a.btn` 의 `href` 가 아니라 **`data-url`** 에 있다(href 는 `javascript:`).
롯데칠성몰 상품 상세로 간다. 2026-10-01 에 4건을 브라우저로 직접 열어 확인했다 —
productNo 133584523/133697374/132122614/124100599 전부 해당 상품 페이지가 뜬다.
(몰은 CSR 이라 HTML 만 받으면 껍데기 12KB 다. 우리는 요청하지 않고 링크만 건다.)
⚠️ 몰 상품은 묶음 SKU 다(`[펩시콜라] 엑스트라 피즈 355ml(24캔)`). 상품은 맞지만
   낱개 소개 페이지는 아니다. 이 사이트에 낱개 상세 주소라는 게 없다.

────────────────────────────────────────────────────────────────────────
TLS — 서버가 중간인증서를 빠뜨린다. `verify=False` 가 아니라 **보충**으로 푼다.
────────────────────────────────────────────────────────────────────────
`openssl s_client -showcerts` 로 센 결과(2026-10-01):

    리프      CN=*.lottechilsung.co.kr
              issuer = GlobalSign GCC R3 DV TLS CA 2020   ← 실제 발급자
    서버가 보낸 체인 1번  GlobalSign Domain Validation CA - SHA256 - G2   ← 엉뚱한 놈
    서버가 보낸 체인 2번  GlobalSign Root CA
    Verify return code: 21 (unable to verify the first certificate)

리프의 AIA 가 가리키는 진짜 중간 인증서를 받아
`collectors/certs/globalsign-gcc-r3-dv-tls-ca-2020.pem` 에 넣고, certifi 루트 번들에
`load_verify_locations()` 로 **더해서** 쓴다. 출처·만료일은 그 파일 머리말에 적어뒀다.
docs/CRAWLING-POLICY.md §6-1 (2026-10-01 운영자 결정)이 허용한 경로다.

검증은 **켜진 채로 돈다.** 보충한 컨텍스트로 실측:
    company.lottechilsung.co.kr   200   (보충 전에는 CERTIFICATE_VERIFY_FAILED)
    wrong.host.badssl.com         실패  Hostname mismatch
    self-signed.badssl.com        실패  self-signed certificate
즉 호스트명·서명 검증이 그대로 살아 있다. `http://` 우회는 쓸 수 없다 —
이 호스트는 http 를 443 으로 302 리다이렉트한다(docs/CANDIDATES-DIRECT2.md §3-1).

컨텍스트를 `base.client(verify=...)` 로 넘긴다. httpx 는 verify 에 경로 말고
`ssl.SSLContext` 도 받는다. 번들 경로를 넘기려면 certifi 전체를 어딘가에 복사해
우리 pem 을 이어붙인 임시 파일을 만들어야 하는데, 그건 루트 번들이 두 벌이 되는 길이라
하지 않았다. 정책 §6-1 이 쓴 표현(`SSLContext` 에 `load_verify_locations()`)도 이쪽이다.
`base.client()` 를 우회해 httpx 를 직접 만들지는 않는다 — verify 를 transport 에
넘기는 그 처리가 base 에 있다.
ℹ️ `certifi` 는 requirements.txt 에 직접 적혀 있지 않지만 httpx 의 필수 의존이라
   항상 설치된다. 이 어댑터가 그걸 import 하는 유일한 곳이다.

────────────────────────────────────────────────────────────────────────
날짜 — 이미지 파일명 타임스탬프를 쓴다. 단 같은 날 몰린 건 출시일로 안 올린다.
────────────────────────────────────────────────────────────────────────
이 사이트가 주는 날짜는 이미지 경로뿐이다: `/image/2026/9/202609220615531610.png`
→ `YYYY/M/` 디렉터리 + 파일명 `YYYYMMDDHHMMSS` + 4자리. 둘이 어긋나면 버린다.

**믿을 만하다고 본 근거** — 18건의 이미지 시각이 `data-seq`(등록 일련번호) 내림차순과
**18/18 완전히 일치한다.** 초 단위까지 역전이 하나도 없다:

    seq 340 → 2026-09-22 06:15   seq 326 → 2026-04-13 05:38
    seq 339 → 2026-09-10 11:42   seq 324 → 2026-04-13 05:35
    seq 338 → 2026-09-10 11:40   …
    seq 336 → 2026-05-08 06:15   seq 312 → 2025-11-26 04:07
    seq 334 → 2026-05-08 06:12   seq 310 → 2025-11-17 03:32
    seq 332 → 2026-05-04 06:19   seq 308 → 2025-11-17 01:45

즉 **이미지는 이 목록에 등록할 때 올라간다.** mega.py 가 거부한 '일괄 재업로드'
(173건 중 81건이 한 달에 뭉침)의 흔적이 여기엔 없다. 그래서 날짜로 쓴다.
반대로 재업로드가 일어나면 이 정렬이 깨지므로 `_trust_dates()` 가 그걸 보고
released_at 을 통째로 비운다(아래).

**그래도 released_at 에 전부 올리지는 않는다.** 2026-04-13 하루에 7건이 05:09~05:38,
29분 안에 몰려 있다. 7종을 같은 날 출시한 게 아니라 페이지를 한 번에 채운 편집
세션이다. maker_lottewellfood.py 와 같은 규칙을 쓴다 — **같은 날짜가 BULK 건 이상이면
그 날은 uploaded_at 으로만 쓰고 released_at 은 비운다.** 현재 7건이 여기 걸리고
나머지 11건(61%)은 released_at 이 찬다.

────────────────────────────────────────────────────────────────────────
is_new — True 로 올리되 **날짜 없이는 올리지 않는다**
────────────────────────────────────────────────────────────────────────
브랜드가 직접 '신제품' 이라고 모아둔 페이지라 is_new=True 의 근거는 충분하다.
**그런데 이 페이지는 이번 달 신상이 아니라 보관함이다.** 18건이 2025-11-17 ~
2026-09-22, 열한 달치다. 전부 is_new=True 로 밀면 작년 11월 상품이 오늘 신상으로
뜬다. 막아주는 건 uploaded_at 이다 — `collect.is_fresh()` 는 is_new=True 라도
날짜가 있으면 WINDOW(60일) 밖을 걸러낸다. 2026-10-01 기준 통과는 3건이다.

⚠️ 거꾸로 **날짜를 못 뽑은 건에 is_new=True 를 주면 영구히 신상 칸에 남는다.**
   `is_fresh()` 가 '날짜 없는 is_new=True' 를 무조건 True 로 돌려주기 때문이고,
   브레댄코가 실제로 그 사고를 냈다(bakery_breadnco.py 머리말). 그래서 이미지
   타임스탬프를 못 읽은 건은 is_new 를 None 으로 떨어뜨려 diff 판정에 맡긴다.

0건·셀렉터 파손은 예외로 드러낸다(gs25.py 와 같은 방식). 조용한 0건을 만들지 않는다.

술: 이 회사는 주류도 만들고 사이트에 `/kor/product/liquor/…` 섹션이 따로 있다.
    다만 이 신제품 페이지 18건에는 주류가 0건이다(base.is_alcohol 로 재봐도 0건).
    주류가 섞여 들어오면 base.is_alcohol 이 받는다. 이름 거르는 규칙을 여기서
    새로 만들지 않았다 — 지금 데이터에 근거가 없다.

robots: https://company.lottechilsung.co.kr/robots.txt → 200 text/plain 291B.
        Group 1 Googlebot 에 5개 Disallow, Group 2 Yeti Allow:/, **Group 3 `*` Allow: /**.
        우리 UA 는 Group 3 이고 수집 경로는 어느 Disallow 에도 없다.
        (Googlebot 금지 목록의 `/kor/company/news/list.do` 는 우리가 안 쓰는 보도자료다.)
약관: /kor/util/terms/contentsid/567/index.do — 수집·복제 금지 조항을 찾지 못했다.
"""
import pathlib
import re
import ssl
from collections import Counter

import certifi
from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "롯데칠성음료"
SITE = "https://company.lottechilsung.co.kr"
LIST = SITE + "/kor/product/newprdt/list.do"

# 서버가 빠뜨린 중간 인증서. 출처·만료일은 파일 머리말 참고.
CA_EXTRA = pathlib.Path(__file__).parent / "certs" / "globalsign-gcc-r3-dv-tls-ca-2020.pem"

BULK = 4        # 같은 날짜가 이만큼 몰리면 일괄 등록으로 보고 released_at 을 비운다
                # (maker_lottewellfood.py 와 같은 값·같은 뜻)

# /image/2026/9/202609220615531610.png — 디렉터리 연·월과 파일명 앞 8자리를 같이 본다.
_IMG_DATE = re.compile(r"/image/(\d{4})/(\d{1,2})/(\d{4})(\d{2})(\d{2})(\d{6})\d*\.")


def _text(node, sel) -> str:
    """선택자에 걸린 것 중 **비지 않은 첫** 노드. p.txt 가 중첩이라 첫 노드가 빈다."""
    for n in node.css(sel):
        t = " ".join(n.text().split())
        if t:
            return t
    return ""


def _stamp(img_url: str) -> str:
    """이미지 경로의 업로드 시각 → 'YYYY-MM-DD HH:MM:SS'. 못 읽으면 빈 문자열.

    디렉터리(/2026/9/)와 파일명 앞 8자리(20260922)의 연·월이 어긋나면 버린다.
    규칙이 바뀐 걸 날짜인 척 통과시키는 게 제일 나쁘다.
    """
    m = _IMG_DATE.search(img_url or "")
    if not m:
        return ""
    dy, dm, y, mo, d, hms = m.groups()
    if (int(dy), int(dm)) != (int(y), int(mo)):
        return ""
    if not (1 <= int(mo) <= 12 and 1 <= int(d) <= 31):
        return ""
    return f"{y}-{mo}-{d} {hms[:2]}:{hms[2:4]}:{hms[4:]}"


def _ssl_context() -> ssl.SSLContext:
    """certifi 루트에 빠진 중간 인증서 한 장을 **더한** 컨텍스트.

    검증을 끄는 게 아니다. check_hostname·verify_mode 는 기본값 그대로다.
    """
    ctx = ssl.create_default_context(cafile=certifi.where())
    if not CA_EXTRA.exists():
        raise FileNotFoundError(
            f"중간 인증서가 없다: {CA_EXTRA} — 이게 없으면 이 사이트는 "
            f"unable to get local issuer certificate 로 붙지 않는다")
    ctx.load_verify_locations(cafile=str(CA_EXTRA))
    return ctx


def _rows(html: str) -> list:
    cards = HTMLParser(html).css(".pdListD > .list")
    if not cards:
        raise ValueError(
            f"롯데칠성 신제품 카드 0건 — '.pdListD > .list' 가 안 걸린다. "
            f"본문 {len(html)}B, 'pdListD' 포함={'pdListD' in html} "
            f"'신제품' 포함={'신제품' in html} — 마크업이 바뀌었는지 확인하라")
    out = []
    for card in cards:
        img = card.css_first("p.img img")
        btn = card.css_first("a.btn")
        src = (img.attributes.get("src", "") or "").strip() if img else ""
        out.append({
            "name": _text(card, "p.tit"),
            "desc": _text(card, "p.txt"),
            # 호스트만 붙이고 그대로 둔다. quote() 를 걸면 이미 인코딩된 URL 이
            # 두 번 인코딩돼 %2520 사고가 재발한다. 규격 위반 문자는 web/seo.py 의
            # _ext_url() 이 한 번만 처리한다(한글 파일명이 들어와도 거기서 받는다).
            "image": (src if src.startswith("http") else SITE + src) if src else "",
            "stamp": _stamp(src),
            # href 는 'javascript:' 다. 상품 주소는 data-url 에 있다.
            "url": (btn.attributes.get("data-url", "") or "").strip() if btn else "",
            # 등록 일련번호. 날짜를 믿어도 되는지 재는 데만 쓴다(_trust_dates).
            "seq": (btn.attributes.get("data-seq", "") or "").strip() if btn else "",
        })
    named = [r for r in out if r["name"]]
    if not named:
        raise ValueError(
            f"롯데칠성 카드 {len(cards)}건은 걸렸는데 'p.tit' 상품명이 0건이다 — "
            f"상품명 셀렉터가 바뀌었는지 확인하라")
    if not any(r["stamp"] for r in named):
        raise ValueError(
            f"롯데칠성 {len(named)}건 전부 이미지 타임스탬프를 못 읽었다 "
            f"(예: {named[0]['image']!r}) — /image/YYYY/M/YYYYMMDDHHMMSS… 규칙이 "
            f"바뀌었다. 이 어댑터의 날짜는 여기서만 나온다")
    return named


def _trust_dates(rows: list) -> bool:
    """이미지 시각이 등록 일련번호(data-seq) 순서와 맞물려 있는가.

    맞물려 있으면 '등록할 때 올린 이미지'다. 어긋나면 일괄 재업로드를 의심한다 —
    mega.py 가 173건 중 81건이 한 달에 뭉친 걸 보고 날짜를 버린 그 경우다.
    2026-10-01 실측 18/18 일치.
    """
    pairs = [(int(r["seq"]), r["stamp"]) for r in rows if r["seq"].isdigit() and r["stamp"]]
    if len(pairs) < 2:
        return False
    pairs.sort(key=lambda p: -p[0])          # 일련번호 내림차순 = 최신순
    stamps = [s for _, s in pairs]
    return all(a >= b for a, b in zip(stamps, stamps[1:]))


def fetch() -> list[Item]:
    with base.client(verify=_ssl_context()) as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()
    rows = _rows(r.text)

    trusted = _trust_dates(rows)
    if not trusted:
        print("  롯데칠성 이미지 시각이 등록순과 어긋난다 — released_at 을 비운다")
    # 같은 날에 몰린 건 편집 세션이다. 그 날짜는 출시일로 올리지 않는다.
    days = Counter(r["stamp"][:10] for r in rows if r["stamp"])
    bulk = {d for d, n in days.items() if n >= BULK}

    items: list[Item] = []
    seen = set()
    for row in rows:
        day = row["stamp"][:10]
        solo = bool(day) and day not in bulk
        it = Item(
            brand=BRAND,
            name=row["name"],
            desc=row["desc"],
            image=row["image"],
            category="음료",
            uploaded_at=day,
            released_at=day if (solo and trusted) else "",
            # 브랜드가 직접 모아둔 '신제품' 목록이다. 다만 열한 달치가 쌓인
            # 보관함이라, 날짜가 없으면 True 로 올리지 않는다 — 날짜 없는
            # is_new=True 는 is_fresh() 에서 영구 신상이 된다(브레댄코 사고).
            is_new=True if day else None,
            url=row["url"],
        )
        if it.key not in seen:
            seen.add(it.key)
            items.append(it)
    return items
