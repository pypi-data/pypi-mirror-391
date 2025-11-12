from enum import Enum
from typing import Optional

from pydantic import BaseModel

from . import InstructionRequestBase, InstructionResponseBase


# 订单类型
class OrderType(str, Enum):
    # 现货
    SPOT = "spot"
    # 合约
    FUTURES = "futures"


# 订单方向
class OrderDirection(str, Enum):
    BUY = "buy"
    SELL = "sell"


# 持仓方向
class OrderPositionSide(str, Enum):
    # 看多
    LONG = "long"
    # 看空
    SHORT = "short"


# 订单交易类型
class OrderTradeType(str, Enum):
    # 市价
    MARKET = "market"
    # 限价
    LIMIT = "limit"


# 订单操作类型 开仓/平仓
class OrderInstructionType(str, Enum):
    OPEN = "open"
    CLOSE = "close"


# 订单信息
class OrderInfo(BaseModel):
    # 交易对
    symbol: str
    # 订单类型 现货/合约
    order_type: OrderType
    # 订单操作类型 开仓/平仓
    instruction_type: OrderInstructionType
    # TODO 删除
    # 卖买方向
    direction: OrderDirection
    # 持仓方向
    position_side: OrderPositionSide
    # 保证金，？什么时候用
    margin: Optional[float] = 0.0
    # 补充保证金，？什么时候用
    supply_margin: Optional[float] = 0.0
    # 杠杆
    level: int
    # 数量(币种，不是USDT)
    quantity: float
    # 限价单才用
    target_price: float
    # 当前价格，？什么时候用
    current_price: Optional[float] = 0.0
    # 交易类型 市价单/限价单
    trade_type: OrderTradeType
    # 风险等级
    risk_level: int
    # 是否强制平仓
    forced_liqu: bool
    # 有效期
    validity_period: Optional[str] = None
    # 策略类型
    strategy_type: Optional[str] = None


# 修改订单信息
class ModifyOrderInfo(BaseModel):
    # 订单ID，自定义的订单id
    order_id: str
    # TODO 暂时不知道修改什么，先定个修改数量
    quantity: Optional[float] = None
    # TODO 暂时不知道修改什么，先定个修改价格
    price: Optional[float] = None


# 已下单信息
class OpenedOrderInfo(BaseModel):
    # 订单ID
    order_id: str
    # 交易对
    symbol: Optional[str]
    # 价格
    price: Optional[float]


# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ 批量下单
# 下单请求
class OrderRequest(InstructionRequestBase):
    orders: list[OrderInfo]


# 下单响应
class OrderResponse(InstructionResponseBase):
    # 返回成功下单的订单信息
    orders: list[OpenedOrderInfo]


# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ 批量修改订单


class ModifyOrderRequest(InstructionRequestBase):
    orders: list[ModifyOrderInfo]


class ModifyOrderResponse(InstructionResponseBase):
    # 返回成功下单的订单信息
    orders: list[OpenedOrderInfo]


# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ 撤销订单


class CancelOrderRequest(InstructionRequestBase):
    # 可选的，可能某些平台需要指定交易对
    symbol: Optional[str]
    # 订单id列表
    orders: list[str]


class CancelOrderResponse(InstructionResponseBase):
    orders: list[OpenedOrderInfo]


# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ 查询当前全部挂单请求
class AllOpenOrdersRequest(InstructionRequestBase):
    # 交易对，用作筛选，不传取全部
    symbol: Optional[str] = None


# 查询当前全部挂单响应
class AllOpenOrdersResponse(InstructionResponseBase):
    # TODO
    orders: list[OpenedOrderInfo]


# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ 调整杠杆
class ChangeLeverageRequest(InstructionRequestBase):
    # 交易对
    symbol: str
    # 杠杆
    level: int


class ChangeLeverageResponse(InstructionResponseBase):
    # 交易对
    symbol: str
    # 杠杆
    level: int


# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ 联合保证金模式
# 查询
class QueryMarginModeRequest(InstructionRequestBase):
    pass


class QueryMarginModeResponse(InstructionResponseBase):
    # 是否联合
    is_margin: bool


# 修改
class ChangeMarginModeRequest(InstructionRequestBase):
    # 是否联合
    is_margin: bool


class ChangeMarginModeResponse(InstructionResponseBase):
    # 是否联合
    is_margin: bool
