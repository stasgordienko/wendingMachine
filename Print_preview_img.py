# -*- coding: utf-8 -*-

from __future__ import division

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from dialogs import *
from os import *
from Print_charge import _print_charge
from spins import intSpinBox
import subprocess
import db

IMAGES = ['jpg', 'jpeg', 'png', 'tiff', 'bmp']
DOCUMENTS = ['pdf', 'doc', 'docx', 'odt', 'xls', 'xlsx', 'ppt', 'pptx', 'rtf']
PLAIN = ['txt', 'pas', 'c', 'cpp', 'py']
SUPPORTED = DOCUMENTS + IMAGES

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

    
class _print_preview_img(QWidget):
    def __init__(self,d):
        QWidget.__init__(self)
        #MainMenu._window_list.append(self)
        self.d=d
        self.l=d['l']
        self.lang=d['lang']

        self.filename=d['print_filename']
        self.path=d['print_path']
        self.fullname=d['print_fullname']
        self.docType=d['docType']
        self.documentCopies = 1
        
        self.source = '/tmp/tempimage'
        
        self.y=842 #(A5)595 #d['yres']-180
        self.x=595 #(A5)420 #(self.y*3)//4
	
	self.disp = QPixmap(self.x, self.y)

	self.printRes = 600
	self.scale = 100
	self.rotate = 0
	self.verticalLayout = 1
	self.horizontalLayout = 1

        self.setupInterface(self)
	self.showFullScreen()
	
	self.alignPressed = self.b_align5
        
        self.transform90 = QTransform()
        self.transform90.rotate(90)
        
        self.myPixmap = None
        
        if 'action' in d.keys(): 
	    if (d['action'].isFinished == False):
		if d['action'].typeId != 'print':
		    d['action'].finish()
		    d['action']=db.action(termId=int(d['device']),balance=float(d['balance']/100),typeId='print')
        else: 
	    d['action']=db.action(termId=int(d['device']),balance=float(d['balance']/100),typeId='print')

        
        self.stimer = QTimer()
        self.l_filename.setText(unicode(self.filename))
        self.b_print.setEnabled(True)
        
        self.connect(self.b_align1, SIGNAL("clicked()"), self.b_align1_clicked)
	self.connect(self.b_align2, SIGNAL("clicked()"), self.b_align2_clicked)
        self.connect(self.b_align3, SIGNAL("clicked()"), self.b_align3_clicked)
        self.connect(self.b_align4, SIGNAL("clicked()"), self.b_align4_clicked)
        self.connect(self.b_align5, SIGNAL("clicked()"), self.b_align5_clicked)
        self.connect(self.b_align6, SIGNAL("clicked()"), self.b_align6_clicked)
        self.connect(self.b_align7, SIGNAL("clicked()"), self.b_align7_clicked)
        self.connect(self.b_align8, SIGNAL("clicked()"), self.b_align8_clicked)
        self.connect(self.b_align9, SIGNAL("clicked()"), self.b_align9_clicked)

	self.connect(self.quantity,  SIGNAL("valueChanged(int)"),  self.quantityChanged)
	self.connect(self.rotateAngle,  SIGNAL("valueChanged(int)"),  self.rotateChanged)
	self.connect(self.scalePercent,  SIGNAL("valueChanged(int)"),  self.scaleChanged)

        self.connect(self.b_eject,  SIGNAL("clicked()"),  self.pop)
        self.connect(self.b_print,  SIGNAL("clicked()"),  self.printAll)
        self.connect(self.b_back,  SIGNAL("clicked()"),  self.back)
        self.connect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
        self.recalc()


        
    def updateView(self):
	if self.myPixmap == None:
	    (out, err) = subprocess.Popen(['cp',self.fullname,self.source], stdout=subprocess.PIPE).communicate()
	    if err == None:
		self.myPixmap = QPixmap(self.source)
		self.updateView()
    	    else:
    		self.pop()
        else:
	    self.disp.fill()
	    if self.rotate == 1:
		pixm=self.myPixmap.transformed(self.transform90)
	    else:
        	pixm=self.myPixmap
        	
	    imgWidth = pixm.width()
	    imgHeight = pixm.height()
	    #print imgWidth, imgHeight
	
	    w = imgWidth//(8.27/(self.scale/100))
	    h = imgHeight//(8.27/(self.scale/100))

	    if self.horizontalLayout == 0:
		x = 1
	    elif self.horizontalLayout == 1:
		x = self.x//2 - w//2
	    elif self.horizontalLayout == 2:
		x = self.x - w
	    
	    if self.verticalLayout == 0:
		y = 1
	    elif self.verticalLayout == 1:
		y = self.y//2 - h//2
	    elif self.verticalLayout == 2:
		y = self.y - h

	    painter = QPainter()
	    painter.begin(self.disp)
	    painter.drawPixmap(x,y,w,h,pixm)
	    painter.end()

	    self.preview.setPixmap(self.disp)
	    #self.stimer.start()


    def quantityChanged(self,q):
	self.documentCopies=q
	self.recalc()

    def scaleChanged(self):
	self.scale = self.scalePercent.value()
	self.updateView()
        
    def rotateChanged(self):
	if self.rotateAngle.value() == 90:
	    self.rotate = 1
	else:
	    self.rotate = 0
	self.updateView()
	

    def b_align1_clicked(self):
	self.horizontalLayout = 0
	self.verticalLayout = 0
	self.alignPressed.setChecked(False)
	self.alignPressed = self.b_align1
	self.updateView()

    def b_align2_clicked(self):
	self.horizontalLayout = 1
	self.verticalLayout = 0
	self.alignPressed.setChecked(False)
	self.alignPressed = self.b_align2
	self.updateView()

    def b_align3_clicked(self):
	self.horizontalLayout = 2
	self.verticalLayout = 0
	self.alignPressed.setChecked(False)
	self.alignPressed = self.b_align3
	self.updateView()

    def b_align4_clicked(self):
	self.horizontalLayout = 0
	self.verticalLayout = 1
	self.alignPressed.setChecked(False)
	self.alignPressed = self.b_align4
	self.updateView()

    def b_align5_clicked(self):
	self.horizontalLayout = 1
	self.verticalLayout = 1
	self.alignPressed.setChecked(False)
	self.alignPressed = self.b_align5
	self.updateView()
	
    def b_align6_clicked(self):
	self.horizontalLayout = 2
	self.verticalLayout = 1
	self.alignPressed.setChecked(False)
	self.alignPressed = self.b_align6
	self.updateView()
	
    def b_align7_clicked(self):
	self.horizontalLayout = 0
	self.verticalLayout = 2
	self.alignPressed.setChecked(False)
	self.alignPressed = self.b_align7
	self.updateView()

    def b_align8_clicked(self):
	self.horizontalLayout = 1
	self.verticalLayout = 2
	self.alignPressed.setChecked(False)
	self.alignPressed = self.b_align8
	self.updateView()

    def b_align9_clicked(self):
	self.horizontalLayout = 2
	self.verticalLayout = 2
	self.alignPressed.setChecked(False)
	self.alignPressed = self.b_align9
	self.updateView()

    
    def printAll(self):
        self.stimer.stop()
	self.d['isDoubleSided']=False #self.DoubleSided.isChecked()
	self.d['duplexType']='DuplexNoTumble' #DuplexTumble #None
	self.d['fitToA4']=False
	self.d['addBorder']=False

	self.d['printNpage'] = self.documentCopies
	self.d['printP2'] = (self.d['printNpage']//2)
	self.d['printP1'] = (self.d['printNpage'] - (self.d['printP2'] * 2) )
	
	self.d['source_type'] = 'img'
	self.d['img_printRes']=self.printRes
	self.d['img_source']=self.myPixmap
	self.d['img_scale']=self.scale
	self.d['img_rotate']=self.rotate
	self.d['img_verticalLayout']=self.verticalLayout
	self.d['img_horizontalLayout']=self.horizontalLayout

        self.d['print_charge']=_print_charge(self.d)
        self.d['print_charge'].showFullScreen()
            
    def pop(self):
        #self.umount()
        self.stimer.stop()
	for window in ['print_fileselect','print_preview_img','cat']:
	    if window in self.d.keys(): 
		try:
		    if self.d[window] != None:
			self.d[window].close() 
		    del self.d[window]
		except:
		    pass
        self.deleteLater()


    def back(self):
        self.close()
        self.deleteLater()


    def helpbox(self):
        hb=helpBox('printimg', self.d)
        hb.exec_()

    def enterEvent(self,event):
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.pop)
	self.updateView()
	event.accept()

    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.pop)
	event.accept

    def recalc(self):
	self.d['printNpage'] = self.documentCopies
        self.d['printDocCost'] =  int(self.d['printNpage']) * int(self.d['print_pagecost'])
        self.l_cost_sum.setText("%4.2f" % (self.d['printDocCost']/100))


    def setupInterface(self,window):
        self.l_filename = QLabel(window)
        font = QFont()
        font.setPointSize(22)
        font.setWeight(75)
        font.setBold(False)
        self.l_filename.setFont(font)
        self.l_filename.setAlignment(Qt.AlignCenter)
        self.l_filename.setObjectName(_fromUtf8("l_filename"))
        self.l_filename.setGeometry(QRect(self.x+40, 120, self.d['xres']-self.x-60, 100))
        self.l_filename.setWordWrap(True)
        self.l_filename.setText(u"название файла.txt")

        self.top = QWidget(window)
        self.top.setAutoFillBackground(True)
        self.top.setObjectName(_fromUtf8("top"))
        self.top.setGeometry(QRect(0, 0, self.d['xres']+1, 120))

        self.b_help = QPushButton(self.top)
        self.b_help.setFont(font)
        self.b_help.setObjectName(_fromUtf8("b_help"))
        self.b_help.setGeometry(QRect((self.d['xres']-250), 15, 220, 90))
        self.b_help.setText(self.l['help'][self.lang])
        self.b_help.setFocusPolicy(Qt.NoFocus)

        self.b_eject = QPushButton(self.top)
        self.b_eject.setFont(font)
        self.b_eject.setObjectName(_fromUtf8("b_eject"))
	self.b_eject.setGeometry(QRect(self.x+10, 15, 400, 90))
        self.b_eject.setText(self.l['eject'][self.lang])
        self.b_eject.setFocusPolicy(Qt.NoFocus)
        self.b_eject.setVisible(False)

        self.b_print = QPushButton(window)
        self.b_print.setFont(font)
        self.b_print.setObjectName(_fromUtf8("b_next"))
        self.b_print.setFocusPolicy(Qt.NoFocus)
        self.b_print.setGeometry(QRect(self.d['xres']-320, self.d['yres']-120, 300, 95))
        #self.b_next.setAlignment(Qt.AlignLeft)
        self.b_print.setText(self.l['next'][self.lang])

        self.l_cost = QLabel(window)
        self.l_cost.setFont(font)
        self.l_cost.setObjectName(_fromUtf8("l_cost"))
        self.l_cost.setGeometry(QRect(650, self.d['yres']-115, 300, 95))
        self.l_cost.setAlignment(Qt.AlignRight)
        self.l_cost.setText(self.l['print_cost'][self.lang])

        self.l_cost_uah = QLabel(window)
        self.l_cost_uah.setFont(font)
        self.l_cost_uah.setObjectName(_fromUtf8("l_cost_uah"))
        self.l_cost_uah.setGeometry(QRect(650, self.d['yres']-65, 300, 95))
        self.l_cost_uah.setAlignment(Qt.AlignRight)
        self.l_cost_uah.setText(self.l['uah'][self.lang])

        font2 = QFont()
        font2.setPointSize(32)
        font2.setWeight(75)
        font2.setBold(True)
        self.l_cost_sum = QLabel(window)
        self.l_cost_sum.setFont(font2)
        self.l_cost_sum.setObjectName(_fromUtf8("l_cost_sum"))
        self.l_cost_sum.setGeometry(QRect(650, self.d['yres']-76, 240, 95))
        self.l_cost_sum.setAlignment(Qt.AlignRight)
        self.l_cost_sum.setText("0.00")

        self.b_back = QPushButton(self.top)
	self.b_back.setGeometry(QRect(30, 15, 400, 90))
        self.b_back.setFont(font)
        self.b_back.setObjectName(_fromUtf8("b_main"))
        self.b_back.setFocusPolicy(Qt.NoFocus)
        self.b_back.setText(self.l['back'][self.lang])

        self.scalePercent = intSpinBox(self,name=self.l['img_scale'][self.lang],value=100,minimum=10,maximum=500,step=5)
        self.scalePercent.setFont(font)
        self.scalePercent.setGeometry(QRect(650,610,600,60))

        self.rotateAngle = intSpinBox(self,name=self.l['img_rotate'][self.lang],value=0,minimum=0,maximum=90,step=90)
        self.rotateAngle.setFont(font)
        self.rotateAngle.setGeometry(QRect(650,690,600,60))
        
        self.quantity = intSpinBox(self,name=self.l['quantity'][self.lang],value=1,minimum=1,maximum=99,step=1)
        self.quantity.setFont(font)
        self.quantity.setGeometry(QRect(650,770,600,60))

        self.preview = QLabel(self)
        self.preview.setObjectName(_fromUtf8("preview"))
        self.preview.setGeometry(QRect(20, 155, self.x, self.y))
        self.preview.setText(self.l['print_preview_wait'][self.lang])
        self.preview.setAlignment(Qt.AlignCenter)
        #self.preview.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        #self.preview.setGeometry(QtCore.QRect(0, 180, 595, 842))

        self.align_label = QLabel(self.l['img_align'][self.lang],self)
        self.align_label.setGeometry(QRect(1000, 200, 250, 48))
        self.align_label.setFont(font)
        self.align_label.setAutoFillBackground(True)
        self.align_label.setAlignment(Qt.AlignCenter)
        self.align_label.setObjectName(_fromUtf8("align_label"))
        
        alignStyleSheet = """* {background-image: url("img/print/arrow_%s.png"); 
        background-position: center; 
        background-origin: content; 
        background-repeat: none;} 
        *:checked {background-image: none; background-color: green;}"""
        
        self.b_align1 = QPushButton(self)
        self.b_align1.setGeometry(QRect(1000, 250, 80, 80))
        self.b_align1.setObjectName(_fromUtf8("b_align1"))
        self.b_align1.setFocusPolicy(Qt.NoFocus)
        self.b_align1.setCheckable(True)
        self.b_align1.setStyleSheet(alignStyleSheet % 'up-left')
        
        self.b_align2 = QPushButton(self)
        self.b_align2.setGeometry(QRect(1085, 250, 80, 80))
        self.b_align2.setObjectName(_fromUtf8("b_align2"))
        self.b_align2.setFocusPolicy(Qt.NoFocus)
        self.b_align2.setCheckable(True)
        self.b_align2.setStyleSheet(alignStyleSheet % 'up')
        
        self.b_align3 = QPushButton(self)
        self.b_align3.setGeometry(QRect(1170, 250, 80, 80))
        self.b_align3.setObjectName(_fromUtf8("b_align3"))
        self.b_align3.setFocusPolicy(Qt.NoFocus)
        self.b_align3.setCheckable(True)
        self.b_align3.setStyleSheet(alignStyleSheet % 'up-right')
        
        self.b_align4 = QPushButton(self)
        self.b_align4.setGeometry(QRect(1000, 335, 80, 80))
        self.b_align4.setObjectName(_fromUtf8("b_align4"))
        self.b_align4.setFocusPolicy(Qt.NoFocus)
        self.b_align4.setCheckable(True)
        self.b_align4.setStyleSheet(alignStyleSheet % 'left')
        
        self.b_align5 = QPushButton(self)
        self.b_align5.setGeometry(QRect(1085, 335, 80, 80))
        self.b_align5.setObjectName(_fromUtf8("b_align5"))
        self.b_align5.setFocusPolicy(Qt.NoFocus)
        self.b_align5.setCheckable(True)
        self.b_align5.setChecked(True)
        self.b_align5.setStyleSheet(alignStyleSheet % '')
        
        self.b_align6 = QPushButton(self)
        self.b_align6.setGeometry(QRect(1170, 335, 80, 80))
        self.b_align6.setObjectName(_fromUtf8("b_align6"))
        self.b_align6.setFocusPolicy(Qt.NoFocus)
        self.b_align6.setCheckable(True)
        self.b_align6.setStyleSheet(alignStyleSheet % 'right')
        
        self.b_align7 = QPushButton(self)
        self.b_align7.setGeometry(QRect(1000, 420, 80, 80))
        self.b_align7.setObjectName(_fromUtf8("b_align7"))
        self.b_align7.setFocusPolicy(Qt.NoFocus)
        self.b_align7.setCheckable(True)
        self.b_align7.setStyleSheet(alignStyleSheet % 'down-left')
        
        self.b_align8 = QPushButton(self)
        self.b_align8.setGeometry(QRect(1085, 420, 80, 80))
        self.b_align8.setObjectName(_fromUtf8("b_align8"))
        self.b_align8.setFocusPolicy(Qt.NoFocus)
        self.b_align8.setCheckable(True)
        self.b_align8.setStyleSheet(alignStyleSheet % 'down')
        
        self.b_align9 = QPushButton(self)
        self.b_align9.setGeometry(QRect(1170, 420, 80, 80))
        self.b_align9.setObjectName(_fromUtf8("b_align9"))
        self.b_align9.setFocusPolicy(Qt.NoFocus)
        self.b_align9.setCheckable(True)
        self.b_align9.setStyleSheet(alignStyleSheet % 'down-right')
