import helper
import numpy as np


def cal_ndvi(img_data, geotrans, proj, out_path):
    """
    归一化差值植被指数 NDVI = (NIR - R) / (NIR + R)
    NDVI 是最常用的植被指数。可以用来表征地面植被密集程度和植物的叶绿素含量。NDVI 数值为 -1 到 1，
    特点：通常正值表示有植被覆盖，数值越高，植被越密集或叶绿素含量越高。0 和负值表示岩石、裸土、水体等非植被覆盖。
    使用阶段：NDVI 在作物最活跃生长阶段的季节中期最准确，可以用于诊断作物的叶绿素、氮素含量，从而指导合理施用氮肥。

    :param img_data: 输入影像矩阵
    :param geotrans: 输入影像仿射系数
    :param proj: 输入影像坐标系
    :param out_path: 输出影像存储路径
    """
    red_arr = img_data[2, :, :]
    nir_arr = img_data[3, :, :]

    denominator = np.array(nir_arr + red_arr, dtype=np.float32)
    numerator = np.array(nir_arr - red_arr, dtype=np.float32)
    nodata = np.full((nir_arr.shape[0], nir_arr.shape[1]), -999, dtype=np.float32)
    ndvi = np.true_divide(numerator, denominator, out=nodata, where=denominator != 0.0)
    # print(np.min(ndvi), np.max(ndvi))
    ndvi[ndvi == -999.0] = None
    ndvi[ndvi <= -1.0] = -1.0
    ndvi[ndvi >= 1.0] = 1.0
    helper.write_tiff(ndvi, geotrans, proj, out_path)


def cal_ndre(img_data, geotrans, proj, out_path):
    """
    归一化差异红边植被指数 NDRE = (NIR – RED EDGE) / (NIR + RED EDGE)
    在高植被区 NDVI 灵敏度较低，也就是 NDVI 的“饱和”现象。为了应对 NDVI 的这个缺陷，就引入了 NDRE。
    特点：用红边波段取代了 NDVI 中的红色波段。红边是红光和近红外波段中间的一个过度波段，是叶绿素在红光区域的吸收和在近红外区域的反射之间的界限。
    使用阶段：NDRE 在高植被区，例如农田作物封行之后，可以更灵敏地反映植被的叶绿素含量。

    :param img_data: 输入影像矩阵
    :param geotrans: 输入影像仿射系数
    :param proj: 输入影像坐标系
    :param out_path: 输出影像存储路径
    """
    redEdge_arr = img_data[4, :, :]
    nir_arr = img_data[3, :, :]

    denominator = np.array(nir_arr + redEdge_arr, dtype=np.float32)
    numerator = np.array(nir_arr - redEdge_arr, dtype=np.float32)
    nodata = np.full((nir_arr.shape[0], nir_arr.shape[1]), -999, dtype=np.float32)
    ndre = np.true_divide(numerator, denominator, out=nodata, where=denominator != 0.0)
    ndre[ndre == -999.0] = None
    # ndre[ndre <= -1.0] = -1.0
    # ndre[ndre >= 1.0] = 1.0
    helper.write_tiff(ndre, geotrans, proj, out_path)


def cal_osavi(img_data, geotrans, proj, out_path):
    """
    优化土壤调整植被指数 NDRE = (NIR – RED) / (NIR + RED + 0.16)
    OSAVI 主要在 NDVI 的基础上将土壤因素纳入考量，在植被生长初期、密度不高的时候，
    可以更好地排除土壤影响、反映植被的叶绿素含量。因此 OSAVI 比较适用于植被稀疏或者农田作物出苗初期的植被健康度诊断。

    :param img_data: 输入影像矩阵
    :param geotrans: 输入影像仿射系数
    :param proj: 输入影像坐标系
    :param out_path: 输出影像存储路径
    """
    red_arr = img_data[2, :, :]
    nir_arr = img_data[3, :, :]

    denominator = np.array(nir_arr + red_arr + 0.16, dtype=np.float32)
    numerator = np.array(nir_arr - red_arr, dtype=np.float32)
    nodata = np.full((nir_arr.shape[0], nir_arr.shape[1]), -999, dtype=np.float32)
    osavi = np.true_divide(numerator, denominator, out=nodata, where=denominator != 0.0)
    osavi[osavi == -999.0] = None
    # osavi[osavi <= -1.0] = -1.0
    # osavi[osavi >= 1.0] = 1.0
    helper.write_tiff(osavi, geotrans, proj, out_path)


def cal_lci(img_data, geotrans, proj, out_path):
    """
    叶面叶绿素指数 LCI = (NIR – RED EDGE) / (NIR + RED)
    LCI 对于判断植物的叶子的叶绿素和含氮量有较好的效果，而相比之下 NDVI 通常用于判断整个冠层的叶绿素和含氮量。

    :param img_data: 输入影像矩阵
    :param geotrans: 输入影像仿射系数
    :param proj: 输入影像坐标系
    :param out_path: 输出影像存储路径
    """
    red_arr = img_data[2, :, :]
    nir_arr = img_data[3, :, :]
    redEdge_arr = img_data[4, :, :]

    denominator = np.array(nir_arr + red_arr, dtype=np.float32)
    numerator = np.array(nir_arr - redEdge_arr, dtype=np.float32)
    nodata = np.full((nir_arr.shape[0], nir_arr.shape[1]), -999, dtype=np.float32)
    lci = np.true_divide(numerator, denominator, out=nodata, where=denominator != 0.0)
    lci[lci == -999.0] = None
    # lci[lci <= -1.0] = -1.0
    # lci[lci >= 1.0] = 1.0
    helper.write_tiff(lci, geotrans, proj, out_path)


