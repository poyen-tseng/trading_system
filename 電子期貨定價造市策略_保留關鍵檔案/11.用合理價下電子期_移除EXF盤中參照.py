from datetime import datetime
import time
import shioaji as sj
from shioaji import TickFOPv1, BidAskFOPv1, Exchange
import numpy as np
from discordwebhook import Discord
import threading

# Discord webhook 初始化
discord = Discord(url="GITHUB重要資訊隱藏")

# 訂單狀態與參數初始化
SJ_buy, SJ_sell = None, None
盤口sell, 盤口buy = None, None
成本價_up, 成本價_down = 1.1, 1.05
sell單, buy單 = None, None
大量區定義 = 1
目前持有ZEF = 0
不再掛sell單, 不再掛buy單 = False, False


class ZEF價格計算機:
    def __init__(
        self, api, txf_contract, exf_contract, zef_contract, params上邊界, params下邊界
    ):
        self.api = api
        self.txf_contract = txf_contract
        self.exf_contract = exf_contract
        self.zef_contract = zef_contract
        self.params上邊界 = params上邊界
        self.params下邊界 = params下邊界

        self.txf即時價 = None
        self.bidask_data = None
        self.txf開盤價 = None
        self.exf開盤價 = None

        # 初始化合約快照
        self.snapshots開盤價()

    def snapshots開盤價(self):
        contracts = [self.exf_contract, self.txf_contract]
        snapshots = self.api.snapshots(contracts)
        self.exf開盤價 = snapshots[0].open
        self.txf開盤價 = snapshots[1].open

    def TXF_tick_callback(self, tick: TickFOPv1):
        if "TXF" in tick.code:
            self.txf即時價 = tick
            self.zef估價區(float(tick.close))

    def zef估價區(self, txf_price):
        txf_pct = (txf_price - self.txf開盤價) / self.txf開盤價
        price計算的上價格 = (
            self.params上邊界[0] * txf_pct + self.params上邊界[1] + 1
        ) * self.exf開盤價
        price計算的下價格 = (
            self.params下邊界[0] * txf_pct + self.params下邊界[1] + 1
        ) * self.exf開盤價

        print(f"{price計算的下價格:.5f}\t{price計算的上價格:.5f}")

    def 啟動報價執行緒(self):
        threading.Thread(target=self.thread_報價執行緒, daemon=True).start()

    def thread_報價執行緒(self):
        while True:
            time.sleep(0.2)
            # if self.bidask_data:
            #     self.EXF_bidask_callback(self.bidask_data)
            if self.txf即時價:
                self.TXF_tick_callback(self.txf即時價)


# * -------------------Callback函式區-----------------------


def SJ_order_callback(stat, msg):
    """
    處理訂單狀態更新，包括倉位管理與訂單取消。
    """
    global 目前持有ZEF, buy單, sell單, 不再掛buy單, 不再掛sell單
    try:
        委託價格 = msg["status"].get("modified_price") or msg["order"]["price"]
        print(
            f'{datetime.now()},\t{msg["order"]["action"]}\t{msg["contract"]["code"]}\t{委託價格}\t{msg["order"]["quantity"] - msg["status"]["cancel_quantity"]}\t{msg["operation"]["op_type"]}\t{msg["operation"]["op_msg"]}'
        )
        if "此" in msg["operation"]["op_msg"]:
            更新目前持有倉位()
            if msg["order"]["action"] == "Sell":
                sell單, 不再掛sell單 = None, not 不再掛buy單
            elif msg["order"]["action"] == "Buy":
                buy單, 不再掛buy單 = None, not 不再掛sell單
    except Exception as e:
        print(f"訂單更新錯誤：{e}")
        更新目前持有倉位()


# * -------------------輔助函式區-----------------------
def 更新目前持有倉位():
    """
    更新持有倉位狀態，檢查多空倉持有狀態。
    """
    global 目前持有ZEF, buy單, sell單, 不再掛sell單, 不再掛buy單
    for key in api.list_positions(api.futopt_account):
        if "ZEF" in key.code:
            if key.direction.value == "Buy":
                目前持有ZEF = 1
                buy單 = None
                if 不再掛sell單:
                    不再掛buy單 = 1
            elif key.direction.value == "Sell":
                目前持有ZEF = -1
                sell單 = None
                if 不再掛buy單:
                    不再掛sell單 = 1


def 訂單更新(訂單, 新價格):
    """
    根據新的價格更新訂單。
    """
    api.update_order(trade=訂單, price=新價格, timeout=0)
    api.update_status(api.futopt_account, timeout=0)


# * -------------------掛單邏輯處理區-----------------------
def sell_thread():
    """
    處理 Sell 掛單邏輯。
    """
    global sell單, 不再掛sell單
    while True:
        if SJ_sell:
            while True:
                台灣內外盤差 = 盤口sell - 盤口buy if 盤口buy is not None else 9999
                if 目前持有ZEF >= 0:
                    if sell單:
                        if 台灣內外盤差 > 成本價_down:
                            訂單更新(sell單, SJ_sell - 0.1)
                        else:
                            print("內外盤差低於成本價_down，離場並取消掛單")
                            訂單更新(sell單, SJ_sell + 10)
                    elif not sell單 and not 不再掛sell單 and 台灣內外盤差 > 成本價_up:
                        order = api.Order(
                            action=sj.constant.Action.Sell,
                            price=SJ_sell + 10,
                            quantity=1,
                            price_type=sj.constant.FuturesPriceType.LMT,
                            order_type=sj.constant.OrderType.ROD,
                            octype=sj.constant.FuturesOCType.Auto,
                            account=api.futopt_account,
                        )
                        sell單 = api.place_order(contract, order)
                        time.sleep(0.2)
                elif 目前持有ZEF < 0:
                    不再掛sell單 = True
                    discord.post(
                        content=f"{datetime.now().strftime('%H:%M')} 目前持有ZEF空倉,不需要掛空單"
                    )
                time.sleep(0.1)


