import pandas as pd
import pandas_ta as ta

df= pd.read_csv("file_name.csv")
df['super_T'] = ta.supertrend(high=df["High"],low=df["Low"],close=df["Close"],period = 7,multiplier=3)['SUPERT_7_3.0']
# we can adjust multiplier and period
print(df)