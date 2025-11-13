import requests
import json

from .common import APPCommon


class APPAuth(APPCommon):

    def get_staff_detail(self, data):
        """
        获取员工详情的请求方法
        """
        # 请求URL
        url = f"{self.handle}/sl/apps/pos/app/staff/get-staff-detail"
        # 构建请求头
        headers = {
            'uid': self.uid,
            'otp': self.otp,
            'deviceinfo': json.dumps(self.device_info),
            'Content-Type': 'application/json',
            'ticket': json.dumps(self.ticket)
        }
        # 发送POST请求
        print("get_staff_detail header:", headers)
        print("get_staff_detail url:", url)
        try:
            response = requests.post(url, headers=headers, json=data)
            # 返回响应结果

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
        if response and response.json().get('code') == 'E0':

            self.ticket.update({'innerToken': response.json().get('data').get('innerToken')})
            return response.json().get('data').get('innerToken')
        else:
            print('get_staff_detail error:', response.json())
            return None

    def lock_cashier_station(self, data, user_agent=None, lang='zh-hans-cn'):
        """
        收银点占用

        Args:
            handle (str): 基础URL
            uid (str): 用户ID
            otp (str): OTP认证信息
            device_info (dict): 设备信息
            user_agent (str): 用户代理
            lang (str): 语言设置
            request_data (dict): 请求数据

        Returns:
            dict: 响应结果
        """
        # 请求URL
        url = f"{self.handle}/sl/apps/pos/app/offline-store/select-one"

        # 构建请求头
        headers = {
            'accept': '*/*',
            'uid': self.uid,
            'otp': self.otp,
            'deviceinfo': self.device_info,
            'user-agent': self.user_agent,
            'lang': lang,
            'Content-Type': 'application/json'
        }

        # 发送POST请求
        print("select_one_offline_store header:", headers)
        print("select_one_offline_store url:", url)
        try:
            response = requests.post(url, headers=headers, json=json.dumps(data))
            print("select_one_offline_store response:", response.json())
            # 返回响应结果
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
