import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# SCOPES: read-only access to Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def get_threads(service, page_token) -> list:
    response = service.users().threads().list(
        userId='me',
        pageToken=page_token,
    ).execute()
    
    threads = response.get('threads', [])
    next_page_token = response.get('nextPageToken', None)
    return threads, next_page_token

def __get_thread_messages(service, thread_id) -> list:
    thread = service.users().threads().get(userId='me', id=thread_id, format='full').execute()
    messages = thread.get('messages', [])
    return messages
  
def subject_matches(message, subject_filter) -> bool:
    payload = message.get('payload', {})
    headers = payload.get('headers', [])
    for header in headers:
        if header['name'].lower() == 'subject':
            return subject_filter.lower() in header['value'].lower()
    return False
  
def fetch_filtered_messages_from_threads(service, threads: list, max_threads: int, subject_filter: str) -> list[list]:
  remaining_threads = max_threads
  result = []
  for thread in threads:
        messages = __get_thread_messages(service, thread['id'])  # Ensure messages are fetched
        if subject_filter and messages and len(messages) > 0:
            if not any(subject_matches(messages[0], subject_filter) for msg in threads):
                continue  # Skip this thread
        result.append(messages)
        remaining_threads -= 1
        if remaining_threads == 0:
            break
  return result