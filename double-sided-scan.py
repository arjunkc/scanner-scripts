#!/usr/bin/python3
# take in directory, prefix and a current time
# get a list of files within five minutes.
# for each found file, determine if both even and odd completed.
# if completed, then return odd
# if not completed, then return even and the timestamp of the odds

# To do and notes.
# ~~Dec 31 2016 To do, finish the scanning and converting into a single file
# part.~~
# ~~Jan 11 2017 perhaps a fairly fail-safe system would be to create a
# compilation file with all the pdfs produces so far called odd, and one called
# even. Then even if you don't copy the even parts, the odd parts will be
# compiled.~~
# ~~Jan 11 2017 seems to be working now~~
# ~~Jul 16 2017 Add more functions so that it is easier to combine two sets of
# files. filelist1 = filelist('globbing string'). filelist2 = filelist('globbing
# string'). allfiles = interleave(filelist1,filelist2.reverse()).
# run_pdftk(allfiles,'filename')~~

# Usage: Jul 17 2017
# double-sided-scan.py <directory> <prefix> <timenow> <device> <resolution>
# <height> <width> <mode>
# total of eight required arguments

import os,sys,re,time,datetime,subprocess

from scanutils import *

# SETTINGS
part = 'part'
ownedby = 'arjun:szhao'
timeoffset = 5*60 # in seconds
as_script = False
debug = True 
logfile = '/home/arjun/brscan/double-sided-scan.log'
logfile_handle = open(logfile,'a')
waitlimit = 300 # a limit for waiting to fix errors
today = datetime.date.today().isoformat() 

# SCRIPT START
# read arguments 
# see if run as a script
print("\n",today," Starting script at ", time.time())

if not re.match(r'/usr/bin/.*python.*',sys.argv[0]):
    as_script = True

args = sys.argv
[directory,prefix,timenow,device,resolution,height,width,mode] \
        = parse_arguments(as_script,args)

# print parameters and arguments on debug
if debug:
    display(directory + ' prefix = ' + prefix + '. timenow = ' + str(timenow) + '\n',logfile=logfile_handle)
    # the timeoffset tells you how long to wait between odd and even scans
    display('timeoffset = ' + str(timeoffset),logfile=logfile_handle)
    display('arguments = ', sys.argv)

# set filename matchstring regular expressions
match_string_time = directory + prefix+'-([0-9]+)-'+part+r'-[0-9]+\..*'
match_string_part = directory + prefix+'-[0-9]+-'+part+r'-([0-9]+)\..*'

# find all files in directory
try:
    files = filelist('ls ' + directory + prefix + '*-part-*.pdf')
except:
    # ls might not find any files
    files = []
    if debug:
        display("\nNo close by files found\n",logfile=logfile_handle)

# find files close in creation time (specified by timeoffset) to other files in the directory
# files close will contain a list of tuples containing (filetime, part number, filename)
filesclose = files_within_timeoffset(files,match_string_time,match_string_part,timenow,timeoffset,debug=debug)
if debug:
    display(files,filesclose,logfile=logfile_handle)

# determine whether to run odd or even; if even, also find the  max part number of the file. 
(output,maxpart) = oddoreven_and_maxpart_number(filesclose,debug=debug)

# run scanner command
outputfile = directory + '/' + prefix + '-' + str(int(timenow)) + '-part-%03d.pnm'
if output == 'run_odd':
    [out,err,processhandle] = run_scancommand(device,outputfile,width=width,height=height,logfile=logfile_handle,debug=debug,mode=mode,resolution=resolution,batch=True,batchstart='1',batchincrement='2')
else: # output == 'run_even'if
    # if no even files found within 5 minutes of each other
    # really these arguments to scancommand should not do type conversion for
    # the numerican arguments. to fix.
    [out,err,processhandle] = run_scancommand(device,outputfile,width=width,height=height,logfile=logfile_handle,debug=debug,mode=mode,resolution=resolution,batch=True,batchstart=str(maxpart+1),batchincrement='-2')

# convert files to pdf
# implement wait limit here. use subprocess.wait for a process to finish.
# otherwise this thing crashes. run_scancommand should return a subprocess
# handle so you can wait for it 
os.system('sleep 3')
run = filelist('ls ' + directory + prefix + '-' + str(int(timenow)) + '-part-*.pnm')
# find number of files by scanning the part number of the last file.
# assumes that the list is sorted.
number_scanned = file_part(run[-1],match_string_part)
if debug:
    display("number_scanned: " + str(number_scanned),logfile=logfile_handle)

# wait for a time proportional to the number scanned
convert_to_pdf(directory=directory,outputtype='pdf',wait=int(number_scanned/3.0),debug=debug,logfile=logfile_handle)

# find newly converted files
newfiles = filelist('ls ' + directory + prefix + '-' + str(int(timenow)) + '-part-*.pdf')

# make a filelist and output filename to pdftk
if output == 'run_odd':
    compiled_pdf_filename = directory + prefix + '-' + today + '-' + str(int(time.time())) + '-odd.pdf'
    filestopdftk = newfiles
elif output == 'run_even':
   # if scanned even parts, and hence max part number is bigger than 1
   oldfiles = [x[2] for x in filesclose]
   oldfiles.sort() #newfiles should be sorted already
   # new files have been ensured to be in sorted order.
   # interleave two lists, nested for loops
   allfiles = interleave_lists(oldfiles,newfiles)
   if debug:
       display('filelist: ' , allfiles,logfile=logfile_handle)
   # ensures that the filename for compiled pdf is unique
   compiled_pdf_filename = directory + prefix + '-' + today + '-' + str(int(time.time())) + '.pdf'
   filestopdftk = allfiles

run_pdftk(filestopdftk,compiled_pdf_filename,debug=debug,logfile=logfile_handle)
#close logfile
logfile_handle.close() 

# make the files owned by certain somebody
if not ownedby:
    subprocess.Popen(['chown',ownedby,compiled_pdf_filename])
