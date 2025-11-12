from decimal import Decimal

from pydantic import BaseModel, Field


class HSStockData(BaseModel):
  """沪深现货行情数据模型"""

  code:str = Field(default=..., description="标的代码")
  tradetime: str = Field(default=..., description="成交时间")
  open: float = Field(default=..., description="开盘价")
  close: float = Field(default=..., description="收盘价")
  high: float = Field(default=..., description="最高价")
  low: float = Field(default=..., description="最低价")
  volume: float = Field(default=..., description="成交量")
  amount: float = Field(default=..., description="成交额")
  sellVolume: float = Field(default=..., description="内盘")
  buyVolume: float = Field(default=..., description="外盘")
  openInterest: float = Field(default=..., description="持仓量")
  tau: float = Field(default=..., description="tau")
  sigma: float = Field(default=..., description="历史波动率")
  d2: float = Field(default=..., description="d2")
  delta: float = Field(default=..., description="delta")
  gamma: float = Field(default=..., description="gamma")
  vega: float = Field(default=..., description="vega")
  theta: float = Field(default=..., description="theta")
  rho: float = Field(default=..., description="rho")
  bsm_value: float = Field(default=..., description="期权BSM价格")
  iv: float = Field(default=..., description="隐含波动率")
  rf: float = Field(default=..., description="无风险利率")

  model_config = {"json_encoders": {Decimal: str}}

class Quote(BaseModel):
  pass

