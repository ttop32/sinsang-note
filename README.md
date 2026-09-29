# 신상노트

편의점·카페·프랜차이즈 신제품을 매일 모아 보여주는 정적 사이트.

## 구조

```
collect.py            수집 → data/products.json → docs/index.html
collectors/
  base.py             Item 데이터클래스 + 중복 판정 키
  mega.py             메가MGC커피 어댑터
data/products.json    수집 결과 (git 이력이 곧 스냅샷 아카이브)
docs/index.html       GitHub Pages 가 서빙하는 실제 페이지
```

서버도 DB도 없다. GitHub Actions 가 매일 06:00(KST) 수집해서 결과를 커밋하고,
GitHub Pages 가 `docs/` 를 그대로 서빙한다.

## 로컬 실행

```bash
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./.venv/bin/python collect.py
open docs/index.html
```

## 브랜드 추가

`collectors/` 에 모듈 하나를 만들고 `BRAND` 와 `fetch() -> list[Item]` 만 채운 뒤
`collect.py` 의 `ADAPTERS` 에 등록하면 끝이다.

조사해둔 것: 스타벅스·이디야·CU·세븐일레븐·이마트24 는 서버 렌더라 HTTP 만으로 되고,
GS25 는 JS 렌더라 별도 처리가 필요하다.

## 신제품 판정

브랜드가 "신제품"이라고 알려주길 기다리지 않는다. 전체 목록을 매일 찍어서
어제 없던 키가 오늘 있으면 신규로 본다. 키는 상품명에서 공백·괄호를 턴 값.

메가는 이미지 파일명에 업로드 시각이 박혀 있어서, 최초 수집분도 `first_seen` 을
그 날짜로 소급한다. 덕분에 첫날부터 최신순 정렬이 의미를 갖는다.

## 주의

상품 이미지는 현재 브랜드 서버를 직접 참조한다. 차단되거나 트래픽이 늘면
Cloudflare R2(무료 10GB, 송출 과금 없음)로 옮긴다.
