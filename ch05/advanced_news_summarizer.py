import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re
import logging
from typing import Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedNewsSummarizer:
    """
    사전 학습된 T5/BART 모델을 사용한 고급 뉴스 요약기
    """
    
    def __init__(self, model_name: str = "paust/pko-t5-large"):
        """
        모델 초기화
        Args:
            model_name: 사용할 모델명 (기본값: 한국어 T5 모델)
        """
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        try:
            logger.info(f"모델 로딩 중: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            self.model.to(self.device)
            logger.info(f"모델 로딩 완료 (디바이스: {self.device})")
        except Exception as e:
            logger.error(f"모델 로딩 실패: {e}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """
        텍스트 전처리
        - HTML 태그 제거
        - 특수문자 정리
        - 공백 정리
        """
        try:
            # HTML 태그 제거
            text = re.sub(r'<[^>]+>', '', text)
            # 여러 공백을 하나로
            text = re.sub(r'\s+', ' ', text)
            # 앞뒤 공백 제거
            text = text.strip()
            return text
        except Exception as e:
            logger.error(f"텍스트 전처리 중 오류: {e}")
            return text
    
    def split_long_text(self, text: str, max_length: int = 1024) -> list:
        """
        긴 텍스트를 모델이 처리할 수 있는 크기로 분할
        """
        try:
            if len(text) <= max_length:
                return [text]
            
            # 문장 단위로 분할
            sentences = re.split(r'[.!?]', text)
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # 현재 청크에 문장 추가 시 길이 확인
                if len(current_chunk + sentence) < max_length:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
            
            # 마지막 청크 추가
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            return chunks if chunks else [text]
            
        except Exception as e:
            logger.error(f"텍스트 분할 중 오류: {e}")
            return [text]
    
    def summarize_text(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """
        텍스트 요약 생성
        Args:
            text: 요약할 텍스트
            max_length: 최대 요약 길이
            min_length: 최소 요약 길이
        Returns:
            요약된 텍스트
        """
        try:
            if not text or len(text.strip()) == 0:
                return "요약할 텍스트가 없습니다."
            
            # 텍스트 전처리
            cleaned_text = self.preprocess_text(text)
            
            # 긴 텍스트 분할
            text_chunks = self.split_long_text(cleaned_text)
            
            summaries = []
            
            for chunk in text_chunks:
                # 토크나이저로 인코딩
                inputs = self.tokenizer(
                    chunk, 
                    max_length=1024, 
                    truncation=True, 
                    padding=True, 
                    return_tensors="pt"
                ).to(self.device)
                
                # 요약 생성
                with torch.no_grad():
                    summary_ids = self.model.generate(
                        inputs["input_ids"],
                        max_length=max_length,
                        min_length=min_length,
                        num_beams=4,
                        length_penalty=2.0,
                        early_stopping=True,
                        no_repeat_ngram_size=3
                    )
                
                # 디코딩
                summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                summaries.append(summary)
            
            # 여러 청크의 요약을 결합
            final_summary = " ".join(summaries)
            
            return final_summary.strip()
            
        except Exception as e:
            logger.error(f"요약 생성 중 오류: {e}")
            return f"요약 생성 중 오류가 발생했습니다: {e}"
    
    def get_summary_info(self, original_text: str, summary: str) -> Dict[str, Any]:
        """
        요약 정보 반환 (원본 길이, 요약 길이, 압축률 등)
        """
        try:
            original_length = len(original_text)
            summary_length = len(summary)
            compression_ratio = (1 - summary_length / original_length) * 100 if original_length > 0 else 0
            
            return {
                "original_length": original_length,
                "summary_length": summary_length,
                "compression_ratio": round(compression_ratio, 2),
                "model_name": self.model_name
            }
        except Exception as e:
            logger.error(f"요약 정보 계산 중 오류: {e}")
            return {}
    
    def interactive_summarize(self):
        """
        대화형 요약 인터페이스
        """
        print("=== 뉴스 기사 요약 프로그램 ===")
        print("종료하려면 'quit' 또는 'exit'를 입력하세요.")
        print()
        
        while True:
            try:
                # 사용자 입력 받기
                print("뉴스 기사를 입력하세요:")
                user_input = input("> ")
                
                if user_input.lower() in ['quit', 'exit', '종료']:
                    print("프로그램을 종료합니다.")
                    break
                
                if not user_input.strip():
                    print("텍스트를 입력해주세요.")
                    continue
                
                print("\n요약 생성 중...")
                
                # 요약 생성
                summary = self.summarize_text(user_input)
                
                # 요약 정보 계산
                info = self.get_summary_info(user_input, summary)
                
                # 결과 출력
                print("\n" + "="*50)
                print("📰 요약 결과")
                print("="*50)
                print(f"📝 요약: {summary}")
                print(f"📊 원본 길이: {info.get('original_length', 0)}자")
                print(f"📊 요약 길이: {info.get('summary_length', 0)}자")
                print(f"📊 압축률: {info.get('compression_ratio', 0)}%")
                print(f"🤖 사용 모델: {info.get('model_name', 'Unknown')}")
                print("="*50)
                print()
                
            except KeyboardInterrupt:
                print("\n프로그램을 종료합니다.")
                break
            except Exception as e:
                logger.error(f"대화형 인터페이스 오류: {e}")
                print(f"오류가 발생했습니다: {e}")


def main():
    """
    메인 함수 - 사용 예시
    """
    try:
        # 모델 초기화 (첫 실행 시 모델 다운로드 시간이 걸릴 수 있습니다)
        print("모델을 로딩하고 있습니다. 잠시만 기다려주세요...")
        summarizer = AdvancedNewsSummarizer()
        
        # 예시 뉴스 텍스트
        sample_news = """
        서울시는 오늘 새로운 환경 정책을 발표했습니다. 
        이번 정책은 탄소 배출량을 2030년까지 40% 감축하는 것을 목표로 합니다.
        시민들의 참여가 중요한 이번 정책은 다양한 인센티브를 제공할 예정입니다.
        전문가들은 이번 정책이 전국적으로 확산될 가능성이 높다고 평가하고 있습니다.
        """
        
        print("=== 예시 요약 ===")
        print(f"원본: {sample_news.strip()}")
        print()
        
        summary = summarizer.summarize_text(sample_news)
        print(f"요약: {summary}")
        print()
        
        # 대화형 인터페이스 시작
        summarizer.interactive_summarize()
        
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류: {e}")
        print(f"프로그램 실행 중 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main() 