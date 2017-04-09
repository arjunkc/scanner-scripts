#!/usr/bin/python3
# take in directory, prefix and a current time
# get a list of files within five minutes.
# for each found file, determine if both even and odd completed.
# if completed, then return odd
# if not completed, then return even and the timestamp of the odds
# Usage: evenorodd.py '/home/arjun/brscan' 'brscan' `date '+%s'`
# Dec 31 2016 To do, finish the scanning and converting into a single file part.
# Jan 11 2017 perhaps a fairly fail-safe system would be to create a compilation file with all the pdfs produces so far called odd, and one called even. Then even if you don't copy the even parts, the odd parts will be compiled. 
# Jan 11 2017 seems to be working now

import os,sys,re,time,datetime,subprocess

from scanutils import *

# SETTINGS
part = 'part'
timeoffset = 5*60 # in seconds
as_script = False
debug = True 
logfile = '/home/arjun/brscan/brscan-skey.log'
lfile = open(logfile,'a')

if not re.match(r'/usr/bin/.*python.*',sys.argv[0]):
    as_script = True

# SCRIPT START
# read arguments 
# see if run as a script
# READ ARGUMENTS
if not as_script:
    directory = r'/home/arjun/brscan/documents/'
    prefix = 'brscan'
    timenow = time.time()
    device = 'brother4:net1;dev0'
    resolution = '300'
    # 11 inches is 279.40mm. 290 is about 11.4 inches to capture longer paper.
    height = '290'
    width = '215.88'
    mode = 'Black & White'
elif len(sys.argv) != 9:
    # check number of command line options
    display("need arguments for directory, prefix, timenow, device, resolution, height, width\n",as_script=as_script,logfile=lfile)
    display("arguments ",sys.argv,"\n",as_script=as_script,logfile=lfile)
    Usage(as_script)
    # return bad exit status
    sys.exit(1)
else:
    # else take options from command line
    directory = sys.argv[1]
    prefix = sys.argv[2]
    timenow = int(sys.argv[3])
    device = sys.argv[4]
    resolution = sys.argv[5]
    height = sys.argv[6]
    width = sys.argv[7]
    mode = sys.argv[8]

# print parameters and arguments on debug
if debug:
    display(directory + ' prefix = ' + prefix + '. timenow = ' + str(timenow) + '\n',as_script=as_script,logfile=lfile)
    display('timeoffset = ' + str(timeoffset),as_script=as_script,logfile=lfile)
    display('arguments = ', sys.argv)

# set filename matchstring regular expressions
match_string_time = directory + prefix+'-([0-9]+)-'+part+r'-[0-9]+\..*'
match_string_part = directory + prefix+'-[0-9]+-'+part+r'-([0-9]+)\..*'

# find all files in directory
try:
    files = subprocess.check_output('ls ' + directory + prefix + '*-part-*.pdf',shell=True)
    files = files.decode().split('\n')
except:
    # ls might not find any files
    files = []
    if debug:
        display("\nNo close by files found\n",as_script=as_script,logfile=lfile)

# find files close in creation time (specified by timeoffset) to other files in the directory
# files close will contain a list of tuples containing (filetime, part number, filename)
filesclose = files_within_timeoffset(files,match_string_time,match_string_part,timenow,timeoffset,debug=debug)
if debug:
    display(files,filesclose,as_script=as_script,logfile=lfile)

# determine whether to run odd or even; if even, also find the  max part number of the file. 
(output,maxpart) = oddoreven_and_maxpart_number(filesclose,debug=debug)

# run scanner command
outputfile = directory + '/' + prefix + '-' + str(int(timenow)) + '-part-%03d.pnm'
if output == 'run_odd':
    run_scancommand(device,outputfile,width=width,height=height,logfile=lfile,debug=debug,mode=mode,resolution=resolution,batch=True,batchstart='1',batchincrement='2',)
else:
    # if no even files found within 5 minutes of each other
    #scancommand=['scanimage','-v','-v','-p','--device-name',device,'--mode',mode,'--resolution',resolution,'-x','-y',height,'--batch='+output_file,'--batch-start',str(maxpart + 1),'--batch-increment','-2']
    run_scancommand(device,outputfile,width=width,height=height,logfile=lfile,debug=debug,mode=mode,resolution=resolution,batch=True,batchstart=str(maxpart+1),batchincrement='2')

# convert files to pdf
os.system('sleep 3')
run = subprocess.check_output('ls ' + directory + prefix + '-' + str(int(timenow)) + '-part-*.pnm',shell=True)
# decode the string, make a list of files and a string
number_scanned = file_part(run.decode().split('\n')[-2],match_string_part)
if debug:
    display("number_scanned: " + str(number_scanned),as_script=as_script,logfile=lfile)

# wait for a time proportional to the number scanned
convert_to_pdf(directory=directory,outputtype='pdf',wait=int(number_scanned/3.0),debug=debug)

# find newly converted files
run = subprocess.check_output('ls ' + directory + prefix + '-' + str(int(timenow)) + '-part-*.pdf',shell=True)
# decode and split into list, then remove last blank entry
newfiles = run.decode().split('\n')[0:-1]
newfile_string = run.decode().replace('\n',' ')

# make a filelist and output filename to pdftk
if output == 'run_odd':
    compiled_pdf_filename = directory + prefix + '-' + datetime.date.today().isoformat() + '-' + str(int(time.time())) + '-odd.pdf'
    filestopdftk = newfiles
elif output == 'run_even':
   # if scanned even parts, and hence max part number is bigger than 1
   oldfiles = [x[2] for x in filesclose]
   oldfiles.sort() #newfiles should be sorted already
   # interleave two lists, nested for loops
   # new files will have to be reversed If you scan the odd pages, turn the
   # document around, and then scan the even pages with the last even page as
   # the first page.
   newfiles.reverse()
   # the new files
   allfiles = [ val for pair in zip(oldfiles,newfiles) for val in pair]
   #if debug:
       #display('filelist: ' , allfiles,as_script=as_script,logfile=lfile)
   # ensures that the filename is unique
   compiled_pdf_filename = directory + prefix + '-' + datetime.date.today().isoformat() + '-' + str(int(time.time())) + '.pdf'
   filestopdftk = allfiles

run_pdftk(filestopdftk,compiled_pdf_filename,debug=debug,logfile=lfile)
lfile.close() #close logfile
