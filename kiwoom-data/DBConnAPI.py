import pymysql # pip install pymysql
from datetime import datetime
from Config import *


class DBConnAPI():
    host = HOST
    user = USER
    password = PASSWORD
    database = DATABASE

    conn = pymysql.connect(host=host,
                        user=user,
                        password=password,
                        db=database,
                        charset='utf8')

    cursor = conn.cursor()

    # 종목 선정 SELECT
    def select_top_volume_stock_list(self):
        query = "SELECT ticker, ticker_nm FROM top_volume_stock_list WHERE created_at = CURDATE()"

        self.cursor.execute(query)
        ret_data = self.cursor.fetchall()
        code_list = [item[0] for item in ret_data]
        ticker_nm = [item[1] for item in ret_data]

        print("select_top_volume_stock_list: ", self.cursor.rowcount, "record selected")
        
        return code_list, ticker_nm        
    
    # 종목 선정 SELECT
    def select_stock_hoga_cnt(self):
        query = "SELECT COUNT(*) FROM stock_hoga WHERE DATE(created_at) = CURDATE()"

        self.cursor.execute(query)
        ret_data = self.cursor.fetchall()
        ret_data = ret_data[0][0]

        print("select_stock_hoga_cnt: ", self.cursor.rowcount, "record selected")
        
        return ret_data

    # 종목 선정 SELECT
    def select_stock_chegyeol_cnt(self):
        query = "SELECT COUNT(*) FROM stock_chegyeol WHERE DATE(created_at) = CURDATE()"

        self.cursor.execute(query)
        ret_data = self.cursor.fetchall()
        ret_data = ret_data[0][0]

        print("select_stock_chegyeol_cnt: ", self.cursor.rowcount, "record selected")
        
        return ret_data       

    # 종목 선정 INSERT
    def insert_top_volume_stock_list(self, row):
        query = "INSERT INTO top_volume_stock_list \
                (`created_at`, \
                 `ticker`, \
                 `ticker_nm`, \
                 `current_price`, \
                 `qty`, \
                 `rate`, \
                 `capital` \
                ) \
                VALUES ( \
                CURDATE(), \
                %s, \
                %s, \
                %s, \
                %s, \
                %s, \
                %s \
                )"
                
        val = ( row['종목코드'],
                row['종목명'],
                row['현재가'],
                row['거래량'],
                row['등락율'],
                row['시가총액']
              )

        self.cursor.execute(query, val)
        self.conn.commit()        

        print("insert_top_volume_stock_list: ", self.cursor.rowcount, "record inserted")

    # 호가 데이터 INSERT
    def insert_stock_hoga(self, row):
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        query = "INSERT INTO stock_hoga \
                (`created_at`, \
                 `ticker`, \
                 `sell_price1`, \
                 `sell_price1_qty`, \
                 `sell_price1_qty_diff`, \
                 `buy_price1`, \
                 `buy_price1_qty`, \
                 `buy_price1_qty_diff`, \
                 `sell_price2`, \
                 `sell_price2_qty`, \
                 `sell_price2_qty_diff`, \
                 `buy_price2`, \
                 `buy_price2_qty`, \
                 `buy_price2_qty_diff`, \
                 `sell_price3`, \
                 `sell_price3_qty`, \
                 `sell_price3_qty_diff`, \
                 `buy_price3`, \
                 `buy_price3_qty`, \
                 `buy_price3_qty_diff`, \
                 `sell_price4`, \
                 `sell_price4_qty`, \
                 `sell_price4_qty_diff`, \
                 `buy_price4`, \
                 `buy_price4_qty`, \
                 `buy_price4_qty_diff`, \
                 `sell_price5`, \
                 `sell_price5_qty`, \
                 `sell_price5_qty_diff`, \
                 `buy_price5`, \
                 `buy_price5_qty`, \
                 `buy_price5_qty_diff`, \
                 `sell_price6`, \
                 `sell_price6_qty`, \
                 `sell_price6_qty_diff`, \
                 `buy_price6`, \
                 `buy_price6_qty`, \
                 `buy_price6_qty_diff`, \
                 `sell_price7`, \
                 `sell_price7_qty`, \
                 `sell_price7_qty_diff`, \
                 `buy_price7`, \
                 `buy_price7_qty`, \
                 `buy_price7_qty_diff`, \
                 `sell_price8`, \
                 `sell_price8_qty`, \
                 `sell_price8_qty_diff`, \
                 `buy_price8`, \
                 `buy_price8_qty`, \
                 `buy_price8_qty_diff`, \
                 `sell_price9`, \
                 `sell_price9_qty`, \
                 `sell_price9_qty_diff`, \
                 `buy_price9`, \
                 `buy_price9_qty`, \
                 `buy_price9_qty_diff`, \
                 `sell_price10`, \
                 `sell_price10_qty`, \
                 `sell_price10_qty_diff`, \
                 `buy_price10`, \
                 `buy_price10_qty`, \
                 `buy_price10_qty_diff`, \
                 `total_sell_qty`, \
                 `total_sell_qty_diff`, \
                 `total_buy_qty`, \
                 `total_buy_qty_diff` \
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
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s, \
                 %s \
                )"
            
        val = ( created_at,
                row['ticker'],
                row['sell_price1'], 
                row['sell_price1_qty'],
                row['sell_price1_qty_diff'],
                row['buy_price1'],
                row['buy_price1_qty'],
                row['buy_price1_qty_diff'],
                row['sell_price2'],
                row['sell_price2_qty'],
                row['sell_price2_qty_diff'],
                row['buy_price2'],
                row['buy_price2_qty'], 
                row['buy_price2_qty_diff'],
                row['sell_price3'],
                row['sell_price3_qty'],
                row['sell_price3_qty_diff'],
                row['buy_price3'],
                row['buy_price3_qty'],
                row['buy_price3_qty_diff'],
                row['sell_price4'],
                row['sell_price4_qty'],
                row['sell_price4_qty_diff'],
                row['buy_price4'],
                row['buy_price4_qty'],
                row['buy_price4_qty_diff'],
                row['sell_price5'],
                row['sell_price5_qty'],
                row['sell_price5_qty_diff'],
                row['buy_price5'],
                row['buy_price5_qty'],
                row['buy_price5_qty_diff'],
                row['sell_price6'],
                row['sell_price6_qty'],
                row['sell_price6_qty_diff'],
                row['buy_price6'],
                row['buy_price6_qty'],
                row['buy_price6_qty_diff'],
                row['sell_price7'],
                row['sell_price7_qty'],
                row['sell_price7_qty_diff'],
                row['buy_price7'],
                row['buy_price7_qty'], 
                row['buy_price7_qty_diff'],
                row['sell_price8'],
                row['sell_price8_qty'],
                row['sell_price8_qty_diff'],
                row['buy_price8'],
                row['buy_price8_qty'], 
                row['buy_price8_qty_diff'],
                row['sell_price9'],
                row['sell_price9_qty'], 
                row['sell_price9_qty_diff'],
                row['buy_price9'],
                row['buy_price9_qty'],
                row['buy_price9_qty_diff'],
                row['sell_price10'],
                row['sell_price10_qty'],
                row['sell_price10_qty_diff'],
                row['buy_price10'],
                row['buy_price10_qty'],
                row['buy_price10_qty_diff'],
                row['total_sell_qty'],
                row['total_sell_qty_diff'],
                row['total_buy_qty'],
                row['total_buy_qty_diff']
              )
        
        self.cursor.execute(query, val)
        self.conn.commit()   

        print("insert_stock_hoga: ", self.cursor.rowcount, "record inserted")

    #  체결 데이터 INSERT
    def insert_stock_chegyeol(self, row):
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        query = "INSERT INTO stock_chegyeol \
                (`created_at`, \
                 `ticker`, \
                 `chegyeol_price`, \
                 `chegyeol_qty` \
                 ) \
                VALUES ( \
                 %s, \
                 %s, \
                 %s, \
                 %s \
                 )"
            
        val = ( created_at,   
                row['ticker'],
                row['chegyeol_price'],
                row['chegyeol_qty'] 
              )
        
        self.cursor.execute(query, val)
        self.conn.commit()       

        print("insert_stock_chegyeol: ", self.cursor.rowcount, "record inserted")