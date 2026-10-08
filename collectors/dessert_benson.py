"""벤슨(Benson) — 자사몰 **NEW 탭** 한 장 + 한화갤러리아 보도자료.

한화갤러리아 자회사 ㈜베러스쿱크리머리가 2025년 5월 압구정 1호점으로 론칭한
**프리미엄 아이스크림** 브랜드다(2026-10 현재 20호점 돌파). 파이브가이즈와
같은 한화 유통·서비스 부문 식음 사업이라 보도자료 소스를 공유한다 —
공용 모듈이 `collectors/hanwhagalleria_press.py` 다.

⚠️ **'음료(에이드·주스)' 브랜드가 아니다.** 착수 지시서에 그렇게 적혀 있었는데
   실측으로 뒤집혔다. 보도자료 원문이 일관되게 "프리미엄 아이스크림 브랜드
   ‘벤슨(Benson)’" 이라 쓰고(2025-04-14 론칭 예고 기사 제목이 `재료 본연에
   집중한 ‘프리미엄 리얼 아이스크림’ ‘벤슨(Benson)’ 5월 론칭` 이다), 자사몰
   카테고리도 아이스크림/프리팩/아이스크림 케이크/커피 및 음료/디저트 다섯 중
   아이스크림이 본체다. 그래서 세부분류는 `음료` 가 아니라 **`아이스크림`** 이다.

## 도메인 확인 — 'benson' 은 흔한 이름이라 본문으로 맞춰 봤다

    https://www.bensonicecream.com/        200 / 37,146B
      푸터: `(주)베러스쿱크리머리 대표이사 : 윤진호
             사업자등록번호 : 294-81-03799
             E-mail : benson@hanwha.com`
`@hanwha.com` 과 법인명이 보도자료의 "베러스쿱크리머리 관계자" 와 맞는다.
이름만 같은 다른 회사가 아니다. (`benson.co.kr`·`bensoncreamery.com` 은
둘 다 NXDOMAIN 이다 — 실측.)

robots: https://www.bensonicecream.com/robots.txt → 200 / 40B / text/plain
        `User-agent: *` / `Allow: /` / **`Crawl-delay: 60`**
        → `DELAY = 60`. 평소 요청이 **1회**라(아래) 실제로는 안 쉰다.

## ⚠️ TLS — 서버가 중간 인증서를 **잘못** 보낸다

    리프   CN=bensonicecream.com (2026-07-31 ~ 2027-02-14, 유효)
           issuer = Sectigo Public Server Authentication CA DV R36
    서버가 함께 보낸 중간 = Sectigo RSA Domain Validation Secure Server CA
                            USERTrust RSA Certification Authority
           → 리프의 발급자가 아니다. certifi 만으로는
             `unable to get local issuer certificate` 로 못 붙는다.
`collectors/japan_motoishi.py` 와 **글자 그대로 같은 사고**라 그 어댑터가 이미
받아 둔 `collectors/certs/sectigo-public-server-auth-ca-dv-r36.pem` 을 그대로
쓴다(발급 체인이 같다 — 새로 받을 필요가 없다). `verify=False` 는 쓰지 않는다
(notes/CRAWLING-POLICY.md §6-1). certifi 루트에 **더하기만** 한다.

## 수집하는 것 — `/product/new.php` 한 장뿐이다

사이트의 PRODUCT 메뉴는 `NEW / 아이스크림 / 프리팩 / 아이스크림 케이크 /
커피 및 음료 / 디저트` 여섯 칸인데, **`NEW` 만 브랜드가 직접 '새것' 이라고
선언한 자리**다. 2026-10-08 실측:

    /product/new.php            200 / 15,919B  →  블랙베리 치즈케이크 **1건**
    /product/list1.php?cat_no=1 200 / 21,599B  →  아이스크림        20건
                        cat_no=2 200 / 17,465B  →  프리팩             8건
                        cat_no=3 200 / 18,734B  →  아이스크림 케이크 11건
                        cat_no=4 200 / 21,599B  →  커피 및 음료      11건
                        cat_no=5 200 / 15,790B  →  디저트             3건
    카탈로그 합계 **53건 / NEW 배지 0건**

카탈로그 카드는 `li > a > .thumb img + .tit span` 뿐이고 **배지도 날짜도 없다.**
그래서 **카탈로그는 안 긁는다** — 긁으면 2025년부터 팔던 바닐라·피스타치오가
전부 신상으로 올라간다(이 레포 제1 규칙 위반).

NEW 탭이 진짜 '최신' 인지 확인했다. 지금 걸린 블랙베리 치즈케이크는 상품
id 가 **58 로 아이스크림 20건 중 최대**이고(그다음이 56·55·19…), 본문 사진
경로가 `/uploaded/webedit/**2610**/…` = 2026년 10월이다.
신호 비율로 말하면 **카탈로그 53건 중 1건(1.9%)** 이다. 배지가 전건에 붙어
있는 '시그니처 배지' 류(설빙·퀴즈노스 사고)와는 반대쪽 끝이라 믿을 만하다.

NEW 탭은 한 번에 한 건을 보여 주고 `?new_idx=±1` 로 넘긴다. 앞뒤 화살표에
`none` 클래스가 붙으면 끝이다(지금은 양쪽 다 `none` = 1건뿐). 다음 화살표를
따라가되 `MAX_NEW` 로 막는다.
⚠️ **범위를 넘는 `new_idx` 는 에러를 안 낸다** — `?new_idx=1` 을 직접 줘 보면
   200 / 15,919B 로 **같은 상품**이 그대로 온다(실측). 즉 끝을 알려 주는 건
   상태코드가 아니라 `none` 클래스뿐이다. 받침으로 `seen`(`it.key`)을 둔다.

### 날짜는 비운다

NEW 탭에도 카탈로그에도 날짜가 없다. 본문 사진 경로의 `2610` 은 **년월까지**라
일(日)을 지어내야 하고 그건 안 한다(`collectors/burger_fiveguys.py` 와 같은
판단). `is_new=True` 만 두면 `rules.is_fresh` 가 `first_seen` + `STALE` 로
수명을 끊는다.

## 두 번째 소스 — 한화갤러리아 보도자료

`collectors/hanwhagalleria_press.py` 참고. 4년치 144건에서 벤슨 기사가 29건인데
**출시 기사는 1건**이다(2026-07-02 하츠투하츠 협업 '레몬탱'). 나머지는 출점·
팝업·콜라보·실적이다. 보도자료 쪽 이름이 자사몰 이름과 어긋날 수 있어
**자사몰(정규 이름)을 먼저 넣고** `it.key` 로 거른다.

## 🔴 0건이 정상이다 → `ALLOW_EMPTY = True`

NEW 탭은 신상이 없으면 비는 자리이고 보도자료는 1년에 한두 건이다.
`collectors/china_hongjjajang.py`·`collectors/snack_yupdduk.py` 와 같은 칸이다.
대신 **파서가 깨진 것과 구분**하려고 바닥 가드를 둔다 — NEW 탭 HTML 에
PRODUCT LNB(카테고리 링크)가 `MIN_LNB` 개 미만이면 마크업이 바뀐 것으로 보고
예외를 올린다. LNB 는 멀쩡한데 `.new-top` 만 없으면 0건이 맞다.
"""
import pathlib
import ssl
import time

