#################################
#       Start of Imports        #
#################################


import subprocess
import time
import sys
import os
import shutil
import argparse
import hashlib
import sqlite3
import base64
import quopri
import re
import pkgutil
import encodings
import mailparser
import datetime
import email
import db_opperations
import writers
import utils
import json



#################################
#        End of Imports         #
#################################


# Test command
# python3 EmailSlicer.py ../EmailSamples/ipleiria.pst output_files -j 8 -t "TESTE REPORT" -e "2151580@my.ipleiria.pt" "2161795@my.ipleiria.pt"
# python3 EmailSlicer.py ../EmailSamples/ipleiria.pst output_files -j 8 -t "TESTE REPORT" -s


#################################
#   Start of variables   #
#################################


# Program author
__author__ = 'Andre Nogueira'

# Program description
__description__ = '''
    This scripts calls readpst wich is a program responsible for extracting all content present inside the given .pst/.ost file.
    The script starts by checking wich operation system is in use to permit it's execution in both windows and linux platforms.
    After the it's execution it's possible to extract relavant information from the extract files.
'''

# There were no problems
SUCCESS = 0

# Invalid operation system
ERROR_OS = -1

# Invalid output directory
ERROR_OUTPUT_DIRECTORY = -2


#################################
#    End of variables    #
#################################


#################################
#      Start of functions       #
#################################


class EmailSlicer:

    def __init__(self, _file, output_directory, output_extraction, report_title, skip, user_email, extract_only, boool):
        
        self._file = _file
        self.output_directory = output_directory
        self.output_extraction = output_extraction
        self.title = report_title
        self.target_email = user_email
        self.boool = boool

        date_dict = {x: 0 for x in range(1, 25)}
        self.date_list = [date_dict.copy() for x in range(7)]

        self.emails_with_sender_receiver = {}

        # Get databse name
        # '6d9c6ff3a7ce5ec7f9dd122b1b4fcf7b'
        self.db_name = utils.md5.calculate(_file)
        
        self.extract_only = extract_only

        self.skip = skip
        if boool or not skip:
            # Rebuild database (drops if exists and creates)
            self.db_rebuild()
        #$else:
            #$print('[INFO] Using previous database')

    def run(self):
        
        #$if not self.skip:
            #$print('[INFO] Started file scaning')
        #$else:
            #$print('[INFO] Skipping file scaning')
        total_count = []

        # Iterates previous base output directory
        for root, _, files in os.walk(self.output_extraction):

            count_ics = 0
            count_vcf = 0
            count_eml = 0
            count_unknown = 0
            number_of_files = [
                count_ics,
                count_vcf,
                count_eml,
                count_unknown
            ]

            # iterate files
            for _file in files:
                # #$print("subd > " + root)
                # #$print("main > " + "".join(dirs))

                # Get full file path
                file_full_path = os.path.join(root, _file)

                # Get file name
                file_name = os.path.basename(_file)

                # Get file extention
                file_extention = file_name.split('.')[1]

                # Check if file extention is supported
                number_of_files = self.process_file_extention(file_extention, file_full_path, number_of_files)
            total_count.append(number_of_files)
            # #$print(root.rsplit('/', 1)[-1] , "\n", number_of_files, "\n\n")
