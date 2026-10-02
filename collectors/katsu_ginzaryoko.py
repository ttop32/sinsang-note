"""긴자료코. 가맹점 109개 — 돈까스 업종 5위.

도메인이 둘이고 **역할이 다르다.** 2026-10-02 실측.
  `ginzaryoko.com`   가맹 모집 랜딩. 정적 HTML 한 장에 `images/menu_img01..12.png` 로
                     '대표메뉴' 12건이 박혀 있다. **상품별 날짜가 없다** — 12장 전부
                     Last-Modified 가 `2026-09-17 02:56:40` 으로 같다(배포 시각).
  `ginzaryoko.co.kr` 브랜드 본사이트. 자체 CMS 라 메뉴가 **DB 에 들어 있고 API 로 나온다.**
이 어댑터는 뒤쪽만 쓴다. 앞쪽은 날짜가 전부 한 값이라 신호가 되지 못한다.

CMS 는 화면이 비어 있고 JS 가 AJAX 로 채운다. 엔드포인트는 페이지 소스에 그대로 있다.

  POST /cms/api/signatureList.ajax
       {"page":1,"pageSize":200,"searchDiv":"0","searchText":"<카테고리키>"}
  카테고리 키는 탭의 onClick 에 박혀 있다 — tonkatsu / rice / noodles / curry / side.
  (화면 라벨은 돈까스·덮밥·면·카레·사이드메뉴. 쿠키·토큰·리퍼러 없이 열린다.)

5요청에 64건. 페이징은 있지만 pageSize=200 으로 한 번에 받는다.
⚠️ `PAGINATION.TOTAL_ENTITY` 는 전 카테고리에서 **0 으로 나온다**(CMS 버그로 보인다).
   건수 판단에 쓰지 마라 — LIST 길이를 봐야 한다.
⚠️ 없는 카테고리 키를 보내면 에러가 아니라 **빈 LIST** 가 온다. 처음에 `donburi`·
   `noodle` 로 찔렀다가 0건을 받고 '덮밥·면은 없는 브랜드'로 오판할 뻔했다.
   그래서 아래에서 카테고리별 0건을 RuntimeError 로 드러낸다.

**신제품 신호가 이 그룹에서 제일 강하다 — `REG_DT` 가 상품마다 붙은 등록 시각이다**
(epoch 밀리초). 사이트 구축 때 몰린 59건과 그 뒤에 얹힌 5건이 또렷하게 갈린다.

  2025-11-07  59건   ← CMS 이관 때 일괄 등록
  2026-04-09   2건   ← 간장계란밥 · 긴자료코 샐러드
  2026-06-17   3건   ← 버터간장계란밥 · 머쉬룸크림우동 · 머쉬룸 크림 돈까스

교차검증: 업로드 디렉터리 경로(`/home/cms/uploaded/2026-06-17-13-19/`)와 이미지의
Last-Modified(`Wed, 17 Jun 2026 04:19:15 GMT`)가 REG_DT 와 같은 날을 가리킨다.
세 값이 독립적으로 일치하므로 등록일로 믿는다. `released_at` 에 넣는다 —
Item 계약이 released_at 을 "출시일/등록일"로 정의하고 있고, 이건 이미지 업로드일이
아니라 **상품 레코드의 등록 시각**이다(본아이에프 cmdtListImg 파일명과 다른 급).
⚠️ 다만 브랜드가 "출시일"이라고 써 둔 값은 아니다. 2025-11-07 59건이 한날한시에
   몰린 게 그 증거다 — 그 59건의 실제 출시일은 훨씬 전이다. 이삭토스트 prdcode 와
   같은 유보를 달아둔다.

`is_new` 는 비운다(None). NEW 배지도 '신메뉴' 카테고리도 없다. `NOTICE_YN` 은 64건
전부 N 이고 게시판 상단 고정 플래그지 신제품 표시가 아니다. 날짜만으로 충분하다.

이미지: `THUMBNAIL_PATH` 는 `/home/cms/uploaded/…` 로 **서버 파일시스템 경로**다.
그대로 쓰면 안 된다. 페이지의 렌더 코드가 하는 대로 접두를 떼고 `/external-images/`
를 붙인다(실측 200, image/jpeg). `HOVAL_*`(호버용)·`MODAL_*`(확대용)도 있지만
목록 썸네일인 `THUMBNAIL_PATH` 만 쓴다.

가격은 응답에 없다. 상품 상세 주소도 없다 — 목록이 모달을 띄우는 구조라 Item.url 은
SITES 폴백(대표메뉴 페이지)으로 떨어진다.

`VISIBLE_YN` 이 N 인 건 숨긴 상품이므로 뺀다(2026-10-02 현재 전건 Y 라 실제로
걸러지는 건 0건이지만, 브랜드가 내린 걸 우리가 올리는 일은 없어야 한다).

robots.txt: `ginzaryoko.com` 은 `User-agent: * / Allow:/` 로 전체 허용.
`ginzaryoko.co.kr` 은 **robots.txt 가 404 이고 그 404 가 HTML 로 온다**
(`text/html`, 관리자 로그인 에러 페이지). 파일이 없는 것이지 막은 게 아니다.
이용약관: 두 도메인 어디에도 링크가 없다. 푸터는 사업자 정보뿐이다 —
`(주)긴자료코 / 762-81-02333 / 대표이사 원일호·김인교`. 확인하지 못했다는 뜻이다.
"""
import datetime
import time

