# coding: utf-8
# 概要
# ビットフライヤーAPI接続
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################

from datetime import datetime
import math
import os
import configparser
import sys
import urllib.request
import json
import time
import hmac
import hashlib
import traceback

class BitflyerApi(object):

	# 初期化処理
	def __init__(self,pid,util,dao):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPMONEYTRADE"]

		# iniconfigファイルを読み出す。
		self.inifile = util.inifile

		# 機能ID
		self.pid = 'BITF'

		# call_pid
		self.call_pid = pid
		

		# Utilクラスの初期化
		self.utilClass = util
		self.daoClass = dao

	# 最終取引価格を取得する。
	def ftpgService(self,cointype='FX_BTC_JPY',datanum=100):
		methodname = sys._getframe().f_code.co_name
		# ログの表示
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 返却辞書を生成する。
		returnDict = {}
		returnDict['resultCode'] = 9

		# ビットコイン/円の場合はパラメータが必要ない
		data = {}
		data['product_code'] = cointype
		data['count'] = datanum
		url_values = urllib.parse.urlencode(data)
		# apitypeとapiurlを取得する。
		apitype = self.inifile.get('apitype','executions')
		apiurl = self.inifile.get('url','futuredatabefore')
		req = urllib.request.Request(apiurl + apitype + "?" + url_values,headers={'User-Agent': 'Mozilla/5.0'})


		# responseの初期値を取得する。
		response = 0
		# HTTPとかタイムアウト時の処理
		try:
			with urllib.request.urlopen(req,timeout=7) as res:
				response = res.read().decode("utf-8")
		except:
			self.utilClass.loggingError(apiurl + '/' + coin + '/' + apitype + 'HttpError')


		# ERROR の場合はreturnする
		if response == 0:
			returnDict['resultCode'] = 9
			return returnDict

		# パースする。
		json_dict = json.loads(response)
		
		# 最終取引額のみ取得する。
		dict = json_dict[0]
		endTradePrice = dict['price']
		
		# SELL,BUYの回数および合計額を算出する。
		sell_count = 0
		buy_count = 0
		sell_ammount = 0
		buy_ammount = 0
		
		for i in range(len(json_dict)):
			# sellの場合
			if json_dict[i]['side'] =='SELL':
				sell_count = sell_count + 1
				sell_ammount = sell_ammount + json_dict[i]['price'] * json_dict[i]['size']
			else:
				buy_count = buy_count + 1
				buy_ammount = buy_ammount + json_dict[i]['price'] * json_dict[i]['size']
		
		returnDict['resultCode'] = 0
		returnDict['endTradePrice'] = endTradePrice
		returnDict['sell_count'] = sell_count
		returnDict['sell_ammount'] = sell_ammount
		returnDict['buy_count'] = buy_count
		returnDict['buy_ammount'] = buy_ammount


		# 終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

		return returnDict


	# 現在の取引予約を取得する。
	def ebtrService(self,apikey,apisecret,cointype='FX_BTC_JPY',datanum=1):
		methodname = sys._getframe().f_code.co_name
		# 開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 返却辞書を生成する。
		returnDict = {}
		returnDict['resultCode'] = 9

		apitype = self.inifile.get('apitype','getchildorders')
		apiurl = self.inifile.get('url','futuredatabefore')	

                # パラメータの調整する。
		data = {}
		data['product_code'] = cointype
		data['count'] = datanum
		data['child_order_state'] = 'ACTIVE'
		url_values = urllib.parse.urlencode(data)
		# GETかPOSTか
		method = 'GET'
		timestamp = str(time.time())
		text = timestamp + method + apitype + '?' + url_values

		sign = hmac.new(bytes(apisecret.encode('utf-8')), bytes(text.encode('utf-8')), hashlib.sha256).hexdigest()
		#sign = hmac.new(bytes(apisecret.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

		req = urllib.request.Request(apiurl + apitype + "?" + url_values,headers={'ACCESS-KEY': apikey,
											'ACCESS-TIMESTAMP': timestamp,
											'ACCESS-SIGN': sign,
											'Content-Type': 'application/json',
											'User-Agent': 'Mozilla/5.0'
												})


		# # responseの初期値を取得する。
		response = 0

                # HTTPとかタイムアウト時の処理
		try:            
			with urllib.request.urlopen(req,timeout=7) as res:
				response = res.read().decode("utf-8")
		except:
			self.utilClass.loggingError(traceback.format_exc())


		
		# ERRORの場合はreturnする。
		if response == 0:
			return returnDict

		# パースする。
		json_dict = json.loads(response)

		# returnする辞書を調整する。
		if len(json_dict) == 0:
			returnDict['resultCode'] = 0
			returnDict['resultNum'] = 0
			return returnDict
		returnDict['resultCode'] = 0
		returnDict['resultNum'] = 1
		returnDict['id'] = json_dict[0]['id']
		returnDict['child_order_id'] = json_dict[0]['child_order_id']
		returnDict['product_code'] = json_dict[0]['product_code']
		returnDict['side'] = json_dict[0]['side']
		returnDict['price'] = json_dict[0]['price']
		returnDict['size'] = json_dict[0]['size']
		returnDict['child_order_date'] = json_dict[0]['child_order_date']
		
		# 終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

		# 返却
		return returnDict

	# 現在の有効取引を取得する。
	def evtrService(self,apikey,apisecret,cointype='FX_BTC_JPY',datanum=1):
		methodname = sys._getframe().f_code.co_name
		# 処理開始
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 返却辞書を生成する。
		returnDict = {}
		returnDict['resultCode'] = 9

		apitype = self.inifile.get('apitype','getpositions')
		apiurl = self.inifile.get('url','futuredatabefore')	

                # パラメータの調整する。
		data = {}
		data['product_code'] = cointype
		url_values = urllib.parse.urlencode(data)
		# GETかPOSTか
		method = 'GET'
		timestamp = str(time.time())
		text = timestamp + method + apitype + '?' + url_values

		sign = hmac.new(bytes(apisecret.encode('utf-8')), bytes(text.encode('utf-8')), hashlib.sha256).hexdigest()
		#sign = hmac.new(bytes(apisecret.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

		req = urllib.request.Request(apiurl + apitype + "?" + url_values,headers={'ACCESS-KEY': apikey,
											'ACCESS-TIMESTAMP': timestamp,
											'ACCESS-SIGN': sign,
											'Content-Type': 'application/json',
											'User-Agent': 'Mozilla/5.0'
												})


		# # responseの初期値を取得する。
		response = 0

                # HTTPとかタイムアウト時の処理
		try:            
			with urllib.request.urlopen(req,timeout=7) as res:
				response = res.read().decode("utf-8")
		except:
			self.utilClass.loggingError(traceback.format_exc())


		
		# ERRORの場合はreturnする。
		if response == 0:
			return returnDict

		# パースする。
		json_dict = json.loads(response)

		# returnする辞書を調整する。
		returnDict = {}
		if len(json_dict) == 0:
			returnDict['resultCode'] = 0
			returnDict['resultNum'] = 0
			return returnDict

		# 複数件取得用に対応
		returnDict['resultNum'] = 1
		returnDict['resultCode'] = 0
		returnDict['side'] = json_dict[0]['side']
		returnDict['price'] = json_dict[0]['price']
		returnDict['product_code'] = json_dict[0]['product_code']
		returnDict['size'] = 0
		for i in range(len(json_dict)):
			returnDict['size'] = returnDict['size'] + json_dict[i]['size']

		returnDict['swap_point_accumulate'] = json_dict[0]['swap_point_accumulate']
		returnDict['open_date'] = json_dict[0]['open_date']

		# 処理終了
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

		# へんきゃく
		return returnDict


	# 予約取消を行う
	def ebtcService(self,apikey,apisecret,id,cointype='FX_BTC_JPY'):
		methodname = sys._getframe().f_code.co_name
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		apitype = self.inifile.get('apitype','cancelchildorder')
		apiurl = self.inifile.get('url','futuredatabefore')	

                # パラメータの調整する。
		data = {}
		data['product_code'] = cointype
		data['child_order_id'] = id
		#url_values = urllib.parse.urlencode(data)
		url_values = json.dumps(data)
		
		# GETかPOSTか
		method = 'POST'
		timestamp = str(time.time())
		text = timestamp + method + apitype + str(url_values)

		sign = hmac.new(bytes(apisecret.encode('utf-8')), bytes(text.encode('utf-8')), hashlib.sha256).hexdigest()
		#sign = hmac.new(bytes(apisecret.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

		req = urllib.request.Request(apiurl + apitype,data=url_values.encode('utf-8'),headers={'ACCESS-KEY': apikey,
											'ACCESS-TIMESTAMP': timestamp,
											'ACCESS-SIGN': sign,
											'Content-Type': 'application/json',
											'User-Agent': 'Mozilla/5.0'
												})


		# # responseの初期値を取得する。
		response = 0

                # HTTPとかタイムアウト時の処理
		try:            
			with urllib.request.urlopen(req,timeout=7) as res:
				response = res.read().decode("utf-8")
		except:
			self.utilClass.loggingError(traceback.format_exc())


		
		# ERRORの場合はreturnする。
		if response == 0:
			return 0


		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
		# へんきゃく
		return 1


	# 新規注文を行う
	def tbkeService(self,apikey,apisecret,side,price,size,lossgain,cointype='FX_BTC_JPY'):
		methodname = sys._getframe().f_code.co_name
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)


		# 返却辞書を生成する。
		returnDict = {}
		returnDict['resultCode'] = 9

		apitype = self.inifile.get('apitype','sendchildorder')
		apiurl = self.inifile.get('url','futuredatabefore')	


		# 新規取引前にビットフライヤー が定める最小単位に繰り上げる
		size = round(size, 5)

                # パラメータの調整する。
		data = {}
		data['product_code'] = cointype		
		data['child_order_type'] = 'LIMIT'
		data['side'] = side
		data['size'] = size

		# 損切り/利益確定の場合はパラメーターを変更する。
		if lossgain == 1: #損切り
			#data['child_order_type'] = 'MARKET'
			data['minute_to_expire'] = 7
			data['price'] = price
		elif lossgain == 2: # 利確
			data['minute_to_expire'] = 6
			#data['child_order_type'] = 'MARKET'
			data['price'] = price
		else:
			data['price'] = price

		url_values = json.dumps(data)


		# GETかPOSTか
		method = 'POST'
		timestamp = str(time.time())
		text = timestamp + method + apitype + str(url_values)

		sign = hmac.new(bytes(apisecret.encode('utf-8')), bytes(text.encode('utf-8')), hashlib.sha256).hexdigest()

		req = urllib.request.Request(apiurl + apitype,data=url_values.encode('utf-8'),headers={'ACCESS-KEY': apikey,
											'ACCESS-TIMESTAMP': timestamp,
											'ACCESS-SIGN': sign,
											'Content-Type': 'application/json',
											'User-Agent': 'Mozilla/5.0'
												})


		# # responseの初期値を取得する。
		response = 0

                # HTTPとかタイムアウト時の処理
		try:            
			with urllib.request.urlopen(req,timeout=7) as res:
				response = res.read().decode("utf-8")
		except:
			self.utilClass.loggingError(traceback.format_exc())


		
		# ERRORの場合はreturnする。
		if response == 0:
			return returnDict


		# パースする。
		json_dict = json.loads(response)

		# returnする辞書を調整する。
		if len(json_dict) == 0:
			returnDict['resultCode'] = 1
			return returnDict
			

		# 成功した場合
		returnDict['resultCode'] = 0
		returnDict['child_order_acceptance_id'] = json_dict['child_order_acceptance_id']

		# オーダー履歴に登録
		insert_dict={}
		insert_dict['LOGIC_DEL_FLG']=0
		insert_dict['INS_PID']=self.pid
		insert_dict['UPD_PID']=self.pid
		insert_dict['ORDER_STS'] = '1'
		insert_dict['ORDER_PRICE'] = price
		insert_dict['ORDER_TYPE'] = '0' if side == 'SELL' else '1'
		insert_dict['ORDER_AMMOUNT'] = size
		insert_dict['ACCEPT_ID'] = returnDict['child_order_acceptance_id']
		self.daoClass.insert('ORDER_BITFLYER_T',insert_dict)


		# 終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

		# へんきゃく
		return returnDict


	# 証拠金履歴を取得する
	def cchrService(self,apikey,apisecret,datanum=100):
		methodname = sys._getframe().f_code.co_name
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)


		apitype = self.inifile.get('apitype','getcollateralhistory')
		apiurl = self.inifile.get('url','futuredatabefore')	

                # パラメータの調整する。
		data = {}
		data['count'] = datanum
		url_values = urllib.parse.urlencode(data)
		# GETかPOSTか
		method = 'GET'
		timestamp = str(time.time())
		text = timestamp + method + apitype + '?' + url_values

		sign = hmac.new(bytes(apisecret.encode('utf-8')), bytes(text.encode('utf-8')), hashlib.sha256).hexdigest()

		req = urllib.request.Request(apiurl + apitype + "?" + url_values,headers={'ACCESS-KEY': apikey,
											'ACCESS-TIMESTAMP': timestamp,
											'ACCESS-SIGN': sign,
											'Content-Type': 'application/json',
											'User-Agent': 'Mozilla/5.0'
												})


		# responseの初期値を取得する。
		response = 0

                # HTTPとかタイムアウト時の処理
		try:            
			with urllib.request.urlopen(req,timeout=7) as res:
				response = res.read().decode("utf-8")
		except:
			self.utilClass.loggingError(traceback.format_exc())


		
		# ERRORの場合はreturnする。
		if response == 0:
			return 0

		# パースする。
		json_dict = json.loads(response)

		# returnする辞書を調整する。
		returnList = []
		returnDict = {}
		if len(json_dict) == 0:
			returnDict['resultnum'] = 0
			return returnDict

		# 返却結果分ループする。
		for info in json_dict:
			returnList.append(info)

		returnDict['resultnum'] = 1
		returnDict['return_list'] = returnList

		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
		
		# へんきゃく
		return returnDict

	# 新規注文確定確認サービス
	def noccService(self,apikey,apisecret,cointype='FX_BTC_JPY',datanum=1):
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name

		# 開始ログ出力
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 返却オブジェクト生成
		returnDict = {}
		returnDict['resultCode'] = 9

		# DBに未確認オーダーがないか確認する
		queryresult = self.daoClass.selectQuery('','get_new_order')

		# 未確認オーダーがない場合は処理を続行する
		if len(queryresult) == 0:
			returnDict['resultCode'] = 0
			returnDict['msg'] = 'unconfirm order is not found'
			return returnDict

		# getchildorders
		apitype = self.inifile.get('apitype','getchildorders')
		apiurl = self.inifile.get('url','futuredatabefore')	

		# getexecutions
		apitype2 = self.inifile.get('apitype','getexecutions')


                # パラメータの調整する。
		data = {}
		data['product_code'] = cointype
		data['count'] = 2
		data['child_order_acceptance_id'] = queryresult[0][5]
		url_values = urllib.parse.urlencode(data)
		# GETかPOSTか
		method = 'GET'
		timestamp = str(time.time())
		text = timestamp + method + apitype + '?' + url_values
		text2 =  timestamp + method + apitype2 + '?' + url_values

		sign = hmac.new(bytes(apisecret.encode('utf-8')), bytes(text.encode('utf-8')), hashlib.sha256).hexdigest()
		sign2 = hmac.new(bytes(apisecret.encode('utf-8')), bytes(text2.encode('utf-8')), hashlib.sha256).hexdigest()
		#sign = hmac.new(bytes(apisecret.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

		req = urllib.request.Request(apiurl + apitype + "?" + url_values,headers={'ACCESS-KEY': apikey,
											'ACCESS-TIMESTAMP': timestamp,
											'ACCESS-SIGN': sign,
											'Content-Type': 'application/json',
											'User-Agent': 'Mozilla/5.0'
												})

		req2 = urllib.request.Request(apiurl + apitype2 + "?" + url_values,headers={'ACCESS-KEY': apikey,
											'ACCESS-TIMESTAMP': timestamp,
											'ACCESS-SIGN': sign2,
											'Content-Type': 'application/json',
											'User-Agent': 'Mozilla/5.0'
											})



		# 最大ループ回数を保持する。
		roopNum = 0
		maxLoop = 50


		# 確認が取れるまで繰り返す
		while(True):
			# # responseの初期値を取得する。
			response = 0
	
	                # HTTPとかタイムアウト時の処理
			try:            
				with urllib.request.urlopen(req,timeout=7) as res:
					response = res.read().decode("utf-8")
			except:
				self.utilClass.loggingError(traceback.format_exc())
	
			
			# ERRORの場合はreturnする。
			if response == 0:
				returnDict['resultCode'] = 9
				return returnDict
	
			# パースする。
			json_dict = json.loads(response)
	
	
			# returnする辞書を調整する。
			if len(json_dict) == 0:
				# 0 件の場合はまだ有効となっていないので再度実行する。
				self.utilClass.logging('[' + self.pid + '][' + methodname + '] again call because order is not valid' ,2)
				time.sleep(8)
				# ループ回数をインクリメントp
				roopNum = roopNum + 1

				# getchildorders に入っていないないか確認
				response = 0

				try:
					with urllib.request.urlopen(req2,timeout=7) as res:
						response = res.read().decode("utf-8")
				except:
					self.utilClass.loggingError(traceback.format_exc())

				# パース
				json_dict2 = json.loads(response)

				if len(json_dict2) != 0:
					# 返却を整える
					returnDict['resultCode'] = 1
					returnDict['resultNum'] = 1
					returnDict['id'] = json_dict2[0]['id']
					returnDict['child_order_id'] = json_dict2[0]['child_order_id']
					returnDict['side'] = json_dict2[0]['side']
					returnDict['price'] = json_dict2[0]['price']
					returnDict['size'] = json_dict2[0]['size']

					# DBの更新処理
					update_dict = {}
					update_dict['ORDER_STS'] = '0'
					where = "WHERE ORDER_ID = '%s'" % queryresult[0][0]
					self.daoClass.update('ORDER_BITFLYER_T',update_dict,where)
					self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
					return returnDict


				#  ループ回数がMaxRloopNumをkoeru
				if roopNum >= maxLoop:
					# 処理を返す
					update_dict = {}
					update_dict['ORDER_STS'] = '0'
					where = "WHERE ORDER_ID = '%s'" % queryresult[0][0]
					self.daoClass.update('ORDER_BITFLYER_T',update_dict,where)
					self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
					returnDict['resultCode'] = 2
					return returnDict

				time.sleep(8)
				continue
			returnDict['resultCode'] = 1
			returnDict['resultNum'] = 1
			returnDict['id'] = json_dict[0]['id']
			returnDict['child_order_id'] = json_dict[0]['child_order_id']
			returnDict['product_code'] = json_dict[0]['product_code']
			returnDict['side'] = json_dict[0]['side']
			returnDict['price'] = json_dict[0]['price']
			returnDict['size'] = json_dict[0]['size']
			returnDict['child_order_state'] = json_dict[0]['child_order_state']
	

			# DBの更新処理
			update_dict = {}
			update_dict['ORDER_STS'] = '0'
			where = "WHERE ORDER_ID = '%s'" % queryresult[0][0]
			self.daoClass.update('ORDER_BITFLYER_T',update_dict,where)

			self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
			# へんきゃく
			return returnDict
