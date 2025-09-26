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
    
    def get_apartment_price_data(self, page_size=1000):
        """
        서울시 아파트 실거래가 데이터를 가져오는 함수
        서울 열린 데이터 광장의 '서울시 아파트 실거래가' API 사용
        """
        try:
            # 서울시 아파트 실거래가 API 엔드포인트
            api_url = f"{self.base_url}/{self.api_key}/json/SeoulApartmentPrice/1/{page_size}"
            
            print("서울시 아파트 실거래가 데이터 수집 중...")
            
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # API 응답 구조 확인 및 데이터 추출
            if 'SeoulApartmentPrice' in data and 'row' in data['SeoulApartmentPrice']:
                return data['SeoulApartmentPrice']['row']
            else:
                print(f"데이터가 없거나 API 응답 구조가 예상과 다릅니다.")
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
    
    def get_officetel_price_data(self, page_size=1000):
        """
        서울시 오피스텔 실거래가 데이터를 가져오는 함수
        """
        try:
            # 서울시 오피스텔 실거래가 API 엔드포인트
            api_url = f"{self.base_url}/{self.api_key}/json/SeoulOfficetelPrice/1/{page_size}"
            
            print("서울시 오피스텔 실거래가 데이터 수집 중...")
            
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'SeoulOfficetelPrice' in data and 'row' in data['SeoulOfficetelPrice']:
                return data['SeoulOfficetelPrice']['row']
            else:
                print(f"오피스텔 데이터가 없거나 API 응답 구조가 예상과 다릅니다.")
                return []
                
        except Exception as e:
            print(f"오피스텔 데이터 수집 중 오류: {e}")
            return []
    
    def get_villa_price_data(self, page_size=1000):
        """
        서울시 빌라/연립 실거래가 데이터를 가져오는 함수
        """
        try:
            # 서울시 빌라/연립 실거래가 API 엔드포인트
            api_url = f"{self.base_url}/{self.api_key}/json/SeoulVillaPrice/1/{page_size}"
            
            print("서울시 빌라/연립 실거래가 데이터 수집 중...")
            
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'SeoulVillaPrice' in data and 'row' in data['SeoulVillaPrice']:
                return data['SeoulVillaPrice']['row']
            else:
                print(f"빌라/연립 데이터가 없거나 API 응답 구조가 예상과 다릅니다.")
                return []
                
        except Exception as e:
            print(f"빌라/연립 데이터 수집 중 오류: {e}")
            return []
    
    def get_recent_5_years_data(self):
        """최근 5년치 데이터를 수집하는 함수"""
        print("최근 5년치 서울 집값 데이터 수집을 시작합니다...")
        
        all_data = []
        
        # 1. 아파트 실거래가 데이터 수집
        apartment_data = self.get_apartment_price_data()
        if apartment_data:
            # 데이터 타입 구분을 위한 컬럼 추가
            for item in apartment_data:
                item['property_type'] = '아파트'
            all_data.extend(apartment_data)
            print(f"아파트 데이터 수집 완료: {len(apartment_data)}개")
        
        # API 호출 제한을 고려한 대기
        time.sleep(2)
        
        # 2. 오피스텔 실거래가 데이터 수집
        officetel_data = self.get_officetel_price_data()
        if officetel_data:
            for item in officetel_data:
                item['property_type'] = '오피스텔'
            all_data.extend(officetel_data)
            print(f"오피스텔 데이터 수집 완료: {len(officetel_data)}개")
        
        # API 호출 제한을 고려한 대기
        time.sleep(2)
        
        # 3. 빌라/연립 실거래가 데이터 수집
        villa_data = self.get_villa_price_data()
        if villa_data:
            for item in villa_data:
                item['property_type'] = '빌라/연립'
            all_data.extend(villa_data)
            print(f"빌라/연립 데이터 수집 완료: {len(villa_data)}개")
        
        return all_data
    
    def filter_recent_5_years(self, data):
        """
        수집된 데이터에서 최근 5년치만 필터링하는 함수
        
        Args:
            data (list): 전체 데이터 리스트
            
        Returns:
            list: 최근 5년치 데이터만 필터링된 리스트
        """
        if not data:
            return []
        
        # 5년 전 날짜 계산
        five_years_ago = datetime.now() - timedelta(days=5*365)
        
        filtered_data = []
        
        for item in data:
            try:
                # 거래일자 필드 확인 (API 응답에 따라 필드명 수정 필요)
                trade_date_str = item.get('거래일자', item.get('TRADE_DATE', ''))
                
                if trade_date_str:
                    # 날짜 형식에 따라 파싱 (YYYYMMDD 또는 YYYY-MM-DD 등)
                    if len(trade_date_str) == 8:  # YYYYMMDD 형식
                        trade_date = datetime.strptime(trade_date_str, '%Y%m%d')
                    elif len(trade_date_str) == 10:  # YYYY-MM-DD 형식
                        trade_date = datetime.strptime(trade_date_str, '%Y-%m-%d')
                    else:
                        continue
                    
                    # 최근 5년치 데이터만 포함
                    if trade_date >= five_years_ago:
                        filtered_data.append(item)
                        
            except (ValueError, TypeError) as e:
                print(f"날짜 파싱 오류: {e}")
                continue
        
        return filtered_data
    
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
            
            # CSV 파일로 저장 (한글 깨짐 방지를 위해 utf-8-sig 인코딩 사용)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            print(f"데이터가 성공적으로 저장되었습니다: {filepath}")
            print(f"총 {len(data)}개의 레코드가 저장되었습니다.")
            
            # 데이터 미리보기 출력
            print("\n=== 데이터 미리보기 ===")
            print(df.head())
            print(f"\n데이터 형태: {df.shape}")
            
            # 컬럼 정보 출력
            print("\n=== 컬럼 정보 ===")
            print(df.columns.tolist())
            
        except Exception as e:
            print(f"CSV 저장 중 오류 발생: {e}")
    
    def run(self):
        """메인 실행 함수"""
        print("서울 집값 데이터 수집을 시작합니다...")
        
        # 모든 유형의 집값 데이터 수집
        all_housing_data = self.get_recent_5_years_data()
        
        if all_housing_data:
            # 최근 5년치 데이터만 필터링
            recent_5_years_data = self.filter_recent_5_years(all_housing_data)
            
            if recent_5_years_data:
                # CSV 파일로 저장
                self.save_to_csv(recent_5_years_data)
            else:
                print("최근 5년치 데이터가 없습니다.")
        else:
            print("수집된 데이터가 없습니다. API 키와 엔드포인트를 확인해주세요.")


def main():
    """메인 함수"""
    print("=== 서울 집값 데이터 수집기 (실제 API 버전) ===")
    
    # 크롤러 인스턴스 생성
    crawler = SeoulHousingPriceCrawler()
    
    # 데이터 수집 및 저장 실행
    crawler.run()


if __name__ == "__main__":
    main() 