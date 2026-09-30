#!/usr/bin/env python3
"""수집 → data/products.json 갱신 → docs/index.html 생성.

신제품 판정은 '어제 없던 키가 오늘 있으면 신규'. 첫 실행은 전부 신규가 아니라,
브랜드가 알려주는 uploaded_at 을 first_seen 으로 쓴다(메가는 이미지 파일명에 들어있음).
"""
import collections
import html
import inspect
import json
import pathlib
from datetime import date, datetime, timedelta, timezone

from collectors import base
from collectors import (burger_burgerking, burger_momstouch, chicken_bbq,
                        chicken_bhc, chicken_kyochon, cu, ediya, emart24,
                        mega, pizza_mrpizza, pizza_pizzahut, seven, starbucks)

# GS25 는 제외. gs25.gsretail.com/gscvs/* 가 기업 소개 페이지로 301 되고
# 상품 카탈로그는 '우리동네GS' 앱 전용으로 옮겨가 공개 웹 소스가 없다.
ADAPTERS = [mega, starbucks, ediya,                                  # 카페
            cu, seven, emart24,                                      # 편의점
            burger_momstouch, burger_burgerking,                     # 햄버거
            chicken_bbq, chicken_bhc, chicken_kyochon,               # 치킨
            pizza_pizzahut, pizza_mrpizza]                           # 피자
# 롯데리아는 뺀다. lotteeatz.com/robots.txt 가 우리 UA 를 전 경로 차단한다.

# 전일 대비 이 비율 밑으로 떨어지면 부분수집으로 보고 실패 처리한다.
# 셀렉터가 하나 깨지면 예외가 아니라 '조용한 부분수집'으로 끝나는 게 이 프로젝트의
# 최대 리스크다. 0건 가드만으로는 절반이 날아가도 통과한다.
FLOOR = 0.7

# 브랜드가 신제품이라고 표시해주지 않는 곳은 날짜로 판단한다. 이 기간 안이면 신제품.
WINDOW = 21

# 브랜드가 NEW 배지를 안 내리는 경우가 있다. 이디야는 2017년 상품에, 버거킹은
# 전체의 31%에 배지가 붙어 있다. 배지를 믿되 날짜가 이만큼 지났으면 신제품이
# 아니라고 본다. WINDOW 보다 넉넉한 건 배지를 몇 달 달아두는 게 흔해서다.
STALE = 90

# 브랜드 하나가 화면을 덮지 못하게 하는 상한. CU 는 NEW 배지 유지 기간이 길어
# 666건이 한꺼번에 올라오고, 그러면 이마트24 가 상위 300건을 덮던 문제가 재발한다.
PER_BRAND = 40

# 첫 화면에 그리는 최대 개수. 전량(2,600건+)을 한 장에 그리면 1MB 를 넘어가고
# 브랜드가 늘수록 감당이 안 된다. 이 사이트의 용건은 '신제품'이라 최신순 앞쪽이
# 대부분의 가치를 갖는다. 전량은 data/products.json 에 그대로 남는다.
SHOW = 300

# 브랜드 하나에서 하루에 이만큼 넘게 새로 등장하면 신제품 출시가 아니라
# 수집 범위가 바뀐 것으로 본다(상한 상향, 파서 개선 등). 그런 건 기준선으로
# 넣어 '오늘 신규'를 오염시키지 않는다. 실제로 이디야 169건·이마트24 590건이
# 이 경로로 들어왔다.
SURGE = 20

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data" / "products.json"
OUT = ROOT / "docs" / "index.html"
SITE = "신상노트"
TAGLINE = "편의점·카페·프랜차이즈 신제품 모아보기"


def load_previous() -> dict:
    if not DATA.exists():
        return {}
    return {p["key"]: p for p in json.loads(DATA.read_text(encoding="utf-8"))["products"]}


