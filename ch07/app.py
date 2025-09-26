from flask import Flask, render_template, request, jsonify, send_file
import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pickle
import warnings
import base64
import io
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # 백엔드 설정
warnings.filterwarnings('ignore')

app = Flask(__name__)

def load_trained_model(model_dir="models"):
    """훈련된 모델을 로드하는 함수"""
    try:
        model_files = glob.glob(f"{model_dir}/*.pkl")
        if not model_files:
            return None, None
        
        latest_model = max(model_files, key=os.path.getctime)
        with open(latest_model, 'rb') as f:
            model = pickle.load(f)
        
        return model, latest_model
    except Exception as e:
        print(f"모델 로드 오류: {e}")
        return None, None

def load_latest_data(data_dir="processed_data"):
    """최신 전처리된 데이터를 로드하는 함수"""
    try:
        test_files = glob.glob(f"{data_dir}/X_test_*.csv")
        if not test_files:
            return None
        
        latest_test = max(test_files, key=os.path.getctime)
        X_test = pd.read_csv(latest_test, index_col=0)
        return X_test
    except Exception as e:
        print(f"데이터 로드 오류: {e}")
        return None

def predict_tomorrow_stock_price(model, X_test):
    """내일의 주가를 예측하는 함수"""
    try:
        latest_data = X_test.iloc[-1:].values
        tomorrow_prediction = model.predict(latest_data)[0]
        confidence_score = 0.9986  # 훈련된 모델의 R² 값
        
        if confidence_score > 0.8:
            confidence_level = "높음"
            confidence_color = "success"
        elif confidence_score > 0.6:
            confidence_level = "보통"
            confidence_color = "warning"
        else:
            confidence_level = "낮음"
            confidence_color = "danger"
        
        return tomorrow_prediction, confidence_level, confidence_color, confidence_score
    except Exception as e:
        print(f"예측 오류: {e}")
        return None, None, None, None

def get_market_trend(X_test):
    """시장 트렌드 분석 함수"""
    try:
        recent_data = X_test.tail(5)
        if 'Daily_Return' in recent_data.columns:
            daily_returns = recent_data['Daily_Return'].values
            trend = "상승" if np.mean(daily_returns) > 0 else "하락"
            volatility = np.std(daily_returns)
        else:
            trend = "중립"
            volatility = 0
        return trend, volatility
    except Exception as e:
        return "중립", 0

def create_prediction_chart(X_test, prediction):
    """예측 차트를 생성하고 base64로 인코딩하는 함수"""
    try:
        # 한글 폰트 설정
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False
        
        recent_data = X_test.tail(30)
        
        plt.figure(figsize=(12, 6))
        
        if 'High' in recent_data.columns:
            plt.plot(recent_data.index, recent_data['High'], 'b-', label='최근 주가', linewidth=2)
        
        tomorrow_idx = len(recent_data)
        plt.scatter(tomorrow_idx, prediction, color='red', s=100, label='내일 예측', zorder=5)
        plt.annotate(f'{prediction:,.0f}원', 
                    xy=(tomorrow_idx, prediction), 
                    xytext=(tomorrow_idx+2, prediction),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=10, color='red')
        
        plt.title('삼성전자 주가 예측 트렌드', fontsize=14, fontweight='bold')
        plt.xlabel('날짜')
        plt.ylabel('주가 (원)')
        plt.xticks(rotation=90)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 그래프를 base64로 인코딩
        img = BytesIO()
        plt.savefig(img, format='png', dpi=300, bbox_inches='tight')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        return graph_url
    except Exception as e:
        print(f"차트 생성 오류: {e}")
        return None

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """주가 예측 API"""
    try:
        # 모델과 데이터 로드
        model, model_file = load_trained_model()
        if model is None:
            return jsonify({'error': '훈련된 모델을 찾을 수 없습니다.'})
        
        X_test = load_latest_data()
        if X_test is None:
            return jsonify({'error': '데이터를 찾을 수 없습니다.'})
        
        # 예측 수행
        prediction, confidence_level, confidence_color, confidence_score = predict_tomorrow_stock_price(model, X_test)
        if prediction is None:
            return jsonify({'error': '예측 중 오류가 발생했습니다.'})
        
        # 시장 트렌드 분석
        trend, volatility = get_market_trend(X_test)
        
        # 차트 생성
        chart_url = create_prediction_chart(X_test, prediction)
        
        # 투자 조언 생성
        investment_advice = ""
        if confidence_score > 0.8:
            if trend == "상승":
                investment_advice = "높은 신뢰도와 상승 트렌드로 매수 고려"
            else:
                investment_advice = "높은 신뢰도이지만 하락 트렌드 주의"
        elif confidence_score > 0.6:
            investment_advice = "보통 신뢰도로 신중한 투자 권장"
        else:
            investment_advice = "낮은 신뢰도로 투자 신중 권장"
        
        # 결과 반환
        result = {
            'prediction': f"{prediction:,.0f}",
            'prediction_date': (datetime.now() + timedelta(days=1)).strftime('%Y년 %m월 %d일'),
            'confidence_level': confidence_level,
            'confidence_color': confidence_color,
            'confidence_score': f"{confidence_score:.1%}",
            'trend': trend,
            'volatility': f"{volatility:.2%}",
            'investment_advice': investment_advice,
            'chart_url': chart_url,
            'model_file': os.path.basename(model_file) if model_file else "Unknown"
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'서버 오류: {str(e)}'})

@app.route('/api/model-info')
def model_info():
    """모델 정보 API"""
    try:
        model_files = glob.glob("models/*.pkl")
        if model_files:
            latest_model = max(model_files, key=os.path.getctime)
            model_size = os.path.getsize(latest_model)
            model_date = datetime.fromtimestamp(os.path.getctime(latest_model))
            
            return jsonify({
                'model_file': os.path.basename(latest_model),
                'model_size': f"{model_size:,} bytes",
                'model_date': model_date.strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'available'
            })
        else:
            return jsonify({'status': 'no_model'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 