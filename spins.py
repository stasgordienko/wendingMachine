# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from os import listdir

nameFont = QFont("FreeSans")
nameFont.setPointSize(24)
nameFont.setWeight(50)
nameFont.setBold(False)

valueFont = QFont("FreeSans")
valueFont.setPointSize(24)
valueFont.setWeight(50)
valueFont.setBold(True)


class intSpinBox(QWidget):
    def __init__(self, parent, name='', value=0, minimum=0, maximum=100, step=1, prop='', reset=[]):
        QWidget.__init__(self)
        self.setParent(parent)
        self.propertyName=prop
        self.VALUE=int(value)
        self.minimum=int(minimum)
        self.maximum=int(maximum)
        self.step=int(step)

	self.nameLabel=QLabel(name.decode('utf8'), self)
	self.nameLabel.setStyleSheet('background-color: transparent; color: #333333')
	self.nameLabel.setWordWrap(True)
	self.nameLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
	self.nameLabel.setFont(self.font())
	if name:
	    self.nameLabel.setVisible(True)
	else:
	    self.nameLabel.setVisible(False)

	self.b_dec=QPushButton("-",self)
	self.connect(self.b_dec, SIGNAL("clicked()"), self.dec)
	self.b_dec.setFont(nameFont)
	self.b_dec.setFocusPolicy(Qt.NoFocus)
	self.b_dec.installEventFilter(self)

	self.label=QLabel(self)
	self.label.setStyleSheet('background-color: #505050; border: 3px solid #ababab; border-radius: 5px; color: #2cd800;')
	self.label.setAlignment(Qt.AlignCenter)
	self.label.setFont(valueFont)

	self.b_inc=QPushButton("+",self)
	self.connect(self.b_inc, SIGNAL("clicked()"), self.inc)
	self.b_inc.setFocusPolicy(Qt.NoFocus)
	self.b_inc.setFont(nameFont)
	self.b_inc.installEventFilter(self)

	if reset!=[]:
	    if type(reset[0])==type(QPushButton()):
		self.resetValue=int(reset[1])
		self.connect(reset[0], SIGNAL("clicked()"), self.reset)
	    elif type(reset[0]).__name__ in ('str','int'):
		self.resetValue=int(reset[1])
		self.b_reset=QPushButton(reset[0].decode('utf8'),self)
		self.connect(self.b_reset, SIGNAL("clicked()"), self.reset)

	self.timer=QTimer(self)
	self.pressed=False
	self.update()
	self.show()


    def eventFilter(self, obj, event):
	if (obj is self.b_inc) and event.type()==2: #QEvent.MouseButtonPress:
	    self.pressed=True
	    self.timer.singleShot(300, self.pressedINC)
	elif (obj is self.b_dec) and event.type()==2: #QEvent.MouseButtonPress:
	    self.pressed=True
	    self.timer.singleShot(300, self.pressedDEC)
	elif ((obj is self.b_inc) or (obj is self.b_dec)) and event.type()==3: #QEvent.MouseButtonRelease:
	    self.pressed=False
	    self.timer.stop()
	
	return QWidget.eventFilter(self, obj, event)

    def resizeEvent(self, event):
	self.b_inc.setGeometry(QRect(self.width()-50,5,50,50))
	self.b_dec.setGeometry(QRect(self.width()-200,5,50,50))
	self.label.setGeometry(QRect(self.width()-147,0,94,60))
	try:
	    if self.b_reset:
		pass
	except:
	    self.nameLabel.setGeometry(QRect(0,5,self.width()-200,50))
	else:
	    self.nameLabel.setGeometry(QRect(0,5,self.width()-250,50))
	    self.b_reset.setGeometry(QRect(self.width()-250,5,50,50))
	QWidget.resizeEvent(self,event)
	event.accept()

    def changeEvent(self, event):
	try:
	    self.nameLabel.setFont(self.font())
	except:
	    pass
	else:
	    pass
	QWidget.changeEvent(self,event)
	event.accept()


    def pressedINC(self):
	if self.pressed:
	    self.inc()
	    self.timer.singleShot(100,self.pressedINC)

    def pressedDEC(self):
	if self.pressed:
	    self.dec()
	    self.timer.singleShot(100,self.pressedDEC)

    def setRange(self,minimum,maximum):
	self.minimum=int(minimum)
        self.maximum=int(maximum)
        self.update()
        
    def update(self):
	self.label.setText(str(self.VALUE))
	if self.VALUE>self.minimum:
	    self.b_dec.setEnabled(True)
	else:
	    self.b_dec.setEnabled(False)
	
	if self.VALUE<self.maximum:
	    self.b_inc.setEnabled(True)
	else:
	    self.b_inc.setEnabled(False)
	self.emit(SIGNAL("valueChanged(int)"),self.VALUE)


    def inc(self):
	if self.VALUE < (self.maximum - self.step):
	    self.VALUE+=self.step
	else:
	    self.VALUE=self.maximum
	self.update()
	
    def dec(self):
	if self.VALUE > (self.minimum + self.step):
	    self.VALUE-=self.step
	else:
	    self.VALUE=self.minimum
	self.update()
	    
    def val(self):
	return int(self.VALUE)

    def value(self):
	return int(self.VALUE)

    def setValue(self,Value):
	self.VALUE = int(Value)
	self.update()
	    
    def text(self):
	return str("%d" % (self.VALUE))

    def reset(self):
	self.VALUE = self.resetValue
	self.update()

    def prop(self):
	return self.propertyName


