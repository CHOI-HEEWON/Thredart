from pykrx import stock
from datetime import datetime, timedelta
import pandas as pd
from KrHexDBConnAPI import *


# ========== #
class KrHexCollector:
   def __init__(self):
      super().__init__()

      # DB 연결
      self.krHexDBConnAPI = KrHexDBConnAPI()    
           
   def get_new_kr_hex_stock_data(self):

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

      # 기존 상한가 데이터 날짜 조회
      hex_date = self.krHexDBConnAPI.select_existing_kr_hex_date()

      for ticker in tickers:
         if "K" not in ticker and "L" not in ticker:
            df = stock.get_market_ohlcv_by_date(start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"), ticker) 

            for date in df.index: 
                  date_index_idx = df.index.get_loc(date) 

                  if date_index_idx - 3 >= 0:
                     pre_date = df[df.index < pd.to_datetime(date)].index  

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

                        if target_date.date() in hex_date:
                           self.krHexDBConnAPI.update_kr_hex_stock_data(row)     
                        else:    
                           self.krHexDBConnAPI.insert_kr_hex_stock_data(row)
                              

      print("Data collection and sorting completed.")

if __name__ == '__main__':
    krHexCollector = KrHexCollector()
    krHexCollector.new_kr_hex_stock_list()