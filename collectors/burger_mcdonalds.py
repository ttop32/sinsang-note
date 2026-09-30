"""맥도날드.

www.mcdonalds.co.kr 은 Nuxt3 SPA 라 HTML 에는 상품이 없지만, 화면이 쓰는 내부 JSON API 가
인증·토큰·Referer 없이 그냥 열린다. 브라우저 불필요.
  GET /api/v1/kor/category/list                                       → 카테고리 7개
  GET /api/v1/kor/product/product/list?page=1&view_rows=N&mainCategory={seq}
  GET /api/v1/kor/product/recommend/list                              → 추천 17건
subCategory 를 빼고 view_rows 를 키우면 카테고리 하나가 1요청에 다 온다. 요청은 총 9회.
robots.txt 는 200 text/plain 에 `Allow: /` 뿐이고 API 경로도 막지 않는다(can_fetch True).
웹 이용약관은 페이지 자체가 없다 — 푸터 법적 링크가 /kor/private(개인정보처리방침) 하나뿐이다.

신제품 신호(2026-09-30 실측):
  - regDate 가 진짜 등록일이다. 고추장버터 세트 2026-09-15, 빅맥® 세트 2019-05-30 처럼
    연식이 그대로 갈린다. 이미지 업로드 시각 같은 대용품이 아니라서 released_at 에 그대로 쓴다.
  - 다만 날짜가 `2026-September-15th` 라는 영문 서수 문자열이다. ISO 가 아니다.
    러너 로케일이 C 일 수 있어 %B 파싱에 기대지 않고 월 이름을 직접 표로 들고 있는다.
    같은 응답의 openTimeStart 는 `2026.September.17th 00:12` 로 오다가 recommend/list 에서는
    `2026-09-17 00:00` 로 온다. 백엔드가 두 포맷을 다 뱉는다는 뜻이라 ISO 도 같이 받아둔다.
  - newIcon(NEW 배지) 필드는 있고 번들에 렌더 코드도 있는데 전 건이 빈 문자열이다.
    상세 페이지의 '신메뉴' 글자는 스크린리더용 span 이고 아이콘 클래스가 비어 있어 화면에
    아무것도 안 뜬다(2019년 상품인 아메리카노 Medium 에도 똑같이 붙는다). 배지로 못 쓴다.
    그래서 is_new 는 None 으로 두고 신제품 판정은 collect 쪽 released_at 에 맡긴다.
  - 행사/할인은 카테고리로 잡는다. 맥런치("점심만의 특별한 할인")와 해피 스낵("할인 가격으로")은
    브랜드 스스로 할인 라인업이라고 쓴 카테고리다. 여기 실린 건 대부분 정규 메뉴의 할인가
    중복 등록이고, 그 중복 레코드의 regDate 는 상품 출시일이 아니라 할인 시작일이다.
    실제로 '불고기 버거'(단품)는 2003년부터 있던 상품인데 해피 스낵 레코드의 regDate 가
    2026-08-18 이다. 이걸 그대로 두면 신제품으로 올라간다.
    대신 같은 이름이 정규 카테고리에도 있으면 할인 전용 상품이 아니므로 promo 를 거둔다(_merge).
  - 세트/단품 구분은 promo 로 안 쓴다. menuStatus 를 labels 에 그대로 넘긴다.

url 은 /kor/menu/detail/{seq}/{rnum}/{subCategorySeq} 로 조립한다(추가 요청 없음).
번들(CRX-Smj4.js)의 카드 링크가 이 형태고, 세 값 모두 목록 응답에 들어 있다.
서버는 없는 경로에도 10KB 셸 HTML 을 200 으로 주므로 상태코드로는 검증이 안 된다.
브라우저로 직접 열어 확인했다: 843/1/16 → '맥크리스피™ 고추장 버터 세트',
28/1/9 → '아메리카노 Medium', 839/6/3 → '제주 풋귤 맥피즈 Medium' 렌더.
rnum·subCategorySeq 는 '다음 메뉴로 이동' 링크에만 쓰여서 값이 틀려도 상품은 seq 로 뜬다.

가격은 어느 응답에도 없다. 영양정보(calorie/allergyList/materialList)는 있으나 Item 에 자리가 없다.
"""
import html
import re
import time

from . import base
from .base import Item

BRAND = "맥도날드"
API = "https://www.mcdonalds.co.kr/api/v1/kor"
IMG = "https://www.mcdonalds.co.kr"          # Nuxt config 의 public.imgUrl
DETAIL = "https://www.mcdonalds.co.kr/kor/menu/detail/{seq}/{rnum}/{sub}"
VIEW_ROWS = 200   # 가장 큰 카테고리가 32건이다. 페이징을 안 돌려도 되게 넉넉히 준다.
MAX_CATEGORIES = 20   # 폭주 방지. 현재 7개.
DELAY = 2.0           # robots 에 Crawl-delay 는 없다. 요청이 9회뿐이라 여유를 둔다.

# 브랜드가 스스로 '할인'이라고 설명하는 카테고리. category/list 의 seq 다.
#   7 맥런치   "점심만의 특별한 할인으로 맥런치 세트를 즐겨보세요!"
#   8 해피 스낵 "시즌 별 인기 스낵을 하루종일 할인 가격으로 만나보세요!"
PROMO_CATEGORIES = {7, 8}

_MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June",
     "July", "August", "September", "October", "November", "December"], 1)}

