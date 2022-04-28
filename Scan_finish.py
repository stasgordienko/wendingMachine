# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from dialogs import *
from os import *
import sys
from dialogs import *

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class _scan_finish(QDialog):
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

	if d['scan_type']=='email':
	    text=self.l['scan_email_finish'][self.lang] % (d['scanFileName'],d['email'])
	else:
	    text=self.l['scan_finish'][self.lang] % (d['scanFileName'])
	    
	self.label=QLabel(text, self)
	self.label.setObjectName('scanfinishlabel')
	stylesheet='background-image: url("img/scan/finish_scan.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.label.setStyleSheet(stylesheet)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,d['xres']-480,450))
	self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
	self.label.setVisible(False)

	self.b_next=QPushButton(self.l['scan_another'][self.lang],self)
	self.b_next.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_next.setFont(font)
	self.b_next.setGeometry(QRect((d['xres']-600)//2, 530, 600, 50))
	self.connect(self.b_next, SIGNAL("clicked()"), self.nextCopy)
	self.b_next.setFocusPolicy(Qt.NoFocus)
	self.b_next.setVisible(False)

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
	self.showTimer.setInterval(500)
	self.connect(self.showTimer, SIGNAL("timeout()"), self.showUI)
	self.showTimer.start()


    def showUI(self):
	self.showTimer.stop()
	self.label.show()
	self.b_back.show()
	self.b_next.show()
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

	self.connect(self.d['cash'], SIGNAL("payoutFinished()"), self.changeOK)
	self.connect(self.d['cash'], SIGNAL("cantGiveChange(int)"), self.cantGiveChange)
	self.d['cash'].payBack(self.d['balance'])

	self.b_next.hide()
	self.b_back.hide()
	self.b_change.hide()
	self.label.hide()
	#self.label.setText("I am giving you change!")


    def changeOK(self):
	if ('action' in self.d.keys()) and self.d['action']:
	    self.d['action'].finish(status='success')
	print "calling changeOK func of scan_finish"
	#end_session
	if 'scan' in self.d.keys(): 
	    self.d['scan'].close()
	    del(self.d['scan'])
        self.close()
        del(self.d['scan_finish'])
        self.deleteLater()

    def cantGiveChange(self):
	self.d['saveData']()
	self.nextCopy()

    def back(self):
	'Back to main menu'
	if self.d['balance']==0 and ('action' in self.d.keys()) and self.d['action']: 
	    self.d['action'].finish(status='success')
	self.disconnect(self.timer, SIGNAL("timeout()"), self.back)
	self.timer.stop()
	self.timer.deleteLater()
	for window in ['scan','scan_charge','scan_finish']:
	    if window in self.d.keys(): 
		try:
		    if self.d[window] != None:
			self.d[window].close() 
		    del self.d[window]
		except:
		    pass
        self.deleteLater()


    def nextCopy(self):
	self.timer.stop()
	self.disconnect(self.timer, SIGNAL("timeout()"), self.change)
	del(self.timer)
        self.close()
        self.deleteLater()
        del(self.d['scan_finish'])


    def help(self):
        pass


    def enterEvent(self,event):
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.back)
	event.accept

    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.back)
	event.accept

