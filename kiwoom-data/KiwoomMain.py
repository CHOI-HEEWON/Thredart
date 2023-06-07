from KiwoomTrList import *
from Config import *
from PyQt5.QtWidgets import *
import KiwoomAPI, ThredartBot
import sys, time, datetime, schedule


# ========== #
class KiwoonMain():
    def __init__(self):
        super().__init__()

        self.KiwoomAPI = KiwoomAPI.KiwoomAPI(KiwoomAPI.MyServer())
        self.KiwoomAPI.run()   
        self.KiwoomAPI.account()    

        self.thredartBot = ThredartBot.ThredartBot()  
        self.today_date = datetime.date.today().strftime("%Y-%m-%d")


# ========== #        
    # 거래대금상위요청
    def opt10032(self):
        self.KiwoomAPI.opt10032()

        return self.KiwoomAPI.server.ret_data['opt10032']
    
    # 주식기본정보요청
    def opt10001(self, code_list):
        self.KiwoomAPI.code_list = code_list
        self.KiwoomAPI.opt10001()

        return self.KiwoomAPI.server.ret_data['opt10001']


# ========== #    
    # 종목 선정(거래대금상위 중 시총10억이상, 8000억이하, 등락율 0.00이상 조회)
    def get_stock_list(self):
        # threading.Timer(60*5, kiwoomMain.SelectionStockEvent).start() # 5분에 한번씩 호출
        try:
            ret_data = kiwoomMain.opt10032()
            code_list = ret_data['Data']['종목코드']

            kiwoomMain.opt10001(code_list)

            code_list, ticker_nm = self.KiwoomAPI.select_stock_list()  # 선정된 종목 조회
            code_list_cnt = len(code_list)
            code_data = "\n".join([code + " " + name for code, name in zip(code_list, ticker_nm)])

            kiwoomMain.sendMsgToThredartBot(kiwoomMain.today_date +" 종목코드 (" + str(code_list_cnt) + "개)\n" + str(code_data)) 

            return code_list 
        
        except Exception as e:
            kiwoomMain.sendMsgToThredartBot("Error occurred in get_stock_list: " + e)      

    # Kospi, Kosdaq 전종목 조회
    def get_kospi_kosdaq_stock_list(self):
        try:
            kr_stock_list = self.KiwoomAPI.get_kospi_kosdaq_stock_list()  # 선정된 종목 조회

            return kr_stock_list 
        
        except Exception as e:
            kiwoomMain.sendMsgToThredartBot("Error occurred in get_stock_list: " + e)                      
    
    # 실시간 호가 및 체결 데이터 조회
    def get_stock_data(self, stock_list):
        try:
            kiwoomMain.sendMsgToThredartBot(kiwoomMain.today_date +" 실시간 호가 및 체결 데이터 수집 중") 

            self.KiwoomAPI.server.is_insert_stock_data_enabled = True

            sScreenNo = "0001"
            sFidList = "10;15;30;41;61;71;81;51;62;72;82;52;63;73;83;53;64;74;84;54;65;75;85;55;66;76;86;56;67;77;87;57;68;78;88;58;69;79;89;59;70;80;90;200;201;291;292;293;294;295"
            sRealType = "0"        
            self.KiwoomAPI.insert_stock_data(sScreenNo, ";".join(stock_list), sFidList, sRealType)
        
        except Exception as e:
            kiwoomMain.sendMsgToThredartBot("Error occurred in get_stock_data: " + e)    

    # 당일 호가 및 체결 데이터 수집 개수 조회
    def get_data_cnt(self):
        stock_hoga_cnt = self.KiwoomAPI.select_stock_hoga_cnt()
        stock_chegyeol_cnt = self.KiwoomAPI.select_stock_chegyeol_cnt()
        kiwoomMain.sendMsgToThredartBot(kiwoomMain.today_date +" 데이터 수집 개수\n호가 데이터 : " + str(stock_hoga_cnt) + "(개)\n체결 데이터 : " + str(stock_chegyeol_cnt)+ "(개)")

    # ThredartBot 메시지 전송
    def sendMsgToThredartBot(self, msg):
        self.thredartBot.sendMessage(msg)       
        

# ========== # 
    # 스케줄링 함수 정의
    def schedule_job(self):
        # 오전 9시 프로그램 시작
        schedule.every().day.at(START_TIME).do(kiwoomMain.main)  

        while True:
            schedule.run_pending()
            time.sleep(1)


# ========== #          
    def main(self):
        self.sendMsgToThredartBot(kiwoomMain.today_date +" Kiwoom 데이터 수집 시작")
        # code_list = kiwoomMain.get_stock_list()
        stock_list = kiwoomMain.get_kospi_kosdaq_stock_list()

        if stock_list:
            kiwoomMain.get_stock_data(stock_list)

        kiwoomMain.get_data_cnt()
        kiwoomMain.stop_main()
       
    def stop_main(self):
        kiwoomMain.sendMsgToThredartBot(kiwoomMain.today_date +" Kiwoom 데이터 수집 종료")
        sys.exit()


# ========== #    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    kiwoomMain = KiwoonMain()
    kiwoomMain.schedule_job()
    # kiwoomMain.main()
 
