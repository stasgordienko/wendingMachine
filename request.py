# -*- coding: utf-8 -*-
#!/usr/bin/env python
  
#import sys
#import os
import chilkat #copy files from chilkat.zip to /usr/lib/pymodules/python26/

# Use EVP api to sign message
from M2Crypto import BIO, RSA, EVP, Rand
from M2Crypto.EVP import MessageDigest

from datetime import datetime
from xml.dom import minidom
from PyQt4.QtNetwork import QSslKey, QSslCertificate, QSslConfiguration, QNetworkRequest, QNetworkAccessManager, QSsl, QSslSocket
from PyQt4.QtCore import QObject, QByteArray, QUrl, SIGNAL

import db

# --------------------------------------------------------------
# Requests
requestsPath='data/Requests/'
checkRequest='<Request><DateTime>TIME</DateTime><Sign>HEX</Sign><Check><ServiceId>int</ServiceId><Account>string</Account></Check></Request>';
paymentRequest="""<Request><DateTime>TIME</DateTime><Sign>HEX</Sign><Payment><ServiceId>int</ServiceId><PartnerObjectId>string</PartnerObjectId>
<OrderId>long</OrderId><Account>string</Account><Amount>decimal</Amount></Payment></Request>""";
confirmRequest="<Request><DateTime>TIME</DateTime><Sign>HEX</Sign><Confirm><PaymentId>long</PaymentId></Confirm></Request>";
statusRequest="<Request><DateTime>TIME</DateTime><Sign>HEX</Sign><Status><PaymentId>long</PaymentId></Status></Request>";
partnerInfoRequest="<Request><DateTime>TIME</DateTime><Sign>HEX</Sign><PartnerInfo/></Request>";
servicesRequest="<Request><DateTime>TIME</DateTime><Sign>HEX</Sign><Services/></Request>";

# --------------------------------------------------------------
# Data
certSign = 'data/Certs/GateSign-Test.pfx'  # test account certificate
certSignPWD = 'test'
certSignSubj = 'GateSign-Test'

signKeyFile='data/partner.ppk' #work account certificate
    
#certSsl = 'data/Certs/Gateway-Test.p12'
certSsl = 'data/client.3039.pfx'
certSslPWD = '30393450'
certSslSubj = 'Gateway_003039'
    
certVerify = 'data/Certs/GateSign-EasySoft.cer'
certVerifySubj = 'GateSign-EasySsoft'
  
gatewayUrl = "https://gateway.easysoft.com.ua:8448/op25.aspx"


# --------------------------------------------------------------
# program parameters
hashalgs  = ['md5', 'ripemd160', 'sha1',
                 'sha224', 'sha256', 'sha384', 'sha512']
  
# default hashing algorithm
hashalg  = 'sha1'

  
# default key parameters
keylen   = 1024
exponent = 65537



#################################################################
# CLASS

