import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler

def load_model_and_scaler():
    """
    훈련된 모델과 스케일러 로드
    """
    try:
        # 모델 로드
        with open('models/seoul_housing_model_20250805_201554.pkl', 'rb') as f:
            model = pickle.load(f)
        
        # 스케일러 학습을 위한 데이터 로드
        X_train = pd.read_csv('processed_data/X_train.csv')
        scaler = StandardScaler()
        scaler.fit(X_train)
        
        print("✓ 모델과 스케일러 로드 완료")
        return model, scaler
        
    except Exception as e:
        print(f"❌ 모델 로드 실패: {e}")
        return None, None

def predict_house_price(property_type, floor, area, build_year, district=1, city=0):
    """
    집값 예측 함수
    
    Args:
        property_type: 건물 유형 (0: 오피스텔, 1: 아파트, 2: 빌라)
        floor: 층수
        area: 면적(㎡)
        build_year: 건축년도
        district: 법정동 (기본값: 1)
        city: 시군구 (기본값: 0)
    
    Returns:
        예측된 집값 (만원)
    """
    # 모델과 스케일러 로드
    model, scaler = load_model_and_scaler()
    if model is None or scaler is None:
        return None
    
    # 입력 데이터 생성
    input_data = pd.DataFrame({
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
    
    # 데이터 스케일링
    input_scaled = scaler.transform(input_data)
    
    # 예측
    predicted_price = model.predict(input_scaled)[0]
    
    return predicted_price

def main():
    """간단한 집값 예측 예제"""
    print("🏠 서울 집값 예측 (간단 버전)")
    print("="*40)
    
    # 예시 1: 아파트
    print("\n📊 예시 1: 아파트")
    price1 = predict_house_price(
        property_type=1,  # 아파트
        floor=15,         # 15층
        area=85.0,        # 85㎡
        build_year=2012   # 2012년 건축
    )
    if price1:
        print(f"   예측 집값: {price1:,.0f}만원")
    
    # 예시 2: 오피스텔
    print("\n📊 예시 2: 오피스텔")
    price2 = predict_house_price(
        property_type=0,  # 오피스텔
        floor=3,          # 3층
        area=35.0,        # 35㎡
        build_year=2008   # 2008년 건축
    )
    if price2:
        print(f"   예측 집값: {price2:,.0f}만원")
    
    # 예시 3: 빌라
    print("\n📊 예시 3: 빌라")
    price3 = predict_house_price(
        property_type=2,  # 빌라
        floor=8,          # 8층
        area=60.0,        # 60㎡
        build_year=2016   # 2016년 건축
    )
    if price3:
        print(f"   예측 집값: {price3:,.0f}만원")
    
    # 사용자 입력 받기
    print(f"\n{'='*40}")
    print("🔍 직접 예측해보기")
    print("부동산 정보를 입력해주세요:")
    
    try:
        property_type = int(input("건물 유형 (0: 오피스텔, 1: 아파트, 2: 빌라): "))
        floor = int(input("층수: "))
        area = float(input("면적(㎡): "))
        build_year = int(input("건축년도: "))
        
        # 예측 수행
        predicted_price = predict_house_price(property_type, floor, area, build_year)
        
        if predicted_price:
            print(f"\n💰 예측 결과:")
            print(f"   예측 집값: {predicted_price:,.0f}만원")
            
            # 가격대 분류
            if predicted_price < 50000:
                category = "저가"
            elif predicted_price < 100000:
                category = "중가"
            else:
                category = "고가"
            
            print(f"   가격대: {category}")
        else:
            print("❌ 예측에 실패했습니다.")
            
    except ValueError:
        print("❌ 잘못된 입력입니다. 숫자로 입력해주세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main() 