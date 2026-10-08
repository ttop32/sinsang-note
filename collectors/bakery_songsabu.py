"""송사부고로케(송사부수제쌀고로케).

`CANDIDATES-BAKERY2.md` §4 가 **"robots 에 주석까지 손으로 달아 AI 봇 10종을 막는다.
앤티앤스와 같은 건이니 붙이지 않는 쪽을 권한다"** 로 접은 곳이다.

```
# 스팸/AI 봇 강력 차단
User-agent: MJ12bot … GPTBot / ChatGPT-User / CCBot / ClaudeBot / Bytespider
Disallow: /
```
`User-agent: *` 는 원래 허용이었고 우리 UA 는 목록에 없었다. 막은 건 규칙이 아니라
브랜드 의사표시였다. **2026-10-02 운영자가 승인**해서 다시 연다. 2026-10-08 실측.

## 경로

홈 `https://songsabu.co.kr/` 는 8,797바이트 스플래시고 본체는 `/main.php` 다.
메뉴는 그누보드5 **갤러리 게시판**이다.

  GET /bbs/board.php?bo_table=menu&page=N        전체. **8건씩** 5페이지 = 36건
  GET /bbs/board.php?bo_table=menu&sca=NEW       NEW 칸. 8건
  GET /bbs/board.php?bo_table=menu&wr_id=<n>     상세

분류 탭은 `NEW / 고로케 / 도넛 / 꽈배기 / 핫도그＆샐러드 / 기타＆구운빵류` 여섯이다
(URL 에 퍼센트 인코딩된 한글로 들어간다). 카테고리별로 돌면 페이징까지 10요청이 더
붙는데 얻는 게 분류명뿐이라 **전체 5장 + NEW 1장**만 받는다.

목록 카드: `li.dp_li` → `h3`(상품명) · `.txt_content`(설명) · `img`(썸네일) ·
`.sd_hidden`(표시 번호) · `a[href*=wr_id]`.

## 신제품 신호 — `sca=NEW` 분류. **36건 중 8건 (22.2%)**

```
밤가득 팥 도나스 · 통통새우야채 고로케 · 크림에그포테이토 고로케 · 콘크림치즈 고로케
정통 베이컨피자 고로케 · 베이컨치즈그라탕 고로케 · 명품고기야채 고로케 · K-궁중불고기 고로케
```
`wr_id` 가 **124~131 로 연속**이다 = 한 번에 올린 한 묶음이다.

⚠️ **목록 정렬을 날짜로 읽으면 안 된다.** 전체 목록 맨 위는 `고소미 도넛`(wr_id 120)
인데 NEW 8건은 `wr_id 124~131` 로 **더 뒤 번호**다. `sst=wr_num` 으로 손수 정렬한
진열 순서지 등록 순서가 아니다.

🔴 **그리고 이 NEW 칸은 지금 8개월째 그대로다**(아래 날짜 참고). 날짜 없이
`is_new=True` 만 올리면 2월 상품이 10월에 신상으로 뜬다. 60일 창이 거르게
**날짜를 반드시 붙인다**(함정 #5).

## 날짜 — 썸네일의 `Last-Modified`. 이 브랜드에서는 **쓸 수 있다**

HTML 어디에도 날짜가 없다. 실측으로 기각한 후보 —
  - 상세 페이지: `작성일`·`등록일`·`wr_datetime` 문자열이 **0건**이다. 스킨이 안 찍는다.
  - `/bbs/rss.php?bo_table=menu` → 본문 40바이트 `RSS 보기가 금지되어 있습니다.`
  - 썸네일 파일명 `thumb-2072903739_JkBnrl4H_<sha1>_490x363.png` 에 시각이 없다.

남은 건 이미지 `Last-Modified` 뿐이다. **이 레포는 원래 이걸 믿지 않는다** —
컴포즈커피(2026-06-16 149건 전부 같은 값)·블루샥에서 배포 시각으로 판명됐다.
그래서 24건을 찍어 분포를 봤는데 **여기는 다르다**:

```
2025-08-19 09:46:18~26   20건   ← 10초 안에 몰린 사이트 이전 일괄
2026-02-20 05:44~05:49    8건   ← NEW 8건. 30초 간격으로 하나씩
2025-11-06 02:23·02:35    2건   ← 야채감자/안동찜닭 고로케
```
전건이 같은 값이 아니고, **묶음 경계가 `sca=NEW` 와 정확히 일치한다**(2026-02-20 의
8건 = NEW 탭 8건). 배포 시각이면 이렇게 갈릴 수 없다. 파일별 업로드 시각이 맞다.

그래도 사진 올린 시각이고 2025-08-19 에 20건이 몰린 일괄이 섞여 있으므로
**`uploaded_at` 에만 넣는다**(`rules.untrust_bulk_dates()` 가 보는 자리).
`released_at` 은 비운다 — 브랜드가 출시일이라고 말한 적이 없다.

⚠️ 그래서 요청이 많다. 목록 6장 + 썸네일 `HEAD` 36번 = **42요청**이다. 본문은 안 받고
헤더만 받는다. 더 싼 날짜 경로가 생기면 이 36번을 먼저 지워라.

등록 제안: 유형 **`CAFE`**, 세부분류 `베이커리`.
⚠️ `FRANCHISE` 로 넣으면 1단 탭이 '카페'가 아니라 '외식'으로 간다.
"""
import time
from email.utils import parsedate_to_datetime

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "송사부고로케"
SITE = "https://songsabu.co.kr"
BOARD = SITE + "/bbs/board.php?bo_table=menu"
DELAY = 1.3
HEAD_DELAY = 0.8     # HEAD 는 본문을 안 받는다. 그래도 간격은 둔다
MAX_PAGES = 10       # 폭주 방지. 현재 8건씩 5페이지(36건)다


