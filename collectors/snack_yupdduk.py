"""동대문엽기떡볶이(엽떡).

`CANDIDATES-KOREAN.md` 가 **"robots 가 우리를 명시적으로 막는다. 순위 문제가 아니라
붙이면 안 된다"** 로 접은 곳이다(`User-agent: * / Disallow: /`, Yeti·Googlebot 만 허용).
**2026-10-02 운영자가 robots 무시를 승인**해서 다시 연다. 2026-10-08 실측.

## 🔴 메뉴판은 쓰지 않는다

`/sub/menu/yup-menu` 한 장에 전 메뉴 **약 60건**이 SSR 로 들어 있다(엽기메뉴 14,000원 /
로제메뉴 16,000원 / 숯불통뼈닭발 15,000원 / 떡추가 1,000원 …). 받기는 제일 쉽다.
**그런데 NEW 배지도 날짜도 하나도 없다.** 그대로 올리면 60건이 전부 신상이 된다 —
이 레포에서 제일 나쁜 결함이다. **손대지 않는다.**

공지사항(`/sub/cs-info/yup-notice`, 105건)도 아니다. 최신 5건이 `추석 연휴 고객센터
휴무`·`CJ ONE 포인트 적립률 변경`·`개인정보처리방침 일부 변경` 처럼 전부 사무 공지다.

## 쓰는 경로 — 이벤트&안내 게시판의 JSON

`/sub/event/yup-event` 의 목록은 jQuery 가 POST 로 받아 그린다.

  POST https://www.yupdduk.com/json/event/j_event
       ftype=list_adm & page=N & rows=10 & opt_ev= & sc_type= & sc_value=
       & opt_s=2 & Isnotice=1 & Ordtype=2

총 **305건**이고 `Ordtype=2` 는 고정글(`Listtop`)을 위로 올린다. 신제품 공지는
`Listtop=99` 로 고정돼 올라오므로 앞 2페이지(20건)면 닿는다.

⚠️ **응답이 무겁다.** 행마다 상세 본문 HTML(`Remark`)이 통째로 들어 있어 한 페이지가
25KB~2.3MB 다. `rows` 를 키우면 수십 MB 가 된다. **10건씩 2페이지만 받는다.**

## 🔴 서버 검색은 쓰지 않는다 — 그리고 그쪽 오류 문구를 우리 로그에 남기지 않는다

`sc_type`/`sc_value` 에 임의 값을 넣으면 응답이 `{"result":"no","errtxt":"…"}` 로
**저쪽 DB 오류 문구를 그대로 돌려준다.** 주입 가능성이 보이는 자리라 **더 찔러보지
않았고, 앞으로도 안 찌른다.** 확인에 쓴 값이 무엇이었는지도 여기 적지 않는다.

지키는 방법은 둘이다.
  ① `_PARAMS` 를 상수로 못박고 `sc_value` 가 비었는지 매번 확인한다. 나중에 누가
     "검색으로 걸러오면 편하겠다" 며 채워 넣는 걸 코드가 막는다.
  ② 실패해도 **`errtxt` 를 로그에 찍지 않는다.** 이 레포의 수집 로그는 공개
     저장소의 Actions 로그다. 그대로 올리면 남의 DB 내부 사정을 우리가 퍼뜨리는
     꼴이 된다. 우리가 알 건 '검색이 아닌 목록 호출이 실패했다' 까지다.

목록 호출(`sc_value` 빈 값)은 정상적으로 `result:"ok"` 를 준다. 우리가 쓰는 건 그것뿐이다.

## 🔴 제목 거르기 — 여기가 이 어댑터의 전부다

게시판은 이름이 '이벤트&안내'인 만큼 **대부분 행사·제휴·모집**이다. 2026-01 ~ 2025-01
구간 **80건을 눈으로 읽고** 추린 결과, 엽떡 **자사 신메뉴** 글은 셋뿐이다.

```
2026-09-11  신메뉴 더착한맛 출시 안내                       ✔
2025-09-09  오리지널(저당)&착한맛(저당) 출시 안내             ✔
2025-06-30  신메뉴 양배추 토핑&대파 토핑 출시 안내            ✔
```
연 2건꼴이다. **0건인 날이 정상이라 `ALLOW_EMPTY = True`** 다
(`china_hongjjajang`·`dessert_yoajung`·`maker_lavelee` 선례).

**반드시 걸러야 하는 것 — 남의 회사 제품이다.** 엽떡은 콜라보를 자주 하는데 그 글의
상품 주인은 엽떡이 아니고, 이 레포가 **이미 그 제조사 어댑터로 수집하고 있다.**

```
2026-08-10  [롯데웰푸드X엽떡] 짱매워요 젤리 출시 이벤트   → maker_lottewellfood
2026-06-22  [농심 X 엽기떡볶이] 포테토칩 엽떡로제맛 출시   → maker_nongshim
2025-08-18  하림 X 동대문엽기떡볶이 맛닭가슴살 출시        → maker_harim
2025-11-30  [필리밀리X엽떡] 어워즈 기획 2종 출시 안내      → 굿즈(비식품)
```

80건을 다 통과시켜 본 규칙은 이렇다.
  ① `출시` 가 있어야 한다.
  ② `[` 로 시작하는 말머리가 있으면 버린다 — 콜라보·이벤트·안내가 전부 여기 걸린다.
  ③ ` X ` / ` x ` / `×` 가 있으면 버린다(대괄호 없는 콜라보. `하림 X 동대문…`).
  ④ `_SKIP` 단어(이벤트·모집·수상·제휴·챌린지·단종·리뉴얼 …)가 있으면 버린다.
     `단종`·`리뉴얼` 도 여기 넣는다 — `[안내] 엽기오돌뼈 메뉴 단종`,
     `[안내] 닭발 메뉴 리뉴얼` 은 신제품이 아니다.

**이름은 `&` 로 쪼갠다.** 셋 중 둘이 2종 묶음 공지라 쪼개야 상품이 된다
(`오리지널(저당)&착한맛(저당)` → 2건, `양배추 토핑&대파 토핑` → 2건). 요아정은
`N종` 을 통째로 버렸는데 여기는 제목에 이름이 그대로 나열돼 있어서 쪼개는 쪽이 맞다.

⚠️ `더착한맛` 은 엄밀히 **맵기 단계**지 접시가 아니다. 그래도 브랜드가 '신메뉴'로
공지한 것이라 그대로 내보낸다. 사람이 보고 걸러야 할 성질의 건이다.

## 날짜

  Sdate     노출 시작일(`20260911`) → `uploaded_at`. 전건에 있다
  Regdate   등록일(`20260909`). Sdate 가 없을 때 폴백
  본문      `[출시 일자] 2026.09.16.(수)` ← **브랜드가 '출시일'이라고 말한 값**이라
            읽히면 `released_at` 에 넣는다. 표본이 1건뿐이라 못 읽으면 조용히 비우고
            `uploaded_at` 에 맡긴다.

이미지는 `Filename`(`/bod/config/event/750x750_7.png`) 포스터다.
상세 주소는 `/sub/event/yup-event-detail?eventno=<Eventno>` 다(`goevent()` 가 만드는 꼴).

등록 제안: 유형 `FRANCHISE`, 세부분류 `분식`.
"""
import re
import time

