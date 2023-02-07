from sentinelsat import SentinelAPI
import os


# ---------------------------------------------------#
#   从欧空局官网下载Sentinel2数据
# ---------------------------------------------------#
def s2_download(params):
    """
    Downloading S2 images from ESA.

    param: params
        These parameters determine the data selection and image saving parameters.
    """
    USER_NAME = params['USER_NAME']
    PASSWORD = params['PASSWORD']
    FOOTPRINT = params['FOOTPRINT']
    START_DATE = params['START_DATE']
    END_DATE = params['END_DATE']
    PRODUCT_TYPE = params['PRODUCT_TYPE']
    CLOUD_COVER_PERCENTAGE = params['CLOUD_COVER_PERCENTAGE']
    SAVE_DIR = params['SAVE_DIR']

    ###########################################
    # 0. CHECK PARAMETERS
    ###########################################

    if USER_NAME is None:
        raise ValueError("ERROR!!! Parameter USER_NAME is none")
    if PASSWORD is None:
        raise ValueError("ERROR!!! Parameter PASSWORD is none")
    if START_DATE is None:
        raise ValueError("ERROR!!! Parameter START_DATE not correctly defined")
    if END_DATE is None:
        raise ValueError("ERROR!!! Parameter END_DATE not correctly defined")
    if SAVE_DIR is None:
        raise ValueError("ERROR!!! Parameter SAVE_DIR is none")

    product_type_required = ['S2MSI2A', 'S2MSI1C', 'S2MS2Ap']
    if PRODUCT_TYPE not in product_type_required:
        raise ValueError("ERROR!!! Parameter PRODUCT_TYPE not correctly defined")

    ###########################################
    # 1. DATA SELECTION
    ###########################################

    # 登录ESA API
    api = SentinelAPI(USER_NAME, PASSWORD, 'https://apihub.copernicus.eu/apihub')

    # 使用API接口查询
    products = api.query(FOOTPRINT,
                         date=(START_DATE, END_DATE),
                         platformname='Sentinel-2',
                         producttype=PRODUCT_TYPE,
                         cloudcoverpercentage=(0, CLOUD_COVER_PERCENTAGE))

    print(f"一共检索到{len(products)}景符合条件的数据\n")
    for product in enumerate(products):
        product_info = api.get_product_odata(str(product))
        # 打印下载的产品数据文件名
        print(product_info['title'])

    ###########################################
    # 2. DOWNLOAD DATA
    ###########################################

    # 创建下载路径
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    # 下载检索数据，对于长期存档的数据（3-6个月以上），会出现offline情况，在下载的时候，需要先请求，后台将数据调档至在线，时间大概是半个小时，才能下载
    for i, product in enumerate(products):
        # 通过OData API获取单一产品数据的主要元数据信息
        product_info = api.get_product_odata(product)
        # 判断数据可以在线下载
        if product_info['Online']:
            print('Product {} is online.Starting download...'.format(product_info['title']))  # 打印产品文件名
            api.download(product_info['id'], SAVE_DIR)
        # 历史存档数据(“Offine”的情况)，暂时不下载和触发LAT标记
        else:
            print('Product {} is not online.'.format(product_info['date']))
