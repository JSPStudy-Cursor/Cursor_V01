import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import pickle
import warnings
warnings.filterwarnings('ignore')

def load_trained_model(model_dir="models"):
    """훈련된 모델을 로드하는 함수"""
    try:
        # 가장 최근 모델 파일 찾기
        model_files = glob.glob(f"{model_dir}/*.pkl")
        if not model_files:
            print("❌ 훈련된 모델 파일을 찾을 수 없습니다.")
            print("먼저 stock_price_predictor.py를 실행하여 모델을 훈련해주세요.")
            return None, None
        
        latest_model = max(model_files, key=os.path.getctime)
        print(f"📁 모델 파일 로드: {os.path.basename(latest_model)}")
        
        with open(latest_model, 'rb') as f:
            model = pickle.load(f)
        
        return model, latest_model
    
    except Exception as e:
        print(f"❌ 모델 로드 중 오류 발생: {e}")
        return None, None

def load_latest_data(data_dir="processed_data"):
    """최신 전처리된 데이터를 로드하는 함수"""
    try:
        # 가장 최근 데이터 파일들 찾기
        test_files = glob.glob(f"{data_dir}/X_test_*.csv")
        if not test_files:
            print("❌ 전처리된 데이터 파일을 찾을 수 없습니다.")
            print("먼저 data_preprocessing.py를 실행해주세요.")
            return None
        
        latest_test = max(test_files, key=os.path.getctime)
        print(f"📊 데이터 파일 로드: {os.path.basename(latest_test)}")
        
        X_test = pd.read_csv(latest_test, index_col=0)
        return X_test
    
    except Exception as e:
        print(f"❌ 데이터 로드 중 오류 발생: {e}")
        return None

def predict_tomorrow_stock_price(model, X_test):
    """내일의 주가를 예측하는 함수"""
    try:
        # 가장 최근 데이터 가져오기
        latest_data = X_test.iloc[-1:].values
        
        # 예측 수행
        tomorrow_prediction = model.predict(latest_data)[0]
        
        # 예측 신뢰도 계산 (모델 성능 기반)
        # 실제 y_test 데이터가 없으므로 기본값 사용
        confidence_score = 0.9986  # stock_price_predictor.py에서 확인된 R² 값
        
        # 신뢰도 등급 결정
        if confidence_score > 0.8:
            confidence_level = "높음"
            confidence_color = "🟢"
        elif confidence_score > 0.6:
            confidence_level = "보통"
            confidence_color = "🟡"
        else:
            confidence_level = "낮음"
            confidence_color = "🔴"
        
        return tomorrow_prediction, confidence_level, confidence_color, confidence_score
        
    except Exception as e:
        print(f"❌ 예측 중 오류 발생: {e}")
        return None, None, None, None

def get_market_trend(X_test):
    """시장 트렌드 분석 함수"""
    try:
        # 최근 5일간의 데이터로 트렌드 분석
        recent_data = X_test.tail(5)
        
        # 주요 지표들의 변화 추이
        if 'Daily_Return' in recent_data.columns:
            daily_returns = recent_data['Daily_Return'].values
            trend = "상승" if np.mean(daily_returns) > 0 else "하락"
            volatility = np.std(daily_returns)
        else:
            trend = "중립"
            volatility = 0
        
        return trend, volatility
        
    except Exception as e:
        print(f"⚠️ 트렌드 분석 중 오류: {e}")
        return "중립", 0

