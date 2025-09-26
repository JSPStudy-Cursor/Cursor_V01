import os
import numpy as np
from flask import Flask, request, jsonify, render_template
from PIL import Image, ImageOps
import base64
import io
import tensorflow as tf
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import Flatten, Dense, Dropout
from tensorflow.keras.datasets import mnist

# 모델 파일 경로
MODEL_PATH = 'mnist_cnn.h5'
IMG_SIZE = 28

# 모델 준비 함수
def get_or_train_model():
    if os.path.exists(MODEL_PATH):
        try:
            model = load_model(MODEL_PATH)
            return model
        except Exception as e:
            print('모델 로드 실패:', e)
            os.remove(MODEL_PATH)
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0
    model = Sequential([
        Flatten(input_shape=(28, 28)),
        Dense(128, activation='relu'),
        Dropout(0.2),
        Dense(10, activation='softmax')
    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    model.fit(x_train, y_train, epochs=3, validation_data=(x_test, y_test), verbose=2)
    model.save(MODEL_PATH)
    return model

# base64 이미지를 28x28 numpy 배열로 변환하는 함수
def preprocess_image(data_url):
    try:
        # data:image/png;base64,... 부분 제거
        header, encoded = data_url.split(',', 1)
        img_bytes = base64.b64decode(encoded)
        img = Image.open(io.BytesIO(img_bytes)).convert('L')
        img = ImageOps.invert(img)
        img = img.resize((IMG_SIZE, IMG_SIZE))
        img = np.array(img) / 255.0
        return img
    except Exception as e:
        print('이미지 전처리 오류:', e)
        return None

# 예측 함수
def predict_digit(model, img):
    try:
        img = img.reshape(1, 28, 28)
        pred = model.predict(img)
        return int(np.argmax(pred)), float(np.max(pred))
    except Exception as e:
        print('예측 오류:', e)
        return None, None

# Flask 앱 생성
app = Flask(__name__)
model = get_or_train_model()

# 메인 페이지 라우트
@app.route('/')
def index():
    return render_template('index.html')

# 예측 API 라우트
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    img_data = data.get('image')
    if not img_data:
        return jsonify({'error': '이미지 데이터가 없습니다.'}), 400
    img = preprocess_image(img_data)
    if img is None:
        return jsonify({'error': '이미지 전처리 실패'}), 400
    pred, conf = predict_digit(model, img)
    if pred is None:
        return jsonify({'error': '예측 실패'}), 500
    return jsonify({'result': pred, 'confidence': round(conf if conf is not None else 0.0, 2)})

if __name__ == '__main__':
    app.run(debug=True) 