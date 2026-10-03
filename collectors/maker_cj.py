"""CJ제일제당 — 뉴스룸 보도자료에서 신제품과 출시일을 뽑는다.

오뚜기·오리온·샘표·삼양식품과 같은 계보다(보도자료 제목 → 상품명).
조인 규칙은 `collectors/maker_orion.py` 것을 그대로 가져왔다.
비비고·고메·햇반·해찬들·백설을 내는 **국내 냉동·간편식 1위 제조사**다.

**1차 조사가 "robots 전면차단" 으로 제외했던 브랜드다.**
robots 는 지금도 `User-agent: * → Disallow: /` 가 맞다. 다만 운영자 판단으로
robots 제약을 무시하기로 했고(2026-10-02), **UA 위장은 하지 않는다**(`base.UA` 고정).
그리고 실제로는 ClaudeBot·anthropic-ai·GPTBot 등 **명명된 AI 크롤러에는 `/kr/` 을
명시 허용**하고 있다. robots 원문은 아래에 전문을 옮겨 뒀다.

수집 경로. 2026-10-02 실측:
  GET https://www.cj.co.kr/kr/newsroom/pressreleases?index=1&offset=0   200 / 68,631B
    <div class="item js-inview">
      <div class="background">
        <span style="background-image: url('/cj_files/news/202609/1790555801465_0.jpg');">
          <img src="/cj_files/news/202609/1790555801465_0.jpg" … /></span></div>
      <div class="module">
        <a href="/kr/newsroom/pressreleases/news-detail/1826" class="anchor">
          <h2 class="name">CJ제일제당, 110g 백미밥 ‘햇반 부드러운 미니밥’ 출시…</h2>
          <p class="date eng-title">2026.09.03</p></a></div></div>
  **완전 SSR. 제목이 잘리지 않는다** — 상세를 열 필요가 없다.
  페이지당 6건. 페이저가 `?index=N&offset=(N-1)*6` 을 그대로 쓴다(하단 마크업에서 읽었다).

  ⚠️ `/sitemap-news.xml` 은 최신 10건만 담는다(2,989B). 목록이 SSR 이라 쓸 일이 없다.
  ⚠️ `www.cjcheiljedang.com` 은 **인증서가 호스트명과 안 맞는다**(Hostname mismatch).
     `/kr/media/news` 같은 경로는 404 인데 **55KB 짜리 HTML 에러 셸**을 준다 —
     상태코드가 아니라 내용으로 판정해야 하는 유형이다(삼양 `view.do?seq=1399` 선례).

**⚠️ 이 브랜드의 진짜 문제 — 출시 기사 밀도가 아주 낮다.**
6페이지 36건(2026-07-08 ~ 10-02, 약 3개월)을 전수로 읽었다. **국내 신제품 출시는 2건**:
    2026-09-03  110g 백미밥 ‘햇반 부드러운 미니밥’ 출시
    2026-08-20  ‘해찬들 옛장’ 출시로 프리미엄 장맛 지평 넓힌다
나머지 34건의 성격 —
    해외·글로벌 11건 (美 비비고 김밥 매출, 멕시코 K-박람회, 뉴욕 타임스퀘어, IFT 2026…)
    **주류** 4건  (프리미엄 K-증류주 `jari` 론칭·품평회·바앤스피릿쇼)  ← 반드시 뺀다
    CSR·안전·채용 7건 · 실적/IR 1건 · 마케팅·협업·클래스 6건 ·
    누적판매 돌파 2건 · 플랫폼 리뉴얼 2건 · 선물세트 1건
→ **월 1건 안팎**이다. 건수가 적은 게 정상이고 '수집 실패'가 아니다.
  그래도 넣는 이유는 냉동·간편식 1위사의 국내 출시를 다른 데서는 못 받기 때문이다.

**⚠️ 주류를 반드시 뺀다.** CJ는 2026년부터 증류주 `jari` 를 민다.
`base.is_alcohol()` 은 `jari`·`증류주` 를 모른다(실측 False). 그래서 `_SKIP` 에
`증류주`·`주류`·`스피릿` 을 넣었다. 세 단어 다 사람 먹는 상품명에 안 쓰여
부분일치 사고가 없다(⚠️ `주` 한 글자로 줄이지 마라 — 거의 모든 말에 걸린다).

**일괄 등록 흔적 — 없다.** 36건의 날짜가 전부 다르고 07-08 ~ 10-02 로 고르다.

robots: https://www.cj.co.kr/robots.txt → 200 / 1,015B. 전문:
```
User-agent: Googlebot-News
Allow: /kr/newsroom/      Allow: /en/newsroom/
Allow: /resources/        Allow: /sitemap-news.xml
Disallow: /

User-agent: Googlebot / Googlebot-Mobile / Googlebot-Image
Allow: /

User-agent: Google-Extended / NaverBot / Yeti / Daumoa / Bingbot / GPTBot /
           OAI-SearchBot / ChatGPT-User / ClaudeBot / Claude-SearchBot /
           Claude-User / Claude-Web / anthropic-ai / PerplexityBot /
           Perplexity-User / Applebot / Applebot-Extended
Allow: /kr/   Allow: /en/   Allow: /sitemap.xml ...

User-agent: *
Disallow: /
```
        우리 UA(`sinsang-note/1.0`)는 어느 그룹에도 없어 `*` 가 적용된다 =
        **형식상 전면 금지**다. 운영자 판단으로 수집하되, 삭제 요청이 오면
        다투지 말고 즉시 내린다(base.BRANDS 의 이마트24·도미노피자와 같은 칸).
약관:   확인하지 않았다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "CJ제일제당"
SITE = "https://www.cj.co.kr"
LIST = SITE + "/kr/newsroom/pressreleases"
PER_PAGE = 6
MAX_PAGES = 8        # 한 페이지 6건 = 약 4개월치. 폭주 방지 상한.
DAYS = 300
DELAY = 2.2

# --- 제목 → 상품명 (maker_orion 과 같은 규칙 + CJ 함정 보강) ----------------
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭|런칭)")
_LAUNCH_ONLY = re.compile(r"(론칭|런칭)")   # 브랜드 출범에 쓰이는 동사
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_TRAIL_SEP = re.compile(r"^\s*[·∙,、/]")
# 따옴표 바로 앞의 '브랜드'. 상품이 아니라 브랜드 소개라는 신호다(아래 _pick 참고).
_BRAND_HEAD = re.compile(r"브랜드\s*$")

_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원", "프로젝트",
         "오픈", "이벤트", "광고", "조회수", "할인", "선물", "프로모션",
         "클래스", "컨퍼런스", "전시회", "품평회", "파트너십", "새단장",
         # 주류. base.is_alcohol() 은 CJ 증류주 'jari' 를 모른다(실측 False).
         # ⚠️ '주' 한 글자로 줄이지 마라 — 거의 모든 말에 걸린다.
         "증류주", "주류", "스피릿",
         # 국내 출시가 아닌 건 화면에 올리면 거짓이 된다. CJ 보도자료의 3분의 1이다.
         "日", "美", "글로벌", "수출", "해외", "현지", "뉴욕", "K-푸드")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")
_REPACK_HEAD = ("에디션", "라벨")
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")
_REPACK_NAME = ("에디션", "컬렉션", "한정판", "선물세트", "기획세트", "기획팩")

# 🔴 **`N종` 을 버리지 않고 꼬리만 뗀다.** 오리온 규칙은 `N종` 이 들어간 제목을
# 통째로 버리는데(따옴표 안이 상품이 아니라 라인 이름일 수 있어서), CJ 는
# 따옴표 안이 **온전한 상품명**이라 그 걱정이 없고 버리면 진짜 신제품이 죽는다.
# 2026-10-03 검수 실측 — 8페이지 48건에서 이 규칙 하나로 죽은 진짜 신제품:
#     CJ제일제당, 전통 수제방식 살린 ‘비비고 김부각’ 3종 출시… “건강스낵 시장 공략”
# 2026-10-02 판이 신세계푸드·풀무원만 되살리고 CJ 를 빠뜨렸다(§5-3 과 같은 사고).
# 풀무원과 같은 처리다 — **따옴표 안만 쓰는 건 그대로 두고** `N종` 꼬리만 턴다.
# 48건 전수 재실행: 2건 → 3건, 새로 들어온 1건이 위의 김부각이다.
# ⚠️ `_MULTI` 는 지웠다. 쓰는 데가 없는데 남겨 두면 다음 사람이 되살린다.
_COUNT_TAIL = re.compile(r"\s*\d+\s*종\s*$")


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열."""
    t = " ".join(title.split())
    if any(w in m.group(1) for m in _HEAD.finditer(t) for w in _REPACK_HEAD):
        return ""
    body = _HEAD.sub(" ", t)
    # ⚠️ `N종` 으로 버리지 않는다. 사유는 _COUNT_TAIL 위 주석.
    if any(w in body for w in _SKIP):
        return ""
    qs = list(_SINGLE.finditer(body))
    if len(qs) >= 2 and any(w in body[qs[-2].end():qs[-1].start()] for w in _REPACK_MID):
        return ""
    verb = None
    for m in _VERB.finditer(body):
        verb = m
    if not verb or any(w in body[verb.end():] for w in _TAIL):
        return ""
    head = body[:verb.start()]
    # '브랜드 ‘X’ 론칭' 은 브랜드 출범이지 상품 출시가 아니다(삼양과 같은 규칙).
    if _LAUNCH_ONLY.match(verb.group(1)) and "브랜드" in head:
        return ""
    quoted = None
    for m in _SINGLE.finditer(head):
        quoted = m
    if not quoted or any(w in head[quoted.end():] for w in _BETWEEN):
        return ""
    # 따옴표 **바로 앞**이 '브랜드' 면 상품이 아니라 브랜드 소개다. 실측:
    #   `프리미엄 참치 브랜드 ‘칼보(Calvo)’ 국내에 선보인다`  → 상품이 아니다
    # 삼양은 같은 걸 동사(론칭)로 갈랐는데 CJ는 '선보인다' 를 쓴다. 그래서
    # 동사가 아니라 **위치**로 본다. `비비고 브랜드 신제품 ‘X’ 출시` 처럼
    # 사이에 다른 말이 끼면 그대로 통과한다 — 그건 진짜 신제품이다.
    if _BRAND_HEAD.search(head[:quoted.start()]):
        return ""
    if _TRAIL_SEP.match(head[quoted.end():]):
        return ""
    name = _COUNT_TAIL.sub("", quoted.group(1).strip()).strip(" ,·∙")
    if len(name) < 2 or any(c in name for c in "·∙&?!"):
        return ""
    if any(w in name for w in _REPACK_NAME):
        return ""
    return name


