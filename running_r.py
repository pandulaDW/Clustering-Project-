import pandas as pd
import subprocess
import os

userhome = os.path.expanduser('~')
desktop = userhome + r'\Desktop'

#  Running the R-script
def runningR(df):

    df.to_csv('{}/Book1.csv'.format(desktop), index=False)
    command = 'Rscript'
    path2script = r'C:\Users\Pandula\Desktop\r_script.R' ## Path of the R script

    # Build subprocess command
    cmd = [command, path2script]

    # check_output will run the command and store to result
    x = subprocess.check_output(cmd)

    # remove the Dataset from the directory
    os.remove('{}/Book1.csv'.format(desktop))
