from collections.abc import Generator

import pytest

from HongTaQuant.HongTaData import HistoricalClient


# 模拟响应对象
class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP error: {self.status_code}")

    def json(self):
        return self._json

@pytest.fixture
def client() -> Generator[HistoricalClient, None, None]:
    yield HistoricalClient(base_url="http://test")

# 测试 HistoricalClient 的OAuth 2.0 连接和数据获取功能
def test_connect_sets_bearer_header(monkeypatch, client: HistoricalClient):
    def fake_request(method, path, **kwargs):
        assert method == "POST"
        assert path == "/api/auth/oauth/token"
        # Ensure Basic header is sent for token request
        headers = kwargs.get("headers", {})
        assert headers.get("Authorization", "").startswith("Basic ")
        return {"access_token": "t123"}

    # 用fake_request替换实际的_request方法
    monkeypatch.setattr(HistoricalClient, "_request", staticmethod(lambda method, path, **kwargs: fake_request(method, path, **kwargs)))

    client.connect("user", "pass")

    assert client.token == "t123"
    assert client._client.headers.get("Authorization") == "Bearer t123"

# 测试连接失败时抛出异常
def test_connect_raises_when_no_token(monkeypatch, client: HistoricalClient):

    # 模拟返回无token的响应
    monkeypatch.setattr(HistoricalClient, "_request", staticmethod(lambda *args, **kwargs: {}))

    with pytest.raises(ValueError):
        client.connect("user", "pass")

# 测试 get_stock_data 方法构建正确的查询参数
def test_get_stock_data_builds_query(monkeypatch, client: HistoricalClient):
    captured = {}

    def capture_request(method, path, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["params"] = kwargs.get("params")
        return [{"ok": True}]

    # 用于捕获请求的模拟方法
    monkeypatch.setattr(HistoricalClient, "_request", staticmethod(lambda method, path, **kwargs: capture_request(method, path, **kwargs)))
    
    result = client.get_stock_data(
        period="min5",
        data_type="stock",
        start="20230101 09:30:00",
        end="20231231 15:00:00",
        symbols=["601236", "000123"],
        params="",
    )

    assert result == [{"ok": True}]
    assert captured["method"] == "GET"
    assert captured["path"] == "/api/data/data/fetch"
    assert captured["params"] == {
        "period": "min5",
        "type": "stock",
        "start": "20230101 09:30:00",
        "end": "20231231 15:00:00",
        "symbols": "601236,000123",  # symbols are joined into a comma-separated string
        "params": "",
    }

# 测试 get_stock_data 在 symbols 不是正确值时抛出异常
def test_get_stock_data_raises_on_invalid_symbols_type(client: HistoricalClient):
    # symbols 传入错误类型（非列表）
    with pytest.raises(ValueError) as excinfo:
        client.get_stock_data(
            period="min5",
            data_type="stock",
            start="20230101 09:30:00",
            end="20231231 15:00:00",
            symbols="601236",  # type: ignore[arg-type] 故意传入错误类型来测试异常处理
            params="",
        )
    assert "symbols参数必须是列表" in str(excinfo.value)

    # symbols 传入空列表
    with pytest.raises(ValueError) as excinfo:
        client.get_stock_data(
            period="min5",
            data_type="stock",
            start="20230101 09:30:00",
            end="20231231 15:00:00",
            symbols=[],
            params="",
        )
    assert "symbols参数不能为空列表" in str(excinfo.value)

    # symbols 传入非字符串元素
    with pytest.raises(ValueError) as excinfo:
        client.get_stock_data(
            period="min5",
            data_type="stock",
            start="20230101 09:30:00",
            end="20231231 15:00:00",
            symbols=["601236", 123],  # type: ignore[arg-type] 故意传入非字符串元素
            params="",
        )
    assert "symbols参数必须是字符串列表" in str(excinfo.value)

    # symbols 传入超过10个元素
    with pytest.raises(ValueError) as excinfo:
        client.get_stock_data(
            period="min5",
            data_type="stock",
            start="20230101 09:30:00",
            end="20231231 15:00:00",
            symbols=[str(i) for i in range(11)],
            params="",
        )
    assert "symbols参数数量不能超过10" in str(excinfo.value)

# 测试 get_stock_data 在 data_type 无效时抛出异常
def test_get_stock_data_raises_on_invalid_type(client: HistoricalClient):
    with pytest.raises(ValueError) as excinfo:
        client.get_stock_data(
            period="min5",
            data_type="invalid_type",
            start="20230101 09:30:00",
            end="20231231 15:00:00",
            symbols=["601236"],
            params="",
        )
    assert "type参数无效" in str(excinfo.value)

# 测试get_stock_data在 period 无效时抛出异常
def test_get_stock_data_raises_on_invalid_period(client: HistoricalClient):
    with pytest.raises(ValueError) as excinfo:
        client.get_stock_data(
            period="invalid_period",
            data_type="stock",
            start="20230101 09:30:00",
            end="20231231 15:00:00",
            symbols=["601236"],
            params="",
        )
    assert "period参数无效" in str(excinfo.value)
  
# 测试 start/end 日期检查逻辑
def test_get_stock_data_raises_on_invalid_date_range(client: HistoricalClient):
    # end 日期早于 start 日期
    with pytest.raises(ValueError) as excinfo:
        client.get_stock_data(
            period="min5",
            data_type="stock",
            start="20231231 15:00:00",
            end="20230101 09:30:00",
            symbols=["601236"],
            params="",
        )
    assert "end日期必须晚于start日期" in str(excinfo.value)

    # 日期范围超过1年
    with pytest.raises(ValueError) as excinfo:
        client.get_stock_data(
            period="min5",
            data_type="stock",
            start="20220101 09:30:00",
            end="20231231 15:00:00",
            symbols=["601236"],
            params="",
        )
    assert "查询时间范围不能超过1年" in str(excinfo.value)

# 测试 close 方法正确调用登出接口并重置 token
def test_close_resets_token_and_calls_delete(monkeypatch, client: HistoricalClient):
    client.token = "abc"
    client._client.headers.update({"Authorization": "Bearer abc"})

    captured = {}

    def capture_delete(method, path, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["headers"] = kwargs.get("headers")
        captured["data"] = kwargs.get("data")
        return {}

    monkeypatch.setattr(HistoricalClient, "_request", staticmethod(lambda method, path, **kwargs: capture_delete(method, path, **kwargs)))

    client.close()

    assert client.token is None
    assert captured["method"] == "DELETE"
    assert captured["path"] == "/api/auth/oauth/token"
    assert captured["headers"]["Authorization"].startswith("Basic ")
    assert captured["data"] == {"access_token": "abc"}
