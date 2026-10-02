"""노랑통닭.

공정위 등록 가맹점 751개로 치킨 업종 9위다.

────────────────────────────────────────────────────────────────────────
🔴 도메인부터 틀리기 쉽다 — `.com` 이 아니라 `.co.kr` 이다
────────────────────────────────────────────────────────────────────────
2026-10-02 실측. notes/CRAWLING-POLICY.md §6-5('도메인 확인을 먼저 한다')가
그대로 걸린 사례다.

    norangtongdak.com     → 115.84.183.200, 인증서 CN=183200.nasanivietnam.com
                            (SAN 에 노랑통닭 도메인이 **없다**). http 로 열면
                            `<html>webserver is functioning normally</html>`
                            47바이트, 나머지 경로는 전부 404.
                            = 공유호스팅 빈 껍데기다. 노랑통닭이 아니다.
    norangtongdak.co.kr   → 121.78.246.190, 인증서 CN=norangtongdak.co.kr
                            (SAN: norangtongdak.co.kr, www.…). 진짜 사이트.

🔴 `.com` 을 치면 '수집 불가' 로 잘못 판정하게 된다. **`.co.kr` 을 쓴다.**

⚠️ `.co.kr` 의 apex(`/`)도 목록이 아니다. '브랜드 홈페이지 / 창업 홈페이지' 두 장
   짜리 스플래시고, 실제 사이트는 **`/main.html`** 아래다. apex 를 폴백 링크로
   쓰지 마라.

────────────────────────────────────────────────────────────────────────
TLS — 구형 DH 파라미터. 검증을 끄지 않고 **암호군 기준만** 낮춘다.
────────────────────────────────────────────────────────────────────────
기본 컨텍스트로는 핸드셰이크 자체가 안 된다.

    httpx 기본        → ConnectError [SSL: DH_KEY_TOO_SMALL] dh key too small

서버가 1024비트급 DH 파라미터를 쓴다. OpenSSS 3 의 기본 보안수준(SECLEVEL=2)이
그걸 거절하는 것이고, **인증서는 멀쩡하다**(위 SAN 확인). 그래서
`ctx.set_ciphers("DEFAULT@SECLEVEL=0")` 로 **암호군 기준만** 내리고
호스트명·서명·만료 검증은 전부 켠 채로 둔다.

🔴 `verify=False` 는 쓰지 않는다. notes/CRAWLING-POLICY.md §6-1 이 명시적으로
   금지한다. §6-1 은 "중간인증서 보충은 다른 이야기(허용)" 라고 적어 뒀는데,
   이건 보충이 아니라 **완화**라 한 걸음 더 나간다. 그래도 같은 기준으로 판단한다 —
   끄는 게 아니라 **무엇을 확인할지는 그대로 두고 무엇을 받아줄지만 넓히는** 것이다.
   중간자가 응답을 바꾸면 여전히 서명·호스트명에서 걸린다. 선례는
   `collectors/chicken_toreore.py`(중간인증서 보충)·`collectors/lottechilsung.py` 다.
   `http://` 폴백도 못 쓴다 — 이 호스트는 평문 경로가 없다.

보충한 컨텍스트로 실측했고 검증은 켜진 채 돈다(2026-10-02):

    norangtongdak.co.kr        200
    wrong.host.badssl.com      실패  Hostname mismatch
    self-signed.badssl.com     실패  self-signed certificate
    expired.badssl.com         실패  certificate has expired

⚠️ 이미지도 같은 호스트라 같은 컨텍스트가 그대로 적용된다.

────────────────────────────────────────────────────────────────────────
목록 — `/menu/chicken.html` 이 아니다
────────────────────────────────────────────────────────────────────────
    /menu/chicken_list.html   치킨 20건
    /menu/side.html           사이드 27건                     → 합계 47건
    /menu/best.html           **0건.** 베스트 탭은 마크업이 아예 달라서
                              `ul.c_list` 가 없다. 실린 상품도 치킨·사이드의
                              부분집합이라 얻을 게 없다. 뺀다.
    /menu/chicken.html        200 이지만 상품 목록이 아니다(소개 면). 쓰지 마라.

⚠️ 상품 이미지가 `<img src>` 가 **아니다.** `span.img_dummy` 의 인라인
   `style="background:url(/pds/product/72_s?1784162256) …"` 안에 들어 있고
   `<img>` 태그에는 투명 더미(`c_dummy.png`)가 박혀 있다. img 를 집으면 전 상품이
   같은 더미 그림이 된다. **style 속성에서 뽑아야 한다.**
   selectolax 로 `ul.c_list li a` 까지 내려가고 style 속성 **안에서만** 정규식을
   쓴다. 문서 전체에 거는 통짜 정규식보다 깨질 자리가 적다.

⚠️ 이미지 응답 헤더가 `Content-Type: text/plain` 이다(서버 설정 오류). 바이트는
   진짜 이미지다. **content-type 으로 거르지 마라** — 47장 전부 그렇다.

────────────────────────────────────────────────────────────────────────
🔴 신호 = 이미지 URL 쿼리스트링이 상품별 업로드 시각(유닉스초)이다
────────────────────────────────────────────────────────────────────────
`/pds/product/72_s?1784162256` 의 `1784162256` 은 캐시버스터가 아니다.
네네치킨의 `?v=20241011`(전 상품 동일)과 정반대로 **상품마다 다르다.**

2026-10-02 **전 47건** 에 대고 HEAD Last-Modified 와 대조했다. **47/47 일치**다:

    대파 간장 치킨          1784162256 → 2026-07-16   LM 2026-07-16  일치
    우도 땅콩 치킨          1766018712 → 2025-12-18   LM 2025-12-18  일치
    우도 땅콩 치킨 반반      1772499271 → 2026-03-03   LM 2026-03-03  일치
    갈릭 인 더 딥          1729124178 → 2024-10-17   LM 2024-10-17  일치
    칼칼한 청양 치킨        1682589010 → 2023-04-27   LM 2023-04-27  일치
    뿌리노랑 치킨          1649307820 → 2022-04-07   LM 2022-04-07  일치
    모짜 체다 치즈볼(5PCS)  1784162010 → 2026-07-16   LM 2026-07-16  일치
    맵싸한 똥집 감자튀김     1784161936 → 2026-07-16   LM 2026-07-16  일치
    … (나머지 39건도 전부 일치. 불일치 0)

2022-04 부터 2026-07 까지 4년에 걸쳐 흩어져 있다. 일괄 재업로드가 아니다.
그래서 **HEAD 를 안 보낸다** — 쿼리스트링에서 바로 읽는다. 썸네일 경로에서
날짜를 읽는 `collectors/chicken_goobne.py` 와 같은 처분이고, 요청 47번을 아낀다.

🔴 어디까지나 **이미지 업로드 시각**이다. 브랜드가 '출시일' 이라고 말해준 값이
   아니므로 `released_at` 이 아니라 `uploaded_at` 이다. `released_at` 은 끝까지 빈다.
   날짜는 KST(Asia/Seoul)로 읽는다 — 한국 사이트의 업로드 시각이다. 2026-10-02
   실측에서는 UTC 로 읽어도 47건 전부 같은 날짜였다.

🔴 **`is_new` 는 전건 None 이다.** NEW 배지도 '신메뉴' 탭도 없다. 목록이 마침
   최신순으로 보이지만 **순서는 날짜가 아니다** — 번호나 순서를 날짜로 환산하지 마라.
   이 브랜드는 `uploaded_at` 날짜 창과 collect.py 의 전날 대비 diff 로만 잡힌다.

🔴 타임스탬프가 반 넘게 안 붙으면 터뜨린다. 마크업이 `<img src>` 로 바뀌거나
   쿼리스트링을 떼면 건수(47)는 그대로인 채 날짜만 사라져서, collect.py 의
   0건 가드도 FLOOR 도 통과하고 "노랑통닭은 신제품이 없다" 가 조용히 굳는다.

────────────────────────────────────────────────────────────────────────
나머지 판단
────────────────────────────────────────────────────────────────────────
url   카드 href 가 `chicken_view.html?mode=VIEW_FORM&p_no=72&…` / 사이드는
      `side_view.html?…` 로 **페이지 기준 상대경로**다. `/menu/` 를 앞에 붙인다.
promo 할인·행사 표시가 사이트에 없다. 전건 False 다. 세트에는 promo 를 찍지
      않는다 — '떡볶이 모둠 튀김 세트' 는 rules.drop_sets() 가 이름으로 본다.
image 전부 https(같은 호스트)라 base.derive() 의 http 폐기에 안 걸린다.
가격·열량은 목록에 없다.
robots: https://norangtongdak.co.kr/robots.txt 는 200 이고 `User-agent: * /
        Allow: /` 뿐이다(2026-10-02 실측). 전체 허용.
"""
import re
import ssl
import time
from datetime import datetime, timedelta, timezone

