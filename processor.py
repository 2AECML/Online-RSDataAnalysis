# processor.py
import rasterio.transform
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


def calculate_ndwi(image_type: str, time: str, coordinates: list) -> str:
    """
    计算NDWI

    参数:
        image_type: 图像类型，如 'Landsat'
        time: 时间标识，如202410
        coordinates: 坐标列表，格式为 [[longitude, latitude], ...]

    返回:
        上传的图层在用户工作区中的完整标识，格式为 'workspace:layer_name'
    """
    
    bands = {'green', 'nir'}

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

    print("NDWI completed")

    geoserver_layer_name = save_and_upload_result(band_files['green'], green_transform, ndwi)
    
    return geoserver_layer_name


def calculate_nwi(image_type: str, time: str, coordinates: list) -> str:
    """
    计算NWI

    参数:
        image_type: 图像类型，如 'Landsat'
        time: 时间标识，如202410
        coordinates: 坐标列表，格式为 [[longitude, latitude], ...]

    返回:
        上传的图层在用户工作区中的完整标识，格式为 'workspace:layer_name'
    """
    
    bands = {'blue', 'nir', 'swir1', 'swir2'}

    # 获取波段文件
    band_files = data_manager.get_band_files(image_type, time, bands)

    # 获取多边形
    polygon = create_polygon_from_points(coordinates)

    # 使用rasterio打开相关波段
    with rasterio.open(band_files['blue']) as blue_src:
        blue_data, blue_transform = mask(blue_src, [polygon], crop=True)
        blue_nodata = blue_src.nodata

    with rasterio.open(band_files['nir']) as nir_src:
        nir_data, nir_transform = mask(nir_src, [polygon], crop=True)
        nir_nodata = nir_src.nodata

    with rasterio.open(band_files['swir1']) as swir1_src:
        swir1_data, swir1_transform = mask(swir1_src, [polygon], crop=True)
        swir1_nodata = swir1_src.nodata

    with rasterio.open(band_files['swir2']) as swir2_src:
        swir2_data, swir2_transform = mask(swir2_src, [polygon], crop=True)
        swir2_nodata = swir2_src.nodata
    
    # 移除 NoData 值
    blue_data = np.where(blue_data == blue_nodata, np.nan, blue_data)
    nir_data = np.where(nir_data == nir_nodata, np.nan, nir_data)
    swir1_data = np.where(swir1_data == swir1_nodata, np.nan, swir1_data)
    swir2_data = np.where(swir2_data == swir2_nodata, np.nan, swir2_data)

    # 计算 NWI 指数
    nwi = (blue_data - (nir_data + swir1_data + swir2_data)) / (blue_data + (nir_data + swir1_data + swir2_data))

    print("NWI completed")

    geoserver_layer_name = save_and_upload_result(band_files['blue'], blue_transform, nwi)

    return geoserver_layer_name


def calculate_awei_nsh(image_type: str, time: str, coordinates: list) -> str:
    """
    计算AWEInsh

    参数:
        image_type: 图像类型，如 'Landsat'
        time: 时间标识，如202410
        coordinates: 坐标列表，格式为 [[longitude, latitude], ...]

    返回:
        上传的图层在用户工作区中的完整标识，格式为 'workspace:layer_name'
    """

    bands = {'green', 'swir1', 'nir', 'swir2'}

    # 获取波段文件
    band_files = data_manager.get_band_files(image_type, time, bands)

    # 获取多边形
    polygon = create_polygon_from_points(coordinates)

    # 使用rasterio打开相关波段
    with rasterio.open(band_files['green']) as green_src:
        green_data, green_transform = mask(green_src, [polygon], crop=True)
        green_nodata = green_src.nodata

    with rasterio.open(band_files['swir1']) as swir1_src:
        swir1_data, swir1_transform = mask(swir1_src, [polygon], crop=True)
        swir1_nodata = swir1_src.nodata

    with rasterio.open(band_files['nir']) as nir_src:
        nir_data, nir_transform = mask(nir_src, [polygon], crop=True)
        nir_nodata = nir_src.nodata

    with rasterio.open(band_files['swir2']) as swir2_src:
        swir2_data, swir2_transform = mask(swir2_src, [polygon], crop=True)
        swir2_nodata = swir2_src.nodata

    # 移除 NoData 值
    green_data = np.where(green_data == green_nodata, np.nan, green_data)
    swir1_data = np.where(swir1_data == swir1_nodata, np.nan, swir1_data)
    nir_data = np.where(nir_data == nir_nodata, np.nan, nir_data)
    swir2_data = np.where(swir2_data == swir2_nodata, np.nan, swir2_data)

    # 计算 AWEInsh 指数
    awei_nsh = 4 * (green_data - swir1_data) - (0.25 * nir_data + 2.75 * swir2_data)

    print("AWEInsh completed")

    geoserver_layer_name = save_and_upload_result(band_files['green'], green_transform, awei_nsh)

    return geoserver_layer_name