def main() -> None:
    today = date.today().isoformat()
    prev = load_previous()
    known_brands = {p["brand"] for p in prev.values()}

    products, errors, failed_brands = [], [], []
    for mod in ADAPTERS:
        try:
            # 이전 수집 결과를 받아 재요청을 줄일 수 있는 어댑터에만 넘긴다(CU 등).
            if "known" in inspect.signature(mod.fetch).parameters:
                items = mod.fetch(known=prev)
            else:
                items = mod.fetch()
            if not items:
                raise RuntimeError("0건 수집 — 파서가 깨졌을 가능성")
            before = sum(1 for p in prev.values() if p["brand"] == mod.BRAND)
            if before and len(items) < before * FLOOR:
                raise RuntimeError(
                    f"수집량 급감 {before} → {len(items)}건 — 부분수집 의심")
            print(f"{mod.BRAND}: {len(items)}건")
            products += items
        except Exception as e:                      # 한 브랜드가 죽어도 나머지는 살린다
            errors.append(f"{mod.BRAND}: {e}")
            failed_brands.append(mod.BRAND)
            print(f"!! {mod.BRAND} 실패: {e}")


    rows = []

    # 실패한 브랜드는 이전 수집분을 그대로 유지한다. 해외 러너에서 국내 사이트가
    # 간헐적으로 DNS 실패하거나 타임아웃 나는데, 그때마다 그 브랜드가 통째로
    # '사라짐' 처리되면 데이터가 깎이고 되돌릴 수 없다.
    carried = [p for p in prev.values() if p["brand"] in failed_brands]
    for c in carried:
        # 이전 수집분은 레지스트리 값이 없을 수 있다(계약이 나중에 늘었다).
        c["brand_type"], c["brand_sub"] = base.kind(c["brand"])
    if carried:
        print(f"   실패 브랜드 이전분 유지: {len(carried)}건")
    rows += carried

    for it in products:
        d = it.to_dict()
        old = prev.get(d["key"])
        if old:
            d["first_seen"] = old.get("first_seen", today)
            d["baseline"] = old.get("baseline", False)
        elif d["brand"] not in known_brands:
            # 브랜드가 막 합류했다. 이건 신제품이 아니라 그 브랜드 메뉴판 전체다.
            # 날짜를 알려주는 브랜드는 소급하고, 나머지는 오늘로 두되 baseline 으로 표시해
            # '오늘 신규' 집계와 화면 배지에서 빼놓는다.
            d["first_seen"] = d.get("uploaded_at") or today
            d["baseline"] = True
        elif d.get("uploaded_at") and d["uploaded_at"] < today:
            # 브랜드가 알려준 등록일이 과거다. 우리가 늦게 발견했을 뿐 신제품이 아니다.
            # (수집기 버그를 고쳐 누락분이 한꺼번에 들어올 때 이 경로를 탄다.)
            d["first_seen"] = d["uploaded_at"]
            d["baseline"] = False
        else:
            d["first_seen"] = today                            # 진짜 신규
            d["baseline"] = False
        rows.append(d)

    # 브랜드별로 오늘 새로 등장한 게 급증이면 수집 범위 변경으로 보고 기준선 처리
    surged = {b for b, n in collections.Counter(
        r["brand"] for r in rows if r["first_seen"] == today and not r["baseline"]
    ).items() if n > SURGE}
    for r in rows:
        if r["brand"] in surged and r["first_seen"] == today and not r["baseline"]:
            r["baseline"] = True
    if surged:
        print(f"   수집범위 변경으로 판단해 기준선 처리: {', '.join(sorted(surged))}")

    rows.sort(key=lambda r: (r["first_seen"], r.get("uploaded_at", "")), reverse=True)
    gone = [k for k in prev if k not in {r["key"] for r in rows}]

    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(
        {"updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "count": len(rows), "products": rows},
        ensure_ascii=False, indent=1), encoding="utf-8")

    fresh = [r for r in rows if is_fresh(r, today)]
    fresh.sort(key=lambda r: (_when(r), r["brand"]), reverse=True)
    fresh = cap_per_brand(fresh)
    new_today = [r for r in fresh if _when(r) == today]
    print(f"총 {len(rows)}건 / 신제품 {len(fresh)}건 (오늘 {len(new_today)}건) / 사라짐 {len(gone)}건")
    render(fresh, new_today)

    # 개별 페이지·sitemap·아이콘. web.seo 가 collect 를 import 하므로 여기서 늦게 부른다.
    from web import assets, pages, seo
    docs = OUT.parent
    paths = pages.build(fresh, rows, docs)
    seo.build(fresh, paths, docs)
    assets.build(docs)
    print(f"→ 개별 페이지 {len(paths)}장 + sitemap·feed·아이콘")

    # 데이터는 위에서 이미 썼다. 실패한 어댑터가 있으면 여기서 죽어 Actions 가 빨갛게 뜬다.
    # (워크플로의 커밋 스텝은 if: always() 라 부분 결과는 반영된다.)
    if errors:
        raise SystemExit("어댑터 실패:\n" + "\n".join(errors))


