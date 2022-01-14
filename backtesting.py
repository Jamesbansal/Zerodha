import pickle
import datetime
import os
import pandas as pd
dirs=os.listdir('Data\_2021')
ins_data = {}
idx=-1
def closestto(t,data):
    if t[0:2]=='09' or t[0:2]=='10':
        for i in range(20,10,-1):
            t=t[0:3]+str(i)+t[5:]
            if len(data.loc[data.time==t]['open'].values) !=0:
                return data.loc[data.time==t]['open'].values[0]
        for i in range(20,59,1):
            t=t[0:3]+str(i)+t[5:]
            if len(data.loc[data.time==t]['open'].values) !=0:
                return data.loc[data.time==t]['open'].values[0]
        return -1
    else:
        for i in range(10,25,1):
            t=t[0:3]+str(i)+t[5:]
            if len(data.loc[data.time==t]['open'].values) !=0:
                return data.loc[data.time==t]['open'].values[0]
        for i in range(10, 0, -1):
            t = t[0:3] + str(i) + t[5:]
            if len(data.loc[data.time == t]['open'].values) != 0:
                return data.loc[data.time == t]['open'].values[0]
        return -1


def getsma(x,y,data):
    # print(x,y,data)
    sum=0
    till=y-x
    for i in range(y,till,-1):
        sum=sum+data[i]['dayclose']
    sum=sum/x
    return sum
    # print(data.iloc[0].instrument_name,data.loc[data.time==t]['open'].values[0])
def getmax(t,data):
    maxi=0
    for index, row in data.iterrows():
        maxi=max(maxi,row['high'])
        if row['time']>=t:
            break
    return maxi

def getmin(t, data):

    mini = 999999
    for index, row in data.iterrows():
        mini = min(mini, row['low'])
        if row['time'] >= t:
            break
    return mini
        # if data['time']==t:
        #     break
    # for i in data:
    #     if data[i]
    #     def getmin(t, data):
def getclosebt(t,data):
    xyz=pd.DataFrame()
    for index, row in data.iterrows():
        if row['time']>=t:
            return row['close']
        xyz=row
    return xyz['close']



for diridx in dirs:
    idx+=1
    if idx==300:
        break
    data = pd.read_csv("Data\_2021/"+diridx)
    df = pd.DataFrame(data)
    futuredf = df.loc[df['instrument_type'] == 'FUT']
    ins_name = (futuredf.instrument_name.unique())
    ins_name = ins_name + "-I"
    ins_name=list(ins_name)
    # x="NIFTYIT-I"
    # if x in ins_name:
    #     ins_name.remove("NIFTYIT-I")
    ins_values = {}
    for i in ins_name:
        ins_values[i] = futuredf.loc[futuredf.ticker == i]
    # dates=[]
    # for j in ins_values['AXISBANK-I']['time']:
    #     dates.append(j)
    # print(dates)
    # print(len(dates))

    # for i in ins_values:
    #     # print(i, ins_values[i]['time'])
    #     # temp=[]
    #     # for j in ins_values[i]['time']:
    #     #     temp.append(j)
    #     # x=0
    #     # y=0
    #     # while x<len(temp) and y<len(dates):
    #     #     if temp[x]==dates[y]:
    #     #         x+=1
    #     #         y+=1
    #     #     else:
    #             #add dates[y] in ins_values[i]
    #     for j in ins_values[i]:
    #         print(ins_values[i].)
    buytime="15:10:59"
    selltime = "09:20:59"
    for i in ins_values:
        # print(ins_values[i].date.iloc[0])
        # print(max(ins_values[i].high))
        # print(min(ins_values[i].low))
        try :
            val= int(list(ins_data[i].keys())[-1])
            val+=1
            ins_data[i] = {**ins_data[i],
                val: {'date': ins_values[i].datetime.iloc[0][0:10], "dayhigh": max(ins_values[i].high), "daylow": min(ins_values[i].low),'btclose':getclosebt(buytime,ins_values[i]),"bthigh":getmax(buytime,ins_values[i]),"btlow":getmin(buytime,ins_values[i]),
                      "dayopen":ins_values[i].open.iloc[0],"dayclose":ins_values[i].close.iloc[-1],"buyprice":closestto(buytime,ins_values[i]),
                      "sellprice":closestto(selltime,ins_values[i]),"volume":ins_values[i].volume.sum()}}
        except:
            ins_data[i] = {0: {'date': ins_values[i].datetime.iloc[0][0:10], "dayhigh": max(ins_values[i].high),
                                 "daylow": min(ins_values[i].low),"bthigh":getmax(buytime,ins_values[i]),"btlow":getmin(buytime,ins_values[i]),'btclose':getclosebt(buytime,ins_values[i]),
                               "dayopen":ins_values[i].open.iloc[0],"dayclose":ins_values[i].close.iloc[-1],
                               "buyprice":closestto(buytime,ins_values[i]),"sellprice":closestto(selltime,ins_values[i]),"volume":ins_values[i].volume.sum()}}

