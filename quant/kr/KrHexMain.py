import sys
import KiwoomAPI, KrHexCollector
from PyQt5.QtWidgets import *


# ========== #
class KrHexMain:
    def __init__(self):
        super().__init__()
        
        self.kiwoomAPI = KiwoomAPI.KiwoomAPI(KiwoomAPI.MyServer())
        self.kiwoomAPI.run()  
        self.kiwoomAPI.account()   
        # self.kiwoomAPI.deposit()  
        # self.kiwoomAPI.balance()    

        self.krHexCollector = KrHexCollector.KrHexCollector()        

    # # 주식시분요청
    # def opt10006(self):
    #     self.kiwoomAPI.opt10006()     

    # # 주식분봉차트조회요청
    # def opt10080(self):
    #     self.kiwoomAPI.opt10080()    

    # # 상하한가요청
    # def opt10017(self):
    #     self.kiwoomAPI.opt10017()

    # 상한가 새 데이터 조회, INSERT, UPDATE
    def get_new_kr_hex_stock_data(self):
        self.krHexCollector.get_new_kr_hex_stock_data()

    # KR HEX 매도
    def kr_hex_sell_order(self):
        self.kiwoomAPI.kr_hex_sell_order()             

    # KR HEX 매수
    def kr_hex_buy_order(self):
        self.kiwoomAPI.kr_hex_buy_order()          


# ========== #    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    krHexMain = KrHexMain()

    # # 매도(08:30-09:00)   
    # krHexMain.kr_hex_sell_order() 

    # # 매수(15:20-15:30)    
    # krHexMain.hex_buy()

    # 수집(15:30)
    krHexMain.get_new_kr_hex_stock_data()