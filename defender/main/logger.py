from threading import Thread
import time
import logging

class Logger(object):
	def __init__(self,name,mode):
		self.mode = mode
		self.format = '[%(levelname)s] %(asctime)s %(message)s'
		fm = logging.Formatter(self.format) 
		logging.basicConfig(
				level = logging.DEBUG,
				format = self.format,
				datefmt = '%Y_%m_%d %H:%M:%S',
				filename = '/dev/null',
				filemode = 'a'
		)
		
		infohandler = logging.FileHandler('%s.info' %name)
		infohandler.setLevel(logging.INFO)
		infohandler.setFormatter(fm)
		self.infologger = logging.getLogger('%sinfologger' %name)
		self.infologger.addHandler(infohandler)

		errorhandler = logging.FileHandler('%s.error' %name)
		errorhandler.setLevel(logging.ERROR)
		errorhandler.setFormatter(fm)
		self.errorlogger = logging.getLogger('%serrorlogger' %name)
		self.errorlogger.addHandler(errorhandler)

		sdkhandler = logging.FileHandler('%s.sdk' %name)
		sdkhandler.setLevel(logging.INFO)
		sdkhandler.setFormatter(fm)
		self.sdklogger = logging.getLogger('%ssdklogger' %name)
		self.sdklogger.addHandler(sdkhandler)
		
	def info(self,msg):
		if self.mode == 'null':
			return
		elif self.mode == 'print':
			print(msg)
		else:
			if self.mode == 'file':
				self.infologger.info(msg)
			else:
				self.infologger.info(msg)
				print(msg)

	def error(self,msg):
		if self.mode == 'null':
			return
		elif self.mode == 'print':
			print(msg)
		else:
			if self.mode == 'file':
				self.errorlogger.error(msg)
			else:
				self.errorlogger.error(msg)
				print(msg)

	def recordsdklog(self,msg):
		self.sdklogger.info(msg)

class RecordData(Thread):
	def __init__(self,name,orderinfo,logger):
		Thread.__init__(self)
		self.logfile = '%s.data' %name
		self.loop = True
		self.name = name
		self.dateformat = "%Y-%m-%d %X"
		self.orderinfo = orderinfo
		self.logger = logger

	def quit(self):
		self.loop = False
	
	def run(self):
		with open(self.logfile,'a') as f:
			while self.loop:
				cur_time = time.strftime(self.dateformat,time.localtime())
				tcId = self.orderinfo['teacher'].get("id")
				stId = self.orderinfo['student'].get("id")
				tcsends = self.orderinfo['teacher'].get("senddatas")
				streceives = self.orderinfo['student'].get("receivedatas")
				stsends = self.orderinfo['student'].get("senddatas")
				tcreceives = self.orderinfo['teacher'].get("receivedatas")
				orderNo = self.orderinfo['orderNo']
				roomId = self.orderinfo['roomId']
				datalist = [
					"Time:%s" %cur_time,
					"tcId:%s" %tcId,
					"stId:%s" %stId,
					"tcsends:%s" %tcsends,
					"streceives:%s" %streceives,
					"stsends:%s" %stsends,
					"tcreceives:%s" %tcreceives,
					"orderNo:%s" %orderNo,
					"roomId:%s" %roomId,
					"mediaIp:%s" %self.orderinfo['media'].get("mediaIp"),
					"mediaPort:%s" %self.orderinfo['media'].get("mediaPort")
				]

				f.write('\n'.join(datalist))
				f.write("\n\n")
				if tcsends - streceives > 1:
					self.logger.error("用例:{name}  时间:{time}  老师发送数据量:{sends}  学生接受数据量:{receives}  订单号:{orderNo}  老师ID:{tcId}  学生ID:{stId}".format(name=self.name,time=cur_time,sends=tcsends,receives=streceives,orderNo=orderNo,tcId=tcId,stId=stId))

				if stsends - tcreceives > 1:
					self.logger.error("用例:{name}  时间:{time}  学生发送数据量:{sends}  老师接受数据量:{receives}  订单号:{orderNo}  老师ID:{tcId}  学生ID:{stId}".format(name=self.name,time=cur_time,sends=stsends,receives=tcreceives,orderNo=orderNo,tcId=tcId,stId=stId))
				time.sleep(1)
			else:
				pass
				
if __name__ == '__main__':
	a = Logger('history/actions','file')
	a.info("testadfadfasdfasdfadfsfsf")

