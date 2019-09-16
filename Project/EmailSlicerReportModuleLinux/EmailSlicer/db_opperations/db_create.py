def create_tables(connection):
        
    # Create cursor
    cursor = connection.cursor()

    # Create users_emails table
    cursor.execute(create_users_emails_table())
    
    # Create users table
    cursor.execute(create_users_table())
    
    # Create users table
    cursor.execute(create_emails_table())
    
    # Create users table
    cursor.execute(create_relations_table())

    # Create queries table
    cursor.execute(create_queries_table())

    
def create_users_emails_table():
    return '''
        CREATE TABLE IF NOT EXISTS 
        users_emails (
            id INTEGER PRIMARY KEY,
            email TEXT,
            UNIQUE (email)
        );
    '''


def create_users_table():
    return '''
        CREATE TABLE IF NOT EXISTS 
        users (
            id INTEGER PRIMARY KEY,
            email_id INTEGER,
            name TEXT,
            FOREIGN KEY (email_id) REFERENCES users_emails (id)
        );
    '''


def create_emails_table():
    return '''
        CREATE TABLE IF NOT EXISTS 
        emails (
            id INTEGER PRIMARY KEY,
            subject TEXT,
            body TEXT,
            location TEXT,
            date INTEGER
        );
    '''


def create_relations_table():
    return '''
        CREATE TABLE IF NOT EXISTS 
        relations (
            email_id INTEGER,
            sender_user_id INTEGER,
            receiver_user_id INTEGER,
            FOREIGN KEY (email_id) REFERENCES emails (id),
            FOREIGN KEY (sender_user_id) REFERENCES users (id),
            FOREIGN KEY (receiver_user_id) REFERENCES users (id)
        );
    '''


def create_queries_table():
    return '''
        CREATE TABLE IF NOT EXISTS 
        queries (
            id INTEGER PRIMARY KEY,
            query TEXT
        );
    '''