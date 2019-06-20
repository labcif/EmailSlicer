import sqlite3

def open_connection(db_name):

    # Create database connection
    connection = sqlite3.connect('output_files/' + db_name + '.db')

    return connection


def close_connection(connection):
    
    # Save (commit) the changes
    connection.commit()
    
    # Closes the connectionection
    # NOTE: Closing connection without a previous ocmmit while discard any previous chnages
    connection.close()