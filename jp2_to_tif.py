import os
from osgeo import gdal


def convert_jp2_to_tif(input_jp2, output_tif):
    # 打开JP2文件
    dataset = gdal.Open(input_jp2)
    
    # 检查是否成功打开文件
    if not dataset:
        print(f"无法打开文件: {input_jp2}")
        return

    # 使用驱动程序创建GeoTIFF文件
    driver = gdal.GetDriverByName('GTiff')
    driver.CreateCopy(output_tif, dataset)

    print(f"成功将 {input_jp2} 转换为 {output_tif}")


# 遍历指定目录中的所有jp2文件，并将其转换为tif文件
def batch_convert_jp2_to_tif(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".jp2"):
            input_jp2 = os.path.join(directory, filename)
            output_tif = os.path.join(directory, filename.replace(".jp2", ".tif"))
            convert_jp2_to_tif(input_jp2, output_tif)


# 使用的文件夹路径
directory = "data/Sentinel/202410"

# 执行批量转换
batch_convert_jp2_to_tif(directory)