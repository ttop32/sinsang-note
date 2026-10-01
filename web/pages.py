"""신제품 낱개 페이지 생성 — 상품 상세 / 브랜드 목록 / 유형 목록.

유입이 전부 검색이라 "메가커피 신메뉴" 같은 검색어가 닿을 페이지가 필요하다.
목록 한 장(docs/index.html)만으로는 그 검색어에 대응할 URL 자체가 없다.

여기서 만드는 건 **신제품(fresh)만**이다. 2,600건 전체 카탈로그를 페이지로 뽑으면
레포가 불어나기도 하지만, 무엇보다 오래된 메뉴를 신상인 척 내보내게 된다.
all_rows 는 '이 브랜드 전체 메뉴 N건' 같은 맥락 숫자에만 쓴다.

색·타이포·URL 은 web/theme.py 것만 쓴다. 여기서 새로 만들지 않는다.
"""
import html
import json
import pathlib
from datetime import date
from urllib.parse import quote, urlsplit

from collectors import base
from web import theme

# 유형 축. collect.SECTIONS 와 같은 순서지만 collect 를 import 하지 않는다 —
# collect 가 나중에 web.pages 를 부르게 되면 순환 import 가 된다.
def _kinds() -> tuple:
    """유형 목록은 collect.SECTIONS 가 정본이다. 여기 따로 두면 어긋난다.
    실제로 5종만 적어놔서 /c/디저트/ 같은 페이지가 없는데 상세가 링크했다."""
    import collect
    return tuple(k for _, k in collect.SECTIONS if k)


KINDS = _kinds()

# 상단 추천에 붙일 같은 브랜드 신제품 개수. 내부 링크가 SEO 의 절반이다.
RELATED = 6

# 사이트 루트. GitHub Pages 가 /sinsang-note/ 아래에 서빙한다.
ROOT_PATH = urlsplit(theme.BASE_URL).path.rstrip("/") + "/"

E = html.escape

EXTRA_CSS = """
.bc{font-size:12px;color:var(--mut);padding:20px 0 0;word-break:keep-all}
.bc a{text-decoration:none}
.bc i{font-style:normal;margin:0 5px;opacity:.45}
.hero{margin:14px 0 0;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:var(--chip)}
@media(min-width:600px){.hero{max-width:420px}}
.hero img,.hero .ph{width:100%;height:auto;aspect-ratio:1;object-fit:cover;display:block}
.tt{margin:18px 0 0;font-size:24px;line-height:1.3;letter-spacing:-.02em;word-break:keep-all}
.bl{margin:8px 0 0;font-size:14px}
.bl a{color:var(--accent);font-weight:600;text-decoration:none}
.dd{margin:12px 0 0;font-size:15px;line-height:1.7;word-break:keep-all}
dl.f{margin:20px 0 0;padding:16px 0 0;border-top:1px solid var(--line);
display:grid;grid-template-columns:76px 1fr;gap:9px 12px;font-size:14px}
dl.f dt{margin:0;color:var(--mut)}
dl.f dd{margin:0;word-break:keep-all}
h2.sec{margin:38px 0 0;font-size:16px;letter-spacing:-.01em}
.more{margin:6px 0 0;font-size:13px;color:var(--mut)}
"""


# ── 작은 도구들 ────────────────────────────────────────────────────────

def _when(r: dict) -> str:
    """정렬용. '언제 것'인가 — 브랜드 날짜 우선, 없으면 처음 본 날."""
    return r.get("released_at") or r.get("uploaded_at") or r.get("first_seen", "")


def _shown_date(r: dict) -> str:
    """화면에 찍을 날짜. 정본은 collect.shown_date 다 — 두 벌로 두면 어긋난다.

    기준선 상품의 first_seen 은 출시일이 아니라 '우리가 처음 본 날'이라 안 찍는다.
    """
    import collect
    return collect.shown_date(r)