from . import base
from .base import Item

BRAND = "엽기떡볶이"
SITE = "https://www.yupdduk.com"
LIST = SITE + "/json/event/j_event"
VIEW = SITE + "/sub/event/yup-event-detail?eventno={}"
DELAY = 1.8
PAGES = 2     # 고정글이 위로 올라오므로 20건이면 닿는다. 응답이 무거워 더 늘리지 않는다
ROWS = 10

# 신제품 공지가 연 2건꼴이라 **0건인 날이 정상**이다. collect 의 0건 가드를 끈다.
ALLOW_EMPTY = True

# 목록 호출에 쓰는 값. **이대로 고정이다.**
# `sc_type`/`sc_value` 는 절대 채우지 않는다 — 윗글 '서버 검색은 쓰지 않는다' 참고.
# 여기를 채우면 저쪽 DB 오류를 끌어내게 되고, 그건 우리가 할 일이 아니다.
_PARAMS = {"ftype": "list_adm", "rows": ROWS, "opt_ev": "",
           "sc_type": "", "sc_value": "", "opt_s": "2",
           "Isnotice": 1, "Ordtype": 2}

# ① 출시를 말해야 한다
_LAUNCH = re.compile(r"출시")
# ③ 대괄호 없는 콜라보. `하림 X 동대문엽기떡볶이 맛닭가슴살 출시`
_COLLAB = re.compile(r"(^|\s)[Xx×](\s|$)")
# ⑤ 꼬리말
_TAIL = re.compile(r"\s*출시\s*(안내|소식)?\s*$")
# 머리말 `신메뉴 ` / `신제품 `
_HEAD = re.compile(r"^\s*(신메뉴|신제품|NEW)\s+", re.I)
# 본문의 `[출시 일자] 2026.09.16.(수)` — 브랜드가 직접 말한 출시일
_RELEASED = re.compile(r"출시\s*일자[^\d]{0,8}(\d{4})[.\-/\s]+(\d{1,2})[.\-/\s]+(\d{1,2})")

