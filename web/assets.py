"""정적 자산 생성: 파비콘·터치아이콘·매니페스트·404.

theme.head() 가 이미 /sinsang-note/{icon.svg,icon-180.png,manifest.webmanifest}
를 참조하고 있는데 실물이 없었다. 여기서 만든다.

원칙 세 가지.

1. **그림은 코드로 그린다.** 외부 이미지를 받아오지 않는다. 마크의 기하(중심·반지름·
   곡률)를 _sparkle_quads() 한 곳에 두고 SVG 의 path 문자열과 PNG 래스터라이저가
   같은 좌표를 쓴다. 둘이 따로 그려지면 반드시 어긋난다.

2. **색은 theme.py 에서 읽는다.** --accent 같은 토큰을 여기에 다시 적어두면
   theme.py 를 고쳤을 때 아이콘만 옛 색으로 남는다. CSS 문자열에서 뽑아 쓰고,
   못 뽑으면 그때만 폴백 상수를 쓴다.

3. **PNG 은 표준 라이브러리로 직접 인코딩한다.** 이 저장소의 .venv 에는
   httpx·selectolax 뿐이고 Pillow 가 없다(설치 금지). apple-touch-icon 은 iOS 가
   SVG 를 받지 않으므로 "SVG 만 쓰자"는 선택지는 iOS 홈화면 아이콘을 포기하는
   것과 같다. 마크가 단색 2도(바탕 1색 + 도형 1색)뿐이라 zlib+struct 로
   truecolor PNG 를 쓰는 건 100 줄이면 되고, 그게 의존성을 늘리는 것보다 싸다.
   자세한 건 _png() 주석 참고.
"""
import json
import pathlib
import re
import struct
import zlib

from . import theme

# ── 색 ────────────────────────────────────────────────────────────────
# theme.CSS 의 :root 선언에서 직접 읽는다. 첫 :root 블록이 라이트 테마다.
_FALLBACK = {"accent": "#b4451f", "bg": "#ffffff", "fg": "#16150f", "chip": "#f4f2ea"}


def _rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _token(name: str) -> str:
    """theme.CSS 에서 --name 토큰을 6자리 hex 로 읽는다. 라이트(첫 :root) 기준.

    theme.CSS 는 --bg:#fff 처럼 3자리로 적혀 있는데, 매니페스트·PNG 양쪽에서
    같은 문자열을 쓰려면 길이를 통일해두는 편이 사고가 없다.
    """
    m = re.search(rf"--{name}\s*:\s*(#[0-9a-fA-F]{{3,8}})", theme.CSS)
    return "#%02x%02x%02x" % _rgb(m.group(1) if m else _FALLBACK[name])


ACCENT = _token("accent")          # 마크 바탕 (#b4451f)
# 마크 자체는 --chip(크림) 계열. 강조색 위에 얹어 라이트/다크 어느 쪽 페이지에
# 놓이든 타일이 스스로 대비를 만든다. 배경색에 기대지 않는 게 핵심이다.
MARK = "#f7f4ea"
BG_LIGHT = _token("bg")            # 매니페스트 background_color (#fff)

# ── 마크 기하 (512 viewBox) ───────────────────────────────────────────
# "신상 = 반짝이는 새것". 4각 스파클 하나(주)와 작은 스파클 하나(부).
# 16px 로 줄면 부(副)는 사실상 사라지고 주(主) 하나만 남는데, 그래도 형태가
# 무너지지 않도록 주를 충분히 크고 굵게 잡았다.
VIEW = 512
MAIN = (224.0, 288.0, 168.0)   # cx, cy, R
SAT = (372.0, 150.0, 66.0)
PINCH = 0.28                   # 0=바늘처럼 가늘다, 1=그냥 원. 굵기 조절 손잡이.
RADIUS = 112                   # 타일 모서리 반경 (SVG 전용)


