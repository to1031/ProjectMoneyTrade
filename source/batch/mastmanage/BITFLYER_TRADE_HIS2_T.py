# coding: utf-8
# 


################ 変更履歴 ######################
## 2017/05/05 作成

###############################################

import itertools
import datetime
import math
import os
import sys

def main():
	# 環境変数を取得する。
	homeDir = os.environ["APPMONEYTRADE"]

	# log用の文字列準備
	pid = os.path.basename(__file__)[0:3] # 機能IDの取

        # 1時的に環境パスを追加する。
	sys.path.append(homeDir)
	from initialize import Initialize
	# 初期化クラスのオブエクトか
	object_dict = {}
	object_dict['pid'] = pid
	Initializer = Initialize.Initialize(object_dict)

	# utilクラスのオブジェクト取得
	utilClass = Initializer.utilClass
	# daoクラスのオブジェクトを取得する。
	daoClass = Initializer.daoClass
	# メール送信クラスを取得する
	MASSClass = Initializer.MASSClass
	object_dict['util'] = utilClass
	object_dict['dao'] = daoClass
	object_dict['mass'] = MASSClass

	# DBから処理年月日のリストを取得する。
	target = daoClass.selectQuery('','iko')

	# 同じexe_timeのばんめ
	count = 0
	exe_time = ''

	# 取得行数分処理する。
	for val in target:
		if exe_time != val[5]:
			count = 0
			count = count + 1


		# 処理対象の年月時分の情報を取得する。
		insert_dict = {}
		insert_dict['INS_PID'] = pid
		insert_dict['UPD_PID'] = pid
		insert_dict['LOGIC_DEL_FLG'] = '0'
		insert_dict['TRADE_ID'] = val[0]
		insert_dict['COIN_TYPE'] = val[1]
		insert_dict['TRADE_TYPE'] = val[2]
		insert_dict['TRADE_AMMOUNT'] = val[3]
		insert_dict['FINAL_TRADE_PRICE'] = val[4]
		insert_dict['EXEC_DATE'] = calc_exe_time(val[5],val[6],count)
		daoClass.insert('BITFLYER_TRADE_HIS2_T',insert_dict)

		count = count + 1
		exe_time = val[5]


def calc_exe_time(date_time,num,count):
	format = '%Y%m%d%H%M%S'
	minutes = round((60 / num) * count,0)
	if minutes >= 60:
		minutes = 59.99

	minute_str = str(minutes)[0:2]
	if '.' in minute_str:
		minute_str = '0' + minute_str[0:1]

	date_time = date_time + minute_str
	print(date_time)
	date_time = datetime.datetime.strptime(date_time, format)
	return date_time







if __name__ == '__main__':
	main()
