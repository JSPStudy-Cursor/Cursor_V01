import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import os
from config import Config

class SeoulHousingPriceDebugger:
    """서울 열린 데이터 광장 API 디버깅 클래스"""
    
    def __init__(self):
        # 설정값 검증
        if not Config.validate_config():
            raise ValueError("API 키가 설정되지 않았습니다. config.py 또는 .env 파일을 확인해주세요.")
        
        # 설정값 출력
        Config.print_config()
        
        # 데이터 저장 디렉토리 생성
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    def test_api_endpoints(self):
        """사용 가능한 API 엔드포인트들을 테스트하는 함수"""
        print("=== 서울 열린 데이터 광장 API 엔드포인트 테스트 ===")
        
        # 서울 열린 데이터 광장에서 제공하는 실제 집값 관련 API들
        test_endpoints = [
            "SeoulApartmentPrice",      # 서울시 아파트 실거래가
            "SeoulOfficetelPrice",      # 서울시 오피스텔 실거래가  
            "SeoulVillaPrice",          # 서울시 빌라/연립 실거래가
            "SeoulHousingPrice",        # 서울시 집값 (일반)
            "SeoulRealEstatePrice",     # 서울시 부동산 가격
            "SeoulApartmentTrade",      # 서울시 아파트 거래
            "SeoulHousingTrade",        # 서울시 주택 거래
            "SeoulApartment",           # 서울시 아파트
            "SeoulHousing",             # 서울시 주택
        ]
        
        working_endpoints = []
        
        for endpoint in test_endpoints:
            print(f"\n--- {endpoint} 테스트 중 ---")
            
            try:
                # API URL 구성
                api_url = f"{Config.SEOUL_BASE_URL}/{Config.SEOUL_API_KEY}/json/{endpoint}/1/10"
                
                print(f"요청 URL: {api_url}")
                
                # API 요청
                response = requests.get(api_url, timeout=Config.REQUEST_TIMEOUT)
                
                print(f"응답 상태 코드: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"응답 구조: {list(data.keys()) if isinstance(data, dict) else '리스트 형태'}")
                    
                    # 데이터 구조 분석
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, dict) and 'row' in value:
                                row_count = len(value['row']) if isinstance(value['row'], list) else 0
                                print(f"  {key}.row: {row_count}개 데이터")
                                
                                # 첫 번째 데이터 샘플 출력
                                if row_count > 0 and isinstance(value['row'], list):
                                    print(f"  첫 번째 데이터 샘플: {value['row'][0]}")
                                    
                                working_endpoints.append({
                                    'endpoint': endpoint,
                                    'data_key': key,
                                    'row_count': row_count,
                                    'sample': value['row'][0] if row_count > 0 else None
                                })
                            elif isinstance(value, list):
                                print(f"  {key}: {len(value)}개 데이터")
                                if len(value) > 0:
                                    print(f"  첫 번째 데이터 샘플: {value[0]}")
                                    
                                working_endpoints.append({
                                    'endpoint': endpoint,
                                    'data_key': key,
                                    'row_count': len(value),
                                    'sample': value[0] if len(value) > 0 else None
                                })
                    elif isinstance(data, list):
                        print(f"  리스트 형태: {len(data)}개 데이터")
                        if len(data) > 0:
                            print(f"  첫 번째 데이터 샘플: {data[0]}")
                            
                        working_endpoints.append({
                            'endpoint': endpoint,
                            'data_key': 'list',
                            'row_count': len(data),
                            'sample': data[0] if len(data) > 0 else None
                        })
                else:
                    print(f"오류: {response.text}")
                    
            except Exception as e:
                print(f"오류 발생: {e}")
            
            # API 호출 제한을 고려한 대기
            time.sleep(1)
        
        return working_endpoints
    
    def get_available_datasets(self):
        """서울 열린 데이터 광장에서 사용 가능한 데이터셋 목록을 가져오는 함수"""
        print("\n=== 사용 가능한 데이터셋 검색 ===")
        
        # 일반적인 데이터셋 키워드들
        search_keywords = [
            "아파트", "apartment", "주택", "housing", "부동산", "real estate",
            "거래", "trade", "가격", "price", "실거래가", "매매",
            "오피스텔", "officetel", "빌라", "villa", "연립", "row house"
        ]
        
        found_datasets = []
        
        for keyword in search_keywords:
            print(f"\n'{keyword}' 관련 데이터셋 검색 중...")
            
            try:
                # 검색 API (실제로는 다른 방식일 수 있음)
                search_url = f"{Config.SEOUL_BASE_URL}/{Config.SEOUL_API_KEY}/json/SearchDataset/1/10"
                params = {'keyword': keyword}
                
                response = requests.get(search_url, params=params, timeout=Config.REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"검색 결과: {data}")
                else:
                    print(f"검색 실패: {response.status_code}")
                    
            except Exception as e:
                print(f"검색 중 오류: {e}")
            
            time.sleep(1)
        
        return found_datasets
    
    def test_common_endpoints(self):
        """일반적으로 사용되는 API 엔드포인트들을 테스트하는 함수"""
        print("\n=== 일반적인 API 엔드포인트 테스트 ===")
        
        # 서울 열린 데이터 광장에서 자주 사용되는 패턴들
        common_patterns = [
            "SeoulApartmentPrice",
            "SeoulApartmentTrade", 
            "SeoulHousingPrice",
            "SeoulHousingTrade",
            "SeoulRealEstatePrice",
            "SeoulRealEstateTrade",
            "SeoulApartment",
            "SeoulHousing",
            "SeoulRealEstate",
            "ApartmentPrice",
            "HousingPrice",
            "RealEstatePrice",
            "ApartmentTrade",
            "HousingTrade",
            "RealEstateTrade"
        ]
        
        working_endpoints = []
        
        for pattern in common_patterns:
            print(f"\n--- {pattern} 테스트 ---")
            
            try:
                api_url = f"{Config.SEOUL_BASE_URL}/{Config.SEOUL_API_KEY}/json/{pattern}/1/5"
                
                response = requests.get(api_url, timeout=Config.REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 성공: {pattern}")
                    print(f"응답 구조: {list(data.keys()) if isinstance(data, dict) else '리스트'}")
                    
                    # 데이터 구조 분석
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, dict) and 'row' in value:
                                row_count = len(value['row']) if isinstance(value['row'], list) else 0
                                print(f"  {key}.row: {row_count}개 데이터")
                                
                                if row_count > 0:
                                    working_endpoints.append({
                                        'endpoint': pattern,
                                        'data_key': f"{key}.row",
                                        'row_count': row_count,
                                        'sample': value['row'][0]
                                    })
                else:
                    print(f"❌ 실패: {pattern} (상태 코드: {response.status_code})")
                    
            except Exception as e:
                print(f"❌ 오류: {pattern} - {e}")
            
            time.sleep(1)
        
        return working_endpoints
    
    def save_test_results(self, working_endpoints):
        """테스트 결과를 파일로 저장하는 함수"""
        if not working_endpoints:
            print("작동하는 엔드포인트가 없습니다.")
            return
        
        # 결과를 JSON 파일로 저장
        results_file = os.path.join(Config.OUTPUT_DIR, "api_test_results.json")
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(working_endpoints, f, ensure_ascii=False, indent=2)
        
        print(f"\n테스트 결과가 저장되었습니다: {results_file}")
        
        # 결과 요약 출력
        print("\n=== 테스트 결과 요약 ===")
        for endpoint in working_endpoints:
            print(f"✅ {endpoint['endpoint']}: {endpoint['row_count']}개 데이터")
            if endpoint['sample']:
                print(f"   샘플 키: {list(endpoint['sample'].keys())}")
    
    def run(self):
        """메인 실행 함수"""
        print("서울 열린 데이터 광장 API 디버깅을 시작합니다...")
        
        try:
            # 1. 일반적인 엔드포인트 테스트
            working_endpoints = self.test_common_endpoints()
            
            # 2. 추가 엔드포인트 테스트
            additional_endpoints = self.test_api_endpoints()
            working_endpoints.extend(additional_endpoints)
            
            # 3. 결과 저장
            self.save_test_results(working_endpoints)
            
            if working_endpoints:
                print(f"\n총 {len(working_endpoints)}개의 작동하는 엔드포인트를 찾았습니다.")
                print("이 정보를 바탕으로 실제 데이터 수집 코드를 수정하세요.")
            else:
                print("\n작동하는 엔드포인트를 찾지 못했습니다.")
                print("서울 열린 데이터 광장 웹사이트에서 실제 API 문서를 확인해주세요.")
                
        except Exception as e:
            print(f"디버깅 중 오류 발생: {e}")


def main():
    """메인 함수"""
    print("=== 서울 열린 데이터 광장 API 디버거 ===")
    
    try:
        # 디버거 인스턴스 생성
        debugger = SeoulHousingPriceDebugger()
        
        # API 테스트 실행
        debugger.run()
        
    except ValueError as e:
        print(f"설정 오류: {e}")
    except Exception as e:
        print(f"예상치 못한 오류: {e}")


if __name__ == "__main__":
    main() 