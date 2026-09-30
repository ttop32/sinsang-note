"""검색엔진·피드 리더가 읽는 산출물과 구조화 데이터.

사람이 보는 HTML 은 web/pages.py 가 만든다. 여기서는 그 결과 경로 목록을 받아
색인 대상으로 적기만 한다. 경로를 직접 조립하지 않는 이유는 하나다 —
생성기와 sitemap 이 각자 만들면 반드시 어긋나고, 없는 URL 이 색인된다.
경로가 필요하면 theme.product_path()/brand_path()/kind_path() 만 쓴다.
"""
import html
import json
import mimetypes
import pathlib
from datetime import datetime, timezone
from urllib.parse import quote

import collect

from . import theme

# 피드에 싣는 최대 건수. 신제품 피드라 최근분이면 용건이 끝난다.
FEED_MAX = 50

# 우리 사이트 경로에서 그대로 둘 문자. 나머지(한글 포함)는 퍼센트 인코딩한다.
# theme.slug() 가 한글을 살려두므로 이 단계가 없으면 sitemap 이 규격을 어긴다.
_PATH_SAFE = "/-._~"

# 외부 이미지 URL 은 최소한만 건드린다. 이미 인코딩된 URL 을 두 번 인코딩하지
# 않도록 %를 남기고, 대괄호는 브랜드 서버가 그 형태로 서빙 중이라 보존한다
# (예: istarbucks .../[9200000007173]_2026....jpg). 공백·따옴표·한글만 인코딩된다.
_URL_SAFE = ":/?#[]@!$&'()*+,;=-._~%"


# ── 문자열 유틸 ──────────────────────────────────────────────────────

def _x(s) -> str:
    """XML 텍스트·속성 이스케이프. 상품명에 &, <, 따옴표가 실제로 들어있다."""
    return html.escape(str(s or ""), quote=True)


def _site_url(path: str) -> str:
    """사이트 루트 기준 상대경로 → 퍼센트 인코딩된 절대 URL."""
    return theme.BASE_URL + "/" + quote(_norm(path), safe=_PATH_SAFE)


def _ext_url(url: str) -> str:
    """브랜드 이미지 등 외부 URL. 규격 위반 문자만 인코딩한다."""
    return quote(str(url or ""), safe=_URL_SAFE)


def _norm(path: str) -> str:
    """경로 표기 흔들림 흡수. 앞의 / 와 끝의 index.html 을 털어낸다."""
    p = str(path or "").lstrip("/")
    if p.endswith("index.html"):
        p = p[: -len("index.html")]
    return p


def _rfc3339(day: str) -> str:
    """YYYY-MM-DD → Atom 이 요구하는 RFC3339. 시각이 없으면 그날 자정 UTC 로 본다."""
    d = str(day or "")
    if len(d) == 10 and d[4] == "-" and d[7] == "-":
        return d + "T00:00:00Z"
    return _now()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── 색인 대상 경로 ───────────────────────────────────────────────────

def _kind_of(r: dict) -> str:
    """화면에서 묶는 축. 프랜차이즈 세부분류가 있으면 그게 우선이다(collect 와 동일)."""
    return r.get("brand_sub") or r.get("brand_type") or ""


def _derive(fresh: list) -> list:
    """page_paths 를 못 받았을 때의 대비책. theme 의 같은 함수를 쓰므로 어긋나지 않는다."""
    out = []
    for r in fresh:
        out.append(theme.product_path(r))
        if r.get("brand"):
            out.append(theme.brand_path(r["brand"]))
        if _kind_of(r):
            out.append(theme.kind_path(_kind_of(r)))
    return out


def _index_paths(fresh: list, page_paths: list) -> list:
    """sitemap 에 적을 경로. 메인이 맨 앞, 나머지는 정렬해 diff 가 흔들리지 않게 한다."""
    given = [_norm(p) for p in (page_paths or [])] or _derive(fresh)
    seen, out = set(), []
    for p in [""] + sorted(given):
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _lastmod(fresh: list) -> dict:
    """경로별 최종 수정일. 상품은 자기 날짜, 목록은 소속 상품 중 가장 최신."""
    m, newest = {}, ""
    for r in fresh:
        w = collect._when(r)
        if not w:
            continue
        newest = max(newest, w)
        for p in (theme.product_path(r),
                  theme.brand_path(r["brand"]) if r.get("brand") else None,
                  theme.kind_path(_kind_of(r)) if _kind_of(r) else None):
            if p and w > m.get(p, ""):
                m[p] = w
    if newest:
        m[""] = newest
    return m


# ── 산출물 ───────────────────────────────────────────────────────────

