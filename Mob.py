# -*- coding: utf-8 -*-
from __future__ import division

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Mob_num import _mob_num
from dialogs import *

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

SERVICE = 1
SERVICE_ID = 0
SERVICE_NAME = 2
SUM_MIN = 3
SUM_MAX = 4
PERCENT = 5
MIN = 6
PTYPE = 7

servicesOrder = ['mobile_services','internet_services','tv_services','money_services']
availableServices = ['mobile_services']

services = {
'mobile_services':
[
[208, 'kyivstar', u'Киевстар', '00.01', '3000.00',4,1,'online'],
[214, 'mts', u'МТС', '00.01', '2870.00',4,1,'online'],
[252, 'beeline', u'Билайн', '00.01', '1000.00',4,1,'online'],
[281, 'intertelecom', u'Интертелеком', '10.00', '1000.00',1,1,'online'],
[393, 'peoplenet', u'ПиплНет', '00.01', '5000.00',1,1,'online'],
[257, 'cdma_new', u'СДМА-UA', '05.00', '1000.00',1.5,1,'online'],
[387, 'tezgsm', u'Тез ДжЕсЕм  ', '05.00', '5000.00',0,0,'online'],
[312, 'travelsim', u'ТрэвэлСим', '10.00', '2000.00',0,0,'online'],
[530, 'simfortour', u'Симфотур (Simfortour)  ', '10.00', '5000.00',3,1,'online']
],

'internet_services':
[
[456, 'life', u'Лайф Астелит вауч.', '01.00', '1000.00',1.5,1,'voucher'],
[264, '', u'ИнюрНет', '01.00', '500.00'],
[304, '', u'СмайлВеб (Online)', '30.00', '5000.00'],
[305, '', u'Хмельницкинфоком online', '05.00', '1000.00'],
[324, '', u'Инфоаура Online', '05.00', '1000.00'],
[331, 'vega', u'Вега (Phone по № тел.(Оптима Телеком)', '01.00', '5000.00'],
[333, '', u'Вега (Internet (Оптима Телеком)', '01.00', '5000.00'],
[341, 'freshtel', u'Фрэштел', '10.00', '3000.00'],
[342, '', u'АйПиНет', '10.00', '5000.00'],
[349, '', u'Интраффик', '01.00', '1000.00'],
[350, '', u'Укртранссеть', '01.00', '5000.00'],
[354, '', u'Триолан Харьков Базис Интернет', '01.00', '1000.00'],
[356, '', u'Триолан Харьков-Эпсилон Интернет', '01.00', '1000.00'],
[358, '', u'Триолан Харьков-Березка Интернет', '01.00', '1000.00'],
[360, '', u'Триолан Харьков-ІТ сервис Интернет', '01.00', '1000.00'],
[362, '', u'Триолан Полтава Интернет', '01.00', '1000.00'],
[364, '', u'Триолан Днепропетровск Интернет', '01.00', '1000.00'],
[366, '', u'Триолан Запорожье Интернет', '01.00', '1000.00'],
[368, '', u'Триолан Одесса Интернет', '01.00', '1000.00'],
[370, '', u'Триолан Донецк Интернет', '01.00', '1000.00'],
[372, '', u'Триолан Луганск Интернет', '01.00', '1000.00'],
[374, '', u'Триолан Симферополь Интернет', '01.00', '1000.00'],
[386, '', u'Матрикс Хом  (Matrix Home)', '00.01', '5000.00'],
[401, '', u'Ланет Нетворк', '01.00', '1000.00'],
[421, '', u'Бриз', '10.00', '1000.00'],
[429, '', u'Орион Сити', '01.00', '2000.00'],
[433, '', u'Фринет', '00.01', '1000.00'],
[446, '', u'Навигатор-Онлайн', '10.00', '5000.00'],
[447, '', u'Крейзи Нетворк', '05.00', '1000.00'],
[464, '', u'Триолан Киев Интернет ', '01.00', '1000.00'],
[477, '', u'Аирбайтс Львов (Airbites)  ', '00.01', '5000.00'],
[478, '', u'Аирбайтс Ивано-Франковск (Airbites)  ', '00.01', '5000.00'],
[479, '', u'Аирбайтс Хмельницкий (Airbites)  ', '00.01', '5000.00'],
[482, '', u'QT.net', '01.00', '5000.00'],
[483, '', u'ХитЛайн (HitLine)', '01.00', '3000.00'],
[484, '', u'L-Com', '00.10', '5000.00'],
[485, '', u'Тринити (TRINITY)', '01.00', '1000.00'],
[491, '', u'Тринити (TRINITY) Донецк  ', '01.00', '1000.00'],
[492, '', u'АйТиВи  ', '05.00', '1000.00'],
[493, '', u'Ирель', '05.00', '1000.00'],
[494, '', u'ТВКОМ', '05.00', '1000.00'],
[495, '', u'Альтаир', '05.00', '5000.00'],
[508, '', u'Аванет', '01.00', '5000.00'],
[509, '', u'СуперСкай  ', '01.00', '5000.00'],
[510, '', u'Кристал', '10.00', '5000.00'],
[511, '', u'Тенет', '05.00', '5000.00'],
[512, '', u'СимНет', '00.01', '5000.00'],
[513, '', u'Датагруп интернет', '01.00', '5000.00'],
[514, '', u'Датагруп телефония', '01.00', '5000.00'],
[515, '', u'Горизонт Плюс', '00.01', '5000.00'],
[516, '', u'Формат интернет', '01.00', '5000.00'],
[517, '', u'Формат ТВ', '01.00', '5000.00'],
[520, '', u'Велтон (телефония)', '01.00', '5000.00'],
[521, '', u'Велтон интернет, цифровое ТВ', '01.00', '5000.00'],
[524, '', u'Стелс ', '30.00', '5000.00'],
[528, '', u'Сатурн', '01.00', '3000.00'],
[533, '', u'Домашня мережа', '02.00', '999.00'],
[536, '', u'Сана (Реноме)', '01.00', '5000.00'],
[537, '', u'Фрегат', '01.00', '5000.00'],
[542, 'vega', u'Вега (Phone (Фарлеп Инвест)', '01.00', '5000.00'],
[543, 'vega', u'Вега (Internet (Фарлеп Инвест)', '01.00', '5000.00'],
[544, 'vega', u'Вега (Phone (Фарлеп Холдинг)', '01.00', '5000.00'],
[545, 'vega', u'Вега (Internet (Фарлеп Холдинг)', '01.00', '5000.00'],
[553, '', u'Аирбайтс Харьков (Airbites)  ', '00.01', '5000.00'],
[554, '', u'Аирбайтс Ровно (Airbites)  ', '00.01', '5000.00'],
[555, '', u'Аирбайтс Луцк (Airbites)  ', '00.01', '5000.00'],
[556, '', u'Инти Львов (Inti)', '00.01', '5000.00'],
[557, '', u'Инти Ивано-Франковск (Inti)  ', '00.01', '5000.00'],
[558, '', u'Инти Хмельницкий (Inti)  ', '00.01', '5000.00'],
[559, '', u'Инти Харьков (Inti)  ', '00.01', '5000.00'],
[564, '', u'Интермедия', '01.00', '5000.00'],
[567, '', u'Українські оптичні системи', '30.00', '5000.00'],
[568, '', u'ДТС (DTS-internet )  ', '05.00', '1000.00'],
[569, '', u'Хоум Нет (Hnet)', '05.00', '1000.00'],
[570, '', u'Д-Лан (D-lan)', '05.00', '1000.00'],
[571, '', u'Альфа ТВ', '01.00', '1000.00'],
[572, '', u'Ютим (UTeam)  ', '01.00', '5000.00'],
[585, '', u'Сохо 5(Soxo 5)  ', '30.00', '30.00'],
[587, '', u'Сохо 10 (Soxo10)  ', '60.00', '60.00'],
[588, '', u'Сохо 20 (Soxo 20)  ', '120.00', '120.00'],
[589, '', u'Сохо 50 (Soxo 50)  ', '300.00', '300.00'],
[590, '', u'Адамант-Телеком', '01.00', '5000.00'],
[592, '', u'Черное море (Интернет)', '25.00', '5000.00'],
[593, '', u'Черное море (Цифровое ТВ)', '25.00', '5000.00'],
[594, '', u'Черное море (Аналоговое ТВ)', '25.00', '5000.00'],
[595, '', u'Хоумнет, ТОВ', '01.00', '5000.00'],
[596, '', u'Эверест кабельное ТВ', '01.00', '5000.00'],
[597, '', u'Эверест цифровое ТВ', '01.00', '5000.00'],
[598, '', u'Эверест интернет', '01.00', '5000.00'],
[599, '', u'Эверест (повторное подключение)', '01.00', '5000.00'],
[609, '', u'Элан-Инет', '05.00', '5000.00'],
[615, '', u'Нашнет', '01.00', '5000.00'],
[617, '', u'ЛокалНет (LocalNet)  ', '10.00', '5000.00'],
[647, '', u'Билинк', '01.00', '5000.00'],
[651, '', u'Интермедия ТВ', '01.00', '5000.00'],
[658, 'vega', u'Вега интерент(ЦСС)   ', '01.00', '5000.00'],
[659, 'vega', u'Вега телефония (ЭЛС)', '01.00', '5000.00'],
[660, 'vega', u'Вега интерент (ЭЛС)  ', '01.00', '5000.00'],
[661, 'vega', u'Вега интернет (Інтерком)    ', '01.00', '5000.00'],
[709, '', u'И-нет(I-NET) ', '01.00', '5000.00']
],

'money_services':
[
[246, '', u'Веб Мани WMU(Online)', '01.00', '1000.00'],
[351, '', u'Пополнение кошельков EasyPay (по № кошелька)', '00.01', '5000.00'],
[448, '', u'Единый кошелек', '00.10', '5000.00']
],

'tv_services':
[
[336, '', u'Воля Киев (Интернет и ТВ)', '01.00', '1000.00'],
[353, '', u'Триолан Харьков Базис ТВ', '01.00', '1000.00'],
[355, '', u'Триолан Харьков-Эпсилон ТВ', '01.00', '1000.00'],
[357, '', u'Триолан Харьков-Березка ТВ', '01.00', '1000.00'],
[359, '', u'Триолан Харьков-ІТ сервис ТВ', '01.00', '1000.00'],
[361, '', u'Триолан Полтава ТВ', '01.00', '1000.00'],
[363, '', u'Триолан Днепропетровск ТВ', '01.00', '1000.00'],
[365, '', u'Триолан Запорожье ТВ', '01.00', '1000.00'],
[367, '', u'Триолан Одесса ТВ', '01.00', '1000.00'],
[369, '', u'Триолан Донецк ТВ', '01.00', '1000.00'],
[371, '', u'Триолан Луганск ТВ', '01.00', '1000.00'],
[373, '', u'Триолан Симферополь ТВ', '01.00', '1000.00'],
[380, '', u'Мисто-ТВ (ТВ)', '01.00', '1000.00'],
[382, '', u'МаксНет интернет', '01.00', '5000.00'],
[383, '', u'МаксНет ТВ', '01.00', '5000.00'],
[384, '', u'МаксНет стац. тел.', '01.00', '5000.00'],
[404, '', u'Воля  Винница (Интернет и ТВ) ', '01.00', '1000.00'],
[407, '', u'Воля Львов (Интернет и ТВ)', '01.00', '1000.00'],
[424, '', u'Воля Кировоград КАБС (Интернет и ТВ)', '01.00', '5000.00'],
[426, '', u'Воля Запорожье КИТС (ТВ)', '01.00', '5000.00'],
[428, '', u'Воля Донецк (Интернет и ТВ) ', '01.00', '5000.00'],
[438, '', u'Мисто-ТВ (Интернет)', '01.00', '1000.00'],
[449, '', u'Воля Хмельницкий ТВ-Сервис (Интернет и ТВ)', '01.00', '5000.00'],
[465, '', u'Триолан Киев ТВ ', '01.00', '1000.00'],
[474, '', u'Воля Харьков Притекс (Интернет и ТВ)', '01.00', '5000.00'],
[519, '', u'Май ТВ(MYtv)', '01.00', '5000.00'],
[527, '', u'Виасат (прямой)', '00.01', '5000.00'],
[539, 'volia-kiev', u'Воля Киев без в/к (Аналоговое ТВ)', '01.00', '1000.00'],
[540, 'volia-kiev', u'Воля Киев без в/к (Премиум ТВ)', '01.00', '1000.00'],
[541, 'volia-kiev', u'Воля Киев без в/к (Интернет и ТВ)', '01.00', '1000.00'],
[546, '', u'Воля Винница без в/к (Аналог. ТВ)', '01.00', '1000.00'],
[547, '', u'Воля Винница без в/к (Премиум ТВ)', '01.00', '1000.00'],
[548, '', u'Воля Винница без в/к (Интернет и ТВ)', '01.00', '1000.00'],
[574, '', u'Воля Краматорск (Интернет и ТВ)', '01.00', '5000.00'],
[575, '', u'Воля Хмельницкий ТВ-Сервис без в/к (Интернет и ТВ)', '01.00', '5000.00'],
[576, '', u'Воля Хмельницкий ТВ-Сервіс без в/к (ТВ)', '01.00', '5000.00']
]
}


