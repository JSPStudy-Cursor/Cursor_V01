import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

def get_samsung_stock_data():
    """
    Yahoo Finance에서 삼성전자 주가 데이터를 가져오는 함수
    삼성전자의 Yahoo Finance 티커는 '005930.KS' (코스피)
    """
    try:
        # 삼성전자 티커 설정 (코스피)
        samsung_ticker = "005930.KS"
        
        # 현재 날짜
        end_date = datetime.now()
        # 5년 전 날짜 계산
        start_date = end_date - timedelta(days=5*365)
        
        print(f"삼성전자 주가 데이터를 가져오는 중...")
        print(f"시작일: {start_date.strftime('%Y-%m-%d')}")
        print(f"종료일: {end_date.strftime('%Y-%m-%d')}")
        
        # Yahoo Finance에서 데이터 가져오기
        samsung_stock = yf.Ticker(samsung_ticker)
        stock_data = samsung_stock.history(start=start_date, end=end_date)
        
        if stock_data.empty:
            print("데이터를 가져올 수 없습니다. 티커를 확인해주세요.")
            return None
            
        print(f"성공적으로 {len(stock_data)}개의 데이터를 가져왔습니다.")
        return stock_data
        
    except Exception as error:
        print(f"데이터 가져오기 중 오류 발생: {error}")
        return None

def save_to_csv(stock_data, filename="samsung_stock_5years.csv"):
    """
    주가 데이터를 CSV 파일로 저장하는 함수
    """
    try:
        if stock_data is None:
            print("저장할 데이터가 없습니다.")
            return False
            
        # CSV 파일로 저장
        stock_data.to_csv(filename, encoding='utf-8-sig')
        print(f"데이터가 '{filename}' 파일로 저장되었습니다.")
        
        # 저장된 파일 정보 출력
        file_size = os.path.getsize(filename)
        print(f"파일 크기: {file_size:,} bytes")
        
        return True
        
    except Exception as error:
        print(f"CSV 저장 중 오류 발생: {error}")
        return False

def display_data_info(stock_data):
    """
    가져온 데이터의 기본 정보를 출력하는 함수
    """
    if stock_data is None:
        return
        
    print("\n=== 데이터 정보 ===")
    print(f"데이터 기간: {stock_data.index[0].strftime('%Y-%m-%d')} ~ {stock_data.index[-1].strftime('%Y-%m-%d')}")
    print(f"총 거래일수: {len(stock_data)}일")
    print(f"컬럼: {list(stock_data.columns)}")
    
    # 최근 5일 데이터 미리보기
    print("\n=== 최근 5일 데이터 ===")
    print(stock_data.tail().round(2))
    
    # 기본 통계 정보
    print("\n=== 기본 통계 ===")
    print(stock_data.describe().round(2))

def main():
    """
    메인 실행 함수
    """
    print("=== 삼성전자 주가 데이터 수집기 ===")
    
    # 1. 데이터 가져오기
    stock_data = get_samsung_stock_data()
    
    if stock_data is not None:
        # 2. 데이터 정보 출력
        display_data_info(stock_data)
        
        # 3. CSV 파일로 저장
        save_to_csv(stock_data)
        
        print("\n=== 작업 완료 ===")
    else:
        print("데이터 수집에 실패했습니다.")

if __name__ == "__main__":
    main() 