#日志模式
logmode = "file"  # all | file | print | null

#开启parallel后才可以跑level=1的case，关闭只能跑level=0的case
parallel = True
#如果parallel开启，并且casemode是all时，先跑level=1的case，然后跑case=0的case
#casemode=parallel  只跑level=1的case
#casemode=serial	只跑level=0的case
casemode = "serial"  # all | parallel | serial
#调试case时打开，生产环境关闭
debug = False
#日志和报告存放文件目录
filepath = '/data'
#日志查看服务端口
serverport = 8081


#学生拥有的方法锁
st_codeActions = ['starts','login','relogin','disconnect','submitquestion','createvoicechannel','cancelorder','newmedia','connectmedia','enterroom','enterroomresult','startaction','uploaddata','stopaction','leaveroom','suspendexplain','closemedia','recoverexplain','endexplain','logout','stops','clear']
#老师拥有的方法锁
tc_codeActions = ['starts','login','disconnect','setfree','setbusy','graborder','regretorder','createvoicechannel','beginexplain','startaction','newmedia','connectmedia','enterroom','enterroomresult','uploaddata','stopaction','leaveroom','closemedia','endexplain','logout','stops','clear']

#codeAction对应的检查点
tc_checklist_mapper = {
        'starts':[('isstart',None)],
        'login':[('isstart',None),('islogin',None)],
	'setfree':[('islogin',None),('issetfree',None)],
	'setbusy':[('islogin',None),('issetbusy',None)],
        'graborder':[('isonline',None),('isgraborder',None),('isnotifyorderresult','expected')],
        'regretorder':[('isonline',None),('isregretorder',None),('isnotifytccancelorder','expected')],
        'createvoicechannel':[('isonline',None),('iscreatevoicechannel',None)],
        'beginexplain':[('isonline',None),('isbeginexplain',None),('isnotifytcbgexplain','expected')],
        'newmedia':[('isonline',None),('isnewmedia',None)],
        'connectmedia':[('isonline',None),('isconnectmedia',None)],
        'enterroom':[('isonline',None),('isenterroom',None)],
	'enterroomresult':[('isonline',None),('isenterroomresult',None)],
        'startaction':[('isonline',None),('isstartaction',None)],
        'uploaddata':[('isonline',None),('isuploaddata',None)],
        'stopaction':[('isonline',None),('isstopaction',None),('isnotifyclosestream','expected')],
        'leaveroom':[('isonline',None),('isleaveroom',None)],
        'closemedia':[('isonline',None),('isclosemedia',None)],
        'endexplain':[('isonline',None),('isendexplain',None),('isnotifytcendexplain','expected')],
        'logout':[('isonline',None),('islogout',None)],
	'disconnect':[('isdisconnect',None)],
        'stops':[('isstop',None)]
}

#执行学生动作后需要检查的学生状态
st_checklist_mapper = {
        'starts':[('isstart',None)],
        'login':[('isstart',None),('islogin',None)],
	'relogin':[('isrelogin',None)],
        'submitquestion':[('isonline',None),('issubmitquestion',None),('isnotifyneworder','expected')],
        'cancelorder':[('isonline',None),('iscancelorder',None),('isnotifystcancelorder','expected')],
        'createvoicechannel':[('isonline',None),('iscreatevoicechannel',None)],
        'newmedia':[('isonline',None),('isnewmedia',None)],
        'connectmedia':[('isonline',None),('isconnectmedia',None)],
        'enterroom':[('isonline',None),('isenterroom',None)],
	'enterroomresult':[('isenterroomresult',None)],
        'startaction':[('isonline',None),('isstartaction',None)],
        'uploaddata':[('isonline',None),('isuploaddata',None)],
        'stopaction':[('isonline',None),('isstopaction',None),('isnotifyclosestream','expected')],
        'leaveroom':[('isonline',None),('isleaveroom',None)],
        'closemedia':[('isonline',None),('isclosemedia',None)],
        'suspendexplain':[('isonline',None),('issuspendedexplain',None),('isnotifystsuspendexplain','expected')],
        'recoverexplain':[('isonline',None),('isrecoverexplain',None),('isnotifystrecoverexplain','expected')],
        'endexplain':[('isonline',None),('isendexplain',None),('isnotifystendexplain','expected')],
        'logout':[('isonline',None),('islogout',None)],
		'disconnect':[('isonline',None),('isdisconnect',None)],
        'stops':[('isstop',None)]
}
