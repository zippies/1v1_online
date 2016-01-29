#encoding=utf-8
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

class StLoginReq(Structure):
    _fields_=[('host',c_char*32),
            ('port',c_int),
            ('userName',c_char*256),
            ('pwd',c_char*256),
            ('clientType',c_uint),
            ('clientVersion',c_char*64),
            ('clientOption',c_char*4096),
            ('mediaList',c_uint),
            ('deviceInfo',c_char*512)]

class StLoginRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128),
            ('userId',c_uint)]
class StLogoutReq(Structure):
    _fields_=[('userId',c_uint)]

class StLogoutRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128)]

class SubmitQuestionReq(Structure):
    _fields_=[('imgUrl',c_char*256),
            ('feedId',c_char*128),
            ('isFirstOrder',c_bool),
            ('aid',c_char*32),
            ('fromType',c_uint)]#9.21 added

class SubmitQuestionRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128),
            ('orderNo',c_char*32)]

class AssignOrderResultReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128),
            ('tcId',c_uint),
            ('tcName',c_char*256)]
class AssignOrderResultRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128)]

class CreateVoiceChannelReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('tcId',c_uint)]
class CreateVoiceChannelRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('tcId',c_uint),
            ('code',c_uint),
            ('errorMsg',c_char*128),
            ('operId',c_char*32),
            ('mediaIp',c_char*32),
            ('mediaPort',c_uint),
            ('roomId',c_uint),
            ('token',c_char*128),
            ('roomUser',c_char*256),
            ('roomPwd',c_char*256),
            ('roomTcUser',c_char*256),
            ('selfV2SessionInfo',c_char*1024)]

class TcCancelOrderReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('reason',c_uint),
            ('oldGrade',c_uint),
            ('newGrade',c_uint),
            ('oldSubject',c_uint),
            ('newSubject',c_uint),
            ('msg',c_char*128)] #9.21 added

class TcCancelOrderRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128)]

class AddQuestionImgReq(Structure):
    _fiedls_=[('imgUrl',c_char*256),
            ('orderNo',c_char*32)]

class AddQuestionImgRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128),
            ('orderNo',c_char*32)]

class StCancelOrderReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('cancelType',c_uint),
            ('errorMsg',c_char*128)]
class StCancelOrderRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128)]

class TcBeginExplainReq(Structure):
    _fields_=[('orderNo',c_char*32)]
class TcBeginExplainRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128),
            ('orderNo',c_char*32)]

class TcEndExplainReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128),
            ('score',c_uint),
            ('explainTime',c_uint),
            ('fee',c_float)]
class TcEndExplainRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128),
            ('orderNo',c_char*32)]

class StEndExplainReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('endType',c_uint),
            ('errorMsg',c_char*128)]
class StEndExplainRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128),
            ('score',c_uint),
            ('explainTime',c_uint),
            ('fee',c_float)]

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

class PeerDisconnectReq(Structure):
    _fields_=[('orderNo',c_char*32)]
class PeerDisconnectRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128)]
class TeacherGrabReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('teacherId',c_uint)]

class TeacherGrabRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128)]
    
class TeacherPushReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('teacherCount',c_uint)]

class TeacherPushRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128)]

class StReportYixinFilenameReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('voiceFilename',c_char*512)]

class StReportYixinFilenameRes(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('errorMsg',c_char*128)]

class StSystemNoticeReq(Structure): #9.21 added
    _fields_=[('type',c_uint),
            ('msg',c_char*128)]

class StSystemNoticeRes(Structure): #9.21 added`
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128)]
class StEnterRoomResultReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('result',c_uint),
            ('resultMsg',c_char*128)]
class StEnterRoomResultRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128)]
class StStartAnalyzeQuestionReq(Structure):
    _fields_=[('orderNo',c_char*32),
            ('code',c_uint),
            ('msg',c_char*128)]
class StStartAnalyzeQuestionRes(Structure):
    _fields_=[('code',c_uint),
            ('errorMsg',c_char*128)]



















if __name__=="__main__":
    a=StLoginRes()
    a.errorMsg=b"ok"
    print (a.errorMsg)
    print (StLoginRes.__dict__)
