"""탐앤탐스.

1차 조사에서 tomntoms.com / www.tomntoms.com / www.tomntoms.co.kr **3개 호스트
전부 TLS 실패**로 '수집 불가(기술)' 판정이 났었다. 다시 보니 **판정이 틀렸다.**
서버가 중간 인증서를 안 내려줘서 체인 검증이 깨지는 것뿐이고,
`base.client(verify=False)` 로 열면 멀쩡히 200 이 온다(또래오래·노랑통닭과 같은 사정).
⚠️ `httpx.Client(transport=..., verify=...)` 는 transport 가 있으면 verify 를 조용히
무시한다. 반드시 `base.client(verify=False)` 를 써야 한다.

www.tomntoms.com 은 React/Vite SPA 라 HTML 이 1.8KB 짜리 껍데기다. 화면이 쓰는 내부
API 가 인증·토큰·Referer 없이 그냥 열린다. 번들 `/assets/index-*.js` 안에
`baseURL:"https://www.tomntoms.com/api"` 가 박혀 있고 메뉴 호출은 네 개다.
  GET /api/v1/menu/drink?page=N&category=&search=    음료 127건
  GET /api/v1/menu/food?page=N&category=&search=     푸드  40건
  GET /api/v1/menu/md?page=N&category=&search=       MD   37건
  GET /api/v1/menu/new?page=N&search=                신메뉴 36건
페이지당 12건 고정이고 **응답에 총건수·마지막페이지 표시가 없다**(`data` 키가
`elements` 하나뿐이다). 그래서 빈 페이지가 올 때까지 돌고 MAX_PAGES 로 막는다.

tomntoms.co.kr 은 **다른 사업**이다 — 그누보드로 만든 '커피케이터링·커피트럭' 사이트고
메뉴 카탈로그가 아니다. 호스트 이름만 보고 같은 사이트로 착각하면 안 된다.

신제품 신호(2026-10-02 실측):
  - 각 상품에 `isNew` 불리언이 있다. 그리고 `/v1/menu/new` 라는 전용 엔드포인트가
    따로 있다. **둘이 같은 집합인지 전수로 대조했다** — 세븐일레븐에서 '신상품' 탭이
    다른 엔드포인트로 같은 목록을 불러 뱃지가 없던 전례 때문이다.
    drink+food+md 204건 중 `isNew=true` 가 36건, `/v1/menu/new` 가 36건,
    **두 집합이 id 기준으로 완전히 일치**했다(차집합 양쪽 0). 가짜가 아니다.
    그래서 new 엔드포인트는 안 때리고 목록 세 개만 받아 `isNew` 를 그대로 쓴다.
  - 비율은 36/204 = 17.6% 다. 버거킹(31%)처럼 과하지 않고, MD 는 37건 전부
    `isNew=false` 라 플래그가 살아 움직인다는 것도 확인된다.
  - `isNew=false` 는 브랜드가 '신제품 아님' 이라고 말한 것이므로 is_new=False 로
    그대로 내보낸다(모름이 아니다).

날짜는 이미지 파일명의 13자리 ms 타임스탬프에서 얻는다. 경로가 두 모양으로 섞여
있어서(`/uploads/menu/{id}/{ts}_…` 와 `/uploads/menu/{ts}_…`) 둘 다 잡아야 한다.
처음에 앞의 것만 잡았더니 날짜가 붙는 신메뉴가 36건 중 7건뿐이었다.
  - 둘 다 잡으면 204건 중 **97건**에 날짜가 붙고, **신메뉴 36건은 전건** 붙는다.
  - ⚠️ 다만 **2025-05-15 에 40건, 2025-05-14 에 16건** 이 몰려 있다. 56건이
    한꺼번에 올라간 **일괄 재업로드**지 출시일이 아니다. 컴포즈커피 Last-Modified 가
    2026-06-16 에 149건 몰렸던 것과 같은 함정이라 이 두 날짜는 **버린다**.
  - 남는 값들은 흩어져 있고(2026-04-03 8건, 2025-11-20 8건, 2026-01-08 7건,
    2026-09-08 6건 …) 신메뉴와도 아귀가 맞는다 — 가을 신메뉴 '쑥 팥 슈페너' 등이
    2026-09-08, '오트 오곡 라떼' 가 2026-08-25.
  - 이건 업로드 시각이지 출시일이 아니므로 `uploaded_at` 에 넣는다.
    released_at 은 어디에도 없으므로 비운다. 지어내지 않는다.

MD 탭(텀블러·머그 등 굿즈)은 먹는 게 아니라 `nonfood=True` 로 표시한다.
이름만 보는 base.is_nonfood 로는 '블랙 보온병' 같은 게 새기 때문에 업체 분류를 믿는다.

가격은 어느 응답에도 없다. 영양정보(nutritional_ingredients)는 있으나 Item 에 자리가 없다.
상품 상세 주소도 SPA 라우트뿐이라 Item.url 은 비우고 SITES 폴백에 맡긴다.
"""
import datetime
import re
import time

