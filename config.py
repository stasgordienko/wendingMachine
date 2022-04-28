# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from spins import intSpinBox, floatSpinBox, intSpinBoxNE, floatSpinBoxNE, textBox, selectBox, _file
from modem import _modem

class _confirmChanges(QDialog):
    def __init__(self, cl):
        QDialog.__init__(self)
        #self.setModal(True)
        self.setAutoFillBackground(False)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        label=QLabel(cl.decode('utf-8'),self)
        label.setGeometry(1,1, 1023, 600)
        label.setAlignment(Qt.AlignLeft)
        #label.setFont(QFont("Helvetica", 45, 75))
        
        yes=QPushButton(u"ПОДТВЕРДИТЬ ИЗМЕНЕНИЯ",self)
        yes.setGeometry(100,650,200,50)
        self.connect(yes, SIGNAL("clicked()"), self, SLOT("accept()"))
        
        no=QPushButton(u"ВОЗВРАТ",self)
        no.setGeometry(300,650,200,50)
        self.connect(no, SIGNAL("clicked()"), self, SLOT("reject()"))
        no.setDefault(True)
        
        self.showFullScreen()
        #self.exec_()


class _passwordCheck(QDialog):
    def __init__(self, d):
        QDialog.__init__(self)
        self.setAutoFillBackground(False)
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.d=d
        l=d['l']
        lang=d['lang']

        self.dig=4
        self.pos=0
        self.a=['.']*self.dig

        bx=(d['xres']-300)//2
        c1=bx
        c2=bx+80
        c3=bx+160       

        by=240
        r1=by
        r2=by+80
        r3=by+160
        r4=by+240

        self.bgroup=QButtonGroup(self)

        self.b1=QPushButton(self)
        self.b2=QPushButton(self)
        self.b3=QPushButton(self)
        self.b4=QPushButton(self)
        self.b5=QPushButton(self)
        self.b6=QPushButton(self)
        self.b7=QPushButton(self)
        self.b8=QPushButton(self)
        self.b9=QPushButton(self)
        self.b0=QPushButton(self)
        self.b_erase=QPushButton(self)
        self.b_enter=QPushButton(self)

        self.b1.setGeometry(QRect(c1, r1, 75, 75))
        self.b2.setGeometry(QRect(c2, r1, 75, 75))
        self.b3.setGeometry(QRect(c3, r1, 75, 75))
        self.b4.setGeometry(QRect(c1, r2, 75, 75))
        self.b5.setGeometry(QRect(c2, r2, 75, 75))
        self.b6.setGeometry(QRect(c3, r2, 75, 75))
        self.b7.setGeometry(QRect(c1, r3, 75, 75))
        self.b8.setGeometry(QRect(c2, r3, 75, 75))
        self.b9.setGeometry(QRect(c3, r3, 75, 75))
        self.b0.setGeometry(QRect(c2, r4, 75, 75))
        self.b_erase.setGeometry(QRect(c3, r4, 75, 75))
        self.b_enter.setGeometry(QRect(c1, r4, 75, 75))

        self.but={}
        self.but[0]=self.b0
        self.but[1]=self.b1
        self.but[2]=self.b2
        self.but[3]=self.b3
        self.but[4]=self.b4
        self.but[5]=self.b5
        self.but[6]=self.b6
        self.but[7]=self.b7
        self.but[8]=self.b8
        self.but[9]=self.b9

        for x in range(10):
            self.but[x].setText(str(x))
            self.bgroup.addButton(self.but[x],x)

        self.connect(self.bgroup, SIGNAL("buttonClicked(int)"), self.digit)
        self.connect(self.b_erase, SIGNAL("clicked()"), self.bs)
        self.b_erase.setEnabled(False)

        self.connect(self.b_enter, SIGNAL("clicked()"), self.enter)
        self.b_enter.setText("#")
        self.b_enter.setEnabled(False)

        self.b_close=QPushButton(self)
        self.b_close.setGeometry(QRect((d['xres']-70), 10, 50, 50))
        self.connect(self.b_close,  SIGNAL("clicked()"),  self.close)

        self.showFullScreen()
        #self.update()


    def digit(self,d):              #Нажатие цифры
        #print  d
        if self.pos==0:
            self.b_erase.setEnabled(True)
        if self.pos<self.dig: 
            self.a[self.pos]=d
            self.pos=self.pos+1;
            if self.pos==self.dig:
               self.b_enter.setEnabled(True)
               for x in range(10):
                  self.but[x].setEnabled(False)
            #self.update()


    def update(self):
        pass


    def bs(self):                         #Нажатие BackSpase
        if (self.pos>0):
            if self.pos==self.dig: 
                self.b_enter.setEnabled(False)
            for x in range(10):
                self.but[x].setEnabled(True)
            self.pos=self.pos-1
            self.a[self.pos]='.'
        if self.pos==0:
            self.b_erase.setEnabled(False)
        #self.update()


    def enter(self):                          #Нажатие кнопки Enter
        self.b_enter.setEnabled(False)
        n="";
        if self.pos == self.dig: 
            for x in self.a:
                n=n+str(x)
        else: n="0"
        #print n
        if n==self.d['pwda']: 
            self.d['config_auth']='admin'
        elif n==self.d['pwds']:
            self.d['config_auth']='service'
        elif n==self.d['pwdc']: 
            self.d['config_auth']='cash'
        else: 
            self.close()
            return 0

        self.d['config'] = _config(self.d)    #Создание окна config
        self.d['config'].showFullScreen()     #Окно config на полный экран
        self.close()                          #Закрытие окна ввода пароля

    def back(self):
        self.close()


