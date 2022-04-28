#!/usr/bin/python
# -*- coding: windows-1251 -*-
from __future__ import division

import sys
sys.path.append('/usr/lib/openoffice/program')

import db
from log import _log

import os
import chardet
from PyQt4.QtCore import QPoint, QObject
from PyQt4.QtGui import QApplication, QWidget, QMouseEvent
#from PyQt4.QtSql import *
from copier import _copier
from cash import _cash
from modem import _modem
from sms import _sms
from ping import _net
from dialogs import *
import mail

from MainMenu import MainMenu


def writeSettings(params,  filename):
    fsock = open(filename, "w")
    fsock.write("\n".join(["%s=%s" % (k, v) for k, v in params.items()]))
    fsock.close()
    return d
    

def saveData(filename='./config'):
    global d
    print "call saveData()"
    
    fsock = open(filename, "w")

    for k in d['tabs']:
    	string="@%s\t\t*%s\t*%s\t\t" % (k, d['tabs'][k][1], d['tabs'][k][0].encode('utf-8'))
    	fsock.write(string)
    	sep='*'
    	for p in d['tabs'][k][2]:
	    fsock.write("%s%s" % (sep, p))
	    sep='/'
	fsock.write("\n")
    fsock.write("\n\n")

    for k in d['k']:
    	fsock.write("%s" % (d['paramline'][k]))
    	#fsock.write("#%s\n" % (d['n'][k].encode('utf-8')))
    	fsock.write("%s=%s\n\n" % (k, d[k]))
    fsock.close()



def readSettings(file):
    d={}
    n={}
    k=[]
    tabs={}
    params=[]
    d['paramline']={}
    encoding='utf-8'
    #encoding='windows-1251'
    try:
        fsock = open(file)
        lines=fsock.readlines()
        i=0
        while (i<len(lines)):
            if ('@' in lines[i]) and (lines[i][0]=='@'):
		t=lines[i][1:-1].split('*')
		key=t[0].strip()
		name=t[2].strip().decode(encoding)
		gif=t[1].strip()
		priv=t[3].split('/')
		tabs[key]=(name,gif,priv)
            elif ('#' in lines[i]) and (lines[i][0]=='#'):
                if ('/' in lines[i]):
		    mas=lines[i][1:-1].split('/')
		    reset=mas[1].split('*')[1:]
		    mas=mas[0]
		else: 
		    mas=lines[i][1:-1]
		    reset=[]
		mas=mas.split('*')
		name=mas[0].decode(encoding)
                line=lines[i+1].strip()
                if ('=' in line) and (line[0].isalpha()):
                    (key, param)=line.split("=")
                    if ('int' in mas[2]) or ('float' in mas[2]):
			d[key]=int(param)
			#print "int/float"
            	    else:
			d[key]=str(param)
			#print "text"
                    n[key]=name
                    k.append(key)
                    params.append([key,mas,reset])
                    d['paramline'][key]=lines[i]
                    i+=1
            i+=1
        fsock.close()
        d['n']=n				#names of parameters was read from config
        d['k']=k				#keys of parameters was read from config
        d['tabs']=tabs
        d['params']=params
    except IOError:
        print "no config file: %s" % file
    return d    

    
def readLang(file):
    l={}
    encoding='utf-8'
    try:
        fsock = open(file)
        lines=fsock.readlines()
        i=0
        while (i<len(lines)):
            if ('*' in lines[i]) and (lines[i][0]=='*'):
                encUA=chardet.detect(lines[i+2][1:-1])
                encRU=chardet.detect(lines[i+3][1:-1])
                ua=encUA['encoding']
                ru=encRU['encoding']
                if ua!='utf-8': ua='windows-1251'
                if ru!='utf-8': ru='windows-1251'
                key=lines[i][1:-1].decode(encoding)
                if key in l.keys():
		    print u'Key <%s> already in dict with phrase: <%s>' % (key, unicode(lines[i+1][0:-1],'utf-8'))
		    print u'phrase in file: <%s>' % (l[key]['ru'])
                l[key]={'ru':u"%s" % lines[i+1][0:-1].decode(encoding),  'ua':u"%s" % lines[i+2][0:-1].decode(encoding),  'en':u"%s" % lines[i+3][0:-1].decode(encoding)}
                i+=4
            i+=1
        fsock.close()
    except IOError:
        print "no config file: %s" % file
    return l


class myApp(QApplication):
    def __init__(self):
	QApplication.__init__()
	QApplication.installEventFilter(self)

    def eventFilter(self, obj, event):
	if event.type()==QEvent.KeyPress and event.key() == Qt.Key_Meta: #QEvent.KeyPress Windows_key:
	    self.screenshot()
	    print "screenShot made"
	    event.accept()
	return 0

    def screenshot(self):
        filename = './'+datetime.now().strftime("%Y%m%d_%H%M%S")+'.jpg'
        pixmap = QPixmap.grabWindow(self.desktop().winId())
        pixmap.save(filename)


if __name__ == "__main__":
    
    mailserver = 'mail.copyprime.tech'
    sender = 'info@copyprime.tech'
    pwd = 'cp2011'
    receiver = ['support@copyprime.tech']
    #receiver = ['hello@mymail']
    subj = 'CopyPrime START'
    txt = unicode(u'Отправлено для %s. Отсканированное изображение находится во вложении (%s)' % (str('txt'), str('txt'))).encode('cp1251')
    scan = []

    #mail.send_mail(sender, receiver, subj, txt, scan, mailserver, sender, pwd)



    configFileName='./config'
    d=readSettings(configFileName)
    
    writeSettings(d, "./config_")
    
    l=readLang("./lang")
 
    d['l']=l
    
    app = QApplication(sys.argv)
    app.setStyle("Plastique")
    #app.setStyle("cleanlooks")
    app.setStyleSheet(open("./main.qss","r").read())
    d['app'] = app
    d['log'] = _log(d)
    d['copier']=_copier(d)
    d['cash']=_cash(d)
    d['sms']=_sms(d)
    d['ping']=_net(d)
    d['xres']=d['app'].desktop().screenGeometry().right()
    d['yres']=d['app'].desktop().screenGeometry().bottom()
    #print d['xres'], d['yres']
    d['balance']= int(0)
    d['payoutEnabled']=False #######
    d['n_start']+=1
    d['lang'] = d['lang_start']
    #_modem(d).sendSMS('1234567890','Starting application...')
    #_modem(d).getBalance()

    app.w=MainMenu(d)
    
    d['main']=app.w
    d['saveData']=saveData
    #d['writeSQL']=writeSQL
    d['configFileName']=configFileName
    #saveData('config1')
    #d['cash'].payBack(255)
    #app.w.show()
    ###filterE=_filterE()
    ###app.installEventFilter(app)
    
    #d['action']=db.action(termId=d['device'],balance=0)
    #d['action'].finish()
    #del d['action']
    
    app.w.showFullScreen()

    runEventLoop=app.exec_()
    
    if runEventLoop==0:
	print "CLOSING APPLICATION..."
	d['copier'].terminate()
	d['cash'].terminate()
	d['sms'].terminate()
    
    sys.exit(runEventLoop)
