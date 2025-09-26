## Stable Diffusion 텍스트→이미지 생성기 (Flask)

### 개요
- **Diffusers 기반 Stable Diffusion v1.5**로 텍스트 프롬프트에서 이미지를 생성합니다.
- **웹 UI(Flask)** 와 **CLI** 모두 지원합니다.

### 필수 요구사항
- **Python 3.10+** 권장
- **Windows 10/11**
- **NVIDIA GPU** 및 최신 그래픽 드라이버/CUDA 런타임 권장(없어도 CPU로 동작 가능하나 매우 느립니다)

### 설치 (PowerShell 기준)
1) 프로젝트 디렉터리로 이동
```powershell
cd C:\Cursor\projects_교재소스_0919\ch06
```

2) 가상환경 생성 및 활성화
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) 필수 패키지 설치
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```
> 주의: torch는 시스템/CUDA 버전에 맞는 휠을 설치해야 합니다.
> - 공식 설치 가이드: [PyTorch Local Guide](https://pytorch.org/get-started/locally/)
> - 예시(CUDA 12.1):
>   ```powershell
>   pip install torch --index-url https://download.pytorch.org/whl/cu121
>   ```
> - CPU 전용(느림):
>   ```powershell
>   pip install torch --index-url https://download.pytorch.org/whl/cpu
>   ```

### 첫 실행 시 모델 다운로드
- diffusers가 `runwayml/stable-diffusion-v1-5` 모델 가중치를 자동 다운로드합니다(수백 MB~수 GB).
- 인터넷 연결이 필요하며, 최초 1회만 다운로드합니다.

### 실행 방법
#### 웹 앱 (Flask)
```powershell
python app.py
```
- 브라우저에서 `http://localhost:5000`
- 생성 이미지는 `outputs/` 폴더에 저장됩니다.

#### CLI
- 기본 실행(예시 프롬프트로 1장 생성):
```powershell
python main.py
```
- 사용자 프롬프트로 생성:
```powershell
python main.py --prompt "A cute cat, 4k, ultra-detailed"
```
- 주요 옵션:
```text
--model-id runwayml/stable-diffusion-v1-5
--steps 30
--guidance 7.5
--width 512 --height 512
--seed 42
--output-dir outputs --output-prefix sd_v15
```

### API
- POST `/generate`
  - Headers: `Content-Type: application/json`
  - 요청 예시
    ```json
    {
      "prompt": "A serene watercolor landscape of misty mountains at sunrise, 4k",
      "settings": {
        "model_id": "runwayml/stable-diffusion-v1-5",
        "num_inference_steps": 30,
        "guidance_scale": 7.5,
        "width": 512,
        "height": 512,
        "seed": 42,
        "output_prefix": "sd_v15"
      }
    }
    ```
  - 성공 응답
    ```json
    {
      "success": true,
      "image_path": "/outputs/<relative-path>",
      "message": "이미지가 성공적으로 생성되었습니다."
    }
    ```

- GET `/outputs/<filename>`: 생성된 이미지 파일 반환
- GET `/health`: 애플리케이션 상태 확인

### 환경 변수
- `SECRET_KEY`: Flask 세션 키(기본값: `dev-secret-key-change-in-production`)
  - PowerShell 예: 
    ```powershell
    $env:SECRET_KEY = "your-secret"
    ```

### 프로젝트 구조
- `app.py`                Flask 웹 서버 및 API 엔드포인트
- `main.py`               CLI 실행 스크립트
- `sd_text2img.py`        텍스트→이미지 생성 로직
- `templates/index.html`  웹 UI 템플릿
- `static/js/script.js`   프론트엔드 스크립트
- `outputs/`              생성 이미지 저장 폴더
- `requirements.txt`      파이썬 의존성 목록
- `package.json`          프론트엔드(개발) 의존성

### 트러블슈팅
- **torch 설치 오류**: 시스템/CUDA에 맞는 휠 사용 여부 확인 → [PyTorch Local Guide](https://pytorch.org/get-started/locally/)
- **CUDA out of memory**: `width`/`height`를 낮추고(예: 512→384), `steps`를 줄이거나 배치를 1로 유지
- **생성이 매우 느림**: GPU 인식 상태 확인, CPU 전용 torch 설치 여부 점검
- **포트 충돌(5000 사용 중)**: 다른 포트로 실행(`set FLASK_RUN_PORT=5001`) 또는 `app.py`에서 포트 수정

### 라이선스 및 모델 사용
- 모델/데이터셋 라이선스를 준수해야 합니다. 상업적 사용 전 라이선스 확인을 권장합니다.

### 문의
- 이슈나 제안은 리포지토리에 등록해주세요.
