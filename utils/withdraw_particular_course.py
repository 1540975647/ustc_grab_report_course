#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from settings import *
import update_weu



def withdraw_particular_course(bgbm):

    # Define the raw payload (URL-encoded form data)
    payload = {
        "data": json.dumps({"BGBM": bgbm}, ensure_ascii=False)
    }
    # Create a session to persist cookies and settings
    session = requests.Session()

    # Send the POST request
    response = session.post(
        url.get("withdraw_courses"),
        headers=headers,
        cookies=cookies,
        data=payload
    )
    print("退课请求已发送")
    update_weu.update_weu(response.headers)

    # Output the response
    print(f"状态码：{response.status_code}")
    # print(f"Status Code: {response.status_code}")
    # print("Response Body:")
    print("响应内容: {}", response.text)
    # return response.headers


if __name__ == "__main__":
    withdraw_particular_course(particular_course)