def cal_gndvi(img_data, geotrans, proj, out_path):
    """
    绿色归一化差异植被指数 GNDVI = (NIR – GREEN) / (NIR + GREEN)
    GNDVI 相比 NDVI 能更稳定地探测植被，因此 GDNVI 也经常用于植被覆盖监测、植被和作物健康度调查中。

    :param img_data: 输入影像矩阵
    :param geotrans: 输入影像仿射系数
    :param proj: 输入影像坐标系
    :param out_path: 输出影像存储路径
    """
    green_arr = img_data[1, :, :]
    nir_arr = img_data[3, :, :]

    denominator = np.array(nir_arr + green_arr, dtype=np.float32)
    numerator = np.array(nir_arr - green_arr, dtype=np.float32)
    nodata = np.full((nir_arr.shape[0], nir_arr.shape[1]), -999, dtype=np.float32)
    gndvi = np.true_divide(numerator, denominator, out=nodata, where=denominator != 0.0)
    gndvi[gndvi == -999.0] = None
    # lci[lci <= -1.0] = -1.0
    # lci[lci >= 1.0] = 1.0
    helper.write_tiff(gndvi, geotrans, proj, out_path)


def cal_reci(img_data, geotrans, proj, out_path):
    """
    红边叶绿素植被指数 RECI = (NIR – RED) - 1
    ReCI 植被指数对受氮滋养的叶子中的叶绿素含量有反应。ReCI 显示了冠层的光合活性。
    特点：由于叶绿素含量直接取决于植物中的氮含量，这是植物“绿色”的原因，因此遥感中的这种植被指数有助于检测黄色或落叶区域。
    使用阶段：ReCI 值在植被活跃发育阶段最有用，但不适用于收获季节。

    :param img_data: 输入影像矩阵
    :param geotrans: 输入影像仿射系数
    :param proj: 输入影像坐标系
    :param out_path: 输出影像存储路径
    """
    red_arr = img_data[2, :, :]
    nir_arr = img_data[3, :, :]

    denominator = np.array(red_arr, dtype=np.float32)
    numerator = np.array(nir_arr, dtype=np.float32)
    nodata = np.full((nir_arr.shape[0], nir_arr.shape[1]), -999, dtype=np.float32)
    reci = np.true_divide(numerator, denominator, out=nodata, where=denominator != 0.0) - 1.0
    reci[reci == -999.0] = None
    # reci[reci <= -1.0] = -1.0
    # reci[reci >= 1.0] = 1.0
    helper.write_tiff(reci, geotrans, proj, out_path)


def cal_ndmi(img_data, geotrans, proj, out_path):
    """
    归一化差值水分指数 NDMI = (NIR - SWIR1) / (NIR + SWIR1)
    NDMI 通过计算近红外与短波红外之间的差异来定量化反映植被冠层的水分含量情况。
    特点：由于植被在短波红外波段对水分的强吸收，导致植被在短波红外波段的反射率相对于近红外波段的反射率要小，因此 NDMI 与冠层水分含量高度相关，
    可以用来估计植被水分含量，而且 NDMI 与地表温度之间存在较强的相关性，因此也常用于分析地表温度的变化情况。
    使用阶段：作物水分含量与地表温度的变化情况。

    :param img_data: 输入影像矩阵
    :param geotrans: 输入影像仿射系数
    :param proj: 输入影像坐标系
    :param out_path: 输出影像存储路径
    """
    nir_arr = img_data[3, :, :]
    swir1_arr = img_data[5, :, :]

    denominator = np.array(nir_arr + swir1_arr, dtype=np.float32)
    numerator = np.array(nir_arr - swir1_arr, dtype=np.float32)
    nodata = np.full((nir_arr.shape[0], nir_arr.shape[1]), -999, dtype=np.float32)
    ndmi = np.true_divide(numerator, denominator, out=nodata, where=denominator != 0.0)
    # print(np.min(ndmi), np.max(ndmi))
    ndmi[ndmi == -999.0] = None
    helper.write_tiff(ndmi, geotrans, proj, out_path)


def cal_ndwi(img_data, geotrans, proj, out_path):
    """
    计算归一化水体指数 NDWI = (GREEN - NIR) / (GREEN + NIR)
    NDWI 利用绿光波段和近红外波段的差异比值来增强水体信息，并减弱植被、土壤、建筑物等地物的信息。
    特点：NDWI 指数经常与 NDMI（归一化差值水分指数）混淆。该指数在纯水体提取方面具有很大的优势，然而该指数不能很好地抑制山体阴影以及高建筑物阴影。
    使用阶段：检测被淹的农田；现场分配洪水；检测灌溉农田；湿地分配。

    :param img_data: 输入影像矩阵
    :param geotrans: 输入影像仿射系数
    :param proj: 输入影像坐标系
    :param out_path: 输出影像存储路径
    """
    green_arr = img_data[1, :, :]
    nir_arr = img_data[3, :, :]

    denominator = np.array(green_arr + nir_arr, dtype=np.float32)
    numerator = np.array(green_arr - nir_arr, dtype=np.float32)
    nodata = np.full((green_arr.shape[0], green_arr.shape[1]), -999, dtype=np.float32)
    ndwi = np.true_divide(numerator, denominator, out=nodata, where=denominator != 0.0)
    # print(np.min(ndwi), np.max(ndwi))
    ndwi[ndwi == -999.0] = None
    helper.write_tiff(ndwi, geotrans, proj, out_path)
