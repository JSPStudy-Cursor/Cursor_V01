import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("이미지 뷰어")
        self.root.geometry("800x600")
        
        # 현재 이미지 정보
        self.current_image = None
        self.current_image_path = None
        self.image_list = []
        self.current_index = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        # 메뉴바 생성
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="이미지 열기", command=self.open_image)
        file_menu.add_command(label="폴더 열기", command=self.open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.quit)
        
        # 도구 메뉴
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도구", menu=tools_menu)
        tools_menu.add_command(label="이전 이미지", command=self.prev_image)
        tools_menu.add_command(label="다음 이미지", command=self.next_image)
        tools_menu.add_command(label="이미지 정보", command=self.show_image_info)
        
        # 메인 프레임
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 이미지 표시 영역
        self.image_frame = tk.Frame(main_frame, bg="white", relief=tk.SUNKEN, bd=2)
        self.image_frame.pack(fill=tk.BOTH, expand=True)
        
        # 이미지 라벨
        self.image_label = tk.Label(self.image_frame, text="이미지를 선택하세요", 
                                   font=("Arial", 14), bg="white")
        self.image_label.pack(expand=True)
        
        # 상태바
        self.status_bar = tk.Label(self.root, text="준비됨", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 키보드 단축키 바인딩
        self.root.bind("<Left>", lambda e: self.prev_image())
        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("<Control-o>", lambda e: self.open_image())
        self.root.bind("<Control-f>", lambda e: self.open_folder())
        
    def open_image(self):
        """단일 이미지 파일 열기"""
        file_path = filedialog.askopenfilename(
            title="이미지 파일 선택",
            filetypes=[
                ("이미지 파일", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                ("모든 파일", "*.*")
            ]
        )
        
        if file_path:
            self.load_image(file_path)
            
    def open_folder(self):
        """폴더에서 이미지 파일들 로드"""
        folder_path = filedialog.askdirectory(title="이미지 폴더 선택")
        
        if folder_path:
            self.image_list = []
            image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')
            
            for file in os.listdir(folder_path):
                if file.lower().endswith(image_extensions):
                    self.image_list.append(os.path.join(folder_path, file))
            
            if self.image_list:
                self.current_index = 0
                self.load_image(self.image_list[0])
                self.status_bar.config(text=f"폴더 로드됨: {len(self.image_list)}개 이미지")
            else:
                messagebox.showwarning("경고", "선택한 폴더에 이미지 파일이 없습니다.")
                
    def load_image(self, image_path):
        """이미지 로드 및 표시"""
        try:
            # 이미지 열기
            image = Image.open(image_path)
            
            # 이미지 크기 조정
            display_size = (700, 500)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # PhotoImage로 변환
            photo = ImageTk.PhotoImage(image)
            
            # 이미지 표시
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # 참조 유지
            
            self.current_image = image
            self.current_image_path = image_path
            
            # 상태바 업데이트
            filename = os.path.basename(image_path)
            size = f"{image.width} x {image.height}"
            self.status_bar.config(text=f"파일: {filename} | 크기: {size}")
            
        except Exception as e:
            messagebox.showerror("오류", f"이미지를 로드할 수 없습니다: {str(e)}")
            
    def prev_image(self):
        """이전 이미지"""
        if self.image_list and self.current_index > 0:
            self.current_index -= 1
            self.load_image(self.image_list[self.current_index])
            
    def next_image(self):
        """다음 이미지"""
        if self.image_list and self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.load_image(self.image_list[self.current_index])
            
    def show_image_info(self):
        """이미지 정보 표시"""
        if self.current_image:
            info = f"파일명: {os.path.basename(self.current_image_path)}\n"
            info += f"크기: {self.current_image.width} x {self.current_image.height}\n"
            info += f"모드: {self.current_image.mode}\n"
            info += f"형식: {self.current_image.format}"
            
            messagebox.showinfo("이미지 정보", info)
        else:
            messagebox.showwarning("경고", "표시할 이미지가 없습니다.")

def main():
    root = tk.Tk()
    app = ImageViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()

