import pandas as pd
import matplotlib.pyplot as plt
# from time import time
import pyarrow as pa
import pyarrow.parquet as pq
import json
# from datetime import datetime

# start=time()
df_OPoi = pd.read_parquet('00.parquet_home/02.STRAT_OPOI.pqt', engine='pyarrow')
df_OPoi['date'] = df_OPoi['date'].astype(str)
# tradeHistory=df_OPoi.iloc[0:2]

class MyPosition:
    def __init__(
        self,
        openPrice=0,
        openContract=0,
        openTaiex=0,
        openDate=0,
        strikePrice=0,
        possibleEarn=0,
        call_put=0,
        strikePrice_another=0,
        on_off=False,
        ):
        self.openPrice=openPrice
        self.openContract=openContract
        self.strikePrice_another=strikePrice_another
        self.openTaiex=openTaiex
        self.openDate=openDate
        self.strikePrice=strikePrice
        self.possibleEarn=possibleEarn
        self.call_put=call_put
        self.on_off=on_off

class MyEquity:
    def __init__(
        self,
        totalEquity=[0],
        maxDrawDown=[0],
        equityDelta=[0],
        equityDate=[0],
        taiexEquity=[0],
        tempData_1=0,
        tempData_list=[[0,0,0,0,0,0,0,0]],
        tempData_2=0,
        tempTaiex_1=0,
        massiveLotStrikePrice=[0],

        ):
        self.totalEquity=totalEquity
        self.maxDrawDown=maxDrawDown
        self.equityDelta=equityDelta
        self.equityDate=equityDate
        self.tempData_1=tempData_1
        self.tempData_list=tempData_list
        self.tempData_2=tempData_2
        self.tempTaiex_1=tempTaiex_1
        self.taiexEquity=taiexEquity
        self.massiveLotStrikePrice=massiveLotStrikePrice