def _date_tag(r: dict) -> str:
    """날짜 칸. 모르면 칸 자체를 비운다 — '미상' 을 쓰면 카드마다 그 말이 깔린다."""
    d = _shown_date(r)
    return f'<time datetime="{E(d)}">{E(d)}</time>' if d else ""


def _kind(r: dict) -> str:
    """대표 유형 하나. 상세 페이지의 '이웃 상품' 처럼 한 값만 필요한 자리에 쓴다."""
    return r.get("brand_sub") or r.get("brand_type", "")


def _kinds_of(r: dict) -> list:
    """이 상품이 들어가는 유형 페이지 전부. 대분류와 세부분류 양쪽이다.

    전에는 세부분류 하나만 썼다. 그러면 카페 상품이 전부 '커피'·'베이커리' 로
    흩어져서 /c/카페/ 가 생성 목록에서 빠지고, 프루너가 색인된 그 주소를
    지워버린다. 실제로 /c/카페/ 와 /c/디저트/ 가 그렇게 죽었다.
    """
    import collect
    out = []
    for k in (collect.primary_of(r), r.get("brand_sub", "")):
        if k and k not in out:
            out.append(k)
    return out


def _href(path: str) -> str:
    """사이트 루트 기준 링크. 경로는 theme 의 *_path() 가 준 것만 넣는다."""
    return ROOT_PATH + path


def _img_url(url: str) -> str:
    """og:image 용. 스타벅스 이미지 URL 에 대괄호가 그대로 들어있어 크롤러가 흘린다."""
    return quote(url, safe=":/?#[]@!$&'()*+,;=%~")


def _kdate(iso: str) -> str:
    """2026-09-29 → 2026년 9월 29일. 못 읽으면 원문 그대로 둔다."""
    try:
        d = date.fromisoformat(iso)
    except (TypeError, ValueError):
        return iso or ""
    return f"{d.year}년 {d.month}월 {d.day}일"


def _clip(text: str, n: int = 155) -> str:
    """검색결과 스니펫 길이. 잘렸으면 말줄임표를 붙여 문장이 끊긴 걸 드러낸다."""
    text = " ".join(text.split())
    return text if len(text) <= n else text[:n - 1].rstrip() + "…"


def _ld(obj: dict) -> str:
    """JSON-LD. </script> 가 본문에 섞여도 깨지지 않게 < 를 이스케이프한다."""
    return json.dumps(obj, ensure_ascii=False).replace("<", "\\u003c")


def _crumb(trail: list) -> str:
    """빵부스러기. (라벨, 경로 또는 None) 목록을 받는다."""
    out = []
    for label, path in trail:
        out.append(f'<a href="{_href(path)}">{E(label)}</a>' if path else E(label))
    return '<nav class="bc" aria-label="위치">' + "<i>›</i>".join(out) + "</nav>"


def _card(r: dict) -> str:
    """목록용 카드. collect.card() 와 같은 모양이되 통째로 링크가 된다."""
    sub = _kind(r)
    if r.get("image"):
        alt = f'{r["brand"]} {r["name"]} 제품 이미지'
        img = (f'<img loading="lazy" width="400" height="400" '
               f'src="{E(r["image"])}" alt="{E(alt)}">')
    else:
        img = '<div class="ph"></div>'
    badge = '<span class="lb">NEW</span>' if r.get("is_new") else ""
    tags = "".join(f'<span class="lb lb2">{E(l)}</span>'
                   for l in base.shown_labels(r.get("labels")))
    when = _when(r)
    return (f'<a class="c" href="{_href(theme.product_path(r))}" data-g="{E(sub)}">{img}'
            f'<div class="b"><div class="m">{badge}{tags}'
            f'<span class="br">{E(r["brand"])}</span></div>'
            f'<h2>{E(r["name"])}</h2>'
            f'<p class="d">{E(r.get("desc", ""))}</p>'
            f'{_date_tag(r)}</div></a>')


