import os
import numpy as np
from osgeo import gdal
import helper
import cal_index as ci


# ---------------------------------------------------#
#   Processing Sentinel-2 L2A product data
# ---------------------------------------------------#
def s2_l2a_process(params):
    """
    Processing Sentinel-2 L2A product.

    :param params: These parameters determine the data processing parameters.
    """
    INPUT_PATH = params['INPUT_PATH']
    OUTPUT_PATH = params['OUTPUT_PATH']
    QUICK_IMG = params['QUICK_IMG']
    REPROJECT = params['REPROJECT']
    CRS = params['CRS']
    CLIP_TO_SHP = params['CLIP_TO_SHP']
    SHP_FILE_PATH = params['SHP_FILE_PATH']
    CAL_NDVI = params['CAL_NDVI']
    CAL_NDRE = params['CAL_NDRE']
    CAL_OSAVI = params['CAL_OSAVI']
    CAL_LCI = params['CAL_LCI']
    CAL_GNDVI = params['CAL_GNDVI']
    CAL_RECI = params['CAL_RECI']
    CAL_NDMI = params['CAL_NDMI']
    CAL_NDWI = params['CAL_NDWI']

    ###########################################
    # 0. CHECK PARAMETERS
    ###########################################

    if INPUT_PATH is None:
        raise ValueError("ERROR!!! Parameter INPUT_PATH not correctly defined")
    if OUTPUT_PATH is None:
        raise ValueError("ERROR!!! Parameter OUTPUT_PATH not correctly defined")
    if QUICK_IMG is None:
        QUICK_IMG = True
    if CLIP_TO_SHP is None:
        CLIP_TO_SHP = False
    if CAL_NDVI is None:
        CAL_NDVI = False
    if CAL_NDRE is None:
        CAL_NDRE = False
    if CAL_OSAVI is None:
        CAL_OSAVI = False
    if CAL_LCI is None:
        CAL_LCI = False
    if CAL_GNDVI is None:
        CAL_GNDVI = False
    if CAL_RECI is None:
        CAL_RECI = False
    if CAL_NDMI is None:
        CAL_NDMI = False
    if CAL_NDWI is None:
        CAL_NDWI = False

    ###########################################
    #   Step 1: 解压缩zip文件，并打印文件相关信息
    ###########################################
    # Create a temporary directory
    unzip_path = OUTPUT_PATH + os.sep + "unzip"
    if not os.path.exists(unzip_path):
        os.makedirs(unzip_path)

    # Pattern of file mode
    pattern_zip = ".zip"
    pattern_safe = ".SAFE"
    for zip_file in os.listdir(INPUT_PATH):
        # 判断是否是.zip文件
        if pattern_zip in zip_file:
            # 获取.zip文件的完整路径
            zip_file_path = os.path.join(INPUT_PATH, zip_file)
            # 解压.zip文件，产生.SAFE格式文件
            helper.unzip_file(zip_file_path, unzip_path)

            # 遍历解压缩文件夹
            for safe_file in os.listdir(unzip_path):
                # 判断是否是.SAFE文件
                if pattern_safe in safe_file:
                    # 获取.SAFE文件的完整路径
                    safe_file_path = os.path.join(unzip_path, safe_file)
                    # 打印.SAFE格式文件信息
                    helper.print_s2_info(safe_file_path)

                    ###########################################
                    #   Step 2: 数据格式转换，由jp2转换为tif格式
                    ###########################################
                    # 检索解压目录下的所有子文件夹，找到IMG_DATA文件夹
                    IMG_DATA_path = ""
                    for root, _, _ in os.walk(safe_file_path):
                        if root.endswith("IMG_DATA"):
                            IMG_DATA_path = root

                    # 获得文件名
                    img_identifier = helper.get_image_name(IMG_DATA_path)
                    # 拼接成各个波段文件绝对路径
                    # 20m分辨率数据
                    jp2_20m_list = [IMG_DATA_path + os.sep + 'R20m\\%s_B8A_20m.jp2' % img_identifier,
                                    IMG_DATA_path + os.sep + 'R20m\\%s_B11_20m.jp2' % img_identifier,
                                    IMG_DATA_path + os.sep + 'R20m\\%s_B12_20m.jp2' % img_identifier,
                                    IMG_DATA_path + os.sep + 'R20m\\%s_B05_20m.jp2' % img_identifier,
                                    IMG_DATA_path + os.sep + 'R20m\\%s_B06_20m.jp2' % img_identifier,
                                    IMG_DATA_path + os.sep + 'R20m\\%s_B07_20m.jp2' % img_identifier]
                    # 10m分辨率数据
                    jp2_10m_list = [IMG_DATA_path + os.sep + 'R10m\\%s_B02_10m.jp2' % img_identifier,
                                    IMG_DATA_path + os.sep + 'R10m\\%s_B03_10m.jp2' % img_identifier,
                                    IMG_DATA_path + os.sep + 'R10m\\%s_B04_10m.jp2' % img_identifier,
                                    IMG_DATA_path + os.sep + 'R10m\\%s_B08_10m.jp2' % img_identifier]

                    # 仅堆叠可见波段NIR、RE和SWIR1和SWIR2（波段2、3、4、8、8A、11、12）。
                    # 将20m波段（8A、11和12）重新采样至10m。
                    # 创建20m分辨率数据存储路径
                    tif_20m_save_path = unzip_path + os.sep + img_identifier + os.sep + "20m"
                    if not os.path.exists(tif_20m_save_path):
                        os.makedirs(tif_20m_save_path)

                    # 将20m分辨率数据由jp2格式转换为tif格式，并记录地址到tif_20m_list
                    tif_20m_list = []
                    for jp2_path in jp2_20m_list:
                        tif_path = helper.jp2_to_tif(jp2_path, tif_20m_save_path)
                        tif_20m_list.append(tif_path)

                    # 创建10m分辨率数据存储路径
                    tif_10m_save_path = unzip_path + os.sep + img_identifier + os.sep + "10m"
                    if not os.path.exists(tif_10m_save_path):
                        os.makedirs(tif_10m_save_path)

                    # 将10m分辨率数据由jp2格式转换为tif格式，并记录地址到tif_10m_list
                    tif_10m_list = []
                    for jp2_path in jp2_10m_list:
                        tif_path = helper.jp2_to_tif(jp2_path, tif_10m_save_path)
                        tif_10m_list.append(tif_path)

                    ###########################################
                    #   Step 3: 数据重采样，将20m分辨率数据重新采样至10m分辨率
                    ###########################################
                    # 获取一景10m分辨率影像作为参考影像
                    reference_tif = tif_10m_list[0]

                    # 将20m分辨率数据重采样至10m,并保存至 tif_10m_save_path 路径下
                    for tif_path in tif_20m_list:
                        file_name = os.path.basename(tif_path)[:-7]
                        save_tif_path = tif_10m_save_path + os.sep + file_name + "10m.tif"
                        helper.reproject_images(tif_path, save_tif_path, reference_tif)

                    ###########################################
                    #   Step 4: 波段叠加
                    #   将多个不同波段的的TIF文件合为一个多波段TIF文件
                    #   叠合波段为可见波段NIR、RE和SWIR1和SWIR2（波段2、3、4、8、8A、11、12）
                    ###########################################
                    # 数据筛选
                    tif_list = os.listdir(tif_10m_save_path)  # 获取所有10m分辨率tif数据的名称
                    tif_path_list = []  # 以列表的形式存储各个波段的路径

                    band_names = ["B02", "B03", "B04", "B08", "B8A", "B11", "B12"]  # 需要堆叠的波段名

                    for band_name in band_names:
                        for tif_name in tif_list:
                            if band_name == tif_name[-11:-8]:
                                tif_path_list.append(tif_10m_save_path + os.sep + tif_name)

                    # 执行叠加函数
                    merge_out = os.path.join(OUTPUT_PATH, img_identifier + "_merge.tif")
                    helper.merge_tif(tif_path_list, merge_out)

                    # 计算植被指数
                    proj, geotrans, img_data, row, column = helper.read_img(merge_out)
                    if CAL_NDVI:
                        ndvi_img = os.path.join(OUTPUT_PATH, img_identifier + "_ndvi.tif")
                        ci.cal_ndvi(img_data, geotrans, proj, ndvi_img)
                    if CAL_NDRE:
                        ndre_img = os.path.join(OUTPUT_PATH, img_identifier + "_ndre.tif")
                        ci.cal_ndre(img_data, geotrans, proj, ndre_img)
                    if CAL_OSAVI:
                        osavi_img = os.path.join(OUTPUT_PATH, img_identifier + "_osavi.tif")
                        ci.cal_osavi(img_data, geotrans, proj, osavi_img)
                    if CAL_LCI:
                        lci_img = os.path.join(OUTPUT_PATH, img_identifier + "_lci.tif")
                        ci.cal_lci(img_data, geotrans, proj, lci_img)
                    if CAL_GNDVI:
                        gndvi_img = os.path.join(OUTPUT_PATH, img_identifier + "_gndvi.tif")
                        ci.cal_gndvi(img_data, geotrans, proj, gndvi_img)
                    if CAL_RECI:
                        reci_img = os.path.join(OUTPUT_PATH, img_identifier + "_reci.tif")
                        ci.cal_reci(img_data, geotrans, proj, reci_img)
                    if CAL_NDMI:
                        ndmi_img = os.path.join(OUTPUT_PATH, img_identifier + "_ndmi.tif")
                        ci.cal_ndmi(img_data, geotrans, proj, ndmi_img)
                    if CAL_NDWI:
                        ndwi_img = os.path.join(OUTPUT_PATH, img_identifier + "_ndwi.tif")
                        ci.cal_ndwi(img_data, geotrans, proj, ndwi_img)

                    ###########################################
                    #   第五步：真彩色影像可视化
                    #   对图像进行拉伸显示
                    #   转换成0-255的快视图并保存
                    ###########################################
                    if QUICK_IMG:
                        proj, geotrans, img_data, row, column = helper.read_img(merge_out)
                        img_data_r = helper.rgb(img_data)  # 提取3波段改变rgb顺序和数据维度
                        # 该操作将改变原始数据，因此data用.copy，不对原始数据进行更改
                        img_data_rgb_s = np.uint8(helper.stretch_n(img_data_r.copy()) * 255)  # 数据值域缩放至（0~255）

                        quickimg = os.path.join(OUTPUT_PATH, img_identifier + "_quickimg.tif")
                        ds = gdal.Open(merge_out)  # 打开文件
                        helper.write_tiff(img_data_rgb_s.transpose(2, 0, 1), ds.GetGeoTransform(), ds.GetProjection(),
                                          quickimg)

                    ###########################################
                    #   第六步：重投影
                    ###########################################
                    if REPROJECT:
                        ds = gdal.Open(merge_out)  # 打开文件
                        reprojected_img = os.path.join(OUTPUT_PATH, img_identifier + "_projected.tif")
                        gdal.Warp(reprojected_img, ds, dstSRS=CRS)  # epsg可以通过https://epsg.io/查询
                        # 计算植被指数
                        proj, geotrans, img_data, row, column = helper.read_img(reprojected_img)
                        if CAL_NDVI:
                            ndvi_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_ndvi.tif")
                            ci.cal_ndvi(img_data, geotrans, proj, ndvi_img)
                        if CAL_NDRE:
                            ndre_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_ndre.tif")
                            ci.cal_ndre(img_data, geotrans, proj, ndre_img)
                        if CAL_OSAVI:
                            osavi_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_osavi.tif")
                            ci.cal_osavi(img_data, geotrans, proj, osavi_img)
                        if CAL_LCI:
                            lci_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_lci.tif")
                            ci.cal_lci(img_data, geotrans, proj, lci_img)
                        if CAL_GNDVI:
                            gndvi_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_gndvi.tif")
                            ci.cal_gndvi(img_data, geotrans, proj, gndvi_img)
                        if CAL_RECI:
                            reci_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_reci.tif")
                            ci.cal_reci(img_data, geotrans, proj, reci_img)
                        if CAL_NDMI:
                            ndmi_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_ndmi.tif")
                            ci.cal_ndmi(img_data, geotrans, proj, ndmi_img)
                        if CAL_NDWI:
                            ndwi_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_ndwi.tif")
                            ci.cal_ndwi(img_data, geotrans, proj, ndwi_img)

                    ###########################################
                    #   第七步：数据裁剪
                    ###########################################
                    if CLIP_TO_SHP:
                        # 执行裁剪
                        clip_output = os.path.join(OUTPUT_PATH, img_identifier + "_clip.tif")
                        # 按矢量轮廓裁剪
                        gdal.Warp(clip_output,  # 裁剪后影像保存位置
                                  merge_out,  # 待裁剪的影像
                                  cutlineDSName=SHP_FILE_PATH,  # 矢量数据
                                  format="GTiff",  # 输出影像的格式
                                  cropToCutline=True)  # 将目标图像的范围指定为cutline矢量图像的范围
                        # 计算植被指数
                        proj, geotrans, img_data, row, column = helper.read_img(clip_output)
                        if CAL_NDVI:
                            ndvi_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_ndvi.tif")
                            ci.cal_ndvi(img_data, geotrans, proj, ndvi_img)
                        if CAL_NDRE:
                            ndre_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_ndre.tif")
                            ci.cal_ndre(img_data, geotrans, proj, ndre_img)
                        if CAL_OSAVI:
                            osavi_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_osavi.tif")
                            ci.cal_osavi(img_data, geotrans, proj, osavi_img)
                        if CAL_LCI:
                            lci_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_lci.tif")
                            ci.cal_lci(img_data, geotrans, proj, lci_img)
                        if CAL_GNDVI:
                            gndvi_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_gndvi.tif")
                            ci.cal_gndvi(img_data, geotrans, proj, gndvi_img)
                        if CAL_RECI:
                            reci_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_reci.tif")
                            ci.cal_reci(img_data, geotrans, proj, reci_img)
                        if CAL_NDMI:
                            ndmi_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_ndmi.tif")
                            ci.cal_ndmi(img_data, geotrans, proj, ndmi_img)
                        if CAL_NDWI:
                            ndwi_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_ndwi.tif")
                            ci.cal_ndwi(img_data, geotrans, proj, ndwi_img)

    ###########################################
    #   第八步：删除临时文件夹
    ###########################################
    helper.del_dir(unzip_path)


