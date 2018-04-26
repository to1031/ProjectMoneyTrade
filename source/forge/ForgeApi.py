# coding: utf-8
# 概要
# 通過情報をAPIを利用して取得する
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
class ForgeApi(object):
	# 初期化処理
	def __init__(self,pid,util):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPMONEYTRADE"]

		# iniconfigファイルを読み出す。
		self.inifile = util.inifile

		# 機能ID
		self.pid = pid
		self.utilClass = util
		

	# 全ての通貨ペアの値段を取得する。
	def quotesApi(self,key,timeout=7):
		# 全ての通貨ペアの値段を取得する。
		parelist = self.inifile.get('moneypare','moneypare')	
		data = {}
		data['pairs'] = parelist
		data['api_key'] = key
		url_values = urllib.parse.urlencode(data)
		req = urllib.request.Request("https://forex.1forge.com/1.0.3/quotes?" + url_values,headers={'User-Agent': 'Mozilla/5.0'})

		# responseの初期値を取得する。
		response = 0
		# HTTPとかタイムアウト時の処理
		try:
			with urllib.request.urlopen(req,timeout=7) as res:
				response = res.read().decode("utf-8")
		except:
			self.utilClass.loggingError('quotesApi is HttpError')

		return response
