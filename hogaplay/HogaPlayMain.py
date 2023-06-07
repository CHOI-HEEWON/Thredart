import sys
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
import pandas as pd 
from HogaPlayDBConnAPI import *
import finplot as fplt
import FinanceDataReader as fdr


# Daily Chart
fplt.candle_bull_color = "#FF0000"
fplt.candle_bull_body_color = "#FF0000" 
fplt.candle_bear_color = "#0000FF"

class HogaPlayMain(QMainWindow):
    def __init__(self):
        super().__init__()
    
        # DB 연동
        self.sDbConnAPI = HogaPlayDBConnAPI()

        # 변수 초기화
        self.hoga_index = 0  # 호가 타임 인덱스
        self.chegyeol_index = 0  # 체결 타임 인덱스
        self.enable_play_btn_clicked = False  # 시뮬레이터 재생 가능 상태
        self.is_playing = False  # 시뮬레이터 재생 상태(Play, Pause(Stop))
        self.delta = timedelta(microseconds=1)  # 데이터 시작 시간(start_time)부터 0.000001씩 추가
        self.pre_chegyeol_price = 0  # 체결가격의 최저가, 최고가 비교 변수

        # Hoga & Chegyeol 테이블 컬러
        self.tw_bg_yellow = QColor(255, 255, 0, 200)  
        self.tw_text_blue = QColor(50, 50, 255)  
        self.tw_bg_blue = QColor(0, 0, 255, 150)  
        self.tw_text_red = QColor(255, 0, 0)  
        self.tw_bg_tw_text_red = QColor(255, 0, 0, 150)  
        self.tw_bg_chegyeol = QColor(25, 25, 5)  
        self.tw_text_black = QColor(0, 0, 0)

        # UI 그리기
        self.setup_ui()        

    def setup_ui(self):
        # ========== #  Full Application # ========== #         
        self.setStyleSheet("background-color: black; color: white; font-family: sans-serif;")   

        # ========== # Hoga & Chegyeol View # ========== #
        # 호가 데이터 리스트 초기화
        self.sell_price_list_ = [[] for _ in range(11)]
        self.sell_price_qty_list_ = [[] for _ in range(11)]
        self.sell_price_qty_diff_list_ = [[] for _ in range(11)]
        self.buy_price_list_ = [[] for _ in range(11)]   
        self.buy_price_qty_list_ = [[] for _ in range(11)]   
        self.buy_price_qty_diff_list_ = [[] for _ in range(11)]    
 
        # 체결 데이터 리스트 초기화
        self.chegyeol_created_at_list_ = [[] for _ in range(11)]   
        self.chegyeol_price_list_ = [[] for _ in range(11)]           
        self.chegyeol_qty_list_ = [[] for _ in range(11)]                  

        # 테이블 위젯 생성
        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(0, 60, 900, 800)
        self.table_widget.setStyleSheet("QTableView { gridline-color: darkgray; }")

        # 테이블 행, 열 설정
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header = self.table_widget.verticalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)        

        self.table_widget.setRowCount(21)
        self.table_widget.setColumnCount(6)
        self.table_widget.verticalHeader().setVisible(False)  # 행 헤더 숨기기
        self.table_widget.horizontalHeader().setVisible(False)  # 열 헤더 숨기기

        # 테이블 그리기
        for i in range(21):
            for j in range(5):
                item = QTableWidgetItem()
                self.table_widget.setItem(i, j, item) 

                # if (j >= 0 and j <= 2) and (i >= 10 and i <= 19):
                #     item.setBackground(self.gray)      

        # 테이블 현재 시간 라벨 생성(실시간 반영)
        self.current_time_lbl = QLabel(self)
        self.current_time_lbl.setGeometry(470, 832, 130, 15)                  

        # ========== # Hoga & Chegyeol Control # ========== #
        # 재생 버튼 생성
        self.play_btn = QPushButton('PLAY', self)
        self.play_btn.setCheckable(True)
        self.play_btn.clicked.connect(self.play_btn_clicked)   
        self.play_btn.setGeometry(20, 880, 100, 30)
        self.play_btn.setStyleSheet("border: 2px solid lightgray;")

        # 재생 시간 슬롯 생성
        self.timer = QTimer()
        self.timer.timeout.connect(self.start_playback)        

        # ========== # Search for conditions # ========== #
        # 날짜 선택 라벨 생성
        self.date_lbl = QLabel(self)
        self.date_lbl.setGeometry(20, 15, 130, 30)
        self.date_lbl.setText('Select a date')
        self.date_lbl.setStyleSheet("border: 1px solid darkgray;")

        # 캘린더 생성
        self.cal = QCalendarWidget(self)  
        self.cal.setGeometry(20, 50, 200, 200)
        self.cal.setVisible(False)  # 초기에는 숨겨진 상태로 설정
        self.cal.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)  # 왼쪽 1열 숫자 숨기기
        self.cal.clicked[QDate].connect(self.show_cal_date)

        # 캘린더 선택 버튼 생성
        self.cal_btn = QPushButton('선택', self)
        self.cal_btn.setCheckable(True)
        self.cal_btn.clicked.connect(self.cal_btn_clicked)   
        self.cal_btn.setGeometry(170, 15, 60, 30)
        self.cal_btn.setStyleSheet("border: 2px solid lightgray;")

        # 종목 선택 콤보박스 생성
        self.stock_cb = QComboBox(self)
        self.stock_cb.setGeometry(250, 15, 250, 30)        
        self.stock_cb.addItem('Select an stock')
        self.stock_cb.activated[str].connect(self.stock_cb_activated)
        self.stock_cb.setStyleSheet("border: 1px solid darkgray;")

        # 조건 검색 버튼 생성
        self.search_btn = QPushButton('검색', self)
        self.search_btn.setCheckable(True)
        self.search_btn.clicked.connect(self.search_btn_clicked) 
        self.search_btn.setGeometry(840, 18, 60, 30)
        self.search_btn.setStyleSheet("border: 2px solid #00FF00;")

        # ========== # Daily Chart # ========== #
        # Daily Chart 생성
        self.graph_view = QGraphicsView(self)     
        self.graph_view.setGeometry(900, 60, 950, 800)
        self.grid_layout = QGridLayout(self.graph_view)
        self.ax0, self.ax1 = fplt.create_plot_widget(master=self.graph_view, rows=2, init_zoom_periods=100)
        self.graph_view.axs = [self.ax0, self.ax1]
        self.grid_layout.addWidget(self.ax0.ax_widget, 0, 0)
        self.grid_layout.addWidget(self.ax1.ax_widget, 1, 0)

        chart_label = QLabel('Daily Chart', self)
        chart_label.setAlignment(Qt.AlignCenter)
        self.grid_layout.addWidget(chart_label, 2, 0)
      
        # ========== # Log Out # ========== #
        self.logout_btn = QPushButton("EXIT", self)
        self.logout_btn.move(1760, 15) 
        self.logout_btn.clicked.connect(self.logout_btn_clicked)        

        # ========== # Copyright Marking # ========== #
        self.statusbar = QStatusBar(self)          
        self.setStatusBar(self.statusbar)        
        self.statusbar.showMessage("(c) 2023. THREDART Corp. All rights reserved. ")        

    # ========== # Log Out # ========== #
    def logout_btn_clicked(self):
        QApplication.instance().quit()
        # self.close

    # ========== # Hover Event : 호버시 아이콘 이미지 색상 변경 # ========== #
    def eventFilter(self, obj, event):
        if event.type() == event.Enter:
            if isinstance(obj, QPushButton):
                self.icon_path = obj.icon()    

                if obj.icon():
                    pixmap = obj.icon().pixmap(obj.iconSize())
                    painter = QPainter(pixmap)
                    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                    painter.fillRect(pixmap.rect(), QColor("white"))
                    painter.end()
                    obj.setIcon(QIcon(pixmap))

        elif event.type() == event.Leave:
            if isinstance(obj, QPushButton):
                # 호버 해제 시 아이콘 이미지 색상 복원
                if obj.icon():
                    obj.setIcon(QIcon(self.icon_path))

        return super().eventFilter(obj, event) 
    
    # ========== # Paint Event : Window 상단 회색 라인 생성 # ========== #
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(QColor("darkgray"), 1))
        painter.drawLine(0, 60, self.width(), 60) 

    # ========== # Search Conditions # ========== #
    def show_cal_date(self, date):
        formatted_date = date.toString(Qt.ISODate)  # "YYYY-MM-DD" 형식으로 변환
        self.date_lbl.setText(formatted_date)
        self.cal.setVisible(False)
        self.select_stock_list(self.date_lbl.text())  

        self.stop_playback()
        self.table_widget.clearContents()  
        self.current_time_lbl.setText("")  
        self.play_btn.setText('PLAY')
        self.enable_play_btn_clicked = False
        self.clear_chart()

    def cal_btn_clicked(self):
        if self.cal.isVisible():
            self.cal.setVisible(False)
        else:
            self.cal.setVisible(True)    

    def select_stock_list(self, data):
        stock_hoga_data = pd.DataFrame(self.sDbConnAPI.select_stock_list(val=data),
                                       columns=['ticker', 'ticker_nm'])
        
        self.stock_cb.clear()
        
        if not stock_hoga_data.empty:
            self.ticker_list = []
            self.ticker_nm_list = []
            self.ticker_list = stock_hoga_data['ticker'] 
            self.ticker_nm_list = stock_hoga_data['ticker_nm'] 

            self.stock_cb.addItem('Select a stock')  
            for ticker, ticker_nm in zip(self.ticker_list, self.ticker_nm_list):
                self.stock_cb.addItem(f'{ticker_nm} ({ticker})')  
        else: 
            self.stock_cb.addItem('Select a stock')        

    def stock_cb_activated(self, text):
        self.stock_cb.setCurrentText(text)
        self.stop_playback()
        self.table_widget.clearContents()  # 테이블 위젯 초기화
        self.current_time_lbl.setText("")  # 테이블 현재 시간 라벨 초기화
        self.play_btn.setText('PLAY')
        self.enable_play_btn_clicked = False
        self.clear_chart()        
    
    def search_btn_clicked(self):
        if not self.date_lbl.text() or self.date_lbl.text() == 'Select a date':
            self.enable_play_btn_clicked = False
            QMessageBox.warning(self, "Notification", "Please select a date")

        elif not self.stock_cb.currentText() or self.stock_cb.currentText() == 'Select a stock':
            self.enable_play_btn_clicked = False     
            QMessageBox.warning(self, "Notification", "Please select a stock")   

        else:
            self.is_playing = False
            self.play_btn.setText('PLAY')      
            self.enable_play_btn_clicked = True

            # Hoga & Chegyeol View
            self.hoga_index = 0  # 호가 타임 인덱스
            self.chegyeol_index = 0  # 체결 타임 인덱스            
            date_lbl = self.date_lbl.text()
            ticker = self.stock_cb.currentText().split('(')[-1].split(')')[0].strip()
            self.hoga_view(date_lbl, ticker)

            # Daily Chart
            df = fdr.DataReader(symbol=ticker, start="2020")
            self.ax0.reset()
            self.ax1.reset()
            fplt.candlestick_ochl(df[['Open', 'Close', 'High', 'Low']], ax=self.ax0)
            fplt.volume_ocv(df[['Open', 'Close', 'Volume']], ax=self.ax1)
            fplt.refresh()      # refresh autoscaling when all plots complete
            fplt.show(qt_exec=False)            

    # ========== # Hoga & Chegyeol View # ========== # 
    def hoga_view(self, created_at, ticker):
        # 호가 데이터
        data = {'created_at': created_at, 'ticker': ticker}
        stock_hoga_data = pd.DataFrame(self.sDbConnAPI.select_stock_hoga(row=data),
                                       columns=['hoga_created_at', 'ticker',
                                                'sell_price1', 'sell_price1_qty', 'sell_price1_qty_diff',
                                                'buy_price1', 'buy_price1_qty', 'buy_price1_qty_diff',
                                                'sell_price2', 'sell_price2_qty', 'sell_price2_qty_diff',
                                                'buy_price2', 'buy_price2_qty', 'buy_price2_qty_diff',
                                                'sell_price3', 'sell_price3_qty', 'sell_price3_qty_diff',
                                                'buy_price3', 'buy_price3_qty', 'buy_price3_qty_diff',
                                                'sell_price4', 'sell_price4_qty', 'sell_price4_qty_diff',
                                                'buy_price4', 'buy_price4_qty', 'buy_price4_qty_diff',
                                                'sell_price5', 'sell_price5_qty', 'sell_price5_qty_diff',
                                                'buy_price5', 'buy_price5_qty', 'buy_price5_qty_diff',
                                                'sell_price6', 'sell_price6_qty', 'sell_price6_qty_diff',
                                                'buy_price6', 'buy_price6_qty', 'buy_price6_qty_diff',
                                                'sell_price7', 'sell_price7_qty', 'sell_price7_qty_diff',
                                                'buy_price7', 'buy_price7_qty', 'buy_price7_qty_diff',
                                                'sell_price8', 'sell_price8_qty', 'sell_price8_qty_diff',
                                                'buy_price8', 'buy_price8_qty', 'buy_price8_qty_diff',
                                                'sell_price9', 'sell_price9_qty', 'sell_price9_qty_diff',
                                                'buy_price9', 'buy_price9_qty', 'buy_price9_qty_diff',
                                                'sell_price10', 'sell_price10_qty', 'sell_price10_qty_diff',
                                                'buy_price10', 'buy_price10_qty', 'buy_price10_qty_diff',
                                                'total_sell_qty', 'total_sell_qty_diff', 'total_buy_qty', 'total_buy_qty_diff'
                                                ]
                                        )
        
        self.hoga_created_at = stock_hoga_data['hoga_created_at'] 
        self.ticker = stock_hoga_data['ticker'] 

        self.sell_price_list = [pd.DataFrame() for _ in range(11)]  # 인덱스 0은 사용하지 않음
        self.sell_price_qty_list = [pd.DataFrame() for _ in range(11)]
        self.sell_price_qty_diff_list = [pd.DataFrame() for _ in range(11)]
        for i in range(1, 11):
            self.sell_price_list[i] = stock_hoga_data[f'sell_price{i}'] 
            self.sell_price_qty_list[i] = stock_hoga_data[f'sell_price{i}_qty']   
            self.sell_price_qty_diff_list[i] = stock_hoga_data[f'sell_price{i}_qty_diff']   

        self.buy_price_list = [pd.DataFrame() for _ in range(11)] 
        self.buy_price_qty_list = [pd.DataFrame() for _ in range(11)] 
        self.buy_price_qty_diff_list = [pd.DataFrame() for _ in range(11)]  
        for i in range(1, 11):
            self.buy_price_list[i] = stock_hoga_data[f'buy_price{i}']   
            self.buy_price_qty_list[i] = stock_hoga_data[f'buy_price{i}_qty']   
            self.buy_price_qty_diff_list[i] = stock_hoga_data[f'buy_price{i}_qty_diff']   

        self.total_sell_qty = stock_hoga_data['total_sell_qty'] 
        self.total_sell_qty_diff = stock_hoga_data['total_sell_qty_diff'] 
        self.total_buy_qty = stock_hoga_data['total_buy_qty'] 
        self.total_buy_qty_diff = stock_hoga_data['total_buy_qty_diff'] 

        # 체결 데이터
        stock_chegyeol_data = pd.DataFrame(self.sDbConnAPI.select_stock_chegyeol(row=data),
                                       columns=['chegyeol_created_at', 'chegyeol_price', 'chegyeol_qty'])  

        self.chegyeol_created_at = stock_chegyeol_data['chegyeol_created_at']     
        self.chegyeol_price = stock_chegyeol_data['chegyeol_price']    
        self.chegyeol_qty = stock_chegyeol_data['chegyeol_qty']    

        # 호가 데이터 + 체결 데이터의 시작 시간 및 끝 시간
        time_data = pd.DataFrame(self.sDbConnAPI.select_stock_time(row=data),
                                       columns=['start_time', 'end_time'])   
        
        self.start_time = time_data['start_time'].values[0]  # 09:02:17.785404
        self.end_time = time_data['end_time'] .values[0]  # 11:00:00.061273

        self.start_time = datetime.strptime(self.start_time, '%H:%M:%S.%f')     
        self.end_time = datetime.strptime(self.end_time, '%H:%M:%S.%f')

        self.current_time_lbl.setText(str(self.start_time.time()))  

        self.update_hoga_data()  
        self.update_chegyeol_data()
        self.check_start_time() 
        self.update_stock_table()

    # 매도 막대그래프 생성
    def build_sell_bargraph_widget(self):
        bargraph_widget = QWidget()
        layout = QVBoxLayout(bargraph_widget)
        pbar = QProgressBar()
        pbar.setFixedHeight(20)
        pbar.setInvertedAppearance(True)  
        pbar.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        pbar.setRange(0, 100000)
        pbar.setFormat("")  # 퍼센트 숫자 표시 제거            
        pbar.setStyleSheet("""
            QProgressBar {background-color : rgba(0, 0, 0, 0%); border : 1}
            QProgressBar::Chunk {background-color : rgba(0, 0, 255, 50%); border : 1}
        """)
        layout.addWidget(pbar)
        layout.setAlignment(Qt.AlignVCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        bargraph_widget.setLayout(layout)

        return pbar, bargraph_widget
    
    # 매수 막대그래프 생성
    def build_buy_bargraph_widget(self):
        bargraph_widget = QWidget()
        layout = QVBoxLayout(bargraph_widget)
        pbar = QProgressBar()
        pbar.setFixedHeight(20)
        pbar.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        pbar.setRange(0, 100000)
        pbar.setFormat("")  # 퍼센트 숫자 표시 제거        
        pbar.setStyleSheet("""
            QProgressBar {background-color : rgba(0, 0, 0, 0%); border : 1}
            QProgressBar::Chunk {background-color : rgba(255, 0, 0, 50%); border : 1}
        """)
        layout.addWidget(pbar)
        layout.setAlignment(Qt.AlignVCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        bargraph_widget.setLayout(layout)

        return pbar, bargraph_widget    
    
    # 호가 데이터 Update
    def update_hoga_data(self):
        for i in range(1, 11):
            self.sell_price_list_[i] = str(self.sell_price_list[i].iloc[self.hoga_index])
            self.sell_price_qty_list_[i] = str(self.sell_price_qty_list[i].iloc[self.hoga_index])
            self.sell_price_qty_diff_list_[i] = str(self.sell_price_qty_diff_list[i].iloc[self.hoga_index])
            self.buy_price_list_[i] = str(self.buy_price_list[i].iloc[self.hoga_index])
            self.buy_price_qty_list_[i] = str(self.buy_price_qty_list[i].iloc[self.hoga_index])
            self.buy_price_qty_diff_list_[i] = str(self.buy_price_qty_diff_list[i].iloc[self.hoga_index])

        self.total_sell_qty_ = str(self.total_sell_qty.iloc[self.hoga_index])
        self.total_sell_qty_diff_ = str(self.total_sell_qty_diff.iloc[self.hoga_index])
        self.total_buy_qty_ = str(self.total_buy_qty.iloc[self.hoga_index])
        self.total_buy_qty_diff_ = str(self.total_buy_qty_diff.iloc[self.hoga_index])  

        self.hoga_index += 1

    # 체결 데이터 Update
    def update_chegyeol_data(self):
        for i in range(1, 11):
            self.chegyeol_created_at_list_[i] = str(self.chegyeol_created_at.iloc[self.chegyeol_index-(i-1)])
            self.chegyeol_price_list_[i] = str(self.chegyeol_price.iloc[self.chegyeol_index-(i-1)]) 
            self.chegyeol_qty_list_[i] = str(self.chegyeol_qty.iloc[self.chegyeol_index-(i-1)])  

        # 최저가, 최고가 비교
        cur_chegyeol_price = self.chegyeol_price_list_[1]
        if  str(self.pre_chegyeol_price) > str(cur_chegyeol_price):
            self.min_chegyeol_price = cur_chegyeol_price
            self.max_chegyeol_price = self.pre_chegyeol_price
        elif  str(self.pre_chegyeol_price) < str(cur_chegyeol_price):
            self.min_chegyeol_price = self.pre_chegyeol_price
            self.max_chegyeol_price = cur_chegyeol_price     
        self.pre_chegyeol_price = self.chegyeol_price_list_[1]
           
        self.chegyeol_index += 1

    def check_start_time(self):
        # 시작 시간에 따른 index 값 조정(테이블을 처음 load할때 시간에 상관없이 호가, 체결 데이터를 한 번에 불러오기 때문)
        if str(self.hoga_created_at.iloc[self.hoga_index]) > str(self.chegyeol_created_at.iloc[self.chegyeol_index]):  # 호가 시간이 더 나중이면 index 0부터 다시 시작
            self.hoga_index = 0

        elif str(self.hoga_created_at.iloc[self.hoga_index]) < str(self.chegyeol_created_at.iloc[self.chegyeol_index]):  # 체결 시간이 이 더 나중이면 index 0부터 다시 시작
            self.chegyeol_index = 0                 
    
    # Hoga & Chegyeol View Update
    def update_stock_table(self):
        for j in range(6):
            if j == 0:
                i = 10
                for k in range(1, 11):
                    item = QTableWidgetItem(self.chegyeol_created_at_list_[k])
                    item.setBackground(self.tw_bg_chegyeol)                     
                    self.table_widget.setItem(i, j, self.set_text_aligment(item, "right"))  # 체결시간
                    i = i + 1  

            if j == 1:
                i = 0
                for k in range(10, 0, -1):
                    self.table_widget.setItem(i, j, self.set_text_aligment(QTableWidgetItem(self.sell_price_qty_diff_list_[k]), "right"))  # 매도1~10호가 잔량대비
                    i = i + 1 

                i = 10
                for k in range(1, 11):
                    item = QTableWidgetItem(self.chegyeol_price_list_[k])
                    item.setBackground(self.tw_bg_chegyeol) 

                    if "-" in self.chegyeol_price_list_[k]:  # value에 "-"가 포함
                        # self.chegyeol_price_list_[k] = "".join(self.chegyeol_price_list_[k].split("-"))
                        # item = QTableWidgetItem(self.sell_price_list_[k])
                        item.setForeground(self.tw_text_blue)
                    else:
                        item.setForeground(self.tw_text_red)                        

                    self.table_widget.setItem(i, j, self.set_text_aligment(item, "right"))  # 체결가격
                    # self.chegyeol_price_list_[k] = '-' + self.chegyeol_price_list_[k]

                    i = i + 1                      
                                      
                self.table_widget.setItem(20, j, self.set_text_aligment(QTableWidgetItem(self.total_sell_qty_diff_), "right"))  # 총매도잔량직전대비

            if j == 2:
                i = 0        
                for k in range(10, 0, -1):   # 매도1~10호가잔량
                    # 매도1~10호가잔량의 막대그래프
                    self.table_widget.setItem(i, j, self.set_text_aligment(QTableWidgetItem(self.sell_price_qty_list_[k]), "right")) 
                    pbar, bargraph_widget = self.build_sell_bargraph_widget()
                    self.table_widget.setCellWidget(i, j, bargraph_widget)  
                    pbar.setFormat(str(self.sell_price_qty_list_[k]))
                    pbar.setValue(int(self.sell_price_qty_list_[k])) 
                    i = i + 1  
                    
                i = 10                       
                for k in range(1, 11):
                    item = QTableWidgetItem(self.chegyeol_qty_list_[k])
                    item.setBackground(self.tw_bg_chegyeol)                        
                    self.table_widget.setItem(i, j, self.set_text_aligment(item, "right"))  # 체결량
                    i = i + 1                      
             
                self.table_widget.setItem(20, j, self.set_text_aligment(QTableWidgetItem(self.total_sell_qty_), "right"))  # 총매도잔량

            if j == 3:
                i = 0
                for k in range(10, 0, -1):

                    item = QTableWidgetItem(self.sell_price_list_[k])

                    if "-" in self.sell_price_list_[k]:  # value에 "-"가 포함
                        # self.sell_price_list_[k] = "".join(self.sell_price_list_[k].split("-"))
                        # item = QTableWidgetItem(self.sell_price_list_[k])
                        item.setForeground(self.tw_text_blue)
                    else:
                        item.setForeground(self.tw_text_red)

                    if self.sell_price_list_[k] == self.max_chegyeol_price:  # 매도1~10호가에 최고가가 있으면
                        item.setForeground(self.tw_text_black)
                        item.setBackground(self.tw_bg_tw_text_red) 
                    if self.sell_price_list_[k] == self.chegyeol_price_list_[1]:  # 매도1~10호가에 현재가가 있으면
                        item.setBackground(self.tw_bg_yellow)

                    self.table_widget.setItem(i, j, self.set_text_aligment(item, "right"))  # 매도1~10호가
                    # self.sell_price_list_[k] = '-' + self.sell_price_list_[k]

                    i = i + 1 

                i = 10                           
                for k in range(1, 11):
                    item = QTableWidgetItem(self.buy_price_list_[k])

                    if "-" in self.buy_price_list_[k]:  # value에 "-"가 포함
                        # self.buy_price_list_[k] = "".join(self.buy_price_list_[k].split("-"))
                        # item = QTableWidgetItem(self.buy_price_list_[k])
                        item.setForeground(self.tw_text_blue)
                    else:
                        item.setForeground(self.tw_text_red)

                    if self.buy_price_list_[k] == self.min_chegyeol_price:  # 매수1~10호가에 최저가가 있으면
                        item.setBackground(self.tw_bg_blue)                     
                    if self.buy_price_list_[k] == self.chegyeol_price_list_[1]:  # 매수1~10호가에 현재가가 있으면
                        item.setBackground(self.tw_bg_yellow)  

                    self.table_widget.setItem(i, j, self.set_text_aligment(item, "right"))  # 매수1~10호가      
                    # self.buy_price_list_[k] = '-' + self.buy_price_list_[k]

                    i = i + 1  

            if j == 4:
                i = 10
                for k in range(1, 11):
                    self.table_widget.setItem(i, j, self.set_text_aligment(QTableWidgetItem(self.buy_price_qty_list_[k]), "right"))  # 매수1~10호가잔량     
                    # 매수1~10호가잔량의 막대그래프
                    pbar, bargraph_widget = self.build_buy_bargraph_widget()
                    self.table_widget.setCellWidget(i, j, bargraph_widget)  
                    pbar.setFormat(str(self.buy_price_qty_list_[k]))
                    pbar.setValue(int(self.buy_price_qty_list_[k]))  
                    i = i + 1  

                self.table_widget.setItem(20, j, self.set_text_aligment(QTableWidgetItem(self.total_buy_qty_), "right"))  # 총매수잔량 

            if j == 5:
                i = 10
                for k in range(1, 11):
                    self.table_widget.setItem(i, j, self.set_text_aligment(QTableWidgetItem(self.buy_price_qty_diff_list_[k]), "right"))  # 매수1~10호가잔량대비  
                    i = i + 1  

                self.table_widget.setItem(20, j, self.set_text_aligment(QTableWidgetItem(self.total_buy_qty_diff_), "right"))  # 총매수잔량직전대비  

    # QTableWidgetItem 텍스트 정렬
    def set_text_aligment(self, item, direction):
        if direction == "left":
            item.setTextAlignment(int(Qt.AlignLeft|Qt.AlignVCenter))
        elif direction == "right":
            item.setTextAlignment(int(Qt.AlignRight|Qt.AlignVCenter))
        elif direction == "center":
            item.setTextAlignment(Qt.AlignVCenter|Qt.AlignHCenter)

        return item    
    
    # ========== # Hoga & Chegyeol Control # ========== #
    def play_btn_clicked(self):
        if self.enable_play_btn_clicked:
            if not self.is_playing:
                self.play_btn.setText('STOP')
                self.is_playing = True
                self.start_playback()
            else:
                self.is_playing = False
                self.play_btn.setText('PLAY')
                self.pause_playback()

    @pyqtSlot()            
    def start_playback(self):
        if self.start_time <= self.end_time:
            hoga_created_at = self.hoga_created_at.iloc[self.hoga_index]
            if str(self.start_time.time()) == str(hoga_created_at):
                self.update_hoga_data()
                self.update_stock_table()

                # 호가 시간 중복 여부 체크 
                while str(hoga_created_at) == str(self.hoga_created_at.iloc[self.hoga_index]):
                    self.update_hoga_data()
                    self.update_stock_table()    

            chegyeol_created_at = self.chegyeol_created_at.iloc[self.chegyeol_index]
            if str(self.start_time.time()) == str(chegyeol_created_at): 
                self.update_chegyeol_data()   
                self.update_stock_table()
            
                # 체결 시간 중복 여부 체크
                while str(chegyeol_created_at) == str(self.chegyeol_created_at.iloc[self.chegyeol_index]):
                    self.update_chegyeol_data()
                    self.update_stock_table()  

            self.start_time += self.delta
            # print(self.start_time, end="\r", flush=True)
            self.current_time_lbl.setText(str(self.start_time.time()))  # 현재 시간

            self.timer.start(0)  # timeout 시그널 발생

    @pyqtSlot()
    def pause_playback(self):
        self.timer.stop()

    def stop_playback(self):
        self.timer.stop()

    # ========== # Daily Chart # ========== #
    def clear_chart(self):
        for ax in self.graph_view.axs:
            ax.clear()

        self.ax0, self.ax1 = fplt.create_plot_widget(master=self.graph_view, rows=2, init_zoom_periods=100)
        self.graph_view.axs = [self.ax0, self.ax1]
        self.grid_layout.addWidget(self.ax0.ax_widget, 0, 0)
        self.grid_layout.addWidget(self.ax1.ax_widget, 1, 0)

        chart_label = QLabel('Daily Chart', self)
        chart_label.setAlignment(Qt.AlignCenter)
        self.grid_layout.addWidget(chart_label, 2, 0)

    # ========== # Window Setting # ========== #
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def open_window(self):
        self.setWindowTitle('Thredart Hoga Play')
        # self.setWindowIcon(QIcon('C:/Users/Choi Heewon/thredart/scalping/simulator/image/logo.png'))
        self.resize(1850, 950)
        self.center()
        self.show()


# ========== #  
if __name__ == '__main__':
    app = QApplication(sys.argv)
    hogaPlayMain = HogaPlayMain()
    hogaPlayMain.open_window()
    sys.exit(app.exec_())    
