import os,sys,time,json
from multiprocessing import Manager,Process
from datetime import datetime
from defender.configs import logmode,parallel,casemode,debug,filepath
from defender.case import TestCase

class Runner(object):
	def __init__(self,stype,logpath,caseData):
		self.testcase = TestCase()
		self.caseData = caseData
		self.logdir = logpath
		self.stype = stype
		self._initLogPath()

	def collectResult(self,case):
		if not case.result['result']:
			json.dump(dict(case.result)['errorMsg'],open('error.json','w'))

	def _initLogPath(self):
		if not os.path.isdir(self.logdir) and logmode != 'null':
			os.makedirs(self.logdir)

	def _initCase(self,case,level=0):
		logpath = os.path.join(self.logdir,'case')
		result = Manager().dict()
		setattr(case,'result',result)
		setattr(case,'logpath',logpath)
		setattr(case,'debug',debug)
		setattr(case,'logmode',logmode)
		setattr(case,'level',level)
		setattr(case,'caseData',self.caseData)
		return case

	def runTest(self):
		case = self._initCase(self.testcase)
		case.run()
		self.collectResult(case)
		json.dump(dict(case.result),open('%s.json' %self.stype,'w'))

if __name__ == '__main__':
	import sys
	ip = sys.argv[1]
	tcnos = sys.argv[2]
	tcpwd = sys.argv[3]
	stnos = sys.argv[4]
	stpwd = sys.argv[5]
	imgurl = sys.argv[6]
	logpath = sys.argv[7]
	stype = sys.argv[8]
	caseData = {
		'students' : [str(i) for i in eval(stnos)],
		'teachers' : [str(i) for i in eval(tcnos)],
		'st_passwd' : stpwd,
		'tc_passwd' : tcpwd,
		'server' : sys.argv[1],
		'imgurl' : imgurl
	}
	runner = Runner(stype,logpath,caseData)
	runner.runTest()
			
			
			