class request(QObject):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# CONSTRUCTOR
    
    def __init__(self,xml):
	QObject.__init__(self)

	self.xml = xml.replace("<Sign></Sign>", "<Sign>" + self.sign(xml) + "</Sign>");
	
	(cer, key) =  self.getPemLocalCertificate(certSsl, certSslSubj, certSslPWD)
    
	cert = QSslCertificate(cer, QSsl.Pem)
	if cert.isNull():
	    print "Local Certificate is Null!"

	pvkey = QSslKey(QByteArray(key), QSsl.Rsa, QSsl.Pem, QSsl.PrivateKey, QByteArray(certSslPWD))


	ssl = QSslConfiguration()
	ssl.setLocalCertificate(cert)
	ssl.setPrivateKey(pvkey)
	ssl.setPeerVerifyMode(QSslSocket.VerifyNone)
    
	#print ssl.localCertificate().toPem()
	#print ssl.privateKey().toPem()
    
    
	req = QNetworkRequest(QUrl(gatewayUrl))
	req.setSslConfiguration(ssl)
    
    
	self.man = QNetworkAccessManager()
	#self.connect(self.man, SIGNAL("sslErrors(QNetworkReply, QList<QSslError>)"), self.sslErr)
	#self.connect(self.man, SIGNAL("authenticationRequired(QNetworkReply, QAuthenticator)"), self.authReq)

	self.reply = self.man.post(req,QByteArray(self.xml))
	self.reply.ignoreSslErrors()
	self.connect(self.reply, SIGNAL("finished()"), self.getReply)
	#print self.xml

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#
    def getReply(self):
	httpStatus = self.reply.attribute(0).toString()
	print "REPLY HTTP STATUS: ",httpStatus
	if self.reply.error(): 
	    print "Connection reply error: %s" % (requestError[self.reply.error()])
	    self.emit(SIGNAL("error(str,int)"), str(httpStatus),self.reply.error())
	else:
	    data = self.reply.readAll()
	
	    doc = minidom.parseString(data)
    
	    self.response = doc.getElementsByTagName('Response')[0];
	    signature = self.response.getElementsByTagName("Sign")[0].childNodes[0].nodeValue


	    if self.verify(data.replace(signature, ""), signature.decode('hex')) == 1:
		result = data
	    else:
		print "Reply Signature Verification Error..."
		result = None

	    self.emit(SIGNAL("reply(str,str)"), str(httpStatus), str(result))
	    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
    def sign(self,message):

	#private = self.pvKeyFromPFX(certSign, certSignSubj, certSignPWD)  #для импорта ключа из .pfx
	private = open(signKeyFile,'r').read() # для private ключа в ppk-файле
	#print private
	
	key = EVP.load_key_string(private)
	# if you need a different digest than the default 'sha1':
	key.reset_context(md=hashalg)
	key.sign_init()
	key.sign_update(message)
	signature = key.sign_final().encode("HEX").upper()
	return signature


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
    def verify(self,message,signature):

	public = self.pubKeyFromCER(certVerify)
	#print public

	bio = BIO.MemoryBuffer(public)
	rsa = RSA.load_pub_key_bio(bio)
	pubkey = EVP.PKey()
	pubkey.assign_rsa(rsa)
	pubkey.reset_context(md=hashalg)
	pubkey.verify_init()
	pubkey.verify_update(message)

	return pubkey.verify_final(signature)

# --------------------------------------------------------------
# functions
  
    def pvKeyFromPFX(self,filename,subject,password):

        ##########################################
        certStore = chilkat.CkCertStore()

        #  Load the PFX file into a certificate store object
        success = certStore.LoadPfxFile(filename,password)
        if (success != True):
	    print certStore.lastErrorText()
	    sys.exit()

	#  Find the cert to be exported by the subject:
	# cert is a CkCert
	cert = certStore.FindCertBySubject(subject)
	if (cert == None ):
	    print "Certificate not found."
	    sys.exit()

	#  Does this cert have a private key?
	if (cert.HasPrivateKey() == True):
	    #  Get the private key
	    # pvkey is a CkPrivateKey
	    pvkey = cert.ExportPrivateKey()
    
	# Export the private key to a PEM file:
	return pvkey.getRsaPem()
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
    def pubKeyFromCER(self,filename):

	##########################################

	# cert is a CkCert
	cert = chilkat.CkCert()
	cert.LoadFromFile(filename)

	#  Get the private key
	# pubkey is a CkPublicKey
	pubkey = cert.ExportPublicKey()

        if type(pubkey) != type(None):
	    # Export the private key to a PEM file:
	    return pubkey.getOpenSslPem()
	else:
	    print "Certificate or/and public key not found in th file: %s" % filename
	    return None

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
    def getPemLocalCertificate(self,filename,subject,pwd):

	##########################################
	certStore = chilkat.CkCertStore()

	#  Load the PFX file into a certificate store object
	success = certStore.LoadPfxFile(filename,pwd)
	if (success != True):
	    print certStore.lastErrorText()
	    sys.exit()

	#  Find the cert to be exported by the subject:
	# cert is a CkCert
	cert = certStore.FindCertBySubject(subject)
	if (cert == None ):
	    print "Certificate not found."
	    sys.exit()

	#  Does this cert have a private key?
	if (cert.HasPrivateKey() == True):
	    #  Get the private key
	    # pvkey is a CkPrivateKey
	    pvkey = cert.ExportPrivateKey()
    
	# Export the private key to a PEM file:
	key = pvkey.getRsaPem()


	#  Save the cert to a PEM file:
	certificate = cert.exportCertPem()

	# Export the certifiate to a PEM file:
	# Export the private key to a PEM file:
	return [certificate,key]
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#END CLASS
# --------------------------------------------------------------

