import datetime
import pandas as pd
import shioaji as sj
import json
from google.oauth2 import service_account

# from winsound import Beep
api = sj.Shioaji(simulation=False)  # 模擬模式
account = api.login(
    api_key="GITHUB隱藏重要資訊",  # 請修改此處
    secret_key="GITHUB隱藏重要資訊",  # 請修改此處
    contracts_timeout=30000,
)
# print(api.margin(api.futopt_account).available_margin ) #查看可動用保證金
# print(api.list_positions(api.futopt_account)) #期權未實現損益 #這個就夠用了
# print(api.list_position_detail(api.futopt_account, 0)) #期權未實現損益 -明細 #特詳細

持有零股清單 = api.list_positions(api.stock_account, unit=sj.constant.Unit.Share)
帳戶資訊 = api.account_balance()
本日證券市值 = 0
# 證券總市值
for i in range(len(持有零股清單)):
    本日證券市值 += 持有零股清單[i].quantity * 持有零股清單[i].last_price
近期交割款_list = api.settlements(api.stock_account)
近期交割總額 = sum(settlement.amount for settlement in 近期交割款_list)
本日證券現金餘額 = 帳戶資訊.acc_balance + 近期交割總額
本日證券總資產 = 本日證券現金餘額 + 本日證券市值

本日期權現金餘額 = api.margin(api.futopt_account).today_balance
本日期權市值 = (
    api.margin(api.futopt_account).equity_amount - 本日期權現金餘額
)  # 庫存市值=總權益-可動保證金
本日期權總資產 = 本日期權市值 + 本日期權現金餘額
# print("本日用量:", api.usage())  # 500MB以下
本日總資產 = 本日證券市值 + 本日證券現金餘額 + 本日期權現金餘額 + 本日期權市值

weekday_number = datetime.date.today().weekday()
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

# 輸出結果
check_time = "".join(
    [datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S "), weekday_chinese]
)

check_today_info = [
    check_time,
    本日總資產,
    本日證券總資產,
    本日證券現金餘額,
    本日證券市值,
    本日期權總資產,
    本日期權現金餘額,
    本日期權市值,
]

import pygsheets

credentials_info = {
    "GITHUB隱藏重要資訊"
}
SCOPES = (
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
)
service_account_info = json.loads(json.dumps(credentials_info))
my_credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)
gc = pygsheets.authorize(custom_credentials=my_credentials)
# gc = pygsheets.authorize(service_file="D:\_TradingSystem\_InTrade\_auth_file\gsheet_auth\poyen-report-net-60808025bbb7.json")
sheet = gc.open_by_url("GITHUB隱藏重要資訊")
total_equity = sheet.worksheet_by_title("total_equity")
total_equity.insert_rows(row=1, number=1, values=check_today_info)
證券column = [
    "序號",
    "股號",
    "方向",
    "數量",
    "均價",
    "最新價格",
    "浮動損益",
    "昨日數量",
    "類別",
    "融資金額",
    "擔保品",
    "保證金",
    "利息",
]
持有零股清單_df = pd.DataFrame(pnl.__dict__ for pnl in 持有零股清單)
# 持有零股清單_df.index.name = None
# 更改列名
if 持有零股清單_df.empty:
    持有零股清單_df = pd.DataFrame(columns=證券column)
else:
    持有零股清單_df.columns = 證券column
position_stock = sheet.worksheet_by_title("position_stock")
position_stock.clear()
position_stock.set_dataframe(
    持有零股清單_df,
    (1, 1),  # include_index=False, include_column_header=False
)

# 期權持倉
期權持倉 = api.list_positions(api.futopt_account)
期權持倉_df = pd.DataFrame(p.__dict__ for p in 期權持倉)
# 期權持倉_df.index.name = None
# 更改列名
期權column = ["序號", "代號", "方向", "數量", "均價", "最新價格", "浮動損益"]
if 期權持倉_df.empty:
    期權持倉_df = pd.DataFrame(columns=期權column)
