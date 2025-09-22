from datetime import datetime
import time
import shioaji as sj
from shioaji import TickFOPv1, BidAskFOPv1, Exchange
import numpy as np
from discordwebhook import Discord
import threading

# from poyen.ibapi_poyen import *
discord = Discord(url="GITHUB隱藏重要資訊")
SJ_buy = 0
SJ_sell = 0
# IB_buy = 0
# IB_sell = 0
成本價_up = 7
成本價_down = 6
sell單 = None
buy單 = None
大量區定義 = 8
目前持有UDF = 0
不再掛sell單 = 0
不再掛buy單 = 0
buy成本 = 0
sell成本 = 0


# * -------------------callback函式區-----------------------
def SJ_callback(exchange: Exchange, SJ_bidask: BidAskFOPv1):
    global SJ_buy, SJ_sell
    volume_buy_array = np.asarray(SJ_bidask["bid_volume"])
    mask_buy = volume_buy_array > 大量區定義
    if np.any(mask_buy):
        selected_buy_index = np.argmax(mask_buy)
    else:
        selected_buy_index = 3
    # selected_buy_index = np.argmax(volume_buy_array)
    SJ_buy = int(SJ_bidask["bid_price"][selected_buy_index])

    volume_sell_array = np.asarray(SJ_bidask["ask_volume"])
    mask_sell = volume_sell_array > 大量區定義
    if np.any(mask_sell):
        selected_sell_index = np.argmax(mask_sell)
    else:
        selected_sell_index = 3
    # selected_sell_index = np.argmax(volume_sell_array)
    SJ_sell = int(SJ_bidask["ask_price"][selected_sell_index])
    # print(
    #     f"{datetime.now()}\t在台灣收到五檔：|買進:{SJ_bidask.bid_price[0]}|賣出:{SJ_bidask.ask_price[0]}"
    # )


def SJ_order_callback(stat, msg):
    global 目前持有UDF, buy單, sell單, 不再掛buy單, 不再掛sell單, buy成本, sell成本
    try:
        # if msg["status"]["modified_price"]:
        #     委託價格 = msg["status"]["modified_price"]
        # else:
        #     委託價格 = msg["order"]["price"]
        # print(
        #     f'{datetime.now()},\t{msg["order"]["action"]}\t{msg["contract"]["code"]}\t{委託價格}\t{msg["order"]["quantity"] - msg["status"]["cancel_quantity"]}\t{msg["operation"]["op_type"]}\t{msg["operation"]["op_msg"]}'
        # )
        if "此" in msg["operation"]["op_msg"]:
            # 目前持有UDF = 0
            # 然後接著檢驗是否持有多空倉
            for key in api.list_positions(api.futopt_account):
                if "UDF" in key.code:
                    if key.direction.value == "Buy":
                        目前持有UDF = 1
                        buy單 = None
                        buy成本 = key.price
                        不再掛buy單 = 1
                    elif key.direction.value == "Sell":
                        目前持有UDF = -1
                        sell成本 = key.price
                        sell單 = None
                        不再掛sell單 = 1
            if msg["order"]["action"] == "Sell":
                sell單 = None
                if 不再掛buy單:
                    不再掛sell單 = 1
            elif msg["order"]["action"] == "Buy":
                buy單 = None
                if 不再掛sell單:
                    不再掛buy單 = 1
    except Exception as e:
        print("錯誤發生！！！")
        print(e)
        time.sleep(2)
        for key in api.list_positions(api.futopt_account):
            if "UDF" in key.code:
                if key.direction.value == "Buy":
                    目前持有UDF = 1
                    buy單 = None
                    buy成本 = key.price
                    # 以下用於?
                    if 不再掛sell單:
                        不再掛buy單 = 1
                elif key.direction.value == "Sell":
                    目前持有UDF = -1
                    sell單 = None
                    sell成本 = key.price
                    if 不再掛buy單:
                        不再掛sell單 = 1


# * -------------------比價改單區-------------------
def sell_thread():
    global SJ_buy, SJ_sell, sell單, 目前持有UDF, contract, 不再掛sell單, 不再掛buy單
    while not 不再掛sell單:
        # 表示可以掛sell單
        台灣內外盤差 = SJ_sell - SJ_buy
        if 目前持有UDF >= 0:
            # if 目前持有多單/沒有單:
            if sell單 is not None:
                # if 目前有掛sell單在市場上
                if 台灣內外盤差 > 成本價_down:
                    # if 台灣高掛程度 < 1000 and 台灣內外盤差>成本價_down:
                    # 就改sell價
                    if SJ_buy - buy成本 > -20:
                        # 不用停損
                        api.update_order(trade=sell單, price=SJ_sell - 1, timeout=0)
                        api.update_status(api.futopt_account, timeout=0)
                    else:
                        # 開始停損
                        # print("停損中")
                        api.update_order(trade=sell單, price=SJ_sell - 8, timeout=0)
                        api.update_status(api.futopt_account, timeout=0)

                elif 台灣內外盤差 < 成本價_down:
                    # 優勢消失就逃跑
                    print("內外盤差低於成本價_down,離場")
                    # api.cancel_order(sell單, timeout=0)
                    api.update_order(trade=sell單, price=SJ_sell + 50, timeout=0)
                    api.update_status(
                        api.futopt_account, timeout=0
                    )  # 必須要update status

            elif sell單 is None and not 不再掛sell單:
                print("the 'sell單' is None")
                if 目前持有UDF >= 0 and 台灣內外盤差 > 成本價_up:
                    # 再次確認真的沒有UDF空倉於是就下單
                    order = api.Order(
                        action=sj.constant.Action.Sell,
                        price=SJ_sell + 50,
                        quantity=1,
                        price_type=sj.constant.FuturesPriceType.LMT,
                        order_type=sj.constant.OrderType.ROD,
                        octype=sj.constant.FuturesOCType.Auto,
                        account=api.futopt_account,
                    )
                    sell單 = api.place_order(contract, order)
                    time.sleep(1)
        elif 目前持有UDF < 0 and 不再掛sell單 == 0:
            # 目前持有空倉
            不再掛sell單 = 1
            print("剛剛掛的已經成交了,或早就持有UDF空倉,不需要掛空單")
            # discord.post(
            #     content=f"{datetime.now().strftime('%H:%M')} 目前持有UDF空倉,不需要掛空單"
            # )
            # print(api.usage())
        time.sleep(0.1)


