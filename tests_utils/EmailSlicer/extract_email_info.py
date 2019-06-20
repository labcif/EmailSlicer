#################################
#       Start of Imports        #
#################################

import re
import sqlite3
import hashlib
import base64
import quopri
import re
import pkgutil
import os
import encodings
import mailparser
import email
import time
import db_opperations
import writers
import datetime

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

date_dict = {x:0 for x in range(1, 25)}
date_list = [date_dict.copy() for x in range(7)]

# Exit codes
SUCCESS = 0
ERROR_OS = -1

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


def process_eml(_file):
    # The process_eml function processes the information present in each email
    # populating the emails_with_sender_receiver with the need information
    # :param file: full email path

    # Calling global copy to modify
    global emails_with_sender_receiver

    # Parse file to be processed by mailparser
    mail = mailparser.parse_from_file(_file)

    # Get email subject
    subject = mail.subject

    # Get date
    date = mail.date

    # Build heat map based on email message received time
    build_heat_map(_file, date)

    # Get email date in epoch time
    date_epoch = get_epoch_unix_time(mail.date)

    # Populate global variable
    emails_with_sender_receiver[_file] = [{
        'subject': subject,
        'date': date_epoch,
        'sender': {},
        'receiver': []
    }]

    # Get formated sender and insert it into the global variable
    filter_sender(_file, mail.from_)

    # Get formated receiver(s) and insert it into the global variable
    filter_receiver(_file, mail.to)

    # Insert data into the database
    db_insert_data('6d9c6ff3a7ce5ec7f9dd122b1b4fcf7b', emails_with_sender_receiver[_file], _file)


def build_heat_map(_file, date):

    # Calling global copy to modify
    global date_list

    try:
        # Received time
        day_of_week = date.weekday()
        hour_of_day = date.hour + 1
        date_list[day_of_week][hour_of_day] += 1
    except:
        print('[ERROR] File \'{}\' file has no received date!'.format(_file))


def get_epoch_unix_time(date_time):
    epoch = datetime.datetime.utcfromtimestamp(0)

    try:
        date_epoch = (date_time - epoch).total_seconds()
    except:
        date_epoch = 'NULL'
    finally:
        return date_epoch


def get_date_time(date_epoch):
    try:
        date_time = datetime.datetime.fromtimestamp(
            date_epoch).strftime('%Y-%m-%d %H:%M:%S')  # .strftime('%c')
    except:
        date_time = 'NULL'
    finally:
        return date_time


