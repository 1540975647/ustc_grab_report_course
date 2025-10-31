# main.py
import requests
import json
import update_weu
from settings import *

def grab_particular_course(new_bgbm):
    # 2. 构造动态 data
    payload = {
        "data": json.dumps({"BGBM": new_bgbm}, ensure_ascii=False)
    }
    session = requests.Session()
    try:
        response = session.post(
            url["grab_courses"],
            headers=headers,
            cookies=cookies,
            data=payload,
            timeout=timeout
        )
        # 更新_WEU
        update_weu.update_weu(response.headers)

        Path(RESPONSE_FILE).write_text(response.text, encoding="utf-8")

        print(f"\n选课请求已发送")
        print(f"状态码: {response.status_code}")
        print("响应内容:", end="\t")
        grab_course_res = json.loads(response.text)

        grab_course_res_headers = response.headers
        # print(grab_course_res_headers)
        print(response.text)
        if grab_course_res.get("code") == "0" and grab_course_res.get("msg") == "成功":
            return True
        else:
            return False

    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return False


if __name__ == "__main__":
    grab_particular_course(particular_course)



