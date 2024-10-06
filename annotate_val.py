import os
import tkinter as tk
from PIL import Image, ImageTk
import glob

# 定义类别名称和映射
class_names = ['火箭兵', '工兵', '普通士兵', '指挥官']
class_dict = {name: idx for idx, name in enumerate(class_names)}

# 设置图片和标签目录
image_dir = 'dataset/images/val'    # 验证集图片目录
label_dir = 'dataset/labels/val'    # 验证集标签保存目录
os.makedirs(label_dir, exist_ok=True)

# 设置最大显示尺寸
MAX_WIDTH = 800
MAX_HEIGHT = 600

# 获取图片列表
image_files = glob.glob(os.path.join(image_dir, '*.jpg'))
image_files += glob.glob(os.path.join(image_dir, '*.png'))
image_files += glob.glob(os.path.join(image_dir, '*.jpeg'))
image_files.sort()

class AnnotationTool:
    def __init__(self, master):
        self.master = master
        self.master.title("标注工具 - 验证集")

        self.image_index = 0
        self.total_images = len(image_files)
        self.bbox_list = []
        self.current_image = None
        self.tkimg = None

        # 初始化缩放比例
        self.resize_ratio = 1

        # 创建界面组件
        self.canvas = tk.Canvas(master, cursor='tcross')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.btn_prev = tk.Button(master, text='上一张 (a)', command=self.prev_image)
        self.btn_prev.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_next = tk.Button(master, text='下一张 (d)', command=self.next_image)
        self.btn_next.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_undo = tk.Button(master, text='撤销 (z)', command=self.undo_bbox)
        self.btn_undo.pack(side=tk.LEFT, padx=5, pady=5)

        self.lbl_info = tk.Label(master, text='')
        self.lbl_info.pack(side=tk.RIGHT, padx=5, pady=5)

        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        self.master.bind('<Key>', self.on_key_press)

        # 初始化变量
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.rect_list = []

        # 加载第一张图片
        self.load_image()

    def load_image(self):
        if self.image_index < 0 or self.image_index >= self.total_images:
            return
        img_path = image_files[self.image_index]
        original_image = Image.open(img_path)
        self.original_img_w, self.original_img_h = original_image.size

        # 计算缩放比例
        ratio = min(MAX_WIDTH / self.original_img_w, MAX_HEIGHT / self.original_img_h, 1)
        new_width = int(self.original_img_w * ratio)
        new_height = int(self.original_img_h * ratio)
        self.resize_ratio = ratio  # 保存缩放比例

        # 缩放图片
        if ratio < 1:
            self.current_image = original_image.resize((new_width, new_height), Image.LANCZOS)
        else:
            self.current_image = original_image

        self.img_w, self.img_h = self.current_image.size
        self.tkimg = ImageTk.PhotoImage(self.current_image)
        self.canvas.config(width=self.img_w, height=self.img_h)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tkimg)
        self.bbox_list = []
        self.rect_list = []
        self.lbl_info.config(text=f"图片 {self.image_index+1}/{self.total_images}: {os.path.basename(img_path)}")

        # 如果存在已保存的标注，加载并显示
        label_path = os.path.join(label_dir, os.path.basename(img_path).rsplit('.', 1)[0] + '.txt')
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    class_idx, x_center, y_center, width, height = map(float, line.strip().split())
                    # 恢复到原始尺寸坐标
                    x_center *= self.original_img_w
                    y_center *= self.original_img_h
                    width *= self.original_img_w
                    height *= self.original_img_h
                    # 缩放到显示尺寸坐标
                    x_center *= self.resize_ratio
                    y_center *= self.resize_ratio
                    width *= self.resize_ratio
                    height *= self.resize_ratio
                    xmin = x_center - width / 2
                    ymin = y_center - height / 2
                    xmax = x_center + width / 2
                    ymax = y_center + height / 2
                    bbox = (xmin, ymin, xmax, ymax, int(class_idx))
                    self.bbox_list.append(bbox)
                    self.draw_bbox(bbox)

    def draw_bbox(self, bbox):
        xmin, ymin, xmax, ymax, class_idx = bbox
        rect = self.canvas.create_rectangle(xmin, ymin, xmax, ymax, outline='red', width=2)
        self.canvas.create_text(xmin, ymin - 10, anchor=tk.NW, text=class_names[class_idx], fill='red')
        self.rect_list.append(rect)

    def save_annotations(self):
        if self.bbox_list:
            img_path = image_files[self.image_index]
            label_file = os.path.join(label_dir, os.path.basename(img_path).rsplit('.', 1)[0] + '.txt')
            with open(label_file, 'w') as f:
                for bbox in self.bbox_list:
                    xmin, ymin, xmax, ymax, class_idx = bbox
                    # 将坐标映射回原始图片尺寸
                    xmin /= self.resize_ratio
                    ymin /= self.resize_ratio
                    xmax /= self.resize_ratio
                    ymax /= self.resize_ratio
                    # 计算归一化坐标
                    x_center = ((xmin + xmax) / 2) / self.original_img_w
                    y_center = ((ymin + ymax) / 2) / self.original_img_h
                    width = (xmax - xmin) / self.original_img_w
                    height = (ymax - ymin) / self.original_img_h
                    annotation = f"{class_idx} {x_center} {y_center} {width} {height}\n"
                    f.write(annotation)
            print(f'标注已保存至 {label_file}')
        else:
            print('没有标注信息，无需保存。')

    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_mouse_move(self, event):
        curX, curY = event.x, event.y
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_mouse_up(self, event):
        end_x, end_y = event.x, event.y
        xmin = min(self.start_x, end_x)
        xmax = max(self.start_x, end_x)
        ymin = min(self.start_y, end_y)
        ymax = max(self.start_y, end_y)
        # 输入类别索引
        class_idx = self.select_class()
        if class_idx is not None:
            bbox = (xmin, ymin, xmax, ymax, class_idx)
            self.bbox_list.append(bbox)
            self.rect_list.append(self.rect)
            self.canvas.create_text(xmin, ymin - 10, anchor=tk.NW, text=class_names[class_idx], fill='red')
        else:
            self.canvas.delete(self.rect)
        self.rect = None

    def select_class(self):
        # 弹出对话框选择类别
        top = tk.Toplevel(self.master)
        top.title('选择类别')
        tk.Label(top, text='请选择类别：').pack()
        var = tk.IntVar()
        var.set(0)
        for idx, name in enumerate(class_names):
            tk.Radiobutton(top, text=f'{idx}: {name}', variable=var, value=idx).pack(anchor=tk.W)
        def on_ok():
            top.destroy()
        tk.Button(top, text='确定', command=on_ok).pack()
        self.master.wait_window(top)
        return var.get()

    def prev_image(self):
        self.save_annotations()
        if self.image_index > 0:
            self.image_index -= 1
            self.canvas.delete("all")
            self.load_image()

    def next_image(self):
        self.save_annotations()
        if self.image_index < self.total_images - 1:
            self.image_index += 1
            self.canvas.delete("all")
            self.load_image()
        else:
            print('所有图片均已标注完成。')

    def undo_bbox(self):
        if self.bbox_list:
            self.bbox_list.pop()
            self.canvas.delete(self.rect_list.pop())
        else:
            print('没有可以撤销的标注。')

    def on_key_press(self, event):
        if event.char == 'a':
            self.prev_image()
        elif event.char == 'd':
            self.next_image()
        elif event.char == 'z':
            self.undo_bbox()
        elif event.char == 'q':
            self.save_annotations()
            self.master.quit()

def main():
    root = tk.Tk()
    tool = AnnotationTool(root)
    root.mainloop()

if __name__ == '__main__':
    main()
