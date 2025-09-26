import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

class Config:
    """설정 클래스 - API 키와 기타 설정값들을 관리"""
    
    # 서울 열린 데이터 광장 API 설정
    SEOUL_API_KEY = os.getenv('SEOUL_API_KEY', 'YOUR_API_KEY_HERE')
    SEOUL_BASE_URL = "http://openapi.seoul.go.kr:8088"
    
    # 데이터 수집 설정
    PAGE_SIZE = 1000  # 한 번에 가져올 데이터 개수
    REQUEST_TIMEOUT = 30  # API 요청 타임아웃 (초)
    REQUEST_DELAY = 2  # API 호출 간 대기 시간 (초)
    
    # 데이터 저장 설정
    OUTPUT_DIR = "housing_data"
    CSV_ENCODING = "utf-8-sig"  # CSV 파일 인코딩
    
    # 날짜 필터링 설정
    YEARS_BACK = 5  # 몇 년 전까지의 데이터를 수집할지 설정
    
    @classmethod
    def validate_config(cls):
        """설정값 유효성 검사"""
        if cls.SEOUL_API_KEY == 'YOUR_API_KEY_HERE':
            print("⚠️  경고: API 키가 설정되지 않았습니다.")
            print("   .env 파일에 SEOUL_API_KEY를 설정하거나")
            print("   config.py 파일에서 직접 설정해주세요.")
            return False
        return True
    
    @classmethod
    def print_config(cls):
        """현재 설정값 출력"""
        print("=== 현재 설정 ===")
        print(f"API 키: {'*' * len(cls.SEOUL_API_KEY) if cls.SEOUL_API_KEY != 'YOUR_API_KEY_HERE' else '설정되지 않음'}")
        print(f"기본 URL: {cls.SEOUL_BASE_URL}")
        print(f"페이지 크기: {cls.PAGE_SIZE}")
        print(f"요청 타임아웃: {cls.REQUEST_TIMEOUT}초")
        print(f"요청 간 대기: {cls.REQUEST_DELAY}초")
        print(f"출력 디렉토리: {cls.OUTPUT_DIR}")
        print(f"수집 기간: 최근 {cls.YEARS_BACK}년")
        print("=" * 20) 