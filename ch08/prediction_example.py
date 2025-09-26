import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
from linear_regression_model import SeoulHousingPricePredictor

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
            model = pickle.load(f)
        print(f"✓ 모델 로드 완료: {model_path}")
        return model
    except Exception as e:
        print(f"❌ 모델 로드 실패: {e}")
        return None

def create_sample_data():
    """
    예측용 샘플 데이터 생성
    다양한 시나리오의 부동산 데이터를 포함
    """
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
    
    return sample_data

def create_custom_data():
    """
    사용자 정의 데이터 생성 함수
    실제 부동산 거래 상황을 반영한 데이터
    """
    print("\n=== 사용자 정의 데이터 생성 ===")
    
    # 사용자 입력 받기
    print("부동산 정보를 입력해주세요:")
    
    property_type = input("건물 유형 (1: 아파트, 0: 오피스텔, 2: 빌라): ")
    floor = input("층수: ")
    area = input("면적(㎡): ")
    build_year = input("건축년도: ")
    district = input("법정동 (0-2): ")
    city = input("시군구 (0-2): ")
    
    # 기본값 설정
    property_type = int(property_type) if property_type else 1
    floor = int(floor) if floor else 10
    area = float(area) if area else 60.0
    build_year = int(build_year) if build_year else 2010
    district = int(district) if district else 1
    city = int(city) if city else 0
    
    custom_data = pd.DataFrame({
        'property_type_encoded': [property_type],
        '층': [floor],
        '면적': [area],
        '건축년도': [build_year],
        '법정동_encoded': [district],
        '시군구_encoded': [city],
        '거래유형_encoded': [0],
        '거래년도': [2024],
        '거래월': [6],
        '거래일': [15]
    })
    
    return custom_data

def predict_with_trained_model():
    """
    훈련된 모델을 사용하여 집값 예측
    """
    print("=== 훈련된 모델로 집값 예측 ===")
    
    # 모델 파일 경로
    model_path = "models/seoul_housing_model_20250805_201554.pkl"
    
    # 모델 로드
    trained_model = load_trained_model(model_path)
    if trained_model is None:
        print("❌ 훈련된 모델을 찾을 수 없습니다.")
        return
    
    # 새로운 모델 인스턴스 생성 (스케일러 등이 필요)
    predictor = SeoulHousingPricePredictor()
    
    try:
        # 데이터 로드 (스케일러 학습을 위해)
        predictor.load_data(
            x_train_path='processed_data/X_train.csv',
            y_train_path='processed_data/y_train.csv',
            x_test_path='processed_data/X_test.csv',
            y_test_path='processed_data/y_test.csv'
        )
        
        # 데이터 전처리 (스케일러 학습)
        predictor.preprocess_data()
        
        # 훈련된 모델로 교체
        predictor.model = trained_model
        predictor.is_trained = True
        
        print("✓ 모델 준비 완료")
        
        return predictor
        
    except Exception as e:
        print(f"❌ 모델 준비 중 오류 발생: {e}")
        return None

def display_prediction_results(predictor, new_data, predictions):
    """
    예측 결과를 보기 좋게 출력
    """
    print(f"\n{'='*50}")
    print("🏠 집값 예측 결과")
    print(f"{'='*50}")
    
    property_types = {0: "오피스텔", 1: "아파트", 2: "빌라"}
    
    for i, (_, row) in enumerate(new_data.iterrows()):
        predicted_price = predictions[i]
        
        print(f"\n📊 샘플 {i+1}:")
        print(f"   🏢 건물 유형: {property_types.get(row['property_type_encoded'], '기타')}")
        print(f"   🏢 층수: {row['층']}층")
        print(f"   📐 면적: {row['면적']}㎡")
        print(f"   🏗️  건축년도: {row['건축년도']}년")
        print(f"   💰 예측 집값: {predicted_price:,.0f}만원")
        
        # 가격대별 분류
        if predicted_price < 50000:
            price_category = "저가"
        elif predicted_price < 100000:
            price_category = "중가"
        else:
            price_category = "고가"
        
        print(f"   📈 가격대: {price_category}")
    
    # 전체 통계
    print(f"\n📈 예측 결과 통계:")
    print(f"   평균 예측 집값: {np.mean(predictions):,.0f}만원")
    print(f"   최소 예측 집값: {np.min(predictions):,.0f}만원")
    print(f"   최대 예측 집값: {np.max(predictions):,.0f}만원")
    print(f"   표준편차: {np.std(predictions):,.0f}만원")

def save_prediction_results(new_data, predictions, save_dir="results"):
    """
    예측 결과를 파일로 저장
    """
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 예측 결과 데이터프레임 생성
        results_df = new_data.copy()
        results_df['예측_집값'] = predictions
        
        # 파일 저장
        filename = f"{save_dir}/new_predictions_{timestamp}.csv"
        results_df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"\n💾 예측 결과 저장: {filename}")
        
    except Exception as e:
        print(f"❌ 결과 저장 실패: {e}")

def main():
    """메인 실행 함수"""
    print("🏠 서울 집값 예측 시스템")
    print("="*50)
    
    # 훈련된 모델로 예측기 준비
    predictor = predict_with_trained_model()
    if predictor is None:
        return
    
    while True:
        print(f"\n{'='*50}")
        print("📋 예측 옵션 선택:")
        print("1. 샘플 데이터로 예측")
        print("2. 사용자 정의 데이터로 예측")
        print("3. 종료")
        print(f"{'='*50}")
        
        choice = input("선택하세요 (1-3): ").strip()
        
        if choice == "1":
            # 샘플 데이터로 예측
            new_data = create_sample_data()
            print(f"\n📊 {len(new_data)}개의 샘플 데이터로 예측을 시작합니다...")
            
        elif choice == "2":
            # 사용자 정의 데이터로 예측
            new_data = create_custom_data()
            print(f"\n📊 사용자 정의 데이터로 예측을 시작합니다...")
            
        elif choice == "3":
            print("👋 프로그램을 종료합니다.")
            break
            
        else:
            print("❌ 잘못된 선택입니다. 다시 선택해주세요.")
            continue
        
        try:
            # 예측 수행
            predictions = predictor.predict_new_data(new_data)
            
            if predictions is not None:
                # 결과 출력
                display_prediction_results(predictor, new_data, predictions)
                
                # 결과 저장 여부 확인
                save_choice = input("\n💾 예측 결과를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
                if save_choice in ['y', 'yes', '예']:
                    save_prediction_results(new_data, predictions)
                    
            else:
                print("❌ 예측에 실패했습니다.")
                
        except Exception as e:
            print(f"❌ 예측 중 오류 발생: {e}")

if __name__ == "__main__":
    main() 