"""한솥(한솥도시락).

가맹점 811개로 공정위 `한식` 업종 2위다(2025년도 정보공개서, 2024년 말 기준.
1위 본죽&비빔밥은 이미 수집 중이다).

메뉴 화면(`/menu/menu_list`)의 HTML 에는 상품이 없고 분류 탭만 있다. 상품은
jQuery 가 내부 API 로 따로 받아온다. 그 API 는 **POST 전용**이라 GET 은 405 다.

  POST www.hsd.co.kr/api/menu/menu_list/<cate1>/<cate2>
      Content-Type: application/json; charset=utf-8
      X-CSRF-TOKEN: <메뉴 페이지 <meta name="_csrf"> 값>

**⚠️ CSRF 토큰 없이 POST 하면 403 이다.** 조사 문서(`notes/CANDIDATES-KOREAN.md`)가
"POST 전용 내부 API" 까지만 적고 멈춘 게 이 403 때문인데, 봇 차단이 아니라
Spring Security 의 평범한 CSRF 방어다. 메뉴 페이지가 `<meta name="_csrf_header"
content="X-CSRF-TOKEN">` 와 `<meta name="_csrf" content="...">` 로 토큰을 그대로
내놓고, 같은 세션(JSESSIONID)으로 그 헤더를 붙이면 200 이 온다. UA 를 위장하지
않았고 로그인도 필요 없다. 2026-10-02 실측.

분류 쌍 (cate1, cate2) 은 메뉴 페이지의 `showMenuList('1', '63')` 호출에서
읽는다. 상수로 박아두면 브랜드가 분류를 바꿀 때 조용히 빠지므로 매번 읽는다.
2026-10-02 현재 19쌍, 중복 제거 후 상품 111건.

신제품 신호가 둘이고 서로 교차검증된다. 2026-10-02 실측:
  is_new  `newYn` Y/N 이 상품마다 붙는다. 111건 중 Y 8건 / N 103건, 빈 값 0건.
          본아이에프와 같은 급으로 **True 와 False 를 양쪽 다 확정할 수 있다.**
  교차검증 cate1=1 이 '신메뉴', 그 아래 cate2=63 이 '10월 신메뉴' 라는 별도 분류다.
          거기 실린 6건이 전부 `newYn=Y` 였다. 세븐일레븐 '신상품' 탭처럼
          분류만 다르고 목록은 같은 가짜가 아니다 — 신메뉴 분류 6건은 전체
          111건 중 6건뿐이고, 나머지 105건은 Y 2건을 빼고 전부 N 이다.
          (Y 8 ⊃ 신메뉴분류 6. 신메뉴 분류에 아직 안 올라간 Y 가 2건 있다.)

  uploaded_at  `imagePath` 파일명이 `<32자리 hex><YYYYMMDDHHMMSS>.jpg` 다.
          111건 전부 14자리가 파싱되고, 범위는 2019-01-09 ~ 2026-09-30 으로
          **미래 날짜가 하나도 없다.** 연도 분포도 2026년 55건 / 2025년 23건 /
          2022년 15건 … 으로 꾸준히 쌓인 모양이다. 에그드랍 때처럼 epoch 로
          착각해 미래가 섞이는 사고는 여기선 없다.
          **다만 released_at 에는 넣지 않는다.** 브랜드가 "출시일"이라고 말한
          값이 아니라 이미지를 올린 시각이다(본아이에프 cmdtListImg 와 같은 처분).
          실제로 10월 신메뉴 6건의 이미지 시각은 09-23 ~ 09-30 으로 출시 직전이다.

released_at 은 **못 채운다.** 응답 필드가 idx/title/subTitle/price/sideDishCount/
series/imagePath/calorie/al1~al18/optionMenu/cate1/cate2/newYn/detailImg/subMenu/
origins 로 끝이고 날짜 항목이 아예 없다. 상세(`/menu/menu_view/<idx>`)도 받아
확인했는데 날짜가 없다. 지어내지 않고 비운다.

가격(price)·열량(calorie)·알레르기(al1~al18)는 Item 에 자리가 없어 버린다.

이용약관: 푸터 `/etc/terms` 에 제16조①11호(자동화 수단 접근)·제17조① 제한
조항이 있다. 운영자 판단으로 수집하되 삭제 요청이 오면 다투지 말고 내린다
(이마트24·도미노피자와 같은 처분).
"""
import json
import re
import time