class floatSpinBox(intSpinBox):
    def update(self):
	self.label.setText("%.2f" % (int(self.VALUE)/100))
	if self.VALUE>self.minimum:
	    self.b_dec.setEnabled(True)
	else:
	    self.b_dec.setEnabled(False)
	
	if self.VALUE<self.maximum:
	    self.b_inc.setEnabled(True)
	else:
	    self.b_inc.setEnabled(False)


class intSpinBoxNE(QWidget):
    def __init__(self, parent, name='', value=0, prop='', reset=[]):
        QWidget.__init__(self)
        self.setParent(parent)
        self.propertyName=prop
        self.VALUE=int(value)

	self.nameLabel=QLabel(name.decode('utf8'), self)
	self.nameLabel.setStyleSheet('background-color: transparent; color: #333333')
	self.nameLabel.setWordWrap(True)
	self.nameLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
	self.nameLabel.setFont(self.font())
	if name:
	    self.nameLabel.setVisible(True)
	else:
	    self.nameLabel.setVisible(False)

	self.label=QLabel(self)
	self.label.setStyleSheet('background-color: #505050; border: 3px solid #ababab; border-radius: 5px; color: #2cd800;')
	self.label.setAlignment(Qt.AlignCenter)
	self.label.setFont(valueFont)

	if reset!=[]:
	    if type(reset[0])==type(QPushButton()):
		self.resetValue=int(reset[1])
		self.connect(reset[0], SIGNAL("clicked()"), self.reset)
	    elif type(reset[0]).__name__ in ('str','int'):
		self.resetValue=int(reset[1])
		self.b_reset=QPushButton(reset[0].decode('utf8'),self)
		self.connect(self.b_reset, SIGNAL("clicked()"), self.reset)

	self.update()
	self.show()


    def resizeEvent(self, event):
	self.label.setGeometry(QRect(self.width()-147,0,94,60))
	try:
	    if self.b_reset:
		pass
	except:
	    self.nameLabel.setGeometry(QRect(0,5,self.width()-200,50))
	else:
	    self.nameLabel.setGeometry(QRect(0,5,self.width()-250,50))
	    self.b_reset.setGeometry(QRect(self.width()-250,5,50,50))
	QWidget.resizeEvent(self,event)
	event.accept()

    def changeEvent(self, event):
	try:
	    self.nameLabel.setFont(self.font())
	except:
	    pass
	else:
	    pass
	QWidget.changeEvent(self,event)
	event.accept()


    def update(self):
	self.label.setText(str(self.VALUE))

    def val(self):
	return int(self.VALUE)

    def value(self):
	return int(self.VALUE)

    def setValue(self,Value):
	self.VALUE = int(Value)
	self.update()
	    
    def text(self):
	return str("%d" % (self.VALUE))

    def reset(self):
	self.VALUE = self.resetValue
	self.update()

    def prop(self):
	return self.propertyName



class floatSpinBoxNE(intSpinBoxNE):
    def update(self):
	self.label.setText("%.2f" % (int(self.VALUE)/100))


