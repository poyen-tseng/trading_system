from datetime import datetime
import shioaji as sj
import json
from google.oauth2 import service_account

# 首先判斷執行與否
import pygsheets

credentials_info = {"GITHUB移除重要資訊"}
SCOPES = (
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
)
service_account_info = json.loads(json.dumps(credentials_info))
my_credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)
gc = pygsheets.authorize(custom_credentials=my_credentials)

sheet = gc.open_by_url("GITHUB移除重要資訊")
sheet_console = sheet.worksheet_by_title("console")

# 獲取第一行的所有值（通常是列標題）
headers_of_sheet_console = sheet_console.get_row(1, include_tailing_empty=False)
headers = sheet_console.get_row(1, include_tailing_empty=False)

# 查找 'strat' 和 'executed' 欄位的索引
strat_column = "策略名稱"
executed_column = "執行與否"
executed_value = None


def OPbcbp_upload_order():
    # 首先要登入
    api = sj.Shioaji(simulation=False)  # 模擬模式
    # 登入一次10M
    account = api.login(
        api_key="GITHUB移除重要資訊",  # 請修改此處
        secret_key="GITHUB移除重要資訊",  # 請修改此處
        contracts_timeout=30000,
    )
    # 判斷帳戶餘額
    本日期權現金餘額 = api.margin(api.futopt_account).available_margin
    print(本日期權現金餘額)
    if 本日期權現金餘額 > 5000:
        # 資金足夠可以交易
        print("期權資金足夠可以交易")
        # =====開始查找最適合的合約=====
        # 先取得最近交易日
        import yfinance as yf

        latestTradeDate = str(
            yf.download("2330.TW", interval="1d", period="1d").index[0].date()
        )
        # 接著取得最近交易日的OP總攬 下午4:30以後更新資料
        from FinMind.data import DataLoader

        api = DataLoader()
        df_op = api.taiwan_option_daily(option_id="TXO", start_date=latestTradeDate)
        latestContract = df_op["contract_date"].iloc[0]
        df_op.drop(
            df_op[df_op["trading_session"] == "after_market"].index, inplace=True
        )
        df_op.drop(df_op[df_op["open_interest"] == 0].index, inplace=True)
        df_op.drop(df_op[df_op["contract_date"] != latestContract].index, inplace=True)

        best_call_8K_lot = df_op[
            (df_op["call_put"] == "call") & (df_op["open_interest"] >= 7700)
        ]

        # print(best_call_8K_lot)
        best_call_8K_lot = best_call_8K_lot.apply(generate_option_string, axis=1)
        print(best_call_8K_lot)

        sheet_observing = sheet.worksheet_by_title("observing")

        # 將當前時間寫入 A2 儲存格
        sheet_observing.update_value("A2", nowTime_poyen_format())
        # 清理A3-A20
        sheet_observing.clear(start="A3", end="A20")
        # 將值覆寫到從 A3 開始的儲存格
        for i, value in enumerate(best_call_8K_lot.values, start=3):
            sheet_observing.update_value(f"A{i}", value)

    elif 本日期權現金餘額 < 5000:
        # 資金不足停止下單
        print("期權資金不足停止下單")
    # print(api.usage())


def nowTime_poyen_format():
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

    # 輸出結果
    return "".join([datetime.today().strftime("%Y/%m/%dT%H:%M:%S "), weekday_chinese])


def generate_option_string(row):

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


if strat_column in headers and executed_column in headers:
    strat_index = headers.index(strat_column) + 1  # 列索引從1開始
    executed_index = headers.index(executed_column) + 1

    # 獲取 'strat' 欄位的所有值
    strat_values = sheet_console.get_col(strat_index, include_tailing_empty=False)

    # 查找 'strat' 欄位中值為 'OPbcbp' 的行索引
    search_value = "OPbcbp"
    if search_value in strat_values:
        row_index = strat_values.index(search_value) + 1  # 行索引從1開始

        # 獲取該行 'executed' 欄位的值
        executed_value = sheet_console.cell((row_index, executed_index)).value
        print(
            f"The value in the 'executed' column for '{search_value}' in 'strat' column is: {executed_value}"
        )

        executed_value = int(executed_value)
        print(executed_value)
        if executed_value == 1:
            # 已經有下單過了，別再下單了，離開
            print("已經有下單過了，別再下單了，離開")
        elif executed_value == 0:
            # 開始下單程序
            # 判斷現在時間 週二或週三早上就算了
            # 獲取當前時間
            today = datetime.today().weekday()

            # 如果今天是星期二（1）或星期三（2），則輸出 "dont"
            if today in [1, 2]:
                print("dont do anything")
            else:
                # 其他時間輸出 "do it"
                print("start opbcbp")
                OPbcbp_upload_order()

        else:
            print("executed_value無法正常判斷數值")
    else:
        print(f"Value '{search_value}' not found in the 'strat' column.")
else:
    print(f"Either '{strat_column}' or '{executed_column}' column not found.")

# 用來下單的function


# print(api.margin(api.futopt_account).available_margin ) #查看可動用保證金
# print(api.list_positions(api.futopt_account)) #期權未實現損益 #這個就夠用了
# print(api.list_position_detail(api.futopt_account, 0)) #期權未實現損益 -明細 #特詳細

# 發送通知即將下單


"""
# 定義組合單的合約
combo_contracts = [
    api.Contracts.Options.TX4.TX420240619600C,  # 買進選擇權合約
    api.Contracts.Options.TX4.TX420240619700C   # 賣出選擇權合約
]

# 定義組合單的委託單
combo_order = api.ComboOrder(
    price_type="LMT",         # 價格類型，限價單
    price=1,                  # 價格
    quantity=1,               # 數量
    order_type="IOC",         # 委託類型，即時成交否則取消
    legs=[1, -1],             # 每個合約的買賣數量，1表示買進，-1表示賣出
    account=api.stock_account # 下單帳號
)

# 下單
trade = api.place_order(combo_contracts, combo_order)
trade
"""