import certifi
from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "노랑통닭"
SITE = "https://norangtongdak.co.kr"   # ⚠️ .com 은 남의 빈 호스트다(docstring 참고)
MENU = SITE + "/menu/"

# (경로, 화면상 분류). best.html 은 마크업이 달라 0건이라 뺐다 — docstring 참고.
LISTS = [
    ("chicken_list.html", "치킨"),
    ("side.html", "사이드"),
]

DELAY = 0.5      # 목록 요청 간격(초). 요청이 2번뿐이다.
MAX_ITEMS = 200  # 폭주 방지. 현재 47건.

KST = timezone(timedelta(hours=9))

# `background:url(/pds/product/72_s?1784162256)` 에서 (경로, 유닉스초).
# style 속성 **안에서만** 돌린다. 문서 전체에 거는 통짜 정규식은 쓰지 않는다.
_BG = re.compile(r"url\(\s*(/pds/product/\d+_s\?(\d+))\s*\)")


def _ssl_context() -> ssl.SSLContext:
    """certifi 루트는 그대로 두고 **암호군 기준만** 낮춘 컨텍스트.

    서버 DH 파라미터가 1024비트급이라 OpenSSL 기본 SECLEVEL 로는
    DH_KEY_TOO_SMALL 로 핸드셰이크가 끊긴다. 검증을 끄는 게 아니다 —
    check_hostname·verify_mode 는 기본값 그대로다(docstring 실측 참고).
    """
    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.set_ciphers("DEFAULT@SECLEVEL=0")
    return ctx


