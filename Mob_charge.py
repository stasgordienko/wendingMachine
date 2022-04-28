# -*- coding: utf-8 -*-
from __future__ import division

import db
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from os import *
import sys
from PyQt4.QtCore import (QByteArray, QDataStream, QDate, QIODevice,
        QRegExp, QString, Qt, SIGNAL)
from PyQt4.QtGui import (QApplication, QDateEdit, QFrame, QGridLayout,
        QHBoxLayout, QLabel, QLineEdit, QPushButton, QRegExpValidator, QWidget)
from request import *
from dialogs import *
import subprocess
import Mob


try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

#################################################################################################################

class _mob_pay(QWidget):
    def __init__(self,d):
	QWidget.__init__(self)
	self.setObjectName(_fromUtf8("Mob_pay"))
        self.d=d
        self.l=d['l']
        self.lang=d['lang']
	
	self.setStyleSheet('* { background-color: transparent;}')
	drawBackground(self, d)

	font = QFont()
        font.setPointSize(24)
        font.setWeight(50)
        font.setBold(False)

	self.label=QLabel(self.l['payment_run'][self.lang], self)
	self.label.setObjectName('scanfinishlabel')
	self.stylesheetBLUE='background-image: url("img/scan/finish_scan.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.stylesheetGREEN='background-image: url("img/mob/payment_ok.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.label.setStyleSheet(self.stylesheetBLUE)
	self.label.setFont(font)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,d['xres']-480,450))
	self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
	self.label.setVisible(True)

	self.retTimer = QTimer()
	self.connect(self.retTimer, SIGNAL("timeout()"), self.toMain)
	
	self.b_back = QPushButton(self.l['dont_print_check'][self.lang],self)
	self.connect(self.b_back, SIGNAL("clicked()"), self.toMain)
	self.b_back.setVisible(False)
	self.b_back.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_back.setFont(font)
	self.b_back.setGeometry(QRect((d['xres']-250)//2+160, 550, 300, 90))
	self.b_back.setFocusPolicy(Qt.NoFocus)

	self.b_print = QPushButton(self.l['print_check'][self.lang],self)
	self.connect(self.b_print, SIGNAL("clicked()"), self.printCheck)
	self.b_print.setVisible(False)
	self.b_print.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_print.setFont(font)
	self.b_print.setGeometry(QRect((d['xres']-250)//2-200, 550, 300, 90))
	self.b_print.setFocusPolicy(Qt.NoFocus)


	
        self.setAutoFillBackground(True)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

        d['n_payment']=str(int(d['n_payment'])+1);
        
        self.d['ping'].dontdisconnect()

	self.connect(self.d['payment'], SIGNAL("success()"), self.payOK)
	self.connect(self.d['payment'], SIGNAL("error()"), self.ERR)
	self.d['payment'].pay(order = d['n_payment'], amount = d['amount'])


    def payOK(self):
	self.disconnect(self.d['payment'], SIGNAL("success()"), self.payOK)
	self.disconnect(self.d['payment'], SIGNAL("error()"), self.ERR)
        summ = self.d['balance']/100 #self.d['payment'].amount + self.d['payment'].tax
        self.d['balance'] = 0 #-= int(summ * 100)
        self.d['action'].usedsumm += summ
        self.d['action'].finish(status='success')
        del self.d['action']

	log="#HTTP:" + self.d['payment'].confirmReplyHttpCode #+ self.d['payment'].confirmStatusDetail
	db.payment(termId=self.d['device'], actionId=0, order=self.d['n_payment'], payment=self.d['payment'].paymentId, 
		    service=self.d['payment'].service, account=self.d['payment'].account, amount=self.d['payment'].amount, 
		    status=self.d['payment'].orderStatus, paymentDate=self.d['payment'].paymentDate, tax=self.d['payment'].tax, 
		    partner=self.d['payment'].partner, checkPrinted='0', log=log)
	print self.d['payment'].paymentId, " ", self.d['payment'].confirmStatusDetail
	self.d['log'].log("PAYMENT: CHARGE: SUCCESS. Account: %s, Amount: %5.2f, Payment: %s, Status: %s" % (self.d['payment'].account,float(self.d['payment'].amount),self.d['payment'].paymentId,self.d['payment'].orderStatus))
	#self.accept() ############################### OK
	#self.payMessage.close()
	n = str(self.d['payment'].account) 
	snum="+38 ("+n[0:3]+") "+n[3:]
	self.label.setText(self.l['payment_ok'][self.lang] % snum)
	self.label.setStyleSheet(self.stylesheetGREEN)
	self.b_back.show()
	self.b_print.show()
	self.retTimer.start(15000)

        ###self.d['payment'].status()
	###self.connect(self.d['payment'], SIGNAL("success()"), self.statusOK)

    def ERR(self):
	self.disconnect(self.d['payment'], SIGNAL("success()"), self.payOK)
	self.disconnect(self.d['payment'], SIGNAL("error()"), self.ERR)
	#self.l.setText(self.d['payment'].errorType + self.d['payment'].errorDetail)
	print self.d['payment'].errorType, self.d['payment'].errorDetail

        summ = self.d['balance']/100 #self.d['payment'].amount + self.d['payment'].tax
        self.d['balance'] = 0 #-= int(summ * 100)
        self.d['action'].usedsumm += summ
        self.d['action'].finish(status='error')
        del self.d['action']

	log="#HTTP:" + self.d['payment'].errorCode #+ self.d['payment'].paymentStatusDetail
	db.payment(termId=self.d['device'], actionId='', order=self.d['n_payment'], payment=self.d['payment'].paymentId, 
		    service=self.d['payment'].service, account=self.d['payment'].account, amount=self.d['payment'].amount, 
		    status=str(self.d['payment'].errorType) + ":" + str(self.d['payment'].errorDetail), paymentDate=self.d['payment'].paymentDate, 
		    tax=self.d['payment'].tax, partner=self.d['payment'].partner, checkPrinted='0', log=log)
	####################
	#ERROR. WRITE payment to DATABASE as TRYtoSENDlater and Dispaly Message "Your account will be charged soon..." 
	self.d['log'].log("PAYMENT: CHARGE: ERROR confirmation. Account: %s, Amount: %5.2f, Payment: %s, Status: %s" % (self.d['payment'].account,float(self.d['payment'].amount),self.d['payment'].paymentId,self.d['payment'].orderStatus))
	#self.payMessage.close()

	n = str(self.d['payment'].account) 
	snum="+38 ("+n[0:3]+") "+n[3:]
	self.label.setText(self.l['payment_later'][self.lang] % snum)
	self.label.setStyleSheet(self.stylesheetGREEN)
	self.b_back.show()
	self.b_print.show()
	self.retTimer.start(7000)


    def statusOK(self):
	self.disconnect(self.d['payment'], SIGNAL("success()"), self.statusOK)
	self.disconnect(self.d['payment'], SIGNAL("error()"), self.ERR)

	print self.d['payment'].statusStatusDetail
	#self.accept() ############################### OK

    def printCheck(self):
	#Возьмите чек
	self.label.setText(self.l['take_check'][self.lang])
	self.label.setStyleSheet(self.stylesheetGREEN)
	self.b_back.setGeometry(QRect((self.d['xres']-300)//2, 550, 300, 90))
	self.b_back.setText(u'OK')
	self.b_back.show()
	self.b_print.hide()
	self.retTimer.start(15000)

	resolution = 600 #dpi
	
	for p in QPrinterInfo.availablePrinters():
	    if p.isDefault():
		defaultPrinter=p
		print "DEFAULT PRINTER:",
	print p.printerName()

	printer=QPrinter(defaultPrinter, QPrinter.HighResolution)
	printer.setPrinterName(QString("xerox4118"))
	#printer.setColorMode(QPrinter.GrayScale)
	printer.setOutputFormat(QPrinter.NativeFormat)
	printer.setResolution(resolution)
	printer.setDuplex(QPrinter.DuplexLongSide)
	printer.setDoubleSidedPrinting(False)
	printer.setPageMargins(0,0,0,0,QPrinter.DevicePixel)
	printer.setPaperSize(QPrinter.A4)
	printer.setFullPage(True)
	printer.setOrientation(QPrinter.Portrait)

	#dlg=QPrintDialog(printer)

	print "printer.printerName():",printer.printerName()
	print "printer.pageRect():",printer.pageRect()
	print "printer.paperRect():",printer.paperRect()
	print "printer.physicalDpiX():",printer.physicalDpiX()
	print "printer.physicalDpiY():",printer.physicalDpiY()
	print "printer.supportedResolutions():",printer.supportedResolutions()
	print "printer.doubleSidedPrinting():",printer.doubleSidedPrinting()
	print "printer.resolution():",printer.resolution()
	print "printer.fullPage():",printer.fullPage()
	print "printer.isValid():",printer.isValid()
	print "printer.paperSize():",printer.paperSize()
	print "printer.orientation():",printer.orientation()


	font = QFont()
        font.setPointSize(10)
        font.setWeight(50)
        font.setBold(False)

	print subprocess.call(['sudo', './usbReset','0x0924','0x420c']) #reset xerox-4118 usb-printer

	painter = QPainter()
	painter.begin(printer)
	painter.setFont(font)
	#painter.drawText(QRect(100,150,1000,1000),Qt.TextSingleLine, u'check')
	painter.drawText(QRect(100,100,4800,500),Qt.AlignLeft, '-----------------------------------------------------------------------------------------------------------------------------------------------------')
	painter.drawText(QRect(100,200,1500,500),Qt.AlignHCenter, 'CopyPrime')
	painter.drawText(QRect(100,300,1500,500),Qt.AlignHCenter, 'support@copyprime.com.ua')
	painter.drawText(QRect(100,400,1500,500),Qt.AlignHCenter, '')
	painter.drawText(QRect(100,500,1500,500),Qt.AlignHCenter, u'Сохраняйте чек')
	painter.drawText(QRect(100,600,1500,500),Qt.AlignHCenter, u'до момента поступления')
	painter.drawText(QRect(100,700,1500,500),Qt.AlignHCenter, u'средств на счет')
	painter.drawText(QRect(100,800,4800,500),Qt.AlignLeft, '-----------------------------------------------------------------------------------------------------------------------------------------------------')
	painter.drawText(QRect(100,900,4800,500),Qt.AlignHCenter, u'Благодарим за пользованием терминалом!')
	painter.drawText(QRect(100,1000,4800,500),Qt.AlignLeft, '----------------------------------------------------------------------------------------------------------------------------------------------------')

	painter.drawText(QRect(1600,200,1400,500),Qt.AlignLeft, u'Терминал: %d' % (int(self.d['device'])))
	painter.drawText(QRect(1600,300,1400,500),Qt.AlignLeft, u'Номер чека: %d' % (int(self.d['payment'].order)))
	painter.drawText(QRect(1600,400,1400,500),Qt.AlignLeft, u'Дата: %s' % (self.d['payment'].paymentDate.split('T')[0]))
	painter.drawText(QRect(1600,500,1400,500),Qt.AlignLeft, u'Время: %s' % (self.d['payment'].paymentDate.split('T')[1]))
	painter.drawText(QRect(1600,600,1400,500),Qt.AlignLeft, u'Оператор: %s' % (self.d['service_name']))

	painter.drawText(QRect(3000,200,1500,500),Qt.AlignLeft, u'Тип платежа: %s' % (u'по № телефона'))
	painter.drawText(QRect(3000,300,1500,500),Qt.AlignLeft, u'№ тел: %s' % (str(self.d['payment'].account)))
	painter.drawText(QRect(3000,400,1500,500),Qt.AlignLeft, u'Внесено: %4.2f грн' % (float(self.d['payment'].tax)+float(self.d['payment'].amount)))
	painter.drawText(QRect(3000,500,1500,500),Qt.AlignLeft, u'Комиссия: %4.2f грн' % (float(self.d['payment'].tax)))
	painter.drawText(QRect(3000,600,1500,500),Qt.AlignLeft, u'Зачислено: %4.2f грн' % (float(self.d['payment'].amount)))


	#painter.drawText(QRect(100,100,2000,1000),Qt.AlignLeft, '----------------------------------------------')
	#painter.drawText(QRect(100,300,2000,1000),Qt.AlignLeft, u'чек №: %d' % (int(self.d['payment'].order)))
	#painter.drawText(QRect(100,500,2000,1000),Qt.AlignLeft, u'номер телефона: %s' % (str(self.d['payment'].account)))
	#painter.drawText(QRect(100,700,2000,1000),Qt.AlignLeft, u'сумма пополнения: %4.2f грн' % (float(self.d['payment'].amount)))
	#painter.drawText(QRect(100,900,2000,1000),Qt.AlignLeft, u'дата операции: %s' % (self.d['payment'].paymentDate))
	#painter.drawText(QRect(100,1100,2000,1000),Qt.AlignLeft, '----------------------------------------------')

	painter.end()

        del(painter)
        del(printer)



    def toMain(self):
	#self.disconnect(self.stimer, SIGNAL("timeout()"), self.toMain)
	#self.disconnect(self.but, SIGNAL("clicked()"), self.toMain)
	#self.stimer.stop()
	self.retTimer.stop()
        self.close()

    def closeEvent(self, event):
	self.d['cash'].stop()
	self.retTimer.stop()
	self.disconnect(self.retTimer, SIGNAL("timeout()"), self.toMain)
	self.disconnect(self.b_back, SIGNAL("clicked()"), self.toMain)
	#del(self.stimer)
	if 'mob' in self.d.keys(): self.d['mob'].close()
        if 'mob_num' in self.d.keys(): self.d['mob_num'].close()
	if 'mob_charge' in self.d.keys(): self.d['mob_charge'].close()
	event.accept()



##############################################################################################################
    
class _mob_charge(QWidget):
    
    def __init__(self,d):
        QWidget.__init__(self)
        self.setObjectName(_fromUtf8("Mob_pay"))
        
        self.d=d
        l=d['l']
        lang=d['lang']
        self.l=l
        self.lang=lang
        
        self.balance=d['balance']

        font5 = QFont()
        font5.setPointSize(22)
        font5.setWeight(75)
        font5.setBold(False)

	nominalsN = [1,2,5,10,20,50,100,200]
	notes = u''
	for i in nominalsN:
	    if i <= d['mob_maxNominal']//100:
		notes = notes + str(i) + ','
	notes = notes[:-1]

	coins = u'5,10,25,50 коп, 1'

        self.label5 = QLabel(self)
        self.label5.setFont(font5)
        self.label5.setObjectName(_fromUtf8("label5"))
        self.label5.setGeometry(QRect(0, 150, d['xres'], 80))
        self.label5.setText(self.l['mob_charge'][self.lang] % (notes,coins))
        self.label5.setStyleSheet("background-color: transparent; color: green;")
        self.label5.setWordWrap(True)
        self.label5.setAlignment(Qt.AlignCenter)

        self.label6 = QLabel(self)
        self.label6.setFont(font5)
        self.label6.setObjectName(_fromUtf8("label6"))
        self.label6.setGeometry(QRect(0, 230, d['xres'], 40))
        self.label6.setText(self.l['mob_nochange'][self.lang])
        self.label6.setStyleSheet("background-color: transparent; color: red;")
        self.label6.setWordWrap(True)
        self.label6.setAlignment(Qt.AlignCenter)


        font = QFont()
        font.setPointSize(22)
        font.setWeight(75)
        font.setBold(False)

        #self.label = QLabel(self)
        #self.label.setFont(font)
        #self.label.setObjectName(_fromUtf8("label"))
        #self.label.setGeometry(QRect((d['xres']-600)//2, 160, 600, 50))
        #self.label.setText(l['mob_charge_charge'][lang])
        #self.label.setAlignment(Qt.AlignCenter)

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
        self.b_main.setText(l['back'][lang])
        self.b_main.setFocusPolicy(Qt.NoFocus)

        self.b_pay=QPushButton(self.l['pay'][self.lang], self)
        self.b_pay.setObjectName("b_pay")
        self.b_pay.setGeometry(QRect((d['xres']-370), d['yres']-180, 300, 95))
        self.b_pay.setFont(font)
        self.b_pay.setFocusPolicy(Qt.NoFocus)

        #self.l_sumUAH=QLabel("0", self)
        #self.l_sumUAH.setGeometry(QRect(((d['xres'])//2), 300, 160, 100))
        #self.l_sumUAH.setFont(QFont("Helvetica", 72, 75))
        #self.l_sumUAH.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        #self.l_sumUAH.setWordWrap(False)
        
        #self.l_sumKOP=QLabel(".00", self)
        #self.l_sumKOP.setGeometry(QRect((d['xres'])//2+160, 300, 210, 100))
        #self.l_sumKOP.setFont(QFont("Helvetica", 60, 50))
        #self.l_sumKOP.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        #self.l_sumKOP.setWordWrap(False)

        #font.setPointSize(25)
        #font.setWeight(50)
        #font.setBold(False)

        operFont = QFont()
        operFont.setPointSize(12)
        operFont.setWeight(75)
        operFont.setBold(False)

	group = Mob.services[Mob.availableServices[int(d['serviceKey'])]]
        for oper in group:
	    if oper[Mob.SERVICE_ID] == int(d['service']):
		operator = oper
	label = Mob.mainLabel(operator[Mob.SERVICE_NAME],self)
	#label.setStyleSheet('background: qlineargradient(x1:0, x2:0, y1:1, y2:1, stop:0 white, stop:0.5 gray, stop:1 green); background-image: url("./payments/logo-'+operator[SERVICE]+'.gif"); background-color: transparent; background-position: top center; background-repeat: no-repeat; background-origin: content; border: 1px solid #777777; border-radius: 10px; color: #777777;')
	if operator[Mob.SERVICE]:
	    logo = 'image: url("./payments/logo-'+operator[Mob.SERVICE]+'.gif"); '
	else:
	    logo =''
	label.setStyleSheet('background: qlineargradient(x1:0, y1:0.7, x2:0, y2:1.1, stop:0 white, stop:0.3 rgba(50,50,50,30));'+logo+'image-position: top center; padding-top: 10px; border: 1px solid #777777; border-radius: 7px; color: #555555;')
	label.setGeometry(QRect(50,d['yres']-220,150,150))
	label.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
	label.setWordWrap(True)
	label.setFont(operFont)
	label.setObjectName(str(operator[Mob.SERVICE_ID]))
	label.setVisible(True)

	self.percent=float(operator[Mob.PERCENT])
	self.taxmin=float(operator[Mob.MIN])
	self.summin=float(operator[Mob.SUM_MIN])
	self.summax=float(operator[Mob.SUM_MAX]) 
	if float(d['mob_summax']) < self.summax:
	    self.summax = float(d['mob_summax'])
        text = self.l['payment_tax'][self.lang] % (self.percent,self.taxmin,self.summin,self.summax)
        self.pad1 = QLabel(text,self)
        self.pad1.setObjectName(_fromUtf8("pad1"))
        self.pad1.setGeometry(QRect(50, 320, 450, 400))
        self.pad1.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.pad1.setFont(QFont("Helvetica", 22, 25))
        self.pad1.show()

        self.l_num=QLabel("number", self)
        self.setObjectName("l_num")
        self.l_num.setGeometry(QRect(210, d['yres']-160, 300, 95))
        self.l_num.setFont(font)
        self.l_num.setText("%s: \n+38(%s)%s" % (self.l['mob_your_num'][self.lang],  str(self.d['account'][0:3]), str(self.d['account'][3:]) ))
        self.l_num.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.l_verify = QLabel(self.l['verify_number'][self.lang],self)
        self.l_verify.setStyleSheet("background-color: transparent; border: none; color: red;")
        self.l_verify.setObjectName(_fromUtf8("l_verify"))
        self.l_verify.setGeometry(QRect(50, d['yres']-60, 700, 50))
        self.l_verify.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.l_verify.setFont(QFont("Helvetica", 18, 25))
        self.l_verify.show()

        self.pad = QWidget(self)
        self.pad.setObjectName(_fromUtf8("pad"))
        self.pad.setGeometry(QRect(550, 320, 650, 400))
        self.pad.show()

	stylesheet="background-color: transparent; border-width: 0px; border: none; color: #333333;"

	self.l_sum_pre=QLabel("0.00", self)
	self.l_sum_pre.setStyleSheet(stylesheet)
        self.l_sum_pre.setGeometry(QRect(300, 350, d['xres']//2-50, 100))
        self.l_sum_pre.setFont(QFont("Helvetica", 38, 25))
        self.l_sum_pre.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.l_sum_pre.setWordWrap(False)

        self.l_sumIN_pre=QLabel("0.00", self)
        self.l_sumIN_pre.setStyleSheet(stylesheet)
        self.l_sumIN_pre.setGeometry(QRect(300, 450, d['xres']//2-50, 100))
        self.l_sumIN_pre.setFont(QFont("Helvetica", 30, 18))
        self.l_sumIN_pre.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.l_sumIN_pre.setWordWrap(False)

        self.l_sumTAX_pre=QLabel("0.00", self)
        self.l_sumTAX_pre.setStyleSheet(stylesheet)
        self.l_sumTAX_pre.setGeometry(QRect(300, 550, d['xres']//2-50, 100))
        self.l_sumTAX_pre.setFont(QFont("Helvetica", 30, 18))
        self.l_sumTAX_pre.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.l_sumTAX_pre.setWordWrap(False)

        self.l_sum=QLabel("0.00", self)
        self.l_sum.setStyleSheet(stylesheet)
        self.l_sum.setGeometry(QRect(d['xres']//2+250, 355, 180, 100))
        self.l_sum.setFont(QFont("Helvetica", 42, 75))
        self.l_sum.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.l_sum.setWordWrap(False)

        self.l_sumIN=QLabel("0.00", self)
        self.l_sumIN.setStyleSheet(stylesheet)
        self.l_sumIN.setGeometry(QRect(d['xres']//2+250, 450, 180, 100))
        self.l_sumIN.setFont(QFont("Helvetica", 32, 25))
        self.l_sumIN.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.l_sumIN.setWordWrap(False)

        self.l_sumTAX=QLabel("0.00", self)
        self.l_sumTAX.setStyleSheet(stylesheet)
        self.l_sumTAX.setGeometry(QRect(d['xres']//2+250, 550, 180, 100))
        self.l_sumTAX.setFont(QFont("Helvetica", 32, 25))
        self.l_sumTAX.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.l_sumTAX.setWordWrap(False)
    
        self.l_sum_currency=QLabel("0.00", self)
        self.l_sum_currency.setStyleSheet(stylesheet)
        self.l_sum_currency.setGeometry(QRect(d['xres']//2+450, 350, 80, 100))
        self.l_sum_currency.setFont(QFont("Helvetica", 32, 15))
        self.l_sum_currency.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.l_sum_currency.setWordWrap(False)

        self.l_sumIN_currency=QLabel("0.00", self)
        self.l_sumIN_currency.setStyleSheet(stylesheet)
        self.l_sumIN_currency.setGeometry(QRect(d['xres']//2+450, 450, 80, 100))
        self.l_sumIN_currency.setFont(QFont("Helvetica", 26, 15))
        self.l_sumIN_currency.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.l_sumIN_currency.setWordWrap(False)

        self.l_sumTAX_currency=QLabel("0.00", self)
        self.l_sumTAX_currency.setStyleSheet(stylesheet)
        self.l_sumTAX_currency.setGeometry(QRect(d['xres']//2+450, 550, 80, 100))
        self.l_sumTAX_currency.setFont(QFont("Helvetica", 26, 15))
        self.l_sumTAX_currency.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.l_sumTAX_currency.setWordWrap(False)	
        
        self.stimer = QTimer()
        self.stimer.setInterval(self.d['timeout']*1000)
        self.connect(self.stimer, SIGNAL("timeout()"), self.time)

        self.connect(self.b_pay,  SIGNAL("clicked()"),  self.pay)
        self.connect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
        self.connect(self.b_main,  SIGNAL("clicked()"),  self.back)
        self.connect(self.d['cash'], SIGNAL("balanceAdded(int)"), self.put)
        self.connect(self.d['cash'], SIGNAL("billStateChanged(QString)"), self.bstate)
        self.connect(self.d['cash'], SIGNAL("coinStateChanged(QString)"), self.cstate)

        if 'action' in d.keys():
	    d['action'].finish()
        d['action']=db.action(termId=int(d['device']),balance=float(d['balance']/100),typeId='payment')

        self.put(0)


    def update(self):
	self.stimer.start()
	self.tax = self.balance * (self.percent/100)
	if self.tax < self.taxmin*100:
	    self.tax = self.taxmin*100
        self.charge = self.balance - self.tax
        if self.charge<0: self.charge=0
        self.d['payment'].tax = self.tax/100
        uah=(self.charge//100)
        kop1=(self.charge-uah*100)//10
        kop2=(self.charge-uah*100)-kop1*10
        #self.l_sumUAH.setText("%1d" % (uah))
        #self.l_sumKOP.setText(".%1d%1d %s" % (kop1, kop2, self.l['uah'][self.lang]))
        self.l_sum_pre.setText("%s:" % self.l['charge'][self.lang])
        self.l_sumIN_pre.setText("%s:" %self.l['vneseno'][self.lang])
        self.l_sumTAX_pre.setText("%s:" %self.l['tax'][self.lang])

        self.l_sum.setText("%4.2f" % (self.charge/100))
        self.l_sumIN.setText("%4.2f" % (self.balance/100))
        self.l_sumTAX.setText("%4.2f" % (self.tax/100))

        self.l_sum_currency.setText(self.l['uah'][self.lang])
        self.l_sumIN_currency.setText(self.l['uah'][self.lang])
        self.l_sumTAX_currency.setText(self.l['uah'][self.lang])
        if self.charge>=self.summin:
            self.b_pay.setEnabled(True)
            self.b_main.setVisible(False)
        else: 
            self.b_pay.setEnabled(False)
            self.b_main.setVisible(True)
            
    
        
    def time(self):
        self.stimer.stop()
        if self.b_pay.isEnabled(): 
	    self.pay()
	elif self.balance == 0:
	    self.toMain()
	elif self.charge == 0:
	    self.d['payoutEnabled'] = True
	    self.toMain()
	    

    def pay(self):
        self.d['cash'].stop()
        self.stimer.stop()
        self.disconnect(self.stimer, SIGNAL("timeout()"), self.time)
        self.d['amount']=str("%.2f" % (self.charge/100))
        self.d['log'].log("PAYMENT: CHARGE: PAY clicked. summ: %s, account: %s, service: %s" % (self.d['amount'],self.d['account'],self.d['service']))
        self.d['mob_pay']=_mob_pay(self.d)
        self.d['mob_pay'].showFullScreen()
        if 'mob' in self.d.keys(): self.d['mob'].close(); del self.d['mob']
        if 'mob_num' in self.d.keys(): self.d['mob_num'].close(); del self.d['mob_num']
        if 'mob_charge' in self.d.keys(): self.d['mob_charge'].close(); del self.d['mob_charge']
            

    def back(self):
	self.d['mob_num'].b_pay.setEnabled(True)
	self.d['mob_num'].b_pay.show()
        self.close()


    def helpbox(self):
        self.stimer.stop()
        hb=helpBox('payment', self.d)
        self.d['log'].log("PAYMENT: CHARGE: help clicked")
        hb.exec_()


    def put(self, n):
        self.balance+=n
        self.update()
        print "INCOMING: %5.2f" % (n/100)
        if self.balance>=self.summax:
	    self.d['cash'].stop()
	else:
	    self.d['cash'].get(self.d['mob_maxNominal'])


    def bstate(self):
	pass


    def cstate(self):
	pass


    def closeEvent(self, event):
	self.d['cash'].stop()
	self.disconnect(self.stimer, SIGNAL("timeout()"), self.time)
        self.disconnect(self.b_pay,  SIGNAL("clicked()"),  self.pay)
        self.disconnect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
        self.disconnect(self.b_main,  SIGNAL("clicked()"),  self.back)
        self.disconnect(self.d['cash'], SIGNAL("balanceAdded(int)"), self.put)
        self.disconnect(self.d['cash'], SIGNAL("billStateChanged(QString)"), self.bstate)
        self.disconnect(self.d['cash'], SIGNAL("coinStateChanged(QString)"), self.cstate)
        self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.powerFailure)
	event.accept()


    def enterEvent(self, event):
    	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.powerFailure)
	self.update()
	event.accept()


    def toMain(self):
	self.stimer.stop()    
	for window in ['mob','mob_num','mob_charge']:
	    if window in self.d.keys(): 
	        try:
		    if self.d[window] != None:
			self.d[window].close() 
			del self.d[window]
		except:
		    pass
	self.deleteLater()
	self.close()

    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.powerFailure)
	event.accept

    def powerFailure(self):
	self.d['cash'].stop()
	if self.d['balance'] < 1000 and self.d['coinSumm'] >= self.d['balance']:
	    self.toMain()
	elif self.d['payment_type'] in ['online'] and self.d['payment_ok'] and self.b_pay.isEnabled():
	    self.pay()
	    
