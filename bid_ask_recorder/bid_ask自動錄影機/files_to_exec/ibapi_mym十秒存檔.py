from poyen.ibapi_poyen import *
import pandas as pd
from datetime import datetime

ib_result_arr = {
    "datetime": [],
    "bid_price": [],
    "ask_price": [],
}

datetime_temp = None


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


app = IBapi()
app.poyen_connect(7497, 3)

mnq_contract = app.poyen_future_contract("MYM", "CBOT", "202412")
app.poyen_setcallback(ib_save2dataframe)
app.poyen_subscribe(1, mnq_contract)
time.sleep(10)  # Sleep interval to allow time for incoming price data
# print(result_arr)
ib_result_df = pd.DataFrame(ib_result_arr)
fileTime = datetime.today().strftime("%Y-%m-%d--%H-%M-%S")

ib_result_df.to_parquet(f"datas/{fileTime}_ib_mym存檔.pqt")
app.disconnect()
