#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Georgy Bunin"
__email__ = "bunin.co.il@gmail.com"

import os           # work with path
import sys
import getopt       # parsing commang line arguments
import mailbox      # work with mbox format
import email.utils
import pydoc        # print __doc__ as help (pydoc.render_doc(str, "Help on %s"))
import re
import base64
from email.header import decode_header

description = {}
currentFolder = {}

searchTypes = ('text', 'html', 'both')
currentSearchType = 'both'
outputFile = ''     # TODO: add parametr for merge logs
outputFolder = 'collect_emails_output'

def getFiles(path):
    """
        Recursive list files in a dir using Python    
        URL: http://mayankjohri.wordpress.com/2008/07/02/create-list-of-files-in-a-dir-tree/ 
    """
    global outputFolder
    global currentFolder

    fileList = []
    for root, subFolders, files in os.walk(path):
        for file in files:
            p = os.path.join(root,file)
            fileList.append( { "short" : p , "long" : os.path.abspath(p) } )

    currentFolder['output'] = os.path.join(os.path.dirname(os.path.abspath(path)), outputFolder)
    if not os.path.exists(currentFolder['output']):
        os.makedirs(currentFolder['output'])

    return tuple(fileList)

def printProperties(o, onlyKeys = True):
    """
        Enumerate an object's properties in Python
        http://stackoverflow.com/questions/1251692/how-to-enumerate-an-objects-properties-in-python
    """
    for property, value in vars(o).iteritems():
        if onlyKeys:
            print(property, ": ", value)
        else:
            print(property)

def to_bool(value):
    """
        Converts 'something' to boolean. Raises exception for invalid formats
           Possible True  values: 1, True, "1", "TRue", "yes", "y", "t"
           Possible False values: 0, False, None, [], {}, "", "0", "faLse", "no", "n", "f", 0.0, ...
        URL: http://stackoverflow.com/questions/715417/converting-from-a-string-to-boolean-in-python
    """
    if str(value).lower() in ("yes", "y", "true",  "t", "1"): return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"): return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))

def confirm(prompt_str="Confirm", allow_empty=True, default=True):
    """
        Python console prompt yes/no
        URL: http://log.brandonthomson.com/2011/01/python-console-prompt-yesno.html
    """
    fmt = (prompt_str, 'y', 'n') if default else (prompt_str, 'n', 'y')
    if allow_empty:
        prompt = '%s [%s]|%s: ' % fmt
    else:
        prompt = '%s %s|%s: ' % fmt

    while True:
        ans = raw_input(prompt).lower()

        if ans == '' and allow_empty:
            return default
        elif ans == 'y':
            return True
        elif ans == 'n':
            return False
        else:
            print('Please enter y or n.')

def getEmail(emailAsString):
    # for email in emailAsString.split(','):
    return emailAsString.split(',')

def get_multilingual_header(header_text, default="ascii"):
    if not header_text is None:
        try:
            headers = decode_header(header_text)
        except email.errors.HeaderParseError:
            return u"Error"

        try:
            header_sections = [unicode(text, charset if charset and charset!='unknown' else default, errors='replace') for text, charset in headers]
        except LookupError:
            header_sections = [unicode(text, default, errors='replace') for text, charset in headers]
            return u"".join(header_sections)
    else:
        return None

def ProccessMBOXFile(mbox_file, NeedConfirm=False):
    global currentFolder
    isConfirmed = True

    if NeedConfirm:
        isConfirmed = confirm("Do you want to analyse this file (" + mbox_file['short'] + ")?")

    if isConfirmed:
        print("Start analyse " + mbox_file['short'] + "...")  
        try:
            mbox = mailbox.mbox(mbox_file['long'])
            currentFolder['short'] = mbox_file['short']
            currentFolder['long'] = mbox_file['long']
            currentFolder['name'] = os.path.basename(mbox_file['long'])
        except Exception as e:        
            print(e) # raise e
            return False

        for message in mbox:
            AnalyseMessage(message)

    return isConfirmed

def InIgnore(message):
    # http://webdesign.about.com/od/multimedia/a/mime-types-by-content-type.htm
    IgnoreTypes = ('alternative', 'application', 'image', 'audio', 'video', 'x-world', 'delivery-status')
    if (message.get_params()):
        for param in message.get_params():
            for ignore_type in IgnoreTypes:
                if param[0].lower().find(ignore_type.lower()) > -1:
                        return True
    return False

