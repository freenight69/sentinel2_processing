import os
import zipfile
import subprocess
import numpy as np
from osgeo import gdal, ogr, osr, gdalconst


# Sen2cor.bat文件所在路径，用于大气校正
sen2cor_path = r"E:\PycharmProjects\sentinel2_processing\Sen2Cor-02.11.00-win64\L2A_Process.bat"


def unzip_file(zip_file_name, unzip_path, mode='rb'):
    """
    Unzipping from the zipped file.

    :param zip_file_name:
        the zipped file name of A Sentinel-2 data.
    :param unzip_path:
        directory for storing unzipped files.
    :param mode:
        Optional parameter, the mode of the zipped file reader.
    :return
    """
    # 打开.zip文件
    zip_file = open(zip_file_name, mode)
    # 利用zipfile包解压文件
    zip_fn = zipfile.ZipFile(zip_file)
    # 获取.zip文件的所有子目录名和文件名
    namelist = zip_fn.namelist()
    for item in namelist:
        # 提取.zip文件的子目录及文件，解压在当前文件夹（'.'表示当前文件夹）
        zip_fn.extract(item, unzip_path)
    # 关闭.zip文件
    zip_fn.close()
    zip_file.close()
    # 打印解压完成
    print("Unzipping finished!")
    # 返回解压后的文件名（字符串，带.SAFE后缀）
    print(namelist[0])
    return namelist[0]


# -------------------------------------------------------------#
#   Sentinel-2产品解压后为SAFE格式，SAFE文件包含以下几个内容：
#   一个manifest.safe文件，其中包含 XML 格式的一般产品信息
#   JPEG2000 格式的预览图像
#   测量（传感器扫描成像）数据集的子文件夹，包括 GML-JPEG2000 格式的图像数据（颗粒/瓦片）
#   数据条级别信息的子文件夹
#   带有辅助数据的子文件夹（例如国际地球自转和参考系统 (IERS) 公告）
#   HTML 预览
# -------------------------------------------------------------#
def print_s2_info(file_path):
    """
    Printing information of Sentinel-2 product.

    :param file_path:
        the file path to be printed.
    """
    xml_path = ''
    for xml_file in os.listdir(file_path):
        # 判断是否是.SAFE文件
        if 'MSIL2A' in xml_file:
            xml_path = file_path + os.sep + 'MTD_MSIL2A.xml'
        elif 'MSIL1C' in xml_file:
            xml_path = file_path + os.sep + 'MTD_MSIL1C.xml'
    root_ds = gdal.Open(xml_path)
    ds_list = root_ds.GetSubDatasets()  # 获取子数据集。该数据以数据集形式存储且以子数据集形式组织
    for i in range(len(ds_list)):
        visual_ds = gdal.Open(ds_list[i][0])  # 打开第i个数据子集的路径。ds_list有4个子集，内部前段是路径，后段是数据信息
        print(ds_list[i][0])
        print(f'数据波段为：{ds_list[i][1]}')
        print(f'仿射矩阵信息：{visual_ds.GetGeoTransform()}')
        print(f'投影信息：{visual_ds.GetProjection()}')
        print(f'栅格波段数：{visual_ds.RasterCount}')
        print(f'栅格列数（宽度）：{visual_ds.RasterXSize} 栅格行数（高度）：{visual_ds.RasterYSize}')
        print("\n")


def get_image_name(image_directory):
    """
    获取Sentinel-2文件的编号,例如T50TLK_20220825T030519

    :param image_directory: jp2数据地址
    :return: 存储地址
    """
    file = image_directory + '\\R10m'
    names = os.listdir(file)[0]
    img_name = names[:22]
    return img_name