position1=MyPosition()
equity1=MyEquity()
call_put_switch='call'
spreadNumVar=100
OI_switch=8000
price_switch_up_call=20
price_switch_down=price_switch_up_call*0.7
tempTaiex_1=df_OPoi['TAIEX_close'].iloc[0:2]
charge=2
tempDate_sell,tempDate_call=0,0
for i in range(0,len(df_OPoi['date'])):
    try:
        if position1.on_off ==False and df_OPoi['open_interest'].iloc[i] >= OI_switch and df_OPoi['OP_close'].iloc[i]< price_switch_up_call and df_OPoi['OP_close'].iloc[i]> price_switch_down and df_OPoi['call_put'].iloc[i]==call_put_switch: # and df_OPoi['contract_date'].iloc[i] != ('202003W4' or '202101W2'):
            #建倉
            position1 = MyPosition(
                on_off=True,
                openPrice = df_OPoi['OP_close'].iloc[i],
                strikePrice = df_OPoi['strike_price'].iloc[i],
                call_put = call_put_switch,
                openDate = df_OPoi['date'].iloc[i],
                openTaiex = df_OPoi['TAIEX_close'].iloc[i],
                openContract = df_OPoi['contract_date'].iloc[i],
                )
            # print(position1.openPrice)
            

            try:
                if position1.call_put=='call':
                    position1.strikePrice_another = position1.strikePrice+spreadNumVar
                if position1.call_put=='put':
                    position1.strikePrice_another = position1.strikePrice-spreadNumVar
                
                anotherOPEN=df_OPoi[
                    (df_OPoi['strike_price'] == position1.strikePrice_another) & 
                    (df_OPoi['date']==position1.openDate) &
                    (df_OPoi['call_put']==position1.call_put)
                    ]['OP_close'].values[0]
                position1.possibleEarn=position1.openPrice - anotherOPEN
                if position1.possibleEarn>spreadNumVar:
                    position1=MyPosition()
                    print('跳過不開倉',position1.openDate)
                    continue
                    #跳過這筆奇怪的交易

                # tradeHistory = tradeHistory.append(df_OPoi.iloc[i])
                tempDate=df_OPoi['date'].iloc[i]
                # tradeHistory=tradeHistory.append(df_OPoi.iloc[i])
                #交易紀錄填寫
                equity1.tempData_list.append([position1.openContract,0,0,0,0,0,0,0])
                equity1.tempData_list[-1][1]=position1.openDate
                equity1.tempData_list[-1][2]=position1.openPrice
                equity1.tempData_list[-1][3]=anotherOPEN
                equity1.tempData_list[-1][4]=position1.strikePrice
                equity1.tempData_list[-1][5]=position1.strikePrice_another
                equity1.tempData_list[-1][6]="open_contract"
                equity1.tempData_list[-1][7]=equity1.totalEquity[-1]
                # equity1.tempData_2_list.append(anotherOPEN)
                #紀錄建倉倉價格

            except:
                #阿就挑食咩，只做50點
                position1=MyPosition()
                pass
            #看一下建倉成果
            # print(json.dumps(vars(position1), sort_keys=True, indent=4))
    except:
        print('\n問題出在第',i,'列 前往parquet查看一下')
    if position1.on_off ==True  and df_OPoi['call_put'].iloc[i] == position1.call_put :
        # 如果有倉，且這個日期還沒取過價格，那麼就進來取這天的OP價
        #and df_OPoi['date'].iloc[i] != tempDate
        if df_OPoi['strike_price'].iloc[i] == position1.strikePrice_another:
            # 如果掃描到買方部分的價位，看他收盤價多少
            equity1.tempData_1=df_OPoi['OP_close'].iloc[i]
            temp_i_buy=i
            tempDate_call=df_OPoi['date'].iloc[i]
        if df_OPoi['strike_price'].iloc[i] == position1.strikePrice:
            # 如果掃描到賣方部分的價位，看他收盤價多少
            equity1.tempData_2=df_OPoi['OP_close'].iloc[i]

            tempDate=df_OPoi['date'].iloc[i]
            # OK這個日期已經取完報價了
            tempDate_sell=df_OPoi['date'].iloc[i]
            tempTaiex_1=df_OPoi['TAIEX_close'].iloc[i]
            #更新一下加權指數價格，之後畫圖時要用
            temp_i_sell=i
    if position1.on_off ==True and ((df_OPoi['current_contract'].iloc[i] != position1.openContract) or (tempDate_call==tempDate_sell and (equity1.tempData_2-equity1.tempData_1<5 or equity1.tempData_2-equity1.tempData_1>spreadNumVar))):# or equity1.tempData_1-equity1.tempData_2<5)  :
        # 如果有倉，而且出現新的周選契約，那麼就將之前的倉位平倉
        # print('平倉',equity1.tempData_2-equity1.tempData_1)
        equity1.equityDelta.append(position1.possibleEarn - equity1.tempData_2 + equity1.tempData_1+charge)
        #計算價差變化
        # print(equity1.equityDelta[-1])
        # if equity1.equityDelta[-1]>=position1.possibleEarn+5 or equity1.equityDelta[-1]< position1.possibleEarn-spreadNumVar-5:
            # print(equity1.equityDelta[-1],'是異常的 日期是',equity1.equityDate[-1],' 履約價是 ',position1.strikePrice)
            # equity1.equityDelta.pop()
            # print(equity1.equityDelta[-1],'pop後')
            # equity1.tempData_1_list.pop()
            # position1=myPosition()
            #出現奇怪報價的時候就不要交易了
            # continue
        
        equity1.equityDate.append(tempDate) 
        #填入昨天的日期
        if position1.openDate==equity1.equityDate[-1]:
            #不可以在周三開倉
            position1=MyPosition()
            equity1.equityDelta.pop()
            equity1.tempData_list.pop()
            equity1.equityDate.pop()
            continue
        equity1.totalEquity.append(equity1.totalEquity[-1] + equity1.equityDelta[-1])
        #把計算完成的價差變化放進淨值

        equity1.tempData_list.append([position1.openContract,0,0,0,0,0,0,0])
        equity1.tempData_list[-1][1]=equity1.equityDate[-1]
        equity1.tempData_list[-1][2]=equity1.tempData_1
        equity1.tempData_list[-1][3]=equity1.tempData_2
        equity1.tempData_list[-1][4]=position1.strikePrice
        equity1.tempData_list[-1][5]=position1.strikePrice_another
        equity1.tempData_list[-1][6]="--------close_contract----------"
        equity1.tempData_list[-1][7]=equity1.totalEquity[-1]
        # print(equity1.tempData_1)

        if equity1.equityDelta[-1]<equity1.maxDrawDown[-1]:
            equity1.maxDrawDown.append(equity1.equityDelta[-1])
            #製作MDD

        equity1.taiexEquity.append(tempTaiex_1)
        #記錄一下平倉時的加權指數
        #手上無持倉了
        #觀察一下淨資產
        position1=MyPosition()
        #把倉位紀錄單刷新
        # tradeHistory=tradeHistory.append(df_OPoi.iloc[temp_i_sell])
        # tradeHistory=tradeHistory.append(df_OPoi.iloc[temp_i_buy])
        #交易紀錄
