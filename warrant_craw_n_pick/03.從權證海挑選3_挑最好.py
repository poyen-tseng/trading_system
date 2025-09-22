import pandas as pd
import yfinance as yf
import requests
import os

def warrantChooser(股號,認購認售):
    warrantOK=warrantData[
        (warrantData['標的代碼'] == 股號) & 
        (warrantData['認購/售類別'] == 認購認售) 
        ]
    待排序最佳價格=warrantOK['權證價格']
    已排序最佳價格=sorted(待排序最佳價格,key=lambda x: abs(x-3.2))
    最優價格前10名=已排序最佳價格[0:10]
    print('最優價格前十名=',最優價格前10名)
    warrantOK=warrantOK[
        (warrantData['權證價格'].isin(最優價格前10名)) 
        # (warrantData['認購/售類別'] == 認購認售) 
        ]
    warrantOK=warrantOK.sort_values(by=['內涵價值','有效槓桿'], ascending=False)
    return warrantOK

"""
lastTradeDate=yf.download(tickers='2330.TW', period='3d',interval='1d')
firstNewDate=str(lastTradeDate.index.date[-1])
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
"""

warrantData=pd.read_excel('02.warrant_home/02.2023-08-16當日的權證資料.xls')

warrantData.rename(columns = {
    '日期：':'權證代碼',
    '2023-08-16 00:00:00':'權證名稱',
    'Unnamed: 2':'發行券商',
    '[權證]  基本資料 / 交易資訊':'權證價格',
    'Unnamed: 4':'權證漲跌',
    'Unnamed: 5':'權證漲跌幅',
    'Unnamed: 6':'權證成交量',
    'Unnamed: 7':'權證買價',
    'Unnamed: 8':'權證賣價',
    'Unnamed: 9':'權證買賣價差',
    'Unnamed: 10':'溢價比率',
    'Unnamed: 11':'價內價外',
    'Unnamed: 12':'理論價格',
    'Unnamed: 13':'隱含波動率',
    'Unnamed: 14':'有效槓桿',
    'Unnamed: 15':'剩餘天數',
    'Unnamed: 16':'最新行使比例',
    'Unnamed: 17':'標的代碼',
    'Unnamed: 18':'標的名稱',
    'Unnamed: 19':'標的價格',
    'Unnamed: 20':'標的漲跌',
    'Unnamed: 21':'標的漲跌幅',
    'Unnamed: 22':'最新履約價',
    'Unnamed: 23':'最新界限價',
    'Unnamed: 24':'標的20日波動率',
    'Unnamed: 25':'標的60日波動率',
    'Unnamed: 26':'標的120日波動率',
    'Unnamed: 27':'權證DELTA',
    'Unnamed: 28':'權證GAMMA',
    'Unnamed: 29':'權證VEGA',
    'Unnamed: 30':'權證THETA',
    'Unnamed: 31':'內涵價值',
    'Unnamed: 32':'時間價值',
    'Unnamed: 33':'流通在外估計張數',
    'Unnamed: 34':'流通在外增減張數',
    'Unnamed: 35':'上市日期',
    'Unnamed: 36':'到期日期',
    'Unnamed: 37':'最新發行量',
    'Unnamed: 38':'權證發行價',
    'Unnamed: 39':'認購/售類別',
}, inplace = True)
dropBefore=warrantData[warrantData['標的代碼']=='1101'].index[0]
# print(dropBefore)
warrantData.drop(warrantData.index[0:dropBefore], inplace = True) 
# warrantData=warrantData.drop(warrantData[warrantData['隱含波動率'] =='-'].index, inplace = True)
warrantData.drop(warrantData[warrantData['權證價格'] <= 0.9].index, inplace = True)
warrantData.drop(warrantData[warrantData['發行券商'].isin(['統一','康和','兆豐','永豐金','國泰','中國信託','台新','國票'])].index, inplace = True)
warrantData.drop(warrantData[warrantData['剩餘天數'] <= 20].index, inplace = True)
warrantData.drop(warrantData[warrantData['價內價外'] == '-'].index, inplace = True)
warrantData.drop(warrantData[warrantData['價內價外'] >= 0.25].index, inplace = True)
warrantData.drop(warrantData[warrantData['有效槓桿'] == '-'].index, inplace = True)
warrantData.drop(warrantData[warrantData['有效槓桿'] >= 10].index, inplace = True)
warrantData.drop(warrantData[(warrantData['有效槓桿'] <= 3.5) & (warrantData['有效槓桿'] >= -2)].index, inplace = True)
warrantData.drop(warrantData[warrantData['隱含波動率'] == '-'].index, inplace = True)
warrantData.drop(warrantData[warrantData['隱含波動率'] >= 0.9].index, inplace = True)
warrantData.drop(warrantData[warrantData['權證THETA'] == '-'].index, inplace = True)
warrantData.drop(warrantData[warrantData['權證THETA'] / warrantData['權證價格'] < -0.018].index, inplace = True)
# print(warrantData.head())

# warrantData.to_excel('02.warrant_home/02.2023-08-16當日的權證資料_修改column.xlsx')
# print(warrantData)
# 待排序最佳價格=warrantData['權證價格']
# print(待排序最佳價格)
# 已排序最佳價格=sorted(待排序最佳價格,key=lambda x: abs(x-3))
# print(已排序最佳價格)
warrantChooser('2308','認購').to_excel('02.warrant_home/03.2454權證OK.xlsx')

