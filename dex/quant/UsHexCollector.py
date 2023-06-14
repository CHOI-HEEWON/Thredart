import requests
import csv
import time
import pandas as pd

# Alpha Vantage API 키
api_key = 'J8AQ46P2NB04MUOP'

# 종목 티커 조회를 위한 API 요청
CSV_URL = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'

# 종목 티커 저장용 리스트
symbol_list = []

with requests.Session() as s:
    download = s.get(CSV_URL)
    decoded_content = download.content.decode('utf-8')
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    my_list = list(cr)

    for row in my_list:
        if row[2] == 'NASDAQ' and row[3] == 'Stock':  # 종목 유형이 'NASDAQ', Stock'인 경우에만 출력
            symbol_list.append((row[0], row[1], row[2]))  # 'symbol', 'name', 'exchange' 저장

# 날짜 범위 설정
start_date = '2022-12-20'
end_date = time.strftime('%Y-%m-%d')  # 현재 날짜

# 컬럼 설정
columns = ['date', 'symbol', 'name', 'exchange']
for column in ['open', 'high', 'low', 'close', 'volume']:
    for i in range(-3, 8):
        columns.append(f'{column}_D{i}')

# 데이터 저장용 리스트
filtered_data = []

# 각 티커에 대해 API 요청
for symbol, name, exchange in symbol_list:
    # 알파베인티지(AlphaVantage) API 엔드포인트 URL
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={api_key}'

    # API 요청 및 응답 데이터 가져오기
    response = requests.get(url)
    data = response.json()

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
                    previous_close = float(filtered_time_series.get(previous_date, {}).get('close', ''))
                    price_change_ratio = (current_close - previous_close) / previous_close  # (현재종가 - 전일종가) / 전일종가

                    # 급등주 비율이 0.4 이상인 경우 종목 데이터 추가
                    if price_change_ratio >= 0.4:
                        row = [date, symbol, name, exchange]
                        for column in ['open', 'high', 'low', 'close', 'volume']:
                            for i in range(-3, 8):
                                cur_date_loc = idx + i
                                key = f"{column}_D{i}"
                                if cur_date_loc < len(filtered_time_series):
                                   cur_date = list(filtered_time_series.keys())[idx+i]
                                   value = filtered_time_series[cur_date].get(column, '')
                                   row.append((key, value))
                                else:
                                   row.append((key, ''))
                        print(row)
                        filtered_data.append(row)

# 데이터프레임 생성
df = pd.DataFrame(filtered_data, columns=columns)

# 'date', 'symbol', 'name' 컬럼의 값을 기준으로 오름차순
df = df.sort_values(by=['date', 'symbol', 'name'])

# Excel 파일로 저장
file_name = f'us_hex_day_data_2023.xlsx'
df.to_excel('C:/Users/Choi Heewon/thredart/dex/quant/'+file_name)

print("Data collection and sorting completed.")