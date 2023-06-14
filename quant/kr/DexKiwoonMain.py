import sys
import DexKiwoomAPI
from PyQt5.QtWidgets import *


# ========== #
class DexKiwoonMain():
    def __init__(self):
        super().__init__()
        self.dexKiwoomAPI = DexKiwoomAPI.DexKiwoomAPI(DexKiwoomAPI.MyServer())
        self.dexKiwoomAPI.run()  
        self.dexKiwoomAPI.account()   
        # self.dexKiwoomAPI.deposit()  
        # self.dexKiwoomAPI.balance()    
        # self.dexCollector = DexCollector()        

    # 주식시분요청
    def opt10006(self):
        self.dexKiwoomAPI.opt10006()     

    # 상하한가요청
    def opt10017(self):
        self.dexKiwoomAPI.opt10017()

    # 주식분봉차트조회요청
    def opt10080(self):
        self.dexKiwoomAPI.opt10080()             

    # dex 매도
    def hex_sell(self):
        self.dexKiwoomAPI.hex_sell()             

    # dex 매수
    def hex_buy(self):
        self.dexKiwoomAPI.hex_buy()          


# ========== #    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    dexKiwoomMain = DexKiwoonMain()
    # dexKiwoomMain.hex_sell()  # 10:00
    dexKiwoomMain.hex_buy()
    # dexKiwoomMain.dexCollector()