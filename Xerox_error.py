# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from dialogs import *
from os import *
import sys
import subprocess

class _xerox_error(QDialog):
    def __init__(self,d):
	QDialog.__init__(self)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
	self.d=d
	self.l=d['l']
	self.lang=d['lang']

	self.setStyleSheet('* { background-color: transparent;}')
	drawBackground(self, d)

	font = QFont()
        font.setPointSize(16)
        font.setWeight(50)
        font.setBold(False)

	self.label=QLabel(self.l['xerox_error'][self.lang] % (str(d['printed_pages']),str(d['ncopies'])), self)
	self.label.setObjectName('scanfinishlabel')
	stylesheet='background-image: url("img/scan/finish_scan.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.label.setStyleSheet(stylesheet)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,d['xres']-480,450))
	self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
	self.label.setVisible(False)


        self.b_back=QPushButton(self)
	self.b_back.setObjectName('scanbuttonback')
	stylesheet='background-image: url("img/b_back_green.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.b_back.setStyleSheet(stylesheet)
        self.b_back.setText(self.l['menu'][self.lang])
        self.b_back.setFont(font)
        self.b_back.setGeometry(QRect(100, 800, 420, 170))
        self.connect(self.b_back,  SIGNAL("clicked()"),  self.back)
        self.b_back.setFocusPolicy(Qt.NoFocus)
        self.b_back.setVisible(False)

	self.b_change=QPushButton(self.l['change'][self.lang],self)
	self.b_change.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_change.setFont(font)
	self.b_change.setGeometry(QRect((d['xres']-600)//2, 600, 600, 50))
	self.connect(self.b_change, SIGNAL("clicked()"), self.change)
	self.b_change.setFocusPolicy(Qt.NoFocus)
	self.b_change.setVisible(False)

	self.timer=QTimer()
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.close)

	print self.d['coinSumm'], self.d['balance']
	if (self.d['balance'] > 0) and (self.d['coinSumm'] > self.d['balance']): 
	    self.b_change.setEnabled(True)
	    self.timer.start(30000)
	    self.connect(self.timer, SIGNAL("timeout()"), self.change)
	else:
	    self.b_change.setEnabled(False)
	    self.timer.start(30000)
	    self.connect(self.timer, SIGNAL("timeout()"), self.back)

	self.showTimer = QTimer()
	self.showTimer.setInterval(500)
	self.connect(self.showTimer, SIGNAL("timeout()"), self.showUI)
	self.showTimer.start()

	

    def showUI(self):
	self.showTimer.stop()
	self.label.show()
	self.b_back.show()
	print self.d['coinSumm'], self.d['balance']
	if (self.d['balance'] > 0) and (self.d['coinSumm'] > self.d['balance']): 
	    self.b_change.show()
	    self.connect(self.timer, SIGNAL("timeout()"), self.change)
	    self.timer.start(30000)
	else:
	    self.b_change.hide()
	    self.connect(self.timer, SIGNAL("timeout()"), self.back)
	    self.timer.start(30000)


    def change(self):
	'zdacha'
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.close)
	self.disconnect(self.timer, SIGNAL("timeout()"), self.change)
	self.timer.stop()
	self.timer.deleteLater()

	self.b_back.hide()
	self.b_change.hide()
	self.label.setText(self.l['giving_change'][self.lang])
	#self.label.hide()

	self.connect(self.d['cash'], SIGNAL("payoutFinished()"), self.changeOK)
	self.connect(self.d['cash'], SIGNAL("cantGiveChange(int)"), self.cantGiveChange)
	self.d['cash'].payBack(self.d['balance'])


    def changeOK(self):
	self.d['action'].finish()
	self.disconnect(self.d['cash'], SIGNAL("changeOK()"), self.changeOK)
	self.disconnect(self.d['cash'], SIGNAL("cantGiveChange(int)"), self.cantGiveChange)
	#end_session
	self.d['saveData']()
	self.close()

    def cantGiveChange(self):
    	self.d['action'].status='cant give ghange'
	self.back()


    def back(self):
	'Back to main menu'
	self.d['action'].status='error'
	if self.d['balance']==0 : self.d['action'].finish()
	self.disconnect(self.timer, SIGNAL("timeout()"), self.back)
        self.disconnect(self.b_back,  SIGNAL("clicked()"),  self.back)
        self.disconnect(self.b_change,  SIGNAL("clicked()"),  self.change)
	self.timer.stop()
	self.timer.deleteLater()
	self.close()


    def help(self):
        pass

    def closeEvent(self,event):
	for window in ['xerox','xerox_scan','xerox_error']:
	    if window in self.d.keys(): 
		try:
		    if self.d[window] != None:
			self.d[window].close() 
		    del self.d[window]
		except:
		    pass
        self.deleteLater()
        event.accept()

    def enterEvent(self,event):
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.close)
	event.accept

    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.close)
	event.accept


