from finlab.backtest import sim
import finlab
import pandas as pd
import json
from datetime import datetime, timedelta
from finlab import data, backtest
from datetime import datetime, timedelta
import time

finlab.login("GITHUB隱藏重要資訊")

data.set_storage(data.FileStorage())


# 改裝監獄兔
處置股資訊 = data.get("disposal_information").sort_index()
close = data.get("price:收盤價")
處置股資訊 = 處置股資訊[~處置股資訊["分時交易"].isna()].dropna(how="all")
處置股資訊 = 處置股資訊[處置股資訊["分時交易"].isin([5, 20])].dropna(how="all")
處置股資訊 = 處置股資訊.reset_index()[["stock_id", "date", "處置結束時間"]]
處置股資訊.columns = ["stock_id", "處置開始時間", "處置結束時間"]
position = close < 0
for i in range(0, 處置股資訊.shape[0]):
    stock_id = 處置股資訊.iloc[i, 0]
    if len(stock_id) == 4:
        start_day = 處置股資訊.iloc[i, 1] + timedelta(days=5)  # 8
        end_day = 處置股資訊.iloc[i, 2] + timedelta(days=-1)
        position.loc[start_day:end_day, stock_id] = True
# =================三頻率 rsi #不能全加入
rsi10 = data.indicator("RSI", timeperiod=10)
短週期RSI高檔頓化 = (rsi10 > 75).sustain(3)  # 好
price_pct = close.pct_change(periods=126)
position_RSI = (((position & ~短週期RSI高檔頓化) * price_pct)).is_largest(5)

report = sim(
    position_RSI.loc["2021":],
    stop_loss=0.15,
    trade_at_price="open",
    fee_ratio=1.425 / 1000 / 3,
    position_limit=0.2,
    name="改裝監獄兔",
    upload=False,
)


# Assuming report.position_info is an HTML object
output = report.position_info()

df = pd.DataFrame.from_dict(output)

# 提取股票代號和status
result = {
    key.split()[0]: value["status"]
    for key, value in output.items()
    if isinstance(value, dict)
}

# 轉換成JSON格式
json_result = json.loads(json.dumps(result, ensure_ascii=False, indent=4))
# print(type(json_result))
# print(json_result)

# =======================================================================

from google.oauth2 import service_account

# 首先判斷執行與否
import pygsheets

credentials_info = {"GITHUB隱藏重要資訊"}
SCOPES = (
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
)
service_account_info = json.loads(json.dumps(credentials_info))
my_credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)
gc = pygsheets.authorize(custom_credentials=my_credentials)
# gc = pygsheets.authorize
sheet = gc.open_by_url("GITHUB隱藏重要資訊")
sheet_observing = sheet.worksheet_by_title("observing")
sheet_console = sheet.worksheet_by_title("console")

策略金額 = "D3"


from datetime import datetime


def convert_to_poyen_format(date_str):
    # 將字串轉換為 datetime 對象
    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")

    # 獲取星期數字
    weekday_number = date_obj.weekday()

    # 星期中文對應表
    weekday_dict = {
        0: "一",
        1: "二",
        2: "三",
        3: "四",
        4: "五",
        5: "六",
        6: "日",
    }

    # 轉換成中文星期表示
    weekday_chinese = weekday_dict.get(weekday_number, "未知")

    # 格式化日期
    formatted_date = date_obj.strftime(f"%Y/%m/%d {weekday_chinese}")
    return formatted_date


def today_poyen_format():
    # 獲取星期數字
    weekday_number = datetime.today().weekday()
    # 星期中文對應表
    weekday_dict = {
        0: "一",
        1: "二",
        2: "三",
        3: "四",
        4: "五",
        5: "六",
        6: "日",
    }
    # 轉換成中文星期表示
    weekday_chinese = weekday_dict.get(weekday_number, "未知")
    # 格式化日期
    check_time = "".join(
        [
            datetime.today().strftime("%Y/%m/%d "),
            weekday_chinese,
            datetime.today().strftime(" %H:%M:%S"),
        ]
    )
    return check_time


def a1_to_rowcol(cell_address):
    """
    將 Excel 樣式的單元格地址轉換為行列號。
    參數:
    cell_address (str): Excel 樣式的單元格地址（如 "A1" 或 "B3"）。
    返回:
    tuple: 包含行號和列號的元組（如 (1, 1) 或 (2, 3)）。
    """
    column = cell_address.rstrip("0123456789")
    row = cell_address[len(column) :]
    col_num = sum(
        (ord(char) - ord("A") + 1) * (26**i) for i, char in enumerate(reversed(column))
    )
    return int(row), int(col_num)


# 將字典轉換為列表
keys = list(json_result.keys())
values = list(json_result.values())
# 計算字典的長度
length = len(json_result)


