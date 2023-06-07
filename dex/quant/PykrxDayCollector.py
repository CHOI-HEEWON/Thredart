from pykrx import stock
from datetime import datetime, timedelta
import pandas as pd
from DexDBConnAPI import *


# DB 연결
dexDBConnAPI = DexDBConnAPI()    

# 시작일과 종료일 설정
start_date = datetime.now() - timedelta(days=15)
end_date = datetime.now().date()

# 컬럼 생성
columns = ['날짜', '종목코드', '종목명']
for column in ['시가', '고가', '저가', '종가', '거래대금']:
  for i in range(-3, 8):
    columns.append(f'{column}_D{i}')

data = pd.DataFrame(columns=columns)

# 코스피 & 코스닥 종목코드
tickers_kospi = stock.get_market_ticker_list()  
tickers_kosdaq = stock.get_market_ticker_list(market="KOSDAQ") 
tickers = tickers_kospi + tickers_kosdaq  

# 상한가 날짜 조회
upper_limit_date = dexDBConnAPI.select_upper_limit_date()

for ticker in tickers:
    if "K" not in ticker and "L" not in ticker:
        df = stock.get_market_ohlcv_by_date(start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"), ticker) 

        for date in df.index: 
            date_index_idx = df.index.get_loc(date) 

            if date_index_idx - 3 >= 0:
               pre_date = df[df.index < pd.to_datetime(date)].index  

               if len(pre_date) > 0:  
                  pre_date = pre_date[-1]
                  df_copy = df[df.index == date].copy()  
                  df_copy['전일종가'] = df.loc[pre_date, '종가']
                  target_df = df_copy[(df_copy['종가'] - df_copy['전일종가']) / df_copy['전일종가'] >= 0.28]  

                  if not target_df.empty:
                     target_date = target_df.index[0]
                     row = {'날짜': target_date, '종목명': stock.get_market_ticker_name(ticker), '종목코드': ticker}

                     for i in range(-3, 8):
                         target_index_idx = df.index.get_loc(target_date) 

                         if target_index_idx + i < len(df.index) and target_index_idx + i >= 0:  
                            cur_date = df.index[df.index.get_loc(target_date) + i]

                            for column in ['시가', '고가', '저가', '종가', '거래대금']:
                                row[f'{column}_D{i}'] = df.loc[cur_date, column]

                         else:
                            row[f'시가_D{i}'] = None
                            row[f'고가_D{i}'] = None
                            row[f'저가_D{i}'] = None
                            row[f'종가_D{i}'] = None
                            row[f'거래대금_D{i}'] = None

                     if target_date.date() in upper_limit_date:
                        dexDBConnAPI.update_upper_limit_stock_list(row)     
                     else:    
                        dexDBConnAPI.insert_upper_limit_stock_list(row)
                          

print("Data collection and sorting completed.")