import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os
from datetime import datetime

def load_stock_data(filename="samsung_stock_5years.csv"):
    """
    CSV 파일에서 주가 데이터를 로드하는 함수
    """
    try:
        # CSV 파일 읽기
        stock_data = pd.read_csv(filename, index_col=0, parse_dates=True)
        print(f"데이터 로드 완료: {len(stock_data)}개 행, {len(stock_data.columns)}개 컬럼")
        return stock_data
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {filename}")
        return None
    except Exception as error:
        print(f"데이터 로드 중 오류 발생: {error}")
        return None

def check_missing_data(stock_data):
    """
    누락된 데이터를 확인하고 정보를 출력하는 함수
    """
    print("\n=== 누락된 데이터 확인 ===")
    
    # 각 컬럼별 누락된 데이터 개수
    missing_counts = stock_data.isnull().sum()
    print("컬럼별 누락된 데이터 개수:")
    for column, count in missing_counts.items():
        if count > 0:
            print(f"  {column}: {count}개 ({count/len(stock_data)*100:.2f}%)")
        else:
            print(f"  {column}: 0개")
    
    # 전체 누락된 데이터 비율
    total_missing = stock_data.isnull().sum().sum()
    total_cells = stock_data.size
    missing_percentage = (total_missing / total_cells) * 100
    
    print(f"\n전체 누락된 데이터: {total_missing}개 ({missing_percentage:.2f}%)")
    
    return missing_counts

def remove_missing_data(stock_data):
    """
    누락된 데이터가 있는 행을 제거하는 함수
    """
    print("\n=== 누락된 데이터 제거 ===")
    
    # 제거 전 데이터 개수
    original_count = len(stock_data)
    print(f"제거 전 데이터 개수: {original_count}개")
    
    # 누락된 데이터가 있는 행 제거
    cleaned_data = stock_data.dropna()
    
    # 제거 후 데이터 개수
    cleaned_count = len(cleaned_data)
    removed_count = original_count - cleaned_count
    
    print(f"제거 후 데이터 개수: {cleaned_count}개")
    print(f"제거된 행 개수: {removed_count}개 ({removed_count/original_count*100:.2f}%)")
    
    return cleaned_data

def create_features(stock_data):
    """
    주가 데이터에서 추가 특성(feature)을 생성하는 함수
    """
    print("\n=== 특성 생성 ===")
    
    # 기술적 지표 계산
    features_data = stock_data.copy()
    
    # 1. 일일 수익률 (Daily Return)
    features_data['Daily_Return'] = features_data['Close'].pct_change()
    
    # 2. 이동평균 (Moving Averages)
    features_data['MA_5'] = features_data['Close'].rolling(window=5).mean()
    features_data['MA_20'] = features_data['Close'].rolling(window=20).mean()
    features_data['MA_60'] = features_data['Close'].rolling(window=60).mean()
    
    # 3. 가격 변동성 (Volatility)
    features_data['Volatility'] = features_data['Daily_Return'].rolling(window=20).std()
    
    # 4. 거래량 이동평균
    features_data['Volume_MA_5'] = features_data['Volume'].rolling(window=5).mean()
    
    # 5. 고가-저가 비율
    features_data['High_Low_Ratio'] = features_data['High'] / features_data['Low']
    
    # 6. 시가-종가 비율
    features_data['Open_Close_Ratio'] = features_data['Open'] / features_data['Close']
    
    # 7. 거래량 변화율
    features_data['Volume_Change'] = features_data['Volume'].pct_change()
    
    # 누락된 데이터가 있는 행 제거 (새로 생성된 특성으로 인한 NaN 값들)
    features_data = features_data.dropna()
    
    print(f"특성 생성 완료: {len(features_data.columns)}개 컬럼")
    print(f"최종 데이터 개수: {len(features_data)}개")
    
    return features_data

def split_train_test_data(stock_data, test_size=0.2, random_state=42):
    """
    데이터를 훈련용과 테스트용으로 나누는 함수
    """
    print(f"\n=== 데이터 분할 (테스트 비율: {test_size*100}%) ===")
    
    # 특성(X)과 타겟(y) 분리
    # 타겟은 다음날의 종가로 설정
    X = stock_data.drop(['Close'], axis=1)  # 종가를 제외한 모든 특성
    y = stock_data['Close']  # 종가를 타겟으로 설정
    
    # 시간 순서를 유지하면서 분할 (시계열 데이터이므로)
    split_index = int(len(stock_data) * (1 - test_size))
    
    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]
    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]
    
    print(f"훈련 데이터: {len(X_train)}개 ({len(X_train)/len(stock_data)*100:.1f}%)")
    print(f"테스트 데이터: {len(X_test)}개 ({len(X_test)/len(stock_data)*100:.1f}%)")
    
    return X_train, X_test, y_train, y_test

def save_split_data(X_train, X_test, y_train, y_test, output_dir="processed_data"):
    """
    분할된 데이터를 CSV 파일로 저장하는 함수
    """
    print(f"\n=== 데이터 저장 ===")
    
    # 출력 디렉토리 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"디렉토리 생성: {output_dir}")
    
    # 파일명에 현재 시간 추가
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 데이터 저장
    X_train.to_csv(f"{output_dir}/X_train_{timestamp}.csv")
    X_test.to_csv(f"{output_dir}/X_test_{timestamp}.csv")
    y_train.to_csv(f"{output_dir}/y_train_{timestamp}.csv")
    y_test.to_csv(f"{output_dir}/y_test_{timestamp}.csv")
    
    print(f"데이터가 '{output_dir}' 폴더에 저장되었습니다:")
    print(f"  - X_train_{timestamp}.csv")
    print(f"  - X_test_{timestamp}.csv")
    print(f"  - y_train_{timestamp}.csv")
    print(f"  - y_test_{timestamp}.csv")

def display_data_summary(X_train, X_test, y_train, y_test):
    """
    분할된 데이터의 요약 정보를 출력하는 함수
    """
    print("\n=== 데이터 요약 ===")
    
    print("훈련 데이터:")
    print(f"  특성 개수: {X_train.shape[1]}")
    print(f"  샘플 개수: {X_train.shape[0]}")
    print(f"  타겟 범위: {y_train.min():.2f} ~ {y_train.max():.2f}")
    
    print("\n테스트 데이터:")
    print(f"  특성 개수: {X_test.shape[1]}")
    print(f"  샘플 개수: {X_test.shape[0]}")
    print(f"  타겟 범위: {y_test.min():.2f} ~ {y_test.max():.2f}")
    
    print(f"\n특성 목록:")
    for i, feature in enumerate(X_train.columns, 1):
        print(f"  {i:2d}. {feature}")

def main():
    """
    메인 실행 함수
    """
    print("=== 주가 데이터 전처리 및 분할 ===")
    
    # 1. 데이터 로드
    stock_data = load_stock_data()
    if stock_data is None:
        return
    
    # 2. 누락된 데이터 확인
    missing_counts = check_missing_data(stock_data)
    
    # 3. 누락된 데이터 제거
    cleaned_data = remove_missing_data(stock_data)
    
    # 4. 특성 생성
    features_data = create_features(cleaned_data)
    
    # 5. 데이터 분할
    X_train, X_test, y_train, y_test = split_train_test_data(features_data)
    
    # 6. 데이터 요약 출력
    display_data_summary(X_train, X_test, y_train, y_test)
    
    # 7. 분할된 데이터 저장
    save_split_data(X_train, X_test, y_train, y_test)
    
    print("\n=== 전처리 완료 ===")

if __name__ == "__main__":
    main() 