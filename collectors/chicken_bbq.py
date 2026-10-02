"""BBQ 치킨.

bbq.co.kr 은 Next.js 정적 export 라 HTML 에는 상품이 한 건도 없다. 화면은 같은
도메인의 /api/delivery/* 를 클라이언트에서 때려 채운다. 이 API 가 쿠키·토큰·리퍼러
없이 그냥 열려서 그쪽만 쓴다. 브라우저 불필요.

신메뉴 전용 카테고리는 없다. 대신 브랜드가 신제품 이름 앞에 '[NEW] ' 를 직접 붙인다.
그게 이 사이트에서 유일한 신제품 표시라 is_new 는 여기서만 뽑고, 접두사는 이름에서
떼어내 labels 로 옮긴다(배지가 떨어질 때 Item.key 가 바뀌어 신규로 오인되는 걸 막는다).
출시일을 알려주는 필드는 목록·상세 어디에도 없어서 released_at 은 비운다.

uploaded_at 은 이미지의 Last-Modified 로 채운다. 파일명에는 타임스탬프가 없고,
대다수가 2026-04-30(사이트 이관일)에 몰려 있어 강한 신호는 아니다. 다만 실제로 새로
올라온 건(필크런치 2026-07-21)은 출시일과 맞아떨어져서, 기준선 소급 용도로만 쓴다.

상품 페이지는 /products/<menu id> 다. 목록 응답의 id 가 그대로 경로 파라미터라
추가 요청 없이 조립만 하면 된다(번들의 /products/[id] 가 그 id 로 상세를 부른다).
정적 export 라 HTML 만 받으면 유효한 id 든 아니든 같은 껍데기가 오니, 검증은
브라우저 렌더로 했다.

가격(menuPrice)·열량·알레르기 정보가 API 에 있지만 Item 에 담을 자리가 없어 버린다.
"""
import time

from . import base
from .base import Item

BRAND = "BBQ"
SITE = "https://www.bbq.co.kr"
API = SITE + "/api/delivery"
MAX_CATEGORIES = 30  # 폭주 방지. 현재 8개.
DELAY = 0.3          # 요청 간격(초)


# 헤더가 없는 것과 우리 쪽이 죽은 것은 다르다. 앞은 정상이고(상시 메뉴는
# Last-Modified 를 안 주는 경우가 많다 — 실측 59%) 뒤는 그날 수집이 통째로
# 날짜를 잃는 사고다. 그런데 둘 다 빈 문자열로 끝나서 구분이 안 됐다.
# 던진 횟수를 세어 두고 fetch 끝에서 본다.
_HEAD_FAIL = 0
_HEAD_FAIL_MAX = 0.3   # 이 비율을 넘게 던지면 우리 쪽 문제로 본다


def _head_guard(tried: int) -> None:
    """HEAD 가 너무 많이 터졌으면 조용히 넘어가지 않는다."""
    if tried and _HEAD_FAIL / tried > _HEAD_FAIL_MAX:
        raise RuntimeError(
            f"이미지 HEAD {tried}건 중 {_HEAD_FAIL}건이 예외로 끝났다 "
            "— 날짜를 통째로 잃는 상태라 수집을 실패로 본다")


def _uploaded_at(client, img_url: str) -> str:
    """이미지의 Last-Modified 를 날짜로. 헤더가 없으면 빈 문자열."""
    global _HEAD_FAIL
    if not img_url:
        return ""
    try:
        r = client.head(img_url)
        lm = r.headers.get("last-modified", "")
    except Exception:
        _HEAD_FAIL += 1
        return ""
    if not lm:
        return ""
    from email.utils import parsedate_to_datetime
    try:
        return parsedate_to_datetime(lm).date().isoformat()
    except (TypeError, ValueError):
        return ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        cats = base.retry(lambda: c.get(f"{API}/menu/category")).json()
        for cat in cats[:MAX_CATEGORIES]:
            time.sleep(DELAY)
            menus = base.retry(
                lambda cid=cat["id"]: c.get(f"{API}/menu/{cid}")).json()
            for m in menus:
                name = " ".join((m.get("menuName") or "").split())
                if not name:
                    continue

                # 브랜드가 붙인 신제품 배지. 이름에서 떼어 labels 로 옮긴다.
                is_new = name.upper().startswith("[NEW]")
                if is_new:
                    name = name.split("]", 1)[1].strip()

                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=" ".join((m.get("description") or "").split()),
                    image=m.get("menuImageUrl") or "",
                    labels=["NEW"] if is_new else [],
                    category=cat.get("categoryName", ""),
                    is_new=is_new or None,   # 접두사 부재는 '아님'의 근거가 못 된다
                    url=f"{SITE}/products/{m['id']}" if m.get("id") else "",
                    # 이름 기준만 쓴다. '세트' 카테고리에는 단품도 섞여 있어서
                    # 카테고리로 잡으면 황금올리브 반마리 같은 단품 9건이 영구 제외된다.
                    # 세트는 promo 가 아니다(collect.drop_sets() 담당).
                    # BBQ 메뉴에는 할인·행사 표시가 없다.
                    promo=False,
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)

        for it in items:
            time.sleep(DELAY / 2)
            it.uploaded_at = _uploaded_at(c, it.image)
    _head_guard(sum(1 for it in items if it.image))
    return items
