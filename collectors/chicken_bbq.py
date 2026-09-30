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

가격(menuPrice)·열량·알레르기 정보가 API 에 있지만 Item 에 담을 자리가 없어 버린다.
"""
import time

from . import base
from .base import Item

BRAND = "BBQ"
API = "https://www.bbq.co.kr/api/delivery"
MAX_CATEGORIES = 30  # 폭주 방지. 현재 8개.
DELAY = 0.3          # 요청 간격(초)


def _uploaded_at(client, img_url: str) -> str:
    """이미지의 Last-Modified 를 날짜로. 실패하면 조용히 비운다."""
    if not img_url:
        return ""
    try:
        r = client.head(img_url)
        lm = r.headers.get("last-modified", "")
    except Exception:
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
                    is_new=is_new,
                    # 세트 카테고리와 이름에 '세트'가 붙은 건 조합 상품이라 신제품이 아니다
                    promo=cat.get("categoryName") == "세트" or "세트" in name,
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)

        for it in items:
            time.sleep(DELAY / 2)
            it.uploaded_at = _uploaded_at(c, it.image)
    return items