def _shell(head: str, body: str) -> str:
    return (f'<!doctype html><html lang="ko"><head>\n{head}\n</head>'
            f'<body><div class="w">\n{body}\n'
            f'<footer><a href="{_href("")}">{E(theme.SITE)}</a> · {E(theme.TAGLINE)}<br>'
            f'{theme.NOTICE}</footer>\n'
            f'</div></body></html>')


def _write(out_dir: pathlib.Path, path: str, doc: str) -> str:
    """docs/<path>index.html 로 쓴다. 돌려주는 값이 sitemap 이 쓰는 경로."""
    f = out_dir / path / "index.html"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(doc, encoding="utf-8")
    return path


# ── 상품 상세 ──────────────────────────────────────────────────────────

def product_page(r: dict, siblings: list, neighbors: list) -> str:
    """검색어는 대부분 '브랜드 + 상품명'이라 <title> 을 그 순서로 짠다."""
    path = theme.product_path(r)
    brand, name = r["brand"], r["name"]
    kind = _kind(r)
    when = _when(r)
    desc = (r.get("desc") or "").strip()

    title = f"{brand} {name} — 신제품 | {theme.SITE}"
    meta_desc = _clip(f"{brand} 신제품 {name}. " + desc) if desc else \
        f"{brand}의 신제품 {name}. 출시 정보와 이미지를 확인하세요."

    if r.get("image"):
        alt = f"{brand} {name} 제품 이미지"
        hero = (f'<img width="600" height="600" fetchpriority="high" '
                f'src="{E(r["image"])}" alt="{E(alt)}">')
    else:
        hero = '<div class="ph" role="img" aria-label="이미지 없음"></div>'

    badge = '<span class="lb">NEW</span>' if r.get("is_new") else ""
    tags = "".join(f'<span class="lb lb2">{E(l)}</span>'
                   for l in base.shown_labels(r.get("labels")))
    chips = f'<div class="m">{badge}{tags}</div>' if (badge or tags) else ""

    # 없는 값은 줄 자체를 빼야 한다. "카테고리: -" 는 검색엔진에도 사람에게도 잡음이다.
    facts = [("브랜드", f'<a href="{_href(theme.brand_path(brand))}">{E(brand)}</a>')]
    if kind:
        facts.append(("유형", f'<a href="{_href(theme.kind_path(kind))}">{E(kind)}</a>'))
    if r.get("category"):
        facts.append(("카테고리", E(r["category"])))
    if r.get("name_en"):
        facts.append(("영문명", E(r["name_en"])))
    shown = _shown_date(r)
    if shown:
        facts.append(("등록일",
                      f'<time datetime="{E(shown)}">{E(_kdate(shown))}</time>'))
    fl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts)

    # 추천은 같은 브랜드가 먼저다. 모자라면 같은 유형으로 채운다 — 빈 칸을 두느니
    # 내부 링크를 하나라도 더 만드는 쪽이 낫다.
    rel = siblings[:RELATED]
    filled = rel + [x for x in neighbors if x["key"] not in
                    {y["key"] for y in rel} | {r["key"]}][:RELATED - len(rel)]
    if rel:
        sec = f"{brand}의 다른 신제품" if len(rel) == len(filled) else f"{kind or brand} 신제품 더 보기"
    else:
        sec = f"{kind} 신제품 더 보기" if kind else "다른 신제품"
    related = ""
    if filled:
        related = (f'<h2 class="sec">{E(sec)}</h2>'
                   f'<div class="g">{"".join(_card(x) for x in filled)}</div>')

    ld = _ld({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Product", "name": name, "brand": {"@type": "Brand", "name": brand},
             "description": desc, "category": r.get("category", ""),
             "image": _img_url(r["image"]) if r.get("image") else "",
             "releaseDate": when, "url": theme.BASE_URL + "/" + path},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": i, "name": n,
                 "item": theme.BASE_URL + "/" + p}
                for i, (n, p) in enumerate(
                    [(theme.SITE, "")] +
                    ([(kind, theme.kind_path(kind))] if kind else []) +
                    [(brand, theme.brand_path(brand)), (name, path)], start=1)]},
        ]})

    head = theme.head(title, meta_desc, "/" + path,
                      image=_img_url(r["image"]) if r.get("image") else "",
                      extra=EXTRA_CSS, jsonld=ld)
    trail = [(theme.SITE, "")]
    if kind:
        trail.append((kind, theme.kind_path(kind)))
    trail += [(brand, theme.brand_path(brand)), (name, None)]

    body = (f'{_crumb(trail)}'
            f'<main>'
            f'<div class="hero">{hero}</div>'
            f'{chips}'
            f'<h1 class="tt">{E(name)}</h1>'
            f'<p class="bl"><a href="{_href(theme.brand_path(brand))}">'
            f'{E(brand)} 신메뉴 전체 보기</a></p>'
            + (f'<p class="dd">{E(desc)}</p>' if desc else "")
            + f'<dl class="f">{fl}</dl>'
            f'{related}'
            f'</main>')
    return _shell(head, body)


