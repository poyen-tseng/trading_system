import pandas as pd
import yfinance as yf
import requests
import os
lastTradeDate=yf.download(tickers='2330.TW', period='3d',interval='1d')

# firstNewDate='2023-08-17'
firstNewDate=str(lastTradeDate.index.date[-1])
# print(firstNewDate)
url = ''.join(['https://iwarrant.capital.com.tw/wdataV2/canonical/capital-newvol/%E6%AC%8A%E8%AD%89%E9%81%94%E4%BA%BA%E5%AF%B6%E5%85%B8_NEWVOL_',firstNewDate,'.xls?4750217'])
r = requests.get(url, allow_redirects=True)
if r.headers['Content-Type']=='application/vnd.ms-excel':
    warrantFileName=''.join(['02.warrant_home/02.',firstNewDate,'當日的權證資料.xls'])
    open(warrantFileName, 'wb').write(r.content)
else:
    #若這天的資料還沒出來
    firstNewDate=str(lastTradeDate.index.date[-2])
    url = ''.join(['https://iwarrant.capital.com.tw/wdataV2/canonical/capital-newvol/%E6%AC%8A%E8%AD%89%E9%81%94%E4%BA%BA%E5%AF%B6%E5%85%B8_NEWVOL_',firstNewDate,'.xls?4750217'])
    r = requests.get(url, allow_redirects=True)
    if r.headers['Content-Type']=='application/vnd.ms-excel':
        warrantFileName=''.join(['02.warrant_home/02.',firstNewDate,'當日的權證資料.xls'])
        open(warrantFileName, 'wb').write(r.content)
    else:
        #這天的資料也是還沒出來
        firstNewDate=str(lastTradeDate.index.date[-3])
        url = ''.join(['https://iwarrant.capital.com.tw/wdataV2/canonical/capital-newvol/%E6%AC%8A%E8%AD%89%E9%81%94%E4%BA%BA%E5%AF%B6%E5%85%B8_NEWVOL_',firstNewDate,'.xls?4750217'])
        r = requests.get(url, allow_redirects=True)
        if r.headers['Content-Type']=='application/vnd.ms-excel':
            warrantFileName=''.join(['02.warrant_home/02.',firstNewDate,'當日的權證資料.xls'])
            open(warrantFileName, 'wb').write(r.content)
        else:
            #怪怪怪
            print('權證達人寶典沒有近三天的資料')
            os.system("pause")


