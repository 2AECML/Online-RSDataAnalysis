import os

# 定义全局变量 DATA_PATH
DATA_PATH = 'D:/VSCode/Commission/20240902/data/'

def get_available_dates(image_type):
    """
    获取指定影像类型中的可用年份与月份
    """

    path = os.path.join(DATA_PATH, image_type)
    
    if not os.path.isdir(path):
        raise ValueError(f'目录 "{path}" 不存在')

    dates = set()
    
    # 遍历区域目录中的每个子目录
    for subdir in os.listdir(path):
        subdir_path = os.path.join(path, subdir)
        if os.path.isdir(subdir_path):
            # 提取年份和月份
            try:
                year = subdir[:4]  # 从目录名称的前4位提取年份
                month = subdir[4:6]  # 从目录名称的第5到第6位提取月份
                dates.add((year, month))  # 使用元组 (year, month) 作为集合的元素
            except IndexError:
                print(f'警告: 目录名称 "{subdir}" 格式不符合预期')

    # 将集合中的元组转换为字典列表
    image_dates = [{'year': year, 'month': month} for year, month in sorted(dates)]

    return image_dates


def get_available_images(image_type, date) :
    path = os.path.join(DATA_PATH, image_type, date)

    if not os.path.isdir(path):
        raise ValueError(f'目录 "{path}" 不存在')

    # 获取目录下的所有文件
    images = os.listdir(path)

    # 过滤只返回文件，不包括子目录
    images = [f for f in images if os.path.isfile(os.path.join(path, f))]
    
    return images

    
