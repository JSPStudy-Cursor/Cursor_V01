프로젝트: 손글씨 숫자 인식 (MNIST)

개요
- 이 저장소는 두 가지 방식으로 MNIST 손글씨 숫자 인식을 실행합니다.
  1) 웹 앱(Flask): 브라우저에서 그림을 그리고 예측
  2) 데스크톱 앱(Tkinter): 윈도우 창에서 그림을 그리고 예측

폴더/파일 구성
- app.py              : Flask 웹 서버 (엔드포인트: /, /predict)
- main.py             : Tkinter 데스크톱 앱
- mnist_cnn.h5        : 학습된 Keras 모델(없으면 자동 학습/저장)
- requirements.txt    : 의존성 목록
- templates/index.html: 웹 메인 페이지 템플릿
- static/script.js    : 웹 클라이언트 스크립트

사전 준비
- Python 3.9 이상 권장
- 가상환경(선택): python -m venv .venv && .venv\Scripts\activate (PowerShell)
- 의존성 설치: pip install -r requirements.txt
  * 주요 패키지: numpy, pillow, tensorflow, flask

실행 방법 (웹 앱: Flask)
1) PowerShell에서 프로젝트 폴더로 이동
2) (선택) 가상환경 활성화
3) 아래 명령 실행
   python app.py
4) 브라우저에서 http://127.0.0.1:5000 접속
5) 캔버스에 숫자를 그린 후 예측 버튼을 눌러 결과 확인

API 요약
- GET  /            : 웹 UI 제공(templates/index.html)
- POST /predict     : JSON { "image": "data:image/png;base64,..." } 입력 → { result, confidence } 반환

실행 방법 (데스크톱 앱: Tkinter)
1) PowerShell에서 프로젝트 폴더로 이동
2) (선택) 가상환경 활성화
3) 아래 명령 실행
   python main.py
4) 나타난 창에서 마우스로 숫자를 그린 뒤 예측 버튼 클릭

모델 로드/학습 동작
- mnist_cnn.h5 파일이 존재하면 로드합니다.
- 없거나 로드에 실패하면 MNIST 데이터셋으로 3 epoch 학습 후 저장합니다.

Windows/환경 이슈 참고
- TensorFlow CPU만으로도 동작합니다. GPU 사용 시 CUDA/CuDNN 호환 버전 확인이 필요합니다.
- Pillow가 .ps(PostScript) 파일을 여는 과정(데스크톱 앱: temp.ps)에서 Ghostscript가 필요할 수 있습니다.
  * 문제가 발생하면 Ghostscript를 설치하거나, PS 저장/로드 대신 다른 캔버스 캡처 방식으로 변환하세요.

문제 해결 가이드
- ImportError/DLL 오류: 가상환경을 재생성하고 requirements 재설치
- TensorFlow 설치 문제: pip 캐시 정리 후 재설치 (pip cache purge), 또는 버전 고정 시도
- 포트 충돌(5000): app.py의 app.run(port=새포트)로 변경

라이선스
- 교육/실습용 예제 코드