equity1.totalEquity.pop(0) #移除第一個值
equity1.maxDrawDown.pop(0)
equity1.equityDelta.pop(0)
equity1.equityDate.pop(0)
equity1.taiexEquity.pop(0)
equity1.tempData_list.pop(0)
inverseSellCall=[]
for i in range(0, len(equity1.totalEquity)):
    inverseSellCall.append(equity1.totalEquity[i])
df_sellcall = pd.DataFrame(
    {'date': pd.to_datetime(equity1.equityDate).values,
    'sellcallequity': inverseSellCall,
    'sellcallTAIEX': equity1.taiexEquity
    })
#=============================================================
class MyPosition:
    def __init__(
        self,
        openPrice=0,
        openContract=0,
        openTaiex=0,
        openDate=0,
        strikePrice=0,
        possibleEarn=0,
        call_put=0,
        strikePrice_another=0,
        on_off=False,
        ):
        self.openPrice=openPrice
        self.openContract=openContract
        self.strikePrice_another=strikePrice_another
        self.openTaiex=openTaiex
        self.openDate=openDate
        self.strikePrice=strikePrice
        self.possibleEarn=possibleEarn
        self.call_put=call_put
        self.on_off=on_off
class MyEquity:
    def __init__(
        self,
        totalEquity=[0],
        maxDrawDown=[0],
        equityDelta=[0],
        equityDate=[0],
        taiexEquity=[0],
        tempData_1=0,
        tempData_list=[[0,0,0,0,0,0,0,0]],
        tempData_2=0,
        tempTaiex_1=0,
        massiveLotStrikePrice=[0],

        ):
        self.totalEquity=totalEquity
        self.maxDrawDown=maxDrawDown
        self.equityDelta=equityDelta
        self.equityDate=equityDate
        self.tempData_1=tempData_1
        self.tempData_list=tempData_list
        self.tempData_2=tempData_2
        self.tempTaiex_1=tempTaiex_1
        self.taiexEquity=taiexEquity
        self.massiveLotStrikePrice=massiveLotStrikePrice
