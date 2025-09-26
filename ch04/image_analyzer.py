import os
import sys
from PIL import Image
import torch
from transformers import ViTImageProcessor, ViTForImageClassification
import requests
from io import BytesIO

class ImageAnalyzer:
    """이미지 분석을 위한 클래스"""
    
    def __init__(self):
        """이미지 분석기 초기화"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = None
        self.model = None
        self.is_loaded = False
        
    def load_model(self):
        """Hugging Face 모델 로드"""
        try:
            print("모델을 로딩 중입니다...")
            # vit-base-patch16-224 모델과 프로세서 로드
            model_name = "google/vit-base-patch16-224"
            self.processor = ViTImageProcessor.from_pretrained(model_name)
            self.model = ViTForImageClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.is_loaded = True
            print(f"모델이 성공적으로 로드되었습니다. (디바이스: {self.device})")
        except Exception as e:
            print(f"모델 로드 중 오류가 발생했습니다: {e}")
            return False
        return True
    
    def load_image_from_path(self, image_path):
        """파일 경로에서 이미지 로드"""
        try:
            if not os.path.exists(image_path):
                print(f"파일을 찾을 수 없습니다: {image_path}")
                return None
            
            # 이미지 파일 확장자 확인
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
            file_ext = os.path.splitext(image_path)[1].lower()
            
            if file_ext not in valid_extensions:
                print(f"지원하지 않는 이미지 형식입니다: {file_ext}")
                print(f"지원되는 형식: {', '.join(valid_extensions)}")
                return None
            
            image = Image.open(image_path)
            return image
        except Exception as e:
            print(f"이미지 로드 중 오류가 발생했습니다: {e}")
            return None
    
    def load_image_from_url(self, image_url):
        """URL에서 이미지 로드"""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            return image
        except Exception as e:
            print(f"URL에서 이미지 로드 중 오류가 발생했습니다: {e}")
            return None
    
    def analyze_image(self, image):
        """이미지 분석 수행"""
        if not self.is_loaded:
            print("모델이 로드되지 않았습니다. 먼저 모델을 로드해주세요.")
            return None
        
        try:
            # 이미지를 RGB로 변환 (RGBA 등 다른 형식 처리)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 이미지 전처리
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 모델 추론
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
            
            # 상위 5개 예측 결과 가져오기
            predicted_class_ids = torch.topk(logits, 5).indices[0]
            probabilities = torch.softmax(logits, dim=1)[0]
            
            # 결과 정리
            results = []
            for i, class_id in enumerate(predicted_class_ids):
                label = self.model.config.id2label[class_id.item()]
                probability = probabilities[class_id].item()
                results.append({
                    'label': label,
                    'probability': probability,
                    'confidence': f"{probability * 100:.2f}%"
                })
            
            return results
            
        except Exception as e:
            print(f"이미지 분석 중 오류가 발생했습니다: {e}")
            return None
    
    def describe_image(self, analysis_results):
        """분석 결과를 자연어로 설명"""
        if not analysis_results:
            return "이미지를 분석할 수 없습니다."
        
        # 가장 확률이 높은 결과를 중심으로 설명
        top_result = analysis_results[0]
        
        description = f"이 사진에는 '{top_result['label']}'이(가) 있는 것으로 보입니다. "
        description += f"확신도는 {top_result['confidence']}입니다.\n\n"
        
        description += "추가로 발견된 객체들:\n"
        for i, result in enumerate(analysis_results[1:], 1):
            description += f"{i}. {result['label']} (확신도: {result['confidence']})\n"
        
        return description

def get_user_input():
    """사용자로부터 이미지 경로 입력 받기"""
    print("\n=== 이미지 분석 프로그램 ===")
    print("1. 로컬 파일 경로 입력")
    print("2. URL 입력")
    print("3. 종료")
    
    while True:
        choice = input("\n선택하세요 (1-3): ").strip()
        
        if choice == '1':
            image_path = input("이미지 파일 경로를 입력하세요: ").strip()
            if image_path:
                return 'file', image_path
        elif choice == '2':
            image_url = input("이미지 URL을 입력하세요: ").strip()
            if image_url:
                return 'url', image_url
        elif choice == '3':
            return 'exit', None
        else:
            print("잘못된 선택입니다. 1, 2, 또는 3을 입력해주세요.")

def main():
    """메인 함수"""
    analyzer = ImageAnalyzer()
    
    # 모델 로드
    if not analyzer.load_model():
        print("프로그램을 종료합니다.")
        return
    
    print("\n이미지 분석기가 준비되었습니다!")
    print("'이 사진에 뭐가 있는지 설명해줘'라는 질문에 답할 수 있습니다.")
    
    while True:
        input_type, input_value = get_user_input()
        
        if input_type == 'exit':
            print("프로그램을 종료합니다.")
            break
        
        # 이미지 로드
        if input_type == 'file':
            image = analyzer.load_image_from_path(input_value)
        else:  # url
            image = analyzer.load_image_from_url(input_value)
        
        if image is None:
            continue
        
        print(f"\n이미지 크기: {image.size}")
        print("이미지를 분석 중입니다...")
        
        # 이미지 분석
        analysis_results = analyzer.analyze_image(image)
        
        if analysis_results:
            # 결과 출력
            print("\n=== 분석 결과 ===")
            description = analyzer.describe_image(analysis_results)
            print(description)
        else:
            print("이미지 분석에 실패했습니다.")
        
        # 계속할지 묻기
        continue_choice = input("\n다른 이미지를 분석하시겠습니까? (y/n): ").strip().lower()
        if continue_choice not in ['y', 'yes', '예']:
            print("프로그램을 종료합니다.")
            break

if __name__ == "__main__":
    main()
