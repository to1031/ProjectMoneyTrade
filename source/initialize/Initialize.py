#coding: utf-8
# 概要
# 初期化クラス
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################
import os
import configparser
import sys

class Initialize(object):

	# 初期化処理
	def __init__(self,pid):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPMONEYTRADE"]

		# iniconfigファイルを読み出す。
		self.inifile = util.inifile

		# 当サービスの機能IDを取得する。
		self.pid = 'MASS'

		# 呼び出し元も機能ID
		self.call_pid = pid

		# iniconfigファイルを読み出す。
		condigPath = self.homeDir + '../../temp_ProjectMoneyTrade/conf'
		inifile = configparser.ConfigParser()
		inifile.read(condigPath + '/config_class.ini', 'UTF-8')
		self.inifile_class = inifile

		# 一時的に環境パスに追加する
		sys.path.append(homeDir)
		sys.path.append(homeDir + 'service/')
		sys.path.append(homeDir + 'batch/')
	
		# import
		from dataBaseAccess import Dao
		from util import Util
		from massmailsendservice import MASSMailSendService

		# utilクラス、daoクラス、メールクラスをインスタンス化
		self.utilClass = Util.Util(self.call_pid)
		self.daoClass = Dao.Dao(self.pid,self.utilClass)
		self.MASSClass = MASSMailSendService.MASSMailSendService(self.pid,self.utilClass)


	# クラスの生成
	def class_ins(self,class_name,util=None,dao=None,mass=Nome):
		# 一時的に環境パスを追加する
		sys.path.append(homeDir)
		sys.path.append(homeDir + 'service/')
		sys.path.append(homeDir + 'batch/')

		# configファイルからクラス情報を取得する。
		pack_class = self.inifile_class.get('class',class_name)
		
		# パッケージ名とクラス名を取得する。
		pack_name = pack_class.split(',')[0]
		class_name = pack_class.split(',')[1]


		# import文の調整
		import_ = 'import ' + pack_name + ' from ' + class_name

		# evalによるimportの実行
		eval(import_)

		# クラスのオブジェクト化命令文調整
		common_str = class_name + '.' + class_name + '(pid'
		plusstr = ')'
		if util is None:
		class_obj = class_name + '.' + class_nam


		
