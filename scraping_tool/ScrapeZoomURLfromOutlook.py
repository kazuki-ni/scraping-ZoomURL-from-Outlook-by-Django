# モジュールのインポート
import win32com.client
import pythoncom
import datetime
import pytz
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
    return str(folder) in ['Inbox', 'inbox', '受信トレイ', 'INBOX']


# 本文に'zoom.us'のhttpアドレスを含むメールのみTrueを返す関数
def contains_zoom(mail):
    body = mail.body
    return 'zoom.us' in body and 'http' in body


# ミーティング参加に関係のないURLは弾く
def exclude_url(url):

    # Zoomの公式サイト関係のURL
    pattern_public = [
        "https://zoom.us/",
        "https://zoom.us/support/download",
        "https://zoom.us/test"
        ]

    # 「カレンダーに追加」系のURL
    pattern_calender_1 = 'zoom.us/meeting/attendee/[\w/:%#\$&\?\(\)~\.=\+\-]+type='
    pattern_calender_2 = 'zoom.us/webinar/[\w/:%#\$&\?\(\)~\.=\+\-]+type='

    # ミーティング登録キャンセルのURL
    pattern_cancel_1 = 'zoom.us/meeting/register/[\w/:%#\$&\?\(\)~\.=\+\-]+act=cancel'
    pattern_cancel_2 = 'zoom.us/webinar/register/[\w/:%#\$&\?\(\)~\.=\+\-]+act=cancel'

    # 国際通話用ダイヤルイン番号ページへのURL
    pattern_dial = 'zoom.us/u/\w+'

    # まとめる
    patterns = re.compile('{}|{}|{}|{}|{}'.format(
        pattern_calender_1,
        pattern_calender_2,
        pattern_cancel_1,
        pattern_cancel_2,
        pattern_dial
    ))

    # 除外処理
    if url in pattern_public:
        return False
    elif patterns.search(url):
        return False
    else:
        return True


# zoomのリンクを抽出する関数
def extract_url(body):
    
    # すべてのurlを抽出
    url_pattern = 'https://[\.\-\w]*zoom.us/[\w/:%#\$&\?\(\)~\.=\+\-]+'
    temp_url_list = list(set(re.findall(url_pattern, body)))

    # 以下のURLは弾く
    url_list = list(filter(exclude_url, temp_url_list))

    # URLを"|"で接続（DBにはリスト型は入らないため、URLに使われない'|'で結合）
    urls = '|'.join(url_list)

    return urls


# メール本文を整える
def format_body(body):

    # <URL>を削除
    pattern = '<https??://[\w/:%#\$&\?\(\)~\.=\+\-]+>'
    modified_body = re.sub(pattern, '', body)

    # \r\nを'|'に置換（HTML表示するときに消えてしまうため）
    modified_body = modified_body.replace('\r\n', '|')

    return modified_body


# テーブルへ入力
def input_table(mails):

    # データセットの作成
    data_set = []

    # zoomアドレスを含むメール１通ごとの内容をテーブルに書き込む
    for mail in mails:

        # 受信日をdatetime(aware)型に変型（このやり方の方がdateutil.parserより速い）
        temp_t = str(mail.ReceivedTime).partition('+')[0].partition('.')[0]
        received_time = datetime.datetime.strptime(temp_t, "%Y-%m-%d %H:%M:%S").astimezone(pytz.utc)

        mail_body = mail.body

        # zoomのURLのかたまりを取り出す
        url_list = extract_url(mail_body)

        # メール本文を成形する
        mail_body = format_body(mail_body)

        # エラー処理
        try:            
            # INSERT
            data = Mail(
                sender = str(mail.sender).split("<")[-1].split('>')[0],     # 両側の<>をあれば取る
                sender_email_address = mail.senderEmailAddress,
                received_time = received_time,
                url_list = url_list,
                body = mail_body
                )
            data_set.append(data)

        except:
            print("Cannot Insert {}".format(mail.subject))
    
    # いっきにmodelに入力
    Mail.objects.bulk_create(data_set)


# 一連の処理をscrape()にまとめる
def scrape(sf, su):

    scrape_from = datetime.datetime(sf.year, sf.month, sf.day, 0, 0, 0)
    scrape_until = datetime.datetime(su.year, su.month, su.day, 0, 0, 0)

    # これがないとerrorが出る
    pythoncom.CoInitialize()

    outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')

    # メールアドレスごとに処理
    for address in outlook.Folders:

        # 受信フォルダを選択
        inbox = list(filter(choose_inbox, address.Folders))[0]
        
        # zoomアドレスを持つメールを集計
        items = choose_period(inbox.Items, scrape_from, scrape_until)
        zoom_mails = list(filter(contains_zoom, items))

        # テーブルに入力
        input_table(zoom_mails)

