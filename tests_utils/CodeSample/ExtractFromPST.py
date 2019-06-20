import pypff
import email
import smtplib
import sys
from email import generator
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid
import struct
import csv
import re

def _folder_iterator(base, message_data, pst_name, folder_name):
    for folder in base.sub_folders:
        if folder.number_of_sub_folders:
            message_data = _folder_iterator(folder, message_data, pst_name, folder.name)
        message_data = _check_messages(folder, message_data, pst_name, folder.name)
    return message_data

def _check_messages(folder, message_data, pst_name, folder_name):
    for message in folder.sub_messages:
        message_dict = _process_message(message)
        message_dict['pst_name'] = pst_name
        message_dict['folder_name'] = folder_name
        message_data.append(message_dict)
    return message_data

def _process_message(message):
    attachments = []
    total_attachment_size_bytes = 0
    if message.number_of_attachments > 0:
        for i in range(message.number_of_attachments):
            total_attachment_size_bytes = total_attachment_size_bytes + (message.get_attachment(i)).get_size()
            attachments.append(((message.get_attachment(i)).read_buffer((message.get_attachment(i)).get_size())))#.decode('ascii', errors="ignore"))
    return {
        'subject': message.subject,
        'sender': message.sender_name,
        'header': message.transport_headers,
        'body': message.plain_text_body,
        'creation_time': message.creation_time,
        'submit_time': message.client_submit_time,
        'delivery_time': message.delivery_time,
        'attachment_count': message.number_of_attachments,
        'total_attachment_size': total_attachment_size_bytes,
        'attachments': attachments
    }


def _recreate_message_eml(message):
    # Create the base text message.
    msg = EmailMessage()
    msg['Subject'] = message['subject']
    msg['From'] = message['sender']
    #msg['To'] = message['']
    
    msg.set_content(message['body'].decode('utf-8'))
    #asparagus_cid = make_msgid()
    #    if message['attachment_count'] > 0:
    #        image = message['attachments'][0]
    #        msg.add_attachment(image, 'image', 'png')#, cid=asparagus_cid)
    
    file_name = message['subject']
    with open('extracted_emails/' + file_name + '.eml', 'w') as file:
        gen = generator.Generator(file)
        gen.flatten(msg)


def _extract_folders_number_messages(message_data):
    folder_name_dict = dict()
    for folder in message_data:
        folder_name = folder['folder_name']
        if not folder_name in folder_name_dict:
            folder_name_dict[folder_name] = 1
        else:
            folder_name_dict[folder_name] += 1
    return folder_name_dict

def writer(headers, output_data):
    with open('csv.csv', 'w') as outfile:
        # We use DictWriter instead of writer to write dictionaries to CSV.
        #w = csv.DictWriter(outfile, fieldnames=headers)#,extrasaction='ignore')
        w = csv.writer(outfile)#,dialect='excel')

        # Writerheader writes the header based on the supplied headers object
        try:
            #w.writeheader()
            w.writerow(headers)
        except TypeError:
            print('[-] Received empty headers...\n[-] Skipping writing output.')
            return
        
        for data in output_data.items():
            w.writerow(data)

def _extract_message(message_data, message_subject):
    for message in message_data:
        print(type(message['subject']))
        if message['subject'] == message_subject:
            _recreate_message_eml(message)

def extract_emails(message_data):
    match = re.findall(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', str(message_data))
    print(match)

if __name__ == "__main__":
    pst_file = r'../EmailSamples/account.pst' #account.pst'
    message_subject = sys.argv[1]

    open_pst = pypff.open(pst_file)
    root_folder = open_pst.get_root_folder()

    message_data = _folder_iterator(root_folder, [], **{'pst_name': pst_file, 'folder_name': 'root'})

    header = [
            'pst_name', 
            'folder_name', 
            'creation_time', 
            'submit_time', 
            'delivery_time',
            'sender', 
            'subject', 
            'attachment_count' , 
            'total_attachment_size'
        ]#, 'attachments']
    
    _extract_message(message_data, message_subject)
    extract_emails(message_data)
    """
    for message in message_data:
        if message['body']:
            _recreate_message_eml(message)
    extracted_folders = _extract_folders_number_messages(message_data)
    headers = ['Folder Name', 'Number of Content']
    writer(headers, extracted_folders)
    """
