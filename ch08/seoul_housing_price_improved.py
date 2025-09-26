import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import os
from config import Config

class SeoulHousingPriceCrawler:
    """서울 열린 데이터 광장에서 서울 집값 데이터를 수집하는 개선된 클래스"""
    
    def __init__(self):
        # 설정값 검증
        if not Config.validate_config():
            raise ValueError("API 키가 설정되지 않았습니다. config.py 또는 .env 파일을 확인해주세요.")
        
        # 설정값 출력
        Config.print_config()
        
        # 데이터 저장 디렉토리 생성
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    def make_api_request(self, endpoint, params=None):
        """
        API 요청을 수행하는 공통 함수
        
        Args:
            endpoint (str): API 엔드포인트
            params (dict): 요청 파라미터
            
        Returns:
            dict: API 응답 데이터
        """
        try:
            api_url = f"{Config.SEOUL_BASE_URL}/{Config.SEOUL_API_KEY}/json/{endpoint}/1/{Config.PAGE_SIZE}"
            
            response = requests.get(
                api_url, 
                params=params, 
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API 요청 중 오류 발생: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            return None
        except Exception as e:
            print(f"예상치 못한 오류: {e}")
            return None
    
    def get_apartment_price_data(self):
        """서울시 아파트 실거래가 데이터를 가져오는 함수"""
        print("서울시 아파트 실거래가 데이터 수집 중...")
        
        data = self.make_api_request("SeoulApartmentPrice")
        
        if data and 'SeoulApartmentPrice' in data and 'row' in data['SeoulApartmentPrice']:
            apartment_data = data['SeoulApartmentPrice']['row']
            # 데이터 타입 구분을 위한 컬럼 추가
            for item in apartment_data:
                item['property_type'] = '아파트'
            return apartment_data
        else:
            print("아파트 데이터를 가져올 수 없습니다.")
            return []
    
    def get_officetel_price_data(self):
        """서울시 오피스텔 실거래가 데이터를 가져오는 함수"""
        print("서울시 오피스텔 실거래가 데이터 수집 중...")
        
        data = self.make_api_request("SeoulOfficetelPrice")
        
        if data and 'SeoulOfficetelPrice' in data and 'row' in data['SeoulOfficetelPrice']:
            officetel_data = data['SeoulOfficetelPrice']['row']
            for item in officetel_data:
                item['property_type'] = '오피스텔'
            return officetel_data
        else:
            print("오피스텔 데이터를 가져올 수 없습니다.")
            return []
    
    def get_villa_price_data(self):
        """서울시 빌라/연립 실거래가 데이터를 가져오는 함수"""
        print("서울시 빌라/연립 실거래가 데이터 수집 중...")
        
        data = self.make_api_request("SeoulVillaPrice")
        
        if data and 'SeoulVillaPrice' in data and 'row' in data['SeoulVillaPrice']:
            villa_data = data['SeoulVillaPrice']['row']
            for item in villa_data:
                item['property_type'] = '빌라/연립'
            return villa_data
        else:
            print("빌라/연립 데이터를 가져올 수 없습니다.")
            return []
    
    def collect_all_housing_data(self):
        """모든 유형의 집값 데이터를 수집하는 함수"""
        print(f"최근 {Config.YEARS_BACK}년치 서울 집값 데이터 수집을 시작합니다...")
        
        all_data = []
        
        # 1. 아파트 실거래가 데이터 수집
        apartment_data = self.get_apartment_price_data()
        if apartment_data:
            all_data.extend(apartment_data)
            print(f"아파트 데이터 수집 완료: {len(apartment_data)}개")
        
        # API 호출 제한을 고려한 대기
        time.sleep(Config.REQUEST_DELAY)
        
        # 2. 오피스텔 실거래가 데이터 수집
        officetel_data = self.get_officetel_price_data()
        if officetel_data:
            all_data.extend(officetel_data)
            print(f"오피스텔 데이터 수집 완료: {len(officetel_data)}개")
        
        # API 호출 제한을 고려한 대기
        time.sleep(Config.REQUEST_DELAY)
        
        # 3. 빌라/연립 실거래가 데이터 수집
        villa_data = self.get_villa_price_data()
        if villa_data:
            all_data.extend(villa_data)
            print(f"빌라/연립 데이터 수집 완료: {len(villa_data)}개")
        
        return all_data
    
    def filter_recent_data(self, data):
        """
        수집된 데이터에서 최근 N년치만 필터링하는 함수
        
        Args:
            data (list): 전체 데이터 리스트
            
        Returns:
            list: 최근 N년치 데이터만 필터링된 리스트
        """
        if not data:
            return []
        
        # N년 전 날짜 계산
        years_ago = datetime.now() - timedelta(days=Config.YEARS_BACK*365)
        
        filtered_data = []
        
        for item in data:
            try:
                # 거래일자 필드 확인 (API 응답에 따라 필드명 수정 필요)
                trade_date_str = item.get('거래일자', item.get('TRADE_DATE', item.get('거래일', '')))
                
                if trade_date_str:
                    # 날짜 형식에 따라 파싱
                    trade_date = self.parse_date(trade_date_str)
                    
                    if trade_date and trade_date >= years_ago:
                        filtered_data.append(item)
                        
            except Exception as e:
                print(f"날짜 파싱 오류: {e}")
                continue
        
        return filtered_data
    
    def parse_date(self, date_str):
        """
        다양한 날짜 형식을 파싱하는 함수
        
        Args:
            date_str (str): 날짜 문자열
            
        Returns:
            datetime: 파싱된 날짜 객체
        """
        if not date_str:
            return None
        
        # 다양한 날짜 형식 시도
        date_formats = [
            '%Y%m%d',      # 20231201
            '%Y-%m-%d',    # 2023-12-01
            '%Y/%m/%d',    # 2023/12/01
            '%Y.%m.%d',    # 2023.12.01
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
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
        
        filepath = os.path.join(Config.OUTPUT_DIR, filename)
        
        try:
            # DataFrame으로 변환
            df = pd.DataFrame(data)
            
            # CSV 파일로 저장
            df.to_csv(filepath, index=False, encoding=Config.CSV_ENCODING)
            
            print(f"데이터가 성공적으로 저장되었습니다: {filepath}")
            print(f"총 {len(data)}개의 레코드가 저장되었습니다.")
            
            # 데이터 미리보기 출력
            print("\n=== 데이터 미리보기 ===")
            print(df.head())
            print(f"\n데이터 형태: {df.shape}")
            
            # 컬럼 정보 출력
            print("\n=== 컬럼 정보 ===")
            print(df.columns.tolist())
            
            # 데이터 타입별 통계
            if 'property_type' in df.columns:
                print("\n=== 데이터 타입별 통계 ===")
                print(df['property_type'].value_counts())
            
        except Exception as e:
            print(f"CSV 저장 중 오류 발생: {e}")
    
    def run(self):
        """메인 실행 함수"""
        print("서울 집값 데이터 수집을 시작합니다...")
        
        try:
            # 모든 유형의 집값 데이터 수집
            all_housing_data = self.collect_all_housing_data()
            
            if all_housing_data:
                # 최근 N년치 데이터만 필터링
                recent_data = self.filter_recent_data(all_housing_data)
                
                if recent_data:
                    # CSV 파일로 저장
                    self.save_to_csv(recent_data)
                else:
                    print(f"최근 {Config.YEARS_BACK}년치 데이터가 없습니다.")
            else:
                print("수집된 데이터가 없습니다. API 키와 엔드포인트를 확인해주세요.")
                
        except Exception as e:
            print(f"프로그램 실행 중 오류 발생: {e}")


def main():
    """메인 함수"""
    print("=== 서울 집값 데이터 수집기 (개선된 버전) ===")
    
    try:
        # 크롤러 인스턴스 생성
        crawler = SeoulHousingPriceCrawler()
        
        # 데이터 수집 및 저장 실행
        crawler.run()
        
    except ValueError as e:
        print(f"설정 오류: {e}")
    except Exception as e:
        print(f"예상치 못한 오류: {e}")


if __name__ == "__main__":
    main() 