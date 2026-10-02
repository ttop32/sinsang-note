"""보배반점 — 보도자료에서 신제품과 출시일을 뽑는다.

공정위 `중식` 업종 가맹점 수 **4위**(198개, 2024년 말). (주)보배에프앤비.

**메뉴 페이지는 쓸 수 없다.** `/menu/main.php`(면/밥류·요리류·사이드/주류)는 상품을
SSR 로 내려주긴 하는데 **NEW 배지도 날짜도 없다.** 짜장면·짬뽕·탕수육 같은 상시
메뉴가 전부라, 긁으면 메뉴판 전체가 '신상' 으로 올라간다. 중식집 메뉴판은 거의
안 바뀌므로 그건 이 서비스가 하면 안 되는 일이다. 그래서 메뉴 페이지는 안 본다.

남은 경로는 보도자료고, 이건 GS25·오뚜기·오리온과 **같은 종류의 소스**다.

수집 경로. 2026-10-02 실측:
  - 목록 `/community/news.php?page=N` 이 SSR 이다. 쿠키·토큰 없이 열린다.
    한 페이지 16건, 5페이지(≈80건, 2024-09~).
  - **목록 한 장에 제목·날짜·이미지가 다 있다.** 카드가
      `<a class="box" href=".../news_detail.php?id=256">`
        `<div class="box-img" style="background: url('…')">`
        `<div class="box-title">[보도기사] 보배반점 ‘크림짬뽕’ 간편식 출시…</div>`
        `<div class="box-date">2026-09-15</div>`
    꼴이라 **제목이 잘리지 않는다**(오리온·탕화쿵푸와 다른 점이다).
  - 이미지는 `style="background: url('https://…')"` 안에 있다. `<img>` 가 아니다.
    파일명이 한글이고 공백이 없어서 그대로 쓸 수 있다.

그래도 **상세를 한 번씩 받는다.** 상품명을 제목과 본문으로 **교차검증**하기
위해서다(탕화쿵푸·춘리 어댑터와 같은 규칙).
  ① 본문에서 ‘…’ 로 인용된 이름을 모으고
  ② 그중 **제목에도 글자 그대로 있는 것만** 채택한다.
한쪽에만 있는 건 버린다. 이 게시판은 따옴표를 아주 자주 쓰는데 그 안이
'보배그린하트'(사회공헌), '마켓보배'(스마트스토어), '2026 올해의 브랜드 대상'(수상),
'빵빵이와 옥지의 중식야차'(프로모션 협업) 처럼 **상품이 아닌 경우가 대부분**이다.
최근 3페이지(≈48건)를 돌려 남은 건 **3건**이다 — 크림짬뽕(2026-09-15, HMR),
바질크림짬뽕·마라크림짬뽕(2026-04-27, 매장 신메뉴). 전건 본문을 열어 실제 제품이
맞는지 확인했다(오집 0건). 같은 제품을 다른 매체가 쓴 중복 기사도 걸러진다.

⚠️ **'크림짬뽕' 은 매장 메뉴가 아니라 간편식(HMR)이다.** 마이셰프와 공동개발해
   컬리에서 단독 판매하는 550g 냉동식품이다. 그래도 담는 이유는, 이 프로젝트가
   hy프레딧·아워홈처럼 **브랜드가 '출시'라고 선언한 신제품**을 담기 때문이다.
   매장 메뉴만 담는다는 규칙은 이 레포에 없다. 판단이 바뀌면 _SKIP 에 '간편식'을
   넣으면 바로 빠진다.
⚠️ 같은 제품을 다른 매체가 쓴 기사가 2건 올라온다('크림짬뽕' 9-15 두 건).
   base.make_key() 가 이름으로 묶어 주지만 어댑터에서도 한 번 더 턴다.

수집량은 **연 1~2건**이다. 그래도 날짜가 정확하고 브랜드가 직접 '출시'라고 말한
건이라 신뢰도는 높다.

robots: `bobaebanjum.co.kr/robots.txt` → 200, text/plain. 본문이 두 줄뿐이다 —
        `User-agent: Yeti` / `Allow:/`. ⚠️ **`User-agent: *` 규칙이 없다**(춘리마라탕과
        똑같다). 네이버 봇만 명시 허용했고 우리에 해당하는 규칙이 없으니 금지도
        아니다. 그래도 허용이라 적힌 것도 아니라서 요청 간격을 길게 잡는다.
약관: 푸터에 개인정보처리방침·회사소개만 있고 **이용약관 페이지가 없다**.
      수집·복제를 금지하는 문구는 찾지 못했다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "보배반점"
SITE = "https://bobaebanjum.co.kr"
LIST = SITE + "/community/news.php"
MAX_PAGES = 3        # 한 페이지 16건. 3페이지면 1년 반쯤 된다
DAYS = 300
DELAY = 2.2

# 상품 기사인가. 이 말이 없으면 상세를 받지 않는다.
_LAUNCH = re.compile(r"(출시|선봬|선보|론칭|신메뉴|신제품|판매)")

# 상품 기사가 아닌데 위 동사를 쓰는 것들. 실측 제목으로 뽑았다.
_SKIP = ("대상", "수상", "선정", "오픈", "공모전", "이벤트", "나눔", "진출",
         "개편", "새단장", "매뉴얼", "강화", "고도화", "성료", "프로모션",
         "창업", "채용", "표준화")

_QUOTED = re.compile(r"[‘'`]([^’'`\n]{2,40})[’'`]")

# 따옴표 안이 상품이 아닌 것들.
_NOT_PRODUCT = ("보배그린하트", "마켓보배", "대상", "브랜드", "프랜차이즈", "미래",
                "이벤트", "캠페인", "점", "협업", "일상")

_IMG = re.compile(r"url\(\s*['\"]?(https://[^'\")]+)")


def _text(node) -> str:
    return " ".join(node.text().split()) if node else ""


def _date(s: str) -> str:
    m = re.search(r"(20\d{2})-(\d{1,2})-(\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    return f"{y:04d}-{mo:02d}-{d:02d}" if 1 <= mo <= 12 and 1 <= d <= 31 else ""


def _names(title: str, body: str) -> list:
    """제목과 본문을 교차검증해 상품명을 뽑는다. 못 고르면 빈 목록."""
    t = " ".join(title.split()).replace("[보도기사]", " ")
    if any(w in t for w in _SKIP) or not _LAUNCH.search(t):
        return []
    flat = t.replace(" ", "")
    out, seen = [], set()
    for m in _QUOTED.finditer(body):
        name = m.group(1).strip(" ,·∙")
        # 본문은 '보배반점 크림짬뽕' 처럼 브랜드명을 붙여 부르기도 한다. 떼고 본다.
        name = re.sub(r"^보배반점\s*", "", name).strip()
        # 제목이 두 상품을 '·' 로 묶어 한 따옴표 안에 넣는 경우가 있다
        # ('바질크림짬뽕·마라크림짬뽕'). 묶음은 버린다 — 본문이 각각을 따로
        # 부르므로 개별 상품은 아래 반복에서 따로 잡힌다(오리온 _pick 과 같은 규칙).
        if len(name) < 2 or any(c in name for c in "·∙&?"):
            continue
        if any(w in name for w in _NOT_PRODUCT):
            continue
        if name.replace(" ", "") not in flat or name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def _rows(html: str) -> list:
    """목록 한 페이지 → [(날짜, 상세URL, 제목, 이미지)]."""
    out = []
    for a in HTMLParser(html).css("a.box"):
        href = a.attributes.get("href", "")
        title = _text(a.css_first(".box-title"))
        when = _date(_text(a.css_first(".box-date")))
        box = a.css_first(".box-img")
        m = _IMG.search(box.attributes.get("style", "")) if box else None
        if href and title and when:
            out.append((when, href, title, m.group(1) if m else ""))
    return out


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    cand, stop = [], False
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"page": page}))
            r.raise_for_status()
            rows = _rows(r.text)
            # 1페이지가 비면 마크업이 바뀐 것이다. 조용히 빈 목록을 돌려주지 않는다.
            if not rows:
                if page == 1:
                    raise RuntimeError(f"{LIST} 1페이지에서 글을 못 찾았다. 마크업을 확인해라")
                break
            for when, href, title, img in rows:
                if when < floor:
                    stop = True
                    continue
                flat = title.replace("[보도기사]", " ")
                if any(w in flat for w in _SKIP) or not _LAUNCH.search(flat):
                    continue
                cand.append((when, href, title, img))
            if stop:
                break

        items: list[Item] = []
        seen = set()
        for when, href, title, img in cand:
            time.sleep(DELAY)
            r = base.retry(lambda: c.get(href))
            r.raise_for_status()
            doc = HTMLParser(r.text)
            for s in doc.css("script,style"):
                s.decompose()
            body = " ".join(doc.text().split())
            for name in _names(title, body):
                it = Item(brand=BRAND, name=name,
                          image=img if img.startswith("https://") else "",
                          released_at=when, is_new=True, url=href)
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
    return items
