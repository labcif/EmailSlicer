import re
import sqlite3
import hashlib
import base64, quopri, re
import pkgutil
import os
import encodings
import mailparser
import email
import time
import db_opperations


# emails_with_sender_receiver = {
#       '../1.eml': 
#       [
#           'subject': mensagem, 
#           'date':: date, 
#           'sender':
#           {
#               'email': John Doe,
#               'name': john@email.com
#           },
#           receiver:   
#           [{
#               'email': Mary Jane,
#               'name': mary@email.com
#           },
#           {
#               'email': Rojer Watson,
#               'name': rojer@email.com
#           }],
#       }]
#   } 

emails_with_sender_receiver = {}

def text_to_encoded_words(text, charset, encoding):
    """
    text: text to be transmitted
    charset: the character set for text
    encoding: either 'q' for quoted-printable or 'b' for base64
    """
    byte_string = text.encode(charset)
    if encoding.lower() is 'b':
        encoded_text = base64.b64encode(byte_string)
    elif encoding.lower() is 'q':
        encoded_text = quopri.encodestring(byte_string)
    return "=?{charset}?{encoding}?{encoded_text}?=".format(
        charset=charset.upper(),
        encoding=encoding.upper(),
        encoded_text=encoded_text.decode('ascii'))

def encoded_words_to_text(encoded_words):
    print(encoded_words)
    encoded_word_regex = r'=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}='
    charset, encoding, encoded_text = re.match(encoded_word_regex, encoded_words).groups()
    if encoding is 'B':
        byte_string = base64.b64decode(encoded_text)
    elif encoding is 'Q':
        byte_string = quopri.decodestring(encoded_text)
    return byte_string.decode(charset)


# TODO: eml, msg, ics, vcf

def process_file_extention(extention, file):
    if extention == 'eml':
        return process_eml(file)
    else:
        return 'unknown'
    """
    # bugs code
    try: 
        return {
        #'ics': process_ics,
        'eml': process_eml,
        'vcf': process_vcf
        }.get(extention)(file)
    except:
        return 'unknown'
        #return func(*args)
        #available_extentions.get(extention, 'unknown')()
    """

def process_ics(file):
    lines = open(file,'r').readlines()
    for line in lines:
        print(line)
    
def all_encodings():
    modnames = set(
        [modname for importer, modname, ispkg in pkgutil.walk_packages(
            path=[os.path.dirname(encodings.__file__)], prefix='')])
    aliases = set(encodings.aliases.aliases.values())
    return modnames.union(aliases)

def process_eml(file):
    # eml_parser
    """
    import datetime
    import json
    import eml_parser


    def json_serial(obj):
        if isinstance(obj, datetime.datetime):
            serial = obj.isoformat()
            return serial

    t1 = time.time()
    with open(file, 'rb') as fhdl:
        raw_email = fhdl.read()

    parsed_eml = eml_parser.eml_parser.decode_email_b(raw_email)

    print(json.dumps(parsed_eml, default=json_serial))
    print('Finished eml: ', time.time() - t1)
    """

    #t2 = time.time()
    global emails_with_sender_receiver
    #print(file)
    mail = mailparser.parse_from_file(file)
    #msg = email.message_from_string(str(mail._message))
    #email_length =  len(msg.get_payload())
    #print('Sender: {}\n To: {}\n Subject: {}'.format(mail.from_, mail.to, mail.subject,))
    
    date = mail.date
    #print(date)
    # get sender

    subject = mail.subject
    emails_with_sender_receiver[file] = [{
        'subject': subject,
        'date': date,
        'sender': {},
        'receiver': []
    }]

    filter_sender(file, mail.from_)
    filter_receiver(file, mail.to)

    #print(emails_with_sender_receiver[file])
    db_insert_data('6d9c6ff3a7ce5ec7f9dd122b1b4fcf7b', emails_with_sender_receiver[file], file)


    #print(emails_with_sender_receiver[file])
    #print('Finished msg: ', time.time() - t2)
    #return 0
    # get receiver(s)
    #search_receivers(file_to_open, line, count)


