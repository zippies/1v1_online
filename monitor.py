from flask import Flask,render_template,request,flash,jsonify,url_for
import json,os,time,pexpect,eventlet
eventlet.monkey_patch()
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate,MigrateCommand
from flask_socketio import SocketIO,send,emit
from configs import config,mode
from defender.configs import filepath


app = Flask(__name__)
app.config.from_object(config[mode])

sockets = SocketIO(app)
db = SQLAlchemy(app)
manager = Manager(app)
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)

class Monitorjob(db.Model):
	__tablename__ = 'monitorjob_' + mode
	id = db.Column(db.Integer,primary_key=True)
	status = db.Column(db.Integer,default=0)
	result = db.Column(db.Boolean)
	errormsg = db.Column(db.String(200))
	logpath = db.Column(db.String(200))
	servertype = db.Column(db.Integer)
	createdtime = db.Column(db.DateTime,default=datetime.now)

class Serviceip(db.Model):
	__tablename__ = 'serviceip_' + mode
	id = db.Column(db.Integer,primary_key=True)
	ip = db.Column(db.String(30))
	servertype = db.Column(db.Integer)

class Users(db.Model):
	__tablename__ = 'users_' + mode
	id = db.Column(db.Integer,primary_key=True)
	type = db.Column(db.String(10))
	usernos = db.Column(db.PickleType)
	password = db.Column(db.String(100))
	password_md5 = db.Column(db.String(100))
	imgurl = db.Column(db.String(100))
	servertype = db.Column(db.Integer)

@manager.command
def dbinit():
    db.create_all()
    db.session.commit()
    print("ok")

@manager.command
def dbdrop():
    db.drop_all()
    print('ok')

@sockets.on('connect')
def onconnect():
	print('[one client connected]')

@sockets.on('disconnect')
def disconnect():
	pass

# @sockets.on('message')
# def onmessage(msg):
# 	print(msg)

@sockets.on('testio')
def handle_testio_event(msg):
	print('receive testio request')


@sockets.on_error()        # Handles the default namespace
def error_handler(e):
	pass

@app.route('/view/<path>/<file>')
def viewlog(path,file):
	errorinfo = ""
	logname = os.path.join(path,file)
	error = os.path.join(filepath,'logs',path,file[:-4]+'error')
	with open(error,'r') as f:
		errorinfo = f.read()

	return render_template('viewlog.html',logname=logname,errorinfo=errorinfo)

@app.route('/getlog/<path>/<file>')
def getlog(path,file):
	logfile = os.path.join(filepath,'logs',path,file)
	with open(logfile,'r') as f:
		return f.read().strip()

@app.route("/")
@app.route("/<stype>")
def index(stype='inline'):
	flash({"type":"info","message":"当前：%s环境！" %('QA' if stype=='inline' else '生产')})
	friendslink = [
		{"alias":"生产环境1v1" ,"link":"#########"} if stype=='inline' else {"alias":"QA环境1v1" ,"link":"################"},
		{"alias":"监控系统","link":"#########################"}
	]
	navitems = [
		{"alias":"手动测试1v1","method":"showhtml('%s/test')" %stype,"id":"run"},
		{"alias":"查看历史错误","method":"showhtml('%s/viewerror')" %stype,"id":"viewerror"},
		{"alias":"查看运行日志","method":"showhtml('%s/viewinfo')" %stype,"id":"viewinfo"},
		{"alias":"修改测试用例","method":"showhtml('%s/editcase')" %stype,"id":"showeditcase"}
	]
	return render_template("index.html",
				friendslink=friendslink,
				navitems=navitems,
				stype=stype
			)

@app.route("/<stype>/test")
def inlinetest(stype):
	servertype = 0 if stype == 'inline' else 1
	serviceip = Serviceip.query.filter_by(servertype=servertype).first().ip if Serviceip.query.filter_by(servertype=servertype).first() else ""
	return render_template("test.html",serviceip=serviceip,stype=stype)

