from dataclasses import dataclass, asdict, field
import re
import time

import httpx

# 공개 봇이니 신원을 밝힌다. 브라우저를 위장하면 사이트 운영자가 우리를 식별하거나
# 연락하거나 선별 차단할 방법이 없다. robots.txt 의 UA별 규칙에도 매칭되지 않는다.
UA = "sinsang-note/1.0 (+https://github.com/ttop32/sinsang-note)"


# 브랜드 유형. 화면에서 이 축으로 나눠 보여준다.
CVS = "편의점"
CAFE = "카페"
FRANCHISE = "프랜차이즈"

# 브랜드 → (유형, 세부분류). 어댑터가 각자 선언하면 표기가 어긋나므로 여기 한 곳에 둔다.
# 세부분류는 프랜차이즈에서만 쓴다(햄버거/피자/치킨).
BRANDS = {
    "메가MGC커피": (CAFE, ""),
    "스타벅스":    (CAFE, ""),
    "이디야커피":  (CAFE, ""),
    "설빙":        (CAFE, ""),
    "빽다방":      (CAFE, ""),
    "커피빈":      (CAFE, ""),
    "CU":         (CVS, ""),
    "세븐일레븐":  (CVS, ""),
    "맘스터치":    (FRANCHISE, "햄버거"),
    "버거킹":      (FRANCHISE, "햄버거"),
    "BBQ":        (FRANCHISE, "치킨"),
    "bhc치킨":     (FRANCHISE, "치킨"),
    "교촌치킨":    (FRANCHISE, "치킨"),
    "피자헛":      (FRANCHISE, "피자"),
    "미스터피자":  (FRANCHISE, "피자"),
    "파파존스":    (FRANCHISE, "피자"),
    "굽네치킨":    (FRANCHISE, "치킨"),
    "프랭크버거":  (FRANCHISE, "햄버거"),
    "배스킨라빈스": (FRANCHISE, "디저트"),
    "던킨":        (FRANCHISE, "디저트"),
    "이삭토스트":  (FRANCHISE, "분식"),
    # 아래는 등록하지 않는다. robots.txt 와 무관하게 이용약관이 스크래핑을 금지한다.
    # 이마트24  — 약관 제8조 ⑧ "크롤러, 매크로 프로그램, 스파이더, 스크래퍼 등… 수집" 금지
    # 도미노피자 — 푸터 "사전 서면동의 없이 정보·콘텐츠를 상업적 목적으로 스크래핑" 금지
    # 폴바셋    — 약관 "정보를 회사의 사전 승낙 없이 복제 또는 유통하거나
    #              상업적으로 이용하는 행위" 금지 (v9.0, 2026-01-22 시행)
    # 롯데리아  — robots.txt 가 알려진 봇 티어 외 모든 UA 를 Disallow: / 로 차단
    # 원래 도미노피자는 보류. robots.txt 는 /goods/ 를 허용하지만 사이트 푸터가
    # "사전 서면동의 없이 정보·콘텐츠를 상업적 목적으로 스크래핑" 을 금지한다.
    # 이마트24(약관 제8조 ⑧)와 같은 종류의 건이라 사용자 판단이 필요하다.
    # 롯데리아는 등록하지 않는다. lotteeatz.com/robots.txt 가 알려진 봇 티어 외
    # 모든 UA 를 Disallow: / 로 막는다. 우리 UA 는 어느 티어에도 없어 전 경로 금지다.
    # 다른 호스트로 우회하는 건 신원을 밝히는 이 프로젝트 방침에 어긋난다.
}


def kind(brand: str) -> tuple:
    """등록되지 않은 브랜드는 조용히 넘기지 않고 드러낸다."""
    if brand not in BRANDS:
        raise KeyError(f"BRANDS 에 없는 브랜드: {brand}")
    return BRANDS[brand]


@dataclass
class Item:
    """브랜드 어댑터가 공통으로 뱉는 상품 1건.

    이 서비스의 용건은 '신제품'이다. 전체 카탈로그가 아니다.
    어댑터는 아래 세 신호로 신제품 여부를 최대한 알려줘야 한다.
      released_at  브랜드가 출시일/등록일을 알려주면 채운다. 가장 강한 신호.
      is_new       브랜드가 NEW 배지 등으로 신제품이라 표시하면 True.
                   신제품이 아니라고 확인되면 False. 알 수 없으면 None.
      promo        1+1·2+1 같은 행사/할인 상품. 신제품이 아니므로 화면에서 뺀다.
                   세트·콤보는 여기 쓰지 마라. collect.drop_sets() 가 이름으로
                   거른다. 어댑터마다 세트 기준이 달라져 신메뉴 세트가 잘렸다.
    셋 다 비어 있으면 '어제 없던 게 오늘 있다'는 diff 로만 판정하게 되고,
    그 브랜드는 합류 첫날엔 신제품을 하나도 못 내놓는다. 그래도 그게 정직하다.
    """
    brand: str
    name: str
    name_en: str = ""
    desc: str = ""
    image: str = ""
    labels: list = field(default_factory=list)   # ICE / HOT 등
    category: str = ""
    uploaded_at: str = ""                        # 브랜드가 알려주면 채움 (YYYY-MM-DD)
    released_at: str = ""                        # 출시일/등록일. uploaded_at 보다 강한 신호
    is_new: bool | None = None                   # 브랜드가 신제품이라 표시했는가
    promo: bool = False                          # 행사/할인 상품 (신제품 아님)
    brand_type: str = ""                         # 레지스트리에서 채운다. 어댑터는 비워둔다
    brand_sub: str = ""                          # 프랜차이즈 세부분류(햄버거/피자/치킨)

    @property
    def key(self) -> str:
        """중복 판정 키. 공백/괄호/용량 표기를 털어낸 상품명."""
        n = re.sub(r"\(.*?\)", "", self.name)
        n = re.sub(r"\s+", "", n)
        return f"{self.brand}:{n}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["key"] = self.key
        d["brand_type"], d["brand_sub"] = kind(self.brand)
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
