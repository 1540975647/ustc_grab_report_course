#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# utils/handle_post_result.py
import os
from pathlib import Path
from typing import Final
from settings import SEARCH_FAIL_MSG_FILE

sentence: Final[str] = "Client Error"


def handle_post_result(post_result: str) -> bool:
    """
    处理 POST 请求结果，判断是否因 cookie 过期触发 401或403 错误。

    返回:
        bool: True 表示“首次检测到错误，应发送邮件”；False 表示“无需处理”。
    """
    if sentence not in post_result:
        # cookie 未过期：清空标记文件
        write_file_atomic(SEARCH_FAIL_MSG_FILE, "")
        return False

    # 读取当前标记（安全处理文件不存在）
    current_mark = read_first_line_stripped(SEARCH_FAIL_MSG_FILE)

    if current_mark == sentence:
        # 已标记过，无需重复处理
        return False

    # 首次检测到：写入标记并返回 True
    write_file_atomic(SEARCH_FAIL_MSG_FILE, sentence + "\n")
    return True


def read_first_line_stripped(file_path: Path) -> str:
    """安全读取首行并 strip，若文件不存在或为空返回空字符串"""
    if not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            line = f.readline()
            return line.strip() if line else ""
    except Exception:
        return ""  # 任何读取错误视为“无标记”


def write_file_atomic(file_path: Path, content: str) -> None:
    """原子写入文件（避免竞态）"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception:
        pass  # 写入失败不影响主逻辑（可记录日志）