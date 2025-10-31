#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import update_weu
from typing import Any
from pathlib import Path
from settings import RESPONSE_FILE, COURSE_FILE
from settings import url, headers, cookies, timeout


def load_bgbm_from_json(filename: str) -> None | tuple[None, None] | tuple[Any, Any]:
    """
    从 JSON 文件中读取第一条记录的 BGBM。
    若文件为空或不存在，返回 None。
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                bgbm = first_item.get("BGBM")
                if bgbm:
                    print(f"检测到可用报告，使用 BGBM: {bgbm}")
                    print(f"   报告主题: {first_item.get('BGTMZW', '未知')}")
                    print(f"   报告时间: {first_item.get('BGSJ', '未知')}")
                    return bgbm, first_item
            else:
                print("JSON 文件中无可用报告记录。")
                return None, None
    except FileNotFoundError:
        print(f"错误: 未找到文件 {filename}，请先运行过滤脚本生成。")
        return None, None
    except json.JSONDecodeError:
        print(f"错误: {filename} 不是有效的 JSON 文件。")
        return None, None


def grab_courses():
    # 1. 尝试读取 BGBM
    new_bgbm, first_item = load_bgbm_from_json(COURSE_FILE)
    if not new_bgbm:
        print("无可用 BGBM，终止选课请求。")
        return False, None

    # 2. 构造动态 data
    payload = {
        "data": json.dumps({"BGBM": new_bgbm}, ensure_ascii=False)
    }

    # 3. 发送请求
    session = requests.Session()
    try:
        response = session.post(
            url["grab_courses"],
            headers=headers,
            cookies=cookies,
            data=payload,
            timeout=timeout
        )
        # 更新_WEU
        update_weu.update_weu(response.headers)

        Path(RESPONSE_FILE).write_text(response.text, encoding="utf-8")

        print(f"\n选课请求已发送")
        print(f"状态码: {response.status_code}")
        print("响应内容:", end="\t")
        grab_course_res = json.loads(response.text)

        grab_course_res_headers = response.headers
        # print(grab_course_res_headers)
        print (response.text)
        if grab_course_res.get("code") == "0" and grab_course_res.get("msg") == "成功":
            return True, first_item
        else:
            return False, None

    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return False, None


if __name__ == "__main__":
    grab_courses()

