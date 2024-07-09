import os
import base64
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pymongo import MongoClient
from datetime import datetime
from transformers import pipeline

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Initialize the sentiment analysis pipeline
sentiment_pipeline = pipeline(model="RashidNLP/Finance-Sentiment-Classification", verbose=False)

def get_next_serial_number(counter_collection):
    counter_doc = counter_collection.find_one_and_update(
        {'_id': 'news_counter'},
        {'$inc': {'next_serial_number': 1}},
        upsert=True,
        return_document=True
    )
    if counter_doc is None:
        counter_collection.insert_one({'_id': 'news_counter', 'next_serial_number': 1})
        return 1
    return counter_doc['next_serial_number']

def fetch_google_alerts():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("D:/code/django/myworld/news/news/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    messages_data = []
    try:
        service = build("gmail", "v1", credentials=creds)
        query_string = 'from:googlealerts-noreply@google.com'
        response = service.users().messages().list(userId='me', q=query_string, labelIds=['INBOX']).execute()
        count = 0
        while 'messages' in response and count < 10:
            messages = response['messages']
            for message in messages:
                if count >= 10:
                    break
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                payload = msg.get('payload')
                headers = payload.get('headers')
                subject = next(header['value'] for header in headers if header['name'] == 'Subject')
                parts = payload.get('parts')
                if parts:
                    for part in parts:
                        if part['mimeType'] == 'text/html':
                            data = part['body'].get('data')
                            if data:
                                body = base64.urlsafe_b64decode(data).decode('utf-8')
                                soup = BeautifulSoup(body, 'html.parser')
                                for a_tag in soup.find_all('a', href=True):
                                    headline_text = a_tag.text.strip()
                                    if headline_text and all(phrase not in headline_text for phrase in
                                        ["Flag as irrelevant", "See more results", 
                                        "Edit this alert", "Unsubscribe", 
                                        "View all your alerts",
                                        "Receive this alert as RSS feed", 
                                        "Send Feedback"]) and headline_text:
                                        sentiment = sentiment_pipeline(headline_text)[0]
                                        messages_data.append({
                                            'subject': subject.replace('Google Alert - ', ''),
                                            'headline': headline_text,
                                            'sentiment': sentiment['label'],
                                            'sentiment_score': sentiment['score'],
                                            'timestamp': datetime.utcnow().isoformat()
                                        })
                count += 1
            if 'nextPageToken' in response and count < 10:
                page_token = response['nextPageToken']
                response = service.users().messages().list(userId='me', q=query_string, labelIds=['INBOX'], pageToken=page_token).execute()
            else:
                break
    except HttpError as error:
        print(f'An error occurred: {error}')
    return messages_data

def insert_into_mongo(data):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['local']
        collection = db['news']
        counter_collection = db['counters']
        new_data = []
        for news in data:
            existing_news = collection.find_one({'subject': news['subject'], 'headline': news['headline']})
            if not existing_news:
                news['_id'] = get_next_serial_number(counter_collection)
                new_data.append(news)
        if new_data:
            collection.insert_many(new_data)
        return new_data
    except Exception as e:
        print(f'An error occurred: {e}')
        return []

if __name__ == "__main__":
    messages_data = fetch_google_alerts()
    if messages_data:
        new_data = insert_into_mongo(messages_data)
        if new_data:
            print(f'Inserted {len(new_data)} new news items.')
        else:
            print('No new news items to insert.')
    else:
        print('No news data fetched.')