observing_cell = "J6"
cell_row, cell_col = a1_to_rowcol(observing_cell)
# 清空舊資料
sheet_observing.clear(
    start=observing_cell, end=(cell_row + 40, cell_col + 3)
)  # 寫入之前先清空舊資料


# 動態生成範圍
# key_range = f"D6:D{5+length}"  # keyrange填入股票代號
# value_range = f"E6:E{5+length}"  # value_range填入exit或hold / buy

# # 寫入鍵（股票代號）
# sheet_observing.update_values(key_range, [[key] for key in keys])
# # 寫入值（status）buy / hold /exit
# sheet_observing.update_values(value_range, [[value] for value in values])
# 動態生成範圍
key_range = (cell_row, cell_col)
value_range = (cell_row, cell_col + 1)
# 寫入鍵（股票代號）
sheet_observing.update_values(key_range, [[key] for key in keys])
# 寫入值（status）buy / hold /exit
sheet_observing.update_values(value_range, [[value] for value in values])

# 寫入時間和讀取每單金額
observing_time = "J2"
# 將策略時間寫入 D2 儲存格
sheet_observing.update_value(
    observing_time, convert_to_poyen_format(output["update_date"])
)
# 找到指定儲存格的位置
cell_row, cell_col = a1_to_rowcol(observing_time)
# 在時間下方讀取每個股要投入的金額
ordervalue = sheet_observing.cell((cell_row + 1, cell_col)).value


import shioaji as sj

api = sj.Shioaji(simulation=False)  # 模擬模式
# 登入一次10M
account = api.login(
    api_key="GITHUB隱藏重要資訊",  # 請修改此處
    secret_key="GITHUB隱藏重要資訊",  # 請修改此處
    contracts_timeout=30000,
)

result = api.activate_ca(
    ca_path="Sinopac.pfx",
    ca_passwd="GITHUB隱藏重要資訊",
    # person_id="Person of this Ca",
)


# 儲存contract的列表
contracts = []
# 快照每個股成交金額
# 要快照的商品清單
# 提取值為 "enter" 的鍵
stock_list = [key for key, value in json_result.items()]  # if value == 'enter']
# print(json_result)
# print(stock_list)


# 使用迴圈來逐一獲取每個股票的最新一筆成交價
contracts = [api.Contracts.Stocks[stock_code] for stock_code in stock_list]
snapshots = api.snapshots(contracts)

# snapshot的格式很麻煩，要用[0],[1],[2]...取得每一項以後再用snapshot.close取得內容
# for snapshot in snapshots:
# print(f"Stock code: {snapshot.code}, close: {snapshot.close}")  #ohyes拿到數據了

# 提取成交金額
latest_closes = [snapshot.close for snapshot in snapshots]
quantity_to_buy = [
    round(float(ordervalue) / float(latest_close)) for latest_close in latest_closes
]
# print(latest_close)
庫存股號清單 = [
    key.code
    for key in api.list_positions(api.stock_account, unit=sj.constant.Unit.Share)
]
# 寫入鍵（股票代號）
# sheet_observing.update_values("F6", [[item] for item in latest_closes])
# sheet_observing.update_values("G6", [[item] for item in quantity_to_buy])
cell_row, cell_col = a1_to_rowcol(observing_cell)
# 動態生成範圍
key_range = (cell_row, cell_col + 2)
value_range = (cell_row, cell_col + 3)
# 寫入鍵（股票代號）
sheet_observing.update_values(key_range, [[item] for item in latest_closes])
# 寫入值（status）buy / hold /exit
sheet_observing.update_values(value_range, [[item] for item in quantity_to_buy])


print("還沒操作過")

要買進的股票清單 = [
    key for key, value in json_result.items() if value in ("enter", "hold")
]
要買進的股票清單剔除已經有的 = [
    stock for stock in 要買進的股票清單 if stock not in 庫存股號清單
]
print("要買進的股票清單剔除已經有的", 要買進的股票清單剔除已經有的)

# 買進的預收款
for 要預收款的股號 in 要買進的股票清單剔除已經有的:
    contracts = [api.Contracts.Stocks[要預收款的股號]]
    預收款預計買N股 = round(
        float(ordervalue) / float(api.snapshots(contracts)[0].close)
    )
    預收款預計成交價 = api.snapshots(contracts)[0].sell_price * 1.1  # 多收10%保證沒問題
    print("contracts是", contracts)
    print("預收款預計買N股:", 預收款預計買N股)
    print("預收款預計成交價", 預收款預計成交價)

    resp = api.reserve_earmarking(
        account[2], contracts, 預收款預計買N股, 預收款預計成交價
    )
    print("resp是", resp)


