
mode = 'debug' # debug,online

class DebugConfig:
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost:3306/monitordb'
	SECRET_KEY = 'WHAT DO YOU WANT FROM ME'

	@staticmethod
	def init_app(app):
		pass

class ProductionOnlineConfig:
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://monitor:monitorautomation@10.10.15.78:3306/monitordb'
	SECRET_KEY = 'WHAT DO YOU WANT FROM ME'

	@staticmethod
	def init_app(app):
		pass

config = {
	'debug':DebugConfig,
	'online':ProductionOnlineConfig
}


bind = "0.0.0.0:7788"

workers = 8

worker_class = "eventlet"

reload = True
