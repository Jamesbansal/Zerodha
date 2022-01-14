import logging, sys
from kiteconnect import KiteConnect, KiteTicker
import pandas as pd
import pandas_ta as ta
import talib
import datetime
import time


api = open('api_key.txt', 'r').read()
api_secret = open('api_secret.txt', 'r').read()
kite=KiteConnect(api_key=api)
#----------------------------------------------------------------------------

# print(kite.generate_session(request_token=input(f"Request Token:{kite.login_url()} \n= "), api_secret="9amef21hjc5m9zasm5pc1fieqh4og1dp")['access_token'])
# sys.exit()

#-----------------------------------------------------------------------------
access="aY8FMh22MFZUJY8tBOm5X7ydueCK3H1a"
kite.set_access_token(access_token=access)
kws=KiteTicker(api , access)

from_date=datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(5),'%Y-%m-%d %H:%M:%S')
to_date=datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(0),'%Y-%m-%d %H:%M:%S')
interval='5minute'

token_to_instrument={3695361:"JKTYRE",3050241:"YESBANK",3677697:"IDEA",377857:"IDBI",}
quantity={"JKTYRE":1,"YESBANK":1,"IDBI":1,"IDEA":1}
live_data={}


def on_ticks(ws,ticks):
    for stock in ticks:
        live_data[token_to_instrument[stock['instrument_token']]]={"Open":stock["ohlc"]["open"],
                          "High":stock["ohlc"]["high"],
                          "Low":stock["ohlc"]["low"],
                          "Close": stock["ohlc"]["close"],
                          "LTP":stock["last_price"]}

def on_connect(ws,response):
    ws.subscribe(list(token_to_instrument.keys()))
    ws.set_mode(ws.MODE_FULL, list(token_to_instrument.keys()))
kws.on_ticks=on_ticks
kws.on_connect=on_connect
kws.connect(threaded=True)


while len(live_data.keys())!=len(list(token_to_instrument.keys())):
    continue
print("Connected to web socket......")

#wait until its 9:20
while datetime.time(9, 20,0)>=datetime.datetime.now().time():
    time.sleep(1)
orderid={}
history={}
instruments=[]
for i in token_to_instrument:
    st='NSE:'+str(token_to_instrument[i])
    instruments.append(st)
arr=kite.quote(*instruments)
circuitbreak={}
for i in instruments:
    st=i[4:]
    circuitbreak[st]={'lower':arr[i]['lower_circuit_limit'], 'upper':arr[i]['upper_circuit_limit']}
print(circuitbreak)
#as soon as it's 9:20 fetch the high and low for every instrument and place slm orders
if datetime.time(9,20,0)<datetime.datetime.now().time()< datetime.time(15,10,0):
    for symbol, values in live_data.items():
        try:
            history[symbol]
        except:
            history[symbol] = {"High": values["High"], "Low": values["Low"], "Traded": False, "Status": 0, "StopLoss": -1}
        if history[symbol]['Low'] <= circuitbreak[symbol]['lower']:
            print("lower circuit")
            continue
        if history[symbol]['High'] >= circuitbreak[symbol]['upper']:
            print("upper circuit")
            continue
        buy_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                        exchange=kite.EXCHANGE_NSE,
                                        order_type=kite.ORDER_TYPE_SLM,
                                        tradingsymbol=symbol,
                                        transaction_type=kite.TRANSACTION_TYPE_BUY,
                                        quantity=quantity[symbol],
                                        validity=kite.VALIDITY_DAY,
                                        product=kite.PRODUCT_MIS,
                                        trigger_price=history[symbol]['High'],
                                        stoploss=history[symbol]['Low'],
                                        )
        sell_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                         exchange=kite.EXCHANGE_NSE,
                                         order_type=kite.ORDER_TYPE_SLM,
                                         tradingsymbol=symbol,
                                         transaction_type=kite.TRANSACTION_TYPE_SELL,
                                         quantity=quantity[symbol],
                                         validity=kite.VALIDITY_DAY,
                                         product=kite.PRODUCT_MIS,
                                         trigger_price=history[symbol]['Low'],
                                         stoploss=history[symbol]['High']
                                         )
        orderid[symbol]={'buyid': buy_order_id, "sellid":sell_order_id}
print(orderid)
#every 5 mins get the candle data and calculate super trend for each instrument
bought=[]
sold=[]
period=7
multiplier=3
def gettoken(symbol):
    listofitems=token_to_instrument.items()
    for item in listofitems:
        if item[1]==symbol:
            return item[0]