class _mob(QWidget):

    def __init__(self,d):
        
        
        l=d['l']
        lang=d['lang']
        self.l=l
        self.lang=lang
        self.d=d
        self.selected = 0
        
        QWidget.__init__(self)
        #self.setupUi(self)
        self.setObjectName(_fromUtf8("Mob"))

        font = QFont()
        font.setPointSize(19)
        font.setWeight(75)
        font.setBold(False)

        operFont = QFont()
        operFont.setPointSize(12)
        operFont.setWeight(75)
        operFont.setBold(False)
	
	tabWidth = 920
	tabHeight = 870

	tabsCount = 0
	self.tabs = []
	self.buttons = []
	for serviceKey in servicesOrder: #services.keys():
	    if serviceKey in availableServices:
		button = myButton(l[serviceKey][lang],self)
		button.setObjectName(str(tabsCount))
		button.setGeometry(10,180+tabsCount*120,300,100)
		#button.setStyleSheet('* {background-color: #DDDDDD; color: #333333;} *:checked {background-color: green; color: white;}')
		button.setFocusPolicy(Qt.NoFocus)
		button.setStyleSheet("""
* {background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 white, stop:0.5 rgba(33,152,17,200), stop:1 rgba(33,152,17,250)); 
border: 3px solid rgba(33,152,17,200); 
border-radius: 10px; color: white;}
*:checked {
background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(33,152,17,250), stop:0.5 rgba(33,152,17,200), stop:1 white); 
border: 3px solid rgba(33,152,17,200); 
border-radius: 10px; color: white;}
	    """)

		button.setCheckable(True)
		button.setFont(font)
		self.connect(button, SIGNAL("clicked(QString)"), self.groupClicked)
		self.buttons.append(button)
	    
		tab=QWidget(self)
		tab.setGeometry(QRect(350, 120, tabWidth, tabHeight))
		tab.setVisible(False)
		self.tabs.append(tab)
		#self.tabs.addTab(tab, QIcon('./payments/mobile.png'), unicode('Mobile'))

		tab.label = QLabel(tab)
		tab.label.setFont(font)
		tab.label.setObjectName(_fromUtf8("label"))
		tab.label.setGeometry(QRect(10, 1, 600, 50))
		tab.label.setText(l[serviceKey][lang])
		tab.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

		width = 150
		height = 150
		xstart=10
		ystart=60
		xstep=165
		ystep=165
		x=xstart
		y=ystart
		self.labels = {}
		group = services[serviceKey]
		for operator in group:
		    label = mainLabel(operator[SERVICE_NAME],tab)
		    #label.setStyleSheet('background: qlineargradient(x1:0, x2:0, y1:1, y2:1, stop:0 white, stop:0.5 gray, stop:1 green); background-image: url("./payments/logo-'+operator[SERVICE]+'.gif"); background-color: transparent; background-position: top center; background-repeat: no-repeat; background-origin: content; border: 1px solid #777777; border-radius: 10px; color: #777777;')
		    if operator[SERVICE]:
			logo = 'image: url("./payments/logo-'+operator[SERVICE]+'.gif"); '
		    else:
			logo =''
		    label.setStyleSheet('background: qlineargradient(x1:0, y1:0.7, x2:0, y2:1.1, stop:0 white, stop:0.3 rgba(50,50,50,30));'+logo+'image-position: top center; padding-top: 10px; border: 1px solid #777777; border-radius: 7px; color: #555555;')
		    label.setGeometry(QRect(x,y,width,height))
		    label.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
		    label.setWordWrap(True)
		    label.setFont(operFont)
		    label.setObjectName(str(operator[SERVICE_ID]))
		    label.setVisible(True)
		    self.connect(label,  SIGNAL("linkActivated(QString)"),  self.oper)
		    self.labels[operator[SERVICE]] = label
		    if x+width*2+15 > tabWidth-20: 
			x = xstart;
			y += ystep
		    else:
			x += xstep
		tabsCount+=1

	if self.tabs: self.tabs[0].setVisible(True)
	if self.buttons: self.buttons[0].setChecked(True)
        
        #self.label1 = QLabel(self)
        #self.label1.setFont(font)
        #self.label1.setObjectName(_fromUtf8("mobile"))
        #self.label1.setGeometry(QRect(10, 200, 1260, 500))
        #self.label1.setText(unicode(open("./payments/mobile.htm").read().decode('utf-8')))
        #print self.label1.text().encode('utf-8')
        #self.label1.setAlignment(Qt.AlignLeft | Qt.AlignTop)

	font = QFont()
        font.setPointSize(22)
        font.setWeight(75)
        font.setBold(False)

        self.top = QWidget(self)
        self.top.setAutoFillBackground(True)
        self.top.setObjectName(_fromUtf8("top"))
        self.top.setGeometry(QRect(0, 0, d['xres']+1, 120))

        self.b_help = QPushButton(self.top)
        self.b_help.setFont(font)
        self.b_help.setObjectName(_fromUtf8("b_help"))
        self.b_help.setGeometry(QRect((d['xres']-250), 15, 220, 90))
        self.b_help.setText(l['help'][lang])
        self.b_help.setFocusPolicy(Qt.NoFocus)

        self.b_main = QPushButton(self.top)
        self.b_main.setFont(font)
        self.b_main.setObjectName(_fromUtf8("b_main"))
        self.b_main.setGeometry(QRect(30, 15, 400, 90))
        self.b_main.setText(l['menu'][lang])
        self.b_main.setFocusPolicy(Qt.NoFocus)

        self.stimer = QTimer()
        self.stimer.setInterval(10000)
        self.connect(self.stimer, SIGNAL("timeout()"), self.close)
        self.connect(self.b_main,  SIGNAL("clicked()"),  self.main)
        self.connect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
        
        self.d['log'].log("MAIN: payment selected")


    def groupClicked(self, name):
	self.stimer.start()
	n = int(name)
	self.buttons[self.selected].setChecked(False)
	self.buttons[n].setChecked(True)
	self.tabs[self.selected].hide()
	self.tabs[n].show()
	self.selected = n


    def oper(self, operator):
	self.stimer.stop()
	#self.disconnect(self.stimer, SIGNAL("timeout()"), self.close)
        self.d['mob_oper'] = operator
        self.d['service'] = operator
        self.d['serviceKey'] = self.selected

        for serv in services[availableServices[self.selected]]:
	    if serv[SERVICE_ID] == int(operator):
		service = serv
		break
        self.d['payment_type'] = service[PTYPE]
        self.d['service_name'] = service[SERVICE_NAME]
	print self.d['payment_type']
        self.d['log'].log("PAYMENT: SERVICE %s SELECTED (%s)" % (self.d['service'],operator))
        self.d['mob_num'] = _mob_num(self.d);  
        self.d['mob_num'].showFullScreen()
        #self.close()
        
    def helpbox(self):
	self.stimer.stop()
	self.d['log'].log("PAYMENT: help called")
        hb = helpBox('payment',  self.d)
        hb.exec_()


    def main(self):
	self.stimer.stop()
	self.d['log'].log("PAYMENT: main pressed")
	self.disconnect(self.stimer, SIGNAL("timeout()"), self.close)
        self.close()

    def closeEvent(self,event):
        self.disconnect(self.stimer, SIGNAL("timeout()"), self.close)
        self.disconnect(self.b_main,  SIGNAL("clicked()"),  self.main)
        self.disconnect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
        event.accept()

    def enterEvent(self,event):
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.main)
	self.stimer.stop()
	self.stimer.start()
	event.accept()

    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.main)
	self.stimer.stop()
	event.accept()
	

class mainLabel(QLabel):
    def mouseReleaseEvent(self,event):
	s=self.objectName()
	self.emit(SIGNAL("linkActivated(QString)"), s)
	event.accept()


class myButton(QPushButton):
    def mouseReleaseEvent(self,event):
	s=self.objectName()
	self.emit(SIGNAL("clicked(QString)"), s)
	event.accept()

