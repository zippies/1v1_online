from multiprocessing import Process
import time
from .cstructs.ststruct import *

class Student(Process):
    def __init__(self,username,pwd,imgurl,server,e_dict,status_dict,orderinfo,userids,callbacks,logger,callbackres=None):
        Process.__init__(self)
        self.username = username.encode('utf-8')
        self.pwd = pwd
        self.imgurl = imgurl
        self.e_dict = e_dict
        self.userids = userids
        self.userId = None
        self.orderNo = None
        self.tcId = None
        self.status_dict = status_dict
        self.orderinfo = orderinfo
        self.senddatas = 0
        self.receivedatas = 0
        self.current_stat = None
        self.streamclosed = None
        self.server = server
        self.callbacks = callbacks
        self.logger = logger
        self.callbackres = callbackres
        self._initSelf()

    def __initSDK(self):
        self.core=CDLL('libStSDKWrap.so')
        self.media=CDLL('libsunet2.so')
        #转发服务回调
        OnLoginCb=CFUNCTYPE(None,StLoginRes,c_uint)
        OnReloginCb=CFUNCTYPE(None,StLoginRes,c_uint)
        OnLogoutCb=CFUNCTYPE(None,StLogoutRes,c_uint)
        OnDisconnectCb=CFUNCTYPE(None,DisconnectInfo)
        OnSubmitQuestionCb=CFUNCTYPE(None,SubmitQuestionRes,c_uint)
        OnCreateVoiceChannelCb=CFUNCTYPE(None,CreateVoiceChannelRes,c_uint)
        NotifyOrderResultCb=CFUNCTYPE(None,AssignOrderResultReq,c_uint)
        NotifyTcCancelOrderCb=CFUNCTYPE(None,TcCancelOrderReq,c_uint)
        OnAddQuestionImgCb=CFUNCTYPE(None,AddQuestionImgRes,c_uint)
        OnStCancelOrderCb=CFUNCTYPE(None,StCancelOrderRes,c_uint)
        NotifyTcBeginExplainCb=CFUNCTYPE(None,TcBeginExplainReq,c_uint)
        NotifyTcEndExplainCb=CFUNCTYPE(None,TcEndExplainReq,c_uint)
        OnStEndExplainCb=CFUNCTYPE(None,StEndExplainRes,c_uint)
        OnStSuspendExplainCb=CFUNCTYPE(None,StSuspendExplainRes,c_uint)
        OnStRecoverExplainCb=CFUNCTYPE(None,StRecoverExplainRes,c_uint)
        NotifyPeerDisconnectCb=CFUNCTYPE(None,PeerDisconnectReq,c_uint)
        NotifyGrabOrderCb=CFUNCTYPE(None,TeacherGrabReq,c_uint)
        NotifyPushOrderCb=CFUNCTYPE(None,TeacherPushReq,c_uint)
        SdkLogCb=CFUNCTYPE(None,c_char_p)
        OnStReportYixinFilenameCb=CFUNCTYPE(None,StReportYixinFilenameRes,c_uint)
        NotifySystemCb=CFUNCTYPE(None,StSystemNoticeReq,c_uint)
        OnStEnterRoomResultCb=CFUNCTYPE(None,StEnterRoomResultRes,c_uint)
        NotifyStartAnalyzeQuestionCb=CFUNCTYPE(None,StStartAnalyzeQuestionReq,c_uint)
        #媒体服务回调
        Data=CFUNCTYPE(None,c_void_p,c_int,c_char_p,c_int)
        Log=CFUNCTYPE(None,c_int,c_char_p,c_int)
        Notify=CFUNCTYPE(None,c_void_p,c_int,c_int)

        #init
        self.media.argtypes=[Data,Log,Notify,c_void_p]
        self.core.CreateWenbaStResponseWrap.argtypes=[OnLoginCb,OnReloginCb,OnLogoutCb,OnDisconnectCb,OnSubmitQuestionCb,NotifyOrderResultCb,OnCreateVoiceChannelCb,NotifyTcCancelOrderCb,OnAddQuestionImgCb,OnStCancelOrderCb,NotifyTcBeginExplainCb,NotifyTcEndExplainCb,OnStEndExplainCb,OnStSuspendExplainCb,OnStRecoverExplainCb,NotifyPeerDisconnectCb,NotifyGrabOrderCb,NotifyPushOrderCb,SdkLogCb,OnStReportYixinFilenameCb]
        self.core.CreateWenbaStResponseWrap.restype=c_void_p
        self._onlogincb_fn_st=OnLoginCb(self.onlogin)
        self._onrelogincb_fn_st=OnReloginCb(self.onrelogin)
        self._onlogoutcb_fn_st=OnLogoutCb(self.onlogout)
        self._ondisconnectcb_fn_st=OnDisconnectCb(self.ondisconnect)
        self._onsubmitquestioncb_fn_st=OnSubmitQuestionCb(self.onsubmitquestion)
        self._notifyorderresultcb_fn_st=NotifyOrderResultCb(self.notifyorderresult)
        self._oncreatevoicechannelcb_fn_st=OnCreateVoiceChannelCb(self.oncreatevoicechannel)
        self._notifytccancelordercb_fn_st=NotifyTcCancelOrderCb(self.notifytccancelorder)
        self._onaddquestionimgcb_fn_st=OnAddQuestionImgCb(self.onaddquestionimg)
        self._onstcancelordercb_fn_st=OnStCancelOrderCb(self.onstcancelorder)
        self._notifytcbeginexplaincb_fn_st=NotifyTcBeginExplainCb(self.notifytcbeginexplain)
        self._notifytcendexplaincb_fn_st=NotifyTcEndExplainCb(self.notifytcendexplain)
        self._onstendexplaincb_fn_st=OnStEndExplainCb(self.onstendexplain)
        self._onstsuspendexplaincb_fn_st=OnStSuspendExplainCb(self.onstsuspendexplain)
        self._onstrecoverexplaincb_fn_st=OnStRecoverExplainCb(self.onstrecoverexplain)
        self._notifypeerdisconnectcb_fn_st=NotifyPeerDisconnectCb(self.notifypeerdisconnect)
        self._notifygrabordercb_fn_st=NotifyGrabOrderCb(self.notifygraborder)
        self._notifypushordercb_fn_st=NotifyPushOrderCb(self.notifypushorder)
        self._sdklogcb=SdkLogCb(self.sdklog)
        self._onstreportyixinfilenamecb_fn_st=OnStReportYixinFilenameCb(self.onstreportyixinfilename)
        self._notifysystemcb_fn_st=NotifySystemCb(self.notifysystem)
        self._onstenterroomresultcb_fn_st=OnStEnterRoomResultCb(self.onstenterroomresult)
        self._notifystartanalyzequestioncb_fn_st=NotifyStartAnalyzeQuestionCb(self.notifystartanalyzequestion)

        self._data_fn=Data(self.data_fn)
        self._log_fn=Log(self.log_fn)
        self._notify_fn=Notify(self.notify_fn)


        self.handlereq=self.core.CreateWenbaStRequestWrap()
        self.handleres=self.core.CreateWenbaStResponseWrap(
                self._onlogincb_fn_st,
                self._onrelogincb_fn_st,
                self._onlogoutcb_fn_st,
                self._ondisconnectcb_fn_st,
                self._onsubmitquestioncb_fn_st,
                self._notifyorderresultcb_fn_st,
                self._oncreatevoicechannelcb_fn_st,
                self._notifytccancelordercb_fn_st,
                self._onaddquestionimgcb_fn_st,
                self._onstcancelordercb_fn_st,
                self._notifytcbeginexplaincb_fn_st,
                self._notifytcendexplaincb_fn_st,
                self._onstendexplaincb_fn_st,
                self._onstsuspendexplaincb_fn_st,
                self._onstrecoverexplaincb_fn_st,
                self._notifypeerdisconnectcb_fn_st,
                self._notifygrabordercb_fn_st,
                self._notifypushordercb_fn_st,
                self._sdklogcb,
                self._onstreportyixinfilenamecb_fn_st,
                self._notifysystemcb_fn_st,
                self._onstenterroomresultcb_fn_st,
                self._notifystartanalyzequestioncb_fn_st
                )
		
    def _initSelf(self):
        self.status_dict['isstart'] = {"status":False,"errorinfo":None}
        self.status_dict['islogin'] = {"status":False,"errorinfo":None}
        self.status_dict['islogout'] = {"status":False,"errorinfo":None}
        self.status_dict['isrelogin'] = {"status":False,"errorinfo":None}
        self.status_dict['isstop'] = {"status":False,"errorinfo":None}
        self.status_dict['isonline'] = {"status":False,"errorinfo":None}
        self.status_dict['issubmitquestion'] = {"status":False,"errorinfo":None}
        self.status_dict['isnotifyorderresult'] = {"status":False,"errorinfo":None}
        self.status_dict['iscreatevoicechannel'] = {"status":False,"errorinfo":None}
        self.status_dict['isnotifytccancelorder'] = {"status":False,"errorinfo":None}
        self.status_dict['isaddimgsuccess'] = {"status":False,"errorinfo":None}
        self.status_dict['iscancelorder'] = {"status":False,"errorinfo":None}
        self.status_dict['isnotifytcbgexplain'] = {"status":False,"errorinfo":None}
        self.status_dict['isnotifytcendexplain'] = {"status":False,"errorinfo":None}
        self.status_dict['isendexplain'] = {"status":False,"errorinfo":None}
        self.status_dict['issuspendedexplain'] = {"status":False,"errorinfo":None}
        self.status_dict['isrecoverexplain'] = {"status":False,"errorinfo":None}
        self.status_dict['isnotifygraborder'] = {"status":False,"errorinfo":None}
        self.status_dict['isnotifypushorder'] = {"status":False,"errorinfo":None}
        self.status_dict['isreportyixinfilename'] = {"status":False,"errorinfo":None}
        self.status_dict['isnotifypeerdisconnect'] = {"status":False,"errorinfo":None}
        self.status_dict["isnewmedia"] = {"status":False,"errorinfo":None}
        self.status_dict['isonmedia'] = {"status":False,"errorinfo":None}
        self.status_dict["isstartaction"] = {"status":False,"errorinfo":None}
        self.status_dict["isstopaction"] = {"status":False,"errorinfo":None}
        self.status_dict["isconnectmedia"] = {"status":False,"errorinfo":None}
        self.status_dict["isclosemedia"] = {"status":False,"errorinfo":None}
        self.status_dict["isenterroom"] = {"status":False,"errorinfo":None}
        self.status_dict["isenterroomresult"] = {"status":False,"errorinfo":None}
        self.status_dict["isuploaddata"] = {"status":False,"errorinfo":None}
        self.status_dict["isleaveroom"] = {"status":False,"errorinfo":None}
        self.status_dict["isdisconnect"] = {"status":False,"errorinfo":None}
        self.status_dict['issdklog'] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifyclosestream"] = {"status":False,"errorinfo":None}
        self.orderinfo['student'] = {"id":None,"name":None,"senddatas":0,"receivedatas":0}
        self.orderinfo['orderNo'] = None
        self.orderinfo['teacher'] = {"id":None,"name":None,"senddatas":0,"receivedatas":0}

    def clear(self):
        self.status_dict['isstart'] = {"status":False,"errorinfo":None}
        self.status_dict['islogin'] = {"status":False,"errorinfo":None}
        self.status_dict['islogout'] = {"status":False,"errorinfo":None}
        self.status_dict['isrelogin'] = {"status":False,"errorinfo":None}
        self.status_dict['isstop'] = {"status":False,"errorinfo":None}
        self.status_dict['isonline'] = {"status":False,"errorinfo":None}
        self.status_dict['issubmitquestion'] = {"status":False,"errorinfo":None}
        self.status_dict['isnotifyorderresult'] = {"status":False,"errorinfo":None}
        self.status_dict['iscreatevoicechannel'] = {"status":False,"errorinfo":None}
        self.status_dict['isnotifytccancelorder'] = {"status":False,"errorinfo":None}
        self.status_dict['isaddimgsuccess'] = {"status":False,"errorinfo":None}
        self.status_dict['iscancelorder'] = {"status":False,"errorinfo":None}
        self.status_dict['isnotifytcbgexplain'] = {"status":False,"errorinfo":None}
        self.status_dict['isnotifytcendexplain'] = {"status":False,"errorinfo":None}
        self.status_dict['isendexplain'] = {"status":False,"errorinfo":None}
        self.status_dict['issuspendedexplain'] = {"status":False,"errorinfo":None}
        self.status_dict['isrecoverexplain'] = {"status":False,"errorinfo":None}
        self.status_dict['isnotifygraborder'] = {"status":False,"errorinfo":None}
        self.status_dict['isnotifypushorder'] = {"status":False,"errorinfo":None}
        self.status_dict['isreportyixinfilename'] = {"status":False,"errorinfo":None}
        self.status_dict['isnotifypeerdisconnect'] = {"status":False,"errorinfo":None}
        self.status_dict["isnewmedia"] = {"status":False,"errorinfo":None}
        self.status_dict['isonmedia'] = {"status":False,"errorinfo":None}
        self.status_dict["isstartaction"] = {"status":False,"errorinfo":None}
        self.status_dict["isstopaction"] = {"status":False,"errorinfo":None}
        self.status_dict["isconnectmedia"] = {"status":False,"errorinfo":None}
        self.status_dict["isclosemedia"] = {"status":False,"errorinfo":None}
        self.status_dict["isenterroom"] = {"status":False,"errorinfo":None}
        self.status_dict["isenterroomresult"] = {"status":False,"errorinfo":None}
        self.status_dict["isuploaddata"] = {"status":False,"errorinfo":None}
        self.status_dict["isleaveroom"] = {"status":False,"errorinfo":None}
        self.status_dict["isdisconnect"] = {"status":False,"errorinfo":None}
        self.status_dict['issdklog'] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifyclosestream"] = {"status":False,"errorinfo":None}

    def data_fn(self,a,b,c,d):
        self.receivedatas += 1
        self.orderinfo['student'] = {"id":self.userId,"name":self.name,"senddatas":self.senddatas,"receivedatas":self.receivedatas}

    def log_fn(self,a,b,c):
        pass

    def openstream(self,id):
        resp1 = self.media.SUnet_openStream(c_int(id),c_void_p(0x12345678))
        resp2 = self.media.SUnet_openAudioStream(c_int(id))
        if resp1 != 0 or resp2 != 0:
            return False
        return True

    def closestream(self,id):
        if self.streamclosed:
            return True
        resp1 = self.media.SUnet_closeAudioStream(c_int(id))
        resp2 = self.media.SUnet_closeStream(c_int(id))
        self.logger.info("        SUnet_closeAudioStream：%s ,SUnet_closeStream：%s" %(resp1,resp2))
        if resp1 != 0 or resp2 != 0:
            return False
        return True
            
    def notify_fn(self,a,type,id):
        if type == 0 and id == 0:
            self.logger.info("        [callback] userno:%s st_notify_fn:disconnect media" %self.username.decode())
            self.callbacks.append('st_onnotify_disconnmedia')
            self.status_dict['isonmedia'] = {"status":False,"errorinfo":"已断开连接媒体服务"}
        elif type == 1 and id == self.tcId:
            self.logger.info("        [callback] userno:%s st_notify_fn:openstream" %self.username.decode())
            self.callbacks.append('st_onnotify_openstream')
            result = self.openstream(id)
            if result:
                self.status_dict['isnewmedia'] = {"status":True,"errorinfo":None}
            else:
                self.status_dict['isnewmedia'] = {"status":False,"errorinfo":"创建媒体失败,openstream异常"}
        elif type == 2 and id == self.tcId:
            self.logger.info("        [callback] userno:%s st_notify_fn:closestream" %self.username.decode())
            self.callbacks.append('st_onnotify_closestream')
            self.status_dict["isnotifyclosestream"] = {"status":True,"errorinfo":None}
			
    def sdklog(self,ch):
        loginfo = "stId:%s %s" %(self.userId,ch)
        self.logger.info("stId:%s sdklog:%s" %(self.userId,ch))
        self.logger.recordsdklog(loginfo)
			
    def onrelogin(self,stReLoginres,seq):
        self.logger.info("        [callback] userno:%s st_onrelogin" %self.username.decode())
        self.callbacks.append('st_onrelogin')
        res = stReLoginres
        self.callbackres.append({"name":"onrelogin","res":res,"seq":seq})
        if self.checkstat('isrelogin'):
            self.checknotify(res,'isrelogin')

    #回调列表
    def onlogin(self,stLoginres,seq):
        self.logger.info("        [callback] userno:%s st_onlogin" %self.username.decode())
        self.callbacks.append('st_onlogin')
        res = stLoginres
        self.callbackres.append({"name":"st_onlogin","res":res,"seq":seq})
        if self.checkstat('islogin'):
            self.checknotify(res,'islogin')

    def onlogout(self,stLogoutres,seq):
        self.logger.info("        [callback] userno:%s st_onlogout" %self.username.decode())
        self.callbacks.append('st_onlogout')
        res = stLogoutres
        self.callbackres.append({"name":"st_onlogout","res":res,"seq":seq})
        if self.checkstat("islogout"):
            self.checknotify(res,'islogout')

    def ondisconnect(self,disconnectinfo):
        self.logger.info("        [callback] userno:%s st_ondisconnect" %self.username.decode())
        self.callbacks.append('st_ondisconnect')
        self.callbackres.append({"name":"st_ondisconnect","res":None,"info":disconnectinfo})
        self.clear()

    def onsubmitquestion(self,submitquestionres,seq):
        self.callbacks.append('st_onsubmitquestion')
        res = submitquestionres
        self.callbackres.append({"name":"st_onsubmitquestion","res":res,"seq":seq})
        self.logger.info("        [callback] userno:%s st_onsubmitquestion  orderNo:%s  errorMsg:%s" %(self.username.decode(),res.orderNo.decode(),res.errorMsg.decode()))
        if res.code==0:
            self.orderinfo['orderNo'] = res.orderNo
            self.orderNo = res.orderNo
        if self.checkstat("issubmitquestion"):
            self.checknotify(res,'issubmitquestion')

    #最终抢单结果回调函数
    def notifyorderresult(self,assignorderresultreq,seq):
        self.callbacks.append('st_onnotifyorderresult')
        res = assignorderresultreq
        self.logger.info("        [callback] userno:%s st_onnotifyorderresult tcId:%s" %(self.username.decode(),res.tcId))

        self.callbackres.append({"name":"st_onnotifyorderresult","res":res,"seq":seq})
        self.checknotify(res,'isnotifyorderresult')

    def oncreatevoicechannel(self,createvoicechannelres,seq):
        self.logger.info("        [callback] userno:%s st_oncreatevoicechannel" %self.username.decode())
        self.callbacks.append('st_oncreatevoicechannel')
        res = createvoicechannelres
        self.callbackres.append({"name":"st_oncreatevoicechannel","res":res,"seq":seq})
        if self.checkstat("iscreatevoicechannel"):
            self.checknotify(res,'iscreatevoicechannel')

    def notifytccancelorder(self,tccancelordereq,seq):
        self.logger.info("        [callback] userno:%s st_onnotifytccancelorder" %self.username.decode())
        self.callbacks.append('st_onnotifytccancelorder')
        res = tccancelordereq
        self.callbackres.append({"name":"st_onnotifytccancelorder","res":res,"seq":seq})
        self.status_dict['isnotifytccancelorder'] = {"status":True,"errorinfo":None}

    def onaddquestionimg(self,addquestionimgres,seq):
        self.logger.info("        [callback] userno:%s st_onaddquestionimg" %self.username.decode())
        self.callbacks.append('st_onaddquestionimg')
        res = addquestionimgres
        self.callbackres.append({"name":"st_onaddquestionimg","res":res,"seq":seq})
        if self.checkstat("isaddimgsuccess"):
            self.checknotify(res,'isaddimgsuccess')

    def onstcancelorder(self,stcancelorderres,seq):
        self.logger.info("        [callback] userno:%s st_oncancelorder" %self.username.decode())
        self.callbacks.append('st_oncancelorder')
        res = stcancelorderres
        self.callbackres.append({"name":"st_oncancelorder","res":res,"seq":seq})
        if self.checkstat("iscancelorder"):
            self.checknotify(res,'iscancelorder')

    def notifytcbeginexplain(self,tcbeginexplainres,seq):
        self.logger.info("        [callback] userno:%s st_onnotifytcbeginexplain" %self.username.decode())
        self.callbacks.append('st_onnotifytcbeginexplain')
        res = tcbeginexplainres
        self.callbackres.append({"name":"st_onnotifytcbeginexplain","res":res,"seq":seq})
        self.status_dict['isnotifytcbgexplain'] = {"status":True,"errorinfo":None}

    def notifytcendexplain(self,tcendexplainres,seq):
        self.logger.info("        [callback] userno:%s st_onnotifytcendexplain" %self.username.decode())
        self.callbacks.append('st_onnotifytcendexplain')
        res = tcendexplainres
        self.callbackres.append({"name":"st_onnotifytcendexplain","res":res,"seq":seq})
        self.status_dict['isnotifytcendexplain'] = {"status":True,"errorinfo":None}

    def onstendexplain(self,stendexplainres,seq):
        self.logger.info("        [callback] userno:%s st_onendexplain" %self.username.decode())
        self.callbacks.append('st_onendexplain')
        res = stendexplainres
        self.callbackres.append({"name":"st_onendexplain","res":res,"seq":seq})
        if self.checkstat("isendexplain"):
            self.checknotify(res,'isendexplain')

    def onstsuspendexplain(self,stsuspendexplainres,seq):
        self.logger.info("        [callback] userno:%s st_onsuspendexplain" %self.username.decode())
        self.callbacks.append('st_onsuspendexplain')
        res = stsuspendexplainres
        self.callbackres.append({"name":"st_onsuspendexplain","res":res,"seq":seq})
        if self.checkstat("issuspendedexplain"):
            self.checknotify(res,'issuspendedexplain')

    def onstrecoverexplain(self,strecoverexplainres,seq):
        self.logger.info("        [callback] userno:%s st_onrecoverexplain" %self.username.decode())
        self.callbacks.append('st_onrecoverexplain')
        res = strecoverexplainres
        self.callbackres.append({"name":"st_onrecoverexplain","res":res,"seq":seq})
        if self.checkstat("isrecoverexplain"):
            self.checknotify(res,'isrecoverexplain')

    def notifypeerdisconnect(self,peerdisconnectreq,seq):
        self.logger.info("        [callback] userno:%s st_onnotifypeerdisconnect" %self.username.decode())
        self.callbacks.append('st_onnotifypeerdisconnect')
        res = peerdisconnectreq
        self.callbackres.append({"name":"st_onnotifypeerdisconnect","res":res,"seq":seq})

    def notifygraborder(self,teachergrabreq,seq):
        self.logger.info("        [callback] userno:%s st_onnotifygraborder" %self.username.decode())
        self.callbacks.append('st_onnotifygraborder')
        res = teachergrabreq
        self.callbackres.append({"name":"st_onnotifygraborder","res":res,"seq":seq})
        #self.checknotify(res,'isnotifygrabordeq')

    def notifypushorder(self,teacherpushres,seq):
        self.logger.info("        [callback] userno:%s st_onnotifypushorder" %self.username.decode())
        self.callbacks.append('st_onnotifypushorder')
        res = teacherpushres
        self.callbackres.append({"name":"st_onnotifypushorder","res":res,"seq":seq})
        #self.checknotify(res,'isnotifypushorder')

    def sdklog(self,log):
        self.status_dict['issdklog'] = {"status":True,"errorinfo":None}

    def onstreportyixinfilename(self,streportyixinfilenameres,seq):
        self.logger.info("        [callback] userno:%s st_onreportyixinfilename" %self.username.decode())
        self.callbacks.append('st_onreportyixinfilename')
        res = streportyixinfilenameres
        self.callbackres.append({"name":"st_onreportyixinfilename","res":res,"seq":seq})
        #self.checknotify(res,'isreportyixinfilename')

    def notifysystem(self,stsystemnoticereq,seq):
        #if 'st_onnotifysystem' not in self.callbacks:
        self.callbacks.append('st_onnotifysystem')
        self.logger.info("        [callback]  userno:%s st_onnotifysystem type:%s  msg:%s" %(self.username.decode(),stsystemnoticereq.type,stsystemnoticereq.msg))

    def onstenterroomresult(self,stenterroomresultres,seq):
        self.logger.info("        [callback] userno:%s st_onenterroomresult" %self.username.decode())
        self.callbacks.append('st_onenterroomresult')
        res = stenterroomresultres
        self.callbackres.append({"name":"st_onenterroomresult","res":res,"seq":seq})
        if self.checkstat('isenterroomresult'):
            self.checknotify(res,'isenterroomresult')

    def notifystartanalyzequestion(self,ststartanalyzequestionreq,seq):
        self.logger.info("        [callback] userno:%s st_onnotifystartanalyzequestion" %self.username.decode())
        res = ststartanalyzequestionreq
        self.callbackres.append({"name":"st_onnotifystartanalyzequestion","res":res,"seq":seq})
        self.callbacks.append('st_onnotifystartanalyzequestion')
        
    def checkstat(self,type):
        if self.current_stat != type:
            self.status_dict[type] = {"status":False,"errorinfo":"ST callback comes before action's done"}
            return False
        else:
            return True


    def checknotify(self,res,status):
        success = True
        if res.code != 0:
            success = False
            self.logger.info("        [warnning] return code:%s，return errorMsg:%s" %(res.code,res.errorMsg.decode()))
            self.status_dict[status] = {"status":False,"errorinfo":"Student '%s' failed,code:%s,errorMsg:%s" %(status[2:],res.code,res.errorMsg.decode())}
        else:
            self.logger.info("        [check] userno:%s callback return code == 0,  pass" %self.username.decode())
            if status == "islogin":
                self.userId = int(res.userId)
                self.userids.append(self.userId)
                self.status_dict["isonline"] = {"status":True,"errorinfo":None}
            elif status == "islogout":
                self.userId = None
                self.orderinfo = {"student":None,"orderNo":None,"teacher":None,"roomId":None,"media":None}
                self.tcId = None
                self.orderNo = None
            elif status == "issubmitquestion":
                length,orderNo = len(res.orderNo.decode()),res.orderNo.decode()
                if len(res.orderNo.decode()) != 20:
                    self.logger.info("invalid orderNo length :%s(%s)" %(orderNo,length))
                    success = False
                    self.status_dict[status] = {"status":False,"errorinfo":"invalid orderNo length :%s(%s位)" %(orderNo,length)}
                else:
                    self.orderNo = res.orderNo
                    self.orderinfo["student"] = {"id":self.userId,"name":self.username.decode(),"senddatas":0,"receivedatas":0}
                    self.orderinfo["orderNo"] = res.orderNo
            elif status == 'isnotifyorderresult':
                if self.orderNo != res.orderNo:
                    self.status_dict[status] = {"status":False,"errorinfo":"student onsubmitquestion's orderNo not equals sended orderNo,onsubmitquestion's orderNo:%s,sended orderNo:%s" %(res.orderNo,self.orderNo)}
                    success = False
                else:
                    self.logger.info("        [check] userno:%s is received orderNo equals request orderNo,  pass" %self.username.decode())
                    self.orderinfo['student'] = {"id":self.userId,"name":self.username.decode(),"senddatas":0,"receivedatas":0}
                    self.tcId = res.tcId
            elif status == "isnotifytccancelorder":
                if self.orderNo != res.orderNo:
                    success = False
                    self.status_dict[status] = {"status":False,
"errorinfo":"received orderNo is not equals request orderNo,received orderNo:%s,request orderNo:%s" %(res.orderNo,self.orderNo)}
                else:
                    self.logger.info("        [check] userno:%s is received orderNo equals request orderNo,  pass" %self.username.decode())
                    self.order = None
            elif status == 'isnotifypushorder':
                pass
            elif status == 'iscancelorder':
                if self.orderNo != res.orderNo:
                    success = False
                    self.status_dict[status] = {"status":False,
"errorinfo":"received orderNo not equals request orderNo,received orderNo:%s,request orderNo:%s" %(res.orderNo,self.orderNo)}
                else:
                    self.logger.info("        [check] userno:%s is received orderNo equals request orderNo,  pass" %self.username.decode())
                    self.orderNo = None
                    self.status_dict['submitquestion'] = {"status":False,"errorinfo":None}
            elif status == 'iscreatevoicechannel':
                if self.tcId != res.tcId:
                    success = False
                    self.status_dict[status] = {"status":False,
"errorinfo":"received tcId not equals request tcId,received tcId:%s,request tcId:%s" %(res.tcId,self.tcId)}
                else:
                    self.logger.info("        [check] userno:%s is received tcId equals request tcId,  pass" %self.username.decode())
                    self.mediaIp = res.mediaIp
                    self.mediaPort = res.mediaPort
                    self.token = res.token
                    self.roomId = res.roomId
            elif status == 'isenterroomresult':
                pass
            elif status == 'isaddimgsuccess':
                pass
            elif status == 'isnotifytcbgexplain':
                pass
            elif status == 'isnotifytcendexplain':
                pass
            elif status == 'isendexplain':
                pass
            elif status == 'issuspendedexplain':
                pass
            elif status == 'isrecoverexplain':
                pass
            elif status == 'isnotifypeerdisconnect':
                pass
            elif status == 'isrelogin':
                self.status_dict['isonline'] = {"status":True,"errorinfo":None}
                self.status_dict['isrelogin'] = {"status":True,"errorinfo":None}
            else:
                pass

        if success:
            self.status_dict[status] = {"status":True,"errorinfo":None}
            #print("设置%s状态成功" %status)

