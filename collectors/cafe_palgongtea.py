"""팔공티(PALGONG TEA). ㈜피앤에프.

https://palgongtea.co.kr 가 공식이다. 200, SSR, 쿠키·세션 없이 열린다.
브라우저 불필요. 상품 목록 경로는 `/goods/newest.html?menu=<탭>` 하나이고
탭이 넷이다 — `신메뉴`·`음료`·`디저트`·`MD`. 쿼리값이 한글 그대로다.

⚠️ `/goods/collection.html`(티 컬렉션)은 **전체 메뉴가 아니다.** 이름만 보면
메뉴판 같은데 실제로는 블랙티·자스민 그린티·얼그레이티·우롱티 네 종류의
'차 설명'(숙성도·바디감·신맛·단맛) 교육 면이라 `li.items` 가 0건이다. 상품은
한 건도 없다. `/goods/season.html`(시즌메뉴)도 `.teaItem` 0건으로 비어 있다.
이 브랜드의 '전체 메뉴'는 **`음료`+`디저트` 탭의 합집합**이다.

⚠️ 탭을 그냥 열면 **첫 소분류 하나만** 온다. 탭 안에 `?cate=` 소분류가 또
있고(음료 9개 Coffee2·Coffee3·coffee4·Coffee5·Coffee6·Coffee9·Coffee10·
Coffee11·gelato2 / 디저트 2개 dessert1·dessert2 / 신메뉴 5개 gelato·JUICE·
Bluesoda·matcha·C12), 기본 화면은 그중 첫 칸이다. 그래서 `음료` 탭만 열면
10건처럼 보이지만 소분류를 다 돌면 114건이다. 소분류를 안 돌면 '신메뉴 7건 중
3건이 음료 10건과 겹친다' 는 엉뚱한 그림이 나온다 — 그게 처음 보이는 모습이다.

카드 구조:
    li.items > span.itemNm(상품명) + img.teaItem[src](사진)
             + a.itemLink[onclick="commonJs.popupOpenFn('newestPop','526')"]
`MD` 탭은 카드가 빈 껍데기 한 장뿐이라(itemNm 없음) 0건이다.

── 신상 판정 (2026-10-03 실측) ─────────────────────────────────────────
`신메뉴` 탭을 믿기 전에 전체와 대조했다.
  신메뉴 탭 소분류 5칸 합집합 = 22건 (칸 사이 중복 0)
  전체(음료 114 + 디저트 18)   = 132건
  신메뉴 ∩ 전체 = 22건 → **22/132 = 16.7%**. 신메뉴에만 있고 전체엔 없는 건 0건.
전건이 아니고(설빙·퀴즈노스·버거운버거 같은 가짜가 아니다) 디저트 18건에는
신메뉴가 0건이다. 탐앤탐스(36/204=17.6%)와 같은 모양이다.

사진 파일명의 10자리 epoch(초)로 교차검증했다 — 신메뉴 22건은 전부
2025-09-24 ~ 2026-07-28 안이고, 전체 132건에는 2021-09(3건)·2023-09(45건)
같은 꼬리가 있는데 그중 신메뉴로 표시된 건 하나도 없다. 신호가 늙지 않았다.

🔴 **같은 상품이 두 탭에 다른 팝업 id 로 중복으로 올라와 있다.**
'베리크런치 요거트 아이스크림'(신메뉴 526 / 음료 527), '달달말차 팥빙수'
(491 / 495), '밀크 팥빙수'(496 / 497)… 사진 파일도 각각 따로 올라가 있어
파일명이 다르다(1785206086 vs 1785206095, 9초 차이). 전체 22건이 다 그렇다.
키(base.make_key)로 접는다 — 빽다방·할리스와 같은 처리다.

가드: 신메뉴가 전체의 절반을 넘으면 '신메뉴 탭'이 전체 목록을 다른 경로로
불러오는 가짜라는 뜻이라 RuntimeError 를 낸다(세븐일레븐 선례).

── 날짜 ───────────────────────────────────────────────────────────────
브랜드가 출시일을 어디에도 적지 않는다. 상세 JSON(아래)에도 날짜 칸이 없다
(같은 CMS 의 시즌메뉴 팝업은 `wtime` 을 주는데 신메뉴 팝업은 안 준다).
사진 파일명의 epoch 를 **uploaded_at** 에만 넣는다 — 사진을 올린 시각이지
브랜드가 말한 출시일이 아니다. released_at 은 비운다(맘스터치 선례. 그쪽도
`/upload_file/.../1789594226-QSQCK.png` 로 파일명 꼴이 같다 — 같은 CMS 다).

⚠️ 일괄 재업로드가 **실재한다.** 전체 132건의 월 분포를 세면 2023-09 에 45건,
2026-03 에 18건이 몰려 있고, 2026-03-23 자 사진 중에는 팝업 id 가 219·250 인
'자몽블랙프룻티 (ICE/HOT)' — 한참 전부터 팔던 상품 — 이 섞여 있다. 사진만
다시 찍어 올린 것이다. 그래서 **신메뉴로 표시된 것 말고는 날짜를 안 쓴다**
(어차피 수집 대상이 아니다). 신메뉴 22건 안에서는 팝업 id 순서와 epoch 순서가
완전히 일치하고(452→2025-09-24 … 527→2026-07-28), 같은 날 몰린 묶음도
최대 5건(말차 라인 2025-09-24, 딸기 라인 2025-12-10)이라 라인 단위 출시로
읽힌다. 이미지 Last-Modified 는 보지 않는다.

── 상세 ───────────────────────────────────────────────────────────────
상세는 독립 URL 이 없다. `commonJs.popupOpenFn('newestPop', idx)` 가
`POST /goods/newest_detail.html` 에 `idx` 를 던져 JSON 을 받아 빈 팝업 틀을
채운다. 응답은 `{"item":[{gname_kr, gmemo, account1/2, file1_chg,
nutrition*…}]}` 이고 **날짜 칸이 없다.** 설명(gmemo)만 쓴다.
`idx` 는 응답 안에서 빈 문자열로 와서 신뢰할 수 없고, 사람이 열 수 있는
주소도 아니라 Item.url 은 신메뉴 탭 주소로 둔다(브랜드로 트래픽을 돌려주는
게 이 링크의 용건이다).

── TLS ───────────────────────────────────────────────────────────────
⚠️ **인증서 호스트명이 안 맞는다.** 카페24 호스팅인데 인증서가 `*.cafe24.com`
(Sectigo DV, 2026-08-10~2027-02-24) 한 장이라 apex 도 www 도 전부 mismatch 다.
체인 자체는 멀쩡하니 `base.client(verify=False)` 로 연다(또래오래·노랑통닭과
같은 처지다). `palgongtea.cafe24.com` 은 NXDOMAIN 이라 우회 호스트도 없다.
그래서 사진 주소(https://palgongtea.co.kr/upload_file/goods/…)도 브라우저에서
막힌다 — rules.verify_images 가 검증을 켜고 때려 보고 image_src 로 내린다.
주소는 그대로 넣어 둔다. 브랜드가 인증서를 고치면 그날 바로 되살아난다
(http 로 바꾸면 base.derive 가 지우고 되살아날 길도 없다).

robots.txt 는 404 다(2026-10-03). RFC 9309 상 '규칙 명시 없음'이라 제한이
없지만 간격은 공통 방침대로 2초를 쓴다.
"""
import re
import time
import urllib.parse
from datetime import datetime, timedelta, timezone

