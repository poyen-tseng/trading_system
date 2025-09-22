# dad_account_alert
# 功能
- 期貨風險指標過低，於TG發布警示
- 在AWS香港使用cron排程呼叫
- 預防永豐伺服器陣亡，登入失敗會新登入，重試{try_count}次
- 每個小時都檢查
- 每次檢查都在google sheet紀錄風險警示
