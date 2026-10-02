"""홍익돈까스. 가맹점 88개 — 돈까스 업종 8위.

식스샵(Sixshop) 사이트다. 조사 문서(CANDIDATES-WESTERN §3)가 "RequireJS SPA, 렌더
529자, 상품 API 를 못 찾았다"며 **불가**로 적어뒀는데, 2026-10-02 재실측으로 **뒤집힌다.**
불가로 본 건 `/menu` 한 장만 봤기 때문이다. `/menu` 는 진짜로 빈 허브 페이지고,
상품은 거기 링크된 **여섯 개 하위 페이지에 SSR 로 들어 있다.**

  /menu_2021_porkcutlet  돈까스   /menu_2021_udon     우동
  /menu_2021_rice        밥       /menu_2021_pasta    파스타
  /menu_2021_side        사이드   /menu_2021_takeout  포장

6요청에 40건. API 가 아니라 식스샵이 뱉은 HTML 을 읽는다. 브라우저 불필요.

**신제품 신호는 이미지 파일명의 epoch 밀리초뿐이다.** NEW 배지도 '신메뉴' 칸도 없고
(전 페이지에서 `NEW`·`신메뉴` 문자열이 0건) 등록일 필드도 없다.
식스샵은 업로드한 파일을 `image_<epoch_ms>.png` 로 저장한다.

  2024-11-08  21건   ← 메뉴판 일괄 교체
  2025-05-15   6건   파스타 6종
  2026-01-05   2건   고구마치즈롤까스 · 치즈롤까스
  2026-02-03   6건   스파이시어니언돈까스 · 카레등심/안심까스 · 치즈까스 · 바삭콘크랩 · 크랩샌드
  2026-02-26   1건   알리오올리오
  2026-03-05   2건   해물볶음우동 · 볶음짬뽕
  2026-04-15   3건   냉모밀 · 애플망고에이드 · 핑크레몬에이드
  2026-09-03   2건   새우볶음밥 · 불고기볶음밥
  (+ 포장 4건은 2022-06·2023-08 이라 이 분포 밖이다)

띄엄띄엄 계속 올라온다 — 할리스·노브랜드버거처럼 한 날짜로 뭉개진 경우가 아니다.
그래서 신호로 쓰되 **`uploaded_at` 까지만이다. `released_at` 로 올리지 않는다.**
⚠️ 이건 **사진을 올린 시각**이다. 브랜드가 기존 상품 사진만 다시 찍어 올려도 날짜가
   새로 찍힌다. 즉 **가짜 신상이 섞일 수 있는 신호**다. 경로명이 `menu_2021_` 로
   2021년에 멈춰 있는 사이트라 메뉴 자체는 거의 안 바뀐다는 점도 같이 보라.
   더 강한 신호가 생기면(브랜드가 NEW 배지를 달면) 그쪽으로 갈아타라.
`is_new` 는 비운다(None).

마크업은 식스샵 페이지빌더 구조다. `div.customSectionColumn` 안에서
`div.item-wrapper.image`(상품 사진) 다음에 `div.item-wrapper.text-body` 또는
`.text-title`(이름·가격)이 오는 짝이 반복된다. 한 칸에 짝이 둘 들어가기도 한다.
그래서 칸을 통째로 `css_first` 하면 안 되고 **문서 순서대로 훑으며 짝을 지어야 한다.**
처음에 `css_first` 로 짰다가 우동 페이지에서 홍익우동·소우동을 통째로 놓쳤다.
사진 태그도 두 모양이다 — `<div class='img' imgSrc=…>` 와 `<img class='img' imgSrc=…>`.
밥 페이지가 후자라 `div.img[imgSrc]` 로는 2건이 날짜를 통째로 잃었다. 속성으로 잡는다.

이름은 텍스트 블록의 `<p>` 줄들에서 고른다. 한 블록에 상품이 둘 들어간 경우가 있어
(`홍익우동 / 6,000원 / 소우동 / 3,500원`) 가격 줄을 건너뛰고 **남는 줄을 전부 이름으로**
본다. 버리는 줄: 가격만 있는 줄, `*`(주의문구)·`(`(맛 옵션)으로 시작하는 줄,
`:` 가 든 줄(`사이즈업 : 22,000원`). `<…>` 로 감싼 줄은 구성 설명이라 desc 로 돌린다
(포장 도시락 4건). 이름 끝에 가격이 붙어 오는 줄은 꼬리를 떼어낸다(`까르보나라 14,000원`).

Item.url 은 **상세 링크를 쓰지 않는다.** 카드마다 `<a href="/seta">` 같은 링크가
붙어 있는데 브랜드가 섹션을 재활용하면서 갱신을 안 해, `스파이시어니언돈까스` 가
`/seta`(세트A) 를 가리키는 식으로 **실제로 어긋나 있다.** 틀린 주소를 거느니 카테고리
페이지로 보낸다.

가격은 Item 에 자리가 없어 버린다.

robots.txt: 200 `text/plain`. `Allow: /` 이고 `/policy`·`/privacy` 만 Disallow.
우리가 받는 `/menu_2021_*` 는 허용 범위다.
이용약관: 푸터에 `/policy` 링크가 있는데 **robots 가 그 경로를 막는다.** 그래서
받지 않았고 **확인하지 못했다**(미소야 `/?mode=policy` 와 같은 상황).
"""
import datetime
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "홍익돈까스"
HOST = "https://www.hongikdonkatsu.com"
IMG_ROOT = "https://contents.sixshop.com/thumbnails"
IMG_SIZE = "_1000"      # 식스샵 썸네일 크기 접미. 원본은 /uploadedFiles/ 쪽이다
DELAY = 1.5             # 요청 간격(초)

