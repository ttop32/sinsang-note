"""롯데리아 — 수집 불가. ADAPTERS 에 등록하지 마라.

fetch() 는 일부러 예외를 던진다. 공개 웹에서 긁을 수 있는 소스가 없는데 빈 리스트나
반쪽짜리 데이터를 돌려주면 '수집은 되는데 신제품이 안 잡힌다'로 오해되기 때문이다.

2026-09-30 실측:
  - 롯데리아 단독 도메인은 없다. lotteria.co.kr / lotteria.com / www.lotteria.co.kr
    전부 DNS 가 안 풀린다. 브랜드 페이지는 롯데GRS 통합몰 www.lotteeatz.com 안에 있다.
  - www.lotteeatz.com/robots.txt 는 UA 를 6개 티어로 나눠 허용하고, 목록에 없는
    UA 는 마지막 블록에서 통째로 막는다.
        # 기타/미지의 봇 (안전장치)
        User-agent: *
        Disallow: /
    우리 UA(sinsang-note/1.0)는 어느 티어에도 없으니 전 경로가 금지다. 브랜드
    페이지(/brand/)도 상품(/products/)도 예외가 아니다.
  - 운영사 홈페이지 www.lottegrs.com 도 robots.txt 가 `User-agent: * / Disallow: /`
    하나뿐이다. 보도자료로 우회하는 길도 막혀 있다.
  - api.lotteeatz.com 은 DNS 가 풀리지만(내부 NLB) www 는 Imperva WAF 뒤에 있다.
    robots.txt 로 명시적으로 거절한 상대를 다른 호스트로 돌아서 긁는 건
    이 프로젝트가 UA 에 신원과 연락처를 박아 둔 이유와 정면으로 어긋난다. 안 한다.

즉 '신제품 신호가 없다'가 아니라 '접근 자체가 거절돼 있다'가 맞다.
길이 하나 있다면 사람이 롯데GRS 에 연락해 우리 UA 를 robots.txt 허용 티어에
넣어 달라고 요청하는 것뿐이고, 그건 코드로 풀 문제가 아니다.
"""
from .base import Item

BRAND = "롯데리아"
SITE = "https://www.lotteeatz.com"


def fetch() -> list[Item]:
    raise RuntimeError(
        f"{BRAND}: {SITE}/robots.txt 가 'User-agent: * / Disallow: /' 로 우리 UA 를 "
        "전 경로 차단한다(운영사 www.lottegrs.com 도 동일). 공개 대체 소스 없음. "
        "ADAPTERS 에 등록하지 말 것."
    )
