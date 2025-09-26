import os
from typing import Optional, Tuple
from flask import Flask, render_template, request, jsonify
from PIL import Image
from werkzeug.datastructures import FileStorage

# 내부 모듈 임포트
from image_analyzer import ImageAnalyzer

# Flask 앱 생성
app = Flask(__name__)

# 업로드 설정 (최대 16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

# 이미지 분석기 전역 초기화
image_analyzer: Optional[ImageAnalyzer] = None


def init_analyzer() -> None:
    """서버 시작 시 이미지 분석기를 초기화"""
    global image_analyzer
    image_analyzer = ImageAnalyzer()
    loaded = image_analyzer.load_model()
    if not loaded:
        # 초기화 실패 시에도 앱은 기동되지만, 요청 시 에러 반환
        print("[경고] 이미지 분석기 초기화 실패")


def is_allowed_file(filename: str) -> bool:
    """허용된 확장자인지 확인"""
    _, ext = os.path.splitext(filename)
    return ext.lower() in app.config['ALLOWED_EXTENSIONS']


def load_image_from_filestorage(file_storage: FileStorage) -> Tuple[Optional[Image.Image], Optional[str]]:
    """업로드된 파일에서 PIL 이미지 로드
    반환: (이미지, 오류메시지)
    """
    try:
        if file_storage.filename is None or file_storage.filename.strip() == '':
            return None, "파일명이 비어 있습니다."
        if not is_allowed_file(file_storage.filename):
            return None, f"지원하지 않는 파일 형식입니다. 허용 확장자: {', '.join(sorted(app.config['ALLOWED_EXTENSIONS']))}"
        image = Image.open(file_storage.stream)
        return image, None
    except Exception:
        return None, "이미지 파일을 열 수 없습니다. 손상되었거나 잘못된 형식일 수 있습니다."


@app.route('/', methods=['GET'])
def index():
    """메인 페이지 렌더링"""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """이미지 분석 API 엔드포인트
    - 업로드 파일 또는 이미지 URL 중 하나를 받아 분석 결과(JSON) 반환
    """
    if image_analyzer is None or not image_analyzer.is_loaded:
        return jsonify({
            'success': False,
            'error': '서버 초기화 중 문제로 모델이 로드되지 않았습니다. 잠시 후 다시 시도해주세요.'
        }), 503

    # 입력 소스 식별: 파일 또는 URL
    image: Optional[Image.Image] = None
    source_type = None
    error_message = None

    # 파일 우선 처리
    if 'image' in request.files:
        uploaded_file = request.files.get('image')
        if uploaded_file and uploaded_file.filename:
            image, error_message = load_image_from_filestorage(uploaded_file)
            source_type = 'file'

    # URL 처리 (파일이 없거나 유효하지 않을 때)
    if image is None:
        image_url = (request.form.get('image_url') or '').strip()
        if image_url:
            image = image_analyzer.load_image_from_url(image_url)
            source_type = 'url'
            if image is None:
                error_message = 'URL에서 이미지를 불러오지 못했습니다. URL을 확인해주세요.'

    if image is None:
        return jsonify({
            'success': False,
            'error': error_message or '이미지 파일 또는 URL을 제공해주세요.'
        }), 400

    # 분석 수행
    analysis_results = image_analyzer.analyze_image(image)
    if not analysis_results:
        return jsonify({'success': False, 'error': '이미지 분석에 실패했습니다.'}), 500

    description = image_analyzer.describe_image(analysis_results)

    # 상위 결과를 간단히 정리하여 반환
    simplified_results = [
        {
            'label': item['label'],
            'confidence': item['confidence'],
            'probability': item['probability']
        }
        for item in analysis_results
    ]

    return jsonify({
        'success': True,
        'source_type': source_type,
        'description': description,
        'results': simplified_results
    })


# 애플리케이션 시작 시 모델 초기화
init_analyzer()

if __name__ == '__main__':
    # 개발 서버 실행
    # 참고: 프로덕션 환경에서는 WSGI 서버(gunicorn/waitress 등) 사용 권장
    app.run(host='0.0.0.0', port=5000, debug=True)
