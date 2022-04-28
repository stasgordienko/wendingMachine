# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from os import *
import sys
from Xerox_error import _xerox_error
from dialogs import *
from Xerox_finish import _xerox_finish

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class _xerox_scan(QDialog):
    def __init__(self,d):
	QDialog.__init__(self)
	self.d=d
	self.l=d['l']
	self.lang=d['lang']
	self.state=-1

        font = QFont()
        font.setPointSize(22)
        font.setWeight(75)
        font.setBold(False)

        self.top = QWidget(self)
        self.top.setAutoFillBackground(True)
        self.top.setObjectName(_fromUtf8("top"))
        self.top.setGeometry(QRect(0, 0, d['xres']+1, 120))
        self.top.show()

        self.b_help = QPushButton(self.top)
        self.b_help.setFont(font)
        self.b_help.setObjectName(_fromUtf8("b_help"))
        self.b_help.setGeometry(QRect((d['xres']-250), 15, 220, 90))
        self.b_help.setText(self.l['help'][self.lang])
        self.b_help.setFocusPolicy(Qt.NoFocus)

        self.b_main = QPushButton(self.top)
        self.b_main.setFont(font)
        self.b_main.setObjectName(_fromUtf8("b_main"))
        self.b_main.setGeometry(QRect(30, 15, 400, 90))
        self.b_main.setText(self.l['back'][self.lang])
        self.b_main.setFocusPolicy(Qt.NoFocus)

	self.b_scan=QPushButton(self.l['copy'][self.lang],self)
	self.b_scan.setObjectName("b_scan")
	self.b_scan.setFont(font)
	self.b_scan.setGeometry(QRect((d['xres']-300)//2, d['yres']-200, 300, 95))
	self.b_scan.show()
	self.b_scan.setEnabled(False)

	self.background2 = QLabel(self)
        self.background2.setStyleSheet('background-color: transparent; background-image: url("img/transp87black-noise.png");')
        self.background2.setGeometry(QRect(0,0,1280,1024))
        self.background2.hide()

        self.label = QLabel(self)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label1"))
        self.label.setText(self.l['xerox_scan_label'][self.lang])
        self.stylesheet1='background:transparent; border-width: 0px; border: none; color: #333333;'
        self.stylesheet2='background-image: url("img/scan/finish_scan.png"); background-position: center; background-origin: content; background-color: transparent; border-width: 0px; border: none; color: white;'
        self.stylesheet3='background-image: url("img/xerox/rotate_xerox.png"); background-position: center; background-origin: content; background-color: transparent; border-width: 0px; border: none; color: white;'
	self.label.setStyleSheet(self.stylesheet1)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,800,450))
	self.label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

	self.progress=QProgressBar(self)
	self.progress.setGeometry(QRect(300,600, d['xres']-600, 50))
	self.progress.setValue(0)
	self.progress.hide()

	self.b_next=QPushButton(self.l['continue'][self.lang],self)
	self.b_next.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_next.setObjectName("b_next1")
	self.b_next.setFont(font)
	self.b_next.setGeometry(QRect((d['xres']-600)//2, 600, 600, 50))
	self.b_next.setFocusPolicy(Qt.NoFocus)
	self.b_next.setVisible(False)

	self.side2Timer = QTimer()
	self.connect(self.side2Timer, SIGNAL("timeout()"), self.side2Click)
	self.side2ClickCounter = 60
	
	self.timer=QTimer()
	self.p=0
	self.w=0
	self.page=0
	self.scanTime=4000 #время сканирования, мсек
	self.printTime=4000 #время печати 1 страницы, мсек
	#self.tprint=self.printTime//
	self.connect(self.b_next, SIGNAL("clicked()"), self.side2)
	self.connect(self.b_scan, SIGNAL("clicked()"), self.go)
	self.connect(self.b_main, SIGNAL("clicked()"), self.back)
	self.connect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
	self.connect(self.d['copier'], SIGNAL("stateChanged(QString)"), self.changeState)
	self.success=False

        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

	self.changeState(self.d['copier'].state)
	self.waitReady()
	

    def go(self):
        self.b_scan.hide()
        self.b_main.hide()
        self.top.hide()
        #self.label.setStyleSheet(self.stylesheet2)
        self.label.setText("")
	self.state=0
	self.page=0
        if self.d['copier'].start()==1:
	    #self.d['action'].scan+=1
	    self.background2.show()
	    #self.progress.show()
	    #self.timeScan()
	    #self.changeState(self.d['copier'].state)
	else:
            self.b_scan.show()
            self.top.show()
	    self.label.setText(self.l['error_occured'][self.lang])
	    self.label.setStyleSheet(self.stylesheet1)

	#self.changeState('ready')
	#self.changeState('scanningFirst')


    def waitReady(self):
        if self.d['copier'].state!='ready':
	    if self.d['copier'].state=='sleeping':
		self.d['copier'].wakeUp()
	        #sleep(3)
	    self.timer.singleShot(500, self.waitReady)
	    if self.d['copier'].state=='warming': return
	    self.w+=1
	    if self.w==20:
		print "something wrong with copier...."
	    elif self.w==30:
		print "ERROR. Copier state is not ready.... State is:", self.d['copier'].state
		self.timer.stop()
		self.d['copier'].set('clearall','')
		self.d['action'].isError=True
		self.d['action'].finish(status='start error')
		self.close()
		del(self)
	else:
	    self.b_scan.setEnabled(True)
	    self.b_scan.setVisible(True)
	

    def timeScan(self):
        if self.p<100:
	    self.timer.singleShot(self.scanTime//10, self.timeScan)
	    self.p+=10
	    self.progress.setValue(self.p)
	else:
	    self.timer.stop()
	    self.progress.hide()
	    self.label.setText("")
	    self.label.setStyleSheet(self.stylesheet1)
	    if self.d['copier'].sided=='1':
		self.changeState('printing')

    def side2(self):
	self.side2Timer.stop()
	self.d['copier'].say('yes')
	self.progress.show()
	self.b_next.hide()
	self.state=1
	self.changeState('scanning')

    def side2Click(self):	# при ожидании нажатия ПРОДОЖИТЬ от пользователя при перевороте страницы 
	if self.side2ClickCounter > 0:
	    if (self.side2ClickCounter / 5) - (self.side2ClickCounter // 5) == 0:
		self.d['copier'].click('right')
		#self.d['copier'].click('left')
	    self.side2ClickCounter -= 1
	    self.b_next.setText(self.l['continue'][self.lang]+' ('+str(self.side2ClickCounter)+')')
	else:
	    #self.side2()	
	    self.d['copier'].say('no')		# Если пользователь не ответил в течении 1 минуты - сканируем только 1-ю сторону и распечатываем документ
	    self.progress.hide()
	    self.b_next.hide()
	    self.state=2
	    self.label.setText(self.l['printing'][self.lang])
	    self.label.setStyleSheet(self.stylesheet2)
	    self.changeState('printing')

    def back(self):
	self.d['xerox'].put(0)
        self.close()
        del(self)

    def helpbox(self):
        #self.ptimer.stop()
        hb=helpBox('xerox', self.d)
        hb.exec_()
        #self.ptimer.start()

	
    def changeState(self,state):
	#state=self.d['copier'].state
	print "CALLING changeState with param(state) %s. Copier state is %s" % (state,self.d['copier'].state)
	
	if self.state==0 and state=='printing':
	    self.label.setText(self.l['printing'][self.lang])
	    self.label.setStyleSheet(self.stylesheet2)
	    self.page=1
	    self.state=3
	    #if self.d['copier'].state=='copying': self.success=True

	elif self.d['sided']=='1' and state=='askScanSide2':
	    self.d['copier'].say('no')
	    
	elif state=='askScanSide2':
	    self.label.setText('')#(u" Переверните документ на 180 градусов и нажмите ПРОДОЛЖИТЬ")
	    self.label.setStyleSheet(self.stylesheet3)
	    self.progress.hide()
	    self.b_next.show()
	    self.state=1
	    self.side2Timer.start(1000)

	elif (self.state==0 and state=='copying'):
	    self.side2Timer.stop()
	    self.label.setText(self.l['scanning'][self.lang])
	    self.label.setStyleSheet(self.stylesheet2)
	    self.d['action'].scan+=1
	    self.p=0
	    self.progress.setValue(self.p)
            self.progress.show()
	    #self.state=1
	    self.timeScan()

	elif (self.state==0 and state=='scanning'):
	    self.side2Timer.stop()
	    self.label.setText(self.l['scanning1side'][self.lang])
	    self.label.setStyleSheet(self.stylesheet2)
	    self.d['action'].scan+=1
	    self.p=0
	    self.progress.setValue(self.p)
            self.progress.show()
	    #self.state=0
	    self.timeScan()

	elif self.state==1 and state=='scanning':
	    self.side2Timer.stop()
	    self.label.setText(self.l['scanning2side'][self.lang])
	    self.label.setStyleSheet(self.stylesheet2)
	    self.d['action'].scan+=1
	    self.p=0
	    self.progress.setValue(self.p)
            self.progress.show()
	    self.b_next.hide()
	    self.state=2
	    self.timeScan()


	elif state=='askScanAnother':
	    self.side2Timer.stop()
	    self.label.setText(self.l['printing'][self.lang])
	    self.label.setStyleSheet(self.stylesheet2)
	    self.p=0
	    self.progress.setValue(self.p)
            self.progress.hide()			#скрыть прогресс во время печати
	    self.state=3
	    self.d['copier'].say('no')

	elif self.state>1 and (state=='copying' or state=='printing'):
	    self.side2Timer.stop()
	    a=self.d['copier'].c1
	    b=self.d['copier'].c2
	    
	    if a=='': 
		a=0
	    else: 
		a=int(a)
	    
	    if b=='': 
		b=0
	    else: 
		b=int(b)
	    
	    if self.d['ncopies']==1:
		self.success=True
	    if b>0 and a>0:
		self.label.setText(self.l['printing_pages'][self.lang] % (a, b))
		self.label.setStyleSheet(self.stylesheet2)
		self.progress.setValue((a*100)//b)
		self.progress.setVisible(True)
		print "success print pages: %d" % (a-1)
		self.page=a-1
		if self.d['ncopies']==a:
		    self.success=True

	elif self.state>0 and (state=='error' or state=='paper' or state=='jam'):
	    self.side2Timer.stop()
	    #error
	    print '!!!!!!!!!!copying error!!!!!!!!!!'
	    print 'successfully print %d from %d pages' % (self.page,self.d['ncopies'])
	    self.state=-1
	    #SEND SMS

	    self.d['printed_pages']=self.page
	    summ=int(self.d['cost']*self.page)
	    self.d['balance'] -= summ
	    self.d['action'].usedsumm += summ/100
	    self.d['action'].paper+=self.page
	    self.d['payoutEnabled']=True
	    print "balance is: %d" % self.d['balance']

	    if self.d['sided']=='2': self.d['n_xerox_dside']+=self.page
	    elif self.d['sided']=='1': self.d['n_xerox_oside']+=self.page
	    self.d['n_paper']+=self.page
	    drum=self.page*int(self.d['sided'])
	    self.d['n_drum']+=drum
	    self.d['action'].drum+=drum
	    self.d['n_scan']+=int(self.d['sided'])

	    self.d['action'].isError=True
	    self.d['action'].status='print error'
	    self.disconnect(self.d['copier'], SIGNAL("stateChanged(QString)"), self.changeState)
	    self.disconnect(self.b_next, SIGNAL("clicked()"), self.side2)
	    self.disconnect(self.b_scan, SIGNAL("clicked()"), self.go)
	    self.d['xerox_error']=_xerox_error(self.d)	    

	    self.close()
	    self.deleteLater()


	elif self.state>0 and state=='ready':
	    #done
	    if True: #self.success==True:
		print "!!!!!!!!!!!OKKKKK!!!!!!!!!!"
		self.page=self.d['ncopies']
		summ=int(self.d['cost']*self.page)
		self.d['balance'] -= summ
		self.d['action'].usedsumm += summ/100
		self.d['payoutEnabled']=True
		print "balance is: %d" % self.d['balance']

		if self.d['sided']=='2': self.d['n_xerox_dside']+=self.page
		elif self.d['sided']=='1': self.d['n_xerox_oside']+=self.page
		self.d['n_paper']+=self.page
		self.d['action'].paper+=self.page
		drum=self.page*int(self.d['sided'])
		self.d['n_drum']+=drum
		self.d['action'].drum+=drum
		self.d['n_scan']+=int(self.d['sided'])

		#PAGE FINISH !!!!!!!!!!!!!!!!!!!
		self.d['action'].status='success'
		self.background2.hide()
		self.label.hide()
		self.progress.hide()
		self.label.setStyleSheet(self.stylesheet1)
		self.repaint()
		self.d['xerox_finish']=_xerox_finish(self.d)
		self.disconnect(self.d['copier'], SIGNAL("stateChanged(QString)"), self.changeState)
		self.disconnect(self.b_next, SIGNAL("clicked()"), self.side2)
		self.disconnect(self.b_scan, SIGNAL("clicked()"), self.go)
		#self.close()
		self.deleteLater()
	    else:
		print "something wrong...."

	elif self.state == 0 and state == 'warming':
	    self.background2.show()
	    self.label.setText(self.l['warming'][self.lang])
	    self.label.setStyleSheet(self.stylesheet2)
	    self.repaint()
	    
	elif self.state == -1 and state == 'ready':
	    self.background2.hide()
	    self.label.setText(self.l['xerox_scan_label'][self.lang])
	    self.label.setStyleSheet(self.stylesheet1)
	    self.repaint()
	
    def enterEvent(self,event):
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.powerFailure)
	event.accept()

    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.powerFailure)
	event.accept()

    def powerFailure(self):
	if self.state in [-1,0,1,2]:
	    self.close()
	    self.d['xerox'].close()