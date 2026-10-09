#!/usr/bin/env python3
"""실패 원인 찍기 — 수집이 깨졌을 때 **왜** 깨졌는지 이름을 붙인다.

예외 문자열만 보고는 구분이 안 된다. `ConnectError` 한 줄이 도메인이 사라진
것일 수도, 해외 IP 라 막힌 것일 수도, 중간 인증서가 빠진 것일 수도 있다.
셋은 대응이 전혀 다르다 — 각각 주소를 고치고, 한국 IP 를 구하고, certs/ 에
인증서를 넣는다. 그런데 로그에는 똑같이 보였다.

그래서 실패하면 **한 번 더 찔러보고** 원인을 찍는다. 그리고 수집 전에 미리
훑어보는 `--doctor` 를 둔다. 터지고 나서 아는 것보다 전날 아는 게 낫다.
"""
import socket
import time
import urllib.parse

from collectors import base

# 원인 코드. 로그에서 눈으로 세기 쉽게 짧게 둔다.
DNS = "DNS"          # 도메인이 안 풀린다 — 주소가 틀렸거나 사라졌다
TLS = "TLS"          # 인증서 체인이 끊겼다 — certs/ 에 중간 인증서를 더하면 된다
GEO = "해외차단"      # 저쪽이 우리 IP 를 거절한다. 러너가 해외라 그렇다
BOT = "차단"          # 한국 IP 인데도 거절 — 봇 탐지
DOWN = "서버오류"     # 저쪽 5xx. 우리 쪽 문제가 아니고 기다리면 낫는다
MUTE = "무응답"       # 연결은 시도되는데 답이 없다
OPEN = "열림"         # 사이트는 열린다 → 어댑터·파서 문제다

# 이만큼 작은 200 은 차단 안내로 본다. 러너에서 막힌 곳들이 763~1610B 였고
# 실제로 열리는 곳은 30KB 부터였다. 근거는 아래 cause() 주석.
SMALL_BYTES = 2000

# 우리가 고칠 수 있는 것. 이것만 수집을 빨갛게 만든다.
OURS = (TLS, OPEN)

_egress = None


def egress() -> str:
    """지금 나가는 IP 가 어느 나라인가. 'KR' 또는 'US' 같은 두 글자.

    403 하나로는 '해외라 막혔다' 와 '봇이라 막혔다' 를 못 가른다. 나라를
    알면 갈라진다. 러너는 Azure 해외(172.184.219.166)고 이 맥은 한국이라
    같은 코드가 두 곳에서 다른 답을 낸다 — 그게 맞는 동작이다.

    ⚠️ ipapi.co 는 쓰지 마라. 한도를 넘기면 200 에 JSON 에러 본문을 주는데
    앞 두 글자를 떼면 `{'` 가 나온다. Cloudflare trace 는 평문이라 안전하다.
    """
    global _egress
    if _egress is None:
        _egress = "??"
        try:
            with base.client(timeout=8) as c:
                for line in c.get("https://cloudflare.com/cdn-cgi/trace").text.splitlines():
                    if line.startswith("loc="):
                        _egress = line[4:].strip()
        except Exception:
            pass
    return _egress


