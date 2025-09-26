import requests
import os

def download_test_image():
    """테스트용 이미지 다운로드"""
    
    # 테스트용 이미지 URL (고양이 이미지)
    test_image_url = "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=400&h=300&fit=crop"
    
    try:
        print("테스트용 이미지를 다운로드 중입니다...")
        
        # 이미지 다운로드
        response = requests.get(test_image_url, timeout=10)
        response.raise_for_status()
        
        # 파일 저장
        filename = "test_cat.jpg"
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        print(f"테스트 이미지가 '{filename}'으로 저장되었습니다.")
        print(f"이제 'python image_analyzer.py'를 실행하고 파일 경로로 '{filename}'을 입력해보세요!")
        
    except Exception as e:
        print(f"이미지 다운로드 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    download_test_image()
