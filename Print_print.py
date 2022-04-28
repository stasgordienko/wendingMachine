# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from dialogs import *
from os import *
import sys
import subprocess
import QtPoppler
import conv
from Print_finish import _print_finish, _print_error

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class _print_print(QDialog):
    def __init__(self,d):
	QDialog.__init__(self)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
	self.d=d
	self.l=d['l']
	self.lang=d['lang']
	self.state=0
	self.pagesOK=0

	for window in ['print_preview','print_charge']:
	    if window in self.d.keys(): 
		try:
		    if self.d[window] != None:
			self.d[window].close()
		except:
		    pass
		del self.d[window]

        font = QFont()
        font.setPointSize(22)
        font.setWeight(75)
        font.setBold(False)

        self.background2 = QLabel(self)
        self.background2.setStyleSheet('background-color: transparent; background-image: url("img/transp87black-noise.png");')
        self.background2.setGeometry(QRect(0,0,1280,1024))
        self.background2.show()

        self.label = QLabel(self)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label_print"))
        self.label.setText(self.l['print_prepare'][self.lang])
        self.stylesheet1='background:transparent; border-width: 0px; border: none; color: #333333;'
        self.stylesheet2='background-image: url("img/scan/finish_scan.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.label.setStyleSheet(self.stylesheet2)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,d['xres']-480,450))
	self.label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
	self.label.show()

	self.progress=QProgressBar(self)
	self.progress.setGeometry(QRect(300,600, d['xres']-600, 50))
	self.progress.setValue(0)
	self.progress.hide()

        self.transform90 = QTransform()
        self.transform90.rotate(90)
	
	self.timer=QTimer()
	self.connect(self.timer, SIGNAL("timeout()"), self.progressUp)
	self.w=0
	self.p=0
	time1side=3700 #время prepare, мсек
	time2side=12000 #время печати, мсек
	timeINIT1=9000
	timeINIT2=12000

	self.stateTimer = QTimer()
	self.stateTimer.setInterval(1000)
	self.connect(self.stateTimer, SIGNAL("timeout()"), self.printerState)
	
	if d['isDoubleSided']:
	    self.time=d['printP2'] * time2side + d['printP1'] * time1side + timeINIT2
	else:
	    self.time=d['printNpage'] * time1side + timeINIT1

	self.connect(self.d['copier'], SIGNAL("stateChanged(QString)"), self.changeState)
	
	print subprocess.call(['sudo', './usbReset','0x0924','0x420c']) #reset xerox-4118 usb-printer
	if d['source_type'] == 'img':
	    self.printIMG()
	elif d['source_type'] == 'pdf':
	    self.printLP()
	else:
	    print "unknown source type in <Print_print> init"
	    self.close()


    def progressUp(self):
	if (self.progress.value() < 100) and (self.d['copier'].state in ['printing','ready']):
	    self.progress.setValue(self.progress.value()+1)


    def closeEvent(self,event):
	self.timer.stop()
	self.stateTimer.stop()
	self.deleteLater()
	event.accept()


    def printLP(self):
	isDoubleSided=self.d['isDoubleSided']
	documentCopies = self.d['documentCopies']
	duplexType=self.d['duplexType']
	startPage=self.d['startPage']
	endPage=self.d['endPage']
	fitToA4=self.d['fitToA4']
	addBorder=self.d['addBorder']
	fileName=self.d['fileName']
	#document=self.d['document']
	printRange=self.d['printRange']
	
	for p in QPrinterInfo.availablePrinters():
	    if p.isDefault():
		defaultPrinter=p
		print "DEFAULT PRINTER:",p.printerName()
		self.d['log'].log("default:"+p.printerName())
		print "destination printer by config:", self.d['systemPrinterName']
		
	#print p.printerName()

	#print document.fonts()
	    
	if isDoubleSided:
	    duplex=duplexType;
	    sides='two-sided-long-edge'
	    #sides='two-sided-short-edge'
	else:
	    duplex='None'
	    sides='one-sided'

	param=['lp', '-d', str(self.d['systemPrinterName']), '-P', printRange, '-n', str(documentCopies), '-q','100', '-o','media=a4','-o', 'sides='+str(sides), '-o','ColorModel=Gray','-o','Resolution=600dpi','-o','StpImageType=TextGraphics','-o','StpQuality=High','-o','Duplex='+str(duplex), fileName]
	print "param orig:",param
	#print subprocess.call(param)
	os_param=''
	for p in param:
	    os_param = os_param + p + ' '
	print "os_param:",os_param
	self.d['log'].log("print_command: "+os_param)
	
	answer = os.popen(os_param)  # START PRINTING
	answer = answer.read()
	if 'Error' not in answer:
	    self.jobID = answer.strip().split(' ')[2]
	    print "ID=",self.jobID," answer=",answer
	    self.d['log'].log("ID="+self.jobID+" answer="+answer)
	else:
	    print "Print start error: ",answer
	    self.d['log'].log("Print start error:"+answer)
	    if 'Print_charge' in self.d.keys() and self.d['Print_charge']: self.d['Print_charge'].close()
	    self.close()

        #self.stateTimer.start() # Запуск PrintState
        self.stateTimeout = 0


    def printIMG(self):
	"""
	self.d['source_type'] = 'img'
	self.d['img_printRes']=self.printRes
	self.d['img_source']=self.myPixmap
	self.d['img_scale']=self.scale
	self.d['img_rotate']=self.rotate = 0
	self.d['img_verticalLayout']=self.verticalLayout
	self.d['img_horizontalLayout']=self.horizontalLayout
        """
	isDoubleSided=self.d['isDoubleSided']
	documentCopies = self.d['printNpage']
	duplexType=self.d['duplexType']
	fitToA4=self.d['fitToA4']
	addBorder=self.d['addBorder']
	scale = self.d['img_scale']
	rotate = self.d['img_rotate']
	verticalLayout = self.d['img_verticalLayout']
	horizontalLayout = self.d['img_horizontalLayout']
	source=self.d['img_source']
	resolution = 600 #dpi
	self.x = int(8.26 * resolution) #A4 width 8.26 inch (4958 pixels@600dpi)
	self.y = int(11.69 * resolution) #A4 height 11.69 inch (7017 pixels@600dpi)

	
	for p in QPrinterInfo.availablePrinters():
	    if p.isDefault():
		defaultPrinter=p
		print "DEFAULT PRINTER:",
	print p.printerName()

	printer=QPrinter(defaultPrinter, QPrinter.HighResolution)
	printer.setPrinterName(QString("xerox4118"))
	#printer.setColorMode(QPrinter.GrayScale)
	printer.setOutputFormat(QPrinter.NativeFormat)
	printer.setResolution(resolution)
	printer.setDuplex(QPrinter.DuplexLongSide)
	printer.setDoubleSidedPrinting(isDoubleSided)
	printer.setPageMargins(0,0,0,0,QPrinter.DevicePixel)
	printer.setPaperSize(QPrinter.A4)
	printer.setFullPage(True)
	printer.setOrientation(QPrinter.Portrait)

	#dlg=QPrintDialog(printer)

	print "printer.printerName():",printer.printerName()
	print "printer.pageRect():",printer.pageRect()
	print "printer.paperRect():",printer.paperRect()
	print "printer.physicalDpiX():",printer.physicalDpiX()
	print "printer.physicalDpiY():",printer.physicalDpiY()
	print "printer.supportedResolutions():",printer.supportedResolutions()
	print "printer.doubleSidedPrinting():",printer.doubleSidedPrinting()
	print "printer.resolution():",printer.resolution()
	print "printer.fullPage():",printer.fullPage()
	print "printer.isValid():",printer.isValid()
	print "printer.paperSize():",printer.paperSize()
	print "printer.orientation():",printer.orientation()

	#self.disp = QPixmap(self.x, self.y)
	#self.disp.fill()

	if rotate == 1:
	    pixmap=source.transformed(self.transform90)
	else:      
	    pixmap=source
        	
	imgWidth = pixmap.width()
	imgHeight = pixmap.height()
	print imgWidth, imgHeight
	
	w = int(imgWidth*(scale/100))
	h = int(imgHeight*(scale/100))

	if horizontalLayout == 0:
	    x = 1
	elif horizontalLayout == 1:
	    x = self.x//2 - w//2
	elif horizontalLayout == 2:
		x = self.x - w
	    
	if verticalLayout == 0:
	    y = 1
	elif verticalLayout == 1:
	    y = self.y//2 - h//2
	elif verticalLayout == 2:
	    y = self.y - h

	painter = QPainter()
	painter.begin(printer)
	for i in range(0,documentCopies):
	    painter.drawPixmap(x,y,w,h,pixmap)
	painter.end()

	#self.label0=QLabel(self)
	#self.label0.setGeometry(QRect(100,100,self.x,self.y))
	#self.label0.setPixmap(self.disp)
	#self.label0.show()

	#painter=QPainter(printer)
	#fileName=QFileDialog.getOpenFileName(None,'open file','/home/stang/')

	#painter.begin(printer)
	#painter.drawImage(0,0,pixmap)
        #painter.end()

        del(painter)
        del(printer)


    def printerState(self):
	st=''
	os_param = 'lpstat'
	answer = os.popen(os_param)
	lpstat = answer.read()
	print "lpstat:",lpstat
	self.d['log'].log("lpstat="+lpstat)

	os_param = 'lpstat -p '+self.d['systemPrinterName']+' -D -l'
	answer = os.popen(os_param)
	answer = answer.read()
	print os_param,":",answer
	self.d['log'].log(os_param+":"+answer)

	state = answer.split(self.d['systemPrinterName'])[1].strip()
	print "state=",state
	percentage=0
	if 'сейчас печатает' in state:
	    st='printing'
	    if 'Finished page' in state:
		finishedPage = int(state.split("Finished page")[1].split('.')[0].strip())
		self.pagesOK = finishedPage
		percentage=self.pagesOK // self.d['printNpage']
		print "state is FINISHED page %s from %s (%s)" % (str(finishedPage), str(self.d['printNpage']), str(percentage))
		self.d['log'].log("state is FINISHED page %s from %s (%s)" % (str(finishedPage), str(self.d['printNpage']), str(percentage)))
	    elif 'Printing page' in state:
		printingPage = int(state.split("Printing page")[1].split(',')[0].strip())
		self.pagesOK = printingPage - 1
		percentage = self.pagesOK // self.d['printNpage']
		print "state is PRINTING page %s from %s (%s)" % (str(printingPage), str(self.d['printNpage']), str(percentage))
		self.d['log'].log("state is PRINTING page %s from %s (%s)" % (str(printingPage), str(self.d['printNpage']), str(percentage)))
		
	elif 'свободен' in state:
	    st='finish'
	    if 'Finished page' in state:
		finishedPage = int(state.split("Finished page")[1].split('.')[0].strip())
		self.pagesOK = finishedPage
		percentage = self.pagesOK // self.d['printNpage']
		print "state is FINISHED!!! Printed page %s from %s (%s)" % (str(finishedPage), str(self.d['printNpage']), str(percentage))
		self.d['log'].log("state is FINISHED page %s from %s (%s)" % (str(finishedPage), str(self.d['printNpage']), str(percentage)))
	
	if self.pagesOK == self.d['printNpage'] and (self.jobID not in lpstat):
	    self.stateTimer.stop()
	    print "DONE"


    def changeState(self,state):
	print "CALLING PRINT changeState with param %s. Copier state is %s" % (state,self.d['copier'].state)
	if self.state==0 and state=='printing':
	    print "START PRINTING..."
	    self.label.setText(self.l['printing'][self.lang])
	    self.progress.show()
	    self.timer.start(self.time//100)
	    self.state=1
	elif self.state==1 and (state=='printing'):
	    if self.progress.value() > 98:
		self.progress.setValue(90)


	elif self.state==1 and (state=='error' or state=='paper' or state=='off'):
	    print "!!!!!!!!!!!printing error!!!!!!!!!!"
	    #print "успешно напечатано %d из %d страниц" % (self.page,self.d['ncopies'])
	    self.state=-1

	    self.disconnect(self.d['copier'], SIGNAL("stateChanged(QString)"), self.changeState)
	    self.d['printed_pages'] = int(self.d['printNpage'] * (self.progress.value()/100))
	    if self.d['isDoubleSided']:
		self.d['printDocCost'] =  int((self.d['printP2'] * int(self.d['print_pagecost2']) + self.d['printP1'] * int(self.d['print_pagecost'])) * (self.progress.value()/100))
	    else:
		self.d['printDocCost'] =  int((self.d['printNpage']) * int(self.d['print_pagecost']) * (self.progress.value()/100))
	    self.d['balance'] -= self.d['printDocCost']
	    paper = int((self.d['printP1'] + self.d['printP2'])* (self.progress.value()/100))
	    self.d['paper'] = int(self.d['paper']) - paper
	    try:
		self.d['action'].paper += paper
		self.d['action'].drum += int(self.d['printNpage'] * (self.progress.value()/100))
		self.d['action'].usedsumm += float(self.d['printDocCost'] / 100)
	    except:
		pass
	    self.d['payoutEnabled']=True

	    #SEND state to site
	    #print _modem(self.d).sendState()
	    #SEND SMS
	    text="N:<%s> Paper:%d;%d\nChange(uah):%d ((50)%d, (25)%d, (5)%d)\nBox(uah):%d Stacker:%d\n" % (int(self.d['device']),int(self.d['paper_up']),int(self.d['paper_down']),
	    int(self.d['coinSumm'])//100,int(self.d['coinC50']),int(self.d['coinC25']),int(self.d['coinC5']),int(self.d['cashBoxSumm'])//100,
	    int(self.d['billSumm'])//100)
	    #print _modem(self.d).sendSMS(str(self.d['phone1']),text)

	    self.d['print_error']=_print_error(self.d)
	    if 'print_print' in self.d.keys(): 
		if self.d['print_print']:
		    self.d['print_print'].close()
		del(self.d['print_print'])
	    self.deleteLater()


	elif self.state>0 and state=='ready' and self.progress.value() > 50:
	    print "!!!!!!!!!!!OKKKKK!!!!!!!!!!"
	    self.label.hide()
	    self.progress.hide()
	    self.repaint()
	    self.disconnect(self.d['copier'], SIGNAL("stateChanged(QString)"), self.changeState)

	    self.d['paper'] = int(self.d['paper']) - (self.d['printP1'] + self.d['printP2'])

	    try:
		self.d['action'].usedsumm += float(self.d['printDocCost'] / 100)
		self.d['action'].paper += self.d['printP1'] + self.d['printP2']
	        self.d['action'].drum += self.d['printNpage']
		self.d['action'].finish(status='success')
	    except:
		pass
	    self.d['balance'] -= self.d['printDocCost']
	    self.d['payoutEnabled']=True

	    self.d['print_finish'] = _print_finish(self.d)
	    if 'print_print' in self.d.keys(): 
		if self.d['print_print']:
		    self.d['print_print'].close()
		del(self.d['print_print'])
	    self.deleteLater()

