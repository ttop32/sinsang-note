"""하삼동커피.

도메인은 **hasamdongcoffee.com** 이다(푸터: 주식회사 하삼동 / 사업자등록번호
462-81-01716). `hasamdong.com` 은 NXDOMAIN 이고, apex(`hasamdongcoffee.com`)로
들어가면 '콜라B' 라는 **다른 브랜드 페이지**가 뜬다. `www.` 를 붙여야 하삼동이다.
http 로 때려도 `302 → https://www.hasamdongcoffee.com:443/index.php` 로 올려보낸다.

⚠️ **TLS 를 먼저 풀어야 한다.** 파이썬으로 열면
`[SSL: DH_KEY_TOO_SMALL] dh key too small` 로 **https·http 둘 다 실패**한다.
그런데 이건 **인증서 문제가 아니다** — 인증서는 Sectigo 발급에 CN 도 맞고
`Verify return code: 0 (ok)` 다. 서버가 1024비트짜리 낡은 DH 파라미터로
DHE 키교환을 하자고 해서 OpenSSL 3 의 기본 보안수준(SECLEVEL=2)이 끊는 것뿐이다.
그래서 **`verify=False` 를 쓰지 않는다.** DHE 만 빼면 인증서 검증을 그대로
켠 채로 200 이 온다 —

    ctx = ssl.create_default_context()
    ctx.set_ciphers("DEFAULT:!DH")
    base.client(verify=ctx)

(`ECDHE+AESGCM` 처럼 더 좁히면 handshake failure 다. `!DH` 만 빼야 한다.)
이게 `verify=False` 보다 나은 이유가 하나 더 있다 — **브라우저는 2016년부터
DHE 자체를 안 쓴다.** 즉 이 서버의 사진은 사람 브라우저에서는 멀쩡히 열린다.
우리만 못 열던 것이고, verify 를 끄고 넘어갔으면 '사진이 깨지는 사이트' 로
잘못 기록할 뻔했다.

robots.txt(2026-10-03, 200)는 `User-agent: * / Allow:/` 두 줄이다. 제한 없음.

메뉴는 `/menu_list.php` 가 겉껍데기고 실제 목록은 그 안에서 부르는 AJAX 다.
    POST /menu_list_ajax.php   (sc_pd_ctg_cd=<분류>, page=1)
**`sc_pd_ctg_cd` 를 비우면 '전체음료' 라 12개 분류가 한 응답(105KB)에 다 온다.**
페이지네이션도 없다 — **요청 1회로 217건**이다. 분류별로 12번 돌 이유가 없다.
분류는 응답 안에 `<h3 class="list-title bul">` 로 같이 들어 있어 그대로 쓴다.
    시그니처 4 / 신메뉴·시즌메뉴 28 / 커피 20 / 콜드브루·디카페인 9 / 보틀 22 /
    라떼 12 / 스무디 19 / 에이드 6 / 주스·버블티 14 / 차 17 / 디저트 57 / MD 9
⚠️ 분류를 가로질러 **같은 상품이 두 번 실리는 게 4건** 있다(시그니처의
달고나카페라떼·돌체라떼·히말라야(소금커피)·구름라떼가 커피 분류에도 있고,
seq 가 서로 다르다). seq 로 접으면 못 잡으니 make_key 로 접는다. 그래서
수집량은 217 이 아니라 **213건**이다.

날짜는 **썸네일 경로**에서 얻는다. `/upld/2026/08/18/tpd_af_img_7831.png` 처럼
업로드 날짜가 경로에 그대로 박혀 있다. 파일명 해시도, 타임스탬프 추측도 아니다.
  - 217건 중 **142건**에 날짜가 붙는다. 나머지 75건은 경로가 `/upld/pd/58_1.png`
    꼴인데, 이건 사이트를 만들 때 옮겨온 **옛 상품 이미지**다(아메리카노·카페라떼·
    바닐라라떼 같은 상설 메뉴가 전부 여기 있다). 날짜를 **지어내지 않고 비운다.**
  - 분포가 흩어져 있다. 가장 큰 덩어리가 2024-07-22 의 27건인데 이건 2024년 7월
    사이트 구축분이다(같은 달 공지가 전부 2024.07.17~19 다). 2년도 더 전이라
    60일 창에 들어올 일이 없어 그냥 둔다 — 탐앤탐스 2025-05-14/15 처럼 **최근
    날짜로 위장되는 일괄이 아니다.** 그 뒤로는 2026-06-12 10건, 2026-06-16 7건,
    2025-07-10 12건, 2025-11-21 6건 … 식으로 출시 묶음 단위로 흩어진다.
  - **공지 게시판과 교차검증했다**(`notice_list_ajax.php`). 신메뉴 공지가 뜨고
    며칠 뒤에 사진이 올라간다 —
        2026.02.03 `2026 봄 신메뉴`      ↔ 2026-02-09 6건(말차구름 5종 등)
        2026.06.05 `2026 여름 2차 신메뉴` ↔ 2026-06-12 10건(꿀 아메리카노·꿀
                                           카페라떼·구름소다스무디·백도스무디 등)
        2026.08.05 `2026 늦여름 신메뉴`   ↔ 2026-08-18 3건(수정과·1.1L옛날냉차 등)
        2025.11.17 `메뉴 개편 안내`       ↔ 2025-11-21 6건
    묶음도 날짜도 아귀가 맞는다. 다만 이건 **사진 업로드일**이지 브랜드가 공표한
    출시일이 아니고 공지보다 5~13일 늦다. 그래서 `released_at` 이 아니라
    `uploaded_at` 에 넣는다.

신제품 신호:
  - 분류 `신메뉴/시즌메뉴`(cd=10)가 **28건 / 217건 = 12.9%** 다. 탐앤탐스
    17.6%·블루샥 4.3% 와 같은 자릿수고, 퀴즈노스(100%)·버거운버거(전건)·
    공차 'New 시즌 메뉴'(43%) 같은 가짜가 아니다.
  - **그래도 이 탭만 믿으면 안 된다.** 쌓이는 탭이라서 2025-05-30 의 `마! 스무디`
    3종, 2025-11-04 의 `댕댕이차`·`배도라지차`·`광동쌍화차` 가 아직 들어 있다.
    1년 넘은 것들이다. 설빙에서 시그니처 배지를 NEW 로 세어 2013년 인절미설빙이
    신상이 된 것과 같은 함정이다.
  - 그래서 **탭 + 날짜를 같이** 본다. `is_new` 는 cd=10 **이면서 날짜가 있는**
    것에만 True 로 둔다. 날짜가 있으면 rules.is_fresh 가 60일 창으로 다시
    거르므로 옛 시즌메뉴는 자동으로 떨어진다.
  - 날짜 없는 cd=10 **1건**(`밀크팥퐁당`, 이미지가 레거시 `/upld/pd/` 경로)은
    `is_new` 를 비운다(None). 날짜 없이 True 를 주면 rules 가 STALE 90일 동안
    화면에 띄우는데, 레거시 경로라는 건 옛 상품이라는 뜻이다.
  - 나머지 189건은 `is_new` 를 **False 가 아니라 None** 으로 둔다. 브랜드가
    '신제품 아님'이라고 말한 적이 없고, False 로 찍으면 rules 가 released_at
    만 보게 돼서 `uploaded_at` 경로가 통째로 막힌다.

`ICE` / `ICE/HOT` 표기는 라벨로 넣는다(목록 두 번째 줄).
상품 상세는 `menu_view.php?pk_seq=<seq>` 로 **GET 이 된다**(화면은 form POST 로
가지만 쿼리로도 열린다). 설명문은 별도 팝업 AJAX(`menu_dtl_pop_ajax.php`)에만
있는데 217회를 더 때려야 해서 받지 않는다. `desc` 는 비운다.

MD 분류(9건)를 통째로 굿즈로 찍지 않는다 — **8건이 먹는 것**이다(자일리톨
스톤 캔디 4종, 트위스트앤드링크 4종). 굿즈는 `하삼동머그컵` 하나뿐이고
base.is_nonfood 의 `머그` 가 이미 잡는다.
"""
import re
import ssl

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "하삼동커피"
SITE = "https://www.hasamdongcoffee.com"
LIST_URL = f"{SITE}/menu_list_ajax.php"
VIEW_URL = f"{SITE}/menu_view.php"
NEW_CODE = "10"        # 분류 '신메뉴/시즌메뉴'
DELAY = 2.0            # 요청이 1회뿐이라 실제로는 안 쉰다. 규약값으로 남긴다.
MIN_ITEMS = 150        # 현재 217건. 크게 모자라면 응답 구조가 바뀐 것이다.