@app.route('/<stype>/viewerror')
def inlineviewerror(stype):
	return render_template("viewerror.html",stype=stype)

@app.route('/<stype>/viewinfo')
def onlineviewinfo(stype):
	return render_template("viewinfo.html",stype=stype)

@app.route('/<stype>/editcase')
def inlineeditcase(stype):
	servertype = 0 if stype == 'inline' else 1
	teachers = Users.query.filter(db.and_(Users.type =='tc',Users.servertype == servertype)).first()
	students = Users.query.filter(db.and_(Users.type =='st',Users.servertype == servertype)).first()
	tcs = ';'.join(teachers.usernos) if teachers else ""
	sts = ';'.join(students.usernos) if students else ""
	tcpwd = teachers.password if teachers else ""
	stpwd = students.password if students else ""
	imgurl = students.imgurl if students else ""
	return render_template(
			'editcase.html',
			tcs = tcs,
			sts = sts,
			stpwd = stpwd,
			tcpwd = tcpwd,
			imgurl = imgurl,
			stype = stype
			)

@app.route('/<stype>/modifyuser/<type>',methods=['POST'])
def modifyuser(stype,type):
	import hashlib
	m = hashlib.md5()
	servertype = 0 if stype == 'inline' else 1
	nos = [i for i in request.form['nos'].split(';') if i]
	pwd = request.form['pwd']
	m.update(pwd.encode())
	md5_pwd = m.hexdigest()
	user = Users.query.filter(db.and_(Users.type==type,Users.servertype==servertype)).first()
	if user:
		user.usernos = nos
		user.password = pwd
		user.password_md5 = md5_pwd
	else:
		user = Users(type=type,usernos=nos,password=pwd,password_md5=md5_pwd,servertype=servertype)
	db.session.add(user)
	db.session.commit()
	return "success"

@app.route('/<stype>/modifyimg',methods=['POST'])
def modifyimg(stype):
	servertype = 0 if stype == 'inline' else 1
	imgurl = request.form['img']
	user = Users.query.filter(db.and_(Users.type == 'st',Users.servertype == servertype)).first()
	if user:
		user.imgurl = imgurl
	else:
		user = Users(type='st',usernos=[],password="",password_md5="",imgurl=imgurl,servertype=servertype)
	db.session.add(user)
	db.session.commit()
	return "success"

@app.route('/<stype>/modifyip',methods=["POST"])
def modifyip(stype):
	import requests
	servertype = 0 if stype == 'inline' else 1
	rip = dealip(request.form['ip'])
	try:
		r = requests.get(rip,timeout=(1,1.5)).status_code
		if r != 200:
			return "failure"
	except:
		return "failure"
	ip = Serviceip.query.filter_by(servertype=servertype).first()

	if ip:
		ip.ip = rip
	else:
		ip = Serviceip(ip=rip,servertype=servertype)
	db.session.add(ip)
	db.session.commit()
	return "success"

def dealip(ip):
	if ip.startswith('http://'):
		return ip
	else:
		return "http://" + ip

@app.route('/getcase')
def getcase():
	if os.path.exists('defender/case.py'):
		with open('defender/case.py','r') as f:
			return f.read()

@app.route('/modifycase',methods=['POST'])
def modifycase():
	case = request.form['case']
	if case and os.path.exists('defender/case.py'):
		try:
			with open('defender/case.py','w') as f:
				f.write(case)
		except Exception as e:
			return "ERROR:%s" %str(e)
	else:
		return "修改失败,用例为空！"
	return "修改成功！"	


@app.route('/<stype>/runjob',methods=['GET','POST'])
def runjob(stype):
    servertype = 0 if stype == 'inline' else 1
    result = {"result":False,"errorMsg":"已有任务正在运行","steps":None}
    if not check(servertype):
        return json.JSONEncoder().encode(result)
    
    if request.method == 'POST':
        result = runone()
        if result:
            return json.JSONEncoder().encode(result)
        else:
            return "failed"
    else:
        return "unsupported method:get"


