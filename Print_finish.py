# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from os import *
import sys
from dialogs import *

class _print_finish(QDialog):
    def __init__(self,d):
	QDialog.__init__(self)
	self.d=d
	self.l=d['l']
	self.lang=d['lang']
	
	self.setStyleSheet('* { background-color: transparent;}')
	drawBackground(self, d)

	font = QFont()
        font.setPointSize(16)
        font.setWeight(50)
        font.setBold(False)

	if 'insertedDeviceName' in self.d.keys():
	    flash = self.l['flash_dontforget'][self.lang]
	else:
	    flash = ''
	text = self.l['print_finish'][self.lang] + flash
	self.label=QLabel(text, self)
	self.label.setObjectName('scanfinishlabel')
	stylesheet='background-image: url("img/scan/finish_scan.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.label.setStyleSheet(stylesheet)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,d['xres']-480,450))
	self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
	self.label.setVisible(False)

	self.b_next=QPushButton(self.l['print_another'][self.lang],self)
	self.b_next.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_next.setFont(font)
	self.b_next.setGeometry(QRect((d['xres']-600)//2, 530, 600, 50))
	self.connect(self.b_next, SIGNAL("clicked()"), self.nextPrint)
	self.b_next.setFocusPolicy(Qt.NoFocus)
	self.b_next.setVisible(False)

        self.b_back=QPushButton(self)
	self.b_back.setObjectName('printbuttonback')
	stylesheet='background-image: url("img/b_back_green.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.b_back.setStyleSheet(stylesheet)
        self.b_back.setText(self.l['menu'][self.lang])
        self.b_back.setFont(font)
        self.b_back.setGeometry(QRect(100, 800, 420, 170))
        self.connect(self.b_back,  SIGNAL("clicked()"),  self.toMain)
        self.b_back.setFocusPolicy(Qt.NoFocus)
        self.b_back.setVisible(False)

	self.b_change=QPushButton(self.l['take_change'][self.lang],self)
	self.b_change.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_change.setFont(font)
	self.b_change.setGeometry(QRect((d['xres']-600)//2, 600, 600, 50))
	self.connect(self.b_change, SIGNAL("clicked()"), self.change)
	self.b_change.setFocusPolicy(Qt.NoFocus)
	self.b_change.setVisible(False)

        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

	self.timer=QTimer()
	self.showTimer = QTimer()
	self.showTimer.singleShot(500, self.showUI)


    def showUI(self):
	self.label.show()
	self.b_back.show()
	self.b_next.show()
	print self.d['coinSumm'], self.d['balance']
	if (self.d['balance'] > 0) and (self.d['coinSumm'] > self.d['balance']): 
	    self.b_change.show()
	    self.timer.start(30000)
	    self.connect(self.timer, SIGNAL("timeout()"), self.change)
	else:
	    self.b_change.hide()
	    self.timer.start(30000)
	    self.connect(self.timer, SIGNAL("timeout()"), self.toMain)


    def change(self):
	'zdacha'
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.toMain)
	self.timer.stop()
	#self.disconnect(self.timer, SIGNAL("timeout()"), self.change)
	self.connect(self.d['cash'], SIGNAL("payoutFinished()"), self.changeOK)
	self.connect(self.d['cash'], SIGNAL("cantGiveChange(int)"), self.cantGiveChange)
	self.d['cash'].payBack(self.d['balance'])

	self.b_next.hide()
	self.b_back.hide()
	self.b_change.hide()
	self.label.hide()


    def changeOK(self):
	try:
	    self.d['action'].finish(status='success')
	except:
	    pass
	print "calling changeOK func of print_finish"
	self.toMain()

    def cantGiveChange(self):
	self.d['saveData']()
	self.d['log'].log('PRINT: Cant Give Change')
	ChangeNet(self.d).exec_()
	self.toMain()

    def toMain(self):
	'Back to main menu'
	self.disconnect(self.d['cash'], SIGNAL("payoutFinished()"), self.changeOK)
	self.disconnect(self.d['cash'], SIGNAL("cantGiveChange(int)"), self.cantGiveChange)

	if self.d['balance']==0 and ('action' in self.d.keys()): 
	    self.d['action'].finish(status='success')
	    del(self.d['action'])

	self.disconnect(self.timer, SIGNAL("timeout()"), self.toMain)
	self.timer.stop()
	self.timer.deleteLater()
	
	for window in ['print_fileselect','print_finish','print_preview','cat']:
	    if window in self.d.keys(): 
	        try:
		    if self.d[window] != None:
		        self.d[window].close() 
		except:
		    pass
		del self.d[window]
	self.deleteLater()


    def nextPrint(self):
	self.timer.stop()
	self.disconnect(self.timer, SIGNAL("timeout()"), self.change)
	del(self.timer)
        for window in ['print_finish','print_preview']:
	    if window in self.d.keys(): 
		try:
		    if self.d[window] != None:
			self.d[window].close() 
		except:
		    pass
		del self.d[window]


    def help(self):
        pass

    def enterEvent(self,event):
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.toMain)
	event.accept

    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.toMain)
	event.accept



class _print_error(QDialog):
    def __init__(self,d):
	QDialog.__init__(self)
	self.d=d
	self.l=d['l']
	self.lang=d['lang']
	
	self.setStyleSheet('* { background-color: transparent;}')
	drawBackground(self, d)

	font = QFont()
        font.setPointSize(16)
        font.setWeight(50)
        font.setBold(False)

	if 'insertedDeviceName' in self.d.keys():
	    flash = self.l['flash_dontforget'][self.lang]
	else:
	    flash = ''
	text = self.l['print_error'][self.lang] + flash

	self.label=QLabel(text, self)
	#self.label=QLabel(text % (str(d['printed_pages']),str(d['printNpage'])), self)
	self.label.setObjectName('scanfinishlabel')
	stylesheet='background-image: url("img/scan/finish_scan.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.label.setStyleSheet(stylesheet)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,d['xres']-480,450))
	self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
	self.label.setVisible(False)

	self.b_email=QPushButton(self.l['email_to_support'][self.lang],self)
	self.b_email.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_email.setFont(font)
	self.b_email.setGeometry(QRect((d['xres']-600)//2, 530, 600, 50))
	self.connect(self.b_email, SIGNAL("clicked()"), self.email)
	self.b_email.setFocusPolicy(Qt.NoFocus)
	self.b_email.setVisible(False)

        self.b_back=QPushButton(self)
	self.b_back.setObjectName('scanbuttonback')
	stylesheet='background-image: url("img/scan/b_back_white.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.b_back.setStyleSheet(stylesheet)
        self.b_back.setText(self.l['menu'][self.lang])
        self.b_back.setFont(font)
        self.b_back.setGeometry(QRect(100, 800, 420, 170))
        self.connect(self.b_back,  SIGNAL("clicked()"),  self.toMain)
        self.b_back.setFocusPolicy(Qt.NoFocus)
        self.b_back.setVisible(False)

	self.b_change=QPushButton(self.l['change'][self.lang],self)
	self.b_change.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_change.setFont(font)
	self.b_change.setGeometry(QRect((d['xres']-600)//2, 600, 600, 50))
	self.connect(self.b_change, SIGNAL("clicked()"), self.change)
	self.b_change.setFocusPolicy(Qt.NoFocus)
	self.b_change.setVisible(False)

        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

	self.timer=QTimer()
	self.showTimer = QTimer()
	self.showTimer.singleShot(500, self.showUI)


    def showUI(self):
	self.label.show()
	self.b_back.show()
	self.b_email.show()
	print self.d['coinSumm'], self.d['balance']
	if (self.d['balance'] > 0) and (self.d['coinSumm'] > self.d['balance']): 
	    self.b_change.show()
	    self.timer.start(30000)
	    self.connect(self.timer, SIGNAL("timeout()"), self.change)
	else:
	    self.b_change.hide()
	    self.timer.start(30000)
	    self.connect(self.timer, SIGNAL("timeout()"), self.toMain)


    def change(self):
	'zdacha'
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.toMain)
	self.disconnect(self.timer, SIGNAL("timeout()"), self.change)
	self.timer.stop()

	self.b_back.hide()
	self.b_change.hide()
	self.label.setText(self.d['giving_change'][self.lang])
	#self.label.hide()

	self.connect(self.d['cash'], SIGNAL("payoutFinished()"), self.toMain)
	self.connect(self.d['cash'], SIGNAL("cantGiveChange(int)"), self.toMain)
	self.d['cash'].payBack(self.d['balance'])
	#self.label.setText("I am giving you change!")


    def toMain(self):
	'Back to main menu'
	try:
	    if self.d['balance']==0 and ('action' in self.d.keys()): 
		self.d['action'].finish(status='error')
		del(self.d['action'])
	except:
	    pass
	self.disconnect(self.timer, SIGNAL("timeout()"), self.toMain)
        self.disconnect(self.b_back,  SIGNAL("clicked()"),  self.toMain)
        self.disconnect(self.b_change,  SIGNAL("clicked()"),  self.change)
        self.disconnect(self.d['cash'], SIGNAL("changeOK()"), self.changeOK)
	self.disconnect(self.d['cash'], SIGNAL("cantGiveChange(int)"), self.cantGiveChange)
	self.timer.stop()
	self.timer.deleteLater()
	
	for window in ['print_fileselect','print_finish','print_preview','cat','print_error']:
	    if window in self.d.keys(): 
		try:
		    if self.d[window] != None:
			self.d[window].close() 
		except:
		    pass
		del self.d[window]
	self.deleteLater()


    def enterEvent(self,event):
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.toMain)
	event.accept

    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.toMain)
	event.accept
	

    def email(self):
	self.timer.stop()
	self.disconnect(self.timer, SIGNAL("timeout()"), self.toMain)
	support(self.d).exec_()
	self.toMain()