# ── 목록(브랜드·유형 공용) ─────────────────────────────────────────────

def _list_page(title: str, h1: str, lead: str, meta_desc: str,
               path: str, rows: list, trail: list, note: str = "") -> str:
    ld = _ld({
        "@context": "https://schema.org", "@type": "ItemList",
        "name": h1, "numberOfItems": len(rows),
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": r["name"],
             "url": theme.BASE_URL + "/" + theme.product_path(r)}
            for i, r in enumerate(rows, start=1)],
    })
    img = next((_img_url(r["image"]) for r in rows if r.get("image")), "")
    head = theme.head(title, meta_desc, "/" + path, image=img,
                      extra=EXTRA_CSS, jsonld=ld)
    cards = "".join(_card(r) for r in rows) or (
        '<p class="empty">최근 새로 올라온 제품이 없습니다.<br>매일 아침 다시 확인합니다.</p>')
    body = (f'{_crumb(trail)}'
            f'<header><h1>{E(h1)}</h1><p class="lead">{E(lead)}</p>'
            + (f'<p class="more">{E(note)}</p>' if note else "")
            + f'</header>'
            f'<main class="g">{cards}</main>')
    return _shell(head, body)


def brand_page(brand: str, rows: list, total: int, today: date) -> str:
    """'메가커피 신메뉴' 로 검색하는 사람이 닿을 페이지."""
    ym = f"{today.year}년 {today.month}월"
    title = f"{brand} 신메뉴 — {ym} | {theme.SITE}"
    lead = f"최근 신제품 {len(rows)}건"
    names = ", ".join(r["name"] for r in rows[:5])
    meta_desc = _clip(f"{brand} 신메뉴 {ym} 기준 {len(rows)}건. " +
                      (names if names else "새로 올라온 제품을 매일 모읍니다."))
    note = f"{brand} 전체 메뉴 {total}건 중 최근 등록분입니다." if total else ""
    return _list_page(title, f"{brand} 신메뉴", lead, meta_desc,
                      theme.brand_path(brand), rows,
                      [(theme.SITE, ""), (brand, None)], note)


# 더 이상 상품이 없는 유형. 분류를 다시 짜면서 비었는데, 검색엔진에 색인된
# 주소라 그냥 지우면 들어온 사람이 404 를 본다. 정적 호스팅이라 301 을 못 보내니
# 어디로 갔는지 적은 안내만 남긴다. noindex 를 달아 색인에서는 빠지게 한다.
# 여기 적힌 유형은 프루너가 지우지 않는다(생성 목록에 들어가므로).
RETIRED = {
    "디저트": ["아이스크림", "도넛", "베이커리"],
}


