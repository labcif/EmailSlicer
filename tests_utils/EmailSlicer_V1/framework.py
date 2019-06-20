import sys
import os
import pypff
import email
import smtplib
from email import generator
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid
import struct
import utils
from multiprocessing import Pool, Manager, Process
import datetime
import sqlite3
import time
import re
import hashlib
from functools import partial
from email.parser import HeaderParser


def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)

    return d.hexdigest()


class EmailSlicer:

    def __init__(self, base, message_data, pst_name, folder_name):
        self.total_time = time.time()        
        print('Start')
        self.base = base
        self.message_data = message_data
        self.pst_name = pst_name
        self.folder_name = folder_name

        self.db = self.DataBase(md5sum(self.pst_name))


    def run(self):
        t1 = time.time()
        print('Initializing folder iteration')
        message_data = self._folder_iterator(self.base, self.message_data, self.pst_name, self.folder_name)
        print('Finished: ', time.time() - t1)

        utils.writers.graphviz_writer.prepare(message_data)

        # if it exists, replaces it
        self.db.replace()
        self.db.insert(message_data)        
        
        t2 = time.time()
        print('Starting message extraction')
        self._extract_all_messages_with_body(message_data)
        print('Finished: ', time.time() - t2)        

        t3 = time.time()
        print('Starting email extraction')
        self._extract_emails(message_data)
        print('Finished: ', time.time() - t3)
        
        t4 = time.time()
        print('Starting messages/folder and sender/count extraction')
        data = self._extract_folders_number_messages(message_data)
        header = ['Folder Name', 'Number of Content']
        self.Writer(utils.writers.csv_writer.folder_message_numbers, header, data)

        data = self._all_senders(message_data)
        header = ['Sender', 'Count']
        self.Writer(utils.writers.csv_writer.all_senders, header, data)
        print('Finished: ', time.time() - t4)

        print('Total Time: ', time.time() - self.total_time)


    def _extract_all_messages_with_body(self, message_data):
        process = Pool(processes=20)
        process.map(utils.writers.eml_writer.message_to_writer, message_data) #waits until the processes are free
        process.close()
        process.join()
        #process.apply_async(utils.writers.eml_writer.message_to_writer, message_data)
        #async_result.get() # gets the result from the async
    

    def _folder_iterator(self, base, message_data, pst_name, folder_name):
        for folder in base.sub_folders:
            
            if folder.number_of_sub_folders:
                message_data = self._folder_iterator(folder, message_data, pst_name, folder.name)
            
            message_data = self._check_messages(folder, message_data, pst_name, folder.name)
        
        return message_data


    def _check_messages(self, folder, message_data, pst_name, folder_name):
        for message in folder.sub_messages:
            message_dict = self._process_message(message)
            message_dict['pst_name'] = pst_name
            message_dict['folder_name'] = folder_name
            message_data.append(message_dict)
        
        return message_data


    def _process_message(self, message):
        attachments = []
        total_attachment_size_bytes = 0
        
        if message.number_of_attachments > 0:
            for i in range(message.number_of_attachments):
                total_attachment_size_bytes = total_attachment_size_bytes + (message.get_attachment(i)).get_size()
                attachments.append(((message.get_attachment(i)).read_buffer((message.get_attachment(i)).get_size())))#.decode('ascii', errors="ignore"))
        
        sender =  message.sender_name
        receiver = None
        
        if message.transport_headers:
            parser = HeaderParser()
            # has more information then message.sender_name  (EX: name and email)
            sender = parser.parsestr(message.transport_headers)['from'] 
            receiver = parser.parsestr(message.transport_headers)['to']
        
        # print all keys
        #print(parser.parsestr(message.transport_headers).keys()) 

        try:
            # encoding used by microsoft
            # makes it easier to read
            body = message.plain_text_body.decode('cp1252')
        except:
            # in case of error while decoding
            body = message.plain_text_body
            
        """
        if total_attachment_size_bytes > 0:
            print('with attach: \n', message.transport_headers)
        else:
            print('without attach: \n', message.transport_headers)
        """

        return {
            'subject': message.subject,
            'sender': sender,
            'receiver': receiver,
            'header': message.transport_headers,
            'body': body,
            'creation_time': message.creation_time,
            'submit_time': message.client_submit_time,
            'delivery_time': message.delivery_time,
            'attachment_count': message.number_of_attachments,
            'total_attachment_size': total_attachment_size_bytes,
            'attachments': attachments
        }


    def _extract_folders_number_messages(self, message_data):
        folder_name_dict = dict()
        for folder in message_data:
            folder_name = folder['folder_name']
        
            if not folder_name in folder_name_dict:
                folder_name_dict[folder_name] = 1
            else:
                folder_name_dict[folder_name] += 1
        
        return folder_name_dict


    def _all_senders(self, message_data):
        senders_out = list()
        for message in message_data:
        
            if message['sender']:
                senders_out.append(message['sender'])
        
        return senders_out
    

    def _messages_from_sender(self, message_data, sender):
        for message in message_data:
            if message['sender'] == sender:
                utils.writers.eml_writer.message_to_writer(message)
    
    def _messages_from_receiver(self, message_data, subject):
        for message in message_data:
            if message['receiver'] == subject:
                utils.writers.eml_writer.message_to_writer(message)


    def _messages_from_subject(self, message_data, subject):
        for message in message_data:
            if message['subject'] == subject:
                utils.writers.eml_writer.message_to_writer(message)


    def _extract_emails(self, message_data):
        process = Pool(processes=20)
        emails_list_list = process.map(utils.email_util.extract_emails, message_data)
        process.close()
        process.join()
        self._prepare_emails(emails_list_list)


    def _prepare_emails(self, emails_list_list):
        emails_without_duplicates = self._single_emails_list(emails_list_list)
        process = Pool(processes=8)
        process.map(utils.writers.txt_writer.all_email, emails_without_duplicates)
        process.close()
        process.join()

    def _single_emails_list(self, emails_list_list):
        emails_list = []
        list(map(emails_list.extend, emails_list_list))
        
        return sorted(set(emails_list), key=lambda x:emails_list.index(x))



    class Writer:

        def __init__(self, writer_type, header, data):
            self.writer = writer_type
            self.header = header
            self.data = data
            self._run()


        def _run(self):
            self.writer(self.header, self.data)
    


    class DataBase:

        def __init__(self, db_name):
            self.name = db_name
            

        def replace(self):
            if os.path.isfile(self.name + '.db'):
                self.drop()
            self.create()


        def create(self):
            utils.writers.sqlite_writer.create_tables(self.name)
        

        def drop(self):
            utils.writers.sqlite_writer.drop_tables(self.name)
            

        def insert(self, message_data):
            utils.writers.sqlite_writer.insert_tables(self.name, message_data)



if __name__ == "__main__":
    pst_file =  r'..\\EmailSamples\\projAutopsy.pst'
    #pst_file = r'..\\EmailSamples\\projautopsy2019@outlook.com.ost'
    #pst_file = r'..\\EmailSamples\\ipleiria.pst'
    #pst_file = r'..\\EmailSamples\\vkaminski_000_1_1_1.pst'
    
    open_pst = pypff.open(pst_file)
    
    root_folder = open_pst.get_root_folder()

    email_slicer = EmailSlicer(root_folder, [], **{'pst_name': pst_file, 'folder_name': 'root'})
    email_slicer.run()