"""모토이시 — '모토이시 이야기' 게시판의 [신메뉴출시] 글만.

야키니쿠(일본식 소고기구이) 전문점이다. motoishi.co.kr 은 SSR 정적 페이지라
브라우저가 필요 없고, 2026-10-02 실측으로 상품 쪽 구조는 이렇다.

  /introduce-menu/main-menu.php · single-menu.php · side-menu.php
      **메뉴 소개 페이지는 쓸 수 없다.** 상품이 `와규 6품 모둠 SET` 처럼 몇 개만
      소개문 형태로 박혀 있고(메인 3건), 날짜도 NEW 표시도 없다. 상품 단위
      마크업이 아니라 디자인 섹션이다.
  /community/story.php  ← '모토이시 이야기'
      여기가 유일한 신호다. 글 **4건**이 전부인데 그중 3건이 브랜드가 직접
      붙인 `[신메뉴출시]` · `[신메뉴]` 머리말을 달고 있고 목록에 날짜가 있다.
          [신메뉴출시] 호르몬동(대창덮밥) 출시!!            2024-07-09
          [신메뉴] 여름 스페셜 메뉴 『히야시우동(냉우동)』출시 안내  2024-06-14
          [신메뉴출시] 호네츠키갈비 & 카니미소              2024-05-14
      나머지 1건은 대표이사 인터뷰 언론보도(2025-05-19)라 걸러진다.

신제품 신호:
  is_new       채택분 전건 True. 브랜드가 제목에 `[신메뉴…]` 를 직접 달았다.
  released_at  목록의 날짜(`.date`, `2024-07-09`). 게시판 등록일이지만 이 글들은
               출시를 알리는 글 자체라 출시일에 가장 가까운 값이다(오리온·GS25
               보도자료와 같은 취급).

⚠️ **이 게시판은 2025-05-19 이후로 멈춰 있다.** 지금 가져오는 3건은 전부 2024년
   이라 화면에 오를 일이 없다. 그래도 어댑터를 둔 건 신호가 가짜가 아니고
   구조가 단순해서다 — 다음 [신메뉴] 글이 올라오면 그날 바로 잡힌다.
   브랜드가 글을 안 올리는 것과 우리가 못 읽는 것은 다르다.

상세(`?mode=view&idx=`)는 받지 않는다. 실측해보니 본문이 포스터 이미지 한 장뿐이고
글자가 없어서, 목록이 주는 제목·날짜·썸네일 말고 더 얻을 게 없다.
썸네일은 `/uploaded/board/story/t_*.png` 이고 https 로 열린다.

상품명은 제목에서 뽑는다. `[태그]` 를 떼고 꼬리의 `출시`·`출시!!`·`출시 안내` 를
턴다. 한 글이 상품 둘을 알리는 경우(`호네츠키갈비 & 카니미소`)는 `&` 로 쪼갠다 —
양쪽 다 짧은 이름일 때만 쪼개고, 그렇지 않으면 통째로 둔다. `규동+얼큰우동세트`
처럼 `+` 로 묶인 건 세트 구성이라 쪼개지 않는다(쪼개면 없는 상품이 생긴다).
`『…』` 겹낫표 안은 상품명이라 그 안만 남긴다.

robots.txt: `User-agent: *` / `Allow:/` — 전면 허용.
약관: 사이트에 이용약관 페이지가 없다. 푸터는 개인정보처리방침과
      이메일무단수집거부 두 개뿐이고 둘 다 수집을 제한하는 조항이 아니다.

────────────────────────────────────────────────────────────────────────
TLS — 서버가 **엉뚱한** 중간인증서를 보낸다. 검증을 끄지 않고 보충한다.
────────────────────────────────────────────────────────────────────────
2026-10-02 실측. 서버가 세 장을 보내는데 리프와 이어지지 않는다.

    리프  CN=motoishi.co.kr  (2026-06-05 ~ 2026-12-20, 유효)
          issuer = Sectigo Public Server Authentication CA DV R36
    서버가 함께 보낸 중간 = Sectigo RSA Domain Validation Secure Server CA
                            USERTrust RSA Certification Authority
          → 리프의 발급자가 아니다. 서버가 체인을 잘못 깔았다.
    → certifi 로는 `unable to get local issuer certificate`

인증서 자체는 멀쩡하다. 리프의 AIA 가 가리키는 올바른 중간 인증서를 받아
`collectors/certs/sectigo-public-server-auth-ca-dv-r36.pem` 에 넣고 certifi
루트에 `load_verify_locations()` 로 **더해서** 쓴다. `verify=False`(=CERT_NONE)는
쓰지 않는다 — notes/CRAWLING-POLICY.md §6-1 이 금지하고, 같은 처리의 선례가
chicken_toreore.py·lottechilsung.py 다.

보충한 컨텍스트로 검증은 켜진 채 돈다(2026-10-02 실측):
    motoishi.co.kr           접속 성공  (보충 전에는 CERTIFICATE_VERIFY_FAILED)
    wrong.host.badssl.com    거부      Hostname mismatch
    self-signed.badssl.com   거부      self-signed certificate
컨텍스트는 `base.client(verify=...)` 로 넘긴다(httpx 는 transport 가 있으면
Client(verify=) 를 조용히 무시한다. base.client 가 그 처리를 들고 있다).
"""
import pathlib
import re
import ssl
import time

