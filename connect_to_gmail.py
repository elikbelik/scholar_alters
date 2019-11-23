# -*- coding: utf-8 -*-
"""
Open emails and aggregate them together
"""

from __future__ import print_function
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors as error


# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
]
CLIENTSECRETS_LOCATION = r'.\data\credentials.json'


def get_service(data_folder='.'):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_filename = os.path.join(data_folder,'token.pickle')
    if os.path.exists(token_filename):
        with open(token_filename, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENTSECRETS_LOCATION, SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(token_filename, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def ListMessagesWithLabels(service, user_id, label_ids=[]):
  """List all Messages of the user's mailbox with label_ids applied.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    label_ids: Only return Messages with these labelIds applied.

  Returns:
    List of Messages that have all required Labels applied. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate id to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id,
                                                 labelIds=label_ids,
                                                 pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except Exception as error:
    print ('An error occurred: %s' % error)
    
    
def GetLabelsId (service, user_id, label_names=[]):
    results = service.users().labels().list(userId=user_id).execute()
    labels = results.get('labels', [])
    
    label_ids = []
    for name in label_names:
        for label in labels:
            if label['name']==name:
                label_ids.append(label['id'])
    return label_ids


def GetMessage(service, user_id, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()

    #print('Message snippet: %s' % message['snippet'])

    return message
  except Exception as error:
    print ('An error occurred: %s' % error)



if __name__ == '__main__':
    # Call the Gmail API
    service = get_service()
    
    # Get all the messages with labels
    labels = GetLabelsId(service,'me',['Papers','UNREAD'])
    messages = ListMessagesWithLabels(service,"me",labels)
    print ('Found $d messages'%len(messages))
    
    
    
    
    
    