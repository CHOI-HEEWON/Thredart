import requests
import csv
import pandas as pd


columns = ['symbol', 'name', 'exchange', 'assetType', 'ipoDate', 'status']

# 종목 티커 저장용 리스트
my_symbol_list = []

# Alpha Vantage API 키
api_key = 'J8AQ46P2NB04MUOP'

# 알파베인티지(AlphaVantage) API - 미국 티커 전체 조회
CSV_URL = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'

with requests.Session() as s:
    download = s.get(CSV_URL)
    decoded_content = download.content.decode('utf-8')
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    symbol_list = list(cr)

for row in symbol_list:
    if all(token not in row[0] for token in ['ZVZZT', 'ZWZZT', 'ZXYZ-A', 'ZXZZT-A']) \
        and row[2] in ['NASDAQ', 'NYSE MKT'] \
        and row[3] == 'Stock' \
        and len(row[0]) < 5:
        
        ticker = row[:5] + row[6:]
        my_symbol_list.append(ticker)

# 데이터프레임 생성
df = pd.DataFrame(my_symbol_list, columns=columns)

# Excel 파일로 저장
file_name = f'us_nasdaq_amex_stock_list.xlsx'
excel_file_path = 'C:/Users/Choi Heewon/thredart/quant/us/data/' + file_name
df.to_excel(excel_file_path, index=False)

print("Data collection and sorting completed.")