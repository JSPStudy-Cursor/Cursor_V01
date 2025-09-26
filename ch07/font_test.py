import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import platform
import os

def check_korean_fonts():
    """시스템에서 사용 가능한 한글 폰트를 확인하는 함수"""
    print("=== 시스템 한글 폰트 확인 ===")
    print(f"운영체제: {platform.system()}")
    print(f"플랫폼: {platform.platform()}")
    
    # 사용 가능한 폰트 목록 가져오기
    font_list = [f.name for f in fm.fontManager.ttflist]
    
    # 한글 폰트 찾기
    korean_fonts = []
    for font in font_list:
        if any(keyword in font.lower() for keyword in ['malgun', 'gothic', 'gulim', 'dotum', 'batang', 'nanum', 'noto']):
            korean_fonts.append(font)
    
    print(f"\n발견된 한글 폰트 ({len(korean_fonts)}개):")
    for i, font in enumerate(korean_fonts, 1):
        print(f"  {i:2d}. {font}")
    
    return korean_fonts

def test_korean_plot():
    """한글 폰트로 그래프를 그려서 테스트하는 함수"""
    print("\n=== 한글 폰트 테스트 ===")
    
    # 샘플 데이터 생성
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    # 그래프 생성
    plt.figure(figsize=(12, 8))
    
    # 서브플롯 1: 기본 그래프
    plt.subplot(2, 2, 1)
    plt.plot(x, y1, 'b-', label='사인 함수', linewidth=2)
    plt.plot(x, y2, 'r--', label='코사인 함수', linewidth=2)
    plt.title('삼각함수 그래프 (한글 제목 테스트)', fontsize=14, fontweight='bold')
    plt.xlabel('X축 (시간)', fontsize=12)
    plt.ylabel('Y축 (값)', fontsize=12)
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    
    # 서브플롯 2: 산점도
    plt.subplot(2, 2, 2)
    np.random.seed(42)
    x_scatter = np.random.randn(50)
    y_scatter = 2 * x_scatter + np.random.randn(50) * 0.5
    plt.scatter(x_scatter, y_scatter, alpha=0.6, color='green')
    plt.title('산점도 예제 (한글)', fontsize=14)
    plt.xlabel('독립 변수', fontsize=12)
    plt.ylabel('종속 변수', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # 서브플롯 3: 막대 그래프
    plt.subplot(2, 2, 3)
    categories = ['카테고리 A', '카테고리 B', '카테고리 C', '카테고리 D']
    values = [23, 45, 56, 78]
    colors = ['red', 'blue', 'green', 'orange']
    bars = plt.bar(categories, values, color=colors, alpha=0.7)
    plt.title('막대 그래프 (한글 라벨)', fontsize=14)
    plt.xlabel('분류', fontsize=12)
    plt.ylabel('수치', fontsize=12)
    
    # 막대 위에 값 표시
    for bar, value in zip(bars, values):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value}', ha='center', va='bottom', fontsize=10)
    
    # 서브플롯 4: 파이 차트
    plt.subplot(2, 2, 4)
    sizes = [30, 25, 20, 15, 10]
    labels = ['첫 번째', '두 번째', '세 번째', '네 번째', '다섯 번째']
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title('파이 차트 (한글 라벨)', fontsize=14)
    
    plt.tight_layout()
    plt.show()
    
    print("한글 폰트 테스트 그래프가 표시되었습니다.")
    print("제목, 축 라벨, 범례가 한글로 제대로 표시되는지 확인해주세요.")

def test_specific_fonts():
    """특정 한글 폰트들을 개별적으로 테스트하는 함수"""
    print("\n=== 특정 폰트 테스트 ===")
    
    # 테스트할 폰트 목록
    test_fonts = [
        'Malgun Gothic',
        '맑은 고딕',
        'Gulim',
        '굴림',
        'Dotum',
        '돋움',
        'Batang',
        '바탕',
        'Nanum Gothic',
        '나눔고딕',
        'Noto Sans CJK KR'
    ]
    
    # 샘플 데이터
    x = np.linspace(0, 5, 100)
    y = np.sin(x)
    
    for font_name in test_fonts:
        try:
            # 폰트 설정
            plt.rcParams['font.family'] = font_name
            plt.rcParams['axes.unicode_minus'] = False
            
            # 간단한 그래프 생성
            plt.figure(figsize=(8, 6))
            plt.plot(x, y, 'b-', linewidth=2)
            plt.title(f'폰트 테스트: {font_name}', fontsize=16, fontweight='bold')
            plt.xlabel('X축 (한글)', fontsize=12)
            plt.ylabel('Y축 (한글)', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            print(f"✓ {font_name} 폰트 테스트 완료")
            plt.show()
            
        except Exception as e:
            print(f"✗ {font_name} 폰트 테스트 실패: {e}")

def main():
    """메인 함수"""
    print("=== 한글 폰트 지원 확인 및 테스트 ===")
    
    # 1. 시스템 한글 폰트 확인
    korean_fonts = check_korean_fonts()
    
    # 2. 기본 한글 폰트 설정 시도
    try:
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False
        print(f"\n✓ Malgun Gothic 폰트 설정 완료")
    except Exception as e:
        print(f"\n✗ Malgun Gothic 폰트 설정 실패: {e}")
    
    # 3. 한글 그래프 테스트
    test_korean_plot()
    
    # 4. 특정 폰트들 개별 테스트 (선택사항)
    response = input("\n특정 폰트들을 개별적으로 테스트하시겠습니까? (y/n): ")
    if response.lower() == 'y':
        test_specific_fonts()

if __name__ == "__main__":
    main() 