#login
    def login(self):
        ret=self.core.Login(self.handlereq,StLoginReq(self.server['ip'].encode(),self.server['port'],self.username,self.pwd,2,b'1.2.1',b'automation',1),self.core.CreateSeqWrap())
        self.current_stat = 'islogin'

    def relogin(self):
        ret = self.core.ReLogin(self.handlereq,self.core.CreateSeqWrap())
        self.current_stat = 'isrelogin'
		
#logout
    def logout(self):
        self.core.Logout(self.handlereq,StLogoutReq(self.userId),self.core.CreateSeqWrap())
        self.current_stat = 'islogout'

#submitquestion(高中问题图片)
    def submitquestion(self):
        self.logger.info("img url:%s" %self.imgurl)
        self.core.SubmitQuestion(self.handlereq,SubmitQuestionReq(self.imgurl,b'1234567890'),self.core.CreateSeqWrap())
        self.current_stat = 'issubmitquestion'

    def cancelorder(self):
        self.core.StCancelOrder(self.handlereq,StCancelOrderReq(self.orderNo,1,b'i am wait so long'),self.core.CreateSeqWrap())
        self.current_stat = 'iscancelorder'

#createvoicechannel
    def createvoicechannel(self):
        self.core.CreateVoiceChannel(self.handlereq,CreateVoiceChannelReq(self.orderNo,self.tcId),self.core.CreateSeqWrap())
        self.current_stat = 'iscreatevoicechannel'