from . import base
from .base import Item

BRAND = "탐앤탐스"
API = "https://www.tomntoms.com/api/v1/menu"
KINDS = ("drink", "food", "md")      # new 는 isNew 와 같은 집합이라 안 때린다
MD = "md"                            # 굿즈 탭
MAX_PAGES = 40                       # 폭주 방지. 현재 가장 큰 drink 가 11페이지.
DELAY = 2.0
OK_CODE = "0000"
END_CODE = "9999"   # 마지막 페이지를 넘기면 200 + code 9999 'Not found Data'

# 이미지 파일명의 13자리 ms 타임스탬프. 경로가 두 모양으로 섞여 있다 —
# `/uploads/menu/{id}/{ts}_….png` 와 상품 폴더 없이 `/uploads/menu/{ts}_….png`.
# 처음에 앞의 것만 잡았더니 날짜가 붙는 신메뉴가 7건에서 멈췄다. 둘 다 잡는다.
_TS = re.compile(r"/menu/(?:\d+/)?(\d{13})_")

# 일괄 재업로드일. 이 날짜의 56건은 출시일이 아니다(docstring 참고).
BULK_UPLOAD_DAYS = {"2025-05-14", "2025-05-15"}


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _uploaded(image: str) -> str:
    """이미지 파일명의 타임스탬프를 YYYY-MM-DD 로. 없거나 일괄업로드면 빈 문자열."""
    m = _TS.search(image or "")
    if not m:
        return ""
    day = datetime.datetime.fromtimestamp(int(m.group(1)) / 1000).strftime("%Y-%m-%d")
    return "" if day in BULK_UPLOAD_DAYS else day


def _item(p: dict, kind: str) -> Item:
    image = p.get("image") or ""
    cat = (p.get("category") or {}).get("name") or ""
    return Item(
        brand=BRAND,
        name=_clean(p.get("title")),
        name_en=_clean(p.get("titleEn")),
        desc=_clean(p.get("description")),
        image=image,
        category=cat,
        uploaded_at=_uploaded(image),
        is_new=bool(p.get("isNew")),
        nonfood=(kind == MD),
    )


def _page(c, kind: str, page: int) -> list:
    def call():
        r = c.get(f"{API}/{kind}", params={"page": page, "category": "", "search": ""})
        r.raise_for_status()
        return r.json()

    res = base.retry(call)
    # 마지막 페이지를 넘기면 200 에 code 9999 'Not found Data' 가 온다.
    # 총건수를 안 주는 API 라 이게 유일한 끝 신호다. 빈 목록으로 바꿔 돌려준다.
    if res.get("code") == END_CODE:
        return []
    # 200 인데 본문이 에러인 경우가 이 프로젝트에서 여러 번 나왔다. code 를 본다.
    if res.get("code") != OK_CODE:
        raise RuntimeError(f"{kind} p{page} 실패: {res.get('code')} {res.get('message')}")
    return (res.get("data") or {}).get("elements") or []


def fetch() -> list[Item]:
    items: list[Item] = []
    seen: set[int] = set()

    # 중간 인증서를 안 내려주는 서버다. docstring 참고.
    with base.client(verify=False) as c:
        for kind in KINDS:
            for page in range(1, MAX_PAGES + 1):
                if items:
                    time.sleep(DELAY)
                rows = _page(c, kind, page)
                if not rows:
                    break
                fresh = [p for p in rows if p.get("id") not in seen]
                # 범위를 넘긴 page 를 서버가 같은 페이지로 되돌려주는 경우를 막는다
                if not fresh:
                    break
                for p in fresh:
                    seen.add(p.get("id"))
                    it = _item(p, kind)
                    if it.name:
                        items.append(it)

    # 세 탭을 다 받으면 200건 안팎이다. 크게 모자라면 파라미터가 바뀐 것이다.
    if len(items) < 100:
        raise RuntimeError(f"탐앤탐스 {len(items)}건 — 메뉴 API 가 바뀌었을 수 있다")
    return items
