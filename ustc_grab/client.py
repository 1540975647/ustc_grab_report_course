import json
import requests
import re
from urllib.parse import quote
from typing import Dict, Any, Tuple, Optional
from .config import Config

class USTCClient:
    """
    HTTP Client for interacting with USTC Graduate School system.
    Handles authentication, request building, and session management.
    """
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        # Initialize headers in session if needed, but we usually pass them per request
        # to ensure we use the latest from config if they change? 
        # Actually config loads them once. Let's trust config.

    def _update_weu_if_present(self, headers: Dict[str, str]):
        """Checks for _WEU in Set-Cookie and updates config if found."""
        cookie_str = headers.get('Set-Cookie', '')
        match = re.search(r'_WEU=([^;]+)', cookie_str)
        if match:
            weu_value = match.group(1)
            print(f"Detected new _WEU, updating config...")
            self.config.update_weu_cookie(weu_value)

    def _build_query_string(self, need_query_setting: bool) ->  str:
        """Constructs the complex query string required by the API."""
        params = []
        data_raw = self.config.data_raw
        
        for key, value in data_raw.items():
            if key != 'querySetting':
                encoded_value = quote(str(value))
                params.append(f"{key}={encoded_value}")
            elif need_query_setting:
                # querySetting is a list/object that needs JSON dumps then Quote
                query_json = json.dumps(value, ensure_ascii=False)
                encoded_query = quote(query_json)
                params.append(f"querySetting={encoded_query}")
                
        return "&".join(params)

    def _build_grade_query_string(self) -> str:
        """Constructs specific query string for grades."""
        params = []
        grade_data = self.config.grade_data
        
        for key, value in grade_data.items():
            if key == 'querySetting':
                # querySetting is an empty list as per user payload
                query_json = json.dumps(value, ensure_ascii=False)
                encoded_query = quote(query_json)
                params.append(f"querySetting={encoded_query}")
            else:
                encoded_value = quote(str(value))
                params.append(f"{key}={encoded_value}")
                
        return "&".join(params)

    def _post(self, url_key: str, data: Any = None, is_raw_data: bool = False, headers: Optional[Dict[str, str]] = None) -> Tuple[bool, Any]:
        """
        Generic POST request handler.
        :param url_key: The key in config.urls to fetch the URL.
        :param data: The data payload (dict or string).
        :param is_raw_data: If True, data is sent as-is.
        :param headers: Optional headers to merge/override global config headers.
        """
        target_url = self.config.urls.get(url_key)
        if not target_url:
            return False, f"URL key '{url_key}' not found in configuration."

        # Merge headers: start with global, override with specific
        request_headers = self.config.headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            # Note: The original code passed 'data' argument. 
            # For search_report, it passed a query string.
            # For grab/withdraw, it passed a dict, which requests converts to form-urlencoded.
            
            response = self.session.post(
                target_url,
                headers=request_headers,
                cookies=self.config.cookies,
                data=data,
                timeout=self.config.timeout
            )
            
            self._update_weu_if_present(response.headers)
            
            # For debugging/logging
            # print(f"Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"HTTP Error: {response.status_code}")
                return False, response.text

            try:
                # Try parsing as JSON
                json_data = response.json()
                return True, json_data
            except json.JSONDecodeError:
                return False, response.text
                
        except requests.RequestException as e:
            print(f"Request Exception: {e}")
            return False, str(e)

    def search_unselected_report(self) -> Tuple[bool, Any]:
        """Searches for unselected reports (courses)."""
        query_string = self._build_query_string(need_query_setting=True)
        headers = self.config.app_specific_headers.get('xsbg')
        return self._post("search_unselected_report", data=query_string, is_raw_data=True, headers=headers)

    def grab_course(self, bgbm: str) -> bool:
        """Attempts to grab a specific course by BGBM."""
        payload = {
            "data": json.dumps({"BGBM": bgbm}, ensure_ascii=False)
        }
        headers = self.config.app_specific_headers.get('xsbg')
        success, result = self._post("grab_courses", data=payload, headers=headers)
        
        if success and isinstance(result, dict):
            print(f"Grab result: {result}")
            return result.get("code") == "0" and result.get("msg") == "成功"
        return False

    def withdraw_course(self, bgbm: str) -> bool:
        """Attempts to withdraw from a specific course by BGBM."""
        payload = {
            "data": json.dumps({"BGBM": bgbm}, ensure_ascii=False)
        }
        headers = self.config.app_specific_headers.get('xsbg')
        success, result = self._post("withdraw_courses", data=payload, headers=headers)
        
        if success and isinstance(result, dict):
            print(f"Withdraw result: {result}")
            return result.get("code") == "0" and result.get("msg") == "成功"
        return False

    def get_grades(self) -> Tuple[bool, Any]:
        """Fetches grade data."""
        query_string = self._build_grade_query_string()
        headers = self.config.app_specific_headers.get('wdcj')
        return self._post("check_grade", data=query_string, is_raw_data=True, headers=headers)
