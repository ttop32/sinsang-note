"""보배반점 — 보도자료에서 신제품과 출시일을 뽑는다.

공정위 `중식` 업종 가맹점 수 **4위**(198개, 2024년 말). (주)보배에프앤비.

**메뉴 페이지는 쓸 수 없다.** `/menu/main.php`(면/밥류·요리류·사이드/주류)는 상품을
SSR 로 내려주긴 하는데 **NEW 배지도 날짜도 없다.** 짜장면·짬뽕·탕수육 같은 상시
메뉴가 전부라, 긁으면 메뉴판 전체가 '신상' 으로 올라간다. 중식집 메뉴판은 거의
안 바뀌므로 그건 이 서비스가 하면 안 되는 일이다. 그래서 메뉴 페이지는 안 본다.

남은 경로는 보도자료고, 이건 GS25·오뚜기·오리온과 **같은 종류의 소스**다.

수집 경로. 2026-10-02 실측:
  - 목록 `/community/news.php?page=N` 이 SSR 이다. 쿠키·토큰 없이 열린다.
    한 페이지 8건, 10페이지 이상(2024-12~).
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
최근 3페이지 24건을 돌려 **필터 통과 4건 → 상품 5건**이 남는다 — 크림짬뽕
(2026-09-15, HMR), 전복중화냉면·전복냉짬뽕(2026-06-01, 여름 한정), 바질크림짬뽕·
마라크림짬뽕(2026-04-27). 전건 본문을 열어 실제 제품이 맞는지 확인했다(오집 0건).
같은 제품을 다른 매체가 쓴 중복 기사도 걸러진다.
탈락한 20건 제목도 전부 눈으로 읽었다 — 매장 오픈·수상·사회공헌·스마트스토어
개편·사내 공모전이라 전부 올바른 탈락이다.

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
# 한 페이지 8건. DAYS(540일)를 덮으려면 10페이지는 받아야 한다 — 실측으로
# 10페이지가 2024-12 까지 간다. ⚠️ 여길 좁게 잡으면 `when < floor` 를 만나기
# 전에 루프가 끝나서 **아무 경고 없이** 창 안의 글을 놓친다. 실제로 3이었을 때
# 전복중화냉면·짬뽕어묵탕·보배고량주·중화빵·육회냉짬뽕을 통째로 흘렸다.
MAX_PAGES = 12
DAYS = 540           # 중식은 신메뉴가 연 1~4건이라 300일이면 브랜드 페이지가 빈다.
                     # 화면 노출은 rules.WINDOW(60일)가 따로 자르므로 넓혀도
                     # '오래된 게 신상으로 뜨는' 일은 없다(짬뽕관 어댑터와 맞췄다).
DELAY = 2.2

# 상품 기사인가. 이 말이 없으면 상세를 받지 않는다.
_LAUNCH = re.compile(r"(출시|선봬|선보|론칭|신메뉴|신제품|판매)")

# 상품 기사가 아닌데 위 동사를 쓰는 것들. 실측 제목으로 뽑았다.
_SKIP = ("대상", "수상", "선정", "오픈", "공모전", "이벤트", "나눔", "진출",
         "개편", "새단장", "매뉴얼", "강화", "고도화", "성료", "프로모션",
         "창업", "채용", "표준화",
         # 아래 셋은 MAX_PAGES 를 넓히고 나서 실제로 걸린 오집이다.
         #   굿즈·콜라보 — '짱구는 못말려' 협업 2차 콜라보 굿즈 출시(2026-03-18).
         #                 따옴표 안이 상품이 아니라 **캐릭터 IP** 다.
         #   옵션       — '매운맛 3단계 선택 옵션' 출시(2026-02-23). 기존 8개 메뉴에
         #                 맵기 선택을 붙인 것이지 새 상품이 아니다.
         # ⚠️ '협업' 은 넣지 마라. CU 와 협업한 '짬뽕어묵탕'(2026-03-06)이 진짜
         #    신제품인데 같이 죽는다.
         "굿즈", "콜라보", "옵션")

_QUOTED = re.compile(r"[‘'`]([^’'`\n]{2,40})[’'`]")

# 따옴표 안이 상품이 아닌 것들.
_NOT_PRODUCT = ("보배그린하트", "마켓보배", "대상", "브랜드", "프랜차이즈", "미래",
                "이벤트", "캠페인", "협업", "일상")

# 지점명. `"점"` 을 _NOT_PRODUCT 에 넣으면 부분일치라 '점보마라탕'·'점보만두'
# 같은 실존 작명을 죽인다(라화쿵부가 실제로 '3KG 점보마라탕' 을 판다).
# 지점명은 항상 '…점' 으로 **끝나므로** 끝자리로만 본다.
_BRANCH = re.compile(r"점$")

_IMG = re.compile(r"url\(\s*['\"]?(https://[^'\")]+)")

# 🔴 제목이 상품명을 안 부르는 기사가 있다. 2026-06-01 실측:
#   제목 `보배반점, 완도산 전복 활용한 여름 한정 메뉴 출시...지역 상생 프로젝트 추진`
#   본문 `신메뉴는 ‘전복중화냉면’과 ‘전복냉짬뽕’ 2종으로 구성됐다.`
# 제목에 이름이 없으니 '본문 인용 ∩ 제목' 규칙으로는 **두 상품을 통째로 잃는다.**
# 그렇다고 교차검증을 풀면 '보배그린하트'·'마켓보배' 같은 비상품이 들어온다.
#
# 그래서 **제목이 따옴표로 아무 상품도 부르지 않을 때만** 범위를 넓힌다. 그때
# 본문에서 믿는 자리는 '신메뉴/신제품' 이 들어간 **그 문장 안의 따옴표**뿐이다.
# 문장 경계는 마침표로 끊는다 — 문서 전체를 보면 "‘보배그린하트’ 캠페인" 같은
# 다른 문단의 따옴표가 섞인다.
_SENTENCE = re.compile(r"[^.!?]*$")
_NEW_WORD = ("신메뉴", "신제품", "새롭게", "선보", "출시")

# 제목이 'A 등 4종 출시' 꼴이면 A 말고 나머지는 제목에 없다. 실측 2025-04-28:
#   제목 `여름 시즌 신메뉴 '육회냉짬뽕' 등 4종 출시`
#   본문 `… ▲'육회냉짬뽕' ▲'냉짬뽕' ▲'중화냉면' ▲'콩국수' 4종이다.`
# 제목에 따옴표가 **있어도** 나머지 3종은 교차검증할 데가 없다. 그래서 'N종' 이
# 보이면 제목 무인용 기사와 같게 다룬다(본문 '신메뉴 문장' 안의 따옴표를 믿는다).
_MULTI = re.compile(r"\d+\s*종")

# 한글 음절. 제목 포함 검사의 경계 판정에 쓴다.
_HANGUL = re.compile(r"[가-힣]")


def _in_title(name: str, flat: str) -> bool:
    """제목이 이 이름을 **낱말로** 부르는가. 단순 포함은 안 된다.

    한국어는 단어 경계가 없어서 `in` 만 쓰면 더 긴 상품명 안에 들어 있는 짧은
    이름이 따로 잡힌다 — 실측: 제목 `'육회냉짬뽕' 등 4종` 에서 본문의 `'냉짬뽕'`
    이 통과했다. 앞뒤 글자가 한글이면 그건 다른 낱말의 일부다.
    """
    k = name.replace(" ", "")
    i = flat.find(k)
    while i >= 0:
        before = flat[i - 1] if i else ""
        after = flat[i + len(k):i + len(k) + 1]
        if not _HANGUL.match(before or " ") and not _HANGUL.match(after or " "):
            return True
        i = flat.find(k, i + 1)
    return False


def _in_new_sentence(body: str, pos: int) -> bool:
    """`body[pos]` 의 따옴표가 '신메뉴' 를 말하는 문장 안에 있는가."""
    # ⚠️ 창을 글자 수로 자르지 마라. 전에 마지막 120자만 봤더니 한 문장 안에서
    #    뒤쪽에 있던 '콩국수'(4종 중 넷째)가 '출시' 에 못 닿아 빠졌다.
    #    문장 경계가 이미 범위를 좁혀 주므로 문장 전체를 본다.
    head = _SENTENCE.search(body[:pos]).group(0)
    return any(w in head for w in _NEW_WORD)


def _text(node) -> str:
    return " ".join(node.text().split()) if node else ""


def _date(s: str) -> str:
    m = re.search(r"(20\d{2})-(\d{1,2})-(\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    return f"{y:04d}-{mo:02d}-{d:02d}" if 1 <= mo <= 12 and 1 <= d <= 31 else ""


def _names(title: str, body: str) -> list:
    """제목과 본문을 교차검증해 상품명을 뽑는다. 못 고르면 빈 목록.

    기본은 **본문 인용 ∩ 제목**이다. 다만 제목이 상품명을 아예 안 부르는 기사가
    있어서(아래 _SENTENCE 주석) 그때만 범위를 넓힌다.
    """
    t = " ".join(title.split()).replace("[보도기사]", " ")
    if any(w in t for w in _SKIP) or not _LAUNCH.search(t):
        return []
    flat = t.replace(" ", "")
    # 제목이 따옴표로 상품을 부르지 않거나 'N종' 이라 나머지를 안 부르면
    # 교차검증할 대상이 없다. 그때만 본문의 '신메뉴 문장' 으로 넓힌다.
    loose = not _QUOTED.search(t) or bool(_MULTI.search(t))
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
        if any(w in name for w in _NOT_PRODUCT) or _BRANCH.search(name):
            continue
        if name in seen:
            continue
        if not _in_title(name, flat):
            if not (loose and _in_new_sentence(body, m.start())):
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
