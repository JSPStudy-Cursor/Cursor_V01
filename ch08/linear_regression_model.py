import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pickle
import os
from datetime import datetime

class SeoulHousingPricePredictor:
    """서울 집값 예측을 위한 선형 회귀 모델 클래스"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # 기본 가격 기준 (만원 단위)
        self.base_prices = {
            '아파트': 80000,    # 아파트 기본 가격
            '오피스텔': 60000,   # 오피스텔 기본 가격
            '빌라/연립': 40000   # 빌라/연립 기본 가격
        }
        
        # 지역별 가격 계수
        self.location_factors = {
            '강남구': 1.3,      # 강남구는 가격이 높음
            '서초구': 1.2,      # 서초구도 가격이 높음
            '마포구': 1.0       # 마포구는 기준 가격
        }
        
        # 법정동별 가격 계수
        self.district_factors = {
            '역삼동': 1.4,      # 역삼동은 매우 높음
            '서초동': 1.3,      # 서초동도 높음
            '합정동': 1.0       # 합정동은 기준
        }
    
    def load_data(self, x_train_path=None, y_train_path=None, x_test_path=None, y_test_path=None):
        """데이터 로드 (더미 데이터 생성)"""
        print("더미 데이터를 생성합니다...")
        
        # 더미 데이터 생성
        np.random.seed(42)
        n_samples = 1000
        
        # 부동산 유형 (0: 오피스텔, 1: 아파트, 2: 빌라/연립)
        property_types = np.random.choice([0, 1, 2], n_samples, p=[0.3, 0.5, 0.2])
        
        # 층수 (1-30층)
        floors = np.random.randint(1, 31, n_samples)
        
        # 면적 (20-150㎡)
        areas = np.random.uniform(20, 150, n_samples)
        
        # 건축년도 (1980-2020)
        build_years = np.random.randint(1980, 2021, n_samples)
        
        # 법정동 (0: 합정동, 1: 역삼동, 2: 서초동)
        districts = np.random.choice([0, 1, 2], n_samples, p=[0.3, 0.4, 0.3])
        
        # 시군구 (0: 강남구, 1: 서초구, 2: 마포구)
        cities = np.random.choice([0, 1, 2], n_samples, p=[0.4, 0.3, 0.3])
        
        # 거래유형 (0: 매매)
        trade_types = np.zeros(n_samples)
        
        # 거래년도 (2020-2024)
        trade_years = np.random.randint(2020, 2025, n_samples)
        trade_months = np.random.randint(1, 13, n_samples)
        trade_days = np.random.randint(1, 29, n_samples)
        
        # 특성 데이터 생성
        self.X = pd.DataFrame({
            'property_type_encoded': property_types,
            '층': floors,
            '면적': areas,
            '건축년도': build_years,
            '법정동_encoded': districts,
            '시군구_encoded': cities,
            '거래유형_encoded': trade_types,
            '거래년도': trade_years,
            '거래월': trade_months,
            '거래일': trade_days
        })
        
        # 가격 생성 (더미 로직)
        self.y = self._generate_dummy_prices(self.X)
        
        print(f"데이터 로드 완료: {len(self.X)}개 샘플")
        return True
    
    def _generate_dummy_prices(self, X):
        """더미 가격 생성"""
        prices = []
        
        for _, row in X.iterrows():
            # 기본 가격
            property_type = row['property_type_encoded']
            if property_type == 0:  # 오피스텔
                base_price = self.base_prices['오피스텔']
            elif property_type == 1:  # 아파트
                base_price = self.base_prices['아파트']
            else:  # 빌라/연립
                base_price = self.base_prices['빌라/연립']
            
            # 면적 계수 (면적이 클수록 가격이 높음)
            area_factor = row['면적'] / 60.0  # 60㎡ 기준
            
            # 층수 계수 (중간층이 가장 높음)
            floor_factor = 1.0 + 0.1 * np.sin((row['층'] - 15) / 15 * np.pi)
            
            # 건축년도 계수 (최신일수록 가격이 높음)
            year_factor = 1.0 + (row['건축년도'] - 2000) * 0.02
            
            # 지역 계수
            city_factor = 1.0
            if row['시군구_encoded'] == 0:  # 강남구
                city_factor = self.location_factors['강남구']
            elif row['시군구_encoded'] == 1:  # 서초구
                city_factor = self.location_factors['서초구']
            
            # 법정동 계수
            district_factor = 1.0
            if row['법정동_encoded'] == 1:  # 역삼동
                district_factor = self.district_factors['역삼동']
            elif row['법정동_encoded'] == 2:  # 서초동
                district_factor = self.district_factors['서초동']
            
            # 최종 가격 계산
            price = base_price * area_factor * floor_factor * year_factor * city_factor * district_factor
            
            # 랜덤 변동 추가 (±10%)
            price *= (1 + np.random.uniform(-0.1, 0.1))
            
            prices.append(max(price, 20000))  # 최소 2억원
        
        return np.array(prices)
    
    def preprocess_data(self):
        """데이터 전처리"""
        print("데이터 전처리를 수행합니다...")
        
        # 특성 스케일링
        self.X_scaled = self.scaler.fit_transform(self.X)
        
        # 훈련/테스트 분할
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X_scaled, self.y, test_size=0.2, random_state=42
        )
        
        print("데이터 전처리 완료")
        return True
    
    def train_model(self):
        """모델 훈련"""
        print("선형 회귀 모델을 훈련합니다...")
        
        # 선형 회귀 모델 생성
        self.model = LinearRegression()
        
        # 모델 훈련
        self.model.fit(self.X_train, self.y_train)
        
        # 훈련 성능 평가
        train_score = self.model.score(self.X_train, self.y_train)
        test_score = self.model.score(self.X_test, self.y_test)
        
        print(f"훈련 성능 (R²): {train_score:.4f}")
        print(f"테스트 성능 (R²): {test_score:.4f}")
        
        self.is_trained = True
        return True
    
    def predict_new_data(self, new_data):
        """새로운 데이터에 대한 예측"""
        if not self.is_trained:
            print("모델이 훈련되지 않았습니다.")
            return None
        
        try:
            # 데이터 전처리
            if isinstance(new_data, pd.DataFrame):
                # 필요한 컬럼이 있는지 확인
                required_columns = [
                    'property_type_encoded', '층', '면적', '건축년도',
                    '법정동_encoded', '시군구_encoded', '거래유형_encoded',
                    '거래년도', '거래월', '거래일'
                ]
                
                for col in required_columns:
                    if col not in new_data.columns:
                        print(f"필수 컬럼이 없습니다: {col}")
                        return None
                
                # 스케일링
                new_data_scaled = self.scaler.transform(new_data)
                
                # 예측
                predictions = self.model.predict(new_data_scaled)
                
                return predictions
            else:
                print("입력 데이터가 DataFrame이 아닙니다.")
                return None
                
        except Exception as e:
            print(f"예측 중 오류 발생: {e}")
            return None
    
    def save_model(self, model_path=None):
        """모델 저장"""
        if not self.is_trained:
            print("훈련된 모델이 없습니다.")
            return False
        
        if model_path is None:
            # 모델 저장 디렉토리 생성
            os.makedirs('models', exist_ok=True)
            
            # 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_path = f"models/seoul_housing_model_{timestamp}.pkl"
        
        try:
            # 모델과 스케일러를 함께 저장
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"모델이 저장되었습니다: {model_path}")
            return True
            
        except Exception as e:
            print(f"모델 저장 중 오류 발생: {e}")
            return False
    
    def load_model(self, model_path):
        """모델 로드"""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.is_trained = model_data['is_trained']
            
            print(f"모델이 로드되었습니다: {model_path}")
            return True
            
        except Exception as e:
            print(f"모델 로드 중 오류 발생: {e}")
            return False
    
    def evaluate_model(self):
        """모델 평가"""
        if not self.is_trained:
            print("훈련된 모델이 없습니다.")
            return None
        
        # 테스트 데이터로 예측
        y_pred = self.model.predict(self.X_test)
        
        # 성능 지표 계산
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        mse = mean_squared_error(self.y_test, y_pred)
        mae = mean_absolute_error(self.y_test, y_pred)
        r2 = r2_score(self.y_test, y_pred)
        
        print("=== 모델 성능 평가 ===")
        print(f"Mean Squared Error: {mse:.2f}")
        print(f"Mean Absolute Error: {mae:.2f}")
        print(f"R² Score: {r2:.4f}")
        
        return {
            'mse': mse,
            'mae': mae,
            'r2': r2
        }


def main():
    """메인 함수 - 모델 훈련 및 저장"""
    print("=== 서울 집값 예측 모델 훈련 ===")
    
    # 예측기 생성
    predictor = SeoulHousingPricePredictor()
    
    # 데이터 로드
    if not predictor.load_data():
        print("데이터 로드에 실패했습니다.")
        return
    
    # 데이터 전처리
    if not predictor.preprocess_data():
        print("데이터 전처리에 실패했습니다.")
        return
    
    # 모델 훈련
    if not predictor.train_model():
        print("모델 훈련에 실패했습니다.")
        return
    
    # 모델 평가
    predictor.evaluate_model()
    
    # 모델 저장
    if predictor.save_model():
        print("모델 훈련 및 저장이 완료되었습니다.")
    else:
        print("모델 저장에 실패했습니다.")


if __name__ == "__main__":
    main()