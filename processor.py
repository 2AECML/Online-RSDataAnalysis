# processor.py
from typing import List, Tuple
from urllib.parse import unquote
import matplotlib
from pyproj import Transformer
import rasterio
from rasterio.mask import mask
import numpy as np
import rasterio.plot
from shapely.geometry import Polygon, mapping
import geoserver_interaction
import os
import tempfile

matplotlib.use('Agg')

OUTPUT_PATH = 'output/'

TEMP_PATH = 'temp/'

DEFAULT_CRS = 'EPSG:4326'   


def calculate_ndvi(image_type, area_code, time, coordinates):

    # 获取图像文件和多边形
    image_src, polygon = get_image_and_polygon(image_type, area_code, time, coordinates)

    # 使用rasterio打开多波段数据
    with rasterio.open(image_src) as src:
        # 使用掩模提取红色波段和近红外波段的多边形区域数据
        red_data, red_transform = mask(src, [mapping(polygon)], crop=True, indexes=4)
        nir_data, nir_transform = mask(src, [mapping(polygon)], crop=True, indexes=5)

        rasterio.plot.show(src)
    
    # 移除NoData值
    red_nodata = src.nodata
    nir_nodata = src.nodata
    
    red_data = np.where(red_data == red_nodata, np.nan, red_data)
    nir_data = np.where(nir_data == nir_nodata, np.nan, nir_data)
    
    # 计算NDVI
    ndvi = (nir_data - red_data) / (nir_data + red_data)

    print("ndvi completed")

    geoserver_layer_name = save_and_upload_result(image_src, red_transform, ndvi)
    
    return geoserver_layer_name


def calculate_ndwi(image_type, area_code, time, coordinates):

    # 获取图像文件和多边形
    image_src, polygon = get_image_and_polygon(image_type, area_code, time, coordinates)

    # 使用rasterio打开多波段数据
    with rasterio.open(image_src) as src:
        # 使用掩模提取绿色波段和近红外波段的多边形区域数据
        green_data, green_transform = mask(src, [mapping(polygon)], crop=True, indexes=3)
        nir_data, nir_transform = mask(src, [mapping(polygon)], crop=True, indexes=5)
    
    # 移除NoData值
    green_nodata = src.nodata
    nir_nodata = src.nodata
    
    green_data = np.where(green_data == green_nodata, np.nan, green_data)
    nir_data = np.where(nir_data == nir_nodata, np.nan, nir_data)

    # 计算NDWI
    ndwi = (green_data - nir_data) / (green_data + nir_data)

    print("ndwi completed")

    geoserver_layer_name = save_and_upload_result(image_src, green_transform, ndwi)
    
    return geoserver_layer_name


def calculate_ndbi(image_type, area_code, time, coordinates):

    # 获取图像文件和多边形
    image_src, polygon = get_image_and_polygon(image_type, area_code, time, coordinates)

    # 使用rasterio打开多波段数据
    with rasterio.open(image_src) as src:
        # 使用掩模提取短波红外2波段和近红外波段的多边形区域数据
        swir2_data, swir2_transform = mask(src, [mapping(polygon)], crop=True, indexes=7)
        nir_data, nir_transform = mask(src, [mapping(polygon)], crop=True, indexes=5)
    
    # 移除NoData值
    swir2_nodata = src.nodata
    nir_nodata = src.nodata
    
    nir_data = np.where(nir_data == nir_nodata, np.nan, nir_data)
    swir2_data = np.where(swir2_data == swir2_nodata, np.nan, swir2_data)
    
    # 计算NDBI
    ndbi = (swir2_data - nir_data) / (swir2_data + nir_data)

    print("ndbi completed")

    geoserver_layer_name = save_and_upload_result(image_src, swir2_transform, ndbi)
    
    return geoserver_layer_name


def calculate_cdi(image_type, area_code, time, coordinates):

    # 获取图像文件和多边形
    image_src, polygon = get_image_and_polygon(image_type, area_code, time, coordinates)

    # 使用rasterio打开多波段数据
    with rasterio.open(image_src) as src:
        # 使用掩模提取蓝色波段、红色波段和近红外波段的多边形区域数据
        blue_data, blue_transform = mask(src, [mapping(polygon)], crop=True, indexes=2)
        red_data, red_transform = mask(src, [mapping(polygon)], crop=True, indexes=4)
        nir_data, nir_transform = mask(src, [mapping(polygon)], crop=True, indexes=5)
    
    # 移除NoData值
    blue_nodata = src.nodata
    red_nodata = src.nodata
    nir_nodata = src.nodata
    
    blue_data = np.where(blue_data == blue_nodata, np.nan, blue_data)
    red_data = np.where(red_data == red_nodata, np.nan, red_data)
    nir_data = np.where(nir_data == nir_nodata, np.nan, nir_data)

    # 计算CDI
    cdi = (blue_data + red_data + nir_data) / 3

    print("cdi completed")

    geoserver_layer_name = save_and_upload_result(image_src, red_transform, cdi)
    
    return geoserver_layer_name


