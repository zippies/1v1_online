from multiprocessing import Process
import time,random
from .cstructs.tcstruct import *

class GrabRes(object):
	def __init__(self,stId,orderNo,code,errorMsg,imgUrl):
		self.stId = stId
		self.orderNo = orderNo
		self.code = code
		self.errorMsg = errorMsg
		self.imgUrl = imgUrl

class Teacher(Process):
    def __init__(self,username,pwd,server,e_dict,status_dict,orderinfo,userids,callbacks,logger,grouplist,callbackres=None):
        Process.__init__(self)
        self.e_dict = e_dict
        self.username = username.encode('utf-8')
        self.pwd = pwd
        self.server = server
        self.userids = userids
        self.userId = None
        self.noticedOrders = []
        self.orderNo = None
        self.stId = None
        self.senddatas = 0
        self.receivedatas = 0
        self.status_dict = status_dict
        self.orderinfo = orderinfo
        self.current_stat = None
        self.streamclosed = None
        self.callbacks = callbacks
        self.logger = logger
        self.grouplist = grouplist
        self.callbackres = callbackres
        self._initSelf()

    def __initSDK(self):
        self.core=CDLL('libTcSDKWrap.so')
        self.media=CDLL('libsunet2.so')
        #控制服务回调
        SdkLogCb=CFUNCTYPE(None,c_char_p)
        OnLoginCb=CFUNCTYPE(None,TcLoginRes,c_uint)
        OnLogoutCb=CFUNCTYPE(None,TcLogoutRes,c_uint)
        OnReconnectCb=CFUNCTYPE(None,)
        OnReconnectSuccessCb=CFUNCTYPE(None,)
        OnDisconnectCb=CFUNCTYPE(None,DisconnectInfo)
        OnGrabOrderCb=CFUNCTYPE(None,POINTER(GrabOrderRes),c_uint)
        NotifyNewOrderCb=CFUNCTYPE(None,NewOrderReq,c_uint)
        OnRegretOrderCb=CFUNCTYPE(None,RegretOrderRes,c_uint)
        OnCreateVoiceChannelCb=CFUNCTYPE(None,CreateVoiceChannelRes,c_uint)
        OnTcBeginExplainCb=CFUNCTYPE(None,TcBeginExplainRes,c_uint)
        NotifyAddQuestionImgCb=CFUNCTYPE(None,POINTER(AddQuestionImgReq),c_uint)
        OnTcEndExplainCb=CFUNCTYPE(None,TcEndExplainRes,c_uint)
        NotifyStEndExplainCb=CFUNCTYPE(None,StEndExplainReq,c_uint)
        OnTcEvaluateStCb=CFUNCTYPE(None,TcEvaluateStRes,c_uint)
        NotifyStSuspendExplainCb=CFUNCTYPE(None,StSuspendExplainReq,c_uint)
        NotifyStRecoverExplainCb=CFUNCTYPE(None,StRecoverExplainReq,c_uint)
        OnTcUploadScreenshotCb=CFUNCTYPE(None,TcUploadScreenshotRes,c_uint)
        NotifyStCancelOrderCb=CFUNCTYPE(None,StCancelOrderReq,c_uint)
        OnReportYixinFilenameCb=CFUNCTYPE(None,ReportYixinFilenameRes,c_uint)
        OnGetThirdpartyMediaCb=CFUNCTYPE(None,GetThirdpartyMediaRes,c_uint)
        NotifyPeerDisconnectCb=CFUNCTYPE(None,PeerDisconnectReq,c_uint)
        OnSetTeacherStatCb=CFUNCTYPE(None,SetTeacherStatRes,c_uint)
        NotifyNewMsgCb=CFUNCTYPE(None,POINTER(NewMsgReq),c_uint)
        OnTcEnterRoomResultCb=CFUNCTYPE(None,TcEnterRoomResultRes,c_uint)
        NotifyStartAnalyzeQuestionCb=CFUNCTYPE(None,TcStartAnalyzeQuestionReq,c_uint)
        NotifyTcKickoutCb=CFUNCTYPE(None,TcKickoutReq,c_uint)
        #媒体服务回调
        Data=CFUNCTYPE(None,c_void_p,c_int,c_char_p,c_int)
        Log=CFUNCTYPE(None,c_int,c_char_p,c_int)
        Notify=CFUNCTYPE(None,c_void_p,c_int,c_int)
        #init
        self.media.argtypes=[Data,Log,Notify,c_void_p]
        self.core.CreateWenbaTcResponseWrap.argtypes=[
                                                        SdkLogCb,
                                                        OnLoginCb,
                                                        OnLogoutCb,
                                                        OnReconnectCb,
                                                        OnReconnectSuccessCb,
                                                        OnDisconnectCb,
                                                        OnGrabOrderCb,
                                                        NotifyNewOrderCb,
                                                        OnRegretOrderCb,
                                                        OnCreateVoiceChannelCb,
                                                        OnTcBeginExplainCb,
                                                        NotifyAddQuestionImgCb,
                                                        OnTcEndExplainCb,
                                                        NotifyStEndExplainCb,
                                                        OnTcEvaluateStCb,
                                                        NotifyStSuspendExplainCb,
                                                        NotifyStRecoverExplainCb,
                                                        OnTcUploadScreenshotCb,
                                                        NotifyStCancelOrderCb,
                                                        OnReportYixinFilenameCb,
                                                        OnGetThirdpartyMediaCb,
                                                        NotifyPeerDisconnectCb,
                                                        OnSetTeacherStatCb,
                                                        NotifyNewMsgCb,
                                                        OnTcEnterRoomResultCb,
                                                        NotifyStartAnalyzeQuestionCb,
                                                        NotifyTcKickoutCb
        ]
        self.core.CreateWenbaTcResponseWrap.restype=c_void_p
        self._sdklogcb_fn=SdkLogCb(self.sdklog)
        self._onlogincb_fn=OnLoginCb(self.onlogin)
        self._onlogoutcb_fn=OnLogoutCb(self.onlogout)
        self._onreconnectcb_fn=OnReconnectCb(self.onreconnect)
        self._onreconnectsuccesscb_fn=OnReconnectSuccessCb(self.onreconnectsuccess)
        self._ondisconnectcb_fn=OnDisconnectCb(self.ondisconnect)
        self._ongrabordercb_fn=OnGrabOrderCb(self.ongraborder)
        self._notifynewordercb_fn=NotifyNewOrderCb(self.notifyneworder)
        self._onregretordercb_fn=OnRegretOrderCb(self.onregretorder)
        self._oncreatevoicechannelcb_fn=OnCreateVoiceChannelCb(self.oncreatevoicechannel)
        self._ontcbeginexpalincb_fn=OnTcBeginExplainCb(self.ontcbeginexplain)
        self._notifyaddquestionimgcb_fn=NotifyAddQuestionImgCb(self.notifyaddquestionimg)
        self._ontcendexplaincb_fn=OnTcEndExplainCb(self.ontcendexplain)
        self._notifystendexplaincb_fn=NotifyStEndExplainCb(self.notifystendexplain)
        self._ontcevaluatestcb_fn=OnTcEvaluateStCb(self.ontcevaluatest)
        self._notifystsuspendexplaincb_fn=NotifyStSuspendExplainCb(self.notifystsuspendexplain)
        self._notifystrecoverexplaincb_fn=NotifyStRecoverExplainCb(self.notifystrecoverexplain)
        self._ontcuploadscreenshotcb_fn=OnTcUploadScreenshotCb(self.ontcuploadscreenshot)
        self._notifystcancelordercb_fn=NotifyStCancelOrderCb(self.notifystcancelorder)
        #self._ontcnotifyroominfocb_fn=OnTcNotifyRoomInfoCb(self.ontcnotifyroominfocb_fn)
        self._onreportyixinfilenamecb_fn=OnReportYixinFilenameCb(self.onreportyixinfilename)
        self._ongetthirdpartymediacb_fn=OnGetThirdpartyMediaCb(self.ongetthirdpartymedia)
        self._notifypeerdisconnectcb_fn=NotifyPeerDisconnectCb(self.notifypeerdisconnect)
        self._onsetteacherstatcb_fn=OnSetTeacherStatCb(self.onsetteacherstat)
        self._notifynewmsgcb_fn=NotifyNewMsgCb(self.notifynewmsg)
        self._ontcenterroomresultcb_fn=OnTcEnterRoomResultCb(self.ontcenterroomresult)
        self._notifystartanalyzequestioncb_fn=NotifyStartAnalyzeQuestionCb(self.notifystartanalyzequestion)
        self._notifytckickoutcb_fn=NotifyTcKickoutCb(self.notifytckickout)

        self._data_fn=Data(self.data_fn)
        self._log_fn=Log(self.log_fn)
        self._notify_fn=Notify(self.notify_fn)
        self.handlereq=self.core.CreateWenbaTcRequestWrap()
        self.handleres=self.core.CreateWenbaTcResponseWrap(
                self._sdklogcb_fn,
                self._onlogincb_fn,
                self._onlogoutcb_fn,
                self._onreconnectcb_fn,
                self._onreconnectsuccesscb_fn,
                self._ondisconnectcb_fn,
                self._ongrabordercb_fn,
                self._notifynewordercb_fn,
                self._onregretordercb_fn,
                self._oncreatevoicechannelcb_fn,
                self._ontcbeginexpalincb_fn,
                self._notifyaddquestionimgcb_fn,
                self._ontcendexplaincb_fn,
                self._notifystendexplaincb_fn,
                self._ontcevaluatestcb_fn,
                self._notifystsuspendexplaincb_fn,
                self._notifystrecoverexplaincb_fn,
                self._ontcuploadscreenshotcb_fn,
                self._notifystcancelordercb_fn,
                self._onreportyixinfilenamecb_fn,
                self._ongetthirdpartymediacb_fn,
                self._notifypeerdisconnectcb_fn,
                self._onsetteacherstatcb_fn,
                self._notifynewmsgcb_fn,
                self._ontcenterroomresultcb_fn,
                self._notifystartanalyzequestioncb_fn,
                self._notifytckickoutcb_fn
                )

    def _initSelf(self):
        self.status_dict["isstart"] = {"status":False,"errorinfo":None}
        self.status_dict["islogin"] = {"status":False,"errorinfo":None}
        self.status_dict["isdisconnect"] = {"status":False,"errorinfo":None}
        self.status_dict["issetfree"] = {"status":False,"errorinfo":None}
        self.status_dict["issetbusy"] = {"status":False,"errorinfo":None}
        self.status_dict["islogout"] = {"status":False,"errorinfo":None}
        self.status_dict["isonline"] = {"status":False,"errorinfo":None}
        self.status_dict["isstop"] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifyneworder"] = {"status":False,"errorinfo":None}
        self.status_dict["isgraborder"] = {"status":False,"errorinfo":None}
        self.status_dict["isregretorder"] = {"status":False,"errorinfo":None}
        self.status_dict["iscreatevoicechannel"] = {"status":False,"errorinfo":None}
        self.status_dict["isbeginexplain"] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifyaddquestionimg"] = {"status":False,"errorinfo":None}
        self.status_dict["isendexplain"] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifystendexplain"] = {"status":False,"errorinfo":None}
        self.status_dict["istcevaluatest"] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifystsuspendexplain"] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifystrecoverexplain"] = {"status":False,"errorinfo":None}
        self.status_dict["istcuploadscreenshot"] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifystcancelorder"] = {"status":False,"errorinfo":None}
        self.status_dict["isgetthirdpartymedia"] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifypeerdisconnect"] = {"status":False,"errorinfo":None}
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
        self.status_dict["isnotifyclosestream"] = {"status":False,"errorinfo":None}
        self.orderinfo['student'] = {"id":None,"name":None,"senddatas":0,"receivedatas":0}
        self.orderinfo['orderNo'] = None
        self.orderinfo['teacher'] = {"id":None,"name":None,"senddatas":0,"receivedatas":0}
        self.orderinfo['imgurl'] = None
        self.orderinfo['specialOrderNo'] = None

    def clear(self):
        self.status_dict["isstart"] = {"status":False,"errorinfo":None}
        self.status_dict["islogin"] = {"status":False,"errorinfo":None}
        self.status_dict["isdisconnect"] = {"status":False,"errorinfo":None}
        self.status_dict["issetfree"] = {"status":False,"errorinfo":None}
        self.status_dict["issetbusy"] = {"status":False,"errorinfo":None}
        self.status_dict["islogout"] = {"status":False,"errorinfo":None}
        self.status_dict["isonline"] = {"status":False,"errorinfo":None}
        self.status_dict["isstop"] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifyneworder"] = {"status":False,"errorinfo":None}
        self.status_dict["isgraborder"] = {"status":False,"errorinfo":None}
        self.status_dict["isregretorder"] = {"status":False,"errorinfo":None}
        self.status_dict["iscreatevoicechannel"] = {"status":False,"errorinfo":None}
        self.status_dict["isbeginexplain"] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifyaddquestionimg"] = {"status":False,"errorinfo":None}
        self.status_dict["isendexplain"] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifystendexplain"] = {"status":False,"errorinfo":None}
        self.status_dict["istcevaluatest"] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifystsuspendexplain"] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifystrecoverexplain"] = {"status":False,"errorinfo":None}
        self.status_dict["istcuploadscreenshot"] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifystcancelorder"] = {"status":False,"errorinfo":None}
        self.status_dict["isgetthirdpartymedia"] = {"status":False,"errorinfo":None}
        self.status_dict["isnotifypeerdisconnect"] = {"status":False,"errorinfo":None}
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
        self.status_dict["isnotifyclosestream"] = {"status":False,"errorinfo":None}
        
    def data_fn(self,a,b,c,d):
        self.receivedatas += 1
        self.orderinfo['teacher'] = {"id":self.userId,"name":"self.name","senddatas":self.senddatas,"receivedatas":self.receivedatas}


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
        self.streamclosed = True
        return True
            
    def notify_fn(self,a,type,id):
        if type == 0 and id == 0:
            self.logger.info("        [callback] userno:%s tc_notify_fn:disconnect media" %self.username.decode())
            self.callbacks.append('tc_onnotify_disconnmedia')
            self.status_dict['isonmedia'] = {"status":False,"errorinfo":"已断开连接媒体服务"}
        elif type == 1 and id == self.stId:
            self.logger.info("        [callback] userno:%s tc_notify_fn:openstream" %self.username.decode())
            self.callbacks.append('tc_onnotify_openstream')
            result = self.openstream(id)
            if result:
                self.status_dict['isnewmedia'] = {"status":True,"errorinfo":None}
            else:
                self.status_dict['isnewmedia'] = {"status":False,"errorinfo":"创建媒体失败,openstream异常"}
        elif type == 2 and id == self.stId:
            self.logger.info("        [callback] userno:%s tc_notify_fn:closestream" %self.username.decode())
            self.callbacks.append('tc_onnotify_closestream')
            self.status_dict["isnotifyclosestream"] = {"status":True,"errorinfo":None}

    def sdklog(self,ch):
        loginfo = "tcId:%s %s" %(self.userId,ch)
        self.logger.info("    tcId:%s sdklog:%s" %(self.userId,ch))
        self.logger.recordsdklog(loginfo)

    #老师登录回调
    def onlogin(self,tcLoginres,seq):
        self.logger.info("        [callback] userno:%s tc_onlogin" %self.username.decode())
        self.callbacks.append('tc_onlogin')
        res = tcLoginres
        self.callbackres.append({"name":"tc_onlogin","res":res,"seq":seq})
        if self.checkstat("islogin"):
            self.checknotify(res,"islogin")

    #老师注销回调
    def onlogout(self,tcLogoutres,seq):
        self.logger.info("        [callback] userno:%s tc_onlogout" %self.username.decode())
        self.callbacks.append('tc_onlogout')
        res = tcLogoutres
        self.callbackres.append({"name":"tc_onlogout","res":res,"seq":seq})
        if self.checkstat("islogout"):
            self.checknotify(res,"islogout")

    def onreconnect(self):
        self.logger.info("        [callback] userno:%s tc_onreconnect" %self.username.decode())
        self.callbacks.append('tc_onreconnect')

    def onreconnectsuccess(self):
        self.logger.info("        [callback] userno:%s tc_onreconnectsuccess" %self.username.decode())
        self.callbacks.append('tc_onreconnectsuccess')


    #老师掉线回调
    def ondisconnect(self,disconnectinfo):
        self.logger.info("        [callback] userno:%s tc_ondisconnect" %self.username.decode())
        self.callbacks.append('tc_ondisconnect')
        self.callbackres.append({"name":"tc_ondisconnect","res":None,"info":disconnectinfo})
        self.status_dict["isonline"] = {"status":False,"errorinfo":"teacher:%s disconnected" %self.username.decode()}
    #老师抢单回调
    def ongraborder(self,graborderres,seq):
        self.logger.info("        [callback] userno:%s tc_ongraborder" %self.username.decode())
        self.callbacks.append('tc_ongraborder')
        graborderres = graborderres[0]
        res = GrabRes(graborderres.stId,graborderres.orderNo,graborderres.code,graborderres.errorMsg,graborderres.imgUrl)
        self.callbackres.append({"name":"tc_ongraborder","res":res,"seq":seq})
        if self.checkstat("isgraborder"):
            self.checknotify(res,"isgraborder")
    #老师收到订单消息
    def notifyneworder(self,neworderreq,seq):
        self.callbacks.append('tc_onnotifyneworder')
        res = neworderreq
        self.callbackres.append({"name":"tc_onnotifyneworder","res":res,"seq":seq})
        self.logger.info("        [callback] userno:%s tc_onnotifyneworder  tcId:%s orderNo:%s" %(self.username.decode(),self.userId,res.orderNo.decode()))
        self.noticedOrders.append(res.orderNo)
        self.status_dict['isnotifyneworder'] = {"status":True,"errorinfo":None}
    #老师取消订单回调
    def onregretorder(self,regretorderres,seq):
        self.logger.info("        [callback] userno:%s tc_onregretorder" %self.username.decode())
        self.callbacks.append('tc_onregretorder')
        res = regretorderres
        self.callbackres.append({"name":"tc_onregretorder","res":res,"seq":seq})
        if self.checkstat("isregretorder"):
            self.checknotify(res,"isregretorder")
    #老师创建语音通道回调
    def oncreatevoicechannel(self,createvoicechannelres,seq):
        self.logger.info("        [callback] userno:%s tc_oncreatevoicechannel" %self.username.decode())
        self.callbacks.append('tc_oncreatevoicechannel')
        res = createvoicechannelres
        self.callbackres.append({"name":"tc_oncreatevoicechannel","res":res,"seq":seq})
        if self.checkstat("iscreatevoicechannel"):
            self.checknotify(res,"iscreatevoicechannel")
    #老师开始讲解回调
    def ontcbeginexplain(self,tcbeginexplainres,seq):
        self.logger.info("        [callback] userno:%s tc_onbeginexplain" %self.username.decode())
        self.callbacks.append('tc_onbeginexplain')
        res = tcbeginexplainres
        self.callbackres.append({"name":"tc_onbeginexplain","res":res,"seq":seq})
        if self.checkstat("isbeginexplain"):
            self.checknotify(res,"isbeginexplain")
    #老师收到学生添加问题图片消息
    def notifyaddquestionimg(self,addquestionimgres,seq):
        self.logger.info("        [callback] userno:%s tc_onnotifyaddquestionimg" %self.username.decode())
        self.callbacks.append('tc_onnotifyaddquestionimg')
        res = addquestionimgres
        self.callbackres.append({"name":"tc_onnotifyaddquestionimg","res":res,"seq":seq})
        #self.checknotify(res,"isnotifyaddquestionimg")
    #老师结束讲解消息
    def ontcendexplain(self,tcendexplainres,seq):
        self.logger.info("        [callback] userno:%s tc_onendexplain" %self.username.decode())
        self.callbacks.append('tc_onendexplain')
        res = tcendexplainres
        self.callbackres.append({"name":"tc_onendexplain","res":res,"seq":seq})
        if self.checkstat("isendexplain"):
            self.checknotify(res,"isendexplain")
    #老师收到学生结束讲解消息
    def notifystendexplain(self,stendexplainres,seq):
        self.logger.info("        [callback] userno:%s tc_onnotifystendexplain" %self.username.decode())
        self.callbacks.append('tc_onnotifystendexplain')
        res = stendexplainres
        self.callbackres.append({"name":"tc_onnotifystendexplain","res":res,"seq":seq})
        self.status_dict['isnotifystendexplain'] = {"status":True,"errorinfo":None}
    #老师评价学生
    def ontcevaluatest(self,tcevaluatestres,seq):
        self.logger.info("        [callback] userno:%s tc_onevaluetest" %self.username.decode())
        self.callbacks.append('tc_onevaluetest')
        res = tcevaluatestres
        self.callbackres.append({"name":"tc_onevaluetest","res":res,"seq":seq})
        #self.checknotify(res,"istcevaluatest")
    #老师收到学生暂停讲解消息
    def notifystsuspendexplain(self,stsuspendexplainreq,seq):
        self.logger.info("        [callback] userno:%s tc_onnotifystsuspendexplain" %self.username.decode())
        self.callbacks.append('tc_onnotifystsuspendexplain')
        res = stsuspendexplainreq
        self.callbackres.append({"name":"tc_onnotifystsuspendexplain","res":res,"seq":seq})
        self.status_dict["isnotifystsuspendexplain"] = {"status":True,"errorinfo":None}
    #老师收到学生恢复讲解消息
    def notifystrecoverexplain(self,strecoverexplainres,seq):
        self.logger.info("        [callback] userno:%s tc_onnotifystrecoverexplain" %self.username.decode())
        self.callbacks.append('tc_onnotifystrecoverexplain')
        res = strecoverexplainres
        self.callbackres.append({"name":"tc_onnotifystrecoverexplain","res":res,"seq":seq})
        self.status_dict['isnotifystrecoverexplain'] = {"status":True,"errorinfo":None}
    #老师上传屏幕截图
    def ontcuploadscreenshot(self,tcuploadscreenshotres,seq):
        self.logger.info("        [callback] userno:%s tc_onuploadscreenshot" %self.username.decode())
        self.callbacks.append('tc_onuploadscreenshot')
        res = tcuploadscreenshotres
        self.callbackres.append({"name":"tc_onuploadscreenshot","res":res,"seq":seq})
        #self.checknotify(res,"istcuploadscreenshot")
    #老师收到学生取消订单消息
    def notifystcancelorder(self,stcancelorderres,seq):
        self.logger.info("        [callback] userno:%s tc_onnotifystcancelorder" %self.username.decode())
        self.callbacks.append('tc_onnotifystcancelorder')
        res = stcancelorderres
        self.callbackres.append({"name":"tc_onnotifystcancelorder","res":res,"seq":seq})
        self.status_dict['isnotifystcancelorder'] = {"status":True,"errorinfo":None}

    def onreportyixinfilename(self,reportyixinfilenameres,seq):
        self.logger.info("        [callback] userno:%s tc_onreportyixinfilename" %self.username.decode())
        self.callbacks.append('tc_onreportyixinfilename')
        res = reportyixinfilenameres
        self.callbackres.append({"name":"tc_onreportyixinfilename","res":res,"seq":seq})

    def ongetthirdpartymedia(self,getthirdpartymediares,seq):
        self.logger.info("        [callback] userno:%s tc_ongetthirdpartymedia" %self.username.decode())
        self.callbacks.append('tc_ongetthirdpartymedia')
        res = getthirdpartymediares
        self.callbackres.append({"name":"tc_ongetthirdpartymedia","res":res,"seq":seq})
        #self.checknotify(res,"isgetthirdpartymedia")

    def notifypeerdisconnect(self,peerdisconnectreq,seq):
        self.logger.info("        [callback] userno:%s tc_onnotifypeerdisconnect" %self.username.decode())
        self.callbacks.append('tc_onnotifypeerdisconnect')
        res = peerdisconnectreq
        self.callbackres.append({"name":"tc_onnotifypeerdisconnect","res":res,"seq":seq})
        #self.checknotify(res,"isnotifypeerdisconnect")
