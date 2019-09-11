def insert_user(connection, user_email, user_name):
    
    # Create cursor
    cursor = connection.cursor()

    try:
        
        # Insert user email
        query = '''
            INSERT INTO users_emails (email)
            VALUES (?);
        '''
        cursor.execute(query, (user_email, ))
    
    except:
        
        # Get email id from table
        query = '''
            SELECT id
            FROM users_emails
            WHERE email = ?;
        '''
        cursor.execute(query, (user_email, ))
        user_email_id = cursor.fetchone()[0]

    else:
        
        # Get email id (last insert)
        user_email_id = cursor.lastrowid

    finally:
        
        # Insert user
        query = '''
            INSERT INTO users (email_id, name)
            VALUES (?, ?)
        '''
        cursor.execute(query, (user_email_id, user_name, ))
    
    # Get user id (last insert)
    user_id = cursor.lastrowid

    return user_id


def insert_email(connection, subject, body, location, date):
    
    # Create cursor
    cursor = connection.cursor()
    
    # Insert email
    query = '''
        INSERT INTO emails (subject, body, body_html, location, date) 
        VALUES (?, ?, ?, ?, ?);
    '''
    cursor.execute(query, (subject, body, body_html, location, date, ))
    
    # Get email id (last insert)
    email_id = cursor.lastrowid
    
    return email_id

def insert_relation(connection, email_id, sender_user_id, receiver_user_id):
    
    # Create cursor
    cursor = connection.cursor()
    
    # Insert relation
    query = '''
        INSERT INTO relations (email_id, sender_user_id, receiver_user_id) 
        VALUES (?, ?, ?);
    '''
    cursor.execute(query, (email_id, sender_user_id, receiver_user_id, ))


def insert_query(connection, expression):
    
    # Create cursor
    cursor = connection.cursor()
    
    # Insert query
    query = '''
        INSERT INTO queries (query)
        VALUES (?);
    '''
    cursor.execute(query, (expression, ))

