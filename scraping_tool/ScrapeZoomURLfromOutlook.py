# モジュールのインポート
import win32com.client
import datetime
import re

from .models import *


# 集計区間内のメールを選ぶ関数（outlookのメールの並びが変なため、変な関数）
def choose_period(mails, scrape_from, scrape_until):

    mail_set = []

    for mail in list(mails)[:100]:

        try:   
            temp_t = str(mail.ReceivedTime).partition('+')[0].partition('.')[0]
            received_time = datetime.datetime.strptime(temp_t, "%Y-%m-%d %H:%M:%S")
            # 集計区間内に受信したメールを選択
            if scrape_from <= received_time <= scrape_until:
                mail_set.append(mail)

        except:
            # ReceivedTimeの変数を持たないメールは 弾く
            continue

    
    for mail in reversed(list(mails)[100:]):

        try:   
            temp_t = str(mail.ReceivedTime).partition('+')[0].partition('.')[0]
            received_time = datetime.datetime.strptime(temp_t, "%Y-%m-%d %H:%M:%S")
            # 集計区間内に受信したメールを選択
            if scrape_from <= received_time <= scrape_until:
                mail_set.append(mail)

        except:
            # ReceivedTimeの変数を持たないメールは弾く
            continue

        if received_time < scrape_from:
            break

    return mail_set


# 受信メールフォルダを選ぶ関数
def choose_inbox(folder):
    return str(folder) in ['Inbox', 'inbox', '受信トレイ']


# 本文に'zoom.us'のhttpアドレスを含むメールのみTrueを返す関数
def contains_zoom(mail):
    body = mail.body
    return 'zoom.us' in body and 'http' in body


# zoomのリンクを抽出する関数
def extract_url(body):
    
    # すべてのurlを抽出
    url_pattern = 'https://[\.\-\w]*zoom.us/[\w/:%#\$&\?\(\)~\.=\+\-]+'
    temp_url_list = list(set(re.findall(url_pattern, body)))

    # 以下のURLは弾く（ひとつのことが多いのでこのコード）
    url_list = filter(
        lambda u: u not in [
            "https://zoom.us/",
            "https://zoom.us/support/download",
            "https://zoom.us/test"
            ],
        temp_url_list
        )

    # URLを"|"で接続
    url_list = '|'.join(url_list)

    return url_list


# テーブルへ入力
def input_table(mails):

    # 作成クエリの配列
    data_set = []

    # zoomアドレスを含むメール１通ごとの内容をテーブルに書き込む
    for mail in mails:

        # 受信日をdatetime型に変型
        temp_t = str(mail.ReceivedTime).partition('+')[0].partition('.')[0]
        received_time = datetime.datetime.strptime(temp_t, "%Y-%m-%d %H:%M:%S")

        # zoomのURLのかたまりと個数を取り出す
        url_list = extract_url(mail.body)

        # エラー処理
        try:            
            # INSERT
            data = Mail(
                sender = str(mail.sender).split("<")[-1].split('>')[0],     # 両側の<>をあれば取る
                sender_email_address = mail.senderEmailAddress,
                received_time = received_time,
                url_list = url_list,
                body = re.sub("[\s]", '|', str(mail.body)).replace('。', '。|')
                )
            data_set.append(data)

        except:
            print("Cannot Insert {}".format(mail.subject))
    
    Mail.objects.bulk_create(data_set)


# 一連の処理をscrape()にまとめる
def scrape(sf, su):

    scrape_from = datetime.datetime(sf.year, sf.month, sf.day, 0, 0, 0)
    scrape_until = datetime.datetime(su.year, su.month, su.day, 0, 0, 0)

    import pythoncom
    pythoncom.CoInitialize()

    outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')
    
    # メールアドレスごとにアカウントを分ける
    accounts = outlook.Folders


    # メールアドレスごとに処理
    for account in accounts:

        # 受信メールフォルダを選択
        folders = account.Folders
        # 受信フォルダはひとつなのでリストの一つ目を選択
        inbox = list(filter(choose_inbox, folders))[0]
        
        # zoomアドレスを持つメールを集計
        all_items = inbox.Items
        items = choose_period(all_items, scrape_from, scrape_until)
        zoom_mails = list(filter(contains_zoom, items))

        # テーブルに入力
        input_table(zoom_mails)

