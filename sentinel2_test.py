#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: sentinel2_test.py
Version: v1.0
Date: 2023-01-13
Authors: Chen G.
Description: This script creates downloading and processing Sentinel-2 images.
License: This code is distributed under the MIT License.

    sentinel2_download Parameter:
        USER_NAME: The account name to log in ESA Copernicus Open Access Hub (https://scihub.copernicus.eu/).
        PASSWORD: The account password to log in ESA Copernicus Open Access Hub.
        FOOTPRINT: The region to include imagery within.
        START_DATE: A time interval filter based on the Sensing Start Time of the products. Following formats:
            - yyyyMMdd
            - yyyy-MM-ddThh:mm:ss.SSSZ (ISO-8601)
            - yyyy-MM-ddThh:mm:ssZ
            - NOW
            - NOW-<n>DAY(S) (or HOUR(S), MONTH(S), etc.)
            - NOW+<n>DAY(S)
            - yyyy-MM-ddThh:mm:ssZ-<n>DAY(S)
            - NOW/DAY (or HOUR, MONTH etc.) - rounds the value to the given unit
        END_DATE: A time interval filter based on the Sensing Start Time of the products.
        PRODUCT_TYPE: Type of sentinel-2 product to apply (String):
            'S2MSI2A' - Sentinel-2 MSI L2A product
            'S2MSI1C' - Sentinel-2 MSI L1C product
            'S2MS2Ap' - Sentinel-2 MSI L2Ap product
        CLOUD_COVER_PERCENTAGE: (Optional) cloud cover percentage to apply s2 products filter.
        SAVE_DIR: Download the sentinel-2 images to local.


    """

import datetime
import sentinel2_download as s2d
import sentinel2_process as s2p


# Parameters
s2_download_parameter = {'USER_NAME': 'gongchen9369',
                         'PASSWORD': '13919389875er',
                         'FOOTPRINT': 'POLYGON((115.5 40.2, 116.0 40.2, 116.0 40.5, 115.5 40.5, 115.5 40.2))',
                         'START_DATE': '20220801',
                         'END_DATE': '20220901',
                         'PRODUCT_TYPE': 'S2MSI2A',
                         'CLOUD_COVER_PERCENTAGE': 30,
                         'SAVE_DIR': 'G:/s2_processing/download'
                         }

s2_l2a_parameter = {'INPUT_PATH': 'G:/s2_processing/l2a/raw',
                    'OUTPUT_PATH': 'G:/s2_processing/l2a/export',
                    'QUICK_IMG': False,
                    'REPROJECT': False,
                    'CRS': 'EPSG:4326',
                    'CLIP_TO_SHP': False,
                    'SHP_FILE_PATH': 'G:/s2_processing/l2a/shp/clippolygon.shp',
                    'CAL_NDVI': True,
                    'CAL_NDRE': True,
                    'CAL_OSAVI': True,
                    'CAL_LCI': True,
                    'CAL_GNDVI': True,
                    'CAL_RECI': True,
                    'CAL_NDMI': True,
                    'CAL_NDWI': True
                    }

s2_l1c_parameter = {'INPUT_PATH': 'G:/s2_processing/l1c/raw',
                    'OUTPUT_PATH': 'G:/s2_processing/l1c/export',
                    'QUICK_IMG': True,
                    'REPROJECT': True,
                    'CRS': 'EPSG:4326',
                    'CLIP_TO_SHP': True,
                    'SHP_FILE_PATH': 'G:/s2_processing/l1c/shp/lingang_field.shp',
                    'CAL_NDVI': True,
                    'CAL_NDRE': True,
                    'CAL_OSAVI': True,
                    'CAL_LCI': True,
                    'CAL_GNDVI': True,
                    'CAL_RECI': True,
                    'CAL_NDMI': True,
                    'CAL_NDWI': True
                    }

# /***************************/
# // MAIN
# /***************************/
if __name__ == "__main__":
    start_time = datetime.datetime.now()

    # (1) Sentinel-2产品数据下载
    s2d.s2_download(s2_download_parameter)

    # (2) Sentinel-2 L1C格式产品数据处理
    # s2p.s2_l2a_process(s2_l2a_parameter)

    # (3) Sentinel-2 L2A格式产品数据处理
    # s2p.s2_l1c_process(s2_l1c_parameter)

    end_time = datetime.datetime.now()
    print("Elapsed Time:", end_time - start_time)  # 输出程序运行所需时间
