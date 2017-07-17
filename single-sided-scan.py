#!/usr/bin/python3

# Objectives: scan single sided files. convert to pdf. 

import os,sys,re,time,datetime,subprocess

from scanutils import *

# SETTINGS
part = 'part'
as_script = False
debug = True 
logfile = '/home/arjun/brscan/double-sided-scan.log'
lfile = open(logfile,'a')
waitlimit = 300 # a limit for waiting to fix errors

# SCRIPT START
# read arguments 
# see if run as a script

if not re.match(r'/usr/bin/.*python.*',sys.argv[0]):
    as_script = True

args = sys.argv
[directory,prefix,timenow,device,resolution,height,width,mode] \
        = parse_arguments(as_script,args)

if debug:
    display(directory + ' prefix = ' + prefix + '. timenow = ' + str(timenow) + '\n',as_script=as_script,logfile=lfile)
    display('arguments = ', sys.argv)

outputfile = directory + '/' + prefix + '-' + str(int(timenow)) + '-part-%03d.pnm'
run_scancommand(device,outputfile,width=width,height=height,logfile=lfile,debug=debug,mode=mode,resolution=resolution,batch=True,batchstart='1',batchincrement='1')

os.system('sleep 3')
files = filelist('ls ' + directory + prefix + '-' + str(int(timenow)) + '-part-*.pnm')
# find number of files by scanning the part number of the last file.
# assumes that the list is sorted.
number_scanned = file_part(files[-1],match_string_part)

if debug:
    display("number_scanned: " + str(number_scanned),as_script=as_script,logfile=lfile)

# wait for a time proportional to the number scanned
convert_to_pdf(directory=directory,outputtype='pdf',wait=int(number_scanned/3.0),debug=debug)

# find newly converted files
convertedfiles = filelist('ls ' + directory + prefix + '-' + str(int(timenow)) + '-part-*.pdf')

# make a filelist and output filename to pdftk
compiled_pdf_filename = directory + prefix + '-' + datetime.date.today().isoformat() + '-' + str(int(time.time())) + '.pdf'

run_pdftk(convertedfiles,compiled_pdf_filename,debug=debug,logfile=lfile)



