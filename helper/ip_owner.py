'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-17 10:32:32
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-17 10:33:14
FilePath: /miaosuan2/helper/ip_owner.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import requests


def _get_public_ip() -> str:
    ip = requests.get("https://api.ipify.org").text
    return ip

def _get_geo_info(ip) -> tuple:
    url = f"http://ip-api.com/json/{ip}?lang=zh-CN"
    resp = requests.get(url)
    data = resp.json()
    if data['status'] == 'success':
        return data['country'], data['regionName']
    else:
        return None, None

def is_chinese_mainland() -> bool:
    ip = _get_public_ip()
    country, region = _get_geo_info(ip)
    if country != "中国":
        return False
    if region != "香港" or region != "澳门" or region != "台湾":
        return False
    return True
 