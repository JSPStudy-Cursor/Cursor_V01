## 손글씨 숫자 인식기 (MNIST)

웹(Flask)과 데스크톱(Tkinter) 두 가지 방식으로 손글씨 숫자(0~9)를 인식하는 예제입니다. 모델은 Keras로 간단한 MLP를 학습하거나, 동일 구조의 사전 학습된 가중치(`mnist_cnn.h5`)를 로드하여 사용합니다.

### 주요 기능
- **웹 앱(Flask)**: 브라우저 캔버스에 숫자를 그려 `/predict` API로 예측 수행
- **데스크톱 앱(Tkinter)**: 윈도우 캔버스에 숫자를 그리고 버튼으로 예측
- **자동 모델 준비**: `mnist_cnn.h5`가 없으면 MNIST를 다운받아 3 epoch 학습 후 저장

### 프로젝트 구조
```
ch02/
  app.py                # Flask 웹 서버 (예측 API 포함)
  main.py               # Tkinter 데스크톱 앱
  mnist_cnn.h5          # 학습된 모델(없으면 자동 학습 후 생성)
  requirements.txt      # 의존성 목록
  templates/
    index.html          # 웹 UI 템플릿 (Tailwind 사용)
  static/
    script.js           # 캔버스 드로잉 및 예측 요청 스크립트
```

### 요구 사항
- Python 3.9+ 권장
- Windows 10 환경(테스트 기준). 다른 OS도 Python/TensorFlow 환경 구성 시 동작 가능

### 설치
```bash
pip install -r requirements.txt
```

### 실행 - 웹(Flask)
```bash
python app.py
```
- 기본 실행 후 브라우저에서 `http://127.0.0.1:5000` 접속
- 캔버스에 숫자를 그리고 "예측하기" 버튼 클릭

#### REST API
- **POST** `/predict`
  - 요청 본문(JSON): `{ "image": "data:image/png;base64,..." }`
  - 응답(JSON): `{ "result": <0~9 정답>, "confidence": <0.0~1.0 신뢰도> }`

### 실행 - 데스크톱(Tkinter)
```bash
python main.py
```
- 창에서 숫자를 그리고 "예측" 버튼 클릭

### 참고 사항
- 최초 실행 시 MNIST 데이터 다운로드 및 간단 학습(약 3 epoch)을 수행할 수 있습니다.
- 학습이 끝나면 `mnist_cnn.h5`가 생성되며 이후부터는 재사용합니다.
- 이미지 전처리: 흑백 반전 및 28x28 리사이즈 후 0~1 스케일링.

### 라이선스
학습 및 교육용 예제 코드입니다. 필요 시 자유롭게 수정/확장하여 사용하세요.


