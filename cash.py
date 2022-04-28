# -*- coding: windows-1251 -*-
from __future__ import division

import sys
import os
from time import sleep

from PyQt4.QtGui import QApplication,  QWidget,  QListWidgetItem
from PyQt4.QtCore import QTimer,  QObject,  QString,  SIGNAL
import serial

d=[]
com=''
retry=0
cmdBuffer=[]
billStacker=0
billState=''
billAccEnabled=False
billSetup=[]
billNominal=[1, 2, 5, 10, 20, 50, 100, 200] #{'01':1, '02':2, '05':5, '0A':10, '14':20, '32':50, '64':100, 'C8':200}
billEnabled=[True, True, True, True, True, True, True, False] #{'01':'True', '02':'True', '05':'True', '0A':'True', '14':'True', '32':'True', '64':'True', 'C8':'False'}
maxSumm=0
coinTubes=[0, 0, 0, 0]
coinTubesNom=[5, 5, 25, 50]
tubeNominal=[50, 25, 5]         #Номиналы в тубах
tubeType={50:3, 25:2, 5:0}      #номиналы и номера туб
coinState='ready'
coinAccEnabled=False
coinSetup=[]
coinNominal=[5, 10, 25, 50, 100] #{'05':5, '0A':10, '19':25, '32':50, '64':100}
coinEnabled=[True, False, True, True, True, False, False, False] #{'05':'True', '0A':'True', '19':'True', '32':'True', '64':'True'}