def calculate_awei_sh(image_type: str, time: str, coordinates: list) -> str:
    """
    计算AWEIsh

    参数:
        image_type: 图像类型，如 'Landsat'
        time: 时间标识，如202410
        coordinates: 坐标列表，格式为 [[longitude, latitude], ...]

    返回:
        上传的图层在用户工作区中的完整标识，格式为 'workspace:layer_name'
    """
    
    bands = {'blue', 'green', 'nir', 'swir1', 'swir2'}

    # 获取波段文件
    band_files = data_manager.get_band_files(image_type, time, bands)

    # 获取多边形
    polygon = create_polygon_from_points(coordinates)

    # 使用rasterio打开相关波段
    with rasterio.open(band_files['blue']) as blue_src:
        blue_data, blue_transform = mask(blue_src, [polygon], crop=True)
        blue_nodata = blue_src.nodata

    with rasterio.open(band_files['green']) as green_src:
        green_data, green_transform = mask(green_src, [polygon], crop=True)
        green_nodata = green_src.nodata

    with rasterio.open(band_files['nir']) as nir_src:
        nir_data, nir_transform = mask(nir_src, [polygon], crop=True)
        nir_nodata = nir_src.nodata

    with rasterio.open(band_files['swir1']) as swir1_src:
        swir1_data, swir1_transform = mask(swir1_src, [polygon], crop=True)
        swir1_nodata = swir1_src.nodata

    with rasterio.open(band_files['swir2']) as swir2_src:
        swir2_data, swir2_transform = mask(swir2_src, [polygon], crop=True)
        swir2_nodata = swir2_src.nodata

    # 移除 NoData 值
    blue_data = np.where(blue_data == blue_nodata, np.nan, blue_data)
    green_data = np.where(green_data == green_nodata, np.nan, green_data)
    nir_data = np.where(nir_data == nir_nodata, np.nan, nir_data)
    swir1_data = np.where(swir1_data == swir1_nodata, np.nan, swir1_data)
    swir2_data = np.where(swir2_data == swir2_nodata, np.nan, swir2_data)

    # 计算 AWEIsh 指数
    awei_sh = blue_data + 2.5 * green_data - 1.5 * (nir_data + swir1_data) - 0.25 * swir2_data

    print("AWEIsh completed")

    geoserver_layer_name = save_and_upload_result(band_files['blue'], blue_transform, awei_sh)

    return geoserver_layer_name


