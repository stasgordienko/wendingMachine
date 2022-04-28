# -*- coding: utf-8 -*-
from os.path import *
from os import listdir, popen, statvfs
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Scan_charge import _scan_charge
from datetime import datetime
import subprocess
from dialogs import *
import re

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class _scan(QWidget):

    def __init__(self,d):
        QWidget.__init__(self)
        self.setObjectName(_fromUtf8("_scan"))
        self.d=d
        self.l=d['l']
        self.lang=d['lang']
        
        font = QFont()
        font.setPointSize(22)
        font.setWeight(75)
        font.setBold(False)

        self.label = QLabel(self)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label.setGeometry(QRect((d['xres']-900)//2, 400, 900, 100))
        self.label.setText(self.l['scan_ins_please'][self.lang])
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setVisible(False)

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

        font = QFont()
        font.setPointSize(18)
        font.setWeight(75)
        font.setBold(True)
        self.l_cost = QLabel(self)
        self.l_cost.setFont(font)
        self.l_cost.setAlignment(Qt.AlignCenter)
        self.l_cost.setObjectName(_fromUtf8("l_cost"))
        self.l_cost.setGeometry(QRect((d['xres']-900)//2, 200, 900, 50))
        self.l_cost.setText(self.l['scan_ins_pagecost'][self.lang] % (float(d['scan_1cost'])/100))
        self.l_cost.setVisible(False)

        self.timeProgress = QProgressBar(self)
        self.timeProgress.setProperty(_fromUtf8("value"), 0)
        self.timeProgress.setObjectName(_fromUtf8("timeProgress"))
        self.timeProgress.setGeometry(QRect(1, d['yres']-10, d['xres'], 10))
        self.timeProgress.setTextVisible(False)

	changeMessage(self.d).exec_()

        self.stimer = QTimer()
        self.stimer.setInterval(500)

        self.connect(self.stimer, SIGNAL("timeout()"), self.timeUpdate)
        self.connect(self.b_main,  SIGNAL("clicked()"),  self.back)
        self.connect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)

        self.stimer.start()
      


    def timeUpdate(self):
        if ('insertedDeviceName' in self.d.keys()):
	    if self.flashMounted():
		self.stimer.stop()
		space = self.freespace(self.d['flash'])
		if space > 20 :             # check if freespace on flash-drive is more then 10 MegaBytes
		    if self.isWriteable():
        		self.d['scan_charge']=_scan_charge(self.d)
        		self.d['scan_charge'].showFullScreen()
        		self.d['log'].log("SCAN: flash-drive insert: OK. FreeSpace is %d MegaBytes, DRIVE: %s" % (space,self.d['insertedDeviceName']))
        		self.stimer.stop()
        		self.close()
		    else:
        		self.d['flashFailWrite']=flashFailWrite(self.d)
        		self.d['log'].log("SCAN: flash-drive insert: WRITE FAIL, DRIVE: %s" % (self.d['insertedDeviceName']))
        		self.close()
        	else:
        	    self.d['flashFailSpace']=flashFailSpace(self.d)
        	    self.d['log'].log("SCAN: flash-drive insert: NO FREESPACE (%d MegaBytes), DRIVE: %s" % (space,self.d['insertedDeviceName']))
        	    self.close()
	    else:
		#change picture to flashOK
		self.label.setStyleSheet("background-color: transparent; color: green;")
		self.label.setText(self.l['scan_inserted'][self.lang])
		self.label.setVisible(True)
		#self.l_cost.hide()

        else:
            #change picture to noFlash
            self.label.setText(self.l['scan_ins_please'][self.lang])
            self.label.setVisible(True)
            #self.l_cost.show()
            self.label.setStyleSheet("background-color: transparent; color: red;")
            val = self.timeProgress.value() + 2
            if val > 100:
                self.stimer.stop()
        	if flashFail(self.d).exec_():
		    self.timeProgress.setValue(0)
        	    self.stimer.start()
		else:
		    self.back()
	    else:
        	self.timeProgress.setValue(val)
    

    def isWriteable(self):    
	try:
	    filename = self.d['flash'] + '/testfile_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	    test = open(filename,'w')
	    test.write('testfile')
	    test.close()
	    print "file writed"
	except:
	    print "flash is not writable"
	    return False
	else:
	    subprocess.call(['rm',filename])
	    print "file deleted"
	    return True


    def flashMounted(self):
        if exists(self.d['flash']): # and exists(self.d['flash_dev']):
            names = listdir(self.d['flash'])
            if len(names)>0:
                return True
        else: 
            return False


    def freespace(self,p):
	"""
	Returns the number of free Megabytes on the drive that "p" is on
	"""
	s = statvfs(str(p))
	return (s.f_bsize * s.f_bavail)//(1024*1024)
	

    def back(self):
        self.stimer.stop()
        self.close()


    def helpbox(self):
        self.stimer.stop()
        hb=helpBox('scanflash', self.d)
        hb.exec_()
        self.stimer.start()
        
    def enterEvent(self,event):
	self.stimer.start()
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.back)
	event.accept()

    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.back)
	event.accept()

class _scan_select(QWidget):
    def __init__(self,d):
        QWidget.__init__(self)
        self.setObjectName(_fromUtf8("_scan_select"))
        self.d=d
        self.l=d['l']
        self.lang=d['lang']
        
        font = QFont()
        font.setPointSize(22)
        font.setWeight(75)
        font.setBold(False)

        self.label = QLabel(self)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label.setGeometry(QRect(0, 150, d['xres'], 50))
        self.label.setText(self.l['scan_select'][self.lang])
        self.label.setAlignment(Qt.AlignCenter)

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
        self.b_main.setText(self.l['menu'][self.lang])
        self.b_main.setFocusPolicy(Qt.NoFocus)

        self.b_next = QPushButton(self)
        self.b_next.setFont(font)
        self.b_next.setObjectName(_fromUtf8("b_next"))
        self.b_next.setText(self.l['next'][self.lang])
        self.b_next.setGeometry(QRect((d['xres']-350), d['yres']-150, 300, 95))
        self.b_next.setFocusPolicy(Qt.NoFocus)

        self.flash_choose = QRadioButton(self)
        font = QFont()
        font.setPointSize(28)
        self.flash_choose.setFont(font)
        self.flash_choose.setObjectName(_fromUtf8("flash_choose"))
        self.flash_choose.setText(self.l['flashdrive'][self.lang])
        self.flash_choose.setGeometry(QRect((d['xres']-900)//2, 225, 900, 100))
        self.flash_choose.setFocusPolicy(Qt.NoFocus)
        self.connect(self.flash_choose, SIGNAL("clicked()"), self.flash_clicked)

        self.email_choose = QRadioButton(self)
        font = QFont()
        font.setPointSize(28)
        self.email_choose.setFont(font)
        self.email_choose.setObjectName(_fromUtf8("email_choose"))
        self.email_choose.setText(self.l['emailsend'][self.lang])
        self.email_choose.setGeometry(QRect((d['xres']-900)//2, 325, 900, 100))
        self.email_choose.setFocusPolicy(Qt.NoFocus)
        self.connect(self.email_choose, SIGNAL("clicked()"), self.email_clicked)
        
        self.email = re.compile(r"[a-z0-9\-\.\_]{1,}[@]{1}([a-z0-9\-\_]{1,}[\.]{1}){1,}[a-z]{2,}")

        l=d['l']
        lang=d['lang']
        self.l = l
        self.d = d

	self.timeoutNew = 30		
	
        self.stimer = QTimer()
        self.newTime()
        self.stimer.setInterval(1000)
        self.connect(self.stimer, SIGNAL("timeout()"), self.time)
        self.stimer.start()
    
        w=70	#button width
        h=70    #button height
	x0=60   #start x
	y0=550	#start y
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
	    bukva = b[2+self.CAPS][0]
	    
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
        self.message.setGeometry(QRect(400, 400, d['xres']-470, 70))
        self.message.setAlignment(Qt.AlignLeft)
        self.message.setFont(QFont("Helvetica", 28, 75))
        self.message.setCursorWidth(5)
        self.message.clearFocus()
        self.message.setStyleSheet('background-color: transparent; color: #777777;')

        self.labelmessage=QLabel(self.l['address'][self.lang],self)
        stylesheet='background-color: transparent; border-width: 0px; border: none; color: #333333;'
	self.labelmessage.setStyleSheet(stylesheet)
        self.labelmessage.setWordWrap(True)
        self.labelmessage.setGeometry(270, 410, 120, 50)
        self.labelmessage.setAlignment(Qt.AlignLeft)
        self.labelmessage.setFont(QFont("Helvetica", 22, 75))

	self.connect(self.message, SIGNAL("stateChanged(bool)"), self.email_clicked)
        self.connect(self.bgroup, SIGNAL("buttonClicked(int)"), self.char)
        #self.connect(self.but['erase'], SIGNAL("clicked()"), self.bs)
        self.connect(self.b_main, SIGNAL("clicked()"), self.close)
        self.connect(self.b_next, SIGNAL("clicked()"), self.scan)
        self.connect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
        
        #self.but['erase'].setEnabled(False)
        self.d['log'].log("EMAIL KEYBOARD: displayed")

        self.setAutoFillBackground(False)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.flash_clicked()


    def flash_clicked(self):
	self.message.setVisible(False)
	self.labelmessage.setVisible(False)
	self.message.clearFocus()
	self.updateKeyboard()
	self.newTime()
	self.b_next.setEnabled(True)
	self.flash_choose.setChecked(True)
	
    def email_clicked(self):
	self.message.setVisible(True)
	self.labelmessage.setVisible(True)
    	self.message.setFocus()
    	self.email_choose.setChecked(True)
        self.updateKeyboard()
	self.newTime()
	if self.correct(self.message.toPlainText()):
	    self.b_next.setEnabled(True)
	else:
	    self.b_next.setEnabled(False)

    def scan(self):
	self.stimer.stop()
        if self.flash_choose.isChecked():
	    self.d['scan_type'] = 'flash'
	    self.d['scan_ins'] = _scan(self.d); self.d['scan_ins'].showFullScreen()
	else:
	    self.d['email'] = self.message.toPlainText()
	    self.d['scan_type'] = 'email'
	    self.d['scan_charge'] = _scan_charge(self.d); self.d['scan_charge'].showFullScreen()


    def enterEvent(self,event):
	self.newTime()
	self.connect(self.stimer, SIGNAL("timeout()"), self.time)
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.close)
	self.stimer.start()
	event.accept()

    def leaveEvent(self,event):
	self.newTime()
	self.disconnect(self.stimer, SIGNAL("timeout()"), self.time)
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.close)
	self.stimer.stop()
	event.accept()

    def updateKeyboard(self):
	global buttons
	for b in buttons:
	    button_id = b[0]
	    bukva = b[2][0]
	    if 'blank' not in b[1]:
		self.but[button_id].setText(QString(bukva))
		#self.but[button_id].setStyleSheet('')
		self.but[button_id].setEnabled(True)
		if self.email_choose.isChecked():
		    self.but[button_id].setVisible(True)
		else:
		    self.but[button_id].setVisible(False)
	    else:
		self.but[button_id].setVisible(False)
		

    def helpbox(self):
        self.stimer.stop()
        self.disconnect(self.stimer, SIGNAL("timeout()"), self.time)
        hb=helpBox('scan', self.d)
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
	    print "TIMEOUT!!!!"
	    self.close()

    def newTime(self):
	if self.flash_choose.isChecked():
	    self.timeout=self.timeoutNew
	else:
	    self.timeout=self.timeoutNew * 2


    def char(self,button_id):
	global buttons
	
	data=buttons[button_id]
	
	receiver = self.message

	if (('alpha' in data[1]) or ('num' in data[1])) and (len(self.message.toPlainText()) < 35):
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

	if self.correct(self.message.toPlainText()):
	    self.b_next.setEnabled(True)
	else:
	    self.b_next.setEnabled(False)

	self.newTime()


    def correct(self,text):
	if (len(self.message.toPlainText()) > 6) and (self.email.search(self.message.toPlainText())):
	    return 1
	else:
	    return 0
	

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
[14,'blank',['Tab','Tab','Tab'],['Tab','Tab','Tab'],0x01000001,15],
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
[27,'blank','|||','|||',0,20],
[28,'blank',['Caps Lock','Caps Lock','Caps Lock'],['Caps Lock','Caps Lock','Caps Lock'],0,18],
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
[40,'blank',['Enter','Enter','Enter'],['Enter','Enter','Enter'],0,28],
[41,'blank',['Shift','Shift','Shift'],['Shift','Shift','Shift'],0,23],
[42,'alphaZ',u'zяя',u'ZЯЯ',0,10],
[43,'alphaX',u'xчч',u'XЧЧ',0,10],
[44,'alphaC',u'cсс',u'CСС',0,10],
[45,'alphaV',u'vмм',u'VММ',0,10],
[46,'alphaB',u'bии',u'BИИ',0,10],
[47,'alphaN',u'nтт',u'NТТ',0,10],
[48,'alphaM',u'mьь',u'MЬЬ',0,10],
[49,'alpha7',u',бб',u'<ББ',0,10],
[50,'alpha8',u'.юю',u'>ЮЮ',0,10],
[51,'blank',u'/..',u'?,,',0,10]
]

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

