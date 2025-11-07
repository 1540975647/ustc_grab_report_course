#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# main_update_weu.py
import random
from time import sleep
from utils.grab_particular_course import grab_particular_course
from utils.withdraw_particular_course import withdraw_particular_course
from settings import *

def run_keep_alive():
    sleep(random.randint(0, 60))
    print("开始保活_WEU...")
    # 保活时首先退课
    print("开始退课")
    withdraw_particular_course(particular_course)
    print(f"{interval}秒后开始选课")
    for i in range(interval):
        print(f"还有{interval - i}秒开始选课")
        sleep(1)

    # 选课
    print("开始选课")
    grab_particular_course(particular_course)

if __name__ == "__main__":
    run_keep_alive()
