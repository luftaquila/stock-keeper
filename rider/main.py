import pandas as pd 

# crawl company name and code lists
stock_code = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0] 
stock_code.sort_values(['상장일'], ascending=True)
stock_code = stock_code[['회사명', '종목코드']] 
stock_code = stock_code.rename(columns={'회사명': 'company', '종목코드': 'code'}) 
stock_code.code = stock_code.code.map('{:06d}'.format) 
# print(stock_code.T.to_dict().values())

# target company
company='LG화학' 
code = stock_code[stock_code.company==company].code.values[0].strip() ## strip() : 공백제거

# crawl target company's date by date data
df = pd.DataFrame()
for page in range(1, 21):
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)     
    url = '{url}&page={page}'.format(url=url, page=page)
    print(url)
    df = df.append(pd.read_html(url, header=0)[0], ignore_index=True)
    
# df.dropna()를 이용해 결측값 있는 행 제거 
df = df.dropna() # remove NaN rows
df = df.rename(columns= {'날짜': 'date', '종가': 'close', '전일비': 'diff', '시가': 'open', '고가': 'high', '저가': 'low', '거래량': 'volume'}) 
df[['close', 'diff', 'open', 'high', 'low', 'volume']] = df[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int) # change datatype to int
df['date'] = pd.to_datetime(df['date']) # change date's datatype to date
df = df.sort_values(by=['date'], ascending=True) 
# print(df) 

