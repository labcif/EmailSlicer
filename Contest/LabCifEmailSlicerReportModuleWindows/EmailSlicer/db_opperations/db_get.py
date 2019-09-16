def get_data(connection, query):
    
    # Create cursor
    cursor = connection.cursor()

    # Create users_emails table
    cursor.execute(query, ())
    result = cursor.fetchall()

    return result