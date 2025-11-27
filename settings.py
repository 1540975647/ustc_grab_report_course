#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# settings.py
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# ==================== 加载 .env ====================
load_dotenv()  # 自动加载项目根目录下的 .env

# ==================== 基础路径 ====================
BASE_DIR = parent_dir = Path(__file__).resolve().parent
# 配置路径
CONFIG_YAML_PATH: Path = BASE_DIR / "config.yml"
SEARCH_FAIL_MSG_FILE: Path = BASE_DIR / "search_fail_msg.txt"
# 搜索获取到的课程
COURSE_FILE = BASE_DIR / os.getenv("COURSE_FILE", "courses.json")
# 选课获取到的响应
RESPONSE_FILE = BASE_DIR / os.getenv("RESPONSE_FILE", "response.json")
# 排除不自动选择的课程
EXCLUDE_FILE = BASE_DIR / os.getenv("EXCLUDE_FILE", "exclude.json")
EXCLUDE_BGBM = "EXCLUDE_BGBM"


if not CONFIG_YAML_PATH.exists():
    raise FileNotFoundError(f"配置文件未找到: {CONFIG_YAML_PATH}")

with open(CONFIG_YAML_PATH, "r", encoding="utf-8") as f:
    _yaml_data: Dict[str, Any] = yaml.safe_load(f) or {}


#  邮件配置
email_settings: Dict[str, any] = _yaml_data.get("email")

# ==================== Cookies ====================
# cookies
cookies = _yaml_data.get("cookies")
# hearders
headers: Dict[str, str] = _yaml_data.get("headers", {})
# url
base_url = _yaml_data.get("base_url", "")
urls: Dict[str, str] = _yaml_data.get("urls", {})
url = {k: f"{base_url}{v}" for k, v in urls.items()}
# 过期时间
timeout: int = _yaml_data.get("timeout")
# 特定抢课退课
particular_course = _yaml_data.get("particular_course").get("BGBM")
# 保活时退课与选课之间的间隔（秒）
interval: int = _yaml_data.get("interval")
# 发送请求时的参数
data_raw = _yaml_data.get("data_raw")

