import re

def extract_emails(message_data):
    match = re.findall(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', str(message_data))
    return match
