import requests
import json
import pandas as pd
import time


# Alpha Vantage API 키
api_key = 'J8AQ46P2NB04MUOP'

# 컬럼 설정
columns = ['date', 'symbol', 'name', 'exchange']
for column in ['open', 'high', 'low', 'close', 'volume']:
    for i in range(-3, 15):
        columns.append(f'{column}_d{i}')

# 데이터 저장용 리스트
filtered_data = []

# 하루에 500번의 호출과 분당 5번의 호출
cnt = 0
calls_today = 0
call_limit_per_day = 500
call_limit_per_minute = 5
start_time = time.time()
start_processing = False  # Flag variable

stock_data = pd.read_excel('C:/Users/Choi Heewon/thredart/quant/us/data/us_nasdaq_amex_stock_list_data.xlsx')
hex_data = pd.read_excel('C:/Users/Choi Heewon/thredart/quant/us/data/us_nasdaq_amex_stock_hex_0.4_daily_data.xlsx')

# 데이터프레임을 리스트로 변환
stock_data_list = stock_data.values.tolist()

target_symbol = 'AACG'

for row in stock_data_list:
    if row[0] == target_symbol:
        start_processing = True
    
    if start_processing:
        symbol = row[0]
        name = row[1]
        exchange = row[2]

        # 알파베인티지(AlphaVantage) API - TIME_SERIES_DAILY_ADJUSTED
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={api_key}'

        # API 요청 및 응답 데이터 가져오기
        response = requests.get(url)

        print("symbol : " + str(symbol))

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
                            current_close = filtered_time_series.get(date, {}).get('close', 0)
                            previous_close = filtered_time_series.get(previous_date, {}).get('close', 0)
                            
                            if current_close and previous_close:
                                current_close = float(current_close)
                                previous_close = float(previous_close)
                                price_change_ratio = (current_close - previous_close) / previous_close  # (현재종가 - 전일종가) / 전일종가

                                # print("idx : " + str(idx))
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
                                        for i in range(-3, 15):
                                            cur_date_loc = idx + i
                                            if cur_date_loc < len(filtered_time_series):
                                                cur_date = list(filtered_time_series.keys())[idx+i]
                                                value = float(filtered_time_series[cur_date].get(column, ''))
                                                row.append(value)
                                            else:
                                                row.append('')

                                    print("row :" + str(row))
                                    filtered_data.append(row)

                                    # 새로운 데이터프레임 생성
                                    fnl_symbol_df = pd.DataFrame(filtered_data, columns=columns)

                                    # 기존 데이터프레임과 새로운 데이터프레임을 병합
                                    updated_data = pd.concat([hex_data, fnl_symbol_df], ignore_index=False)

                                    # 업데이트된 데이터를 Excel 파일로 저장 (index 제거)
                                    updated_data.to_excel('C:/Users/Choi Heewon/thredart/quant/us/data/us_nasdaq_amex_stock_hex_0.4_daily_data.xlsx', index=False)                                         

        calls_today += 1
        cnt += 1
        elapsed_time = time.time() - start_time

        print("cnt : " + str(cnt))
        print("calls_today: " + str(calls_today))

        if calls_today >= call_limit_per_day:
            break

        if cnt % call_limit_per_minute == 0:
            elapsed_time = time.time() - start_time
            sleep_time = max(60 - elapsed_time, 0)
            print(f"\t\tSleeping for {sleep_time} seconds to reset minute call limit")
            time.sleep(sleep_time)
            start_time = time.time()
            cnt = 0

print("Data collection and sorting completed.")