position2=MyPosition()
equity2=MyEquity()
call_put_switch='put'
spreadNumVar=100
OI_switch=10000
OI_switch2=2000
price_switch_up_put=10
price_switch_down=price_switch_up_put*0.7
tempTaiex_1=df_OPoi['TAIEX_close'].iloc[0:2]
for i in range(0,len(df_OPoi['date'])):
    try:
        if position2.on_off ==False and df_OPoi['open_interest'].iloc[i] <= OI_switch and df_OPoi['open_interest'].iloc[i] >= OI_switch2 and df_OPoi['OP_close'].iloc[i]< price_switch_up_put and df_OPoi['OP_close'].iloc[i]> price_switch_down and df_OPoi['call_put'].iloc[i]==call_put_switch: # and df_OPoi['contract_date'].iloc[i] != ('202003W4' or '202101W2'):
            #建倉
            position2 = MyPosition(
                on_off=True,
                openPrice = df_OPoi['OP_close'].iloc[i],
                strikePrice = df_OPoi['strike_price'].iloc[i],
                call_put = call_put_switch,
                openDate = df_OPoi['date'].iloc[i],
                openTaiex = df_OPoi['TAIEX_close'].iloc[i],
                openContract = df_OPoi['contract_date'].iloc[i],
                )
            # print(position2.openPrice)
            # print(equity2.totalEquity[-1])

            try:
                if position2.call_put=='call':
                    position2.strikePrice_another = position2.strikePrice+spreadNumVar
                if position2.call_put=='put':
                    position2.strikePrice_another = position2.strikePrice-spreadNumVar
                
                anotherOPEN=df_OPoi[
                    (df_OPoi['strike_price'] == position2.strikePrice_another) & 
                    (df_OPoi['date']==position2.openDate) &
                    (df_OPoi['call_put']==position2.call_put)
                    ]['OP_close'].values[0]
                position2.possibleEarn=position2.openPrice - anotherOPEN
                if position2.possibleEarn>spreadNumVar:
                    position2=MyPosition()
                    print('跳過不開倉',position2.openDate)
                    continue
                    #跳過這筆奇怪的交易

                # tradeHistory = tradeHistory.append(df_OPoi.iloc[i])
                tempDate=df_OPoi['date'].iloc[i]
                # tradeHistory=tradeHistory.append(df_OPoi.iloc[i])
                #交易紀錄填寫
                equity2.tempData_list.append([position2.openContract,0,0,0,0,0,0,0])
                equity2.tempData_list[-1][1]=position2.openDate
                equity2.tempData_list[-1][2]=position2.openPrice
                equity2.tempData_list[-1][3]=anotherOPEN
                equity2.tempData_list[-1][4]=position2.strikePrice
                equity2.tempData_list[-1][5]=position2.strikePrice_another
                equity2.tempData_list[-1][6]="open_contract"
                equity2.tempData_list[-1][7]=equity2.totalEquity[-1]
                # equity2.tempData_2_list.append(anotherOPEN)
                #紀錄建倉倉價格

            except:
                #阿就挑食咩，只做50點
                position2=MyPosition()
                pass
            #看一下建倉成果
            # print(json.dumps(vars(position2), sort_keys=True, indent=4))
    except:
        print('\n問題出在第',i,'列 前往parquet查看一下')
    if position2.on_off ==True  and df_OPoi['call_put'].iloc[i] == position2.call_put :
        # 如果有倉，且這個日期還沒取過價格，那麼就進來取這天的OP價
        #and df_OPoi['date'].iloc[i] != tempDate
        if df_OPoi['strike_price'].iloc[i] == position2.strikePrice_another:
            # 如果掃描到買方部分的價位，看他收盤價多少
            equity2.tempData_1=df_OPoi['OP_close'].iloc[i]
            temp_i_buy=i
            tempDate_call=df_OPoi['date'].iloc[i]

        if df_OPoi['strike_price'].iloc[i] == position2.strikePrice:
            # 如果掃描到賣方部分的價位，看他收盤價多少
            equity2.tempData_2=df_OPoi['OP_close'].iloc[i]

            tempDate=df_OPoi['date'].iloc[i]
            # OK這個日期已經取完報價了
            tempDate_sell=df_OPoi['date'].iloc[i]
            
            tempTaiex_1=df_OPoi['TAIEX_close'].iloc[i]
            #更新一下加權指數價格，之後畫圖時要用
            temp_i_sell=i

    if position2.on_off ==True and (df_OPoi['current_contract'].iloc[i] != position2.openContract or (tempDate_call==tempDate_sell and (equity2.tempData_2-equity1.tempData_1<2 or equity2.tempData_2-equity2.tempData_1>spreadNumVar))) :
        # 如果有倉，而且出現新的周選契約，那麼就將之前的倉位平倉

        equity2.equityDelta.append(position2.possibleEarn - equity2.tempData_2 + equity2.tempData_1+charge)
        #計算價差變化
        # print(equity2.equityDelta[-1])
        equity2.equityDate.append(tempDate) 
        #填入昨天的日期
        if position2.openDate==equity2.equityDate[-1]:
            #不可以在周三開倉啦
            position2=MyPosition()
            equity2.equityDelta.pop()
            equity2.tempData_list.pop()
            equity2.equityDate.pop()
            continue

        equity2.totalEquity.append(equity2.totalEquity[-1] + equity2.equityDelta[-1])
        #把計算完成的價差變化放進淨值


        equity2.tempData_list.append([position2.openContract,0,0,0,0,0,0,0])
        equity2.tempData_list[-1][1]=equity2.equityDate[-1]
        equity2.tempData_list[-1][2]=equity2.tempData_1
        equity2.tempData_list[-1][3]=equity2.tempData_2
        equity2.tempData_list[-1][4]=position2.strikePrice
        equity2.tempData_list[-1][5]=position2.strikePrice_another
        equity2.tempData_list[-1][6]="--------close_contract----------"
        equity2.tempData_list[-1][7]=equity2.totalEquity[-1]
        # print(equity2.tempData_1)

        if equity2.equityDelta[-1]<equity2.maxDrawDown[-1]:
            equity2.maxDrawDown.append(equity2.equityDelta[-1])
            #製作MDD

        equity2.taiexEquity.append(tempTaiex_1)
        #記錄一下平倉時的加權指數
        #手上無持倉了
        #觀察一下淨資產
        position2=MyPosition()
        #把倉位紀錄單刷新
        # tradeHistory=tradeHistory.append(df_OPoi.iloc[temp_i_sell])
        # tradeHistory=tradeHistory.append(df_OPoi.iloc[temp_i_buy])
        #交易紀錄
