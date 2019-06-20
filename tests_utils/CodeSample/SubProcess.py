import subprocess

def convert_pst_to_mbox(pstfilename, outputfolder):
    subprocess.call(['readpst', '-o', outputfolder, '-r', pstfilename])