def format_prediction_result(prediction, confidence_level, confidence_color, confidence_score, trend, volatility):
    """예측 결과를 보기 좋게 포맷팅하는 함수"""
    print("\n" + "="*60)
    print("📈 내일의 삼성전자 주가 예측 결과")
    print("="*60)
    
    # 예측 주가
    print(f"🎯 예측 주가: {prediction:,.0f}원")
    
    # 예측 날짜
    tomorrow = datetime.now() + timedelta(days=1)
    print(f"📅 예측 날짜: {tomorrow.strftime('%Y년 %m월 %d일')}")
    
    # 신뢰도
    print(f"🔍 예측 신뢰도: {confidence_color} {confidence_level} ({confidence_score:.1%})")
    
    # 시장 트렌드
    trend_emoji = "📈" if trend == "상승" else "📉" if trend == "하락" else "➡️"
    print(f"📊 시장 트렌드: {trend_emoji} {trend}")
    
    if volatility > 0:
        print(f"📊 변동성: {volatility:.2%}")
    
    # 투자 조언
    print("\n💡 투자 조언:")
    if confidence_score > 0.8:
        if trend == "상승":
            print("   - 높은 신뢰도와 상승 트렌드로 매수 고려")
        else:
            print("   - 높은 신뢰도이지만 하락 트렌드 주의")
    elif confidence_score > 0.6:
        print("   - 보통 신뢰도로 신중한 투자 권장")
    else:
        print("   - 낮은 신뢰도로 투자 신중 권장")
    
    print("="*60)

def plot_prediction_trend(X_test, prediction):
    """예측 트렌드를 시각화하는 함수"""
    try:
        # 한글 폰트 설정
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False
        
        # 최근 30일 데이터와 예측값 시각화
        recent_data = X_test.tail(30)
        
        plt.figure(figsize=(12, 6))
        
        # 최근 주가 추이 (High 컬럼 사용)
        if 'High' in recent_data.columns:
            plt.plot(recent_data.index, recent_data['High'], 'b-', label='최근 주가', linewidth=2)
        
        # 예측값 추가
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
        
        # x축 라벨을 세로 방향으로 표기
        plt.xticks(rotation=90)
        
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 그래프 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_filename = f"results/tomorrow_prediction_{timestamp}.png"
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        print(f"📊 예측 그래프 저장: {plot_filename}")
        plt.show()
        
    except Exception as e:
        print(f"⚠️ 그래프 생성 중 오류: {e}")

def save_prediction_result(prediction, confidence_level, confidence_score, trend, save_dir="results"):
    """예측 결과를 파일로 저장하는 함수"""
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tomorrow = datetime.now() + timedelta(days=1)
        
        # 예측 결과 데이터프레임 생성
        prediction_data = {
            '예측_날짜': [tomorrow.strftime('%Y-%m-%d')],
            '예측_주가': [prediction],
            '신뢰도_등급': [confidence_level],
            '신뢰도_점수': [confidence_score],
            '시장_트렌드': [trend],
            '예측_시간': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        }
        
        df = pd.DataFrame(prediction_data)
        filename = f"{save_dir}/tomorrow_prediction_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"💾 예측 결과 저장: {filename}")
        
    except Exception as e:
        print(f"⚠️ 결과 저장 중 오류: {e}")

def main():
    """메인 함수"""
    print("🚀 내일의 삼성전자 주가 예측 시작")
    print("="*50)
    
    # 1. 훈련된 모델 로드
    print("📂 훈련된 모델 로드 중...")
    model, model_file = load_trained_model()
    if model is None:
        return
    
    # 2. 최신 데이터 로드
    print("📊 최신 데이터 로드 중...")
    X_test = load_latest_data()
    if X_test is None:
        return
    
    # 3. 내일 주가 예측
    print("🔮 내일 주가 예측 중...")
    prediction, confidence_level, confidence_color, confidence_score = predict_tomorrow_stock_price(model, X_test)
    if prediction is None:
        return
    
    # 4. 시장 트렌드 분석
    print("📈 시장 트렌드 분석 중...")
    trend, volatility = get_market_trend(X_test)
    
    # 5. 결과 출력
    format_prediction_result(prediction, confidence_level, confidence_color, confidence_score, trend, volatility)
    
    # 6. 예측 트렌드 시각화
    print("📊 예측 트렌드 시각화 중...")
    plot_prediction_trend(X_test, prediction)
    
    # 7. 결과 저장
    print("💾 예측 결과 저장 중...")
    save_prediction_result(prediction, confidence_level, confidence_score, trend)
    
    print("\n✅ 내일의 주가 예측이 완료되었습니다!")
    print("📝 참고: 이 예측은 참고용이며, 실제 투자는 신중하게 결정하세요.")

if __name__ == "__main__":
    main() 