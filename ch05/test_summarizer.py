#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스 요약기 테스트 스크립트
"""

import time
from news_summarizer import NewsSummarizer

def test_basic_summarizer():
    """
    기본 요약기 테스트
    """
    print("=== 기본 요약기 테스트 ===")
    
    # 테스트 뉴스 텍스트들
    test_news = [
        {
            "title": "환경 정책",
            "text": """
            서울시는 오늘 새로운 환경 정책을 발표했습니다. 
            이번 정책은 탄소 배출량을 2030년까지 40% 감축하는 것을 목표로 합니다.
            시민들의 참여가 중요한 이번 정책은 다양한 인센티브를 제공할 예정입니다.
            전문가들은 이번 정책이 전국적으로 확산될 가능성이 높다고 평가하고 있습니다.
            """
        },
        {
            "title": "기술 개발",
            "text": """
            국내 연구팀이 새로운 인공지능 기술을 개발했습니다.
            이 기술은 의료 진단의 정확도를 크게 향상시킬 것으로 기대됩니다.
            임상 시험이 성공적으로 완료되어 내년부터 실제 의료 현장에 적용될 예정입니다.
            """
        },
        {
            "title": "경제 뉴스",
            "text": """
            한국은행이 기준금리를 0.25%p 인상했다고 발표했습니다.
            이번 인상은 물가 상승 압박을 고려한 조치로 분석됩니다.
            금융권에서는 이번 결정이 대출 시장에 미칠 영향을 주목하고 있습니다.
            """
        }
    ]
    
    # 요약기 생성
    summarizer = NewsSummarizer()
    
    for i, news in enumerate(test_news, 1):
        print(f"\n--- 테스트 {i}: {news['title']} ---")
        print(f"원본: {news['text'].strip()}")
        
        # 요약 생성
        start_time = time.time()
        summary = summarizer.create_summary(news['text'])
        end_time = time.time()
        
        print(f"요약: {summary}")
        print(f"처리 시간: {end_time - start_time:.2f}초")
        
        # 키워드 추출
        keywords = summarizer.extract_keywords(news['text'])
        print(f"키워드: {keywords}")

def test_performance():
    """
    성능 테스트
    """
    print("\n=== 성능 테스트 ===")
    
    # 긴 텍스트 생성
    long_text = """
    인공지능 기술의 발전으로 다양한 분야에서 혁신이 일어나고 있습니다. 
    특히 자연어 처리 분야에서는 GPT와 같은 대형 언어 모델의 등장으로 
    텍스트 생성과 이해 능력이 크게 향상되었습니다. 이러한 기술은 
    뉴스 요약, 문서 작성, 번역 등 다양한 업무에 활용되고 있습니다.
    
    의료 분야에서도 AI 기술이 활발히 적용되고 있습니다. 의료 영상 분석을 
    통한 질병 진단, 환자 데이터 분석을 통한 예측 의학 등이 대표적인 
    사례입니다. 이러한 기술들은 의료진의 업무 효율성을 높이고 
    환자 치료의 정확도를 향상시키는 데 기여하고 있습니다.
    
    교육 분야에서도 AI 기술이 활용되고 있습니다. 개인화 학습 시스템, 
    자동 채점 시스템, 학습 진도 관리 시스템 등이 개발되어 
    학생들의 학습 효과를 높이는 데 도움을 주고 있습니다.
    """
    
    summarizer = NewsSummarizer()
    
    # 처리 시간 측정
    start_time = time.time()
    summary = summarizer.create_summary(long_text)
    end_time = time.time()
    
    print(f"긴 텍스트 처리 시간: {end_time - start_time:.2f}초")
    print(f"원본 길이: {len(long_text)}자")
    print(f"요약 길이: {len(summary)}자")
    print(f"압축률: {(1 - len(summary) / len(long_text)) * 100:.1f}%")

def main():
    """
    메인 테스트 함수
    """
    print("뉴스 요약기 테스트를 시작합니다...")
    
    try:
        # 기본 요약기 테스트
        test_basic_summarizer()
        
        # 성능 테스트
        test_performance()
        
        print("\n=== 테스트 완료 ===")
        
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    main() 