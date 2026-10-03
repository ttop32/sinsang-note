"""홈(docs/index.html) 한 장. 카드·검색·탭이 전부 여기 있다.

나머지 1,400여 장은 web/pages.py 가 만든다. 홈만 따로인 건 검색·필터가
붙은 유일한 장이라 인라인 스크립트가 통째로 들어가서다.
"""
import collections
import html
import pathlib
from datetime import datetime, timezone

import rules
import taxonomy
from collectors import base
from web import seo, theme

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "index.html"

ROOT_PATH = theme.ROOT_PATH
SITE = theme.SITE
TAGLINE = theme.TAGLINE

CSS_EXTRA = """
/* 홈 전용. 공통 토큰·카드·그리드는 web/theme.py CSS 가 정의한다. */
.skip{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.skip:focus{position:fixed;left:16px;top:8px;width:auto;height:auto;z-index:9;
background:var(--accent);color:#fff;padding:8px 12px;border-radius:8px;text-decoration:none}

.tools{display:flex;gap:8px;margin-top:14px}
#q{flex:1;min-width:0;font:inherit;font-size:15px;padding:10px 14px;border-radius:999px;
border:1px solid var(--line);background:var(--chip);color:var(--fg);min-height:42px;
-webkit-appearance:none;appearance:none}
#q::placeholder{color:var(--mut)}
#q:focus{outline:none;border-color:var(--accent)}
/* 검색 추천. 입력칸 바로 아래 겹쳐 띄운다 — 자리를 차지하면 카드가 밀린다. */
.qwrap{position:relative;flex:1;min-width:0;display:flex}
#sug{position:absolute;top:calc(100% + 4px);left:0;right:0;z-index:8;margin:0;
padding:4px;list-style:none;background:var(--bg);border:1px solid var(--line);
border-radius:12px;box-shadow:0 6px 24px rgba(0,0,0,.12);max-height:46vh;overflow:auto}
#sug li{padding:9px 12px;border-radius:8px;font-size:15px;cursor:pointer;
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#sug li[aria-selected="true"],#sug li:hover{background:var(--chip)}
#sug .k{float:right;margin-left:10px;font-size:12px;color:var(--mut)}
#sort{flex:none}
.cnt{margin:10px 0 0;font-size:12px;color:var(--mut);min-height:16px}
/* 푸터의 분류·업체 목록. 업체가 50곳 넘어서 그냥 흘리면 푸터가 화면을 덮는다. */
.fl{margin:10px 0;line-height:2}
.fl b{display:block;font-weight:600;color:var(--fg);margin-bottom:2px}
.fl a{margin-right:2px}
.bn{font-size:10px;color:var(--mut);margin:0 8px 0 2px}

nav{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);
margin:12px -16px 0;padding:10px 16px;overflow-x:auto;-webkit-overflow-scrolling:touch;
scrollbar-width:none}
nav::-webkit-scrollbar{display:none}
.tw{display:flex;gap:6px;width:max-content}
.t{appearance:none;-webkit-appearance:none;border:1px solid var(--line);background:var(--chip);
color:var(--fg);font:inherit;font-size:14px;line-height:1;padding:0 10px;border-radius:999px;
cursor:pointer;white-space:nowrap;min-height:40px;display:inline-flex;align-items:center;gap:6px}
.t.on{background:var(--accent);border-color:var(--accent);color:#fff}
.t .n{font-size:12px;opacity:.7}
/* 2단은 가로로 흐른다. 외식이 7칩 500px 이라 375px 화면에서는 뒤가 잘리는데,
   스크롤 막대를 숨겨놔서 더 있다는 걸 알 수가 없었다. 오른쪽 끝에 그라데이션을
   깔아 "뒤에 더 있다" 를 보여준다. 끝까지 밀면 사라진다(아래 스크립트). */
.subnav{margin:0 -16px;padding:8px 16px;overflow-x:auto;scrollbar-width:none;
border-bottom:1px solid var(--line);position:relative}
.subnav::-webkit-scrollbar{display:none}
.subwrap{position:relative}
.subwrap::after{content:"";position:absolute;right:0;top:0;bottom:1px;width:36px;
pointer-events:none;opacity:0;transition:opacity .15s;
background:linear-gradient(90deg,transparent,var(--bg) 70%)}
.subwrap.more::after{opacity:1}
.t.s{min-height:34px;font-size:13px;padding:0 12px;background:transparent}
.t.s.on{background:var(--fg);border-color:var(--fg);color:var(--bg)}

/* 넓은 화면에서는 줄을 바꾼다. 가로 스크롤은 375px 에서 세로를 아끼려고
   둔 것이지, 자리가 남는데도 칩을 자를 이유가 없다. 실제로 외식 탭의
   '일식 44' 가 '일식 4' 로 잘려 **숫자가 틀리게 읽혔다** — 안 보이는 것보다
   틀리게 보이는 게 나쁘다. 줄바꿈하면 잘릴 일 자체가 없어서 끝 그라데이션도
   같이 끈다. 기준 560px 는 1단 탭 5개가 들어가고도 남는 폭이다. */
@media (min-width: 560px){
  .subnav{overflow-x:visible;margin:0;padding:8px 0}
  .subnav .tw{width:auto;flex-wrap:wrap;row-gap:6px}
  .subwrap::after{display:none}
  nav .tw{flex-wrap:wrap;row-gap:6px;width:auto}
}

a.c{text-decoration:none;color:inherit;transition:border-color .15s}
a.c:hover,a.c:focus-visible{border-color:var(--accent)}
.c[hidden]{display:none}
/* .t 가 display:inline-flex 라 브라우저 기본 [hidden]{display:none} 을 이긴다.
   카드(.c)에서 같은 사고가 났을 때 그쪽만 고치고 칩은 놔뒀다 — 그래서 2단
   칩이 지금껏 한 번도 안 숨겨졌고, 카페를 골라도 치킨·피자 칩이 남아 있었다. */
.t[hidden]{display:none}          /* .c 의 display:flex 가 브라우저 기본 [hidden] 을 덮는다 */
.go{display:block;padding:0 11px 12px;font-size:11px;color:var(--accent);font-weight:600}
.en{margin:0;font-size:11px;color:var(--mut)}
/* 주류 표시. NEW 와 같은 칩이되 색으로 구분한다. */
.lb19{background:#8a1b1b}
"""




