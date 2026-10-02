"""농심 — 브랜드관 '신제품' 페이지를 읽는다. 라면 점유율 1위사다.

보도자료 제목을 파싱하는 오리온·삼양 계보가 **아니다.** 팔도와 같은 계보다 —
**브랜드가 직접 켜고 끄는 신제품 목록**을 그대로 받는다. 농심 본사 사이트의
보도자료 게시판은 지금 쓸 수 없고(아래), 브랜드관에 신제품 전용 면이 따로 있다.

**1차 조사가 "robots 전면차단" 으로 제외했던 브랜드다.**
운영자 판단으로 robots 제약을 무시하기로 했고(2026-10-02), **UA 위장은 하지 않는다**
(`base.UA` 고정). robots 원문은 아래에 옮겨 뒀다.

## 쓸 수 없는 경로부터 (여기서 시간 버리지 마라)

  GET https://www.nongshim.com/promotion/list_news   (보도자료)   200 / 103,120B
  GET https://www.nongshim.com/promotion/news_list   (같은 면)    200 / 103,031B
    **날짜 토큰 0개 · '출시' 0개.** 103KB 가 전부 내비·사이트맵이고 게시판 본문이
    없다. 브라우저로 실제로 열어 봐도(2026-10-02) 목록 자리가 **비어 있다** —
    JS 가 늦게 붙는 게 아니라 **렌더된 화면에도 글이 한 줄도 없다.**
    게시판이 죽었거나 사내망 전용으로 보인다. XHR 도 안 뜬다.
  GET https://www.nongshim.com/product/productNewList                404 / 197B

## 쓰는 경로

  GET https://brand.nongshim.com/new_product/index   200 / 436,603B   **완전 SSR**
    <div class="newProductList"><ul>
     <li><div>
       <h1>신라면로제</h1>
       <div>
         <p class="img"><span><img src="https://image.nongshim.com/non/pro/1781829117013.jpg"
                                   alt="신라면로제" /></span></p>
         <h2>매콤 크림 토마토의 조합</h2>
         <p class="strong">제품의 특징</p><div class="txt">…</div>
         <p class="btn"><a href="/shinrose/main/index?prodCode=1360">…</a></p>
       </div></div></li>
  선택자: `.newProductList li` → `h1`(상품명) · `h2`(한 줄 설명) · `.img img`(사진) ·
  `.btn a`(상세). 사진은 **절대 https URL** 이라 그대로 쓴다.
  페이지네이션 없음. 2026-10-02 현재 **9건**.

## 날짜 — 이미지 파일명의 epoch(ms) 를 `uploaded_at` 으로 쓴다

목록에도 상세에도 **출시일이 없다.** 대신 사진 파일명이 13자리 epoch 밀리초다:
    1781829117013.jpg → 2026-06-19 09:31
`released_at` 에는 **넣지 않는다.** 이건 출시일이 아니라 사진 업로드 시각이다
(mega.py 가 같은 판단을 했다). `uploaded_at` 자리가 정확히 이 용도다.

**일괄 재업로드인가 — 아니다.** 9건 전수:
```
2025-11-13  누들핏 새우탕맛        2026-01-16  바삭츄리 고튀
2025-12-15  빵부장 말차빵          2026-05-13  망고킥
2026-01-13  라뽁구리큰사발면        2026-05-15  누룽지팝 매콤한맛
2026-05-20  신라면 로제 큰사발면     2026-06-19  신라면로제
(농심라면큰사발면 1건은 옛 파일명 `434_bowl.jpg` 라 시각이 없다 → **버린다**.
 처음엔 '비워 둔다' 였는데 그게 틀렸다 — 아래 §시각 없는 행 참고)
```
8개 시각이 11개월에 걸쳐 흩어져 있다. 컴포즈(149건이 하루에 몰림)·롯데웰푸드
(7개 날짜에 54건)와 다른 모양이다. 시각(09:31·13:09·15:41…)도 제각각이다.

## 🔴 시각 없는 행은 버린다 (2026-10-02 검수에서 뒤집힌 판단)

날짜를 비우고 `is_new=True` 로 내보내면 **안전한 쪽이 아니라 제일 위험한 쪽**이다.
`rules.is_fresh()` 는 `is_new=True` 인데 `released_at`·`uploaded_at` 이 **둘 다
비면** 날짜 판정을 건너뛰고 `first_seen` 기준 `STALE`(90일) 동안 **무조건 화면에
올린다**(rules.py 의 '날짜도 없고 붙은 라벨이 행사뿐이면…' 아래 분기).
즉 **날짜를 비우는 게 60일 창을 우회하는 길**이 된다.

실제로 그렇게 됐다. 검수 실측(2026-10-02, `rules.is_fresh` 직접 호출):
    수집 9건 → 화면 1건, 그 1건이 **`농심라면큰사발면`**
    (나머지 8건은 가장 최신이 2026-06-19 = 105일 전이라 60일 창 밖)
그런데 농심라면은 **1975년 제품을 2025년 1월에 복각 재출시**한 것이다
(창립 60주년 '50년 만의 재출시'). 21개월 된 복각 상품 하나만 신상으로 걸리고
진짜 신제품 8건은 다 떨어지는, 정확히 뒤집힌 결과였다.

→ 이 면의 유일한 시간 신호가 사진 파일명 epoch 이므로, **그게 없는 행은
  시간에 놓을 수 없는 행**이고 늙은 사진을 쓰고 있다는 표식이다. 버린다.

**신호 교차검증 — 두 신호가 일치한다.** 같은 페이지 내비(`.sub-item a img.new`)에
`icon_new.png` 배지가 **8개** 붙어 있고, 그 8개가 신제품 목록 9건과 정확히 맞는다
(신라면로제가 봉지·큰사발면 2건으로 갈려서 9 ↔ 8 이다):
    농심라면 · 누들핏 · 누룽지팝 · 라뽁구리큰사발면 · 망고킥 · 바삭츄리 고튀 ·
    빵부장 · 신라면로제
해태 `productNewIconYn`(2024년 상품이 아직 true)·이디야(2017년 상품에 NEW)
같은 '낡은 배지' 사고를 걱정할 자리다. 비율(8.2%)은 건강하지만 **배지 하나가
이미 늙어 있다 — `농심라면`(2025-01 복각 재출시)이 배지를 달고 있다.**
배지는 '이 면에 올릴 만큼 최근' 까지만 말해 주고 60일은 모른다. 그래서
**배지가 아니라 업로드 시각이 최종 판정**이고, 시각이 없으면 버린다(위 §).

⚠️ 창 기준으로 보면 이 브랜드는 **대부분의 날 0건**이다. 2026-10-02 실측에서
   8건 중 60일 창 안에 드는 게 하나도 없었다(최신이 2026-06-19). 이 면은
   갱신이 느리다 — 0건이 정상이고 '수집 실패' 가 아니다.

robots: https://www.nongshim.com/robots.txt → 200 / 1,037B.
        `User-agent: * → Disallow: /` 이고 Googlebot·Bingbot·Yeti·Naverbot·Daumoa 와
        GPTBot·**ClaudeBot**·anthropic-ai·PerplexityBot·CCBot 등 명명된 봇만 `Allow: /`.
        우리 UA 는 어느 그룹에도 없어 `*` 가 적용된다 = **형식상 전면 금지.**
        운영자 판단으로 수집하되 삭제 요청이 오면 다투지 말고 즉시 내린다.
        ⚠️ **`Crawl-delay: 10` 을 선언한다.** 이 어댑터는 요청이 1회뿐이라 사실상
           걸릴 일이 없지만, 경로를 늘리게 되면 10초를 지켜라(`DELAY`).
        `brand.nongshim.com/robots.txt` 도 200 / 724B 로 따로 있다.
약관:   확인하지 않았다.
"""
import datetime
import re

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "농심"
SITE = "https://brand.nongshim.com"
LIST = SITE + "/new_product/index"
DELAY = 10.0        # robots 가 Crawl-delay: 10 을 선언한다. 경로를 늘리면 지켜라.