def cause(url: str) -> tuple:
    """주소 하나를 찔러보고 (원인코드, 한 줄 설명) 을 돌려준다.

    ⚠️ `열림` 은 '수집이 된다' 는 뜻이 **아니다.** 이 레포에서 200 에 속은
    적이 여러 번이다 — 탕화쿵푸는 트래픽 차단 안내를 200 으로 주고, 모리샤브는
    없는 경로와 바이트까지 같은 soft-404 를 준다. 여기서 `열림` 은 딱
    '못 닿은 건 아니다' 까지다. 그 다음은 어댑터가 할 말이다.
    """
    import httpx
    u = urllib.parse.urlparse(url)
    host = u.hostname or ""
    # ⚠️ 스킴을 봐야 한다. 처음엔 무조건 443 으로 찔렀는데, http 로만 서비스하는
    # 빨라쪼가 '인증서 이름 불일치' 로 찍혔다. 쓰지도 않는 포트를 깐 것이다.
    tls = u.scheme != "http"
    port = u.port or (443 if tls else 80)

    # ① 이름부터. 여기서 걸리면 아래는 볼 것도 없다.
    #    한 번은 봐준다 — HTTP 쪽은 재시도하는데 여기만 단판이라, 노랑통닭이
    #    한 번 못 풀린 걸로 `DNS 없음` 에 올랐다. dig 로 다시 보니 멀쩡했다.
    #    진짜로 사라진 도메인과 잠깐 못 푼 것은 다르게 다뤄야 한다.
    for attempt in (0, 1):
        try:
            socket.getaddrinfo(host, port)
            break
        except socket.gaierror as e:
            if attempt:
                return DNS, f"{host} 가 두 번 다 안 풀린다 ({e.strerror or e})"
            time.sleep(1.5)

    # ② 실제로 받아 본다. **어댑터와 똑같은 경로**(base.client — 프록시·UA·
    #    재시도 포함)로 간다. 전엔 소켓으로 직접 악수해 보고 인증서 메시지를
    #    더 곱게 뽑았는데, 농심이 거기서만 SSLV3_ALERT_HANDSHAKE_FAILURE 로
    #    찍히고 httpx 로는 200 600KB 가 왔다. 점검이 수집과 다른 문을 두드리면
    #    그건 진단이 아니라 또 하나의 오보다.
    try:
        with base.client(timeout=httpx.Timeout(12.0, connect=8.0)) as c:
            try:
                r = c.get(url)
            except httpx.TransportError:
                # 한 번은 봐준다. 부어치킨이 `Connection reset by peer` 로
                # 찍혔는데 어댑터는 57건을 받아왔다 — base.client 가 세 번
                # 다시 거는 걸 점검만 안 하고 있었다.
                #
                # 쉬었다 건다. 점검은 여러 주소를 동시에 두드리는데, 작은
                # 서버는 그걸 못 견디고 끊는다. 유가네가 그랬다 — 혼자
                # 네 번 찌르면 네 번 다 200 인데 동시 점검에서만 끊겼다.
                # 바로 다시 걸면 같은 이유로 또 끊긴다.
                time.sleep(1.5)
                r = c.get(url)
    except (httpx.ConnectTimeout, httpx.ReadTimeout):
        loc = egress()
        if loc not in ("KR", "??"):
            return GEO, f"응답이 없다 — egress 가 {loc} 라 막힌 것으로 본다"
        return MUTE, "연결은 되는데 답이 없다"
    except httpx.ConnectError as e:
        msg = str(e)
        if "SSL" in msg or "certificate" in msg:
            return TLS, msg.strip("[]")
        if "not known" in msg or "Name or service" in msg:
            return DNS, f"{host} 가 안 풀린다"
        loc = egress()
        if loc not in ("KR", "??"):
            return GEO, f"연결이 안 된다 — egress 가 {loc} 다 ({msg})"
        return MUTE, msg
    except httpx.TransportError as e:
        return MUTE, f"{type(e).__name__}: {e}"

    if r.status_code in (403, 429):
        loc = egress()
        if loc == "KR":
            return BOT, f"{r.status_code} — 한국 IP 인데도 거절한다(봇 탐지)"
        return GEO, f"{r.status_code} — egress 가 {loc} 다. 한국 IP 면 열린다"
    if r.status_code >= 500:
        return DOWN, f"{r.status_code} — 저쪽 장애"
    if r.status_code >= 400:
        return OPEN, f"{r.status_code} — 주소가 바뀐 듯하다"

    # 🔴 200 이라고 열린 게 아니다. 2026-10-09 러너 로그에서 처음 드러났다 —
    # 열두 곳이 `[열림]` 으로 찍혀 **우리 잘못으로 분류됐는데**, 본문이
    # 763·775·783·785·786·794B 와 1598·1600·1610B 였다. 같은 크기가 반복되는
    # 건 차단 안내 두 종류를 돌려주고 있다는 뜻이고, 실제로 열리는 곳들은
    # 30KB·79KB·145KB 였다. 해외 IP 를 200 으로 막은 것이다.
    #
    # 이 레포가 여러 번 당한 '200 ≠ 성공' 의 또 다른 얼굴이다(탕화쿵푸 차단
    # 안내 200, 모리샤브 soft-404, 삼다수 87B meta refresh, 머거본 240B alert).
    # 해외에서 몸통이 이만큼 작으면 차단으로 본다. 한국에서 작으면 그건
    # 주소가 틀린 쪽이라 그대로 우리 몫으로 둔다.
    if len(r.content) < SMALL_BYTES:
        loc = egress()
        if loc not in ("KR", "??"):
            return GEO, (f"{r.status_code} 인데 본문이 {len(r.content)}B뿐이다 — "
                         f"egress 가 {loc} 다. 차단 안내로 본다")
        return OPEN, (f"{r.status_code} {len(r.content)}B — 너무 작다. "
                      f"빈 셸이거나 주소가 틀렸을 수 있다")
    return OPEN, f"{r.status_code} {len(r.content)}B — 사이트는 열린다"