arg = lambda x,y: x or y 

class payment(QObject):
    def __init__(self, account='',service='',partner='',order='',amount='',bank=''):
	QObject.__init__(self)
	self.paymentId = '0'
	self.paymentDate=''
	self.orderStatus=''
        self.tryPay = 0
        self.tryConfirm = 0
        self.tryStatus = 0
        
        self.bank = bank
        self.account = account
        self.service = service
        self.partner = partner
        self.order = order
        self.amount = amount
        self.tax = 0
        self.errorType = ''
        self.errorCode = ''
        self.errorDetail = ''
        self.confirmStatusDetail = ''
        self.paymentReplyHttpCode = ''
        self.confirmReplyHttpCode = ''
        self.checkReplyHttpCode = ''
        self.partnerReplyHttpCode = ''
        
#######################################
## PAYMENT
#######################################
    def pay(self, amount='', order='', partner=''):
        self.amount = arg(amount,self.amount)
	self.order = arg(order, self.order)
	self.partner = arg(partner, self.partner)
	
        xml = paymentRequest.replace("<Sign>HEX</Sign>", 
	    "<Sign></Sign>").replace("<DateTime>TIME</DateTime>", 
	    "<DateTime>" + datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "</DateTime>");
	xml = xml.replace("<Account>string</Account>", "<Account>" + self.account + "</Account>").replace("<ServiceId>int</ServiceId>", 
	    "<ServiceId>" + self.service + "</ServiceId>")
	xml = xml.replace("<PartnerObjectId>string</PartnerObjectId>", "<PartnerObjectId>" + self.partner + "</PartnerObjectId>").replace("<OrderId>long</OrderId>", 
	    "<OrderId>" + self.order + "</OrderId>").replace("<Amount>decimal</Amount>", "<Amount>" + self.amount + "</Amount>")
	#print "PAYMENT XML: ",xml
	self.paymentRequestXML = xml
	
	self.r = request(xml)
	self.connect(self.r, SIGNAL("reply(str,str)"), self.paymentReady)
	self.connect(self.r, SIGNAL("error(str,int)"), self.paymentError)


    def paymentReady(self,code,reply):
	self.disconnect(self.r, SIGNAL("reply(str,str)"), self.paymentReady)
	#print "PAYMENT REPLY XML: ",reply
	self.paymentReplyXML=reply
	self.paymentReplyHttpCode = code
	
	if type(reply) != type(None):
	    doc = minidom.parseString(reply)
	    self.paymentStatusCode = doc.getElementsByTagName("StatusCode")[0].childNodes[0].nodeValue
	    self.paymentStatusDetail = doc.getElementsByTagName("StatusDetail")[0].childNodes[0].nodeValue.encode('utf-8')
	    self.paymentId = str(doc.getElementsByTagName("PaymentId")[0].childNodes[0].nodeValue)

	    if int(self.paymentStatusCode) == 0:   # SUCCESS
		print "StatusCode  : ", self.paymentStatusCode
		print "StatusDetail: ", self.paymentStatusDetail
		print "PaymentId   : ", self.paymentId
		####################  # SUCCESS payment creating - confirm
		self.confirm()

	    elif self.tryPay<2:
		print "Error creating payment"
		print "StatusDetail: ", self.paymentStatusDetail
		#### write to log: error. retry
		###############################
		self.pay()
		self.tryPay+=1
        else:
    	    self.errorDetail = self.sr.reply.error()
    	    self.errorCode = code
    	    self.errorType = 'HTTP'
	    self.emit(SIGNAL("error()"))

	
    def paymentError(self,code,error):
	self.disconnect(self.r, SIGNAL("error(str,int)"), self.paymentError)
	self.errorType = 'HTTP'
	self.errorCode = code
	self.errorDetail = error
	self.emit(SIGNAL("error()"))
	

