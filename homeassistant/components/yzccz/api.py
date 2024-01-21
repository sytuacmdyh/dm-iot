import asyncio  # noqa: D100
import ipaddress
import socket
import time

import aiohttp

cache = {"timestamp": 0, "devices": []}


async def fetch(sem, session, ip):
    """检查IP是否是目标服务器."""
    async with sem:
        try:
            response = await session.get(f"http://{ip}:1912/api/device_list", timeout=1)
            if response.status == 200:
                data = await response.json()
                if data.get("code") == 0 and len(data.get("data")) > 0:
                    return [str(ip) + "|" + device for device in data.get("data")]
        except Exception:  # pylint: disable=broad-exception-caught
            pass
    return []


async def discover_devices():
    """检查局域网中所有满足条件的HTTP服务器列表.

    条件:端口号为1912,请求方法为GET,路径为/api/device_list,返回值为{"code":0,"data":["light"]}.
    """
    # 如果缓存的结果在5分钟内，直接返回缓存的结果
    if time.time() - MyUtil.cache["timestamp"] < 300:
        return MyUtil.cache["devices"]

    # 获取主机IP地址
    host_ip = socket.gethostbyname(socket.gethostname())
    # 获取子网
    subnet = ipaddress.ip_network(f"{host_ip}/24", strict=False)

    sem = asyncio.Semaphore(10)  # Limit to 10 concurrent requests

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(sem, session, ip) for ip in subnet.hosts()]
        results = await asyncio.gather(*tasks)

    devices = [device for sublist in results for device in sublist]

    # 更新缓存
    MyUtil.cache["timestamp"] = time.time()
    MyUtil.cache["devices"] = devices

    return devices


async def get_device_list(device_type: str):
    """获取指定类型的设备."""
    devices = await discover_devices()
    if device_type == "light":
        return [device for device in devices if device.split("|")[1] == "light"]
    if device_type == "fan":
        return [device for device in devices if device.split("|")[1] == "fan01"]
    return devices


class MyUtil:
    """Communicate Util."""

    def __init__(self) -> None:
        """init."""

    # async def get_device_data(self, device_id: str):
    #     async with aiohttp.ClientSession() as session:
    #         async with session.post(
    #             self.host
    #             + "/APIServerV2/v3/device/deviceinfo/product/5e7af43818828a4ea7d67e3a/device/"
    #             + device_id,
    #             headers=self.headers,
    #         ) as response:
    #             response_text = await response.text()
    #             response = json.loads(response_text)
    #             if response["code"] != 0:
    #                 return None
    #             info = response["data"]["fan"]
    #             status = response["data"]["fan_status"]
    #             status["is_online"] = info["is_online"]
    #             return status

    # async def set_device_data(self, device_id: str, data: dict):
    #     body = {
    #         "action": 4,
    #         "resource_id": 9031,
    #         "version": "zeico_3.0.0",
    #         "data": {"source": "manual"},
    #     }
    #     body["data"].update(data)
    #     body = json.dumps(body)
    #     headers = self.headers.copy()
    #     headers["Content-Type"] = "application/json"
    #     async with aiohttp.ClientSession() as session:
    #         async with session.post(
    #             self.host
    #             + "/APIServerV2/v3/control/product/5e7af43818828a4ea7d67e3a/device/"
    #             + device_id,
    #             data=body,
    #             headers=headers,
    #         ) as response:
    #             await asyncio.sleep(1)
    #             return None