"""
# 等他扣款成功
time.sleep(5)
# 要買進的股票清單 ['2357', '2530', '2545', '2731', '3592', '4560', '4722', '5538', '6807', '8476']
for 要買的股號 in 要買進的股票清單剔除已經有的:
    contracts = [api.Contracts.Stocks[要買的股號]]
    # print(api.snapshots(contracts)[0].close)
    snapshot_quantity = round(
        float(ordervalue) / float(api.snapshots(contracts)[0].close)
    )
    snapshot_sell_price = api.snapshots(contracts)[0].sell_price + (
        api.snapshots(contracts)[0].sell_price - api.snapshots(contracts)[0].buy_price
    )  # 加上一個tick去買 就是要用市價去做撮合 就能保證成交

    # 證券委託單 - 請修改此處
    order = api.Order(
        price=snapshot_sell_price,  # 價格
        quantity=snapshot_quantity,  # 數量
        action=sj.constant.Action.Buy,  # 買賣別
        # price_type=sj.constant.StockPriceType.LMT,  # 委託價格類別
        price_type=sj.constant.StockPriceType.LMT,  # 委託價格類別
        order_type=sj.constant.OrderType.ROD,  # 委託條件
        order_lot=sj.constant.StockOrderLot.IntradayOdd,  #!!!!!!!!!!!!!!!!!!!!是零股非常重要!!!!!!!!!!!!!!!!!!!!!!!!!!!
        account=api.stock_account,  # 下單帳號
    )
    # 下單
    # print("\n要買的股號", 要買的股號)
    trade = api.place_order(api.Contracts.Stocks[要買的股號], order)

# 隨時要找出要停損停利的部分
庫存總覽 = api.list_positions(api.stock_account, unit=sj.constant.Unit.Share)

要賣出的股票清單 = [key for key, value in json_result.items() if value == "exit"]
print("要賣出的股票清單", 要賣出的股票清單)

# 賣出要圈存
for 持有零股部位 in 庫存總覽:
    if 持有零股部位.code in 要賣出的股票清單:
        contracts = [api.Contracts.Stocks[持有零股部位.code]]
        預收款預計買N股 = round(
            float(ordervalue) / float(api.snapshots(contracts)[0].close)
        )
        resp = api.reserve_stock(account, contracts, 持有零股部位.quantity)
# 等他圈存成功
time.sleep(5)

for 持有零股部位 in 庫存總覽:
    if 持有零股部位.code in 要賣出的股票清單:
        # print(f"Stock to sell: {持有零股部位.code}, quantity: {持有零股部位.quantity}")
        contracts = [api.Contracts.Stocks[持有零股部位.code]]
        snapshot_quantity = 持有零股部位.quantity
        snapshot_buy_price = api.snapshots(contracts)[0].buy_price - (
            api.snapshots(contracts)[0].sell_price
            - api.snapshots(contracts)[0].buy_price
        )  # 減去一個tick去賣 就是要用市價去做撮合 就能保證成交
        # 證券委託單 - 請修改此處
        order = api.Order(
            price=snapshot_buy_price,  # 價格
            quantity=snapshot_quantity,  # 數量
            action=sj.constant.Action.Sell,  # 買賣別
            # price_type=sj.constant.StockPriceType.LMT,  # 委託價格類別
            price_type=sj.constant.StockPriceType.LMT,  # 委託價格類別
            order_type=sj.constant.OrderType.ROD,  # 委託條件
            order_lot=sj.constant.StockOrderLot.IntradayOdd,  #!!!!!!!!!!!!!!!!!!!!是零股非常重要!!!!!!!!!!!!!!!!!!!!!!!!!!!
            account=api.stock_account,  # 下單帳號
        )
        # 下單
        # print("\n持有零股部位.code", 持有零股部位.code)
        trade = api.place_order(api.Contracts.Stocks[持有零股部位.code], order)
api.logout()

# sheet_console.update_value("B4", 1)  # 標記為「已經執行」
# sheet_console.update_value("C4", today_poyen_format())  # 寫上執行日期

# 指定儲存格和要寫入的資料
console_cell = "B5"
data = [1, today_poyen_format()]

# 找到指定儲存格的位置
cell_row, cell_col = a1_to_rowcol(console_cell)

# 寫入資料
for i, value in enumerate(data):
    sheet_console.update_value((cell_row, cell_col + i), value)


# 要買進的股票清單剔除已經有的 ['2243', '3047', '3363', '3379', '3535', '3593', '4510', '4927', '5484', '6133', '6187', '6218', '6231', '6442', '6937', '8906', '8937']
# 要賣出的股票清單 ['2349', '2467', '2486', '4562', '6698', '8374']


"""
