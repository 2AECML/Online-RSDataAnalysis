# data_manager.py
import os
from pyproj import Proj, transform


# 定义全局变量 DATA_PATH
DATA_PATH = 'D:/VSCode/Commission/20240902/data/'

BAND_MAP = {
    'Landsat': {
        'coastal': '1',
        'blue': '2',
        'green': '3',
        'red': '4',
        'nir': '5',
        'swir1': '6',
        'swir2': '7',
        'pan': '8',
        'cirrus': '9',
        'tir1': '10',
        'tir2': '11'
    },
    'Sentinel': {
        'coastal': '1',
        'blue': '2',
        'green': '3',
        'red': '4',
        're1': '5',
        're2': '6',
        're3': '7',
        'nir': '8',
        'nnir': '8A',
        'wv': '9',
        'cirrus': '10',
        'swir1': '11',
        'swir2': '12',
    },
    'MODIS': {

    }
}


def get_available_dates(image_type: str) -> list[dict]:
    """
    获取指定影像类型中的可用年份与月份

    参数:
        image_type: 图像类型，如 'Landsat'

    返回:
        表示可用年份于月份的字典列表，如{'year': 2024, 'month': 10}
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


def get_available_images(image_type: str, date: str) -> list:
    """
    获得可用图像列表

    参数:
        image_type: 图像类型，如 'Landsat'
        date: 时间标识，如202410
    
    返回:
        可用图像文件名列表
    """
    path = os.path.join(DATA_PATH, image_type, date)

    if not os.path.isdir(path):
        raise ValueError(f'目录 "{path}" 不存在')

    # 获取目录下的所有文件
    images = os.listdir(path)

    # 过滤只返回文件，不包括子目录
    images = [f for f in images if os.path.isfile(os.path.join(path, f))]
    
    return images

    
def get_band_files(image_type: str, date: str, bands: set) -> dict:
    """
    获得指定波段文件路径

    参数:
        image_type: 图像类型，如 'Landsat'
        date: 时间标识，如202410
        bands: 集合，指定指数计算所需的波段名称，如 {'green', 'swir1', 'nir'}
    
    返回:
        对应波段文件路径字典
    """
    # 根据时间和图像类型构建文件夹路径
    folder = os.path.join(DATA_PATH, image_type, date)
    folder = os.path.normpath(folder)

    print(folder)

    abbreviation = get_abbreviation(image_type)

    # 获取当前图像类型的波段号
    if image_type not in BAND_MAP:
        raise ValueError(f"Unsupported image type: {image_type}")
    
    bands_with_numbers = BAND_MAP[image_type]

    # 根据传入的波段名称集合，构建波段文件路径
    band_files = {}
    for band_name in bands:
        if band_name in bands_with_numbers:
            band_number = bands_with_numbers[band_name]
            band_files[band_name] = os.path.join(folder, f"{abbreviation}_{date}_B{band_number}.TIF")
        else:
            raise ValueError(f"Unsupported band: {band_name} for image type: {image_type}")

    return band_files


def get_abbreviation(image_type: str) -> str:
    """
    获取图像类型的简称

    参数:
        image_type: 图像类型

    返回:
        该图像类型对应的简称
    """
    if (image_type == 'Landsat'): 
        return 'LAND'
    elif (image_type == 'MODIS'):
        return 'MODS'
    elif (image_type == 'Sentinel'):
        return 'SENT'
    

def convert_coordinates(src_crs: str, target_crs: str, coords: list) -> list:
    """
    将坐标从一个坐标系转换为另一个坐标系。

    参数:
        src_crs: 原始坐标系的 EPSG 代码，例如 'epsg:4326'
        target_crs: 目标坐标系的 EPSG 代码，例如 'epsg:32649'
        coords: 坐标列表，格式为 [[longitude, latitude], ...]

    返回:
        目标坐标系的坐标列表，格式为 [[easting, northing], ...]
    """
    # 定义坐标系
    wgs84 = Proj(src_crs)  # 原始坐标系
    target = Proj(target_crs)  # 目标坐标系

    # 转换坐标
    converted_coords = [transform(wgs84, target, lon, lat) for lon, lat in coords]
    return converted_coords