#######################################
# CONFIRM
#######################################

    def confirm(self, paymentId=''):
	self.paymentId = arg(paymentId,self.paymentId)
        xml = confirmRequest.replace("<Sign>HEX</Sign>","<Sign></Sign>").replace("<DateTime>TIME</DateTime>", 
	    "<DateTime>" + datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "</DateTime>");
	xml = xml.replace("<PaymentId>long</PaymentId>", "<PaymentId>" + self.paymentId + "</PaymentId>")
	self.cr = request(xml)

	self.confirmRequestXML = xml
	#print "CONFIRMATION XML:",xml

	self.connect(self.cr, SIGNAL("reply(str,str)"), self.confirmReady)
	self.connect(self.cr, SIGNAL("error(str,int)"), self.confirmError)


    def confirmReady(self,code,reply):
	self.disconnect(self.cr, SIGNAL("reply(str,str)"), self.confirmReady)
	self.confirmReplyXML = reply
	self.confirmReplyHttpCode = code
	if reply != None:
	    doc = minidom.parseString(reply)
	    self.confirmStatusCode = doc.getElementsByTagName("StatusCode")[0].childNodes[0].nodeValue
	    self.confirmStatusDetail = doc.getElementsByTagName("StatusDetail")[0].childNodes[0].nodeValue.encode('utf-8')
	    self.orderStatus = doc.getElementsByTagName("OrderStatus")[0].childNodes[0].nodeValue
	    if self.orderStatus in ['Accepted','Declined']:
		self.paymentDate = doc.getElementsByTagName("PaymentDate")[0].childNodes[0].nodeValue
	    else: self.paymentDate = '';

	    if int(self.confirmStatusCode) == 0:   # SUCCESS
		print "StatusCode  : ", self.confirmStatusCode
		print "StatusDetail: ", self.confirmStatusDetail
		print "OrderStatus : ", self.orderStatus
		print "PaymentDate : ", self.paymentDate
		if self.orderStatus in ['Accepted','InProcess']:   #FINISH - PAYMENT OK!
		    self.emit(SIGNAL("success()"))
		
	    elif self.tryConfirm<2:
		self.confirm(self.paymentId)
		self.tryConfirm+=1
        else:
    	    self.errorDetail = self.sr.reply.error()
    	    self.errorType = 'HTTP'
    	    self.errorCode = code
	    self.emit(SIGNAL("error()"))
	
    def confirmError(self,code,error):
	self.disconnect(self.cr, SIGNAL("error(str,int)"), self.confirmError)
	self.errorType = 'HTTP'
	self.errorCode = code
	self.errorDetail = error
	self.emit(SIGNAL("error()"))


#######################################
# STATUS
#######################################


    def status(self, paymentId=''):
        self.paymentId= arg(paymentId, self.paymentId)
        xml = statusRequest.replace("<Sign>HEX</Sign>","<Sign></Sign>").replace("<DateTime>TIME</DateTime>", 
	    "<DateTime>" + datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "</DateTime>");
	xml = xml.replace("<PaymentId>long</PaymentId>", "<PaymentId>" + self.paymentId + "</PaymentId>")
	self.sr = request(xml)
	#print "STATUS XML:",xml
	self.statusRequestXML = xml
	self.connect(self.sr, SIGNAL("reply(str,str)"), self.statusReady)
	self.connect(self.sr, SIGNAL("error(str,int)"), self.statusError)


    def statusReady(self,code,reply):
	self.disconnect(self.sr, SIGNAL("reply(str,str)"), self.statusReady)
        #print "STATUS REPLY XML: ",reply
        self.statusReplyXML = reply
        self.statusReplyHttpCode = code
	if reply != None:
	    doc = minidom.parseString(reply)
	    self.statusStatusCode = doc.getElementsByTagName("StatusCode")[0].childNodes[0].nodeValue
	    self.statusStatusDetail = doc.getElementsByTagName("StatusDetail")[0].childNodes[0].nodeValue.encode('utf-8')
	    self.orderStatus = doc.getElementsByTagName("OrderStatus")[0].childNodes[0].nodeValue
	    if self.orderStatus in ['Accepted','Declined']:
		self.paymentDate = doc.getElementsByTagName("PaymentDate")[0].childNodes[0].nodeValue
	    else: self.paymentDate = '';

	    if int(self.statusStatusCode) == 0:   # SUCCESS
		print "StatusCode  : ",self.statusStatusCode
		print "StatusDetail: ", self.statusStatusDetail
		print "OrderStatus : ", self.orderStatus
		print "PaymentDate : ", self.paymentDate
		if self.orderStatus in ['Accepted','InProcess']:   #FINISH - STATUS OK!
		    self.emit(SIGNAL("success()"))
	    elif self.tryStatus<1:
		self.status(self.paymentId)
		self.tryStatus+=1
        else:
    	    self.errorDetail = self.sr.reply.error()
    	    self.errorType = 'HTTP'
    	    self.errorCode = code
	    self.emit(SIGNAL("error()"))
	
    def statusError(self,code,error):
	self.disconnect(self.sr, SIGNAL("error(str,int)"), self.statusError)
	self.errorType = 'HTTP'
	self.errorCode = code
	self.errorDetail = error
	self.emit(SIGNAL("error()"))