#1
    def onsetteacherstat(self,setteacherstatres,seq):
        self.logger.info("        [callback] userno:%s tc_onsetteacherstat" %self.username.decode())
        self.callbacks.append('tc_onsetteacherstat')
        res = setteacherstatres
        self.callbackres.append({"name":"tc_onsetteacherstat","res":res,"seq":seq})

    def notifynewmsg(self,newmsgreq,seq):
        self.logger.info("        [callback] userno:%s tc_onnotifynewmsg" %self.username.decode())
        self.callbacks.append('tc_onnotifynewmsg')
        res = newmsgreq
        self.callbackres.append({"name":"tc_onnotifynewmsg","res":res,"seq":seq})

    def ontcenterroomresult(self,tcenterroomresultres,seq):
        self.logger.info("        [callback] userno:%s tc_onenterroomresult" %self.username.decode())
        self.callbacks.append('tc_onenterroomresult')
        res = tcenterroomresultres
        self.callbackres.append({"name":"tc_onenterroomresult","res":res,"seq":seq})
        if self.checkstat('isenterroomresult'):
            self.checknotify(res,'isenterroomresult')
		
    def notifystartanalyzequestion(self,tcstartanalyzequestionreq,seq):
        self.logger.info("        [callback] userno:%s tc_onnotifystartanalyzequestion" %self.username.decode())
        self.callbacks.append('tc_onnotifystartanalyzequestion')
        res = tcstartanalyzequestionreq
        self.callbackres.append({"name":"tc_onnotifystartanalyzequestion","res":res,"seq":seq})

    def notifytckickout(self,tckickoutreq,seq):
        self.logger.info("        [callback] userno:%s tc_onnotifytckickout" %self.username.decode())
        self.callbacks.append('tc_onnotifytckickout')

    def checkstat(self,type):
        if self.current_stat != type:
            self.status_dict[type] = {"status":False,"errorinfo":"TC callback comes before action's done"}
            return False
        else:
            return True

    def compairImg(self,img):
        import filecmp,os
        return filecmp.cmp('%s/defender/main/history/questionimg.png' %os.getcwd(),img)
			
    def _downloadimg(self,url):
        import requests,os
        path = os.getcwd()
        img = '%s/defender/main/history/%s.png' %(path,time.strftime("%Y-%m-%d_%H-%M-%S",time.localtime()))
        info = {'success':False,"msg":None}
        try:
            r = requests.get(url,timeout=(2,8))
            if r.status_code == 200:
                with open(img,'wb') as f:
                    f.write(r.content)

                if self.compairImg(img):
                    info['success'] = True
                    self.logger.info("        [check] userno:%s download question_img,  pass" %self.username.decode())
            else:
                info['msg'] = "download question_img failed，code:%s,url:%s" %(r.status_code,url)
        except Exception as e:
            info['msg'] = 'download question_img failed：%s' %str(e)
        finally:
            return info

    def checknotify(self,res,status):
        success = True
        if res.code != 0:
            success = False
            self.logger.info("        [warnning] return code:%s，return errorMsg:%s" %(res.code,res.errorMsg.decode()))
            self.status_dict[status] = {"status":False,"errorinfo":"Teacher '%s' failed,code:%s,errorMsg:%s" %(status[2:],res.code,res.errorMsg.decode())}
        else:
            self.logger.info("        [check] userno:%s callback return code == 0,  pass" %self.username.decode())
            if status == "islogin":
                self.userId = int(res.userId)
                self.userids.append(self.userId)
                self.status_dict['isonline'] = {"status":True,"errorinfo":None}
            elif status == "isgraborder":
                self.logger.info("        Teacher:%s has grabed order,orderNo:%s,stId:%s,imgurl:%s" %(self.userId,res.orderNo.decode(),res.stId,res.imgUrl))
                info = self._downloadimg(res.imgUrl)
                if not info['success']:
                    success = False
                    self.status_dict[status] = {"status":False,"errorinfo":info['msg']}
                else:
                    self.orderinfo["teacher"] = {"id":self.userId,"name":self.username.decode(),"senddatas":0,"receivedatas":0}
                    self.orderNo = res.orderNo
                    self.stId = res.stId
                    self.grouplist.append({
                                    "tcId":self.userId,
									"stId":res.stId
                    })
            elif status == "iscreatevoicechannel":
                if self.orderNo != res.orderNo:
                    self.status_dict[status] = {"status":False,"errorinfo":"语音通道orderNo与订单ID不一致,返回orderNo:%s,订单orderNo:%s" %(res.orderNo,self.orderNo)}
                    success = False
                elif self.stId != res.stId:
                    self.logger.info("        [check] userno:%s received orderNo equals student's orderNo,  pass" %self.username.decode())
                    self.status_dict[status] = {"status":False,"errorinfo":"语音通道学生ID与订单学生ID不一致,返回stId:%s,订单stId:%s" %(res.stId,self.stId)}
                    success = False
                else:
                    self.logger.info("        [check] userno:%s received stId equals student's stId,  pass" %self.username.decode())
                    self.mediaIp = res.mediaIp
                    self.mediaPort = res.mediaPort
                    self.token = res.token
                    self.roomId = res.roomId
            elif status == "isregretorder":
                if self.orderNo != res.orderNo:
                    self.status_dict[status] = {"status":False,"errorinfo":"老师悔单收到的订单号与抢单的订单号不一致,悔单orderNo:%s,抢单orderNo:%s" %(res.orderNo,self.orderNo)}
                    success = False
                else:
                    self.logger.info("        [check] userno:%s received orderNo equals student's orderNo,  pass" %self.username.decode())
                    self.orderNo = None
            elif status == "isbeginexplain":
                if self.orderNo != res.orderNo:
                    success = False
                    self.status_dict[status] = {"status":False,"errorinfo":"老师开始讲解的订单号与接到的订单号不一致,开始讲解orderNo:%s,抢单orderNo:%s" %(res.orderNo,self.orderNo)}
            elif status == "isnotifystendexplain":
                if self.orderNo != res.orderNo:
                    self.status_dict[status] = {"status":False,"errorinfo":"老师收到学生取消订单的订单号与抢到的订单号不一致,取消订单orderNo:%s,抢单orderNo:%s" %(res.orderNo,self.orderNo)}
                    success = False
                self.orderNo = None
            elif status == "isnotifystcancelorder":
                pass
            elif status == "isendexplain":
                pass
            elif status == "isenterroomresult":
                pass
            elif status == "":
                pass
            elif status == "":
                pass
            elif status == "":
                pass
            elif status == "":
                pass
            elif status == "islogout":
                self.userId = None
                self.orderNo = None
            else:
                pass

        if success:
            self.status_dict[status] = {"status":True,"errorinfo":None}
            #print("设置%s状态：成功" %status)
    
