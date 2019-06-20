import os
import sys
import argparse
import json
from shutil import rmtree
import re

import pypff

sys.setrecursionlimit(10000)
"""
pypff download and installation guide:
https://github.com/libyal/libpff/wiki/Building
Example of usage:
python2.7 extractMessagesFromPST.py --pst-file '/backup.pst' --output-dir 'test/'
"""
__author__ = 'Denis Candido'
__date__ = '20180406'
__version__ = 0.02
__description__ = 'Script used to extract messages from PST file to json format'

class MessageExtractor(object):
    def __init__(self, pst_file):
        opst = pypff.open(pst_file)
        self.root = opst.get_root_folder()

    def extract(self, out_dir):
        self._folderTraverse(self.root, out_dir)

    def _folderTraverse(self, base, out_dir, first=True):
        """
        The folderTraverse function walks through the base of the folder and scans for sub-folders and messages
        :param base: Base folder to scan for new items within the folder.
        :return: None
        """
        if first:
            self._writeMessages(base, out_dir)
            print(base.number_of_sub_messages)
        for folder in base.sub_folders:
            print(folder.number_of_sub_messages)
            if folder.number_of_sub_folders > 0:
                self._folderTraverse(folder, out_dir, first=False) # Call new folder to traverse:
            self._writeMessages(folder, out_dir)
            

    def _check_and_rename(self, file, add=0):
        original_file = file
        if add != 0:
            split = file.split(".")
            part1 = split[0] + "_" + str(add)
            file = ".".join([part1, split[1]])
        if os.path.isfile(file):
            add += 1
            file = self._check_and_rename(original_file, add=add)

        return file

    def _writeMessages(self, folder, out_dir):
        """
        The writeMessages function reads folder messages if present and write each message at the out_dir as
        a json file.
        :param folder: pypff.Folder object
        :return: None
        """
        for message in folder.sub_messages:
            message_dict = self._processMessage(message)
            json_file_name = out_dir + re.sub('\/', '', message_dict['subject']) + '.json'
            json_file_name = self._check_and_rename(json_file_name)
            with open(json_file_name, 'w') as f:
                json.dump(message_dict, f)

    def _processMessage(self, message):
        """
        The processMessage function processes multi-field messages to simplify collection of information
        :param message: pypff.Message object
        :return: A dictionary with message fields (values) and their data (keys)
        """
        return {
            "subject": message.subject,
            "sender": message.sender_name,
            "header": message.transport_headers,
            "body": message.plain_text_body,
            #"client_submit_time": message.client_submit_time,
            #"delivery_time": message.delivery_time,
            # "attachments": message.attachments,
            "conversation_topic": message.conversation_topic,
            "number_of_attachments": message.number_of_attachments
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__description__,
                                     epilog='Developed by ' + __author__ + ' on ' + __date__)
    parser.add_argument('--pst-file', dest="PST_FILE", type=str, help="PST File Format from Microsoft Outlook")
    parser.add_argument('--output-dir', dest="OUTPUT_DIR", type=str, help="Directory of output for message files.")
    args = parser.parse_args()

    output_directory = args.OUTPUT_DIR
    if os.path.isdir(output_directory):
        rmtree(output_directory)
    os.makedirs(output_directory)

    messageExtractor = MessageExtractor(args.PST_FILE)
    messageExtractor.extract(output_directory)

    print('Done.')