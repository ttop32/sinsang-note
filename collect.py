#!/usr/bin/env python3
"""수집 → data/products.json 갱신 → docs/index.html 생성.

신제품 판정은 '어제 없던 키가 오늘 있으면 신규'. 첫 실행은 전부 신규가 아니라,
브랜드가 알려주는 uploaded_at 을 first_seen 으로 쓴다(메가는 이미지 파일명에 들어있음).
"""
import html
import inspect
import json
import pathlib
from datetime import date, datetime, timezone

from collectors import cu, ediya, emart24, mega, seven, starbucks

# GS25 는 제외. gs25.gsretail.com/gscvs/* 가 기업 소개 페이지로 301 되고
# 상품 카탈로그는 '우리동네GS' 앱 전용으로 옮겨가 공개 웹 소스가 없다.
ADAPTERS = [mega, starbucks, cu, seven, emart24, ediya]

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

    rows.sort(key=lambda r: (r["first_seen"], r.get("uploaded_at", "")), reverse=True)
    gone = [k for k in prev if k not in {r["key"] for r in rows}]

    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(
        {"updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "count": len(rows), "products": rows},
        ensure_ascii=False, indent=1), encoding="utf-8")

    new_today = [r for r in rows if r["first_seen"] == today and not r["baseline"]]
    baseline = [r for r in rows if r["baseline"]]
    print(f"총 {len(rows)}건 / 오늘 신규 {len(new_today)}건 "
          f"/ 신규 브랜드 기준선 {len(baseline)}건 / 사라짐 {len(gone)}건")
    render(rows, new_today)

    # 데이터는 위에서 이미 썼다. 실패한 어댑터가 있으면 여기서 죽어 Actions 가 빨갛게 뜬다.
    # (워크플로의 커밋 스텝은 if: always() 라 부분 결과는 반영된다.)
    if errors:
        raise SystemExit("어댑터 실패:\n" + "\n".join(errors))


def card(r: dict) -> str:
    e = html.escape
    labels = "".join(f'<span class="lb">{e(l)}</span>' for l in r.get("labels", []))
    return f'''<article class="c">
<img loading="lazy" src="{e(r["image"])}" alt="{e(r["name"])}">
<div class="b"><div class="m">{labels}<span class="br">{e(r["brand"])}</span></div>
<h2>{e(r["name"])}</h2><p class="en">{e(r.get("name_en",""))}</p>
<p class="d">{e(r.get("desc",""))}</p>
<time datetime="{e(r["first_seen"])}">{e(r["first_seen"])}</time></div></article>'''


def render(rows: list, new_today: list) -> None:
    updated = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    banner = (f'<p class="new">오늘 새로 올라온 메뉴 {len(new_today)}건</p>'
              if new_today else "")
    doc = f'''<!doctype html><html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{SITE} — {TAGLINE}</title>
<meta name="description" content="{TAGLINE}. 매일 자동 수집.">
<meta property="og:title" content="{SITE}"><meta property="og:description" content="{TAGLINE}">
<style>
:root{{--bg:#fff;--fg:#16150f;--mut:#6b6a63;--line:#e6e4dc;--card:#fff;--accent:#b4451f}}
@media(prefers-color-scheme:dark){{:root{{--bg:#16150f;--fg:#f2f0e8;--mut:#a3a199;--line:#2e2c24;--card:#1e1c15}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Pretendard",sans-serif}}
.w{{max-width:1100px;margin:0 auto;padding:0 16px}}
header{{padding:40px 0 20px;border-bottom:1px solid var(--line)}}
h1{{margin:0;font-size:26px;letter-spacing:-.02em}}
.sub{{color:var(--mut);margin:6px 0 0;font-size:14px}}
.new{{margin:14px 0 0;color:var(--accent);font-weight:600;font-size:14px}}
.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:20px;padding:28px 0 60px}}
.c{{background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;display:flex;flex-direction:column}}
.c img{{width:100%;aspect-ratio:1;object-fit:cover;background:var(--line);display:block}}
.b{{padding:14px;display:flex;flex-direction:column;gap:4px;flex:1}}
.m{{display:flex;gap:6px;align-items:center;flex-wrap:wrap}}
.lb{{font-size:11px;font-weight:700;padding:2px 6px;border-radius:4px;background:var(--accent);color:#fff}}
.br{{font-size:11px;color:var(--mut)}}
.c h2{{margin:2px 0 0;font-size:16px;line-height:1.35;letter-spacing:-.01em}}
.en{{margin:0;font-size:12px;color:var(--mut)}}
.d{{margin:6px 0 0;font-size:13px;color:var(--mut);flex:1}}
time{{font-size:11px;color:var(--mut);margin-top:10px}}
footer{{border-top:1px solid var(--line);padding:20px 0 40px;color:var(--mut);font-size:13px}}
</style></head><body><div class="w">
<header><h1>{SITE}</h1><p class="sub">{TAGLINE}</p>{banner}</header>
<main class="g">
{chr(10).join(card(r) for r in rows)}
</main>
<footer>마지막 갱신 {updated} · 총 {len(rows)}개 ·
이미지와 상품 정보의 저작권은 각 브랜드에 있습니다.</footer>
</div></body></html>'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc, encoding="utf-8")
    print(f"→ {OUT.relative_to(ROOT)} 생성")


if __name__ == "__main__":
    main()