# -------------------------------------------------------------#
#   数据格式转换：
#   所需要的图像数据储存在IMG_DATA文件夹里，该文件夹内有三个子文件夹，
#   分别存有三种不同分辨率的数据，数据格式为JPEG2000。接下来的任务为：
#   在解压缩后的文件夹查找到jp2数据
#   对各个波段的jp2数据进行解压缩，保存为GeoTiff格式数据
# -------------------------------------------------------------#
def jp2_to_tif(jp2_path, save_path):
    """
    格式转换: jp2 转 tif

    :param jp2_path: jp2数据地址
    :param save_path: 存储路径
    :return: 存储地址
    """
    file_name = os.path.basename(jp2_path)[:-4]
    save_file = os.path.join(save_path, file_name)
    save_file = save_file + '.tif'
    dataset = gdal.Open(jp2_path)
    rows = dataset.RasterYSize
    cols = dataset.RasterXSize
    projection = dataset.GetProjection()
    trans = dataset.GetGeoTransform()
    data = dataset.ReadAsArray()
    if data.dtype == 'uint16':
        driver = gdal.GetDriverByName('GTiff')
        out_dataset = driver.Create(save_file, cols, rows, 1, gdal.GDT_UInt16)
        out_dataset.SetProjection(projection)
        out_dataset.SetGeoTransform(trans)
        out_dataset.GetRasterBand(1).WriteArray(data)
        out_dataset.GetRasterBand(1).SetNoDataValue(0)
        out_dataset.FlushCache()
        del dataset, out_dataset
    elif data.dtype == 'uint8':
        driver = gdal.GetDriverByName('GTiff')
        out_dataset = driver.Create(save_file, cols, rows, 1, gdal.GDT_Byte)
        out_dataset.SetProjection(projection)
        out_dataset.SetGeoTransform(trans)
        out_dataset.GetRasterBand(1).WriteArray(data)
        out_dataset.GetRasterBand(1).SetNoDataValue(0)
        out_dataset.FlushCache()
        del dataset, out_dataset
    return save_file


# -------------------------------------------------------------#
#   数据重采样：
#   仅堆叠可见波段NIR、RE和SWIR1和SWIR2（波段2、3、4、8、8A、11、12）。
#   将20m波段（8A、11和12）重新采样至10m。
# -------------------------------------------------------------#
def reproject_images(inputfilePath, outputfilePath, referencefilePath):
    """
    数据重采样: 将20m波段（8A、11和12）重新采样至10m

    :param inputfilePath: 输入影像存储路径
    :param outputfilePath: 输出影像存储路径
    :param referencefilefilePath: 参考影像存储路径
    """
    # 获取输入影像信息
    inputrasfile = gdal.Open(inputfilePath, gdal.GA_ReadOnly)
    inputProj = inputrasfile.GetProjection()
    # 获取参考影像信息
    referencefile = gdal.Open(referencefilePath, gdal.GA_ReadOnly)
    referencefileProj = referencefile.GetProjection()
    referencefileTrans = referencefile.GetGeoTransform()
    bandreferencefile = referencefile.GetRasterBand(1)
    Width = referencefile.RasterXSize
    Height = referencefile.RasterYSize
    nbands = referencefile.RasterCount
    # 创建重采样输出文件（设置投影及六参数）
    driver = gdal.GetDriverByName('GTiff')
    output = driver.Create(outputfilePath, Width, Height, nbands, bandreferencefile.DataType)
    output.SetGeoTransform(referencefileTrans)
    output.SetProjection(referencefileProj)
    # 参数说明 输入数据集、输出文件、输入投影、参考投影、重采样方法(最邻近内插\双线性内插\三次卷积等)、回调函数
    gdal.ReprojectImage(inputrasfile, output, inputProj, referencefileProj, gdalconst.GRA_Bilinear, 0.0, 0.0, )


def read_img(filename):
    """
    读图像文件

    :param filename: 输入影像路径
    :return: 输入影像的坐标系、仿射变换参数、影像数组、栅格矩阵的列数、栅格矩阵的行数
    """
    dataset = gdal.Open(filename)  # 打开文件

    im_width = dataset.RasterXSize  # 栅格矩阵的列数
    im_height = dataset.RasterYSize  # 栅格矩阵的行数
    # im_bands = dataset.RasterCount  # 波段数
    im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵，左上角像素的大地坐标和像素分辨率
    im_proj = dataset.GetProjection()  # 地图投影信息，字符串表示
    im_data = dataset.ReadAsArray(0, 0, im_width, im_height)

    del dataset  # 关闭对象dataset，释放内存
    # return im_width, im_height, im_proj, im_geotrans, im_data,im_bands
    return im_proj, im_geotrans, im_data, im_width, im_height


