# bid_ask_recorder

## 功能
- 在AWS Taipei錄製兩個市場的造市資訊  
- 改寫ibapi，比較方便使用  
- 只需要簡短的程式碼就能啟動錄製功能，儲存為parquet格式，作為後續觀察分析  

## 程式結構：
1. 由全天候掛單錄影機.py啟動"files_to_exec"裡面的其中一種錄影方式，該錄影方式會進去poyen資料夾尋找改裝過的ibapi進行呼叫
2. 錄影方式首選"sj_ib共同運作"，同時錄製台美兩個市場
3. 自動將錄製完成的parquet儲存在"datas"資料夾
