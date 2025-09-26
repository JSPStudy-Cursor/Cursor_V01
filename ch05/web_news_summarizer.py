from flask import Flask, render_template, request, jsonify
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re
import logging
from typing import Optional, Dict, Any
import warnings
import os
warnings.filterwarnings('ignore')

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class WebNewsSummarizer:
    """
    웹용 뉴스 요약기
    """
    
    def __init__(self, model_name: str = "paust/pko-t5-large"):
        """
        모델 초기화
        """
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """
        모델 로딩 (필요할 때만 로딩)
        """
        if self.model is None:
            try:
                logger.info(f"모델 로딩 중: {self.model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                self.model.to(self.device)
                logger.info(f"모델 로딩 완료 (디바이스: {self.device})")
            except Exception as e:
                logger.error(f"모델 로딩 실패: {e}")
                raise
    
    def clean_text(self, text: str) -> str:
        """
        텍스트 정리
        """
        try:
            # HTML 태그 제거
            text = re.sub(r'<[^>]+>', '', text)
            # 여러 공백을 하나로
            text = re.sub(r'\s+', ' ', text)
            # 앞뒤 공백 제거
            return text.strip()
        except Exception as e:
            logger.error(f"텍스트 정리 중 오류: {e}")
            return text
    
    def summarize(self, text: str, max_length: int = 100) -> str:
        """
        텍스트 요약
        """
        try:
            if not text or len(text.strip()) == 0:
                return "요약할 텍스트가 없습니다."
            
            # 모델 로딩
            self.load_model()
            
            # 텍스트 정리
            cleaned_text = self.clean_text(text)
            
            # 토크나이저로 인코딩
            inputs = self.tokenizer(
                cleaned_text, 
                max_length=1024, 
                truncation=True, 
                padding=True, 
                return_tensors="pt"
            ).to(self.device)
            
            # 요약 생성
            with torch.no_grad():
                summary_ids = self.model.generate(
                    inputs["input_ids"],
                    max_length=max_length,
                    min_length=30,
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True,
                    no_repeat_ngram_size=3
                )
            
            # 디코딩
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"요약 생성 중 오류: {e}")
            return f"요약 생성 중 오류가 발생했습니다: {e}"
    
    def get_summary_stats(self, original: str, summary: str) -> Dict[str, Any]:
        """
        요약 통계 정보
        """
        try:
            original_length = len(original)
            summary_length = len(summary)
            compression_ratio = (1 - summary_length / original_length) * 100 if original_length > 0 else 0
            
            return {
                "original_length": original_length,
                "summary_length": summary_length,
                "compression_ratio": round(compression_ratio, 2),
                "model_name": self.model_name
            }
        except Exception as e:
            logger.error(f"통계 계산 중 오류: {e}")
            return {}

def create_html_template():
    """
    HTML 템플릿 생성
    """
    html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>뉴스 요약 프로그램</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        textarea {
            width: 100%;
            height: 200px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            resize: vertical;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat-item {
            background: white;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }
        .stat-label {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
        .error {
            color: #dc3545;
            background-color: #f8d7da;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📰 뉴스 기사 요약 프로그램</h1>
        
        <div class="form-group">
            <label for="newsText">뉴스 기사를 입력하세요:</label>
            <textarea id="newsText" placeholder="여기에 뉴스 기사를 붙여넣으세요..."></textarea>
        </div>
        
        <button id="summarizeBtn" onclick="summarizeText()">요약 생성</button>
        
        <div id="result" class="result" style="display: none;">
            <h3>📝 요약 결과</h3>
            <div id="summaryText"></div>
            
            <div class="stats" id="stats">
                <div class="stat-item">
                    <div class="stat-value" id="originalLength">0</div>
                    <div class="stat-label">원본 길이</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="summaryLength">0</div>
                    <div class="stat-label">요약 길이</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="compressionRatio">0%</div>
                    <div class="stat-label">압축률</div>
                </div>
            </div>
        </div>
        
        <div id="loading" class="loading" style="display: none;">
            요약을 생성하고 있습니다. 잠시만 기다려주세요...
        </div>
        
        <div id="error" class="error" style="display: none;"></div>
    </div>

    <script>
        async function summarizeText() {
            const text = document.getElementById('newsText').value.trim();
            const button = document.getElementById('summarizeBtn');
            const result = document.getElementById('result');
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            
            if (!text) {
                alert('뉴스 기사를 입력해주세요.');
                return;
            }
            
            // UI 상태 변경
            button.disabled = true;
            button.textContent = '요약 생성 중...';
            result.style.display = 'none';
            loading.style.display = 'block';
            error.style.display = 'none';
            
            try {
                const response = await fetch('/summarize', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: text })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // 결과 표시
                    document.getElementById('summaryText').textContent = data.summary;
                    document.getElementById('originalLength').textContent = data.stats.original_length;
                    document.getElementById('summaryLength').textContent = data.stats.summary_length;
                    document.getElementById('compressionRatio').textContent = data.stats.compression_ratio + '%';
                    
                    result.style.display = 'block';
                } else {
                    throw new Error(data.error || '요약 생성에 실패했습니다.');
                }
                
            } catch (err) {
                error.textContent = err.message;
                error.style.display = 'block';
            } finally {
                // UI 상태 복원
                button.disabled = false;
                button.textContent = '요약 생성';
                loading.style.display = 'none';
            }
        }
        
        // Enter 키로 요약 실행
        document.getElementById('newsText').addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                summarizeText();
            }
        });
    </script>
</body>
</html>
    """
    
    # templates 디렉토리 생성
    os.makedirs('templates', exist_ok=True)
    
    # HTML 파일 생성
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

# 전역 요약기 인스턴스
summarizer = WebNewsSummarizer()

@app.route('/')
def index():
    """
    메인 페이지
    """
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize_text():
    """
    텍스트 요약 API
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': '텍스트가 입력되지 않았습니다.'}), 400
        
        # 요약 생성
        summary = summarizer.summarize(text)
        stats = summarizer.get_summary_stats(text, summary)
        
        return jsonify({
            'summary': summary,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"요약 API 오류: {e}")
        return jsonify({'error': f'요약 생성 중 오류가 발생했습니다: {e}'}), 500

@app.route('/health')
def health_check():
    """
    헬스 체크
    """
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # HTML 템플릿 생성
    create_html_template()
    app.run(debug=True, host='0.0.0.0', port=5000) 