def cap_per_brand(rows: list) -> list:
    """브랜드별 상한을 적용한다. 날짜순으로 이미 정렬돼 있어 최근 것부터 남는다."""
    seen = collections.Counter()
    out = []
    for r in rows:
        if seen[r["brand"]] < PER_BRAND:
            seen[r["brand"]] += 1
            out.append(r)
    return out


def _when(r: dict) -> str:
    """이 상품이 '언제 것'인가. 브랜드가 준 날짜를 우선하고 없으면 우리가 처음 본 날."""
    return r.get("released_at") or r.get("uploaded_at") or r.get("first_seen", "")


def is_fresh(r: dict, today: str) -> bool:
    """화면에 올릴 신제품인가.

    사용자 요구는 '그날 새로 올라온 것만'이다. 전체 메뉴판은 필요 없다.
    브랜드가 신제품이라고 말해주면 그걸 믿고, 아니면 날짜가 최근인지 본다.
    아무 근거도 없으면 올리지 않는다 — 카탈로그를 신상인 척 내보내는 게
    이 서비스에서 제일 큰 거짓말이다.
    """
    d0 = date.fromisoformat(today)
    cutoff = (d0 - timedelta(days=WINDOW)).isoformat()
    stamped = r.get("released_at") or r.get("uploaded_at")

    # 신제품 근거가 먼저다. 갓 나온 상품이 도입 행사를 하는 건 당연하고,
    # promo 를 먼저 보면 그런 상품이 통째로 잘린다(CU 신제품 107건).
    # promo 는 '신제품 근거 없이 행사라서 목록에 실린 것'을 거르는 용도다.
    if r.get("is_new") is True:
        # 배지는 믿되, 날짜가 한참 전이면 브랜드가 안 내린 것으로 본다.
        stale = (d0 - timedelta(days=STALE)).isoformat()
        return not (stamped and stamped < stale)

    if r.get("promo"):
        return False                      # 행사라서 실린 상품. 신제품 근거가 없다.

    # 브랜드가 준 날짜가 최근이면 신제품이다. 우리가 그 브랜드를 언제 붙였는지와 무관하다.
    # (기준선이라고 빼면 합류 직전에 나온 진짜 신메뉴까지 사라진다.)
    if stamped:
        return stamped >= cutoff

    # 날짜를 안 주는 브랜드는 '어제 없던 게 오늘 있다'로만 판단한다.
    # 합류 시 쌓은 기준선은 그 판단의 출발점이라 신제품이 아니다.
    if r.get("baseline"):
        return False
    return r.get("first_seen", "") >= cutoff


SECTIONS = [("전체", ""), ("편의점", "편의점"), ("카페", "카페"),
            ("햄버거", "햄버거"), ("피자", "피자"), ("치킨", "치킨")]


def card(r: dict) -> str:
    e = html.escape
    sub = r.get("brand_sub") or r.get("brand_type", "")
    img = (f'<img loading="lazy" src="{e(r["image"])}" alt="{e(r["name"])}">'
           if r.get("image") else '<div class="ph"></div>')
    badge = '<span class="lb">NEW</span>' if r.get("is_new") else ""
    tags = "".join(f'<span class="lb lb2">{e(l)}</span>'
                   for l in r.get("labels", []) if l)
    return (f'<article class="c" data-g="{e(sub)}">{img}'
            f'<div class="b"><div class="m">{badge}{tags}'
            f'<span class="br">{e(r["brand"])}</span></div>'
            f'<h2>{e(r["name"])}</h2>'
            f'<p class="d">{e(r.get("desc", ""))}</p>'
            f'<time datetime="{e(_when(r))}">{e(_when(r))}</time></div></article>')


