#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# build_query_string.py
import yaml
import json
from settings import data_raw
from urllib.parse import quote


def build_unselected_query_string():
    params = []

    # 遍历 data-raw 中的每个键值对
    for key, value in data_raw.items():
        if key == 'querySetting':
            # querySetting 是列表，需要 JSON 序列化后 URL 编码
            query_json = json.dumps(value, ensure_ascii=False)
            encoded_query = quote(query_json)
            params.append(f"querySetting={encoded_query}")
        else:
            # 其他字段直接编码（支持布尔值自动转字符串）
            encoded_value = quote(str(value))
            params.append(f"{key}={encoded_value}")

    # 拼接为最终字符串
    query_string = "&".join(params)
    return query_string

def build_selected_query_string():
    params = []
    for key, value in data_raw.items():
        if key == 'querySetting':
            # 什么都不做
            continue
        else:
            encoded_value = quote(str(value))
            params.append(f"{key}={encoded_value}")
    # 拼接为最终字符串
    query_string = "&".join(params)
    return query_string


if __name__ == '__main__':
    print("Building query string")