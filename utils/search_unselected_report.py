#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# utils/search_unselected_report.py
"""
Description:
    使用 requests 库向 USTC 研究生报到管理系统发送带过滤条件的 POST 请求，
    查询特定院系（如计算机、软件学院等）的学生报到数据。
    已完整保留原始请求的 headers、cookies 和复杂 data 参数。

    注意：Cookie 中的 GS_DBLOGIN_TOKEN , GS_SESSIONID, _WEU 具有时效性，请确保有效。
"""

import json

from build_query_string import build_unselected_query_string
from utils.withdraw_exclude_courses import SearchExcludeCourses
from utils.search_report import search_report
from datetime import datetime
from typing import List, Dict, Any
from settings import COURSE_FILE


# ==================== 配置区域 ====================

# ================================================

def search_unselected_report():
    return search_report("search_unselected_report" , build_unselected_query_string())


def parse_date(date_str: str) -> datetime:
    """
    解析 BGSJ 日期字符串，支持 'YYYY-MM-DD HH:MM' 或 'YYYY-MM-DD HH:MM:SS'
    """
    if date_str is None:
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            return datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(f"日期格式错误，跳过: {date_str}")
            return None


def filter_and_write_reports(
        input_data: Dict[str, Any],
        filename: str = COURSE_FILE
) -> bool | None:
    """
    从嵌套结构中提取 rows，过滤后写入文件。
    过滤条件：
        1. BGSJ 不为 null 且晚于今日（含时间）
        2. KXRS (int) < YXRS (str → int)
    """
    # 1. 安全提取 rows 列表
    try:
        rows = input_data["datas"]["wxbgbgdz"]["rows"]
    except (KeyError, TypeError):
        print("错误: 数据结构不符合预期，缺少 datas.wxbgbgdz.rows")
        return

    today = datetime.now()
    filtered_rows: List[Dict[str, Any]] = []

    for item in rows:
        dd = item.get("DD")
        bgsj_str = item.get("BGSJ")
        yxrs_str = item.get("YXRS")
        jzsj_str = item.get("JZSJ")
        kxrs = item.get("KXRS")
        bgbm = item.get("BGBM")
        bgtmzw = item.get("BGTMZW")

        # --- 条件 0: DD 必须包含 "高新"或者 "G" 或者 "直播"
        # if dd is None or not ("高新" in dd or "G" in dd or "g" in dd or "直播" in dd or "先" in dd):
        #     continue

        # --- 条件 1: BGSJ（报告时间） 和 JZSJ（截至时间）必须有效且晚于今天 ---
        bgsj_dt = parse_date(bgsj_str)
        jzsj_dt = parse_date(jzsj_str)
        if bgsj_dt is None or bgsj_dt <= today:
            continue
        if jzsj_dt is None or jzsj_dt <= today:
            continue

        # --- 条件 2: YXRS 转为整数 ---
        try:
            yxrs_int = int(yxrs_str) if yxrs_str is not None else 0
        except (ValueError, TypeError):
            print(f"警告: YXRS 无法转换为整数，跳过记录: {yxrs_str}")
            continue

        # --- 条件 3: KXRS（可选人数） 是整数且必须大于 YXRS （已选人数） ---
        if not isinstance(kxrs, int):
            try:
                kxrs = int(kxrs)
            except (ValueError, TypeError):
                continue
        if kxrs <= yxrs_int:
            continue

        # --- 条件 4： 该BGBM 存在于排除序列(exclude.json)中
        try:
            exclude_bgbms = SearchExcludeCourses().search_exclude_courses()
            if bgbm in exclude_bgbms:  # 直接使用 in 操作符，简洁高效
                print(f"包含排除文件里的课程，课程号：{bgbm}，课程主题：{bgtmzw}")
                continue
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            # 可选：记录日志或默认行为（如视作无排除）
            pass

        # 所有条件满足
        filtered_rows.append(item)

    # --- 写入文件 ---
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(filtered_rows, f, ensure_ascii=False, indent=4)

    print(f"筛选完成：共保留 {len(filtered_rows)} 条符合条件的报告")
    print(f"文件已保存至: {filename}")
    if len(rows) > len(filtered_rows):
        print(f"共排除 {len(rows) - len(filtered_rows)} 条不符合条件的记录")

    return len(filtered_rows) > 0


def search_report_and_write():
    print("正在向 USTC 研究生综合服务平台发送查询报告请求（计算机、软件学院等）...")
    post_flag, post_result = search_unselected_report()
    has_searched_useful_courses = False
    if post_flag:
        # 写入 JSON 文件
        print(post_result)
        has_searched_useful_courses = filter_and_write_reports(post_result, COURSE_FILE)

        print("\n任务完成，JSON 数据已成功写入 data.json。")
    else:
        print("\n任务失败。")

    return has_searched_useful_courses, post_result


if __name__ == "__main__":
    search_report_and_write()
