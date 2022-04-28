# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os
import mail
from os.path import *
#from os import listdir, popen, statvfs
import sys
import subprocess
from Scan_error import _scan_error
from Scan_finish import _scan_finish
from datetime import datetime
from dialogs import *

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class _scan_scan(QDialog):
    def __init__(self,d):
	QDialog.__init__(self)
	self.d=d
	self.l=d['l']
	self.lang=d['lang']
	self.state=-2

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

	#self.setStyleSheet('* { background-color: transparent;}')

	self.b_scan=QPushButton(self.l['scan'][self.lang],self)
	self.b_scan.setObjectName("b_scan")
	self.b_scan.setFont(font)
	self.b_scan.setGeometry(QRect((d['xres']-300)//2, d['yres']-200, 300, 95))
	self.b_scan.show()
	self.b_scan.setEnabled(False)

        self.background2 = QLabel(self)
        self.background2.setStyleSheet('background-color: transparent; background-image: url("img/transp87black-noise.png");')
        self.background2.setGeometry(QRect(0,0,1280,1024))
        self.background2.hide()

        self.label = QLabel(self)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        #self.label.setGeometry(QRect((d['xres']-800)//2, 400, 800, 160))
        self.label.setText(self.l['scan_scan_label'][self.lang])
        self.stylesheet1='background:transparent; border-width: 0px; border: none; color: #333333;'
        self.stylesheet2='background-image: url("img/scan/finish_scan.png"); background-color: transparent; border-width: 0px; border: none; color: white;'
	self.label.setStyleSheet(self.stylesheet1)
	self.label.setWordWrap(True)
	self.label.setGeometry(QRect(240,280,d['xres']-480,450))
	self.label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

	self.progress=QProgressBar(self)
	self.progress.setGeometry(QRect(300,600, d['xres']-600, 50))
	self.progress.setValue(0)
	self.progress.hide()


	self.w = 0
	self.p = 0
	self.progtime = 1000 #время prepare, мсек
	self.scanTime = 15000 #время сканирования, мсек
	self.writeTime = 3000 #время write to flash, мсек

	self.ptimer=QTimer()
	self.ptimer.setInterval(self.progtime//20)
	
	self.wtimer=QTimer()
	self.wtimer.setInterval(1000)
	
	self.scanTimer=QTimer()
	self.scanTimer.setInterval(1000)

        self.connect(self.b_main,  SIGNAL("clicked()"),  self.back)
        self.connect(self.b_scan, SIGNAL("clicked()"), self.go)
        self.connect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
        self.connect(self.ptimer, SIGNAL("timeout()"), self.timeScan)
        self.connect(self.wtimer, SIGNAL("timeout()"), self.waitReady)
        self.connect(self.scanTimer, SIGNAL("timeout()"), self.checkScan)


	if self.d['copier'].state=='error' or self.d['copier'].state=='off':
	    notAccessible(d).exec_()
	    self.toMain()
	    return

	#self.setStyleSheet("background-color: white; border-width: 0px; border: none; color: #333333;")
        self.setAutoFillBackground(True)
        #self.setAttribute(Qt.WA_TranslucentBackground, True)
	self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

	self.waitReady()
	

    def go(self):
        if self.d['sided']=='1':
	    format='jpg'
	    resolution='300' #2560x4151
	    mode='Gray'
	    tempfile='/temp.'+format
	    if self.d['scaling']: 
	        self.crop = '2400x3500+0+0'
	    else:
	        self.crop = '2560x4151+0+0'
	else:
	    format='jpg'
	    resolution='200'  #1728x2767
	    mode='Color'
	    tempfile='./temp.'+format
	    if self.d['scaling']: 
	        self.crop = '1630x2350+0+0'
	    else:
	        self.crop = '1728x2767+0+0'
	    

        if self.d['copier'].state=='ready' or self.d['copier'].state=='sleeping' or self.d['copier'].state=='warming' or self.d['copier'].state=='pc-scan' or self.d['copier'].state=='paper':
	    #self.connect(self.d['copier'], SIGNAL("stateChanged(QString)"), self.changeState)
	    self.b_scan.hide()
	    self.top.hide()
	    
	    self.scanFileName = 'scan' + datetime.now().strftime("""%Y-%m-%d_%H-%M-%S""") + '.' + format

	    if exists('./tempscan.tiff'):
		subprocess.call(['rm', './tempscan.tiff'])
	    self.state = -1
	    self.checkScan()

	    if self.d['scan_type']== 'flash':
		self.quality = '100'
		self.resizeXY = '100x100%'
		self.scanFullFileName = self.d['flash'] + '/' + self.scanFileName
		self.d['copier'].set('scan','./scantoflash '+resolution+' '+mode+' '+self.scanFullFileName+' '+self.quality+' '+self.resizeXY+' '+self.crop)
		print "scanFileName:",self.scanFullFileName
		self.d['scanFullFileName'] = self.scanFullFileName
		self.d['scanFileName'] = self.scanFileName
	    elif self.d['scan_type']== 'email':
		self.quality = '100'
		self.resizeXY = '25x25%'
		self.scanFullFileName = './' + self.scanFileName
		self.d['copier'].set('scan','./scantoemail '+resolution+' '+mode+' '+self.scanFullFileName+' '+self.quality+' '+self.resizeXY+' '+self.crop)
		self.d['scanFullFileName'] = self.scanFullFileName
		self.d['scanFileName'] = self.scanFileName
		
	else:
            self.ptimer.stop()
            self.b_scan.show()
	    self.top.show()
	    self.label.setText(self.l['scan_fail'][self.lang])
	    self.state = -2
	    

    def checkScan(self):
	if self.state == -1 and not exists('./tempscan.tiff'):
	    #self.repaint()
	    self.background2.show()
	    self.p = 0
	    self.w = 0
	    self.scanTimer.start()
	    # START SCANNING
	    self.ptimer.start()
	    self.label.setText(self.l['scan_prep'][self.lang])
	    self.label.setStyleSheet(self.stylesheet2)
	    self.progress.show()
	    self.state = 0

	elif self.state == 0 and exists('./tempscan.tiff'): #and self.d['copier'].state=='pc-scan':
	    self.progress.hide()
    	    self.label.setText(self.l['scan_scan'][self.lang])
	    self.d['action'].scan+=1
	    self.state = 1
	    self.ptimer.setInterval(self.scanTime//20)
	    self.p = 0
	    self.ptimer.start()

	elif self.state == 1 and exists(self.scanFullFileName): #not exists('./tempscan.tiff'):
	    self.progress.hide()
	    self.ptimer.setInterval(self.writeTime//10)
	    self.p = 0
	    if self.d['scan_type'] == 'email':
		self.label.setText(self.l['send_email'][self.lang])
	    elif self.d['scan_type'] == 'flash':
		self.label.setText(self.l['write_flash'][self.lang])
	    self.ptimer.start()
	    self.state = 2

	elif (self.state == 2) and (not exists('./tempscan.tiff')) and (exists(self.scanFullFileName)):
	    if self.d['scan_type'] == 'email':
		mailserver = 'mail.copyprime.com.ua'
		sender = 'scan@copyprime.com.ua'
		pwd = 'VDSCP2011'
		receiver = [str(self.d['email'])]
		subj = 'CopyPrime SCANIMAGE '+str(self.scanFileName)
		txt = unicode(self.l['scan_sent'][self.lang] % (str(receiver[0]), str(self.scanFileName))).encode('cp1251')
		scan = [str(self.scanFullFileName)]

		self.d['email_message']={'sender':sender, 
					'receiver':receiver, 
					'subj':subj, 
					'txt':txt, 
					'attach':scan, 
					'mailserver':mailserver, 
					'sender':sender, 
					'pwd':pwd}

		self.d['log'].log('SCAN TO EMAIL:'+unicode(self.d['email']).encode('utf-8'))
	    elif self.d['scan_type'] == 'flash':
		#flush flash buffer
		#self.label.setText(self.l['write_flash'][self.lang])
		pass
	    self.state = 3

	elif (self.state == 3) and (not exists('./tempscan.tiff')) and (exists(self.scanFullFileName)) and self.progress.value() > 98:
	    self.progress.hide()
	    self.scanTimer.stop()
	    self.ptimer.stop()
	    self.label.setText("")
	    self.state=3
	    #self.update()
	    print "!!!!!!!!!!!OKKKKK!!!!!!!!!!"
	    summ = int(self.d['cost'])
	    self.d['balance'] -= summ
	    self.d['action'].usedsumm += float(summ/100)
	    self.d['payoutEnabled']=True
	    print "balance is: %d" % self.d['balance']

	    self.d['n_scan']+=1

	    #PAGE FINISH !!!!!!!!!!!!!!!!!!!
	    self.background2.hide()
	    self.label.hide()
	    self.repaint()
	    self.d['scan_finish']=_scan_finish(self.d)
	    self.disconnect(self.b_scan, SIGNAL("clicked()"), self.go)
	    self.close()
	    self.deleteLater()
	    del(self.d['scan_scan'])
	else:
	    print "SCANNING. self.state=%d" % self.state


    def waitReady(self):
	self.wtimer.stop()
        if self.d['copier'].state=='warming':
	    ##sleep(3)
	    self.background2.show()
	    self.label.setText(self.l['warming'][self.lang])
	    self.label.setStyleSheet(self.stylesheet2)
	    self.wtimer.start()
	    self.w+=1
	    print self.d['copier'].state
	    #if self.w==25:
		#print "something wrong with copier...."
	elif self.d['copier'].state=='paper' or self.d['copier'].state=='sleeping':
	    self.b_scan.setEnabled(True)
	elif self.w==30 or self.d['copier'].state=='off' or self.d['copier'].state=='error':
	    print "ERROR. Copier state is not ready...."
	    self.toMain()
	else:
	    self.background2.hide()
	    self.label.setText(self.l['scan_scan_label'][self.lang])
	    self.label.setStyleSheet(self.stylesheet1)
	    self.b_scan.setEnabled(True)
	

    def timeScan(self):
        if self.p<100:
	    if self.p == 0:
		self.progress.show()
	    self.p+=5
	    self.progress.setValue(self.p)
	else:
	    self.ptimer.stop()


    def back(self):
	self.ptimer.stop()
	#if self.d['scan_charge']!=None: self.d['scan_charge'].put(0)
        self.close()
        self.deleteLater()

    def toMain(self):
	self.ptimer.stop()
	for window in ['scan','scan_charge','scan_scan']:
	    if window in self.d.keys(): 
		try:
		    if self.d[window] != None:
			self.d[window].close() 
		    del self.d[window]
		except:
		    pass
        self.deleteLater()

    def enterEvent(self,event):
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.toMain)
	event.accept

    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.toMain)
	event.accept

    def helpbox(self):
        #self.ptimer.stop()
        if self.d['scan_type'] == 'email':
	    page = 'scanemail'
	else:
	    page = 'scanflash'
        hb=helpBox(page, self.d)
        hb.exec_()
        #self.ptimer.start()