def buy_thread():
    """
    處理 Buy 掛單邏輯。
    """
    global buy單, 不再掛buy單
    while True:
        if SJ_buy:
            while True:
                台灣內外盤差 = 盤口sell - 盤口buy if 盤口buy is not None else 9999
                if 目前持有ZEF <= 0:
                    if buy單:
                        if 台灣內外盤差 > 成本價_down:
                            訂單更新(buy單, SJ_buy + 0.1)
                        else:
                            print("內外盤差低於成本價_down，離場並取消掛單")
                            訂單更新(buy單, SJ_buy - 10)
                    elif not buy單 and not 不再掛buy單 and 台灣內外盤差 > 成本價_up:
                        order = api.Order(
                            action=sj.constant.Action.Buy,
                            price=SJ_buy - 10,
                            quantity=1,
                            price_type=sj.constant.FuturesPriceType.LMT,
                            order_type=sj.constant.OrderType.ROD,
                            octype=sj.constant.FuturesOCType.Auto,
                            account=api.futopt_account,
                        )
                        buy單 = api.place_order(contract, order)
                        time.sleep(0.2)
                elif 目前持有ZEF > 0:
                    不再掛buy單 = True
                    discord.post(
                        content=f"{datetime.now().strftime('%H:%M')} 目前持有ZEF多倉,不需要掛多單"
                    )
                time.sleep(0.1)


# * -------------------登入連線區-------------------------
api = sj.Shioaji(simulation=True)
account = api.login(
    api_key="GITHUB重要資訊隱藏",
    secret_key="GITHUB重要資訊隱藏",
    contracts_timeout=30000,
)
result = api.activate_ca(
    ca_path="GITHUB重要資訊隱藏",
    # ca_path="/home/ec2-user/poyen_file/api_key_all/Sinopac.pfx",
    ca_passwd="GITHUB重要資訊隱藏",
    # person_id="Person of this Ca",
)

# 檢查目前持倉
更新目前持有倉位()
print("目前持有ZEF", 目前持有ZEF)
ZEF計算機01 = ZEF價格計算機(
    api=api,
    txf_contract=api.Contracts.Futures["TXFR1"],
    exf_contract=api.Contracts.Futures["EXFR1"],
    zef_contract=api.Contracts.Futures["ZEFR1"],
    params上邊界=(1.18274, 0.00226),
    params下邊界=(1.14191, -0.00250),
)


# 設定回調函數
def tick_callback(exchange: Exchange, tick: TickFOPv1):
    ZEF計算機01.TXF_tick_callback(tick)


def bidask_callback(exchange: Exchange, SJ_bidask: BidAskFOPv1):
    """
    處理來自台灣的即時五檔報價。
    """
    global SJ_buy, SJ_sell, 盤口buy, 盤口sell
    SJ_buy, 盤口buy = float(SJ_bidask["bid_price"][1]), float(SJ_bidask["bid_price"][0])
    SJ_sell, 盤口sell = float(SJ_bidask["ask_price"][1]), float(
        SJ_bidask["ask_price"][0]
    )
    print(
        f"{datetime.now()}\t在台灣收到五檔：|買進:{盤口buy}|賣出:{盤口sell}|內外差:{盤口sell - 盤口buy}"
    )


# 訂閱報價與設定委託回報
api.quote.set_on_bidask_fop_v1_callback(bidask_callback)
api.quote.set_on_tick_fop_v1_callback(tick_callback)
api.set_order_callback(SJ_order_callback)


# 訂閱合約
for contract, quote_type in [
    (ZEF計算機01.txf_contract, sj.constant.QuoteType.Tick),
    (ZEF計算機01.exf_contract, sj.constant.QuoteType.BidAsk),
    (ZEF計算機01.zef_contract, sj.constant.QuoteType.BidAsk),
]:
    api.quote.subscribe(
        contract, quote_type=quote_type, version=sj.constant.QuoteVersion.v1
    )
# 啟動掛單執行緒
threading.Thread(target=sell_thread, daemon=True).start()
threading.Thread(target=buy_thread, daemon=True).start()

ZEF計算機01.啟動報價執行緒()
# 程式持續執行並處理掛單，最後逾時取消未完成訂單並登出

time.sleep(72000)
try:
    api.cancel_order(sell單, timeout=0)
    api.cancel_order(buy單, timeout=0)
    api.update_status(api.futopt_account, timeout=0)
    print(api.usage())
    discord.post(
        content=f"{datetime.now().strftime('%H:%M')} 逾時取消ZEF大量區動態雙向"
    )
    api.logout()
except:
    api.logout()
    pass
