# -*- coding: utf-8 -*-
from __future__ import division

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from config import _passwordCheck
from Mob import _mob
from Print_ins import _print_ins
from Scan import _scan_select
from Xerox_charge import _xerox_charge
from catalog import _catalog
from datetime import datetime
import subprocess

from spins import intSpinBox
from dialogs import *

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class MainMenu(QWidget):

    d={}
    l={}
    lang='ru'

    def __init__(self,dg):
        super(MainMenu, self).__init__()

        global l
        global d
        global lang
        d=dg
        l=d['l']
        lang=d['lang']

        self.changeTimer = QTimer()
        self.setupUi(self)        
        
        self.connect(self.b_ru, SIGNAL("clicked()"), self.ruClick)
        self.connect(self.b_ua, SIGNAL("clicked()"), self.uaClick)
        self.connect(self.b_en, SIGNAL("clicked()"), self.enClick)

        self.connect(self.mob, SIGNAL("linkActivated(QString)"), self.oper)
        self.connect(self.printer, SIGNAL("linkActivated(QString)"), self.oper)
        self.connect(self.scan, SIGNAL("linkActivated(QString)"), self.oper)
        self.connect(self.xerox, SIGNAL("linkActivated(QString)"), self.oper)
        self.connect(self.catalog, SIGNAL("linkActivated(QString)"), self.oper)

        self.connect(self.b_help, SIGNAL("clicked()"), self.helpbox)
        self.connect(self.b_email, SIGNAL("clicked()"), self.dialog_email)
        self.connect(self.b_bal, SIGNAL("clicked()"), self.changeClick)
        self.connect(self.b_price, SIGNAL("clicked()"), self.priceClick)
        
        self.connect(self.b_conf, SIGNAL("clicked(str)"), self.conf)
        self.connect(self.b_conf1, SIGNAL("clicked(str)"), self.conf)
        self.connect(self.b_conf2, SIGNAL("clicked(str)"), self.conf)

        if lang=='ru':
            self.ruClick()
        elif lang=='ua':
            self.uaClick()
        else: self.enClick()
        
        self.b_ru.setText("RU")
        self.b_ua.setText("UA")
        self.b_en.setText("EN")

	self.configTimer = QTimer()
	self.configTimer.setInterval(1000)
	self.connect(self.configTimer, SIGNAL("timeout()"), self.configTimeout)
	self.configSequence = []
	
	self.STimer = QTimer()
	self.STimer.setInterval(1000)
	self.connect(self.STimer, SIGNAL("timeout()"), self.checkServices)
	self.STimer.start()
	
	self.connect(self.changeTimer, SIGNAL("timeout()"), self.changeEat)
	
	self.haltRun = False
	#Для возможности скриншота по нажатию"windows key"
	d['app'].installEventFilter(self)	# MONITORED_OBJ.installEventFilter(FILTERED_OBJ)
	


    def screenshot(self,d):
        filename = './'+datetime.now().strftime("%Y%m%d_%H%M%S")+'.jpg'
        pixmap = QPixmap.grabWindow(d['app'].desktop().winId())
        pixmap.save(filename)


    def conf(self,button):
	global d
	self.configSequence.append(button)
	print self.configSequence
	if self.configSequence == ['1','2','2','3']:
	    d['pwdcheck'] = _passwordCheck(d)
	    d['pwdcheck'].exec_()
	else:
	    self.configTimer.start()
	    
	
    def configTimeout(self):
	self.configSequence = []
	self.configTimer.stop()

	
    def helpbox(self):
        #from Scan_finish import _scan_finish
	#d['scanFileName'] = '/123.jpg'
	#x1 = _scan_finish(d)
	#x1.exec_()
        hb = helpBox('main', d)
        hb.exec_()

    def priceClick(self):
        #self.pwindow = prices(d)
        #pwindow.exec_()
        hb = helpBox('price', d)
        hb.exec_()


    def dialog_email(self):
	if support(d).exec_():
	    print "send email"
	else:
	    print "cancel send"

        
    def checkServices(self):
	global d
	if d['xerox_enabled']=='yes' and d['xerox_ok']: 
	    if self.xerox.isEnabled() == False:
		self.xerox.setEnabled(True)
		self.xeffect.setEnabled(False)
	else: 
	    if self.xerox.isEnabled() == True:
		self.xerox.setEnabled(False)
		self.xeffect.setEnabled(True)
	    	
	if d['printer_enabled']=='yes' and d['printer_ok'] and (('converter' in d.keys()) and (d['converter'] != None)): 
	    if self.printer.isEnabled() == False:
		self.printer.setEnabled(True)
		self.peffect.setEnabled(False)
	else: 
	    if self.printer.isEnabled() == True:
		self.printer.setEnabled(False)
		self.peffect.setEnabled(True)
	
	if d['catalog_enabled']=='yes' and d['catalog_ok']: 
	    if self.catalog.isEnabled() == False:
		self.catalog.setEnabled(True); 
		self.ceffect.setEnabled(False)
	else: 
	    if self.catalog.isEnabled() == True:
		self.catalog.setEnabled(False); 
		self.ceffect.setEnabled(True)
	
	if d['scan_enabled']=='yes' and d['scan_ok']:  
	    if self.scan.isEnabled() == False:
		self.scan.setEnabled(True); 
		self.seffect.setEnabled(False)
	else: 
	    if self.scan.isEnabled() == True:
		self.scan.setEnabled(False); 
		self.seffect.setEnabled(True)
	    
	if d['payment_enabled']=='yes' and d['payment_ok']: 
	    if self.mob.isEnabled() == False:
		self.mob.setEnabled(True); 
		self.meffect.setEnabled(False)
        else: 
	    if self.mob.isEnabled() == True:
		self.mob.setEnabled(False); 
		self.meffect.setEnabled(True)

	if d['DOP_enabled']=='yes' and d['DOP_ok']: 
	    if self.DOP.isEnabled() == False:
		self.DOP.setEnabled(True); 
		self.deffect.setEnabled(False)
        else: 
	    if self.DOP.isEnabled() == True:
		self.DOP.setEnabled(False); 
		self.deffect.setEnabled(True)


    def oper(self,op):
	global d
	self.changeTimer.stop()
        if op=='mob' : d['mob'] = _mob(d); d['mob'].showFullScreen()
        elif op=='printer' : d['printer'] = _print_ins(d); d['printer'].showFullScreen()
        elif op=='xerox' : d['xerox'] = _xerox_charge(d); d['xerox'].showFullScreen()
        elif op=='scan' : d['scan'] = _scan_select(d); d['scan'].showFullScreen()
        elif op=='catalog' : d['cat'] = _catalog(d); d['cat'].showFullScreen()


    def ruClick(self):
	global lang
        lang='ru'
        self.b_ru.setChecked(True)
        self.b_ua.setChecked(False)
        self.b_en.setChecked(False)
        self.update()

    def uaClick(self):
        global lang
        lang='ua'
        self.b_ru.setChecked(False)
        self.b_ua.setChecked(True)
        self.b_en.setChecked(False)
        self.update()

    def enClick(self):
        global lang
        lang='en'
        self.b_ru.setChecked(False)
        self.b_ua.setChecked(False)
        self.b_en.setChecked(True)
        self.update()
    
    def changeClick(self):
	self.changeTimer.stop()
	if d['coinSumm'] > d['balance']: 
	    d['cash'].payBack(d['balance'])
	    self.b_bal.setEnabled(False)

    def enterEvent(self,e):
	self.connect(d['ping'], SIGNAL("powerFailure()"), self.powerFailure)
	self.update()
	d['saveData']()
	print "enter MainMenu"
	if d['powerFailure'] and not self.haltRun:
	    self.powerFailure()
	e.accept()

    def leaveEvent(self,event):
	self.disconnect(d['ping'], SIGNAL("powerFailure()"), self.powerFailure)
	print "leave MainMenu"
	self.changeTimer.stop()
	event.accept()

    def changeEat(self):
	global d
	print "zero"
	d['log'].log("USER INACTIVITY ABOUT 2 min.. BALANCE WAS %4.2f uah." % (int(d['balance'])/100))
    	self.changeTimer.stop()
	d['balance'] = 0
	d['payoutEnabled'] = False
	self.update()

    def update(self):
	global d
	#if int(d['balance']) > 0 : self.changeTimer.start(120000)
        d['lang']=lang
        self.b_help.setText(l['help'][lang])
        self.b_email.setText(l['emailsupport'][lang])
        #self.bal.setText("%s: %4.2f%s" % (l['balance'][lang],d['balance']/100,l['uah'][lang]))
        self.bal.setText("%4.2f" % (d['balance']/100))
        self.l_bal.setText(l['balance'][lang])
        self.l_uah.setText(l['uah'][lang])
        self.b_bal.setText(l['change'][lang])
        self.b_price.setText(l['price'][lang])
        self.label.setText("<html><center><h1>%s</h1></center></html>" % l['main_select'][lang])
        self.printer.setText("<html><center><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><h2> %s </h2></center></html>" % l['main_print'][lang])
        self.scan.setText("<html><center><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><h2> %s </h2></center></html>" % l['main_scan'][lang])
        self.xerox.setText(u"<html><center><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><h2> %s </h2></center></html>" % l['main_xerox'][lang])
        self.mob.setText("<html><center><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><h2> %s </h2></center></html>" % l['main_mob'][lang])
        self.catalog.setText("<html><center><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><h2> %s </h2></center></html>" % l['main_cat'][lang])
        self.DOP.setText("<html><center><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><h2> %s </h2></center></html>" % l['main_DOP'][lang])
	
	if d['balance']>0:
	    self.l_bal.setVisible(True)
	    self.bal.setVisible(True)
	    self.l_uah.setVisible(True)
	    self.b_price.setVisible(False)    ### hide prices button
	    if d['payoutEnabled']:
		self.b_bal.setEnabled(True)
		self.b_bal.setVisible(True)
	else:
	    self.l_bal.setVisible(False)
	    self.bal.setVisible(False)
	    self.l_uah.setVisible(False)
	    self.b_bal.setEnabled(False)
	    self.b_bal.setVisible(False)
	    self.b_price.setVisible(True)    ### show prices button
	    
	#if d['payoutEnabled']: self.b_bal.setVisible(True)
	#else: self.b_bal.setVisible(False)
	
    def setupUi(self, MainMenu):
	global d
        #MainMenu.setObjectName(_fromUtf8("MainMenu"))
        MainMenu.setWindowModality(Qt.NonModal)
        MainMenu.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainMenu.sizePolicy().hasHeightForWidth())
        MainMenu.setSizePolicy(sizePolicy)
        MainMenu.setMinimumSize(QSize(1280,1024))
        MainMenu.setCursor(Qt.ArrowCursor)
        MainMenu.setContextMenuPolicy(Qt.NoContextMenu)
        MainMenu.setAutoFillBackground(False)

        self.printer = mainLabel(MainMenu)
        self.printer.setContextMenuPolicy(Qt.NoContextMenu)
        self.printer.setAlignment(Qt.AlignVCenter|Qt.AlignHCenter)
        self.printer.setObjectName(_fromUtf8("printer"))
        self.printer.setEnabled(False)
        
        self.scan = mainLabel(MainMenu)
        self.scan.setContextMenuPolicy(Qt.NoContextMenu)
        self.scan.setAlignment(Qt.AlignVCenter|Qt.AlignHCenter)
        self.scan.setObjectName(_fromUtf8("scan"))
        self.scan.setEnabled(False)

        self.xerox = mainLabel(MainMenu)
        self.xerox.setContextMenuPolicy(Qt.NoContextMenu)
        self.xerox.setAlignment(Qt.AlignVCenter|Qt.AlignHCenter)
        self.xerox.setObjectName(_fromUtf8("xerox"))
        self.xerox.setEnabled(False)

        self.mob = mainLabel(MainMenu)
        self.mob.setSizePolicy(sizePolicy)
        self.mob.setMouseTracking(True)
        self.mob.setContextMenuPolicy(Qt.NoContextMenu)
        self.mob.setLayoutDirection(Qt.LeftToRight)
        self.mob.setAutoFillBackground(False)
        self.mob.setFrameShape(QFrame.NoFrame)
        self.mob.setFrameShadow(QFrame.Plain)
        self.mob.setTextFormat(Qt.AutoText)
        self.mob.setAlignment(Qt.AlignVCenter|Qt.AlignHCenter)
        self.mob.setWordWrap(False)
        self.mob.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.mob.setObjectName(_fromUtf8("mob"))
        self.mob.setEnabled(False)
        
        self.catalog = mainLabel(MainMenu)
        self.catalog.setContextMenuPolicy(Qt.NoContextMenu)
        self.catalog.setAlignment(Qt.AlignVCenter|Qt.AlignHCenter)
        self.catalog.setObjectName(_fromUtf8("catalog"))
        self.catalog.setEnabled(False)

        self.DOP = mainLabel(MainMenu)
        self.DOP.setContextMenuPolicy(Qt.NoContextMenu)
        self.DOP.setAlignment(Qt.AlignVCenter|Qt.AlignHCenter)
        self.DOP.setObjectName(_fromUtf8("DOP"))
        self.DOP.setEnabled(False)
        self.DOP.setVisible(False)

        self.label = mainLabel(MainMenu)
        self.label.setGeometry(QRect(390, 120, 271, 41))
        self.label.setLayoutDirection(Qt.LeftToRight)
        self.label.setTextFormat(Qt.AutoText)
        self.label.setObjectName(_fromUtf8("label"))
        
        self.top = QWidget(MainMenu)
        self.top.setGeometry(QRect(0, 0, 1024, 120))
        self.top.setAutoFillBackground(True)
        self.top.setObjectName(_fromUtf8("top"))


	self.peffect = QGraphicsColorizeEffect()
	self.peffect.setColor(QColor.fromRgb(200,200,200,200))
	self.peffect.setStrength(1)

	self.xeffect = QGraphicsColorizeEffect()
	self.xeffect.setColor(QColor.fromRgb(200,200,200,200))
	self.xeffect.setStrength(1)

	self.seffect = QGraphicsColorizeEffect()
	self.seffect.setColor(QColor.fromRgb(200,200,200,200))
	self.seffect.setStrength(1)

	self.ceffect = QGraphicsColorizeEffect()
	self.ceffect.setColor(QColor.fromRgb(200,200,200,200))
	self.ceffect.setStrength(1)

	self.meffect = QGraphicsColorizeEffect()
	self.meffect.setColor(QColor.fromRgb(200,200,200,200))
	self.meffect.setStrength(1)

	self.deffect = QGraphicsColorizeEffect()
	self.deffect.setColor(QColor.fromRgb(200,200,200,200))
	self.deffect.setStrength(1)

	self.printer.setGraphicsEffect(self.peffect)
	self.xerox.setGraphicsEffect(self.xeffect)
	self.scan.setGraphicsEffect(self.seffect)
	self.catalog.setGraphicsEffect(self.ceffect)
	self.mob.setGraphicsEffect(self.meffect)
	self.DOP.setGraphicsEffect(self.deffect)

        self.b_ru = QPushButton(self.top)
        font = QFont()
        font.setPointSize(16)
        self.b_ru.setFont(font)
        self.b_ru.setFocusPolicy(Qt.NoFocus)
        self.b_ru.setContextMenuPolicy(Qt.NoContextMenu)
        self.b_ru.setCheckable(True)
        self.b_ru.setChecked(False)
        self.b_ru.setDefault(False)
        self.b_ru.setFlat(False)
        self.b_ru.setObjectName(_fromUtf8("b_ru"))
        self.b_ua = QPushButton(self.top)
        font = QFont()
        font.setPointSize(16)
        self.b_ua.setFont(font)
        self.b_ua.setCheckable(True)
        self.b_ua.setChecked(False)
        self.b_ua.setObjectName(_fromUtf8("b_ua"))
        self.b_en = QPushButton(self.top)
        font = QFont()
        font.setPointSize(16)
        self.b_en.setFont(font)
        self.b_en.setCheckable(True)
        self.b_en.setChecked(False)
        self.b_en.setObjectName(_fromUtf8("b_en"))

        self.b_help = QPushButton(self.top)
        font = QFont()
        font.setPointSize(16)
        font.setWeight(50)
        font.setBold(False)
        self.b_help.setFont(font)
        self.b_help.setObjectName(_fromUtf8("b_help_main"))

        self.b_email = QPushButton(self.top)
        self.b_email.setFont(font)
        self.b_email.setObjectName(_fromUtf8("b_email"))
        self.b_email.setGeometry(QRect(d['xres']//2-145, 15, 200, 90))

        self.top.setGeometry(QRect(0, 0, d['xres']+1, 120))
        self.b_help.setGeometry(QRect((d['xres'])//2+65, 15, 200, 90))
        self.b_en.setGeometry(QRect(d['xres']-100, 15, 90, 90))
        self.b_ua.setGeometry(QRect(d['xres']-200, 15, 90, 90))
        self.b_ru.setGeometry(QRect(d['xres']-300, 15, 90, 90))
        self.label.setGeometry(QRect((d['xres']-300)//2, 150, 300, 80))

        w=330 #width
        h=330 #height
        b=100 #border
        self.xerox.setGeometry(QRect((d['xres'])//2-w-50, 250, w, h))
        self.printer.setGeometry(QRect((d['xres'])//2+50, 250, w, h))
        self.catalog.setGeometry(QRect(70, 650, w, h))
	self.mob.setGeometry(QRect((d['xres']-w)//2, 650, w, h))
        self.scan.setGeometry(QRect((d['xres']-w-70), 650, w, h))
        
        
        self.l_bal=QLabel("YOUR BALANCE:",self.top)
        self.l_bal.setObjectName("l_bal")
        self.l_bal.setFont(font)
        self.l_bal.setWordWrap(True)
        self.l_bal.setAlignment(Qt.AlignRight)
        self.l_bal.setGeometry(QRect(15, 30, 185, 30))

        self.bal=QLabel("125.75",self.top)
        self.bal.setObjectName("bal")
        font_balance = QFont()
        font_balance.setPointSize(24)
        font_balance.setWeight(50)
        font_balance.setBold(True)
        self.bal.setFont(font_balance)
        self.bal.setWordWrap(True)
        self.bal.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.bal.setGeometry(QRect(15, 52, 135, 45))

        self.l_uah=QLabel("uah", self.top)
        self.l_uah.setObjectName("l_uah")
        self.l_uah.setFont(font)
        self.l_uah.setWordWrap(True)
        self.l_uah.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.l_uah.setGeometry(QRect(155, 55, 40, 40))
        
        self.b_price=QPushButton(self.top)
        self.b_price.setGeometry(QRect(10, 15, 250, 90))
        self.b_price.setObjectName(_fromUtf8("b_price"))
        self.b_price.setFont(font)

        self.b_bal=QPushButton(self.top)
        self.b_bal.setGeometry(QRect(210, 15, 200, 90))
        self.b_bal.setObjectName(_fromUtf8("b_bal"))
        self.b_bal.setFont(font)

        self.b_conf=hiddenButton("1",self.top)#QPushButton("C", self.top)
        self.b_conf.setGeometry(QRect(d['xres']-375, 5, 70, 115))

        self.b_conf1=hiddenButton("2",self)#QPushButton("C", self.top)
        self.b_conf1.setGeometry(QRect(d['xres']-90, 125, 90, 95))

        self.b_conf2=hiddenButton("3",self)#QPushButton("C", self.top)
        self.b_conf2.setGeometry(QRect(1, 125, 90, 90))



        self.b_help.setFocusPolicy(Qt.NoFocus)
	self.b_ru.setFocusPolicy(Qt.NoFocus)
	self.b_ua.setFocusPolicy(Qt.NoFocus)
	self.b_en.setFocusPolicy(Qt.NoFocus)
	self.b_conf.setFocusPolicy(Qt.NoFocus)
	self.b_email.setFocusPolicy(Qt.NoFocus)
	self.b_bal.setFocusPolicy(Qt.NoFocus)
	self.b_price.setFocusPolicy(Qt.NoFocus)


        self.test = QPushButton(self)
        self.test.setObjectName("test_button")
        self.test.setGeometry(QRect(300,300,300,200))
        #self.test.setAlignment(Qt.AlignHCenter | Qt.AlignVBottom)
        self.test.setText("Button TEST")
        self.test.setAutoFillBackground(False)
        self.test.hide()

        QMetaObject.connectSlotsByName(MainMenu)


    def closeEvent(self, event):
        #self.d['cash'].stop()
        if 'action' in self.d.keys():
	    if self.d['balance'] == 0:
		if self.d['action'].usedsumm == 0:
		    del(self.d['action'])
		else:
		    self.d['action'].finish()
		    del(self.d['action'])
	    else:
		self.d['action'].finish(status='client leave the change')
		self.d['balance']=0
		self.d['payoutEnabled'] = False
        self.disconnect(self.b_ru, SIGNAL("clicked()"), self.ruClick)
        self.disconnect(self.b_ua, SIGNAL("clicked()"), self.uaClick)
        self.disconnect(self.b_en, SIGNAL("clicked()"), self.enClick)

        self.disconnect(self.mob, SIGNAL("linkActivated(QString)"), self.oper)
        self.disconnect(self.printer, SIGNAL("linkActivated(QString)"), self.oper)
        self.disconnect(self.scan, SIGNAL("linkActivated(QString)"), self.oper)
        self.disconnect(self.xerox, SIGNAL("linkActivated(QString)"), self.oper)
        self.disconnect(self.catalog, SIGNAL("linkActivated(QString)"), self.oper)

        self.disconnect(self.b_help, SIGNAL("clicked()"), self.helpbox)
        self.disconnect(self.b_email, SIGNAL("clicked()"), self.dialog_email)
        self.disconnect(self.b_bal, SIGNAL("clicked()"), self.changeClick)
        self.disconnect(self.b_price, SIGNAL("clicked()"), self.priceClick)
        
        self.disconnect(self.b_conf, SIGNAL("clicked(str)"), self.conf)
        self.disconnect(self.b_conf1, SIGNAL("clicked(str)"), self.conf)
        self.disconnect(self.b_conf2, SIGNAL("clicked(str)"), self.conf)
        event.accept()

    def eventFilter(self, obj, event):
	if event.type()==QEvent.KeyPress and event.key() == Qt.Key_Meta: #QEvent.KeyPress Windows_key:
	    self.screenshot(d)
	    print "screenShot made"
	    event.accept()
	return 0


    def powerFailure(self):
        global d
        self.toPay = 0
        self.haltRun = True
        self.disconnect(d['ping'], SIGNAL("powerFailure()"), self.powerFailure)
	#self.disconnect(self.d['cash'], SIGNAL("changeOK()"), self.changeOK)
	#self.disconnect(self.d['cash'], SIGNAL("cantGiveChange(int)"), self.cantGiveChange)
	d['cash'].stop()
	self.connect(d['cash'], SIGNAL("payoutStarted()"), self.changeMessage)
	self.connect(d['cash'], SIGNAL("payoutFinished()"), self.quickChange)
	#self.connect(d['cash'], SIGNAL("cantGiveChange(int)"), self.quickChange)
    	if (d['balance'] > 0): 
    	    if (d['coinSumm'] > d['balance']):
    		self.toPay = d['balance']
		d['cash'].payBack(d['balance'])
	    else:
		self.toPay = d['coinSumm']
		d['cash'].payBack(d['coinSumm'])
	else:
	    text = u'<br><br><br><br>СБОЙ ЭЛЕКТРОПИТАНИЯ!<br><br>ВЫКЛЮЧЕНИЕ...'
	    self.powerMessage = message(d,text,timeout=5)
	    self.powerMessage.exec_()
	    self.quickChange(0)
	    
    def quickChange(self,summ=0):
        global d
        if summ == 0:
	    #print u'Аварийный останов. Сдача выдана.'
	    d['log'].log('Power Failure. Change Paid.')
	    #if self.powerMessage != None:
		#self.powerMessage.accept()
	else:
	    #print u'Аварийный останов. Сдача НЕ выдана.'
	    d['log'].log('Power Failure. Change NOT Paid. Summ: %4.2f' % (summ/100))
	text = u'<br><br><br><br><br>СБОЙ ЭЛЕКТРОПИТАНИЯ!'
	self.powerMessage = message(d,text,timeout=7)
	self.powerMessage.exec_()
	if d['powerFailure']:
	    subprocess.call(['halt'])
	    self.close()
	else:
	    self.haltRun = False

    def changeMessage(self):
	global d
	print 'MESSAGE POWER FAIL'
	d['log'].log('Power Failure. Change NOT Paid. Summ: %4.2f' % (self.toPay/100))
	text = u'<br><br><br><br>СБОЙ ЭЛЕКТРОПИТАНИЯ. <br><br> Баланс: %4.2f. Выдача...' % (self.toPay/100)
	self.powerMessage = message(d,text,timeout=7)
	self.powerMessage.exec_()
	

class hiddenButton(QPushButton):
    def paintEvent(self,event):
	event.accept()
	pass
    def mousePressEvent(self,event):
	self.emit(SIGNAL("clicked(str)"), str(self.text()))
	#print "button %s clicked" % str(self.text())
	event.accept()


class myButton(QPushButton):
    def paintEvent(self,event):
	event.accept()

class mainLabel(QLabel):
    def mouseReleaseEvent(self,event):
	s=self.objectName()
	self.emit(SIGNAL("linkActivated(QString)"), s)
	event.accept()
	