#newmedia
    def newmedia(self):
        rp = self.media.SUnet_new(self._data_fn,self._log_fn,self._notify_fn,c_void_p(0))
        if rp != 0:
            self.status_dict['isnewmedia'] = {"status":False,"errorinfo":"newmedia failed,return code:%s" %rp}
        else:
            self.status_dict['isnewmedia'] = {"status":True,"errorinfo":None}

#connectmedia
    def connectmedia(self):
        rp = self.media.SUnet_connect(c_char_p(self.mediaIp),c_int(self.mediaPort),c_int(0),c_int(self.userId),c_char_p(self.token),c_uint(16))
        if rp == 0:
            self.status_dict['isconnectmedia'] = {"status":True,"errorinfo":None}
        else:
            self.status_dict['isconnectmedia'] = {"status":False,"errorinfo":"connectmedia falied,return code:%s" %rp}

#enterroom
    def enterroom(self):
        rp = self.media.SUnet_enterRoom(c_int(self.roomId),c_int(0),c_char_p(self.orderNo),c_int(14))
        if rp == 0:
            self.logger.info("        [check] userno:%s enterromm request response == 0,  pass" %self.username.decode())
            self.status_dict['isenterroom'] = {"status":True,"errorinfo":None}
        else:
            self.status_dict['isenterroom'] = {"status":False,"errorinfo":"enterroom failed,return code:%s" %rp}

    def enterroomresult(self):
        ret=self.core.StEnterRoomResult(self.handlereq,StEnterRoomResultReq(self.orderNo,0,b'enterroom successful'),self.core.CreateSeqWrap())
        self.current_stat = 'isenterroomresult'


