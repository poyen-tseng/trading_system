from datetime import datetime
import shioaji as sj
import time
from datetime import timedelta
from shioaji import TickFOPv1, BidAskFOPv1, Exchange
import numpy as np
import pandas as pd

# from winsound import Beep
api = sj.Shioaji(simulation=False)
# 登入一次10M
account = api.login(
    api_key="GITHUB隱藏重要資訊",
    secret_key="GITHUB隱藏重要資訊",
    contracts_timeout=30000,
)


差距_arr = np.array([])
datetime1_arr = np.array([])
bid_arr = np.array([])
ask_arr = np.array([])


def quote_callback(exchange: Exchange, bidask: BidAskFOPv1):
    global 差距_arr, datetime1_arr, bid_arr, ask_arr
    # 取得現在的時間，精確到微秒
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    datetime1_arr = np.append(datetime1_arr, current_time)  # !注意這裡datetime1或2
    bid_arr = np.append(bid_arr, bidask.bid_price[0])
    ask_arr = np.append(ask_arr, bidask.ask_price[0])

    # print(
    #     f"{current_time}\t在py收到成交資料：| {bidask.datetime} | {bidask.close}| 差距：{差距}"
    # )
    # Console.WriteLine($"{formattedTime}\t收到成交資料\t|\t{quote.datetime}\t|\t{quote.close}");
    # 2024/09/18 18:15:51.900996      py收到成交資料：|2024-09-18 18:15:52.091000|21728


api.quote.set_on_bidask_fop_v1_callback(quote_callback)
api.quote.subscribe(
    api.Contracts.Futures.UDF["UDF202412"],
    quote_type=sj.constant.QuoteType.BidAsk,
    version=sj.constant.QuoteVersion.v1,
)
time.sleep(10)
print(api.usage())
api.logout()

order_book_df = pd.DataFrame(
    {"datetime": datetime1_arr, "bid": bid_arr, "ask": ask_arr}
)
fileTime = datetime.today().strftime("%Y-%m-%d--%H-%M-%S")
order_book_df.to_parquet(f"datas/{fileTime}sj_udf存檔.pqt")
