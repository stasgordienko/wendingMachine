#!/usr/bin/python

from PyQt4.QtCore import QObject
import sys
from datetime import datetime

d = []

class _log(QObject):
    def __init__(self,dd):
	QObject.__init__(self)
	global d
	d = dd
	self.buffer = ''
	if not d['logfilename']: sys.exit(1)
	self.log("--- LOG INIT ---")
	

    def log(self,message):
	fd = open(d['logfilename'], "a")
	date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	fd.write("%s %s\n" % (date,message))
	fd.close()