#            #$print(rootdir)
#           #$print(root.rsplit('/', 1)[-1])
        # #$print(tree)
    
            
        # Write reports
        #$print('[INFO] Generating report...')
        
        
        if not self.extract_only:

            try:
                total_count_aux = []
                with open(output_directory + "/" + "total_count.txt") as fp:
                    lines = fp.readlines()
                    for line in lines:
                        total_count_aux.append(line.replace('\n', ''))
                    total_count_aux = [n.strip() for n in total_count_aux]
                    total_count = []            
                    for s in total_count_aux:
                        total_count.append(json.loads(s))
            except:
                pass

            # Write email messages sent by each email account in a .csv file
            sender_frequency = self.email_messages_sent_by_user_email()

            # Write total number of email messages and email addresses in a .csv file
            total_email_address = self.total_emails_and_users_emails()[0]['total_email_address']

            # Write data to tsv
            writers.tsv_writer.write(self.output_directory, self.date_list)

            users_communication, counts = self.sender_receiver_total()
            
            user_messages = self.users_messages(counts)

            # Write data to html report
            writers.html_report_writer.Report(self.output_directory, self.title, total_email_address, total_count, self.output_directory, sender_frequency, self.date_list, users_communication, user_messages)
            # writers.html_report_writer.write(self.title, self._file, sorted_email_frequency)

            # Comunication between all users
            self.users_communication()
            
            # In case of specified user email
            if self.target_email:
                for target in self.target_email:
                    self.user_communication(target)
        else:
            with open(self.output_directory + "/" + "total_count.txt", "w") as fp:
                for item in total_count:
                    fp.write(''.join(str(item)))
                    fp.write('\n')

            

    #################################
    #          End of run           #
    #################################


    def process_file_extention(self, extention, _file, data):
        # The process_file_extention function returns the correct funtion to process the given file
        # depending on it's file extention
        # :param file: full email path
        # :param erxtention: file extention

        if extention == 'ics':

            data[0] += 1

        elif extention == 'vcf':

            data[1] += 1

        # Check if extention if eml
        elif extention == 'eml':

            # Returns function to process eml email
            self.process_eml(_file)
            data[2] += 1

        # There is no match
        else:
            
            # In case of unknown file format
            data[3] += 1

            # #$Print error message and skips to the next file
            #$print('[WARNING] Unknown file extention (\'.{}\')!'.format(extention))
            # Returns string unknown if the extention is not known by the program

        return_data = [data[0], data[1], data[2], data[3]]
        return return_data


    def process_eml(self, _file):
        # The process_eml function processes the information present in each email
        # populating the emails_with_sender_receiver with the need information
        # :param file: full email path

        # Parse file to be processed by mailparser
        mail = mailparser.parse_from_file(_file)

        # Get email subject
        subject = mail.subject

        # Get date
        date = mail.date
        
        # Build heat map based on email message received time
        self.build_heat_map(_file, date)
        
        if not self.boool:
            # Get body
            eplainBody = "".join(mail.text_plain).encode('utf-8')
            ehtmlBody = "".join(mail.text_html).encode('utf-8')

            dplainBody = eplainBody.decode('utf-8')
            dhtmlBody = ehtmlBody.decode('utf-8')

            body = dplainBody
            body_html = dhtmlBody

        

            if not self.skip:
                # Get email date in epoch time
                date_epoch = utils.date.get_epoch_unix_time(mail.date)

                # Populate variable
                self.emails_with_sender_receiver[_file] = [{
                    'subject': subject,
                    'body': body,
                    'body_html': body_html,
                    'date': date_epoch,
                    'sender': {},
                    'receiver': []
                }]

                # Get formated sender and insert it into the variable
                
                # #$print(mail.from_)
                self.filter_sender(_file, mail.from_)

                # Get formated receiver(s) and insert it into the variable
                self.filter_receiver(_file, mail.to)

                # Insert data into the database
                self.db_insert_data(self.emails_with_sender_receiver[_file], _file)


    def build_heat_map(self, _file, date):

        try:
            # Received time
            day_of_week = date.weekday()
            hour_of_day = date.hour + 1
            self.date_list[day_of_week][hour_of_day] += 1
        except:
            pass
            #$print('[WARNING] File \'{}\' file has no received date!'.format(_file))


    def filter_sender(self, _file, sender_list):
        # The filter_sender function processes the a list of  given senders, formats the information
        # and insert it correctly inside the variable
        # :param file: email with eml extention
        # :param sender_list: list with senders of teh given file

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
            # Insert the previous obtained data (sender_email and sender_name) in the variable
            self.emails_with_sender_receiver[_file][0]['sender'] = (
                {
                    'email': sender_email,
                    'name': sender_name
                }
            )
        except: #$Exception as exeption:
            pass
            # #$Print error in case of one
            #$print('ERROR \'sender\': ', exeption)


    def filter_receiver(self, _file, receiver_list):
        # The filter_receiver function processes the a list of given receivers, formats the information
        # and insert it correctly inside the variable
        # :param file: email with eml extention
        # :param receiver_list: list with receivers of teh given file

        # Case where there are no receivers comes empty
        if receiver_list == []:

            # Set both receiver email and name to NULL string
            receiver_email = 'NULL'
            receiver_name = 'NULL'

            try:
                # Insert the previous obtained data (receiver_email and receiver_name) in the variable
                self.emails_with_sender_receiver[_file][0]['receiver'].append(
                    {
                        'email': receiver_email,
                        'name': receiver_name
                    }
                )
            except: #$Exception as exeption:
                pass
                # #$Print error in case of one
                #$print('ERROR \'receiver\': ', exeption)

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
                # Insert the previous obtained data (receiver_email and receiver_name) in the variable
                self.emails_with_sender_receiver[_file][0]['receiver'].append(
                    {
                        'email': receiver_email,
                        'name': receiver_name
                    }
                )
            except: #$Exception as exeption:
                pass
                # #$Print error in case of one
                #$print('ERROR \'receiver\': ', exeption)


    def db_insert_data(self, data, email_path):
        # The db_inser_data function formats data and inserts it correctly into the database
        # :param db_name: name of the database
        # :param data: data to be fotmated
        # :email_path: path of the email

        # Get database connection
        connection = db_opperations.db_connection.open_connection(self.output_directory, self.db_name)

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

        # Set body
        body = data[0]['body']
        body_html = data[0]['body_html']

        # Insert email into table:
        #       - emails
        # Get id from emails table

        email_id = db_opperations.db_insert.insert_email(
            connection, subject, body, body_html, location, date)

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


    def db_rebuild(self):
        # The db_rebuild function checks whether or not the given database and acts accordingly
        # :param db_name: name of the database

        #$print('[INFO] Rebuilding database')

        # Get database connection
        connection = db_opperations.db_connection.open_connection(self.output_directory, self.db_name)

        # Check if file exists
        if os.path.isfile(self.output_directory + self.db_name + '.db'):
    
            # Delete database table
            db_opperations.db_drop.drop_tables(connection)

        # Create database table
        db_opperations.db_create.create_tables(connection)

        # Close database connection
        db_opperations.db_connection.close_connection(connection)


    def email_messages_sent_by_user_email(self):
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
        connection = db_opperations.db_connection.open_connection(self.output_directory, self.db_name)

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
        return_data = writers.csv_writer.write(self.output_directory, file_name, headers, data, return_data, [], parameters, True)

        return return_data


    def total_emails_and_users_emails(self):
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
        connection = db_opperations.db_connection.open_connection(self.output_directory, self.db_name)

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
        return_data = writers.csv_writer.write(self.output_directory, file_name, headers, data, return_data, [], parameters, True)

        return return_data

    def users_communication(self):
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
        connection = db_opperations.db_connection.open_connection(self.output_directory, self.db_name)

        # Get data from query
        data = db_opperations.db_get.get_data(connection, query)

        # Close database connection
        db_opperations.db_connection.close_connection(connection)

        # Set file name
        file_name = 'users_communication'

        # Pass data to be written in both a .gv and a .pdf file
        writers.graphviz_writer.write(self.output_directory, file_name, data)


    def user_communication(self, target):
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
        '''.format(target, target)

        # Get database connection
        connection = db_opperations.db_connection.open_connection(self.output_directory, self.db_name)

        # Get data from query
        data = db_opperations.db_get.get_data(connection, query)

        # Close database connection
        db_opperations.db_connection.close_connection(connection)

        # Set file name
        file_name = target + '_communication'

        # Pass data to be written in both a .gv and a .pdf file
        writers.graphviz_writer.write(self.output_directory, file_name, data, False)
    
    def sender_receiver_total(self):
        query = '''
            SELECT se.email as sender_email , re.email as receiver_email, COUNT(*)
            FROM relations 
                JOIN users s ON s.id = relations.sender_user_id
                JOIN users r ON r.id = relations.receiver_user_id 
                JOIN users_emails se ON r.email_id = re.id
                JOIN users_emails re ON s.email_id = se.id
			GROUP BY sender_email
        '''

        # Get database connection
        connection = db_opperations.db_connection.open_connection(self.output_directory, self.db_name)

        # Get data from query
        data = db_opperations.db_get.get_data(connection, query)

        # Close database connection
        db_opperations.db_connection.close_connection(connection)

        # Set file name
        file_name = 'sender_receiver_total'

        # Set headers
        headers = ['Sender Email', 'Receier Email', 'Total Messages']

        return_data = []
        parameters = ['row_id', 'sender', 'receiver', 'count']
        
        # Pass data to be written to a .csv file
        return_data, return_data_counts = writers.csv_writer.write(self.output_directory, file_name, headers, data, return_data, [], parameters)


        return return_data, return_data_counts


    def users_messages(self, data_count):    
        query = '''
            SELECT  e.subject as subject, e.location as location, e.date as date
            FROM relations 
                JOIN users s 		ON s.id = relations.sender_user_id
                JOIN users r 		ON r.id = relations.receiver_user_id 
                JOIN users_emails se 	ON r.email_id = re.id
                JOIN users_emails re 	ON s.email_id = se.id
                JOIN emails e 		ON e.id = relations.email_id
            ORDER BY se.email
        '''

        # Get database connection
        connection = db_opperations.db_connection.open_connection(self.output_directory, self.db_name)

        # Get data from query
        data = db_opperations.db_get.get_data(connection, query)

        # Close database connection
        db_opperations.db_connection.close_connection(connection)

        # Set file name
        file_name = 'users_messages'

        # Set headers
        headers = ['Email Subject', 'Email Location', 'Email Received Date']

        return_data = []
        parameters = ['row_id', 'subject', 'location', 'date']        
        
        # Pass data to be written to a .csv file
        return_data = writers.csv_writer.write(self.output_directory, file_name, headers, data, return_data, data_count, parameters)

        return return_data


    #################################
    #       End of functions        #
    #################################




#################################
#        Start of main          #
#################################


if __name__ == "__main__":
    
    # Start time count in order to get program execution time
    #$start_time = time.time()
    #$print('##########\n[INFO] Started program')

    # Create an ArgumentParser object to specify arguments for the program
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog='Developed by ' + __author__)

    # FILE: rquired
    parser.add_argument('FILE',
                        help='File to extract (suported formats: PST/OST)')

    # OUTPUT_DIRECTORY: rquired
    parser.add_argument('OUTPUT_DIRECTORY',
                        help='Directory of output for the extracted and report files.')

    # title: NOT rquired
    parser.add_argument('-t', '--title',
                        help='Title of the HTML Report. (default=PST Report)',
                        default='PST Report')

    # skip: NOT rquired
    parser.add_argument('-s', '--skip',
                        help='Skip file extraction and database rebuild. Only gets the report files (default=false)', 
                        action='store_true', 
                        default=False)
    
    # skip: NOT rquired
    parser.add_argument('-o', '--only',
                        help='Only extract files, do not generate report (default=false)', 
                        action='store_true',
                        default=False)


    # email: NOT rquired
    parser.add_argument('-e', '--email',
                        help='Specific user(s) email(s) to be analized.', nargs='+')

    """ TODO
    # query: NOT rquired
    parser.add_argument('-q', '--query',
                        help='Specific query to be executed. The result will be outputed in a .csv file inside the output directory.')
    """

    # jobs: NOT rquired
    parser.add_argument('-j', '--jobs',
                        help='Number of parallel jobs to be used when extracting the files. (default=8)', default='8')

    # Get all args
    args = parser.parse_args()

    # Get file path
    file_path = args.FILE

    # Get base name (name of file)
    file = os.path.basename(file_path)

    # Get file name without extention
    file_name = file.split('.')[0]

    # Set output directory
    output_directory = os.path.abspath(args.OUTPUT_DIRECTORY)
    output_directory = re.sub(r'\s+', '', output_directory)
    
    output_extraction = os.path.abspath(args.OUTPUT_DIRECTORY + '/' + file_name)
    output_extraction = re.sub(r'\s+', '', output_extraction)

    try:

        # In cose of the file doesn't exist
        if not os.path.exists(output_extraction):

            # Create new path
            os.makedirs(output_extraction)
            #$print('[INFO] Successfully created the directory \'%s\'!' %
            #$    output_extraction)

        else:
            pass#exit(SUCCESS)
            # In case it exists
            #$print('[INFO] Directory \'%s\' already exists!' 
            #$    % output_extraction)

    except OSError:
        pass
        # In case of error
        #$print('[ERROR] Creation of the directory \'%s\' failed!' 
        #$    % output_extraction)

        # Exit program (code -2)
        #exit(ERROR_OUTPUT_DIRECTORY)

    # Get number of jobs
    number_processes = args.jobs

    # Command 'readpst' ptions used:
    # -D                - Include deleted items in output
    # -b                - Don't save RTF-Body attachments
    # -e                - As with -M, but include extensions on output files
    # -j <integer>      - Number of parallel jobs to run
    # -q                - Quiet. Only #$print error messages
    # -d <filename>     - Debug to file.
    # -o <dirname>      - Output directory to write files to. CWD is changed *after* opening pst file

    # Get current operation system
    operation_system = os.name

    # Get agrs.skip value
    skip = args.skip

    # Get agrs.only value
    extract_only = args.only

    # DB hash    
    dbHash = utils.md5.calculate(file_path)

    boool = dbHash + ".db" not in next(os.walk(output_extraction))[2]
    
    # Case where skip is specified
    if not boool:
    
        # Check current operation system
        if operation_system == 'nt':

            # Operation System: Windows
            cmd = ('{}\\utils\\readpst\\bin\\readpst.exe -q -D -b -e -j {} -o {} {}'
                .format(os.path.dirname(os.path.realpath(__file__)), number_processes, output_extraction, "\"" + file_path + "\""))  # retunrs 0 in case of success
            subprocess.call(cmd, shell=True)
            
        elif operation_system == 'posix':

            # Operation System: Linux
            # retunrs 0 in case of success
            cmd = 'readpst -q -D -b -e -j {} -o {} {}'.format(
                number_processes, output_extraction, "\"" + file_path + "\"")
            subprocess.call(cmd, shell=True)

        else:

            # In case the Operation System is different
            #$print('[ERROR] Invalid operation system ({})! Exited...'
            #$    .format(operation_system))

            # Program execution time
            #$end_time = time.time()
            #$execution_time = end_time - start_time
            #$print('[INFO] Exited program: {}\n##########'
            #$    .format(execution_time))

            # Exit program (code -1)
            exit(ERROR_OS)
    else:
        pass
        #$print('[INFO] Skipping email extraction')

    user_email = args.email

    es = EmailSlicer(
        file_path, 
        output_directory, 
        output_extraction, 
        args.title, 
        skip, 
        user_email,
        extract_only,
        boool
    )
    es.run()
    
    # Program execution time
    #$end_time = time.time()
    #$execution_time = end_time - start_time
    #$print('[INFO] Finished program: {} ({} min)\n##########'
    #$    .format(execution_time, execution_time/60))

    # Exit program (code 0)
    exit(SUCCESS)


#################################
#          End of main          #
#################################
