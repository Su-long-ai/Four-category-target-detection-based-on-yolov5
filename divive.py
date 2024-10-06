import os
import shutil
import random

# 设置随机种子，保证每次运行结果一致
random.seed(42)

# 定义源数据集路径和目标数据集路径
source_folder = 'photos'
target_folder = 'dataset'

# 定义数据集划分比例
train_ratio = 0.8  # 80% 作为训练集，20% 作为验证集

# 定义类别名称与索引的映射
class_mapping = {
    'class 1': '火箭兵',
    'class 2': '工兵',
    'class 3': '普通士兵',
    'class 4': '指挥官'
}

# 创建目标文件夹结构
def create_folder_structure(base_path):
    folders = [
        os.path.join(base_path, 'images', 'train'),
        os.path.join(base_path, 'images', 'val'),
        os.path.join(base_path, 'labels', 'train'),
        os.path.join(base_path, 'labels', 'val')
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

# 复制并划分数据集
def split_dataset(source_folder, target_folder, train_ratio):
    for class_dir in os.listdir(source_folder):
        class_path = os.path.join(source_folder, class_dir)
        if os.path.isdir(class_path):
            # 获取所有图片文件
            images = [f for f in os.listdir(class_path) if f.endswith(('.jpg', '.png', '.jpeg'))]
            # 打乱数据
            random.shuffle(images)
            # 计算训练集和验证集的分界索引
            train_count = int(len(images) * train_ratio)
            train_images = images[:train_count]
            val_images = images[train_count:]
            # 获取类别索引
            class_index = list(class_mapping.keys()).index(class_dir)
            # 处理训练集
            for img_name in train_images:
                src_img_path = os.path.join(class_path, img_name)
                dst_img_path = os.path.join(target_folder, 'images', 'train', img_name)
                shutil.copyfile(src_img_path, dst_img_path)
                # 创建对应的空标签文件（如果还未标注，可以先创建空的 .txt 文件）
                label_path = os.path.join(target_folder, 'labels', 'train', img_name.replace('.jpg', '.txt').replace('.png', '.txt').replace('.jpeg', '.txt'))
                open(label_path, 'w').close()
            # 处理验证集
            for img_name in val_images:
                src_img_path = os.path.join(class_path, img_name)
                dst_img_path = os.path.join(target_folder, 'images', 'val', img_name)
                shutil.copyfile(src_img_path, dst_img_path)
                # 创建对应的空标签文件
                label_path = os.path.join(target_folder, 'labels', 'val', img_name.replace('.jpg', '.txt').replace('.png', '.txt').replace('.jpeg', '.txt'))
                open(label_path, 'w').close()

# 主函数
def main():
    create_folder_structure(target_folder)
    split_dataset(source_folder, target_folder, train_ratio)
    print("数据整理完成！")

if __name__ == "__main__":
    main()
