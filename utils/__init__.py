#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# utils/__init__.py
from .search_report import search_report_and_write
from .grab_courses import grab_courses  # 假设函数在此文件中
from .send_email import send_success_email, send_fail_email  # 假设函数在此文件中
from .handle_post_result import handle_post_result

# 重新导出为更简洁的名称（可选）
search_report = type('obj', (), {})()  # 创建伪对象
setattr(search_report, 'search_report_and_write', search_report_and_write)

# 或者直接导出函数（更直接）
__all__ = [
    'search_report',
    'grab_courses',
    'send_success_email',
    'send_fail_email',
    'handle_post_result'
]

# __all__ = ["search_report_and_write",
#            "grab_courses",
#            "send_success_email",
#            "send_fail_email",
#            "handle_post_result"
#            ]


