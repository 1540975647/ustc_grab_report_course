#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

# utils/withdraw_exclude_courses.py
import json
from settings import *
from build_query_string import build_selected_query_string
from utils.search_report import search_report
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
        return search_report("search_selected_report", build_selected_query_string())


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
        success, response = self.search_selected_courses()

        # 安全提取 rows 列表
        try:
            self.selected_courses_json = response['datas']['yxbgbgdz']['rows']
        except (KeyError, TypeError):
            print("错误: 数据结构不符合预期，缺少 datas.yxbgbgdz.rows")
            return


        if not success:
            # 查询已选课程失败，直接结束
            return False

        # 查询已选课程成功
        print(self.selected_courses_json)
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