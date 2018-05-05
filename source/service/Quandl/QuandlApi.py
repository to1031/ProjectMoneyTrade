# coding: utf-8
# 概要
# 株価を取得
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################

import itertools
from datetime import datetime
import math
import os
import configparser
import sys
import quandl
import traceback

class QuandlApi(object):
	# 初期化処理
	def __init__(self,dict):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPMONEYTRADE"]

		self.inifile = dict['util'].inifile

		# 機能ID
		self.pid = dict['pid']

		# Utilクラスの初期化
		# 1時的に環境変数を追加する。
		sys.path.append(self.homeDir)
		from util import Util
		self.utilClass = Util.Util(self.pid)
		

	# 全ての通貨ペアの値段を取得する。
	def stocksApi(self,key,value,timeout=7):
		response = 0
		# HTTPとかタイムアウト時の処理
		try:
			response = quandl.get(value,authtoken=key)
		except:
			self.utilClass.logging("".join(traceback.format_stack()),2)
			self.utilClass.loggingError('stocksApi is HttpError')
		return response
