# geoserver_interaction.py
from geo.Geoserver import Geoserver
import os
import uuid
import rasterio
import schedule
import threading
import time


SERVICE_URL = 'http://localhost:8080/geoserver'
USER_NAME = 'admin'
PASSWORD = 'geoserver'
USER_WORKSPACE = 'user_cal_res'
LOCAL_WORKSPACE = 'local'
LOCAL_DATA_PATH = 'data'
GEOSERVER_DATA_PATH = 'D:/GeoServer/data_dir/data'
MAX_THUMBNAIL_WIDTH = 128
MAX_THUMBNAIL_HEIGHT = 128
TEMP_PATH = 'temp/'

geo = Geoserver(SERVICE_URL, username=USER_NAME, password=PASSWORD)


def upload_local_geotiffs() -> None: 
    """
    上传本地 GeoTIFF 文件到指定工作区

    此函数会遍历 LOCAL_DATA_PATH 目录及其子目录，找到所有文件，并将每个文件作为图层上传到指定的工作区。

    返回:
        None
    """
    create_workspace_if_not_exists(LOCAL_WORKSPACE)

    existing_layers_name = get_existing_layers_name(LOCAL_WORKSPACE)

    for root, dirs, files in os.walk(LOCAL_DATA_PATH):
        for file in files:
            file_path = os.path.join(root, file)
            layer_name = os.path.basename(file_path)
            if (layer_name in existing_layers_name):
                print(f"图层 '{layer_name}' 已存在，跳过上传。")
                continue
            print(f"正在上传图层 '{layer_name}'...")
            geo.create_coveragestore(layer_name=layer_name, path=file_path, workspace=LOCAL_WORKSPACE)
            print(f"已上传图层 '{layer_name}'。")


def downsample_and_upload_geotiffs() -> None:
    """
    降低本地 GeoTIFF 文件的分辨率并上传到指定工作区

    此函数会遍历 LOCAL_DATA_PATH 目录及其子目录，找到所有文件，并将每个文件的分辨率降低后上传到指定的工作区。

    返回:
        None
    """
    create_workspace_if_not_exists(LOCAL_WORKSPACE)

    existing_layers_name = get_existing_layers_name(LOCAL_WORKSPACE)

    for root, dirs, files in os.walk(LOCAL_DATA_PATH):
        for file in files:
            file_path = os.path.join(root, file)
            layer_name = os.path.basename(file_path)  # 获取带扩展名的图层名称
            
            if layer_name in existing_layers_name:
                print(f"图层 '{layer_name}' 已存在，跳过上传。")
                continue
            
            # 确保只处理 TIFF 文件
            if file.lower().endswith('.tif') or file.lower().endswith('.tiff'):
                print(f"开始处理文件: {file_path}")
                with rasterio.open(file_path) as src:
                    print(f"读取文件成功: {file_path}")
                    print("重采样中...")

                    # 获取原始元数据信息
                    meta = src.meta.copy()
                    
                    # 计算新的宽度和高度（比如降低为原来的1/10）
                    new_width = int(meta['width'] / 10)
                    new_height = int(meta['height'] / 10)

                    # 更新元数据以反映新的分辨率
                    meta.update({
                        'width': new_width,
                        'height': new_height,
                        'transform': rasterio.transform.from_origin(
                            meta['transform'][2], meta['transform'][5],  # 左上角坐标
                            meta['transform'][0] * 10,                 # 新像素宽度
                            -meta['transform'][4] * 10                  # 新像素高度为负
                        ),
                    })

                    # 生成新的低分辨率 TIFF 文件路径
                    downsampled_tif_path = os.path.join(TEMP_PATH, f"{layer_name}")  # 保留扩展名
                    with rasterio.open(downsampled_tif_path, 'w', **meta) as dst:
                        # 逐波段读写数据，并进行重采样
                        for i in range(1, src.count + 1):
                            data = src.read(i)
                            data_downsampled = data[::10]
                            
                            dst.write(data_downsampled, i)
                    print(f"已生成低分辨率文件: {downsampled_tif_path}")

                # 通过 geo 对象上传低分辨率 TIFF 文件
                print(f"正在上传低分辨率 TIFF 文件 '{downsampled_tif_path}' ...")
                try:
                    geo.create_coveragestore(layer_name=layer_name, path=downsampled_tif_path, workspace=LOCAL_WORKSPACE)
                    print(f"已上传低分辨率 TIFF 文件 '{downsampled_tif_path}'。")
                except Exception as e:
                    print(f"上传失败: {e}")
                    print(f"错误类型: {type(e).__name__}，内容: {str(e)}")
                finally:
                    # 上传完成后自动删除临时文件
                    if os.path.exists(downsampled_tif_path):
                        os.remove(downsampled_tif_path)
                        print(f"已删除临时文件: {downsampled_tif_path}")

            else:
                print(f"跳过非 TIFF 文件: {file_path}")