from selectolax.parser import HTMLParser

from . import base
from .base import Item

KST = timezone(timedelta(hours=9))

BRAND = "팔공티"
SITE = "https://palgongtea.co.kr"
LIST_URL = f"{SITE}/goods/newest.html"
DETAIL_URL = f"{SITE}/goods/newest_detail.html"

NEW_TAB = "신메뉴"             # 브랜드가 직접 묶어 준 신메뉴 탭
FULL_TABS = ("음료", "디저트")  # 전체 메뉴. 대조용이고 상품으로는 안 담는다
                               # (MD 탭은 빈 카드 한 장이라 아예 안 연다)

DELAY = 2.0
MAX_CATES = 20       # 폭주 방지. 현재 탭당 최대 9칸.
MAX_DETAILS = 60     # 폭주 방지. 현재 신메뉴 22건.

# 신메뉴가 전체의 이 비율을 넘으면 '신메뉴 탭'이 가짜다. 실측 16.7%.
MAX_NEW_RATIO = 0.5

# 사진 파일명의 10자리 epoch(초). `/upload_file/goods/1785206086-KMLPG.png`.
_STAMP = re.compile(r"/(\d{10})-[A-Za-z]+\.")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(src: str) -> str:
    if not src:
        return ""
    return src if src.startswith("http") else SITE + "/" + src.lstrip("./")


def _uploaded_at(src: str) -> str:
    """사진 파일명의 epoch(초) → 'YYYY-MM-DD'. 없거나 터무니없으면 빈 문자열."""
    m = _STAMP.search(src or "")
    if not m:
        return ""
    ts = int(m.group(1))
    # 2015~오늘+1일 밖이면 epoch 가 아니라 다른 숫자다. 지어내지 않는다.
    if not (1420070400 <= ts <= datetime.now().timestamp() + 86400):
        return ""
    # 러너가 UTC 면 로컬 타임존으로는 KST 새벽 업로드분이 하루 당겨진다.
    return datetime.fromtimestamp(ts, KST).strftime("%Y-%m-%d")