#######################################
# SERVICES
#######################################

    def services(self,paymentId=''):
        self.paymentId= arg(paymentId, self.paymentId)
        xml = servicesRequest.replace("<Sign>HEX</Sign>","<Sign></Sign>").replace("<DateTime>TIME</DateTime>", 
	    "<DateTime>" + datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "</DateTime>");
	self.sr = request(xml)
	print "services XML:",xml
	self.statusRequestXML = xml
	self.connect(self.sr, SIGNAL("reply(str,str)"), self.servicesReady)
	self.connect(self.sr, SIGNAL("error(str,int)"), self.servicesError)


    def servicesReady(self,code,reply):
	self.disconnect(self.sr, SIGNAL("reply(str,str)"), self.servicesReady)
        #print "services REPLY XML: ",reply
        open('services.xml','w').write(reply)
        self.servicesReplyXML = reply
        self.servicesReplyHttpCode = code
	if reply != None:
	    doc = minidom.parseString(reply)
	    self.servicesStatusCode = doc.getElementsByTagName("StatusCode")[0].childNodes[0].nodeValue
	    self.servicesStatusDetail = doc.getElementsByTagName("StatusDetail")[0].childNodes[0].nodeValue.encode('utf-8')

	    if int(self.servicesStatusCode) == 0:   # SUCCESS
		print "StatusCode  : ",self.servicesStatusCode
		print "StatusDetail: ", self.servicesStatusDetail

		servFile = open('services.txt','w')
		text=''
		self.SERVICE = {}
		allServices = doc.getElementsByTagName("Services")[0]
		groups = allServices.getElementsByTagName("Group")
		for group in groups:
		    attr = {}
		    for (name,value) in group.attributes.items():
		        attr[name] = value
		    groupName=attr['name']
		    groupId=attr['id']

		    services = group.getElementsByTagName("Service")
		    for service in services:
			attr = {}
			for (name,value) in service.attributes.items():
			    attr[name] = value
			#serviceName=
			#serviceId=
			#seviceMin=
			#serviceMax=
			self.SERVICE[attr['serviceId']] = (attr['name'], attr['amountMin'], attr['amountMax'], groupName, groupId)
                        text=text+attr['serviceId']+', \'\', \''+attr['name']+'\', \''+attr['amountMin']+'\', \''+attr['amountMax']+'\' '+groupName+' '+groupId+'\n'
                        #text=text+'['+attr['serviceId']+', \'\', u\''+attr['name']+'\', \''+attr['amountMin']+'\', \''+attr['amountMax']+'\'],\n'
		#print self.SERVICE
		print text
		servFile.write(unicode(text).encode('utf-8'))
		servFile.close()
		self.emit(SIGNAL("success()"))

        else:
    	    self.errorDetail = self.sr.reply.error()
    	    self.errorType = 'HTTP'
    	    self.errorCode = code
	    self.emit(SIGNAL("error()"))
	
    def servicesError(self,code,error):
	self.disconnect(self.sr, SIGNAL("error(str,int)"), self.servicesError)
	self.errorType = 'HTTP'
	self.errorCode = code
	self.errorDetail = error
	self.emit(SIGNAL("error()"))

