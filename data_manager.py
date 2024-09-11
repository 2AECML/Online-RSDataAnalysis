import os

# 定义全局变量 DATA_PATH
DATA_PATH = 'D:/VSCode/Commission/20240902/data/'

def get_available_dates(image_type, area_code):
    """
    获取指定影像类型和区域代码中的可用年份与月份
    """
    image_data = []
    area_path = os.path.join(DATA_PATH, image_type, area_code)
    
    if not os.path.isdir(area_path):
        raise ValueError(f'区域目录 "{area_path}" 不存在')

    dates = set()
    
    # 遍历区域目录中的每个子目录
    for subdir in os.listdir(area_path):
        subdir_path = os.path.join(area_path, subdir)
        if os.path.isdir(subdir_path):
            # 提取年份和月份
            try:
                year = subdir[:4]  # 从目录名称的前4位提取年份
                month = subdir[4:6]  # 从目录名称的第5到第6位提取月份
                dates.add((year, month))  # 使用元组 (year, month) 作为集合的元素
            except IndexError:
                print(f'警告: 目录名称 "{subdir}" 格式不符合预期')

    # 将集合中的元组转换为字典列表
    image_data = [{'year': year, 'month': month} for year, month in sorted(dates)]

    return image_data


def get_available_area_codes(image_type):
    """
    获取指定影像类型中的可用 area_code 范围
    """
    area_codes = set()
    image_path = os.path.join(DATA_PATH, image_type)
    
    if not os.path.isdir(image_path):
        raise ValueError(f'影像类型目录 "{image_path}" 不存在')

    # 遍历影像类型目录中的每个子目录
    for subdir in os.listdir(image_path):
        subdir_path = os.path.join(image_path, subdir)
        if os.path.isdir(subdir_path):
            # 将 area_code 添加到集合中
            area_codes.add(subdir)

    # 返回一个包含 area_code 的排序列表
    return sorted(area_codes)


# print(get_available_area_codes('landsat8'))
# print(get_available_dates('landsat8', '118041'))