class _cash (QObject):
    
    def __init__(self, dd):
        global d
        d=dd
        self.d = dd
        
        QObject.__init__(self)
        self.getTimer = QTimer()
        self.openTimer = QTimer()
        self.buffer=""
        self.empty=0
        self.resetTime=0
        
        
        
        self.ser=serial.Serial(baudrate=38400, 
                                    bytesize=serial.EIGHTBITS, 
                                    parity=serial.PARITY_NONE, 
                                    stopbits=serial.STOPBITS_ONE, 
                                    timeout=0, 
                                    xonxoff=False, 
                                    rtscts=False, 
                                    writeTimeout=None, 
                                    dsrdtr=False)
        self.openPort()
        self.calcCoinSumm()

    def terminate(self):
	pass
    

    def calcCoinSumm(self):
	global d
	summ=0
        for nom in tubeNominal:
            name="coinC%d" % (nom)  #name
            summ+=d[name]*nom            #количество монет номинала nom
	d['coinSumm']=summ

    
    def openPort(self):
        try:
            self.ser.port=d['cash_port']                                  
            if self.ser.isOpen():
                self.ser.close()
            self.ser.open() 
        except:
            print "Cant open cash com-port:", sys.exc_info()[0]
            self.d['log'].log("CASH: Cant open com-port")
            self.openTimer.singleShot(2000,  self.openPort)
        else:
            self.ser.flushInput()
            self.readSerial()
            self.d['log'].log("CASH: com-port opened successfully")

    
    def time(self):
        self.getTimer.singleShot(200,  self.readSerial)


    def readSerial(self):
        try:
            w=self.ser.inWaiting()
            if w>0:
                s = self.ser.read(w)
        except (RuntimeError, IOError,  serial.SerialException,  ValueError,  TypeError, NameError):
            print "Cant read from com-port:", sys.exc_info()[0]
            self.d['log'].log("CASH: Cant read from com-port")
            self.openPort()
        else:
            if (w>0):
                self.buffer+=s
                self.empty=0
            else:
                self.empty+=1
                if self.empty>20:
                    self.pollIsStopped()
                    self.empty=0

            #while (len(self.buffer)>5 (">" in self.buffer)) :
            #    posStart=self.buffer.index(">")
            #    
            #    oper=self.buffer[0:posEOL]
            #    self.buffer=self.buffer[posEOL+2:]
            #    self.recognizeAnswer(oper)

            while ("\x0D\x0A" in self.buffer) :
                posEOL=self.buffer.index("\x0D\x0A")
                oper=self.buffer[0:posEOL]
                if '>' in oper:
		    posStart=oper.index(">")
		    oper=oper[posStart:]
		self.buffer=self.buffer[posEOL+2:]
		self.recognizeAnswer(oper)


            self.time()
    
    
    def pollIsStopped(self):
        print "(cash)POLL is STOPPED... Sending \'p\'..."
        self.d['log'].log("CASH: poll is stopped. Sending \'p\'...")
        self.ser.write('\x0A\x0Ap')
    
    
    def send(self, bytes):
        global cmdBuffer
        mas=bytes.split()
        cmd=''
        crc=0
        
        for i in mas:
            n=int(i, 16)
            crc+=n
            cmd+=(i+" ")
        
        crc="%x" % crc
        if len(crc)==1: 
            a="0"
        else: a=''
        
        crc=a+crc[-2:]
        
        cmd+=crc
        cmd+='\x0A'
        
        cmdBuffer.append(cmd)
        if len(cmdBuffer)==1:
            self.sendCmd()
    
    
    def sendCmd(self):
        if len(cmdBuffer)>0:
            cmd=cmdBuffer[0]
            try:
        	self.ser.write(cmd)
	    except:
		print "CANT send to cash-port. DATA:", cmd
		self.d['log'].log("CASH: Cant send data: %s" % cmd)


    def sendNextCmd(self):
        if len(cmdBuffer)>0: 
            cmdBuffer.pop(0)
        if len(cmdBuffer)>0: 
            self.sendCmd()
    
    
    def enableCoin(self):
        self.send('0C FF FF 00 00')
    
    def disableCoin(self):
        self.send('0C 00 00 00 00')
    
    def enableBill(self):
        self.send('34 FF FF FF FF')

    def disableBill(self):
        self.send('34 00 00 00 00')
    
    def stop(self):
        global billAccEnabled
        global coinAccEnabled
        billAccEnabled=False
        coinAccEnabled=False
        self.disableBill()
        self.disableCoin()
        

    
    def summAdded(self, summ):
        global d

        d['balance']+=int(summ)

        if ('action' in d.keys()) and d['action']:
	    s = int(summ)/100
	    d['action'].insumm += s
	    d['action'].money = d['action'].money + " +" + "%3.2f" % (s)
	else:
	    self.d['log'].log("CASH: balance added BUT no action created yet...")

        self.emit(SIGNAL("balanceAdded(int)"), (summ))
        self.d['log'].log("CASH: EMIT SIGNAL balanceAdded(int). summAdded=%d, balanceAfter=%d" % (summ, d['balance']))
        

    
    def payBack(self, summ):
        global d
        c={}
        summPay=summ
        print "summ for payback: %5.2f" % (summ/100)
        self.d['log'].log("CASH: summ for payback: %5.2f" % (summ/100))
        d['payoutEnabled']=False
        
        for nom in tubeNominal:
            name="coinC%d" % (nom)  #name
            c[nom]=summ//nom            #количество монет номинала nom
            if d[name]<=c[nom]:             #если такого кол нет в наличии
                summ-=d[name]*nom       #выдаем сколько есть
            else:
                summ-=c[nom]*nom
        
        if summ>0:
            if d['coinC5']==0:
                print 'Change is over... summ=%2.2f' % (summ/100)
                self.d['log'].log("CASH: Change is over... summ=%2.2f" % (summ/100))
            else:
                print "ERROR. The change don't divide by 5... summ=%2.2f" % (summ/100)
                self.d['log'].log("CASH: The change don't divide by 5... summ=%2.2f" % (summ/100))
            self.emit(SIGNAL('cantGiveChange(int)'), (summ))
        else: 
                
            s=0
            for nom in tubeNominal:
                a=int(c[nom]//15)
                for i in range(a): 
                    self.send('0D F3')          # выплата 15 монет
                self.send("0D %x%x" % (c[nom]-a*15, tubeType[nom]))
                name="coinC%d" % (nom)
                d[name]-=c[nom]
                if d[name]<1: 
                    self.emit(SIGNAL('coinTubeEmpty()'), (nom))
                s+=c[nom]*nom
                print "pay %d coins by nominal %d - summ: %5.2f" % (c[nom],  nom,  (c[nom]*nom)/100)
                self.d['log'].log("CASH: pay %d coins by nominal %d - summ: %5.2f" % (c[nom],  nom,  (c[nom]*nom)/100))

            print ">>>ALL: %5.2f" % (s/100)
            self.d['log'].log("CASH: PAYED CHANGE: %5.2f" % (s/100))

            d['balance']-=int(summPay)

            if ('action' in d.keys()) and d['action']:
		d['action'].change+=int(summPay)/100

            self.calcCoinSumm()
            if 'main' in self.d.keys(): self.d['main'].update()
            self.emit(SIGNAL('changeOK()'))
            print"changeOK"


    def get(self, summ):
        global maxSumm
        global billAccEnabled
        global coinAccEnabled
        maxSumm=summ
        billAccEnabled=True #разрешаем прием всех купюр
        coinAccEnabled=True #разрешаем прием всех монет
        self.enableCoin()

    def fillTubesState(self,state):
        global billAccEnabled
        global coinAccEnabled
	if state:
	    billAccEnabled=False #разрешаем прием всех купюр
	    coinAccEnabled=True #разрешаем прием всех монет
	    self.enableCoin()
	    self.temp_balance = self.d['balance']
	else:
	    billAccEnabled=False #разрешаем прием всех купюр
	    coinAccEnabled=False #разрешаем прием всех монет
	    self.disableCoin()
	    self.d['balance'] = self.temp_balance


    def recognizeAnswer(self, ans):
        global d
        global com
        global cmdBuffer
        global maxSumm
        global billState
        global billAccEnabled
        global billNominal
        global billEnabled
        global coinState
        global coinAccEnabled
        global coinNominal
        global coinEnabled
        global retry
        

        #print "answer: %s" % ans
        if ans.startswith('>'): #commands
            com=ans[1:3]
            #if com.startswith('>'):######################################################???
	    #com=com[1:]
         
            if '<' in ans:          #poll answer
                ans=ans[5:].split()
                #print "com:%s, ans:%s" % (com, ans)
                if com=='33' and len(ans)>0:    #poll answer from bill validator
                    
                    if len(ans)>1:
                        ans=ans[:-1]
                    state=billState
                    
                    if self.resetTime>0: 
                        ans=''
                        self.resetTime-=1
                        print self.resetTime
                    elif billState=='justreset': 
                        self.send('31') #send bill setup
                        self.send('09') #send coin setup                       
                        
                    for a in ans:
                	try: 
                	    value=int(a, 16)
                	except:
                	    break

                        if a=='00':
                            if billAccEnabled:
                                state='ready'
                            else:
                                self.disableBill()
                        elif a=='FF':
                            state='disconnected'                    
                        elif a=='03':
                            state='busy'
                        elif a=='09':
                            if billAccEnabled:
                                self.enableBill()
                            else: 
                                state='disabled'
                        elif a=='06':
                            state='justreset'
                            self.resetTime=45
                        elif a=='07':                   #bill removed
                            self.emit(SIGNAL('billRemoved()'))
                        elif a=='02' or a=='03' or a=='04' or a=='05' or a=='08': #error 
                            state='error'
                        elif int(a, 16)>127:
                            bit=bin(int(a, 16))[2:]
                            routing=int(bit[1:4], 2)
                            type=int(bit[4:8], 2)
                            if type<len(billNominal): 
                                nominal=billNominal[type]
                            else:
                                nominal=0
                            if routing==0:      #bill stacked
                                self.summAdded(nominal*100)
                                d['billSumm']+=nominal*100
                                d['billStacker']+=1
                                d['billN%d'%(nominal)]+=1
                                d['n_all_money']+=nominal*100
                                print "-Bill accepted to STACKER."
                                self.d['log'].log("CASH: BILL ACCEPTED to STACKER: %d" % (nominal))
                            elif routing==1:    #bill in escrow position
                                print "BILL INSERTED - type %s, nominal: %d" % (type,  nominal)
                                self.d['log'].log("CASH: BILL INSERTED: %d" % (nominal))
                                if (maxSumm < nominal*100) or (billEnabled[type]==False):
                                    self.send('35 00') # back
                                    print "-return. The nominal(%d) greater then allowed(%d)." % (nominal, maxSumm)
                                    self.d['log'].log("CASH: RETURN: The nominal(%d) greater then allowed(%d)." % (nominal, maxSumm))
                                else: 
                                    self.send('35 01') # accept
                                    print "-accept."
                            elif routing==10:    #returned
                                print "-Bill(billNominal[type]) returned to CUSTOMER."
                        if state!=billState:
                            billState=state
                            self.emit(SIGNAL('billStateChanged(QString)'), (state))
                            print "BILL state: %s" % state

                if com=='0B' and len(ans)>0:    #poll answer from coin acceptor
		    #print "cash:", ans
                    if len(ans)>1:
                        ans=ans[:-1]
                    state=coinState
                    for a in ans: 
                    	try: 
                	    value=int(a, 16)
                	except:
                	    break

                        bit=bin(int(a, 16))[2:].zfill(8)
                        ##print "coin %s" % (bit)
                        if a=='00':
                            if coinAccEnabled==True and coinState=='disabled':
                                self.enableCoin()
                                state='ready'
                            elif coinAccEnabled==False and coinState=='ready':
                                self.disableCoin()
                                state='disabled'
                            elif coinState=='payout':
                        	state='disabled'
                        	print "state <payout> finish"
                        	self.emit(SIGNAL('payoutFinished()'))
                        elif a=='FF':
                            state='disconnected'
                        elif a=='0A':
                            state='busy'
                        elif a=='09':
                            state='disabled'
                        elif a=='0B':
                            state='disabled'  # just reset
                            self.send('09') #send coin setup
                        elif a=='07':                   #coin removed
                            state='coin rejected'
                        elif a=='02':
                            state='payout'
                            print "catch state <payout>"
                            if coinState != 'payout':
                        	self.emit(SIGNAL('payoutStarted()'))
                        elif a=='03' or a=='04' or a=='05' or a=='08': #error 
                            state='error'
                        elif bit[0:2]=='01':
                            routing=int(bit[3:4], 2)
                            type=int(bit[4:8], 2)
                            if type<len(coinNominal):
                                nominal=coinNominal[type]
                        	print "coin type: %s, coin nominal: %d" % (type,  nominal)
                        	if routing==0:      #COIN accepted to CASH BOX
                            	    self.summAdded(nominal)
                            	    d['cashBoxSumm']+=nominal
                            	    print "coin accepted to CASHBOX"
                            	    self.d['log'].log("CASH: COIN nominal(%d) accepted to CASHBOX." % (nominal))
                        	elif routing==1:    #COIN accepted to TUBE
                            	    name="coinC%d" % (nominal)
                            	    if name in d.keys():
                            		d[name]+=1
                            	    else:
                            		print "wrong nominal!!!!!!!! (cash-coinAccept)"
                            	    self.calcCoinSumm()
                            	    self.summAdded(nominal)
                            	    print "coin accepted to TUBE, coinSumm=",d['coinSumm']
                            	    self.d['log'].log("CASH: COIN nominal(%d) accepted to TUBE." % (nominal))
                        	elif routing==11:    #rejected
                            	    print "coin rejected"
                            	    self.d['log'].log("CASH: COIN rejected.")
                            else:
                                nominal=0 #coinNominal[type-11]
                        	print "Payout coin type: %s, coin nominal: %d" % (type,  nominal)

                            break
                        if state!=coinState:
                            coinState=state
                            self.emit(SIGNAL('coinStateChanged(QString)'), (state))
                            print "COIN state: %s" % state


        elif ans.startswith('<'): #answer
            ans=ans[1:].split()
            
            if len(ans)==1:
                if ans[0]=='00':
                    self.sendNextCmd()
                elif ans[0]=='FF' or ans[0]=='FE':
                    if len(cmdBuffer)>0: 
                        if retry<10: 
                            self.sendCmd()
                            retry+=1        # if error - retry send cmd
                        else:
                            failedCmd=cmdBuffer.pop(0)
                            retry=0
                            print "ERROR executing command %s" % (failedCmd)
                            self.d['log'].log("CASH: ERROR executing command %s" % (failedCmd))
            
            elif com=='31' and len(ans)==28 :           #answer for 31H - BILL SETUP - 27 HEX bytes
                print "BILL SETUP"
                self.sendNextCmd()
            
            elif com=='36' and len(ans)==3 :           #answer for 36H - STACKER STATUS - 2 HEX bytes
                bit=bin(int(ans[0:2], 16))[2:].zfill(16)
                if bit[0]=='1':
                    billState='stackerFull'
                    self.emit(SIGNAL('billStateChanged(QString)'), (billState))
                    self.d['log'].log("CASH: STACKER FULL")
                self.sendNextCmd()

            elif com=='09' and len(ans)==13 :           #answer for 09H - COIN SETUP - up to 23 HEX bytes
                print "COIN SETUP"
                self.sendNextCmd()
                
            elif com=='0A' and len(ans)==19 :           #answer for 0AH - TUBE STATUS - 18 HEX bytes
                self.sendNextCmd()

            else:
                if len(cmdBuffer)>0:
                    print "Unknown answer for command %s. Answer is: %s" % (cmdBuffer[0],  ans)
                    self.d['log'].log("CASH: Unknown answer for command %s. Answer is: %s" % (cmdBuffer[0],  ans))
                self.sendNextCmd()
                    

