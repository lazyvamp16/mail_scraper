import os
import base64
from bs4 import BeautifulSoup
from django.http import JsonResponse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pymongo import MongoClient
from bson import ObjectId
import datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def fetch_google_alerts():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "D:/code/django/myworld/news/news/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    messages_data = []
    try:
        service = build("gmail", "v1", credentials=creds)
        query_string = 'from:googlealerts-noreply@google.com'
        response = service.users().messages().list(userId='me', q=query_string, labelIds=['INBOX']).execute()
        count = 0
        serial_index = 1
        while 'messages' in response and count < 10:
            messages = response['messages']
            for message in messages:
                if count >= 10:
                    break
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                payload = msg.get('payload')
                headers = payload.get('headers')

                # Find the subject of the email
                subject = next(header['value'] for header in headers if header['name'] == 'Subject')
                
                # Extract the body of the email
                parts = payload.get('parts')
                if parts:
                    for part in parts:
                        if part['mimeType'] == 'text/html':
                            data = part['body'].get('data')
                            if data:
                                body = base64.urlsafe_b64decode(data).decode('utf-8')

                                # Use BeautifulSoup to parse the HTML and extract headlines
                                soup = BeautifulSoup(body, 'html.parser')

                                # Find all <a> tags with relevant headlines
                                for a_tag in soup.find_all('a', href=True):
                                    headline_text = a_tag.text.strip()
                                    # Exclude headlines containing any of the specified phrases
                                    if headline_text and all(phrase not in headline_text for phrase in
                                         ["Flag as irrelevant", "See more results", 
                                          "Edit this alert", "Unsubscribe", 
                                          "View all your alerts",
                                          "Receive this alert as RSS feed", 
                                          "Send Feedback"]) and headline_text:
                                        # Add timestamp and serial index
                                        news_item = {
                                            'serial_index': serial_index,
                                            'subject': subject,
                                            'headline': headline_text,
                                            'timestamp': datetime.datetime.utcnow()
                                        }
                                        messages_data.append(news_item)
                                        serial_index += 1
                count += 1
                        
            if 'nextPageToken' in response and count < 10:
                page_token = response['nextPageToken']
                response = service.users().messages().list(userId='me', q=query_string, labelIds=['INBOX'], pageToken=page_token).execute()
            else:
                break

    except HttpError as error:
        return JsonResponse({'error': str(error)}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    # Convert MongoDB ObjectId to string for JSON serialization
    for message in messages_data:
        if '_id' in message:
            message['_id'] = str(message['_id'])

    return messages_data

def save_to_mongodb(messages_data):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['local']
        collection = db['news']
        collection.insert_many(messages_data)
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")

def get_headers(request):
    messages_data = fetch_google_alerts()
    save_to_mongodb(messages_data)
    return JsonResponse({'messages': messages_data})

if __name__ == "__main__":
    messages_data = fetch_google_alerts()
    save_to_mongodb(messages_data)
    print("Data fetched and inserted successfully.")