@app.route('/<stype>/geterror')
def getError(stype):
	servertype = 0 if stype == 'inline' else 1
	#errors = []
	errorjobs = Monitorjob.query.filter(db.and_(Monitorjob.result==0,Monitorjob.servertype==servertype)).all()
	errors = [' — '.join([str(e.createdtime),e.errormsg]) for e in errorjobs]
	return json.JSONEncoder().encode(errors[::-1])

@app.route("/<stype>/delerror")
def delerror(stype):
	servertype = 0 if stype == 'inline' else 1
	errorjobs = Monitorjob.query.filter(db.and_(Monitorjob.result==0,Monitorjob.servertype==servertype)).all()
	for job in errorjobs:
		job.result = 1
		db.session.add(job)
		db.session.commit()
	return jsonify([])

@app.route('/<stype>/dellog',methods=['POST'])
def dellog(stype):
	servertype = 0 if stype == 'inline' else 1
	jobs = Monitorjob.query.filter_by(servertype=servertype).all()
	for job in jobs:
		db.session.delete(job)
	db.session.commit()
	return jsonify([])

@app.route('/<stype>/getinfo')
def getInfo(stype):
	servertype = 0 if stype == 'inline' else 1
	jobs = Monitorjob.query.filter_by(servertype=servertype).order_by(db.desc('id')).all()
	info = {
		"success":[],
		"failed":[]
	}
	for job in jobs:
		if job.result == 1:
			info['success'].append(job.logpath)
		else:
			info['failed'].append(job.logpath)
	return json.JSONEncoder().encode(info)

@app.route('/getloginfo')
def getloginfo():
	file = request.args.get('file')
	with open(file,'r') as f:
		return json.JSONEncoder().encode(f.readlines())
	
def check(servertype):
    job = Monitorjob.query.filter(db.and_(Monitorjob.status==1,Monitorjob.servertype==servertype)).first()
    if job is not None:
        return False
    else:
        return True

def checkserver(ip):
	import requests,random
	r = None
	try:
		r = requests.get(ip)
	except:
		return {"result":False,"errorMsg":"server is not reachable:%s" %ip}
	servers = []
	if r.status_code == 200:
		try:
			servers = eval(r.text)['hosts']
		except:
			return {"result":False,"errorMsg":"All server is crashed,%s" %r.text}
	else:
		return {"result":False,"errorMsg":"Server return:%s" %r.status_code}

	return {"result":True}


