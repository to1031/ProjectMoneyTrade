# coding: utf-8
# 概要
# ビットフライヤー API接続
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################

import itertools
from datetime import datetime
import math
import os
import configparser
import sys
import urllib.request
import json

class BitflyerApi(object):
	START = 'start.'
	END = 'end.'
	INFO = '[INFO] '
	ERROR = '[ERROR] '
	WARN = '[WARN] '
	utilClass = None
	
	# 初期化処理
	def __init__(self,pid):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPMONEYTRADE"]

		# iniconfigファイルを読み出す。
		condigPath = self.homeDir + 'conf'
		inifile = configparser.ConfigParser()
		inifile.read(condigPath + '/config.ini', 'UTF-8')
		self.inifile = inifile

		# 機能ID
		self.pid = pid

		# Utilクラスの初期化
		# 1時的に環境変数を追加する。
		sys.path.append(self.homeDir)
		from util import Util
		self.utilClass = Util.Util(pid)
		

	# board + execuru
	def boardApi(self,apiurl,coin,puery,apitype,timeout=7):
		# ビットコイン/円の場合はパラメータが必要ない
		data = {}
		data['product_code'] = coin
		if 'executions' in apitype:
			data['count'] = 500
		url_values = urllib.parse.urlencode(data)
		if puery != '':
			req = urllib.request.Request(apiurl + apitype + "?" + url_values,headers={'User-Agent': 'Mozilla/5.0'})
		else:
			req = urllib.request.Request(apiurl + apitype,headers={'User-Agent': 'Mozilla/5.0'})

		# responseの初期値を取得する。
		response = 0
		# HTTPとかタイムアウト時の処理
		try:
			with urllib.request.urlopen(req,timeout=7) as res:
				response = res.read().decode("utf-8")
		except:
			self.utilClass.loggingError(apiurl + '/' + coin + '/' + apitype + 'HttpError')

		return response


	# 過去の取引履歴を取得する。
	def executions_pastApi(self,apiurl,targetcoin,puery,apitype,before):
		# ビットコイン/円の取引高を取得する。
		data = {}
		data['product_code'] = targetcoin
		data['count'] = 99
		data['before'] = before
		url_values = urllib.parse.urlencode(data)
		req = urllib.request.Request(apiurl + apitype + "?" + url_values,headers={'User-Agent': 'Mozilla/5.0'})
		response = 0
		try:
			with urllib.request.urlopen(req,timeout=7) as res:
				response = res.read().decode("utf-8")
		except:
			self.utilClass.loggingError(apiurl + '/' + coin + '/' + apitype + 'HttpError')

		return response
