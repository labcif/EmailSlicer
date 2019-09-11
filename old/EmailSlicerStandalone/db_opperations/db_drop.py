def drop_tables(connection):
 
    # Create cursor
    cursor = connection.cursor()

    # Drop queries table
    cursor.execute(drop_queries_table())

    # Drop users table
    cursor.execute(drop_relations_table())
    
    # Drop users table
    cursor.execute(drop_emails_table())
    
    # Drop users table
    cursor.execute(drop_users_table())
    
    # Drop users_emails table
    cursor.execute(drop_users_emails_table())


def drop_queries_table():
    return 'DROP TABLE IF EXISTS queries;'


def drop_relations_table():
    return 'DROP TABLE IF EXISTS relations;'


def drop_emails_table():
    return 'DROP TABLE IF EXISTS emails;'


def drop_users_table():
    return 'DROP TABLE IF EXISTS users;'


def drop_users_emails_table():
    return 'DROP TABLE IF EXISTS users_email;'