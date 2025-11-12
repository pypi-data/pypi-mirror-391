"""历史数据HTTP客户端模块。"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from HongTaQuant.HongTaData.config import settings


class HistoricalClient:
    """HTTP客户端用于获取历史金融数据.
    
    Example:
        async with HistoricalClient(base_url="https://api.example.com") as client:
            data = await client.get_stock_data(period="min1", type="stock", start="2024-01-01", end="2024-01-31", symbols=["000001.SZ"], params="")
    """
    
    def __init__(
        self,
        base_url: str | None = None,
        timeout: int | None = None,
    ) -> None:
        """初始化HTTP客户端.
        
        Args:
            base_url: API基础URL，默认使用配置中的值
            timeout: 请求超时时间（秒），默认使用配置中的值
        """
        self.base_url = base_url or settings.http_base_url
        self.token = None
        self.timeout = timeout or settings.http_timeout
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Authorization": "Basic dnVlOnZ1ZQ=="} if self.token else {},
        )
    
    async def __aenter__(self) -> HistoricalClient:
        return self
    
    # async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
    #     await self._client.close()
    
    @retry(wait=wait_exponential(min=0.1, max=2), stop=stop_after_attempt(3))
    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """发起HTTP请求（带重试）.
        
        Returns:
            dict: 认证相关接口返回字典
            list[dict]: 数据查询接口返回列表
        """
        response = self._client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()
    
    # 登录获取token
    def connect(self, username: str | None = None, password: str | None = None) -> None:
        """使用用户名和密码登录以获取API令牌.
        
        Args:
            username: API用户名，默认使用配置中的值
            password: API密码，默认使用配置中的值
            
        Returns:
            获取到的API令牌
        """
        username = username or settings.http_username
        password = password or settings.http_password
        
        data = {
            "username": username,
            "password": password,
            "grant_type": "password",
        }
        result = self._request("POST", "/api/auth/oauth/token", headers={"Content-Type": "application/x-www-form-urlencoded", "Authorization": "Basic dnVlOnZ1ZQ=="}, data=data)
        if not isinstance(result, dict):
            raise ValueError("登录响应格式错误")
        token = result.get("access_token")
        if not token:
            raise ValueError("登录失败，未获取到令牌")
        self.token = token
        # 更新客户端头部
        self._client.headers.update({"Authorization": "Bearer " + token})

    # 登出并移除token
    def close(self) -> None:
        """登出并使当前令牌失效."""
        data = {
            "access_token": self.token
        }
        self._request("DELETE", "/api/auth/oauth/token", headers={"Authorization": "Basic dnVlOnZ1ZQ=="}, data=data)
        self.token = None

    # 获取股票历史数据
    def get_stock_data(
        self,
        period: str,
        data_type: str,
        start: str,
        end: str,
        symbols: list[str],
        params: str,
    ) -> list[dict[str, Any]]:
        """获取股票历史数据.
        
        Args:
            period: 数据周期 (e.g., min1, min5, day1)
            type: 数据类型 (e.g., stock, index, etf, hk, bond, option, bsm)
            start: 开始日期 (yyyyMMdd hh:mm:ss)
            end: 结束日期 (yyyyMMdd hh:mm:ss)
            symbols: 股票代码
            params: 其他参数
            
        Returns:
            股票数据列表
        """
        # symbols检查
        if type(symbols) is not list:
            raise ValueError("symbols参数必须是列表")
        if not all(isinstance(s, str) for s in symbols):
            raise ValueError("symbols参数必须是字符串列表")
        if not symbols or len(symbols) == 0:
            raise ValueError("symbols参数不能为空列表")
        if len(symbols) > 10:
            raise ValueError("symbols参数数量不能超过10")
        
        # data_type类型检查
        valid_types = {"stock", "index", "etf", "hk", "bond", "option", "bsm"}
        if data_type not in valid_types:
            raise ValueError(f"type参数无效，期望值之一: {valid_types}")
        
        # period检查
        valid_periods = {"min1", "min5", "day1"}
        if period not in valid_periods:
            raise ValueError(f"period参数无效，期望值之一: {valid_periods}")

        # start/end检查, end - start <= 1年
        start_dt = datetime.strptime(start, "%Y%m%d %H:%M:%S")
        end_dt = datetime.strptime(end, "%Y%m%d %H:%M:%S")
        if end_dt <= start_dt:
            raise ValueError("end日期必须晚于start日期")
        if end_dt - start_dt > timedelta(days=366):
            raise ValueError("查询时间范围不能超过1年")

        # 组装查询参数
        symbols_str = ",".join(symbols)
        query_params = {
            "period": period,
            "type": data_type,
            "start": start,
            "end": end,
            "symbols": symbols_str,
            "params": params,
        }
        result = self._request("GET", "/api/data/data/fetch", params=query_params)
        if not isinstance(result, list):
            raise ValueError("数据响应格式错误，期望列表")
        return result
