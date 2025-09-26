# 뉴스 기사 요약 프로그램

뉴스 기사 본문을 한 줄로 요약하는 파이썬 프로그램입니다. 사전 학습된 T5/BART 모델을 사용하여 정확한 요약을 생성합니다.

## 📁 파일 구조

- `news_summarizer.py` - 기본 키워드 기반 요약기
- `advanced_news_summarizer.py` - 고급 T5/BART 모델 요약기
- `simple_news_summarizer.py` - 간단한 대화형 요약기
- `web_news_summarizer.py` - 웹 인터페이스 요약기

## 🚀 주요 기능

### 1. 기본 요약기 (키워드 기반)

- **텍스트 전처리**: 특수문자 제거, 공백 정리
- **키워드 추출**: 빈도수 기반 키워드 추출 (불용어 제거)
- **핵심 문장 추출**: 첫 번째 문장 또는 주요 문장 추출
- **한 줄 요약**: 키워드와 핵심 문장을 조합한 요약 생성

### 2. 고급 요약기 (T5/BART 모델)

- **사전 학습된 모델**: 한국어 T5 모델 사용
- **정확한 요약**: 자연어 처리 기반 요약
- **긴 텍스트 처리**: 자동 텍스트 분할 및 요약
- **통계 정보**: 압축률, 길이 등 상세 정보 제공

### 3. 웹 인터페이스

- **사용자 친화적 UI**: 웹 브라우저에서 쉽게 사용
- **실시간 요약**: AJAX를 통한 비동기 요약
- **통계 시각화**: 요약 결과를 시각적으로 표시

## 📦 설치 방법

```bash
# 필요한 패키지 설치
pip install -r requirements.txt
```

## 🎯 사용 방법

### 1. 기본 요약기 사용

```python
from news_summarizer import NewsSummarizer

# 요약기 생성
summarizer = NewsSummarizer()

# 뉴스 텍스트
news_text = """
서울시는 오늘 새로운 환경 정책을 발표했습니다.
이번 정책은 탄소 배출량을 2030년까지 40% 감축하는 것을 목표로 합니다.
"""

# 요약 생성
summary = summarizer.create_summary(news_text)
print(summary)
```

### 2. 고급 요약기 사용

```python
from advanced_news_summarizer import AdvancedNewsSummarizer

# 요약기 생성 (첫 실행 시 모델 다운로드)
summarizer = AdvancedNewsSummarizer()

# 요약 생성
summary = summarizer.summarize_text(news_text)
print(summary)
```

### 3. 간단한 대화형 사용

```bash
python simple_news_summarizer.py
```

### 4. 웹 인터페이스 사용

```bash
python web_news_summarizer.py
```

웹 브라우저에서 `http://localhost:5000` 접속

## 📊 실행 예시

### 기본 요약기

```bash
python news_summarizer.py
```

### 고급 요약기

```bash
python advanced_news_summarizer.py
```

### 웹 인터페이스

```bash
python web_news_summarizer.py
```

## 🔧 주요 특징

- **한국어 최적화**: 한국어 불용어 처리 및 텍스트 전처리
- **에러 처리**: 각 단계별 예외 처리로 안정성 확보
- **로깅**: 상세한 로그 기록으로 디버깅 지원
- **확장 가능**: 새로운 요약 알고리즘 추가 용이
- **사용자 친화적**: 웹 인터페이스로 쉬운 사용

## 📈 성능 비교

| 방법         | 정확도 | 속도 | 메모리 사용량 |
| ------------ | ------ | ---- | ------------- |
| 키워드 기반  | 보통   | 빠름 | 낮음          |
| T5/BART 모델 | 높음   | 보통 | 높음          |

## 🚀 향후 개선 방향

- KoBERT, KoNLPy 등 한국어 자연어 처리 라이브러리 통합
- 더 정교한 문장 중요도 계산 알고리즘
- 다양한 뉴스 사이트별 스크래핑 최적화
- 요약 품질 평가 기능 추가
- 모바일 앱 버전 개발