def _rows(html: str) -> list:
    """`li.dp_li` → (이름, 설명, 썸네일, 상세 URL)."""
    out = []
    for li in HTMLParser(html).css("li.dp_li"):
        h3 = li.css_first("h3")
        name = " ".join(h3.text().split()) if h3 else ""
        if not name:
            continue
        img = li.css_first("img")
        desc = li.css_first(".txt_content")
        a = li.css_first("a")
        # selectolax 는 값 없는 속성에 None 을 준다. 기본값이 안 먹는다.
        out.append((
            name,
            " ".join(desc.text().split()) if desc else "",
            (img.attributes.get("src") or "") if img else "",
            (a.attributes.get("href") or "") if a else "",
        ))
    return out


def _last_modified(c, url: str) -> str:
    """썸네일 헤더의 Last-Modified → 'YYYY-MM-DD'. 모듈 주석의 근거 참고."""
    if not url:
        return ""
    try:
        r = base.retry(lambda: c.head(url), tries=2)
    except Exception:
        return ""
    v = r.headers.get("last-modified")
    if not v:
        return ""
    try:
        return parsedate_to_datetime(v).date().isoformat()
    except (TypeError, ValueError):
        return ""


def fetch() -> list[Item]:
    with base.client() as c:
        rows = []
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda page=page: c.get(f"{BOARD}&page={page}"))
            r.raise_for_status()
            got = _rows(r.text)
            if not got:
                break
            rows += got

        if not rows:
            raise RuntimeError(
                f"{BOARD}: 상품 0건 — 'li.dp_li > h3' 가 깨졌다. "
                f"2026-10-08 실측은 8건씩 5페이지(36건)였다")

        time.sleep(DELAY)
        rn = base.retry(lambda: c.get(f"{BOARD}&sca=NEW"))
        rn.raise_for_status()
        new_names = {x[0] for x in _rows(rn.text)}
        # NEW 칸이 비면 분류명이 바뀐 것이다. 조용히 '신상 0건'으로 넘기면
        # 브랜드가 통째로 죽은 걸 아무도 모른다.
        if not new_names:
            raise RuntimeError(
                f"{BOARD}&sca=NEW: NEW 칸 0건 — 분류명이 바뀌었는지 확인하라. "
                f"2026-10-08 실측은 8건(wr_id 124~131)이었다")

        items: list[Item] = []
        seen = set()
        for name, desc, src, href in rows:
            time.sleep(HEAD_DELAY)
            it = Item(
                brand=BRAND,
                name=name,
                desc=desc,
                image=src,
                # 썸네일 Last-Modified. 2025-08-19 에 20건이 몰린 사이트 이전
                # 일괄이 섞여 있어 released_at 에 넣지 않는다 — 모듈 주석 참고.
                uploaded_at=_last_modified(c, src),
                is_new=name in new_names,
                url=href,
            )
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)

    new_count = sum(1 for i in items if i.is_new)
    if not new_count:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 NEW 0건 — 전체 목록과 NEW 칸의 상품명이 "
            f"안 맞는다(이름으로 짝지운다). 2026-10-08 실측은 36건 중 8건이었다")
    if new_count > len(items) * 0.5:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {new_count}건이 NEW 다 — 2026-10-08 실측은 "
            f"36건 중 8건(22.2%)이었다. 전체 목록 페이징이 끊겼는지 확인하라")
    dated = sum(1 for i in items if i.uploaded_at)
    if dated < len(items) * 0.9:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 날짜를 {dated}건밖에 못 읽었다 — 썸네일이 "
            f"Last-Modified 를 안 준다. **NEW 칸이 8개월째 같은 묶음이라 날짜 없이는 "
            f"2월 상품이 오늘 신상으로 뜬다**")
    return items
