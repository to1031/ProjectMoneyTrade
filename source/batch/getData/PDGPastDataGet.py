# codine: utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import sys
import os
import configparser
import urllib.request
import json

def main():
	# 環境変数を取得する。
	homeDir = os.environ["APPMONEYTRADE"]

	# log用の文字列準備
	pid = os.path.basename(__file__)[0:3] # 機能IDの取得

        # 1時的に環境変数を追加する。
	sys.path.append(homeDir)
	sys.path.append(homeDir)
	from initialize import Initialize

	# 初期化クラスのオブエクトか
	object_dict = {}
	object_dict['pid'] = pid
	Initializer = Initialize.Initialize(object_dict)

	# utilクラスのオブジェクト取得
	utilClass = Initializer.utilClass
	# daoクラスのオブジェクトを取得する。
	dao = Initializer.daoClass
	# メール送信クラスを取得する
	MASSClass = Initializer.MASSClass
	object_dict['util'] = utilClass
	object_dict['dao'] = dao
	object_dict['mass'] = MASSClass

	# jsonparseクラスのオブジェクト取得
	jsonClass = Initializer.class_ins('JsonParse',object_dict)

	# bitflyyerApiクラスを取得
	bitflyerClass = Initializer.class_ins('BitflyerApi',object_dict)

	# configファイルから情報を抜き出す.
	inifile = utilClass.inifile

	# 呼び出す仮想通貨の種類を洗い出す
	coinlist = utilClass.coinlistGet()
	cointype = utilClass.cointypeGet()

	# pueryの固定文字列をs￥抜き出す
	pueryStayStr = inifile.get('url','productcode')

	# 対象コインタイプを絞る
	targetcoin = coinlist[1]

	# 呼び出すAPIの種類を探す
	board = inifile.get('apitype','board')
	executions = inifile.get('apitype','executions')

	# apiurlを取得する。
	apiurl = inifile.get('url','futuredatabefore')

	# qyeryで空文字のやつを取得する。
	brankcoin = inifile.get('coin','nonpuery')

	# ファイルパスを取得する。
	outPath = inifile.get('filepath','inoutpath')

	# このバッチ処理の開始log
	utilClass.logging(pid,0)

	###################################
	# 104000000 start
	###################################
	# log
	logstr = ''
	logstr = 'call webAPI by ' + targetcoin
	utilClass.logging(logstr,0)
	lastNum = 1000000000000

	# 前回実行時間を取得する。
	f = open(homeDir + 'batch/getData/PDGEXE_NO.txt', "r")
	exetime = f.read()
	if exetime == '':
		utilClass.logging('before no is not found',2)
		return

	before = int(exetime)
	f.close()

	for i in range(lastNum):

		try:

			# ファイルパスを取得する。
			filepath = homeDir + outPath + 'executions_past' + '/'  + targetcoin

			puery = ''
			puery = pueryStayStr
	
			# webapiを呼び出す。
			josnStr = bitflyerClass.executions_pastApi(apiurl,targetcoin,puery,executions,before)

			# 取れなかった値を取得する。
			if josnStr == 0:
				utilClass.logging('can not get api is' + str(before),2)
				continue
		
			#ファイルを保存する。
			savaFile(josnStr,filepath)


			#filepath
			filepath = homeDir + outPath + 'executions_past' + '/' + targetcoin + '.json'

			# log
			logstr = ''
			logstr = 'read json by ' + filepath
			utilClass.logging(logstr,0)

			# ファイルの存在チェック
			if not os.path.exists(filepath):
				logstr = 'file not found:' + filepath
				utilClass.loggingError(logstr,before)
				continue

			# json読み込みとパース
			resultDict = jsonClass.executionsPostParse(filepath,'02')
			# デバッグ返却リストの数
			utilClass.logging('get datas num = ' + str(len(resultDict)) + 'by [' + str(before) + ']' ,2)
			# boradの挿入を行う。
			boardInsert(resultDict,pid,dao,before)

			# ファイルを消する。
			os.remove(filepath)

			# イン売り面と
			before = before + 99

		except:
			import traceback
			error_text = traceback.format_exc()
			utilClass.loggingError(error_text)
			utilClass.logging('except occurrd',2)
			f = open(homeDir + 'batch/getData/PDGEXE_NO.txt', "w")
			f.write(str(before))
			f.close()
			break

	# このバッチ処理の終了log
	utilClass.logging(pid,1)


# webapi取得結果の保存
def savaFile(jsonStr,path):
	# ファイルを保存する。
	f = open(path + ".json", "w")
	f.write(jsonStr)
	f.close()


# board結果の保存
def boardInsert(dict,pid,dao,before):
	
	for i in range(len(dict)):
		# DBinsert 
		if before - 99 > dict[i]['TRADE_ID']:
			continue
		dao.insert('BITFLYER_TRADE_HIS_T',dict[i])

if __name__ == '__main__':
	main()
