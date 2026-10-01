"""정적 자산 생성: 파비콘·터치아이콘·매니페스트·공유 커버·404.

theme.head() 가 이미 /sinsang-note/{icon.svg,icon-180.png,manifest.webmanifest}
를 참조하고 있는데 실물이 없었다. 여기서 만든다.

원칙 세 가지.

1. **그림은 코드로 그린다.** 외부 이미지를 받아오지 않는다. 마크의 기하(중심·반지름·
   곡률)를 _sparkle_quads() 한 곳에 두고 SVG 의 path 문자열과 PNG 래스터라이저가
   같은 좌표를 쓴다. 둘이 따로 그려지면 반드시 어긋난다.
   og 커버(og.png)도 같은 이유로 코드로 그린다. 브랜드 상품 사진을 받아 합성하면
   남의 이미지를 우리 도메인에서 재배포하는 것이고, PRODUCT-PLAN §4 가 그걸 금지한다.

2. **색은 theme.py 에서 읽는다.** --accent 같은 토큰을 여기에 다시 적어두면
   theme.py 를 고쳤을 때 아이콘만 옛 색으로 남는다. CSS 문자열에서 뽑아 쓰고,
   못 뽑으면 그때만 폴백 상수를 쓴다.

3. **PNG 은 표준 라이브러리로 직접 인코딩한다.** 2026-10-01 에 requirements.txt 로
   Pillow 가 들어왔지만 여기서는 안 쓴다. 이유는 의존성이 아니라 **폰트**다.
   - 글자를 그리려면 폰트 파일이 필요한데, 맥(/System/Library/Fonts)과
     CI 러너 ubuntu-latest(/usr/share/fonts)는 **겹치는 폰트 경로가 하나도 없다**
     (이 맥에는 /usr/share/fonts 디렉터리 자체가 없다). 어느 쪽을 적어도
     다른 쪽에서 깨지고, 깨진 쪽을 여기서 확인할 방법이 없다.
   - Pillow 내장 기본 폰트에는 한글이 아예 없다. 직접 찍어 보니
     '신상노트'가 두부 네 개(□□□□)로 나왔다. 로마자만 멀쩡하다.
   → 그래서 글자도 폰트가 아니라 **선분 좌표**로 그린다(_GLYPHS). 어느 기계에서
     돌려도 바이트가 같고, 폰트가 없어 조용히 두부가 찍히는 경로가 아예 없다.
   apple-touch-icon 은 iOS 가 SVG 를 받지 않으므로 "SVG 만 쓰자"는 선택지는 iOS
   홈화면 아이콘을 포기하는 것과 같다. 그림이 단색 2도(바탕 1색 + 잉크 1색)뿐이라
   zlib+struct 로 truecolor PNG 를 쓰는 건 100 줄이면 된다. 자세한 건 _scan() 주석 참고.
"""
import json
import math
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
# 색이 두 가지뿐이라 래스터라이저는 스캔라인 하나면 된다.

def _orient(poly: list) -> list:
    """다각형의 감김 방향을 하나로 맞춘다(넓이 부호가 양수가 되게).

    _scan() 이 nonzero 규칙으로 합치므로, 방향이 섞이면 겹친 자리가 서로를
    지워 구멍이 난다. 글자는 선분 사각형 수백 개가 이음매에서 겹친다.
    """
    s = 0.0
    for i, (x0, y0) in enumerate(poly):
        x1, y1 = poly[(i + 1) % len(poly)]
        s += x0 * y1 - x1 * y0
    return poly if s >= 0 else poly[::-1]


def _span(acc: list, xa: float, xb: float, w: int) -> None:
    """한 행의 [xa, xb) 구간을 커버리지에 더한다. 양 끝의 소수점은 면적 그대로."""
    xa = min(max(xa, 0.0), w)
    xb = min(max(xb, 0.0), w)
    if xb <= xa:
        return
    ia, ib = int(xa), min(int(xb), w - 1)
    if ia == ib:
        acc[ia] += xb - xa
    else:
        acc[ia] += ia + 1 - xa
        for c in range(ia + 1, ib):
            acc[c] += 1.0
        acc[ib] += xb - ib


