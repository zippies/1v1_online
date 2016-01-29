from multiprocessing import Manager,Event,Process
from .logger import RecordData,Logger
from .student import Student
from .teacher import Teacher
from ..configs import st_checklist_mapper,tc_checklist_mapper,\
					st_codeActions,tc_codeActions
from collections import Counter
import time,threading,sys,os

class ActionTimeOut(Exception):
	def __init__(self,info):
		self.info = info

	def __str__(self):
		return self.info

class CheckError(Exception):
	def __init__(self,info):
		self.info = info

	def __str__(self):
		return self.info

class CaseError(Exception):
	def __init__(self,info):
		self.info = info

	def __str__(self):
		return self.info

class ServerError(Exception):
	def __init__(self,info):
		self.info = info

	def __str__(self):
		return self.info		

		
class NoneType(object):
	def __init__(self):
		self.code = None
		
class CallbackRes(object):
	def __init__(self,res=NoneType(),name=None,seq=None,info=None):
		self.res = res
		self.name = name
		self.seq = seq
		self.info = info			

def testcase(caseData):
	
	def _getLock(eventDict):
		'''
			生成多进程的锁，通过该锁控制学生和老师动作的执行
		'''
		lock = {}
		for key in eventDict:
			lock[key] = Event()
		return lock

		
	def _getserver(ip):
		'''
			获取测试服务ip
		'''
		import requests,random
		r = requests.get(ip)
		servers = []
		if r.status_code == 200:
			try:
				servers = eval(r.text)['hosts']
			except:
				raise ServerError("All server is crashed,%s" %r.text)
		else:
			raise ServerError("Server return:%s" %r.status_code)

		return random.sample(servers,1)[0]
		
	def _deco(func):
	
		def _func(self):
			starttime = time.time()
			self.students = self.caseData.get('students')
			self.teachers = self.caseData.get('teachers')
			self.tc_passwd = self.caseData.get('tc_passwd')
			self.st_passwd = self.caseData.get('st_passwd')
			self.imgurl = self.caseData.get('imgurl')
			self.server = _getserver(self.caseData.get('server'))
			#self.tc_server = {"ip":"180.150.184.115","port":19932}
			#self.st_server = {"ip":"180.150.184.115","port":19933}
			self.result["logpath"] = self.logpath
			self.grouplist = Manager().list()

			#学生和老师进程list
			self.processes = []
			#存放订单状态字典

			#存放case用户id的字典
			self.userids = {
					"student":{},
					"teacher":{}
			}
			#存放收到的所有回调的list
			self.callbacks = {
					"student":{},
					"teacher":{}
			}
			#记录所有回调类，可以基于该字典拿到回调所有返回信息
			self.callbackres = {
					"student":{},
					"teacher":{}
			}

			self.locks = {
					"student":{},
					"teacher":{}
				}

			self.user_status = {
					"student":{},
					"teacher":{}
			}

			self.orderinfo = Manager().dict()

			self.logger = Logger(self.logpath,getattr(self,'logmode'))

			for st_no in self.students:
				self.locks['student'][st_no] = _getLock(self.st_codeActions)
				self.user_status['student'][st_no] = Manager().dict()
				self.callbackres['student'][st_no] = Manager().list()
				self.userids['student'][st_no] = Manager().list()
				self.callbacks['student'][st_no] = Manager().list()
				try:
					st = Student(
								st_no,
								self.st_passwd.encode(),
								self.imgurl.encode(),
								self.server,
								self.locks["student"][st_no],
								self.user_status['student'][st_no],
								self.orderinfo,
								self.userids['student'][st_no],
								self.callbacks['student'][st_no],
								self.logger,
								self.callbackres['student'][st_no]
								)
					self.processes.append(st)

				except Exception as e:
					self.result["result"] = False
					self.result["errorMsg"] = "Start Student Failed!,ErrorInfo:%s" %str(e)
					return

			for tc_no in self.teachers:
				self.locks['teacher'][tc_no] = _getLock(self.tc_codeActions)
				self.user_status['teacher'][tc_no] = Manager().dict()
				self.callbackres['teacher'][tc_no] = Manager().list()
				self.userids['teacher'][tc_no] = Manager().list()
				self.callbacks['teacher'][tc_no] = Manager().list()
				try:
					tc = Teacher(
								tc_no,
								self.tc_passwd.encode(),
								self.server,
								self.locks["teacher"][tc_no],
								self.user_status['teacher'][tc_no],
								self.orderinfo,
								self.userids['teacher'][tc_no],
								self.callbacks['teacher'][tc_no],
								self.logger,
								self.grouplist,
								self.callbackres['teacher'][tc_no]
								)
					self.processes.append(tc)
				except Exception as e:
					self.result["result"] = False
					self.result["errorMsg"] = "Start Teacher Failed!,ErrorInfo:%s" %str(e)
					return
					
			for p in self.processes:
				p.daemon = True
				p.start()

			if self.debug:
				self.starts(self.teachers+self.students)
				func(self)
				for i,pro in enumerate(self.processes):
					if pro.is_alive():
						sts = len(self.students)
						if i <= sts - 1 :
							self.stops(self.students[i])
						else:
							self.stops(self.teachers[i-sts])
					else:
						self.logger.info("pro is dead:%s"%i)
				for p in self.processes:
					p.join()

				runtime = time.time() - starttime
				self.result['result'] = True
				self.result['errorMsg'] = None
				self.result['runtime'] = round(runtime,2)
			else:
				try:
					self.starts(self.teachers+self.students)
					func(self)
					for i,pro in enumerate(self.processes):
						if pro.is_alive():
							sts = len(self.students)
							if i <= sts - 1 :
								self.stops(self.students[i])
							else:
								self.stops(self.teachers[i-sts])
						else:
							self.logger.info("pro is dead:%s"%i)
					for p in self.processes:
						p.join()
						
					runtime = time.time() - starttime
					self.result['result'] = True
					self.result['errorMsg'] = None
					self.result['runtime'] = round(runtime,2)
					self.logger.info(self.result)
				except Exception as e:
					self.ispass = False
					runtime = time.time() - starttime
					self.result['result'] = False
					stId = self.getUserId(self.students[0]) if self.students else None
					tcId = self.getUserId(self.teachers[0]) if self.teachers else None
					orderNo = self.orderinfo['orderNo'].decode() if self.orderinfo['orderNo'] else None
					errorMsg = "%s.(stId:%s,tcId:%s,orderNo:%s)" %(str(e),stId,tcId,orderNo)
					self.result['errorMsg'] = errorMsg
					self.result['runtime'] = round(runtime,2)
					self.logger.info(errorMsg)
					self.logger.error(errorMsg)
					return
					
					
				if self.ispass:
					runtime = time.time() - starttime
					self.result['result'] = True
					self.result['errorMsg'] = None
					self.result['runtime'] = round(runtime,2)
		return _func
		
	return _deco