import certifi
from selectolax.parser import HTMLParser

from . import base
from .base import Item
from . import hanwhagalleria_press as press

BRAND = "벤슨"
SITE = "https://www.bensonicecream.com"
NEW = SITE + "/product/new.php"

# 신상이 없으면 NEW 탭이 비고 보도자료는 1년에 한두 건이다. 사유는 docstring.
ALLOW_EMPTY = True

DELAY = 60           # robots.txt 의 Crawl-delay. 평소 요청은 1회라 안 쉰다.
MAX_NEW = 6          # NEW 탭을 `?new_idx` 로 넘기는 상한. 폭주 방지.
MIN_LNB = 3          # PRODUCT 카테고리 링크 수 바닥(현재 5). 미만이면 마크업 변경

# 서버가 잘못 보내는 중간 인증서. japan_motoishi.py 가 받아 둔 것을 공유한다.
CA_EXTRA = (pathlib.Path(__file__).parent / "certs"
            / "sectigo-public-server-auth-ca-dv-r36.pem")


def _ssl_context() -> ssl.SSLContext:
    """certifi 루트 + 서버가 빠뜨린 중간인증서. 검증은 켜 둔 채로 쓴다."""
    if not CA_EXTRA.exists():
        raise FileNotFoundError(
            f"중간 인증서가 없다: {CA_EXTRA} — 이게 없으면 이 사이트는 "
            "unable to get local issuer certificate 로 붙지 않는다")
    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.load_verify_locations(cafile=str(CA_EXTRA))
    return ctx


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _new_items(html: str) -> tuple[list[Item], str]:
    """NEW 탭 한 장 → (상품, 다음 쪽 href). 다음이 없으면 href 는 빈 문자열."""
    doc = HTMLParser(html)
    if len(doc.css('.lnb-wrap a[href*="list1.php"]')) < MIN_LNB:
        raise RuntimeError(
            f"{NEW}: PRODUCT 카테고리 링크가 {MIN_LNB}개 미만이다"
            f"({len(html)}B) — 마크업이 바뀌었는지 확인하라")

    out: list[Item] = []
    top = doc.css_first(".new-top .info")
    if top is not None:
        h3 = top.css_first("h3")
        name = _clean(h3.text()) if h3 is not None else ""
        if name:
            h4 = top.css_first("h4")
            body = doc.css_first(".new-detail .txt")
            img = body.css_first("img") if body is not None else None
            # ⚠️ selectolax 는 값 없는 속성에 None 을 준다. `or ""` 로 받는다.
            src = (img.attributes.get("src") or "") if img is not None else ""
            out.append(Item(
                brand=BRAND,
                name=name,
                name_en=_clean(h4.text()) if h4 is not None else "",
                desc=_clean(body.text()) if body is not None else "",
                image=SITE + src if src.startswith("/") else src,
                is_new=True,      # 브랜드가 'NEW' 칸에 올려 둔 것이다
                # 날짜 없음 — 지어내지 않는다(docstring §날짜는 비운다).
                url=NEW,
            ))

    nxt = doc.css_first("a.new-pagination.next")
    href = (nxt.attributes.get("href") or "") if nxt is not None else ""
    if nxt is None or "none" in (nxt.attributes.get("class") or ""):
        href = ""
    return out, href


def fetch() -> list[Item]:
    items: list[Item] = []
    seen: set[str] = set()

    url = NEW
    with base.client(verify=_ssl_context()) as c:
        for i in range(MAX_NEW):
            if i:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(url))
            r.raise_for_status()
            got, nxt = _new_items(r.text)
            for it in got:
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)
            if not nxt:
                break
            url = NEW + nxt if nxt.startswith("?") else (
                SITE + nxt if nxt.startswith("/") else nxt)

    # 보도자료는 **뒤에** 더한다. 자사몰 이름이 정규 표기라 겹치면 그쪽을 남긴다.
    for it in press.items(BRAND):
        if it.key not in seen:
            seen.add(it.key)
            items.append(it)
    return items