def _date_tag(r: dict) -> str:
    """날짜 칸. 모르면 칸 자체를 비운다 — '미상' 을 쓰면 카드마다 그 말이 깔린다."""
    d = rules.shown_date(r)
    return f'<time datetime="{html.escape(d)}">{html.escape(d)}</time>' if d else ""


def card(r: dict) -> str:
    e = html.escape
    sub = taxonomy.sub_of(r)
    pri = taxonomy.primary_of(r)
    img = (f'<img loading="lazy" decoding="async" width="400" height="400"'
           f' src="{e(r["image"])}" alt="{e(r["brand"])} {e(r["name"])}">'
           if r.get("image") else '<div class="ph" aria-hidden="true"></div>')
    badge = '<span class="lb">NEW</span>' if r.get("is_new") else ""
    # 술은 보기만 해도 술인 줄 알아야 한다. 구매는 우리 쪽에서 일어나지 않지만
    # 미성년자가 섞여 들어온 카드를 모르고 누르는 일은 없게 한다.
    if r.get("alcohol"):
        badge += '<span class="lb lb19">19</span>'

    # 1+1·2+1 은 뺀다. 편의점은 신상품에 도입 행사를 거의 항상 붙여서(세븐일레븐
    # 신상품 탭 91건 전부) 그대로 두면 신상 목록이 할인 목록처럼 읽힌다.
    # 행사 정보 자체는 data/products.json 과 상세 페이지에 남는다.
    tags = "".join(f'<span class="lb lb2">{e(l)}</span>'
                   for l in base.shown_labels(r.get("labels")))
    # 카드를 누르면 브랜드의 그 상품 페이지로 간다. 우리가 정보를 붙들지 않고
    # 트래픽을 브랜드로 돌려주는 구조여야 한다.
    #
    # 다만 상품 페이지가 아예 없는 브랜드가 있다(메가·빽다방·프랭크버거·이마트24
    # — 카드에 href 가 없고 같은 페이지 모달로 뜬다). 그런 곳을 메뉴판으로
    # 보내면 사용자가 그 제품을 다시 찾아야 한다. 차라리 우리 상세 페이지로
    # 보낸다. 사진·설명·날짜가 다 있고 거기서 브랜드로 한 번 더 나갈 수 있다.
    url, external = r.get("url", ""), True
    if not url or url == base.site(r["brand"]):
        from web import theme
        url, external = ROOT_PATH + theme.product_path(r), False
    # 영문명은 화면 보조이자 검색 대상이다("Latte" 로 검색해도 걸리게)
    en = f'<p class="en">{e(r["name_en"])}</p>' if r.get("name_en") else ""
    inner = (f'{img}<div class="b"><div class="m">{badge}{tags}'
             f'<span class="br">{e(r["brand"])}</span></div>'
             f'<h2>{e(r.get("display") or r["name"])}</h2>{en}'
             f'<p class="d">{e(r.get("desc", ""))}</p>'
             f'{_date_tag(r)}</div>')
    # 외부(브랜드)로 나갈 때만 새 탭 + nofollow. 우리 상세는 같은 탭.
    attrs = ' target="_blank" rel="noopener nofollow"' if external else ""
    go = "브랜드에서 보기" if external else "자세히 보기"
    # 화면에는 다듬은 이름을 쓰지만 원본도 검색에 걸려야 한다. POS 이름
    # (롯데)꼬깔콘애플시나몬)으로 찾던 사람이 0건을 보면 안 된다.
    raw = r["name"] if (r.get("display") or r["name"]) != r["name"] else ""
    return (f'<a class="c" data-p="{e(pri)}" data-s="{e(sub)}"'
            f'{f' data-raw="{e(raw)}"' if raw else ""}'
            f' href="{e(url)}"{attrs}>{inner}'
            f'<span class="go">{go} &rarr;</span></a>')


