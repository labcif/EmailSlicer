import hashlib


def calculate(_file):
    # The calculate_md5 function returns a md5 chechsum of the give file
    # :param file: file to calculate hash

    # Call md5 from hashlib
    hash_md5 = hashlib.md5()

    # Open file in binary read mode
    with open(_file, 'rb') as f:

        # Read chunks of 4096 bytes sequntially
        for chunk in iter(lambda: f.read(4096), b''):

            # Feed the chunks to the md5 funtion
            hash_md5.update(chunk)

    # Return md5 hash of the given file
    return hash_md5.hexdigest()