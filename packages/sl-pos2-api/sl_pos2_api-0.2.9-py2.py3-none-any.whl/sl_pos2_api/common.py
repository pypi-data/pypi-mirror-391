# file: /Users/SL/PythonProject/sl_pos2_api_tool/sl_pos2_api/common.py

import time
import json
import hashlib
import base64

import requests
from cryptography.fernet import Fernet


class APPCommon:
    '''
    This class is used to define the common variables and methods for POS2 API.
    '''

    def __init__(self, handle, uid, otp, device_info=None, ticket=None, user_agent=None):
        self.handle = handle
        self.uid = uid
        self.otp = otp
        self.device_info = device_info
        self.ticket = ticket
        if user_agent is None:
            self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"

    def _send_request(
            self,
            endpoint,
            data=None,
            method='POST',
            lang='zh-hans-cn'
    ):
        """
        发送HTTP请求的通用方法

        Args:
            endpoint: API端点路径
            data: 请求数据
            method: HTTP方法，默认为'POST'
            lang: 语言设置，默认为'zh-hans-cn'

        Returns:
            dict: JSON响应数据或None（如果发生错误）
        """
        # 构建完整请求URL
        url = f"{self.handle}{endpoint}"

        # 请求头
        headers = {
            "content-type": "application/json",
            "uid": self.uid,
            "accept": "*/*",
            "ticket": json.dumps(self.ticket),
            "otp": self.otp,
            "accept-language": "zh-Hans-CN;q=1.0",
            "deviceinfo": json.dumps(self.device_info),
            "user-agent": self.user_agent,
            "lang": lang
        }

        print(f'{endpoint} headers:', headers)
        if data:
            print(f'{endpoint} data:', data)

        try:
            # 发送请求
            if method.upper() == 'POST':
                response = requests.post(
                    url=url,
                    headers=headers,
                    data=json.dumps(data) if data else None,
                    verify=True
                )
            elif method.upper() == 'GET':
                response = requests.get(
                    url=url,
                    headers=headers,
                    params=data,
                    verify=True
                )
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求发生错误: {e}")
            return None