#login
    def login(self):
        ret = self.core.Login(self.handlereq,TcLoginReq(self.server['ip'].encode(),self.server['port'],self.username,self.pwd,b'1.2.1'))
        self.current_stat = 'islogin'
		
    def setfree(self):
        ret = self.core.SetTeacherStat(self.handlereq,SetTeacherStatReq(0))
        if ret > 0:
            self.status_dict['issetfree'] = {"status":True,"errorinfo":None}
        else:
            self.status_dict['issetfree'] = {"status":False,"errorinfo":"setfree failed, return code:%s" %ret}

    def setbusy(self):
        ret = self.core.SetTeacherStat(self.handlereq,SetTeacherStatReq(1))
        if ret > 0:
            self.status_dict['issetbusy'] = {"status":True,"errorinfo":None}
        else:
            self.status_dict['issetbusy'] = {"status":False,"errorinfo":"setbusy failed, return code:%s" %ret}
#logout
    def logout(self):
        ret=self.core.Logout(self.handlereq,TcLogoutReq(self.userId))
        self.current_stat = 'islogout'

#graborder
    def graborder(self):
        if self.noticedOrders:
            orderNo = self.orderinfo['specialOrderNo'].encode() if self.orderinfo['specialOrderNo'] else random.sample(self.noticedOrders,1)[0]
            self.logger.info("        Teacher GrabOrder:%s,Current noticedOrders:%s" %(orderNo.decode(),','.join([i.decode() for i in self.noticedOrders])))
            self.core.GrabOrder(self.handlereq,GrabOrderReq(orderNo,1))
        else:
            self.status_dict["isnotifyneworder"] = {"status":False,"errorinfo":"haven't notify new order!"}
        self.current_stat = 'isgraborder'

