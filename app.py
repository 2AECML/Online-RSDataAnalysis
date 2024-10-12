from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import processor
import data_manager

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
    area_code = data.get('areaCode')
    time = data.get('time')

    # 打印接收到的数据
    print('calculateTypes:', calculate_types)
    print('coordinates:', coordinates)
    print('imageType:', image_type)
    print('areaCode:', area_code)
    print('time:', time)

    results = process_calculations(image_type, area_code, time, coordinates, calculate_types)

    # 返回成功响应
    return jsonify({
        'status': 'success',
        'calculateTypes': calculate_types,
        'coordinates': coordinates,
        'imageType': image_type,
        'areaCode': area_code,
        'time': time,
        'results': results
    })


@app.route('/get_available_dates', methods=['POST'])
def get_available_dates():
    data = request.json
    image_type = data.get('imageType')
    area_code = data.get('areaCode')

    print('imageType:', image_type)
    print('areaCode:', area_code)

    dates = data_manager.get_available_dates(image_type, area_code)

    return jsonify({
        'status': 'success',
        'imageType': image_type,
        'areaCode': area_code,
        'dates': dates
    })


img_types = ['Landsat8', 'Sentinel2', 'MODIS']
@app.route('/get_available_types_and_areas', methods=['POST'])
def get_available_types_and_areas():
    area_codes_map = {}
    for img_type in img_types:
        area_codes = data_manager.get_available_area_codes(img_type)
        area_codes_map[img_type] = area_codes
        print(img_type, area_codes)

    return jsonify({
        'status': 'success',
        'imgTypes': img_types,
        'areaCodes': area_codes_map
    })


def process_calculations(image_type, area_code, time, coordinates, calculate_types):
    results = {}
    
    if 'NDVI' in calculate_types:
        results['NDVI'] = processor.calculate_ndvi(image_type, area_code, time, coordinates)
    
    if 'NDWI' in calculate_types:
        results['NDWI'] = processor.calculate_ndwi(image_type, area_code, time, coordinates)
    
    if 'NDBI' in calculate_types:
        results['NDBI'] = processor.calculate_ndbi(image_type, area_code, time, coordinates)
    
    if 'CDI' in calculate_types:
        results['CDI'] = processor.calculate_cdi(image_type, area_code, time, coordinates)
    
    return results


if __name__ == '__main__':
    app.run(debug=True)
