# WebBot - 웹 기반 챗봇 (Tailwind CSS 버전)

Flask와 Tailwind CSS를 사용하여 만든 모던한 웹 챗봇입니다.

## 🚀 기능

- **웹 기반 인터페이스**: 브라우저에서 바로 사용 가능
- **실시간 채팅**: AJAX를 통한 비동기 메시지 전송
- **반응형 디자인**: 모바일과 데스크톱 모두 지원
- **모던 UI**: Tailwind CSS로 구현된 아름다운 디자인
- **키워드 기반 응답**: 미리 정의된 규칙에 따른 응답
- **다크 모드 지원**: 시스템 설정에 따른 자동 테마 변경
- **애니메이션**: 부드러운 전환 효과와 호버 애니메이션

## 📁 프로젝트 구조

```
ch03/
├── app.py                 # Flask 메인 애플리케이션
├── simple_chatbot.py      # 콘솔용 챗봇
├── requirements.txt       # Python 패키지 의존성
├── README.md             # 프로젝트 설명서
├── templates/
│   └── index.html        # 메인 HTML 페이지 (Tailwind CSS)
└── static/
    └── js/
        └── script.js     # JavaScript 코드
```

## 🛠️ 설치 및 실행

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 웹 서버 실행

```bash
python app.py
```

### 3. 브라우저에서 접속

```
http://localhost:5000
```

## 💬 사용 가능한 키워드

- **안녕**: 인사말
- **이름**: 봇 이름 안내
- **날씨**: 날씨 관련 응답
- **시간**: 시간 확인 안내
- **도움**: 도움말
- **감사**: 감사 인사
- **잘가**: 작별 인사
- **웹**: 웹 인터페이스 관련
- **파이썬**: Python 관련
- **flask**: Flask 프레임워크 관련

## 🎨 주요 특징

### 프론트엔드 (Tailwind CSS)

- **모던 디자인**: Tailwind CSS로 구현된 깔끔한 UI
- **반응형 레이아웃**: 모든 디바이스에서 최적화된 경험
- **실시간 피드백**: 로딩 인디케이터와 상태 표시
- **접근성**: 키보드 단축키 지원 (Enter, Ctrl+Enter, Escape)
- **애니메이션**: 부드러운 전환 효과와 호버 애니메이션
- **그라데이션**: 아름다운 그라데이션 배경과 버튼

### 백엔드

- **Flask 프레임워크**: 가벼운 웹 서버
- **JSON API**: RESTful API 설계
- **에러 처리**: 안정적인 오류 관리
- **확장 가능**: 새로운 규칙 쉽게 추가 가능

## 🔧 개발 정보

### 기술 스택

- **Backend**: Python, Flask
- **Frontend**: HTML5, Tailwind CSS, JavaScript (ES6+)
- **스타일링**: Tailwind CSS (Utility-First CSS Framework)
- **폰트**: Google Fonts (Noto Sans KR)
- **아이콘**: Font Awesome

### 브라우저 지원

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## 🎯 Tailwind CSS 특징

- **Utility-First**: 클래스 기반 스타일링
- **반응형**: 모바일 우선 접근법
- **커스터마이징**: 테마 설정으로 브랜드 맞춤
- **성능**: 최적화된 CSS 번들
- **접근성**: 기본 접근성 기능 내장

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. 이 저장소를 포크합니다
2. 새로운 기능 브랜치를 생성합니다 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/AmazingFeature`)
5. Pull Request를 생성합니다

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해주세요.
