from geo.Geoserver import Geoserver
import os
import uuid
import rasterio

SERVICE_URL = 'http://localhost:8080/geoserver'
USER_NAME = 'admin'
PASSWORD = 'geoserver'
USER_WORKSPACE = 'user_cal_res'
LOCAL_WORKSPACE = 'local'
LOCAL_DATA_PATH = 'data'
GEOSERVER_DATA_PATH = 'D:/GeoServer/data_dir/data'

geo = Geoserver(SERVICE_URL, username=USER_NAME, password=PASSWORD)


def upload_local_geotiffs() -> None: 
    """
    上传本地 GeoTIFF 文件到指定工作区

    此函数会遍历 LOCAL_DATA_PATH 目录及其子目录，找到所有文件，并将每个文件作为图层上传到指定的工作区。

    返回:
        None
    """
    create_workspace_if_not_exists(LOCAL_WORKSPACE)

    for root, dirs, files in os.walk(LOCAL_DATA_PATH):
        for file in files:
            file_path = os.path.join(root, file)
            layer_name = os.path.basename(file_path)
            geo.create_coveragestore(layer_name=layer_name, path=file_path, workspace=LOCAL_WORKSPACE)


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
        dict: 包含文件元数据的字典
    """
    with rasterio.open(file_path) as src:
        metadata = src.meta
    return metadata


upload_local_geotiffs()