def retired_page(kind: str, goes: list) -> str:
    """빈 유형 안내. 들어온 사람을 대신 갈 곳으로 보낸다."""
    links = " · ".join(
        f'<a href="{_href(theme.kind_path(k))}">{E(k)}</a>' for k in goes)
    # theme.head 의 extra 는 <style> 안으로 들어간다. meta 는 따로 앞에 붙인다.
    head = ('<meta name="robots" content="noindex,follow">\n' + theme.head(
        f"{kind} 신상 | {theme.SITE}",
        f"{kind} 분류는 더 세분해서 {', '.join(goes)} 로 나눴습니다.",
        "/" + theme.kind_path(kind)))
    return _shell(head, (
        f'<header><h1>{E(kind)}</h1>'
        f'<p class="lead">{E(kind)} 분류는 더 세분해서 나눴습니다.</p></header>'
        f'<main><p>{links}</p>'
        f'<p><a href="{_href("")}">신제품 전체 보기</a></p></main>'))


def kind_page(kind: str, rows: list, brands: list, today: date) -> str:
    """'편의점 신상' 같은 유형 검색어용."""
    ym = f"{today.year}년 {today.month}월"
    title = f"{kind} 신상 — {ym} | {theme.SITE}"
    lead = f"최근 신제품 {len(rows)}건"
    meta_desc = _clip(f"{kind} 신제품 {ym} 기준 {len(rows)}건. "
                      f"{', '.join(brands)} 신메뉴를 한 곳에서 봅니다.")
    links = " · ".join(
        f'<a href="{_href(theme.brand_path(b))}">{E(b)}</a>' for b in brands)
    page = _list_page(title, f"{kind} 신상", lead, meta_desc,
                      theme.kind_path(kind), rows,
                      [(theme.SITE, ""), (kind, None)])
    # 유형 → 브랜드 링크를 헤더 밑에 끼워 넣는다. 유형 페이지의 값은 이 갈래길에 있다.
    return page.replace('</header>', f'<p class="more">{links}</p></header>', 1)


# ── 진입점 ────────────────────────────────────────────────────────────

# 굿즈는 홈 탭에 넣지 않는다 — 먹을 걸 보러 온 사람의 1단 탭을 늘리면 375px 폭이
# 깨진다. 대신 유형 페이지 하나로 모으고 푸터에서 링크한다.
GOODS = "굿즈"


