#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# withdraw_particular_course.py
import json
import requests
from settings import *
import update_weu


def withdraw_particular_course(bgbm):
    # 1. 构造动态 data
    payload = {
        "data": json.dumps({"BGBM": bgbm}, ensure_ascii=False)
    }

    # 2. 发送请求
    session = requests.Session()
    try:
        response = session.post(
            url.get("withdraw_courses"),
            headers=headers,
            cookies=cookies,
            data=payload
        )
        print("退课请求已发送")
        print(f"状态码：{response.status_code}")
        print("响应内容: {}", response.text)
        withdraw_course_res = json.loads(response.text)

        # 3. 更新_WEU
        update_weu.update_weu(response.headers)

        return withdraw_course_res.get("code") == "0" and withdraw_course_res.get("msg") == "成功"
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return False


if __name__ == "__main__":
    withdraw_particular_course(particular_course)
