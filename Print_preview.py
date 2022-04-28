# -*- coding: utf-8 -*-

from __future__ import division

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from os import *
from dialogs import *
from spins import intSpinBox
from Print_charge import _print_charge
import QtPoppler
import subprocess
import conv
import db

IMAGES = ['jpg', 'jpeg', 'png', 'tiff', 'bmp']
DOCUMENTS = ['pdf', 'doc', 'docx', 'odt', 'xls', 'xlsx', 'ppt', 'pptx', 'rtf']
PLAIN = ['txt', 'pas', 'c', 'cpp', 'py']
SUPPORTED = DOCUMENTS + IMAGES

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class clickLabel(QLabel):
    def mousePressEvent(self,event):
        self.emit(SIGNAL("clicked()"))
	event.accept()


class _print_preview(QWidget):
    def __init__(self,d):
        QWidget.__init__(self)
        #MainMenu._window_list.append(self)
        self.d=d
        self.l=d['l']
        self.lang=d['lang']

        font = QFont()
        font.setPointSize(22)
        font.setWeight(75)
        font.setBold(False)

	self.document = None
	self.temppdf = str(self.d['temppdf'])
	self.source = str("/tmp/tempsource")
        self.filename=d['print_filename']
        self.path=d['print_path']
        self.fullname=d['print_fullname']
        self.docType=d['docType']
        self.n=1
        self.npages=0
        self.documentCopies=1
        self.isOpening = False
        
        self.select = {}
        self.npagesSelected = 0

        self.A4y=842 #(A5)595 #d['yres']-180
        self.A4x=595 #(A5)420 #(self.y*3)//4
	
	self.y=748 #decrease to 60 dpi
	self.x=528

        self.setupInterface(self)
	self.showFullScreen()

        self.connect(self.b_eject,  SIGNAL("clicked()"),  self.pop)
        self.connect(self.b_print,  SIGNAL("clicked()"),  self.printAll)
        self.connect(self.b_back,  SIGNAL("clicked()"),  self.back)
        self.connect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
        self.connect(self.b_prev,  SIGNAL("clicked()"),  self.prev)
        self.connect(self.b_next,  SIGNAL("clicked()"),  self.next)
        self.connect(self.b_first,  SIGNAL("clicked()"),  self.first)
        self.connect(self.b_last,  SIGNAL("clicked()"),  self.last)
        self.connect(self.print_all, SIGNAL("clicked()"),  self.printall)
        self.connect(self.print_diap, SIGNAL("clicked()"),  self.printdiap)
        self.connect(self.print_select, SIGNAL("clicked()"),  self.printselect)
        self.connect(self.startPage,  SIGNAL("valueChanged(int)"),  self.startChanged)
        self.connect(self.endPage,  SIGNAL("valueChanged(int)"),  self.endChanged)
        self.connect(self.DoubleSided,  SIGNAL("stateChanged(int)"),  self.doubleChanged)
        self.connect(self.quantity,  SIGNAL("valueChanged(int)"),  self.quantityChanged)
        self.connect(self.cover,  SIGNAL("clicked()"),  self.coverClick)
        self.connect(self.cover_prev,  SIGNAL("clicked()"),  self.prev)
        self.connect(self.cover_next,  SIGNAL("clicked()"),  self.next)


        self.transform90 = QTransform()
        self.transform90.rotate(90)

        if 'action' in d.keys(): 
	    if (d['action'].isFinished == False):
		if d['action'].typeId != 'print':
		    d['action'].finish()
		    d['action']=db.action(termId=int(d['device']),balance=float(d['balance']/100),typeId='print')
        else: 
	    d['action']=db.action(termId=int(d['device']),balance=float(d['balance']/100),typeId='print')


        self.stimer = QTimer()
        self.stimer.setInterval(30000)   # timeout 30 sec
        self.connect(self.stimer, SIGNAL("timeout()"), self.pop)
        
        self.label.setText(unicode(self.filename))
        self.b_print.setEnabled(True)
        self.b_next.setEnabled(True)
        self.b_prev.setEnabled(False)
        self.cover_prev.setEnabled(False)
        
	#self.updateView()

    def startChanged(self, val):
	if self.startPage.value() > self.endPage.value():
	    self.endPage.setValue(val)
	self.recalc()
	
    def endChanged(self, val):
	if self.endPage.value() < self.startPage.value():
	    self.startPage.setValue(val)
	self.recalc()

    def doubleChanged(self,state):
	self.recalc()

    def quantityChanged(self,q):
	self.documentCopies=q
	self.recalc()

    def coverClick(self):
	if self.print_select.isChecked():
	    if self.n in self.select.keys():
		self.select.pop(self.n)
	    else:
		self.select[self.n]=1
	    self.recalc()
	    self.updateView()

    def printall(self):
	self.print_all.setChecked(True)
	self.print_diap.setChecked(False)
	self.print_select.setChecked(False)
	#self.print_all.setGeometry(QRect(self.x+60, 300, 650, 70))
	#self.print_diap.setGeometry(QRect(self.x+60, 380, 650, 70))
        self.print_select.setGeometry(QRect(self.x+60, 460, 650, 70))
	self.print_pages.setVisible(False)
	self.startPage.setVisible(False)
	self.endPage.setVisible(False)
	self.recalc()
	self.updateView()


    def printdiap(self):
    	self.print_all.setChecked(False)
	self.print_diap.setChecked(True)
	self.print_select.setChecked(False)
	#self.print_all.setGeometry(QRect(self.x+60, 300, 650, 70))
	#self.print_diap.setGeometry(QRect(self.x+60, 380, 650, 70))
        self.print_select.setGeometry(QRect(self.x+60, 610, 650, 70))
	self.print_pages.setVisible(False)
	self.startPage.setVisible(True)
	self.endPage.setVisible(True)
	self.recalc()
	self.updateView()


    def printselect(self):
    	self.print_all.setChecked(False)
	self.print_diap.setChecked(False)
	self.print_select.setChecked(True)
	#self.print_all.setGeometry(QRect(self.x+60, 300, 650, 70))
	#self.print_diap.setGeometry(QRect(self.x+60, 380, 650, 70))
        self.print_select.setGeometry(QRect(self.x+60, 460, 650, 70))
    	self.print_pages.setVisible(True)
	self.startPage.setVisible(False)
	self.endPage.setVisible(False)
	self.recalc()
	self.updateView()


        
    def toPDF(self):
	result=0
	if self.docType=='pdf':
	    result=1
	elif self.docType in DOCUMENTS:
    	    print "call toPDF() - doc type is: ",self.docType
	    try:
		#self.converter = conv.DocumentConverter() 
		self.d['converter'].convert(self.source, self.temppdf)
		#del(self.converter)
	    except conv.DocumentConversionException, exception:
		print "(ups!)ERROR conversion to PDF " + str(exception)
	    except conv.ErrorCodeIOException, exception:
		print "(ups!)ERROR conversion to PDF: ErrorCodeIOException %d" % exception.ErrCode
	    else:
		self.source=self.temppdf
		print "finish toPDF() - OK. FILENAME: ", self.filename
    		result=1
	else:
    	    print "the type of the document not suported"
	return result


    def updateView(self):
        if (not self.isOpening) and (self.npages == 0):
	    try:
		(out, err) = subprocess.Popen(['cp',self.fullname,self.source], stdout=subprocess.PIPE).communicate()
		#subprocess.call(['cp',self.fullname,self.source])
		#self.fullname
		#print "out:",out,"err:",err
	    except:
		self.close()
	    else:
		self.isOpening = True

	    if self.toPDF():
		#print "start poppler"
    		self.document = QtPoppler.Poppler.Document.load(self.source)
    		self.document.setRenderHint(QtPoppler.Poppler.Document.Antialiasing and QtPoppler.Poppler.Document.TextAntialiasing)
    		self.npages = self.document.numPages()
    		self.print_all.setText(self.l['print_all_pages'][self.lang] + " (%d)" % self.npages)
    		#print "finish poppler"
    		self.endPage.setRange(1,self.npages)
    		self.startPage.setRange(1,self.npages)
    		pageWidth = self.document.page(0).pageSize().width()
		pageHeight = self.document.page(0).pageSize().height()
		print pageWidth, pageHeight
		self.updateView()
		self.recalc()
    	    else:
    		self.pop()
        
        else:
	    if self.n==self.npages:
        	self.b_next.setEnabled(False)
        	self.cover_next.setEnabled(False)
        	self.b_last.setEnabled(False)
	    if self.n==1:
		self.b_prev.setEnabled(False)
		self.cover_prev.setEnabled(False)
		self.b_first.setEnabled(False)

	    pageWidth = self.document.page(self.n-1).pageSize().width()
	    pageHeight = self.document.page(self.n-1).pageSize().height()
	    
	    if True and (pageWidth < (self.A4x - 50)) and (pageHeight < (self.A4y - 50)): #fit to page
		resx = 64 * (self.A4x / pageWidth)
		resy = 64 * (self.A4y / pageHeight)
    		#myImage = myImage.scaled(self.A4x, self.A4y, transformMode=Qt.SmoothTransformation)
            else:
		resx = 64
		resy = 64
	    
	    myImage=self.document.page(self.n-1).renderToImage(resx, resy)
	    
	    #orient = self.document.page(self.n-1).orientation()
	    #print orient
	    if myImage.width() > myImage.height(): #QtPoppler.Landscape:
        	myImage=myImage.transformed(self.transform90)
        
	    pixmap = QPixmap.fromImage(myImage)
	    
	    self.preview.setPixmap(pixmap)#.scaled(self.A4x, self.A4y, transformMode=Qt.SmoothTransformation))
	    self.l_page.setText(self.l['page_from'][self.lang] % (self.n, self.npages))
	    
	    if self.print_select.isChecked():
		self.cover_prev.setVisible(True)
		self.cover_next.setVisible(True)
		self.cover.setVisible(True)
		if self.n in self.select.keys():
		    self.cover.setStyleSheet(self.coverStyleSheet2)
		    self.cover.setText(self.l['page_selected'][self.lang])
		else:
		    self.cover.setStyleSheet(self.coverStyleSheet1)
		    self.cover.setText(self.l['page_press'][self.lang])
	    else:
		self.cover_prev.setVisible(False)
		self.cover_next.setVisible(False)
		self.cover.setVisible(False)


	    if self.d['printNpage'] > 0: 
		self.b_print.setEnabled(True)
	    else:
		self.b_print.setEnabled(False)
	    #self.recalc()
	    #self.preview.setPixmap(QPixmap.fromImage(self.d.page(self.n).renderToImage(30, 30)))
	    self.stimer.start()


    def recalc(self):
	self.d['startPage']=self.startPage.value()
	self.d['endPage']=self.endPage.value()

	if self.print_all.isChecked():
	    self.d['printRange']="1-"
	    self.d['printNpage']=self.npages
	    self.print_all.setText(self.l['print_all_pages'][self.lang] + " (%d)" % (self.npages))
	else:
	    self.print_all.setText(self.l['print_all_pages'][self.lang])

	if self.print_diap.isChecked():
	    self.d['printRange']=str(self.d['startPage'])+'-'+str(self.d['endPage'])
	    self.d['printNpage']=(self.d['endPage']-self.d['startPage']+1) #self.npages
	    self.print_diap.setText(self.l['print_range'][self.lang] + " (%d):" % (self.d['printNpage']))
	else:
	    self.print_diap.setText(self.l['print_range'][self.lang])

	if self.print_select.isChecked():
	    self.d['printRange']=str(self.print_pages.text())
	    (self.npagesSelected,self.selectedRange)=self.calcSelectedRange(self.select)
	    self.d['printNpage']=self.npagesSelected
	    self.d['printRange']=self.selectedRange
	    self.print_pages.setText(self.selectedRange)
	    #print "preview print_pages.text:",self.print_pages.text() ###########################################
	    #print "preview printRange:",self.d['printRange'] ###########################################
	    self.print_select.setText(self.l['print_selected'][self.lang] + " (%d):" % self.npagesSelected)
	else:
	    self.print_select.setText(self.l['print_selected'][self.lang])

	self.d['printP2'] = (self.d['printNpage']//2)
	self.d['printP1'] = (self.d['printNpage'] - (self.d['printP2'] * 2) )
	
	self.d['printNpage'] *= self.documentCopies
	self.d['printP1'] *= self.documentCopies
	self.d['printP2'] *= self.documentCopies

    	if self.DoubleSided.isChecked():
	    self.d['printDocCost'] =  self.d['printP2'] * int(self.d['print_pagecost2']) + self.d['printP1'] * int(self.d['print_pagecost']) 
	else:
	    self.d['printDocCost'] =  int(self.d['printNpage']) * int(self.d['print_pagecost'])

	self.l_cost_sum.setText("%4.2f" % (self.d['printDocCost']/100))
	
	self.stimer.start()


        
    def first(self):
        if self.n > 10:
            self.n -= 10
        else:
	    self.n = 1
        if self.npages > 1 :
	    self.b_next.setEnabled(True)
	    self.cover_next.setEnabled(True)
	    self.b_last.setEnabled(True)
        self.updateView()

    def prev(self):
        if self.n>1:
            self.n-=1
            self.b_next.setEnabled(True)
            self.b_last.setEnabled(True)
            self.cover_next.setEnabled(True)
            self.updateView()

    def next(self):
        if self.n<self.npages:
            self.n+=1
            self.b_prev.setEnabled(True)
            self.b_first.setEnabled(True)
            self.cover_prev.setEnabled(True)
            self.updateView()

    def last(self):
        if self.n+10 < self.npages:
            self.n += 10
        else:
            self.n = self.npages
        self.b_prev.setEnabled(True)
        self.b_first.setEnabled(True)
        self.updateView()


    def calcSelectedRange(self,selected):
	n = 0
	N = 0
	text = ''
	prev = 0
	keys = selected.keys()
	keys.sort()

	for item in keys:
	    if n == 0: 
		prev = item
		n = 1
		text = str(item)
	    elif item-prev > 1:
		if n == 1:
		    text = text+','+str(item)
		else:
		    text = text+'-'+str(prev)+','+str(item)
		prev = item
		n = 1
	    else:
		prev = item
		n += 1
	    N += 1

	if n > 1:
	    text = text+'-'+str(item)

	return (N,text)

    
    def printAll(self):
        self.stimer.stop()
        self.d['documentCopies']=self.documentCopies
	self.d['isDoubleSided']=self.DoubleSided.isChecked()
	self.d['duplexType']='DuplexNoTumble' #DuplexTumble #None
	self.d['startPage']=self.startPage.value()
	self.d['endPage']=self.endPage.value()
	self.d['fitToA4']=False
	self.d['addBorder']=False
	self.d['fileName']=self.source
	
	self.d['source_type'] = 'pdf'
	
        self.d['print_charge']=_print_charge(self.d)
        self.d['print_charge'].showFullScreen()

            
    def pop(self):
        #self.umount()
        self.stimer.stop()
	for window in ['print_fileselect','print_preview','cat']:
	    if window in self.d.keys(): 
		try:
		    if self.d[window] != None:
			self.d[window].close() 
		    del self.d[window]
		except:
		    pass
        #self.deleteLater()

    def closeEvent(self, event):
        self.disconnect(self.stimer, SIGNAL("timeout()"), self.pop)
        self.disconnect(self.b_eject,  SIGNAL("clicked()"),  self.pop)
        self.disconnect(self.b_print,  SIGNAL("clicked()"),  self.printAll)
        self.disconnect(self.b_back,  SIGNAL("clicked()"),  self.back)
        self.disconnect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
        self.disconnect(self.b_prev,  SIGNAL("clicked()"),  self.prev)
        self.disconnect(self.b_next,  SIGNAL("clicked()"),  self.next)
        self.disconnect(self.b_first,  SIGNAL("clicked()"),  self.first)
        self.disconnect(self.b_last,  SIGNAL("clicked()"),  self.last)
        self.disconnect(self.print_all, SIGNAL("clicked()"),  self.printall)
        self.disconnect(self.print_diap, SIGNAL("clicked()"),  self.printdiap)
        self.disconnect(self.print_select, SIGNAL("clicked()"),  self.printselect)
        self.disconnect(self.startPage,  SIGNAL("valueChanged(int)"),  self.startChanged)
        self.disconnect(self.endPage,  SIGNAL("valueChanged(int)"),  self.endChanged)
        self.disconnect(self.DoubleSided,  SIGNAL("stateChanged(int)"),  self.doubleChanged)
        self.disconnect(self.quantity,  SIGNAL("valueChanged(int)"),  self.quantityChanged)
        self.disconnect(self.cover,  SIGNAL("clicked()"),  self.coverClick)
        self.disconnect(self.cover_prev,  SIGNAL("clicked()"),  self.prev)
        self.disconnect(self.cover_next,  SIGNAL("clicked()"),  self.next)
        
        try:
	    del(self.document)
	except:
	    pass

	event.accept()


    def back(self):
        self.stimer.stop()
	for window in ['print_preview']:
	    if window in self.d.keys(): 
		try:
		    if self.d[window] != None:
			self.d[window].close() 
		except:
		    pass
		del(self.d[window])
        self.deleteLater()


    def helpbox(self):
	self.stimer.stop()
	if 'cat' in self.d.keys():
	    page = 'catalog'
	else:
	    page = 'printdoc'
        hb=helpBox(page, self.d)
        hb.exec_()
        self.stimer.start()

    def enterEvent(self,event):
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.pop)
	self.updateView()
	event.accept()


    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.pop)
	event.accept


    def setupInterface(self,window):
        font = QFont()
        font.setPointSize(22)
        font.setWeight(75)
        font.setBold(False)

        self.label = QLabel(window)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label.setGeometry(QRect(self.x+40, 70, self.d['xres']-self.x-60, 200))
        self.label.setText('FILENAME')
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)

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

        self.b_print = QPushButton(window)
        self.b_print.setFont(font)
        self.b_print.setObjectName(_fromUtf8("b_next"))
        self.b_print.setFocusPolicy(Qt.NoFocus)
        self.b_print.setGeometry(QRect(self.d['xres']-320, self.d['yres']-120, 300, 95))
        #self.b_next.setAlignment(Qt.AlignLeft)
        self.b_print.setText(self.l['print'][self.lang])

        self.l_cost = QLabel(window)
        self.l_cost.setFont(font)
        self.l_cost.setObjectName(_fromUtf8("l_cost"))
        self.l_cost.setGeometry(QRect(self.x+50, self.d['yres']-115, 350, 95))
        self.l_cost.setAlignment(Qt.AlignRight)
        self.l_cost.setText(self.l['print_cost'][self.lang])

        self.l_cost_uah = QLabel(window)
        self.l_cost_uah.setFont(font)
        self.l_cost_uah.setObjectName(_fromUtf8("l_cost_uah"))
        self.l_cost_uah.setGeometry(QRect(self.x+50, self.d['yres']-65, 350, 95))
        self.l_cost_uah.setAlignment(Qt.AlignRight)
        self.l_cost_uah.setText(self.l['uah'][self.lang])

        font2 = QFont()
        font2.setPointSize(32)
        font2.setWeight(75)
        font2.setBold(True)
        self.l_cost_sum = QLabel(window)
        self.l_cost_sum.setFont(font2)
        self.l_cost_sum.setObjectName(_fromUtf8("l_cost_sum"))
        self.l_cost_sum.setGeometry(QRect(self.x+50, self.d['yres']-76, 290, 95))
        self.l_cost_sum.setAlignment(Qt.AlignRight)
        self.l_cost_sum.setText("0.00")

        self.b_back = QPushButton(self.top)
	self.b_back.setGeometry(QRect(30, 15, 400, 90))
        self.b_back.setFont(font)
        self.b_back.setObjectName(_fromUtf8("b_main"))
        self.b_back.setFocusPolicy(Qt.NoFocus)
        self.b_back.setText(self.l['back'][self.lang])

        self.preview = QLabel(self)
        self.preview.setObjectName(_fromUtf8("preview"))
        self.preview.setGeometry(QRect(15, 135, self.x, self.y))
        self.preview.setText(self.l['print_preview_wait'][self.lang])
        self.preview.setAlignment(Qt.AlignCenter)
        #self.preview.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        coverFont = QFont()
        coverFont.setPointSize(18)
        coverFont.setWeight(75)
        coverFont.setBold(True)
        self.cover = clickLabel(self)
        self.cover.setObjectName(_fromUtf8("cover"))
        self.cover.setGeometry(QRect(15, 135, self.x, self.y))
        self.coverStyleSheet1='background-color: transparent; color: #5555FF; background-position: center; background-repeat: no-repeat; background-origin: content; background-image: url("img/print/plashka.png"); border: none; font-size: 15pt;'
        self.coverStyleSheet2='background-color: transparent; color: #55FF55; background-position: center; background-repeat: no-repeat; background-origin: content; background-image: url("img/print/plashka.png"); border: none; font-size: 20pt;'
        self.cover.setStyleSheet(self.coverStyleSheet1)
        self.cover.setText(self.l['page_press'][self.lang])
        #self.cover.setFont(coverFont)
        self.cover.setAlignment(Qt.AlignCenter)
        self.cover.setVisible(False)

        self.cover_prev = QPushButton(self)
        self.cover_prev.setGeometry(QRect(0, 425, 120, 150))
	self.cover_prev.setStyleSheet('background-color: transparent; background-position: center; background-repeat: no-repeat; background-origin: content; background-image: url("img/b_left_green.png"); border: none;')
        self.cover_prev.setFocusPolicy(Qt.NoFocus)
        self.cover_prev.setFont(font)
        self.cover_prev.setObjectName(_fromUtf8("cover_prev"))
        self.cover_prev.setVisible(False)

        self.cover_next = QPushButton(self)
        self.cover_next.setGeometry(QRect(440, 425, 120, 150))
        self.cover_next.setStyleSheet('background-color: transparent; background-position: center; background-repeat: no-repeat; background-origin: content; background-image: url("img/b_right_green.png"); border: none;')
        self.cover_next.setFocusPolicy(Qt.NoFocus)
        self.cover_next.setFont(font)
        self.cover_next.setObjectName(_fromUtf8("cover_next"))
        self.cover_next.setVisible(False)


        self.l_page = QLabel(self)
        font1 = QFont()
        font1.setPointSize(18)
        self.l_page.setFont(font1)
        self.l_page.setObjectName(_fromUtf8("l_page"))
        self.l_page.setText('...')
        self.l_page.setGeometry(QRect(170, 900, 220, 100))
        self.l_page.setAlignment(Qt.AlignCenter)

        self.b_first = QPushButton(self)
        self.b_first.setGeometry(QRect(5, 910, 90, 90))
        self.b_first.setFocusPolicy(Qt.NoFocus)
        self.b_first.setFont(font)
        self.b_first.setObjectName(_fromUtf8("b_firstpage"))
        self.b_first.setStyleSheet('* {background-image: url("img/mob/b_num.png"); background-position: center; border: none;} *:pressed {background-image: url("img/mob/b_num_pressed.png"); background-position: center; border: none;}')

        self.b_prev = QPushButton(self)
        self.b_prev.setGeometry(QRect(96, 910, 90, 90))
        self.b_prev.setFocusPolicy(Qt.NoFocus)
        self.b_prev.setFont(font)
        self.b_prev.setObjectName(_fromUtf8("b_prevpage"))
        self.b_prev.setStyleSheet('* {background-image: url("img/mob/b_num.png"); background-position: center; border: none;} *:pressed {background-image: url("img/mob/b_num_pressed.png"); background-position: center; border: none;}')

        self.b_next = QPushButton(self)
        self.b_next.setGeometry(QRect(390, 910, 90, 90))
        self.b_next.setFocusPolicy(Qt.NoFocus)
        self.b_next.setFont(font)
        self.b_next.setObjectName(_fromUtf8("b_nextpage"))
        self.b_next.setStyleSheet('* {background-image: url("img/mob/b_num.png"); background-position: center; border: none;} *:pressed {background-image: url("img/mob/b_num_pressed.png"); background-position: center; border: none;}')

        self.b_last = QPushButton(self)
        self.b_last.setGeometry(QRect(480, 910, 90, 90))
        self.b_last.setFocusPolicy(Qt.NoFocus)
        self.b_last.setFont(font)
        self.b_last.setObjectName(_fromUtf8("b_lastpage"))
        self.b_last.setStyleSheet('* {background-image: url("img/mob/b_num.png"); background-position: center; border: none;} *:pressed {background-image: url("img/mob/b_num_pressed.png"); background-position: center; border: none;}')

        font = QFont()
        font.setPointSize(24)
        
        self.stylePages="""*:checked {background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(33,152,17,254), stop:0.5 rgba(33,152,17,220), stop:1 rgba(33,152,17,180)); 
border: 3px solid rgba(33,152,17,200); 
border-radius: 10px; color: white;
}
*
{background-color: orange; 
border: 3px solid yellow; 
border-radius: 10px; color: white;
}
"""

        self.print_all = QPushButton(self)
        self.print_all.setFont(font)
        self.print_all.setObjectName(_fromUtf8("print_all"))
        self.print_all.setText(self.l['print_all_pages'][self.lang])
        self.print_all.setGeometry(QRect(self.x+60, 300, 650, 70))
        self.print_all.setFocusPolicy(Qt.NoFocus)
        self.print_all.setCheckable(True)
        self.print_all.setChecked(True)
        self.print_all.setStyleSheet(self.stylePages)

        self.print_diap = QPushButton(self)
        self.print_diap.setFont(font)
        self.print_diap.setObjectName(_fromUtf8("print_diap"))
        self.print_diap.setText(self.l['print_range'][self.lang])
        self.print_diap.setGeometry(QRect(self.x+60, 380, 650, 70))
        self.print_diap.setFocusPolicy(Qt.NoFocus)
        self.print_diap.setCheckable(True)
        self.print_diap.setStyleSheet(self.stylePages)

        self.startPage=intSpinBox(self,name=self.l['start_page'][self.lang],value=1,minimum=1,maximum=1,step=1)
        self.startPage.setFont(font)
        self.startPage.setGeometry(QRect(self.x+100, 460, 610, 60))
        self.startPage.setVisible(False)
        self.endPage=intSpinBox(self,name=self.l['end_page'][self.lang],value=1,minimum=1,maximum=1,step=1)
        self.endPage.setFont(font)
        self.endPage.setGeometry(QRect(self.x+100, 530, 610, 60))
        self.endPage.setVisible(False)


        #self.b_scale=QCheckBox(self)
        #self.b_scale.setText(u"%s" % (self.l['xerox_scale'][self.lang]))
        #self.b_scale.setGeometry(QRect((d['xres']-700)//2, 400, 700, 100))
        #self.b_scale.setChecked(False)
        #font = QFont()
        #font.setPointSize(24)
        #self.b_scale.setFont(font)
        #self.b_scale.setFocusPolicy(Qt.NoFocus)


        self.print_select = QPushButton(self)
        self.print_select.setFont(font)
        self.print_select.setObjectName(_fromUtf8("print_select"))
        self.print_select.setText(self.l['print_selected'][self.lang])
        self.print_select.setGeometry(QRect(self.x+60, 460, 650, 70))
        self.print_select.setFocusPolicy(Qt.NoFocus)
        self.print_select.setCheckable(True)
        self.print_select.setStyleSheet(self.stylePages)

        self.print_pages = QLineEdit(self)
        self.print_pages.setFont(font)
        self.print_pages.setObjectName(_fromUtf8("print_pages"))
        self.print_pages.setText("")
        self.print_pages.setGeometry(QRect(self.x+60, 550, 650, 100))
        self.print_pages.setFocusPolicy(Qt.NoFocus)
        self.print_pages.setVisible(False)


        self.DoubleSided=QCheckBox(self.l['duplex_print'][self.lang],self)
        self.DoubleSided.setObjectName('duplex_print')
        self.DoubleSided.setFont(font)
        self.DoubleSided.setChecked(False)
        self.DoubleSided.setGeometry(QRect(self.x+60,700,550,50))
        self.DoubleSided.setFocusPolicy(Qt.NoFocus)
        
        self.quantity = intSpinBox(self,name=self.l['quantity'][self.lang],value=1,minimum=1,maximum=99,step=1)
        self.quantity.setFont(font)
        self.quantity.setGeometry(QRect(self.x+60,770,650,60))


        #self.setWindowTitle("print_preview")
        self.b_help.setText(self.l['help'][self.lang])
        self.b_eject.setText('')
        self.b_back.setText(self.l['another_file'][self.lang])
        self.l_page.setText(u". . .")
        self.b_print.setText(self.l['next'][self.lang])
        self.b_first.setText(u"<<")
        self.b_prev.setText(u"<")
        self.b_next.setText(u">")
        self.b_last.setText(u">>")
        