#rejectorder
    def regretorder(self):
        self.core.RegretOrder(self.handlereq,RegretOrderReq(self.orderNo,2))
        self.current_stat = 'isregretorder'
		
    def pushorder(self):
        self.core.PushOrder(self.handlereq,PushOrderReq())
		
#createvoicehannel
    def createvoicechannel(self):
        #print("self.stId",self.stId)
        self.core.CreateVoiceChannel(self.handlereq,CreateVoiceChannelReq(self.orderNo,self.stId))
        self.current_stat = 'iscreatevoicechannel'

#beginexplain
    def beginexplain(self):
        self.core.TcBeginExplain(self.handlereq,TcBeginExplainReq(self.orderNo,self.roomId))
        self.current_stat = 'isbeginexplain'

#newmedia
    def newmedia(self):
        rp = self.media.SUnet_new(self._data_fn,self._log_fn,self._notify_fn,c_void_p(0))
        if rp != 0:
            self.status_dict['isnewmedia'] = {"status":False,"errorinfo":"new media failed, return code:%s" %rp}
        else:
            self.status_dict['isnewmedia'] = {"status":True,"errorinfo":None}

#connectmedia
    def connectmedia(self):
        rp = self.media.SUnet_connect(c_char_p(self.mediaIp),c_int(self.mediaPort),c_int(0),c_int(self.userId),c_char_p(self.token),c_uint(16))
        if rp == 0:
            self.status_dict['isconnectmedia'] = {"status":True,"errorinfo":None}
        else:
            self.status_dict['isconnectmedia'] = {"status":False,"errorinfo":"connect media failed,return code:%s" %rp}