#uploaddata
    def uploaddata(self):
        loop = 50
        noerror = True
        while loop:
            rp = self.media.SUnet_uploadAVdata(c_int(0),c_char_p(b'0'*256),c_int(88))
            if rp != 0:
                noerror = False
            else:
                self.senddatas += 1
                self.orderinfo['student'] = {"id":self.userId,"name":self.name,"senddatas":self.senddatas,"receivedatas":self.receivedatas}
                loop -= 1
            if loop:
                time.sleep(0.1)
            else:
                break

        self.status_dict['isuploaddata'] = {"status":True,"errorinfo":None}

#startaction
    def startaction(self):
        rp = self.media.SUnet_startAction(c_char_p(b'0'*256),c_int(256))
        if rp != 0:
            self.status_dict["isstartaction"] = {"status":False,"errorinfo":"startAction failed,return code:%s" %rp}
        else:
            self.status_dict["isstartaction"] = {"status":True,"errorinfo":None}

#stopaction
    def stopaction(self):
        rp = self.media.SUnet_stopAction()
        if rp != 0:
            self.status_dict['isstopaction'] = {"status":False,"errorinfo":"stopAction failed,return code:%s" %rp}
        else:
            self.status_dict['isstopaction'] = {"status":True,"errorinfo":None}

#leaveroom
    def leaveroom(self):
        result = self.closestream(self.tcId)
        if result:
            rp  = self.media.SUnet_leaveRoom()
            if rp != 0:
                self.status_dict['isleaveroom'] = {"status":False,"errorinfo":"leaveroom failed,return code:%s" %rp}
            else:
                self.status_dict['isleaveroom'] = {"status":True,"errorinfo":None}
        else:
            self.status_dict['isleaveroom'] = {"status":False,"errorinfo":"closestream failed!"}

	
