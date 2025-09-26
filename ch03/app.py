#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask 웹 기반 챗봇 애플리케이션
웹 브라우저에서 챗봇과 대화할 수 있는 인터페이스를 제공합니다.
"""

from flask import Flask, render_template, request, jsonify
import random
from datetime import datetime
import os

app = Flask(__name__)

class WebChatbot:
    """웹용 챗봇 클래스"""
    
    def __init__(self):
        """챗봇 초기화 - 대화 규칙과 패턴을 설정합니다."""
        # 대화 규칙을 딕셔너리로 저장 (키워드: 응답)
        self.conversation_rules = {
            '안녕': ['안녕하세요!', '반갑습니다!', '안녕하세요, 무엇을 도와드릴까요?'],
            '이름': ['제 이름은 WebBot입니다.', '저는 WebBot이라고 해요!'],
            '날씨': ['오늘 날씨는 어떤가요?', '날씨 정보를 확인해보시는 건 어떨까요?'],
            '시간': ['현재 시간을 확인해보세요!', '시계를 확인해보시는 건 어떨까요?'],
            '도움': ['무엇을 도와드릴까요?', '질문이 있으시면 언제든 말씀해주세요!'],
            '감사': ['천만에요!', '도움이 되어서 기뻐요!', '별 말씀을요!'],
            '잘가': ['안녕히 가세요!', '다음에 또 만나요!', '좋은 하루 되세요!'],
            '웹': ['웹에서 대화할 수 있어서 편리하죠!', '웹 인터페이스가 마음에 드시나요?'],
            '파이썬': ['파이썬으로 만들어진 챗봇입니다!', '파이썬은 정말 멋진 언어죠!'],
            'flask': ['Flask로 웹 서버를 구축했습니다!', 'Flask는 가벼운 웹 프레임워크예요!']
        }
        
        # 기본 응답 (규칙에 맞지 않을 때)
        self.default_responses = [
            '죄송해요, 이해하지 못했어요.',
            '다른 말로 표현해주실 수 있나요?',
            '무엇을 도와드릴까요?',
            '흥미로운 질문이네요!',
            '더 구체적으로 말씀해주세요.'
        ]
    
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
            # 여러 응답 중에서 랜덤하게 선택
            return random.choice(self.conversation_rules[keyword])
        else:
            return random.choice(self.default_responses)

# 챗봇 인스턴스 생성
chatbot = WebChatbot()

@app.route('/')
def index():
    """메인 페이지를 렌더링합니다."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """챗봇과의 대화를 처리합니다."""
    try:
        # JSON 데이터에서 사용자 메시지 추출
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        # 빈 메시지 처리
        if not user_message:
            return jsonify({
                'response': '메시지를 입력해주세요!',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
        
        # 입력 전처리
        processed_input = chatbot.preprocess_user_input(user_message)
        
        # 매칭되는 키워드 찾기
        matching_keyword = chatbot.find_matching_keyword(processed_input)
        
        # 응답 생성
        if matching_keyword:
            bot_response = chatbot.get_response(matching_keyword)
        else:
            bot_response = chatbot.get_response("")  # 기본 응답
        
        # 현재 시간
        current_time = datetime.now().strftime('%H:%M:%S')
        
        return jsonify({
            'response': bot_response,
            'timestamp': current_time
        })
        
    except Exception as error:
        # 오류 처리
        return jsonify({
            'response': f'오류가 발생했습니다: {str(error)}',
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }), 500

@app.route('/health')
def health_check():
    """서버 상태 확인용 엔드포인트"""
    return jsonify({'status': 'healthy', 'message': '챗봇 서버가 정상 작동 중입니다.'})

if __name__ == '__main__':
    # 개발 서버 실행 (디버그 모드 활성화)
    app.run(debug=True, host='0.0.0.0', port=5000) 