import sqlite3


def create_tables(table_name):
   # Create database 
    connection = sqlite3.connect('output_files/' + table_name + '.db')
    cursor = connection.cursor()

    # Create emails table
    emails_sql = '''
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY,
        folder_name TEXT,
        subject TEXT,
        sender TEXT,
        receiver TEXT,
        header TEXT,
        body TEXT,
        creation_time TEXT,
        submit_time TEXT,
        delivery_time TEXT,
        total_attachment_size REAL);'''
    cursor.execute(emails_sql)

    # Create attachments table
    attachments_sql = '''
    CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY,
        email_id INTEGER,
        attachments TEXT,
        FOREIGN KEY (email_id) REFERENCES emails (id));'''
    cursor.execute(attachments_sql)

    # Create queries table
    queries_sql = '''
    CREATE TABLE IF NOT EXISTS queries (
        id INTEGER PRIMARY KEY,
        query TEXT);'''
    cursor.execute(queries_sql)

    # Save (commit) the changes
    connection.commit()

    # Closes the connectionection
    # NOTE: Just be sure any changes have been committed or they will be lost
    connection.close()


def insert_tables(table_name, message_data):
    # connectionects to database 
    connection = sqlite3.connect('output_files/' + table_name + '.db')
    cursor = connection.cursor()
    
    # Insert a row of data (email)
    for data in message_data:
        insert_email = '''
        INSERT INTO emails (
            folder_name,
            subject, 
            sender,
            receiver,
            header,
            body, 
            creation_time, 
            submit_time, 
            delivery_time, 
            total_attachment_size) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''
        cursor.execute(insert_email, (
            data['folder_name'],
            data['subject'], 
            data['sender'],
            data['receiver'],
            data['header'],
            data['body'], 
            data['creation_time'], 
            data['submit_time'], 
            data['delivery_time'], 
            data['total_attachment_size']))
        
        if data['total_attachment_size'] > 0:
            # Get last insert ID curremsponding to the attachment(s)
            email_id = cursor.lastrowid
            
            # Insert a row of data (attachment)
            for attachment in data['attachments']:
                insert_attachment = '''INSERT INTO attachments (
                    email_id,
                    attachments)
                    VALUES (?, ?);'''
                cursor.execute(insert_attachment, (email_id, attachment))
    
    # Save (commit) the changes
    connection.commit()

    # Closes the connectionection
    # NOTE: Just be sure any changes have been committed or they will be lost
    connection.close()


def drop_tables(table_name):
    # connectionects to database 
    connection = sqlite3.connect('output_files/' + table_name + '.db')
    cursor = connection.cursor()

    # Drop emails table
    drop_emails_sql = 'DROP TABLE IF EXISTS emails;'
    cursor.execute(drop_emails_sql)

    # Drop attachments table
    drop_attachments_sql = 'DROP TABLE IF EXISTS attachments;'
    cursor.execute(drop_attachments_sql)

    # Drop queries table
    drop_queries_sql = 'DROP TABLE IF EXISTS queries;'
    cursor.execute(drop_queries_sql)

    # Save (commit) the changes
    connection.commit()

    # Closes the connectionection
    # NOTE: Just be sure any changes have been committed or they will be lost
    connection.close()