class textBox(QWidget):
    def __init__(self, parent, name='', value='', prop='', l=30):
        QWidget.__init__(self)
        self.setParent(parent)
        self.propertyName=prop
        self.VALUE = value

	self.nameLabel=QLabel(name.decode('utf8'), self)
	self.nameLabel.setStyleSheet('background-color: transparent; color: #333333')
	self.nameLabel.setWordWrap(True)
	self.nameLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
	self.nameLabel.setFont(self.font())
	if name:
	    self.nameLabel.setVisible(True)
	else:
	    self.nameLabel.setVisible(False)

	self.label=QLineEdit(self)
	self.label.setStyleSheet('background-color: #505050; border: 3px solid #ababab; border-radius: 5px; color: #2cd800;')
	self.label.setAlignment(Qt.AlignCenter)
	self.label.setFont(valueFont)

	self.update()
	self.show()


    def resizeEvent(self, event):
	self.label.setGeometry(QRect(self.width()-200,0,200,60))
	self.nameLabel.setGeometry(QRect(0,5,self.width()-200,50))
	QWidget.resizeEvent(self,event)
	event.accept()

    def changeEvent(self, event):
	try:
	    self.nameLabel.setFont(self.font())
	except:
	    pass
	else:
	    pass
	QWidget.changeEvent(self,event)
	event.accept()


    def update(self):
	self.label.setText(str(self.VALUE))
	#self.emit(SIGNAL("valueChanged(int)"),self.VALUE)

    def val(self):
	return self.label.text()

    def value(self):
	return self.label.text()

    def setValue(self,Value):
	self.VALUE = Value
	self.update()
	    
    def text(self):
	return str("%s" % (self.VALUE))

    def prop(self):
	return self.propertyName


class selectBox(QWidget):
    def __init__(self, parent, name='', value=0, prop='', mas=[]):
        QWidget.__init__(self)
        self.setParent(parent)
        self.propertyName=prop
        self.VALUE=int(value)
        self.mas=mas
        self.minimum=0
        self.maximum=len(mas)-1
        self.step=1

	self.nameLabel=QLabel(name.decode('utf8'), self)
	self.nameLabel.setStyleSheet('background-color: transparent; color: #333333')
	self.nameLabel.setWordWrap(True)
	self.nameLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
	self.nameLabel.setFont(self.font())
	if name:
	    self.nameLabel.setVisible(True)
	else:
	    self.nameLabel.setVisible(False)

	self.b_dec=QPushButton("-",self)
	self.connect(self.b_dec, SIGNAL("clicked()"), self.dec)
	self.b_dec.setFont(nameFont)
	self.b_dec.setFocusPolicy(Qt.NoFocus)
	self.b_dec.installEventFilter(self)

	self.label=QLabel(self)
	self.label.setStyleSheet('background-color: #505050; border: 3px solid #ababab; border-radius: 5px; color: #2cd800;')
	self.label.setAlignment(Qt.AlignCenter)
	self.label.setFont(valueFont)

	self.b_inc=QPushButton("+",self)
	self.connect(self.b_inc, SIGNAL("clicked()"), self.inc)
	self.b_inc.setFocusPolicy(Qt.NoFocus)
	self.b_inc.setFont(nameFont)
	self.b_inc.installEventFilter(self)

	self.timer=QTimer(self)
	self.pressed=False
	self.update()
	self.show()


    def eventFilter(self, obj, event):
	if (obj is self.b_inc) and event.type()==2: #QEvent.MouseButtonPress:
	    self.pressed=True
	    self.timer.singleShot(300, self.pressedINC)
	elif (obj is self.b_dec) and event.type()==2: #QEvent.MouseButtonPress:
	    self.pressed=True
	    self.timer.singleShot(300, self.pressedDEC)
	elif ((obj is self.b_inc) or (obj is self.b_dec)) and event.type()==3: #QEvent.MouseButtonRelease:
	    self.pressed=False
	    self.timer.stop()
	
	return QWidget.eventFilter(self, obj, event)

    def resizeEvent(self, event):
	self.b_inc.setGeometry(QRect(self.width()-50,5,50,50))
	self.b_dec.setGeometry(QRect(self.width()-200,5,50,50))
	self.label.setGeometry(QRect(self.width()-147,0,94,60))
	self.nameLabel.setGeometry(QRect(0,5,self.width()-200,50))
	QWidget.resizeEvent(self,event)
	event.accept()

    def changeEvent(self, event):
	try:
	    self.nameLabel.setFont(self.font())
	except:
	    pass
	else:
	    pass
	QWidget.changeEvent(self,event)
	event.accept()


    def pressedINC(self):
	if self.pressed:
	    self.inc()
	    self.timer.singleShot(100,self.pressedINC)

    def pressedDEC(self):
	if self.pressed:
	    self.dec()
	    self.timer.singleShot(100,self.pressedDEC)

    def setRange(self,minimum,maximum):
	self.minimum=int(minimum)
        self.maximum=int(maximum)
        self.update()
        
    def update(self):
	self.label.setText(self.mas[self.VALUE])
	if self.VALUE>self.minimum:
	    self.b_dec.setEnabled(True)
	else:
	    self.b_dec.setEnabled(False)
	
	if self.VALUE<self.maximum:
	    self.b_inc.setEnabled(True)
	else:
	    self.b_inc.setEnabled(False)


    def inc(self):
	if self.VALUE < (self.maximum - self.step):
	    self.VALUE+=self.step
	else:
	    self.VALUE=self.maximum
	self.update()
	
    def dec(self):
	if self.VALUE > (self.minimum + self.step):
	    self.VALUE-=self.step
	else:
	    self.VALUE=self.minimum
	self.update()
	    
    def val(self):
	return str("%s" % (str(self.mas[self.VALUE])))

    def value(self):
	return str("%s" % (str(self.mas[self.VALUE])))    

    def setValue(self,Value):
	self.VALUE = int(Value)
	self.update()
	    
    def text(self):
	return str("%d" % (self.VALUE))

    def prop(self):
	return self.propertyName



