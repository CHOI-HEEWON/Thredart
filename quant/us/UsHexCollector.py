import requests
import json
import pandas as pd
import time

######################## 설정 ########################
# Alpha Vantage API 키
api_key = 'J8AQ46P2NB04MUOP'

# 종목 티커 조회를 위한 API 요청
CSV_URL = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'

# # 날짜 범위 설정
# start_date = '1999-11-01'
# # 미국 동부 표준시 (EST) 타임존 설정
# est_timezone = pytz.timezone('America/New_York')
# # 현재 날짜와 시간 가져오기 (미국 동부 표준시)
# current_datetime = datetime.datetime.now(est_timezone)
# # 날짜 포맷 지정
# end_date = current_datetime.strftime('%Y-%m-%d')

# # 종목 티커 저장용 리스트
# my_symbol_list = []
# fnl_symbol_list = []

# 컬럼 설정
columns = ['date', 'symbol', 'name', 'exchange']
for column in ['open', 'high', 'low', 'close', 'volume']:
    for i in range(-3, 8):
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

################## 미국 주식 종목 전체 조회 ##################
# with requests.Session() as s:
#     download = s.get(CSV_URL)
#     decoded_content = download.content.decode('utf-8')
#     cr = csv.reader(decoded_content.splitlines(), delimiter=',')
#     symbol_list = list(cr)

# print("len(symbol_list): " + str(len(symbol_list)))  # 11555 -> 11550

# for row in symbol_list:    
#     if 'Warrants' not in row[1] and (row[2] == 'NASDAQ' or row[2] == 'NYSE MKT') and row[3] == 'Stock':
#         my_symbol_list.append(row[:5] + row[6:])

# print("len(my_symbol_list): " + str(len(my_symbol_list)))  # 4536 > 4539

# symbol_df = pd.DataFrame(my_symbol_list, columns=['symbol', 'name', 'exchange', 'assetType', 'ipoDate', 'status'])
# symbol_df.to_excel('C:/Users/Choi Heewon/thredart/quant/us/data/us_nasdaq_amex_stock_list_all.xlsx', index=False)

###################### 시가총액 조회 ######################
# # 기존의 Excel 파일 읽기
# existing_data = pd.read_excel('C:/Users/Choi Heewon/thredart/quant/us/data/us_nasdaq_amex_stock_list_mc_over0.xlsx')

# symbol_nm = 'ACOR'

# for row in my_symbol_list:   
#     if row[0] == symbol_nm:
#         start_processing = True

#     if start_processing:    
#         url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={row[0]}&apikey={api_key}'

#         # API 요청 및 응답 받기
#         response = requests.get(url)

#         try:
#             data = response.json()
#         except json.decoder.JSONDecodeError:
#             print("json.decoder.JSONDecodeError")
#             break

#         if data:
#             if '5 calls per minute and 500 calls per day' in data:
#                 print("5 calls per minute and 500 calls per day")
#                 break

#             # 시가총액 추출
#             market_cap = data.get('MarketCapitalization')    

#             print("symbol_nm: " + str(row[0]))
#             print("\tmarket_cap : " + str(market_cap))

#             if 'None' != market_cap:  # 시가총액 'None' 제외
#                 print("\trow : " + str(row))
#                 fnl_symbol_list.append(row) 

#                 # 새로운 데이터프레임 생성
#                 fnl_symbol_df = pd.DataFrame(fnl_symbol_list, columns=['symbol', 'name', 'exchange', 'assetType', 'ipoDate', 'status'])

#                 # 기존 데이터프레임과 새로운 데이터프레임을 병합
#                 updated_data = pd.concat([existing_data, fnl_symbol_df], ignore_index=False)

#                 # 업데이트된 데이터를 Excel 파일로 저장 (index 제거)
#                 updated_data.to_excel('C:/Users/Choi Heewon/thredart/quant/us/data/us_nasdaq_amex_stock_list_mc_over0.xlsx', index=False)     

#             calls_today += 1
#             cnt += 1
#             elapsed_time = time.time() - start_time

#             print("\tcalls_today: " + str(calls_today))

#             if calls_today >= call_limit_per_day:
#                 break

#             if cnt % call_limit_per_minute == 0:
#                 elapsed_time = time.time() - start_time
#                 sleep_time = max(60 - elapsed_time, 0)
#                 print(f"Sleeping for {sleep_time} seconds to reset minute call limit")
#                 time.sleep(sleep_time)
#                 start_time = time.time()
#                 cnt = 0

# sys.exit()

stock_data = pd.read_excel('C:/Users/Choi Heewon/thredart/quant/us/data/us_nasdaq_amex_stock_list_all.xlsx')
hex_data = pd.read_excel('C:/Users/Choi Heewon/thredart/quant/us/data/us_nasdaq_amex_stock_hex_0.4_data.xlsx')

# 데이터프레임을 리스트로 변환
stock_data_list = stock_data.values.tolist()

# AACG, ATEST-L, CDTX, FTCI, IBRX
symbol_nm = 'SOFO'

for row in stock_data_list:
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

                                    # 새로운 데이터프레임 생성
                                    fnl_symbol_df = pd.DataFrame(filtered_data, columns=columns)

                                    # 기존 데이터프레임과 새로운 데이터프레임을 병합
                                    updated_data = pd.concat([hex_data, fnl_symbol_df], ignore_index=False)

                                    # 업데이트된 데이터를 Excel 파일로 저장 (index 제거)
                                    updated_data.to_excel('C:/Users/Choi Heewon/thredart/quant/us/data/us_nasdaq_amex_stock_hex_0.4_data.xlsx', index=False)                                         

        calls_today += 1
        cnt += 1
        elapsed_time = time.time() - start_time

        print("\t\tcalls_today: " + str(calls_today))
        # print("\t\telapsed_time: " + str(elapsed_time))

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