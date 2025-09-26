import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import os

class SeoulHousingPriceCrawler:
    """서울 열린 데이터 광장에서 서울 집값 데이터를 수집하는 클래스"""
    
    def __init__(self):
        # 서울 열린 데이터 광장 API 키 (실제 사용시 발급받아야 함)
        self.api_key = "YOUR_API_KEY_HERE"  # 실제 API 키로 교체 필요
        self.base_url = "http://openapi.seoul.go.kr:8088"
        
        # 데이터 저장 디렉토리 생성
        self.output_dir = "housing_data"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_housing_price_data(self, start_date, end_date, page_size=1000):
        """
        서울 집값 데이터를 API로부터 가져오는 함수
        
        Args:
            start_date (str): 시작 날짜 (YYYY-MM-DD 형식)
            end_date (str): 종료 날짜 (YYYY-MM-DD 형식)
            page_size (int): 한 번에 가져올 데이터 개수
            
        Returns:
            list: 수집된 데이터 리스트
        """
        try:
            # 서울 열린 데이터 광장의 집값 관련 API 엔드포인트
            # 실제 API는 서울 열린 데이터 광장에서 확인 후 수정 필요
            api_url = f"{self.base_url}/{self.api_key}/json/SeoulHousingPrice/1/{page_size}"
            
            # API 요청 파라미터
            params = {
                'START_DATE': start_date,
                'END_DATE': end_date
            }
            
            print(f"데이터 수집 중: {start_date} ~ {end_date}")
            
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()  # HTTP 오류 체크
            
            data = response.json()
            
            # API 응답 구조에 따라 데이터 추출
            # 실제 API 응답 구조에 맞게 수정 필요
            if 'SeoulHousingPrice' in data and 'row' in data['SeoulHousingPrice']:
                return data['SeoulHousingPrice']['row']
            else:
                print(f"데이터가 없거나 API 응답 구조가 예상과 다릅니다: {data}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"API 요청 중 오류 발생: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            return []
        except Exception as e:
            print(f"예상치 못한 오류: {e}")
            return []
    
    def get_recent_5_years_data(self):
        """최근 5년치 데이터를 수집하는 함수"""
        # 현재 날짜로부터 5년 전까지의 데이터 수집
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)  # 5년 전
        
        # 날짜를 문자열로 변환
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        print(f"최근 5년치 데이터 수집 시작: {start_date_str} ~ {end_date_str}")
        
        all_data = []
        
        # API 호출 제한을 고려하여 월별로 데이터 수집
        current_date = start_date
        while current_date <= end_date:
            month_end = min(current_date + timedelta(days=30), end_date)
            
            month_start_str = current_date.strftime("%Y-%m-%d")
            month_end_str = month_end.strftime("%Y-%m-%d")
            
            month_data = self.get_housing_price_data(month_start_str, month_end_str)
            all_data.extend(month_data)
            
            print(f"수집된 데이터 개수: {len(all_data)}")
            
            # API 호출 제한을 고려한 대기
            time.sleep(1)
            
            current_date = month_end + timedelta(days=1)
        
        return all_data
    
    def save_to_csv(self, data, filename=None):
        """
        수집된 데이터를 CSV 파일로 저장하는 함수
        
        Args:
            data (list): 저장할 데이터 리스트
            filename (str): 저장할 파일명 (기본값: 현재 날짜)
        """
        if not data:
            print("저장할 데이터가 없습니다.")
            return
        
        # 파일명이 지정되지 않으면 현재 날짜로 생성
        if filename is None:
            current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"seoul_housing_price_{current_date}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # DataFrame으로 변환
            df = pd.DataFrame(data)
            
            # CSV 파일로 저장
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            print(f"데이터가 성공적으로 저장되었습니다: {filepath}")
            print(f"총 {len(data)}개의 레코드가 저장되었습니다.")
            
            # 데이터 미리보기 출력
            print("\n=== 데이터 미리보기 ===")
            print(df.head())
            print(f"\n데이터 형태: {df.shape}")
            
        except Exception as e:
            print(f"CSV 저장 중 오류 발생: {e}")
    
    def run(self):
        """메인 실행 함수"""
        print("서울 집값 데이터 수집을 시작합니다...")
        
        # 최근 5년치 데이터 수집
        housing_data = self.get_recent_5_years_data()
        
        if housing_data:
            # CSV 파일로 저장
            self.save_to_csv(housing_data)
        else:
            print("수집된 데이터가 없습니다. API 키와 엔드포인트를 확인해주세요.")


def main():
    """메인 함수"""
    print("=== 서울 집값 데이터 수집기 ===")
    
    # 크롤러 인스턴스 생성
    crawler = SeoulHousingPriceCrawler()
    
    # 데이터 수집 및 저장 실행
    crawler.run()


if __name__ == "__main__":
    main() 