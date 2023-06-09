import requests
import csv
import pandas as pd
import time
import sys


# 종목 티커 저장용 리스트
my_symbol_list = []
fnl_symbol_list = []

# 컬럼 설정
columns = ['date', 'symbol', 'name', 'exchange']
for column in ['open', 'high', 'low', 'close', 'volume']:
    for i in range(2, 8):
        columns.append(f'{column}_d{i}')

# 티커 저장용 리스트
my_stock_data_list = []
# 데이터 저장용 리스트
filtered_data = []

# 하루에 500번의 호출과 분당 5번의 호출
cnt = 0
calls_today = 0
call_limit_per_minute = 5
start_time = time.time()
start_processing = False
next_processing = True

# Alpha Vantage API 키
# api_key = '5XA0U3886DHOGE4C'
# api_key = 'J8AQ46P2NB04MUOP'
# api_key = '6NZBSL488LQRXW6R'
api_key = '5XA0U3886DHOGE4C'

stock_data = pd.read_excel('C:/Users/Choi Heewon/thredart/quant/us/data/us_nasdaq_amex_stock_hex_0.4_list_data.xlsx')
hex_data = pd.read_excel('C:/Users/Choi Heewon/thredart/quant/us/data/us_nasdaq_amex_stock_hex_0.4_intraday_09_35_00_data.xlsx')

# 데이터프레임을 리스트로 변환
stock_data_list = stock_data.values.tolist()
for row in stock_data_list:
    if len(row[1]) < 5:
        my_stock_data_list.append(row)

target_symbol = 'BTDR'
target_date = '2023-06-16'
target_time = '09:31:00'

for row in my_stock_data_list:
    if row[0] == target_date and row[1] == target_symbol:
        start_processing = True
    
    if start_processing:
        next_processing = True 
        my_list = []      

        print("date : " + str(row[0]))
        print("symbol : " + str(row[1]))      

        date = row[0]
        symbol = row[1]
        name = row[2]
        exchange = row[3]

        for y_cnt in range(1, 3):
            if not next_processing:
                break                
            print("y_cnt : " + str(y_cnt))

            for m_cnt in range(1, 13):
                if not next_processing:
                    break                     
                print("m_cnt : " + str(m_cnt))

                # 알파베인티지(AlphaVantage) API - Intraday (Extended History)
                CSV_URL = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol={symbol}&interval=5min&slice=year{y_cnt}month{m_cnt}&outputsize=full&apikey={api_key}'
                print("CSV_URL : " + str(CSV_URL))

                with requests.Session() as s:
                    download = s.get(CSV_URL)
                    decoded_content = download.content.decode('utf-8')
                    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
                    my_list = list(cr)[1:]

                    error_message = '5 calls per minute and 500 calls per day'
                    error_message2 = 'Error Message'
                    if any(error_message or error_message2 in sublist[0] for sublist in my_list):
                        print("Error message found in my_list")
                        sys.exit()

                    print("my_list : " + str(my_list))

                    fnl_my_list = []
                    for sublist in my_list:
                        print("sublist : " + str(sublist))
                        fnl_my_list.append(sublist[0][:10])
                        fnl_my_list = list(set(fnl_my_list))
                        print("fnl_my_list : " + str(fnl_my_list))

                    print("fnl_my_list : " + str(fnl_my_list))

                    for sublist in my_list:
                        index = next((i for i, sublist in enumerate(fnl_my_list) if sublist[0].startswith(date)), None)
                        print("index : " + str(index))
                    
                        if index is not None:
                            row = [date, symbol, name, exchange]

                            for column in ['open', 'high', 'low', 'close', 'volume']:
                                if column == 'open': col_index = 1
                                elif column == 'high': col_index = 2
                                elif column == 'low': col_index = 3
                                elif column == 'close': col_index = 4
                                elif column == 'volume': col_index = 5

                                for i in range(2, 8):
                                    new_index = index - i
                                    if new_index >= 0:
                                        new_date = fnl_my_list[new_index]
                                        print("new_date : " + str(new_date))

                                        if sublist[0].startswith(new_date) and sublist[0].endswith(target_time):
                                            try:
                                                value = my_list[new_date][col_index]
                                                print("value : " + str(value))

                                            except IndexError:
                                                value = ''                                        
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
                            updated_data.to_excel('C:/Users/Choi Heewon/thredart/quant/us/data/us_nasdaq_amex_stock_hex_0.4_intraday_09_35_00_data.xlsx', index=False)    

                            next_processing = False

                            break
                cnt += 1
                calls_today += 1
                elapsed_time = time.time() - start_time

                print("\tcnt : " + str(cnt))
                print("\tcalls_today: " + str(calls_today))

                time.sleep(5)

                if cnt % call_limit_per_minute == 0:
                    elapsed_time = time.time() - start_time
                    sleep_time = max(60 - elapsed_time, 0)
                    print(f"\t\tSleeping for {sleep_time} seconds to reset minute call limit")
                    time.sleep(sleep_time)
                    start_time = time.time()
                    cnt = 0

print("Data collection and sorting completed.")