class _keyboard(QWidget):   #Виртуальная клавиатура
    def __init__(self,d):
        QWidget.__init__(self)
        

class myTabWidget(QWidget):
    def __init__(self,d,name):
        QWidget.__init__(self)
        self.d = d
        self.name = name
        self.controls = {}

    def showEvent(self, event):
	if 'cash' in self.name:
	    self.d['cash'].fillTubesState(True)
	    self.connect(self.d['cash'], SIGNAL("balanceAdded(int)"), self.recalc)
	    print "enter in cash"
	event.accept()

    def hideEvent(self, event):
	if 'cash' in self.name:
	    self.d['cash'].fillTubesState(False)
	    self.disconnect(self.d['cash'], SIGNAL("balanceAdded(int)"), self.recalc)
	    print "leave cash"
	event.accept()

    def closeEvent(self, event):
	if 'cash' in self.name:
	    self.d['cash'].fillTubesState(False)
	    self.disconnect(self.d['cash'], SIGNAL("balanceAdded(int)"), self.recalc)
	    print "leave cash"
	event.accept()
	
    def recalc(self,summ):
	for c in self.controls.keys():
	    if 'coin' in c:
		self.controls[c].setValue(self.d[c])
    
    

class _config(QTabWidget):
    def __init__(self,d):
        QTabWidget.__init__(self)

        self.d=d
        self.l=d['l']
        self.n=d['n']
        self.lang=d['lang']
        self.wl=[]

	self.tabs={}

        self.setIconSize(QSize(50, 50))
        self.setTabPosition(QTabWidget.South)
        
        nameFont = QFont('FreeSans',16,50)


        for k in d['tabs'].keys():
	    name=d['tabs'][k][0]
	    icon=d['tabs'][k][1]
	    priv=d['tabs'][k][2]
	    tab=myTabWidget(d,k)
	    tab.controls={}
	    tab.setGeometry(QRect(1,1, d['xres'], d['yres']-70))
	    tab.x=10
	    tab.y=10
	    self.tabs[k]=tab
	    #print name
	    
	    if d['config_auth'] in priv:
		#tab.show()
		self.addTab(tab, QIcon(icon), unicode(name))
	    else:
		pass
		#tab.hide()
	    
        lastReset=None
        
        for (param,mas,reset) in d['params']:
	    name=mas[0]
	    tab=mas[1]
	    page=self.tabs[tab]
	    if (len(self.wl)>0):
		if (hasattr(self.wl[len(self.wl)-1], 'b_reset')):
		    lastReset=self.wl[len(self.wl)-1].b_reset
	    if (reset!=[]):
		if (len(reset)==1) and (lastReset!=None):
		    reset=(lastReset,reset[0])
	    
	    if len(mas)>2:
	    
		if mas[2] in ('int','float'):
		    min=int(mas[3])
		    max=int(mas[4])
		    step=int(mas[5])
		    val=d[param]
		    if mas[2]=='int':
			page.control=intSpinBox(page, prop=param, name=name, value=val, minimum=min, maximum=max, step=step, reset=reset)
		    else:
			page.control=floatSpinBox(page, prop=param, name=name, value=val, minimum=min, maximum=max, step=step, reset=reset)
		    page.control.setFont(nameFont)
		    page.control.setGeometry(QRect(page.x,page.y,500,60))
		    page.controls[param]=page.control
		    self.wl.append(page.control)
		    if page.y > (self.d['yres'])-200: 
        		page.x+=600
			page.y=10
		    else:
			page.y+=95

		elif mas[2] in ('intNE', 'floatNE'):
		    val=d[param]
		    if mas[2]=='intNE':
			page.control=intSpinBoxNE(page, prop=param, name=name, value=val, reset=reset)
		    else:
			page.control=floatSpinBoxNE(page, prop=param, name=name, value=val, reset=reset)
		    page.control.setFont(nameFont)
		    page.control.setGeometry(QRect(page.x,page.y,500,60))
		    page.controls[param]=page.control
		    self.wl.append(page.control)
		    if page.y > (self.d['yres'])-200: 
        		page.x+=600
			page.y=10
		    else:
			page.y+=95


		elif mas[2] in ('text'):
		    val=d[param]
		    l=int(mas[3])
		    page.control=textBox(page, prop=param, name=name, value=val, l=l)
		    page.control.setFont(nameFont)
		    page.control.setGeometry(QRect(page.x,page.y,500,60))
		    page.controls[param]=page.control
		    self.wl.append(page.control)
		    if page.y > (self.d['yres'])-200: 
        		page.x+=600
			page.y=10
		    else:
			page.y+=95


		elif mas[2]=='select':
		    lines=mas[3].split("|")
		    val=lines.index(d[param])
		    page.control=selectBox(page, prop=param, name=name, value=val, mas=lines)
		    page.control.setGeometry(QRect(page.x,page.y,500,60))
		    page.control.setFont(nameFont)
		    page.controls[param]=page.control
		    self.wl.append(page.control)
		    if page.y > (self.d['yres'])-200: 
        		page.x+=600
			page.y=10
		    else:
			page.y+=95

		elif mas[2]=='file1':
		    val=d[param]
		    page.control=_file(page, page.x, page.y, param, name, val)
		    page.control.setFont(nameFont)
		    page.controls[param]=page.control
		    self.wl.append(page.control)
		    if page.y > (self.d['yres'])-200: 
        		page.x+=600
			page.y=10
		    else:
			page.y+=95


	    else:   
		pass


        c=self.count()
        for i in range(c):
            self.setSaveCancel(self.widget(i))
        

    def save(self):
	lc="<html><table border=1><tr><td width=100><H2><b> ПОЛЕ </b></H2></td><td width=100> БЫЛО </td><td width=100> СТАЛО </td></tr>"
	ch=0
        for m in self.wl:
            if self.d[m.prop()]!=m.val():
        	#print "different: %s = %s" % (m.prop(),m.text())
        	lc+="<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (self.d['n'][m.prop()].encode('utf-8'), self.d[m.prop()], m.text().encode('utf-8'))
        	ch+=1
	lc+="</table></html>"
	
	if (ch>0) and _confirmChanges(lc).exec_():

            for m in self.wl:
	        self.d[m.prop()]=m.val()
	        #print "%s = %s" % (m.prop(),m.text())

	    self.d['saveData'](self.d['configFileName'])


    def cancel(self):
        self.close()
        del(self)


    def setSaveCancel(self, tab):
        tab.cancel=QPushButton(u"ВЫХОД", tab)
        tab.cancel.setGeometry(QRect(self.d['xres']-160,self.d['yres']-200, 150, 50))
        tab.connect(tab.cancel,  SIGNAL("clicked()"),  self.cancel)
        tab.save=QPushButton(u"СОХРАНИТЬ", tab)
        tab.save.setGeometry(QRect(self.d['xres']-160,self.d['yres']-120, 150, 50))        
        tab.connect(tab.save,  SIGNAL("clicked()"),  self.save)