def calculate_wi2015(image_type: str, time: str, coordinates: list) -> str:
    """
    计算WI2015

    参数:
        image_type: 图像类型，如 'Landsat'
        time: 时间标识，如202410
        coordinates: 坐标列表，格式为 [[longitude, latitude], ...]

    返回:
        上传的图层在用户工作区中的完整标识，格式为 'workspace:layer_name'
    """
    
    bands = {'green', 'red', 'nir', 'swir1', 'swir2'}

    # 获取波段文件
    band_files = data_manager.get_band_files(image_type, time, bands)

    # 获取多边形
    polygon = create_polygon_from_points(coordinates)

    # 使用rasterio打开相关波段
    with rasterio.open(band_files['green']) as green_src:
        green_data, green_transform = mask(green_src, [polygon], crop=True)
        green_nodata = green_src.nodata

    with rasterio.open(band_files['red']) as red_src:
        red_data, red_transform = mask(red_src, [polygon], crop=True)
        red_nodata = red_src.nodata

    with rasterio.open(band_files['nir']) as nir_src:
        nir_data, nir_transform = mask(nir_src, [polygon], crop=True)
        nir_nodata = nir_src.nodata

    with rasterio.open(band_files['swir1']) as swir1_src:
        swir1_data, swir1_transform = mask(swir1_src, [polygon], crop=True)
        swir1_nodata = swir1_src.nodata

    with rasterio.open(band_files['swir2']) as swir2_src:
        swir2_data, swir2_transform = mask(swir2_src, [polygon], crop=True)
        swir2_nodata = swir2_src.nodata

    # 移除 NoData 值
    green_data = np.where(green_data == green_nodata, np.nan, green_data)
    red_data = np.where(red_data == red_nodata, np.nan, red_data)
    nir_data = np.where(nir_data == nir_nodata, np.nan, nir_data)
    swir1_data = np.where(swir1_data == swir1_nodata, np.nan, swir1_data)
    swir2_data = np.where(swir2_data == swir2_nodata, np.nan, swir2_data)

    # 计算 WI2015 指数
    wi2015 = 1.7204 + 171 * green_data + 3 * red_data - 70 * nir_data - 45 * swir1_data - 71 * swir2_data

    print("WI2015 completed")

    geoserver_layer_name = save_and_upload_result(band_files['green'], green_transform, wi2015)

    return geoserver_layer_name


def calculate_mbwi(image_type: str, time: str, coordinates: list) -> str:
    """
    计算MBWI

    参数:
        image_type: 图像类型，如 'Landsat'
        time: 时间标识，如202410
        coordinates: 坐标列表，格式为 [[longitude, latitude], ...]

    返回:
        上传的图层在用户工作区中的完整标识，格式为 'workspace:layer_name'
    """
    
    bands = {'red', 'nir', 'swir1', 'tir1', 'swir2'}

    # 获取波段文件
    band_files = data_manager.get_band_files(image_type, time, bands)

    # 获取多边形
    polygon = create_polygon_from_points(coordinates)

    # 使用rasterio打开相关波段
    with rasterio.open(band_files['red']) as red_src:
        red_data, red_transform = mask(red_src, [polygon], crop=True)
        red_nodata = red_src.nodata

    with rasterio.open(band_files['nir']) as nir_src:
        nir_data, nir_transform = mask(nir_src, [polygon], crop=True)
        nir_nodata = nir_src.nodata

    with rasterio.open(band_files['swir1']) as swir1_src:
        swir1_data, swir1_transform = mask(swir1_src, [polygon], crop=True)
        swir1_nodata = swir1_src.nodata

    with rasterio.open(band_files['tir1']) as tir1_src:
        tir1_data, tir1_transform = mask(tir1_src, [polygon], crop=True)
        tir1_nodata = tir1_src.nodata

    with rasterio.open(band_files['swir2']) as swir2_src:
        swir2_data, swir2_transform = mask(swir2_src, [polygon], crop=True)
        swir2_nodata = swir2_src.nodata

    # 移除 NoData 值
    red_data = np.where(red_data == red_nodata, np.nan, red_data)
    nir_data = np.where(nir_data == nir_nodata, np.nan, nir_data)
    swir1_data = np.where(swir1_data == swir1_nodata, np.nan, swir1_data)
    tir1_data = np.where(tir1_data == tir1_nodata, np.nan, tir1_data)
    swir2_data = np.where(swir2_data == swir2_nodata, np.nan, swir2_data)

    # 计算 MBWI 指数
    mbwi = 2 * red_data - nir_data - swir1_data - tir1_data - swir2_data

    print("MBWI completed")

    geoserver_layer_name = save_and_upload_result(band_files['red'], red_transform, mbwi)

    return geoserver_layer_name


