import os
rootdir = '/home/nogueira/Documents/EmailSlicer/CodeSample'

if __name__ == "__main__":    
    for sub_directory, directories, files in os.walk(rootdir):
        # iterate folders
        for directory in directories:
            print(os.path.join(sub_directory, directory))            

        # iterate files
        for file in files:
            print(os.path.join(sub_directory, file))