def _sparkle_quads(cx: float, cy: float, r: float) -> list:
    """스파클을 (시작점, 제어점, 끝점) 2차 베지에 4개로 돌려준다.

    꼭짓점은 상·우·하·좌. 제어점을 중심 쪽으로 당길수록(PINCH↓) 변이 오목해져
    끝이 뾰족해진다. SVG path 와 PNG 래스터가 이 함수 하나를 공유한다.
    """
    p = PINCH * r
    n, e, s, w = (cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)
    return [
        (n, (cx + p, cy - p), e),
        (e, (cx + p, cy + p), s),
        (s, (cx - p, cy + p), w),
        (w, (cx - p, cy - p), n),
    ]


def _sparkle_path(cx: float, cy: float, r: float) -> str:
    """SVG path d 속성."""
    q = _sparkle_quads(cx, cy, r)
    d = f"M{q[0][0][0]:g} {q[0][0][1]:g}"
    for _, c, end in q:
        d += f"Q{c[0]:g} {c[1]:g} {end[0]:g} {end[1]:g}"
    return d + "Z"


def _flatten(cx: float, cy: float, r: float, steps: int = 16) -> list:
    """스파클을 다각형 꼭짓점 목록으로 펴 놓는다(PNG 래스터용)."""
    pts = []
    for p0, c, p2 in _sparkle_quads(cx, cy, r):
        for i in range(steps):
            u = i / steps
            v = 1 - u
            pts.append((v * v * p0[0] + 2 * v * u * c[0] + u * u * p2[0],
                        v * v * p0[1] + 2 * v * u * c[1] + u * u * p2[1]))
    return pts


# ── icon.svg ─────────────────────────────────────────────────────────

def _svg() -> str:
    # 파비콘은 브라우저 탭·북마크·검색결과에 쓰인다. 배경 투명으로 두면 다크
    # 탭바에서 어두운 마크가 사라지므로, 색 타일을 깔고 그 위에 크림색 마크를
    # 얹어 어디에 놓이든 같은 대비를 갖게 한다.
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW} {VIEW}" '
        f'role="img" aria-label="{theme.SITE}">'
        f"<title>{theme.SITE}</title>"
        f'<rect width="{VIEW}" height="{VIEW}" rx="{RADIUS}" fill="{ACCENT}"/>'
        f'<path fill="{MARK}" d="{_sparkle_path(*MAIN)}"/>'
        f'<path fill="{MARK}" d="{_sparkle_path(*SAT)}"/>'
        "</svg>"
    )


# ── PNG 인코딩 (표준 라이브러리만) ────────────────────────────────────
# Pillow 없이 PNG 을 만든다. PNG 은 "8비트 truecolor + 필터 0(None) + zlib"
# 조합이면 사양이 아주 단순하다: 시그니처 → IHDR → IDAT → IEND.
# 색이 두 가지뿐이고 도형도 다각형 둘뿐이라 래스터라이저는 스캔라인 하나면 된다.

def _raster(size: int, scale: float) -> list:
    """size×size 픽셀의 마크 커버리지(0.0~1.0) 행렬.

    수평은 스팬의 소수점 끝단을 그대로 면적으로 더해 정확히 계산하고,
    수직만 SS 배로 과표본한다. 픽셀당 점 검사를 돌리면 파이썬에서 수십 초가
    걸리지만, 이 방식은 (행 × 변) 규모라 180px 기준 0.05초쯤 걸린다.
    """
    ss = 8
    k = size / VIEW

    def to_px(pt):
        # scale 은 중심 기준 축소. 애플 터치아이콘은 iOS 가 자체 마스크로
        # 모서리를 깎으므로 마크를 안쪽으로 물려둬야 잘리지 않는다.
        return ((pt[0] - VIEW / 2) * scale + VIEW / 2) * k, \
               ((pt[1] - VIEW / 2) * scale + VIEW / 2) * k

    polys = [[to_px(p) for p in _flatten(*MAIN)], [to_px(p) for p in _flatten(*SAT)]]
    edges = []
    for poly in polys:
        for i, a in enumerate(poly):
            b = poly[(i + 1) % len(poly)]
            if a[1] != b[1]:
                edges.append((a, b))

    rows = []
    for py in range(size):
        acc = [0.0] * size
        for sub in range(ss):
            y = py + (sub + 0.5) / ss
            xs = []
            for (x0, y0), (x1, y1) in edges:
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            if not xs:
                continue
            xs.sort()
            # 두 스파클은 겹치지 않으므로 교차 개수 홀짝(even-odd)으로 충분하다.
            for i in range(0, len(xs) - 1, 2):
                xa = min(max(xs[i], 0.0), size)
                xb = min(max(xs[i + 1], 0.0), size)
                if xb <= xa:
                    continue
                ia, ib = int(xa), min(int(xb), size - 1)
                if ia == ib:
                    acc[ia] += xb - xa
                else:
                    acc[ia] += ia + 1 - xa
                    for c in range(ia + 1, ib):
                        acc[c] += 1.0
                    acc[ib] += xb - ib
        rows.append([min(v / ss, 1.0) for v in acc])
    return rows