# 경로 조각 → 화면 분류. 경로가 `menu_2021_` 로 굳어 있어 그대로 적는다.
PAGES = {
    "porkcutlet": "돈까스",
    "udon":       "우동",
    "rice":       "밥",
    "pasta":      "파스타",
    "side":       "사이드",
    "takeout":    "포장",
}

_EPOCH = re.compile(r"image_(\d{13})")
_PRICE_ONLY = re.compile(r"^[\d,]+\s*원?$")
_TAIL_PRICE = re.compile(r"\s*[\d,]{3,}\s*원?$")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _uploaded_at(src: str) -> str:
    """이미지 파일명의 epoch 밀리초를 날짜로. 값이 이상하면 비운다."""
    m = _EPOCH.search(src or "")
    if not m:
        return ""
    try:
        d = datetime.datetime.fromtimestamp(int(m.group(1)) / 1000)
    except (OverflowError, OSError, ValueError):
        return ""
    if not (2000 <= d.year <= datetime.date.today().year + 1):
        return ""
    return d.strftime("%Y-%m-%d")


def _image(src: str) -> str:
    """`/uploadedFiles/…/image_x.png` → 식스샵 썸네일 절대주소."""
    if not src.startswith("/uploadedFiles/"):
        return ""
    stem, dot, ext = src.rpartition(".")
    return f"{IMG_ROOT}{stem}{IMG_SIZE}{dot}{ext}" if dot else ""


def _parse_text(block) -> tuple:
    """텍스트 블록에서 (이름들, 구성설명). 한 블록에 상품이 둘 있을 수 있다."""
    names, desc = [], ""
    for p in block.css("p"):
        s = _clean(p.text())
        if not s:
            continue
        if s.startswith("<") and s.endswith(">"):   # <등심돈까스 + 생선까스> = 구성
            desc = desc or s.strip("<>").strip()
            continue
        if s[0] in "*(" or ":" in s:                # 주의문구·맛 옵션·사이즈업
            continue
        if _PRICE_ONLY.match(s):
            continue
        s = _TAIL_PRICE.sub("", s).strip()          # `까르보나라 14,000원`
        if len(s) >= 2:
            names.append(s)
    return names, desc


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        for slug, label in PAGES.items():
            url = f"{HOST}/menu_2021_{slug}"
            r = base.retry(lambda: c.get(url))
            r.raise_for_status()

            found = 0
            for col in HTMLParser(r.text).css("div.customSectionColumn"):
                src = ""
                # 칸 안을 문서 순서대로 훑으며 (사진, 텍스트) 짝을 짓는다.
                for w in col.css("div.item-wrapper"):
                    cls = (w.attributes.get("class") or "").split()
                    if "image" in cls:
                        node = w.css_first("[imgsrc]")   # div.img / img.img 둘 다
                        src = (node.attributes.get("imgsrc") or "") if node else ""
                        continue
                    if "text-body" not in cls and "text-title" not in cls:
                        continue
                    names, desc = _parse_text(w)
                    for name in names:
                        it = Item(
                            brand=BRAND,
                            name=name,
                            desc=desc,
                            image=_image(src),
                            category=label,
                            # 사진 올린 날이다. 출시일이 아니다(docstring 경고 참고).
                            uploaded_at=_uploaded_at(src),
                            is_new=None,
                            url=url,
                        )
                        if it.key in seen:
                            continue
                        seen.add(it.key)
                        items.append(it)
                        found += 1

            if not found:
                raise RuntimeError(f"홍익돈까스 {label}({slug}): 상품 0건 — 셀렉터가 깨졌다")
            time.sleep(DELAY)

    if not items:
        raise RuntimeError("홍익돈까스: 상품 0건")
    return items
