import pymysql
from Config import *
from datetime import datetime


class HogaPlayDBConnAPI():
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
    def select_stock_list(self, val):
        query =  "SELECT \
                 `ticker`, \
                 `ticker_nm` \
                  FROM stock_list \
                  WHERE created_at = %s"
        
        self.cursor.execute(query, val)
        ret_data = self.cursor.fetchall()

        print("select_stock_list: ", self.cursor.rowcount, "record selected")
        
        return ret_data   
    
    def select_stock_hoga(self, row):   
        query =  "SELECT \
                  DATE_FORMAT(created_at, '%%h:%%i:%%s.%%f') AS hoga_created_at, \
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
                  FROM stock_hoga \
                  WHERE DATE(created_at) = %s \
                  AND ticker = %s"
        
        val = ( row['created_at'],   
                row['ticker']
              )        
        
        self.cursor.execute(query, val)
        ret_data = self.cursor.fetchall()
        
        print("select_stock_hoga: ", self.cursor.rowcount, "record selected")
        
        return ret_data  
    
    def select_stock_time(self, row):       
        query = "SELECT \
                DATE_FORMAT(MIN(created_at), '%%h:%%i:%%s.%%f') AS start_time, \
                DATE_FORMAT(MAX(created_at), '%%h:%%i:%%s.%%f') AS end_time \
                FROM ( \
                    SELECT created_at FROM stock_hoga \
                    WHERE DATE(created_at) = %s \
                    AND ticker = %s \
                    UNION DISTINCT \
                    SELECT created_at FROM stock_chegyeol \
                    WHERE DATE(created_at) = %s \
                    AND ticker = %s \
                ) AS combined_tables(created_at) \
                ORDER BY created_at"        

        val = ( row['created_at'],   
                row['ticker'],
                row['created_at'],   
                row['ticker']                
              )        
        
        self.cursor.execute(query, val)
        ret_data = self.cursor.fetchall()
        
        print("select_stock_time: ", self.cursor.rowcount, "record selected")
        
        return ret_data                 
        
    def select_stock_chegyeol(self, row):   
        query =  "SELECT \
                  DATE_FORMAT(created_at, '%%h:%%i:%%s.%%f') AS chegyeol_created_at, \
                 `chegyeol_price`, \
                 `chegyeol_qty` \
                  FROM stock_chegyeol \
                  WHERE DATE(created_at) = %s \
                  AND ticker = %s"
        
        val = ( row['created_at'],   
                row['ticker']
              )        
        
        self.cursor.execute(query, val)
        ret_data = self.cursor.fetchall()
        
        print("select_stock_chegyeol: ", self.cursor.rowcount, "record selected")
        
        return ret_data         

    #  체결 데이터 INSERT
    def insert_trading_agent(self, row):
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        
        query = "INSERT INTO trading_agent \
                (`created_at`, \
                 `ticker`, \
                 `balance`, \
                 `sell_price`, \
                 `sell_price_qty`, \
                 `buy_price`, \
                 `buy_price_qty`, \
                 `reward` \
                ) \
                VALUES ( \
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
                row['balance'],
                row['sell_price'],
                row['sell_price_qty'],
                row['buy_price'],
                row['buy_price_qty'],
                row['reward']                         
              )
        
        self.cursor.execute(query, val)
        self.conn.commit()       

        print("insert_trading_agent: ", self.cursor.rowcount, "record inserted")                