#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

import requests

# utils/withdraw_exclude_courses.py
import update_weu
import build_query_string
from settings import *
from utils.send_email import send_withdraw_exclude_course_success
from utils.withdraw_particular_course import withdraw_particular_course

class SearchExcludeCourses:
    # 排除的课程
    exclude_courses = []

    # 已经选择的课程
    selected_courses_json = []

    def __init__(self):
        self.exclude_courses = []
        self.selected_courses_json = []


    # 查询已经选择的课程
    def search_selected_courses(self):

        session = requests.Session()
        query_string = build_query_string.build_selected_query_string()
        # print(query_string)
        # print(url.get("withdraw_courses"))
        try:
            response = session.post(
                url=url.get("search_selected_report"),
                headers=headers,
                cookies=cookies,
                data="*order=-BGSJ&pageSize=20&pageNumber=1",
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
                print (json_data)
                return True, json_data["datas"]["yxbgbgdz"]["rows"]
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


    # 查询排除文件中的课程
    def search_exclude_courses(self):
        # 单例模式
        if len(self.exclude_courses) == 0:
            try:
                with open(EXCLUDE_FILE, 'r', encoding='utf-8') as f:
                    self.exclude_courses = json.load(f).get(EXCLUDE_BGBM, [])  # 默认空列表防 None
            except FileNotFoundError:
                self.exclude_courses = []
        return self.exclude_courses


    def withdraw_exclude_courses(self):
        self.exclude_courses = self.search_exclude_courses()
        success, self.selected_courses_json = self.search_selected_courses()

        if not success:
            # 查询已选课程失败，直接结束
            return False

        # 查询已选课程成功
        for exclude_course in self.exclude_courses:
            for selected_course_json in self.selected_courses_json:
                if exclude_course == selected_course_json['BGBM']:
                    # 需要退课
                    print(f"查询到已选择的排除项：{exclude_course}")
                    if withdraw_particular_course(exclude_course):
                        send_withdraw_exclude_course_success(selected_course_json)

        return True

if __name__ == "__main__":
    SearchExcludeCourses().withdraw_exclude_courses()