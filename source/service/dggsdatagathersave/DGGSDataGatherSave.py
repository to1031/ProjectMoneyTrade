#coding: utf-8
# 概要
# データ収集クラス
################ 変更履歴 ######################
## 2017/09/13 作成
###############################################

import itertools
from datetime import datetime
import math
import os
import configparser
import sys

class DGGSDataGatherSave(object):
	# 初期化処理
	def __init__(self,dict):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPMONEYTRADE"]

		# iniconfigファイルを読み出す。
		self.inifile = dict['util'].inifile

		# 当サービスの機能IDを取得する。
		self.pid = 'DGGS'

		# 呼び出し元も機能ID
		self.called_pid = dict['pid']

		# util dao を静的に
		self.utilClass = dict['util']
		self.daoClass = dict['dao']
		self.MASSClass = dict['mass']


	# 予想結果保存サービス
	def prssService(self,predict,result):
		# 当メソッドの名前を取得する。
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 返却IF用辞書を準備
		resultIFdict = {}
		resultIFdict['resultCode'] = 0

		# insert_dict
		insert_dict = {}
		insert_dict['LOGIC_DEL_FLG'] = 0
		insert_dict['INS_PID'] = self.pid
		insert_dict['UPD_PID'] = self.pid
		insert_dict['PREDICT'] = predict
		insert_dict['RESULT'] = result

		# DBインサート
		self.daoClass.insert('PREDICT_RESULT_T',insert_dict)

		# 処理終了のログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

		# 返却IFをreruenする
		return resultIFdict





