#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division

""" Python to MySQL using mysql-python

"""
from PyQt4.QtCore import QObject
import MySQLdb as mdb
from datetime import datetime
import sys


class action(QObject):
    def __init__(self,termId=0, balance=0, typeId='xerox'):
	QObject.__init__(self)
	self.timestart = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	self.timeend = ''
	self.insumm=0
	self.usedsumm=0
	self.change=0
	self.paper=0
	self.drum=0
	self.scan=0
	self.money=''
	self.errors=''
	self.status=''
	self.detail=''
	self.termId = termId
	self.inbalance = balance
	self.typeId = typeId
	self.isFinished=False
	self.isError=False

    def finish(self,status='success'):
	if self.isFinished: return 1
	self.status=status
	self.timeend = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	self.isError=True
	
	conn = mdb.connect('localhost', 'root', '240457', 'cp');
	try:
	    cursor = conn.cursor()
	    cursor.execute("""INSERT INTO action(termId,timestart,timeend,inbalance,insumm,usedsumm,`change`,
			    paper,drum,scan,`type`,`status`,money,errors,detail) VALUES 
			    (%d, '%s', '%s', %5.2f, %5.2f, %5.2f, %5.2f, %d, %d, %d, '%s', '%s', '%s', '%s', '%s')""" % (
			    self.termId, self.timestart, self.timeend, self.inbalance, self.insumm, self.usedsumm, self.change,
			    self.paper, self.drum, self.scan, self.typeId, self.status, self.money, self.errors, self.detail))
	    conn.commit()
	    cursor.close()
	    conn.close()
	    self.isFinished=True
	    self.isError=False
	    return 0

	except mdb.Error, e:
	    conn.rollback()
	    print "Error %d: %s" % (e.args[0],e.args[1])
	    #sys.exit(1)
	    return -1


def payment(termId, actionId, order, payment, service, account, amount, status, paymentDate, tax, partner, checkPrinted, log):
    if actionId=='': actionId='0'
    timeOper = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = log + "#chargeTime:%s#" % timeOper

    conn = mdb.connect('localhost', 'root', '240457', 'cp');
    try:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO payment(`termid`, `actionid`, `order`, `payment`, `service`, `account`, `amount`, `status`, `datetime`, `tax`, `partner`, `print`, `log`) VALUES 
    		    (%d, %d, %d, %d, %d, '%s', '%5.2f', '%s', '%s', '%5.2f', '%s', '%s', '%s')""" % (
    		    int(termId), int(actionId), int(order), int(payment), int(service), account, float(amount), status, paymentDate, tax, partner, checkPrinted, log))

        #cursor.execute("""INSERT INTO payment(`termid`, `actionid`, `order`, `payment`, `service`, `account`, `amount`, `status`, `datetime`, `tax`, `partner`, `print`, `log`) VALUES 
    	#	    (',"""+int(termId)+"""', '"""+int(actionId)+"""', '"""+int(order)+"""', '"""+int(payment)+"""', '"""+int(service)+"""', '"""+account+"""', '"""+float(amount)+"""', '"""+status+"""', '"""+paymentDate+"""', '"""+tax+"""', '"""+partner+"""', '"""+checkPrinted+"""', '"""+log+""")""")

        conn.commit()
        cursor.close()
        conn.close()
        return 0

    except mdb.Error, e:
        conn.rollback()
        print "Error %d: %s" % (e.args[0],e.args[1])
        #sys.exit(1)
        self.isError=True
        return -1

a="""
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    `actionid` BIGINT unsigned NOT NULL,
    `order` BIGINT unsigned NOT NULL,
    `payment` BIGINT unsigned,
    `service` integer unsigned,
    `account` CHAR(16),
    `amount` DECIMAL(5,2),
    `status` CHAR(16),
    `datetime` datetime,
    `tax` DECIMAL(5,2),
    `partner` CHAR(16),
    `print` CHAR(1),
    `log` BLOB


    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    `termid` integer NOT NULL,
    `timestart` datetime default '0000-00-00 00:00:00',
    `timeend` datetime default '0000-00-00 00:00:00',
    `inbalance` DECIMAL(5,2),
    `insumm` DECIMAL(5,2),
    `usedsumm` DECIMAL(5,2),
    `change` DECIMAL(5,2),
    `paper` integer unsigned,
    `drum` integer unsigned,
    `scan` integer unsigned,
    `type` CHAR(16), #print,printReady,xerox,payment,scan
    `status` CHAR(16), #success,error
    `money` CHAR(255), #coins a-g, notes A-G
    `errors` CHAR(255), #noChange, powerOff, paperJam, paperOut, networkOff
    `detail` CHAR(255),
    `sent` char(1) default '0'


-----------
try:
    conn = mdb.connect('localhost', 'testuser', 'test623', 'testdb');

    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS \
        Writers(Id INT PRIMARY KEY AUTO_INCREMENT, Name VARCHAR(25))")
    cursor.execute("INSERT INTO Writers(Name) VALUES('Jack London')")
    cursor.execute("INSERT INTO Writers(Name) VALUES('Honore de Balzac')")
    cursor.execute("INSERT INTO Writers(Name) VALUES('Lion Feuchtwanger')")
    cursor.execute("INSERT INTO Writers(Name) VALUES('Emile Zola')")
    cursor.execute("INSERT INTO Writers(Name) VALUES('Truman Capote')")

    conn.commit()

    cursor.close()
    conn.close()

except mdb.Error, e:
  
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)



------------
try:
    conn = mdb.connect('localhost', 'testuser', 
        'test623', 'testdb');

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Writers")

    rows = cursor.fetchall()

    for row in rows:
        print row

    cursor.close()
    conn.close()

except mdb.Error, e:
  
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)



#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys

try:
    conn = mdb.connect('localhost', 'testuser', 
        'test623', 'testdb');

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Writers")

    numrows = int(cursor.rowcount)

    for i in range(numrows):
        row = cursor.fetchone()
        print row[0], row[1]

    cursor.close()
    conn.close()

except mdb.Error, e:
  
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)




#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys

try:
    conn = mdb.connect('localhost', 'testuser', 
        'test623', 'testdb');

    cursor = conn.cursor(mdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Writers")

    rows = cursor.fetchall()

    for row in rows:
        print "%s %s" % (row["Id"], row["Name"])

    cursor.close()
    conn.close()

except mdb.Error, e:
  
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)




--------------------------------------------------
#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys

try:
    fin = open("chrome.png")
    img = fin.read()
    fin.close()

except IOError, e:

    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)

 
try:
    conn = mdb.connect(host='localhost',user='testuser',
       passwd='test623', db='testdb')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Images SET Data='%s'" % \
        mdb.escape_string(img))

    conn.commit()

    cursor.close()
    conn.close()

except mdb.Error, e:
  
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)
---------------------------------------------------------

#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys

try:
    conn = mdb.connect('localhost', 'testuser', 
        'test623', 'testdb');

    cursor = conn.cursor()
    
    cursor.execute("UPDATE Writers SET Name = %s WHERE Id = %s", 
        ("Leo Tolstoy", "1"))       
    cursor.execute("UPDATE Writers SET Name = %s WHERE Id = %s", 
        ("Boris Pasternak", "2"))
    cursor.execute("UPDATE Writer SET Name = %s WHERE Id = %s", 
        ("Leonid Leonov", "3"))   

    conn.commit()

    cursor.close()
    conn.close()

except mdb.Error, e:
  
    conn.rollback()
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)


----------------------------------------------------------

"""