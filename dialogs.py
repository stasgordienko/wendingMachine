# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
import mail
from xml.dom import minidom

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

reason=QString('')

#from PyQt4.QtCore import QTimer, QRect, SIGNAL, SLOT
#from PyQt4.QtGui import QDialog, QLabel, QPushButton
#from PyQt4 import Qt.FramelessWindowHint, Qt.WindowStaysOnTopHint, Qt.AlignCenter

#from PyQt4.QtCore import Qt, QString, SIGNAL, SLOT, QTimer
#from PyQt4.QtGui import QDialog, QPushButton, QLabel

def drawBackground(self, d):
    self.background1 = QLabel(self)
    self.background1.setStyleSheet("background-color: white;")
    self.background1.setPixmap(QPixmap.grabWindow(d['app'].desktop().winId()))
    self.background1.show()

    self.background2 = QLabel(self)
    self.background2.setStyleSheet('background-color: transparent; background-image: url("img/transp87black-noise.png");')
    self.background2.setGeometry(QRect(0,0,1280,1024))
    self.background2.show()


class message(QDialog):
    def __init__(self,d,text='',button='',timeout=3):
	QDialog.__init__(self)
	self.d=d
	self.l=d['l']
	self.lang=d['lang']
	self.button = button
	
	self.setStyleSheet('* { background-color: transparent;}')
	drawBackground(self, d)

	font = QFont()
        font.setPointSize(24)
        font.setWeight(50)
        font.setBold(False)

	self.label=QLabel(text, self)
	self.label.setObjectName('scanfinishlabel')
	stylesheet='background-image: url("img/scan/finish_scan.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.label.setStyleSheet(stylesheet)
	self.label.setFont(font)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,d['xres']-480,450))
	self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
	self.label.setVisible(False)

	self.b_close=QPushButton(button,self)
	self.b_close.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_close.setFont(font)
	self.b_close.setGeometry(QRect((d['xres']-300)//2, 550, 300, 100))
	self.connect(self.b_close, SIGNAL("clicked()"), self.accept)
	self.b_close.setFocusPolicy(Qt.NoFocus)
	self.b_close.setVisible(False)

        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

	self.timer = QTimer()
	self.timer.setInterval(timeout*1000)
	self.connect(self.timer, SIGNAL("timeout()"), self.reject)
	self.timer.start()
	
	self.showTimer = QTimer()
	self.showTimer.setInterval(1000)
	self.connect(self.showTimer, SIGNAL("timeout()"), self.showUI)
	self.showTimer.start()

    def showUI(self):
	self.showTimer.stop()
	self.label.show()
	if self.button: self.b_close.show()


class HelpBox(QDialog):
    def __init__(self, page, d):
        QDialog.__init__(self)
        self.d = d
        self.page = page
        
        self.setObjectName("HelpBox")
        self.widthMax=800
        self.width=0

        self.stimer = QTimer()
        self.stimer.setInterval(d['helpTimeout']*1000)
        self.connect(self.stimer, SIGNAL("timeout()"), self.accept)
        
        self.anim = QTimer()
        self.anim.setInterval(30)
        self.connect(self.anim, SIGNAL("timeout()"), self.animation)
        
	self.setStyleSheet('* { background-color: transparent;}')
	drawBackground(self,d)

        self.text=QLabel(self)
	self.text.setStyleSheet('background-color: #FFFFFF; border: 10px solid #ababab; border-radius: 20px; color: #2cd800;')
        #self.text.setGeometry((d['xres']-self.width)//2, 100, self.width, d['yres']-200)
        self.text.setWordWrap(True)
        self.text.setAlignment(Qt.AlignCenter)

        self.ok=QPushButton(d['l']['close'][d['lang']],self)
        self.ok.setStyleSheet('background-color: #EEEEEE; border: 10px solid #ababab; border-radius: 20px; color: #2cd800;')
        self.ok.setGeometry((d['xres']-200)//2, d['yres']-135,200,70)
        self.connect(self.ok, SIGNAL("clicked()"), self, SLOT("accept()"))
        self.ok.setFocusPolicy(Qt.NoFocus)
        self.ok.hide()

        self.setAutoFillBackground(False)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        #self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.powerFailure)
        self.showFullScreen()
        self.animation()

    def animation(self):
	if self.width < self.widthMax:
	    self.width += 100
	    self.text.setGeometry((self.d['xres']-self.width)//2, 100, self.width, self.d['yres']-200)
	else:
	    self.anim.stop()
	    self.ok.show()
	    self.text.setText(self.page)

    def closeEvent(self, event):
	self.stimer.stop()
	self.disconnect(self.stimer, SIGNAL("timeout()"), self.accept)
	event.accept()

    def powerFailure(self):
	#self.d['ping'].repeatPowerSignal()
	self.accept()

    def enterEvent(self, event):
	self.stimer.start()
	self.anim.start()
	event.accept()

class helpBox(QDialog):
    def __init__(self, page, d):
        QDialog.__init__(self)
        self.d = d
        self.lang = d['lang']
	self.l=d['l']

	self.lnk = page
	self.helptext = ''

        self.setObjectName("helpBox")
        self.width=0
        self.timeout = 30

        self.stimer = QTimer()
        self.stimer.setInterval(int(d['helpTimeout'])*1000)
        self.connect(self.stimer, SIGNAL("timeout()"), self.accept)
        
        self.anim = QTimer()
        self.anim.setInterval(30)
        self.connect(self.anim, SIGNAL("timeout()"), self.animation)
        
	self.setStyleSheet('* { background-color: transparent;}')
	drawBackground(self,d)

        self.text=QLabel(self)
	self.text.setStyleSheet('background-color: #FFFFFF; border: 10px solid #ababab; border-radius: 20px; color: #333333; padding-left: 20px; padding-right: 20px; padding-top: 20px;')
        #self.text.setGeometry((d['xres']-self.width)//2, 100, self.width, d['yres']-200)
        self.text.setWordWrap(True)
        self.text.setAlignment(Qt.AlignLeft)
        self.connect(self.text, SIGNAL("linkActivated(QString)"), self.link)

        self.ok=QPushButton(d['l']['close'][d['lang']],self)
        self.ok.setStyleSheet('background-color: #EEEEEE; border: 10px solid #ababab; border-radius: 20px; color: #222222;')
        self.ok.setGeometry((d['xres']-200)//2, d['yres']-90,200,70)
        self.connect(self.ok, SIGNAL("clicked()"), self, SLOT("accept()"))
        self.ok.setFocusPolicy(Qt.NoFocus)
        self.ok.hide()
	
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.powerFailure)
        self.setAutoFillBackground(False)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        #self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

    def link(self,lnk):
	self.helptext = self.getText(lnk)
	self.lnk = lnk
	self.stimer.start(self.timeout*1000)
	#print lnk
	self.width=0
	self.ok.hide()
	self.text.setText('')
	self.anim.start()
	

    def getText(self,page):
	helptext = self.helptext
	xml = open('help.xml','r').read()
	helpfile = minidom.parseString(xml).getElementsByTagName('help')[0]
	doc = helpfile.getElementsByTagName(page)
	if len(doc)>0: 
	    attr = {}
	    for (name,value) in doc[0].attributes.items():
	        attr[name] = value
	    if 'width' in attr.keys(): self.widthMax=int(attr['width'])
	    else: self.widthMax = 900
	    if 'height' in attr.keys(): self.heightMax=int(attr['height'])
	    else: self.heightMax=700
	    if 'timeout' in attr.keys(): self.timeout=int(attr['timeout'])
	    else: self.timeout=30

	    
	    langpage = doc[0].getElementsByTagName(self.lang)
	    if len(langpage)>0:
		langpage = langpage[0].getElementsByTagName('html')
		if len(langpage)>0:
		    helptext = langpage[0].toxml()
    
	return helptext


    def animation(self):
	if self.width < self.widthMax:
	    self.width += 100
	    self.text.setGeometry((self.d['xres']-self.width)//2, (self.d['yres']-self.heightMax-70)//2, self.width, self.heightMax)
	    self.ok.setGeometry((self.d['xres']+self.width)//2-200, ((self.d['yres']-self.heightMax-65)//2)+self.heightMax,200,70)
	else:
	    self.anim.stop()
	    self.ok.show()
	    self.text.setText(self.helptext)

    def closeEvent(self, event):
	self.stimer.stop()
	self.disconnect(self.stimer, SIGNAL("timeout()"), self.accept)
	event.accept()

    def enterEvent(self, event):
	self.link(self.lnk)
	event.accept()

    def powerFailure(self):
	self.d['powerFailure'] = False
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.powerFailure)
	self.d['ping'].repeatPowerSignal()
	self.accept()
	

class prices(QDialog):  #------------------- NOT USED MORE
    def __init__(self,d):
        QDialog.__init__(self)
        l=d['l']
        self.d=d
	self.l=d['l']
	self.lang=d['lang']

	self.timeoutNew = 3		# 5 second for message
	
        self.stimer = QTimer()
        self.newTime()
        self.stimer.setInterval(1000)
        self.connect(self.stimer, SIGNAL("timeout()"), self.time)
        self.stimer.start()
    
	self.setStyleSheet('* { background-color: transparent;}')
	drawBackground(self,d)

        label=QLabel(u"<h3>Ксерокопирование: <br>односторонняя - 0.25 грн <br>двусторонняя - 0.50 грн</h3>",self)
        label.setStyleSheet('background-color: #FFFFFF; border: 10px solid #ababab; border-radius: 20px; color: #2cd800;')
        label.setGeometry(10,200,d['xres']-20, 200)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Helvetica", 25, 75))
        
        yes=QPushButton(l['close'][d['lang']],self)
        yes.setGeometry((d['xres']-200)//2,d['yres']-200,200,100)
        self.connect(yes, SIGNAL("clicked()"), self, SLOT("accept()"))
        yes.setStyleSheet('background-color: #EEEEEE; border: 10px solid #ababab; border-radius: 20px; color: #2cd800;')
        yes.setDefault(True)
        
	#self.setStyleSheet("background-color: white; border-width: 0px; border: none; color: #333333;")
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

    def time(self):
        if self.timeout>0:
	    self.timeout-=1
	else:
	    self.stimer.stop()
	    self.disconnect(self.stimer, SIGNAL("timeout()"), self.time)
	    self.accept()

    def newTime(self):
	self.timeout=self.timeoutNew



class notAccessible(QDialog):
    def __init__(self, d):
        QDialog.__init__(self)
        self.d=d
	self.l=d['l']
	self.lang=d['lang']

        self.stimer = QTimer()
        self.stimer.setInterval(5000)
        self.connect(self.stimer, SIGNAL("timeout()"), self.accept)
        self.stimer.start()

	self.setStyleSheet('* { background-color: transparent;}')
	drawBackground(self,d)

	font = QFont()
        font.setPointSize(24)
        font.setWeight(50)
        font.setBold(False)

	self.label=QLabel(self.l['service_unavailable'][self.lang], self)
	self.label.setObjectName('scanfinishlabel')
	stylesheet='background-image: url("img/scan/finish_scan.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.label.setStyleSheet(stylesheet)
	self.label.setFont(font)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,d['xres']-480,450))
	self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
	self.label.setVisible(True)

	self.b_close=QPushButton(d['l']['close'][d['lang']],self)
	self.b_close.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_close.setFont(font)
	self.b_close.setGeometry(QRect((d['xres']-300)//2, 550, 300, 100))
	self.connect(self.b_close, SIGNAL("clicked()"), self.accept)
	self.b_close.setFocusPolicy(Qt.NoFocus)
	self.b_close.setVisible(True)

        self.setAutoFillBackground(False)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

    def closeEvent(self, event):
	self.stimer.stop()
	self.disconnect(self.stimer, SIGNAL("timeout()"), self.accept)
	event.accept()


class flashFailW(QDialog):
    def __init__(self,d):
        QDialog.__init__(self)
        l=d['l']
        self.d=d
	self.l=d['l']
	self.lang=d['lang']

	self.setStyleSheet('* { background-color: transparent;}')
	drawBackground(self,d)

	self.timeoutNew = 5		# 5 second for message
	
        self.stimer = QTimer()
        self.newTime()
        self.stimer.setInterval(1000)
        self.connect(self.stimer, SIGNAL("timeout()"), self.time)
        self.stimer.start()
    
	font = QFont()
        font.setPointSize(24)
        font.setWeight(50)
        font.setBold(False)

	self.label=QLabel(self.l['flash_not_writable'][self.lang], self)
	self.label.setObjectName('scanfinishlabel')
	stylesheet='background-image: url("img/scan/finish_scan.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.label.setStyleSheet(stylesheet)
	self.label.setFont(font)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,d['xres']-480,450))
	self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
	self.label.setVisible(True)

	self.b_close=QPushButton(d['l']['close'][d['lang']],self)
	self.b_close.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_close.setFont(font)
	self.b_close.setGeometry(QRect((d['xres']-300)//2, 550, 300, 100))
	self.connect(self.b_close, SIGNAL("clicked()"), self.accept)
	self.b_close.setFocusPolicy(Qt.NoFocus)
	self.b_close.setVisible(True)
        
        self.setAutoFillBackground(True)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

    def time(self):
        if self.timeout>0:
	    self.timeout-=1
	else:
	    self.stimer.stop()
	    self.disconnect(self.stimer, SIGNAL("timeout()"), self.time)
	    self.accept()

    def newTime(self):
	self.timeout=self.timeoutNew


class flashFailSpace(QDialog):
    def __init__(self,d):
        QDialog.__init__(self)
        l=d['l']
        self.d=d
	self.l=d['l']
	self.lang=d['lang']

	self.setStyleSheet('* { background-color: transparent;}')
	drawBackground(self,d)

	self.timeoutNew = 5		# 5 second for message
	
        self.stimer = QTimer()
        self.newTime()
        self.stimer.setInterval(1000)
        self.connect(self.stimer, SIGNAL("timeout()"), self.time)
        self.stimer.start()
    
	font = QFont()
        font.setPointSize(24)
        font.setWeight(50)
        font.setBold(False)

	self.label=QLabel(l['scan_nofreespace'][d['lang']], self)
	self.label.setObjectName('scanfinishlabel')
	stylesheet='background-image: url("img/scan/finish_scan.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.label.setStyleSheet(stylesheet)
	self.label.setFont(font)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,d['xres']-480,450))
	self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
	self.label.setVisible(True)

	self.b_close=QPushButton(d['l']['close'][d['lang']],self)
	self.b_close.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_close.setFont(font)
	self.b_close.setGeometry(QRect((d['xres']-300)//2, 550, 300, 100))
	self.connect(self.b_close, SIGNAL("clicked()"), self.accept)
	self.b_close.setFocusPolicy(Qt.NoFocus)
	self.b_close.setVisible(True)
        
        self.setAutoFillBackground(False)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()


    def time(self):
        if self.timeout>0:
	    self.timeout-=1
	else:
	    self.stimer.stop()
	    self.disconnect(self.stimer, SIGNAL("timeout()"), self.time)
	    self.accept()

    def newTime(self):
	self.timeout=self.timeoutNew
        


class flashFail(QDialog):
    def __init__(self,d):
        QDialog.__init__(self)
        l=d['l']
        self.d=d
	self.l=d['l']
	self.lang=d['lang']

	self.setStyleSheet('* { background-color: transparent;}')
	drawBackground(self,d)

	self.timeoutNew = 5		# 5 second for message
	
        self.stimer = QTimer()
        self.newTime()
        self.stimer.setInterval(1000)
        self.connect(self.stimer, SIGNAL("timeout()"), self.time)
        self.stimer.start()
    
	font = QFont()
        font.setPointSize(24)
        font.setWeight(50)
        font.setBold(False)

	self.label=QLabel(self.l['flash_not_inserted'][self.lang], self)
	self.label.setObjectName('scanfinishlabel')
	stylesheet='background-image: url("img/scan/finish_scan.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.label.setStyleSheet(stylesheet)
	self.label.setFont(font)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,d['xres']-480,450))
	self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
	self.label.setVisible(True)

	self.b_close=QPushButton(d['l']['close'][d['lang']],self)
	self.b_close.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_close.setFont(font)
	self.b_close.setGeometry(QRect((d['xres']-300)//2, 550, 300, 100))
	self.connect(self.b_close, SIGNAL("clicked()"), self.accept)
	self.b_close.setFocusPolicy(Qt.NoFocus)
	self.b_close.setVisible(True)
        
        self.setAutoFillBackground(False)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()


    def time(self):
        if self.timeout>0:
	    self.timeout-=1
	else:
	    self.stimer.stop()
	    self.disconnect(self.stimer, SIGNAL("timeout()"), self.time)
	    self.reject()

    def newTime(self):
	self.timeout=self.timeoutNew
        

class ChangeNet(QDialog):
    def __init__(self,d):
        QDialog.__init__(self)
        l=d['l']
        self.d=d
	self.l=d['l']
	self.lang=d['lang']


	self.timeoutNew = 5		# 5 second for message
	
        self.stimer = QTimer()
        self.newTime()
        self.stimer.setInterval(1000)
        self.connect(self.stimer, SIGNAL("timeout()"), self.time)
        self.stimer.start()
        
        self.setStyleSheet('* { background-color: transparent;}')
        drawBackground(self,d)
    
	font = QFont()
        font.setPointSize(24)
        font.setWeight(50)
        font.setBold(False)

	self.label=QLabel(u'\n\n\nSorry, but We can\'t give you change... \n You can charge your mobile phone', self)
	self.label.setObjectName('scanfinishlabel')
	stylesheet='background-image: url("img/scan/finish_scan.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.label.setStyleSheet(stylesheet)
	self.label.setFont(font)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,d['xres']-480,450))
	self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
	self.label.setVisible(True)

	self.b_close=QPushButton(d['l']['close'][d['lang']],self)
	self.b_close.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_close.setFont(font)
	self.b_close.setGeometry(QRect((d['xres']-300)//2, 550, 300, 100))
	self.connect(self.b_close, SIGNAL("clicked()"), self.accept)
	self.b_close.setFocusPolicy(Qt.NoFocus)
	self.b_close.setVisible(Truee)
        
        self.setAutoFillBackground(False)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()


    def time(self):
        if self.timeout>0:
	    self.timeout-=1
	else:
	    self.stimer.stop()
	    self.disconnect(self.stimer, SIGNAL("timeout()"), self.time)
	    self.reject()

    def newTime(self):
	self.timeout=self.timeoutNew


class myTextEdit(QTextEdit):
    def key(self, keyEvent):
	self.keyPressEvent(keyEvent)
    def mousePressEvent(self,event):
	self.emit(SIGNAL("stateChanged(bool)"), True)
	#event.accept()
    def focusInEvent(self,event):
	self.setStyleSheet('background-color: #DDFFFF; color: #222222;')
	QTextEdit.focusInEvent(self,event)
	#event.accept()
    def focusOutEvent(self,event):
	self.setStyleSheet('background-color: transparent; color: #777777;')
	QTextEdit.focusOutEvent(self,event)
	#event.accept()


class myPhoneEdit(QLabel):
    def __init__(self,parent):
	QLabel.__init__(self)
	self.setParent(parent)
	self.activeState = False
	self.cursor = -1
	self.maxDigits = 9
	self.empty = '*'
	self.number = str('*' * self.maxDigits)
	self.setActive(self.activeState)
	self.updateNumber()
	self.show()
	
    def updateNumber(self):
	text = '+38(0'+self.number[0:2]+')'+self.number[2:]
	self.setText(text)

    def toPlainText(self):
	return self.text()

    def key(self, keyEvent):
	n=keyEvent.text()
	key=keyEvent.key()
	if n in ['0','1','2','3','4','5','6','7','8','9','0']:
	    if self.cursor < self.maxDigits-1:
		self.cursor+=1
		self.number = self.number[:self.cursor]+n+self.number[self.cursor+1:]
		self.updateNumber()
		if self.cursor == self.maxDigits-1:
		    self.setActive(False)
	    else:                                       
		self.setActive(False)
        elif key == Qt.Key_Backspace and self.cursor > -1:
	    #self.number[self.cursor]=self.empty
	    self.number = self.number[:self.cursor]+self.empty+self.number[self.cursor+1:]
	    self.cursor -= 1
	    if self.cursor < self.maxDigits-1:
		self.setActive(True)
	    self.updateNumber()

    def mousePressEvent(self,event):
	self.setActive(True)
	event.accept()

    def setActive(self,state):
	self.activeState = state
	self.emit(SIGNAL("stateChanged(bool)"), state)
	if state == True:
	    if self.cursor < self.maxDigits-1:
		self.setStyleSheet('background-color: #DDFFFF; color: red; border: solid; border-width: 3px;')
	    else:
		self.setStyleSheet('background-color: #DDFFFF; color: green; border: solid; border-width: 3px;')
        else:
	    if self.cursor < self.maxDigits-1:
		self.setStyleSheet('background-color: white; color: red; border: none;')
	    else:
		self.setStyleSheet('background-color: white; color: green; border: none;')
	
    def isActive(self):
	return self.activeState

    def isComplete(self):
	return self.cursor == self.maxDigits-1

#name, (en,ru,ukr), (en,ru,ukr)+shift, button_code, button_width
buttons = [
[0,'alpha','@@@','@@@',0,10],
[1,'num1','111','!!!',0,10],
[2,'num2','222','@""',0,10],
[3,'num3','333',"""###""",0,10],
[4,'num4','444','$;;',0,10],
[5,'num5','555','%%%',0,10],
[6,'num6','666','^::',0,10],
[7,'num7','777','???',0,10],
[8,'num8','888','***',0,10],
[9,'num9','999','(((',0,10],
[10,'num0','000',')))',0,10],
[11,'alpha-','---','___',0,10],
[12,'alpha+','+++','===',0,10],
[13,'bs',['<- BackSpase','<- BackSpase','<- BackSpase'],['<- BackSpase','<- BackSpase','<- BackSpase'],0x01000003,25],
[14,'tab',['Tab','Tab','Tab'],['Tab','Tab','Tab'],0x01000001,15],
[15,'alphaQ',u'qйй',u'QЙЙ',0,10],
[16,'alphaW',u'wцц',u'WЦЦ',0,10],
[17,'alphaE',u'eуу',u'EУУ',0,10],
[18,'alphaR',u'rкк',u'RКК',0,10],
[19,'alphaT',u'tее',u'TЕЕ',0,10],
[20,'alphaY',u'yнн',u'YНН',0,10],
[21,'alphaU',u'uгг',u'UГГ',0,10],
[22,'alphaI',u'iшш',u'IШШ',0,10],
[23,'alphaO',u'oщщ',u'OЩЩ',0,10],
[24,'alphaP',u'pзз',u'PЗЗ',0,10],
[25,'alpha2',u'[хх',u'[ХХ',0,10],
[26,'alpha3',u']ъi',u']ЪI',0,10],
[27,'alpha4','|||','|||',0,20],
[28,'caps',['Caps Lock','Caps Lock','Caps Lock'],['Caps Lock','Caps Lock','Caps Lock'],0,18],
[29,'alphaA',u'aфф',u'AФФ',0,10],
[30,'alphaS',u'sыi',u'SЫI',0,10],
[31,'alphaD',u'dвв',u'DВВ',0,10],
[32,'alphaF',u'fаа',u'FАА',0,10],
[33,'alphaG',u'gпп',u'GПП',0,10],
[34,'alphaH',u'hрр',u'HРР',0,10],
[35,'alphaJ',u'jоо',u'JОО',0,10],
[36,'alphaK',u'kлл',u'KЛЛ',0,10],
[37,'alphaL',u'lдд',u'LДД',0,10],
[38,'alpha5',u';жж',u':ЖЖ',0,10],
[39,'alpha6',u'\'эе',u'\"ЭЕ',0,10],
[40,'enter',['Enter','Enter','Enter'],['Enter','Enter','Enter'],0,28],
[41,'shift',['Shift','Shift','Shift'],['Shift','Shift','Shift'],0,23],
[42,'alphaZ',u'zяя',u'ZЯЯ',0,10],
[43,'alphaX',u'xчч',u'XЧЧ',0,10],
[44,'alphaC',u'cсс',u'CСС',0,10],
[45,'alphaV',u'vмм',u'VММ',0,10],
[46,'alphaB',u'bии',u'BИИ',0,10],
[47,'alphaN',u'nтт',u'NТТ',0,10],
[48,'alphaM',u'mьь',u'MЬЬ',0,10],
[49,'alpha7',u',бб',u'<ББ',0,10],
[50,'alpha8',u'.юю',u'>ЮЮ',0,10],
[51,'alpha9',u'/..',u'?,,',0,10],
[52,'shift',['Shift','Shift','Shift'],['Shift','Shift','Shift'],0,34],
[53,'lang',[u'Русский',u'Украiнська',u'English'],[u'Русский',u'Украiнська',u'English'],0,28],
[54,'space',['Space','Space','Space'],['Space','Space','Space'],0,105],
[55,'lang',[u'Русский',u'Украiнська',u'English'],[u'Русский',u'Украiнська',u'English'],0,30]
]

ls = {'en':0, 'ru':1, 'ua':2}

lang = 'ru'

class mybutton(QPushButton):
    def __init__(self,buttonTYPE,buttonKEY,buttonSYMBOL):
        QPushButton.__init__(self)
        self.buttonTYPE=buttonTYPE
        self.buttonKEY=buttonKEY
        self.buttonSYMBOL=buttonSYMBOL
        
    def TYPE(self):
	return self.buttonTYPE

    def KEY(self):
	return self.buttonKEY

    def SYMBOL(self):
	return self.buttonSYMBOL
	

class clickButton(QPushButton):
    def mousePressEvent(self,event):
	self.emit(SIGNAL("click(str)"), self.text())


class support(QDialog):
    def __init__(self,d):
	QDialog.__init__(self)
	global reason
	self.d=d
	self.l=d['l']
	self.lang=d['lang']

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
        self.connect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
        self.b_help.setFocusPolicy(Qt.NoFocus)

        self.b_main = QPushButton(self.top)
        self.b_main.setFont(font)
        self.b_main.setObjectName(_fromUtf8("b_main"))
        self.b_main.setGeometry(QRect(30, 15, 400, 90))
        self.b_main.setText(self.l['menu'][self.lang])
        self.connect(self.b_main,  SIGNAL("clicked()"),  self.close)
        self.b_main.setFocusPolicy(Qt.NoFocus)

	font = QFont()
        font.setPointSize(22)
        font.setWeight(50)
        font.setBold(False)

	self.label=QLabel(self.l['support_select'][self.lang], self)
	self.label.setObjectName('support_select')
	stylesheet='background-color: transparent; border-width: 0px; border: none; color: #333333;'
	self.label.setStyleSheet(stylesheet)
	self.label.setWordWrap(True)
	self.label.setFont(font)
	self.label.setGeometry(QRect(200,150,d['xres']-400,100))
	self.label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
	self.label.setVisible(False)

	self.d1=QPushButton(self.l['offers'][self.lang],self)
	self.d1.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.d1.setFont(font)
	self.d1.setGeometry(QRect((d['xres']-600)//2, 400, 600, 100))
	self.connect(self.d1, SIGNAL("clicked()"), self.d1click)
	self.d1.setFocusPolicy(Qt.NoFocus)
	self.d1.setVisible(False)

	self.d3=QPushButton(self.l['complaints'][self.lang],self)
	self.d3.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.d3.setFont(font)
	self.d3.setGeometry(QRect((d['xres']-600)//2, 550, 600, 100))
        self.connect(self.d3,  SIGNAL("clicked()"),  self.d3click)
	self.d3.setFocusPolicy(Qt.NoFocus)
	self.d3.setVisible(False)

	style2='background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;'
	
	self.zmas={}
	self.zbuttons = {
	0:self.l['quality_problems'][self.lang],
	1:self.l['change_problems'][self.lang],
	2:self.l['tarif_problems'][self.lang],
	3:self.l['xerox_problems'][self.lang],
	4:self.l['print_problems'][self.lang],
	5:self.l['scan_problems'][self.lang],
	6:self.l['other_problems'][self.lang],
	}
	for b in self.zbuttons.keys():
	    self.zmas[b]=clickButton(self.zbuttons[b],self)
	    self.zmas[b].setStyleSheet(style2)
	    self.zmas[b].setFont(font)
	    self.zmas[b].setGeometry(QRect((d['xres']-600)//2, 270+b*70, 600, 50))
	    self.connect(self.zmas[b],  SIGNAL("click(str)"),  self.zclick)
	    self.zmas[b].setFocusPolicy(Qt.NoFocus)
	    self.zmas[b].setVisible(False)

        self.b_back=QPushButton(self)
	self.b_back.setObjectName('scanbuttonback')
	stylesheet='background-image: url("img/scan/b_back_white.png"); background-color: transparent; border-width: 0px; border: none; color: blue;'
	self.b_back.setStyleSheet(stylesheet)
        self.b_back.setText(self.l['back'][self.lang])
        self.b_back.setFont(font)
        self.b_back.setGeometry(QRect(50, 850, 420, 170))
        self.connect(self.b_back,  SIGNAL("clicked()"),  self.back)
        self.b_back.setFocusPolicy(Qt.NoFocus)
        self.b_back.setVisible(False)

        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

	self.timer=QTimer()
	self.timer.setInterval(10000)
	self.showTimer = QTimer()
	self.showTimer.setInterval(500)
	#self.connect(self.showTimer, SIGNAL("timeout()"), self.showUI)
	#self.showTimer.start()
	self.showUI()

    def showUI(self):
	self.showTimer.stop()
	self.label.show()
	self.d3.show()
	self.d1.show()
	self.connect(self.timer, SIGNAL("timeout()"), self.close)
	self.timer.start()

    def d1click(self):
	global reason
	self.timer.stop()
	reason=self.l['wishes'][self.lang].encode('utf-8')
	w=email(self.d,reason).exec_()
	self.close()

    def d3click(self):
	self.timer.stop()
	self.d1.hide()
	self.d3.hide()
	self.b_back.show()
	self.label.setText(self.l['problem_select'][self.lang])
	for b in self.zbuttons.keys():
	    self.zmas[b].setVisible(True)
	self.timer.start()

    def back(self):
	self.timer.stop()
	self.d1.show()
	self.d3.show()
	self.b_back.hide()
	self.label.setText(self.l['support_select'][self.lang])
	for b in self.zbuttons.keys():
	    self.zmas[b].setVisible(False)
	self.timer.start()

    def zclick(self,name):
    	global reason
    	self.timer.stop()
	reason=unicode(name).encode('utf-8')
	if email(self.d,reason).exec_():
	    self.accept()
	else:
	    self.reject()

    def helpbox(self):
	self.timer.stop()
        hb=helpBox('main', self.d)
        hb.exec_()
        self.timer.start()



class email(QDialog):
    def __init__(self,d,page):
        QDialog.__init__(self)
        global buttons
        global lang
        l=d['l']
        lang=d['lang']
        self.lang = lang
        self.l = l
        self.d = d

	self.timeoutNew = 60		# 5 second for message
	
        self.stimer = QTimer()
        self.newTime()
        self.stimer.setInterval(1000)
        self.connect(self.stimer, SIGNAL("timeout()"), self.time)
        self.stimer.start()
    
        self.label=QLabel(self.l['enter_phone'][self.lang],self)
        stylesheet='background-color: transparent; border-width: 0px; border: none; color: red;'
	self.label.setStyleSheet(stylesheet)
        self.label.setWordWrap(True)
        self.label.setGeometry(70,150,d['xres']-140, 100)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Helvetica", 20, 75))

        self.labelBackground=QLabel(self.l['press_to_enter'][self.lang],self)
        stylesheet='background-color: transparent; border-width: 0px; border: none; color: #DDDDDD;'
	self.labelBackground.setStyleSheet(stylesheet)
        self.labelBackground.setWordWrap(True)
        self.labelBackground.setGeometry(QRect(320, 450, d['xres']-400, 100))
        self.labelBackground.setAlignment(Qt.AlignCenter)
        self.labelBackground.setFont(QFont("Helvetica", 32, 75))


        label1=QLabel(self.l['type_message'][self.lang],self)
        stylesheet='background-color: transparent; border-width: 0px; border: none; color: #333333;'
	label1.setStyleSheet(stylesheet)
        label1.setWordWrap(True)
        label1.setGeometry(70,250,d['xres']-140, 50)
        label1.setAlignment(Qt.AlignCenter)
        label1.setFont(QFont("Helvetica", 16, 75))
        
        font = QFont()
        font.setPointSize(22)
        font.setWeight(75)
        font.setBold(False)

        self.top = QWidget(self)
        self.top.setAutoFillBackground(True)
        self.top.setObjectName(_fromUtf8("top"))
        self.top.setGeometry(QRect(0, 0, d['xres']+1, 120))

        self.b_main = QPushButton(self.top)
        self.b_main.setFont(font)
        self.b_main.setObjectName(_fromUtf8("b_main"))
        self.b_main.setGeometry(QRect(30, 15, 400, 90))
        self.b_main.setText(self.l['menu'][lang])
        self.b_main.setFocusPolicy(Qt.NoFocus)

        self.b_next = QPushButton(self.top)
        self.b_next.setFont(font)
        self.b_next.setObjectName(_fromUtf8("b_next"))
        self.b_next.setText(self.l['send'][lang])
        self.b_next.setGeometry(QRect((d['xres']-320), 15, 300, 95))
        self.b_next.setFocusPolicy(Qt.NoFocus)
        self.b_next.setEnabled(False)
        
        
        w=70	#button width
        h=70    #button height
	x0=60   #start x
	y0=620	#start y
	x=x0    #current x
	y=y0	#current y
	
	self.CAPS = 0
	self.SHIFT = 0

        self.bgroup=QButtonGroup(self)
	self.but={}
        for b in buttons:
            button_id = b[0]
	    name = b[1]
	    width = b[5]*w//10
	    height= h
	    bukva = b[2+self.CAPS][ls[lang]]
	    
	    if x > self.d['xres']-width-x0:
		y+=h+5
		x=x0

	    self.but[button_id]=QPushButton(parent=self)
	    self.but[button_id].setFocusPolicy(Qt.NoFocus)
	    self.but[button_id].setObjectName(name)
	    self.but[button_id].setGeometry(QRect(x, y, width, height))
	    self.but[button_id].setFont(QFont("Helvetica", 16, 75))
	    self.but[button_id].setText(QString(bukva))
            self.bgroup.addButton(self.but[button_id],button_id)

	    if x>self.d['xres']-w-x0:
		y+=h+5
		x=x0
	    else:
		x+=width+5


        self.message = myTextEdit(self)
        self.message.setGeometry(QRect(300, 400, d['xres']-370, 200))
        self.message.setAlignment(Qt.AlignLeft)
        self.message.setFont(QFont("Helvetica", 22, 75))
        self.message.setCursorWidth(5)
        self.message.clearFocus()
        self.message.setStyleSheet('background-color: transparent; color: #777777;')
        self.connect(self.message, SIGNAL("stateChanged(bool)"), self.changeMessageFocus)

        labelmessage=QLabel(self.l['comment'][self.lang],self)
        stylesheet='background-color: transparent; border-width: 0px; border: none; color: #333333;'
	labelmessage.setStyleSheet(stylesheet)
        labelmessage.setWordWrap(True)
        labelmessage.setGeometry(60, 400, 250, 50)
        labelmessage.setAlignment(Qt.AlignLeft)
        labelmessage.setFont(QFont("Helvetica", 17, 75))

        self.phone = myPhoneEdit(self)
        self.phone.setGeometry(QRect(300, 330, 300, 50))
        self.phone.setAlignment(Qt.AlignLeft)
        self.phone.setFont(QFont("Helvetica", 22, 75))
        self.connect(self.phone, SIGNAL("stateChanged(bool)"), self.changePhoneFocus)
        self.phone.setActive(True)
        
        self.phone_bs = QPushButton('<-',self)
        self.phone_bs.setGeometry(QRect(610, 330, 50, 50))
        self.phone_bs.setFont(QFont("Helvetica", 22, 75))
        self.phone_bs.setFocusPolicy(Qt.NoFocus)
        self.connect(self.phone_bs, SIGNAL("clicked()"), self.phone_bs_clicked)
        

        labelphone=QLabel(self.l['your_phone'][self.lang],self)
        stylesheet='background-color: transparent; border-width: 0px; border: none; color: #333333;'
	labelphone.setStyleSheet(stylesheet)
        labelphone.setWordWrap(True)
        labelphone.setGeometry(60, 330, 250, 50)
        labelphone.setAlignment(Qt.AlignLeft)
        labelphone.setFont(QFont("Helvetica", 19, 75))

        self.connect(self.bgroup, SIGNAL("buttonClicked(int)"), self.char)
        #self.connect(self.but['erase'], SIGNAL("clicked()"), self.bs)
        self.connect(self.b_main, SIGNAL("clicked()"), self.reject)
        self.connect(self.b_next, SIGNAL("clicked()"), self.send)
        
        #self.but['erase'].setEnabled(False)
        self.updateKeyboard()
        self.d['log'].log("SEND EMAIL: displayed")

        self.setAutoFillBackground(False)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

    def send(self):
	global reason
	mailserver = 'mail.copyprime.com.ua'
	sender = 'info@copyprime.com.ua'
	pwd = 'VDSCP2011'
	receiver = ['support@copyprime.com.ua']
	#receiver = ['stang@ukr.net']
	subj = 'CopyPrime Support (Device N'+str(self.d['device'])+')'
	txt =  unicode(reason, 'utf-8').encode('cp1251') + '\n'.encode('cp1251') + unicode(self.phone.toPlainText()).encode('cp1251') + '\n'.encode('cp1251') + unicode(self.message.toPlainText()).encode('cp1251')
	#print txt
	#txt = txt.encode('cp1251')
	attachments = []

	self.d['email_message']={'sender':sender, 
				'receiver':receiver, 
				'subj':subj, 
				'txt':txt, 
				'attach':attachments, 
				'mailserver':mailserver, 
				'sender':sender, 
				'pwd':pwd}


	self.d['log'].log("MESSAGE TO SUPPORT: "+reason+'\nPhone:'+unicode(self.phone.toPlainText()).encode('utf-8')+'\nComment:'+unicode(self.message.toPlainText()).encode('utf-8'))
	
	message(self.d,self.l['message_sent'][self.lang],'OK',5).exec_()
	self.accept()


    def helpbox(self):
        self.stimer.stop()
        self.disconnect(self.stimer, SIGNAL("timeout()"), self.time)
        hb=HelpBox(self.l["help_xerox"][lang], self.d)
        hb.exec_()
        self.newTime()
        self.connect(self.stimer, SIGNAL("timeout()"), self.time)
        self.stimer.start()


    def time(self):
        if self.timeout>0:
	    self.timeout-=1
	else:
	    self.stimer.stop()
	    self.disconnect(self.stimer, SIGNAL("timeout()"), self.time)
	    #if 'support' in self.d.keys() and self.d['supprt']:
		#self.d['supprt'].close()
	    self.reject()

    def newTime(self):
	self.timeout=self.timeoutNew

    def phone_bs_clicked(self):
	self.phone.setActive(True)
	self.message.setFocusPolicy(Qt.NoFocus)
	self.message.clearFocus()
	self.phone.setFocusPolicy(Qt.ClickFocus)
	self.phone.setFocus()
	self.updateKeyboard()
	self.label.show()

	self.char(13)

    def updateKeyboard(self):
	global buttons
	global ls
	
        if self.phone.isActive():
	    for b in buttons:
        	button_id = b[0]
		bukva = b[2+(False)][ls[lang]]
		buttonName=b[1]
		self.but[button_id].setText(QString(bukva))
		if 'num' in buttonName or 'bs' in buttonName:
		    self.but[button_id].setStyleSheet('background-color: #DDDDFF; color: blue;')
		else:
		    self.but[button_id].setStyleSheet('')
		    self.but[button_id].setEnabled(False)
        else:
	    for b in buttons:
        	button_id = b[0]
		bukva = b[2+(self.CAPS or self.SHIFT)][ls[lang]]
		self.but[button_id].setText(QString(bukva))
		self.but[button_id].setStyleSheet('')
		self.but[button_id].setEnabled(True)
		if ('shift' in b[1]):
		    if self.SHIFT == 1:
			self.but[button_id].setText('SHIFT')
		    else:
			self.but[button_id].setText('Shift')
		if ('caps' in b[1]):
		    if self.CAPS == 1:
			self.but[button_id].setText('CAPS')
		    else:
			self.but[button_id].setText('Caps')


    def changePhoneFocus(self, state):
	if state:
	    self.message.setFocusPolicy(Qt.NoFocus)
	    self.message.clearFocus()
	else:
	    self.message.setFocusPolicy(Qt.ClickFocus)
	    self.message.setFocus()
	self.updateKeyboard()

	if self.phone.isComplete():
	    self.label.hide()
	else:
	    self.label.show()

	    
    def changeMessageFocus(self, state):
	if state:
	    self.phone.setActive(False)
	    self.message.setFocusPolicy(Qt.ClickFocus)
	    self.message.setFocus()
	else:
	    self.message.setFocusPolicy(Qt.NoFocus)



    def char(self,button_id):
	global buttons
	global lang
	global ls
	
	update_flag=0
	
	data=buttons[button_id]
	
	if self.SHIFT == 1 and ('shift' not
	 in data[1]):
	    self.SHIFT = 0
	    update_flag=1

	if self.phone.isActive():
	    receiver = self.phone
	else:
	    self.message.setFocus()
	    receiver = self.message
	

	if ('alpha' in data[1]) and (receiver == self.message):
	    keyEvent = QKeyEvent(QEvent.KeyPress, 0, Qt.NoModifier, QString(self.but[button_id].text()) )
	    receiver.key(keyEvent)
	elif ('num' in data[1]):
	    keyEvent = QKeyEvent(QEvent.KeyPress, 0, Qt.NoModifier, QString(self.but[button_id].text()) )
	    receiver.key(keyEvent)
	elif ('space' in data[1]) and (receiver == self.message):
	    keyEvent = QKeyEvent(QEvent.KeyPress, 0, Qt.NoModifier, QString(' ') )
	    receiver.key(keyEvent)
	elif ('enter' in data[1]) and (receiver == self.message):
	    keyEvent = QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier, QString('') )
	    receiver.key(keyEvent)
	elif ('bs' in data[1]):
	    keyEvent = QKeyEvent(QEvent.KeyPress, Qt.Key_Backspace, Qt.NoModifier, QString('') )
	    receiver.key(keyEvent)
	elif ('caps' in data[1]):
	    if self.CAPS == 1:
		self.CAPS = 0
	    else: 
		self.CAPS = 1
	    update_flag=1
	elif ('shift' in data[1]):
	    if self.SHIFT == 0:
		self.SHIFT = 1
	    else: 
		self.SHIFT = 0
	    update_flag=1

	elif ('lang' in data[1]):
	    if lang == 'ru':
		lang = 'ua'
	    elif lang == 'ua':
		lang = 'en'
	    elif lang == 'en':
		lang = 'ru'
	    update_flag=1
	
	if len(self.message.toPlainText())>5:
	    self.b_next.setEnabled(True)
	else:
	    self.b_next.setEnabled(False)

	if update_flag:
	    self.updateKeyboard()

	self.newTime()


class changeMessage(QDialog):
    def __init__(self,d):
	QDialog.__init__(self)
	self.d=d
	self.l=d['l']
	self.lang=d['lang']

	timeout = 3
        min5Summ = 200
        minSumm = 1000

	self.timer = QTimer()
	self.timer.setInterval(timeout*1000)
	self.connect(self.timer, SIGNAL("timeout()"), self.reject)

	self.showTimer = QTimer()
	self.showTimer.setInterval(500)
	self.connect(self.showTimer, SIGNAL("timeout()"), self.showUI)
	
	self.setStyleSheet('* { background-color: transparent;}')
	self.stylesheetBLUE='background-image: url("img/scan/finish_scan.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.stylesheetRED='background-image: url("img/mob/error_number.png"); background-color: transparent; border-width: 0px; border: none; color: white;'

        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        #self.showFullScreen()

        if (int(self.d['coinSumm']) < minSumm):
	    self.text=self.l['change_end'][self.lang]
	    self.styleSheet = self.stylesheetRED
	    self.construct()
	elif (int(self.d['coinC5']) * 5 < min5Summ):
	    self.text=self.l['change_ending'][self.lang]
	    self.styleSheet = self.stylesheetBLUE
	    self.construct()
	else:
	    self.resize(1,1)
	    self.timer.start(1)


    def construct(self):
	drawBackground(self, self.d)

	font = QFont()
        font.setPointSize(24)
        font.setWeight(50)
        font.setBold(False)

	self.label=QLabel(self)
	self.label.setObjectName('changeLabel')
	self.label.setFont(font)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,self.d['xres']-480,450))
	self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
	self.label.setVisible(False)
	self.label.setStyleSheet(self.styleSheet)
	self.label.setText(self.text)

	self.b_close=QPushButton('OK',self)
	self.b_close.setStyleSheet('background-color: #EEEEAA; border: 2px solid #ababab; border-radius: 10px; color: #333333;')
	self.b_close.setFont(font)
	self.b_close.setGeometry(QRect((self.d['xres']-300)//2, 550, 300, 100))
	self.connect(self.b_close, SIGNAL("clicked()"), self.accept)
	self.b_close.setFocusPolicy(Qt.NoFocus)
	self.b_close.setVisible(False)

	self.timer.start()
	self.showTimer.start()
    
    def showUI(self):
	self.showTimer.stop()
	self.label.show()
	self.b_close.show()

	