#closemedia
    def closemedia(self):
        success = True
        errorinfo = ""
        rp1 = self.media.SUnet_close()
        if rp1 != 0:
            success = False
            errorinfo += "SUnet_close failed,return code:%s" %rp1

        rp2 = self.media.SUnet_release()
        if rp2 != 0:
            success = False
            errorinfo += "SUnet_close failed,return code:%s" %rp2

        if success:
            self.status_dict['isclosemedia'] = {"status":True,"errorinfo":None}
        else:
            self.status_dict['isclosemedia'] = {"status":False,"errorinfo":errorinfo}

#suspendexplain
    def suspendexplain(self):
        self.core.StSuspendExplain(self.handlereq,StSuspendExplainReq(self.orderNo),self.core.CreateSeqWrap())
        self.current_stat = 'issuspendedexplain'

#strecoverexplain
    def recoverexplain(self):
        self.core.StRecoverExplain(self.handlereq,StRecoverExplainReq(self.orderNo),self.core.CreateSeqWrap())
        self.current_stat = 'isrecoverexplain'

#stendexplain
    def endexplain(self):
        ret=self.core.StEndExplain(self.handlereq,StEndExplainReq(self.orderNo,1,b'i want to quit'),self.core.CreateSeqWrap())
        self.logger.info("        endexplain ret:%s" %ret)
        self.current_stat = 'isendexplain'
            

    def starts(self):
        try:
            starta=self.core.startAction(self.handlereq,self.handleres)
            self.status_dict['isstart'] = {"status":True,"errorinfo":None}
        except Exception as e:
            self.status_dict['isstart'] = {"status":False,"errorinfo":"StartAction Failed,info:%s" %str(e)}

    def stops(self):
        try:
            self.core.stopAction(self.handlereq,self.handleres)
            self.status_dict['isstop'] = {"status":True,"errorinfo":None}
        except Exception as e:
            self.status_dict["isstop"] = {"status":False,"errorinfo":"StopAction Failed,info:%s" %str(e)}

    def disconnect(self):
        ret = self.core.Disconnect(self.handlereq)
        self.logger.info("Disconnect called,ret:%s" %ret)
        self.status_dict['isdisconnect'] = {"status":True,"errorinfo":None}
			
    def run(self):
        self.__initSDK()
        isloop = True
        while isloop:
            for ename,e in self.e_dict.items():
                if ename == 'stops':
                    if e.is_set():
                        isloop = False
                        self.stops()
                        break
                else:
                    if e.is_set():
                        self.logger.info("        [action]userno:%s userId:%s action:%s begin" %(self.username.decode(),self.userId,ename))
                        eval('self.%s()' %ename)
                        self.logger.info("        [action]userno:%s userId:%s action:%s end" %(self.username.decode(),self.userId,ename))
                        e.clear()
            time.sleep(0.1)
        else:
            self.logger.info("        student stopped")
            self.status_dict['isstop'] = {"status":True,"errorinfo":None}

if __name__ == '__main__':
	pass