import certifi
from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "모토이시"
SITE = "https://motoishi.co.kr"
LIST = SITE + "/community/story.php"
MAX_PAGES = 5      # 폭주 방지. 현재 1페이지(전체 4건).
DELAY = 1.5

# 서버가 빠뜨린(정확히는 잘못 보낸) 중간 인증서. 출처·지문은 파일 머리말 참고.
CA_EXTRA = (pathlib.Path(__file__).parent / "certs"
            / "sectigo-public-server-auth-ca-dv-r36.pem")


def _ssl_context() -> ssl.SSLContext:
    """certifi 루트 + 빠진 중간인증서. 검증은 그대로 켜 둔다."""
    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.load_verify_locations(cafile=str(CA_EXTRA))
    return ctx


# 브랜드가 직접 붙인 머리말. 이게 있는 글만 신제품으로 본다.
_NEW_TAG = re.compile(r"\[\s*(?:신메뉴|신상품|신제품)[^\]]*\]")
# 제목 맨 앞 `[…]` 태그. 뽑고 나면 이름에서 지운다.
_LEAD_TAG = re.compile(r"^\s*\[[^\]]*\]\s*")
# 겹낫표 안이 상품명이다 — `여름 스페셜 메뉴 『히야시우동(냉우동)』출시 안내`
_BRACKET = re.compile(r"[『「]([^』」]{2,30})[』」]")
# 꼬리의 출시 문구. `출시!!` · `출시 안내` · `출시합니다` 를 다 턴다.
_TAIL = re.compile(r"\s*(?:정식\s*)?출시(?:\s*안내|합니다|했습니다)?\s*[!！.。]*\s*$")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _date(s: str) -> str:
    m = re.search(r"(20\d{2})[-.](\d{1,2})[-.](\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _names(title: str) -> list:
    """제목 → 상품명들. 특정 못 하면 빈 목록."""
    t = _clean(title)
    m = _BRACKET.search(t)
    if m:
        return [m.group(1).strip()]
    t = _LEAD_TAG.sub("", t)
    t = _TAIL.sub("", t).strip(" ·,-")
    if len(t) < 2:
        return []
    # `A & B` 는 한 글에서 알린 상품 둘이다. 양쪽이 다 짧은 이름일 때만 쪼갠다.
    parts = [p.strip() for p in re.split(r"\s*[&＆]\s*", t)]
    if len(parts) == 2 and all(2 <= len(p) <= 15 for p in parts):
        return parts
    return [t]


def fetch() -> list[Item]:
    items: list[Item] = []
    seen, seen_href = set(), set()
    with base.client(verify=_ssl_context()) as c:
        for page in range(1, MAX_PAGES + 1):
            r = base.retry(lambda: c.get(LIST, params={"boardid": "story",
                                                       "goPage": page}))
            r.raise_for_status()
            rows = HTMLParser(r.text).css(".gallery-list li a")
            if not rows:
                if page == 1:
                    raise RuntimeError("모토이시 이야기: 글 0건 — 셀렉터가 깨졌을 수 있다")
                break
            # 범위를 넘긴 page 는 마지막 페이지를 되돌려준다. 전부 본 글이면 종료.
            hrefs = [a.attributes.get("href", "") for a in rows]
            if all(h in seen_href for h in hrefs):
                break
            seen_href.update(hrefs)

            for a in rows:
                tit, dat = a.css_first(".tit"), a.css_first(".date")
                if not (tit and dat):
                    continue
                title = _clean(tit.text())
                if not _NEW_TAG.search(title):
                    continue          # 언론보도·공지는 신제품 글이 아니다
                when = _date(dat.text())
                thumb = a.css_first(".thumb img")
                src = thumb.attributes.get("src", "") if thumb else ""
                href = a.attributes.get("href", "")
                for name in _names(title):
                    it = Item(
                        brand=BRAND,
                        name=name,
                        image=(src if src.startswith("http") else SITE + src) if src else "",
                        released_at=when,
                        is_new=True,   # 제목에 브랜드가 [신메뉴] 를 달았다
                        url=SITE + href if href.startswith("/") else href,
                    )
                    if it.key not in seen:
                        seen.add(it.key)
                        items.append(it)
            time.sleep(DELAY)
    return items