class _file(QWidget):
    def __init__(self, parent, x, y, prop, name, value):
        QWidget.__init__(self)
        self.setParent(parent)
        self.value=value
        self.propertyName=prop
	
	self.nameLabel=QLabel(name.decode('utf8'), self)
	self.nameLabel.setWordWrap(True)
	self.nameLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
	self.nameLabel.setFont(self.font())
	self.nameLabel.setGeometry(QRect(x,y,190,50))

	self.label=QLineEdit(self)
	#self.label.setAlignment(Qt.AlignCenter)
	self.label.setFont(valueFont)
	self.label.setGeometry(QRect(x+200,y,200,50))


	self.b_sel=QPushButton('...',self)
	self.b_sel.setGeometry(QRect(x+400,y,50,50))
	self.connect(self.b_sel, SIGNAL("clicked()"), self.sel)

	self.update()


    def update(self):
	self.label.setText(str(self.value))


    def sel(self):
	#print self.value
	#name=QFileDialog.getOpenFileName(self,'open file', self.value, options=QFileDialog.DontResolveSymlinks)
        name=_sel_dev().get(self.label.text())
	
	if name!='' and name!=None:
	    self.value=name
	    print "returned value: ", self.value
	self.update()

    def val(self):
	return str(self.label.text())
	    
    def text(self):
	return str(self.label.text())

    def prop(self):
	return self.propertyName


class _sel_dev(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        #self.setAutoFillBackground(False)
        #self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.encoding='utf8'

	self.b_open=QPushButton('open', self)
	self.b_open.setGeometry(QRect(200,550,50,50))
	self.b_open.setEnabled(False)
        self.connect(self.b_open,  SIGNAL("clicked()"),  SLOT("accept()"))
        
        self.list=QListWidget(self)
        self.list.setGeometry(QRect(10, 10, 500, 300))
        self.connect(self.list,  SIGNAL("itemClicked(QListWidgetItem *)"),  self.itemClicked)

	
    def get(self,name):
        self.filename=name
        self.currentPath=''
        
        if (len(name)>0) and ('/' in name):
	    mas=name.split('/')[1:-1]
	    for node in mas:
		self.currentPath+='/'+node
	else:
	    self.currentPath='/dev/serial/by-id'
	    
        #print name, '---', self.currentPath

        self.listUpdate()
	return self.exec_()
        
        
    def listUpdate(self):
        self.list.clear()

        names = listdir(self.currentPath)

        for name in names:
            fullname = self.currentPath + '/' + name
            item= QListWidgetItem(QString(fullname))
            item.setFont(QFont("FreeSans", 14, 25))
            self.list.addItem(item)

    def itemClicked(self, item):
            self.filename=item.text() #unicode(item.text()).encode('utf-8')
            self.b_open.setEnabled(True)
            #self.listUpdate()

	    
    def exec_(self):
	print "exec called."
	if QDialog.exec_(self):
	    return self.filename