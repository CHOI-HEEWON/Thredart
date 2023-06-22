import requests
import json
import csv
import pandas as pd
import pytz
import time
from datetime import datetime, timedelta


# 날짜 범위 설정
# 미국 동부 표준시 (EST) 타임존 설정
est_timezone = pytz.timezone('America/New_York')
# 현재 날짜와 시간 가져오기 (미국 동부 표준시)
current_datetime = datetime.now(est_timezone)
# 날짜 포맷 지정
start_date = (current_datetime - timedelta(days=15)).strftime('%Y-%m-%d')
end_date = current_datetime.strftime('%Y-%m-%d')
# start_date와 end_date를 datetime 객체로 변환
start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

# 컬럼 설정
columns = ['date', 'symbol', 'name', 'exchange']
for column in ['open', 'high', 'low', 'close', 'volume']:
    for i in range(-3, 8):
        columns.append(f'{column}_d{i}')

# 종목 티커 저장용 리스트
my_symbol_list = []
# 데이터 저장용 리스트
filtered_data = []

# 하루에 500번의 호출과 분당 5번의 호출
cnt = 0
calls_today = 0
call_limit_per_day = 500
call_limit_per_minute = 5
start_time = time.time()
start_processing = False  # Flag variable

# Alpha Vantage API 키
api_key = 'J8AQ46P2NB04MUOP'

# 알파베인티지(AlphaVantage) API - 미국 티커 전체 조회
CSV_URL = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'

with requests.Session() as s:
    download = s.get(CSV_URL)
    decoded_content = download.content.decode('utf-8')
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    symbol_list = list(cr)

print("len(symbol_list): " + str(len(symbol_list)))

for row in symbol_list:
    # NASDAQ or NYSE MKT & Stock 조회, Warrants 제외, symbol len 5이상 제외, symbol = 'ZVZZT', 'ZWZZT', 'ZXYZ-A', 'ZXZZT-A' 제외
    if all(token not in row[0] for token in ['ZVZZT', 'ZWZZT', 'ZXYZ-A', 'ZXZZT-A']) and 'Warrants' not in row[1] and row[2] in ['NASDAQ', 'NYSE MKT'] and row[3] == 'Stock' and len(row[0]) < 5:
        my_symbol_list.append(row[:5] + row[6:])

print("len(my_symbol_list): " + str(len(my_symbol_list)))

for row in my_symbol_list:
      symbol = row[0]
      name = row[1]
      exchange = row[2]

      # 알파베인티지(AlphaVantage) API - TIME_SERIES_DAILY_ADJUSTED
      url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={api_key}'

      # API 요청 및 응답 데이터 가져오기
      response = requests.get(url)

      try:
          data = response.json()
      except json.decoder.JSONDecodeError:
          print("json.decoder.JSONDecodeError")
          break

      if data:
          if '5 calls per minute and 500 calls per day' in data:
              print("5 calls per minute and 500 calls per day")
              break

          # 종목별로 데이터 조회 및 필터링
          if 'Time Series (Daily)' in data:
              time_series = data['Time Series (Daily)']

              # 날짜 범위에 해당하는 데이터만 가져오기
              filtered_time_series = dict(
                  sorted(
                      {
                          date: {column.split(". ")[1]: value for column, value in values.items() if "." in column}
                          for date, values in time_series.items()
                          if datetime.strptime(date, '%Y-%m-%d') >= start_date_dt and datetime.strptime(date, '%Y-%m-%d') <= end_date_dt
                      }.items()
                  )
              )

              # 데이터가 존재하는 경우 처리
              if filtered_time_series:
                  for idx, (date, values) in enumerate(filtered_time_series.items()):
                      # 인덱스가 3 이상인 경우 처리
                      if idx >= 3:
                          # 이전 날짜
                          previous_date = list(filtered_time_series.keys())[idx-1]

                          # 종가 계산
                          current_close = filtered_time_series.get(date, {}).get('close', '')
                          previous_close = filtered_time_series.get(previous_date, {}).get('close', '')

                          if current_close and previous_close:
                              current_close = float(current_close)
                              previous_close = float(previous_close)
                              price_change_ratio = (current_close - previous_close) / previous_close

                              # 급등주 비율이 0.4 이상인 경우 종목 데이터 추가
                              if price_change_ratio >= 0.4:
                                  row = [date, symbol, name, exchange]
                                  for column in ['open', 'high', 'low', 'close', 'volume']:
                                      for i in range(-3, 8):
                                          cur_date_loc = idx + i
                                          if cur_date_loc < len(filtered_time_series):
                                              cur_date = list(filtered_time_series.keys())[idx+i]
                                              value = float(filtered_time_series[cur_date].get(column, ''))
                                              row.append(value)
                                          else:
                                              row.append('')
                                  print("row :" + str(row))
                                  filtered_data.append(row)                                   

      cnt += 1
      elapsed_time = time.time() - start_time

      print("cnt : " + str(cnt))
      print("calls_today: " + str(calls_today))

      if calls_today >= call_limit_per_day:
          break
      
      if cnt % call_limit_per_minute == 0:
          elapsed_time = time.time() - start_time
          sleep_time = max(60 - elapsed_time, 0)
          print(f"Sleeping for {sleep_time} seconds to reset minute call limit")
          time.sleep(sleep_time)
          start_time = time.time()
          cnt = 0

# 데이터프레임 생성
df = pd.DataFrame(filtered_data, columns=columns)

# Excel 파일로 저장
file_name = f'{end_date}.xlsx'
excel_file_path = 'C:/Users/Choi Heewon/thredart/quant/us/data/' + file_name
df.to_excel(excel_file_path, index=False)

print("Data collection and sorting completed.")