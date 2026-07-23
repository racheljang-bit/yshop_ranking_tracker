# yshop_ranking_tracker

Yahoo Shopping 한국 화장품(K-beauty) 카테고리 랭킹 자동 수집 도구

## 개요
Yahoo Shopping 프로모션 페이지의 카테고리랭킹 섹션(화장수, 미용액, 크림, 시트마스크, 클렌징, 자외선차단제, 베이스메이크, 아이메이크, 립)에서
인기 브랜드·상품 데이터를 자동으로 수집합니다.

## 기술 스택
- Python (requests, BeautifulSoup4)
- Yahoo Shopping 내부 API(`mc-module`) 응답 파싱

## 수집 데이터
- 상품명 / 브랜드명
- 상품 링크
- 실질가
- 리뷰 수 / 별점

## 진행 상황
- [x] 렌더링 방식 조사 (서버사이드 렌더링 vs API 기반)
- [x] 데이터 소스 API 특정 (`mc-module` 응답 구조 확인)
- [ ] 파싱 로직 구현
- [ ] Google Sheets 연동 자동화