from . import base
from .base import Item

BRAND = "한솥"
HOST = "https://www.hsd.co.kr"
LIST_URL = HOST + "/menu/menu_list"
API = HOST + "/api/menu/menu_list/{}/{}"
VIEW_URL = HOST + "/menu/menu_view/{}?cate1={}&cate2={}"
DELAY = 1.0          # 요청 간격(초)
MAX_PAIRS = 60       # 폭주 방지. 현재 19쌍.

_PAIR = re.compile(r"showMenuList\('(\d+)',\s*'(\d+)'\)")
_CSRF = re.compile(r'name="_csrf"\s+content="([^"]+)"')
# 이미지 파일명 꼬리의 업로드 시각. 32자리 hex 뒤에 YYYYMMDDHHMMSS 가 붙는다.
_STAMP = re.compile(r"(\d{4})(\d{2})(\d{2})\d{6}\.[a-zA-Z]+$")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _uploaded_at(img: str) -> str:
    """이미지 파일명 꼬리의 업로드 날짜. 출시일이 아니라서 released_at 엔 안 넣는다."""
    m = _STAMP.search(img or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen_idx, keys = set(), set()
    with base.client(headers={"Referer": LIST_URL}) as c:
        r = base.retry(lambda: c.get(LIST_URL))
        r.raise_for_status()

        m = _CSRF.search(r.text)
        if not m:
            raise RuntimeError("한솥: CSRF 토큰(<meta name=\"_csrf\">)을 못 찾았다 "
                               "— 페이지 구조가 바뀌었으면 POST 가 전부 403 이 된다")
        headers = {
            "Accept": "application/json; charset=utf-8",
            "Content-Type": "application/json; charset=utf-8",
            "X-CSRF-TOKEN": m.group(1),
        }

        pairs, order = [], set()
        for c1, c2 in _PAIR.findall(r.text):
            if (c1, c2) not in order:
                order.add((c1, c2))
                pairs.append((c1, c2))
        if not pairs:
            raise RuntimeError("한솥: 분류 쌍 0개 — showMenuList() 호출이 사라졌다")

        for c1, c2 in pairs[:MAX_PAIRS]:
            rr = base.retry(lambda: c.post(API.format(c1, c2), headers=headers))
            rr.raise_for_status()
            data = json.loads(rr.content.decode("utf-8-sig"))
            time.sleep(DELAY)

            cate1 = _clean((data.get("cate1Info") or {}).get("name"))
            for sub in data.get("subdata") or []:
                cate2 = _clean((sub.get("cate2Info") or {}).get("name"))
                for g in sub.get("goodsList") or []:
                    idx = g.get("idx")
                    name = _clean(g.get("title"))
                    if idx in seen_idx or not name:
                        continue
                    seen_idx.add(idx)
                    img = g.get("imagePath") or ""
                    new = g.get("newYn")
                    it = Item(
                        brand=BRAND,
                        name=name,
                        desc=_clean(g.get("subTitle")),
                        image=img,
                        # '신메뉴' 는 판매채널이지 상품 분류가 아니다. 그 상품이
                        # 다음 달에 어느 칸으로 갈지는 모르므로 분류를 비운다.
                        category="" if cate1 == "신메뉴" else (cate2 or cate1),
                        uploaded_at=_uploaded_at(img),
                        is_new=True if new == "Y" else False if new == "N" else None,
                        url=VIEW_URL.format(idx, c1, c2),
                    )
                    # cate1='신메뉴' 와 본래 분류에 같은 상품이 겹쳐 실린다.
                    # idx 는 달라도 Item.key 가 같은 쌍이 나올 수 있어 한 번 더 턴다.
                    if it.key in keys:
                        continue
                    keys.add(it.key)
                    items.append(it)

    if not items:
        raise RuntimeError("한솥: 상품 0건 — API 응답 형태가 바뀌었을 수 있다")
    return items
