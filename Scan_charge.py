# -*- coding: utf-8 -*-
from __future__ import division

import db
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from os import *
from Scan_scan import _scan_scan
from PyQt4.QtCore import (QByteArray, QDataStream, QDate, QIODevice,
        QRegExp, QString, Qt, SIGNAL)
from PyQt4.QtGui import (QApplication, QDateEdit, QFrame, QGridLayout,
        QHBoxLayout, QLabel, QLineEdit, QPushButton, QRegExpValidator,
        QWidget)
from dialogs import *


try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class _scan_charge(QWidget):
    
    def __init__(self,d):
        QWidget.__init__(self)
        self.setObjectName(_fromUtf8("Scan_charge"))
        #self.setStyleSheet('background-color:white;')
        self.d=d
        self.l=d['l']
        self.lang=d['lang']

        font5 = QFont()
        font5.setPointSize(22)
        font5.setWeight(75)
        font5.setBold(False)

	nominalsN = [1,2,5,10,20,50,100,200]
	notes = u''
	for i in nominalsN:
	    if i <= d['scan_maxNominal']//100:
		notes = notes + str(i) + ','
	notes = notes[:-1]

	coins = u'5,10,25,50 коп, 1'

        self.label5 = QLabel(self)
        self.label5.setFont(font5)
        self.label5.setObjectName(_fromUtf8("label5"))
        #self.label5.setGeometry(QRect((d['xres']-900)//2, 400, 900, 100))
        self.label5.setGeometry(QRect(0, 130, d['xres'], 80))
        self.label5.setText(self.l['scan_charge'][self.lang] % (notes,coins))
        self.label5.setStyleSheet("background-color: transparent; color: red;")
        self.label5.setWordWrap(True)
        self.label5.setAlignment(Qt.AlignCenter)

        font = QFont()
        font.setPointSize(28)
        font.setWeight(75)
        font.setBold(False)

        self.label = QLabel(self)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label.setGeometry(QRect(1, 562, d['xres'], 150))
        self.label.setAlignment(Qt.AlignCenter)

        self.label_ = QLabel(self)
        self.label_.setFont(font)
        self.label_.setObjectName(_fromUtf8("label_"))
        self.label_.setGeometry(QRect(1, 605, 650, 50))
        self.label_.setStyleSheet("background-color: transparent; color: white;")
	self.label_.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        self.label_uah = QLabel(self)
        self.label_uah.setFont(font)
        self.label_uah.setObjectName(_fromUtf8("label_uah"))
        self.label_uah.setGeometry(QRect(810, 605, 80, 50))
        self.label_uah.setStyleSheet("background-color: transparent; color: white;")
	self.label_uah.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

        font = QFont()
        font.setPointSize(35)
        font.setWeight(75)
        font.setBold(True)
        self.label_sum = QLabel(self)
        self.label_sum.setFont(font)
        self.label_sum.setObjectName(_fromUtf8("label_sum"))
        self.label_sum.setGeometry(QRect(650, 597, 150, 60))
        self.label_sum.setStyleSheet("background-color: transparent; color: white;")
        self.label_sum.setAlignment(Qt.AlignRight | Qt.AlignBottom)

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
        self.b_help.setText(self.l['help'][self.lang])
        self.b_help.setFocusPolicy(Qt.NoFocus)

        self.b_main = QPushButton(self.top)
        self.b_main.setFont(font)
        self.b_main.setObjectName(_fromUtf8("b_main"))
        self.b_main.setGeometry(QRect(30, 15, 400, 90))
        self.b_main.setText(self.l['back'][self.lang])
        self.b_main.setFocusPolicy(Qt.NoFocus)

        self.b_next = QPushButton(self)
        self.b_next.setFont(font)
        self.b_next.setObjectName(_fromUtf8("b_next"))
        self.b_next.setText(self.l['next'][self.lang])
        self.b_next.setGeometry(QRect((d['xres']-450), d['yres']-200, 300, 95))
        self.b_next.setFocusPolicy(Qt.NoFocus)

        self.l_able = QLabel(self)
        font = QFont()
        font.setPointSize(16)
        self.l_able.setFont(font)
        self.l_able.setAlignment(Qt.AlignCenter)
        self.l_able.setObjectName(_fromUtf8("l_able"))
        self.l_able.setGeometry(QRect(1, 665, 880, 40))
        self.l_able.setWordWrap(True)
        self.l_able.setAlignment(Qt.AlignRight)


        self.oneside = QRadioButton(self)
        font = QFont()
        font.setPointSize(28)
        self.oneside.setFont(font)
        self.oneside.setObjectName(_fromUtf8("oneside"))
        self.oneside.setText(u"%s - %5.2f грн" % (self.l['scan_gray'][self.lang],  float(self.d['scan_1cost'])/100 ))
        self.oneside.setGeometry(QRect((d['xres']-900)//2, 225, 900, 100))
        self.oneside.setFocusPolicy(Qt.NoFocus)

        self.doubleside = QRadioButton(self)
        font = QFont()
        font.setPointSize(28)
        self.doubleside.setFont(font)
        self.doubleside.setObjectName(_fromUtf8("doubleside"))
        self.doubleside.setText(u"%s - %5.2f грн" % (self.l['scan_color'][self.lang],  float(self.d['scan_2cost'])/100))
        self.doubleside.setGeometry(QRect((d['xres']-900)//2, 325, 900, 100))
        self.doubleside.setFocusPolicy(Qt.NoFocus)

        self.summax=d['scan_summax']
        self.sided='1'
        self.cost=0
        self.oneside.setChecked(True)
        self.l_status=QLabel('status')
        
        self.b_scale=QCheckBox(self)
        self.b_scale.setObjectName(_fromUtf8("b_scale"))
        self.b_scale.setText(u"%s" % (self.l['scan_scale'][self.lang]))
        self.b_scale.setGeometry(QRect((d['xres']-900)//2, 435, 900, 100))
        self.b_scale.setChecked(False)
        font = QFont()
        font.setPointSize(28)
        self.b_scale.setFont(font)
        self.b_scale.setFocusPolicy(Qt.NoFocus)

        self.stimer = QTimer()
        self.newTime()
        self.stimer.setInterval(1000)

        self.connect(self.stimer, SIGNAL("timeout()"), self.time)
        self.connect(self.d['cash'], SIGNAL("balanceAdded(int)"), self.put)
        self.connect(self.d['cash'], SIGNAL("billStateChanged(QString)"), self.bstate)
        self.connect(self.d['cash'], SIGNAL("coinStateChanged(QString)"), self.cstate)
        self.connect(self.b_next,  SIGNAL("clicked()"),  self.scan)
        self.connect(self.b_main,  SIGNAL("clicked()"),  self.back)
        self.connect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
        self.connect(self.oneside,  SIGNAL("clicked()"),  self.oside)
        self.connect(self.doubleside,  SIGNAL("clicked()"),  self.dside)
        self.connect(self.b_scale,  SIGNAL("clicked()"),  self.scale)


        if 'action' in d.keys(): 
	    if (d['action'].isFinished == False):
		if d['action'].typeId != 'scan':
		    d['action'].finish()
		    d['action']=db.action(termId=int(d['device']),balance=float(d['balance']/100),typeId='scan')
        else: 
	    d['action']=db.action(termId=int(d['device']),balance=float(d['balance']/100),typeId='scan')

        self.put(0)
    

    def time(self):
	if (self.d['scan_type']=='flash') and (not path.exists(self.d['flash']) ): #or not path.exists(self.d['flash_dev'])):
	    print "SCANCHARGE TIMEOUT!!!"
	    self.back()
	    return

        if self.timeout>0:
	    self.timeout-=1
	else:
	    #todo: dialog with question: "are you still here?" (timeout 10 sec)
	    self.back()
	    return

	    
    def newTime(self):
	self.timeout=int(self.d['timeout'])
	self.d['ping'].dontdisconnect()
        self.stimer.start()

    def scan(self):
        self.stimer.stop()
        self.d['cash'].stop()
        self.d['sided']=self.sided
        self.d['cost']=self.cost
        self.d['scaling']=self.b_scale.isChecked()
        
        self.d['scan_scan']=_scan_scan(self.d)
        self.close()
	del(self.d['scan_charge'])
	self.deleteLater()
        #self.d['saveData']()

            
    def back(self):
        #self.d['cash'].stop()
        #self.d['main'].update()
        self.stimer.stop()
        self.disconnect(self.stimer, SIGNAL("timeout()"), self.time)
	del(self.d['scan_charge'])
        self.close()
        self.deleteLater()


    def helpbox(self):
        self.stimer.stop()
        if self.d['scan_type'] == 'email':
	    page = 'scanemail'
	else:
	    page = 'scanflash'
        hb=helpBox(page, self.d)
        hb.exec_()
        self.newTime()
        


    def put(self, n):
        self.update()
        if self.d['balance']>(self.summax):
	    self.d['cash'].stop()
        else:
	    self.d['cash'].get(self.d['scan_maxNominal'])

    def update(self):
        self.newTime()
        #self.label.setText(self.l['xerox_vneseno'][self.lang] % (self.d['balance']/100))
        self.label_.setText(self.l['xerox_vneseno'][self.lang])
        self.label_sum.setText("%4.2f" % (self.d['balance']/100))
        self.label_uah.setText(self.l['uah'][self.lang])
        self.cost=int(self.d['scan_'+str(self.sided)+'cost'])
        self.npage=int(self.d['balance']//self.cost)
        
        if self.d['balance']>=self.cost:
            self.l_able.setText(self.l['scan_youcan'][self.lang]  % (self.npage))
            self.l_able.setStyleSheet("background-color: green; color: white;")
            self.label.setStyleSheet("background-color: green; color: white;")
            self.label5.hide()
            self.l_able.hide() 							# <--- always hide label
            self.b_next.show()
        elif self.d['balance']==0:
            #self.l_able.setText(self.l['xerox_youhaveno'][self.lang]  % (self.sided))
            self.l_able.hide()
            self.b_next.hide()
            self.label5.show()
            self.label.setStyleSheet("background-color: red; color: white;")
            self.l_able.setStyleSheet("background-color: red; color: red;")
        else:
            #self.l_able.setText(self.l['scan_youhaveno'][self.lang])
            self.l_able.hide()
            self.label5.show()
            self.l_able.setStyleSheet("background-color: orange; color: white;")
            self.label.setStyleSheet("background-color: orange; color: white;")
            self.b_next.hide()


    def oside(self):
        if self.sided=='2':
            self.sided='1'
            #self.doubleside.setChecked(False)
            self.update()
        
    def dside(self):
        if self.sided=='1':
            self.sided='2'
            self.update()

        
    def scale(self):
	pass
	
	
    def closeEvent(self, event):
        self.d['cash'].stop()
        if 'action' in self.d.keys():
	    if self.d['balance'] == 0:
		if self.d['action'].usedsumm == 0:
		    del(self.d['action'])
		else:
		    self.d['action'].finish()
		    del(self.d['action'])
	else:
	    print "action not found"

        self.disconnect(self.d['cash'], SIGNAL("balanceAdded(int)"), self.put)
        self.disconnect(self.d['cash'], SIGNAL("billStateChanged(QString)"), self.bstate)
        self.disconnect(self.d['cash'], SIGNAL("coinStateChanged(QString)"), self.cstate)

        event.accept()

    def toMain(self):
	for window in ['scan','scan_charge']:
	    if window in self.d.keys(): 
		try:
		    if self.d[window] != None:
			self.d[window].close() 
		    del self.d[window]
		except:
		    pass

    def enterEvent(self,event):
	self.update()
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.toMain)
	event.accept()

    def bstate(self):
	pass
	
    def cstate(self):
	pass
	

    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.toMain)
	event.accept
