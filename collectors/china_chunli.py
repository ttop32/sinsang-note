"""춘리마라탕 — 워드프레스 REST 로 '춘리 소식'을 받아 신메뉴와 출시일을 뽑는다.

공정위 `중식` 업종 가맹점 수 **3위**(202개, 2024년 말). (주)씨엘케이에프앤비.

**메뉴 페이지는 쓸 수 없다.** `/menu/` 를 받아 보면 2026-10-02 현재 상품이 아니라
**마라탕에 넣는 재료 80여 종**이 깔려 있다(청경채·알배기·얼갈이·숙주나물·분모자·
뉴진면·목이버섯…). 탕화쿵푸와 같은 사정이다 — 마라탕집에서 '메뉴판'은 재료
바구니라 카탈로그가 아니다. 그 페이지엔 `NEW` 라는 글자가 **0건**이고(실측) 날짜도
없다. 긁으면 재료 80개가 전부 '신상' 으로 올라간다. 그래서 안 본다.

⚠️ 재료 이미지의 업로드 경로(`/wp-content/uploads/2026/07/청경채.png`)에 연·월이
   박혀 있지만 **날짜로 쓰면 안 된다.** 2026/07 에 재료가 한꺼번에 몰려 있어
   사이트 개편 때 일괄 업로드한 흔적이다(본아이에프 BF114 와 같은 함정).

수집 경로. 2026-10-02 실측:
  - 이 사이트는 워드프레스고 **REST API 가 인증 없이 열려 있다.**
    `/wp-json/wp/v2/types` 로 커스텀 포스트 타입을 세어 보면 `chunli_news`,
    `chunli_faq`, `chunli_voice`, `partner_notice` … 가 있다.
    기본 `posts` 는 **0건**이다 — 기사는 전부 `chunli_news` 에 들어 있다.
    (`/notice/` 화면이 그리는 게 이 타입이다.)
  - `GET /wp-json/wp/v2/chunli_news?per_page=50&_embed=wp:featuredmedia` 한 번이면
    27건 전량이 온다(2025-08~2026-10). 페이징이 필요 없다.
  - `date` 가 게시일, `_embedded["wp:featuredmedia"][0]["source_url"]` 이 대표
    이미지(https, 같은 도메인)다. 본문은 `content.rendered` 에 통째로 들어온다.

신제품 판정 근거는 **기사 자체**다. 브랜드가 '신메뉴 … 출시' 라고 낸 글이라
is_new=True 로 둔다(GS25·오뚜기·오리온과 같은 근거).

상품명은 제목·본문을 **교차검증**해서만 뽑는다(탕화쿵푸 어댑터와 같은 규칙).
  ① 본문에서 ‘…’ 로 인용된 이름을 모으고
  ② 그중 **제목에도 글자 그대로 있는 것만** 채택한다.
한쪽에만 있는 건 버린다 — 이 게시판은 27건 중 20건이 **매장 오픈·이벤트·수상**이고
거기 따옴표 안은 '신검단점'·'2026 올해의 브랜드 대상'·'춘리로 키움데이' 같은
상품이 아닌 것들이다. 실측으로 남은 건 1건 —
  `춘리마라탕, 건강 트렌드 반영한 신메뉴 ‘대한민국 대표 마라탕 Lite’ 출시`
  (2026-07-02, 본문도 ‘대한민국 대표 마라탕 Lite’ 로 같은 이름을 부른다)
기사 본문을 눈으로 읽어 실제 메뉴가 맞는지 확인했다(오집 0건).

⚠️ **날짜에 쓰레기가 섞인다.** 27건 중 1건의 `date` 가 `0025-08-29T...` 다
   (운영자가 연도를 잘못 입력한 것으로 보인다). 연도를 20xx 로 검증해 버린다.
   검증 없이 쓰면 '어제 없던 게 오늘 있다' 판정이 영원히 참이 된다.

수집량은 **연 1~2건**이다. 그래도 날짜가 정확하고 브랜드가 직접 '출시'라고 말한
건이라 신뢰도는 높다. 가맹점 202개짜리 3위 브랜드를 비워두는 것보다 낫다.

robots: `chunlimalatang.com/robots.txt` → 200, text/plain. 본문이 두 줄뿐이다 —
        `User-agent: Yeti` / `Allow:/`. ⚠️ **`User-agent: *` 규칙이 아예 없다**
        (라화쿵부·투파인드피터와 같은 꼴). 네이버 봇만 명시 허용했고 우리에
        해당하는 규칙이 없으니 금지도 아니다. 그래도 허용이라 적힌 것도 아니라서
        요청 간격을 길게 잡는다. 어차피 요청은 **1회**다.
약관: 푸터에 개인정보처리방침만 있고 **이용약관 페이지가 없다**. 수집·복제를
      금지하는 문구는 찾지 못했다.
"""
import re
import time
from datetime import date, timedelta

