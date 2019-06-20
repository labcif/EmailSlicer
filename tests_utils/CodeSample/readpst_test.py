import subprocess
import sys

if __name__ == "__main__":
    #cmd = ['readpst', '-D', '-b', '-e', '-j 8' , '-o /home/nogueira/Documents/EmailSlicer/CodeSample/output_files', '../EmailSamples/vkaminski_000_1_1_1.pst']
    cmd = 'readpst -D -b -e -j 8 -o /home/nogueira/Documents/EmailSlicer/CodeSample/output_files ../EmailSamples/vkaminski_000_1_1_1.pst'
    subprocess.call(cmd, shell=True)