def filter_sender(_file, sender_list):
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

        # Set variable to NULL string meaning that the message doensn't have a sender name
        sender_name = 'NULL'

    # Check for email
    search_email = re.findall(
        r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', sender_list[0][1])

    # Initialize variable with NULL string
    sender_email = 'NULL'

    # Check if there are any emails present in the sender list
    if len(search_email) == 1:

        # In case of an email present, change the variable with the email found
        sender_email = search_email[0]

    try:
        # Insert the previous obtained data (sender_email and sender_name) in the global variable
        emails_with_sender_receiver[_file][0]['sender'] = (
            {
                'email': sender_email,
                'name': sender_name
            }
        )
    except Exception as exeption:

        # Print error in case of one
        print('ERROR \'sender\': ', exeption)


def filter_receiver(_file, receiver_list):
    # The filter_receiver function processes the a list of given receivers, formats the information
    # and insert it correctly inside the global variable
    # :param file: email with eml extention
    # :param receiver_list: list with receivers of teh given file

    # Calling global copy to modify
    global emails_with_sender_receiver

    # Case where there are no receivers comes empty
    if receiver_list == []:

        # Set both receiver email and name to NULL string
        receiver_email = 'NULL'
        receiver_name = 'NULL'

        try:
            # Insert the previous obtained data (receiver_email and receiver_name) in the global variable
            emails_with_sender_receiver[_file][0]['receiver'].append(
                {
                    'email': receiver_email,
                    'name': receiver_name
                }
            )
        except Exception as exeption:

            # Print error in case of one
            print('ERROR \'receiver\': ', exeption)

    # Iterate over each receiver
    for receiver in receiver_list:

        # Get receiver name
        receiver_name = receiver[0]

        # Check if sender_name has characters
        if not re.search('[a-zA-Z]', receiver_name):

            # Set variable to NULL string meaning that the message doensn't have a receiver name
            receiver_name = 'NULL'

        # Check for email
        search_email = re.findall(
            r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', receiver[1])

        # Initialize variable with NULL string
        receiver_email = 'NULL'

        # Check if there are any emails present in the sender list
        if len(search_email) == 1:

            # In case of an email present, change the variable with the email found
            receiver_email = search_email[0]

        try:
            # Insert the previous obtained data (receiver_email and receiver_name) in the global variable
            emails_with_sender_receiver[_file][0]['receiver'].append(
                {
                    'email': receiver_email,
                    'name': receiver_name
                }
            )
        except Exception as exeption:

            # Print error in case of one
            print('ERROR \'receiver\': ', exeption)


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
    sender_user_id = db_opperations.db_insert.insert_user(
        connection, sender['email'], sender['name'])

    # Set subject
    subject = data[0]['subject']

    # Set location
    location = email_path

    # Set date
    date = data[0]['date']

    # Insert email into table:
    #       - emails
    # Get id from emails table

    email_id = db_opperations.db_insert.insert_email(
        connection, subject, location, date)

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
        receiver_user_id = db_opperations.db_insert.insert_user(
            connection, receiver['email'], receiver['name'])

        # Inserts sender id,  receiver id and email id into table:
        #       - relations
        db_opperations.db_insert.insert_relation(
            connection, email_id, sender_user_id, receiver_user_id)

    else:

        # More than one receiver
        # Set receiver
        for receiver in receivers:

            # Insert receiver into tables:
            #       - users
            #       - users_email
            # Get id from users table
            receiver_user_id = db_opperations.db_insert.insert_user(
                connection, receiver['email'], receiver['name'])

            # Insert sender id, receiver id and email id into table:
            #       - relations
            db_opperations.db_insert.insert_relation(
                connection, email_id, sender_user_id, receiver_user_id)

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


def email_messages_sent_by_user_email():
    # The number_emails_sent_by_user_email function handles the data related to:
    #   - number of email messages sent by each email address
    # and parses it to be written in a .csv file

    # Query to get data related to the number of emails inboxes each user sent a email message
    query = '''
        SELECT users_emails.email, COUNT(DISTINCT(relations.email_id))
        FROM relations 
            JOIN users ON users.id = relations.sender_user_id 
            JOIN users_emails ON users.email_id = users_emails.id 
        GROUP BY users_emails.email;
    '''

    # Get database connection
    connection = db_opperations.db_connection.open_connection(db_name)

    # Get data from query
    data = db_opperations.db_get.get_data(connection, query)

    # Close database connection
    db_opperations.db_connection.close_connection(connection)

    # Set file name
    file_name = 'email_messages_sent_by_email'

    # Set headers
    headers = ['Sender Email', 'Number of email inboxes']
    
    return_data = []
    parameters = ['email', 'count']

    # Pass data to be written to a .csv file
    return_data = writers.csv_writer.write(file_name, headers, data, return_data, parameters)

    return return_data


def total_emails_and_users_emails():
    # The total_emails function handles the data related to:
    #   - total number of email messages
    # and parses it to be written in a .csv file

    # List to store queries
    query_list = []

    # Query to get data related to the total number of email messages
    query = '''
        SELECT COUNT(*)
        FROM users_emails;
    '''

    # Add query to the list
    query_list.append(query)

    # Query to get data related to the total number of email adresses
    query = '''
        SELECT COUNT(*)
        FROM emails;
    '''

    # Add query to the list
    query_list.append(query)

    # Get database connection
    connection = db_opperations.db_connection.open_connection(db_name)

    # List to store result of query
    data = []

    # Get data from each query
    for query in query_list:
        data.append(db_opperations.db_get.get_data(connection, query))

    # Close database connection
    db_opperations.db_connection.close_connection(connection)

    # Prepare data to write
    data = [(data[1][0][0], data[0][0][0])]

    # Set file name
    file_name = 'total_emails_and_users_emails'

    # Set headers
    headers = ['Total Emails Messages', 'Total Emails Adresses']

    return_data = []
    parameters = ['total_email_messages', 'total_email_address']

    # Pass data to be written to a .csv file
    return_data = writers.csv_writer.write(file_name, headers, data, return_data, parameters)

    return return_data

def users_communication():
    # The users_communication function handles the data related to:
    #   - communication between senders and receivers emails
    # and parses it to be written in both a .gv and a .pdf file

    # query to get data related to the communication between senders and receivers
    query = '''
        SELECT 'email_' ||  se.id as sender_id, se.email as sender_email , 'email_' || re.id as receiver_id, re.email as receiver_email
        FROM relations 
            JOIN users s ON s.id = relations.sender_user_id
            JOIN users r ON r.id = relations.receiver_user_id 
            JOIN users_emails se ON r.email_id = re.id
            JOIN users_emails re ON s.email_id = se.id;
    '''

    # Get database connection
    connection = db_opperations.db_connection.open_connection(db_name)

    # Get data from query
    data = db_opperations.db_get.get_data(connection, query)

    # Close database connection
    db_opperations.db_connection.close_connection(connection)

    # Set file name
    file_name = 'users_communication'

    # Pass data to be written in both a .gv and a .pdf file
    writers.graphviz_writer.write(file_name, data)


def user_communication(email):
    # The users_communication function handles the data related to:
    #   - communication between a given sender and receiver email
    # and parses it to be written in both a .gv and a .pdf file

    # query to get data related to the communication between senders and receivers
    query = '''
        SELECT 'email_' ||  se.id as sender_id, se.email as sender_email , 'email_' || re.id as receiver_id, re.email as receiver_email
        FROM relations 
            JOIN users s ON s.id = relations.sender_user_id
            JOIN users r ON r.id = relations.receiver_user_id 
            JOIN users_emails se ON r.email_id = re.id
            JOIN users_emails re ON s.email_id = se.id
        WHERE se.email = '{}' OR re.email = '{}';
    '''.format(email, email)

    # Get database connection
    connection = db_opperations.db_connection.open_connection(db_name)

    # Get data from query
    data = db_opperations.db_get.get_data(connection, query)

    # Close database connection
    db_opperations.db_connection.close_connection(connection)

    # Set file name
    file_name = email + '_communication'

    # Pass data to be written in both a .gv and a .pdf file
    writers.graphviz_writer.write(file_name, data, False)

#################################
#       End of functions        #
#################################


#################################
#        Start of main          #
#################################

if __name__ == "__main__":
    # The __name__ function is the begining of the the program

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
        print('[ERROR] Invalid operation system ({})! Exited...'.format(
            operation_system))

        # Exit program (code -1)
        exit(ERROR_OS)

    # Start time count in order to get program execution time
    start_time = time.time()
    print('Start...')

    # Test file
    pst_file = r'../EmailSamples/ipleiria.pst'

    # Get md5 hash of given file
    #db_name = calculate_md5(pst_file)
    db_name = '6d9c6ff3a7ce5ec7f9dd122b1b4fcf7b'

    # Rebuild database (drops if exists and creates)
    #db_rebuild(db_name)

    """
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

            # In case of unknown file format
            if result == 'unknown':

                # Print error message and skips to the next file
                print('[ERROR] Unknown file extention (\'.{}\')!'.format(
                    file_extention))
    """

    # Write reports
    print('Generating Reports...')

    # Write email messages sent by each email account in a .csv file
    email_frequency = email_messages_sent_by_user_email()

    # Write total number of email messages and email addresses in a .csv file
    #total_emails_and_users_emails()

    # Write data to tsv
    #writers.tsv_writer.write(date_list)

    sorted_email_frequency = sorted(email_frequency, key=lambda x: -x['count'])

    # Write data to html report
    writers.html_report_writer.write('PST Report', pst_file, sorted_email_frequency)

    # Program execution time
    end_time = time.time()
    execution_time = end_time - start_time
    print('Finished program: ', execution_time)

    # Exit program (code 0)
    exit(SUCCESS)

#################################
#        Start of main          #
#################################
