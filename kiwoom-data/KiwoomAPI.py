from kiwoom import Bot, Server, config
from kiwoom.data.preps import prep
from kiwoom.utils import name
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from DBConnAPI import *
from KiwoomTrList import *
from Config import *
import time
import pandas as pd
from datetime import datetime


# ========== #
# 서버에 데이터를 요청하는 클래스
class KiwoomAPI(Bot):
    def __init__ (self, server=None):
        super().__init__(server)
        
        config.MUTE = True

        # DB 연결
        self.dBConnAPI = DBConnAPI()        

        # 변수 초기화
        self.acc_num = None  # 계좌번호      
        self.code_list = []  # 종목코드

        """
        # Bot(Signal), Server(Slot) and Event 연결과정
        # 1) KiwoomAPI 클래스에서 서버에 self.api.comm_connect() 함수를 통해 요청하면 
        # 2) 서버에서 응답이 오며 이 벤트인 self.api.on_event_connect() 함수가 호출된다.
        # 3) 따라서 self.api.on_event_connect() 호출되면, self.server.login() 함수가 호출될 수 있도록 연결해 준다.
        
        # 자세한 사항은 KOA Studio 개발가이드와 help(Kiwoom.connect) 참조
        # 'on_event_connect' 이벤트의 경우 자동으로 signal, slot이 설정되어 있음
        """
        self.api.connect(
            event='on_event_connect',
            signal=self.login,
            slot=self.server.login
        )      

        self.api.set_connect_hook('on_receive_tr_data', 'rq_name')
        self.api.connect('on_receive_tr_data', signal=self.deposit, slot=self.server.deposit)
        self.api.connect('on_receive_tr_data', signal=self.balance, slot=self.server.balance)   
        self.api.connect('on_receive_tr_data', signal=self.opt10032, slot=self.server.opt10032)  
        self.api.connect('on_receive_tr_data', signal=self.opt10001, slot=self.server.opt10001)  
        self.api.connect('on_receive_real_data', signal=self.insert_stock_data, slot=self.server.insert_stock_data)

    def run(self):
        """
        작성했던 코드 실행함수
        1) 로그인
        2) 로그인 상태 확인
        """
        print('KiwoomAPI.run() 호출')

        # 로그인 요청
        self.login()

        # 접속 성공여부 확인
        if not self.connected():
            raise RuntimeError(f'Server NOT connected.')
            # or you may exit script - import sys; sys.exit()

        # ... to be continued
        print('KiwoomAPI.run() 종료')

    def login(self):
        """
        로그인 요청함수
        * Note
        comm_connect 실행 시 on_connect_event 함수가 호출된다.
        이 함수는 사실 이미 KiwoomAPI 클래스에 간결하게 구현되어 있어서 다시 정의해 줄 필요는 없다.
        * KOA Studio 참고 가이드
        개발가이드 > 로그인 버전처리 > 관련함수 > CommConnect 참조
        """
        print('\tKiwoomAPI.login() 호출')

        # 연결 요청 API 가이드
        # help(Kiwoom.comm_connect)

        # 서버에 접속 요청
        self.api.comm_connect()

        # [필수] 이벤트가 호출될 때까지 대기 (on_event_connect)
        self.api.loop()

        print('\tKiwoomAPI.login() 종료')

    def connected(self):
        """
        로그인 상태확인 요청함수
        * Note
        GetConnectState 반환 값이 '0'이면 연결안됨, '1'이면 연결됨.
        * KOA Studio 참고 가이드
        개발가이드 > 로그인 버전처리 > 관련함수 > GetConnectState 참조
        :return: 연결상태 확인 후 연결되어 있다면 True, 그렇지 않다면 False
        """
        # 현재 접속상태 표시 API 가이드
        # help(Kiwoom.get_connect_state)
        # 0 (연결안됨), 1 (연결됨)

        state = self.api.get_connect_state()
        print(f'\t현재 접속상태 = {state}')

        if state == 1:
            return True  # 연결된 경우
        return False  # 연결되지 않은 경우
    
    def account(self):
        """
        기본적인 계좌 및 유저 정보 확인 요청함수
        * Note
        get_login_info 함수는 이벤트를 거치지 않고 즉시 요청값을 반환해주기 때문에,
        별도로 이벤트를 통해 요청한 데이터를 받아볼 수 있는 slot 함수와 api.loop()
        함수가 필요없다. 즉, Server 클래스의 사용이 필요없다.
        * KOA Studio 참고 가이드
        개발가이드 > 로그인 버전처리 > 관련함수 > GetLoginInfo
        """
        # 로그인 계좌 정보확인 API 개발가이드
        # help(Kiwoom.get_login_info)

        cnt = int(self.api.get_login_info('ACCOUNT_CNT'))  # 계좌개수
        accounts = self.api.get_login_info('ACCLIST').split(';')[:cnt]  # 계좌번호

        user_id = self.api.get_login_info('USER_ID')  # 유저아이디
        user_name = self.api.get_login_info('USER_NAME')  # 유저이름

        # 접속 서버 타입
        server = self.api.get_login_info('GetServerGubun')
        server = '모의투자' if server.strip() == '1' else '실서버'

        # 첫번 째 계좌 사용 (거래종목에 따라 확인)
        self.acc_num = accounts[0]

        return {  # 딕셔너리 리턴
            '계좌개수': cnt,
            '계좌번호': accounts,
            '유저아이디': user_id,
            '유저이름': user_name,
            '서버구분': server
        }

    def deposit(self):
        """
        예수금 정보 요청함수
        * Note
        comm_rq_data 실행 시 올바르게 요청했다면 on_receive_tr_data 함수가 호출된다.
        * KOA Studio 참고 가이드
        1) TR 목록 > opw00001 > INPUT
        2) 개발가이드 > 조회와 실시간데이터처리 > 관련함수 > SetInputValue
        3) 개발가이드 > 조회와 실시간데이터처리 > 관련함수 > CommRqData
        """
        print('KiwoomAPI.deposit() 호출')

        # 예수금상세현황요청 TR
        tr_code = 'opw00001'

        # 입력데이터
        inputs = {
            '계좌번호': self.acc_num,
            '비밀번호': '0000',
            '비밀번호입력매체구분': '00',
            '조회구분': '1'
        }

        # 요청 시 필요한 입력데이터 세팅함수 API 개발가이드
        # help(Kiwoom.set_input_value)
        for key, val in inputs.items():
            self.api.set_input_value(key, val)

        # TR Data 요청함수 API 개발가이드
        # > help(Kiwoom.comm_rq_data)
        # > comm_rq_data(rq_name, tr_code, prev_next, scr_no)
        self.api.comm_rq_data('deposit', tr_code, '0', '0000')

        # [필수] 'on_receive_tr_data' 이벤트가 호출 될 때까지 대기
        self.api.loop()

        print('KiwoomAPI.deposit() 종료')

    def balance(self, prev_next='0'):
        """
        계좌평가잔고내역 요청함수
        * Note
        comm_rq_data 실행 시 올바르게 요청했다면 on_receive_tr_data 함수가 호출된다.
        * KOA Studion 참고 가이드
        1) TR 목록 > opw00018 > INPUT
        2) 개발가이드 > 조회와 실시간데이터처리 > 관련함수 > SetInputValue
        3) 개발가이드 > 조회와 실시간데이터처리 > 관련함수 > CommRqData
        """
        print('KiwoomAPI.balance(prev_next) 호출')

        # 계좌평가잔고내역요청 TR
        tr_code = 'opw00018'

        # 입력데이터
        inputs = {
            '계좌번호': self.acc_num,
            '비밀번호': '0000',
            '비밀번호입력매체구분': '00',
            '조회구분': '1'
        }

        # 요청 시 필요한 입력데이터 세팅함수 API 개발가이드
        # > help(Kiwoom.set_input_value)
        for key, val in inputs.items():
            self.api.set_input_value(key, val)

        # TR Data 요청함수 API 개발가이드
        # > help(Kiwoom.comm_rq_data)
        # > comm_rq_data(rq_name, tr_code, prev_next, scr_no)
        self.api.comm_rq_data('balance', tr_code, prev_next, '0000')

        # [필수] on_receive_tr_data 이벤트가 호출 될 때까지 대기
        self.api.loop()

        print('KiwoomAPI.balance(prev_next) 종료')

    # Send orders of futures and options
    def trade(self):
        """
        실계좌일 경우 종목코드 입력하지 마세요.
        어떠한 경우에도 손실 책임지지 않습니다.
        """
        inputs = (
            'trade',     # rq_name
            '0000',      # 화면번호
            self.acc_num,    # 계좌번호
            '------',    # 입력금지!! (종목코드)
            1,           # 신규매매 (주문종류)
            2,           # Long (매매구분)
            3,           # 시장가 (거래구분)
            10,          # 주문수량
            '0',         # 주문가격
            '',          # 원주문번호
        )
        
        if self.api.get_login_info('GetServerGubun') != 1:
            print('실제 계좌이므로 주문하지 않습니다.')
            return

        if self.api.send_order_fo(*inputs) == 0:
            self.api.loop()
        else:
            # Do something to handle error
            raise RuntimeError(f'Sending order went wrong.')     

    # opt10032 TR 조회(거래대금상위요청)
    def opt10032(self, rq_name='opt10032', tr_code='opt10032', prev_next='0', scr_no='0101'):
        print('KiwoomAPI.opt10032(rq_name, tr_code, prev_next, scr_no) 호출')
        print('rq_name, tr_code, prev_next, scr_no : ', rq_name, tr_code, prev_next, scr_no)   

        # 시장구분 = 000:전체, 001:코스피, 101:코스닥
        self.api.set_input_value("시장구분", "000")

        # 관리종목포함 = 0:관리종목 미포함, 1:관리종목 포함
        self.api.set_input_value("관리종목포함"	, "0")

        # TR Data 요청함수 API 개발가이드
        # > help(Kiwoom.comm_rq_data)
        # > comm_rq_data(rq_name, tr_code, prev_next, scr_no)
        self.api.comm_rq_data(rq_name, tr_code, prev_next, scr_no)   

        # [필수] on_receive_tr_data 이벤트가 호출 될 때까지 대기
        self.api.loop()

        print('KiwoomAPI.opt10032(rq_name, tr_code, prev_next, scr_no) 종료')

    # opt10001 TR 조회(주식기본정보요청)
    def opt10001(self, rq_name='opt10001', tr_code='opt10001', prev_next='0', scr_no='0101'):
        print('KiwoomAPI.opt10001(rq_name, tr_code, prev_next, scr_no) 호출')   

        for code in self.code_list:
            self.api.set_input_value("종목코드", code)
        
            # TR Data 요청함수 API 개발가이드
            # > help(Kiwoom.comm_rq_data)
            # > comm_rq_data(rq_name, tr_code, prev_next, scr_no)           
            self.api.comm_rq_data(rq_name, tr_code, prev_next, scr_no)  

            # [필수] on_receive_tr_data 이벤트가 호출 될 때까지 대기
            self.api.loop()

            time.sleep(1)

        print('KiwoomAPI.opt10001(rq_name, tr_code, prev_next, scr_no) 종료')    

    # 종목 선정 조회
    def select_stock_list(self):
        print('KiwoomAPI.select_stock_list() 호출') 

        ret_data = self.dBConnAPI.select_stock_list()

        print('KiwoomAPI.select_stock_list() 종료')         

        return ret_data    

    # 실시간 데이터 조회
    def insert_stock_data(self, scr_no, code_list, fid_list, opt_type):
        print('KiwoomAPI.insert_stock_data(self, scr_no, code_list, fid_list, opt_type) 호출')  

        self.api.set_real_reg(scr_no, code_list, fid_list, opt_type)

        self.api.loop()

        print('KiwoomAPI.insert_stock_data(self, scr_no, code_list, fid_list, opt_type) 종료')  

    # 호가 데이터 개수 조회
    def select_stock_hoga_cnt(self):
        print('KiwoomAPI.select_stock_hoga_cnt() 호출') 

        ret_data = self.dBConnAPI.select_stock_hoga_cnt()

        print('KiwoomAPI.select_stock_hoga_cnt() 종료')         

        return ret_data        
    
    # 체결 데이터 개수 조회
    def select_stock_chegyeol_cnt(self):
        print('KiwoomAPI.select_stock_chegyeol_cnt() 호출') 

        ret_data = self.dBConnAPI.select_stock_chegyeol_cnt()

        print('KiwoomAPI.select_stock_chegyeol_cnt() 종료')         

        return ret_data       

    def get_kospi_kosdaq_stock_list(self):
        print('KiwoomAPI.get_kospi_kosdaq_stock_list() 호출') 

        kr_stock_list = []

        kospi_list = self.api.get_code_list_by_market("0")
        kospi_stock_list = kospi_list.split(";")[:-1]

        # print("kospi_stock_list : " + str(kospi_stock_list))

        kosdaq_list = self.api.get_code_list_by_market("10")
        kosdaq_stock_list = kosdaq_list.split(";")[:-1]

        # print("kosdaq_stock_list : " + str(kosdaq_stock_list))

        kr_stock_list = kospi_stock_list + kosdaq_stock_list

        # print("kr_stock_list : " + str(kr_stock_list))

        print('KiwoomAPI.get_kospi_kosdaq_stock_list() 종료')     

        return kr_stock_list 