# 썸네일 경로에 박힌 업로드 날짜. `/upld/2026/08/18/tpd_af_img_7831.png`
_DAY = re.compile(r"/upld/(\d{4})/(\d{2})/(\d{2})/")

# `background-image:url('/upld/…')`
_BG = re.compile(r"url\(['\"]?([^'\")]+)['\"]?\)")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _context() -> ssl.SSLContext:
    """DHE 만 뺀 기본 컨텍스트. 인증서 검증은 켠 채로 둔다(docstring 참고)."""
    ctx = ssl.create_default_context()
    ctx.set_ciphers("DEFAULT:!DH")
    return ctx


def _day(image: str) -> str:
    m = _DAY.search(image or "")
    return "-".join(m.groups()) if m else ""


def _abs(src: str) -> str:
    if not src:
        return ""
    return src if src.startswith("http") else SITE + src


def fetch() -> list[Item]:
    with base.client(verify=_context()) as c:
        r = base.retry(lambda: c.post(LIST_URL, data={"sc_pd_ctg_cd": "", "page": "1"}))
        r.raise_for_status()

    items: list[Item] = []
    seen = set()
    doc = HTMLParser(r.text)
    groups = doc.css(".list-group")
    if not groups:
        raise RuntimeError("하삼동커피 분류 묶음을 못 찾았다 — 목록 응답이 바뀌었다")

    for g in groups:
        h = g.css_first("h3")
        cat = _clean(h.text()) if h else ""
        for li in g.css("li"):
            a = li.css_first("a.btnView")
            if a is None:
                continue
            lines = [_clean(p.text()) for p in li.css(".detail p")]
            name = lines[0] if lines else ""
            if not name:
                continue
            thumb = li.css_first(".thumb")
            m = _BG.search(thumb.attributes.get("style", "") if thumb else "")
            image = _abs(m.group(1) if m else "")
            day = _day(image)
            seq = a.attributes.get("seq") or ""
            code = a.attributes.get("cd") or ""
            # 온도 표기는 두 번째 줄에만 온다. 세 번째 줄은 영양정보 버튼이다.
            temp = lines[1] if len(lines) > 1 else ""
            it = Item(
                brand=BRAND,
                name=name,
                image=image,
                category=cat,
                labels=[t for t in temp.split("/") if t in ("ICE", "HOT")],
                uploaded_at=day,
                # 탭만으로는 못 믿는다. 날짜가 같이 있을 때만 신제품으로 본다.
                is_new=True if (code == NEW_CODE and day) else None,
                url=f"{VIEW_URL}?pk_seq={seq}" if seq else "",
            )
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)

    if len(items) < MIN_ITEMS:
        raise RuntimeError(f"하삼동커피 {len(items)}건 — 메뉴 응답 구조가 바뀌었을 수 있다")
    # 날짜가 통째로 사라지면 썸네일 경로 규칙이 바뀐 것이다. 조용히 넘기지 않는다.
    if not any(it.uploaded_at for it in items):
        raise RuntimeError("하삼동커피 날짜가 0건 — 썸네일 경로(/upld/YYYY/MM/DD/)가 바뀌었다")
    return items
