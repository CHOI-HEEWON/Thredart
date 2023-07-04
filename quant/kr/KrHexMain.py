import sys
import KrHexAPI, KrHexCollector
from PyQt5.QtWidgets import *


# ========== #
class KrHexMain:
    def __init__(self):
        super().__init__()
        
        self.krHexAPI = KrHexAPI.KrHexAPI(KrHexAPI.MyServer())
        self.krHexAPI.run()  
        self.krHexAPI.account()   
        # self.krHexAPI.deposit()  
        # self.krHexAPI.balance()    

        self.krHexCollector = KrHexCollector.KrHexCollector()        

    # # 주식시분요청
    # def opt10006(self):
    #     self.krHexAPI.opt10006()     

    # # 주식분봉차트조회요청
    # def opt10080(self):
    #     self.krHexAPI.opt10080()    

    # # 상하한가요청
    # def opt10017(self):
    #     self.krHexAPI.opt10017()

    # 상한가 새 데이터 조회, INSERT, UPDATE
    def get_new_kr_hex_stock_data(self):
        self.krHexCollector.get_new_kr_hex_stock_data()

    # krHex 매도
    def kr_hex_sell(self):
        self.krHexAPI.kr_hex_sell()             

    # krHex 매수
    def kr_hex_buy(self):
        self.krHexAPI.kr_hex_buy()          


# ========== #    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    krHexMain = KrHexMain()

    # # 매도(08:30-09:00)   
    # krHexMain.kr_hex_sell() 

    # # 매수(15:20-15:30)    
    # krHexMain.hex_buy()

    # 수집(15:30)
    krHexMain.get_new_kr_hex_stock_data()