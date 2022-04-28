# -*- coding: windows-1251 -*-
from __future__ import division

import sys
import os
from time import sleep

from PyQt4.QtCore import QTimer,  QObject,  QString,  SIGNAL
import serial

d=[]

class _modem (QObject):
    
    def __init__(self, dd):
        global d
        d=dd
        QObject.__init__(self)
        self.openTimer = QTimer()
        self.ser=serial.Serial(baudrate=9600, 
                                    bytesize=serial.EIGHTBITS, 
                                    parity=serial.PARITY_NONE, 
                                    stopbits=serial.STOPBITS_ONE, 
                                    timeout=1, 
                                    xonxoff=False, 
                                    rtscts=False, 
                                    writeTimeout=None, 
                                    dsrdtr=False)
	self.portIsOpen=False
        self.openPort() 
    
    
    def findPort(self,name):
	port=d['modem_port']
	return port

    def openPort(self):
	port=self.findPort(d['modem_name'])
	self.portIsOpen=False
	#print port
	if port!='':
	    self.ser.port=port
            try:
	        if self.ser.isOpen():
        	    self.ser.close()
        	self.ser.open()
	    except:
        	print "Cant open MODEM port:", self.ser.port, sys.exc_info()[0]
        	self.openTimer.singleShot(500,  self.openPort)
	    else:
        	self.portIsOpen=True
        	#print "Modem is on"
        else:
	    #print "Modem is off"
	    pass

    

    def send(self,cmd):
	timeout=20
	answer=''
	buffer=''
	
	t=10
	while not self.portIsOpen and t>0:
	    sleep(0.5)
	    t-=1
        
        if t>0:
	    
	    w=self.ser.inWaiting()
	    if w>0:
		s=self.ser.read(w)
		#print "unhandled answer in modem buffer: %s" % s
	    
	    self.ser.write(cmd)
	    
	    t=timeout
	    while answer=='' and t>0:
		sleep(0.1)
		t-=1
		try:
        	    w=self.ser.inWaiting()
        	    #print "waiting=", w
		    if w>0:
			s = self.ser.read(w)
			#print s
    		except (RuntimeError, IOError,  serial.SerialException,  ValueError,  TypeError, NameError):
        	    print "Cant read from modem port:", sys.exc_info()[0]
        	    #self.openPort()
		else:
        	    if (w>0):
			buffer+=s
        	    else:
			if len(buffer)>0:
			    answer=buffer
	else:
	    answer='ERROR'

	return answer


    def wait(self,key):
	timeout=50
	answer=''
	buffer=''
	found=False
	
	t=10
	while not self.portIsOpen and t>0:
	    sleep(0.2)
	    t-=1
        
        if t>0:
	    self.ser.flushInput()
	    
	    t=timeout
	    while not found and t>0:
		sleep(0.1)
		t-=1
		try:
        	    w=self.ser.inWaiting()
        	    #print "waiting=", w
		    if w>0:
			s = self.ser.read(w)
			#print s
    		except (RuntimeError, IOError,  serial.SerialException,  ValueError,  TypeError, NameError):
        	    print "Cant read from modem port:", sys.exc_info()[0]
        	    #self.openPort()
		else:
        	    if (w>0):
			buffer+=s
        	    else:
			if len(buffer)>0:
			    answer=buffer
			posStart = answer.find(key)
			if posStart>0:
			    found = True
			else:
			    found=False
			    buffer=''
	if found:
	    answer=answer[posStart:]
	    posEnd = answer.find('\x0A')
	    answer=answer[:posEnd]
	else:
	    answer=''

	return answer
          
    
    def sendSMStest(self,n,text):
        print "Asking modem...%s" % (self.send('AT\r'))
	print self.send('AT+CMGF=1\r')
	print self.send('AT+CMGS="%s"\r' % (n))
	print self.send("%s\n" % (text))
	print self.send(chr(26))
	self.ser.close()
	return 1


    def sendSMS(self,n,text):
        t=10
        while ('OK' not in self.send('AT\r')):
	    sleep(0.5)
	    t-=1
        
        if (t>0) and ('OK' in self.send('AT+CMGF=1\r')):
	    self.send('AT+CMGS="%s"\r' % (n))
	    self.send("%s\n" % (text))
	    self.send(chr(26))
	    result=1
	else:
	    result=0
	
	self.ser.close()
	return result


    def getBalance(self):
	global d
	result=0
        t=10
        while ('OK' not in self.send('AT\r')):
	    sleep(0.5)
	    t-=1

        if (t>0):
	    if 'OK' in self.send("""AT+CUSD=1,*100#,15\r"""):
		answer=self.wait('+CUSD:')
		if answer:
		    balance=answer.split('zagal\'nyi')[1].split(';')[0]
		    d['mobile_balance'] = balance
		    print "ANSWER: %s" % answer
		    print "MOBILE BALANCE: %s" % balance
		    #print self.send(chr(26))
		    result=1
		else:
		    print "No answer for AT+CUSD command."
	    else:
		print "AT+CUSD command failed."
	self.ser.close()
	return result


    
    def close(self):
	self.ser.close()
	del(self)