# for i in ins_data:
#     print(i, ins_data[i])
Totalprofit=0
totalinvested=0
sold=0
pddataall=[]
for i in ins_data:#for each instument
    for j in ins_data[i].keys():#for each day in instrument
        if j>=50:
            latesthigh=ins_data[i][j]['bthigh']
            latestlow=ins_data[i][j]['btlow']
            latestclose = ins_data[i][j]['btclose']
            latestopen = ins_data[i][j]['dayopen']
            bool=True
            for x in range(1,8):
                if latesthigh-latestlow<=(ins_data[i][j-x]['dayhigh']-ins_data[i][j-x]['daylow']):
                    bool=False
                    break
            if bool:
                if latestclose<=latestopen or latestclose<=ins_data[i][j-1]['dayclose'] or ins_data[i][j-5]['dayclose']<=ins_data[i][j-5]['dayopen'] or ins_data[i][j-20]['dayclose']<=ins_data[i][j-20]['dayopen'] or ins_data[i][j-1]['volume']<=10000:
                    bool=False
            if bool:
                if getsma(20,j,ins_data[i])<=getsma(50,j,ins_data[i]):
                    bool=False
            if bool:
                if (j+1) in ins_data[i].keys():
                    format_str = '%d/%m/%Y'
                    print("bought ", i, "at price ", latestclose, "on date ", ins_data[i][j]['date'])
                    print(" and Sold ",i, "at price ", ins_data[i][j+1]['sellprice'],"on date ",ins_data[i][j+1]['date'])
                    totalinvested += latestclose
                    Totalprofit =Totalprofit+latestclose-ins_data[i][j+1]['sellprice']
                    # sold += ins_data[i][j+1]['sellprice']
                    profit=latestclose-ins_data[i][j+1]['sellprice']
                    proper=(profit/latestclose)*100
                    # datetime_obj = datetime.datetime.strptime(ins_data[i][j]['date'], format_str)
                    # datetime_obj2 = datetime.datetime.strptime(ins_data[i][j+1]['date'], format_str)
                    pddata = [ins_data[i][j]['date'], i, latestclose, ins_data[i][j + 1]['sellprice'],ins_data[i][j+1]['date'],profit,proper]
                    pddataall.append(pddata)


df=pd.DataFrame(pddataall, columns=['Entry Date','instrument_name','Buy Price','Sell Price','Exit Date','profit','profit-percent'])
if totalinvested!=0:
    profitpercent=(abs(Totalprofit)/totalinvested)*100
else:
    profitpercent=0
print("total profit/loss =",Totalprofit)
print("total profit/loss percentage =",profitpercent)
df.sort_values(by='Entry Date', ascending=True, inplace=True)
print(df)
df.to_csv("2021shortlisted.csv")






