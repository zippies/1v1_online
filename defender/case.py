from .main.basecase import BaseCase,CheckError,testcase
from collections import Counter
import random

class TestCase(BaseCase):
	desc = "一学生，一老师,全流程正确性检查"
	caseData = None
	def __init__(self):
		BaseCase.__init__(self)

	@testcase(caseData)
	def run(self):
		num = random.randint(0,1)
		assert self.checkCallbacks(self.students[0],[]) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],[])
		assert self.checkCallbacks(self.teachers[0],[]) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],[])
		self.clearCallbacks()

		self.login(self.teachers)
		assert self.checkCallbacks(self.teachers[0],['tc_onlogin']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],['tc_onlogin'])
		
		print("老师登录成功|1")

		self.login(self.students)

		assert self.checkCallbacks(self.students[0],['st_onlogin']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],['st_onlogin'])
		self.clearCallbacks()
		print("学生登录成功|2")
		
		self.setfree(self.teachers)

		self.submitquestion(self.students)
		
		assert self.checkCallbacks(self.teachers[0],['tc_onsetteacherstat','tc_onnotifyneworder']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],['tc_onsetteacherstat','tc_onnotifyneworder'])
		assert self.checkCallbacks(self.students[0],['st_onsubmitquestion']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],['st_onsubmitquestion'])
		self.clearCallbacks()
		print("学生发题成功|3")
		
		storderNo = self.getStOrderNo(self.students[0])
		self.graborder(self.teachers)
		
		assert self.checkCallbacks(self.students[0],['st_onnotifygraborder', 'st_onnotifyorderresult']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],['st_onnotifygraborder', 'st_onnotifyorderresult'])
		assert self.checkCallbacks(self.teachers[0],['tc_ongraborder']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],['tc_ongraborder'])
		self.clearCallbacks()
		print("老师抢单成功|4")
		
		self.setbusy(self.teachers)

		tcorderNo = self.getTcOrderNo(self.teachers[0])
		
		assert tcorderNo == storderNo,"student orderNo:%s not equals teacher grabbed orderNo:%s" %(storderNo,tcorderNo)
		
		self.createvoicechannel(self.teachers+self.students)
		
		assert self.checkCallbacks(self.students[0],['st_oncreatevoicechannel']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],['st_oncreatevoicechannel'])
		assert self.checkCallbacks(self.teachers[0],['tc_onsetteacherstat','tc_oncreatevoicechannel']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],['tc_onsetteacherstat','tc_oncreatevoicechannel'])
		self.clearCallbacks()
		
		self.newmedia(self.teachers+self.students)
		assert self.checkCallbacks(self.students[0],[]) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],[])
		assert self.checkCallbacks(self.teachers[0],[]) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],[])
		self.clearCallbacks()
		
		self.connectmedia(self.teachers+self.students)
		assert self.checkCallbacks(self.students[0],[]) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],[])
		assert self.checkCallbacks(self.teachers[0],[]) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],[])
		self.clearCallbacks()
		
		self.enterroom(self.teachers+self.students)
		assert self.checkCallbacks(self.students[0],[]) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],[])
		assert self.checkCallbacks(self.teachers[0],[]) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],[])
		self.clearCallbacks()
		
		self.enterroomresult(self.teachers+self.students)

		self.waitCallback(self.students[0],'st_onnotifystartanalyzequestion')
		self.waitCallback(self.teachers[0],'tc_onnotifystartanalyzequestion')
		assert self.checkCallbacks(self.students[0],['st_onnotifystartanalyzequestion','st_onenterroomresult']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],['st_onnotifystartanalyzequestion','st_onenterroomresult'])
		assert self.checkCallbacks(self.teachers[0],['tc_onnotifystartanalyzequestion','tc_onenterroomresult']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],['tc_onnotifystartanalyzequestion','tc_onenterroomresult'])
		self.clearCallbacks()
		
		self.startaction(self.teachers+self.students)

		self.beginexplain(self.teachers)
		assert self.checkCallbacks(self.students[0],['st_onnotifytcbeginexplain', 'st_onnotify_openstream']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],['st_onnotifytcbeginexplain','st_onnotify_openstream'])
		assert self.checkCallbacks(self.teachers[0],['tc_onbeginexplain', 'tc_onnotify_openstream']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],['tc_onbeginexplain', 'tc_onnotify_openstream'])
		self.clearCallbacks()
		print("老师开始讲解|5")
		self.sleep(1)
		
		self.suspendexplain(self.students)
		assert self.checkCallbacks(self.students[0],['st_onsuspendexplain']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],['st_onsuspendexplain'])
		assert self.checkCallbacks(self.teachers[0],['tc_onnotifystsuspendexplain']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],['tc_onnotifystsuspendexplain'])
		self.clearCallbacks()
		if num == 2:
			self.endexplain(self.students)  
			assert self.checkCallbacks(self.students[0],['st_onendexplain']) is True,"callbacks check failed\
			:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],['st_onendexplain'])
			assert self.checkCallbacks(self.teachers[0],['tc_onnotifystendexplain']) is True,"callbacks check failed\
			:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],['tc_onnotifystendexplain'])
			self.clearCallbacks()
			print("学生结束讲解|6")
		else:
			self.endexplain(self.teachers)
			assert self.checkCallbacks(self.teachers[0],['tc_onendexplain']) is True,"callbacks check failed\
			:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],['tc_onendexplain'])
			assert self.checkCallbacks(self.students[0],['st_onnotifytcendexplain']) is True,"callbacks check failed\
			:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],['st_onnotifytcendexplain'])
			self.clearCallbacks()
			print("老师结束讲解|6")
		
		self.stopaction(self.teachers+self.students)
		assert self.checkCallbacks(self.students[0],['st_onnotify_closestream']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],['st_onnotify_closestream'])
		assert self.checkCallbacks(self.teachers[0],['tc_onnotify_closestream']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],['tc_onnotify_closestream'])
		self.clearCallbacks()
		
		self.leaveroom(self.teachers+self.students)
		assert self.checkCallbacks(self.students[0],[]) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],[])
		assert self.checkCallbacks(self.teachers[0],[]) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],[])
		self.clearCallbacks()
		
		self.closemedia(self.teachers+self.students)
		assert self.checkCallbacks(self.students[0],[]) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],[])
		assert self.checkCallbacks(self.teachers[0],[]) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],[])
		self.clearCallbacks()
		
		self.logout(self.teachers)
		assert self.checkCallbacks(self.teachers[0],['tc_onlogout']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['teacher'][self.teachers[0]],['tc_onlogout'])
		print("老师退出成功|7")

		self.logout(self.students)
		assert self.checkCallbacks(self.students[0],['st_onlogout']) is True,"callbacks check failed\
		:received callbacks:%s,expected callbacks:%s" %(self.callbacks['student'][self.students[0]],['st_onlogout'])
		self.clearCallbacks()
		print("学生退出成功|8")
