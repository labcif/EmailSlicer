import subprocess
import time
import sys
import os

if __name__ == "__main__":
    # subprocess.run(["ls", "-l"])
    # EX: readpst -D -b -e -j 8 -q -d ./outlook.log -o ./outlook outlook.pst
    # only file
    file = os.path.basename(sys.argv[1]) 
    file_path = sys.argv[1] 

    file_name = file.split('.')[0]
    output_dir = os.getcwd() + '/output_files/' + file_name

    number_processes = '8'

    access_rights = 0o755
    
    try:  
        #os.mkdir(output_dir, access_rights)
        os.mkdir(output_dir)
    except OSError:
        print ("Creation of the directory %s failed" % output_dir)
    else: 
        print ("Successfully created the directory %s" % output_dir)

    # -D                - Include deleted items in output
    # -b                - Don't save RTF-Body attachments
    # -e                - As with -M, but include extensions on output files
    # -j <integer>      - Number of parallel jobs to run
    # -q                - Quiet. Only print error messages
    # -d <filename>     - Debug to file.
    # -o <dirname>      - Output directory to write files to. CWD is changed *after* opening pst file
    t1 = time.time()
    print('Start')
    #subprocess.run(['readpst', '-D', '-b', '-e', '-o ' + output_dir, file_path])

    #cmd = ['readpst', '-D', '-b', '-e', '-j ' + number_processes , '-o ' + output_dir, file_path]
    #subprocess.run(cmd)
    cmd = 'readpst -D -b -e -j {} -o {} {}'.format(number_processes, output_dir, file_path)
    print(cmd)
    x = subprocess.call(cmd, shell=True)
    #subprocess.run(['readpst', '-D', '-b', '-e', '-j 8', '-q' ,'-d ./' + file_name + '.log', '-o ' + output_dir, file_path])
    print('Finish: ', time.time() - t1)
