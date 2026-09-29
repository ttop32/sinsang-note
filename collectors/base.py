from dataclasses import dataclass, asdict, field
import re

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