def _text(node, sel: str) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _image_and_date(a) -> tuple:
    """`span.img_dummy` 의 인라인 배경에서 (이미지 주소, 업로드일)을 뽑는다.

    `<img src>` 는 투명 더미라 쓸 수 없다. 쿼리스트링은 캐시버스터가 아니라
    상품별 업로드 시각이다 — 47/47 이 Last-Modified 와 일치했다(docstring).
    """
    span = a.css_first("span.img_dummy")
    m = _BG.search(span.attributes.get("style", "") or "") if span else None
    if not m:
        return "", ""
    try:
        day = datetime.fromtimestamp(int(m.group(2)), KST).date().isoformat()
    except (OverflowError, OSError, ValueError):
        day = ""        # 형식이 바뀌면 틀린 날짜를 쓰느니 비운다
    return SITE + m.group(1), day


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()

    with base.client(verify=_ssl_context()) as c:
        for path, category in LISTS:
            time.sleep(DELAY)
            r = base.retry(lambda p=path: c.get(MENU + p))
            r.raise_for_status()
            cards = HTMLParser(r.text).css("ul.c_list li a")
            # 한쪽 면만 깨져도 건수는 절반이 남아 FLOOR(0.7)에 안 걸릴 수 있다.
            if not cards:
                raise RuntimeError(
                    f"노랑통닭 {path} 메뉴 0건 — 'ul.c_list li a' 가 안 걸린다. "
                    f"셀렉터가 깨졌을 가능성")

            for a in cards:
                name = _text(a, "p")
                if not name:
                    continue
                image, day = _image_and_date(a)
                href = (a.attributes.get("href", "") or "").strip()

                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=_text(a, "div.ellipsis"),
                    image=image,
                    category=category,
                    # 이미지 업로드 시각이다. 브랜드가 말해준 출시일이 아니라서
                    # released_at 은 비운다.
                    uploaded_at=day,
                    released_at="",
                    # 🔴 전건 None. NEW 배지도 신메뉴 탭도 없다. 목록이 최신순으로
                    # 보이지만 순서는 날짜가 아니다.
                    is_new=None,
                    # 할인·행사 표시가 없다. 세트에는 promo 를 찍지 않는다
                    # (rules.drop_sets() 가 이름으로 거른다).
                    promo=False,
                    url=MENU + href if href else "",
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
                if len(items) >= MAX_ITEMS:
                    break

    # 건수는 멀쩡한데 날짜만 사라지는 경로를 막는다. 이 브랜드의 유일한 신호다.
    dated = sum(1 for it in items if it.uploaded_at)
    if dated * 2 < len(items):
        raise RuntimeError(
            f"노랑통닭 업로드일 {len(items)}건 중 {dated}건만 붙었다 — "
            f"'span.img_dummy' 의 background url 이나 쿼리스트링이 바뀌었을 "
            f"가능성. 이 브랜드의 유일한 신제품 신호다")
    return items
