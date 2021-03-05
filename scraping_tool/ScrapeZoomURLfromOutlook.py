# Import module
import win32com.client
import pythoncom
import datetime
import pytz
import re

from .models import *


# Find the index which between scrape_from & scrape_until by binary serach
def find_target_hint(mail_list, scrape_from, scrape_until):
    
    start_pos = 0
    end_pos = len(mail_list)

    while True:
        # Find an index of the center
        center = int((start_pos + end_pos)/2)

        # Shift the center if the mail does not have "ReceivedTime" property
        center = find_valid_center(center, mail_list)

        # Pick ReceivedTime of the mail and Format it to datetime type
        center_time = format_datetime(mail_list[center].receivedTime)

        if center_time < scrape_from:
            start_pos = center
        elif scrape_from <= center_time <= scrape_until:
            target_hint = center
            break
        else:
            end_pos = center

    return target_hint, start_pos, end_pos


# Format to datetime type
def format_datetime(t):
    temp_time = str(t).partition('+')[0].partition('.')[0]
    format_time = datetime.datetime.strptime(temp_time, "%Y-%m-%d %H:%M:%S").astimezone(pytz.utc)
    return format_time


# Shift the center if the mail does not have the ReceivedTime property
def find_valid_center(center, mail_list):
    while True:
        try:
            _ = mail_list[center].receivedTime
            return center
        except:
            center += 1


# Input to model
def input_to_model(mail_list, scrape_from, scrape_until):

    # Find the index to efficiently input to model
    target_hint, start_pos, end_pos = find_target_hint(mail_list, scrape_from, scrape_until)

    # Create a data box to input to model
    data_set = []

    # After target_hint
    for i in range(target_hint+1, end_pos):
        mail = mail_list[i]
        
        # Skip the mail whose body does not have a http address of 'zoom.us'
        body = mail.body
        if not ('zoom.us' in body and 'http' in body):
            continue

        # Skip the mail whose body does not have zoom URL
        url_list = extract_url(body)
        if url_list == '':
            continue

        try:   
            received_time = format_datetime(mail.receivedTime)

            # (target_hint) <= mails <= (scrape_until)
            if received_time <= scrape_until:
                # INSERT
                data = Mail(
                    sender = str(mail.sender).split("<")[-1].split('>')[0],     # Remove <>
                    sender_email_address = mail.senderEmailAddress,
                    received_time = received_time,
                    url_list = url_list,
                    body = format_body(body)
                    )
                data_set.append(data)

            else:
                break

        except:
            # Exclude the mails which does not have the "ReceivedTime" property
            pass

    # Before target_hint
    for i in range(target_hint, start_pos, -1):
        mail = mail_list[i]

        # Skip the mail whose body does not have a http address of 'zoom.us'
        body = mail.body
        if not ('zoom.us' in body and 'http' in body):
            continue

        # Skip the mail whose body does not have zoom URL
        url_list = extract_url(body)
        if url_list == '':
            continue

        try:   
            received_time = format_datetime(mail.receivedTime)
            # (scrape_from) <= mails <= (target_hint) 
            if scrape_from <= received_time:
                # INSERT
                data = Mail(
                    sender = str(mail.sender).split("<")[-1].split('>')[0],     # Remove <>
                    sender_email_address = mail.senderEmailAddress,
                    received_time = received_time,
                    url_list = url_list,
                    body = format_body(body)
                    )
                data_set.append(data)
            else:
                break

        except:
            # Exclude the mails which does not have the "ReceivedTime" property
            pass

    # Input to model at once
    Mail.objects.bulk_create(data_set)


# Choose only inbox folder
def choose_inbox(folder):
    return str(folder) in ['Inbox', 'inbox', '受信トレイ', 'INBOX']


# Exclude URLs that are not related to Zoom meeting participation
def exclude_url(url):

    # URL related to Zoom's official website
    pattern_public = [
        "https://zoom.us/",
        "https://zoom.us/support/download",
        "https://zoom.us/test"
        ]

    # "Add to calendar" URL
    pattern_calender_1 = 'zoom.us/meeting/attendee/[\w/:%#\$&\?\(\)~\.=\+\-]+type='
    pattern_calender_2 = 'zoom.us/webinar/[\w/:%#\$&\?\(\)~\.=\+\-]+type='

    # URL for canceling meeting registration
    pattern_cancel_1 = 'zoom.us/meeting/register/[\w/:%#\$&\?\(\)~\.=\+\-]+act=cancel'
    pattern_cancel_2 = 'zoom.us/webinar/register/[\w/:%#\$&\?\(\)~\.=\+\-]+act=cancel'

    # URL to the dial-in number page for international calls
    pattern_dial = 'zoom.us/u/\w+'

    # Summarize to one pattern set
    patterns = re.compile('{}|{}|{}|{}|{}'.format(
        pattern_calender_1,
        pattern_calender_2,
        pattern_cancel_1,
        pattern_cancel_2,
        pattern_dial
    ))

    # Exclusion processing
    if url in pattern_public:
        return False
    elif patterns.search(url):
        return False
    else:
        return True


# Extract zoom URLs
def extract_url(body):
    
    # Extract all URLs
    url_pattern = 'https://[\.\-\w]*zoom.us/[\w/:%#\$&\?\(\)~\.=\+\-]+'
    temp_url_list = list(set(re.findall(url_pattern, body)))

    # Exclude the following URLs
    url_list = list(filter(exclude_url, temp_url_list))

    # Connect URL with "|" 
    # List type cannot be included in DB, so join with'|' which is not used in URL
    urls = '|'.join(url_list)

    return urls


# Format the email body
def format_body(body):

    # Remove <URL>
    pattern = '<https??://[\w/:%#\$&\?\(\)~\.=\+\-]+>'
    modified_body = re.sub(pattern, '', body)

    # Replace these code with '|' or space to express the same condition in the template
    modified_body = modified_body.replace('\r\n', '|')
    modified_body = modified_body.replace('\n', '|')
    modified_body = modified_body.replace('\u3000', ' ')

    return modified_body


# Combine a series of processes into scrape()
def scrape(sf, su):

    scrape_from = datetime.datetime(sf.year, sf.month, sf.day, 0, 0, 0).astimezone(pytz.utc)
    scrape_until = datetime.datetime(su.year, su.month, su.day+1, 0, 0, 0).astimezone(pytz.utc)

    # Get an error without this
    pythoncom.CoInitialize()

    outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')

    # Process by email address
    for address in outlook.Folders:

        # Select an inbox folder
        inbox = list(filter(choose_inbox, address.Folders))[0]
        all_items = inbox.Items
        all_items.Sort("[ReceivedTime]", False)
    
        # Input to model
        input_to_model(all_items, scrape_from, scrape_until)