def write_tiff(img_arr, geomatrix, projection, path):
    """
    遥感影像的存储，写入GeoTiff文件

    :param img_arr: 输入影像数组
    :param geomatrix: 输入影像仿射变换参数
    :param projection: 输入影像坐标系
    :param path: 输出影像路径
    """
    #     img_bands, img_height, img_width = img_arr.shape
    if 'int8' in img_arr.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in img_arr.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    if len(img_arr.shape) == 3:
        img_bands, img_height, img_width = img_arr.shape
        driver = gdal.GetDriverByName("GTiff")
        dataset = driver.Create(path, int(img_width), int(img_height), int(img_bands), datatype)
        #     print(path, int(img_width), int(img_height), int(img_bands), datatype)
        if (dataset is not None) and (geomatrix != '') and (projection != ''):
            dataset.SetGeoTransform(geomatrix)  # 写入仿射变换参数
            dataset.SetProjection(projection)  # 写入投影
        for i in range(img_bands):
            dataset.GetRasterBand(i + 1).WriteArray(img_arr[i])
        del dataset

    elif len(img_arr.shape) == 2:
        # img_arr = np.array([img_arr])
        img_height, img_width = img_arr.shape
        img_bands = 1
        # 创建文件
        driver = gdal.GetDriverByName("GTiff")
        dataset = driver.Create(path, int(img_width), int(img_height), int(img_bands), datatype)
        #     print(path, int(img_width), int(img_height), int(img_bands), datatype)
        if dataset is not None:
            dataset.SetGeoTransform(geomatrix)  # 写入仿射变换参数
            dataset.SetProjection(projection)  # 写入投影
        dataset.GetRasterBand(1).WriteArray(img_arr)
        del dataset


def merge_tif(tif_path_list, output_tif):
    """
    波段叠合，将多个不同波段的的TIF文件合为一个多波段TIF文件

    :param tif_path_list: 输入影像列表
    :param output_tif: 输出保存影像
    """
    global geotrans, proj
    arr_list = []
    for tif_path in tif_path_list:
        proj, geotrans, data, row, column = read_img(tif_path)
        arr_list.append(data)
    all_arr = np.array(arr_list)
    write_tiff(all_arr, geotrans, proj, output_tif)


def stretch(band, lower_percent=2, higher_percent=98):  # 2和98表示分位数
    """
    对波段做归一化拉伸处理

    :param band: 输入波段
    :param lower_percent: 波段值频率分布的最低可信百分数
    :param higher_percent: 波段值频率分布的最高可信百分数
    """
    band = np.array(band, dtype=np.float32)
    c = np.percentile(band, lower_percent) * 1.0
    d = np.percentile(band, higher_percent) * 1.0
    band[band < c] = c
    band[band > d] = d
    out = (band - c) / (d - c)
    return out.astype(np.float32)


def stretch_n(data, n_band=3):
    """
    对RGB3个波段做归一化拉伸处理

    :param data: 输入影像数组
    :param n_band: 输入波段数
    """
    data = np.array(data, dtype=np.float32)
    for k in range(n_band):
        data[:, :, k] = stretch(data[:, :, k])
    return data


def rgb(img_data, iftran=True):
    """
    对波段做归一化拉伸处理

    :param img_data: 输入影像数组
    :param iftran: 判断是否做波段顺序调换的标志
    """
    img_data_3b = img_data[:3, :, :]  # 取前三个波段 B02,B03,B04
    if iftran:
        img_data_3b = img_data_3b[::-1, :, :]  # 将B02,B03,B04转成B04,B03,B02 (BGR转RGB)
    img_data = img_data_3b.transpose(1, 2, 0)  # C,H,W -> H,W,C
    return img_data


def compress(path, target_path, method="LZW"):
    """
    使用gdal进行文件压缩，LZW方法属于无损压缩

    :param path: 待压缩影像
    :param target_path: 压缩后保存影像
    :param method: 压缩方法，LZW方法属于无损压缩
    """
    dataset = gdal.Open(path)
    driver = gdal.GetDriverByName('GTiff')
    driver.CreateCopy(target_path, dataset, strict=1,
                      options=["TILED=YES", "COMPRESS={0}".format(method), "BIGTIFF=YES"])
    del dataset


