"""버거킹.

www.burgerking.co.kr 은 Vue SPA 라 HTML 에는 아무것도 없다. 대신 bizMOB 프레임워크가
전문코드(trcode)별로 같은 오리진에 POST 하는 구조라, 그 전문을 직접 부르면 된다.
  POST https://www.burgerking.co.kr/burgerking/BKR0632.json
  Content-Type: application/x-www-form-urlencoded
  message={"header":{...,"trcode":"BKR0632"},"body":{"menuKeywordList":[]}}
전체 메뉴가 한 번에 오므로 요청은 딱 한 번이다. 쿠키·세션·토큰 불필요, 브라우저 불필요.
응답은 JSON(UTF-8). 헤더 result 가 false 면 실패다.

신제품 신호(2026-09-30 실측):
  - 각 메뉴의 menuFlagList 에 {"menuFlagPk":"01","menuFlagNm":"NEW"} 가 붙는다.
    화면 배지와 같은 값이라 이걸 is_new=True 로 쓴다. 전체 228건 중 71건.
  - 신메뉴 전용 목록은 없다. 키워드 필터(BKR0633 의 '신제품'·'신메뉴')가 있지만
    마케팅용 태그라 배지보다 신뢰도가 낮아 쓰지 않는다.
  - 출시일을 알려주는 필드는 목록에도 상세(BKR0634)에도 없다. released_at 은 못 채운다.
  - 이미지 URL 경로에 박힌 /2026/09/07/ 은 업로드 날짜라 uploaded_at 으로만 넣는다.
    전체로 보면 85건이 2025-01-06 한 날에 몰려 있지만(사이트 개편 때 일괄 업로드)
    NEW 71건은 전부 2026년 날짜로 흩어져 있어 이 범위에선 쓸 만하다.
  - 행사/할인 표시는 메뉴 전문에 없다(상세의 prmCd 는 전부 null). promo 는 못 채운다.

가격은 상세 전문(BKR0634)의 dineInprc 로 나오지만 Item 에 자리가 없어 버린다.
설명도 상세에 menuDesc 가 있으나 목록의 menuComponents 와 거의 같아 추가 호출을 안 한다.
"""
import json
import re

import httpx

from . import base
from .base import UA, Item

BRAND = "버거킹"
URL = "https://www.burgerking.co.kr/burgerking/BKR0632.json"
TRCODE = "BKR0632"
NEW_FLAG = "NEW"


def _message(body: dict) -> str:
    return json.dumps({
        "header": {"result": True, "error_code": "", "error_text": "", "info_text": "",
                   "message_version": "", "login_session_id": "", "trcode": TRCODE},
        "body": body,
    }, ensure_ascii=False)


def _uploaded_at(img_url: str) -> str:
    """이미지 경로의 /YYYY/MM/DD/ 가 업로드 날짜다."""
    m = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", img_url or "")
    return "-".join(m.groups()) if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client(headers={"Referer": "https://www.burgerking.co.kr/menu/main"}) as c:
        def call():
            r = c.post(URL, data={"message": _message({"menuKeywordList": []})},
                       headers={"Content-Type":
                                "application/x-www-form-urlencoded; charset=UTF-8"})
            r.raise_for_status()
            return r.json()

        res = base.retry(call)
        if not res.get("header", {}).get("result"):
            raise RuntimeError(f"BKR0632 실패: {res.get('header')}")

        for cat in res.get("body", {}).get("allMenuList") or []:
            category = (cat.get("menuCategoryNm") or "").strip()
            for m in cat.get("menuInfo") or []:
                labels = [(f.get("menuFlagNm") or "").strip()
                          for f in m.get("menuFlagList") or []]
                if NEW_FLAG not in labels:          # 배지 없는 건 신제품이 아니다
                    continue
                img = m.get("menuImgPath") or m.get("menuImgMPath") or ""
                it = Item(
                    brand=BRAND,
                    name=(m.get("menuNm") or "").strip(),
                    desc=(m.get("menuComponents") or "").strip(),
                    image=img,
                    labels=labels,
                    category=category,
                    uploaded_at=_uploaded_at(img),
                    is_new=True,
                )
                # 추천메뉴 카테고리가 다른 카테고리의 상품을 다시 담아서 겹친다.
                if it.name and it.key not in seen:
                    seen.add(it.key)
                    items.append(it)
    return items
