from dataclasses import dataclass, asdict, field
import re
import time

import httpx

# 공개 봇이니 신원을 밝힌다. 브라우저를 위장하면 사이트 운영자가 우리를 식별하거나
# 연락하거나 선별 차단할 방법이 없다. robots.txt 의 UA별 규칙에도 매칭되지 않는다.
UA = "sinsang-note/1.0 (+https://github.com/ttop32/sinsang-note)"


@dataclass
class Item:
    """브랜드 어댑터가 공통으로 뱉는 상품 1건."""
    brand: str
    name: str
    name_en: str = ""
    desc: str = ""
    image: str = ""
    labels: list = field(default_factory=list)   # ICE / HOT 등
    category: str = ""
    uploaded_at: str = ""                        # 브랜드가 알려주면 채움 (YYYY-MM-DD)

    @property
    def key(self) -> str:
        """중복 판정 키. 공백/괄호/용량 표기를 털어낸 상품명."""
        n = re.sub(r"\(.*?\)", "", self.name)
        n = re.sub(r"\s+", "", n)
        return f"{self.brand}:{n}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["key"] = self.key
        return d


# 해외 러너에서 국내 사이트는 간헐적으로 연결 실패·타임아웃이 난다.
# 연결 단계 재시도는 transport 가 맡고, 읽기 타임아웃은 retry() 로 감싼다.
def client(**kw) -> httpx.Client:
    # 어댑터가 Referer 같은 헤더를 더할 수 있게 UA 위에 덮어쓴다.
    headers = {"User-Agent": UA} | dict(kw.pop("headers", {}))
    kw.setdefault("timeout", httpx.Timeout(30.0, connect=15.0))
    return httpx.Client(headers=headers, follow_redirects=True,
                        transport=httpx.HTTPTransport(retries=3), **kw)


def retry(fn, tries: int = 3, delay: float = 2.0):
    """일시적 오류는 간격을 늘려가며 다시 시도한다. 끝까지 실패하면 그대로 올린다."""
    for i in range(tries):
        try:
            return fn()
        except (httpx.TransportError, httpx.HTTPStatusError):
            if i == tries - 1:
                raise
            time.sleep(delay * (i + 1))
