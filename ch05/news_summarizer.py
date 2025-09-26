import re
import requests
from typing import Optional, List
from collections import Counter
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsSummarizer:
    """
    뉴스 기사 본문을 한 줄로 요약하는 클래스
    """
    
    def __init__(self):
        # 불용어 목록 (한국어)
        self.stop_words = {
            '이', '그', '저', '것', '수', '등', '때', '곳', '말', '일',
            '년', '월', '일', '시', '분', '초', '주', '개', '명', '회',
            '있다', '없다', '하다', '되다', '있다고', '없다고', '한다고',
            '라고', '이라고', '에서', '으로', '에게', '을', '를', '이', '가',
            '은', '는', '도', '만', '도', '부터', '까지', '에서', '으로',
            '그리고', '또는', '하지만', '그러나', '따라서', '그래서'
        }
    
    def preprocess_text(self, text: str) -> str:
        """
        텍스트 전처리 함수
        - 특수문자 제거
        - 공백 정리
        - 줄바꿈 제거
        """
        try:
            # 특수문자 제거 (한글, 영문, 숫자, 공백만 유지)
            cleaned_text = re.sub(r'[^\w\s가-힣]', ' ', text)
            # 여러 공백을 하나로 통일
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            # 앞뒤 공백 제거
            cleaned_text = cleaned_text.strip()
            return cleaned_text
        except Exception as e:
            logger.error(f"텍스트 전처리 중 오류 발생: {e}")
            return text
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """
        텍스트에서 키워드 추출
        - 단어 빈도수 기반
        - 불용어 제거
        """
        try:
            # 텍스트 전처리
            cleaned_text = self.preprocess_text(text)
            
            # 단어 분리 (공백 기준)
            words = cleaned_text.split()
            
            # 불용어 제거 및 길이 필터링 (2글자 이상)
            filtered_words = [
                word for word in words 
                if word not in self.stop_words and len(word) >= 2
            ]
            
            # 단어 빈도수 계산
            word_counts = Counter(filtered_words)
            
            # 상위 N개 키워드 추출 (빈도수 기준으로 정렬)
            keywords = []
            for word, count in word_counts.most_common(top_n * 2):  # 더 많은 후보에서 선택
                # 조사나 어미가 붙은 단어는 원형으로 변환 시도
                clean_word = self._clean_word(word)
                if clean_word and clean_word not in keywords:
                    keywords.append(clean_word)
                    if len(keywords) >= top_n:
                        break
            
            return keywords
        except Exception as e:
            logger.error(f"키워드 추출 중 오류 발생: {e}")
            return []
    
    def _clean_word(self, word: str) -> str:
        """
        단어 정리 (조사, 어미 제거)
        """
        # 조사 제거
        particles = ['은', '는', '이', '가', '을', '를', '의', '에', '에서', '로', '으로', '와', '과', '도', '만', '부터', '까지']
        for particle in particles:
            if word.endswith(particle):
                word = word[:-len(particle)]
                break
        
        # 2글자 이상인 경우만 반환
        return word if len(word) >= 2 else ""
    
    def extract_main_sentence(self, text: str) -> str:
        """
        텍스트에서 핵심 문장 추출
        - 첫 번째 문장 또는 가장 긴 문장 선택
        """
        try:
            # 문장 분리 (마침표, 느낌표, 물음표 기준)
            sentences = re.split(r'[.!?]', text)
            
            # 빈 문장 제거 및 정리
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return ""
            
            # 첫 번째 문장 반환 (보통 기사의 핵심 내용)
            return sentences[0]
        except Exception as e:
            logger.error(f"핵심 문장 추출 중 오류 발생: {e}")
            return ""
    
    def create_summary(self, text: str, max_length: int = 100) -> str:
        """
        뉴스 기사를 한 줄로 요약
        - 키워드와 핵심 문장을 조합
        """
        try:
            if not text or len(text.strip()) == 0:
                return "요약할 텍스트가 없습니다."
            
            # 키워드 추출
            keywords = self.extract_keywords(text, top_n=3)
            
            # 핵심 문장 추출
            main_sentence = self.extract_main_sentence(text)
            
            # 요약 생성
            if keywords and main_sentence:
                # 키워드와 핵심 문장을 조합
                summary = f"{', '.join(keywords)}: {main_sentence}"
            elif keywords:
                # 키워드만 있는 경우
                summary = f"주요 키워드: {', '.join(keywords)}"
            elif main_sentence:
                # 핵심 문장만 있는 경우
                summary = main_sentence
            else:
                # 둘 다 없는 경우 텍스트 앞부분 사용
                summary = text[:max_length] + "..." if len(text) > max_length else text
            
            # 길이 제한
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
            
        except Exception as e:
            logger.error(f"요약 생성 중 오류 발생: {e}")
            return "요약 생성 중 오류가 발생했습니다."
    
    def summarize_from_url(self, url: str) -> str:
        """
        URL에서 뉴스 기사를 가져와서 요약
        """
        try:
            # 간단한 웹 스크래핑 (실제 사용시에는 더 정교한 방법 필요)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # HTML 태그 제거 (간단한 방법)
            text = re.sub(r'<[^>]+>', '', response.text)
            text = re.sub(r'\s+', ' ', text)
            
            return self.create_summary(text)
            
        except Exception as e:
            logger.error(f"URL에서 텍스트 추출 중 오류 발생: {e}")
            return f"URL 처리 중 오류가 발생했습니다: {e}"


def main():
    """
    사용 예시
    """
    summarizer = NewsSummarizer()
    
    # 예시 뉴스 텍스트
    sample_news = """
    서울시는 오늘 새로운 환경 정책을 발표했습니다. 
    이번 정책은 탄소 배출량을 2030년까지 40% 감축하는 것을 목표로 합니다.
    시민들의 참여가 중요한 이번 정책은 다양한 인센티브를 제공할 예정입니다.
    전문가들은 이번 정책이 전국적으로 확산될 가능성이 높다고 평가하고 있습니다.
    """
    
    print("=== 뉴스 요약 예시 ===")
    print(f"원본 텍스트: {sample_news.strip()}")
    print()
    
    # 요약 생성
    summary = summarizer.create_summary(sample_news)
    print(f"요약 결과: {summary}")
    print()
    
    # 키워드 추출
    keywords = summarizer.extract_keywords(sample_news)
    print(f"추출된 키워드: {keywords}")


if __name__ == "__main__":
    main() 