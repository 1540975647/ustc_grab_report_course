import yaml
import json
from settings import CONFIG_YAML_PATH
from urllib.parse import quote


def build_query_string(config_path=CONFIG_YAML_PATH):
    # 读取 YAML 文件
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    data_raw = config.get('data-raw', {})

    params = []

    # 遍历 data-raw 中的每个键值对
    for key, value in data_raw.items():
        if key == 'querySetting':
            # querySetting 是列表，需要 JSON 序列化后 URL 编码
            query_json = json.dumps(value, ensure_ascii=False)
            encoded_query = quote(query_json)
            params.append(f"querySetting={encoded_query}")
        else:
            # 其他字段直接编码（支持布尔值自动转字符串）
            encoded_value = quote(str(value))
            params.append(f"{key}={encoded_value}")

    # 拼接为最终字符串
    query_string = "&".join(params)
    return query_string


if __name__ == '__main__':
    print("Building query string")