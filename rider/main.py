import sys
import urllib
import datetime
import pandas as pd 
import requests

# load listed company
stock_code = pd.read_excel('data.xls')
stock_code = stock_code[['기업명', '종목코드']] 
stock_code = stock_code.rename(columns={'기업명': 'company', '종목코드': 'code'}) 
stock_code.code = stock_code.code.map('{:06d}'.format)
#print(stock_code)
#print(stock_code.T.to_dict().values())

for index, row in stock_code.iterrows():
  df = pd.DataFrame()
  delisted_flag = False
  
  for page in range(1, 3): # get recent 20 records
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=row.code)     
    url = '{url}&page={page}'.format(url=url, page=page)
    df = df.append(pd.read_html(url, header=0)[0], ignore_index=True).dropna()    

  print(row.code, row.company)
  df['거래량'] = df['거래량'].astype(int)
  stock_code[index, 'volume'] = df['거래량'].mean()
  
  
print(stock_code)
sys.exit()