def _scan(polys: list, w: int, h: int, ss: int = 8) -> list:
    """다각형 목록 → w×h 커버리지(0.0~1.0) 행렬.

    수평은 스팬의 소수점 끝단을 그대로 면적으로 더해 정확히 계산하고,
    수직만 ss 배로 과표본한다. 픽셀당 점 검사를 돌리면 파이썬에서 수십 초가
    걸리지만, 이 방식은 (행 × 변) 규모라 180px 아이콘이 0.05초쯤 걸린다.

    합치는 규칙은 nonzero(감김수)다. 아이콘의 스파클 둘은 겹치지 않아
    even-odd 와 결과가 같지만, 커버의 글자는 선분 사각형이 이음매마다 겹치고
    even-odd 로 하면 거기가 뚫린다. 규칙을 둘로 두지 않는다.

    변은 행별로 담아 둔다. 1200×630 커버는 변이 수천 개라, 매 행마다 전부
    훑으면 한 장에 수십 초가 걸린다.
    """
    buckets = [[] for _ in range(h)]
    for poly in polys:
        p = _orient(poly)
        for i, a in enumerate(p):
            b = p[(i + 1) % len(p)]
            if a[1] == b[1]:
                continue
            e = (a, b, 1 if b[1] > a[1] else -1)
            lo = max(0, int(math.floor(min(a[1], b[1]))))
            hi = min(h - 1, int(math.ceil(max(a[1], b[1]))))
            for row in range(lo, hi + 1):
                buckets[row].append(e)

    rows = []
    for py in range(h):
        acc = [0.0] * w
        for sub in range(ss) if buckets[py] else ():
            y = py + (sub + 0.5) / ss
            xs = []
            for (x0, y0), (x1, y1), d in buckets[py]:
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append((x0 + (y - y0) * (x1 - x0) / (y1 - y0), d))
            if not xs:
                continue
            xs.sort()
            wind, start = 0, 0.0
            for x, d in xs:
                if wind == 0:
                    start = x
                wind += d
                if wind == 0:
                    _span(acc, start, x, w)
        rows.append([min(v / ss, 1.0) for v in acc])
    return rows


def _encode(rows: list, bg: tuple, fg: tuple) -> bytes:
    """커버리지 행렬 → truecolor PNG 바이트. 투명도 없음.

    apple-touch-icon 은 투명 영역이 있으면 iOS 가 검게 채우므로 알파를 안 쓴다.
    바탕색과 잉크색을 커버리지로 섞기만 하면 안티에일리어싱이 그대로 나온다.
    """
    h = len(rows)
    w = len(rows[0]) if h else 0
    if not (w and h):
        raise ValueError("빈 이미지는 쓰지 않는다")
    raw = bytearray()
    for row in rows:
        raw.append(0)                       # 필터 타입 0 = None
        for c in row:
            for i in range(3):
                raw.append(int(bg[i] + (fg[i] - bg[i]) * c + 0.5))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)  # 8bit, RGB
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def _mark_polys(cx: float, cy: float, r: float) -> list:
    """마크(주 스파클 + 부 스파클)를 임의의 위치·크기로. 비율은 MAIN/SAT 에서 뽑는다.

    여기서 좌표를 새로 적으면 아이콘과 커버의 마크가 서로 달라진다 — 이 파일 원칙 1번.
    """
    k = r / MAIN[2]
    return [_flatten(cx, cy, r),
            _flatten(cx + (SAT[0] - MAIN[0]) * k, cy + (SAT[1] - MAIN[1]) * k, SAT[2] * k)]


def _raster(size: int, scale: float) -> list:
    """정사각 아이콘용 커버리지. scale 은 중심 기준 축소."""
    k = size / VIEW

    def to_px(pt):
        # 애플 터치아이콘은 iOS 가 자체 마스크로 모서리를 깎으므로 마크를
        # 안쪽으로 물려둬야 잘리지 않는다.
        return ((pt[0] - VIEW / 2) * scale + VIEW / 2) * k, \
               ((pt[1] - VIEW / 2) * scale + VIEW / 2) * k

    return _scan([[to_px(p) for p in _flatten(*MAIN)],
                  [to_px(p) for p in _flatten(*SAT)]], size, size)


def _png(size: int, scale: float = 0.82) -> bytes:
    """단색 바탕 + 크림 마크의 정사각 PNG."""
    return _encode(_raster(size, scale), _rgb(ACCENT), _rgb(MARK))


# ── 글자를 선분으로 그린다 ────────────────────────────────────────────
# 폰트를 안 쓰는 이유는 모듈 docstring 3번에 있다(맥·러너에 공통 폰트 경로가 없고,
# Pillow 기본 폰트에는 한글이 없어 '신상노트'가 두부로 찍힌다).
# 그래서 쓰는 글자만 좌표로 적어 둔다. 한 글자는 (가로폭배수, [획, 획, ...])이고,
# 획은 (x, y) 점들을 잇는 폴리라인이다. x·y 는 글자 상자 안의 0~1 비율,
# y 는 위가 0 아래가 1(= 글자 높이 전체). 점이 하나뿐인 획은 점 하나를 찍는다.
#
# 🔴 여기 없는 글자를 _text() 에 넘기면 KeyError 로 죽는다. 일부러 그렇게 뒀다 —
#    글자 하나가 조용히 빠진 공유 카드가 나가는 것보다 빌드가 죽는 게 낫다.
#    글자를 늘릴 때는 추가하고, 반드시 눈으로 확인해라.

