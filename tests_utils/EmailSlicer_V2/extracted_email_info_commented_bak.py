#################################
#       Start of Imports        #
#################################

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

#################################
#        End of Imports         #
#################################



#################################
#   Start of global variables   #
#################################

# Structure to store data to be inserted inside the database
emails_with_sender_receiver = {}

# Example of the way the data will be stored
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


# Exit codes
ERROR_OS = -1
SUCCESS = -1

#################################
#    End of global variables    #
#################################



#################################
#      Start of functions       #
#################################

def process_file_extention(extention, file):
    # The process_file_extention function returns the correct funtion to process the given file
    # depending on it's file extention
    # :param file: full email path
    # :param erxtention: file extention

    # Check if extention if eml
    if extention == 'eml':

        # Returns function to process eml email 
        return process_eml(file)
    # There is no match
    else:
        # Returns string unknown if the extention is not known by the program
        return 'unknown'



def process_eml(file):
    # The process_eml function processes the information present in each email
    # populating the emails_with_sender_receiver with the need information
    # :param file: full email path

    # Calling global copy to modify
    global emails_with_sender_receiver

    # Parse file to be processed by mailparser
    mail = mailparser.parse_from_file(file)

    # Get email subject
    subject = mail.subject

    # Get email date
    date = mail.date

    # Populate global variable
    emails_with_sender_receiver[file] = [{
        'subject': subject,
        'date': date,
        'sender': {},
        'receiver': []
    }]

    # Get formated sender and insert it into the global variable 
    filter_sender(file, mail.from_)

    # Get formated receiver(s) and insert it into the global variable 
    filter_receiver(file, mail.to)

    # Insert data into the database
    db_insert_data('6d9c6ff3a7ce5ec7f9dd122b1b4fcf7b', emails_with_sender_receiver[file], file)



def filter_sender(file, sender_list):
    # The filter_sender function processes the a list of  given senders, formats the information
    # and insert it correctly inside the global variable
    # :param file: email with eml extention
    # :param sender_list: list with senders of teh given file

    # Calling global copy to modify
    global emails_with_sender_receiver

    # Get sender name
    sender_name = sender_list[0][0]
    
    # Check if sender_name has characters
    if not re.search('[a-zA-Z]', sender_name):
        
        # Set variable to NULL string meaning that the message it has not a sender name 
        sender_name = 'NULL'

    # Check is has email    
    search_email = re.findall(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', sender_list[0][1])
    
    
    # Initialize variable with NULL string 
    sender_email = 'NULL'

    # Check if there are any emails present in the sender list
    if len(search_email) == 1:
        
        # In case of an email present, change the variable with the email found 
        sender_email = search_email[0]

    try:
        # Insert the previous obtained data (sender_email and sender_name) in the global variable
        emails_with_sender_receiver[file][0]['sender'] = (
            {
                'email': sender_email,
                'name': sender_name
            }
        )
    except Exception as e:
        # Print error in case of one
        print('ERROR \'sender\': ', e)



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



def db_insert_data(db_name, data, email_path):
    # The db_inser_data function formats data and inserts it correctly into the database
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
    # The db_rebuild function checks whether or not the given database and acts accordingly
    # :param db_name: name of the database

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
    # The calculate_md5 function returns a md5 chechsum of the give file
    # :param file: file to calculate hash

    # Call md5 from hashlib
    hash_md5 = hashlib.md5()

    # Open file in binary read mode
    with open(file, 'rb') as f:
        
        # Read chunks of 4096 bytes sequntially
        for chunk in iter(lambda: f.read(4096), b''):
            
            # Feed the chunks to the md5 funtion
            hash_md5.update(chunk)
    
    # Return md5 hash of the given file
    return hash_md5.hexdigest()

#################################
#       End of functions        #
#################################



#################################
#        Start of main          #
#################################

if __name__ == "__main__":
    
    # Start time count in order to get program execution time
    start_time = time.time()
    print('Start')
    
    # Test file
    pst_file = r'../EmailSamples/ipleiria.pst'
    
    # Get md5 hash of given file
    db_name = calculate_md5(pst_file)
    
    # Rebuild database (drops if exists and creates)
    db_rebuild(db_name)

    # Get current operation system
    operation_system = os.name

    # Check current operation system
    if operation_system == 'nt':

        # Operation System: Windows
        # Set base output directory from previous email extraction
        rootdir = 'C:/Users/2151580/Documents/Projeto/EmailSlicer/EmailSlicer_V2/output_files'

    elif operation_system == 'posix':

        # Operation System: Linux (desktop)
        # Set base output directory from previous email extraction
        rootdir = '/mnt/c/Users/2151580/Documents/Projeto/EmailSlicer/EmailSlicer_V2/output_files/'

        # Operation System: Linux (laptop)
        # Set base output directory from previous email extraction
        #rootdir = '/home/nogueira/Documents/EmailSlicer/EmailSlicer_V2/output_files/'    

    else:
        
        # In case the Operation System is different
        print('[ERROR] Invalid operation system ({})! Exited...'.format(operation_system))
    
        # Exit program (code -1)
        exit(ERROR_OS)
    
    # Iterates previous base output directory
    for sub_directory, directories, files in os.walk(rootdir):

        # iterate files
        for _file in files:

            # Get full file path
            file_with_path = os.path.join(sub_directory, _file)
            
            # Get file name
            file_name = os.path.basename(_file) 
            
            # Get file extention
            file_extention = file_name.split('.')[1]

            # Check if file extention is supported
            result = process_file_extention(file_extention, file_with_path)

            # In case of unknown file format, skips to the next one
            if result == 'unknown':
                print('[ERROR] Unknown file extention (\'.{}\')!'.format(file_extention))

    # Program execution time
    end_time = time.time()
    execution_time = end_time = start_time
    print('Finished program: ', execution_time)    

    # Exit program (code 0)
    exit(SUCCESS)

#################################
#        Start of main          #
#################################