import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

def load_and_clean_data(file_path):
    """
    CSV 파일을 로드하고 누락된 데이터를 제거하는 함수
    
    Args:
        file_path (str): CSV 파일 경로
        
    Returns:
        pandas.DataFrame: 정제된 데이터프레임
    """
    try:
        # CSV 파일 로드
        print("데이터 로드 중...")
        df = pd.read_csv(file_path)
        print(f"원본 데이터 크기: {df.shape}")
        
        # 누락된 데이터 확인
        missing_data = df.isnull().sum()
        print("\n누락된 데이터 개수:")
        print(missing_data[missing_data > 0])
        
        # 누락된 데이터가 있는 행 제거
        df_cleaned = df.dropna()
        print(f"\n정제 후 데이터 크기: {df_cleaned.shape}")
        print(f"제거된 행 수: {len(df) - len(df_cleaned)}")
        
        return df_cleaned
        
    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다 - {file_path}")
        return None
    except Exception as e:
        print(f"오류: 데이터 로드 중 문제가 발생했습니다 - {e}")
        return None

def preprocess_data(df):
    """
    데이터 전처리를 수행하는 함수
    
    Args:
        df (pandas.DataFrame): 원본 데이터프레임
        
    Returns:
        tuple: 전처리된 특성(X)과 타겟(y)
    """
    try:
        # 거래금액에서 쉼표 제거하고 숫자로 변환
        df['거래금액'] = df['거래금액'].str.replace(',', '').astype(float)
        
        # 거래일자를 날짜 형식으로 변환
        df['거래일자'] = pd.to_datetime(df['거래일자'], format='%Y%m%d')
        
        # 건축년도를 숫자로 변환
        df['건축년도'] = pd.to_numeric(df['건축년도'], errors='coerce')
        
        # 층수를 숫자로 변환
        df['층'] = pd.to_numeric(df['층'], errors='coerce')
        
        # 면적을 숫자로 변환
        df['면적'] = pd.to_numeric(df['면적'], errors='coerce')
        
        # 범주형 변수들을 숫자로 인코딩
        categorical_columns = ['property_type', '건물명', '동', '지번', '법정동', '시군구', '거래유형']
        label_encoders = {}
        
        for column in categorical_columns:
            if column in df.columns:
                le = LabelEncoder()
                df[f'{column}_encoded'] = le.fit_transform(df[column].astype(str))
                label_encoders[column] = le
        
        # 특성 선택 (모델링에 사용할 컬럼들)
        feature_columns = [
            'property_type_encoded', '층', '면적', '건축년도',
            '법정동_encoded', '시군구_encoded', '거래유형_encoded'
        ]
        
        # 거래일자에서 년, 월, 일 추출
        df['거래년도'] = df['거래일자'].dt.year
        df['거래월'] = df['거래일자'].dt.month
        df['거래일'] = df['거래일자'].dt.day
        
        feature_columns.extend(['거래년도', '거래월', '거래일'])
        
        # 특성과 타겟 분리
        X = df[feature_columns]
        y = df['거래금액']
        
        print(f"특성 개수: {X.shape[1]}")
        print(f"샘플 개수: {X.shape[0]}")
        
        return X, y, label_encoders
        
    except Exception as e:
        print(f"오류: 데이터 전처리 중 문제가 발생했습니다 - {e}")
        return None, None, None

def split_train_test(X, y, test_size=0.2, random_state=42):
    """
    데이터를 훈련용과 테스트용으로 나누는 함수
    
    Args:
        X (pandas.DataFrame): 특성 데이터
        y (pandas.Series): 타겟 데이터
        test_size (float): 테스트 세트 비율 (기본값: 0.2)
        random_state (int): 랜덤 시드 (기본값: 42)
        
    Returns:
        tuple: 훈련용 특성, 테스트용 특성, 훈련용 타겟, 테스트용 타겟
    """
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=None
        )
        
        print(f"훈련 세트 크기: {X_train.shape[0]} ({X_train.shape[0]/len(X)*100:.1f}%)")
        print(f"테스트 세트 크기: {X_test.shape[0]} ({X_test.shape[0]/len(X)*100:.1f}%)")
        
        return X_train, X_test, y_train, y_test
        
    except Exception as e:
        print(f"오류: 데이터 분할 중 문제가 발생했습니다 - {e}")
        return None, None, None, None

def save_processed_data(X_train, X_test, y_train, y_test, output_dir='processed_data'):
    """
    전처리된 데이터를 파일로 저장하는 함수
    
    Args:
        X_train, X_test, y_train, y_test: 분할된 데이터
        output_dir (str): 저장할 디렉토리 경로
    """
    try:
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 훈련 데이터 저장
        X_train.to_csv(f'{output_dir}/X_train.csv', index=False)
        y_train.to_csv(f'{output_dir}/y_train.csv', index=False)
        
        # 테스트 데이터 저장
        X_test.to_csv(f'{output_dir}/X_test.csv', index=False)
        y_test.to_csv(f'{output_dir}/y_test.csv', index=False)
        
        print(f"\n전처리된 데이터가 '{output_dir}' 폴더에 저장되었습니다.")
        print("저장된 파일:")
        print("- X_train.csv (훈련용 특성)")
        print("- y_train.csv (훈련용 타겟)")
        print("- X_test.csv (테스트용 특성)")
        print("- y_test.csv (테스트용 타겟)")
        
    except Exception as e:
        print(f"오류: 데이터 저장 중 문제가 발생했습니다 - {e}")

def main():
    """
    메인 실행 함수
    """
    # 데이터 파일 경로
    data_file = 'housing_data/seoul_housing_price_20250805_124148.csv'
    
    print("=== 서울 집값 데이터 전처리 시작 ===")
    
    # 1. 데이터 로드 및 정제
    df_cleaned = load_and_clean_data(data_file)
    if df_cleaned is None:
        return
    
    # 2. 데이터 전처리
    X, y, label_encoders = preprocess_data(df_cleaned)
    if X is None or y is None:
        return
    
    # 3. 훈련/테스트 데이터 분할
    X_train, X_test, y_train, y_test = split_train_test(X, y)
    if X_train is None:
        return
    
    # 4. 전처리된 데이터 저장
    save_processed_data(X_train, X_test, y_train, y_test)
    
    print("\n=== 전처리 완료 ===")
    print(f"최종 훈련 세트: {X_train.shape[0]}개 샘플")
    print(f"최종 테스트 세트: {X_test.shape[0]}개 샘플")
    print(f"특성 개수: {X_train.shape[1]}개")

if __name__ == "__main__":
    main() 