# -*- coding: utf-8 -*-
from __future__ import division

from PyQt4.QtCore import QTimer,  QObject,  QString,  SIGNAL, QThread
import serial
import sys
import os
from time import sleep
from modem import _modem
import conv
import subprocess
from os.path import *
from os import listdir, popen, statvfs
import mail

d=[]
officeTimer = 1
office_period = 5

pingTimer=5
ping_period = 5

balanceTimer = 300
balance_period = 3600

class _net (QThread):
    def __init__(self, dd):
        QThread.__init__(self)

        global d
        global ping_period
        global balance_period
        d=dd

	#self.log=file("log","a")
	self.oldList = self.getDevList()
	self.officeHasRestart = False

	self.pings=[]
        d['payment_ok'] = False
        d['DOP_ok'] = True
        ping_period = int(d['ping_period'])
        d['powerFailure'] = False

	self.powerTimer = QTimer()
        
        self.start()
    

    def run(self):
	while True:
	    sleep(1)
	    if self.deviceInserted(): pass
	    self.powerCheck()
	    self.mail()
	    self.time()
	

    def dontdisconnect(self):
	global balanceTimer
	global balance_period
	if balanceTimer < 120:
	    balanceTimer += 60

    def repeatPowerSignal(self):
	d['powerFailure'] = False
	self.powerTimer.start(1000)
	self.connect(self.powerTimer, SIGNAL("timeout()"), self.power)

    def powerCheck(self):
	global d
	powerON = int(open('/etc/acpower','r').read())
	if d['powerFailure']:
	    if powerON:
		d['powerFailure'] = False
	else:
	    if (not powerON):
		self.power()
	    else:
		if d['powerFailure'] == True:
		    d['powerFailure'] = False


    def power(self):
	global d
	self.powerTimer.stop()
	self.disconnect(self.powerTimer, SIGNAL("timeout()"), self.power)
	print "PING: EMIT SIGNAL POWER_FAILURE"
	d['powerFailure'] = True
	self.emit(SIGNAL("powerFailure()"))

    def time(self):
	global pingTimer
	global officeTimer
	global balanceTimer
	global ping_period
	global balance_period
	global office_period
        global d
        
        #print "call time func ", timer
        
        if (balanceTimer==0) or (balanceTimer > balance_period):
	    balanceTimer = balance_period
	elif balanceTimer==1:
	    balanceTimer = balance_period
	    subprocess.call(['poff','utel'])
	    sleep(3)
	    _modem(d).getBalance()
	    #sleep(2)
	    #subprocess.call(['pon','utel'])
	    #sleep(3)
	    self.pings=[]
	else:
	    balanceTimer-=1

        

        if (pingTimer==0) or (pingTimer > ping_period):
	    pingTimer = ping_period
	elif pingTimer==1:
	    pingTimer = ping_period

	    answer = os.popen('ping '+str(d['ping_address'])+' -c 1 -w 5 | grep "icmp_seq=1 ttl="')
	    ping = answer.read()
	    if ping: self.pings.append(1)
	    else: self.pings.append(0)
	    
     	    up_ = 0                     #количество изменений в списке состояния индикатора ping
            do_ = 0
            last = 0
	    
	    for p in self.pings:         #подсчет количества изменений значения в последних 5 полученных состояниях индикаторов 
		if p : up_ += 1;
		else: do_ += 1;
		last = p
		
	    if len(self.pings) > 5: self.pings.pop(0)

		    
	    if (do_ < 4  and  last == 1): 
		if d['payment_ok']==False:
		    d['payment_ok']=True; 
		    self.emit(SIGNAL("yes"))
		    d['log'].log('INTERNET ACCESSIBLE')
		    ping_period = int(d['ping_period'])
		    balance_period = 3600
		    print "inetOK";


	    elif (do_ > 4 and last == 0)  or (len(self.pings) == 1 and last == 0): 
		answer = os.popen('ps ax | grep "pppd call"')
		ppp_present = answer.read().split('\n')[-1]
		if 'grep' in ppp_present: ppp_present=''
		print "ppp_present: ", ppp_present
		
		if int(d['mobile_balance'].split(',')[0]) > 0: 
		    if not ppp_present and exists(d['modem_port']):
			subprocess.call(['sudo','-s','pppd','call', 'utel'])
			#subprocess.call(['pon','utel'])
			sleep(7)
			self.pings=[]
		    else:
			subprocess.call(['sudo','-s','kill',ppp_present.lstrip().split(' ')[0]])
			self.pings=[]
		else:
		    print "INET CAN NOT START.... BALANCE IS ZERO"
		    ping_period = 60
		    #balanceTimer = 1
		    balance_period = 300

		answer = os.popen('netstat -r -n | grep ppp')
		ppp_present = answer.read().split('\n')[0]
		print "ppp_present: ", ppp_present

		if not ppp_present and d['payment_ok']==True:
		    d['payment_ok']=False; 
		    self.emit(SIGNAL("no"))
		    d['log'].log('INTERNET FAILED')
		    print "ineta NET";

        else: 
	    pingTimer -= 1;


        if (officeTimer==0) or (officeTimer > office_period):
	    officeTimer = office_period
	elif officeTimer==1:
	    officeTimer = office_period

	    answer = os.popen('ps ax | grep "soffice"')
	    proc = answer.read()
	    if 'soffice.bin' not in proc:
		print proc
		print "OpenOffice.org if not running. Restarting..."
		#subprocess.call(['soffice', '-headless', '-norestore', '-accept="socket,host=127.0.0.1,port=8100;urp;"'])
		os.popen('soffice -headless -norestore -accept="socket,host=127.0.0.1,port=8100;urp;"')
		self.officeHasRestart = True
		officeTimer = 3
	    else:
		if self.officeHasRestart or (('converter' not in d.keys()) or d['converter'] == None): 
		    print "No converter or office restart. Creating..."
		    d['converter']= conv.DocumentConverter() 
		    self.officeHasRestart = False
	else: 
	    #print "self.officeHasRestart", self.officeHasRestart
	    #print "converter not in d.keys()",('converter' not in d.keys()) 
	    #print "d[converter] == None", d['converter'] == None
	    officeTimer -= 1;

    def mail(self):
	global d
	if 'email_message' in d.keys():
	    msg = d['email_message']
	    try:
		mail.send_mail(msg['sender'], msg['receiver'], msg['subj'], msg['txt'], msg['attach'], msg['mailserver'], msg['sender'], msg['pwd'])
	    except:
		print "error sending mail"
	    else:
		print "mail was sent successfully"
	    del(msg)
	    del(d['email_message'])

    def deviceInserted(self):
	global d
        self.currentList = self.getDevList()
        if ('insertedDeviceName' in d.keys()) and (d['insertedDeviceName'] in self.currentList):
	    return True
        elif len(self.currentList) > len(self.oldList):
            for i in self.currentList:
        	if i not in self.oldList:
        	    d['insertedDeviceName'] = i
        	    self.oldList = self.currentList
        	    return True
        else: 
	    if 'insertedDeviceName' in d.keys(): 
		del(d['insertedDeviceName'])
	    self.oldList = self.currentList
            return False

    def getDevList(self):
	answer = popen('lsusb')
	devList = answer.read().split('\n')
	return devList