def build(fresh: list, all_rows: list, out_dir: pathlib.Path,
          goods: list = ()) -> list:
    """신제품 상세 + 브랜드 목록 + 유형 목록을 만들고 생성한 경로를 돌려준다."""
    today = date.today()
    out_dir = pathlib.Path(out_dir)

    # 슬러그가 겹치면 뒤엣것이 앞엣것을 덮어쓴다. 조용히 사라지느니 먼저(=최신) 것만 남긴다.
    seen, items = set(), []
    for r in fresh:
        p = theme.product_path(r)
        if p in seen:
            continue
        seen.add(p)
        items.append(r)

    order = sorted(items, key=lambda r: (_when(r), r["brand"]), reverse=True)

    by_brand, by_kind = {}, {}
    for r in order:
        by_brand.setdefault(r["brand"], []).append(r)
        for k in _kinds_of(r):
            by_kind.setdefault(k, []).append(r)

    total_by_brand = {}
    for r in all_rows:
        total_by_brand[r["brand"]] = total_by_brand.get(r["brand"], 0) + 1

    paths = []
    for r in order:
        sib = [x for x in by_brand[r["brand"]] if x["key"] != r["key"]][:RELATED]
        nb = [x for x in by_kind.get(_kind(r), []) if x["brand"] != r["brand"]]
        paths.append(_write(out_dir, theme.product_path(r),
                            product_page(r, sib, nb)))

    for brand, rows in by_brand.items():
        paths.append(_write(out_dir, theme.brand_path(brand),
                            brand_page(brand, rows, total_by_brand.get(brand, 0), today)))

    # 유형은 KINDS 순서를 지킨다(목록 화면 탭과 같은 순서). 신제품이 없는 유형은
    # 페이지를 만들지 않는다 — 빈 페이지를 뿌리면 색인 품질만 깎인다.
    for kind in KINDS:
        rows = by_kind.get(kind)
        if not rows:
            continue
        brands = sorted({r["brand"] for r in rows})
        paths.append(_write(out_dir, theme.kind_path(kind),
                            kind_page(kind, rows, brands, today)))

    # 비워진 유형은 안내만 남긴다. paths 에 넣어야 프루너가 안 지운다.
    for kind, goes in RETIRED.items():
        if kind not in by_kind:
            paths.append(_write(out_dir, theme.kind_path(kind),
                                retired_page(kind, goes)))

    # 굿즈. 먹는 게 아니라 본 목록에서는 뺐지만 신제품인 건 맞아서 따로 모은다.
    # 상세도 같이 만든다 — 목록만 있고 상세가 없으면 카드가 메뉴판으로 떨어진다.
    gseen, gitems = set(), []
    for r in sorted(goods, key=lambda r: (_when(r), r["brand"]), reverse=True):
        gp = theme.product_path(r)
        if gp in seen or gp in gseen:
            continue
        gseen.add(gp)
        gitems.append(r)
    if gitems:
        for r in gitems:
            sib = [x for x in gitems
                   if x["brand"] == r["brand"] and x["key"] != r["key"]][:RELATED]
            paths.append(_write(out_dir, theme.product_path(r),
                                product_page(r, sib, [])))
        gbrands = sorted({r["brand"] for r in gitems})
        paths.append(_write(out_dir, theme.kind_path(GOODS),
                            kind_page(GOODS, gitems, gbrands, today)))

    _sweep(out_dir, paths)
    return paths


def _sweep(out_dir: pathlib.Path, paths: list) -> None:
    """이번에 안 만든 상세·목록 페이지를 지운다.

    신제품 창을 벗어난 상품의 페이지가 디스크에 계속 남아 있었다. 사이트맵에는
    없는데 주소로는 열려서, 검색에서 들어온 사람이 몇 달 전 메뉴를 신상으로 본다.
    생성 결과를 정본으로 삼고 그 바깥을 턴다 — 지우는 쪽이라 sitemap 문자열이 아니라
    이번 실행이 실제로 돌려준 경로와 대조해야 한다(전에 접두 'p/' 를 빼고 비교해
    상세 337장을 통째로 날린 적이 있다).
    """
    keep = {(out_dir / rel / "index.html").resolve() for rel in paths}
    # 수집에는 FLOOR 급감 가드가 있는데 삭제에는 대응물이 없었다. 생성이 비정상
    # 적으로 적은 날 이 함수가 사이트를 통째로 턴다. 전에 접두를 빼고 비교해
    # 상세 337장을 날린 적이 있고, 그때도 코드는 조용히 끝까지 돌았다.
    if len(keep) < 10:
        raise RuntimeError(f"생성 경로가 {len(keep)}개뿐이다 — 삭제를 멈춘다")
    gone, leftover = 0, []
    for sub in ("p", "b", "c"):
        d = out_dir / sub
        if not d.is_dir():
            continue
        for child in d.iterdir():
            f = child / "index.html"
            if child.is_dir() and f.is_file() and f.resolve() not in keep:
                f.unlink()
                # 디렉터리에 군더더기가 있으면 rmdir 이 터진다. 거기서 멈추면
                # 이미 지운 앞쪽만 사라진 채로 끝난다 — 지나가고 나중에 알린다.
                try:
                    child.rmdir()
                except OSError:
                    leftover.append(str(child))
                gone += 1
    if gone:
        print(f"→ 더 이상 만들지 않는 페이지 {gone}장 정리")
    if leftover:
        print(f"   !! 빈 디렉터리로 못 지운 것 {len(leftover)}개: {leftover[:3]}")
