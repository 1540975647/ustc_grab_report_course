#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# main.py
from utils import search_report, grab_courses, send_success_email, send_fail_email, handle_post_result


def runAll():
    # 示例：发送查询课程请求
    has_searched_useful_courses, post_result = search_report.search_report_and_write()
    if handle_post_result(post_result):
        send_fail_email(post_result)
    if not has_searched_useful_courses:
        return

    # 示例：加载课程
    try:
        while True:
            grab_success, first_item = grab_courses()
            if not grab_success:
                return
            send_success_email(first_item)
            search_report.search_report_and_write()

    except FileNotFoundError:
        print("课程文件未找到")


if __name__ == "__main__":
    runAll()