def _png(size: int, scale: float = 0.82) -> bytes:
    """단색 바탕 + 크림 마크의 정사각 PNG. 투명도 없음(truecolor).

    apple-touch-icon 은 투명 영역이 있으면 iOS 가 검게 채우고, 직접 깎은
    둥근 모서리는 iOS 마스크와 이중으로 겹친다. 그래서 여기서는 모서리를
    깎지 않고 꽉 찬 정사각으로 낸다.
    """
    bg, fg = _rgb(ACCENT), _rgb(MARK)
    raw = bytearray()
    for row in _raster(size, scale):
        raw.append(0)                       # 필터 타입 0 = None
        for c in row:
            for i in range(3):
                raw.append(int(bg[i] + (fg[i] - bg[i]) * c + 0.5))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)  # 8bit, RGB
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


# ── manifest ─────────────────────────────────────────────────────────

def _root() -> str:
    """사이트 루트의 절대 경로. BASE_URL 이 바뀌면 여기만 따라간다.

    GitHub Pages 프로젝트 사이트라 '/'가 아니라 '/sinsang-note/' 다. 매니페스트의
    start_url·scope 와 404 의 홈 링크가 각자 이 값을 적어두면 반드시 어긋난다.
    """
    host_and_path = theme.BASE_URL.split("//", 1)[-1]
    if "/" not in host_and_path:
        return "/"
    return "/" + host_and_path.split("/", 1)[1].strip("/") + "/"


def _notice() -> str:
    """푸터 고지. 정본은 theme.NOTICE 다 — 여기서 문구를 새로 쓰지 마라."""
    return theme.NOTICE