def filter_sender(file, sender_list):
    global emails_with_sender_receiver
    #print(emails_with_sender_receiver)

    sender_name = sender_list[0][0]
    if not re.search('[a-zA-Z]', sender_name):
        sender_name = 'NULL'
    
    search_email = re.findall(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', sender_list[0][1])
    sender_email = 'NULL'
    if len(search_email) == 1:
        sender_email = search_email[0]

    try:
        emails_with_sender_receiver[file][0]['sender'] = (
            {
                'email': sender_email,
                'name': sender_name
            }
        )
    except Exception as e:
        print('ERROR \'sender\': ', e)
    
    #print(emails_with_sender_receiver[file])


def filter_receiver(file, receiver_list):
    global emails_with_sender_receiver

    for receiver in receiver_list:
        receiver_name = receiver[0]
        if not re.search('[a-zA-Z]', receiver_name):
            receiver_name = 'NULL'
        
        search_email = re.findall(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', receiver[1])
        receiver_email = 'NULL'
        if len(search_email) == 1:
            receiver_email = search_email[0]

        try:
            emails_with_sender_receiver[file][0]['receiver'].append(
                {                
                    'email': receiver_email,
                    'name': receiver_name
                }
            )
        except Exception as e:
            print('ERROR \'receiver\': ', e)
    #print(emails_with_sender_receiver[file])
    return 0


def process_vcf(file):
    pass


def db_insert_data(db_name, data, email_path):
    # The db_inser_data formats data and inserts it correctly into the database
    # :param db_name: name of the database
    # :param data: data to be fotmated
    # :email_path: path of the email

    # Get database connection
    connection = db_opperations.db_connection.open_connection(db_name)

    # Set sender
    sender = data[0]['sender']

    # Insert sender into tables: 
    #       - users
    #       - users_email
    # Get id from users table
    sender_user_id = db_opperations.db_insert.insert_user(connection, sender['email'], sender['name'])

    # Set subject
    subject = data[0]['subject']

    # Set location 
    location = email_path

    # Set date
    date = data[0]['date']    

    # Insert email into table: 
    #       - emails
    # Get id from emails table
    
    email_id = db_opperations.db_insert.insert_email(connection, subject, location, date)

    # Set receivers
    receivers = data[0]['receiver']

    # Check for more than one receiver
    if len(receivers) == 1:

        # Only one receiver
        # Set receiver
        receiver = receivers[0]
        
        # Insert receiver into tables: 
        #       - users
        #       - users_email
        # Get id from users table
        receiver_user_id = db_opperations.db_insert.insert_user(connection, receiver['email'], receiver['name'])

        # Inserts sender id,  receiver id and email id into table: 
        #       - relations
        db_opperations.db_insert.insert_relation(connection, email_id, sender_user_id, receiver_user_id)
    
    else:

        # More than one receiver
        # Set receiver
        for receiver in receivers:
    
            # Insert receiver into tables: 
            #       - users
            #       - users_email
            # Get id from users table
            receiver_user_id = db_opperations.db_insert.insert_user(connection, receiver['email'], receiver['name'])
            
            # Insert sender id, receiver id and email id into table: 
            #       - relations
            db_opperations.db_insert.insert_relation(connection, email_id, sender_user_id, receiver_user_id)

    # Close database connection
    db_opperations.db_connection.close_connection(connection)


def db_rebuild(db_name):

    # Get database connection
    connection = db_opperations.db_connection.open_connection(db_name)

    # Check if file exists 
    if os.path.isfile('output_files/' + db_name + '.db'):
        
        # Delete database table
        db_opperations.db_drop.drop_tables(connection)

    # Create database table
    db_opperations.db_create.create_tables(connection)

    # Close database connection
    db_opperations.db_connection.close_connection(connection)



def calculate_md5(file):
    hash_md5 = hashlib.md5()
    with open(file, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


if __name__ == "__main__":
    t = time.time()
    print('Start')
    # test function 'process_email'
    #file = '/home/nogueira/Documents/EmailSlicer/EmailSlicer_V2/output_files/ipleiria/Ficheiro de Dados do Outlook/Correio Eletrónico Não Solicitado/27.eml'
    #process_eml(file)
    #exit(0)
    #mail = mailparser.parse_from_file_msg(file)
    #mail = mailparser.parse_from_file(file)
    # Read EML
    #f = r'../EmailSamples/thunderbird.eml'
    #mail = mailparser.parse_from_file(f)

    #print(mail._message)
    #msg = email.message_from_string(str(mail._message))
    #email_length =  len(msg.get_payload())
    
    #print('Sender: {}\n To: {}\n Subject: {}\n Body{}'.format(mail.from_, mail.to, mail.subject, mail.message_as_string))
    #print('Sender: {}\n To: {}\n Subject: {}'.format(mail.from_, mail.to, mail.subject,))
    # Read Attachments
    #for attach in mail.attachments:
    #    print(attach)
    #exit(0)
    pst_file = r'../EmailSamples/ipleiria.pst'
    # Get md5 hash of given file
    db_name = calculate_md5(pst_file)
    
    # 
    db_rebuild(db_name)

    operation_system = os.name
    if operation_system == 'nt':
        rootdir = 'C:/Users/2151580/Documents/Projeto/EmailSlicer/EmailSlicer_V2/output_files'

    elif operation_system == 'posix':
        # desktop
        rootdir = '/mnt/c/Users/2151580/Documents/Projeto/EmailSlicer/EmailSlicer_V2/output_files/'
        # laptop
        #rootdir = '/home/nogueira/Documents/EmailSlicer/EmailSlicer_V2/output_files/'    
    else:
        print('[ERROR] Invalid operation system! Exited...')
        exit(-1)
    
    for sub_directory, directories, files in os.walk(rootdir):
        # iterate folders
        #for directory in directories:
        #    print(os.path.join(sub_directory, directory))            

        # iterate files
        for file in files:
            file_with_path = os.path.join(sub_directory, file)
            file_base_name = os.path.basename(file) 
            file_extention = file_base_name.split('.')[1]

            result = process_file_extention(file_extention, file_with_path)

            if result == 0:
                #print('First eml message!')
                print(emails_with_sender_receiver[file_with_path][0])

                #pass
                exit(0)

            #if result == 'unknown':
            #    print('[ERROR] Unknown file extention (\'.{}\')!'.format(file_extention))
    #print(emails_with_sender_receiver)
    print('Finished program: ', time.time() - t)    