@app.route('/<stype>/run',methods=['POST'])
def run(stype):
	servertype = 0 if stype == 'inline' else 1
	job = Monitorjob.query.filter(db.and_(Monitorjob.status==1,Monitorjob.servertype==servertype)).first()
	if job is not None:
		result = {"result":False,"errorMsg":"exists running job","logpath":job.logpath}
		return json.JSONEncoder().encode(result)
	else:
		try:
			logpath = os.path.join(filepath,"logs",stype,datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
			job = Monitorjob(
				status = 1,
				logpath = logpath+'/case.info',
				servertype = servertype
			)
			db.session.add(job)
			db.session.commit()
			ip = Serviceip.query.filter_by(servertype=servertype).first().ip
			result = checkserver(ip)
			if result['result']:
				tc = Users.query.filter(db.and_(Users.type=='tc',Users.servertype==servertype)).first()
				st = Users.query.filter(db.and_(Users.type=='st',Users.servertype==servertype)).first()
				tcnos,tcpwd = tc.usernos,tc.password_md5
				stnos,stpwd,imgurl = st.usernos,st.password_md5,st.imgurl
				logpath = job.logpath[:-10]
				cmd = "python autoTest.py '%s' '%s' '%s' '%s' '%s' '%s' '%s' '%s'" %(ip,tcnos,tcpwd,stnos,stpwd,imgurl,logpath,stype)
				p = pexpect.spawnu(cmd)
				id = 0
				while p.isalive():
					index = p.expect(['\n',pexpect.EOF])
					type = None
					if index == 0:
						id += 1
						info = p.before
						if "|" in info:
							type = info.split("|")[1]
						sockets.emit(stype,{"id":"index"+str(id),"info":info,'type':type})
				result = json.load(open('%s.json' %stype,'r'))
				result['logpath'] += '.info'
				os.remove('%s.json' %stype)
				job.status = 2
				job.result = result['result']
				job.errormsg = result['errorMsg'][:180] if result['errorMsg'] else None
				db.session.add(job)
				db.session.commit()
			else:
				db.session.delete(job)
				db.session.commit()
		except Exception as e:
			print(e)
			result = {"result":False,"errorMsg":str(e)}
			db.session.delete(job)
			db.session.commit()
		finally:
			return json.JSONEncoder().encode(result)
		
		
@app.route('/<stype>/runnow',methods=['POST'])
def runnow(stype):
	import eventlet
	servertype = 0 if stype == 'inline' else 1
	eventname = request.form.get('eventname')
	if not eventname:
		result = {"result":False,"errorMsg":"eventname could not be None"}
		return json.JSONEncoder().encode(result)
	job = Monitorjob.query.filter(db.and_(Monitorjob.status==1,Monitorjob.servertype==servertype)).first()
	if job is not None:
		result = {"result":False,"errorMsg":"exists running job","logpath":job.logpath}
		return json.JSONEncoder().encode(result)
	else:
		logpath = os.path.join(filepath,"logs",datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
		job = Monitorjob(
			status = 1,
			logpath = logpath+'/case.info',
			servertype=servertype
		)
		db.session.add(job)
		db.session.commit()
		# t = Thread(target=runjob,args=(stype,eventname))
		# t.setDaemon(True)
		# t.start()
		eventlet.spawn_n(runjob,stype,eventname)
		return json.JSONEncoder().encode({"result":True,"errorMsg":None,"logpath":job.logpath})

def runjob(stype,eventname):
	time.sleep(0.5)
	servertype = 0 if stype == 'inline' else 1
	job = Monitorjob.query.filter(db.and_(Monitorjob.status==1,Monitorjob.servertype==servertype)).first()
	ip = Serviceip.query.filter_by(servertype=servertype).first().ip
	tc = Users.query.filter(db.and_(Users.type=='tc',Users.servertype==servertype)).first()
	st = Users.query.filter(db.and_(Users.type=='st',Users.servertype==servertype)).first()
	tcnos,tcpwd = tc.usernos,tc.password_md5
	stnos,stpwd,imgurl = st.usernos,st.password_md5,st.imgurl
	try:
		logpath = job.logpath[:-10]
		cmd = "python autoTest.py '%s' '%s' '%s' '%s' '%s' '%s' '%s' '%s'" %(ip,tcnos,tcpwd,stnos,stpwd,imgurl,logpath,stype)
		p = pexpect.spawnu(cmd)
		id = 0
		while p.isalive():
			type = None
			index = p.expect(['\n',pexpect.EOF])
			if index == 0:
				id += 1
				info = p.before
				if "|" in info:
					info,type = info.split("|")
				sockets.emit(eventname,{"id":"index"+str(id),"info":info,'type':type})
				print("eventname:",eventname,"info:",info)
		result = json.load(open('%s.json' %stype,'r'))
		result['logpath'] += '.info'
		os.remove('%s.json' %stype)
		job.status = 2
		job.result = result['result']
		job.errormsg = result['errorMsg'][:180] if result['errorMsg'] else None
		db.session.add(job)
		db.session.commit()
	except Exception as e:
		print(e)
		result = {"result":False,"errorMsg":str(e)}
		db.session.delete(job)
		db.session.commit()
	finally:
		sockets.emit(eventname,result)
		
if __name__ == '__main__':
	#manager.run()
	sockets.run(app,'0.0.0.0',7788)


