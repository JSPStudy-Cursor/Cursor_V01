from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
from linear_regression_model import SeoulHousingPricePredictor

app = Flask(__name__)

# 전역 변수로 예측기 저장
predictor = None

def load_trained_model(model_path):
    """
    훈련된 모델 로드
    
    Args:
        model_path: 모델 파일 경로
    
    Returns:
        로드된 모델과 스케일러
    """
    try:
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        print(f"✓ 모델 로드 완료: {model_path}")
        return model_data
    except Exception as e:
        print(f"❌ 모델 로드 실패: {e}")
        return None

def initialize_predictor():
    """
    예측기 초기화 및 모델 로드
    """
    global predictor
    
    print("=== 집값 예측 모델 초기화 ===")
    
    # 모델 파일 경로 (가장 최근 파일 사용)
    models_dir = "models"
    if os.path.exists(models_dir):
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.pkl')]
        if model_files:
            # 가장 최근 파일 선택
            model_files.sort(reverse=True)
            model_path = os.path.join(models_dir, model_files[0])
        else:
            print("❌ 훈련된 모델 파일을 찾을 수 없습니다.")
            return False
    else:
        print("❌ models 디렉토리가 없습니다.")
        return False
    
    # 모델 로드
    model_data = load_trained_model(model_path)
    if model_data is None:
        print("❌ 훈련된 모델을 찾을 수 없습니다.")
        return False
    
    # 새로운 모델 인스턴스 생성
    predictor = SeoulHousingPricePredictor()
    
    try:
        # 데이터 로드 (스케일러 학습을 위해)
        predictor.load_data()
        
        # 데이터 전처리 (스케일러 학습)
        predictor.preprocess_data()
        
        # 훈련된 모델과 스케일러로 교체
        predictor.model = model_data['model']
        predictor.scaler = model_data['scaler']
        predictor.is_trained = model_data['is_trained']
        
        print("✓ 모델 준비 완료")
        return True
        
    except Exception as e:
        print(f"❌ 모델 준비 중 오류 발생: {e}")
        return False

def predict_house_price(input_data):
    """
    입력 데이터로 집값 예측
    
    Args:
        input_data: 사용자 입력 데이터 딕셔너리
    
    Returns:
        예측 결과 딕셔너리
    """
    global predictor
    
    if predictor is None:
        return {"error": "모델이 초기화되지 않았습니다."}
    
    try:
        # 입력 데이터를 DataFrame으로 변환
        prediction_data = pd.DataFrame([input_data])
        
        # 예측 수행
        predictions = predictor.predict_new_data(prediction_data)
        
        if predictions is not None and len(predictions) > 0:
            predicted_price = predictions[0]
            
            # 가격대별 분류
            if predicted_price < 50000:
                price_category = "저가"
            elif predicted_price < 100000:
                price_category = "중가"
            else:
                price_category = "고가"
            
            # 건물 유형 매핑
            property_types = {0: "오피스텔", 1: "아파트", 2: "빌라"}
            property_type_name = property_types.get(input_data['property_type_encoded'], "기타")
            
            return {
                "success": True,
                "predicted_price": int(predicted_price),
                "price_category": price_category,
                "property_type_name": property_type_name,
                "formatted_price": f"{predicted_price:,.0f}만원"
            }
        else:
            return {"error": "예측에 실패했습니다."}
            
    except Exception as e:
        return {"error": f"예측 중 오류 발생: {str(e)}"}

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """집값 예측 API 엔드포인트"""
    try:
        # 폼 데이터 받기
        data = {
            'property_type_encoded': int(request.form.get('property_type', 1)),
            '층': int(request.form.get('floor', 10)),
            '면적': float(request.form.get('area', 60.0)),
            '건축년도': int(request.form.get('build_year', 2010)),
            '법정동_encoded': int(request.form.get('district', 1)),
            '시군구_encoded': int(request.form.get('city', 0)),
            '거래유형_encoded': 0,  # 기본값
            '거래년도': 2024,  # 현재 년도
            '거래월': 6,  # 기본값
            '거래일': 15  # 기본값
        }
        
        # 예측 수행
        result = predict_house_price(data)
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "predicted_price": result["predicted_price"],
                "formatted_price": result["formatted_price"],
                "price_category": result["price_category"],
                "property_type_name": result["property_type_name"],
                "input_data": data
            })
        else:
            return jsonify({"success": False, "error": result.get("error", "예측 실패")})
            
    except Exception as e:
        return jsonify({"success": False, "error": f"서버 오류: {str(e)}"})

@app.route('/sample_predictions')
def sample_predictions():
    """샘플 예측 결과 페이지"""
    return render_template('sample_predictions.html')

@app.route('/get_sample_predictions')
def get_sample_predictions():
    """샘플 데이터로 예측 결과 반환"""
    global predictor
    
    if predictor is None:
        return jsonify({"error": "모델이 초기화되지 않았습니다."})
    
    try:
        # 샘플 데이터 생성
        sample_data = pd.DataFrame({
            'property_type_encoded': [1, 0, 2, 1, 0, 1, 2, 0],  # 아파트, 오피스텔, 빌라
            '층': [15, 3, 8, 20, 5, 12, 6, 25],  # 층수
            '면적': [85.0, 35.0, 60.0, 95.0, 40.0, 120.0, 45.0, 30.0],  # 면적
            '건축년도': [2012, 2008, 2016, 2010, 2006, 2018, 2014, 2004],  # 건축년도
            '법정동_encoded': [1, 2, 0, 1, 2, 0, 1, 2],  # 법정동
            '시군구_encoded': [0, 1, 2, 0, 1, 2, 0, 1],  # 시군구
            '거래유형_encoded': [0, 0, 0, 0, 0, 0, 0, 0],  # 거래유형
            '거래년도': [2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024],  # 거래년도
            '거래월': [6, 6, 6, 6, 6, 6, 6, 6],  # 거래월
            '거래일': [15, 15, 15, 15, 15, 15, 15, 15]  # 거래일
        })
        
        # 예측 수행
        predictions = predictor.predict_new_data(sample_data)
        
        if predictions is not None:
            property_types = {0: "오피스텔", 1: "아파트", 2: "빌라"}
            results = []
            
            for i, (_, row) in enumerate(sample_data.iterrows()):
                predicted_price = predictions[i]
                
                # 가격대별 분류
                if predicted_price < 50000:
                    price_category = "저가"
                elif predicted_price < 100000:
                    price_category = "중가"
                else:
                    price_category = "고가"
                
                results.append({
                    "sample_id": i + 1,
                    "property_type": property_types.get(row['property_type_encoded'], "기타"),
                    "floor": int(row['층']),
                    "area": float(row['면적']),
                    "build_year": int(row['건축년도']),
                    "predicted_price": int(predicted_price),
                    "formatted_price": f"{predicted_price:,.0f}만원",
                    "price_category": price_category
                })
            
            return jsonify({"success": True, "results": results})
        else:
            return jsonify({"error": "예측에 실패했습니다."})
            
    except Exception as e:
        return jsonify({"error": f"샘플 예측 중 오류 발생: {str(e)}"})

if __name__ == '__main__':
    # 모델 초기화
    if initialize_predictor():
        print("✓ Flask 서버 시작 준비 완료")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ 모델 초기화 실패로 서버를 시작할 수 없습니다.") 