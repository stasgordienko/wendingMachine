# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from os import *
from Print_print import _print_print
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


class _print_charge(QWidget):
    def __init__(self,d):
        QWidget.__init__(self)
        self.d=d
        self.l=d['l']
        self.lang=d['lang']

        self.filename=d['print_filename']
        self.path=d['print_path']
        self.fullname=d['print_fullname']
        self.doctype=d['docType']
        self.npage=d['printNpage']
        self.balance=d['balance']
        self.cost=d['printDocCost']

        font5 = QFont()
        font5.setPointSize(22)
        font5.setWeight(75)
        font5.setBold(False)

	nominalsN = [1,2,5,10,20,50,100,200]
	notes = u''
	for i in nominalsN:
	    if i <= d['print_maxNominal']//100:
		notes = notes + str(i) + ','
	notes = notes[:-1]

	coins = u'5,10,25,50 коп, 1'

        self.label5 = QLabel(self)
        self.label5.setFont(font5)
        self.label5.setObjectName(_fromUtf8("label5"))
        #self.label5.setGeometry(QRect((d['xres']-900)//2, 400, 900, 100))
        self.label5.setGeometry(QRect(0, 130, d['xres'], 80))
        self.label5.setText(self.l['print_charge'][self.lang] % (notes,coins))
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
        self.label.setGeometry(QRect(1, 512, d['xres'], 150))
        self.label.setAlignment(Qt.AlignCenter)

        self.label_ = QLabel(self)
        self.label_.setFont(font)
        self.label_.setObjectName(_fromUtf8("label_"))
        self.label_.setGeometry(QRect(1, 555, 650, 50))
        self.label_.setStyleSheet("background-color: transparent; color: white;")
        self.label_.setText(self.l['xerox_vneseno'][self.lang])
	self.label_.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        self.label_uah = QLabel(self)
        self.label_uah.setFont(font)
        self.label_uah.setObjectName(_fromUtf8("label_uah"))
        self.label_uah.setGeometry(QRect(860, 555, 80, 50))
        self.label_uah.setStyleSheet("background-color: transparent; color: white;")
        self.label_uah.setText(self.l['uah'][self.lang])
	self.label_uah.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

        self.label_cost_uah = QLabel(self)
        self.label_cost_uah.setFont(font)
        self.label_cost_uah.setObjectName(_fromUtf8("label_cost_uah"))
        self.label_cost_uah.setGeometry(QRect(860, 450, 80, 50))
        self.label_cost_uah.setStyleSheet("background-color: transparent; color: #333333;")
        self.label_cost_uah.setText(self.l['uah'][self.lang])
	self.label_cost_uah.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

        self.label1 = QLabel(self)
        self.label1.setFont(font)
        self.label1.setObjectName(_fromUtf8("label1"))
        self.label1.setGeometry(QRect(1, 450, 650, 50))
        self.label1.setStyleSheet("background-color: transparent; color: #333333;")
        self.label1.setText(self.l['print_doc_cost'][self.lang])
        self.label1.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.label1.show()

        font = QFont()
        font.setPointSize(35)
        font.setWeight(75)
        font.setBold(True)
        self.label_sum = QLabel(self)
        self.label_sum.setFont(font)
        self.label_sum.setObjectName(_fromUtf8("label_sum"))
        self.label_sum.setGeometry(QRect(650, 547, 200, 60))
        self.label_sum.setStyleSheet("background-color: transparent; color: white;")
        self.label_sum.setAlignment(Qt.AlignRight | Qt.AlignBottom)

	self.l_cost = QLabel(self)
        self.l_cost.setFont(font)
        self.l_cost.setObjectName(_fromUtf8("l_cost"))
        self.l_cost.setText(str("%6.2f" % (self.cost/100)))
        self.l_cost.setGeometry(QRect(650, 445, 200, 60))
        self.l_cost.setAlignment(Qt.AlignRight | Qt.AlignBottom)

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

        self.b_print = QPushButton(self)
        self.b_print.setFont(font)
        self.b_print.setObjectName(_fromUtf8("b_next"))
        self.b_print.setText(self.l['print'][self.lang])
        self.b_print.setGeometry(QRect((d['xres']-300)//2, d['yres']-200, 300, 95))
        self.b_print.setFocusPolicy(Qt.NoFocus)

        font = QFont()
        font.setPointSize(14)
        font.setWeight(25)
        font.setBold(False)
        self.label3 = QLabel(self)
        self.label3.setFont(font)
        self.label3.setObjectName(_fromUtf8("label3"))
        self.label3.setStyleSheet("background-color: transparent; color: #333333;")
        self.label3.setText(self.l['print_cost_detail'][self.lang] % (self.npage, float(d['print_pagecost'])/100))
        self.label3.setGeometry(QRect(20, 670, d['xres']-40, 50))
        self.label3.setAlignment(Qt.AlignCenter)

        self.connect(self.b_print,  SIGNAL("clicked()"),  self.printAll)
        self.connect(self.b_main,  SIGNAL("clicked()"),  self.back)
        self.connect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)

        self.stimer = QTimer()
        self.stimer.setInterval(int(self.d['timeout'])*1000)
        self.connect(self.stimer, SIGNAL("timeout()"), self.pop)

        self.connect(self.d['cash'], SIGNAL("balanceAdded(int)"), self.put)
        self.connect(self.d['cash'], SIGNAL("billStateChanged(QString)"), self.bstate)
        self.connect(self.d['cash'], SIGNAL("coinStateChanged(QString)"), self.cstate)

        self.put(0)



    def printAll(self):
        self.stimer.stop()
        self.d['cash'].stop()
        #self.d['print_pages']=self.pages
        self.d['print_print']=_print_print(self.d)
        self.d['print_print'].showFullScreen()


    def back(self):
        self.close()


    def put(self, n):
        #self.time()
        if (n>0 or self.d['balance']>0): #and (self.d['copier'].getState()!='ready'): 
	    self.d['copier'].zero()
	    
        self.label_sum.setText("%6.2f" % (self.d['balance']/100))
        
        if self.d['balance']>=self.cost:
            self.label.setStyleSheet("background-color: green;")
            self.label5.hide()
            self.b_print.setEnabled(True)
            self.b_print.setVisible(True)
            self.top.setVisible(True)
            self.d['cash'].stop()
        elif self.d['balance']==0:
	    self.label.setStyleSheet("background-color: red;")
	    self.label5.show()
            self.b_print.setEnabled(False)
            self.b_print.setVisible(False)
            self.d['cash'].get(self.d['print_maxNominal'])
        else:
	    self.label.setStyleSheet("background-color: orange;")
	    self.label5.show()
            self.b_print.setEnabled(False)
            self.b_print.setVisible(False)
            self.d['cash'].get(self.d['print_maxNominal'])
        
        self.stimer.start()


    def pop(self):
	for window in ['print_fileselect','print_preview','cat','print_charge']:
	    if window in self.d.keys(): 
		try:
		    if self.d[window] != None:
			self.d[window].close()
		    del self.d[window]
		except:
		    pass

        
    def closeEvent(self, event):
	self.stimer.stop()
        self.disconnect(self.b_print,  SIGNAL("clicked()"),  self.printAll)
        self.disconnect(self.b_main,  SIGNAL("clicked()"),  self.back)
        self.disconnect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
        self.disconnect(self.stimer, SIGNAL("timeout()"), self.pop)
        self.disconnect(self.d['cash'], SIGNAL("balanceAdded(int)"), self.put)
        self.disconnect(self.d['cash'], SIGNAL("billStateChanged(QString)"), self.bstate)
        self.disconnect(self.d['cash'], SIGNAL("coinStateChanged(QString)"), self.cstate)
        self.d['cash'].stop()
	self.deleteLater()
        event.accept()


    def helpbox(self):
        self.stimer.stop()
        if self.d['source_type'] == 'pdf':
	    if 'cat' in self.d.keys():
		page = 'catalog'
	    else:
		page = 'printdoc'
	else:
	    page = 'printimg'
        hb=helpBox(page, self.d)
        hb.exec_()
	self.stimer.start()

    def bstate(self):
	pass
	
    def cstate(self):
	pass
	
    def enterEvent(self,event):
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.pop)
	event.accept()

    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.pop)
	event.accept