def del_dir(data_path):
    """
    清空文件夹下文件

    :param path_data: 文件夹路径
    """
    if not os.path.exists(data_path):
        return False
    if os.path.isfile(data_path):
        os.remove(data_path)
        return
    for i in os.listdir(data_path):
        t = os.path.join(data_path, i)
        if os.path.isdir(t):
            del_dir(t)  # 重新调用次方法
        else:
            os.unlink(t)
    if os.path.exists(data_path):
        os.removedirs(data_path)  # 递归删除目录下面的空文件夹


def sen2Cor(l1c_path, output_l2a_path):
    """
    调用sen2cor工具箱对Sentinel-2 L1C级数据进行大气校正，生成L2A级数据

    :param l1c_path: L1C级原始数据输入路径
    :param unzip_path: 临时解压缩文件路径
    :param output_l2a_path: 大气校正后L2A级数据输出路径
    """
    # 设置Sen2cor命令行参数，按照原始分辨率处理
    cmd_args = [sen2cor_path, l1c_path, '--output_dir', output_l2a_path]
    # 打印处理开始的消息
    print("{} processing begin!".format(l1c_path))
    # 传入命令行参数并调用命令行(cmd)执行命令
    subprocess.call(cmd_args)
    # 打印处理完成的消息
    print("{} processing finished!\n".format(l1c_path))


# -------------------------------------------------------------#
#   去云函数：
#   （1）生成云掩膜tif文件。
# -------------------------------------------------------------#
def get_s2_cloud_tiff(safe_path, output_path):
    """
    生成云掩膜tif文件。

    :param safe_path: .SAFE文件路径
    :param output_path: 云掩膜tif文件保存路径
    """
    # 打开栅格数据集
    safe_file = safe_path + os.sep + 'MTD_MSIL2A.xml'
    root_ds = gdal.Open(safe_file)
    # 返回结果是一个list，list中的每个元素是一个tuple，每个tuple中包含了对数据集的路径，元数据等的描述信息
    # tuple中的第一个元素描述的是数据子集的全路径
    ds_list = root_ds.GetSubDatasets()  # 获取子数据集。该数据以数据集形式存储且以子数据集形式组织
    visual_ds = gdal.Open(ds_list[1][0])  # 打开第2个数据子集的路径。ds_list有4个子集，内部前段是路径，后段是数据信息
    visual_arr = visual_ds.ReadAsArray()  # 将数据集中的数据读取为ndarray

    # 创建.tif文件
    xSize = visual_ds.RasterXSize
    ySize = visual_ds.RasterYSize
    out_tif_name = output_path + os.sep + "classification_temp.tif"
    driver = gdal.GetDriverByName("GTiff")
    out_tif = driver.Create(out_tif_name, xSize, ySize, 1, gdal.GDT_Byte)
    out_tif.SetProjection(visual_ds.GetProjection())  # 设置投影坐标
    out_tif.SetGeoTransform(visual_ds.GetGeoTransform())

    # 只输出Classification Map波段
    out_tif.GetRasterBand(1).WriteArray(visual_arr[-3])
    out_tif.FlushCache()  # 最终将数据写入硬盘
    del out_tif  # 注意必须关闭tif文件

    # 对20m分辨率的classification.tif重采样到10m分辨率
    resample_tif = output_path + os.sep + "classification.tif"
    gdal.Warp(resample_tif,  # 裁剪后影像保存位置
              out_tif_name,  # 待裁剪的影像
              format='GTiff',  # 输出影像的格式
              # dstSRS='EPSG:4326',  # 参考坐标系：WGS84
              resampleAlg='cubic',  # 重采样方法
              xRes=10,
              yRes=10,
              outputType=gdal.GDT_Byte)  # 目标图像数据格式
    os.remove(out_tif_name)