def _sitemap(paths: list, lastmod: dict) -> str:
    rows = []
    for p in paths:
        when = lastmod.get(p, "")
        # lastmod 는 W3C Datetime. 날짜만 아는 건 날짜만 적는 게 규격에 맞다.
        # 근거가 없는 경로는 아예 비운다 — 모르는 날짜를 지어내지 않는다.
        mod = f"\n  <lastmod>{_x(when)}</lastmod>" if when else ""
        rows.append(f" <url>\n  <loc>{_x(_site_url(p))}</loc>{mod}\n </url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(rows) + "\n</urlset>\n")


def _robots() -> str:
    """전부 허용 + sitemap 위치. 남의 robots.txt 를 지키자고 문서까지 썼으니 우리 것도 둔다."""
    return ("User-agent: *\n"
            "Allow: /\n"
            "\n"
            f"Sitemap: {theme.BASE_URL}/sitemap.xml\n")


def _entry(r: dict) -> str:
    url = _site_url(theme.product_path(r))
    name = r.get("name", "")
    desc = r.get("desc") or f'{r.get("brand", "")} 신제품 {name}'
    img = _ext_url(r.get("image", ""))
    when = _rfc3339(collect._when(r))

    # 이미지는 두 갈래로 낸다. 리더에 따라 enclosure 를 쓰기도, 본문 img 를 쓰기도 한다.
    enc = ""
    inner = f"<p>{html.escape(desc)}</p>"
    if img:
        mime = mimetypes.guess_type(img)[0] or "image/jpeg"
        enc = f'\n  <link rel="enclosure" type="{_x(mime)}" href="{_x(img)}"/>'
        inner = (f'<p><img src="{html.escape(img, quote=True)}"'
                 f' alt="{html.escape(name, quote=True)}"></p>') + inner
    # type="html" 본문은 두 번 감싼다. HTML 로 한 번(속성 안의 따옴표·꺾쇠),
    # XML 로 한 번. 한 번만 하면 상품명에 든 </script> 가 리더에서 태그로 살아난다.
    body = _x(inner)

    return (f" <entry>\n"
            f"  <title>{_x(name)}</title>\n"
            f'  <link rel="alternate" type="text/html" href="{_x(url)}"/>{enc}\n'
            f"  <id>{_x(url)}</id>\n"
            f"  <updated>{_x(when)}</updated>\n"
            f"  <author><name>{_x(r.get('brand', ''))}</name></author>\n"
            f'  <category term="{_x(r.get("brand", ""))}"/>\n'
            f'  <summary type="text">{_x(desc)}</summary>\n'
            f'  <content type="html">{body}</content>\n'
            f" </entry>")


def _feed(fresh: list) -> str:
    rows = sorted(fresh,
                  key=lambda r: (collect._when(r), r.get("brand", ""), r.get("name", "")),
                  reverse=True)[:FEED_MAX]
    updated = _rfc3339(collect._when(rows[0])) if rows else _now()
    home = theme.BASE_URL + "/"
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="ko">\n'
            f" <title>{_x(theme.SITE)} 신제품</title>\n"
            f" <subtitle>{_x(theme.TAGLINE)}</subtitle>\n"
            f" <id>{_x(home)}</id>\n"
            f' <link rel="alternate" type="text/html" href="{_x(home)}"/>\n'
            f' <link rel="self" type="application/atom+xml" href="{_x(home)}feed.xml"/>\n'
            f" <updated>{_x(updated)}</updated>\n"
            f" <author><name>{_x(theme.SITE)}</name></author>\n"
            f" <rights>상품 정보와 이미지의 저작권은 각 브랜드에 있습니다.</rights>\n"
            + "\n".join(_entry(r) for r in rows)
            + ("\n" if rows else "") + "</feed>\n")


def build(fresh: list, page_paths: list, out_dir: pathlib.Path) -> None:
    """sitemap.xml · robots.txt · feed.xml 을 out_dir 에 쓴다.

    page_paths 는 web/pages.py 가 실제로 만든 페이지 경로 목록(사이트 루트 기준
    상대경로)이다. 비어 있으면 fresh 에서 같은 theme 함수로 되짚어 채운다.
    """
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = _index_paths(fresh, page_paths)
    (out / "sitemap.xml").write_text(_sitemap(paths, _lastmod(fresh)), encoding="utf-8")
    (out / "robots.txt").write_text(_robots(), encoding="utf-8")
    (out / "feed.xml").write_text(_feed(fresh), encoding="utf-8")


# ── JSON-LD ─────────────────────────────────────────────────────────
# theme.head(jsonld=...) 가 <script> 안에 그대로 넣으므로, 문자열이 스크립트를
# 조기 종료시키지 못하게 </ 와 <!-- 를 막아둔다.

def _ld(obj) -> str:
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return s.replace("</", "<\\/").replace("<!--", "<\\!--")


def product_jsonld(item: dict) -> str:
    """상품 상세용 Product."""
    d = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": item.get("name", ""),
        "url": _site_url(theme.product_path(item)),
        "description": item.get("desc") or f'{item.get("brand", "")} 신제품 {item.get("name", "")}',
        "brand": {"@type": "Brand", "name": item.get("brand", "")},
    }
    if item.get("image"):
        d["image"] = _ext_url(item["image"])
    cat = item.get("category") or _kind_of(item)
    if cat:
        d["category"] = cat
    when = collect._when(item)
    if when:
        d["releaseDate"] = when
    return _ld(d)


def itemlist_jsonld(items: list, name: str) -> str:
    """목록 페이지용 ItemList. 순서가 곧 화면 순서다."""
    return _ld({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": name,
        "numberOfItems": len(items),
        "itemListElement": [
            {"@type": "ListItem",
             "position": i,
             "name": r.get("name", ""),
             "url": _site_url(theme.product_path(r))}
            for i, r in enumerate(items, 1)
        ],
    })


def website_jsonld() -> str:
    """사이트 전역. 메인에 한 번만 심으면 된다."""
    home = theme.BASE_URL + "/"
    return _ld({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite",
             "name": theme.SITE,
             "alternateName": "sinsang-note",
             "url": home,
             "description": theme.TAGLINE,
             "inLanguage": "ko-KR"},
            {"@type": "BreadcrumbList",
             "itemListElement": [
                 {"@type": "ListItem", "position": 1, "name": theme.SITE, "item": home}
             ]},
        ],
    })
