# -*- coding: utf-8 -*-
from os import listdir, popen, path
from os.path import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Print_finish import _print_finish
from dialogs import *
from Print_preview import _print_preview
from Print_preview_img import _print_preview_img
import chardet
import sys


try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class _print_ins(QWidget):

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

        self.label = QLabel(self)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label.setGeometry(QRect((d['xres']-900)//2, 400, 900, 100))
        self.label.setText(self.l['scan_ins_please'][self.lang])
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setVisible(False)

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
        self.b_main.setText(self.l['menu'][self.lang])
        self.b_main.setFocusPolicy(Qt.NoFocus)

        self.l_cost = QLabel(self)
        self.l_cost.setFont(font)
        self.l_cost.setAlignment(Qt.AlignCenter)
        self.l_cost.setObjectName(_fromUtf8("l_cost"))
        self.l_cost.setGeometry(QRect((d['xres']-900)//2, 200, 900, 150))
        self.l_cost.setText(self.l['print_ins_pagecost'][self.lang] % (float(d['print_pagecost'])/100, float(d['print_pagecost2'])/100))
        self.l_cost.setVisible(False)

        self.connect(self.b_main,  SIGNAL("clicked()"),  self.back)
        self.connect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
        
        self.timeProgress = QProgressBar(self)
        self.timeProgress.setProperty(_fromUtf8("value"), 0)
        self.timeProgress.setObjectName(_fromUtf8("timeProgress"))
        self.timeProgress.setGeometry(QRect(1, d['yres']-10, d['xres'], 10))
        self.timeProgress.setTextVisible(False)

	changeMessage(self.d).exec_()
        
        self.stimer = QTimer()
        self.stimer.setInterval(500)
        self.connect(self.stimer, SIGNAL("timeout()"), self.timeUpdate)
        self.stimer.start()
      

    def timeUpdate(self):
        if ('insertedDeviceName' in self.d.keys()):
	    if self.flashMounted():
		self.stimer.stop()
        	self.d['print_fileselect']=_print_fileselect(self.d)
        	self.d['print_fileselect'].showFullScreen()
            
        	#self.d['print_finish']=_print_finish(self.d)
        	self.disconnect(self.stimer, SIGNAL("timeout()"), self.timeUpdate)
		if 'printer' in self.d.keys(): del(self.d['printer'])
		self.close()
		self.deleteLater()
	    else:
		#change picture to flashOK
		self.label.setText(self.l['scan_inserted'][self.lang])
		self.label.setStyleSheet("background-color: transparent; color: green;")
		self.label.setVisible(True)

	else:
            #change picture to noFlash
            self.label.setText(self.l['scan_ins_please'][self.lang])
            self.label.setVisible(True)
            #self.l_cost.show()
            self.label.setStyleSheet("background-color: transparent; color: red;")
            val = self.timeProgress.value() + 2
            if val > 100:
                self.stimer.stop()
        	if flashFail(self.d).exec_():
		    self.timeProgress.setValue(0)
        	    self.stimer.start()
		else:
		    self.back()
	    else:
        	self.timeProgress.setValue(val)
    

    def flashMounted(self):
        if exists(self.d['flash']): #and exists(self.d['flash_dev']):
            names = listdir(self.d['flash'])
            if len(names)>0:
                return True
            # !check free space!!!!!!!!!!!!!!
            #filter=()
            #listOfSystems=QStorageMetaInfo.fileSystems(filter,connectedOnly=True)
        else: 
            return False


    def back(self):
	self.disconnect(self.stimer, SIGNAL("timeout()"), self.timeUpdate)
        self.stimer.stop()
	if 'printer' in self.d.keys(): del(self.d['printer'])
	self.close()
	self.deleteLater()

    def helpbox(self):
	self.stimer.stop()
	hb=helpBox('print', self.d)
        hb.exec_()
	self.stimer.start()
	
    def closeEvent(self,event):
	pass
	event.accept()
    
    def enterEvent(self,event):
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.close)
	event.accept

    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.close)
	event.accept
	


IMAGES = ['jpg', 'png', 'tiff', 'bmp']
DOCUMENTS = ['pdf', 'doc', 'docx', 'odt', 'xls', 'xlsx', 'ppt', 'rtf']
PLAIN = ['txt', 'pas', 'c', 'cpp', 'py']
SUPPORTED = DOCUMENTS + IMAGES

class _print_fileselect(QWidget):

    def __init__(self,d):
        QWidget.__init__(self)
        reload(sys)
        sys.setdefaultencoding("utf-8")
        reload(sys)
        self.d=d
        self.lang=d['lang']
        self.l=d['l']
        self.prev=[]
        self.filename=unicode('')
        self.current=unicode(d['flash'])
        self.currentPath=self.current
        self.level=0
        self.doctype=''
        self.encoding='utf8'

        font = QFont()
        font.setPointSize(22)
        font.setWeight(75)
        font.setBold(False)

        self.label = QLabel(self)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        #self.label.setGeometry(QRect((d['xres']-900)//2, 400, 900, 100))
        self.label.setGeometry(QRect(0, 130, d['xres'], 80))
        self.label.setText(self.l['fileselect'][self.lang])
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)

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

        #self.b_eject = QPushButton(self.top)
        #self.b_eject.setFont(font)
        #self.b_eject.setObjectName(_fromUtf8("b_eject"))
        #self.b_eject.setGeometry(QRect(30, 15, 400, 90))
        #self.b_eject.setText(self.l['eject'][self.lang])
        #self.b_eject.setFocusPolicy(Qt.NoFocus)

        self.b_back = QPushButton(self.top)
	self.b_back.setGeometry(QRect(30, 15, 400, 90))
        self.b_back.setFont(font)
        self.b_back.setObjectName(_fromUtf8("b_main"))
        self.b_back.setFocusPolicy(Qt.NoFocus)
        self.b_back.setText(self.l['menu'][self.lang])

        self.b_next = QPushButton(self)
        self.b_next.setFont(font)
        self.b_next.setObjectName(_fromUtf8("b_next"))
        self.b_next.setFocusPolicy(Qt.NoFocus)
        self.b_next.setGeometry(QRect(d['xres']-320, d['yres']-120, 300, 95))
        #not working with qpushbutton# self.b_next.setAlignment(Qt.AlignLeft)
        self.b_next.setText(self.l['next'][self.lang])

        self.filelist = QListWidget(self)
        self.filelist.setObjectName(_fromUtf8("filelist"))
        self.filelist.setGeometry(QRect(30, 250, d['xres']-400, d['yres']-250))
	#self.filelist.setStyleSheet("""QListWidget::item {}""")
        self.filelist.verticalScrollBar().setStyleSheet("""
	QScrollBar:vertical {width: 70px; height: 50px; background-color: #EEEEEE; border: none;} 
        """)
        self.connect(self.b_back,  SIGNAL("clicked()"),  self.back)
        self.connect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
        self.connect(self.b_next,  SIGNAL("clicked()"),  self.select)
        self.connect(self.filelist,  SIGNAL("itemClicked(QListWidgetItem *)"),  self.itemClicked)
        

        self.stimer = QTimer()
        self.stimer.setInterval(10000)
        self.connect(self.stimer, SIGNAL("timeout()"), self.pop)
        
        self.listUpdate()
        
        self.b_next.setEnabled(False)
        
        self.flashTimer = QTimer()
        self.flashTimer.setInterval(1000)
        self.connect(self.flashTimer, SIGNAL("timeout()"), self.timeUpdate)
        self.flashTimer.start()
        self.stimer.start()


    def timeUpdate(self):
        if not (('insertedDeviceName' in self.d.keys()) and exists(self.d['flash']) ): #and exists(self.d['flash_dev'])):
	    self.flashTimer.stop()
	    self.stimer.start()
	    self.pop()

        
    def listUpdate(self):
        self.filelist.clear()
        dir=unicode('')

        for p in self.prev[:]:
            dir=dir + p + unicode('/')
            
        self.currentPath= unicode(dir + self.current) #+ '/'
        
        print self.currentPath.encode('utf-8')
        #print "current:", self.current,  "path:", self.currentPath, "dir:",  dir
        
        dirs=[]
        files=[]
        names=[]

        try:
	    if exists(self.currentPath.encode('utf-8')):
		names = listdir(self.currentPath.encode('utf-8'))
	except:
	    names=[]
	else:
	    pass
	    
        for name in names:
            fullname = self.currentPath + unicode('/') + unicode(name)
            #enc=chardet.detect(fullname)['encoding']
            #key=lines[i][1:-1].decode(encoding)
            #print "dir:",  self.currentPath,  "name:",  name,  "fullname:",  fullname
            #print enc
            if path.isfile(fullname.encode('utf-8')):
                #files.append(name) #unicode(name, self.encoding))
                files.append(unicode(name))
            else:
                #dirs.append(name) #unicode(name, self.encoding))
                dirs.append(unicode(name))
        
        #root, dirs, files = walk(self.currentPath).next()
	self.filelist.setViewMode(0)
	self.filelist.setIconSize(QSize(50,50))
	self.filelist.setModelColumn(2)

        if self.level>0: 
            item= QListWidgetItem(QIcon("img/ico/back.png"), QString(".."), type=0)
            item.setFont(QFont("FreeSans", 22, 75))
            c=int((self.filelist.count() % 2 and '240') or '255')
            item.setBackgroundColor(QColor(c,c,c))
            item.setSizeHint(QSize(0,70))
            self.filelist.addItem(item)
            self.b_back.setText(self.l['back'][self.lang])
        else:
	    self.b_back.setText(self.l['menu'][self.lang])

        for cat in dirs:
            item= QListWidgetItem(QIcon("img/ico/folder.png"), QString(cat), type=1)
            item.setFont(QFont("FreeSans", 22, 75))
            c=int((self.filelist.count() % 2 and '240') or '255')
            item.setBackgroundColor(QColor(c,c,c))
            item.setSizeHint(QSize(0,70))
            
            self.filelist.addItem(item)
        
        for file in files:
            item= QListWidgetItem(QString(file),type=2)
            item.setFont(QFont("FreeSans", 22, 25))
            ff=file.split(".")
            ext = ff[-1]#.toLower()
            if ext in SUPPORTED:
                item.setWhatsThis(QString(ext))
                if ('doc' in ext) or ('rtf' in ext) or ('odt' in ext): 
		    iconFile="img/ico/doc.png"
                if 'xls' in ext: 
		    iconFile='img/ico/xls.png'
                elif 'ppt' in ext: 
		    iconFile='img/ico/psd.ico'
                elif 'pdf' in ext: 
		    iconFile='img/ico/pdf.png'
                elif 'jpg' in ext: 
		    iconFile='img/ico/jpg.png'
		elif 'png' in ext: 
		    iconFile='img/ico/jpg.png'
		elif 'tiff' in ext: 
		    iconFile='img/ico/jpg.png'

            else: 
        	item.setWhatsThis('')
        	iconFile="img/ico/blank.png"
            c=int((self.filelist.count() % 2 and '240') or '255')
            item.setBackgroundColor(QColor(c,c,c))
            item.setSizeHint(QSize(0,70))
            item.setIcon(QIcon(iconFile))
            self.filelist.addItem(item)
            
        self.filelist.scrollToItem(self.filelist.item(0))


    def itemClicked(self, item):
        #print "Click:",  unicode(item.text())
        #self.stimer.stop()
        if item.type()==1:  
            self.level+=1
            self.prev.append(self.current)
            self.current=item.text()#unicode(item.text()).encode('utf-8')
            self.filename=unicode('')
            self.b_next.setEnabled(False)
            self.listUpdate()
        elif item.type()==2: 
            self.filename=unicode(item.text())
            self.doctype=item.whatsThis()
            if self.doctype!='':
                self.b_next.setEnabled(True)
            else:
                self.b_next.setEnabled(False)
        elif item.type()==0: 
            self.current=self.prev.pop()
            self.level-=1
            self.filename=unicode('')
            self.b_next.setEnabled(False)
            self.listUpdate()
        self.stimer.start()


    def select(self):
        if self.filename:
            self.stimer.stop()
            self.flashTimer.stop()
            self.d['print_filename']=self.filename.encode('utf-8')
            self.d['print_path']=self.currentPath.encode('utf-8')
            full=self.currentPath + unicode("/") + self.filename
            self.d['print_fullname']=full.encode('utf-8')
            self.d['docType']=self.doctype
            if self.doctype in IMAGES:
        	self.d['print_preview']=_print_preview_img(self.d)
            elif self.doctype in DOCUMENTS:
        	self.d['print_preview']=_print_preview(self.d)
	    self.d['print_preview'].b_eject.setVisible(False)

            
    def back(self):
        #self.umount()
        if self.level > 0:
            self.current=self.prev.pop()
            self.level-=1
            self.filename=unicode('')
            self.b_next.setEnabled(False)
            self.listUpdate()
            self.stimer.start()
        else:
	    self.flashTimer.stop()
	    self.stimer.stop()
	    self.pop()


    def helpbox(self):
        self.stimer.stop()
        self.flashTimer.stop()
        hb=helpBox('print', self.d)
        hb.exec_()
        self.stimer.start()
        self.flashTimer.start()


    def enterEvent(self, event):
	self.connect(self.d['ping'], SIGNAL("powerFailure()"), self.close)
        if not 'insertedDeviceName' in self.d.keys():
	    self.d['printer'] = _print_ins(self.d)
	    self.d['printer'].showFullScreen()
	    self.pop()
	else:
	    self.flashTimer.start()
	    self.stimer.start()


    def leaveEvent(self,event):
	self.disconnect(self.d['ping'], SIGNAL("powerFailure()"), self.close)
	event.accept

	    
    def pop(self):
	self.close()


    def closeEvent(self, event):
        self.flashTimer.stop()
        self.stimer.stop()
        self.disconnect(self.b_back,  SIGNAL("clicked()"),  self.back)
        self.disconnect(self.b_help,  SIGNAL("clicked()"),  self.helpbox)
        self.disconnect(self.b_next,  SIGNAL("clicked()"),  self.select)
        self.disconnect(self.filelist,  SIGNAL("itemClicked(QListWidgetItem *)"),  self.itemClicked)
        self.disconnect(self.flashTimer, SIGNAL("timeout()"), self.timeUpdate)
        self.disconnect(self.stimer, SIGNAL("timeout()"), self.pop)
        if 'printer' in self.d.keys(): del(self.d['printer'])
	self.deleteLater()
	event.accept()