# ============================================== #
# 서버에서 데이터를 받아 처리하는 클래스
class MyServer(Server):
    def __init__(self):
        """
        Server Class 초기화 함수
        1) KiwoomAPI Class와 Kiwoom(), Share() 클래스의 인스턴스를 공유한다.
            - self.api, self.share = Kiwoom(), Share()
            - KiwoomAPI 클래스를 초기화 할 때 공유된다.
            > Bot.__init__(sever=Server())
        2) 사용할 변수들을 초기화 한다.
            - self.downloading
        """
        super().__init__()

        # KiwoomAPI 클래스를 초기화 할 때 다음 두 변수가 자동 설정됨
        # self.api = Kiwoom()
        # self.share = Share()

        # DB 연결
        self.dBConnAPI = DBConnAPI.DBConnAPI()    

        # 변수 초기화
        self.downloading = False
        self.checking = False
        self.is_searching_enabled = True
        self.ret_data = {}   
        self.ret_data_list = []
        self.ret_data_dict = {}    
        self.is_insert_stock_data_enabled = False  # opt10001 요청 시 insert_stock_data 호출되는 오류 해결

    def login(self, err_code):
        """
        Signal.login() 함수로 인해 OnEventConnect 이벤트 발생 시 로그인 메세지 처리함수
        * Note
        comm_connect 실행 결과로 on_event_connect 이벤트 함수가 호출될 때 이 함수가 호출되도록 한다.
        >> self.api.connect(event='on_event_connect', signal=self.login, slot=self.server.login)  # 31번째 줄 참고
        * KOA Studio 참고 가이드
        개발가이드 > 로그인 버전처리 > 관련함수 > OnEventConnect 참조
        """
        print('\t\tServer.login(err_code) 호출')

        # 접속 요청 시 발생하는 이벤트 API 가이드
        # help(Kiwoom.on_event_connect)

        # 에러 메세지 출력 함수 가이드
        # help(kiwoom.config.error.msg)

        # err_code에 해당하는 메세지
        emsg = config.error.msg(err_code)

        # 로그인 성공/실패 출력
        print(f'\t\tLogin ({emsg})')

        # [필수] 이벤트를 기다리며 대기중이었던 코드 실행 (60번째 줄)
        self.api.unloop()

        print('\t\tServer.login(err_code) 종료')

    def deposit(self, _, rq_name, tr_code, __, ___):
        """
        KiwoomAPI.deposit() 함수로 인해 OnReceiveTrData 이벤트 발생 시 예수금 데이터 처리함수
        * Note
        KiwoomAPI.deposit 함수에서 comm_rq_data(..., rq_name='deposit', ...) 함수 호출로 인해,
        on_receive_tr_data 이벤트 함수가 호출될 때 이 함수가 호출되도록 한다.  # 319 번째 줄 참고
        >> self.api.connect('on_receive_tr_data', signal=self.signal.deposit, slot=self.slot.deposit)
        * KOA Studio 참고 가이드
        1) TR 목록 > opw00001 > INPUT
        2) 개발가이드 > 조회와 실시간데이터처리 > 관련함수 > GetCommData
        3) 개발가이드 > 조회와 실시간데이터처리 > 관련함수 > OnReceiveTrData
        """
        print('\tServer.deposit(scr_no, rq_name, tr_code, record_name, prev_next) 호출')

        # 예수금 데이터 저장
        self.share.update_single('deposit', '예수금', int(self.api.get_comm_data(tr_code, rq_name, 0, '예수금')))

        # [필수] 대기중인 코드 실행 (177번째 줄)
        self.api.unloop()

        print('\tServer.deposit(scr_no, rq_name, tr_code, record_name, prev_next) 종료')

    def balance(self, scr_no, rq_name, tr_code, record_name, prev_next):
        """
        Signal.balance() 함수로 인해 OnReceiveTrData 이벤트 발생 시 계좌평가잔고내역 데이터 처리함수
        * Note
        Signal.balance 함수에서 comm_rq_data(..., rq_name='balance', ...) 함수 호출로 인해,
        on_receive_tr_data 이벤트 함수가 호출될 때 이 함수가 호출되도록 한다.  # 98 번째 줄 참고
        >> self.api.connect('on_receive_tr_data', signal=KiwoomAPI.balance, slot=self.server.balance)
        * KOA Studio 참고 가이드
        1) TR 목록 > opw00018 > INPUT
        2) 개발가이드 > 조회와 실시간데이터처리 > 관련함수 > GetCommData
        3) 개발가이드 > 조회와 실시간데이터처리 > 관련함수 > GetRepeatCnt
        3) 개발가이드 > 조회와 실시간데이터처리 > 관련함수 > OnReceiveTrData
        """
        print('\tServer.balance(scr_no, rq_name, tr_code, record_name, prev_next) 호출')

        # TR 데이터 수신 API 개발가이드
        # help(Kiwoom.on_receive_tr_data)

        # 다운로드 시작을 위한 변수 초기화
        if not self.downloading:
            self.downloading = True

        # 멀티데이터 저장
        keys = ['종목번호', '종목명', '평가손익', '수익률(%)', '보유수량', '매입가', '현재가']
        data = {key: list() for key in keys}
        cnt = self.api.get_repeat_cnt(tr_code, rq_name)
        for i in range(cnt):
            for key in keys:
                val = prep(self.api.get_comm_data(tr_code, rq_name, i, key))
                data[key].append(val)

        # 봇 인스턴스와 데이터 공유
        for key in keys:
            self.share.extend_multi('balance', key, data[key])

        # 만일, 데이터가 더 있다면 signal 함수 한번 더 호출 (종목 수 25개 이상인 경우)
        if prev_next == '2':
            fn = self.api.signal('on_receive_tr_data', 'balance')
            fn(prev_next)  # call signal function again to receive remaining data

        # 요청 할 데이터가 더 없는 경우
        else:
            # Single 데이터 저장
            for key in ['총평가손익금액', '총수익률(%)']:
                val = prep(self.api.get_comm_data(tr_code, rq_name, 0, key))
                self.share.update_single(name(), key, val)  # name() = 'balance'

            # 다운로드 완료
            self.downloading = False
            self.api.unloop()  # 216번 째 줄 실행

            print('\tServer.balance(scr_no, rq_name, tr_code, record_name, prev_next) 종료')        

     # Mapped by hook, if rq_name='trade' when on_receive_tr_data() is called.
    def trade(self, scr_no, rq_name, tr_code, record_name, prev_next):
        num = self.api.get_comm_data(tr_code, rq_name, 0, '주문번호').strip()
        if num == '':
            self.api.unloop()
            raise RuntimeError('Executing order failed.')
        
        # Order filled.
        pass
    
    # opt10032 TR 조회(거래대금상위요청)
    def opt10032(self, scr_no, rq_name, tr_code, record_name, prev_next):
        print('\tServer.opt10032(self, scr_no, rq_name, tr_code, record_name, prev_next) 호출')
        print("\tscr_no, rq_name, tr_code, record_name, prev_next : ", scr_no, rq_name, tr_code, record_name, prev_next)

        # 변수 초기화
        self.ret_data[tr_code] = {}
        self.ret_data[tr_code]['Data'] = {} 

        # 멀티데이터 저장
        keys = opt10032_list[tr_code]
        data = {key: list() for key in keys}
        
        cnt = self.api.get_repeat_cnt(tr_code, rq_name)

        for i in range(cnt):
            for key in keys:
                val = self.api.get_comm_data(tr_code, rq_name, i, key).strip()
                data[key].append(val)

        # 봇 인스턴스와 데이터 공유
        for key in keys:
            self.share.extend_multi(rq_name, key, data[key])

        # 만일, 데이터가 더 있다면 signal 함수 한번 더 호출 (종목 수 25개 이상인 경우)
        if prev_next == '2':
            self.is_searching_enabled = False
            fn = self.api.signal('on_receive_tr_data', rq_name)
            fn(prev_next) # call signal function again to receive remaining data

        ## 요청 할 데이터가 더 없는 경우
        else:
            # Single 데이터 저장
            for key in keys:
                val = self.api.get_comm_data(tr_code, rq_name, 0, key).strip()
                self.share.update_single(name(), key, val)  # name() = 'balance'

        self.ret_data[tr_code]['Data'] = data 
        print(" ===> self.ret_data[tr_code]['Data']['종목명'] : ", self.ret_data[tr_code]['Data']['종목명'])

        # 이벤트 루프 종료
        self.api.unloop()             

        # data = pd.DataFrame(data) 
        # out_name = "거래대금상위요청.xlsx"
        # data.to_excel('C:/Users/Choi Heewon/thredart/db/'+out_name)            

        print('\tServer.opt10032(scr_no, rq_name, tr_code, record_name, prev_next) 종료')    

    # opt10001 TR 조회(주식기본정보요청)
    def opt10001(self, scr_no, rq_name, tr_code, record_name, prev_next):
        print('\tServer.opt10001(self, scr_no, rq_name, tr_code, record_name, prev_next) 호출')
        
        # 변수 초기화
        self.ret_data[tr_code] = {}
        self.ret_data[tr_code]['Data'] = {}   
        self.ret_stock_df = pd.DataFrame()
        self.checking = False

        # 멀티데이터 저장
        keys = opt10001_list[tr_code]  #['종목코드', '종목명', '결산월', '액면가', '자본금', '상장주식', '신용비율', '연중최고', '시가총액', '시가총액비중', '외인소진률', '대용가PER', 'EPS', 'ROE', 'PBR', 'EV', 'BPS', '매출 액', '영업이익', '당기순이익', '250최고', '250최저', '시가', '고가', '저가', '상한가', '하한가', '기준가', '예상체결가', '예상체결수량', '250최 고가일', '250최고가대비율', '250최저가일', '250 최저가대비율', '현재가', '대비기호', '전일대비', '등락율', '거래량', '거래대비', '액면가단위', '유통주식', '유통비율']
        data = {key: list() for key in keys}

        captial = self.api.get_comm_data(tr_code, rq_name, 0, '시가총액').strip()
        rate = self.api.get_comm_data(tr_code, rq_name, 0, '등락율').strip()
        ticker_nm = self.api.get_comm_data(tr_code, rq_name, 0, '종목명').strip()

        # 시총10억이상, 8000억이하, 등락율 0.00이상 
        if 'KODEX' not in ticker_nm and 'TIGER' not in ticker_nm and '미래에셋' not in ticker_nm and 'KBSTAR' not in ticker_nm and '삼성' not in ticker_nm:
            if captial and rate and int(captial) >= 10 and int(captial) <= 8000 and float(rate) > 0.00:
                self.checking = True
                for key in keys:
                    val = self.api.get_comm_data(tr_code, rq_name, 0, key).strip()
                    self.ret_data_dict[key] = val  #{'종목코드': '131400', '종목명': '이브이첨단소재', '결산월': '12', '액면가': '500', '자본 금': '241', '상장주식': '48167', '신용비율': '+1.33', '연중최고': '+8890', '시가총액': '3863', '시가총액비중': '', '외인소진률': '+0.58', '대용 가PER': '', 'EPS': '-306', 'ROE': '-17.6', 'PBR': '3.95', 'EV': '517.83', 'BPS': '2032', '매출액': '581', '영업이익': '-29', '당기순이익': '-107', '250최고': '+8890', '250최저': '-951', '시가': '-6700', '고가': '+8890', '저가': '-5300', '상한가': '+9540', '하한가': '-5140', '기준가': '7340', '예상체결가': '-0', '예상체결수량': '0', '250최고가일': '20230413', '250최고가대비율': '-9.79', '250최저가일': '20221208', '250최저가대비율': '+743.32', '현재가': '+8020', '대비기호': '2', '전일대비': '+680', '등락율': '+9.26', '거래량': '56217298', '거래대비': '0.00', '액면가단위': '원', '유통주식': '43347', '유통비율': '90.0'}
                    data[key].append(val)  #{'종목코드': ['131400'], '종목명': ['이브이첨단소재'], '결산월': ['12'], '액면가': ['500'], '자본금': ['241'], '상장주식': ['48167'], '신용비율': ['+1.33'], '연중최고': ['+8890'], '시가총액': ['3839'], '시가총액비중': [''], '외인소진률': ['+0.58'], '대용가PER': [''], 'EPS': ['-306'], 'ROE': ['-17.6'], 'PBR': ['3.92'], 'EV': ['514.77'], 'BPS': ['2032'], '매출액': ['581'], '영업이익': ['-29'], '당기순이익': ['-107'], '250최고': ['+8890'], '250최저': ['-951'], '시가': ['-6700'], '고가': ['+8890'], '저가': ['-5300'], '상한가': ['+9540'], '하한가': ['-5140'], '기준 가': ['7340'], '예상체결가': ['-0'], '예상체결수량': ['0'], '250최고가일': ['20230413'], '250최 고가대비율': ['-10.35'], '250최저가일': ['20221208'], '250최저가대비율': ['+738.07'], '현재가': ['+7970'], '대비기호': ['2'], '전일대비': ['+630'], '등락율': ['+8.58'], '거래량': ['56329076'], '거래대비': ['0.00'], '액면가단위': ['원'], '유통주식': ['43347'], '유통비율': ['90.0']}      

                # DB 저장
                self.ret_stock_df = pd.DataFrame.from_dict(self.ret_data_dict, orient='index').T
                for i, row in self.ret_stock_df.iterrows():
                    # print("i, row : ", i, row)
                    self.dBConnAPI.insert_stock_list(row)

        # data의 key 값이 있을 때 실행할 코드
        if self.checking:
            self.ret_data_list.append(data)
            self.ret_data[tr_code]['Data'] = self.ret_data_list

        # 이벤트 루프 종료
        self.api.unloop()

        print('\tServer.opt10001(self, screen_no, rq_name, tr_code, record_name, prev_next) 종료')  

    # 실시간 호가 및 체결 데이터 조회
    def insert_stock_data(self, code, real_type, real_data):
        # print('\tServer.insert_stock_data(self, code, real_type, real_data) 호출')
        # print('\t\t', self.is_insert_stock_data_enabled)

        if not self.is_insert_stock_data_enabled:
            return

        real_data_list = real_data.split()
        del real_data_list[0]  # current_time(HHMMSS) 삭제
        real_data_list.insert(0, code)  # code(종목코드) 추가        

        if real_type == "주식체결":
            keys = stock_chegyeol_list['stock_chegyeol']
            data = {key: list() for key in keys}

            ret_data_list = []  #  real_data_list의 종목코드, 체결가, 체결량만 담을 리스트 선언
            ret_data_list.append(code)  # 종목코드
            ret_data_list.append(real_data_list[1])  # 체결가
            ret_data_list.append(real_data_list[6])  # 체결량

            i = 0
            for key in keys:
                val = ret_data_list[i]  
                data[key].append(val)
                i = i + 1

            # DB 저장
            ret_df = pd.DataFrame.from_dict(data)
            for i, row in ret_df.iterrows():
                self.dBConnAPI.insert_stock_chegyeol(row)            

        elif real_type == "주식호가잔량":
            keys = stock_hoga_list['stock_hoga']
            data = {key: list() for key in keys}

            i = 0
            for key in keys:
                val = real_data_list[i]
                data[key].append(val)
                i = i + 1

            # DB 저장
            ret_df = pd.DataFrame.from_dict(data)
            for i, row in ret_df.iterrows():
                self.dBConnAPI.insert_stock_hoga(row)

        # 오전 11시시 프로그램 종료
        if datetime.now().strftime("%H:%M:%S") == END_TIME:
            self.api.unloop()

        # print('\tServer.insert_stock_data(self, code, real_type, real_data) 종료')