# * ------------然後是處理掛多單的部份--------------
def buy_thread():
    global SJ_buy, SJ_sell, buy單, sell單, 目前持有UDF, contract, 不再掛sell單, 不再掛buy單, buy成本, sell成本
    while True:
        台灣內外盤差 = SJ_sell - SJ_buy
        if 目前持有UDF <= 0:
            # if 目前持有空單/沒有單:
            if buy單 is not None:
                # if 目前有掛sell單在市場上
                if 台灣內外盤差 > 成本價_down:
                    # 就改sell價
                    api.update_order(trade=buy單, price=SJ_buy + 1)
                    api.update_status(api.futopt_account, timeout=0)

                elif 台灣內外盤差 < 成本價_down:
                    # 優勢消失就逃跑
                    print("內外盤差低於成本價_down,離場")
                    # api.cancel_order(buy單, timeout=0)
                    api.update_order(trade=buy單, price=SJ_buy - 50)
                    api.update_status(api.futopt_account, timeout=0)

            elif buy單 is None and not 不再掛buy單:
                print("the 'buy單' is None")
                if 目前持有UDF <= 0 and 台灣內外盤差 > 成本價_up:
                    # 再次確認真的沒有UDF多倉於是就下單
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
                    time.sleep(0.1)
        elif 目前持有UDF > 0 and 不再掛buy單 == 0:
            # 目前持有多倉
            不再掛buy單 = 1
            print("剛剛掛的已經成交了,或早就持有UDF多倉,不需要掛多單,改成賣出")
            # 現在要把他賣掉
            # discord.post(
            #     content=f"{datetime.now().strftime('%H:%M')} 目前持有UDF多倉,不需要掛多單,改成賣出"
            # )
            不再掛sell單 = 0
            time.sleep(2)
            sell_thread()
            print(api.usage())
        if 不再掛buy單 and 不再掛sell單:
            # 準備下一個迴圈
            不再掛buy單 = 0
            不再掛sell單 = 0
            buy單 = None
            sell單 = None
            目前持有UDF = 0
            for key in api.list_positions(api.futopt_account):
                if "UDF" in key.code:
                    if key.direction.value == "Buy":
                        目前持有UDF = 1
                        buy成本 = key.price
                    elif key.direction.value == "Sell":
                        sell成本 = key.price
                        目前持有UDF = -1
            print("本次多單結束")
            time.sleep(60)
            # 2秒後再重新下單
        time.sleep(0.1)


# * -------------------登入連線區-------------------------
# from winsound import Beep
api = sj.Shioaji(simulation=False)
# 登入一次10M
account = api.login(
    api_key="GITHUB隱藏重要資訊",  # os.environ["SJ_API_KEY"],  # 請修改此處
    secret_key="GITHUB隱藏重要資訊",  # os.environ["SJ_LOGIN_KEY"],  # 請修改此處
    contracts_timeout=30000,
)
result = api.activate_ca(
    # ca_path="D:\API_key_all\shiaoji\ekey\Sinopac.pfx",
    ca_path="/home/ec2-user/poyen_file/api_key_all/Sinopac.pfx",
    ca_passwd="GITHUB隱藏重要資訊",
    # person_id="Person of this Ca",
)
# * --------------------首先檢查持倉--------------------
# 先假設沒有空倉也沒有多倉
目前持有UDF = 0
# 然後接著檢驗是否持有多空倉
for key in api.list_positions(api.futopt_account):
    if "UDF" in key.code:
        if key.direction.value == "Buy":
            目前持有UDF = 1
            buy成本 = key.price

        elif key.direction.value == "Sell":
            目前持有UDF = -1
            sell成本 = key.price
print("目前持有UDF", 目前持有UDF)

# * -------------------報價訂閱區-------------------------
api.quote.set_on_bidask_fop_v1_callback(SJ_callback)
contract = api.Contracts.Futures.UDF["UDF202412"]
api.quote.subscribe(
    contract,
    # api.Contracts.Futures.UDF["UDF202412"],
    quote_type=sj.constant.QuoteType.BidAsk,
    version=sj.constant.QuoteVersion.v1,
)

# * -------------設定委託回報--------------
api.set_order_callback(SJ_order_callback)

# *-------------------各自收報價-------------------

# threading.Thread(target=sell_thread, daemon=True).start()
threading.Thread(target=buy_thread, daemon=True).start()


time.sleep(72000)
try:
    api.cancel_order(sell單, timeout=0)
    api.cancel_order(buy單, timeout=0)
    api.update_status(api.futopt_account, timeout=0)
    time.sleep(2)
    print(api.usage())
    discord.post(
        content=f"{datetime.now().strftime('%H:%M')} 逾時取消UDF大量區動態雙向"
    )
    # *-------------------登出---------------------
    api.logout()
except:
    api.logout()
    pass