def match_file(image_type, area_code, time):
    # 基础路径
    data_path = r'D:\VSCode\Commission\20240902\data'

    # 构造要查找的路径
    target_path = os.path.join(data_path, image_type, str(area_code), str(time))

    # 检查目标路径是否存在
    if os.path.exists(target_path):
        print(f"找到匹配的文件夹: {target_path}")

        # 列出所有以 .TIF 结尾的文件
        tif_files = [os.path.join(target_path, file) for file in os.listdir(target_path) if file.endswith('.TIF')]

        # 判断 .TIF 文件的数量
        if len(tif_files) > 1:
            raise ValueError(f"发现多个 .TIF 文件 ({len(tif_files)})，请检查文件夹：{target_path}")
        elif len(tif_files) == 1:
            print(f"找到唯一的 .TIF 文件: {tif_files[0]}")
            return tif_files[0]
        else:
            print("未找到 .TIF 文件")
            return None
    else:
        print(f"未找到匹配的文件夹: {target_path}")
        return None


def create_polygon_from_points(points):
    # 将点列表转换为Shapely多边形
    polygon = Polygon(points)
    return polygon


def transform_coordinates(coords: List[Tuple[float, float]], src_crs: str, dest_crs: str) -> List[Tuple[float, float]]:
    # 创建 Transformer 对象
    transformer = Transformer.from_crs(src_crs, dest_crs, always_xy=True)
    # 转换坐标
    transformed_coords = [transformer.transform(x, y) for x, y in coords]
    return transformed_coords


def get_image_and_polygon(image_type, area_code, time, coordinates):

    # 匹配图像文件
    image_src = match_file(image_type, area_code, time)

    print("image_src: ", image_src)

    # 从点创建多边形
    polygon = create_polygon_from_points(coordinates)

    print("polygon: ", polygon)

    return image_src, polygon


def get_raster_crs(image_src):
    with rasterio.open(image_src) as src:
        return src.crs


def get_raster_bounds(image_src):
    with rasterio.open(image_src) as src:
        return src.bounds


def get_polygon_width_and_height(polygon: Polygon):
    
    # 获取多边形的边界框
    minx, miny, maxx, maxy = polygon.bounds
    
    # 计算宽度和高度
    width = maxx - minx
    height = maxy - miny

    print(width, height)
    
    # 返回包含宽度和高度的字典
    return {
        'width': width,
        'height': height
    }


def save_and_upload_result(image_src, transform, data):
    if not os.path.exists(TEMP_PATH):
        os.makedirs(TEMP_PATH)

    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as temp_file:
        temp_filename = temp_file.name

    # 计算 NDVI 数据的宽度和高度
    if data.ndim == 3:
        data_width = data.shape[2]
        data_height = data.shape[1]
    else:
        data_width = data.shape[1]
        data_height = data.shape[0]

    print("data width:", data_width)
    print("data height:", data_height)

    # 保存 NDVI 数据为临时 TIF 文件
    with rasterio.open(image_src) as src:

        # 设置新的元数据
        metadata = {
            'driver': 'GTiff',
            'count': 1,  # 单波段
            'dtype': 'float32',
            'width': data_width,
            'height': data_height,
            'crs': src.crs.to_proj4(),
            'transform': transform,
            'nodata': 0.0,
        }
        with rasterio.open(temp_filename, 'w', **metadata) as dst:
            dst.write(data.astype(rasterio.float32), 1)

    print(f"data saved to temporary TIF file: {temp_filename}")

    # 使用上传函数将临时 TIF 文件上传到 GeoServer
    try:
        geoserver_layername = geoserver_interaction.upload_geotiff(temp_filename)
        print(f"Temporary TIF file uploaded to GeoServer: {temp_filename}")
    except Exception as e:
        print(f"Error uploading TIF file to GeoServer: {e}")

    # 清理临时文件
    os.remove(temp_filename)

    return geoserver_layername