#######################################
# CHECK
#######################################

    def check(self, account='', service=''):
        self.account = arg(account,self.account)
	self.service = arg(service, self.service)
        xml = checkRequest.replace("<Sign>HEX</Sign>", 
	    "<Sign></Sign>").replace("<DateTime>TIME</DateTime>", 
	    "<DateTime>" + datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "</DateTime>");
	xml = xml.replace("<Account>string</Account>", "<Account>" + self.account + "</Account>").replace("<ServiceId>int</ServiceId>", 
	    "<ServiceId>" + self.service + "</ServiceId>")
	#print "CHECK XML: ",xml
	self.checkRequestXML = xml
	self.hr = request(xml)
	self.connect(self.hr, SIGNAL("reply(str,str)"), self.checkReady)
	self.connect(self.hr, SIGNAL("error(str,int)"), self.checkError)

    
    def checkReady(self,code,reply):
	self.disconnect(self.hr, SIGNAL("reply(str,str)"), self.checkReady)
        self.checkReplyXML = reply
        self.checkReplyHttpCode = code
	if reply != None:
	    doc = minidom.parseString(reply)
	    
	    statusCode = doc.getElementsByTagName("StatusCode")
	    if statusCode: 
		self.checkStatusCode = statusCode[0].childNodes[0].nodeValue
	    else:
		self.checkStatusCode = -1
	    
	    statusDetail = doc.getElementsByTagName("StatusDetail")[0].childNodes
	    if statusDetail:
		self.checkStatusDetail = statusDetail[0].nodeValue.encode('utf-8')
	    else:
		self.checkStatusDetail = ''
	    
	    serviceId = doc.getElementsByTagName("ServiceId")
	    if serviceId:
		self.service = serviceId[0].childNodes[0].nodeValue
	    
	    accountInfo = doc.getElementsByTagName("AccountInfo")
	    if accountInfo:
		#self.d['accountInfo']=accountInfo[0]
		self.accountInfo = accountInfo[0]
	    else: self.accountInfo = None
	
	    bankingDetails = doc.getElementsByTagName("BankingDetails")
	    if bankingDetails:
		self.bank = bankingDetails[0]
	    else: self.bank = ''
	
	    if int(self.checkStatusCode) == 0:   ########## SUCCESS
		print "StatusCode  : ", self.checkStatusCode
		print "StatusDetail: ", self.checkStatusDetail
		print "ServiceId   : ", self.service
		print "AccountInfo : ", self.accountInfo
    
		self.emit(SIGNAL("success()"))
		
	    else:
		print "StatusDetail: ", self.checkStatusDetail
		self.errorDetail='not found'
    		self.errorType = 'CHECK'
    		self.errorCode = code
		self.emit(SIGNAL("error()"))

        else:
    	    self.errorDetail = self.sh.reply.error()
    	    self.errorType = 'HTTP'
    	    self.errorCode = code
	    self.emit(SIGNAL("error()"))
	
    def checkError(self,code,error):
	self.disconnect(self.hr, SIGNAL("error(str,int)"), self.statusError)
	self.errorType = 'HTTP'
	self.errorCode = code
	self.errorDetail = error
	self.emit(SIGNAL("error()"))


