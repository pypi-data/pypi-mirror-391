"""Test data models."""
    
import pytest
from pydantic import ValidationError

from HongTaQuant.HongTaData.models import HSStockData


def test_stock_data_creation() -> None:
    """测试创建股票数据模型."""
    data = HSStockData(
        code="000001.SZ",
        tradetime="2024-01-01 09:30:00",
        open=10.50,
        high=11.00,
        low=10.20,
        close=10.80,
        volume=1000000.0,
        amount=10800000.0,
        sellVolume=500000.0,
        buyVolume=500000.0,
        openInterest=0.0,
        tau=0.0,
        sigma=0.0,
        d2=0.0,
        delta=0.0,
        gamma=0.0,
        vega=0.0,
        theta=0.0,
        rho=0.0,
        bsm_value=0.0,
        iv=0.0,
        rf=0.0,
    )
    
    assert data.code == "000001.SZ"
    assert data.open == 10.50
    assert data.volume == 1000000.0


def test_stock_data_validation() -> None:
    """测试股票数据验证."""
    with pytest.raises(ValidationError):
        HSStockData(code="000001.SZ")  # 缺少必需字段


# def test_quote_creation() -> None:
#     """测试创建行情模型."""
#     quote = Quote(
#         symbol="000001.SZ",
#         timestamp=datetime(2024, 1, 1, 9, 30),
#         bid_price=Decimal("10.50"),
#         ask_price=Decimal("10.51"),
#         last_price=Decimal("10.50"),
#     )
    
#     assert quote.symbol == "000001.SZ"
#     assert quote.bid_price == Decimal("10.50")
