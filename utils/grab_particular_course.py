#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# utils/grab_particular_course.py
import requests
import json
import update_weu
from settings import *

def grab_particular_course(new_bgbm):
    # 1. 构造动态 data
    payload = {
        "data": json.dumps({"BGBM": new_bgbm}, ensure_ascii=False)
    }

    # 2. 发送请求
    session = requests.Session()
    try:
        response = session.post(
            url["grab_courses"],
            headers=headers,
            cookies=cookies,
            data=payload,
            timeout=timeout
        )

        Path(RESPONSE_FILE).write_text(response.text, encoding="utf-8")

        print(f"\n选课请求已发送")
        print(f"状态码: {response.status_code}")
        print(f"响应内容:{response.text}")
        grab_course_res = json.loads(response.text)
        # 3. 更新_WEU
        update_weu.update_weu(response.headers)

        return grab_course_res.get("code") == "0" and grab_course_res.get("msg") == "成功"
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return False


if __name__ == "__main__":
    grab_particular_course(particular_course)



