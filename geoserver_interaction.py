# geoserver_interaction.py
from geo.Geoserver import Geoserver
import os
import uuid
import rasterio
import rasterio.enums
import schedule
import threading
import time


SERVICE_URL = 'http://localhost:8080/geoserver'
USER_NAME = 'admin'
PASSWORD = 'geoserver'
USER_WORKSPACE = 'user_cal_res'
LOCAL_WORKSPACE = 'local'
LOCAL_DATA_PATH = 'data/'
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


def generate_pyramids_and_upload_geotiffs() -> None:
    """
    为本地 GeoTIFF 文件生成金字塔层，并上传到指定工作区。

    此函数会遍历 LOCAL_DATA_PATH 目录及其子目录，找到所有 TIFF 文件，
    确保 NoData 值设置正确，将其金字塔层嵌入到文件中后上传到指定的工作区。

    返回:
        None
    """
    create_workspace_if_not_exists(LOCAL_WORKSPACE)
    existing_layers_name = get_existing_layers_name(LOCAL_WORKSPACE)

    for root, dirs, files in os.walk(LOCAL_DATA_PATH):
        for file in files:
            file_path = os.path.join(root, file)
            layer_name = os.path.basename(file_path)

            if layer_name in existing_layers_name:
                print(f"图层 '{layer_name}' 已存在，跳过上传。")
                continue

            # 仅处理 TIFF 文件
            if file.lower().endswith('.tif') or file.lower().endswith('.tiff'):
                print(f"开始处理文件: {file_path}")
                
                with rasterio.open(file_path, 'r+') as src:
                    print(f"读取文件成功: {file_path}")
                    print("检查和设置 NoData 值...")

                    # 设置 NoData 值，如果尚未定义
                    if src.nodata is None:
                        src.nodata = 0  # 根据实际情况设置合适的 NoData 值
                        print(f"已设置 NoData 值为 {src.nodata}")

                    print("生成嵌入金字塔层级 (overviews)...")
                    factors = [2, 4, 8, 16]
                    src.build_overviews(factors, rasterio.enums.Resampling.bilinear)
                    src.update_tags(ns='rio_overview', resampling='bilinear')
                
                print(f"正在上传包含金字塔的 TIFF 文件 '{file_path}' ...")
                try:
                    geo.create_coveragestore(
                        layer_name=layer_name,
                        path=file_path,
                        workspace=LOCAL_WORKSPACE
                    )
                    print(f"已上传包含金字塔的 TIFF 文件 '{file_path}'。")
                except Exception as e:
                    print(f"上传失败: {e}")
                    print(f"错误类型: {type(e).__name__}，内容: {str(e)}")

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


def clear_user_geotiffs() -> None:
    """
    清理用户生成的图层

    返回:
        None
    """
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



def schedule_task() -> None:
    """
    定时清理用户生成的图层

    返回:
        None
    """
    schedule.every().day.at("04:00").do(clear_user_geotiffs)
    
    while True:
        schedule.run_pending()
        time.sleep(1)


# 在独立线程中运行定时任务
task_thread = threading.Thread(target=schedule_task)
task_thread.daemon = True  # 确保主线程退出时，定时任务线程也能停止
task_thread.start()