# -------------------------------------------------------------#
#   去云函数：
#   （2）云掩膜tif文件转成shp矢量文件。
# -------------------------------------------------------------#
def raster2shp(input_path):
    """
    云掩膜tif文件转成shp矢量文件。

    :param input_path: 云掩膜tif文件存储路径
    """
    pattern = "classification.tif"
    for in_file in os.listdir(input_path):  # 遍历路径中每一个文件
        if pattern in in_file:
            raster = os.path.join(input_path, in_file)
            inraster = gdal.Open(raster)  # 读取路径中的栅格数据
            inband = inraster.GetRasterBand(1)  # 这个波段就是最后想要转为矢量的波段，如果是单波段数据的话那就都是1
            prj = osr.SpatialReference()
            prj.ImportFromWkt(inraster.GetProjection())  # 读取栅格数据的投影信息，用来为后面生成的矢量做准备

            outshp = raster[:-4] + ".shp"  # 给后面生成的矢量准备一个输出文件名，这里就是把原栅格的文件名后缀名改成shp了
            drv = ogr.GetDriverByName("ESRI Shapefile")
            if os.path.exists(outshp):  # 若文件已经存在，则删除它继续重新做一遍
                drv.DeleteDataSource(outshp)
            Polygon = drv.CreateDataSource(outshp)  # 创建一个目标文件
            Poly_layer = Polygon.CreateLayer(raster[:-4], srs=prj,
                                             geom_type=ogr.wkbMultiPolygon)  # 对shp文件创建一个图层，定义为多个面类
            newField = ogr.FieldDefn('value', ogr.OFTReal)  # 给目标shp文件添加一个字段，用来存储原始栅格的pixel value
            Poly_layer.CreateField(newField)

            gdal.FPolygonize(inband, None, Poly_layer, 0)  # 核心函数，执行的就是栅格转矢量操作
            Polygon.SyncToDisk()
            del Polygon
            print(outshp + " has been created")


def delete_shp_feature(path, strValue):
    """
    云掩膜tif文件转成shp矢量文件。

    :param path: shp矢量文件存储路径
    :param strValue: shp矢量待删除value
    """
    # 打开矢量数据
    # 解决中文路径乱码问题
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    driver = ogr.GetDriverByName('ESRI Shapefile')
    pFeatureDataset = driver.Open(path, 1)
    pFeaturelayer = pFeatureDataset.GetLayer(0)

    # 按条件查询空间要素，本例查询字段名为Value，字段值为strValue的所有要素
    strFilter = "value = '" + str(strValue) + "'"
    pFeaturelayer.SetAttributeFilter(strFilter)
    # 获取要素数量
    pFeaturelayer.GetFeatureCount()

    # 删除第二部查询到的矢量要素，注意，此时获取到的Feature皆为选择的Feature
    # pFeatureDef = pFeaturelayer.GetLayerDefn()
    # pFieldName = "value"
    # pFieldIndex = pFeatureDef.GetFieldIndex(pFieldName)
    for pFeature in pFeaturelayer:
        pFeatureFID = pFeature.GetFID()
        pFeaturelayer.DeleteFeature(int(pFeatureFID))
    strSQL = "REPACK " + str(pFeaturelayer.GetName())
    pFeatureDataset.ExecuteSQL(strSQL, None, "")
    pFeatureLayer = None
    pFeatureDataset = None


# -------------------------------------------------------------#
#   去云函数：
#   （3）生成云掩膜shp矢量文件。
# -------------------------------------------------------------#
def remove_cloud_shp(shp_path, tif_path, output_path):
    """
    生成云掩膜shp矢量文件。

    :param shp_path: shp矢量文件存储路径
    :param tif_path: 待裁剪tif影像文件存储路径
    :param output_path: 裁剪后tif影像文件存储路径

    Sentinel-2 Sen2Cor Classification Map
    0,No data
    1,Saturated or defective
    2,Dark area pixels
    3,Cloud Shadows
    4,Vegetation
    5,Not Vegetated
    6,Water
    7,Unclassified
    8,Cloud Medium Probability
    9,Cloud High Probability
    10,Thin Cirrus
    11,Snow
    """
    file_path = os.path.join(shp_path, "classification.shp")
    maskValve = [0, 8, 9]
    for i in maskValve:
        delete_shp_feature(file_path, i)
    print(file_path + " has generated cloud mask")

    # 按矢量轮廓裁剪
    gdal.Warp(output_path,  # 裁剪后影像保存位置
              tif_path,  # 待裁剪的影像
              cutlineDSName=file_path,  # 矢量数据
              format="GTiff",  # 输出影像的格式
              cropToCutline=True)  # 将目标图像的范围指定为cutline矢量图像的范围