equity2.totalEquity.pop(0) #移除第一個值
equity2.maxDrawDown.pop(0)
equity2.equityDelta.pop(0)
equity2.equityDate.pop(0)
equity2.taiexEquity.pop(0)
equity2.tempData_list.pop(0)

# ax1[1].ylim(top = min(tradeHistory['OP_close']))res_list = []
""" sellcall_list=[]
for i in range(0, len(equity1.taiexEquity)):
    sellcall_list.append(equity1.taiexEquity[i] - equity1.totalEquity[i]*10)
sellput_list=[]
for i in range(0, len(equity2.taiexEquity)):
    sellput_list.append(equity2.taiexEquity[i] - equity2.totalEquity[i]*10) """
# inverseSellput=equity2.totalEquity
# for i in range(0, len(equity2.totalEquity)):
    # inverseSellput.append(0-equity2.totalEquity[i])

df_sellput = pd.DataFrame({
    'date': pd.to_datetime(equity2.equityDate).values,
    'sellputequity': equity2.totalEquity,
    'sellputTAIEX': equity2.taiexEquity
    })
# df_sellput.to_csv('07.sellputequity怎麼了.csv')
# print(call_put_switch)
# print(df_sellput.iloc[:20])

# df_sellcallput = pd.concat([df_sellcall,df_sellput], join='outer',) #交集為Inner
# df_sellcallput=pd.merge(df_sellcall,df_sellput,how='outer', on='date')#, right_on=df_sellput['date'])
df_sellcallput_onlydate=pd.merge(df_sellput['date'],df_sellcall['date'],how='outer')#, on=df_sellcall['date'])#, right_on=df_sellput['date'])
df_sellcallput_onlydate = df_sellcallput_onlydate.drop_duplicates(subset=["date"], keep='first')
df_sellcallput_onlydate=df_sellcallput_onlydate.sort_values(by='date')
df_sellcallput_onlydate.to_csv('07.雙向單的日期.csv')

# df_sellcallput=pd.merge(pd.merge(df_sellcallput_onlydate,df_sellcall,left_on='date'),df_sellput,left_on='date')  
df_sellcallput=pd.DataFrame(df_sellcallput_onlydate,columns=['date','sellcallequity','sellputequity','TAIEX','Final_equity'])
df_sellcallput=pd.concat(
    [pd.DataFrame([[0]*len(df_sellcallput.columns)],
                columns=['date','sellcallequity','sellputequity','TAIEX','Final_equity']),
    df_sellcallput]
    ).reset_index(drop=True)