# ④ 상품 글이 아닌 것들. 2026-01~2025-01 80건을 읽고 추렸다.
_SKIP = ("이벤트", "모집", "수상", "캠페인", "챌린지", "제휴", "인증", "응원",
         "투표", "후원", "굿즈", "쿠폰", "할인", "증정", "상품권", "멤버십",
         "단종", "리뉴얼", "휴무", "변경", "안내방송", "채용", "가맹", "창업",
         "티징", "SNS", "라이브", "팝업", "성료", "돌파")


def _pick(title: str) -> list:
    """제목 → 상품명 목록. 걸러지면 빈 목록.

    80건 실측으로 맞춘 규칙이다 — 모듈 주석의 ①~④ 를 그대로 옮겼다.
    """
    t = " ".join((title or "").split())
    if not t or not _LAUNCH.search(t):
        return []
    if "[" in t or _COLLAB.search(t):      # 콜라보·말머리는 전부 남의 건이다
        return []
    if any(w in t for w in _SKIP):
        return []
    body = _HEAD.sub("", _TAIL.sub("", t)).strip()
    if not body:
        return []
    out = []
    for part in body.split("&"):
        name = part.strip(" ,·∙")
        if len(name) >= 2 and name not in out:
            out.append(name)
    return out


def _date(v: str) -> str:
    """`20260911` → `2026-09-11`."""
    v = (v or "").strip()
    if len(v) != 8 or not v.isdigit():
        return ""
    return f"{v[:4]}-{v[4:6]}-{v[6:]}"


def _released_at(remark: str) -> str:
    m = _RELEASED.search(re.sub(r"<[^>]+>", " ", remark or ""))
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    rows_seen = 0

    with base.client(headers={"Referer": SITE + "/sub/event/yup-event",
                              "X-Requested-With": "XMLHttpRequest"}) as c:
        for page in range(1, PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            if _PARAMS["sc_type"] or _PARAMS["sc_value"]:
                raise RuntimeError(
                    "서버 검색 파라미터가 채워져 있다. 이 게시판은 임의 검색어에 "
                    "DB 오류를 그대로 돌려주는 자리라 목록만 받기로 한 곳이다 "
                    "— 모듈 주석 '서버 검색은 쓰지 않는다' 참고")
            r = base.retry(lambda page=page: c.post(LIST,
                                                    data=_PARAMS | {"page": page}))
            r.raise_for_status()
            body = r.json()
            if body.get("result") != "ok":
                # ⚠️ `errtxt` 를 찍지 않는다. 저쪽 DB 오류 문구가 그대로 담겨
                #    오는데, 우리 수집 로그는 공개 저장소의 Actions 로그다.
                #    우리가 알 건 '목록 호출이 실패했다' 까지다.
                raise RuntimeError(
                    f"{LIST} page={page}: result={body.get('result')} — "
                    f"목록 호출이 거절됐다(응답 본문은 일부러 안 찍는다)")

            rows = body.get("rows") or []
            rows_seen += len(rows)
            for row in rows:
                e = (row or {}).get("EVT") or {}
                title = " ".join((e.get("Eventname") or "").split())
                img = (e.get("Filename") or "").strip()
                uploaded = _date(e.get("Sdate")) or _date(e.get("Regdate"))
                released = _released_at(e.get("Remark"))
                for name in _pick(title):
                    it = Item(
                        brand=BRAND,
                        name=name,
                        desc=title,
                        image=SITE + img if img.startswith("/") else img,
                        # 브랜드가 본문에 '[출시 일자]' 로 못박은 값만 released_at.
                        # 그 외엔 게시글 노출 시작일이라 uploaded_at 이다.
                        released_at=released,
                        uploaded_at=uploaded,
                        is_new=True,
                        url=VIEW.format(e.get("Eventno") or ""),
                    )
                    if it.key not in seen:
                        seen.add(it.key)
                        items.append(it)

    # 목록 자체가 비면 게시판 API 가 바뀐 것이다. 상품 0건과는 다른 얘기다.
    if rows_seen < ROWS:
        raise RuntimeError(
            f"{LIST}: {PAGES}페이지에서 {rows_seen}행밖에 못 읽었다 — 2026-10-08 "
            f"실측은 페이지당 10행(전체 305건)이었다. ftype/Ordtype 파라미터가 "
            f"바뀌었는지 확인하라")
    return items
