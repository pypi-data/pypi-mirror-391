# 定义 服务器api
import time
from abc import ABC, abstractmethod

from kaq_quant_common.api.common.api_interface import ApiInterface, api_method
from kaq_quant_common.api.rest.api_server_base import ApiServerBase
from kaq_quant_common.api.rest.instruction.models import InstructionResponseBase
from kaq_quant_common.api.rest.instruction.models.account import (
    ContractBalanceRequest,
    ContractBalanceResponse,
)
from kaq_quant_common.api.rest.instruction.models.order import (
    AllOpenOrdersRequest,
    AllOpenOrdersResponse,
    CancelOrderRequest,
    CancelOrderResponse,
    ChangeLeverageRequest,
    ChangeLeverageResponse,
    ModifyOrderRequest,
    ModifyOrderResponse,
    OrderRequest,
    OrderResponse,
)
from kaq_quant_common.api.rest.instruction.models.transfer import (
    TransferRequest,
    TransferResponse,
)


class InstructionServerBase(ApiServerBase, ApiInterface, ABC):

    def __init__(self, host="0.0.0.0", port=5000):
        super().__init__(self, host, port)

    # 统一处理返回数据
    def _wrap_response(self, rsp: InstructionResponseBase):
        if rsp is not None:
            # 时间
            if rsp.event_time is None:
                rsp.event_time = int(time.time() * 1000)
        return rsp

    # 下单
    @api_method(OrderRequest, OrderResponse)
    def order(self, request: OrderRequest) -> OrderResponse:
        return self._on_order(request)

    # 修改订单
    @api_method(ModifyOrderRequest, ModifyOrderResponse)
    def modify_order(self, request: ModifyOrderRequest) -> ModifyOrderResponse:
        return self._on_modify_order(request)

    # 取消订单
    @api_method(CancelOrderRequest, CancelOrderResponse)
    def cancel_order(self, request: CancelOrderRequest) -> CancelOrderResponse:
        return self._on_cancel_order(request)

    # 查询当前全部挂单
    @api_method(AllOpenOrdersRequest, AllOpenOrdersResponse)
    def all_open_orders(self, request: AllOpenOrdersRequest) -> AllOpenOrdersResponse:
        return self._on_all_open_orders(request)

    # 调整杠杆
    @api_method(ChangeLeverageRequest, ChangeLeverageResponse)
    def change_leverage(self, request: ChangeLeverageRequest) -> ChangeLeverageResponse:
        return self._on_change_leverage(request)

    # 划转
    @api_method(TransferRequest, TransferResponse)
    def transfer(self, request: TransferRequest) -> TransferResponse:
        return self._on_transfer(request)

    # 查询合约账户余额
    @api_method(ContractBalanceRequest, ContractBalanceResponse)
    def contract_balance(self, request: ContractBalanceRequest) -> ContractBalanceResponse:
        return self._on_contract_balance(request)

    # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ abstract methods

    @abstractmethod
    def _on_order(self, request: OrderRequest) -> OrderResponse:
        pass

    @abstractmethod
    def _on_modify_order(self, request: ModifyOrderRequest) -> ModifyOrderResponse:
        pass

    @abstractmethod
    def _on_cancel_order(self, request: CancelOrderRequest) -> CancelOrderResponse:
        pass

    @abstractmethod
    def _on_all_open_orders(self, request: AllOpenOrdersRequest) -> AllOpenOrdersResponse:
        pass

    @abstractmethod
    def _on_change_leverage(self, request: ChangeLeverageRequest) -> ChangeLeverageResponse:
        pass

    @abstractmethod
    def _on_transfer(self, request: TransferRequest) -> TransferResponse:
        pass

    @abstractmethod
    def _on_contract_balance(self, request: ContractBalanceRequest) -> ContractBalanceResponse:
        pass
