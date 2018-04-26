# coding: utf-8
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
	import MASSMailSendService
	from dataBaseAccess import SELECTGET
	from util import Util
	from util import JsonParse
	from forge import ForgeApi
	from dataBaseAccess import Dao

	# utilクラスのオブジェクト取得
	utilClass = Util.Util(pid)

	# Test対象クラスのインスタンスを生成する。
	MASSMailSendServiceClass = MASSMailSendService.MASSMailSendService(pid)


	# 送信メールのdict
	dict = {}
	dict['subject'] = '取引予約完了'
	body =  ['取引が完了しました。']
	body.append('▼詳細情報')
	dict['body'] = body


	# mainクラスを呼び出す。
	MASSMailSendServiceClass.massService(dict)




if __name__ == '__main__':
	main()
