import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from sd_text2img import generate_image_from_text


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'outputs'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')


def _get_default_settings() -> Dict[str, Any]:
    """
    기본 설정값을 반환한다.
    """
    return {
        'model_id': 'runwayml/stable-diffusion-v1-5',
        'num_inference_steps': 30,
        'guidance_scale': 7.5,
        'width': 512,
        'height': 512,
        'seed': None,
        'output_prefix': 'sd_v15'
    }


def _validate_input(prompt: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    입력값을 검증하고 안전한 기본값으로 보정한다.
    """
    errors = []
    
    # 프롬프트 검증
    if not prompt or not prompt.strip():
        errors.append("프롬프트는 비어 있을 수 없습니다.")
        return {'errors': errors}
    
    # 숫자 값 검증 및 보정
    try:
        steps = int(settings.get('num_inference_steps', 30))
        if steps <= 0:
            steps = 30
    except (ValueError, TypeError):
        steps = 30
    
    try:
        guidance = float(settings.get('guidance_scale', 7.5))
        if guidance <= 0:
            guidance = 7.5
    except (ValueError, TypeError):
        guidance = 7.5
    
    try:
        width = int(settings.get('width', 512))
        if width <= 0:
            width = 512
    except (ValueError, TypeError):
        width = 512
    
    try:
        height = int(settings.get('height', 512))
        if height <= 0:
            height = 512
    except (ValueError, TypeError):
        height = 512
    
    try:
        seed = settings.get('seed')
        if seed is not None:
            seed = int(seed)
    except (ValueError, TypeError):
        seed = None
    
    return {
        'prompt': prompt.strip(),
        'model_id': settings.get('model_id', 'runwayml/stable-diffusion-v1-5'),
        'num_inference_steps': steps,
        'guidance_scale': guidance,
        'width': width,
        'height': height,
        'seed': seed,
        'output_prefix': settings.get('output_prefix', 'sd_v15'),
        'errors': errors
    }


@app.route('/')
def index():
    """
    메인 페이지를 렌더링한다.
    """
    return render_template('index.html', default_settings=_get_default_settings())


@app.route('/generate', methods=['POST'])
def generate_image():
    """
    이미지 생성을 처리한다.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        prompt = data.get('prompt', '')
        settings = data.get('settings', {})
        
        # 입력값 검증
        validated = _validate_input(prompt, settings)
        if validated.get('errors'):
            return jsonify({'errors': validated['errors']}), 400
        
        # 이미지 생성
        output_path = generate_image_from_text(
            prompt=validated['prompt'],
            model_id=validated['model_id'],
            num_inference_steps=validated['num_inference_steps'],
            guidance_scale=validated['guidance_scale'],
            width=validated['width'],
            height=validated['height'],
            seed=validated['seed'],
            output_dir=app.config['UPLOAD_FOLDER'],
            output_prefix=validated['output_prefix']
        )
        
        # 상대 경로로 변환
        relative_path = os.path.relpath(output_path, app.config['UPLOAD_FOLDER'])
        
        return jsonify({
            'success': True,
            'image_path': f'/outputs/{relative_path}',
            'message': '이미지가 성공적으로 생성되었습니다.'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'이미지 생성 중 오류가 발생했습니다: {str(e)}'
        }), 500


@app.route('/outputs/<path:filename>')
def serve_output(filename):
    """
    생성된 이미지 파일을 제공한다.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/health')
def health_check():
    """
    헬스 체크 엔드포인트
    """
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # 출력 디렉토리 생성
    Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
    
    # 개발 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5000)
