#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division

from PyQt4.QtCore import QTimer,  QObject,  QString,  SIGNAL, QThread
import serial
import sys
import os
import re
from time import sleep


key={
'0':'64',
'1':'51',
'2':'61',
'3':'71',
'4':'52',
'5':'62',
'6':'72',
'7':'53',
'8':'63',
'9':'73',
'up':'23',
'down':'87',
'left':'33',
'right':'34',
'menu':'21',
'enter':'22',
'start':'14',
'stop':'24',
'clear':'85',
'paper':'78',
'copier':'76',
'fax':'77',
'bri':'42',
'scaling':'32',
'sided':'86'
}

copier=''

pButtons=re.compile(r"[01]{3}[sS][kK]")
#pcomp=re.compile(r"[01]{3}[sS][kK][\|][0-9a-zA-Z \.\/\~\%\:\-\=\[\]\>]+[\|][0-9a-zA-Z \.\/\~\%\:\-\=\[\]\>]+[\|][bB][rR][dD][lL][jJ]")
#pline2=re.compile(r"[\|]{3}[sS][kK]")
pLeds=re.compile(r"[\|][bB][rR][dD][lL][jJ]")


class _copier (QObject):
    def __init__(self, d):
	global copier
        QObject.__init__(self)
        self.getTimer = QTimer()
        self.openTimer = QTimer()
        self.buffer=""
        self.empty=0
        self.off=0
        self.d=d
        self.port=d['copier_port']
        self.ser=serial.Serial(baudrate=38400, 
                                    bytesize=serial.EIGHTBITS, 
                                    parity=serial.PARITY_NONE, 
                                    stopbits=serial.STOPBITS_ONE, 
                                    timeout=0, 
                                    xonxoff=False, 
                                    rtscts=False, 
                                    writeTimeout=None, 
                                    dsrdtr=False)
	self.d['xerox_ok'] = False
	self.d['printer_ok'] = False
	self.d['catalog_ok'] = False
        self.d['scan_ok'] = False

	self.stateHaveChanges=False
	self.percentage="100%"
	self.quantity=''
	self.answer=''
	self.sided='1'
	self.c1=''
	self.c2=''
	self.settingName=''
	self.settingValue=''
	self.leds=[]
	self.paperUp='disabled'
	self.paperDown='disabled'
	self.paperRi='disabled'
	self.down='disabled'
	self.up='disabled'
	self.ri='disabled'
	self.working=0
	self.statusNoPaper=0
	self.state = 'off'
	#self.stateChanged('off')

	copier=self
	self.prep=_prep(self)
	self.prep.start()
	
	self.openPort()
    
    def terminate(self):
	self.prep.terminate()

    def openPort(self):
        try:
            self.ser.port=self.port
            if self.ser.isOpen():
                self.ser.close()
            self.ser.open() 
        except:
            #print "Cant open XEROX com-port:", sys.exc_info()[0]
            self.d['log'].log("XEROX: cant open com-port")
            self.openTimer.singleShot(2000,  self.openPort)
        else:
            self.ser.flushInput()
            self.ser.flushOutput()
            self.readSerial()
            self.d['log'].log("XEROX: com-port opened successfully")
            #self.copierLOG = open('copierLOG1','a')

    def time(self):
        self.getTimer.singleShot(100,  self.readSerial)

    def readSerial(self):
        try:
            w=self.ser.inWaiting()
            if w>0:
                s = self.ser.read(w)
        except (RuntimeError, IOError,  serial.SerialException,  ValueError,  TypeError, NameError):
            print "Cant read from XEROX com-port:", sys.exc_info()[0]
            self.d['log'].log("XEROX: cant read from com-port")
            self.openPort()
        else:
            if (w>0):
                self.buffer+=s
                self.empty=0
            else:
                self.empty+=1
                #self.d['log'].log(self.buffer)
	    
	    if ('\x0D' in self.buffer) or ('\x0A' in self.buffer) or (self.empty>0):
		if (len(self.buffer)>5):
        	    buf=self.buffer
        	    #print "BUFFER===%s" % buf
        	    buttons=''
        	    line1=''
        	    line2=''
        	    leds=''
        	    end=0
		    mButtons=pButtons.search(buf)
		    if mButtons:
			buttons=mButtons.group()
			i=mButtons.end()
			buf=buf[i:]
			
			mButtons=pButtons.search(buf)
			mLeds=pLeds.search(buf)
			if mLeds: 
			    if mButtons:
				if mLeds.start() < mButtons.start():
				    leds=mLeds.group()
				    buf=buf[:mLeds.start()]
				    end=mLeds.end()
				else:
				    end=mButtons.start()
				    buf=buf[:end]
			    else:
				leds=mLeds.group()
				buf=buf[:mLeds.start()]
				end=mLeds.end()
			elif mButtons:
			    end=mButtons.start()
			    buf=buf[:end]
			if end>0:
			    self.buffer=self.buffer[end+i:]

			if (len(buf)>0) and (buf.count('|') == 2):
			    sep1=buf.index('|')+1
			    sep2=buf[sep1:].index('|')+1
			    #print sep1, sep2
			    line1=buf[sep1:sep2].strip()
			    line2=buf[sep2+1:sep2+21].strip()
			    if end==0:
				end=sep2+21
				self.buffer=self.buffer[end+i:]
				#print self.buffer
			#print "buttons=%s line1=%s line2=%s leds=%s" % (buttons, line1, line2, leds)
			#self.copierLOG.write("buttons=%s line1=%s line2=%s leds=%s\n" % (buttons, line1, line2, leds))
			#self.d['log'].log("to parse: %s %s %s %s" % (buttons,line1,line2,leds))
			state=self.parse(buttons,line1,line2,leds)
			
			if (self.state != state) or (self.stateHaveChanges): #or (state=='ready' and self.waserror):
			    if (self.state in ['jam','paper']) and (state in ['printing','copying']) :
				self.click('stop')
				self.click('stop')
				self.click('stop')
				self.click('stop')
				self.click('stop')
				return 0
                	    if self.state=='off' and (state=='warming' or state=='ready'):
                		self.emit(SIGNAL('powerON'))
                		self.set('bri',self.d['xerox_brightness'])
                	    self.state=state;
                	    self.stateChanged(state);

		    
		    if (line1=='' and line2=='' and leds==''):
			self.off+=1
			if self.off>20:
        		    if self.state != "off":
        			try:
        			    answer = os.popen('lsusb | grep "0924:420c Xerox"')
				    on = answer.read()
				except:
				    on=''
			
				if not on: 
				    self.stateChanged('off')
				    self.emit(SIGNAL('powerOFF'))
        			self.off=0
		    else:
			self.off=0

	    if self.empty>30:
        	self.stateChanged('error')
        	self.empty=0            
        	self.openPort()
	    else:
		self.time()


    def init(self):
        if self.state=='ready':
	    self.prep.append('copier','')
	    self.prep.append('stop','')
	    #self.ser.write("85")
	    #self.ser.write("22")
	    return 0
	else: return 1

    def getState(self):
        return self.state;

    def wakeUp(self):
        if copier.state!='ready':
	    self.prep.append('stop','')
    
    def getReady(self):
        if copier.state!='ready':
	    self.prep.append('stop','')

    def zero(self):
	self.prep.append('zero','')

    def send_email(self,addr):
	self.prep.append('send_email',addr)

    def start(self):
	self.prep.append('start','')
	timeout=30
	#while (copier.state!='copying' and copier.state!='printing' and copier.state!='scanning') and (timeout>0):
	#    print copier.state
	#    sleep(0.1)
	#    timeout-=1
	if timeout>0:
	    result=1
	else: 
	    result=0
	print "copier.start returns %d" % result
	return result


    def set(self,cmd,param):
	if (cmd in ['n','sided','scaling','bri','answer','scan','paper','click']):
	    self.prep.append(cmd,param)

    def click(self,KEY):
	if KEY in key.keys():
	    self.set('click',KEY)

    def say(self,ans):
	self.set('answer',ans)
	#if self.answer==ans:
	#    self.ser.write(key['enter'])
	#else: 
	#    self.ser.write(key['right'])
	#    sleep(0.2)
	#    self.ser.write(key['enter'])

    def stateChanged(self, state):
        st="XEROX: %s " % (state)
        if state=='ready': 
	    st+="%s %s" % (self.percentage,self.quantity)
        elif state=='copying': 
	    st+="%s / %s" % (self.c1, self.c2)
        elif state.startswith('ask'): 
	    st+=self.answer
	elif state=='settings':
	    st+="%s %s" % (self.settingName, self.settingValue)
	print(st)
	self.d['log'].log(st)
        self.state=state
        self.emit(SIGNAL('stateChanged(QString)'), (state))
        self.stateHaveChanges=False
        
        if self.state in ['ready','sleeping','warming']:
	    self.d['xerox_ok'] = True
	    self.d['printer_ok'] = True
	    self.d['catalog_ok'] = True
	else: 
	    self.d['xerox_ok'] = False
	    self.d['printer_ok'] = False
	    self.d['catalog_ok'] = False

	if self.state in ['off','error','jam']:
	    self.d['scan_ok'] = False
	else: 
	    self.d['scan_ok'] = True

    

    def parse(self,buttons,line1,line2,leds):
	state=self.state
	
	if leds: self.leds.append(leds) #добавляем в список состояние индикаторов на панели аппарата
	if len(self.leds)>5:            #храним 5 значений
	    self.leds.pop(0)
	    up_ = 0                     #количество изменений в списке состояния индикатора верхнего лотка
	    down_ = 0                   #нижнего
	    ri_ = 0                     #бокового
	    up = self.leds[0][4]        #
	    down = self.leds[0][3]      #текущие(последние полученные) состояния индикаторов
	    ri = self.leds[0][2]        #
	    
	    for l in self.leds:         #подсчет количества изменений значения в последних 5 полученных состояниях индикаторов 
		if l[4] != up : 
		    up_ += 1
		    up = l[4]
		if l[3] != down : 
		    down_ += 1
		    down = l[3]
		if l[2] != ri : 
		    ri_ += 1
		    ri = l[3]
		    
	    if up_ < 1 and up =='l': self.up='disabled';
	    elif up_ < 1 and up =='L': self.up='ok';
	    elif up_ > 3 : self.up='empty'; self.d['paper_up']='0'

	    if down_ < 1 and down =='d' : self.down='disabled';
	    elif down_ < 1 and down =='D' : self.down='ok';
	    elif down_ > 3 : self.down='empty'; self.d['paper_down']='0'

	    if ri_ < 1 and ri =='r' : self.ri='disabled';
	    elif ri_ < 1 and ri =='R' : self.ri='ok';
	    elif ri_ > 3 : self.ri='empty';
	   
	    if self.down != self.paperDown : self.paperDown = self.down; self.stateHaveChanges=True; print "lotok DOWN: %s" % self.down;
	    if self.up != self.paperUp : self.paperUp = self.up; self.stateHaveChanges=True; print "lotok UP: %s" % self.up;
	    if self.ri != self.paperRi : self.paperRi = self.ri; self.stateHaveChanges=True; print "lotok RIGHT: %s" % self.ri;


	if (line1!='') and (line2!='') and (line1.find('?')<0) and (line2.find('[')>=0) and (line2.find(']')>=0) and (line1.find('...')<0):
	    state='settings'
	    if self.settingName!=line1.strip() or self.settingValue!=line2.strip(): self.stateHaveChanges=True
	    self.settingName=line1.strip()
	    self.settingValue=line2.strip()
	
	elif (line1.find("Pre-Scanning")>0):
	    state='scanning'


	elif True:
	    if line1=='Ready To Copy':
		state='ready'
		if line2.find('%')>0 or line2.startswith('Clone'):
		    temp=line2.split()
		    self.percentage=temp[0]
		    if len(temp)>1:
			quantity=temp[1]
		    else: 
			quantity=self.quantity
		else:
		    line2split = line2.split()
		    if len(line2split) == 3: 
			self.percentage=line2split[0]
			quantity=line2split[2]
		
		try:
		    quantityINT = int(quantity)
		except:
		    pass
		else:
		    if self.quantity != quantity: 
			self.stateHaveChanges=True
		    self.quantity=quantity
	    
	    elif line1=='Power Save Mode':
		state='sleeping'
	    
	    elif line1.startswith('Copying...'):
		state='copying'
		if len(line1.split())>1 and len(line1.split()[1].split('/'))>1:
		    if (self.c1,self.c2) != line1.split()[1].split('/'): 
			self.stateHaveChanges=True
		    (self.c1,self.c2)=line1.split()[1].split('/')
		else:
		    self.c1=''
		    self.c2=''
	    
	    elif line1.startswith('Printing...'):
		state='printing'
		if len(line1.split())>1 and len(line1.split()[1].split('/'))>1:
		    if (self.c1,self.c2) != line1.split()[1].split('/'): 
			self.stateHaveChanges=True
		    (self.c1,self.c2)=line1.split()[1].split('/')
		else:
		    self.c1=''
		    self.c2=''

	    
	    elif line1.startswith('Scanning...'):
		state='scanning'
		if line2.find('Side')>0:
		    self.scanSide=line2.split('Side')[1]
		else:
		    self.scanSide='1'
		print "scan SIDE: ", self.scanSide
		
	    elif line1.startswith('PC-Scan...'):
		state='pc-scan'

	    
	    elif line1=='Warming Up':
		state='warming'
	    
	    elif line1=='No Paper':
		self.statusNoPaper+=1
		if self.paperDown == 'empty' and self.paperUp == 'empty':
		    state='paper'
		else:
		    if self.statusNoPaper>5:
			self.set('paper','')
			self.statusNoPaper=0

	    elif line1=='No Toner':
		state='toner'
	    
	    elif line1=='Paper Jamming':
		state='jam'

	    elif line1=='Duplex Jam':
		state='jam'
	    
	    elif line1=='Paper Type':
		if self.state!='settings': self.ser.write(key['enter']); state='settings';

	    elif line1=='Scan Side 2?':
		if line2.find('Yes')==1:
		    state='askScanSide2'
		    if self.answer.find('yes')==-1: 
			self.stateHaveChanges=True
		    self.answer='yes'
		elif line2.find('No')==1:
		    state='askScanSide2'
		    if self.answer.find('no')==-1: 
			self.stateHaveChanges=True
		    self.answer='no'

	    
	    elif line1=='Scan Another?':
		if line2.find('Yes')==1:
		    state='askScanAnother'
		    if self.answer.find('yes')==-1: 
			self.stateHaveChanges=True
		    self.answer='yes'
		elif line2.find('No')==1:
		    state='askScanAnother'
		    if self.answer.find('no')==-1: 
			self.stateHaveChanges=True
		    self.answer='no'
	
	    elif line1=='Clear All Settings':
		if line2.find('Yes')==1:
		    state='clearAllSettings'
		    if self.answer.find('yes')==-1: 
			self.stateHaveChanges=True
		    self.answer='yes'
		elif line2.find('No')==1:
		    state='clearAllSettings'
		    if self.answer.find('no')==-1: 
			self.stateHaveChanges=True
		    self.answer='no'
	
	
	return state