while datetime.time(9,20,0)<datetime.datetime.now().time()< datetime.time(15,10,0):
    arr = kite.orders()
    for i in arr:
        if i['status'] == 'COMPLETE' and i['transaction_type'] == 'BUY' and i['order_id'] not in bought:
            bought.append(i['tradingsymbol'])
            print(bought, i['tradingsymbol'], " bought")
        if i['status'] == 'COMPLETE' and i['transaction_type'] == 'SELL' and i['order_id'] not in sold:
            sold.append(i['tradingsymbol'])
            print(sold, i['tradingsymbol'], " sold")
        if i['status'] == 'COMPLETE' and i['transaction_type'] == 'BUY' and i['order_id'] in sold:
            sold.remove(i['tradingsymbol'])
            print(sold, i['tradingsymbol'], " remove sold")
        if i['status'] == 'COMPLETE' and i['transaction_type'] == 'SELL' and i['order_id'] in bought:
            bought.remove(i['tradingsymbol'])
            print(bought, i['tradingsymbol'], " remove bought")
    if (datetime.datetime.now().second==0) and datetime.datetime.now().minute%5==0 and  datetime.time(9,20,0)<datetime.datetime.now().time()< datetime.time(15,10,0):
        for symbol in bought:
            print(bought)
            token=gettoken(symbol)
            from_date = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(5), '%Y-%m-%d %H:%M:%S')
            to_date = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(0), '%Y-%m-%d %H:%M:%S')
            records=kite.historical_data(token,from_date=from_date,to_date=to_date,interval=interval)
            x = 0
            for i in range(len(records)):
                st = str(records[i]['date'])
                if st[0:10] == datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d'):
                    x = i - period - 2
                    break
            records = records[x:]
            df=pd.DataFrame(records)
            df.drop(df.tail(1).index, inplace=True)
            open=df['open'].values
            high=df['high'].values
            low=df['low'].values
            close=df['close'].values
            df['ST'] = ta.supertrend(high=df["high"], low=df["low"], close=df["close"], period=period, multiplier=multiplier)['SUPERT_7_3.0']
            n=len(df)
            print(df)
            if df['Close'][n-2]>=df['ST'][n-2] and df['Close'][n-1]<df['ST'][n-1]:
                sell_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                                 exchange=kite.EXCHANGE_NSE,
                                                 order_type=kite.ORDER_TYPE_MARKET,
                                                 tradingsymbol=symbol,
                                                 transaction_type=kite.TRANSACTION_TYPE_SELL,
                                                 quantity=quantity[symbol],
                                                 validity=kite.VALIDITY_DAY,
                                                 product=kite.PRODUCT_MIS
                                                 )
                print("st sell order")
                kite.cancel_order(order_id=orderid[symbol]['sellid'], variety=kite.VARIETY_REGULAR)

        for symbol in sold:
            print(sold)
            token = gettoken(symbol)
            from_date = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(5), '%Y-%m-%d %H:%M:%S')
            to_date = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(0), '%Y-%m-%d %H:%M:%S')
            records = kite.historical_data(token, from_date=from_date, to_date=to_date, interval=interval)
            for i in range(len(records)):
                st = str(records[i]['date'])
                if st[0:10] == datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d'):
                    i = i - period - 1
                    break
            records = records[i:]
            df = pd.DataFrame(records)
            df.drop(df.tail(1).index, inplace=True)
            open = df['open'].values
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            df['ST'] =ta.supertrend(high=df["high"], low=df["low"], close=df["close"], period=period, multiplier=multiplier)['SUPERT_7_3.0']
            n = len(df)
            print(df)
            if df['Close'][n - 2] <= df['ST'][n - 2] and df['Close'][n - 1] > df['ST'][n - 1]:
                buy_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                                 exchange=kite.EXCHANGE_NSE,
                                                 order_type=kite.ORDER_TYPE_MARKET,
                                                 tradingsymbol=symbol,
                                                 transaction_type=kite.TRANSACTION_TYPE_SELL,
                                                 quantity=quantity[symbol],
                                                 validity=kite.VALIDITY_DAY,
                                                 product=kite.PRODUCT_MIS
                                                 )
                print("st buy order")
                kite.cancel_order(order_id=orderid[symbol]['buyid'], variety=kite.VARIETY_REGULAR)
    time.sleep(1)




