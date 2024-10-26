# processor.py
import data_manager
import matplotlib
import rasterio
from rasterio.mask import mask
import numpy as np
import rasterio.plot
from shapely.geometry import Polygon
import geoserver_interaction
import os
import tempfile

matplotlib.use('Agg')

DATA_PATH = 'data/'

OUTPUT_PATH = 'output/'

TEMP_PATH = 'temp/'

DEFAULT_CRS = 'EPSG:4326'


def calculate_ndvi(image_type, time, coordinates):
    
    bands = {'red': 4, 'nir': 5}

    # 获取波段文件
    band_files = data_manager.get_band_files(image_type, time, bands)

    # 获取多边形
    polygon = create_polygon_from_points(coordinates)

    # 使用rasterio打开红色波段和近红外波段
    with rasterio.open(band_files['red']) as red_src:
        # 使用掩模提取红色波段的多边形区域数据
        red_data, red_transform = mask(red_src, [polygon], crop=True)
        red_nodata = red_src.nodata

    with rasterio.open(band_files['nir']) as nir_src:
        # 使用掩模提取近红外波段的多边形区域数据
        nir_data, nir_transform = mask(nir_src, [polygon], crop=True)
        nir_nodata = nir_src.nodata
    
    # 移除 NoData 值
    red_data = np.where(red_data == red_nodata, np.nan, red_data)
    nir_data = np.where(nir_data == nir_nodata, np.nan, nir_data)

    # 计算 NDVI 指数
    ndvi = (nir_data - red_data) / (nir_data + red_data)

    print("ndvi completed")

    geoserver_layer_name = save_and_upload_result(band_files['red'], red_transform, ndvi)
    
    return geoserver_layer_name


def calculate_ndwi(image_type, time, coordinates):
    
    bands = {'green': 3, 'nir': 5}

    # 获取波段文件
    band_files = data_manager.get_band_files(image_type, time, bands)

    # 获取多边形
    polygon = create_polygon_from_points(coordinates)

    # 使用rasterio打开绿色波段和近红外波段
    with rasterio.open(band_files['green']) as green_src:
        green_data, green_transform = mask(green_src, [polygon], crop=True)
        green_nodata = green_src.nodata

    with rasterio.open(band_files['nir']) as nir_src:
        nir_data, nir_transform = mask(nir_src, [polygon], crop=True)
        nir_nodata = nir_src.nodata
    
    # 移除 NoData 值
    green_data = np.where(green_data == green_nodata, np.nan, green_data)
    nir_data = np.where(nir_data == nir_nodata, np.nan, nir_data)

    # 计算 NDWI 指数
    ndwi = (green_data - nir_data) / (green_data + nir_data)

    print("ndwi completed")

    geoserver_layer_name = save_and_upload_result(band_files['green'], green_transform, ndwi)
    
    return geoserver_layer_name


def calculate_ndbi(image_type, time, coordinates):
    
    bands = {'swir': 6, 'nir': 5}

    # 获取波段文件
    band_files = data_manager.get_band_files(image_type, time, bands)

    # 获取多边形
    polygon = create_polygon_from_points(coordinates)

    # 使用rasterio打开SWIR波段和近红外波段
    with rasterio.open(band_files['swir']) as swir_src:
        swir_data, swir_transform = mask(swir_src, [polygon], crop=True)
        swir_nodata = swir_src.nodata

    with rasterio.open(band_files['nir']) as nir_src:
        nir_data, nir_transform = mask(nir_src, [polygon], crop=True)
        nir_nodata = nir_src.nodata
    
    # 移除 NoData 值
    swir_data = np.where(swir_data == swir_nodata, np.nan, swir_data)
    nir_data = np.where(nir_data == nir_nodata, np.nan, nir_data)

    # 计算 NDBI 指数
    ndbi = (swir_data - nir_data) / (swir_data + nir_data)

    print("ndbi completed")

    geoserver_layer_name = save_and_upload_result(band_files['swir'], swir_transform, ndbi)
    
    return geoserver_layer_name


def calculate_cdi(image_type, time, coordinates):
    
    bands = {'blue': 2, 'green': 3}

    # 获取波段文件
    band_files = data_manager.get_band_files(image_type, time, bands)

    # 获取多边形
    polygon = create_polygon_from_points(coordinates)

    # 使用rasterio打开蓝色波段和绿色波段
    with rasterio.open(band_files['blue']) as blue_src:
        blue_data, blue_transform = mask(blue_src, [polygon], crop=True)
        blue_nodata = blue_src.nodata

    with rasterio.open(band_files['green']) as green_src:
        green_data, green_transform = mask(green_src, [polygon], crop=True)
        green_nodata = green_src.nodata
    
    # 移除 NoData 值
    blue_data = np.where(blue_data == blue_nodata, np.nan, blue_data)
    green_data = np.where(green_data == green_nodata, np.nan, green_data)

    # 计算 CDI 指数
    cdi = (blue_data - green_data) / (blue_data + green_data)

    print("cdi completed")

    geoserver_layer_name = save_and_upload_result(band_files['blue'], blue_transform, cdi)
    
    return geoserver_layer_name


def create_polygon_from_points(points):
    # 将点列表转换为Shapely多边形
    polygon = Polygon(points)
    # print(polygon)
    return polygon


def save_and_upload_result(image_src, transform, data):
    if not os.path.exists(TEMP_PATH):
        os.makedirs(TEMP_PATH)

    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as temp_file:
        temp_filename = temp_file.name

    # 确保 data 是正确的形状
    if data.ndim == 4:
        data = data[0, 0, :, :]  # 提取出 (1, 1) 的维度，变成 (height, width)
    elif data.ndim == 3:
        data = data[0, :, :]  # 提取出 (bands) 的维度，变成 (height, width)

    # 计算数据的宽度和高度
    data_height, data_width = data.shape

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
        geoserver_layername = geoserver_interaction.upload_user_geotiff(temp_filename)
        print(f"Temporary TIF file uploaded to GeoServer: {temp_filename}")
    except Exception as e:
        print(f"Error uploading TIF file to GeoServer: {e}")

    # 清理临时文件
    os.remove(temp_filename)

    return geoserver_layername

    

