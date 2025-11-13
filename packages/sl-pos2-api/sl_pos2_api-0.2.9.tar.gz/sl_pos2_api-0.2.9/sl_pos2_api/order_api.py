import requests
import json

from sl_pos2_api.app_auth import APPAuth


class OrderAPI(APPAuth):

    def checkout(
            self,
            data,
            lang='zh-hans-cn'
    ):
        """
        发起订单结算请求

        Args:
            data: 订单数据
            lang: 语言设置，默认为'zh-hans-cn'
        """
        return self._send_request(
            endpoint="/sl/apps/pos/app/order/checkout",
            data=data,
            lang=lang
        )

    def create_order(
            self,
            data,
            lang='zh-hans-cn'
    ):
        """
        创建订单

        Args:
            data: 订单数据
            lang: 语言设置，默认为'zh-hans-cn'
        """
        return self._send_request(
            endpoint="/sl/apps/pos/app/order/createOrder",
            data=data,
            lang=lang
        )

    def calculate(
            self,
            data,
            lang='zh-hans-cn'
    ):
        """
        计算退款金额

        Args:
            data: 退款计算所需数据
            lang: 语言设置，默认为'zh-hans-cn'
        """
        return self._send_request(
            endpoint="/sl/apps/pos/app/after-sale/calculate",
            data=data,
            lang=lang
        )

    def process_refund(
            self,
            data,
            lang='zh-hans-cn'
    ):
        """
        处理退款

        Args:
            data: 退款处理所需数据
            lang: 语言设置，默认为'zh-hans-cn'
        """
        return self._send_request(
            endpoint="/sl/apps/pos/app/after-sale/refund",
            data=data,
            lang=lang
        )

    def exchange(
            self,
            data,
            lang='zh-hans-cn'
    ):
        """
        发起换货请求

        Args:
            data: 换货数据
            lang: 语言设置，默认为'zh-hans-cn'
        """
        return self._send_request(
            endpoint="/sl/apps/pos/app/after-sale/exchange",
            data=data,
            lang=lang
        )

    def modify_order_shipped(
            self,
            data,
            lang='zh-hans-cn'
    ):
        """
        修改订单发货信息

        Args:
            data: 修改订单发货所需数据，例如：
                  {
                      "sendNotify": false,
                      "storeId": 1709983459019,
                      "deliverLocationId": "6369562508760987402",
                      "productInfos": [{"id": 7614, "quantity": 1}],
                      "expressCode": "",
                      "orderId": "21072591371297290149132095"
                  }
            lang: 语言设置，默认为'zh-hans-cn'
        """
        return self._send_request(
            endpoint="/sl/apps/pos/app/order/modify-order-shipped",
            data=data,
            lang=lang
        )

    def order_detail(
            self,
            data,
            lang='zh-hans-cn'
    ):
        """
        获取订单详情

        Args:
            data: 订单详情请求数据，包含orderId等信息
            lang: 语言设置，默认为'zh-hans-cn'
        """
        return self._send_request(
            endpoint="/sl/apps/pos/app/order/detail",
            data=data,
            lang=lang
        )

    def repay(
            self,
            data,
            lang='zh-hans-cn'
    ):
        """
        发起换货请求

        Args:
            data: 换货数据
            lang: 语言设置，默认为'zh-hans-cn'
        """
        return self._send_request(
            endpoint="/sl/apps/pos/app/pay/repay",
            data=data,
            lang=lang
        )


if __name__ == '__main__':
    zpf_url = 'https://uizidonghuaceshi.myshoplinestg.com'
    zpf_uid = '4600508114'
    otp = '0501000001560297eac3686000139605a5cfdde0a32600fff8b7594b202054ee07df66f92139c8c53ae104e68eb515c5ee2fbd36e9a9d24747a6c30bb110bbec94e202291714228352bb5285f4c7a3da34c643b1edab8ddc4db44ce6af56071f4ba537e5494991ba80607f9c299a0000c08b3e109a000290004d3a559b9ed5a9e624c1323e0fb7c58175898f0a09de4b9700f824478461c9324f887207df0b0b8f29c2e672942efbe8520e108ba98bbd4fd684f92e56ebc0fb5ff9fc04cbdc57521d113369bb1d2f2f1310e862f4f675f25c7cbf690e3456b87d82cbbcdf8bac21e45192a4b2a9be6916e57f6a463d3183fef9c491fb605077c89e2c6a3f6cc7ed7613a6aec85782a7'
    ticket = {"storeId": 1709983459019,
              "merchantId": "4600508114",
              "offlineStoreId": 6369562508760987402,
              "posStaffId": 3787}

    device_info = {"os": "ios", "appVersion": "2.15.0", "newDeviceId": "b099a7742a01db20d33a21934ae129d5bbbec77f",
                   "deviceId": "7C92D974-C934-4D63-BC24-DC208916A14D", "brand": "Apple", "osVersion": "17.3.1",
                   "model": "iPhone 13"}

    orderapi = OrderAPI(zpf_url, zpf_uid, otp, ticket=ticket, device_info=device_info)
    data = {
        "openDutyFree": False,
        "productInfos": [
            {
                "price": "100.00",
                "quantity": 1,
                "serviceCharge": False,
                "skuId": "18063695978625661748802405",
                "source": 1,
                "spuId": "16063695978613582153162405",
                "title": "单库存商品001"
            }
        ],
        "roundingType": 0
    }

    data2 = {
        "offlineStoreId": "6369562508760987402",
        "storeId": "1709983459019",
        "uid": "4600508114"
    }
    inner_token = orderapi.get_staff_detail(data2)

    print(orderapi.checkout(data))
