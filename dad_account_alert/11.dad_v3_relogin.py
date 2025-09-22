import shioaji as sj
from datetime import datetime
import requests
import pygsheets
from google.oauth2 import service_account
import json
import time


def send_line_notify(message):
    line_權杖token = CP_risk_set_page.cell("B5").value
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {line_權杖token}"}
    data = {"message": message}
    response = requests.post(url, headers=headers, data=data)
    return response.status_code


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
    return "".join(
        [
            datetime.today().strftime("%Y/%m/%d "),
            weekday_chinese,
            datetime.today().strftime(" %H:%M:%S "),
        ]
    )


def 風險指標提醒():
    # print(api.usage())
    風險指標建議值 = int(CP_risk_set_page.cell("B1").value)
    風險指標 = int(api.margin(api.futopt_account).risk_indicator)
    # 原始保證金 = int(api.margin(api.futopt_account).initial_margin)
    # 可動用保證金 = int(api.margin(api.futopt_account).available_margin)
    # 建議的可動用保證金 = int(round(原始保證金 * (風險指標建議值 * 0.012 - 1), -2))
    # 建議匯入金額 = int(round(建議的可動用保證金 - 可動用保證金, -3))
    if 風險指標 < 風險指標建議值:
        # Send notification after script execution
        訊息 = f"你的風險指標只有 {風險指標}, 低於理想值 {風險指標建議值} "
        status_code = send_line_notify(訊息)
        data_to_insert = [nowTime_poyen_format(), 風險指標, 風險指標建議值, "觸發"]
        CP_risk_set_page.insert_rows(row=7, number=1, values=data_to_insert)
    else:
        data_to_insert = [nowTime_poyen_format(), 風險指標, 風險指標建議值, ""]
        CP_risk_set_page.insert_rows(row=7, number=1, values=data_to_insert)


def 期貨到期提醒():
    所有持有期權 = api.list_positions(api.futopt_account)
    即期商品 = {}
    for 持有期權 in 所有持有期權:
        商品資料 = api.Contracts.Futures[持有期權.code]
        today = datetime.today()  # 取得今天的日期
        商品到期日 = 商品資料.delivery_date  # 取得商品到期日
        商品到期日 = datetime.strptime(商品到期日, "%Y/%m/%d")  # 日期格式parse
        剩餘天數 = (商品到期日 - today).days  # 計算剩餘天數
        if 剩餘天數 < 10:
            即期商品[商品資料.name] = 剩餘天數
    if 即期商品:  # 當dict為空 相當於false
        訊息 = ""
        訊息 = "".join([訊息, "\n以下期貨即將到期，記得換倉\n"])
        for key, value in 即期商品.items():
            訊息 = "".join([訊息, f"{value}天  {key}\n"])
        send_line_notify(訊息)


if __name__ == "__main__":
    # Your script logic here
    # ...
    credentials_info = {
        "GITHUB隱藏重要資訊",
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
    # 選取by名稱
    CP_risk_set_page = sheet.worksheet_by_title("CP期貨警示")
    CP_risk_set_page_api_key = CP_risk_set_page.cell("B3").value
    CP_risk_set_page_secret_key = CP_risk_set_page.cell("B4").value

    try_counts = 3
    for try_count in reversed(range(try_counts)):
        api = sj.Shioaji(simulation=False)  # 模擬模式
        try:
            # 登入一次10M
            account = api.login(
                api_key=CP_risk_set_page_api_key,  # 請修改此處
                secret_key=CP_risk_set_page_secret_key,  # 請修改此處
                contracts_timeout=30000,
                receive_window=60000,
            )
        except:
            print(f"登入失敗 並還有{try_count}次嘗試")
            time.sleep(5)
            continue

        風險指標提醒()
        # 取得現在的時間
        # 判斷時間是否介於早上7點到12點之間(可交易時間)
        if 7 <= datetime.now().hour < 14:
            期貨到期提醒()

        api.logout()
        break