def of(brands: list, exc: Exception) -> tuple:
    """어댑터가 터졌을 때 쓰는 입구. 주소를 못 찾으면 예외를 그대로 넘긴다."""
    url = ""
    for b in brands:
        url = base.SITES.get(b) or ""
        if url:
            break
    if not url:
        return ("", f"{type(exc).__name__}: {exc}")
    try:
        return cause(url)
    except Exception as e:                  # 진단이 수집을 죽이면 본말전도다
        return ("", f"진단 실패 — {type(e).__name__}: {e}")


def endpoints(mod) -> list:
    """어댑터가 **실제로 긁는** 주소들. 호스트마다 하나씩.

    처음엔 `base.SITES` 만 찔렀는데, 그건 카드에 붙는 **사람용 링크**지
    수집 경로가 아니다. 여섯 곳이 빨갛게 찍혔는데 전부 헛것이었다 —
    투썸은 `mo.twosome.co.kr` API 로 받고 SITES 의 `m.` 은 403 이고,
    엔제리너스는 롯데잇츠로 옮겨갔는데 SITES 에 옛 주소가 남아 있었다.

    그래도 SITES 쪽은 따로 봐야 한다. 거기가 죽으면 **우리 사이트의 링크가
    죽는다.** 수집과 링크는 다른 문제라 따로 센다.

    소스의 문자열에서 주소를 줍는다. 이미지 호스트는 뺀다 — 거긴 열려 있어도
    수집과 상관없고, 막혀 있어도 미러가 받아준다.
    """
    import inspect
    import re
    try:
        src = inspect.getsource(mod)
    except Exception:
        return []
    seen, out = {}, []
    for m in re.finditer(r"https?://[^\s\"'`]+", src):
        url = m.group(0).rstrip(".,)`")
        # f-string 자리표시자가 섞인 주소는 그대로 못 찌른다. `{page}` 가
        # 들어간 목록 주소가 그렇고, `[` 가 들어가면 urlparse 가 IPv6 로 보고
        # 통째로 터진다 — 진단이 수집을 죽이면 본말전도다.
        # f-string 자리표시자는 그대로 못 찌른다. 앞부분만 잘라 쓴다 —
        # `.../menu.html?depth1={i}` → `.../menu.html`. 통째로 버렸더니
        # 유가네처럼 **도메인 루트만 남는** 어댑터가 생겼고, 그 루트가
        # 간헐적으로 끊기는 바람에 멀쩡한 어댑터가 빨갛게 찍혔다.
        if "{" in url:
            url = url.split("{", 1)[0].split("?", 1)[0].rstrip("&/")
        if any(ch in url for ch in "}[]%") or url.count("/") < 3:
            continue
        try:
            host = urllib.parse.urlparse(url).hostname or ""
        except ValueError:
            continue
        if not host or host.startswith("image.") or host.startswith("img"):
            continue
        # robots.txt 는 **수집 주소가 아니다.** 어댑터 주석이 "robots 를 이렇게
        # 확인했다" 며 적어 두는 자리라 소스에 흔한데, 경로가 길어서 호스트
        # 대표로 뽑히기 쉽다. 그게 막혀도 수집과는 상관없다.
        if url.endswith("/robots.txt"):
            continue
        # 같은 호스트면 **경로가 긴 쪽**을 쓴다. 루트는 열려 있는데 정작
        # 쓰는 경로가 404 인 경우가 이 레포에 여럿 있었다(BBQ /menu 등).
        if len(url) > len(seen.get(host, "")):
            seen[host] = url
    for host in sorted(seen):
        out.append(seen[host])
    return out[:3]