def AnalyseMessage(message, processesMultipartMessages = []):
    MultipartMessages = processesMultipartMessages

    if type(message) == type([]) or type(message) == type(None):
        return

    contentType = message.get_content_type()
    if contentType == 'message/rfc822':
        AnalyseMessage(message.get_payload(), [])
        return
    
    if not InIgnore(message):

        if not (message.get_boundary() is None):
            MultipartMessages.append(message.get_boundary())

        ShowId = False
        if ShowId:
            if 'message-id' in message:
                print('Message-ID:', message['message-id'])

        EmailFields = ('Reply-To', 'Cc', 'Bcc', 'To', 'From') # 'In-Reply-To'
        EmailList = []

        m = ''
        if message.has_key('Return-Path'):
            m = message.get('Return-Path')
        else:
            if message.has_key('Received'):
                m = message.get('Received')
        for mail_from_message in getEmail(m):
            EmailList.append(mail_from_message)

        for field in EmailFields:
            if message.has_key(field):
                m = message.get(field)
                for mail_from_message in getEmail(m):
                    EmailList.append(mail_from_message)

        mailString = ""

        for single_email in EmailList:
            if len(single_email) > 0:
                mail_list = email.utils.parseaddr(single_email)

                str_list = []

                if type(mail_list[1]) != type(None):
                    if len(mail_list[0]) == 0:
                        str_list.append(mail_list[1])
                    elif mail_list[0][:-len(mail_list[0])+2] == '=?':
                        h = decode_header(mail_list[0]) 
                        # h = get_multilingual_header(mail_list[0])
                        if type(h) == type(None):
                            str_list.append(mail_list[0])
                        else:
                            try:
                                str_list.append( h[0][0].decode(h[0][1]).encode("utf-8") )
                            except Exception as e:
                                str_list.append(mail_list[0])
                            
                    else:
                        str_list.append(mail_list[0])

                    str_list.append(mail_list[1])
                    str_list.append(currentFolder['root'] + "." + currentFolder['name'])
                    str_list.append('\n')
                    mailString += '\t'.join(str_list)

        print(mailString)
        
        with open(os.path.join(currentFolder['output'], currentFolder['root'] + "." + currentFolder['name'] + ".dat"), "a") as myfile:
            myfile.write(mailString)

        with open(os.path.join(currentFolder['output'], currentFolder['root'] + "._all_.dat"), "a") as myfile:
            myfile.write(mailString)

        # ---------------------------------------------------------------------
        if (message.is_multipart()):
            for submessage in message.walk():
                needAnalyse = True

                if (submessage.is_multipart()):
                    needAnalyse = not (submessage.get_boundary() in MultipartMessages)

                if needAnalyse:
                    AnalyseMessage(submessage, MultipartMessages)
        # ---------------------------------------------------------------------


def main(argv):
    global currentFolder
    files = []
    needConfirm = False

    try:
        opts, args = getopt.getopt(argv,"hHs:a:p:")
        if not opts:
            print(description['short'])
    except getopt.GetoptError:
        print(description['short'])
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print(description['short']) 
            sys.exit()
        elif opt == '-H':
            print(description['long'])
            sys.exit()                    
        elif opt == '-p':
            files = getFiles(arg)
            currentFolder['root'] = os.path.basename(os.path.abspath(arg)) 
        elif opt == '-s':
            files = ({"short" : arg , "long" : os.path.abspath(arg)},)
            currentFolder['root'] = os.path.basename(os.path.abspath(arg)) 
        elif opt == '-a':
            needConfirm = not to_bool(arg)  # automatic = False => needConfirm = True
    
    for f in files:
        ProccessMBOXFile(f, needConfirm)

if  __name__ ==  "__main__":
    #global description
    description = {
    'short' :  
    """
    Collect emails from MBOX files.

    Usage: 
    $ python collect_emails.py.py [OPTIONS]
        [OPTIONS]
        -h\t- Show this help
        -H\t- Show step by step tutorial
        -a [True|False]\t- Automatic process all files (default = True)
        -m [True|False]\t- if true output to one file (default = False)
        -b [html|text|both]\t- Find emails addresses in text message, html message or both (default == both)
        -f\t- Path to folder with MBOX files
        -s\t- Single MBOX file

    Examples:
    $ collect_emails.py -s -d /path/to/folder
    """
    ,
    'sortDeprecated' : 
    """
        \t-s\t- Include all sub-folders
    """,
    'long' : 
    """
    Collect emails from MBOX files.

    Usage:
        1. Export your outllok folder to PST file (outlook.pst)

        2. Install libpst utils (http://www.five-ten-sg.com/libpst/)
            user@mac$ brew install libpst --pst2dii --with-python
            user@linux$ sudo apt-get install libpst4

        3. Convert PST file to MBOX with libpst utils
            $ cd path/to/outlook.pst
            $ mkdir outlook
            $ readpst -D -b -d ./outlook.log -o ./outlook outlook.pst
            [optional] $ tail -f outlook.log

        4. Collect all emails with collect_emails_from_mbox.py
            $ python collect_emails.py -s -d ./outlook
    """
    }
    
    main(sys.argv[1:])