class BaseCase(object):
	st_codeActions = st_codeActions
	tc_codeActions = tc_codeActions
	def __init__(self):
		self.ispass = True

	def gettype(self,userno):
		return 'teacher' if userno in self.teachers else 'student'
			
	def doAction(self,usernos,action,nowait=False,timeout=20):
		'''
		args
			action  :  sample - starts,login,graborder
			type    :  teacher  |  student
			usernos :  userno
			nowait  :  只执行动作，不判断回调等，如需验证在testcase内执行waitnotify进行判断
			timeout :  timeout(seconds)
		'''
		if action not in self.tc_codeActions+self.st_codeActions:
			raise CaseError("action '%s' undefined" %action)
		if not isinstance(usernos,list):
			usernos = [usernos]

		for userno in usernos:
			if userno not in self.teachers+self.students:
				raise CaseError("unknown user '%s'" %userno)
			type = self.gettype(userno)
			self.logger.info("    %s:%s %s" %(type,userno,action))
			self.locks[type][userno][action].set()
			#check all notify
			if nowait:
				continue
			check_items = tc_checklist_mapper[action] if type=='teacher' else st_checklist_mapper[action]
	
			for check_item in check_items:
				#check_item : ('islogin',None)
				checktype = check_item[1] or type
				
				res = self.check_status(checktype,userno,check_item[0],timeout)

				if not res['result']:
					raise CheckError(res['errorMsg'])
					
			print("%s %s success.." %(type,action))

	def doActionWithNoWait(self,param):
		'''
		params:
			action  :  (userno,action)   sample : ('11166660002','login','st_onlogin')
		'''
		userno = param[0]
		action = param[1]
		type = self.gettype(userno)
		self.logger.info("    %s:%s %s" %(type,userno,action))
		self.locks[type][userno][action].set()
	
	def doMultiAction(self,usernos,action):
		'''
		同时执行多个动作，不判断回调等，如需验证在testcase内执行waitnotify进行判断
			actionlist  :  [(userno,action),(userno,action)]
		'''
		if not isinstance(usernos,list):
			usernos = [usernos]
		actions = [(userno,action) for userno in usernos]
		threads = []
		for a in actions:
			t = threading.Thread(target=self.doActionWithNoWait,args=(a,))
			threads.append(t)
		
		for t in threads:
			t.start()
		
		for t in threads:
			t.join()

						
	def check_status(self,type,userno,check_item,timeout=20):
		'''
		args
			type     :  teacher |  student  |  expected  |  any
			userno   :  userno
			check_item  :  isnfneworder,issubmitquestion,..
		return
			result   :  True|False
			type     :  0 成功  |  -1 收到errorinfo   |  -2  wait timeout
			errorMsg :  错误信息
		'''
		if type in ['teacher','student']:
			return self.waitStatus(type,userno,check_item,timeout)
		elif type == 'expected':
			type = 'student' if userno in self.teachers else 'teacher'
			userno = self.students[0] if userno in self.teachers else self.teachers[0]
			return self.waitStatus(type,userno,check_item,timeout)
		else:
			pass

	def waitStatus(self,type,userno,check_item,timeout=20):
		'''
			type    :  teacher | student
			userno  :  userno
			check_item :  islogin
		'''
		start = time.time()
		#print("%s,%s,%s" %(type,userno,check_item))
		while not self.user_status[type][userno][check_item].get("status"):
			errorinfo = self.user_status[type][userno][check_item].get('errorinfo')
			if errorinfo:
				return {"result":False,"errorMsg":errorinfo}

			if time.time()-start < timeout:
				time.sleep(0.1)
			else:
				break
		else:
			return {"result":True,"type":0,"errorMsg":None}
		
		#20秒超时
		raise ActionTimeOut("%s '%s' timeout" %(type.capitalize(),check_item[2:]))
	
	def waitCallback(self,userno,expect_callback,timeout=20):
		'''
		等待某个回调，并返回回调内容
			expect_callback  :  ongraborder
		'''
		if not isinstance(userno,str):
			raise CaseError("waitCallback need a userno,not a list")
		type = self.gettype(userno)
		self.logger.info("    %s:%s waitting callback:%s %ss" %(type,userno,expect_callback,timeout))
		start = time.time()
		while expect_callback not in self.callbacks[type][userno]:
			if time.time() - start < timeout:
				time.sleep(0.1)
			else:
				break
		else:
			callbackreslist = self.callbackres[type][userno]
			return self.getCallbackResitems(expect_callback,callbackreslist)
		
		if expect_callback in ['tc_onnotifyneworder']:
			return [CallbackRes()]
		else:
			self.logger.info("    wait [%s] timeout,current callbacks:%s" %(expect_callback,self.callbacks[type][userno]))
			raise ActionTimeOut("wait callback '%s' timeout" %expect_callback)

	def waitCallbacks(self,usernos,expect_callback,timeout=20):
		if not isinstance(usernos,list):
			usernos = [usernos]
		r = []
		for userno in usernos:
			r.append(self.waitCallback(userno,expect_callback,timeout))
		return r
		
	def getCallbackResitems(self,expect_callback,callbackreslist):
		'''
			返回callbackreslist中所有name等于expect_callback的子元素
			items  :  sample - {'seq': 1, 'name': 'tc_onlogin', 'res': <cstructs.tcstruct.TcLoginRes object at 0x7f21941f44d0>}
		'''
		items = [item for item in callbackreslist if item['name'] == expect_callback]
		callbackResList = []
		for i in items:
			callbackResList.append(CallbackRes(i['res'],i['name'],i.get('seq',None),i.get('info',None)))

		return callbackResList or [CallbackRes()]

	def getUserId(self,userno):
		'''
			返回userno对应的stId or tcId
		'''
		type = self.gettype(userno)
		return self.userids[type][userno][0] if self.userids[type][userno] else None
	
	def getUserNo(self,userId):
		'''
			返回userId对应的userno
		'''
		for userno in self.teachers:
			if userId in self.userids['teacher'][userno]:
				return userno
		
		for userno in self.students:
			if userId in self.userids['student'][userno]:
				return userno
	
	def removefromlist(self,elems,elist):
		for ele in elems:
			if ele in elist:
				count = Counter(elist)
				for i in range(count[ele]):
					elist.remove(ele)

	def checkCallbacks(self,usernos,expect_callbacks,ignore=[]):
		'''
			判断当前时间点userno 收到的callbacks是否和预期的expect_callbacks一致
		'''
		if isinstance(usernos, str):
			usernos = [usernos]

		if isinstance(ignore, str):
			ignore = [ignore]

		for userno in usernos:
			type = self.gettype(userno)
			cb_now = self.callbacks[type][userno]
			self.removefromlist(ignore,cb_now)
			self.logger.info("    %s:%s checking callbacks.." %(type,userno))
			self.logger.info("        Current received:%s Expected:%s" %(cb_now,expect_callbacks))

			if set(expect_callbacks) != set(cb_now):
				for cb in cb_now:
					if cb not in expect_callbacks:
						return False
					
					count_cb = Counter(cb_now)
					count_expect = Counter(expect_callbacks)

					if count_cb[cb] != count_expect[cb]:
						if cb == 'tc_onnotifyneworder':
							continue
						else:
							return False
				for cb in expect_callbacks:
					if cb not in cb_now:
						return False
		return True

	def getCallbacks(self,userno):
		if isinstance(userno,list):
			if len(userno) > 1:
				raise CaseError("need one but %s were given" %len(userno))
			else:
				userno = userno[0]
		elif isinstance(userno,str):
			pass
		else:
			raise CaseError("TypeError:need str or list but %s were given" %type(usernos))
			
		type = self.gettype(userno)
		return self.callbacks[type][userno]
			
		
	def getGroups(self):
		groups = []
		if self.grouplist:
			for i in self.grouplist:
				stId = i['stId']
				tcId = i['tcId']
				groups.append((self.getUserNo(tcId),self.getUserNo(stId)))
			return groups
		else:
			self.logger.info("no connections")
			return []
		
	def getOpesiteUserno(self,userno):
		type = self.gettype(userno)
		groups = self.getGroups()
		for i in groups:
			search_no = i[1] if type == 'student' else i[0]
			expect_no = i[0] if type == 'student' else i[1]
			if search_no == userno:
				return expect_no
		
	def getOrderedTc(self):
		for tc in self.teachers:
			r = self.waitCallback(tc,'tc_ongraborder')[0]
			if r.res.code == 0:
				return tc

	def getOrderedSt(self):
		for st in self.students:
			r = self.waitCallback(st,'st_onsubmitquestion')[0]
			if r.res.code == 0:
				return st
				
				
	def getsubmitsuccessorders(self,usernos):
		orders = []
		if isinstance(usernos,str):
			usernos = [usernos]
		for userno in usernos:
			type = self.gettype(userno)
			if type != 'student':
				raise CaseError('teacher do not have this method "getsubmitsuccessorders"')
			r = self.waitCallback(userno,'st_onsubmitquestion')[0]
			if r.res.code == 0:
				orders.append((userno,r.res.orderNo.decode()))
				
		return orders
				
	def sleep(self,second):
		self.logger.info("    case sleeping(%ss)" %second)
		time.sleep(second)
		self.logger.info("    case waked up")
		
		
	def getStOrderNo(self,userno,timeout=20):
		'''
			获取学生发题的订单号
		'''
		type = self.gettype(userno)
		if type == 'teacher':
			raise CaseError('teacher has no such function getStOrderNo!')
		
		if self.waitStatus(type,userno,'issubmitquestion',timeout=timeout):
			r = self.getCallbackResitems('st_onsubmitquestion',self.callbackres[type][userno])[0]
			return r.res.orderNo.decode() if r.res.code == 0 and r.res.orderNo else None
		
	def getTcOrderNo(self,userno,timeout=20):
		'''
			获取老师抢到的订单号
		'''
		type = self.gettype(userno)
		if type == 'student':
			raise CaseError('student has no such function getTcOrderNo!')
		
		if self.waitStatus(type,userno,'isnotifyneworder',timeout=timeout) and self.waitStatus(type,userno,'isgraborder',timeout=timeout):
			r = self.getCallbackResitems('tc_ongraborder',self.callbackres[type][userno])[0]
			return r.res.orderNo.decode() if r.res.code == 0 and r.res.orderNo else None
			
	def getStIdByOrderNo(self,orderNo):
		'''
			获取老师对应的学生Id
		'''
		pass
		
	def waitOrder(self,usernos,orderNo,timeout=20):
		if isinstance(userno, str):
			usernos = [usernos]

		starttime = time.time()
		while time.time() - starttime <= timeout:
			for userno in usernos:
				cbs = self.waitCallback(userno,'tc_onnotifyneworder')
				orders = [r.res.orderNo for r in cbs]
				if orderNo in orders:
					return

		raise ActionTimeOut("等待订单通知超时，orderNo:%s" %orderNo)


	def starts(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)

	def stops(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
		
	def login(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)

	def relogin(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
			
			
	def logout(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)

	def setfree(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
		
	def setbusy(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
		
	def submitquestion(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
		
	def graborder(self,usernos,orderNo=None,setbusy=False,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if self.level == 1:
			orderNo = self.getStOrderNo(self.students[0])
		self.orderinfo['specialOrderNo'] = orderNo
		if multi:
			if setbusy:
				self.setbusy(usernos)
				self.sleep(3)
				self.clearCallbacks(usernos)
			self.doMultiAction(usernos,action)

		else:
			if setbusy:
				self.setbusy(usernos)
				self.sleep(3)
				self.clearCallbacks(usernos)
			self.doAction(usernos,action,nowait,timeout)


	def regretorder(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)

	def cancelorder(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
			
	def beginexplain(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
		
	def suspendexplain(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
		
	def recoverexplain(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
		
	def endexplain(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
		
	def startaction(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
		
	def stopaction(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
		
	def newmedia(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
		
	def connectmedia(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)

	def closemedia(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
		
	def enterroom(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
		
	def enterroomresult(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)

	def leaveroom(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)
		
	def createvoicechannel(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)

	def uploaddata(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)

	def disconnect(self,usernos,multi=False,nowait=False,timeout=20):
		action = sys._getframe().f_code.co_name
		if multi:
			self.doMultiAction(usernos,action)
		else:
			self.doAction(usernos,action,nowait,timeout)

	def closenetwork(self,timeout=50):
		self.logger.info("    [close network]begin")
		os.system('ifconfig eth0 down')
		self.logger.info("    [close network]action done")
		start = time.time()
		while True:
			info = os.popen('netstat -apn|grep 180.150.184.115:19933|grep ESTABLISHED').readline()
			if not info:
				break
			if time.time() - start > timeout:
				raise CheckError('network did not close after %s seconds' %timeout)

		self.logger.info("    [close network]end")

	def opennetwork(self):
		self.logger.info("    [open network]begin")
		os.system('service network restart')
		self.logger.info("    [open network]end")

	def limitnetwork(self,usernos,limit=10):
		limit = limit*10
		if len(self.processes) > 2:
			raise CaseError("make sure there's only one student and one teacher in caseData")
		
		if isinstance(usernos,list):
			userno = usernos[0]

		type = self.gettype(userno)
		server = '180.150.184.115:19933' if type == 'student' else '180.150.184.115:19932'
		info = os.popen('netstat -apn|grep %s|grep ESTABLISHED' %server).readline()
		if not info:
			raise CaseError("there's no tcp connection established!")
		port = info.split(':')[1].split(' ')[0]
		self.logger.info("    [limit %s:%s network]begin" %(type,userno))
		os.system("tc qdisc add dev eth0 root handle 1:0 cbq bandwidth 100Mbit avpkt 1000 cell 8")
		os.system("tc class add dev eth0 parent 1:0 classid 1:1 cbq bandwidth 100Mbit rate %sKbit prio 8 allot 1514 cell 8 maxburst 20 avpkt 1000 bounded" %limit)
		os.system("tc class add dev eth0 parent 1:1 classid 1:2 cbq bandwidth 100Mbit rate %sKbit prio 5 allot 1514 cell 8 maxburst 20 avpkt 1000" %limit)
		os.system("tc qdisc add dev eth0 parent 1:2 handle 40: sfq")
		os.system("tc filter add dev eth0 parent 1:0 protocol ip prio 1 u32 match ip sport %s 0xffff flowid 1:2" %port)
		self.logger.info("    [limitting %s:%s]end" %(type,userno))

	def limitnetworks(self,limit=10):
		limit = limit*10
		os.system("tc qdisc add dev eth0 root handle 1:0 cbq bandwidth 100Mbit avpkt 1000 cell 8")
		os.system("tc class add dev eth0 parent 1:0 classid 1:1 cbq bandwidth 100Mbit rate %sKbit prio 8 allot 1514 cell 8 maxburst 20 avpkt 1000 bounded" %limit)
		os.system("tc class add dev eth0 parent 1:1 classid 1:2 cbq bandwidth 100Mbit rate %sKbit prio 5 allot 1514 cell 8 maxburst 20 avpkt 1000" %limit)
		os.system("tc qdisc add dev eth0 parent 1:2 handle 40: sfq")
		for server in ['180.150.184.115:19933','180.150.184.115:19932']:
			info = os.popen('netstat -apn|grep %s|grep ESTABLISHED' %server).readline()
			if not info:
				raise CaseError("there's no tcp connection established!")
			port = info.split(':')[1].split(' ')[0]
			self.logger.info("    [limit network]begin")
			os.system("tc filter add dev eth0 parent 1:0 protocol ip prio 1 u32 match ip sport %s 0xffff flowid 1:2" %port)
			self.logger.info("    [limit network]end")

	def dislimitnetwork(self):
		self.logger.info("    [dislimit network]begin")
		os.system("tc qdisc del dev eth0 root")
		self.logger.info("    [dislimit network]end")

	def kill(self,usernos):
		if isinstance(usernos,str):
			usernos = [usernos]
	
		for userno in usernos:
			self.logger.info('    killing user:%s' %userno)
			type = self.gettype(userno)
			p = self.processes[0] if type == 'student' else self.processes[1]
			p.terminate()
			self.logger.info("    user:%s is dead" %userno)	

	def clearCallbacks(self,usernos=[]):
		if not usernos:
			usernos = self.teachers + self.students
		if isinstance(usernos, str):
			usernos = [usernos]
		for userno in usernos:
			type = self.gettype(userno)
			cbs = self.callbacks[type][userno]

			for j in range(len(cbs)):
				self.callbacks[type][userno].pop()


class BackendFlow(threading.Thread,BaseCase):
	'''
		该类用于模拟后台多个老师和学生处理订单的情况
	'''
	default_flow = [
				'tc_setbusy',
				'tc_createvoicechannel',
				'st_createvoicechannel',
				'tc_newmedia',
				'st_newmedia',
				'tc_connectmedia',
				'st_connectmedia',
				'tc_enterroom',
				'st_enterroom',
				'tc_enterroomresult',
				'st_enterroomresult',
				'tc_waitCallback:tc_onnotifystartanalyzequestion',
				'st_waitCallback:st_onnotifystartanalyzequestion',
				'tc_startaction',
				'st_startaction',
				'tc_beginexplain',
				'st_suspendexplain',
				'st_endexplain',
				'tc_stopaction',
				'st_stopaction',
				'tc_leaveroom',
				'st_leaveroom',
				'tc_closemedia',
				'st_closemedia',
				'tc_logout',
				'st_logout',
				'tc_stops',
				'st_stops'
			  ]
	def __init__(self,case,groups,backresult,action_flow=None,blockOn=None):
		BaseCase.__init__(self)
		threading.Thread.__init__(self)
		self.case = case
		self.groups = groups
		self.action_flow = action_flow or self.default_flow
		self.blockOn = blockOn
		self.backresult = backresult

	def doActionFlow(self,group,action_flow,blockOn):
		for action in action_flow:
			waitcallback = None
			if ':' in action:
				action,waitcallback = action.split(':')

			type,action = action.split('_')
			tcno,stno = group[0],group[1]
			
			if type not in ['st','tc']:
				raise CaseError("action_flow should start with 'tc' or 'st'")
				
			userno = tcno if type == 'tc' else stno
			actionstr = "self.case.%s('%s')" %(action,userno) if not waitcallback else "self.case.%s('%s','%s')" %(action,userno,waitcallback)
			try:
				eval(actionstr)
			except Exception as e:
				self.backresult.append({'tcno':tcno,'stno':stno,'errorMsg':str(e)})
				break

	def run(self):
		ts = []
		for group in self.groups:
			t = threading.Thread(target=self.doActionFlow,args=(group,self.action_flow,self.blockOn))
			ts.append(t)
		
		for t in ts:
			t.start()
		
		for t in ts:
			t.join()

			
			
			
			
			
			
			
			
			
			
			
			
		