def tls_handled(mod) -> bool:
    """이 어댑터가 TLS 를 이미 따로 다루는가.

    점검이 `TLS` 라고 찍는 곳 중 상당수는 **이미 고쳐둔 곳**이다. 에그드랍·
    퀴즈노스·벤슨처럼 certs/ 에 중간 인증서를 더해 놓았거나, 또래오래·
    노랑통닭처럼 옛 암호 설정에 맞춰 전송을 따로 잡아둔 곳들이다. 기본
    신뢰 저장소로 찌르는 점검은 그 사정을 모르고 똑같이 빨갛게 찍는다.

    그걸 섞어두면 경고가 무뎌져서 **진짜 새로 끊긴 곳을 못 본다.** 이 레포가
    같은 실수를 한 적이 있다 — 일부러 내려둔 어댑터와 배선이 빠진 어댑터를
    한 줄에 섞어 찍다가 SPC삼립이 죽은 채로 방치됐다.

    모듈 소스에 TLS 를 건드리는 흔적이 있는지로 본다. 정확한 판정은 아니고
    '이 파일은 이미 알고 있다' 는 표시다.
    """
    import inspect
    try:
        src = inspect.getsource(mod)
    except Exception:
        return False
    return any(k in src for k in ("certs/", "CA_EXTRA", "ssl.create_default_context",
                                  "set_ciphers", "verify="))


def sweep(urls: dict, workers: int = 8) -> list:
    """{이름: 주소} 를 한꺼번에 훑는다. [(이름, 코드, 설명)] 을 돌려준다.

    🔴 **막힌 것은 한꺼번에 두드리기를 끝낸 뒤 혼자 다시 본다.**

    동시에 찌르는 것 자체가 오보를 만든다. 이 레포에서 두 번 겪었다 —
    유가네는 서버가 동시 접속을 못 견디고 끊었고(혼자 네 번 찌르면 네 번 다
    200), 노랑통닭은 **맥의 리졸버가 몰린 질의에서 이름을 못 풀었다**(혼자
    풀면 세 번 다 풀리고 어댑터는 47건을 받아온다).

    둘 다 `cause()` 안에서 한 번 더 걸어 봤지만 소용없었다. 재시도가 **같은
    burst 안**에 있으면 같은 이유로 또 막힌다. 그래서 실패만 모아 스레드를
    다 거둔 뒤에 순차로 다시 본다. 실패는 원래 몇 건 안 되니 비싸지 않고,
    여기서 살아나면 그건 우리 탐침이 만든 오보였다는 뜻이다.
    """
    import concurrent.futures as cf
    out = {}
    with cf.ThreadPoolExecutor(workers) as pool:
        jobs = {pool.submit(cause, u): n for n, u in urls.items()}
        for j in cf.as_completed(jobs):
            name = jobs[j]
            try:
                out[name] = j.result()
            except Exception as e:
                out[name] = ("", f"{type(e).__name__}: {e}")

    for name, (code, why) in list(out.items()):
        if code in ("", OPEN):
            continue
        time.sleep(0.3)
        try:
            out[name] = cause(urls[name])
        except Exception:
            pass
    return sorted((n, c, w) for n, (c, w) in out.items())
