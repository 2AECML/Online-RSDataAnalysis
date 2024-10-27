import os
from pyproj import Proj, transform

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

    
def get_band_files(image_type, time, bands):
    """
    返回指定波段文件路径
    :param image_type: 图像类型，如 'Landsat'
    :param time: 时间标识
    :param bands: 字典，指定指数计算所需的波段 {波段名称: 波段号}
                  例如，NDVI 可传 {'red': 4, 'nir': 5}
    :return: 对应波段文件路径字典
    """
    # 根据时间和图像类型构建文件夹路径
    folder = os.path.join(DATA_PATH, image_type, time)
    folder = os.path.normpath(folder)

    print(folder)

    abbreviation = getAbbreviation(image_type)
    
    # 根据传入的波段字典，构建波段文件路径
    band_files = {}
    for band_name, band_number in bands.items():
        band_files[band_name] = os.path.join(folder, f"{abbreviation}_{time}_B{band_number}.TIF")

    return band_files


def getAbbreviation(image_type):
    if (image_type == 'Landsat'): 
        return 'LAND'
    elif (image_type == 'MODIS'):
        return 'MODS'
    elif (image_type == 'Sentinel'):
        return 'SENT'
    

def convert_coordinates(src_crs, target_crs, coords):
    """
    将坐标从一个坐标系转换为另一个坐标系。

    参数:
        src_crs (str): 原始坐标系的 EPSG 代码，例如 'epsg:4326'。
        target_crs (str): 目标坐标系的 EPSG 代码，例如 'epsg:32649'。
        coords (list): 坐标列表，格式为 [[longitude, latitude], ...].

    返回:
        list: 目标坐标系的坐标列表，格式为 [[easting, northing], ...].
    """
    # 定义坐标系
    wgs84 = Proj(src_crs)  # 原始坐标系
    target = Proj(target_crs)  # 目标坐标系

    # 转换坐标
    converted_coords = [transform(wgs84, target, lon, lat) for lon, lat in coords]
    return converted_coords