def _date(s: str) -> str:
    """'2026.09.03' → '2026-09-03'. 월·일 범위를 검증한다."""
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})\s*$", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _rows(html: str) -> list[tuple]:
    """목록 HTML → (날짜, 제목, href, 이미지) 목록."""
    out = []
    for item in HTMLParser(html).css(".item"):
        a = item.css_first("a.anchor")
        tit = item.css_first("h2.name")
        if not (a and tit) or "news-detail" not in (a.attributes.get("href") or ""):
            continue
        dt = item.css_first("p.date")
        img = item.css_first(".background img")
        src = (img.attributes.get("src") or "").strip() if img else ""
        out.append((_date(dt.text(strip=True) if dt else ""),
                    " ".join(tit.text().split()),
                    (a.attributes.get("href") or "").strip(),
                    SITE + src if src.startswith("/") else src))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"index": page,
                                                       "offset": (page - 1) * PER_PAGE}))
            r.raise_for_status()
            rows = _rows(r.text)

            # 셀렉터가 바뀌면 조용히 0건이 되는 게 제일 나쁘다. 출시 기사가
            # 월 1건이라 '상품 0건'은 정상이지만 '목록 0행'은 고장이다.
            if page == 1 and not rows:
                raise ValueError(
                    f"CJ제일제당 보도자료 1페이지가 비었다. {r.url} → "
                    f"{len(r.content)}B — 목록 셀렉터(.item / a.anchor / "
                    f"h2.name / p.date)가 바뀌었는지 확인하라")
            if not rows:
                break

            for released, title, href, img in rows:
                if released and released < floor:
                    continue
                name = _pick(title)
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=re.sub(r"^\s*CJ제일제당\s*", "", title).lstrip(" ,"),
                    image=img,
                    released_at=released,
                    is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                    url=SITE + href if href.startswith("/") else (href or LIST),
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            fresh = [d for d, *_ in rows if d]
            if fresh and max(fresh) < floor:
                break
    return items