# 배지 비율 가드의 상한. 전체 상품의 이만큼을 넘게 '신제품' 이라고 하면 그건
# 신호가 아니라 장식이다 — 아래 fetch() 의 가드 주석 참고.
MAX_NEW_RATIO = 0.6

# 사진 파일명의 13자리 epoch(ms). `1781829117013.jpg` 꼴.
_STAMP = re.compile(r"/(\d{13})\.[A-Za-z]{3,4}(?:\?|$)")


def _uploaded(src: str) -> str:
    """사진 파일명의 epoch(ms) → 'YYYY-MM-DD'. 옛 파일명이면 빈 문자열."""
    m = _STAMP.search(src or "")
    if not m:
        return ""
    ts = int(m.group(1)) / 1000
    # 2015~오늘+1일 밖이면 epoch 가 아니라 다른 숫자다. 지어내지 않는다.
    now = datetime.datetime.now().timestamp()
    if not (1420070400 <= ts <= now + 86400):
        return ""
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    dropped: list[str] = []      # 시각 없는 옛 파일명 행. 아래 가드의 진단용.
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()
        doc = HTMLParser(r.text)
        rows = doc.css(".newProductList li")

        # 셀렉터가 바뀌면 조용히 0건이 된다. 이 페이지는 '신제품 리스트' 하나만
        # 담은 면이라 0행은 고장이다 — 농심이 신제품을 0개로 내릴 일은 없다.
        if not rows:
            raise ValueError(
                f"농심 신제품 목록이 비었다. {r.url} → {len(r.content)}B — "
                f"목록 셀렉터(.newProductList li / h1 / .img img)가 "
                f"바뀌었는지 확인하라")

        # ── 배지 비율 가드 ────────────────────────────────────────────
        # **배지는 존재가 아니라 비율로 믿어야 한다.** 이 레포가 같은 종류로
        # 세 번 데였다:
        #   설빙     `span.flag` 에 시그니처 배지가 섞여 오는데 존재만 보고 다
        #            세서 2013년부터 팔던 인절미설빙이 신상이 됐다(14 → 4건)
        #   퀴즈노스  NEW 가 66건 **전부**에 붙어 있었다 = 신호가 아니라 장식
        #   컴포즈    배지가 썸네일 **그림 안에 합성**돼 HTML 엔 0건. 200건
        #            수집하고 노출 0건이었다(0 → 16건)
        # 농심은 같은 페이지 내비가 전 상품 목록이라 분모를 바로 셀 수 있다.
        # 2026-10-02 실측: 내비 97개 중 NEW 8개 = **8.2%**, 신제품 목록 9건(9.3%).
        # 두 신호가 서로를 받쳐 준다. 어느 쪽이 0% 가 되거나 과반을 넘으면
        # 신호가 깨진 것이므로 조용히 넘기지 않고 터뜨린다.
        nav = doc.css(".sub-item a")
        badged = [a for a in nav if a.css_first("img.new")]
        if nav and not badged:
            raise ValueError(
                f"농심 내비 NEW 배지가 {len(nav)}개 중 0개다. 배지 셀렉터"
                f"(.sub-item a img.new)가 바뀌었거나 배지가 그림 안으로 들어갔는지"
                f" 확인하라 — 컴포즈 선례. 신제품 목록은 {len(rows)}행이다")
        if nav and len(badged) > len(nav) * MAX_NEW_RATIO:
            raise ValueError(
                f"농심 내비 NEW 배지가 {len(nav)}개 중 {len(badged)}개"
                f"({len(badged) / len(nav):.0%})다. 과반이 신제품일 수는 없다 —"
                f" 배지가 장식으로 바뀌었는지 확인하라(퀴즈노스 선례: 66건 전부)")
        if len(rows) > len(nav) * MAX_NEW_RATIO >= 1:
            raise ValueError(
                f"농심 신제품 목록이 {len(rows)}행인데 전 상품이 {len(nav)}개뿐이다."
                f" 신제품 면이 전체 카탈로그로 바뀌었는지 확인하라")

        for li in rows:
            h1 = li.css_first("h1")
            name = " ".join(h1.text().split()) if h1 else ""
            if not name:
                continue
            h2 = li.css_first("h2")
            img = li.css_first(".img img")
            a = li.css_first(".btn a")
            src = (img.attributes.get("src") or "").strip() if img else ""
            href = (a.attributes.get("href") or "").strip() if a else ""
            # 🔴 **옛 파일명(=시각 없음)은 버린다. 이 어댑터에서 제일 비싼 줄이다.**
            # 이 면의 유일한 시간 신호가 사진 파일명의 epoch 다. 그게 없으면
            # 그 행은 **시간에 놓을 수가 없는데**, `is_new=True` 만 달고 나가면
            # `rules.is_fresh()` 의 '날짜 없는 is_new' 분기를 타고 **STALE(90일)
            # 동안 무조건 화면에 오른다**. 설빙 인절미설빙과 같은 사고다.
            # 2026-10-02 실측 — 이게 이론이 아니다:
            #   `농심라면큰사발면` 사진이 `434_bowl.jpg`(옛 이름) 하나뿐이라
            #   시각이 비었다. 농심라면은 1975년 제품을 **2025년 1월에 복각
            #   재출시**한 것이라 이미 21개월 됐는데, 나머지 8건은 전부 60일
            #   창 밖이라 떨어져서 **농심이 화면에 올리는 단 한 건이 이것**이었다.
            # 옛 파일명은 사진을 옛 체계로 올렸다는 뜻이고, 이 면에서 그건
            # 늙은 행의 표식이다. 틀린 걸 올리느니 놓치는 쪽이 이 레포 방침이다.
            uploaded = _uploaded(src)
            if not uploaded:
                dropped.append(name)
                continue
            it = Item(
                brand=BRAND,
                name=name,
                desc=" ".join(h2.text().split()) if h2 else "",
                image=src,
                # 출시일이 아니라 사진 업로드 시각이다. released_at 에 넣지 마라.
                uploaded_at=uploaded,
                # 브랜드가 직접 관리하는 신제품 면이다. 내비 NEW 배지와도 맞는다.
                is_new=True,
                url=SITE + href if href.startswith("/") else (href or LIST),
            )
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)

    # 파일명 체계가 통째로 바뀌면 위 가드가 전건을 버려 조용한 0건이 된다.
    # 목록은 멀쩡한데(위 rows 가드를 통과했다) 상품이 하나도 안 남는 건 고장이다.
    if not items:
        raise ValueError(
            f"농심 신제품 {len(rows)}행에서 사진 epoch 를 하나도 못 읽었다 "
            f"(버린 행={dropped}) — 파일명 체계(`/<13자리>.jpg`)가 바뀌었는지 "
            f"_STAMP 를 확인하라")
    return items
