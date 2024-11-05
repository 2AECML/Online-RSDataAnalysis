# app.py
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import processor
import data_manager
import geoserver_interaction


app = Flask(__name__)


# 配置 CORS
CORS(app, resources={r"/*": {"origins": "*"}})  # 允许所有来源


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    # 从请求体中解析 JSON 数据
    data = request.json
    calculate_types = data.get('calculateTypes')
    coordinates = data.get('coordinates')
    image_type = data.get('imageType')
    time = data.get('time')

    # 打印接收到的数据
    print('calculateTypes:', calculate_types)
    print('coordinates:', coordinates)
    print('imageType:', image_type)
    print('time:', time)

    results = process_calculations(image_type, time, coordinates, calculate_types)

    # 返回成功响应
    return jsonify({
        'status': 'success',
        'calculateTypes': calculate_types,
        'coordinates': coordinates,
        'imageType': image_type,
        'time': time,
        'results': results
    })


@app.route('/get_available_dates', methods=['POST'])
def get_available_dates():
    data = request.json
    image_type = data.get('imageType')

    print('imageType:', image_type)

    dates = data_manager.get_available_dates(image_type)

    return jsonify({
        'status': 'success',
        'imageType': image_type,
        'dates': dates
    })


img_types = ['Landsat8', 'Sentinel2', 'MODIS']
@app.route('/get_available_images', methods=['POST'])
def get_available_images():
    data = request.json
    image_type = data.get('imageType')
    date = data.get('date')
    date = date['year'] + date['month']

    print('imageType:', image_type)
    print('date:', date)

    images = data_manager.get_available_images(image_type, date)

    return jsonify({
        'status': 'success',
        'imageType': image_type,
        'date': date,
        'images': images
    })


def process_calculations(image_type: str, time: str, coordinates: list, calculate_types: list) -> dict:
    """
    处理计算并返回结果

    参数:
        image_type: 图像类型，如 'Landsat'
        time: 时间标识，如202410
        coordinates: 坐标列表，格式为 [[longitude, latitude], ...]
        calculate_types: 要计算的指数类型列表，如 ['NDWI', 'NWI']

    返回:
        dict: 包含计算结果的字典，格式为 {'指数名称': 结果}
    """
    results = {}
    
    if 'NDWI' in calculate_types:
        results['NDWI'] = processor.calculate_ndwi(image_type, time, coordinates)

    if 'NWI' in calculate_types:
        results['NWI'] = processor.calculate_nwi(image_type, time, coordinates)

    if 'AWEInsh' in calculate_types:
        results['AWEInsh'] = processor.calculate_awei_nsh(image_type, time, coordinates)

    if 'AWEIsh' in calculate_types:
        results['AWEIsh'] = processor.calculate_awei_sh(image_type, time, coordinates)

    if 'WI2015' in calculate_types:
        results['WI2015'] = processor.calculate_wi2015(image_type, time, coordinates)

    if 'MBWI' in calculate_types:
        results['MBWI'] = processor.calculate_mbwi(image_type, time, coordinates)

    if 'NDMBWI' in calculate_types:
        results['NDMBWI'] = processor.calculate_ndmbwi(image_type, time, coordinates)

    if 'GRN-WI' in calculate_types:
        results['GRN-WI'] = processor.calculate_grnwi(image_type, time, coordinates)
    
    return results


if __name__ == '__main__':
    geoserver_interaction.clear_user_geotiffs()
    geoserver_interaction.downsample_and_upload_geotiffs()

    app.run(debug=False)


