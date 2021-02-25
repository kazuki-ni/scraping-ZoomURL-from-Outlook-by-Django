# モジュールのインポート
import datetime
import pytz
import re
import json
import os

from .models import *


# テーブルへ入力
def input_table(mails):

    # データセットの作成
    data_set = []

    # zoomアドレスを含むメール１通ごとの内容をテーブルに書き込む
    for mail in mails:

        # エラー処理
        try:            
            # INSERT
            data = Mail(
                sender = mail['sender'],     # 両側の<>をあれば取る
                sender_email_address = mail['sender_email_address'],
                received_time = mail['received_time'],
                url_list = mail['url_list'],
                body = mail['mail_body']
                )
            data_set.append(data)

        except:
            print("Cannot Insert {}".format(mail.subject))
    
    # いっきにmodelに入力
    Mail.objects.bulk_create(data_set)


# 一連の処理をscrape()にまとめる
def scrape_sample_data():

    json_path = os.path.join(os.path.dirname(__file__), 'static/scraping_tool/mail_data_set.json')
    json_open = open(json_path, 'r')
    zoom_mails = json.load(json_open)

    # テーブルに入力
    input_table(zoom_mails)

