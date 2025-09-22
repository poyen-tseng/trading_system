from datetime import datetime
import shioaji as sj
import time

# from datetime import timedelta
from shioaji import TickFOPv1, BidAskFOPv1, Exchange
import numpy as np
import pandas as pd
from poyen.ibapi_poyen import *


app = IBapi()
app.poyen_connect(7497, 3)

# from winsound import Beep
api = sj.Shioaji(simulation=False)
# 登入一次10M
account = api.login(
    api_key="GITHUB隱藏重要資訊",
    secret_key="GITHUB隱藏重要資訊",
    contracts_timeout=30000,
)


datetime1_arr = np.array([])
sj_bid_arr = np.array([])
sj_ask_arr = np.array([])

ib_result_arr = {
    "datetime": [],
    "bid_price": [],
    "ask_price": [],
}

datetime_temp = None


def sj_quote_callback(exchange: Exchange, bidask: BidAskFOPv1):
    global datetime1_arr, sj_bid_arr, sj_ask_arr
    # 取得現在的時間，精確到微秒
    current_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S.%f")
    datetime1_arr = np.append(datetime1_arr, current_time)  # !注意這裡datetime1或2
    sj_bid_arr = np.append(sj_bid_arr, bidask.bid_price[0])
    sj_ask_arr = np.append(sj_ask_arr, bidask.ask_price[0])

    # print(
    #     f"{current_time}\t在py收到成交資料：| {bidask.datetime} | {bidask.close}| 差距：{差距}"
    # )
    # Console.WriteLine($"{formattedTime}\t收到成交資料\t|\t{quote.datetime}\t|\t{quote.close}");
    # 2024/09/18 18:15:51.900996      py收到成交資料：|2024-09-18 18:15:52.091000|21728


def ib_save2dataframe(ib_data):
    global ib_result_arr
    global datetime_temp
    if all(
        key in ib_data[1] and ib_data[1][key] is not None
        for key in ["bid_price", "ask_price", "bid_size", "ask_size", "datetime"]
    ):
        if datetime_temp != ib_data[1]["datetime"]:
            datetime_temp = ib_data[1]["datetime"]
            ib_result_arr["datetime"].append(ib_data[1]["datetime"])
            ib_result_arr["bid_price"].append(ib_data[1]["bid_price"])
            ib_result_arr["ask_price"].append(ib_data[1]["ask_price"])
    else:
        print("missing data")


api.quote.set_on_bidask_fop_v1_callback(sj_quote_callback)
api.quote.subscribe(
    api.Contracts.Futures.UDF["UDF202412"],
    quote_type=sj.constant.QuoteType.BidAsk,
    version=sj.constant.QuoteVersion.v1,
)


mnq_contract = app.poyen_future_contract("MYM", "CBOT", "202412")
app.poyen_setcallback(ib_save2dataframe)
app.poyen_subscribe(1, mnq_contract)

# 3300=55min
time.sleep(3300)
print(api.usage())
api.logout()

sj_order_book_df = pd.DataFrame(
    {"datetime": datetime1_arr, "bid": sj_bid_arr, "ask": sj_ask_arr}
)
ib_result_df = pd.DataFrame(ib_result_arr)

fileTime = datetime.today().strftime("%Y-%m-%d--%H-%M")
sj_order_book_df.to_parquet(f"datas/{fileTime}_sj_udf存檔.pqt")
ib_result_df.to_parquet(f"datas/{fileTime}_ib_mym存檔.pqt")
app.disconnect()
