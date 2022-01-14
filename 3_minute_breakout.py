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
access="bSFDdOZYC034tRyQkNNUKrvxZcTCIzhQ"
kite.set_access_token(access_token=access)

token_to_instrument={3695361:"JKTYRE"}
quantity={"JKTYRE":1}
live_data={}
kws=KiteTicker(api , access)

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
arr=kite.orders()
for i in arr:
    print(i)
for symbol, values in live_data.items():
    try:
        history[symbol]
    except:
        history[symbol] = {"High": values["High"], "Low": values["Low"], "Traded": False, "Status": 0, "StopLoss": -1}
    print("bp1")
    print(history)
    # sys.exit()
    buy_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NSE,
                                    order_type=kite.ORDER_TYPE_SLM,
                                    tradingsymbol=symbol,
                                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                                    quantity=quantity[symbol],
                                    validity=kite.VALIDITY_DAY,
                                    product=kite.PRODUCT_MIS,
                                    trigger_price=history[symbol]['Low']
                                    )
    sell_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                     exchange=kite.EXCHANGE_NSE,
                                     order_type=kite.ORDER_TYPE_SLM,
                                     tradingsymbol=symbol,
                                     transaction_type=kite.TRANSACTION_TYPE_SELL,
                                     quantity=quantity[symbol],
                                     validity=kite.VALIDITY_DAY,
                                     product=kite.PRODUCT_MIS,
                                     trigger_price=history[symbol]['Low']
                                     )
    print(buy_order_id,sell_order_id)
while datetime.time(9,18,0)<datetime.datetime.now().time()< datetime.time(15,10,0):
    for symbol, values in live_data.items():
        try:
            history[symbol]
        except:
            history[symbol]={"High":values["High"],"Low":values["Low"],"Traded":False,"Status":0, "StopLoss":-1}
        if values['High']>history[symbol]['High'] and values["Open"]==values['Low'] and not history[symbol]['Traded']:
            print("Buy :",symbol, f" at {values['High']} and Time{datetime.datetime.now().time()}")
            history[symbol]["Traded"]=True
            history[symbol]["Status"] = 1
            history[symbol]["StopLoss"] = history[symbol]['Low']
        if values['Low']< history[symbol]['Low'] and values["Open"]== values['High'] and not history[symbol]['Traded']:
            print("Sell :",symbol, f" at {values['Low']} and Time {datetime.datetime.now().time()}")
            history[symbol]['Traded']=True
            history[symbol]["Status"] = 2
            history[symbol]["StopLoss"] = history[symbol]['High']
        if history[symbol]["Traded"]==True and  history[symbol]["Status"] == 1 and  values['Low']<history[symbol]['StopLoss']:
            print("Sell :", symbol, f" at {values['Low']} and Time {datetime.datetime.now().time()}")
            history[symbol]["Status"] = 0
        if history[symbol]["Traded"] == True and history[symbol]["Status"] == 2 and values['High'] > history[symbol]['StopLoss']:
            print("Buy :", symbol, f" at {values['High']} and Time{datetime.datetime.now().time()}")
            history[symbol]["Status"] = 0
    time.sleep(1)
time.sleep(5)
    #Squaring off at the end of 3:10
for symbol, values in live_data.items():
    if history[symbol]["Traded"]==True and  history[symbol]["Status"] == 1:
        print("Sell :", symbol, f" at {values['Low']} and Time {datetime.datetime.now().time()}")
        sell_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                        exchange=kite.EXCHANGE_NSE,
                                        order_type=kite.ORDER_TYPE_MARKET,
                                        tradingsymbol=symbol,
                                        transaction_type=kite.TRANSACTION_TYPE_SELL,
                                        quantity=quan[symbol],
                                        validity=kite.VALIDITY_DAY,
                                        product=kite.PRODUCT_MIS,
                                        )
        history[symbol]["Status"] = 0
    if history[symbol]["Traded"] == True and history[symbol]["Status"] == 2:
        print("Buy :", symbol, f" at {values['High']} and Time{datetime.datetime.now().time()}")
        buy_order_id=kite.place_order(variety=kite.VARIETY_REGULAR,
                                      exchange=kite.EXCHANGE_NSE,
                                      order_type=kite.ORDER_TYPE_MARKET,
                                      tradingsymbol=symbol,
                                      transaction_type=kite.TRANSACTION_TYPE_BUY,
                                      quantity=quantity[symbol],
                                      validity=kite.VALIDITY_DAY,
                                      product=kite.PRODUCT_MIS,
                                      )
        history[symbol]["Status"] = 0
time.sleep(5)
print("Session Ended !!!!!") if datetime.datetime.now().time()> datetime.time(15,10) else print("Wait till 9:28 !!!!")