def calculate_ndmbwi(image_type: str, time: str, coordinates: list) -> str:
    """
    计算NDMBWI

    参数:
        image_type: 图像类型，如 'Landsat'
        time: 时间标识，如202410
        coordinates: 坐标列表，格式为 [[longitude, latitude], ...]

    返回:
        上传的图层在用户工作区中的完整标识，格式为 'workspace:layer_name'
    """
    
    bands = {'green', 'blue', 'red', 'nir'}

    # 获取波段文件
    band_files = data_manager.get_band_files(image_type, time, bands)

    # 获取多边形
    polygon = create_polygon_from_points(coordinates)

    # 使用rasterio打开相关波段
    with rasterio.open(band_files['green']) as green_src:
        green_data, green_transform = mask(green_src, [polygon], crop=True)
        green_nodata = green_src.nodata

    with rasterio.open(band_files['blue']) as blue_src:
        blue_data, blue_transform = mask(blue_src, [polygon], crop=True)
        blue_nodata = blue_src.nodata

    with rasterio.open(band_files['red']) as red_src:
        red_data, red_transform = mask(red_src, [polygon], crop=True)
        red_nodata = red_src.nodata

    with rasterio.open(band_files['nir']) as nir_src:
        nir_data, nir_transform = mask(nir_src, [polygon], crop=True)
        nir_nodata = nir_src.nodata

    # 移除 NoData 值
    green_data = np.where(green_data == green_nodata, np.nan, green_data)
    blue_data = np.where(blue_data == blue_nodata, np.nan, blue_data)
    red_data = np.where(red_data == red_nodata, np.nan, red_data)
    nir_data = np.where(nir_data == nir_nodata, np.nan, nir_data)

    # 计算 NDMBWI 指数
    numerator = (3 * green_data - blue_data + 2 * red_data - 5 * nir_data)
    denominator = (3 * green_data + blue_data + 2 * red_data + 5 * nir_data)

    # 避免除以零
    ndmbwi = np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator != 0)

    print("NDMBWI completed")

    geoserver_layer_name = save_and_upload_result(band_files['green'], green_transform, ndmbwi)

    return geoserver_layer_name


def calculate_grnwi(image_type: str, time: str, coordinates: list) -> str:
    """
    计算GRN-WI

    参数:
        image_type: 图像类型，如 'Landsat'
        time: 时间标识，如202410
        coordinates: 坐标列表，格式为 [[longitude, latitude], ...]

    返回:
        上传的图层在用户工作区中的完整标识，格式为 'workspace:layer_name'
    """
    
    bands = {'green', 'red', 'nir'}

    # 获取波段文件
    band_files = data_manager.get_band_files(image_type, time, bands)

    # 获取多边形
    polygon = create_polygon_from_points(coordinates)

    # 使用rasterio打开相关波段
    with rasterio.open(band_files['green']) as green_src:
        green_data, green_transform = mask(green_src, [polygon], crop=True)
        green_nodata = green_src.nodata

    with rasterio.open(band_files['red']) as red_src:
        red_data, red_transform = mask(red_src, [polygon], crop=True)
        red_nodata = red_src.nodata

    with rasterio.open(band_files['nir']) as nir_src:
        nir_data, nir_transform = mask(nir_src, [polygon], crop=True)
        nir_nodata = nir_src.nodata

    # 移除 NoData 值
    green_data = np.where(green_data == green_nodata, np.nan, green_data)
    red_data = np.where(red_data == red_nodata, np.nan, red_data)
    nir_data = np.where(nir_data == nir_nodata, np.nan, nir_data)

    # 计算 GRNWI 指数
    grnwi = green_data + red_data - 2 * nir_data

    print("GRN-WI completed")

    geoserver_layer_name = save_and_upload_result(band_files['green'], green_transform, grnwi)

    return geoserver_layer_name


def create_polygon_from_points(points: list) -> Polygon:
    """
    从点列表创建多边形

    参数:
        points: 点列表，格式为[[longitude, latitude], ...]

    返回:
        多边形
    """
    # 将点列表转换为Shapely多边形
    polygon = Polygon(points)
    return polygon


def save_and_upload_result(image_src: str, transform : rasterio.transform.Affine, data: np.ndarray) -> str:
    """
    保存和上传结果

    参数:
        image_src: 输入影像的路径
        transform: 与影像相关的空间变换
        data: 计算得到的数据数组

    返回:
        str: 上传的图层名称
    """
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

    

