import sys
import KisAPI
import pandas as pd
import matplotlib as plt
import time


class UsHexMain:
    def __init__():
        super().__init__()
        
        KisAPI.auth()
        KisAPI.get_acct_balance()


    # US HEX 매도
    def sell_us_hex_stock():
        KisAPI.sell_us_hex_stock()             


    # US HEX 매수
    def buy_us_hex_stock():
        KisAPI.buy_us_hex_stock()  


if __name__ == '__main__':
    usHexMain = UsHexMain()
    usHexMain.sell_us_hex_stock()
    usHexMain.buy_us_hex_stock()


# stock_code_list = df.index.to_list()
# for x in stock_code_list:
#     sdf = ka.get_stock_history(x, '20180101')
#     print(x, df.loc[x]['종목명'], df.loc[x]['현재가'])
#     sdf.Close.plot()
#     plt.show()

# time.sleep(.1)

# print(ka.get_current_price('377990'))    

# ka.do_sell('052300',  1,  1100)
# time.sleep(1)
# ka.do_buy('052300', 1, 950 ) 
# time.sleep(1)

# df_orders = ka.get_orders()
# ka.do_cancel_all()

# oll = df_orders.index.to_list()
# ka.do_revise(oll[0], 1, 1050)

# from datetime import datetime
# sdt = datetime.now().strftime('%Y%m%d')
# df_complete = ka.get_my_complete(sdt, sdt)

# ar = ka.get_buyable_cash()
# print(ar)

# ocl = ka.get_stock_completed('052300')

# hdf1 = ka.get_stock_history('052300')
# time.sleep(.5)
# hdf2 = ka.get_stock_history('052300', 'W')
# time.sleep(.5)
# hdf3 = ka.get_stock_history('052300', 'M')
# time.sleep(.5)
# hdfi = ka.get_stock_investor('052300')

