from kiwoom import Bot, Server, config
from kiwoom.data.preps import prep
from kiwoom.utils import name
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import DexDBConnAPI
import pandas as pd
from DexKiwoomTrList import *
from textwrap import dedent
import time


# ========== #
# 서버에 데이터를 요청하는 클래스
class DexKiwoomAPI(Bot):
    def __init__ (self, server=None):
        super().__init__(server)
        config.MUTE = True
        self.dexDBConnAPI = DexDBConnAPI.DexDBConnAPI()   
        self.acc = None

        self.api.connect(
            event='on_event_connect',
            signal=self.login,
            slot=self.server.login
        )      

        self.api.set_connect_hook('on_receive_tr_data', 'rq_name')
        self.api.connect('on_receive_tr_data', signal=self.deposit, slot=self.server.deposit)
        self.api.connect('on_receive_tr_data', signal=self.balance, slot=self.server.balance)
        self.api.connect('on_receive_tr_data', signal=self.trade_sell, slot=self.server.trade)
        self.api.connect('on_receive_tr_data', signal=self.trade_buy, slot=self.server.trade)        
        self.api.connect('on_receive_chejan_data', slot=self.server.chejan)  # without hook   

        self.api.connect('on_receive_tr_data', signal=self.opt10006 , slot=self.server.opt10006)
        self.api.connect('on_receive_tr_data', signal=self.opt10017 , slot=self.server.opt10017)
        self.api.connect('on_receive_tr_data', signal=self.opt10075 , slot=self.server.opt10075)
        self.api.connect('on_receive_tr_data', signal=self.opt10080 , slot=self.server.opt10080)
        
    def run(self):
        print('DexKiwoomAPI.run() 호출')

        self.login()    

        # 계좌 정보 출력
        # info = self.account()
        # print('-- 계좌 정보 --')
        # for key, val in info.items():
        #     print(f'{key}: {val}')      
        # 
        
        print('DexKiwoomAPI.run() 종료')

    def login(self):
        print('\tDexKiwoomAPI.login() 호출')

        self.api.comm_connect()
        self.api.loop()

        print('\tDexKiwoomAPI.login() 종료')

    def account(self):
        # 로그인 계좌 정보확인 API 개발가이드
        # help(self.api.get_login_info)

        cnt = int(self.api.get_login_info('ACCOUNT_CNT'))  # 계좌개수
        accounts = self.api.get_login_info('ACCLIST').split(';')[:cnt]  # 계좌번호 => ['6154119010', '6154119131', '6154119271', '6154119372', '6154119480']

        user_id = self.api.get_login_info('USER_ID')  # 유저아이디
        user_name = self.api.get_login_info('USER_NAME')  # 유저이름
        server = '실서버'  # 접속 서버 타입
        self.acc = accounts[0]  # 첫번 째 계좌 사용 (거래종목에 따라 확인)

        return {  # 딕셔너리 리턴
            '계좌개수': cnt,
            '계좌번호': accounts,
            '유저아이디': user_id,
            '유저이름': user_name,
            '서버구분': server
        }

    def deposit(self):
        print('Bot.deposit() 호출')

        # 예수금상세현황요청 TR
        tr_code = 'opw00001'

        # 입력데이터
        inputs = {
            '계좌번호': self.acc,
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

        print('\n-- 예수금확인 --')
        print(f"\n예수금 : {format(self.share.get_single('deposit', '예수금'), ',')}원")            

        print('Bot.deposit() 종료')

    def balance(self, prev_next='0'):
        print('Bot.balance(prev_next) 호출')

        # 계좌평가잔고내역요청 TR
        tr_code = 'opw00018'

        # 입력데이터
        inputs = {
            '계좌번호': self.acc,
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

        print('\n-- 계좌잔고확인 --')
        print(dedent(
            f"""
            Single Data: 
                총수익률(%) = {self.share.get_single('balance', '총수익률(%)')}%
                총평가손익금액 = {self.share.get_single('balance', '총평가손익금액')}원
            """
        ))
        print(f"Multi Data: {self.share.get_multi('balance', key=None)}")        

        print('Bot.balance(prev_next) 종료') 
    
    # 주식시분요청
    def opt10006(self, ticker, rq_name='opt10006', tr_code='opt10006', prev_next='0', scr_no='0101'):
        print('DexKiwoomAPI.opt10006(rq_name, tr_code, prev_next, scr_no) 호출')

        self.api.set_input_value("종목코드", ticker)

        self.api.comm_rq_data(rq_name, tr_code, prev_next, scr_no)

        self.api.loop()

        print('DexKiwoomAPI.opt10006(rq_name, tr_code, prev_next, scr_no) 종료')

    # 상하한가요청
    def opt10017(self, rq_name='opt10017', tr_code='opt10017', prev_next='0', scr_no='0101'):
        print('DexKiwoomAPI.opt10017(rq_name, tr_code, prev_next, scr_no) 호출')

        self.api.set_input_value("시장구분", "000")
        self.api.set_input_value("상하한구분", "1")
        self.api.set_input_value("종목조건", "1")

        self.api.comm_rq_data(rq_name, tr_code, prev_next, scr_no)   

        self.api.loop()

        print('DexKiwoomAPI.opt10017(rq_name, tr_code, prev_next, scr_no) 종료')

    # 미체결요청
    def opt10075(self, ticker, rq_name='opt10075', tr_code='opt10075', prev_next='0', scr_no='0101'):
        print('DexKiwoomAPI.opt10075(rq_name, tr_code, prev_next, scr_no) 호출')

        self.api.set_input_value("계좌번호", self.acc)
        self.api.set_input_value("전체종목구분", "0")  # 0:전체, 1:주식
        self.api.set_input_value("매매구분", "2")  # 0:전체, 1:매도, 2:매수
        self.api.set_input_value("종목코드", ticker)
        self.api.set_input_value("체결구분", "1")  # 0:전체, 2:체결, 1:미체결

        self.api.comm_rq_data(rq_name, tr_code, prev_next, scr_no)   

        self.api.loop()

        print('DexKiwoomAPI.opt10075(rq_name, tr_code, prev_next, scr_no) 종료')

    # 주식분봉차트조회요청
    def opt10080(self, rq_name='opt10080', tr_code='opt10080', prev_next='0', scr_no='0101'):
        print('DexKiwoomAPI.opt10080(rq_name, tr_code, prev_next, scr_no) 호출')
        # print('rq_name, tr_code, prev_next, scr_no : ', rq_name, tr_code, prev_next, scr_no) 
        # '030790', '269620, 019490
        ticker_list = ['222420','299170','333050','115610','137940','015020','014970','378800','257720','425290','104040','234300','290520','052690','014990','101140','115530','320000','096350','291810','377300','007980','249420','143210','288980','023900','076080','068940','030350','003075','058430','351320','019175','270520','099750','226360','008290','066410','219550','080720','214390','005110','152550','304100','330350','005965','008870','033320','377450','006140','053950','419530','121800','417180','347770','002990','002995','037440','425290','001745','053590','389260','004105','380540','032685','036030','025620','036810','189330','277810','402030','039010','093640','417860','373200','086960','277070','367000','016880','315640','086900','394280','388790','355150','005420','112040','123420','208370','028080','389500','348340','064480','001430','175250','214680','041020','009520','121850','227950','234920','115500','322180','282720','006110','317830','008500','051780','096630','114190','058450','051980','074610','294630','127980','096775','259630','025820','003075','245620','000910','004565','012320','033790','137940','317770','052670','204630','900300','024810','042040','073640','065150','054220','131400','091340','093230','000760','001000','023960','119650','312610','332290','011230','101000','009320','044180','109960','263920','139050','056730','263810','014910','038870','388790','050090','417500','001795','123700','950140','900250','065500','059210','069640','021880','145210','195990','317530','073640','146320','219550','000725','009440','189330','372800','060310','290690','059270','203690','060900','012030','053610','290270','357550','006200','048410','291650','405920','277410','014990','007540','250000']
        # for ticker in ticker_list:
        for ticker in ticker_list:

            print(ticker)

            time.sleep(1)

            self.api.set_input_value("종목코드", ticker)  # 종목 코드 입력
            self.api.set_input_value("틱범위", "60")  # 분봉 간격 입력 (1, 3, 5, 10, 15, 30, 45, 60 중 선택)
            self.api.set_input_value("수정주가구분", "0")  # 수정주가구분 (0: 무수정주가, 1: 수정주가)

            self.api.comm_rq_data(rq_name, tr_code, prev_next, scr_no)

            self.api.loop()

        print('DexKiwoomAPI.opt10080(rq_name, tr_code, prev_next, scr_no) 종료')

    # hex 매도
    def hex_sell(self):    
        print('DexKiwoomAPI.hex_sell(self) 호출')

        hex_date, ticker_list = self.dexDBConnAPI.select_hex_ticker_order_status_1()

        if len(ticker_list) > 0:
            for hex_date, ticker in zip(hex_date, ticker_list):
                print("\tticker : " + str(ticker))
                print("\thex_date : " + str(hex_date))

                self.opt10006(ticker)
                price = self.server.ret_data['opt10006']['Data']['종가']
                
                self.opt10075(ticker)
                qty = self.server.ret_data['opt10006']['Data']['주문수량']

                print("\tprice : " + str(price))                
                print("\tqty : " + str(qty))

                self.trade_sell(ticker, qty, price)  # 매도

                row = {'날짜': hex_date, '종목코드': ticker}
                self.dexDBConnAPI.update_hex_ticker_order_status_2(row)

        print('DexKiwoomAPI.hex_sell(self) 종료')

    def trade_sell(self, ticker, qty, price):
        print('DexKiwoomAPI.trade_sell(self, ticker, qty, price) 호출')

        sell_inputs = (
            '매도주문',       # 사용자 구분명
            '0000',          # 화면번호
            self.acc,        # 계좌번호
            ticker,          # 종목코드
            1,               # 주문종류 1:신규매매, 2:정정, 3:취소
            1,               # 매매구분	1:매도, 2:매수
            3,               # 거래구분 1:지정가, 2:조건부지정가, 3:시장가, 4:최유리지정가, 5:지정가(IOC), 6:지정가(FOK), 7:시장가(IOC), 8:시장가(FOK), 9:최유리지정가(IOC), A : 최유리지정가(FOK), 장종료 후 시간외 주문은 지정가 선택
            qty,             # 주문수량
            price,           # 주문가격
            '',              # 원주문번호
        )

        if self.api.get_login_info('GetServerGubun') != 1:
            print('실제 계좌이므로 주문하지 않습니다.')
            return

        # 매수 주문 실행
        if self.api.send_order_fo(*sell_inputs) == 0:
            self.api.loop()
        else:
            # Do something to handle error
            raise RuntimeError(f'Sending buy order went wrong.')
        
        print('DexKiwoomAPI.trade_sell(self, ticker, qty, price) 종료')

    # hex 매수
    def hex_buy(self):      
        print('DexKiwoomAPI.hex_buy(self) 호출')

        score = 0
        ticker_list = []
        
        ticker, d_2_v, d_1_v, d0_v, d0_high_price = self.dexDBConnAPI.select_hex_ticker()

        for ticker, d_2_v, d_1_v, d0_v, d0_high_price in zip(ticker, d_2_v, d_1_v, d0_v, d0_high_price):
            print("ticker: " + ticker)

            self.opt10006(ticker)
            close_price = self.server.ret_data['opt10006']['Data']['종가']
            low_price = self.server.ret_data['opt10006']['Data']['저가']

            print("close_price: " + str(close_price))
            print("low_price: " + str(low_price))

            # FACTOR. A
            if (d_2_v < d_1_v and d_1_v > d0_v) or (d_2_v > d_1_v and d_1_v > d0_v):
                score += 2

            # FACTOR. E
            if d_1_v > d0_v * 0.75:
                score += 1           

            # FACTOR. F
            if not (d_2_v < d_1_v and d_1_v < d0_v):
                score += 1       

            print(str(ticker) + ' = ' + str(score))

            if score >= 2:  # 합산 2점 이상 종목만 매매
                ticker_list.append(ticker)   

        print("ticker_list : " + str(ticker_list))  

        # for ticker in ticker_list:
        #     self.trade_buy(ticker, qty, buy_price)  # 매수   

        print('DexKiwoomAPI.hex_buy(self) 종료')

    def trade_buy(self, ticker, qty, price):
        print('DexKiwoomAPI.trade_buy(self, ticker, qty, price) 호출')

        stoploss_percent = 0.07  # 스톱로스 가격 계산을 위한 감소 비율 (7%를 나타내는 경우)
        stoploss_price = price - (price * stoploss_percent)  # 스톱로스 가격 계산

        buy_inputs = (
            '매수주문',       # 사용자 구분명
            '0000',          # 화면번호
            self.acc,        # 계좌번호
            ticker,          # 종목코드
            1,               # 신규매매 (주문종류)
            2,               # 매매구분	1:매도, 2:매수
            3,               # 거래구분 1:지정가, 2:조건부지정가, 3:시장가, 4:최유리지정가, 5:지정가(IOC), 6:지정가(FOK), 7:시장가(IOC), 8:시장가(FOK), 9:최유리지정가(IOC), A : 최유리지정가(FOK), 장종료 후 시간외 주문은 지정가 선택
            qty,             # 주문수량
            price,           # 주문가격
            '',              # 원주문번호
        )

        stoploss_inputs = (
            '매도스탑주문',   # 사용자 구분명
            '0000',          # 화면번호
            self.acc,        # 계좌번호
            ticker,          # 종목코드
            1,               # 신규매매 (주문종류)
            1,               # 매매구분	1:매도, 2:매수
            3,               # 거래구분 1:지정가, 2:조건부지정가, 3:시장가, 4:최유리지정가, 5:지정가(IOC), 6:지정가(FOK), 7:시장가(IOC), 8:시장가(FOK), 9:최유리지정가(IOC), A : 최유리지정가(FOK), 장종료 후 시간외 주문은 지정가 선택
            qty,             # 주문수량
            stoploss_price,  # 스톱로스가격
            '',              # 원주문번호
        )

        if self.api.get_login_info('GetServerGubun') != 1:
            print('실제 계좌이므로 주문하지 않습니다.')
            return

        # 매수 주문 실행
        if self.api.send_order_fo(*buy_inputs) == 0:
            self.api.loop()
        else:
            # Do something to handle error
            raise RuntimeError(f'Sending buy order went wrong.')

        # 매도 스톱로스 주문 실행
        if self.api.send_order_fo(*stoploss_inputs) == 0:
            self.api.loop()
        else:
            # Do something to handle error
            raise RuntimeError(f'Sending stoploss order went wrong.')   

        print('DexKiwoomAPI.trade_buy(self, ticker, qty, price) 종료')             


# ===================================================================================== #
# 서버에서 데이터를 받아 처리하는 클래스
class MyServer(Server):
    def __init__(self):
        super().__init__()
        self.ret_data = {}           
        self.downloading = False

    def login(self, err_code):
        print('\t\tServer.login(err_code) 호출')

        # err_code에 해당하는 메세지
        emsg = config.error.msg(err_code)

        # 로그인 성공/실패 출력
        print(f'\t\tLogin ({emsg})')

        # [필수] 이벤트를 기다리며 대기중이었던 코드 실행 (60번째 줄)
        self.api.unloop()

        print('\t\tServer.login(err_code) 종료')

    def deposit(self, _, rq_name, tr_code, __, ___):
        print('\tServer.deposit(scr_no, rq_name, tr_code, record_name, prev_next) 호출')

        # 예수금 데이터 저장
        self.share.update_single('deposit', '예수금', int(self.api.get_comm_data(tr_code, rq_name, 0, '예수금')))

        # [필수] 대기중인 코드 실행 (177번째 줄)
        self.api.unloop()

        print('\tServer.deposit(scr_no, rq_name, tr_code, record_name, prev_next) 종료')

    def balance(self, scr_no, rq_name, tr_code, record_name, prev_next):
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

    # Mapped directly from on_receive_chejan_data() without hook.
    def chejan(self, gubun, item_cnt, fid_list):
        # Only for Python >= 3.10.4.
        # Use if / elif / else, otherwise.
        gubun = ''  # gubun 값

        if gubun == '0':  # 접수/체결
            # 접수/체결 처리 코드 작성
            pass
        elif gubun == '1':  # 잔고변경
            # 잔고변경 처리 코드 작성
            pass
        elif gubun == '4':  # 파생잔고변경
            # 파생잔고변경 처리 코드 작성
            pass
        else:
            raise RuntimeError('Execution went wrong.')

        # cf. 9203 : 주문번호
        for fid in fid_list:
            self.api.get_chejan_data(fid)
        
        # Don't forget to self.api.unloop() somewhere.
        pass
    
    # 주식시분요청
    def opt10006(self, scr_no, rq_name, tr_code, record_name, prev_next):
        print('\tServer.opt10006(self, scr_no, rq_name, tr_code, record_name, prev_next) 호출')
        print("\tscr_no, rq_name, tr_code, record_name, prev_next : ", scr_no, rq_name, tr_code, record_name, prev_next)

        # 변수 초기화
        self.ret_data[tr_code] = {}
        self.ret_data[tr_code]['Data'] = {} 

        # 멀티데이터 저장
        keys = opt10006_list[tr_code]
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
            self.is_searching_enabled = True
            fn = self.api.signal('on_receive_tr_data', rq_name)
            fn(prev_next) # call signal function again to receive remaining data

        ## 요청 할 데이터가 더 없는 경우
        else:
            # Single 데이터 저장
            for key in keys:
                val = self.api.get_comm_data(tr_code, rq_name, 0, key).strip()
                self.share.update_single(name(), key, val)  # name() = 'balance'

        self.ret_data[tr_code]['Data'] = data 

        # 이벤트 루프 종료
        self.api.unloop()             

        print('\tServer.opt10006(scr_no, rq_name, tr_code, record_name, prev_next) 종료')

    # 상하한가요청
    def opt10017(self, scr_no, rq_name, tr_code, record_name, prev_next):
        print('\tServer.opt10017(self, scr_no, rq_name, tr_code, record_name, prev_next) 호출')
        print("\tscr_no, rq_name, tr_code, record_name, prev_next : ", scr_no, rq_name, tr_code, record_name, prev_next)

        # 변수 초기화
        self.ret_data[tr_code] = {}
        self.ret_data[tr_code]['Data'] = {} 

        # 멀티데이터 저장
        keys = opt10017_list[tr_code]
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
            self.is_searching_enabled = True
            fn = self.api.signal('on_receive_tr_data', rq_name)
            fn(prev_next) # call signal function again to receive remaining data

        ## 요청 할 데이터가 더 없는 경우
        else:
            # Single 데이터 저장
            for key in keys:
                val = self.api.get_comm_data(tr_code, rq_name, 0, key).strip()
                self.share.update_single(name(), key, val)  # name() = 'balance'

        self.ret_data[tr_code]['Data'] = data 

        # 이벤트 루프 종료
        self.api.unloop()             

        # data = pd.DataFrame(data)
        # out_name = "opt10017_230605.xlsx"
        # data.to_excel('C:/Users/Choi Heewon/thredart/dex/test_data/'+out_name)            

        print('\tServer.opt10017(scr_no, rq_name, tr_code, record_name, prev_next) 종료')  

    # 미체결요청
    def opt10075(self, scr_no, rq_name, tr_code, record_name, prev_next):
        print('\tServer.opt10075(self, scr_no, rq_name, tr_code, record_name, prev_next) 호출')   
        print("\tscr_no, rq_name, tr_code, record_name, prev_next : ", scr_no, rq_name, tr_code, record_name, prev_next)

        # 변수 초기화
        self.ret_data[tr_code] = {}
        self.ret_data[tr_code]['Data'] = {} 

        # 멀티데이터 저장
        keys = opt10075_list[tr_code]
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
            self.is_searching_enabled = True
            fn = self.api.signal('on_receive_tr_data', rq_name)
            fn(prev_next) # call signal function again to receive remaining data

        ## 요청 할 데이터가 더 없는 경우
        else:
            # Single 데이터 저장
            for key in keys:
                val = self.api.get_comm_data(tr_code, rq_name, 0, key).strip()
                self.share.update_single(name(), key, val)  # name() = 'balance'

        self.ret_data[tr_code]['Data'] = data 

        # 이벤트 루프 종료
        self.api.unloop()        

        data = pd.DataFrame(data)
        data.to_excel('C:/Users/Choi Heewon/thredart/dex/one_hour_candle_data/opt10075_230607.xlsx')            

        print('\tServer.opt10075(scr_no, rq_name, tr_code, record_name, prev_next) 종료')         

    # 주식분봉차트조회요청
    def opt10080(self, scr_no, rq_name, tr_code, record_name, prev_next):
        print('\tServer.opt10080(self, scr_no, rq_name, tr_code, record_name, prev_next) 호출')
        # print("\tscr_no, rq_name, tr_code, record_name, prev_next : ", scr_no, rq_name, tr_code, record_name, prev_next)

        # 변수 초기화
        self.ret_data[tr_code] = {}
        self.ret_data[tr_code]['Data'] = {} 

        # 멀티데이터 저장
        keys = opt10080_list[tr_code]
        data = {key: list() for key in keys}
        
        cnt = self.api.get_repeat_cnt(tr_code, rq_name)

        print("cnt : " + str(cnt))

        for i in range(cnt):
            for key in keys:
                val = self.api.get_comm_data(tr_code, rq_name, i, key).strip()
                data[key].append(val)


        # 봇 인스턴스와 데이터 공유
        for key in keys:
            self.share.extend_multi(rq_name, key, data[key])

        # 만일, 데이터가 더 있다면 signal 함수 한번 더 호출 (종목 수 25개 이상인 경우)
        if prev_next == '2':
            self.is_searching_enabled = True
            fn = self.api.signal('on_receive_tr_data', rq_name)
            fn(prev_next) # call signal function again to receive remaining data

        ## 요청 할 데이터가 더 없는 경우
        else:
            # Single 데이터 저장
            for key in keys:
                val = self.api.get_comm_data(tr_code, rq_name, 0, key).strip()
                self.share.update_single(name(), key, val)  # name() = 'balance'

        self.ret_data[tr_code]['Data'] = data 

        # 이벤트 루프 종료
        self.api.unloop()       

        ticker = data['종목코드'][0]
        data = pd.DataFrame(data)
        file_name = f'kr_hex_hour_{str(ticker)}.xlsx'
        data.to_excel('C:/Users/Choi Heewon/thredart/quant/kr/data/'+file_name)       

        print('\tServer.opt10080(scr_no, rq_name, tr_code, record_name, prev_next) 종료')              