def _manifest() -> str:
    root = _root()
    return json.dumps({
        "name": f"{theme.SITE} — {theme.TAGLINE}",
        "short_name": theme.SITE,
        "description": f"{theme.TAGLINE}. 매일 아침 자동으로 모읍니다.",
        "lang": "ko",
        "dir": "ltr",
        "start_url": root,
        "scope": root,
        "display": "standalone",
        # theme.head() 가 내보내는 라이트 테마 theme-color(=--bg) 와 맞춘다.
        # 다크는 매니페스트로 표현할 수 없어 meta 쪽에만 남는다.
        "theme_color": BG_LIGHT,
        "background_color": BG_LIGHT,
        "icons": [
            {"src": f"{root}icon.svg", "sizes": "any", "type": "image/svg+xml"},
            {"src": f"{root}icon-180.png", "sizes": "180x180", "type": "image/png"},
            {"src": f"{root}icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    }, ensure_ascii=False, indent=2) + "\n"


# ── 방문자 분석 ───────────────────────────────────────────────────────
# 기본은 꺼둔다. 켤 때는 ANALYTICS 를 고치기만 하면 되고, 코드 수정은 필요 없다.
# 권고안과 비교 근거는 이 모듈을 부른 쪽에 보고한다(요약: GoatCounter).
#
#   goatcounter : 쿠키 0, 방문자 식별자 저장 0(IP+UA 해시를 매일 바뀌는 솔트로
#                 돌려 하루 지나면 대조 불가), 오픈소스, 개인/비상업 무료.
#   cloudflare  : 쿠키 0, 무제한 무료. 다만 폐쇄형이고 CF 계정이 필요하다.
#
# 어느 쪽이든 스크립트를 '넣는 순간' 방문자의 IP 가 제3자 서버에 도달한다는
# 사실은 변하지 않는다. 저장하지 않을 뿐이다. 그 점을 감수할 수 없으면 끈 채로 둔다.
ANALYTICS = {"enabled": False, "provider": "goatcounter", "site": ""}

_SNIPPETS = {
    "goatcounter": '<script data-goatcounter="https://{site}.goatcounter.com/count"'
                   ' async src="//gc.zgo.at/count.js"></script>',
    "cloudflare": '<script defer src="https://static.cloudflareinsights.com/beacon.min.js"'
                  ' data-cf-beacon=\'{{"token":"{site}"}}\'></script>',
}


def analytics_snippet() -> str:
    """분석 스크립트 한 줄. 꺼져 있거나 site 가 비면 빈 문자열."""
    cfg = ANALYTICS
    if not cfg.get("enabled") or not cfg.get("site"):
        return ""
    tpl = _SNIPPETS.get(cfg.get("provider", ""))
    return tpl.format(site=cfg["site"]) if tpl else ""


# ── 404 ──────────────────────────────────────────────────────────────

_404_CSS = """
.nf{padding:72px 0 96px;text-align:center}
.nf .code{font-size:56px;font-weight:800;letter-spacing:-.04em;color:var(--accent);margin:0}
.nf h2{margin:12px 0 0;font-size:18px;font-weight:700;letter-spacing:-.02em}
.nf p{margin:8px 0 0;color:var(--mut);font-size:14px;line-height:1.8}
.nf .home{display:inline-block;margin-top:24px;padding:12px 22px;border-radius:999px;
background:var(--accent);color:#fff;text-decoration:none;font-size:14px;font-weight:600}
"""


def _404() -> str:
    title = f"페이지를 찾을 수 없습니다 — {theme.SITE}"
    desc = f"{theme.SITE}에 없는 주소입니다. {theme.TAGLINE}"
    # canonical 은 없는 페이지 자신이 아니라 홈을 가리키게 한다. 색인은 막는다.
    return f"""<!doctype html><html lang="ko"><head>
{theme.head(title, desc, "/", extra=_404_CSS)}
<meta name="robots" content="noindex,follow">
{analytics_snippet()}
</head><body><div class="w">
<header><h1>{theme.SITE}</h1><p class="sub">{theme.TAGLINE}</p></header>
<main class="nf">
<p class="code">404</p>
<h2>없는 주소입니다</h2>
<p>주소가 바뀌었거나, 제품 페이지가 내려갔을 수 있습니다.<br>
신제품 목록은 아래에서 계속 보실 수 있습니다.</p>
<a class="home" href="{_root()}">신제품 목록으로</a>
</main>
<footer>{_notice()}</footer>
</div></body></html>
"""


# ── 진입점 ───────────────────────────────────────────────────────────

def build(out_dir: pathlib.Path) -> list:
    """정적 자산을 out_dir 에 쓰고 만든 파일 경로 목록을 돌려준다."""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    written = []

    def put(name: str, data) -> None:
        p = out_dir / name
        if isinstance(data, bytes):
            p.write_bytes(data)
        else:
            p.write_text(data, encoding="utf-8")
        written.append(str(p))

    put("icon.svg", _svg())
    put("icon-180.png", _png(180))
    put("icon-512.png", _png(512))
    put("manifest.webmanifest", _manifest())
    put("404.html", _404())
    return written


if __name__ == "__main__":
    import sys
    for f in build(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs")):
        print(f)
