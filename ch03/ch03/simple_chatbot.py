#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 룰 기반 챗봇
사용자 입력에 따라 미리 정의된 규칙에 따라 응답하는 챗봇입니다.
"""

import re
from typing import Dict, List, Tuple

class SimpleChatbot:
    """간단한 룰 기반 챗봇 클래스"""
    
    def __init__(self):
        """챗봇 초기화 - 대화 규칙과 패턴을 설정합니다."""
        # 대화 규칙을 딕셔너리로 저장 (키워드: 응답)
        self.conversation_rules = {
            '안녕': ['안녕하세요!', '반갑습니다!', '안녕하세요, 무엇을 도와드릴까요?'],
            '이름': ['제 이름은 SimpleBot입니다.', '저는 SimpleBot이라고 해요!'],
            '날씨': ['오늘 날씨는 어떤가요?', '날씨 정보를 확인해보시는 건 어떨까요?'],
            '시간': ['현재 시간을 확인해보세요!', '시계를 확인해보시는 건 어떨까요?'],
            '도움': ['무엇을 도와드릴까요?', '질문이 있으시면 언제든 말씀해주세요!'],
            '감사': ['천만에요!', '도움이 되어서 기뻐요!', '별 말씀을요!'],
            '잘가': ['안녕히 가세요!', '다음에 또 만나요!', '좋은 하루 되세요!']
        }
        
        # 기본 응답 (규칙에 맞지 않을 때)
        self.default_responses = [
            '죄송해요, 이해하지 못했어요.',
            '다른 말로 표현해주실 수 있나요?',
            '무엇을 도와드릴까요?'
        ]
        
        # 대화 종료 키워드
        self.exit_keywords = ['종료', '끝', '나가기', 'quit', 'exit', 'bye']
    
    def preprocess_user_input(self, user_input: str) -> str:
        """사용자 입력을 전처리합니다."""
        # 소문자로 변환하고 앞뒤 공백 제거
        processed_input = user_input.lower().strip()
        return processed_input
    
    def find_matching_keyword(self, user_input: str) -> str:
        """사용자 입력에서 매칭되는 키워드를 찾습니다."""
        for keyword in self.conversation_rules.keys():
            if keyword in user_input:
                return keyword
        return ""
    
    def get_response(self, keyword: str) -> str:
        """키워드에 해당하는 응답을 반환합니다."""
        if keyword in self.conversation_rules:
            import random
            # 여러 응답 중에서 랜덤하게 선택
            return random.choice(self.conversation_rules[keyword])
        else:
            import random
            return random.choice(self.default_responses)
    
    def is_exit_command(self, user_input: str) -> bool:
        """종료 명령인지 확인합니다."""
        for exit_keyword in self.exit_keywords:
            if exit_keyword in user_input.lower():
                return True
        return False
    
    def chat(self):
        """메인 채팅 루프입니다."""
        print("=== SimpleBot 챗봇 ===")
        print("안녕하세요! 저는 SimpleBot입니다.")
        print("종료하려면 '종료'를 입력하세요.")
        print("-" * 30)
        
        while True:
            try:
                # 사용자 입력 받기
                user_input = input("사용자: ").strip()
                
                # 빈 입력 처리
                if not user_input:
                    print("봇: 말씀해주세요!")
                    continue
                
                # 종료 명령 확인
                if self.is_exit_command(user_input):
                    print("봇: 안녕히 가세요! 다음에 또 만나요!")
                    break
                
                # 입력 전처리
                processed_input = self.preprocess_user_input(user_input)
                
                # 매칭되는 키워드 찾기
                matching_keyword = self.find_matching_keyword(processed_input)
                
                # 응답 생성
                if matching_keyword:
                    response = self.get_response(matching_keyword)
                else:
                    response = self.get_response("")  # 기본 응답
                
                print(f"봇: {response}")
                
            except KeyboardInterrupt:
                print("\n봇: 프로그램이 종료됩니다. 안녕히 가세요!")
                break
            except Exception as error:
                print(f"봇: 오류가 발생했습니다: {error}")
                print("봇: 다시 시도해주세요.")

def main():
    """메인 함수 - 챗봇을 실행합니다."""
    chatbot = SimpleChatbot()
    chatbot.chat()

if __name__ == "__main__":
    main() 