else:
    期權持倉_df.columns = 期權column
position_future = sheet.worksheet_by_title("position_future")
position_future.clear()
position_future.set_dataframe(
    期權持倉_df,
    (1, 1),  # include_index=False, include_column_header=False
)

# 加入當週交易紀錄
# 找到過去最近的週六
過去最近完整週六 = datetime.date.today()
while 過去最近完整週六.weekday() != 5:
    過去最近完整週六 += datetime.timedelta(days=-1)

過去最近完整週日 = 過去最近完整週六 + datetime.timedelta(days=-6)
當週日 = datetime.date.today()
while 當週日.weekday() != 6:
    當週日 += datetime.timedelta(days=-1)
# print("當週日 =", 當週日)

# .strftime("%Y-%m-%d")
# 現在這週的資料
trade_history_week = sheet.worksheet_by_title("trade_history_week")
# try:
profitloss_summary = api.list_profit_loss_summary(
    api.stock_account, str(當週日), str(datetime.date.today())
)
現在這週證券損益_df = pd.DataFrame(
    pnl.__dict__ for pnl in profitloss_summary.profitloss_summary
)
# print("證券區間損益:\n", 現在這週證券損益_df)
# except:
#     現在這週證券損益_df = pd.DataFrame()
#     pass

# try:
profitloss_summary = api.list_profit_loss_summary(
    api.futopt_account, str(當週日), str(datetime.date.today())
)
現在這週期權損益_df = pd.DataFrame(
    pnl.__dict__ for pnl in profitloss_summary.profitloss_summary
)
# print("期權區間損益:\n", 現在這週期權損益_df)
# except:
#     現在這週期權損益_df = pd.DataFrame()
#     pass
現在這週所有損益_df = pd.concat(
    [現在這週證券損益_df, 現在這週期權損益_df], ignore_index=True
)
trade_history_week.clear()
trade_history_week.set_dataframe(現在這週所有損益_df, (1, 1))


# 過去一週的資料
trade_history = sheet.worksheet_by_title("trade_history")
上次交易紀錄區間 = trade_history.get_value("A2").split("~")
上周交易紀錄截止日 = 上次交易紀錄區間[1].strip()
上周交易紀錄截止日 = datetime.datetime.strptime(上周交易紀錄截止日, "%Y-%m-%d")
if datetime.date.today() > (上周交易紀錄截止日 + datetime.timedelta(days=6)).date():
    # 舊資料太舊 要開始打包上傳資料

    # try:
    profitloss_summary = api.list_profit_loss_summary(
        api.stock_account, str(過去最近完整週日), str(過去最近完整週六)
    )
    過去該週證券損益_df = pd.DataFrame(
        pnl.__dict__ for pnl in profitloss_summary.profitloss_summary
    )
    # print("證券區間損益:\n", df)
    # except:
    #     過去該週證券損益_df = pd.DataFrame()
    #     pass

    # try:
    profitloss_summary = api.list_profit_loss_summary(
        api.futopt_account, str(過去最近完整週日), str(過去最近完整週六)
    )
    過去該週期權損益_df = pd.DataFrame(
        pnl.__dict__ for pnl in profitloss_summary.profitloss_summary
    )
    # print("期權區間損益:\n", df)
    # except:
    #     過去該週期權損益_df = pd.DataFrame()
    #     pass
    過去該週所有損益_df = pd.concat(
        [過去該週證券損益_df, 過去該週期權損益_df], ignore_index=True
    )
    過去該週所有損益_df["日期"] = f"{過去最近完整週日} ~ {過去最近完整週六}"

    # 再把當週所有損益加進去gsheet的歷史成交紀錄
    舊的交易紀錄 = trade_history.get_as_df()
    updated_data = pd.concat([過去該週所有損益_df, 舊的交易紀錄], ignore_index=True)
    trade_history.set_dataframe(updated_data, (1, 1))


api.logout()