from . import base
from .base import Item

BRAND = "춘리마라탕"
SITE = "https://chunlimalatang.com"
API = SITE + "/wp-json/wp/v2/chunli_news"
DAYS = 540           # 중식은 신메뉴가 연 1~4건이라 300일이면 브랜드 페이지가 빈다.
                     # 화면 노출은 rules.WINDOW(60일)가 따로 자르므로 넓혀도
                     # '오래된 게 신상으로 뜨는' 일은 없다(짬뽕관 어댑터와 맞췄다).
DELAY = 2.0

# 상품 기사인가. 이 말이 없으면 보지 않는다.
_LAUNCH = re.compile(r"(출시|선봬|선보|론칭|신메뉴|신제품)")

# 상품 기사가 아닌데 위 동사를 쓰는 것들.
_SKIP = ("오픈", "수상", "선정", "대상", "협력", "체결", "이벤트", "성료",
         "캐릭터", "퀴즈", "빙고", "키움데이", "댓글", "투표", "박람회")

# 한국 기사는 ‘ ’ 와 ' 를 섞어 쓴다.
_QUOTED = re.compile(r"[‘'`]([^’'`\n]{2,40})[’'`]")

# 따옴표 안이 상품이 아닌 것들.
_NOT_PRODUCT = ("점", "대상", "이벤트", "데이", "브랜드", "프랜차이즈", "캠페인",
                "협약", "축제", "시리즈")


def _strip(html: str) -> str:
    return " ".join(re.sub(r"<[^>]*>", " ", html or "").replace("&nbsp;", " ").split())


def _date(s: str) -> str:
    """'2026-07-02T20:28:41' → '2026-07-02'. 연도가 20xx 가 아니면 버린다.

    운영자 오타로 `0025-08-29` 가 실재한다(docstring 참고). 그대로 두면 정렬과
    diff 판정이 통째로 망가지므로 날짜를 비우는 쪽이 낫다.
    """
    m = re.match(r"(20\d{2})-(\d{2})-(\d{2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    return f"{y:04d}-{mo:02d}-{d:02d}" if 1 <= mo <= 12 and 1 <= d <= 31 else ""


def _names(title: str, body: str) -> list:
    """제목과 본문을 교차검증해 상품명을 뽑는다. 못 고르면 빈 목록."""
    t = " ".join(title.split())
    if any(w in t for w in _SKIP) or not _LAUNCH.search(t):
        return []
    flat = t.replace(" ", "")
    out, seen = [], set()
    for m in _QUOTED.finditer(body):
        name = m.group(1).strip(" ,·∙")
        if len(name) < 2 or any(w in name for w in _NOT_PRODUCT):
            continue
        if name.replace(" ", "") not in flat or name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    with base.client(headers={"Accept": "application/json"}) as c:
        r = base.retry(lambda: c.get(API, params={"per_page": 50,
                                                  "_embed": "wp:featuredmedia"}))
        r.raise_for_status()
        posts = r.json()
        time.sleep(DELAY)

    # 목록이 통째로 비면 커스텀 포스트 타입 이름이 바뀐 것이다. 조용히 넘기지 않는다.
    if not posts:
        raise RuntimeError(f"{API} 가 0건이다. 포스트 타입이 바뀌었는지 확인해라")

    items: list[Item] = []
    seen = set()
    for p in posts:
        when = _date(p.get("date", ""))
        if not when or when < floor:
            continue
        title = _strip((p.get("title") or {}).get("rendered", ""))
        body = _strip((p.get("content") or {}).get("rendered", ""))
        media = ((p.get("_embedded") or {}).get("wp:featuredmedia") or [{}])[0]
        img = media.get("source_url", "") or ""
        for name in _names(title, body):
            it = Item(brand=BRAND, name=name,
                      image=img if img.startswith("https://") else "",
                      released_at=when, is_new=True, url=p.get("link", ""))
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)
    return items