def render(rows: list, new_today: list, total: int = 0) -> None:
    """홈 한 장. rows 는 브랜드 상한을 거친 목록, total 은 상한 전 전체 건수다.

    둘을 구분해야 푸터가 거짓말을 안 한다 — 상한이 헤드라인 숫자까지 줄이면
    '신제품 329건' 이라고 써놓고 실제로는 1,403건의 페이지가 있게 된다.
    """
    # 숫자는 화면에 실제로 있는 것만 센다. 전에 len(rows) 를 써서 "483건" 이라
    # 써놓고 끝까지 내려도 300장뿐이던 적이 있다. 지금은 rules.SHOW=0 이라 안 자른다.
    shown = rows[:rules.SHOW] if rules.SHOW else rows
    more = len(rows) - len(shown)
    pcount = collections.Counter(taxonomy.primary_of(r) for r in shown)
    scount = collections.Counter(x for x in map(taxonomy.sub_of, shown) if x)

    tabs = "".join(
        f'<button class="t{" on" if i == 0 else ""}" data-f="{html.escape(key)}"'
        f' aria-pressed="{"true" if i == 0 else "false"}">'
        f'{html.escape(label)}</button>'
        for i, (label, key) in enumerate(taxonomy.PRIMARY)
        if not key or pcount.get(key))
    # 건수 많은 순. 가로로 흐르는 줄이라 화면 안에 드는 건 앞의 네댓 개뿐이고,
    # 선언 순서대로 깔면 제일 볼 게 많은 분류가 화면 밖으로 밀린다.
    # 맨 앞에 '전체'. 세부를 골랐다가 되돌릴 길이 다시 누르는 것뿐이었는데
    # 그걸 아는 사람이 없다. 그리고 카페는 145장 중 커피가 94장이라 첫 칩이
    # 커피면 "왜 커피부터지" 가 된다 — 기본값이 뭔지 보여줘야 한다.
    subs = ('<button class="t s on" data-s="" aria-pressed="true">'
            '전체<span class="n"></span></button>')
    subs += "".join(
        f'<button class="t s" data-s="{html.escape(k)}" aria-pressed="false">'
        f'{html.escape(k)}<span class="n">{scount[k]}</span></button>'
        for k in sorted((k for k in taxonomy.SUBS if scount.get(k)),
                        key=lambda k: (k in taxonomy.DEMOTE,
                                       -scount[k], taxonomy.SUBS.index(k))))

    updated = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    # 홈에서 /c/ 로 나가는 길이 하나도 없었다. rules.SHOW 가 자른 분량과, 홈 칩에
    # 안 뜨는 분류(화면 300장 안에 한 건도 없는 유형)가 여기서만 닿는다.
    from web import theme as _t
    kinds = [k for _, k in taxonomy.SECTIONS if k and any(
        taxonomy.primary_of(r) == k or r.get("brand_sub") == k or r.get("brand_type") == k
        for r in rows)]
    klinks = " · ".join(
        f'<a href="{ROOT_PATH}{_t.kind_path(k)}">{html.escape(k)}</a>' for k in kinds)
    klinks += f' · <a href="{ROOT_PATH}{_t.kind_path("굿즈")}">굿즈</a>'
    # 업체별로도 찾는다. /b/ 는 만들어만 놓고 사이트 어디서도 링크하지 않아
    # 사이트맵으로만 닿을 수 있었다. 건수 많은 순, 이름순은 동점일 때만.
    bcount = collections.Counter(r["brand"] for r in rows)
    blinks = " · ".join(
        f'<a href="{ROOT_PATH}{_t.brand_path(b)}">{html.escape(b)}</a>'
        f'<span class="bn">{n}</span>'
        for b, n in sorted(bcount.items(), key=lambda kv: (-kv[1], kv[0])))
    whole = total or len(rows)
    # 숫자가 다르면 왜 다른지까지 말해야 한다. 전에는 "1,237건 — 이 화면에
    # 360장" 이라고만 써서 나머지 877장이 어디 갔는지 알 수가 없었다.
    count = (f"최근 {rules.WINDOW}일 신제품 {whole}건 · "
             f"브랜드마다 최신 {rules.PER_BRAND}장씩 {len(shown)}장"
             if whole > len(shown) else f"최근 {rules.WINDOW}일 신제품 {len(shown)}건")
    lead = (f"오늘 {len(new_today)}건" if new_today
            else f"최근 {rules.WINDOW}일 신제품 {len(shown)}건")
    # 공유 카드에 그날 첫 상품의 브랜드 CDN 사진이 나가고 있었다. 날마다 바뀌고
    # 남의 얼굴이다. 코드로 그린 우리 커버를 쓴다(web/assets.py 가 만든다).
    # 콜라주는 반려됐다 — 브랜드 이미지를 받아 합성한 사본을 우리 도메인에서
    # 재배포하는 것이라 "브랜드 이미지 자체 호스팅 금지" 와 충돌한다.
    _head = theme.head(
        f"{SITE} — {TAGLINE}",
        f"{TAGLINE}. 편의점·카페·햄버거·피자·치킨·베이커리 신제품을 매일 자동으로 모읍니다.",
        "/", image=ROOT_PATH + "og.png",
        # 홈에만 JSON-LD 가 없었다. 하위 페이지는 web/pages 가 자기 것을 넣는다.
        jsonld=seo.website_jsonld(),
        extra=CSS_EXTRA)

    body = "\n".join(card(r) for r in shown) or (
        '<p class="empty">아직 새로 올라온 제품이 없습니다.<br>'
        '매일 아침 다시 확인합니다.</p>')

    doc = f"""<!doctype html><html lang="ko"><head>
{_head}
</head><body><div class="w">
<a class="skip" href="#g">본문으로 건너뛰기</a>
<header><h1>{SITE}</h1><p class="sub">{TAGLINE}</p><p class="lead">{lead}</p></header>
<div class="tools">
  <div class="qwrap">
    <input id="q" type="search" placeholder="상품·브랜드 검색" aria-label="상품 또는 브랜드 검색"
           autocomplete="off" enterkeyhint="search" role="combobox"
           aria-expanded="false" aria-controls="sug" aria-autocomplete="list">
    <ul id="sug" role="listbox" aria-label="검색 추천" hidden></ul>
  </div>
  <button id="sort" class="t" data-s="date" aria-label="정렬 바꾸기">최신순</button>
</div>
<nav aria-label="분류"><div class="tw">{tabs}</div></nav>
<div class="subwrap" id="subwrap" hidden><div class="subnav" id="subnav"><div class="tw">{subs}</div></div></div>
<p id="cnt" class="cnt" role="status" aria-live="polite"></p>
<main class="g" id="g">
{body}
<p class="empty" id="noresult" hidden>찾는 제품이 없습니다.<br>다른 말로 검색해 보세요.</p>
</main>
<footer>마지막 갱신 {updated} · {count}
<div class="fl"><b>분류</b> {klinks}</div>
<div class="fl"><b>업체</b> {blinks}</div>
{theme.NOTICE}<br>
<a href="{ROOT_PATH}feed.xml">RSS 구독</a></footer>
</div>
<script>
const g = document.getElementById('g'), q = document.getElementById('q'),
      cnt = document.getElementById('cnt'), sortBtn = document.getElementById('sort'),
      subnav = document.getElementById('subnav'),
      subwrap = document.getElementById('subwrap'),
      empty = document.getElementById('noresult');
const cards = [...g.querySelectorAll('.c')];
const priBtns = [...document.querySelectorAll('nav .t')];
const subBtns = [...subnav.querySelectorAll('.t.s')];

cards.forEach((c, i) => {{
  c.dataset.i = i;                                  // 원래 순서(최신순)
  // 카드 안 UI 문구("브랜드에서 보기")까지 색인하면 그 말로 전건이 걸린다.
  // 원본 상품명(data-raw)도 색인한다. 화면에는 다듬은 이름만 보이지만
  // 'CJ)얼큰우동221g' 처럼 POS 이름으로 찾는 사람이 있다.
  c.dataset.q = ([c.querySelector('h2'), c.querySelector('.en'),
                  c.querySelector('.br'), c.querySelector('.d')]
      .filter(Boolean).map(n => n.textContent).concat(c.dataset.raw || [])
      ).join(' ').toLowerCase();
  c.dataset.b = (c.querySelector('.br') || {{}}).textContent || '';
}});

let kind = '', sub = '', words = [];

function apply() {{
  let n = 0;
  for (const c of cards) {{
    const ok = (!kind || c.dataset.p === kind)
            && (!sub  || c.dataset.s === sub)
            // 통째로 찾으면 '얼큰 우동'·'바닐라 라떼' 가 0건이 된다. 상품명은
            // 붙여 쓰는데(얼큰우동) 사람은 띄어서 친다. 낱말마다 따로 본다.
            && words.every(w => c.dataset.q.includes(w));
    c.hidden = !ok;
    if (ok) n++;
  }}
  const filtering = kind || sub || words.length;
  cnt.textContent = filtering ? n + '건' : '';
  empty.hidden = n > 0;
  if (!n) showEmpty();
}}

// 0건일 때 무엇 때문인지 말해준다. 전에는 탭 조합 탓인데도 "다른 말로
// 검색해 보세요" 라고 해서 엉뚱한 쪽을 가리켰다.
function showEmpty() {{
  const on = [];
  if (kind) on.push(kind);
  if (sub) on.push(sub);
  if (words.length) on.push('\u2018' + words.join(' ') + '\u2019');
  empty.innerHTML = on.length
    ? on.join(' + ') + ' 에 해당하는 제품이 없습니다.'
      + '<br><button type="button" class="t" id="reset">조건 모두 지우기</button>'
    : '찾는 제품이 없습니다.<br>다른 말로 검색해 보세요.';
}}

function resetAll() {{
  kind = ''; sub = ''; words = []; q.value = ''; closeSug();
  priBtns.forEach((t, i) => {{
    t.classList.toggle('on', i === 0);
    t.setAttribute('aria-pressed', i === 0);
  }});
  subBtns.forEach(x => {{
    const on = !x.dataset.s;
    x.classList.toggle('on', on); x.setAttribute('aria-pressed', on);
  }});
  syncSub(); apply();
}}

document.addEventListener('click', e => {{
  if (e.target.id === 'reset') resetAll();
}});

function syncSub() {{
  // 그 대분류에 실제로 있는 세부만 남기고 **숫자도 그 대분류 안에서 센다.**
  // 전에는 숫자가 전체 기준이라 '가공식품 > 커피 95' 라고 써놓고 누르면
  // 1건이 나왔다 — 95는 카페의 커피였다. 숫자와 필터의 범위가 달랐다.
  let any = false;
  const inKind = cards.filter(c => !kind || c.dataset.p === kind);
  for (const b of subBtns) {{
    // data-s 가 빈 것이 '전체' 칩이다. 늘 보이고 숫자는 그 대분류 총합이다.
    const all = !b.dataset.s;
    const n = all ? inKind.length
                  : inKind.filter(c => c.dataset.s === b.dataset.s).length;
    const tag = b.querySelector('.n');
    if (tag) tag.textContent = n;
    b.hidden = !all && !n;
    if (!all && n) any = true;
  }}
  // '전체' 에서는 숨긴다. 13칩 1,051px 중 676px 가 화면 밖인 데다 커피·라면·
  // 일식·햄버거가 뒤섞여 있어 고르는 데 도움이 안 된다.
  // 칩이 하나뿐일 때도 숨긴다 — 고를 게 없으면 필터가 아니라 라벨이다.
  const shownChips = subBtns.filter(b => !b.hidden && b.dataset.s).length;
  subwrap.hidden = !kind || shownChips < 2;
  subnav.scrollLeft = 0;
  hint();
}}

// 2단이 가로로 넘치면 오른쪽에 그라데이션을 켠다. 스크롤 막대를 숨겨놔서
// 더 있다는 걸 알 수가 없었다. 끝까지 밀면 끈다.
function hint() {{
  const left = subnav.scrollWidth - subnav.clientWidth - subnav.scrollLeft;
  subwrap.classList.toggle('more', left > 4);
}}
subnav.addEventListener('scroll', hint, {{passive: true}});
addEventListener('resize', hint);

document.querySelector('nav').addEventListener('click', e => {{
  const b = e.target.closest('.t'); if (!b) return;
  priBtns.forEach(t => {{
    const on = t === b;
    t.classList.toggle('on', on); t.setAttribute('aria-pressed', on);
  }});
  kind = b.dataset.f;
  sub = '';                                         // 대분류를 바꾸면 세부는 초기화
  subBtns.forEach(x => {{
    const on = !x.dataset.s;                        // '전체' 칩이 켜진 상태로 돌아간다
    x.classList.toggle('on', on); x.setAttribute('aria-pressed', on);
  }});
  syncSub(); apply();
}});

subnav.addEventListener('click', e => {{
  const b = e.target.closest('.t.s'); if (!b) return;
  // '전체' 는 해제 토글이 아니다 — 누르면 늘 '세부 없음' 으로 간다.
  const off = b.dataset.s && b.classList.contains('on');
  subBtns.forEach(x => {{
    const on = !off && x === b;
    x.classList.toggle('on', on); x.setAttribute('aria-pressed', on);
  }});
  sub = off ? '' : b.dataset.s;
  apply();
}});

// ── 검색 추천 ────────────────────────────────────────────────────
// 낱말 목록을 따로 내려받지 않는다. 브랜드·분류·상품명이 이미 카드 안에
// 다 있어서 DOM 에서 긁는다. 추천 때문에 늘어나는 바이트가 0 이다.
//
// 한국어는 띄어쓰기가 없어서 앞글자 일치로는 거의 안 걸린다('우동'으로
// '얼큰우동'을 못 찾는다). 부분일치로 본다. 대신 앞에서 걸린 것을 위로
// 올린다 — '라떼'를 치면 '라떼'로 시작하는 것이 먼저다.
const sug = document.getElementById('sug');
const VOCAB = (() => {{
  const brands = new Map(), subs = new Map(), names = new Set();
  for (const c of cards) {{
    const b = c.dataset.b, k = c.dataset.s;
    if (b) brands.set(b, (brands.get(b) || 0) + 1);
    if (k) subs.set(k, (subs.get(k) || 0) + 1);
    const h = c.querySelector('h2');
    if (h) names.add(h.textContent.trim());
  }}
  const out = [];
  for (const [t, n] of subs) out.push({{t: t, n: n, kind: '분류', rank: 0}});
  for (const [t, n] of brands) out.push({{t: t, n: n, kind: '업체', rank: 1}});
  for (const t of names) out.push({{t: t, n: 0, kind: '', rank: 2}});
  return out;
}})();

let sugItems = [], sugAt = -1;
const ESC = ch => ({{'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}}[ch]);

function closeSug() {{
  sug.hidden = true; sug.innerHTML = ''; sugItems = []; sugAt = -1;
  q.setAttribute('aria-expanded', 'false');
}}

function showSug() {{
  // 마지막 낱말만 본다. '커피 라'까지 쳤으면 '라'로 고른다.
  const typed = q.value.toLowerCase();
  const head = typed.replace(/[^ ]*$/, '');
  const tail = typed.slice(head.length).trim();
  if (!tail) return closeSug();
  const hit = [];
  for (const v of VOCAB) {{
    const at = v.t.toLowerCase().indexOf(tail);
    if (at < 0) continue;
    if (v.t.toLowerCase() === typed.trim()) continue;   // 이미 다 친 것
    hit.push({{v: v, at: at}});
  }}
  // 분류·업체 먼저, 그 다음 앞에서 걸린 것, 그 다음 건수 많은 것.
  hit.sort((a, b) => a.v.rank - b.v.rank || a.at - b.at || b.v.n - a.v.n);
  sugItems = hit.slice(0, 8).map(h => ({{text: head + h.v.t, label: h.v.t,
                                        kind: h.v.kind, n: h.v.n}}));
  if (!sugItems.length) return closeSug();
  sug.innerHTML = sugItems.map((it, i) =>
    '<li role="option" aria-selected="false" data-i="' + i + '">' +
    (it.kind ? '<span class="k">' + it.kind + ' ' + it.n + '건</span>' : '') +
    it.label.replace(/[&<>"]/g, ESC) + '</li>').join('');
  sug.hidden = false; sugAt = -1;
  q.setAttribute('aria-expanded', 'true');
}}

function markSug() {{
  const lis = sug.children;
  for (let i = 0; i < lis.length; i++)
    lis[i].setAttribute('aria-selected', i === sugAt ? 'true' : 'false');
  if (sugAt >= 0) lis[sugAt].scrollIntoView({{block: 'nearest'}});
}}

function takeSug(i) {{
  if (!sugItems[i]) return;
  q.value = sugItems[i].text;
  closeSug();
  words = q.value.trim().toLowerCase().split(' ').filter(Boolean);
  apply();
  q.focus();
}}

// click 이 아니라 mousedown 이다 — click 은 blur 뒤에 와서 목록이 이미 닫혀 있다.
sug.addEventListener('mousedown', e => {{
  const li = e.target.closest('li');
  if (li) {{ e.preventDefault(); takeSug(+li.dataset.i); }}
}});
q.addEventListener('blur', () => setTimeout(closeSug, 120));
q.addEventListener('focus', showSug);
q.addEventListener('keydown', e => {{
  if (sug.hidden) return;
  if (e.key === 'ArrowDown') {{
    e.preventDefault();
    sugAt = sugAt + 1 >= sugItems.length ? -1 : sugAt + 1;
    markSug();
  }} else if (e.key === 'ArrowUp') {{
    e.preventDefault();
    sugAt = sugAt - 1 < -1 ? sugItems.length - 1 : sugAt - 1;
    markSug();
  }} else if (e.key === 'Enter' && sugAt >= 0) {{
    e.preventDefault(); takeSug(sugAt);
  }} else if (e.key === 'Escape') {{
    closeSug();
  }}
}});

let timer;
q.addEventListener('input', () => {{
  showSug();
  clearTimeout(timer);
  timer = setTimeout(() => {{
    words = q.value.trim().toLowerCase().split(/\\s+/).filter(Boolean);
    apply();
  }}, 150);
}});

sortBtn.addEventListener('click', () => {{
  const byDate = sortBtn.dataset.s === 'date';
  sortBtn.dataset.s = byDate ? 'brand' : 'date';
  sortBtn.textContent = byDate ? '브랜드순' : '최신순';
  [...cards].sort((a, b) => byDate
    ? (a.dataset.b.localeCompare(b.dataset.b, 'ko') || a.dataset.i - b.dataset.i)
    : (a.dataset.i - b.dataset.i)).forEach(c => g.appendChild(c));
}});

syncSub();
</script>
</body></html>"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc, encoding="utf-8")
    print(f"→ {OUT.relative_to(ROOT)} ({len(doc)//1024}KB)")