def render(rows: list, new_today: list) -> None:
    counts = collections.Counter()
    for r in rows:
        counts[r.get("brand_sub") or r.get("brand_type", "")] += 1

    tabs = "".join(
        f'<button class="t{" on" if i == 0 else ""}" data-f="{html.escape(key)}">'
        f'{html.escape(label)}<span class="n">{len(rows) if not key else counts.get(key, 0)}</span></button>'
        for i, (label, key) in enumerate(SECTIONS)
        if not key or counts.get(key))

    updated = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    lead = (f"오늘 {len(new_today)}건" if new_today
            else f"최근 {WINDOW}일 신제품 {len(rows)}건")
    body = "\n".join(card(r) for r in rows[:SHOW]) or (
        '<p class="empty">아직 새로 올라온 제품이 없습니다.<br>'
        '매일 아침 다시 확인합니다.</p>')

    doc = f"""<!doctype html><html lang="ko"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#16150f" media="(prefers-color-scheme:dark)">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme:light)">
<title>{SITE} — {TAGLINE}</title>
<meta name="description" content="{TAGLINE}. 편의점·카페·햄버거·피자·치킨 신제품을 매일 자동으로 모읍니다.">
<meta property="og:title" content="{SITE}"><meta property="og:description" content="{TAGLINE}">
<style>
:root{{--bg:#fff;--fg:#16150f;--mut:#6b6a63;--line:#e6e4dc;--card:#fff;--accent:#b4451f;--chip:#f4f2ea}}
@media(prefers-color-scheme:dark){{:root{{--bg:#16150f;--fg:#f2f0e8;--mut:#a3a199;--line:#2e2c24;--card:#1e1c15;--chip:#26241c}}}}
*{{box-sizing:border-box;-webkit-tap-highlight-color:transparent}}
html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:var(--bg);color:var(--fg);
font:16px/1.55 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",Pretendard,sans-serif}}
.w{{max-width:1120px;margin:0 auto;padding:0 16px;padding-left:max(16px,env(safe-area-inset-left));padding-right:max(16px,env(safe-area-inset-right))}}
header{{padding:28px 0 12px}}
h1{{margin:0;font-size:22px;letter-spacing:-.02em}}
.sub{{color:var(--mut);margin:4px 0 0;font-size:13px}}
.lead{{margin:10px 0 0;font-size:14px;font-weight:600;color:var(--accent)}}
nav{{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);
margin:14px -16px 0;padding:8px 16px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}}
nav::-webkit-scrollbar{{display:none}}
.tw{{display:flex;gap:6px;width:max-content}}
.t{{appearance:none;border:1px solid var(--line);background:var(--chip);color:var(--fg);
font:inherit;font-size:14px;padding:9px 14px;border-radius:999px;cursor:pointer;
white-space:nowrap;min-height:40px;display:flex;align-items:center;gap:5px}}
.t.on{{background:var(--accent);border-color:var(--accent);color:#fff}}
.n{{font-size:12px;opacity:.7}}
.g{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;padding:16px 0 56px}}
@media(min-width:600px){{.g{{grid-template-columns:repeat(3,1fr);gap:16px}}}}
@media(min-width:900px){{.g{{grid-template-columns:repeat(4,1fr);gap:20px}}}}
.c{{background:var(--card);border:1px solid var(--line);border-radius:12px;
overflow:hidden;display:flex;flex-direction:column}}
.c img,.ph{{width:100%;aspect-ratio:1;object-fit:cover;background:var(--chip);display:block}}
.b{{padding:11px;display:flex;flex-direction:column;gap:3px;flex:1}}
.m{{display:flex;gap:4px;align-items:center;flex-wrap:wrap;min-height:18px}}
.lb{{font-size:10px;font-weight:700;padding:2px 5px;border-radius:4px;background:var(--accent);color:#fff}}
.lb2{{background:var(--chip);color:var(--mut)}}
.br{{font-size:11px;color:var(--mut)}}
.c h2{{margin:2px 0 0;font-size:14px;line-height:1.35;letter-spacing:-.01em;word-break:keep-all}}
.d{{margin:4px 0 0;font-size:12px;color:var(--mut);flex:1;
display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
time{{font-size:11px;color:var(--mut);margin-top:8px}}
.empty{{grid-column:1/-1;text-align:center;color:var(--mut);padding:64px 0;font-size:14px;line-height:1.8}}
footer{{border-top:1px solid var(--line);padding:18px 0 40px;color:var(--mut);font-size:12px;line-height:1.7}}
</style></head><body><div class="w">
<header><h1>{SITE}</h1><p class="sub">{TAGLINE}</p><p class="lead">{lead}</p></header>
<nav><div class="tw">{tabs}</div></nav>
<main class="g" id="g">
{body}
</main>
<footer>마지막 갱신 {updated} · 최근 {WINDOW}일 신제품 {len(rows)}건<br>
상품 정보와 이미지의 저작권은 각 브랜드에 있습니다.</footer>
</div>
<script>
document.querySelector('nav').addEventListener('click', e => {{
  const b = e.target.closest('.t'); if (!b) return;
  document.querySelectorAll('.t').forEach(t => t.classList.toggle('on', t === b));
  const f = b.dataset.f;
  document.querySelectorAll('#g .c').forEach(c => {{
    c.style.display = (!f || c.dataset.g === f) ? '' : 'none';
  }});
}});
</script>
</body></html>"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc, encoding="utf-8")
    print(f"→ {OUT.relative_to(ROOT)} ({len(doc)//1024}KB)")


if __name__ == "__main__":
    main()