# ---------------------------------------------------#
#   Processing Sentinel-2 L1C product data
# ---------------------------------------------------#
def s2_l1c_process(params):
    """
    Processing Sentinel-2 L1C product.

    :param params: These parameters determine the data processing parameters.
    """
    INPUT_PATH = params['INPUT_PATH']
    OUTPUT_PATH = params['OUTPUT_PATH']
    QUICK_IMG = params['QUICK_IMG']
    REPROJECT = params['REPROJECT']
    CRS = params['CRS']
    CLIP_TO_SHP = params['CLIP_TO_SHP']
    SHP_FILE_PATH = params['SHP_FILE_PATH']
    CAL_NDVI = params['CAL_NDVI']
    CAL_NDRE = params['CAL_NDRE']
    CAL_OSAVI = params['CAL_OSAVI']
    CAL_LCI = params['CAL_LCI']
    CAL_GNDVI = params['CAL_GNDVI']
    CAL_RECI = params['CAL_RECI']
    CAL_NDMI = params['CAL_NDMI']
    CAL_NDWI = params['CAL_NDWI']

    ###########################################
    #   Step 0: CHECK PARAMETERS
    ###########################################

    if INPUT_PATH is None:
        raise ValueError("ERROR!!! Parameter INPUT_PATH not correctly defined")
    if OUTPUT_PATH is None:
        raise ValueError("ERROR!!! Parameter OUTPUT_PATH not correctly defined")
    if QUICK_IMG is None:
        QUICK_IMG = True
    if CLIP_TO_SHP is None:
        CLIP_TO_SHP = False
    if CAL_NDVI is None:
        CAL_NDVI = False
    if CAL_NDWI is None:
        CAL_NDWI = False

    ###########################################
    #   Step 1: 解压缩zip文件，并打印文件相关信息
    ###########################################
    # Create a temporary directory
    unzip_path = OUTPUT_PATH + os.sep + "unzip"
    if not os.path.exists(unzip_path):
        os.makedirs(unzip_path)

    # Pattern of file mode
    pattern_zip = ".zip"
    pattern_safe = ".SAFE"
    for zip_file in os.listdir(INPUT_PATH):
        # 判断是否是.zip文件
        if pattern_zip in zip_file:
            # 获取.zip文件的完整路径
            zip_file_path = os.path.join(INPUT_PATH, zip_file)
            # 解压.zip文件，产生.SAFE格式文件
            zip_in_file = helper.unzip_file(zip_file_path, unzip_path)
            safe_in_file_path = os.path.join(unzip_path, zip_in_file)
            print(safe_in_file_path)

            ###########################################
            #   Step 2: 大气校正
            ###########################################
            helper.sen2Cor(safe_in_file_path, unzip_path)
            print(os.getcwd())

            # 遍历解压缩文件夹
            for safe_file in os.listdir(unzip_path):
                # 判断是否是MSIL1C文件
                if "MSIL1C" in safe_file:
                    # 获取MSIL1C.SAFE文件的完整路径
                    unzip_file_path = os.path.join(unzip_path, safe_file)
                    print(unzip_file_path)
                    # 打印.SAFE格式文件信息
                    helper.print_s2_info(unzip_file_path)

                    ###########################################
                    #   Step 3: 数据格式转换，由jp2转换为tif格式
                    ###########################################
                    for safe_l2a_file in os.listdir(unzip_path):
                        # 判断是否是MSIL2A.SAFE文件
                        if "MSIL2A" in safe_l2a_file:
                            # 获取MSIL2A.SAFE文件的完整路径
                            safe_file_path = os.path.join(unzip_path, safe_l2a_file)

                            # 检索解压目录下的所有子文件夹，找到IMG_DATA文件夹
                            IMG_DATA_path = ""
                            for root, _, _ in os.walk(safe_file_path):
                                if root.endswith("IMG_DATA"):
                                    IMG_DATA_path = root

                            # 获得文件名
                            img_identifier = helper.get_image_name(IMG_DATA_path)
                            # 拼接成各个波段文件绝对路径
                            # 20m分辨率数据
                            jp2_20m_list = [IMG_DATA_path + os.sep + 'R20m\\%s_B8A_20m.jp2' % img_identifier,
                                            IMG_DATA_path + os.sep + 'R20m\\%s_B11_20m.jp2' % img_identifier,
                                            IMG_DATA_path + os.sep + 'R20m\\%s_B12_20m.jp2' % img_identifier,
                                            IMG_DATA_path + os.sep + 'R20m\\%s_B05_20m.jp2' % img_identifier,
                                            IMG_DATA_path + os.sep + 'R20m\\%s_B06_20m.jp2' % img_identifier,
                                            IMG_DATA_path + os.sep + 'R20m\\%s_B07_20m.jp2' % img_identifier]
                            # 10m分辨率数据
                            jp2_10m_list = [IMG_DATA_path + os.sep + 'R10m\\%s_B02_10m.jp2' % img_identifier,
                                            IMG_DATA_path + os.sep + 'R10m\\%s_B03_10m.jp2' % img_identifier,
                                            IMG_DATA_path + os.sep + 'R10m\\%s_B04_10m.jp2' % img_identifier,
                                            IMG_DATA_path + os.sep + 'R10m\\%s_B08_10m.jp2' % img_identifier]

                            # 仅堆叠可见波段NIR、RE和SWIR1和SWIR2（波段2、3、4、8、8A、11、12）。
                            # 将20m波段（8A、11和12）重新采样至10m。
                            # 创建20m分辨率数据存储路径
                            tif_20m_save_path = unzip_path + os.sep + img_identifier + os.sep + "20m"
                            if not os.path.exists(tif_20m_save_path):
                                os.makedirs(tif_20m_save_path)

                            # 将20m分辨率数据由jp2格式转换为tif格式，并记录地址到tif_20m_list
                            tif_20m_list = []
                            for jp2_path in jp2_20m_list:
                                tif_path = helper.jp2_to_tif(jp2_path, tif_20m_save_path)
                                tif_20m_list.append(tif_path)

                            # 创建10m分辨率数据存储路径
                            tif_10m_save_path = unzip_path + os.sep + img_identifier + os.sep + "10m"
                            if not os.path.exists(tif_10m_save_path):
                                os.makedirs(tif_10m_save_path)

                            # 将10m分辨率数据由jp2格式转换为tif格式，并记录地址到tif_10m_list
                            tif_10m_list = []
                            for jp2_path in jp2_10m_list:
                                tif_path = helper.jp2_to_tif(jp2_path, tif_10m_save_path)
                                tif_10m_list.append(tif_path)

                            ###########################################
                            #   Step 4: 数据重采样，将20m分辨率数据重新采样至10m分辨率
                            ###########################################
                            # 获取一景10m分辨率影像作为参考影像
                            reference_tif = tif_10m_list[0]

                            # 将20m分辨率数据重采样至10m,并保存至 tif_10m_save_path 路径下
                            for tif_path in tif_20m_list:
                                file_name = os.path.basename(tif_path)[:-7]
                                save_tif_path = tif_10m_save_path + os.sep + file_name + "10m.tif"
                                helper.reproject_images(tif_path, save_tif_path, reference_tif)

                            ###########################################
                            #   Step 5: 波段叠加
                            #   将多个不同波段的的TIF文件合为一个多波段TIF文件
                            #   叠合波段为可见波段NIR、RE和SWIR1和SWIR2（波段2、3、4、8、8A、11、12）
                            ###########################################
                            # 数据筛选
                            tif_list = os.listdir(tif_10m_save_path)  # 获取所有10m分辨率tif数据的名称
                            tif_path_list = []  # 以列表的形式存储各个波段的路径

                            band_names = ["B02", "B03", "B04", "B08", "B8A", "B11", "B12"]  # 需要堆叠的波段名

                            for band_name in band_names:
                                for tif_name in tif_list:
                                    if band_name == tif_name[-11:-8]:
                                        tif_path_list.append(tif_10m_save_path + os.sep + tif_name)

                            # 执行叠加函数
                            merge_out = os.path.join(OUTPUT_PATH, img_identifier + "_merge.tif")
                            helper.merge_tif(tif_path_list, merge_out)

                            # 计算植被指数
                            proj, geotrans, img_data, row, column = helper.read_img(merge_out)
                            if CAL_NDVI:
                                ndvi_img = os.path.join(OUTPUT_PATH, img_identifier + "_ndvi.tif")
                                ci.cal_ndvi(img_data, geotrans, proj, ndvi_img)
                            if CAL_NDRE:
                                ndre_img = os.path.join(OUTPUT_PATH, img_identifier + "_ndre.tif")
                                ci.cal_ndre(img_data, geotrans, proj, ndre_img)
                            if CAL_OSAVI:
                                osavi_img = os.path.join(OUTPUT_PATH, img_identifier + "_osavi.tif")
                                ci.cal_osavi(img_data, geotrans, proj, osavi_img)
                            if CAL_LCI:
                                lci_img = os.path.join(OUTPUT_PATH, img_identifier + "_lci.tif")
                                ci.cal_lci(img_data, geotrans, proj, lci_img)
                            if CAL_GNDVI:
                                gndvi_img = os.path.join(OUTPUT_PATH, img_identifier + "_gndvi.tif")
                                ci.cal_gndvi(img_data, geotrans, proj, gndvi_img)
                            if CAL_RECI:
                                reci_img = os.path.join(OUTPUT_PATH, img_identifier + "_reci.tif")
                                ci.cal_reci(img_data, geotrans, proj, reci_img)
                            if CAL_NDMI:
                                ndmi_img = os.path.join(OUTPUT_PATH, img_identifier + "_ndmi.tif")
                                ci.cal_ndmi(img_data, geotrans, proj, ndmi_img)
                            if CAL_NDWI:
                                ndwi_img = os.path.join(OUTPUT_PATH, img_identifier + "_ndwi.tif")
                                ci.cal_ndwi(img_data, geotrans, proj, ndwi_img)

                            ###########################################
                            #   第六步：真彩色影像可视化
                            #   对图像进行拉伸显示
                            #   转换成0-255的快视图并保存
                            ###########################################
                            if QUICK_IMG:
                                proj, geotrans, img_data, row, column = helper.read_img(merge_out)
                                img_data_r = helper.rgb(img_data)  # 提取3波段改变rgb顺序和数据维度
                                # 该操作将改变原始数据，因此data用.copy，不对原始数据进行更改
                                img_data_rgb_s = np.uint8(helper.stretch_n(img_data_r.copy()) * 255)  # 数据值域缩放至（0~255）

                                quickimg = os.path.join(OUTPUT_PATH, img_identifier + "_quickimg.tif")
                                ds = gdal.Open(merge_out)  # 打开文件
                                helper.write_tiff(img_data_rgb_s.transpose(2, 0, 1), ds.GetGeoTransform(), ds.GetProjection(),
                                                  quickimg)

                            ###########################################
                            #   第七步：重投影
                            ###########################################
                            if REPROJECT:
                                ds = gdal.Open(merge_out)  # 打开文件
                                reprojected_img = os.path.join(OUTPUT_PATH, img_identifier + "_projected.tif")
                                gdal.Warp(reprojected_img, ds, dstSRS=CRS)  # epsg可以通过https://epsg.io/查询
                                # 计算植被指数
                                proj, geotrans, img_data, row, column = helper.read_img(reprojected_img)
                                if CAL_NDVI:
                                    ndvi_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_ndvi.tif")
                                    ci.cal_ndvi(img_data, geotrans, proj, ndvi_img)
                                if CAL_NDRE:
                                    ndre_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_ndre.tif")
                                    ci.cal_ndre(img_data, geotrans, proj, ndre_img)
                                if CAL_OSAVI:
                                    osavi_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_osavi.tif")
                                    ci.cal_osavi(img_data, geotrans, proj, osavi_img)
                                if CAL_LCI:
                                    lci_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_lci.tif")
                                    ci.cal_lci(img_data, geotrans, proj, lci_img)
                                if CAL_GNDVI:
                                    gndvi_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_gndvi.tif")
                                    ci.cal_gndvi(img_data, geotrans, proj, gndvi_img)
                                if CAL_RECI:
                                    reci_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_reci.tif")
                                    ci.cal_reci(img_data, geotrans, proj, reci_img)
                                if CAL_NDMI:
                                    ndmi_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_ndmi.tif")
                                    ci.cal_ndmi(img_data, geotrans, proj, ndmi_img)
                                if CAL_NDWI:
                                    ndwi_img = os.path.join(OUTPUT_PATH, img_identifier + "_proj_ndwi.tif")
                                    ci.cal_ndwi(img_data, geotrans, proj, ndwi_img)

                            ###########################################
                            #   第八步：数据裁剪
                            ###########################################
                            if CLIP_TO_SHP:
                                # 执行裁剪
                                clip_output = os.path.join(OUTPUT_PATH, img_identifier + "_clip.tif")
                                # 按矢量轮廓裁剪
                                gdal.Warp(clip_output,  # 裁剪后影像保存位置
                                          merge_out,  # 待裁剪的影像
                                          cutlineDSName=SHP_FILE_PATH,  # 矢量数据
                                          format="GTiff",  # 输出影像的格式
                                          cropToCutline=True)  # 将目标图像的范围指定为cutline矢量图像的范围
                                # 计算植被指数
                                proj, geotrans, img_data, row, column = helper.read_img(clip_output)
                                if CAL_NDVI:
                                    ndvi_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_ndvi.tif")
                                    ci.cal_ndvi(img_data, geotrans, proj, ndvi_img)
                                if CAL_NDRE:
                                    ndre_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_ndre.tif")
                                    ci.cal_ndre(img_data, geotrans, proj, ndre_img)
                                if CAL_OSAVI:
                                    osavi_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_osavi.tif")
                                    ci.cal_osavi(img_data, geotrans, proj, osavi_img)
                                if CAL_LCI:
                                    lci_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_lci.tif")
                                    ci.cal_lci(img_data, geotrans, proj, lci_img)
                                if CAL_GNDVI:
                                    gndvi_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_gndvi.tif")
                                    ci.cal_gndvi(img_data, geotrans, proj, gndvi_img)
                                if CAL_RECI:
                                    reci_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_reci.tif")
                                    ci.cal_reci(img_data, geotrans, proj, reci_img)
                                if CAL_NDMI:
                                    ndmi_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_ndmi.tif")
                                    ci.cal_ndmi(img_data, geotrans, proj, ndmi_img)
                                if CAL_NDWI:
                                    ndwi_img = os.path.join(OUTPUT_PATH, img_identifier + "_clip_ndwi.tif")
                                    ci.cal_ndwi(img_data, geotrans, proj, ndwi_img)

    ###########################################
    #   第九步：删除临时文件夹
    ###########################################
    helper.del_dir(unzip_path)