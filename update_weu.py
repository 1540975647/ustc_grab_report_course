#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# update_weu.py
import yaml
import re
from pathlib import Path
from settings import CONFIG_YAML_PATH

# ------------------- 1. default response_headers  -------------------
res = {
    'Server': 'nginx',
    'Date': 'Tue, 28 Oct 2025 03:13:43 GMT',
    'Content-Type': 'application/json;charset=UTF-8',
    'Transfer-Encoding': 'chunked',
    'Connection': 'keep-alive',
    'Keep-Alive': 'timeout=20',
    'Vary': 'Accept-Encoding',
    'Set-Cookie': '_WEU=xxxxx',
    'X-Upstream-IP': '20',
    'X-Frame-Options': 'SAMEORIGIN',
    'Content-Encoding': 'gzip',
    'Strict-Transport-Security': 'max-age=15769000'
}


def update_weu(response_headers):
    # ------------------- 2. 提取 _WEU 值 -------------------
    cookie_str = response_headers.get('Set-Cookie', '')
    match = re.search(r'_WEU=([^;]+)', cookie_str)
    if not match:
        print("未在 Set-Cookie 中找到 _WEU")
        return None
    weu_value = match.group(1)

    print(f"提取到的 _WEU: {weu_value[:60]}...")

    # ------------------- 3. 更新 config.yml（只更新 _WEU） -------------------
    CONFIG_FILE = Path(CONFIG_YAML_PATH)

    try:
        # 读取
        with CONFIG_FILE.open('r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}

        # 确保 cookies 存在
        cookies_dict = config.setdefault('cookies', {})
        # 关键：更新 _WEU（已存在则覆盖）
        cookies_dict['_WEU'] = weu_value
        # 写回（保持 2 空格缩进 + 字段顺序）
        with CONFIG_FILE.open('w', encoding='utf-8') as f:
            yaml.safe_dump(
                config,
                f,
                allow_unicode=True,
                default_flow_style=False,
                indent=2,
                sort_keys=False  # 保持原有顺序
            )
    except FileNotFoundError:
        print("config.yml not exists!")



    print(f"_WEU 已成功更新到 {CONFIG_FILE}")
    return True


if __name__ == '__main__':
    update_weu(res)