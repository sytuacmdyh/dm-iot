"""API."""
import logging
import time

import aiohttp

_LOGGER = logging.getLogger(__name__)


class MyUtil:
    """Communicate Util."""

    def __init__(self, host: str) -> None:
        """init."""
        self.cache = {"timestamp": 0, "devices": []}
        self.http_prefix = f"http://{host}/api/rmt"

    def deal_with_response(self, response):
        """处理响应."""
        if response.get("code", 1) != 0:
            raise Exception(response.get("msg", "未知错误"))  # pylint: disable=broad-exception-raised

        return response.get("data", None)

    async def http_get(self, url, params):
        """Get."""
        async with aiohttp.ClientSession() as session, session.get(
            self.http_prefix + url, params=params
        ) as response:
            return self.deal_with_response(await response.json())

    async def http_post(self, url, data, params):
        """Post."""
        async with aiohttp.ClientSession() as session, session.post(
            self.http_prefix + url, json=data, params=params
        ) as response:
            return self.deal_with_response(await response.json())

    async def discover_devices(self):
        """检查局域网中设备列表."""
        # 如果缓存的结果在5分钟内，直接返回缓存的结果
        if time.time() - self.cache["timestamp"] < 300:
            return self.cache["devices"]

        try:
            # 请求 http://rt-ctrl.local/api/rmt/getDeviceList，响应{"code":0,"msg":"success","data":[{"name":"l1","product":"light"}]}
            devices = await self.http_get("/getDeviceList", {})

            # 更新设备列表
            self.cache["timestamp"] = time.time()
            self.cache["devices"] = devices
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error(
                "Http Error: %s",
                err,
            )
        return self.cache["devices"]

    async def get_device_list(self, device_type: str):
        """获取指定类型的设备."""
        devices = await self.discover_devices()
        return [device for device in devices if device["product"] == device_type]

    async def do_action(self, device_name, action_name: str):
        """执行动作."""
        return await self.http_post(
            "/doAction", {"device": device_name, "action": action_name}, {}
        )
