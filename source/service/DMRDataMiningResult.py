#coding: utf-8
# 概要
# 教師あり学習のため答えデータを作成
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################

import itertools
from datetime import datetime
import math
import os
import configparser
import sys

class DMRDataMiningResult(object):
	
	# 初期化処理
	def __init__(self,pid):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPMONEYTRADE"]

		# iniconfigファイルを読み出す。
		condigPath = self.homeDir + 'conf'
		inifile = configparser.ConfigParser()
		inifile.read(condigPath + '/config.ini', 'UTF-8')
		self.inifile = inifile

		# 当サービスの機能IDを取得する。
		self.pid = __name__[0:3]

		# 呼び出し元も機能ID
		self.call_pid = pid

		# Utilクラスの初期化
		# 1時的に環境変数を追加する。
		sys.path.append(self.homeDir)
		from util import Util
		self.utilClass = Util.Util(self.pid)
		from dataBaseAccess import SELECTGET
		self.SELECT = SELECTGET.MySQLselect()
		from dataBaseAccess import Dao
		self.daoClass = Dao.Dao(pid)

	# メインメソッド
	def main(self,date_time):
		# 当メソッドの名前を取得する。
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging(self.pid + '/' + date_time + '/' + methodname ,0)

		# DB格納値のdictを予めに初期化
		insert_dict = {}
		insert_dict['LOGIC_DEL_FLG'] = 0
		insert_dict['INS_PID'] = self.pid + '_' + self.call_pid
		insert_dict['UPD_PID'] = self.pid + '_' + self.call_pid
		insert_dict['DATA_TIME'] = date_time
		

		# 過去のデータから各値を取得する。
		insert_dict = self.getDataByPostData(insert_dict)	

		# nullcheck
		insert_dict = self.nullcheck(insert_dict)

		# 取得した情報をinsertする。
		self.daoClass.DATA_MINING_RESULT_T_Insert(insert_dict)


	# 過去データを取得して各値を取得する。
	def getDataByPostData(self,insert_dict):
		# 基準日を取得する。
		condList = {}
		condDateTime = insert_dict['DATA_TIME'] # 条件日時分
		condList['plus1M'] = plus1M = self.utilClass.addDateTimeStr(condDateTime,0,0,1) # 1分後
		condList['plus2M'] = plus2M = self.utilClass.addDateTimeStr(condDateTime,0,0,2) # 2分後
		condList['plus3M'] = plus3M = self.utilClass.addDateTimeStr(condDateTime,0,0,3) # 3分後
		condList['plus4M'] = plus4M = self.utilClass.addDateTimeStr(condDateTime,0,0,4) # 4分後
		condList['plus5M'] = plus5M = self.utilClass.addDateTimeStr(condDateTime,0,0,5) # 5分後
		condList['plus6M'] = plus6M = self.utilClass.addDateTimeStr(condDateTime,0,0,6) # 6分後
		condList['plus7M'] = plus7M = self.utilClass.addDateTimeStr(condDateTime,0,0,7) # 7分後
		condList['plus8M'] = plus8M = self.utilClass.addDateTimeStr(condDateTime,0,0,8) # 8分後
		condList['plus9M'] = plus9M = self.utilClass.addDateTimeStr(condDateTime,0,0,9) # 9分後
		condList['plus10M'] = plus10M = self.utilClass.addDateTimeStr(condDateTime,0,0,10) # 10分後
		condList['plus15M'] = plus15M = self.utilClass.addDateTimeStr(condDateTime,0,0,15) # 15分後
		condList['plus20M'] = plus20M = self.utilClass.addDateTimeStr(condDateTime,0,0,20) # 20分後
		condList['plus30M'] = plus30M = self.utilClass.addDateTimeStr(condDateTime,0,0,30) # 30分後
		condList['plus60M'] = plus60M = self.utilClass.addDateTimeStr(condDateTime,0,0,60) # 60分後
		condList['plus2H'] = plus2H = self.utilClass.addDateTimeStr(condDateTime,0,2,0) # 2時間後
		condList['plus3H'] = plus3H = self.utilClass.addDateTimeStr(condDateTime,0,3,0) # 3時間後
		condList['plus4H'] = plus4H = self.utilClass.addDateTimeStr(condDateTime,0,4,0) # 4時間後
		condList['plus5H'] = plus5H = self.utilClass.addDateTimeStr(condDateTime,0,5,0) # 5時間後
		condList['plus6H'] = plus6H = self.utilClass.addDateTimeStr(condDateTime,0,6,0) # 6時間後
		condList['plus12H'] = plus12H = self.utilClass.addDateTimeStr(condDateTime,0,12,0) # 12時間後
		condList['plus18H'] = plus18H = self.utilClass.addDateTimeStr(condDateTime,0,18,0) # 18時間後
		condList['plus24H'] = plus24H = self.utilClass.addDateTimeStr(condDateTime,0,24,0) # 24時間後

		# 基準日のログ出力
		self.utilClass.logging('condtime is ..' + str(condList),2)

		# 1 . 1日分を取得する。
		where = ["WHERE COIN_TYPE = '02' AND DATA_TIME >= '%s'" % condDateTime,"AND DATA_TIME <= '%s'"% plus24H,
			" ORDER BY DATA_TIME ASC"]
		postData = self.SELECT.selectexe(where,'currency_t')
		
		# 1日分をループして各値取得する。
		# 事前処理
		ftp = 0 # 最終取引価格

		# 最大値系初期化
		high5M = 0
		high10M = 0
		high15M = 0
		high20M = 0
		high30M = 0
		high60M = 0
		high2H = 0
		high3H = 0
		high4H = 0
		high5H = 0
		high6H = 0
		high12H = 0
		high18H = 0
		high24H = 0
		low5M=10000000
		low10M=10000000
		low15M=10000000
		low20M=10000000
		low30M=10000000
		low60M=10000000
		low2H=10000000
		low3H=10000000
		low4H=10000000
		low5H=10000000
		low6H=10000000
		low12H=10000000
		low18H=10000000
		low24H=10000000
		for data in postData:
			# 最終取引価格取得
			if data[0] == condDateTime:
				ftp = data[1]
			if ftp == 0:# 基準時間と同時刻の最終鳥日価格が取得できない場合は処理しない。
				self.utilClass.logging(condDateTime + 'is skiped not to get lastprice' ,2)
				return False

			# 1分後までの処理
			if data[0] == plus1M:
				insert_dict['FTP_DIS_1MINUTE'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_1MINUTE'] = self.compareTo(data[1],ftp)		

			# 2分後までの処理
			if data[0] == plus2M:
				insert_dict['FTP_DIS_2MINUTE'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_2MINUTE'] = self.compareTo(data[1],ftp)

			# 3分後までの処理
			if data[0] == plus3M:
				insert_dict['FTP_DIS_3MINUTE'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_3MINUTE'] = self.compareTo(data[1],ftp)

			# 4分後までの処理
			if data[0] == plus4M:
				insert_dict['FTP_DIS_4MINUTE'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_4MINUTE'] = self.compareTo(data[1],ftp)

			# 5分後までの処理
			if data[0] == plus5M:
				insert_dict['FTP_DIS_5MINUTE'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_5MINUTE'] = self.compareTo(data[1],ftp)

			# 6分後までの処理
			if data[0] == plus6M:
				insert_dict['FTP_DIS_6MINUTE'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_6MINUTE'] = self.compareTo(data[1],ftp)

			# 7分後までの処理
			if data[0] == plus7M:
				insert_dict['FTP_DIS_7MINUTE'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_7MINUTE'] = self.compareTo(data[1],ftp)

			# 8分後までの処理
			if data[0] == plus8M:
				insert_dict['FTP_DIS_8MINUTE'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_8MINUTE'] = self.compareTo(data[1],ftp)

			# 9分後までの処理
			if data[0] == plus9M:
				insert_dict['FTP_DIS_9MINUTE'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_9MINUTE'] = self.compareTo(data[1],ftp)

			# 10分後までの処理
			if data[0] == plus10M:
				insert_dict['FTP_DIS_10MINUTE'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_10MINUTE'] = self.compareTo(data[1],ftp)


			# 1分から5分までの処理
			if data[0] <= plus5M:
				if high5M < data[1]:
					high5M = data[1]

				if low5M > data[1]:
					low5M = data[1]

			# 5分から10分までの処理
			if data[0] > plus5M and data[0] <= plus10M:
				if high10M < data[1]:
					high10M = data[1]

				if low10M > data[1]:
					low10M = data[1]


			# 15分後までの処理
			if data[0] > plus10M and data[0] <= plus15M:
				insert_dict['FTP_DIS_15MINUTE'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_15MINUTE'] = self.compareTo(data[1],ftp)

				if high15M < data[1]:
					high10M = data[1]

				if low15M > data[1]:
					low10M = data[1]


			# 20分後までの処理
			if data[0] > plus15M and data[0] <= plus20M:
				insert_dict['FTP_DIS_20MINUTE'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_20MINUTE'] = self.compareTo(data[1],ftp)

				if high20M < data[1]:
					high20M = data[1]

				if low20M > data[1]:
					low20M = data[1]


			# 30分後までの処理
			if data[0] > plus20M and data[0] <= plus30M:
				insert_dict['FTP_DIS_30MINUTE'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_30MINUTE'] = self.compareTo(data[1],ftp)
				if high30M < data[1]:
					high30M = data[1]

				if low30M > data[1]:
					low30M = data[1]




			# 60分後までの処理
			if data[0] > plus30M and data[0] <= plus60M:
				insert_dict['FTP_DIS_60MINUTE'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_60MINUTE'] = self.compareTo(data[1],ftp)

				if high60M < data[1]:
					high60M = data[1]

				if low10M > data[1]:
					low60M = data[1]

			# 2時間後までの処理
			if data[0] > plus60M and data[0] <= plus2H:
				insert_dict['FTP_DIS_2HOUR'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_2HOUR'] = self.compareTo(data[1],ftp)

				if high2H < data[1]:
					high2H = data[1]

				if low2H > data[1]:
					low2H = data[1]

			# 3時間後までの処理
			if data[0] > plus2H and data[0] <= plus3H:
				insert_dict['FTP_DIS_3HOUR'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_3HOUR'] = self.compareTo(data[1],ftp)

				if high3H < data[1]:
					high3H = data[1]

				if low3H > data[1]:
					low3H = data[1]

			# 4時間後までの処理
			if data[0] > plus3H and data[0] <= plus4H:
				insert_dict['FTP_DIS_4HOUR'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_4HOUR'] = self.compareTo(data[1],ftp)

				if high4H < data[1]:
					high4H = data[1]

				if low4H > data[1]:
					low4H = data[1]

			# 5時間後までの処理
			if data[0] > plus4H and data[0] <= plus5H:
				insert_dict['FTP_DIS_5HOUR'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_5HOUR'] = self.compareTo(data[1],ftp)

				if high5H < data[1]:
					high5H = data[1]

				if low5H > data[1]:
					low5H = data[1]

			# 6時間後までの処理
			if data[0] > plus5H and data[0] <= plus6H:
				insert_dict['FTP_DIS_6HOUR'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_6HOUR'] = self.compareTo(data[1],ftp)

				if high6H < data[1]:
					high6H = data[1]

				if low6H > data[1]:
					low6H = data[1]

			# 12時間後までの処理
			if data[0] > plus6H and data[0] <= plus12H:
				insert_dict['FTP_DIS_12HOUR'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_12HOUR'] = self.compareTo(data[1],ftp)

				if high12H < data[1]:
					high12H = data[1]

				if low12H > data[1]:
					low12H = data[1]

			# 18時間後までの処理
			if data[0] > plus12H and data[0] <= plus18H:
				insert_dict['FTP_DIS_18HOUR'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_18HOUR'] = self.compareTo(data[1],ftp)
				if high18H < data[1]:
					high18H = data[1]

				if low18H > data[1]:
					low18H = data[1]

			# 24時間後までの処理
			if data[0] > plus18H and data[0] <= plus24H:
				insert_dict['FTP_DIS_24HOUR'] = data[1] / ftp				
				insert_dict['FLG_UPDOWN_24HOUR'] = self.compareTo(data[1],ftp)
				if high24H < data[1]:
					high24H = data[1]

				if low24H > data[1]:
					low24H = data[1]



		insert_dict['LOW_5MINUTE'] = low5M / ftp
		insert_dict['LOW_10MINUTE'] = low10M / ftp 
		insert_dict['LOW_15MINUTE'] = low15M / ftp
		insert_dict['LOW_20MINUTE'] = low20M / ftp
		insert_dict['LOW_30MINUTE'] = low30M / ftp
		insert_dict['LOW_60MINUTE'] = low60M / ftp
		insert_dict['LOW_2HOUR'] = low2H / ftp
		insert_dict['LOW_3HOUR'] = low3H / ftp
		insert_dict['LOW_4HOUR'] = low4H / ftp
		insert_dict['LOW_5HOUR'] = low5H / ftp
		insert_dict['LOW_6HOUR'] = low6H / ftp
		insert_dict['LOW_12HOUR'] = low12H / ftp
		insert_dict['LOW_18HOUR'] = low18H / ftp
		insert_dict['LOW_24HOUR'] = low24H / ftp
		insert_dict['HIGH_5MINUTE'] = high5M / ftp
		insert_dict['HIGH_10MINUTE'] = high10M / ftp
		insert_dict['HIGH_15MINUTE'] = high15M / ftp
		insert_dict['HIGH_20MINUTE'] = high20M / ftp
		insert_dict['HIGH_30MINUTE'] = high30M / ftp
		insert_dict['HIGH_60MINUTE'] = high60M / ftp
		insert_dict['HIGH_2HOUR'] = high2H / ftp
		insert_dict['HIGH_3HOUR'] = high3H / ftp
		insert_dict['HIGH_4HOUR'] = high4H / ftp
		insert_dict['HIGH_5HOUR'] = high5H / ftp
		insert_dict['HIGH_6HOUR'] = high6H / ftp
		insert_dict['HIGH_12HOUR'] = high12H / ftp
		insert_dict['HIGH_18HOUR'] = high18H / ftp
		insert_dict['HIGH_24HOUR'] = high24H / ftp

		# オブジェクトを返却する。
		return insert_dict



	# 終了処理
	def finish(self):
		self.SELECT.closeConn()

	# インサート情報のnullチェック
	def nullcheck(self,dict):
		list = [
		'FTP_DIS_1MINUTE',
		'FTP_DIS_2MINUTE',
		'FTP_DIS_3MINUTE',
		'FTP_DIS_4MINUTE',
		'FTP_DIS_5MINUTE',
		'FTP_DIS_6MINUTE',
		'FTP_DIS_7MINUTE',
		'FTP_DIS_8MINUTE',
		'FTP_DIS_9MINUTE',
		'FTP_DIS_10MINUTE',
		'FTP_DIS_15MINUTE',
		'FTP_DIS_20MINUTE',
		'FTP_DIS_30MINUTE',
		'FTP_DIS_60MINUTE',
		'FTP_DIS_2HOUR',
		'FTP_DIS_3HOUR',
		'FTP_DIS_4HOUR',
		'FTP_DIS_5HOUR',
		'FTP_DIS_6HOUR',
		'FTP_DIS_12HOUR',
		'FTP_DIS_18HOUR',
		'FTP_DIS_24HOUR',
		'FLG_UPDOWN_1MINUTE',
		'FLG_UPDOWN_2MINUTE',
		'FLG_UPDOWN_3MINUTE',
		'FLG_UPDOWN_4MINUTE',
		'FLG_UPDOWN_5MINUTE',
		'FLG_UPDOWN_6MINUTE',
		'FLG_UPDOWN_7MINUTE',
		'FLG_UPDOWN_8MINUTE',
		'FLG_UPDOWN_9MINUTE',
		'FLG_UPDOWN_10MINUTE',
		'FLG_UPDOWN_15MINUTE',
		'FLG_UPDOWN_20MINUTE',
		'FLG_UPDOWN_30MINUTE',
		'FLG_UPDOWN_60MINUTE',
		'FLG_UPDOWN_2HOUR',
		'FLG_UPDOWN_3HOUR',
		'FLG_UPDOWN_4HOUR',
		'FLG_UPDOWN_5HOUR',
		'FLG_UPDOWN_6HOUR',
		'FLG_UPDOWN_12HOUR',
		'FLG_UPDOWN_18HOUR',
		'FLG_UPDOWN_24HOUR',
		'LOW_5MINUTE',
		'LOW_10MINUTE',
		'LOW_15MINUTE',
		'LOW_20MINUTE',
		'LOW_30MINUTE',
		'LOW_60MINUTE',
		'LOW_2HOUR',
		'LOW_3HOUR',
		'LOW_4HOUR',
		'LOW_5HOUR',
		'LOW_6HOUR',
		'LOW_12HOUR',
		'LOW_18HOUR',
		'LOW_24HOUR',
		'HIGH_5MINUTE',
		'HIGH_10MINUTE',
		'HIGH_15MINUTE',
		'HIGH_20MINUTE',
		'HIGH_30MINUTE',
		'HIGH_60MINUTE',
		'HIGH_2HOUR',
		'HIGH_3HOUR',
		'HIGH_4HOUR',
		'HIGH_5HOUR',
		'HIGH_6HOUR',
		'HIGH_12HOUR',
		'HIGH_18HOUR',
		'HIGH_24HOUR']
		for val in list:
			if val not in dict.keys():
				dict[val] = 9
			if dict[val] > 10:
				dict[val] = 9

		return dict


	# 2つの引数a,b -> a / (a + b)
	def getWariai(self,valueA,valueB):
		return valueA / (valueA + valueB)



	# 大小のフラグを整える。
	def compareTo(self,valA,valB):
		if valA > valB:
			return 1
		else:
			return 0