#enterroom
    def enterroom(self):
        rp = self.media.SUnet_enterRoom(c_int(self.roomId),c_int(0),c_char_p(self.orderNo),c_int(14))
        if rp == 0:
            self.logger.info("        [check] userno:%s enterromm request response == 0,  pass" %self.username.decode())
            self.status_dict['isenterroom'] = {"status":True,"errorinfo":None}
        else:
            self.status_dict['isenterroom'] = {"status":False,"errorinfo":"enterroom failed,return code:%s" %rp}
			
    def enterroomresult(self):
        ret=self.core.TcEnterRoomResult(self.handlereq,TcEnterRoomResultReq(self.orderNo,0,b'enterroom successful'))
        self.current_stat = 'isenterroomresult'
        #self.logger.info("00000000000000000000tcenterroomresult ret:%s" %ret)

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
                self.orderinfo['teacher'] = {"id":self.userId,"name":self.name,"senddatas":self.senddatas,"receivedatas":self.receivedatas}
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
            self.status_dict["isstartaction"] = {"status":False,"errorinfo":"startAction failed, return code:%s" %rp}
        else:
            self.status_dict["isstartaction"] = {"status":True,"errorinfo":None}

#stopaction
    def stopaction(self):
        rp = self.media.SUnet_stopAction()
        if rp != 0:
            self.status_dict['isstopaction'] = {"status":False,"errorinfo":"stopAction failed, return code:%s" %rp}
        else:
            self.status_dict['isstopaction'] = {"status":True,"errorinfo":None}

