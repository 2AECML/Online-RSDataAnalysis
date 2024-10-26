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

geo = Geoserver(SERVICE_URL, username=USER_NAME, password=PASSWORD)

def upload_local_geotiffs(): 
    create_workspace_if_not_exists(LOCAL_WORKSPACE)

    for root, dirs, files in os.walk(LOCAL_DATA_PATH):
        for file in files:
            file_path = os.path.join(root, file)
            layer_name = os.path.basename(file_path)
            geo.create_coveragestore(layer_name=layer_name, path=file_path, workspace=LOCAL_WORKSPACE)


def upload_user_geotiff(file_path):

    create_workspace_if_not_exists(USER_WORKSPACE)

    original_filename = os.path.basename(file_path)

    layer_name = generate_unique_layer_name(original_filename)

    geo.create_coveragestore(layer_name=layer_name, path=file_path, workspace=USER_WORKSPACE)

    return USER_WORKSPACE + ':' + layer_name


def generate_unique_layer_name(original_filename):
    # 获取文件的扩展名
    base_name, extension = os.path.splitext(original_filename)

    # 生成唯一的 UUID
    unique_id = uuid.uuid4()

    # 生成新的文件名
    unique_layer_name = f"{base_name}_{unique_id}"
    
    return unique_layer_name


def create_workspace_if_not_exists(workspace_name):
    try:
        workspaces = geo.get_workspaces()
        # print("Existing workspaces:", workspaces)
        
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


def get_geotiff_metadata(file_path):
    with rasterio.open(file_path) as src:
        metadata = src.meta
    return metadata

upload_local_geotiffs()