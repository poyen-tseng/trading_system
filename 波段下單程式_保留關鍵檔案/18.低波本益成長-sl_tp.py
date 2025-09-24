from finlab import data
from finlab.backtest import sim
import finlab
import pandas as pd
import json
import warnings

warnings.filterwarnings("ignore")

finlab.login("GITHUB隱藏重要資訊")

data.set_storage(data.FileStorage())
pe = data.get("price_earning_ratio:本益比")
rev = data.get("monthly_revenue:當月營收")
rev_ma3 = rev.average(3)
rev_ma12 = rev.average(12)
營業利益成長率 = data.get("fundamental_features:營業利益成長率")
peg = pe / 營業利益成長率

cond1 = rev_ma3 / rev_ma12 > 1.1
cond2 = rev / rev.shift(1) > 0.9

# 進場訊號波動率
atr = data.indicator("ATR", adjust_price=True, timeperiod=10)
adj_close = data.get("etl:adj_close")
entry_volatility = atr / adj_close

# 低波動因子
融資使用率 = data.get("margin_transactions:融資使用率")
業外收支營收率 = data.get("fundamental_features:業外收支營收率")
tree_select_factor = (
    (融資使用率 <= 34) & (entry_volatility <= 0.032) & (業外收支營收率 < 5.2)
)

cond_all = cond1 & cond2 & tree_select_factor

position = (
    peg[cond_all & (peg > 0)]
    .is_smallest(10)
    .reindex(rev.index_str_to_date().index, method="ffill")
)

report = sim(
    position=position,
    fee_ratio=1.425 / 1000 / 3,
    position_limit=0.15,
    stop_loss=0.1,
    trade_at_price="open",
    live_performance_start="2022-04-01",
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

sheet = gc.open_by_url("GITHUB隱藏重要資訊")
sheet_observing = sheet.worksheet_by_title("observing")
sheet_console = sheet.worksheet_by_title("console")

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


# 將字典轉換為列表
keys = list(json_result.keys())
values = list(json_result.values())
# 計算字典的長度
length = len(json_result)

# 動態生成範圍
key_range = f"D6:D{5+length}"
value_range = f"E6:E{5+length}"

# 清空舊資料
sheet_observing.clear(start="D6", end="G40")

# 寫入鍵（股票代號）
sheet_observing.update_values(key_range, [[key] for key in keys])

# 寫入值（status）
sheet_observing.update_values(value_range, [[value] for value in values])

# 讀取每個股要投入的金額
每單買進金額 = sheet_observing.get_value("D3")


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
本日現金餘額 = api.account_balance().acc_balance

# 使用迴圈來逐一獲取每個股票的最新一筆成交價
contracts = [api.Contracts.Stocks[stock_code] for stock_code in stock_list]
snapshots = api.snapshots(contracts)

# snapshot的格式很麻煩，要用[0],[1],[2]...取得每一項以後再用snapshot.close取得內容
# for snapshot in snapshots:
# print(f"Stock code: {snapshot.code}, close: {snapshot.close}")  #ohyes拿到數據了

# 提取成交金額
latest_closes = [snapshot.close for snapshot in snapshots]
quantity_to_buy = [
    round(float(每單買進金額) / float(latest_close)) for latest_close in latest_closes
]
# print(latest_close)
庫存股號清單 = [
    key.code
    for key in api.list_positions(api.stock_account, unit=sj.constant.Unit.Share)
]
# 寫入鍵（股票代號）
sheet_observing.update_values("F6", [[item] for item in latest_closes])
sheet_observing.update_values("G6", [[item] for item in quantity_to_buy])

print("還沒操作過")
# 將策略時間寫入 D2 儲存格
sheet_observing.update_value("D2", convert_to_poyen_format(output["update_date"]))
要買進的股票清單 = [
    key for key, value in json_result.items() if value in ("enter", "hold")
]
要買進的股票清單剔除已經有的 = [
    stock for stock in 要買進的股票清單 if stock not in 庫存股號清單
]
安全下單金額 = float(每單買進金額) * float(len(要買進的股票清單剔除已經有的)) * 1.2
部位總額 = float(每單買進金額) * float(len(要買進的股票清單))
sheet_console.update_value("B1", 本日現金餘額)
sheet_console.update_value("C1", today_poyen_format())
啟動與否 = sheet_console.get_value("B10")

if 啟動與否:
    if 本日現金餘額 > 安全下單金額:
        print("\n餘額", 本日現金餘額)
        print("\n安全下單金額", 安全下單金額)
        print("\n要買進的股票清單剔除已經有的", 要買進的股票清單剔除已經有的)
        sheet_console.update_value("E10", f"現金餘額達{安全下單金額}")
        sheet_console.update_value("D10", 部位總額)
        # 要買進的股票清單 ['2357', '2530', '2545', '2731', '3592', '4560', '4722', '5538', '6807', '8476']
        for 要買的股號 in 要買進的股票清單剔除已經有的:
            contracts = [api.Contracts.Stocks[要買的股號]]
            # print(api.snapshots(contracts)[0].close)
            snapshot_quantity = round(
                float(每單買進金額) / float(api.snapshots(contracts)[0].close)
            )
            snapshot_sell_price = api.snapshots(contracts)[0].sell_price + (
                api.snapshots(contracts)[0].sell_price
                - api.snapshots(contracts)[0].buy_price
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
            # trade = api.place_order(api.Contracts.Stocks[要買的股號], order)

    else:
        print("\n餘額", 本日現金餘額)
        print("\n安全下單金額", 安全下單金額)
        sheet_console.update_value("E10", f"現金餘額未達{安全下單金額}")
    # 隨時要找出要停損停利的部分
    庫存總覽 = api.list_positions(api.stock_account, unit=sj.constant.Unit.Share)
    要賣出的股票清單 = [
        key
        for key, value in json_result.items()
        if value in ["exit", "sl_", "sl", "tp_", "tp"]
    ]
    print("要賣出的股票清單", 要賣出的股票清單)
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
            # trade = api.place_order(api.Contracts.Stocks[持有零股部位.code], order)
else:
    # if 啟動與否 不成立
    sheet_console.update_value("E10", "停止交易")  # 標記為「已經執行」

api.logout()

sheet_console.update_value("C10", today_poyen_format())  # 寫上執行日期
