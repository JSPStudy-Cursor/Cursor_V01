# 삼성전자 주가 데이터 수집 및 전처리

Yahoo Finance에서 삼성전자 주가의 최근 5년치 데이터를 가져와서 전처리하고 훈련용/테스트용으로 분할하는 파이썬 스크립트입니다.

## 기능

### 데이터 수집 (`samsung_stock_data.py`)

- Yahoo Finance에서 삼성전자(005930.KS) 주가 데이터 수집
- 최근 5년간의 일별 주가 데이터 (시가, 고가, 저가, 종가, 거래량)
- CSV 파일로 데이터 저장
- 데이터 통계 정보 및 미리보기 제공

### 데이터 전처리 (`data_preprocessing.py`)

- 누락된 데이터 확인 및 제거
- 기술적 지표 생성 (이동평균, 변동성, 수익률 등)
- 훈련용/테스트용 데이터 분할 (시계열 순서 유지)
- 전처리된 데이터 CSV 저장

## 설치 방법

1. 필요한 라이브러리 설치:

```bash
pip install -r requirements.txt
```

## 사용 방법

### 1단계: 데이터 수집

```bash
python samsung_stock_data.py
```

### 2단계: 데이터 전처리 및 분할

```bash
python data_preprocessing.py
```

## 출력 파일

### 데이터 수집 결과

- `samsung_stock_5years.csv`: 삼성전자 주가 데이터 (최근 5년)

### 전처리 결과

- `processed_data/` 폴더에 다음 파일들이 생성됩니다:
  - `X_train_[timestamp].csv`: 훈련용 특성 데이터
  - `X_test_[timestamp].csv`: 테스트용 특성 데이터
  - `y_train_[timestamp].csv`: 훈련용 타겟 데이터
  - `y_test_[timestamp].csv`: 테스트용 타겟 데이터

## 생성되는 특성 (Features)

### 기본 특성

- **Open**: 시가
- **High**: 고가
- **Low**: 저가
- **Volume**: 거래량
- **Dividends**: 배당금
- **Stock Splits**: 주식 분할

### 생성되는 기술적 지표

- **Daily_Return**: 일일 수익률
- **MA_5/20/60**: 5일/20일/60일 이동평균
- **Volatility**: 20일 변동성
- **Volume_MA_5**: 5일 거래량 이동평균
- **High_Low_Ratio**: 고가-저가 비율
- **Open_Close_Ratio**: 시가-종가 비율
- **Volume_Change**: 거래량 변화율

## 주의사항

- 인터넷 연결이 필요합니다
- Yahoo Finance API를 사용하므로 네트워크 상태에 따라 데이터 수집 속도가 달라질 수 있습니다
- 삼성전자의 Yahoo Finance 티커는 '005930.KS'입니다 (코스피)
- 시계열 데이터이므로 시간 순서를 유지하여 분할합니다

## 웹 애플리케이션

Flask를 사용한 웹 인터페이스를 제공합니다:

### 웹 애플리케이션 실행

```bash
python app.py
```

### 웹 애플리케이션 기능

- **실시간 예측**: 내일의 삼성전자 주가 예측
- **시각화**: 예측 트렌드 차트 제공
- **신뢰도 분석**: 예측 신뢰도 및 시장 트렌드 분석
- **투자 조언**: AI 기반 투자 조언 제공

### 웹 접속 방법

1. `python app.py` 실행
2. 브라우저에서 `http://localhost:5000` 접속
3. "내일 주가 예측하기" 버튼 클릭
4. 예측 결과 확인