#############################################################
# PARTNER INFO

    def partnerInfo(self):
        xml = partnerInfoRequest.replace("<Sign>HEX</Sign>", 
	    "<Sign></Sign>").replace("<DateTime>TIME</DateTime>", 
	    "<DateTime>" + datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "</DateTime>");
	self.pr = request(xml)
	#print "Partner XML:",xml
	self.partnerRequestXML = xml
	self.connect(self.pr, SIGNAL("reply(str,str)"), self.partnerReady)
	self.connect(self.pr, SIGNAL("error(str,int)"), self.partnerError)


    def partnerReady(self,code,reply):
	self.disconnect(self.pr, SIGNAL("reply(str,str)"), self.partnerReady)
	self.partnerReplyXML = reply
	self.partnerReplyHttpCode = code
	if reply != None:
	    doc = minidom.parseString(reply)
	    statusCode = doc.getElementsByTagName("StatusCode")
	    if statusCode: 
		self.partnerStatusCode = statusCode[0].childNodes[0].nodeValue
	    else:
		self.partnerStatusCode = -1
	    
	    statusDetail = doc.getElementsByTagName("StatusDetail")
	    if statusDetail:
		self.partnerStatusDetail = statusDetail[0].childNodes[0].nodeValue.encode('utf-8')
	    else:
		self.partnerStatusDetail = ''

	    if int(self.partnerStatusCode) == 0:   # SUCCESS
		try:
		    self.partnerBalance = doc.getElementsByTagName("Balance")[0].childNodes[0].nodeValue
		    self.partnerLimit = doc.getElementsByTagName("Limit")[0].childNodes[0].nodeValue
		    self.partnerLimitActive = doc.getElementsByTagName("LimitActive")[0].childNodes[0].nodeValue
		except:
		    print "StatusDetail: ", self.partnerStatusDetail
		    self.errorDetail='not found'
    		    self.errorType = 'PARTNERINFO'
    		    self.errorCode = code
		    self.emit(SIGNAL("error()"))
                else:
		    print "StatusDetail: ", self.partnerStatusDetail
		    print "Balance     : ", self.partnerBalance
		    print "Limit       : ", self.partnerLimit
		    print "LimitActive : ", self.partnerLimitActive
		    self.emit(SIGNAL("success()"))
	    else:
		self.errorDetail='not found'
    		self.errorType = 'PARTNERINFO'
    		self.errorCode = code
		self.emit(SIGNAL("error()"))
        else:
    	    self.errorDetail = self.sr.reply.error()
    	    self.errorType = 'HTTP'
    	    self.errorCode = code
	    self.emit(SIGNAL("error()"))


    def partnerError(self,code,error):
	self.disconnect(self.pr, SIGNAL("error(str,int)"), self.partnerError)
	self.errorType = 'HTTP'
	self.errorCode = code
	self.errorDetail = error
	self.emit(SIGNAL("error()"))

##################################################################################################################
# END CLASS payment



requestError = {
0:"no error condition. Note: When the HTTP protocol returns a redirect no error will be reported. You can check if there is a redirect with the QNetworkRequest::RedirectionTargetAttribute attribute.",
1:"the remote server refused the connection (the server is not accepting requests)",
2:"the remote server closed the connection prematurely, before the entire reply was received and processed",
3:"the remote host name was not found (invalid hostname)",
4:"the connection to the remote server timed out",
5:"the operation was canceled via calls to abort() or close() before it was finished.",
6:"the SSL/TLS handshake failed and the encrypted channel could not be established. The sslErrors() signal should have been emitted.",
7:"the connection was broken due to disconnection from the network, however the system has initiated roaming to another access point. The request should be resubmitted and will be processed as soon as the connection is re-established.",
101:"the connection to the proxy server was refused (the proxy server is not accepting requests)",
102:"the proxy server closed the connection prematurely, before the entire reply was received and processed",
103:"the proxy host name was not found (invalid proxy hostname)",
104:"the connection to the proxy timed out or the proxy did not reply in time to the request sent",
105:"the proxy requires authentication in order to honour the request but did not accept any credentials offered (if any)",
201:"the access to the remote content was denied (similar to HTTP error 401)",
202:"the operation requested on the remote content is not permitted",
203:"the remote content was not found at the server (similar to HTTP error 404)",
204:"the remote server requires authentication to serve the content but the credentials provided were not accepted (if any)",
205:"the request needed to be sent again, but this failed for example because the upload data could not be read a second time.",
301:"the Network Access API cannot honor the request because the protocol is not known",
302:"the requested operation is invalid for this protocol",
99:"an unknown network-related error was detected",
199:"an unknown proxy-related error was detected",
299:"an unknown error related to the remote content was detected",
399:"a breakdown in protocol was detected (parsing error, invalid or unexpected responses, etc.)"
}