def _cards(html: str) -> list:
    """목록 HTML → [(상품명, 사진 src, 팝업 idx)]. 빈 껍데기 카드는 버린다."""
    out = []
    for li in HTMLParser(html).css("li.items"):
        nm = li.css_first(".itemNm")
        name = _clean(nm.text()) if nm else ""
        if not name:                      # MD 탭의 빈 카드
            continue
        img = li.css_first("img.teaItem")
        a = li.css_first("a.itemLink")
        m = re.search(r"popupOpenFn\('newestPop',\s*'(\d+)'\)",
                      a.attributes.get("onclick", "") if a else "")
        out.append((name,
                    _abs(img.attributes.get("src", "") if img else ""),
                    m.group(1) if m else ""))
    return out


def _cates(html: str, tab: str) -> list:
    """탭 안의 소분류 코드. 기본 화면은 첫 칸뿐이라 이걸 다 돌아야 전부 나온다."""
    out, seen = [], set()
    for a in HTMLParser(html).css("a"):
        href = a.attributes.get("href", "") or ""
        m = re.search(r"cate=([^&#]+)", href)
        # 같은 탭의 소분류만 본다. 다른 탭 링크에도 cate 가 붙어 있다.
        if not m or f"menu={urllib.parse.quote(tab)}" not in href and f"menu={tab}" not in href:
            continue
        code = m.group(1)
        if code not in seen:
            seen.add(code)
            out.append(code)
    return out[:MAX_CATES]


def _tab(c, tab: str) -> list:
    """탭 하나의 전체 카드. 기본 화면 + 소분류를 모두 돌아 합친다."""
    r = base.retry(lambda: c.get(LIST_URL, params={"menu": tab}))
    r.raise_for_status()
    rows = list(_cards(r.text))
    for code in _cates(r.text, tab):
        time.sleep(DELAY)
        rr = base.retry(lambda: c.get(LIST_URL, params={"menu": tab, "cate": code}))
        rr.raise_for_status()
        rows += _cards(rr.text)
    return rows


def _desc(c, idx: str) -> str:
    """팝업 JSON 의 gmemo(상품 설명). 실패하면 조용히 빈 값으로 둔다."""
    r = base.retry(lambda: c.post(DETAIL_URL, data={"idx": idx},
                                  headers={"X-Requested-With": "XMLHttpRequest"}))
    r.raise_for_status()
    try:
        rows = r.json().get("item") or []
    except ValueError:
        return ""
    if not rows:
        return ""
    # gmemo 는 HTML 조각이다 — 줄바꿈이 <br> 로, 간혹 &nbsp; 로 들어온다.
    memo = re.sub(r"<[^>]+>", " ", rows[0].get("gmemo", "") or "")
    return _clean(memo.replace("\xa0", " ").replace("&nbsp;", " "))


def fetch() -> list[Item]:
    ref = f"{LIST_URL}?menu={urllib.parse.quote(NEW_TAB)}"
    with base.client(verify=False, headers={"Referer": ref}) as c:
        new_rows = _tab(c, NEW_TAB)
        if not new_rows:
            raise RuntimeError("팔공티 신메뉴 0건 — 셀렉터나 탭 이름이 깨졌을 수 있다")

        full_rows = []
        for tab in FULL_TABS:
            time.sleep(DELAY)
            full_rows += _tab(c, tab)
        if not full_rows:
            raise RuntimeError("팔공티 전체 메뉴 0건 — 대조를 못 하니 신상 판정도 못 한다")

        # 🔴 '신메뉴 탭'이 사실은 전체 목록이면 신상이 아니다. 비율로 센다.
        new_names = {n for n, _, _ in new_rows}
        full_names = {n for n, _, _ in full_rows}
        ratio = len(new_names & full_names) / len(full_names)
        if ratio > MAX_NEW_RATIO:
            raise RuntimeError(
                f"팔공티 신메뉴가 전체의 {ratio:.0%}({len(new_names)}/{len(full_names)}) — "
                "탭이 전체 목록을 불러오는 가짜로 보인다")

        items: list[Item] = []
        seen = set()
        pending = []                                   # (Item, 팝업 idx)
        for name, img, idx in new_rows:
            it = Item(
                brand=BRAND,
                name=name,
                image=img,
                uploaded_at=_uploaded_at(img),
                is_new=True,
                url=ref,
            )
            if it.key in seen:        # 같은 상품이 소분류·탭에 겹쳐 올라와 있다
                continue
            seen.add(it.key)
            items.append(it)
            if idx:
                pending.append((it, idx))

        for it, idx in pending[:MAX_DETAILS]:
            time.sleep(DELAY)
            it.desc = _desc(c, idx)

    return items
