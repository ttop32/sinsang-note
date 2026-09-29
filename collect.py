#!/usr/bin/env python3
"""수집 → data/products.json 갱신 → docs/index.html 생성.

신제품 판정은 '어제 없던 키가 오늘 있으면 신규'. 첫 실행은 전부 신규가 아니라,
브랜드가 알려주는 uploaded_at 을 first_seen 으로 쓴다(메가는 이미지 파일명에 들어있음).
"""
import html
import json
import pathlib
from datetime import date, datetime, timezone

from collectors import mega

ADAPTERS = [mega]

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
    first_run = not prev

    products, errors = [], []
    for mod in ADAPTERS:
        try:
            items = mod.fetch()
            if not items:
                raise RuntimeError("0건 수집 — 파서가 깨졌을 가능성")
            print(f"{mod.BRAND}: {len(items)}건")
            products += items
        except Exception as e:                      # 한 브랜드가 죽어도 나머지는 살린다
            errors.append(f"{mod.BRAND}: {e}")
            print(f"!! {mod.BRAND} 실패: {e}")

    if errors and not products:
        raise SystemExit("모든 어댑터 실패:\n" + "\n".join(errors))

    rows = []
    for it in products:
        d = it.to_dict()
        old = prev.get(d["key"])
        if old:
            d["first_seen"] = old.get("first_seen", today)
        elif first_run:
            d["first_seen"] = d.get("uploaded_at") or today   # 첫 실행은 업로드일로 소급
        else:
            d["first_seen"] = today                            # 진짜 신규
        rows.append(d)

    rows.sort(key=lambda r: (r["first_seen"], r.get("uploaded_at", "")), reverse=True)
    gone = [k for k in prev if k not in {r["key"] for r in rows}]

    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(
        {"updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "count": len(rows), "products": rows},
        ensure_ascii=False, indent=1), encoding="utf-8")

    new_today = [r for r in rows if r["first_seen"] == today] if not first_run else []
    print(f"총 {len(rows)}건 / 오늘 신규 {len(new_today)}건 / 사라짐 {len(gone)}건")
    render(rows, new_today)


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