# 2026-September-15th / 2026.September.15th 둘 다 받는다. 서수 접미는 있어도 없어도 된다.
_ORDINAL = re.compile(r"^(\d{4})[-.]([A-Za-z]+)[-.](\d{1,2})(?:st|nd|rd|th)?", re.I)
_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")

_BR = re.compile(r"<\s*/?\s*br\s*/?\s*>", re.I)
_TAG = re.compile(r"<[^>]+>")


def _date(s: str) -> str:
    """regDate 를 YYYY-MM-DD 로. 못 읽으면 빈 문자열(추측해서 채우지 않는다)."""
    s = (s or "").strip()
    m = _ISO.match(s)
    if m:
        return "-".join(m.groups())
    m = _ORDINAL.match(s)
    if not m:
        return ""
    year, name, day = m.groups()
    # 약어(Sept 등)로 바뀌어도 살아남게 앞 세 글자로도 한 번 더 찾는다.
    mon = _MONTHS.get(name.lower())
    if mon is None:
        cand = [v for k, v in _MONTHS.items() if k.startswith(name[:3].lower())]
        if len(cand) != 1:
            return ""
        mon = cand[0]
    return f"{year}-{mon:02d}-{int(day):02d}"


def _plain(s: str) -> str:
    """korName 에 <sub class=reg>™</sub>, korContent 에 <br> 이 박혀 있다. 벗긴다.

    <br> 만 공백으로 바꾸고 나머지 태그는 그냥 지운다. 전부 공백으로 바꾸면
    '맥크리스피™' 가 '맥크리스피 ™' 로 벌어지고, 전부 지우면 engName 의 <br> 3건에서
    앞뒤 단어가 붙어버린다.
    """
    return " ".join(html.unescape(_TAG.sub("", _BR.sub(" ", s or ""))).split())


def _merge(old: Item, new: Item) -> Item:
    """같은 상품이 여러 카테고리에 따로 등록돼 있다. 한 건으로 합친다.

    출시일은 가장 이른 것을 쓴다. 할인 카테고리의 중복 레코드는 regDate 가 할인 시작일이라
    늦게 찍힌다('아이스 드립 커피 Medium' 은 맥카페 2019-05-30 / 해피 스낵 2026-05-13).
    promo 는 등록된 카테고리가 전부 할인 카테고리일 때만 남긴다. 추천 목록은 카테고리가
    없어서 promo=False 로 들어오는데, 그것도 할인이 아닌 노출면이라 그대로 거둬도 맞다
    ('그리머스 쉐이크' 가 이 경로다 — 해피 스낵에만 있지만 추천에도 실려 있다).
    """
    promo = old.promo and new.promo
    keep = old if (not old.promo or new.promo) else new   # 정규 카테고리 쪽을 본으로
    drop = new if keep is old else old
    keep.promo = promo
    dates = sorted(d for d in (old.released_at, new.released_at) if d)
    keep.released_at = dates[0] if dates else ""
    # 본이 추천 레코드면 카테고리가 비어 있다. 버리는 쪽에 있는 값으로 메운다.
    for f in ("category", "desc", "name_en", "image"):
        if not getattr(keep, f) and getattr(drop, f):
            setattr(keep, f, getattr(drop, f))
    if not keep.labels and drop.labels:
        keep.labels = drop.labels
    return keep


def _item(p: dict, category: str, promo: bool) -> Item:
    seq = p.get("seq")
    image = p.get("pcImageUrl") or p.get("moImageUrl") or ""
    return Item(
        brand=BRAND,
        name=_plain(p.get("korName")),
        name_en=_plain(p.get("engName")),
        desc=_plain(p.get("korContent")),
        image=IMG + image if image else "",
        labels=[t for t in (p.get("menuStatus") or "").split(",") if t.strip()],
        category=category,
        released_at=_date(p.get("regDate")),
        promo=promo,
        url=DETAIL.format(seq=seq, rnum=p.get("rnum") or 1,
                          sub=p.get("subCategorySeq") or 0) if seq else "",
    )


def _list(c, path: str, **params) -> list:
    def call():
        r = c.get(f"{API}/{path}", params=params)
        r.raise_for_status()
        return r.json()

    res = base.retry(call)
    # 200 인데 본문이 에러인 경우가 이 프로젝트에서 여러 번 나왔다. resultCode 를 본다.
    if res.get("resultCode") != 100:
        raise RuntimeError(f"{path} 실패: {res.get('resultCode')} {res.get('resultMessage')}")
    return (res.get("resultObject") or {}).get("list") or []


def fetch() -> list[Item]:
    merged: dict[str, Item] = {}

    def add(it: Item) -> None:
        if not it.name:
            return
        old = merged.get(it.key)
        merged[it.key] = _merge(old, it) if old else it

    with base.client() as c:
        categories = _list(c, "category/list")[:MAX_CATEGORIES]
        if not categories:
            raise RuntimeError("category/list 가 비어 있다")

        for cat in categories:
            time.sleep(DELAY)
            seq = cat.get("seq")
            name = _plain(cat.get("korName"))
            for p in _list(c, "product/product/list", page=1,
                           view_rows=VIEW_ROWS, mainCategory=seq):
                add(_item(p, name, seq in PROMO_CATEGORIES))

        # 추천 목록에만 있고 카테고리 목록에는 안 나오는 상품이 있다(제주 풋귤 맥피즈 Medium).
        # 상세 페이지는 정상이라 빠뜨릴 이유가 없다. 카테고리는 알 수 없어 비운다.
        time.sleep(DELAY)
        for p in _list(c, "product/recommend/list"):
            add(_item(p, "", False))

    return list(merged.values())
