import os.path

import email
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.http import HttpResponse

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]



def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "D:/code/django/myworld/news/news/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    #results = service.users().labels().list(userId="me").execute()
    
    q_str = 'TATA'
    resultado = service.users().messages().list(userId= 'me',q=q_str,labelIds= ['INBOX']).execute()
    mensajes = resultado.get('messages', [])
    print ("Mensaje:")
    for mensaje in mensajes[:1]:
        leer = service.users().messages().get(userId='me', id=mensaje['id']).execute()
        payload = leer.get("payload")
        header = payload.get("headers")
        for x in header:
            if x['name'] == 'subject':
                sub = x['value'] #subject
                print(sub)
        print(leer['snippet'])  #body


    #https://gmail.googleapis.com/gmail/v1/users/{userId}/messages/{id}
    
    #labels = results.get("labels", [])
    #labels = results.get("messages", [])

    #if not labels:
    #  print("No labels found.")
    #  return
    #print("Labels:")
    #for label in labels:
    #  print(label["name"])

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")



def hi (request):
  return HttpResponse("hi")   


def getheaders (request) :

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
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  r_str = []
  try:    
    service = build("gmail", "v1", credentials=creds)
    #results = service.users().labels().list(userId="me").execute()    
    q_str = 'Gold'
    resultado = service.users().messages().list(userId= 'me',q=q_str,labelIds= ['INBOX']).execute()
    mensajes = resultado.get('messages', [])
    print ("Response1:")
    
    for mensaje in mensajes[:1]:
        leer = service.users().messages().get(userId='me', id=mensaje['id']).execute()
        payload = leer.get("payload")
        header = payload.get("headers")
        for x in header:
            if x['name'] == 'subject':
                sub = x['value'] #subject
                print(sub)
               # r_str.append(sub)
                print('r_str')               
        print(leer['snippet'])
        r_str.append(leer['snippet'])

  except HttpError as error:  
    print(f"An error occurred: {error}")
    r_str = r_str + error
  return HttpResponse(r_str)




if __name__ == "__main__":
  main()