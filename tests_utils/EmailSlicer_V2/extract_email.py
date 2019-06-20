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

#################################
#        End of Imports         #
#################################


# Test command
# python3 extract_email.py ../EmailSamples/ipleiria.pst output_files -j 8


#################################
#   Start of global variables   #
#################################

__author__ = 'Andre Nogueira'
__description__ = '''
    This scripts calls readps wich is responsible for extracting all content present inside the given .pst file.
    The script starts by checking wich operation system is in use to permit it's execution in both windows and linux platforms. 
    After the it's execution it's possible to scrap relavant information from the extract files.
'''

# Exit codes
SUCCESS = 0
ERROR_OS = -1
ERROR_OUTPUT_DIRECTORY = -2

#################################
#    End of global variables    #
#################################


#################################
#        Start of main          #
#################################

if __name__ == "__main__":
    # Start time count in order to get program execution time
    start_time = time.time()
    print('Start')

    # Create an ArgumentParser object to specify arguments for the program
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog='Developed by ' + __author__)

    # FILE: rquired
    parser.add_argument('FILE',
                        help='PST File Format from Microsoft Outlook')

    # OUTPUT_DIRECTORY: rquired
    parser.add_argument('OUTPUT_DIRECTORY',
                        help='Directory of output for the extracted and report files.')

    # title: NOT rquired
    parser.add_argument('-t', '--title',
                        help='Title of the HTML Report. (default=PST Report)', default='PST Report')

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
    output_directory = os.path.abspath(args.OUTPUT_DIRECTORY + '/' + file_name)

    try:

        # In cose of the file doesn't exist
        if not os.path.exists(output_directory):

            # Create new path
            os.makedirs(output_directory)
            print('Successfully created the directory \'%s\'!' %
                  output_directory)

        else:

            # In case it exists
            print('Directory \'%s\' already exists!' % output_directory)

    except OSError:

        # In case of error
        print('Creation of the directory \'%s\' failed!' % output_directory)

        # Exit program (code -2)
        exit(ERROR_OUTPUT_DIRECTORY)

    # Get number of jobs
    number_processes = args.jobs

    # Command 'readpst' ptions used:
    # -D                - Include deleted items in output
    # -b                - Don't save RTF-Body attachments
    # -e                - As with -M, but include extensions on output files
    # -j <integer>      - Number of parallel jobs to run
    # -q                - Quiet. Only print error messages
    # -d <filename>     - Debug to file.
    # -o <dirname>      - Output directory to write files to. CWD is changed *after* opening pst file

    # Get current operation system
    operation_system = os.name

    # Check current operation system
    if operation_system == 'nt':

        # Operation System: Windows
        cmd = 'C:/Users/2151580/Desktop/bin/readpst.exe -D -b -e -j {} -o {} {}'.format(
            number_processes, output_directory, file_path)  # retunrs 0 in case of success
        subprocess.call(cmd, shell=True)

        # Program execution time
        end_time = time.time()
        execution_time = end_time - start_time
        print('Finished program: ', execution_time)

    elif operation_system == 'posix':
        # Start time count in order to get program execution time
        start_time = time.time()
        print('Start')

        # Operation System: Linux
        # retunrs 0 in case of success
        cmd = 'readpst -D -b -e -j {} -o {} {}'.format(
            number_processes, output_directory, file_path)
        subprocess.call(cmd, shell=True)

    else:

        # In case the Operation System is different
        print('[ERROR] Invalid operation system ({})! Exited...'.format(
            operation_system))

        # Program execution time
        end_time = time.time()
        execution_time = end_time - start_time
        print('Finished program: ', execution_time)

        # Exit program (code -1)
        exit(ERROR_OS)

    # Program execution time
    end_time = time.time()
    execution_time = end_time - start_time
    print('Finished program: ', execution_time)

    # Exit program (code 0)
    exit(SUCCESS)

#################################
#        Start of main          #
#################################