from . import base
from .base import Item

BRAND = "긴자료코"
API = "https://ginzaryoko.co.kr/cms/api/signatureList.ajax"
IMG_ROOT = "https://ginzaryoko.co.kr/external-images/"
UPLOAD_PREFIX = "/home/cms/uploaded/"
PAGE_SIZE = 200      # 카테고리 최대가 17건이라 한 번에 받는다
DELAY = 1.5          # 요청 간격(초)

# 탭 onClick 의 키 → 화면 라벨. 응답의 CATEGORY 와도 일치한다(그쪽을 우선 쓴다).
CATEGORIES = {
    "tonkatsu": "돈까스",
    "rice":     "덮밥",
    "noodles":  "면",
    "curry":    "카레",
    "side":     "사이드",
}


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _image(path: str) -> str:
    """서버 파일시스템 경로를 공개 주소로. 접두가 다르면 이미지를 포기한다."""
    if not path or not path.startswith(UPLOAD_PREFIX):
        return ""
    return IMG_ROOT + path[len(UPLOAD_PREFIX):]


def _released_at(ms) -> str:
    """REG_DT(epoch ms) 를 날짜로. 값이 이상하면 비운다 — 지어내지 않는다."""
    if not isinstance(ms, (int, float)) or ms <= 0:
        return ""
    try:
        d = datetime.datetime.fromtimestamp(ms / 1000)
    except (OverflowError, OSError, ValueError):
        return ""
    # 서버가 0 이나 먼 미래를 주면 날짜로 쓰지 않는다.
    if not (2000 <= d.year <= datetime.date.today().year + 1):
        return ""
    return d.strftime("%Y-%m-%d")


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        for key, label in CATEGORIES.items():
            r = base.retry(lambda: c.post(API, json={
                "page": 1, "pageSize": PAGE_SIZE, "searchDiv": "0",
                "searchText": key}))
            r.raise_for_status()
            rows = (r.json().get("ServiceResult") or {}).get("LIST") or []
            # 키가 틀리면 에러가 아니라 빈 목록이 온다(docstring 참고).
            # 조용히 넘기면 카테고리 하나가 통째로 사라진 걸 아무도 모른다.
            if not rows:
                raise RuntimeError(
                    f"긴자료코 {label}({key}): 상품 0건 — 카테고리 키가 바뀌었을 수 있다")

            for x in rows:
                if x.get("VISIBLE_YN") == "N":
                    continue
                name = _clean(x.get("TITLE"))
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en=_clean(x.get("TITLE_EN")),
                    image=_image(x.get("THUMBNAIL_PATH")),
                    category=_clean(x.get("CATEGORY")) or label,
                    released_at=_released_at(x.get("REG_DT")),
                    # NEW 배지도 신메뉴 칸도 없다. 모름은 모름으로 둔다.
                    is_new=None,
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)

            time.sleep(DELAY)

    if not items:
        raise RuntimeError("긴자료코: 상품 0건 — API 응답 형식이 바뀌었다")
    return items