#leaveroom
    def leaveroom(self):
        result = self.closestream(self.stId)
        if result:
            rp  = self.media.SUnet_leaveRoom()
            if rp != 0:
                self.status_dict['isleaveroom'] = {"status":False,"errorinfo":"leaveroom failed,return code:%s" %rp}
            else:
                self.status_dict['isleaveroom'] = {"status":True,"errorinfo":None}
        else:
            self.status_dict['isleaveroom'] = {"status":False,"errorinfo":"leaveroom failed,closestream failed!"}

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
            errorinfo += "SUnet_release failed,return code:%s" %rp2

        if success:
            self.status_dict['isclosemedia'] = {"status":True,"errorinfo":None}
        else:
            self.status_dict['isclosemedia'] = {"status":False,"errorinfo":errorinfo}

#endexplain
    def endexplain(self):
        ret = self.core.TcEndExplain(self.handlereq,TcEndExplainReq(self.orderNo))
        self.logger.info("        tc_endexplain ret:%s" %ret)
        self.current_stat = 'isendexplain'

    def starts(self):
        try:
            self.core.startAction(self.handlereq,self.handleres)
            self.status_dict['isstart'] = {"status":True,"errorinfo":None}
        except Exception as e:
            self.status_dict['isstart'] = {"status":False,"errorinfo":"StartAction Failed,info:%s" %str(e)}

    def stops(self):
        try:
            self.core.stopAction(self.handlereq,self.handleres)
            self.status_dict['isstop'] = {"status":True,"errorinfo":None}
        except Exception as e:
            self.status_dict['isstop'] = {"status":False,"errorinfo":"StopAction Failed,info:%s" %str(e)}

    def disconnect(self):
        ret = self.core.Disconnect(self.handlereq)
        self.logger.info("Disconnect called,ret:%s" %ret)
        self.status_dict['isdisconnect'] = {"status":True,"errorinfo":None}
        self.status_dict["isdisconnect"] = {"status":True,"errorinfo":None}	
			
#run
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
                        self.logger.info("        userno:%s userId:%s action:%s begin" %(self.username.decode(),self.userId,ename))
                        try:
                            eval('self.%s()' %ename)
                        except Exception as e:
                            self.logger.info(str(e))
                        self.logger.info("        userno:%s userId:%s action:%s end" %(self.username.decode(),self.userId,ename))
                        e.clear()
            time.sleep(0.1)
        else:
            self.logger.info("        teacher stopped")
            self.status_dict['isstop'] = {"status":True,"errorinfo":None}

if __name__ == '__main__':
	pass


