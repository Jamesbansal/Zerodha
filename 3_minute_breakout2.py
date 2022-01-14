import logging, sys
from kiteconnect import KiteConnect, KiteTicker
import pandas as pd
import talib
import datetime
import time

api = open('api_key.txt', 'r').read()
api_secret = open('api_secret.txt', 'r').read()
kite=KiteConnect(api_key=api)
#----------------------------------------------------------------------------
#
# print(kite.generate_session(request_token=input(f"Request Token:{kite.login_url()} \n= "), api_secret="9amef21hjc5m9zasm5pc1fieqh4og1dp")['access_token'])
# sys.exit()
#-----------------------------------------------------------------------------
access="aY8FMh22MFZUJY8tBOm5X7ydueCK3H1a"
kite.set_access_token(access_token=access)
kws=KiteTicker(api , access)


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
print(live_data)
while datetime.time(9, 18)>=datetime.datetime.now().time():
    time.sleep(1)
history={}
instruments=[]
for i in token_to_instrument:
    st='NSE:'+str(token_to_instrument[i])
    instruments.append(st)
arr=kite.quote(*instruments)
print("hi")
print(arr)
circuitbreak={}

for i in instruments:
    st=i[4:]
    circuitbreak[st]={'lower':arr[i]['lower_circuit_limit'], 'upper':arr[i]['upper_circuit_limit']}
print(circuitbreak)

#placing buy and sell orders at 3 min high and low
if datetime.time(9,18,0)<datetime.datetime.now().time()< datetime.time(15,10,0):
    for symbol, values in live_data.items():
        try:
            history[symbol]
        except:
            history[symbol] = {"High": values["High"], "Low": values["Low"], "Traded": False, "Status": 0, "StopLoss": -1}
        print("bp1")
        if history[symbol]['Low']<=circuitbreak[symbol]['lower']:
            print("lower circuit")
            continue
        if history[symbol]['High']>=circuitbreak[symbol]['upper']:
            print("upper circuit")
            continue
        print(history)
        # sys.exit()
        # buy_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
        #                                 exchange=kite.EXCHANGE_NSE,
        #                                 order_type=kite.ORDER_TYPE_SLM,
        #                                 tradingsymbol=symbol,
        #                                 transaction_type=kite.TRANSACTION_TYPE_BUY,
        #                                 quantity=quantity[symbol],
        #                                 validity=kite.VALIDITY_DAY,
        #                                 product=kite.PRODUCT_MIS,
        #                                 trigger_price=history[symbol]['High'],
        #                                 )
        # sell_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
        #                                  exchange=kite.EXCHANGE_NSE,
        #                                  order_type=kite.ORDER_TYPE_SLM,
        #                                  tradingsymbol=symbol,
        #                                  transaction_type=kite.TRANSACTION_TYPE_SELL,
        #                                  quantity=quantity[symbol],
        #                                  validity=kite.VALIDITY_DAY,
        #                                  product=kite.PRODUCT_MIS,
        #                                  trigger_price=history[symbol]['Low'],
        #                                  )
        # print(buy_order_id,sell_order_id)
arr=kite.orders()
# for i in arr:
#     print(i)
bought=[]
sold=[]
#keeping track of all orders placed, if they have been executed or not.
while datetime.time(9,18,0)<datetime.datetime.now().time()< datetime.time(15,10,0):
    arr = kite.orders()
    for i in arr:
        print("-----------------------------------")
        print(i)
        if i['status']=='COMPLETE' and i['transaction_type']=='BUY' and i['tradingsymbol'] not in bought:
            bought.append(i['tradingsymbol'])
            print(bought, i['tradingsymbol'], " bought")
        if i['status']=='COMPLETE' and i['transaction_type']=='SELL' and i['tradingsymbol'] not in sold:
            sold.append(i['tradingsymbol'])
            print(sold, i['tradingsymbol'], " sold")
        if i['status']=='COMPLETE' and i['transaction_type']=='BUY' and i['tradingsymbol'] in sold:
            sold.remove(i['tradingsymbol'])
            print(sold, i['tradingsymbol'], " remove sold")
        if i['status']=='COMPLETE' and i['transaction_type']=='SELL' and i['tradingsymbol'] in bought:
            bought.remove(i['tradingsymbol'])
            print(bought, i['tradingsymbol'], " remove bought")

time.sleep(1)
time.sleep(5)
arr=kite.orders()
#After 3:10 all open orders should be closed
for i in arr:
    if i['status'] == 'TRIGGER PENDING':
        kite.cancel_order(order_id=i['order_id'], variety=kite.VARIETY_REGULAR)
        print(i['order_id'], " cancelled")

#all instruments bought is squared off at market price
for i in bought:
    sell_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                     exchange=kite.EXCHANGE_NSE,
                                     order_type=kite.ORDER_TYPE_MARKET,
                                     tradingsymbol=i,
                                     transaction_type=kite.TRANSACTION_TYPE_SELL,
                                     quantity=quantity[i],
                                     validity=kite.VALIDITY_DAY,
                                     product=kite.PRODUCT_MIS
                                     )
    print(i, " sold at market")
#all instruments sold is squared off at market price
for i in sold:
    buy_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NSE,
                                    order_type=kite.ORDER_TYPE_MARKET,
                                    tradingsymbol=i,
                                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                                    quantity=quantity[i],
                                    validity=kite.VALIDITY_DAY,
                                    product=kite.PRODUCT_MIS
                                    )
    print(i, " bought at market")
print("Session Ended !!!!!") if datetime.datetime.now().time()> datetime.time(15,10) else print("Wait till 9:28 !!!!")