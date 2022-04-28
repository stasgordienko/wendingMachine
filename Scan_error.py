# -*- coding: windows-1251 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from os import *
from dialogs import *
import sys

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class _scan_error(QDialog):
    def __init__(self,d):
	QDialog.__init__(self)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
	self.d=d
	self.l=d['l']
	self.lang=d['lang']

	self.label=QLabel(self.l['error_occured'][self.lang], self)
	self.label.setGeometry(QRect(10,100,d['xres']-20,d['yres']-200))
	self.label.show()

        self.b_back=QPushButton(self)
        self.b_back.setText(self.l['back'][self.lang])
        self.b_back.setGeometry(QRect((d['xres']-150)//2, 700, 150, 70))
        self.connect(self.b_back,  SIGNAL("clicked()"),  self.back)
        self.b_back.show()

	self.b_change=QPushButton(self.l['take_change'][self.lang],self)
	self.b_change.setGeometry(QRect((d['xres']-120)//2, 800, 120, 70))
	self.connect(self.b_change, SIGNAL("clicked()"), self.change)
	self.b_change.show()

	self.timer=QTimer()

	print self.d['coinSumm'], self.d['balance']
	if (self.d['balance'] > 0) and (self.d['coinSumm'] > self.d['balance']): 
	    self.b_change.setEnabled(True)
	    self.timer.start(30000)
	    self.connect(self.timer, SIGNAL("timeout()"), self.change)
	else:
	    self.b_change.setEnabled(False)
	    self.timer.start(30000)
	    self.connect(self.timer, SIGNAL("timeout()"), self.back)

	

    def change(self):
	'zdacha'
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.close)
	self.disconnect(self.timer, SIGNAL("timeout()"), self.change)
	self.timer.stop()
	self.timer.deleteLater()

	self.PB=QDialog(self)
	#self.PB.label=QLabel("I am giving you change!",PB)
	self.PB.showFullScreen()

	self.connect(self.d['cash'], SIGNAL("changeOK()"), self.changeOK)
	self.connect(self.d['cash'], SIGNAL("cantGiveChange(int)"), self.cantGiveChange)
	self.d['cash'].payBack(self.d['balance'])

    def changeOK(self):
	self.disconnect(self.d['cash'], SIGNAL("changeOK()"), self.changeOK)
	self.disconnect(self.d['cash'], SIGNAL("cantGiveChange(int)"), self.cantGiveChange)
	self.PB.close()
	del(self.PB)
	self.d['xerox'].close()
	del(self.d['xerox'])
	#end_session
	self.d['saveData']()
	self.d['main'].update()
	self.close()
	del(self)

    def cantGiveChange(self):
	self.PB.close()
	del(self.PB)
	self.back()


    def back(self):
	'Back to main menu'
	self.disconnect(self.timer, SIGNAL("timeout()"), self.back)
        self.disconnect(self.b_back,  SIGNAL("clicked()"),  self.back)
        self.disconnect(self.b_change,  SIGNAL("clicked()"),  self.change)
	self.timer.stop()
	self.timer.deleteLater()
	for window in ['scan','scan_charge','scan_error']:
	    if window in self.d.keys(): 
		try:
		    if self.d[window] != None:
			self.d[window].close() 
		    del self.d[window]
		except:
		    pass
        self.deleteLater()


    def help(self):
        pass

    def enterEvent(self,event):
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.back)
	event.accept

    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.back)
	event.accept
