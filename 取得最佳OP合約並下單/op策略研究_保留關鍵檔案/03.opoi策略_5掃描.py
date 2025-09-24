import pandas as pd
import matplotlib.pyplot as plt
from time import time
import json

start=time()
df_OPoi = pd.read_parquet('00.parquet_home/02.STRAT_OPOI.pqt', engine='pyarrow')
fig,ax1=plt.subplots(2,3)

call_put_switch='call'
# OI_switch=[10000,10000,10000,10000,10000,10000]
price_switch_up=[160,150,140,130,120,110]#[40,30,20,15,10,5]#[65,60,55,50,45,40]#[90,85,80,75,70,65]##[110,80,50,25,10,5] #[300,250,200,150,100,50]
# price_switch_down=[80,80,80,80,80,80,80,80,80,80,80,80]
for i_manyplot in range(6):
    OI_switch_var= 10000#OI_switch[i_manyplot]

    class myPosition:
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

    class myEquity:
        def __init__(
            self,
            totalEquity=[0],
            maxDrawDown=[0],
            equityDelta=[0],
            equityDate=[0],
            taiexEquity=[0],
            tempData_1=0,
            tempData_2=0,
            tempTaiex_1=0,

        ):
            self.totalEquity=totalEquity
            self.maxDrawDown=maxDrawDown
            self.equityDelta=equityDelta
            self.equityDate=equityDate
            self.tempData_1=tempData_1
            self.tempData_2=tempData_2
            self.tempTaiex_1=tempTaiex_1
            self.taiexEquity=taiexEquity


    position1=myPosition()
    equity1=myEquity()
    # equity1.totalEquity.append(0) #入金0元 :)
    if i_manyplot==0:
        ax1_var=ax1[0,0]
    if i_manyplot==1:
        ax1_var=ax1[0,1]
    if i_manyplot==2:
        ax1_var=ax1[0,2]
    if i_manyplot==3:
        ax1_var=ax1[1,0]
    if i_manyplot==4:
        ax1_var=ax1[1,1]
    if i_manyplot==5:
        ax1_var=ax1[1,2]


    price_switch_up_var=price_switch_up[i_manyplot]
    price_switch_down_var=price_switch_up_var*0.8
    tempTaiex_1=df_OPoi['TAIEX_close'].iloc[0]
    for i in range(len(df_OPoi['date'])):
        if position1.on_off ==False and df_OPoi['open_interest'].iloc[i] >= OI_switch_var and df_OPoi['OP_close'].iloc[i]< price_switch_up_var and df_OPoi['OP_close'].iloc[i]> price_switch_down_var and df_OPoi['call_put'].iloc[i]==call_put_switch: # and df_OPoi['contract_date'].iloc[i] != ('202003W4' or '202101W2'):
            #建倉
            position1 = myPosition(
                on_off=True,
                openPrice = df_OPoi['OP_close'].iloc[i],
                strikePrice = df_OPoi['strike_price'].iloc[i],
                call_put = df_OPoi['call_put'].iloc[i],
                openDate = df_OPoi['date'].iloc[i],
                openTaiex = df_OPoi['TAIEX_close'].iloc[i],
                openContract = df_OPoi['contract_date'].iloc[i],            
                )
            # print('建倉sell put 開倉價位',position1.openPrice,'==============')
            # print('履約價:',df_OPoi['strike_price'].iloc[i])
            # print('建倉日期',position1.openDate)
            # print('建倉淨值',round(equity1.totalEquity[-1],2))
            tempDate=df_OPoi['date'].iloc[i]
            try:
                if position1.call_put=='call':
                    position1.strikePrice_another = position1.strikePrice+150
                if position1.call_put=='put':
                    position1.strikePrice_another = position1.strikePrice-150
                position1.possibleEarn=position1.openPrice - df_OPoi[
                    (df_OPoi['strike_price'] == position1.strikePrice_another) & 
                    (df_OPoi['date']==position1.openDate) &
                    (df_OPoi['call_put']==position1.call_put)
                    ]['OP_close'].values[0]
            except:
                try:
                    if position1.call_put=='call':
                        position1.strikePrice_another = position1.strikePrice+100
                    if position1.call_put=='put':
                        position1.strikePrice_another = position1.strikePrice-100
                    position1.possibleEarn=position1.openPrice - df_OPoi[
                        (df_OPoi['strike_price'] == position1.strikePrice_another) & 
                        (df_OPoi['date']==position1.openDate) &
                        (df_OPoi['call_put']==position1.call_put)
                        ]['OP_close'].values[0]
                except:
                    try:
                        if position1.call_put=='call':
                            position1.strikePrice_another = position1.strikePrice+50
                        if position1.call_put=='put':
                            position1.strikePrice_another = position1.strikePrice-50
                        position1.possibleEarn=position1.openPrice - df_OPoi[
                            (df_OPoi['strike_price'] == position1.strikePrice_another) & 
                            (df_OPoi['date']==position1.openDate) &
                            (df_OPoi['call_put']==position1.call_put)
                            ]['OP_close'].values[0]
                    except:
                        pass
            #看一下建倉成果
            # print(json.dumps(vars(position1), sort_keys=True, indent=4))
        

        if position1.on_off ==True  and df_OPoi['date'].iloc[i] != tempDate and df_OPoi['call_put'].iloc[i] == position1.call_put :
            # 如果有倉，且這個日期還沒取過價格，那麼就進來取這天的OP價        
            if df_OPoi['strike_price'].iloc[i] == position1.strikePrice_another:
                # 如果掃描到買方部分的價位，看他收盤價多少
                equity1.tempData_1=df_OPoi['OP_close'].iloc[i]
            if df_OPoi['strike_price'].iloc[i] == position1.strikePrice:
                # 如果掃描到賣方部分的價位，看他收盤價多少
                equity1.tempData_2=df_OPoi['OP_close'].iloc[i]
                tempDate=df_OPoi['date'].iloc[i]
                # OK這個日期已經取完報價了
                tempTaiex_1=df_OPoi['TAIEX_close'].iloc[i]
                #更新一下加權指數價格，之後畫圖時要用
                # print('平倉sell put 平倉價位',df_OPoi['OP_close'].iloc[i])
                # print('平倉日期',df_OPoi['date'].iloc[i])
                # print('平倉淨值',round(equity1.totalEquity[-1],2))
        if position1.on_off ==True and df_OPoi['current_contract'].iloc[i] != position1.openContract :
            # 如果有倉，而且出現新的周選契約，那麼就將之前的倉位平倉
            equity1.equityDate.append(tempDate) 
            #填入昨天的日期
            equity1.equityDelta.append(position1.possibleEarn - equity1.tempData_2 + equity1.tempData_1)
            #計算價差變化
            equity1.totalEquity.append(equity1.totalEquity[-1] + equity1.equityDelta[-1])
            #把計算完成的價差變化放進淨值
            if equity1.equityDelta[-1]<equity1.maxDrawDown[-1]:
                equity1.maxDrawDown.append(equity1.equityDelta[-1])
                #製作MDD
            equity1.taiexEquity.append(tempTaiex_1)
            #記錄一下平倉時的加權指數
            #position1.on_off=False
            #手上無持倉了
            #觀察一下淨資產
            position1=myPosition()
            #把倉位紀錄單刷新
    # print(time()-start) 
    equity1.totalEquity.pop(0)
    equity1.maxDrawDown.pop(0)
    equity1.equityDelta.pop(0)
    equity1.equityDate.pop(0)
    equity1.taiexEquity.pop(0)
    # print(json.dumps(vars(equity1), sort_keys=True, indent=4))


    #fig, ax1 = plt.subplots()
    ax1_var.plot(equity1.equityDate,equity1.totalEquity,color='red')
    #plt.plot(equity1.equityDate,equity1.totalEquity,color='red')
    # plt.set_xticks([])
    # plt.xticks(rotation = 90)
    ax2 = ax1_var.twinx()
    ax2.plot(equity1.equityDate,equity1.taiexEquity)
    #plt.plot(equity1.equityDate,equity1.taiexEquity)
    #ax1_var.tick_params(bottom=False,top=False,labelbottom=False,axis="x",which='both')
    #plt.xticks(rotation = 90)
    ax2.grid(color = 'grey', linestyle = '--', linewidth = 1,axis='both')
    #plt.grid(color = 'grey', linestyle = '--', linewidth = 1,axis='both')
    titleTemp=''.join(['sell ',call_put_switch,' at ',str(OI_switch_var),' lot ',str(price_switch_up_var),'and ',str(price_switch_down_var)])
    ax1_var.set_title(titleTemp)
    #plt.title(titleTemp)
    #plt.tight_layout() #讓X軸文字不要出格
plt.show()


