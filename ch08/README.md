# 서울 집값 데이터 수집기

서울 열린 데이터 광장에서 서울 집값의 최근 5년치 데이터를 수집하여 CSV 파일로 저장하는 파이썬 프로그램입니다.

## 기능

- 서울시 아파트 실거래가 데이터 수집
- 서울시 오피스텔 실거래가 데이터 수집
- 서울시 빌라/연립 실거래가 데이터 수집
- 최근 5년치 데이터 필터링
- CSV 파일로 데이터 저장

## 설치 방법

1. 필요한 패키지 설치:

```bash
pip install -r requirements.txt
```

## 사용 방법

### 1. API 키 발급

서울 열린 데이터 광장(https://data.seoul.go.kr/)에서 API 키를 발급받으세요:

1. 서울 열린 데이터 광장 웹사이트 접속
2. 회원가입 및 로그인
3. "API 신청" 메뉴에서 API 키 발급
4. 발급받은 API 키를 코드에 입력

### 2. API 키 설정

다음 중 하나의 방법으로 API 키를 설정하세요:

#### 방법 1: 환경변수 사용 (권장)

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```
SEOUL_API_KEY=your_actual_api_key_here
```

#### 방법 2: config.py 파일 직접 수정

`config.py` 파일에서 다음 줄을 수정하세요:

```python
SEOUL_API_KEY = "your_actual_api_key_here"  # 실제 API 키로 교체
```

#### 방법 3: 기존 파일 수정

`seoul_housing_price_actual.py` 파일에서 다음 줄을 수정하세요:

```python
self.api_key = "your_actual_api_key_here"  # 실제 API 키로 교체
```

### 3. 프로그램 실행

#### 개선된 버전 사용 (권장)

```bash
python seoul_housing_price_improved.py
```

#### 기본 버전 사용

```bash
python seoul_housing_price_actual.py
```

## 파일 구조

```
ch08/
├── seoul_housing_price_crawler.py      # 기본 버전 (일반적인 API 구조)
├── seoul_housing_price_actual.py       # 실제 서울 열린 데이터 광장 API 사용
├── seoul_housing_price_improved.py     # 개선된 버전 (설정 파일 사용)
├── config.py                           # 설정 관리 파일
├── requirements.txt                     # 필요한 패키지 목록
├── README.md                           # 사용법 설명
└── housing_data/                       # 수집된 데이터 저장 폴더 (자동 생성)
    └── seoul_housing_price_YYYYMMDD_HHMMSS.csv
```

## 주요 특징

### 에러 처리

- API 요청 실패 시 재시도 로직
- JSON 파싱 오류 처리
- 날짜 형식 오류 처리
- 네트워크 타임아웃 설정

### 데이터 관리

- 한글 깨짐 방지를 위한 UTF-8-SIG 인코딩 사용
- 자동으로 데이터 저장 폴더 생성
- 타임스탬프가 포함된 파일명으로 저장

### API 호출 최적화

- API 호출 제한을 고려한 대기 시간 설정
- 월별 데이터 수집으로 메모리 효율성 확보

## 수집되는 데이터 항목

실제 API 응답에 따라 다를 수 있지만, 일반적으로 다음과 같은 정보가 포함됩니다:

- 거래일자
- 거래금액
- 건물명
- 동
- 층
- 면적
- 지번
- 법정동
- 시군구
- 건축년도
- 물건종류 (아파트/오피스텔/빌라/연립)

## 주의사항

1. **API 키 보안**: API 키를 코드에 직접 하드코딩하지 말고 환경변수나 설정 파일을 사용하세요.
2. **API 호출 제한**: 서울 열린 데이터 광장의 API 호출 제한을 확인하고 준수하세요.
3. **데이터 용량**: 5년치 데이터는 용량이 클 수 있으므로 충분한 저장 공간을 확보하세요.

## 문제 해결

### API 키 오류

- API 키가 올바르게 설정되었는지 확인
- API 키의 권한과 사용량 제한 확인

### 데이터가 수집되지 않는 경우

- API 엔드포인트 URL 확인
- 네트워크 연결 상태 확인
- API 응답 구조 확인 후 코드 수정

### 한글이 깨지는 경우

- CSV 파일이 UTF-8-SIG 인코딩으로 저장되었는지 확인
- 엑셀에서 열 때 인코딩 설정 확인

## 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제작되었습니다.
