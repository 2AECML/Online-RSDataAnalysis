from geo.Geoserver import Geoserver
import os
import uuid

import rasterio

SERVICE_URL = 'http://localhost:8080/geoserver'
USER_NAME = 'admin'
PASSWORD = 'geoserver'

geo = Geoserver(SERVICE_URL, username=USER_NAME, password=PASSWORD)


def upload_geotiff(file_path):

    workspace = 'users_cal_res'

    create_workspace_if_not_exists(workspace)

    original_filename = os.path.basename(file_path)

    layer_name = generate_unique_layer_name(original_filename)

    geo.create_coveragestore(layer_name=layer_name, path=file_path, workspace=workspace)

    return workspace + ':' + layer_name


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