from PyQt4.QtCore import QTimer,  QObject,  QString,  SIGNAL, QThread
import serial
import sys
from time import sleep
from modem import _modem

d=[]
timer1=1
timer2=1

class _sms (QThread):
    def __init__(self, dd):
        QThread.__init__(self)

        global d
        d=dd

	#self.log=file("log","a")

        self.start()


    def run(self):
	while True:
	    sleep(60)
	    self.time()
	

    def SMStext(self):
	s="N:<%s> Paper:%d\nChange(uah):%d ((50)%d, (25)%d, (5)%d)\nBox(uah):%d Stacker:%d\n" % (int(d['device']),int(d['paper']),
	    int(d['coinSumm'])//100,int(d['coinC50']),int(d['coinC25']),int(d['coinC5']),int(d['cashBoxSumm'])//100,
	    int(d['billSumm'])//100)
	return s


    def send_status(self):
	pass

    def time(self):
	global timer1
	global timer2
        #global d
        
        #print "call time func ", timer1, timer2 

        if (timer1==0) or (timer1 > int(d['sms1_period'])):
	    timer1 = int(d['sms1_period'])
	else:
	    if timer1==1:
		#print _modem(d).sendSMS(str(d['phone1']),self.SMStext())
		print "SEND SMS to: %s\n%s" % (d['phone1'],self.SMStext())
		timer1 = int(d['sms1_period'])
	    else:
		timer1-=1
	    

	if (timer2==0) or (timer2 > int(d['sms2_period'])):
	    timer2 = int(d['sms2_period'])
        else:
	    if timer2==1:
		#print _modem(d).sendSMS(str(d['phone2']),self.SMStext())
		print "SEND SMS to: %s\n%s" % (d['phone2'],self.SMStext())
		timer2 = int(d['sms2_period'])
	    else:
		timer2-=1

