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
    
    # filter delisted company
    if page == 1 and (not len(df) or datetime.datetime.now().strftime('%Y.%m.%d') != df.head(1)['날짜'].values[0]):
      delisted_flag = True
      break
      
  if delisted_flag:
    stock_code.drop(index, inplace=True) # drop delisted company
  else: # else add mean volume
    print(row.code, row.company, c)
    df['거래량'] = df['거래량'].astype(int)
    stock_code[index, 'volume'] = df['거래량'].mean()
  
print(stock_code)
sys.exit()
# targeting company
company='LG화학' 
code = stock_code[stock_code.company == company].code.values[0].strip() ## strip() : 공백제거


# crawl target company's date by date data
df = pd.DataFrame()
for page in range(1, 21):
  url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)     
  url = '{url}&page={page}'.format(url=url, page=page)
  print('working on: ', url)
  df = df.append(pd.read_html(url, header=0)[0], ignore_index=True)
  
    
    
df = df.dropna() # remove NaN rows
df = df.rename(columns= {'날짜': 'date', '종가': 'close', '전일비': 'diff', '시가': 'open', '고가': 'high', '저가': 'low', '거래량': 'volume'}) 
df[['close', 'diff', 'open', 'high', 'low', 'volume']] = df[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int) # change datatype to int
df['date'] = pd.to_datetime(df['date']) # change date's datatype to date
df = df.sort_values(by=['date'], ascending=True) 
print(df) 

