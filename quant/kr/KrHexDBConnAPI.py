import pymysql # pip install pymysql
from Config import *


class KrHexDBConnAPI():
    host = L_HOST
    user = L_USER
    password = L_PASSWORD
    database = L_DATABASE

    conn = pymysql.connect(host=host,
                           user=user,
                           password=password,
                           db=database,
                           charset='utf8')

    cursor = conn.cursor()

    #  상한가 INSERT
    def insert_kr_hex_stock_data(self, row):
        query = "INSERT INTO kr_hex_stock_list \
                (`hex_date`, \
                 `ticker`, \
                 `ticker_nm`, \
                 `d_3_open_price`, \
                 `d_2_open_price`, \
                 `d_1_open_price`, \
                 `d0_open_price`, \
                 `d1_open_price`, \
                 `d2_open_price`, \
                 `d3_open_price`, \
                 `d4_open_price`, \
                 `d5_open_price`, \
                 `d6_open_price`, \
                 `d7_open_price`, \
                 `d_3_high_price`, \
                 `d_2_high_price`, \
                 `d_1_high_price`, \
                 `d0_high_price`, \
                 `d1_high_price`, \
                 `d2_high_price`, \
                 `d3_high_price`, \
                 `d4_high_price`, \
                 `d5_high_price`, \
                 `d6_high_price`, \
                 `d7_high_price`, \
                 `d_3_low_price`, \
                 `d_2_low_price`, \
                 `d_1_low_price`, \
                 `d0_low_price`, \
                 `d1_low_price`, \
                 `d2_low_price`, \
                 `d3_low_price`, \
                 `d4_low_price`, \
                 `d5_low_price`, \
                 `d6_low_price`, \
                 `d7_low_price`, \
                 `d_3_close_price`, \
                 `d_2_close_price`, \
                 `d_1_close_price`, \
                 `d0_close_price`, \
                 `d1_close_price`, \
                 `d2_close_price`, \
                 `d3_close_price`, \
                 `d4_close_price`, \
                 `d5_close_price`, \
                 `d6_close_price`, \
                 `d7_close_price`, \
                 `d_3_v`, \
                 `d_2_v`, \
                 `d_1_v`, \
                 `d0_v`, \
                 `d1_v`, \
                 `d2_v`, \
                 `d3_v`, \
                 `d4_v`, \
                 `d5_v`, \
                 `d6_v`, \
                 `d7_v`, \
                 `order_status` \
                 ) \
                 VALUES ( \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s \
                 )"
                
        val = ( row['날짜'],
                row['종목코드'],               
                row['종목명'],
                row['시가_D-3'],
                row['시가_D-2'],
                row['시가_D-1'],
                row['시가_D0'],
                row['시가_D1'],
                row['시가_D2'],
                row['시가_D3'],
                row['시가_D4'],       
                row['시가_D5'],
                row['시가_D6'],
                row['시가_D7'],          
                row['고가_D-3'],
                row['고가_D-2'],
                row['고가_D-1'],
                row['고가_D0'],
                row['고가_D1'],
                row['고가_D2'],
                row['고가_D3'],
                row['고가_D4'],       
                row['고가_D5'],
                row['고가_D6'],
                row['고가_D7'],                
                row['저가_D-3'],
                row['저가_D-2'],
                row['저가_D-1'],
                row['저가_D0'],
                row['저가_D1'],
                row['저가_D2'],
                row['저가_D3'],
                row['저가_D4'],       
                row['저가_D5'],
                row['저가_D6'],
                row['저가_D7'],    
                row['종가_D-3'],
                row['종가_D-2'],
                row['종가_D-1'],
                row['종가_D0'],
                row['종가_D1'],
                row['종가_D2'],
                row['종가_D3'],
                row['종가_D4'],       
                row['종가_D5'],
                row['종가_D6'],
                row['종가_D7'],            
                row['거래대금_D-3'],
                row['거래대금_D-2'],
                row['거래대금_D-1'],
                row['거래대금_D0'],
                row['거래대금_D1'],
                row['거래대금_D2'],
                row['거래대금_D3'],
                row['거래대금_D4'],       
                row['거래대금_D5'],
                row['거래대금_D6'],
                row['거래대금_D7'],     
                '0'                                                           
              )

        self.cursor.execute(query, val)
        self.conn.commit()        

        print("insert_kr_hex_stock_data: ", self.cursor.rowcount, "record inserted")

    # 상한가 UPDATE
    def update_kr_hex_stock_data(self, row):
        query = "UPDATE kr_hex_stock_list \
                SET \
                `d_3_open_price` = %s, \
                `d_2_open_price` = %s, \
                `d_1_open_price` = %s, \
                `d0_open_price` = %s, \
                `d1_open_price` = %s, \
                `d2_open_price` = %s, \
                `d3_open_price` = %s, \
                `d4_open_price` = %s, \
                `d5_open_price` = %s, \
                `d6_open_price` = %s, \
                `d7_open_price` = %s, \
                `d_3_high_price` = %s, \
                `d_2_high_price` = %s, \
                `d_1_high_price` = %s, \
                `d0_high_price` = %s, \
                `d1_high_price` = %s, \
                `d2_high_price` = %s, \
                `d3_high_price` = %s, \
                `d4_high_price` = %s, \
                `d5_high_price` = %s, \
                `d6_high_price` = %s, \
                `d7_high_price` = %s, \
                `d_3_low_price` = %s, \
                `d_2_low_price` = %s, \
                `d_1_low_price` = %s, \
                `d0_low_price` = %s, \
                `d1_low_price` = %s, \
                `d2_low_price` = %s, \
                `d3_low_price` = %s, \
                `d4_low_price` = %s, \
                `d5_low_price` = %s, \
                `d6_low_price` = %s, \
                `d7_low_price` = %s, \
                `d_3_close_price` = %s, \
                `d_2_close_price` = %s, \
                `d_1_close_price` = %s, \
                `d0_close_price` = %s, \
                `d1_close_price` = %s, \
                `d2_close_price` = %s, \
                `d3_close_price` = %s, \
                `d4_close_price` = %s, \
                `d5_close_price` = %s, \
                `d6_close_price` = %s, \
                `d7_close_price` = %s, \
                `d_3_v` = %s, \
                `d_2_v` = %s, \
                `d_1_v` = %s, \
                `d0_v` = %s, \
                `d1_v` = %s, \
                `d2_v` = %s, \
                `d3_v` = %s, \
                `d4_v` = %s, \
                `d5_v` = %s, \
                `d6_v` = %s, \
                `d7_v` = %s \
                WHERE \
                `hex_date` = %s AND `ticker` = %s"  

        val =  (row['시가_D-3'],
                row['시가_D-2'],
                row['시가_D-1'],
                row['시가_D0'],
                row['시가_D1'],
                row['시가_D2'],
                row['시가_D3'],
                row['시가_D4'],       
                row['시가_D5'],
                row['시가_D6'],
                row['시가_D7'],          
                row['고가_D-3'],
                row['고가_D-2'],
                row['고가_D-1'],
                row['고가_D0'],
                row['고가_D1'],
                row['고가_D2'],
                row['고가_D3'],
                row['고가_D4'],       
                row['고가_D5'],
                row['고가_D6'],
                row['고가_D7'],                
                row['저가_D-3'],
                row['저가_D-2'],
                row['저가_D-1'],
                row['저가_D0'],
                row['저가_D1'],
                row['저가_D2'],
                row['저가_D3'],
                row['저가_D4'],       
                row['저가_D5'],
                row['저가_D6'],
                row['저가_D7'],    
                row['종가_D-3'],
                row['종가_D-2'],
                row['종가_D-1'],
                row['종가_D0'],
                row['종가_D1'],
                row['종가_D2'],
                row['종가_D3'],
                row['종가_D4'],       
                row['종가_D5'],
                row['종가_D6'],
                row['종가_D7'],            
                row['거래대금_D-3'],
                row['거래대금_D-2'],
                row['거래대금_D-1'],
                row['거래대금_D0'],
                row['거래대금_D1'],
                row['거래대금_D2'],
                row['거래대금_D3'],
                row['거래대금_D4'],       
                row['거래대금_D5'],
                row['거래대금_D6'],
                row['거래대금_D7'],     
                row['날짜'],
                row['종목코드']                
                ) 

        self.cursor.execute(query, val)
        self.conn.commit()        

        print("update_kr_hex_stock_data: ", self.cursor.rowcount, "record updated")       

    # 상한가 날짜 조회(중복 제외)
    def select_existing_kr_hex_date(self):
        query = "SELECT DISTINCT(hex_date) FROM kr_hex_stock_list order by hex_date"

        self.cursor.execute(query)
        ret_data = self.cursor.fetchall()

        hex_date = [item[0] for item in ret_data]

        print("select_existing_kr_hex_date: ", self.cursor.rowcount, "record selected")
        
        return hex_date                       

    # 상한가 `ticker, d_2_v, d_1_v, d0_v, d0_high_price` SELECT
    def select_kr_hex_ticker(self):    
        query = "SELECT ticker, d_2_v, d_1_v, d0_v, d0_high_price FROM kr_hex_stock_list WHERE hex_date = (SELECT MAX(hex_date) FROM kr_hex_stock_list)"

        self.cursor.execute(query)
        ret_data = self.cursor.fetchall()

        ticker = [item[0] for item in ret_data]
        d_2_v = [item[1] for item in ret_data]      
        d_1_v = [item[2] for item in ret_data]
        d0_v = [item[3] for item in ret_data]        
        d0_high_price = [item[4] for item in ret_data]

        print("select_kr_hex_ticker: ", self.cursor.rowcount, "record selected")
        
        return ticker, d_2_v, d_1_v, d0_v, d0_high_price             
    
    # 상한가 주문상태(1:매수) SELECT
    def select_kr_hex_ticker_order_status_1(self):    
        query = "SELECT hex_date, ticker FROM kr_hex_stock_list WHERE order_status = '1'"

        self.cursor.execute(query)
        ret_data = self.cursor.fetchall()

        hex_date = [item[0] for item in ret_data]
        ticker_list = [item[1] for item in ret_data]

        print("select_kr_hex_ticker_order_status_1: ", self.cursor.rowcount, "record selected")
        
        return hex_date, ticker_list
    
    # 상한가 주문상태(0:미매)을 주문상태(1:매수)로 UPDATE
    def update_kr_hex_ticker_order_status_1(self, row):    

        query = "UPDATE kr_hex_stock_list \
                SET \
                `order_status` = '1' \
                WHERE \
                `hex_date` = %s AND `ticker` = %s"    

        val =  (row['날짜'],
                row['종목코드']                
                )                             

        self.cursor.execute(query, val)
        self.conn.commit()        

        print("update_kr_ticker_order_status_2: ", self.cursor.rowcount, "record updated")             

    # 상한가 주문상태(1:매수)을 주문상태(2:매도)로 UPDATE
    def update_kr_hex_ticker_order_status_2(self, row):    

        query = "UPDATE kr_hex_stock_list \
                SET \
                `order_status` = '2' \
                WHERE \
                `hex_date` = %s AND `ticker` = %s"    

        val =  (row['날짜'],
                row['종목코드']                
                )                             

        self.cursor.execute(query, val)
        self.conn.commit()        

        print("update_kr_ticker_order_status_2: ", self.cursor.rowcount, "record updated")             