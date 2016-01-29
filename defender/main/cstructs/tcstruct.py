from ctypes import *

class PackHeader(Structure):
    _fields_=[('mark',c_char*2),
            ('version',c_uint),
            ('ebcryption',c_uint),
            ('length',c_uint),
            ('mode',c_uint),
            ('content_type',c_uint),
            ('command',c_uint),
            ('agent_id',c_uint),
            ('error',c_uint),
            ('cseq',c_uint),
            ('reserve',c_uint),
            ('data',c_char*0)]
class DisconnectInfo(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128)]

class TcLoginReq(Structure):
    _fields_=[('host',c_char*32),
            ('port',c_int),
            ('userName',c_char*256),
            ('pwd',c_char*256),
            ('clientVersion',c_char*64),
            ('clientType',c_uint),
            ('clientOption',c_char*4096),
            ('media_list',c_uint),
            ('deviceInfo',c_char*512)]

class TcLoginRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char *128),
            ('userId',c_uint),
            ('name',c_char*256),
            ('phoneNo',c_char*20),
            ('subject',c_uint),
            ('grade',c_uint),
            ('avatar',c_char*512),
            ('birthDate',c_char*32),
            ('sex',c_uint),
            ('startFreezeTime',c_uint),
            ('endFreezeTime',c_uint),
            ('freezeReason',c_char*128),
            ('cookieName',c_char*128),
            ('cookieValue',c_char*128),
            ('configInfo',c_char*10240),
            ('status',c_int32),
            ('forbid',c_int32),
            ('accountStatus',c_uint32),
            ('forbidReason',c_char*128),
            ('breakReason',c_char*128),
            ('deniedLoginReason',c_char*128)]
class TcLogoutReq(Structure):
    _fields_=[('userId',c_uint)]

class TcLogoutRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128)]

class GrabOrderReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('action',c_uint)]
class GrabOrderRes(Structure):
    _fields_=[('code',c_uint32),
            ('errorMsg',c_char*128),
            ('orderNo',c_char*32),
            ('imgUrl',c_char*256),
            ('answer',c_char*10485760),
            ('stId',c_uint32),
            ('stName',c_char*256),
            ('grades',c_char*64),
            ('points',c_char*1024),
            ('imgUrlBak',c_char*256),#9.21 added
            ('isFirstOrder',c_bool),#9.21 added
            ('rotate',c_int32),
            ('aid',c_char*32),
            ('fromType',c_uint),
            ('pureStem',c_char*1048576),
            ('pureAnswer',c_char*10485760),
            ('tags',c_char*1024*4)] #10.19 added
class NewOrderReq(Structure):
    _fields_=[('orderNo',c_char*32)]

class NewOrderRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128),
            ('orderNo',c_char*32)]
class RegretOrderReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('reason',c_uint),
            ('oldSubject',c_uint), #9.21 added 
            ('oldGrade',c_uint),# 9.21 added
            ('newSubject',c_uint),# 9.21 added 
            ('newGrade',c_uint)] #9.21 added
class RegretOrderRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128),
            ('orderNo',c_char*32)]
class CreateVoiceChannelReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('stId',c_uint)]
class CreateVoiceChannelRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('stId',c_uint),
            ('code',c_uint),
            ('errorMsg',c_char*128),
            ('operId',c_char*32),
            ('mediaIp',c_char*32),
            ('mediaPort',c_uint),
            ('roomId',c_uint),
            ('token',c_char*128),
            ('roomUser',c_char*256),
            ('roomPwd',c_char*256),
            ('selfV2SessionInfo',c_char*1024)]
class TcBeginExplainReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('roomId',c_uint)]
class TcBeginExplainRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128),
            ('orderNo',c_char*32)]

class AddQuestionImgReq(Structure):
    _fiedls_=[('imgUrl',c_char*256),
            ('orderNo',c_char*32),
            ('answer',c_char*10485760),
            ('points',c_char*1024),
            ('imgUrlBak',c_char*256), #9.21 added
            ('rotate',c_int32),
            ('aid',c_char*32)] #10.19 added

class AddQuestionImgRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128),
            ('orderNo',c_char*32)]

class TcEndExplainReq(Structure):
    _fields_=[('orderNo',c_char*32)]
class TcEndExplainRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128),
            ('fee',c_float),
            ('explainTime',c_uint)]
class StEndExplainReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128),
            ('explainTime',c_uint),
            ('fee',c_float)]
class StEndExplainRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128)]
class TcEvaluateStReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('star',c_uint),
            ('comment',c_char*1024),
            ('grade',c_uint),
            ('tags',c_char*1024*4),
            ('difficulty',c_uint)]
class TcEvaluateStRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128)]

class StSuspendExplainReq(Structure):
    _fields_=[('orderNo',c_char*32)]
class StSuspendExplainRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128)]
class StRecoverExplainReq(Structure):
    _fields_=[('orderNo',c_char*32)]
class StRecoverExplainRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128)]
class TcUploadScreenshotReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('imgExtName',c_char*8),
            ('imgContent',c_char*10240)]
class TcUploadScreenshotRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128)]
class StCancelOrderReq(Structure):
    _fields_=[('orderNo',c_char*32)]
class StCancelOrderRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128)]
class ReportYixinFilenameReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('roomId',c_uint),
            ('voiceFilename',c_char*1024),
            ('noteFilename',c_char*1024)]
class ReportYixinFilenameRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128)]
class GetThirdpartyMediaRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128),
            ('yixinUser',c_char*256),
            ('yixinPwd',c_char*256)]
class PeerDisconnectReq(Structure):
    _fields_=[('orderNo',c_char*32)]
class PeerDisconnectRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128)]
class SetTeacherStatReq(Structure):
    _fields_=[('stat',c_uint)]

class SetTeacherStatRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128)]
class NewMsgReq(Structure):
    _fields_=[]
class NewMsgRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128)]

class TcEnterRoomResultReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('result',c_uint),
            ('resultMsg',c_char*128)]

class TcEnterRoomResultRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128)]

class TcStartAnalyzeQuestionReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('msg',c_char*128)]
class TcStartAnalyzeQuestionRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128)]

class TcKickoutReq(Structure):
    _fields_=[('teacherID',c_uint)]

class TcKickoutRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128)]