def _ring(cx: float, cy: float, r: float, n: int = 28) -> list:
    """원을 폴리라인으로. 마지막에 첫 점을 다시 넣어 닫는다(획이라 자동으로 안 닫힌다)."""
    pts = [(cx + r * math.cos(2 * math.pi * i / n),
            cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    return pts + [pts[0]]


_GLYPHS = {
    # 로마자 — 기하학적 단선. 곡선은 45° 모따기로 대신한다(마크의 각진 느낌과 맞춘다).
    " ": (0.40, []),
    "A": (0.70, [[(0.02, 1.0), (0.50, 0.0), (0.98, 1.0)], [(0.19, 0.66), (0.81, 0.66)]]),
    "E": (0.60, [[(0.94, 0.0), (0.06, 0.0), (0.06, 1.0), (0.94, 1.0)],
                 [(0.06, 0.50), (0.76, 0.50)]]),
    "G": (0.76, [[(0.96, 0.22), (0.72, 0.0), (0.28, 0.0), (0.04, 0.26), (0.04, 0.74),
                  (0.28, 1.0), (0.72, 1.0), (0.96, 0.74), (0.96, 0.54), (0.56, 0.54)]]),
    "I": (0.22, [[(0.50, 0.0), (0.50, 1.0)]]),
    "N": (0.74, [[(0.06, 1.0), (0.06, 0.0), (0.94, 1.0), (0.94, 0.0)]]),
    "O": (0.78, [[(0.28, 0.0), (0.72, 0.0), (0.96, 0.26), (0.96, 0.74), (0.72, 1.0),
                  (0.28, 1.0), (0.04, 0.74), (0.04, 0.26), (0.28, 0.0)]]),
    "S": (0.68, [[(0.94, 0.18), (0.72, 0.0), (0.26, 0.0), (0.05, 0.20), (0.05, 0.34),
                  (0.26, 0.50), (0.72, 0.50), (0.94, 0.66), (0.94, 0.80), (0.72, 1.0),
                  (0.26, 1.0), (0.05, 0.82)]]),
    "T": (0.66, [[(0.03, 0.0), (0.97, 0.0)], [(0.50, 0.0), (0.50, 1.0)]]),

    # 한글 — 자모가 직선·원이라 선분으로 그리기 좋다. 초성·중성·종성을
    # 상자 안에서 위/오른쪽/아래로 나눠 배치한다.
    # 아래 숫자는 눈으로 맞춘 것이다. 두 가지만 지키면 된다 —
    # ① 초성·중성 덩어리와 종성 사이를 획 두께(0.105)보다 넉넉히 띄울 것.
    #    붙으면 자모가 하나로 뭉쳐 다른 글자로 읽힌다.
    # ② 네 글자의 아래 끝을 0.90~0.95 에 모아 밑선을 맞출 것.
    "신": (1.00, [[(0.05, 0.46), (0.34, 0.02), (0.63, 0.46)],        # ㅅ
                  [(0.87, 0.02), (0.87, 0.46)],                      # ㅣ
                  [(0.09, 0.62), (0.09, 0.95), (0.93, 0.95)]]),      # ㄴ
    "상": (1.00, [[(0.06, 0.44), (0.32, 0.02), (0.58, 0.44)],        # ㅅ
                  [(0.84, 0.02), (0.84, 0.44)],                      # ㅏ 세로
                  [(0.84, 0.24), (0.97, 0.24)],                      # ㅏ 곁가지
                  _ring(0.50, 0.770, 0.180)]),                       # ㅇ
    "노": (1.00, [[(0.17, 0.03), (0.17, 0.42), (0.66, 0.42)],        # ㄴ
                  [(0.50, 0.62), (0.50, 0.92)],                      # ㅗ 세로
                  [(0.05, 0.95), (0.95, 0.95)]]),                    # ㅗ 가로
    "트": (1.00, [[(0.17, 0.03), (0.17, 0.52)],                      # ㅌ 세로
                  [(0.17, 0.03), (0.72, 0.03)],
                  [(0.17, 0.275), (0.70, 0.275)],
                  [(0.17, 0.52), (0.72, 0.52)],
                  [(0.05, 0.90), (0.95, 0.90)]]),                    # ㅡ
}


def _disc(cx: float, cy: float, r: float, n: int = 12) -> list:
    """획 끝·이음매를 막는 원(정n각형). 끝이 네모로 삐져나오지 않게 한다."""
    return [(cx + r * math.cos(2 * math.pi * i / n),
             cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _stroke(points: list, t: float) -> list:
    """폴리라인 하나 → 두께 t 의 다각형 목록. 겹침은 _scan() 의 nonzero 가 합쳐 준다."""
    r = t / 2
    out = [_disc(x, y, r) for x, y in points]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        if length < 1e-9:
            continue
        nx, ny = -dy / length * r, dx / length * r
        out.append([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
                    (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)])
    return out


def _glyph(ch: str) -> tuple:
    """글자 하나의 (가로폭배수, 획들). 없는 글자는 여기서 바로 죽는다."""
    if ch not in _GLYPHS:
        raise KeyError(f"_GLYPHS 에 없는 글자: {ch!r} — 좌표를 추가하고 눈으로 확인해라")
    return _GLYPHS[ch]


def _width(s: str, cap: float, track: float) -> float:
    """글자열의 가로 폭. 가운데 정렬하려면 그리기 전에 알아야 한다."""
    if not s:
        return 0.0
    return sum(_glyph(ch)[0] * cap for ch in s) + track * (len(s) - 1)


def _text(s: str, x: float, y: float, cap: float, weight: float, track: float) -> list:
    """글자열을 다각형 목록으로. x·y 는 글자 상자의 왼쪽 위 모서리, cap 은 글자 높이."""
    polys, cx = [], x
    for ch in s:
        wr, strokes = _glyph(ch)
        box = wr * cap
        for st in strokes:
            polys += _stroke([(cx + px * box, y + py * cap) for px, py in st], weight)
        cx += box + track
    return polys


# ── og 커버 (공유 카드) ───────────────────────────────────────────────

COVER = (1200, 630)   # 카카오톡·슬랙·트위터가 공통으로 기대하는 비율(1.91:1)


def _cover() -> bytes:
    """홈 og:image 로 쓸 1200×630 PNG.

    브랜드 상품 사진을 쓰지 않는 이유는 둘이다. ① 날마다 바뀌어서 공유 카드의
    얼굴이 그날 걸린 아무 브랜드가 된다. ② 그 사진을 받아 합성하면 남의 이미지를
    우리 도메인에서 재배포하는 것이고 PRODUCT-PLAN §4 가 금지한다.

    날짜·건수를 넣지 않는다. 카카오톡·슬랙은 og:image 를 길게 캐시하므로 숫자를
    박으면 대부분의 시점에 틀린 수를 보여주게 되고, 날마다 바이트가 달라져
    저장소에 매일 바이너리 커밋이 쌓인다. 바뀌는 값은 og:title·og:description 이
    글자로 말한다 — 이미지는 '누구인지'만 하면 된다.
    """
    w, h = COVER
    mid = w / 2

    # 가운데 정렬로 쌓는다. 공유 카드는 서비스마다 가장자리를 다르게 잘라서,
    # 한쪽에 몰아 두면 잘린 쪽에서 글자가 반만 보인다.
    #   마크(중심 y 170, 반지름 58) · 한글(285~433) · 로마자(478~508)
    polys = _mark_polys(mid, 170.0, 58.0)

    cap, track = 148.0, 34.0
    polys += _text(theme.SITE, mid - _width(theme.SITE, cap, track) / 2, 285.0,
                   cap, cap * 0.105, track)

    # 작은 로마자 줄은 흐리게 깔아 위계를 만든다. 색이 두 가지뿐이라 커버리지를
    # 낮춰 섞는다 — 알파 채널 없이 같은 효과가 난다.
    sub_cap, sub_track = 30.0, 12.0
    sub = _text("SINSANG NOTE", mid - _width("SINSANG NOTE", sub_cap, sub_track) / 2,
                478.0, sub_cap, 4.2, sub_track)

    ink = _scan(polys, w, h)
    dim = _scan(sub, w, h)
    rows = [[max(a, b * 0.62) for a, b in zip(ra, rb)] for ra, rb in zip(ink, dim)]

    # 조용한 실패 금지. 글자표가 깨지거나 좌표가 화면 밖으로 나가면 바탕색
    # 한 장이 그대로 공유 카드가 된다. 그건 빌드가 죽는 쪽이 낫다.
    painted = sum(1 for row in rows for c in row if c > 0.5)
    if painted < w * h * 0.01:
        raise ValueError(f"og 커버가 거의 비었다 — 칠해진 픽셀 {painted}개")
    return _encode(rows, _rgb(ACCENT), _rgb(MARK))


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
    put("og.png", _cover())
    put("manifest.webmanifest", _manifest())
    put("404.html", _404())
    return written


if __name__ == "__main__":
    import sys
    for f in build(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs")):
        print(f)
