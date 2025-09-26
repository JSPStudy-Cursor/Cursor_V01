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

class SimpleNewsSummarizer:
    """
    사용자 친화적인 간단한 뉴스 요약기
    """
    
    def __init__(self, model_name: str = "paust/pko-t5-large"):
        """
        모델 초기화
        """
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """
        모델 로딩 (필요할 때만 로딩)
        """
        if self.model is None:
            try:
                logger.info(f"모델 로딩 중: {self.model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                self.model.to(self.device)
                logger.info(f"모델 로딩 완료 (디바이스: {self.device})")
            except Exception as e:
                logger.error(f"모델 로딩 실패: {e}")
                raise
    
    def clean_text(self, text: str) -> str:
        """
        텍스트 정리
        """
        try:
            # HTML 태그 제거
            text = re.sub(r'<[^>]+>', '', text)
            # 여러 공백을 하나로
            text = re.sub(r'\s+', ' ', text)
            # 앞뒤 공백 제거
            return text.strip()
        except Exception as e:
            logger.error(f"텍스트 정리 중 오류: {e}")
            return text
    
    def summarize(self, text: str, max_length: int = 100) -> str:
        """
        텍스트 요약
        """
        try:
            if not text or len(text.strip()) == 0:
                return "요약할 텍스트가 없습니다."
            
            # 모델 로딩
            self.load_model()
            
            # 텍스트 정리
            cleaned_text = self.clean_text(text)
            
            # 토크나이저로 인코딩
            inputs = self.tokenizer(
                cleaned_text, 
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
                    min_length=30,
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True,
                    no_repeat_ngram_size=3
                )
            
            # 디코딩
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"요약 생성 중 오류: {e}")
            return f"요약 생성 중 오류가 발생했습니다: {e}"
    
    def get_summary_stats(self, original: str, summary: str) -> Dict[str, Any]:
        """
        요약 통계 정보
        """
        try:
            original_length = len(original)
            summary_length = len(summary)
            compression_ratio = (1 - summary_length / original_length) * 100 if original_length > 0 else 0
            
            return {
                "original_length": original_length,
                "summary_length": summary_length,
                "compression_ratio": round(compression_ratio, 2),
                "model_name": self.model_name
            }
        except Exception as e:
            logger.error(f"통계 계산 중 오류: {e}")
            return {}


def main():
    """
    간단한 사용 예시
    """
    print("=== 간단한 뉴스 요약 프로그램 ===")
    print("모델을 로딩하고 있습니다. 잠시만 기다려주세요...")
    
    try:
        # 요약기 생성
        summarizer = SimpleNewsSummarizer()
        
        # 예시 뉴스
        sample_news = """
        서울시는 오늘 새로운 환경 정책을 발표했습니다. 
        이번 정책은 탄소 배출량을 2030년까지 40% 감축하는 것을 목표로 합니다.
        시민들의 참여가 중요한 이번 정책은 다양한 인센티브를 제공할 예정입니다.
        """
        
        print("\n=== 예시 요약 ===")
        print(f"원본: {sample_news.strip()}")
        
        summary = summarizer.summarize(sample_news)
        print(f"요약: {summary}")
        
        stats = summarizer.get_summary_stats(sample_news, summary)
        print(f"압축률: {stats.get('compression_ratio', 0)}%")
        
        print("\n=== 대화형 모드 ===")
        print("뉴스 기사를 입력하세요 (종료: quit)")
        
        while True:
            try:
                user_input = input("\n> ")
                
                if user_input.lower() in ['quit', 'exit', '종료']:
                    print("프로그램을 종료합니다.")
                    break
                
                if not user_input.strip():
                    print("텍스트를 입력해주세요.")
                    continue
                
                print("요약 생성 중...")
                summary = summarizer.summarize(user_input)
                print(f"📰 요약: {summary}")
                
            except KeyboardInterrupt:
                print("\n프로그램을 종료합니다.")
                break
            except Exception as e:
                print(f"오류가 발생했습니다: {e}")
                
    except Exception as e:
        print(f"프로그램 실행 중 오류: {e}")


if __name__ == "__main__":
    main() 