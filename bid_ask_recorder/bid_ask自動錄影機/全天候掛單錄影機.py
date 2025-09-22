from datetime import datetime

now = datetime.now()
if 14 <= now.hour <= 23 or 0 <= now.hour < 4 or 8 <= now.hour < 13:
    print("期貨交易時段")
    if 49 <= now.minute <= 59:
        print("需要啟動錄影")
        from files_to_exec.sj_ib共同運作一小時存檔 import *

# from files_to_exec.sj_udf一小時存檔 import *

# from files_to_exec.ibapi_mym一小時存檔 import *