def upload_user_geotiff(file_path: str) -> str:
    """
    上传用户指定的 GeoTIFF 文件到用户工作区

    参数:
        file_path: 要上传的 GeoTIFF 文件的完整路径

    返回:
        上传的图层在用户工作区中的完整标识，格式为 'workspace:layer_name'
    """
    create_workspace_if_not_exists(USER_WORKSPACE)

    original_filename = os.path.basename(file_path)

    layer_name = generate_unique_layer_name(original_filename)

    geo.create_coveragestore(layer_name=layer_name, path=file_path, workspace=USER_WORKSPACE)

    return USER_WORKSPACE + ':' + layer_name


def generate_unique_layer_name(original_filename: str) -> str:
    """
    生成唯一的图层名称，基于原始文件名和 UUID

    参数:
        original_filename: 原始文件名，包括扩展名

    返回:
        生成的唯一图层名称
    """
    base_name, extension = os.path.splitext(original_filename)
    unique_id = uuid.uuid4()
    unique_layer_name = f"{base_name}_{unique_id}"
    
    return unique_layer_name


def create_workspace_if_not_exists(workspace_name: str) -> None:
    """
    创建工作区，如果它尚不存在

    参数:
        workspace_name: 要创建的工作区名称

    返回:
        None
    """
    try:
        workspaces = geo.get_workspaces()
        
        if 'workspaces' in workspaces and 'workspace' in workspaces['workspaces']:
            existing_workspaces = [ws['name'] for ws in workspaces['workspaces']['workspace']]
            if workspace_name not in existing_workspaces:
                geo.create_workspace(workspace=workspace_name)
                print(f"Workspace '{workspace_name}' created successfully.")
            else:
                print(f"Workspace '{workspace_name}' already exists.")
        else:
            print("Unexpected format for workspaces:", workspaces)
    except Exception as e:
        print(f"Error creating workspace: {e}")


def get_geotiff_metadata(file_path: str) -> dict:
    """
    获取 GeoTIFF 文件的元数据

    参数:
        file_path: GeoTIFF 文件的完整路径

    返回:
        包含文件元数据的字典
    """
    with rasterio.open(file_path) as src:
        metadata = src.meta
    return metadata


def get_existing_layers_name(workspace: str) -> list[str]:
    """
    获取指定工作空间的所有已存在的图层名称

    参数:
        workspace: 指定的工作空间
    
    返回:
        字符串列表
    """
    layers_name = []
    for layer in geo.get_layers(workspace)['layers']['layer']:
        layers_name.append(layer['name'])
    return layers_name


def clear_user_geotiffs():
    print("清理用户的 GeoTIFF 文件...")
    try:
        workspaces = geo.get_workspaces()
        
        if 'workspaces' in workspaces and 'workspace' in workspaces['workspaces']:
            existing_workspaces = [ws['name'] for ws in workspaces['workspaces']['workspace']]
            if USER_WORKSPACE in existing_workspaces:
                geo.delete_workspace(USER_WORKSPACE)
                print("清理完成")
            else:
                print("不存在用户的 GeoTIFF 文件，跳过清理")
        else:
            print("Unexpected format for workspaces:", workspaces)
    except Exception as e:
        print(f"Error deleting workspace: {e}")


# 定义定时任务函数
def schedule_task():
    schedule.every().day.at("04:00").do(clear_user_geotiffs)
    
    while True:
        schedule.run_pending()
        time.sleep(1)


# 在独立线程中运行定时任务
task_thread = threading.Thread(target=schedule_task)
task_thread.daemon = True  # 确保主线程退出时，定时任务线程也能停止
task_thread.start()