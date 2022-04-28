# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Mob_charge import _mob_charge
from request import *
from dialogs import *

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class _mob_num(QWidget):

    def __init__(self,d):
        QWidget.__init__(self)
        self.setObjectName(_fromUtf8("Mob_num"))
        self.d=d
        self.l=d['l']
        l=d['l']
        lang=d['lang']
        self.lang=d['lang']
        self.operator=d['mob_oper']
        
        self.dig=10
        self.pos=0
        self.a=['.']*self.dig

        font = QFont()
        font.setPointSize(22)
        font.setWeight(75)
        font.setBold(False)

        self.numpad = QWidget(self)
        self.numpad.setObjectName(_fromUtf8("numpad"))
        self.numpad.setGeometry(QRect((self.d['xres']-380)//2, 480, 380, 500))
        self.numpad.show()

        self.b_erase = QPushButton(self)
        self.b_erase.setFont(font)
        self.b_erase.setObjectName(_fromUtf8("b_erase"))
        self.b_erase.setEnabled(False)
        self.b_erase.setFocusPolicy(Qt.NoFocus)

        self.b_erase2 = QPushButton(self)
        self.b_erase2.setFont(font)
        self.b_erase2.setObjectName(_fromUtf8("b_erase2"))
        self.b_erase2.setEnabled(False)
        self.b_erase2.setFocusPolicy(Qt.NoFocus)
        self.b_erase2.setGeometry(QRect(1100, 280, 90, 90))

        
        self.bgroup=QButtonGroup(self.numpad)
        
        self.but={}
        for x in range(10):
    	    self.but[x] = QPushButton(self)
            self.but[x].setText(str(x))
            self.but[x].setObjectName(_fromUtf8("b%d" % x))
            self.but[x].setFont(QFont("Helvetica", 32, 90))
            self.but[x].setFocusPolicy(Qt.NoFocus)
            self.but[x].setVisible(True)
            self.bgroup.addButton(self.but[x],x)


        bx=(d['xres']-300)//2
        C=[bx,bx+105,bx+210]
           
        by=510
        R=[by,by+110,by+220,by+330]

        x=1
        for r in R:
	    for c in C:
		if x<10: self.but[x].setGeometry(QRect(c, r, 90, 90))
		elif x==11: self.but[0].setGeometry(QRect(c, r, 90, 90))
		elif x==12: self.b_erase.setGeometry(QRect(c, r, 90, 90))
		x+=1

        self.b_pay = QPushButton(self)
        self.b_pay.setObjectName(_fromUtf8("b_pay"))
        self.b_pay.setGeometry(QRect(910, 650, 300, 95))
        self.b_pay.setText(l['next'][lang])
        self.b_pay.setFont(font)
        self.b_pay.setFocusPolicy(Qt.NoFocus)
        self.b_pay.setEnabled(False)
        self.b_pay.hide()
        
        self.b_back = QPushButton(self)
        self.b_back.setGeometry(QRect(70, 650, 300, 95))
        self.b_back.setText(l['back'][lang])
        self.b_back.setFont(font)
        self.b_back.setFocusPolicy(Qt.NoFocus)
        self.b_back.setObjectName(_fromUtf8("b_back"))
        
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

        self.label = QLabel(self)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label.setGeometry(QRect((d['xres']-600)//2, 160, 600, 50))
        self.label.setText(l['mob_num'][lang])
        self.label.setAlignment(Qt.AlignCenter)

        self.number = QLabel(self)
        self.number.setFont(font)
        self.number.setObjectName(_fromUtf8("number"))
        self.number.setGeometry(QRect((d['xres']-900)//2, 250, 900, 160))
        self.number.setAlignment(Qt.AlignCenter)
        self.number.setFont(QFont("Helvetica", 72, 50))

        self.stimer = QTimer()
        self.stimer.setInterval(30000)
        self.connect(self.stimer, SIGNAL("timeout()"), self.close)
        self.connect(self.bgroup, SIGNAL("buttonClicked(int)"), self.digit)
        self.connect(self.b_erase, SIGNAL("clicked()"), self.bs)
        self.connect(self.b_erase2, SIGNAL("clicked()"), self.bs)
        self.connect(self.b_pay, SIGNAL("clicked()"), self.pay)
        self.connect(self.b_back,  SIGNAL("clicked()"),  self.back)
        self.connect(self.b_main,  SIGNAL("clicked()"),  self.main)
        self.connect(self.b_help, SIGNAL("clicked()"), self.helpbox)

        self.update()
        self.d['log'].log("PAYMENT: ACCOUNT INPUT: displayed")


    def digit(self,d):
        #print  d
        if self.pos==0:
            self.b_erase.setEnabled(True)
            self.b_erase2.setEnabled(True)
        if self.pos<self.dig: 
            self.a[self.pos]=d
            self.pos=self.pos+1;
            if self.pos==self.dig:
               self.b_pay.setEnabled(True)
               self.b_pay.show()
               for x in range(10):
                  self.but[x].setEnabled(False)
            self.update()


    def get(self,operator):
        self.operator=operator
        self.pos=0
        self.a=['.']*self.dig
        self.b_pay.setEnabled(False)
        self.b_pay.hide()
        self.b_erase.setEnabled(False)
        self.b_erase2.setEnabled(False)
        for x in range(10):
            self.but[x].setEnabled(True)
        self.update()
        self.showFullScreen()
        return 1

    def update(self):
        self.stimer.start()
        number=""
        for x in self.a: 
            number=number+str(x)
        s="+38 ("+number[0:3]+")"+number[3:]
        
        ss=''
        for x in s:
            if x=='.': x=' .';
            ss+=x
        self.number.setText(ss)

    def bs(self):                         #Нажатие BackSpase
        if (self.pos>0):
            if self.pos==self.dig: 
                self.b_pay.setEnabled(False)
                self.b_pay.hide()
            for x in range(10):
                self.but[x].setEnabled(True)
            self.pos=self.pos-1
            self.a[self.pos]='.'
        if self.pos==0:
            self.b_erase.setEnabled(False)
            self.b_erase2.setEnabled(False)
        self.update()

    def pay(self):
	self.stimer.stop()                          #Нажатие кнопки ОПЛАТИТЬ
        self.b_pay.setEnabled(False)
        self.b_pay.hide()
        n="";
        if self.pos == self.dig: 
            for x in self.a:
                n=n+str(x)
        else: n="0"
        print "account number: ",n
        self.d['account']=n
        self.d['log'].log("PAYMENT: ACCOUNT INPUT: PAY clicked with account N (%s)" % (n))

        if _valid(self.d).exec_():                      #Проверка номера успешна
            self.d['mob_charge'] = _mob_charge(self.d)
            self.d['mob_charge'].showFullScreen()     #Окно внесения наличных
            #self.close()               #Закрытие окна ввода номера
        else: 
            #self.d['mob_num'].b_pay.setEnabled(True)
            self.d['mob_num'].b_pay.show()



    def helpbox(self):
        self.stimer.stop()
        hb=helpBox('payment', self.d)
        self.d['log'].log("PAYMENT: ACCOUNT INPUT: help clicked")
        hb.exec_()

    def back(self):
        self.stimer.stop()
        self.d['log'].log("PAYMENT: ACCOUNT INPUT: back clicked")
        self.close()
        
    def main(self):
        self.stimer.stop()
        if 'mob' in self.d.keys(): self.d['mob'].close()
        self.d['log'].log("PAYMENT: ACCOUNT INPUT: main clicked")
        self.close()
        
    def timeout(self):
	self.stimer.stop()
        self.d['log'].log("PAYMENT: ACCOUNT INPUT: timeout")
	self.close()
        
    def closeEvent(self, event):
	self.stimer.stop()
	self.disconnect(self.stimer, SIGNAL("timeout()"), self.close)
        self.disconnect(self.bgroup, SIGNAL("buttonClicked(int)"), self.digit)
        self.disconnect(self.b_erase, SIGNAL("clicked()"), self.bs)
        self.disconnect(self.b_erase2, SIGNAL("clicked()"), self.bs)
        self.disconnect(self.b_pay, SIGNAL("clicked()"), self.pay)
        self.disconnect(self.b_back,  SIGNAL("clicked()"),  self.back)
        self.disconnect(self.b_main,  SIGNAL("clicked()"),  self.main)
        self.disconnect(self.b_help, SIGNAL("clicked()"), self.helpbox)

	event.accept()

    def enterEvent(self, event):
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.close)
	self.update()
	event.accept()

    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.close)
	event.accept


##############################################################################################################################
# CLASS VALID
##############################################################################################################################

class _valid(QDialog):
    def __init__(self,d):
	QDialog.__init__(self)
	self.d = d
	self.l = d['l']
	self.lang = d['lang']

	self.setStyleSheet('* { background-color: transparent;}')
	drawBackground(self, d)

	font = QFont()
        font.setPointSize(24)
        font.setWeight(50)
        font.setBold(False)

	self.label=QLabel(self.l['account_check'][self.lang], self)
	self.label.setObjectName('scanfinishlabel')
	self.stylesheetBLUE='background-image: url("img/scan/finish_scan.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.stylesheetRED='background-image: url("img/mob/error_number.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.label.setStyleSheet(self.stylesheetBLUE)
	self.label.setFont(font)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,d['xres']-480,450))
	self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
	self.label.setVisible(True)
	
	self.retTimer = QTimer()
	self.connect(self.retTimer, SIGNAL("timeout()"), self.toMain)
	
	self.b_back = QPushButton('OK',self)
	self.connect(self.b_back, SIGNAL("clicked()"), self.ret)
	self.b_back.setVisible(False)
	self.b_back.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_back.setFont(font)
	self.b_back.setGeometry(QRect((d['xres']-300)//2, 550, 300, 100))
	self.b_back.setFocusPolicy(Qt.NoFocus)

        self.setAutoFillBackground(True)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        
        print "service: ", d['service']
        self.d['payment'] = payment(account=d['account'],service=d['service'],partner=d['partnerObjectId'])
	
	#self.connect(self.d['payment'], SIGNAL("success()"), self.partOK)
	#self.connect(self.d['payment'], SIGNAL("error()"), self.partERR)
	#self.d['ping'].dontdisconnect()	
	#self.d['payment'].partnerInfo()
	
	self.d['ping'].dontdisconnect()

	self.connect(self.d['payment'], SIGNAL("success()"), self.checkOK)
	self.connect(self.d['payment'], SIGNAL("error()"), self.checkERR)
	self.d['payment'].check()
	

    def checkOK(self):
	self.disconnect(self.d['payment'], SIGNAL("error()"), self.checkERR)
	self.disconnect(self.d['payment'], SIGNAL("success()"), self.checkOK)

	print self.d['payment'].checkStatusDetail
	print "original service: ", self.d['payment'].service
	self.d['log'].log("PAYMENT: ACCOUNT VERIFY: account OK: %s(%s)" % (self.d['payment'].account,self.d['payment'].checkStatusDetail))
	#self.checkMessage.close()
	self.retTimer.stop()
	self.accept() ############################### OK
	
	#self.d['payment'].partnerInfo()
	#self.connect(self.d['payment'], SIGNAL("success()"), self.partOK)
	#self.connect(self.d['payment'], SIGNAL("error()"), ERR)

    def checkERR(self):
	self.disconnect(self.d['payment'], SIGNAL("success()"), self.checkOK)
	self.disconnect(self.d['payment'], SIGNAL("error()"), self.checkERR)

	#self.l.setText(self.d['payment'].errorType + self.d['payment'].errorDetail)
	print self.d['payment'].errorType, self.d['payment'].errorDetail
	self.d['log'].log("PAYMENT: ACCOUNT VERIFY: check error: %s(%s)" % (self.d['payment'].account, str(self.d['payment'].errorType) + str(self.d['payment'].errorDetail)))
	####################
	#self.checkMessage.close()
	n = str(self.d['payment'].account) 
	snum="+38 ("+n[0:3]+") "+n[3:]
	self.label.setText(self.l['invalid_number'][self.lang] % snum)
	self.label.setStyleSheet(self.stylesheetRED)
	self.b_back.show()
	self.retTimer.start(7000)


    def partOK(self):
	self.disconnect(self.d['payment'], SIGNAL("success()"), self.partOK)
	self.disconnect(self.d['payment'], SIGNAL("error()"), self.partERR)

	print self.d['payment'].partnerStatusDetail
	self.d['log'].log("PAYMENT: ACCOUNT VERIFY: partnerInfo is OK")

	self.connect(self.d['payment'], SIGNAL("error()"), self.servERR)
	self.connect(self.d['payment'], SIGNAL("success()"), self.servOK)
	self.d['payment'].services()

	#self.connect(self.d['payment'], SIGNAL("success()"), self.checkOK)
	#self.connect(self.d['payment'], SIGNAL("error()"), self.checkERR)
	#self.d['payment'].check()

    def partERR(self):
	self.disconnect(self.d['payment'], SIGNAL("success()"), self.partOK)
	self.disconnect(self.d['payment'], SIGNAL("error()"), self.partERR)

	#self.l.setText(self.d['payment'].errorType + self.d['payment'].errorDetail)
	print self.d['payment'].errorType, self.d['payment'].errorDetail
	self.d['log'].log("PAYMENT: ACCOUNT VERIFY: partnerInfo get error: (%s)" % (self.d['payment'].errorType))
	####################
	#self.checkMessage.close()
	n = str(self.d['payment'].account) 
	snum="+38 ("+n[0:3]+") "+n[3:]
	self.label.setText(self.l['invalid_number'][self.lang] % snum)
	self.b_back.show()
	self.retTimer.start(7000)

    def servOK(self):
	self.disconnect(self.d['payment'], SIGNAL("error()"), self.servERR)
	self.disconnect(self.d['payment'], SIGNAL("success()"), self.servOK)

	print self.d['payment'].servicesStatusDetail
	self.d['log'].log("PAYMENT: SERVICES: %s" % (self.d['payment'].servicesStatusDetail))
	#self.checkMessage.close()
	self.retTimer.stop()
	self.accept() ############################### OK
	
	#self.d['payment'].partnerInfo()
	#self.connect(self.d['payment'], SIGNAL("success()"), self.partOK)
	#self.connect(self.d['payment'], SIGNAL("error()"), ERR)

    def servERR(self):
	self.disconnect(self.d['payment'], SIGNAL("error()"), self.servERR)
	self.disconnect(self.d['payment'], SIGNAL("success()"), self.servOK)

	#self.l.setText(self.d['payment'].errorType + self.d['payment'].errorDetail)
	print self.d['payment'].errorType, self.d['payment'].errorDetail
	self.d['log'].log("PAYMENT: SERVICES: %s" % (str(self.d['payment'].errorType) + str(self.d['payment'].errorDetail)))
	####################
	#self.checkMessage.close()
	self.retTimer.start(1000)


    def ret(self):
	#self.d['mob_num'].close()
        self.retTimer.stop()
        self.reject()

    def toMain(self):
	self.retTimer.stop()
	self.d['mob_num'].close()
	self.d['mob'].close()
        self.reject()
	
##############################################################################################################


class _confNum(QDialog):
    def __init__(self,d):
        QDialog.__init__(self)
        l=d['l']
        
        label=QLabel(str(d['account']),self)
        label.setGeometry((d['xres']-600)//2, 200, 600, 100)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Helvetica", 45, 75))
        
        yes=QPushButton(l['pay'][d['lang']],self)
        yes.setGeometry((d['xres']-200)//2-200,d['yres']-200,200,100)
        self.connect(yes, SIGNAL("clicked()"), self, SLOT("accept()"))
        yes.setDefault(True)
        
        no=QPushButton(l['back'][d['lang']],self)
        no.setGeometry((d['xres']-100)//2+200,d['yres']-200,200,100)
        self.connect(no, SIGNAL("clicked()"), self, SLOT("reject()"))
        
        self.stimer = QTimer()
	self.stimer.singleShot(10000, self.reject)
        
        self.setAutoFillBackground(False)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()


