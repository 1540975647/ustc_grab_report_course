#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# utils/search_report.py

import requests
import update_weu
from settings import *


def search_report(search_type, query_string) -> tuple:
    """
    发送 POST 请求，返回响应数据。
    """

    session = requests.Session()

    try:
        response = session.post(
            url=url.get(search_type),
            headers=headers,
            cookies=cookies,
            data=query_string,
            timeout=timeout
        )
        # 更新_WEU
        print(response.headers)
        update_weu.update_weu(response.headers)

        response.raise_for_status()

        # 尝试解析 JSON
        try:
            json_data = response.json()
            print("请求成功，接收到 JSON 数据（已过滤特定院系）：")
            # print(json.dumps(json_data, ensure_ascii=False, indent=2))
            return True, json_data
        except ValueError:
            print("响应非 JSON 格式，原始文本如下：")
            print(response.text)
            return False, response.text

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误: {http_err}")
        print(f"状态码: {response.status_code}")
        print(f"响应体: {response.text}")
        return False, f"HTTP 错误: {http_err}, 状态码: {response.status_code}, 响应体: {response.text}"
    except requests.exceptions.RequestException as req_requests_err:
        print(f"请求异常: {req_requests_err}")
        return False, f"请求异常: {req_requests_err}"
    except Exception as err:
        print(f"未知错误: {err}")
        return False, f"未知错误: {err}"