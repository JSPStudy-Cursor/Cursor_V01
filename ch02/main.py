import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageOps
import numpy as np
import tensorflow as tf
import os

# keras를 명확히 import
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import Flatten, Dense, Dropout
from tensorflow.keras.datasets import mnist

# 모델 파일 경로
MODEL_PATH = 'mnist_cnn.h5'

# 28x28 크기의 캔버스 설정
CANVAS_SIZE = 280  # 실제 그리는 캔버스 크기 (10배)
IMG_SIZE = 28      # 모델 입력 크기

# 모델이 없으면 자동으로 학습해서 저장하는 함수
def get_or_train_model():
    # 모델 파일이 있으면 로드
    if os.path.exists(MODEL_PATH):
        try:
            model = load_model(MODEL_PATH)
            return model
        except Exception as e:
            print('모델 로드 실패:', e)
            os.remove(MODEL_PATH)
    # 모델이 없으면 새로 학습
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

# tkinter 캔버스에서 그린 그림을 28x28 이미지로 변환하는 함수
def get_image_from_canvas(canvas, canvas_widget):
    # 캔버스 내용을 이미지로 저장
    canvas_widget.postscript(file='temp.ps', colormode='mono')
    img = Image.open('temp.ps')
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img = ImageOps.invert(img.convert('L'))  # 흑백 반전
    img = np.array(img) / 255.0
    os.remove('temp.ps')
    return img

# 예측 함수
def predict_digit(model, img):
    try:
        img = img.reshape(1, 28, 28)
        pred = model.predict(img)
        return np.argmax(pred), float(np.max(pred))
    except Exception as e:
        print('예측 오류:', e)
        return None, None

# 캔버스 초기화 함수
def clear_canvas(canvas, draw):
    canvas.delete('all')
    draw.rectangle([0, 0, CANVAS_SIZE, CANVAS_SIZE], fill='white')

# 마우스 드래그로 그림 그리기 함수
def paint(event, canvas, draw, last_pos):
    x, y = event.x, event.y
    r = 8  # 브러시 반지름
    if last_pos[0] is not None and last_pos[1] is not None:
        canvas.create_line(last_pos[0], last_pos[1], x, y, width=r*2, fill='black', capstyle=tk.ROUND, smooth=True)
        draw.line([last_pos[0], last_pos[1], x, y], fill='black', width=r*2)
    else:
        canvas.create_oval(x-r, y-r, x+r, y+r, fill='black', outline='black')
        draw.ellipse([x-r, y-r, x+r, y+r], fill='black')
    last_pos[0], last_pos[1] = x, y

def reset_last_pos(event, last_pos):
    last_pos[0], last_pos[1] = None, None

# 예측 버튼 클릭 시 동작 함수
def on_predict(model, canvas, canvas_widget, result_label, draw):
    img = get_image_from_canvas(canvas_widget, canvas_widget)
    pred, conf = predict_digit(model, img)
    if pred is not None:
        result_label.config(text=f'예측 결과: {pred} (신뢰도: {conf:.2f})')
    else:
        result_label.config(text='예측 실패')

# 메인 함수
def main():
    # 모델 준비
    model = get_or_train_model()

    # tkinter 윈도우 생성
    root = tk.Tk()
    root.title('손글씨 숫자 인식기')

    # 캔버스와 이미지 드로잉 객체 생성
    canvas = tk.Canvas(root, width=CANVAS_SIZE, height=CANVAS_SIZE, bg='white')
    canvas.pack()
    pil_img = Image.new('L', (CANVAS_SIZE, CANVAS_SIZE), 'white')
    draw = ImageDraw.Draw(pil_img)
    last_pos = [None, None]

    # 마우스 이벤트 바인딩
    canvas.bind('<B1-Motion>', lambda e: paint(e, canvas, draw, last_pos))
    canvas.bind('<ButtonRelease-1>', lambda e: reset_last_pos(e, last_pos))

    # 결과 표시 라벨
    result_label = tk.Label(root, text='숫자를 그리고 예측 버튼을 누르세요')
    result_label.pack()

    # 버튼 프레임
    btn_frame = tk.Frame(root)
    btn_frame.pack()

    # 예측 버튼
    predict_btn = tk.Button(btn_frame, text='예측', command=lambda: on_predict(model, pil_img, canvas, result_label, draw))
    predict_btn.pack(side='left')

    # 초기화 버튼
    clear_btn = tk.Button(btn_frame, text='초기화', command=lambda: clear_canvas(canvas, draw))
    clear_btn.pack(side='left')

    root.mainloop()

if __name__ == '__main__':
    main() 