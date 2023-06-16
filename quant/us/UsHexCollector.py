import requests
import json
import csv
import pandas as pd
import pytz
import time
import datetime

# Alpha Vantage API 키
api_key = 'J8AQ46P2NB04MUOP'

# 종목 티커 조회를 위한 API 요청
CSV_URL = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'

# 날짜 범위 설정
start_date = '2022-12-20'
# 미국 동부 표준시 (EST) 타임존 설정
est_timezone = pytz.timezone('America/New_York')
# 현재 날짜와 시간 가져오기 (미국 동부 표준시)
current_datetime = datetime.datetime.now(est_timezone)
# 날짜 포맷 지정
end_date = current_datetime.strftime('%Y-%m-%d')

# 컬럼 설정
columns = ['date', 'symbol', 'name', 'exchange']
for column in ['open', 'high', 'low', 'close', 'volume']:
    for i in range(-3, 8):
        columns.append(f'{column}_d{i}')

# 종목 티커 저장용 리스트
my_symbol_list = []
# 데이터 저장용 리스트
filtered_data = []

cnt = 0
calls_today = 0
call_limit_per_day = 400
call_limit_per_minute = 4
start_time = time.time()
start_processing = False  # Flag variable

with requests.Session() as s:
    download = s.get(CSV_URL)
    decoded_content = download.content.decode('utf-8')
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    symbol_list = list(cr)

print("len(symbol_list): " + str(len(symbol_list)))  # 11555

for row in symbol_list:    
    if 'Warrants' not in row[1] and (row[2] == 'NASDAQ' or row[2] == 'NYSE MKT') and row[3] == 'Stock':
        my_symbol_list.append(row) 

print("len(my_symbol_list): " + str(len(my_symbol_list)))  # 4536

# my_symbol_df = pd.DataFrame(my_symbol_list)

# # Excel 파일로 저장
# file_name = f'us_nasdaq_amex_stock_list.xlsx'
# my_symbol_df.to_excel('C:/Users/Choi Heewon/thredart/quant/us/'+file_name)

symbol_nm = 'CDTX'

for row in my_symbol_list:
    if row[0] == symbol_nm:
        start_processing = True
    
    if start_processing:
        symbol = row[0]
        name = row[1]
        exchange = row[2]

        # 알파베인티지(AlphaVantage) API 엔드포인트 URL
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={api_key}'

        # API 요청 및 응답 데이터 가져오기
        response = requests.get(url)

        try:
            data = response.json()

        except json.decoder.JSONDecodeError:
            print("-----------------------------> json.decoder.JSONDecodeError")
            pass  # 데이터를 건너뛰고 다음 작업으로 넘어감

        print("symbol : " + str(symbol))

        if data:
            if '5 calls per minute and 500 calls per day' in data:
                print("!!! 5 calls per minute and 500 calls per day !!!")
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
                            if start_date <= date <= end_date
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
                            current_close = float(filtered_time_series[date]['close'])
                            previous_close = float(filtered_time_series.get(previous_date).get('close', ''))
                            price_change_ratio = (current_close - previous_close) / previous_close  # (현재종가 - 전일종가) / 전일종가

                            # print("idx : " + str(idx))
                            # print("symbol : " + str(symbol))
                            # print("name : " + str(name))
                            # print("date : " + str(date))
                            # print("previous_date : " + str(previous_date))
                            # print("current_close : " + str(current_close))
                            # print("previous_close : " + str(previous_close))
                            # print("price_change_ratio : " + str(price_change_ratio))

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

        calls_today += 1
        cnt += 1
        elapsed_time = time.time() - start_time

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

# 'date', 'symbol', 'exchange' 컬럼의 값을 기준으로 오름차순
# df = df.sort_values(by=['date', 'symbol', 'exchange'])

# Excel 파일로 저장
file_name = 'us_hex_day_data_2023_{}.xlsx'.format(symbol_nm)
df.to_excel('C:/Users/Choi Heewon/thredart/quant/us/'+file_name)

print("Data collection and sorting completed.")