df_sellcallput=df_sellcallput.fillna(0)
# df_sellcallput['date']=df_sellcallput_onlydate['date'].values
# df_sellcallput.to_csv('07.op雙向互補明細.csv')
df_sellcallput['date'].iloc[1:] = df_sellcallput['date'].iloc[1:].astype('datetime64[ns]')


for i, date in enumerate(df_sellcallput_onlydate['date'].values):
    i=i+1
    # print(df_sellput.iloc[i])
    
    try:
        df_sellcallput['sellcallequity'].iloc[i]=df_sellcall.loc[df_sellcall['date']==date]['sellcallequity'].values[0]
        df_sellcallput['TAIEX'].iloc[i]=df_sellcall.loc[df_sellcall['date']==date]['sellcallTAIEX'].values[0].copy()
    except:
        df_sellcallput['sellcallequity'].iloc[i]=df_sellcallput['sellcallequity'].iloc[i-1]
    # print(df_sellcallput.iloc[i])
    
    try:
        df_sellcallput['sellputequity'].iloc[i]=df_sellput.loc[df_sellput['date']==date]['sellputequity'].values[0]
        df_sellcallput['TAIEX'].iloc[i]=df_sellput.loc[df_sellput['date']==date]['sellputTAIEX'].values[0].copy()
    except:
        df_sellcallput['sellputequity'].iloc[i]=df_sellcallput['sellputequity'].iloc[i-1]
    # print(df_sellcallput.iloc[i])

#buycal也buyput
df_sellcallput['Final_equity'] = df_sellcallput.apply(lambda x: 0-x['sellcallequity'] - x['sellputequity'], axis=1)
df_sellcallput['date'].iloc[0]='2013-01-01'
df_sellcallput['TAIEX'].iloc[0]=7500
df_sellcallput['date']=pd.to_datetime(df_sellcallput['date']).values
# df_sellcallput=df_sellcallput.sort_values(by='date')
df_sellcallput['Final_equity']=df_sellcallput['Final_equity'].astype('float64')
df_sellcallput.to_csv('07.op雙向互補明細.csv')

fig,ax1=plt.subplots(2,1)
plottingDate=pd.to_datetime(df_sellcallput['date']).values

ax1[0].plot(plottingDate,df_sellcallput['sellcallequity'],color='red')
ax2 = ax1[0].twinx()
ax2.plot(plottingDate,df_sellcallput['sellputequity'])
ax1[0].grid(color = 'grey', linestyle = '--', linewidth = 1,axis='both')

ax2_2=ax2.twinx()
ax2_2.plot(plottingDate,df_sellcallput['TAIEX'],color='black')

titleTemp=''.join([str(spreadNumVar),' spread sell call',str(price_switch_up_call),' and put ',str(price_switch_up_put)])
ax2.set_title(titleTemp)

ax1[1].plot(plottingDate,df_sellcallput['Final_equity'].values,color='darkviolet')
ax1[1].grid(color = 'grey', linestyle = '--', linewidth = 1,axis='both')
ax3 = ax1[1].twinx()
ax3.plot(plottingDate,df_sellcallput['TAIEX'],color='black')

#ax3.bar(x=pd.to_datetime(tradeHistory['date']),height=tradeHistory['OP_close'],bottom=0,width = 2,color='limegreen')
#ax3.bar(x=pd.to_datetime(equity1.equityDate),height=equity1.equityDelta,bottom=0,width = 2,color=['tomato' if y<0 else 'lime' for y in equity1.equityDelta])
# ax3.axis(ymin=min(equity1.equityDelta),ymax=max(equity1.equityDelta))
# ax3.invert_yaxis()
plt.tight_layout() #讓X軸文字不要出格

plt.subplots_adjust(left=0.05,
                    bottom=0.04,
                    right=0.95,
                    top=0.96,
                    wspace=0.4,
                    hspace=0.07)

plt.show()
'''
equityFILE=json.dumps(vars(equity1), sort_keys=True, indent=4)
with open("07.op避險策略.json", "w") as outfile:
    outfile.write(equityFILE)
'''
