#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# utils/grab_courses.py
import json
from typing import Any
from . import grab_particular_course
from settings import COURSE_FILE


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

    # 2. 尝试发送选课请求
    grab_success = grab_particular_course.grab_particular_course(new_bgbm)
    if grab_success:
        return True, first_item
    else:
        return False, None


if __name__ == "__main__":
    grab_courses()

