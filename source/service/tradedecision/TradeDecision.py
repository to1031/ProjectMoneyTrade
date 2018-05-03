#coding: utf-8
# 概要
# 取引判定サービスクラス
################ 変更履歴 ######################
## 2017/09/13 作成
###############################################

import itertools
from datetime import datetime
import math
import os
import configparser
import sys

class TradeDecision(object):
	# 初期化処理
	def __init__(self,pid,util,dao,mail):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPMONEYTRADE"]

		self.inifile = util.inifile

		# 当サービスの機能IDを取得する。
		self.pid = 'TDC'

		# 呼び出し元も機能ID
		self.called_pid = pid

		# util dao を静的に
		self.utilClass = util
		self.daoClass = dao
		self.MASSClass = mail


	# 証拠金更新サービス
	def gchuService(self,dict):
		# 当メソッドの名前を取得する。
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 取引履歴を取得する。
		result = self.daoClass.selectQuery('','get_COLLATERAL_BITFLYER_T')
		
		idList = [ info[0] for info in result]

		# 返却IF用辞書を準備
		resultIFdict = {}
		resultIFdict['updata'] = 0

		# 辞書をループして処理する。
		for dictinfo in dict:
			if dictinfo['id'] in idList:
				# 既に格納さているのでコンティニュー
				continue

			# 新しい取引履歴なので格納する。
			# 返却IFを整える。
			resultIFdict['updata'] = 1
			resultIFdict['updatedict'] = dictinfo

			# insert_dict
			insert_dict = {}
			insert_dict['LOGIC_DEL_FLG'] = 0
			insert_dict['INS_PID'] = self.pid
			insert_dict['UPD_PID'] = self.pid
			insert_dict['HIS_ID'] = dictinfo['id']
			insert_dict['CURRENT_PRICE'] = dictinfo['amount']
			insert_dict['CHANGE_PRICE'] = dictinfo['change']
			insert_dict['REASON_CODE'] = dictinfo['reason_code']
			insert_dict['EXE_TIME'] = self.utilClass.convertJapaneseTime(dictinfo['date'])

			# DBインサート
			self.daoClass.insert('COLLATERAL_BITFLYER_T',insert_dict)


		# 処理終了のログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

		# 返却IFをreruenする
		return resultIFdict




	# 予約取引取消判定サービス
	def btcdService(self,resultftpg,resultebtr,resultevtr,resultdnns):
		# 返却辞書を生成する。
		returnDict = {}
		returnDict['resultCode'] = 9
		returnDict['orderCancelFlg'] = 0

		# メソッド名を取得する
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 予約取引判定に必要な情報を取得する。
		endTradePrice = resultftpg['endTradePrice'] # 現在の価格
		orderside = resultebtr['side'] # 既存予約のサイド
		orderprice = resultebtr['price'] # 既存予約の価格
		ordersize = resultebtr['size'] # 既存予約のサイズ
		dnnsigmoid = resultdnns['predict'] # sigmoidの機械学習結果

		# 設定ファイルから必要な情報を取得する
		canceldistance = 10000 * float(self.inifile.get('tradedicition','canceldistance'))

		# 機械学習結果から上がるか1、下がるか2、微妙か判断する
		updownFlg = self.hanteibyMLtobtcd(resultdnns)['updownflg']

		# キャンセル判定に追加フラグを初期化
		canceldistanceFlg = None
		positionFlg = None

		# 現在価格と予約価格の差額がcanceldistanceより大きい場合 取引を取り消す
		if abs(endTradePrice - orderprice) > canceldistance:
			canceldistanceFlg = 1

		# 予約ポジションが売り and  機会学習結果が上がりそうな場合　or
		# 予約ポジションが買い and  機会学習結果が下がりそうな場合　は 取引予約を取り消し
		if updownFlg == 1 and orderside == 'SELL':
			positionFlg = 1
		elif updownFlg == 2 and orderside == 'BUY':
			positionFlg = 1

			
		if resultevtr['resultNum'] == 0: # 既存有効取引がない場合
			if canceldistanceFlg == 1 or positionFlg == 1:
				returnDict['orderCancelFlg'] = 1

		else: # 既存有効取引がある場合
			self.utilClass.logging('has a valid trade so order is not canceled',2)					

		# 処理終了のログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)


		# 正常を格納する
		returnDict['resultCode'] = 0
		return returnDict



	# 新規取引判定
	def ntrdService(self,resultftpg,resultdnns):
		# 返却辞書を生成する。
		returnDict = {}
		returnDict['resultCode'] = 9
		returnDict['newOrderFlg'] = 0

		# メソッド名を取得する
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 予約取引判定に必要な情報を取得する。
		endTradePrice = resultftpg['endTradePrice'] # 現在の価格
		dnnsigmoid = resultdnns['predict'] # sigmoidの機械学習結果

		# 設定ファイルから必要な情報を取得する
		newtradedistance = 10000 * float(self.inifile.get('tradedicition','newtradedistance'))
		newordersize = 1 * float(self.inifile.get('tradedicition','newordersize'))

		# 機械学習結果から上がるか1、下がるか2、微妙か判断する
		updownFlg = self.hanteibyMLtobtcd(resultdnns)['updownflg']

		# 機械学習結果によって挙動を決める。
		if updownFlg == 1:
			returnDict['side'] = 'BUY'
			returnDict['size'] = newordersize
			returnDict['price'] = endTradePrice
			returnDict['newOrderFlg'] = 1
		elif updownFlg == 2:
			returnDict['side'] = 'SELL'
			returnDict['size'] = newordersize
			returnDict['price'] = endTradePrice
			returnDict['newOrderFlg'] = 1
		elif updownFlg == 0:
			returnDict['newOrderFlg'] = 0


		# 処理終了のログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

		# 正常を格納する
		returnDict['resultCode'] = 0
		return returnDict


	# 損切/利益確定判定
	# 引数1 現在価格取得サービス結果
	# 引数2 既存有効取引サービス結果
	# 引数3 機械学習(sigmoid)サービス結果
	# 戻り値 辞書型
	def lptdService(self,resultftpg,resultevtr,resultdnns):
		# 返却辞書を生成する。
		returnDict = {}

		# メソッド名を取得する
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 損切利益判定に必要な情報を取得する。
		endTradePrice = resultftpg['endTradePrice'] # 現在の価格
		side = resultevtr['side'] # 既存有効取引のサイド
		price = resultevtr['price'] # 既存有効取引の価格
		size = resultevtr['size'] # 既存有効取のサイズ
		dnnsigmoid = resultdnns['predict'] # sigmoidの機械学習結果

		# 設定ファイルから必要な情報を取得する
		constantLoss = 10000 * float(self.inifile.get('tradedicition','constantloss')) # 損切価格の定数

		# デフォルト損切
		defaultlosscut = 0
		if abs(endTradePrice - price) > constantLoss:
			defaultlosscut = 1


		# 機械学習結果から上がるか1、下がるか2、微妙か判断する
		updownFlg = self.hanteibyMLtolptd(resultdnns)['updownflg']

		# 各種フラグの初期化
		ftpCompareToPrice = 0 # 最終取引価格の方が大きい → 1
		posision = 0 # 売り → 1

		# 最終取引価格と既存有効取引の価格の比較
		if endTradePrice >= price:
			ftpCompareToPrice = 1
		else:
			ftpCompareToPrice = 0

		# 売りかどうかのポシション
		if side == 'SELL':
			posision = 1
		else:
			posision = 0

		

		# 各種フラグから利確/損切判定を実施する。
		returnDict = self.lossOrGainHantei(updownFlg,ftpCompareToPrice,posision,defaultlosscut)
		returnDict['resultCode'] = 0


		# 判定結果と現在価格、既存価格の差から損きり判定する。
		if returnDict['executeflg'] == 1:
			returnDict['price'] = endTradePrice
			returnDict['size'] = size


		# 処理終了のログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

		# 正常を格納する
		return returnDict

	# エラー管理
	def ercrService(self,type,className = None,service = None,msg = None,remark = None):
		# 返却辞書を生成する。
		returnDict = {}

		# メソッド名を取得する
		methodname = sys._getframe().f_code.co_name
		
		# ログ出力
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)
		
		# typeで挿入処理を行うかどうか判断する。
		if type != '00':
			# errorのデータベース挿入を行う
			insert_dict={}
			insert_dict['LOGIC_DEL_FLG']=0
			insert_dict['INS_PID']=self.pid+'_'+self.called_pid
			insert_dict['UPD_PID']=self.pid+'_'+self.called_pid
			insert_dict['ERROR_TYPE'] = type 
			insert_dict['ERROR_CLASS'] = className
			insert_dict['ERROR_SERVICE'] = service
			insert_dict['ERROR_MSG'] = msg
			insert_dict['REMARK_MEMO'] = remark
			self.daoClass.insert('TRADE_ERROR_BITF_T',insert_dict)

			dict = {}
			if int(type[0:1]) > 5:
				if type[0:1] == 6:
					# システムトレード中止メールを送信する
					dict['subject']='システムトレード中止通知'
					body=['新規オーダー確認にて確認が取れなかったので一旦中止します。']
					body.append('確認が取れたら再開(スタート)命令をお願いします')

				else:
					# システムトレード中止メールを送信する
					dict['subject']='システムトレード中止通知'
					body=['システムトレードにて重大なエラーが発生したため中止します']

			else:
				if type[0:1] == 2:
					# システムトレード再開メールを送信する
					dict['subject']='システムトレード再開通知'
					body=['受信メールによりシステムトレードを再開します']
					body.append('再開に起因した情報を記載いたします')
				else:
					# システムトレード失敗メールを送信する
					dict['subject']='システムトレード失敗通知'
					body=['システムトレードにてエラーが発生ししました']
					body.append('中止にしませんが詳細情報を送付いたします。')

			body.append('▼詳細情報')
			body.append('発生クラス：'+className)
			body.append('発生サービス：'+service)
			body.append('ERRORメッセージ：'+msg)
			dict['body'] = body
			self.MASSClass.massService(dict)				


		# データベースから最大のERROR情報を取得する
		result = self.daoClass.selectQuery('','get_error_new')

		# 取得した結果を返却辞書に格納
		if len(result) == 0:
			returnDict['resultCode'] = 1
			return result

		returnDict['resultCode'] = 0
		returnDict['id'] = result[0][0]
		returnDict['type'] = result[0][1]
		returnDict['msg'] = result[0][2]

		# 処理終了
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

		# 返却
		return returnDict


	# 状況確認
	def stscService(self,data_time,resultebtr,resultevtr):
		# 返却辞書を生成する。
		returnDict = {}

		# メソッド名を取得する
		methodname = sys._getframe().f_code.co_name
		
		# ログ出力
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 前回の状況を照会する。
		queryresult = self.daoClass.selectQuery('','get_trade_sts_bit')

		# DB挿入値を確定
		insert_dict={}
		insert_dict['LOGIC_DEL_FLG']=0
		insert_dict['INS_PID']=self.pid
		insert_dict['UPD_PID']=self.pid
		insert_dict['DATA_TIME']=data_time

		# メール送信サービスを呼び出す。
		dict = {}
		dict['subject']='システムトレード状況通知'
		body = ['システムトレードの状況を通知します。']
		body.append('状況取得実行時間:' + self.utilClass.convertStrToDateTime(data_time))
		body.append('-----前回通知時の状況-----')		
		if len(queryresult) != 0:
			body.append('前回取得実行時間:' + self.utilClass.convertStrToDateTime(queryresult[0][0]))
			body.append('■予約注文')
			#予約注文
			if queryresult[0][1] == '0':
				body.append(' 前回の予約注文はありません。')
			else:
				body.append(' 注文額：' + str(queryresult[0][2]))
				body.append(' 注文サイド：' + ('SELL' if queryresult[0][3] == 0 else 'BUY'))
				body.append(' 注文量：' + str(queryresult[0][4]))
				body.append(' 注文時刻：' + str(queryresult[0][5])[0:19])

			body.append('■有効取引')
			# 有効取引
			if queryresult[0][6] == '0':
				body.append(' 前回の有効取引はありません。')
			else:
				body.append(' 取引額：' + str(queryresult[0][7]))
				body.append(' 取引サイド：' + ('SELL' if queryresult[0][7] == 0 else 'BUY'))
				body.append(' 取引量：' + str(queryresult[0][9]))
				body.append(' 取引時刻：' + str(queryresult[0][10])[0:19])
		else:
			 body.append('前回の状況通知はありませんでした')

		body.append('-----現在の状況-----')
		body.append('■予約注文')
		if resultebtr['resultNum'] != 0:
			# DB格納値の更新
			insert_dict['ORDER_KBN'] = '1'
			insert_dict['ORDER_PRICE'] = resultebtr['price']
			insert_dict['ORDER_TYPE'] = '0' if resultebtr['side'] == 'SELL' else '1'
			insert_dict['ORDER_AMMOUNT'] = resultebtr['size']
			insert_dict['ORDER_TIME'] = self.utilClass.convertJapaneseTime(resultebtr['child_order_date'])

			# メール文の調整
			body.append(' 注文額：' + str(insert_dict['ORDER_PRICE']))
			body.append(' 注文サイド：' + resultebtr['side'])
			body.append(' 注文量：' + str(insert_dict['ORDER_AMMOUNT']))
			body.append(' 注文時刻：' + str(insert_dict['ORDER_TIME']))
			
		else:
			# DB格納値の更新
			insert_dict['ORDER_KBN'] = '0'

			# メール文の調整
			body.append(' 予約注文はありません。')

		body.append('■有効取引')
		if resultevtr['resultNum'] != 0:
			# DB格納値の更新
			insert_dict['POSITION_KBN'] = '1'
			insert_dict['POSITION_PRICE'] = resultevtr['price']
			insert_dict['POSITION_TYPE'] = '0' if resultevtr['side'] == 'SELL' else '1'
			insert_dict['POSITION_AMMOUNT'] = resultevtr['size']
			insert_dict['POSITION_TIME'] = self.utilClass.convertJapaneseTime(resultevtr['open_date'])

			# メール文の調整
			body.append(' 取引額：' + str(insert_dict['POSITION_PRICE']))
			body.append(' 取引サイド：' + resultevtr['side'])
			body.append(' 取引量：' + str(insert_dict['POSITION_AMMOUNT']))
			body.append(' 取引時刻：' + str(insert_dict['POSITION_TIME']))
			
		else:
			# DB格納値の更新
			insert_dict['POSITION_KBN'] = '0'

			# メール文の調整
			body.append(' 有効取引はありません。')


		dict['body'] = body
		self.MASSClass.massService(dict)

		# DBインサート
		self.daoClass.insert('TRADE_STS_BITFLYER_T',insert_dict)

		# 終了
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

		# 返却
		returnDict['resultCode'] = 0
		return returnDict

	################### ここの実装は見当が必要 ############################################
	################### ここの実装は見当が必要 ############################################
	################### ここの実装は見当が必要 ############################################
	################### ここの実装は見当が必要 ############################################
	# 新規取引判定
	def lossOrGainHantei(self,updownFlg,ftpCompareToPrice,posision,defaultlosscut):
		# 返却辞書を生成する。
		returnDict = {}
		returnDict['executeflg'] = 0 # 何もしない
		returnDict['side'] = 0
		returnDict['lossgain'] = 0 # 1:loss,2:gain 


		# 各種ロジックを組む
		# 1. 既存：高、既存ポジション：売、機械学習：上
		if ftpCompareToPrice == 0 and posision == 1 and updownFlg == 1:
			# 上がりそうなので利益確定する。
			returnDict['executeflg'] = 1
			returnDict['lossgain'] = 2
			returnDict['side'] = 'BUY'
			self.utilClass.logging('[' + self.pid + '] gain is being much will stop so gainorder' ,2)


		# 2. 既存：高、既存ポジション：売、機械学習：下
		elif ftpCompareToPrice == 0 and posision == 1 and updownFlg == 2:
			# まだまだ下がりそうなので待つ。
			self.utilClass.logging('[' + self.pid + '] gain is being much so dont anything' ,2)

		# 3. 既存：高、既存ポジション：買、機械学習：上
		elif ftpCompareToPrice == 0 and posision == 0 and updownFlg == 1:
			# デフォルト損切フラグ
			if defaultlosscut == 1:
				returnDict['lossgain'] = 1
				returnDict['executeflg'] = 1
				returnDict['side'] = 'SELL'
			else:
				# 損切りしたいが上がりそうなので待つ:
				self.utilClass.logging('[' + self.pid + '] loss is being decreasing so dont anything' ,2)


		# 4. 既存：高、既存ポジション：買、機械学習：下
		elif ftpCompareToPrice == 0 and posision == 0 and updownFlg == 2:
			# 損切りしないとやばいので損きりする。
			returnDict['lossgain'] = 1
			returnDict['executeflg'] = 1
			returnDict['side'] = 'SELL'
			self.utilClass.logging('[' + self.pid + '] loss is being much will dont stop so lossorder' ,2)

		# 5. 既存：低、既存ポジション：売、機械学習：上
		if ftpCompareToPrice == 1 and posision == 1 and updownFlg == 1:
			# 損切りしないとやばいので損きりする。
			returnDict['lossgain'] = 1
			returnDict['executeflg'] = 1
			returnDict['side'] = 'BUY'
			self.utilClass.logging('[' + self.pid + '] loss is being much will dont stop so lossorder' ,2)

		# 6. 既存：低、既存ポジション：売、機械学習：下
		elif ftpCompareToPrice == 1 and posision == 1 and updownFlg == 2:
			# デフォルト損切フラグ
			if defaultlosscut == 1:
				returnDict['lossgain'] = 1
				returnDict['executeflg'] = 1
				returnDict['side'] = 'BUY'
			else:
				# 下がりそうなので待つ。
				self.utilClass.logging('[' + self.pid + '] loss is being decreasing so dont anything' ,2)

		# 7. 既存：低、既存ポジション：買、機械学習：上
		elif ftpCompareToPrice == 1 and posision == 0 and updownFlg == 1:
			# デフォルト損切フラグ
			if defaultlosscut == 1:
				returnDict['lossgain'] = 1
				returnDict['executeflg'] = 1
				returnDict['side'] = 'BUY'
			else:
				# まだまだ上がりそうなので待つ:
				self.utilClass.logging('[' + self.pid + '] gain is being much so dont anything' ,2)

		# 8. 既存：低、既存ポジション：買、機械学習：下
		elif ftpCompareToPrice == 1 and posision == 0 and updownFlg == 2:
			# 下がりそうなので利益確定する。
			returnDict['lossgain'] = 2
			returnDict['executeflg'] = 1
			returnDict['side'] = 'SELL'
			self.utilClass.logging('[' + self.pid + '] gain is being much will stop so gainorder' ,2)


		# 返却する
		return returnDict










	################### ここの実装は見当が必要 ############################################
	################### ここの実装は見当が必要 ############################################
	################### ここの実装は見当が必要 ############################################
	################### ここの実装は見当が必要 ############################################
	# 機械学習結果から上がりそうか下がりそうか、微妙か判断する。
	def hanteibyMLtobtcd(self,resultdnns):
		# 返却辞書を生成する。
		returnDict = {}
		returnDict['updownflg'] = 0 # 判断できない
		#returnDict['updownflg'] = 1 上がる
		#returnDict['updownflg'] = 2 下がる

		# 仮実装
		if resultdnns['predict'] >= 0.48:
			returnDict['updownflg'] = 1
		elif resultdnns['predict'] <= 0.41:
			returnDict['updownflg'] = 2
		else:
			returnDict['updownflg'] = 0

		# 返却する
		return returnDict






	################### ここの実装は見当が必要 ############################################
	################### ここの実装は見当が必要 ############################################
	################### ここの実装は見当が必要 ############################################
	################### ここの実装は見当が必要 ############################################
	# 機械学習結果から上がりそうか下がりそうか、微妙か判断する。
	def hanteibyMLtolptd(self,resultdnns):
		# 返却辞書を生成する。
		returnDict = {}
		returnDict['updownflg'] = 0 # 判断できない
		#returnDict['updownflg'] = 1 上がる
		#returnDict['updownflg'] = 2 下がる

		# 仮実装
		if resultdnns['predict'] >= 0.4500000:
			returnDict['updownflg'] = 1
		elif resultdnns['predict'] <= 0.45:
			returnDict['updownflg'] = 2
		else:
			returnDict['updownflg'] = 0

		# 返却する
		return returnDict


