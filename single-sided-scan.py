#!/usr/bin/python3

# Objectives: scan single sided files. convert to pdf. 

import os,sys,re,time,datetime,subprocess

from scanutils import *

# SETTINGS
part = 'part'
ownedby = 'arjun:szhao'
as_script = False
debug = True 
logfile = '/home/arjun/brscan/single-sided-scan.log'
lfile = open(logfile,'a')
waitlimit = 300 # a limit for waiting to fix errors
today = datetime.date.today().isoformat() 

# SCRIPT START
# read arguments 
# see if run as a script

print("\n",today," Starting ", sys.argv[0]," at",time.time())

if not re.match(r'/usr/bin/.*python.*',sys.argv[0]):
    as_script = True

args = sys.argv
[directory,prefix,timenow,device,resolution,height,width,mode] \
        = parse_arguments(as_script,args)

# print parameters and arguments on debug
if debug:
    display(directory + ' prefix = ' + prefix + '. timenow = ' + str(timenow) + '\n',logfile=lfile)
    display('arguments = ', sys.argv)

# set filename matchstring regular expressions
match_string_time = directory + prefix+'-([0-9]+)-'+part+r'-[0-9]+\..*'
match_string_part = directory + prefix+'-[0-9]+-'+part+r'-([0-9]+)\..*'

# make outputfile
outputfile = directory + '/' + prefix + '-' + str(int(timenow)) + '-part-%03d.pnm'

# run scan command
[out,err,processhandle] = run_scancommand(device,outputfile,width=width,height=height,logfile=lfile,debug=debug,mode=mode,resolution=resolution,batch=True,batchstart='1',batchincrement='1')

os.system('sleep 3')
try:
    files = filelist('ls ' + directory + prefix + '-' + str(int(timenow)) + '-part-*.pnm')
except:
    display("error in ls; probably no scanned files found. check permissions and/or pathname.")

# find number of files by scanning the part number of the last file.
# assumes that the list is sorted.
number_scanned = file_part(files[-1],match_string_part)

if debug:
    display("number_scanned: " + str(number_scanned),logfile=lfile)

# wait for a time proportional to the number scanned
convert_to_pdf(directory=directory,outputtype='pdf',wait=int(number_scanned/3.0),debug=debug,logfile=lfile)

# find newly converted files
convertedfiles = filelist('ls ' + directory + prefix + '-' + str(int(timenow)) + '-part-*.pdf')

# make a filelist and output filename to pdftk
compiled_pdf_filename = directory + prefix + '-' + today + '-' + str(int(time.time())) + '.pdf'

run_pdftk(convertedfiles,compiled_pdf_filename,debug=debug,logfile=lfile)

# make the files owned by a certain somebody
run_chown(ownedby,compiled_pdf_filename,debug=debug,logfile=lfile)

