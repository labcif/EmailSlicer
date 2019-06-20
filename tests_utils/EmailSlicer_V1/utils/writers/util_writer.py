from re import sub as rep
from string import punctuation as pont
import os


def create_path(file_name):
    """
    The makePath function provides an absolute path between the output_directory and a file
    :param file_name: A string representing a file name
    :return: A string representing the path to a specified file
    """
    return os.path.abspath(os.path.join('output_files', file_name))

def sanitize_string(_string):
    return rep(' +', ' ', _string.translate(str.maketrans('', '', pont)).replace('|', ':').replace('/', ':').replace('\t', ' ').replace('\n', ' '))

