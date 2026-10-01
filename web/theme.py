"""페이지 전체가 공유하는 디자인 토큰과 공통 뼈대.

페이지 종류(목록·상품·브랜드·404)가 늘어도 색·타이포·레이아웃이 갈라지지
않도록 여기 한 곳에서만 정의한다. 각 페이지 모듈은 head()/shell() 을 쓰고
자기 본문만 만든다.
"""
import html

SITE = "신상노트"
TAGLINE = "편의점·카페·프랜차이즈 신제품 모아보기"
BASE_URL = "https://ttop32.github.io/sinsang-note"

# 게시 중단 요청 창구. CRAWLING-POLICY §6 이 "요청이 오면 바로 내린다" 고
# 약속해 놓고 정작 사이트에 연락할 곳이 없었다. 공개 레포의 이슈가 실제로
# 열려 있는 유일한 창구다.
CONTACT = "https://github.com/ttop32/sinsang-note/issues"

# 푸터 고지. 홈·하위 페이지·404 세 군데가 같은 문구를 쓴다. 전에는 세 군데에
# 복붙돼 있어서 한 곳만 고치면 조용히 어긋났다. 여기가 정본이다.
NOTICE = (
    "먹는 것만 모읍니다 — 굿즈와 주류는 목록에서 뺍니다.<br>"
    "상품 정보와 이미지의 저작권은 각 브랜드에 있습니다. "
    f'브랜드 관계자께서 <a href="{CONTACT}" rel="nofollow">게시 중단을 요청</a>하시면 '
    "확인 후 바로 내리겠습니다."
)

CSS = """
:root{--bg:#fff;--fg:#16150f;--mut:#6b6a63;--line:#e6e4dc;--card:#fff;--accent:#b4451f;--chip:#f4f2ea}
@media(prefers-color-scheme:dark){:root{--bg:#16150f;--fg:#f2f0e8;--mut:#a3a199;--line:#2e2c24;--card:#1e1c15;--chip:#26241c}}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);
font:16px/1.55 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",Pretendard,sans-serif}
a{color:inherit}
.w{max-width:1120px;margin:0 auto;padding:0 16px;
padding-left:max(16px,env(safe-area-inset-left));padding-right:max(16px,env(safe-area-inset-right))}
header{padding:28px 0 12px}
h1{margin:0;font-size:22px;letter-spacing:-.02em}
.sub{color:var(--mut);margin:4px 0 0;font-size:13px}
.lead{margin:10px 0 0;font-size:14px;font-weight:600;color:var(--accent)}
footer{border-top:1px solid var(--line);padding:18px 0 40px;color:var(--mut);font-size:12px;line-height:1.7}
.g{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;padding:16px 0 56px}
@media(min-width:600px){.g{grid-template-columns:repeat(3,1fr);gap:16px}}
@media(min-width:900px){.g{grid-template-columns:repeat(4,1fr);gap:20px}}
.c{background:var(--card);border:1px solid var(--line);border-radius:12px;
overflow:hidden;display:flex;flex-direction:column;text-decoration:none}
.c img,.ph{width:100%;aspect-ratio:1;object-fit:cover;background:var(--chip);display:block}
.b{padding:11px;display:flex;flex-direction:column;gap:3px;flex:1}
.m{display:flex;gap:4px;align-items:center;flex-wrap:wrap;min-height:18px}
.lb{font-size:10px;font-weight:700;padding:2px 5px;border-radius:4px;background:var(--accent);color:#fff}
.lb2{background:var(--chip);color:var(--mut)}
.br{font-size:11px;color:var(--mut)}
.c h2{margin:2px 0 0;font-size:14px;line-height:1.35;letter-spacing:-.01em;word-break:keep-all}
.d{margin:4px 0 0;font-size:12px;color:var(--mut);flex:1;
display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
time{font-size:11px;color:var(--mut);margin-top:8px}
.empty{grid-column:1/-1;text-align:center;color:var(--mut);padding:64px 0;font-size:14px;line-height:1.8}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}
"""


def head(title: str, desc: str, path: str = "/", image: str = "",
         extra: str = "", jsonld: str = "") -> str:
    """모든 페이지가 쓰는 <head>. canonical·OG·테마색을 빠뜨리지 않게 한 곳에서 만든다."""
    e = html.escape
    url = BASE_URL + path
    og_img = f'<meta property="og:image" content="{e(image)}">' if image else ""
    ld = f'<script type="application/ld+json">{jsonld}</script>' if jsonld else ""
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#16150f" media="(prefers-color-scheme:dark)">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme:light)">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(SITE)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}">
{og_img}
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/sinsang-note/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/sinsang-note/icon-180.png">
<link rel="manifest" href="/sinsang-note/manifest.webmanifest">
<link rel="alternate" type="application/atom+xml" title="{e(SITE)} 신제품" href="/sinsang-note/feed.xml">
<style>{CSS}{extra}</style>
{ld}"""


# ── URL 규칙 ──────────────────────────────────────────────────────────
# 페이지 생성기와 sitemap 이 각자 경로를 만들면 반드시 어긋난다. 여기서만 만든다.
# GitHub Pages 는 /sinsang-note/ 아래에 서빙되므로 BASE_URL 에 그 접두가 들어있다.
# 아래 함수들은 사이트 루트 기준 상대 경로를 돌려준다(앞에 / 없음).

def slug(text: str) -> str:
    """한글을 살린 URL 조각. 검색엔진이 한글 URL 을 읽으므로 로마자화하지 않는다."""
    import re
    s = re.sub(r"[^\w가-힣]+", "-", text.strip())
    return re.sub(r"-{2,}", "-", s).strip("-").lower()[:60]


def product_path(item: dict) -> str:
    """상품 상세. 예: p/메가mgc커피-하우스밀크-라떼/"""
    return f"p/{slug(item['brand'])}-{slug(item['name'])}/"


def brand_path(brand: str) -> str:
    """브랜드 목록. 예: b/스타벅스/"""
    return f"b/{slug(brand)}/"


def kind_path(kind: str) -> str:
    """유형 목록. 예: c/편의점/"""
    return f"c/{slug(kind)}/"
