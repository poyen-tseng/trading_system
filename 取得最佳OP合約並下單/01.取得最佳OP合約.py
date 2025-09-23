# 先取得最近交易日
import yfinance as yf

latestTradeDate = str(
    yf.download("2330.TW", interval="1d", period="1d").index[0].date()
)
print(latestTradeDate)


# 接著取得最近交易日的OP總攬 下午4:30以後更新資料
from FinMind.data import DataLoader

api = DataLoader()
# api.login_by_token(api_token='token')
# api.login(user_id='user_id',password='password')
df_op = api.taiwan_option_daily(option_id="TXO", start_date=latestTradeDate)
# print(df_op)
df_op.rename(
    columns={"open": "OP_open", "max": "OP_max", "min": "OP_min", "close": "OP_close"},
    inplace=True,
)
# df_op_month_no_W = df_op[~df_op["contract_date"].str.contains('W')].copy()
# df_op_month_no_W['contract_date'] = df_op_month_no_W['contract_date'].astype(str)+'W3'

latestContract = df_op["contract_date"].iloc[0]
# print(latestContract)

df_op.drop(df_op[df_op["trading_session"] == "after_market"].index, inplace=True)
df_op.drop(df_op[df_op["open_interest"] == 0].index, inplace=True)
df_op.drop(df_op[df_op["contract_date"] != latestContract].index, inplace=True)
df_op.to_parquet("00.hot_datas/01.latest_op.pqt", compression="brotli")

"""
ready = []
ready[0] = df_op[df_op["call_put"] == "call" & df_op["open_interest"] >= 8000]
ready[1] = df_op[
    df_op["call_put"] == "put" & df_op["OP_close"] <= 10 & df_op["OP_close"] >= 7
]
print(ready)
"""
best_call = df_op[(df_op["call_put"] == "call") & (df_op["open_interest"] >= 7700)]
best_put = df_op[
    (df_op["call_put"] == "put") & (df_op["OP_close"] <= 11) & (df_op["OP_close"] >= 7)
]
print(best_call)
# print(best_put)

import pandas as pd


def generate_option_string(row):
    """
    根據提供的表格數據生成所需的字符串。

    :param row: pandas 表格中的一行數據
    :return: 生成的字符串
    """
    date = row["date"]
    contract_date = row["contract_date"]
    strike_price = int(row["strike_price"])
    call_put = row["call_put"]

    # 分析合約類型
    if "W" in contract_date:
        contract_type = f"TX{contract_date[-1]}"
    else:
        contract_type = "TXO"

    # 組合年月份
    year_month = contract_date[:6]

    # 處理看漲或看跌
    if call_put.lower() == "call":
        call_put_indicator = "C"
    elif call_put.lower() == "put":
        call_put_indicator = "P"
    else:
        raise ValueError("call_put 必須是 'call' 或 'put'")

    # 組合整個字符串
    option_string = f"api.Contracts.Options.{contract_type}.{contract_type}{year_month}{strike_price:05d}{call_put_indicator}"

    return option_string


# 新增一列來儲存生成的字符串
df_op["option_string"] = df_op.apply(generate_option_string, axis=1)

# 顯示結果
# print(df_op[["date", "contract_date", "strike_price", "call_put", "option_string"]])

"""
        date   contract_date  strike_price  call_put     option_string
1178  2024-06-25      202406W4       19600.0     call  api.Contracts.Options.TX4.TX420240619600C
1179  2024-06-25      202406W4       19600.0      put  api.Contracts.Options.TX4.TX420240619600P
1180  2024-06-25      202406W4       19700.0     call  api.Contracts.Options.TX4.TX420240619700C
1181  2024-06-25      202406W4       19700.0      put  api.Contracts.Options.TX4.TX420240619700P
"""
