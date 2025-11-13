import threading
import time
from typing import Callable

from kaq_quant_common.api.rest.instruction.models.order import (
    OrderInfo,
    OrderSide,
    OrderStatus,
    PositionStatus,
)
from kaq_quant_common.utils import logger_utils, uuid_utils


class OrderHelper:
    def __init__(self, ins_server):
        # 必须放在这里 延迟引入，否则会有循环引用问题
        from kaq_quant_common.api.rest.instruction.instruction_server_base import (
            InstructionServerBase,
        )

        self._server: InstructionServerBase = ins_server
        self._logger = logger_utils.get_logger(self)

        self._mysql_table_name_order = "kaq_futures_instruction_order"
        self._mysql_table_name_position = "kaq_futures_instruction_position"

    def process_order(self, order: OrderInfo, get_order_result: Callable):
        # 获取交易所
        exchange = self._server._exchange
        #
        if not self._do_process_order(exchange, order, get_order_result, True):
            # 马上执行，没有成功，开启线程执行
            thread = threading.Thread(
                target=self._do_process_order,
                args=(exchange, order, get_order_result, False),
            )
            thread.name = f"process_order_{order.instruction_id}_{exchange}_{order.symbol}_{order.order_id}"
            thread.daemon = True
            thread.start()

    def _do_process_order(
        self,
        exchange: str,
        order: OrderInfo,
        get_order_result: Callable,
        first=True,
    ):
        # 获取mysql
        mysql = self._server._mysql

        #
        ins_id = order.instruction_id
        order_id = order.order_id
        symbol = order.symbol
        side = order.side
        position_side = order.position_side

        side_str = "开仓"
        if side == OrderSide.SELL:
            side_str = "平仓"

        if first:
            self._logger.info(f"{ins_id}_{exchange}_{symbol} step 1. {side_str}挂单成功 {order_id}")

            # 步骤1.挂单成功 插入到订单记录
            # 获取当前时间-ms
            current_time = int(time.time() * 1000)

            if mysql is not None:
                status = OrderStatus.CREATE
                sql = f"""
                INSERT INTO {self._mysql_table_name_order} (ins_id, exchange, symbol, side, position_side, orig_price, orig_coin_quantity, order_id, status, create_time, last_update_time) 
                VALUES ( '{ins_id}', '{exchange}', '{symbol}', '{side.value}', '{order.position_side.value}', {order.target_price}, {order.quantity}, '{order_id}', '{status.value}', {current_time}, {current_time} );
                """
                execute_ret = mysql.execute_sql(sql, True)

        # 步骤2.查询订单状态 直到订单成交后
        while True:
            # 获取订单结果
            order_info = get_order_result()
            if order_info is not None:
                break
            # 只查询一次
            if first:
                return False
            # 等待
            time.sleep(1)

        # 步骤3.把最终持仓写进去
        # 平均成交价格 转float
        avg_price = float(order_info["avg_price"])
        # 最终成交数量 转float
        executed_qty = float(order_info["executed_qty"])
        # 计算出usdt数量
        executed_usdt = avg_price * executed_qty

        current_time = int(time.time() * 1000)

        if mysql is None:
            self._logger.warning(f"{ins_id}_{exchange}_{symbol} 仅操作，没有入库，请设置 mysql!!")
            return

        status = OrderStatus.FINISH
        # 更新写入最终信息
        sql = f"""
        UPDATE {self._mysql_table_name_order} 
        SET price = {avg_price}, coin_quantity = {executed_qty}, usdt_quantity = {executed_usdt}, status = '{status.value}', last_update_time = {current_time} 
        WHERE ins_id = '{ins_id}' AND exchange = '{exchange}' AND symbol = '{symbol}';
        """
        execute_ret = mysql.execute_sql(sql, True)

        self._logger.info(
            f"{ins_id}_{exchange}_{symbol} step 2. 订单成交 {order_id}, {side_str}价格 {avg_price}, {{side_str}}数量 {executed_qty}, {{side_str}}usdt {executed_usdt}"
        )
        if side == OrderSide.BUY:
            # 同时插入持仓表
            position_id = uuid_utils.generate_uuid()
            sql = f"""
            INSERT INTO {self._mysql_table_name_position} (id, exchange, symbol, position_side, coin_quantity, usdt_quantity, open_ins_id, open_price, open_time, status) 
            VALUES ( '{position_id}', '{exchange}', '{symbol}', '{position_side.value}', '{executed_qty}', '{executed_usdt}', '{ins_id}', '{avg_price}', {current_time}, '{PositionStatus.OPEN.value}' );
            """
            execute_ret = mysql.execute_sql(sql, True)

            self._logger.info(f"{ins_id}_{exchange}_{symbol} step 3. 创建持仓记录 {position_id}")
        else:
            # 需要找到对应的持仓记录
            sql = f"""
            SELECT * FROM {self._mysql_table_name_position}
            WHERE exchange = '{exchange}' AND symbol = '{symbol}' AND position_side = '{position_side.value}' AND status = '{PositionStatus.OPEN.value}' 
            ORDER BY open_time ASC;
            """
            execute_ret = mysql.execute_sql(sql)
            try:
                position_id = execute_ret.fetchone().id
                if position_id is not None:
                    # 更新持仓信息
                    sql = f"""
                    UPDATE {self._mysql_table_name_position} 
                    SET close_ins_id = '{ins_id}', close_price = {avg_price}, close_time = {current_time}, status = '{PositionStatus.CLOSE.value}'
                    WHERE id = '{position_id}';
                    """
                    execute_ret = mysql.execute_sql(sql, True)

                    self._logger.info(f"{ins_id}_{exchange}_{symbol} step 3. 更新持仓记录 {position_id}")
            except:
                pass

        return True
