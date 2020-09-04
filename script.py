import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
import mimetypes



# If modifying these scopes, delete the file token.pickle.
#SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES = ['https://mail.google.com/']


def get_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    return service
def send_message(service, user_id, message ):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print('message ID: {}'.format(message['id']))
        return message
    except Exception as e:
        print('an error occured: {}'.format(e))
    pass

def create_message_with_attachment(sender, to, subject, body, file):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    msg = MIMEText(body)
    message.attach(msg)

    (content_type, encoding) = mimetypes.guess_type(file)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'

    (main_type, sub_type) = content_type.split('/', 1)

    if main_type == 'text':
        with open(file, 'rb') as f:
            msg = MIMEText(f.read().decode('utf-8'), _subtype=sub_type)

    elif main_type == 'image':
        with open(file, 'rb') as f:
            msg = MIMEImage(f.read(), _subtype=sub_type)

    elif main_type == 'audio':
        with open(file, 'rb') as f:
            msg = MIMEAudio(f.read(), _subtype=sub_type)

    else:
        with open(file, 'rb') as f:
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(f.read())


    filename = os.path.basename(file)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    raw_msg = base64.urlsafe_b64encode(message.as_string().encode('utf-8'))

    return {'raw': raw_msg.decode('utf-8')}

if __name__ == '__main__':
    service = get_service()
    user_id = 'me'
    sender = 'apitestproject123@gmail.com'
    to = '	iamlouis972@gmail.com'
    subject = 'IMPORTANT: do not delete (just kidding)'
    body = "Copied: I am cool and Python is useful"
    file = 'sample.txt'

    msg = create_message_with_attachment(sender, to, subject, body, file)
    send_message(service, user_id, msg)