class _prep (QThread):
    def init (self):
        QThread.__init__(self)
        self.cmdBuffer=[]

    def run(self):
	#self.timer.singleShot(100, self.sendN)
	self.cmdBuffer=[]
	while True:
	    if len(self.cmdBuffer)>0:
		(cmd,param)=self.cmdBuffer.pop(0)

		p=3
		while self.nextCMD(cmd,param)==0 and p>0:
		    p-=1

		if p==0:
		    print "EROOR executing command '%s' with param '%s' in the copier thread" % (cmd,param)
		    #self.d['log'].log("XEROX: ERROR executing command '%s' with param '%s' in the copier thread" % (cmd,param))
		
		if len(self.cmdBuffer)==0:
		    self.emit(SIGNAL("ok"))
	    sleep(0.05)
        #self.exec_()

    def append(self,cmd,param):
	self.cmdBuffer.append([cmd,param])

    def waitState(self,state,timeout=1):
	while copier.state!=state and timeout>0:
	    sleep(0.01)
	    timeout-=1
	if timeout>0:
	    return 1
	else: return 0


    def waitInValue(self,val,timeout=1):
	while (val in copier.settingValue)==False and timeout>0:
	    sleep(0.01)
	    timeout-=1
	if timeout>0:
	    return 1
	else: return 0

		

    def nextCMD(self,cmd,param):
	global copier
	
	result=0

	if cmd=='start':
	    if self.waitState('ready',1000)==1:
		print "copier ready. START COPYING...."
		#self.d['log'].log("XEROX: READY - START COPYING...")
		oldVal=copier.state
		copier.ser.write(key['start'])
		#result=1
		
		t=20
		while (oldVal==copier.state) and (t>0):
		    sleep(0.1)
		    t-=1
		if t>0:
		    result=1
		else: 
		    print "ERROR start copying...."
		    result=0
	    else:
		print "ERROR get ready to start...."
		#self.d['log'].log("XEROX: ERROR get ready to start")
		result=0

	
	elif cmd=='paper':
	    print "executing paper command...copier state is %s" % copier.state
	    if copier.state in ['paper','ready','warming','toner','settings','sleeping']:
		p=15
		while ((copier.paperUp == 'disabled') or (copier.paperDown == 'disabled')) and p>0:
		    oldUP=copier.paperUp
		    oldDOWN=copier.paperDown
		    copier.ser.write(key['paper'])
		    t=15
		    while (oldUP == copier.paperUp) and  (oldDOWN == copier.paperDown) and t>0:
			    sleep(0.5)
			    t-=1
		    p-=1
		
		if p==0: 
		    print "ERROR setting PAPER SOURCE"
		else: 
		    print "PAPER SOURCE set OK"
		    result=1
		
		

	elif cmd=='n':
	    num=str(param)
	    if self.waitState('ready',1500)==1:
		if int(copier.quantity)!=int(num):
		    if int(copier.quantity)!=1:
			copier.ser.write(key['clear'])
			sleep(0.1)
		    for n in num:
			copier.ser.write(key[n])
			sleep(0.07)
		t=100
		while int(copier.quantity)!=int(num) and t>0:
		    sleep(0.01)
		    t-=1
		if t>0:
		    print "NUMBER (success) set to: %s" %(copier.quantity)
		    result=1
		else:
		    print "NUMBER (ERROR) not set...: %s" %(copier.quantity)
		    copier.ser.write(key['stop'])
		    sleep(0.05)
		    result=0
	    else:
		print "ERROR get ready to set N...."
		result=0
		

	elif cmd=='sided':
	    if (copier.sided!=param):
		if self.waitState('ready',1000)==1:
		    copier.ser.write(key['sided'])
		    self.waitInValue('Sided',1000)

		    sided={'1':'1-1','2':'Short','3':'Long'}

		    p=10
		    while sided[param] not in copier.settingValue and p>0:
			print "need:", sided[param], "is: ", copier.settingValue
			copier.ser.write(key['sided'])
			oldVal=copier.settingValue
			t=10
			while oldVal==copier.settingValue and t>0:
			    sleep(0.1)
			    t-=1
			p-=1
                
		    if p>0:
			print "SIDED set to: %s" % (copier.settingValue)
			copier.sided=param
			sleep(0.05)
			copier.ser.write(key['enter'])
			sleep(0.15)
			copier.ser.write(key['enter'])
			result=1
		    else:
			print "ERROR set sided...."
			copier.ser.write(key['stop'])
			sleep(0.1)
			result=0
	    else:
		result=1


	elif cmd=='scaling':
	    if copier.percentage != param:
		p=10
		while ('25-400' not in copier.settingValue) and p>0:
		    copier.ser.write(key['scaling'])
		    oldVal=copier.settingValue
		    timeout=10
		    while oldVal==copier.settingValue and timeout>0:
		        sleep(0.05)
		        timeout-=1
		    p-=1

		if p>0:
		    for n in param[:-1]:
			oldVal=copier.settingValue
			copier.ser.write(key[n])
			t=50
			while oldVal==copier.settingValue and t>0:
			    sleep(0.05)
			    t-=1

		    sleep(0.05)
		    copier.ser.write(key['enter'])
		    sleep(0.15)
		    copier.ser.write(key['enter'])
		    print "SCALE set to = %s"  % (copier.settingValue)
		    result=1
		else:
		    print "ERROR set scale..."
		    copier.ser.write(key['stop'])
		    sleep(0.05)
		    result=0
	    else:
		result=1


	elif cmd=='bri':
	    if self.waitState('ready',2000)==1:
		p=10
		while ( (copier.state != 'settings') or ( int(param) != (len(copier.settingValue.split('[')[1].split(']')[0].split('\xff')[0]) + 1)) or (not ((']D' in copier.settingValue) and ('L[' in copier.settingValue))) )  and p>0:
		    copier.ser.write(key['bri'])
		    sleep(0.1)
		    oldVal=copier.settingValue
		    timeout=10
		    while oldVal==copier.settingValue and timeout>0:
		        sleep(0.1)
		        timeout-=1
		    p-=1
		if p>0:
		    p=5
		    while (copier.state == 'settings') and p>0:
			copier.ser.write(key['enter'])
			sleep(0.1)
			p-=1
                    result = 1


	elif cmd=='stop':
	    copier.ser.write(key['stop'])
	    result=1

	elif cmd=='start0':
	    oldVal=copier.state
	    copier.ser.write(key['start'])
	    t=100
	    while oldVal==copier.state and t>0:
	        sleep(0.01)
	        t-=1
            
            if t>0:
        	result=1
    	    else:
    		copier.ser.write(key['stop'])
    		result=0


	elif cmd=='scan':
	    # START SCANNING
	    os.system(str(param))
            result=1
	    

	elif cmd=='clear':
	    copier.ser.write(key['clear'])
	    result=1


	elif cmd=='zero':
	    sleep(0.01)
	    copier.ser.write(key['0'])
	    sleep(0.01)
	    copier.ser.write(key['0'])
	    sleep(0.01)
	    copier.ser.write(key['0'])
	    sleep(0.01)
	    result=1

	elif cmd=='answer':
	    if copier.answer==param:
	        copier.ser.write(key['enter'])
	        #print ".........sending key ENTER to copier as right answer..........."
	    else: 
		copier.ser.write(key['right'])
		sleep(0.2)
		copier.ser.write(key['enter'])
	    result=1


	elif cmd=='click':
	    if param in key.keys():
		copier.ser.write(key[param])
		sleep(0.2)
	    result=1


	elif cmd=='clearall':
	    copier.ser.write(key['stop'])
	    sleep(0.5)
	    copier.ser.write(key['clear'])
	    if self.waitState('clearAllSettings',100)==1:
		copier.answer('yes')
		if self.waitState('ready', 500)==1:
		    result=1

	elif cmd=='send_email':
	    answer = os.popen(str('ssmtp '+param+' < ./msg'))
	    answer = answer.read()
	    if answer:
		print answer
	    else:
		print "Email to %s was sent successfully." % param
		result=1
	
	return result
		
