from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.ticktype import TickTypeEnum
import threading
import time
from datetime import datetime


class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextorderId = None
        self.midprice = None
        self.bid_price = None
        self.ask_price = None
        self.bid_size = None
        self.ask_size = None
        self.contract_data = {}
        self.custom_callback = None  # Add this line to store the custom callback
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print("The next valid order id is: ", self.nextorderId)

    def tickPrice(self, reqId, tickType, price, attrib):
        if reqId not in self.contract_data:
            self.contract_data[reqId] = {}
        if tickType == 1:  # Bid price
            self.contract_data[reqId]["bid_price"] = price
        elif tickType == 2:  # Ask price
            self.contract_data[reqId]["ask_price"] = price
        self.print_order_book(reqId)

    def tickSize(self, reqId, tickType, size):
        if reqId not in self.contract_data:
            self.contract_data[reqId] = {}
        if tickType == 0:  # Bid size
            self.contract_data[reqId]["bid_size"] = size
        elif tickType == 3:  # Ask size
            self.contract_data[reqId]["ask_size"] = size
        self.print_order_book(reqId)

    def print_order_book(self, reqId):
        data = self.contract_data.get(reqId, {})
        if all(
            key in data for key in ["bid_price", "ask_price", "bid_size", "ask_size"]
        ):
            formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            self.contract_data[reqId]["datetime"] = formatted_time
            if self.contract_data[reqId]["快速印製"]:
                print(
                    f"{formatted_time} | ReqID: {reqId} | 買: {data['bid_size']} @ {data['bid_price']} | 賣: {data['ask_size']} @ {data['ask_price']}"
                )
            # self.poyen_setcallback(data=self.contract_data)
            if self.custom_callback:
                self.custom_callback(self.contract_data)

    # Add this method to set the custom callback
    def poyen_setcallback(self, callback_func):
        self.custom_callback = callback_func
    # 用來取消下單
    # def modifyOrderAfterDelay(self, contract, delay):
    #     time.sleep(delay)
    #     if self.order:
    #         new_limit_price = self.order.lmtPrice + 1.0
    #         self.order.lmtPrice = new_limit_price
    #         self.placeOrder(self.nextOrderId, contract, self.order)
    #         print(f"Modified order limit price to {new_limit_price}")

    def orderStatus(
        self,
        orderId: int,
        status: str,
        filled: float,
        remaining: float,
        avgFillPrice: float,
        permId: int,
        parentId: int,
        lastFillPrice: float,
        clientId: int,
        whyHeld: str,
        mktCapPrice: float,
    ):
        print(
            f"Order Status - OrderID: {orderId} Status: {status} "
            f"Filled: {filled} Remaining: {remaining} AvgFillPrice: {avgFillPrice}"
        )

        if status == "Filled" or filled > 0:
            print("your order is filled")

    def poyen_connect(self, port, client_id):
        def run_loop():
            self.run()

        self.connect("127.0.0.1", port, client_id)
        # Start the socket in a thread
        api_thread = threading.Thread(target=run_loop, daemon=True)
        api_thread.start()
        # Wait for nextValidId
        while True:
            if isinstance(self.nextorderId, int):
                print("connected")
                break
            else:
                print("waiting for connection")
                time.sleep(1)

    def poyen_subscribe(self, ID: int, 商品檔,快速印製:bool=False):
        # Request Market Data
        self.reqMktData(ID, 商品檔, "", False, False, [])
        if ID not in self.contract_data:
            self.contract_data[ID] = {}
        self.contract_data[ID]["快速印製"]=快速印製

    def poyen_unsubscribe(self, ID: int):
        self.cancelMktData(ID)  # Use the same reqId (1) as used in reqMktData

    def poyen_future_contract(self, 商品代號: str, 交易所: str, 到期日: str):
        """
        舉例 "MYM" "CBOT" "202412"
        """
        contract = Contract()
        contract.symbol = 商品代號  # "MYM"
        contract.secType = "FUT"
        contract.exchange = 交易所  # "CBOT"
        contract.currency = "USD"
        contract.lastTradeDateOrContractMonth = (
            到期日  # "202412"  # 請替換為合適的合約月份
        )
        return contract

    def poyen_order(買賣別: str, 數量: int, 價格: float):
        """
        "BUY" "SELL" 0=市價單
        """
        order = Order()
        order.action = 買賣別  # "BUY" 或 "SELL"
        if 價格 == 0:
            order.orderType = "MKT"  # 使用限價單
        else:
            order.orderType = "LMT"  # 使用限價單
        order.totalQuantity = 數量
        order.lmtPrice = 價格
        order.eTradeOnly = ""
        order.firmQuoteOnly = ""
        return order


# Cancel all active subscriptions
# app.cancel_all_subscriptions()
# Cancel Market Data subscription
# app.cancelMktData(1)  # Use the same reqId (1) as used in reqMktData
