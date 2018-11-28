# Apr 03 2017 Copyright Arjun Krishnan, distributed under GNU Public License
# Bunch of scanner utilities that allow double sided scanning from an auto
# To be imported as a module

import os,sys,re,time,datetime,subprocess
import argparse,traceback

# define a function that takes in a list of files, and returns a list of files with timestamps that are within timeoffset 

def Usage(as_script):
    if as_script:
        sys.stdout.write("Usage:\n")
        sys.stdout.write("\t" + sys.argv[0] + "<outputdir name> <fileprefix=brscan> <time in seconds from epoch> <etc>\n")
        sys.stdout.flush()

global debug,logfile

#def logprint(*s,logfile=None,debug=False):
def logprint(*s):
    # display string with the correct function.
    '''
    prints to global variable defined by logfile
    if not found prints to stdout

    if debug is set, will always print to stdout
    '''

    global logfile,debug

    try:
        # will throw exception is logfile not found globally, I guess
        if logfile:
            print(*s,file=logfile)
            logfile.flush()
            if debug:
                print(*s)
        else:
            print('logfile is none')
            # if logfile is None, simply output to stdout
            print(*s)
    except:
        # if something fails, simply output to stdout
        print("Error writing to logfile")
        print(*s)
        if debug:
            traceback.print_exc(file=sys.stdout)
        

# file name handling functions
def file_time(filename,match_string_time):
    #takes in a string representing a filename in the format
    # directory-prefix-epoch-part-number.pnm
    try:
        return int(re.sub(match_string_time,r'\1',filename))
    except:
        return None

def file_part(filename,match_string_part):
    #takes in a string representing a filename and returns part
    # directory-prefix-epoch-part-number.pnm
    try:
        return int(re.sub(match_string_part,r'\1',filename))
    except:
        # if not found
        return None

def files_within_timeoffset(l,match_string_time,match_string_part,timenow,timeoffset,debug=False):
    # l is a list of files, timenow is an epoch, timeoffset is the time within timenow to find files. all times in seconds
    # returns a list of tuples (filetime,partno,file) of most recent files within five minutes from timenow 
    matches = []
    for x in l:
        # extract time in seconds from file
        xtime = file_time(x,match_string_time)
        partno = file_part(x,match_string_part)
        if debug and xtime != None:
            logprint('xtime = ' + str(xtime) + '. part number = ' + str(partno) + '\n')
            # logprint('type xtime = ' + str(type(xtime)) + '. type timenow = ' + str(type(timenow)) + '. type timeoffset = ' + str(type(timeoffset)) + '\n')
        if xtime != None:
            if abs(xtime - timenow) <= timeoffset:
                if debug:
                    logprint('match = ' +str((xtime,partno,x) ) )
                matches.append((xtime,partno,x))

    if len(matches) > 0:
        # if any matches are found
        matches.sort(reverse=True) # will sort by first integer key, by default. it appears to work correctly
        # return list of most recent matches
        matches = [ x for x in matches if x[0] == matches[0][0] ]
    # matches is a 3-tuple containing, (filetime, part number, filename)
    return matches

def filelist(directory,regex):
    '''
    Returns full pathname of files found matching a particular regular expression

    I was originally using ls to return the full pathname.
    '''
    files = os.listdir(directory)
    if debug:
        logprint('scanutils.filelist: Trying to find',regex,' in ',files)

    matched_files = []
    for f in files:
        if re.match(regex,f):
            matched_files.append(directory + '/' + f)

    # sort filelist. They have been made in such a way so that they will sort part-001,part-002 and so on
    matched_files.sort()

    return matched_files

def interleave_lists(l1,l2):
    # will interleave upto the shorter of the lengths of l1 and l2
    return [ val for pair in zip(l1,l2) for val in pair]

# parsing arguments, setting default ones

def get_default_device():
    """
    runs scanimage -L, and picks the first Brother scanning device on the list
    """
    cmd = subprocess.Popen(['scanimage','-L'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out,err = cmd.communicate()
    # get list of devices
    out = out.decode().split('\n')
    for x in out:
        if re.findall(r'(?i)brother',x):
            # ok a bit inefficient
            dev = re.sub(r"device `([^']*).*",r'\1',x)

    # if dev not set return None
    try:
        dev
        return dev
    except:
        print('No brother device found by script: here is scanimage -L output: ' + out,file=sys.stderr)
        return None

def get_default_duplex_source(device_name):
    cmd = subprocess.Popen(['scanimage','-A','-d',device_name],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out,err = cmd.communicate()
    out = out.decode()
    if re.findall(r'--source',out):
        try:
            if debug:
                logprint('get_default_duplex_source: Found source line in scanimage output.')
        except:
            logprint('debug not defined')
        # scanner sources for paper
        sources = re.sub(r'.*?--source\s*([^\n]*).*',r'\1',out,flags=re.DOTALL).split('|')
        for x in sources:
            if re.findall(r'duplex',x,re.IGNORECASE):
                return x

# odd or even part numbers
def oddoreven_and_maxpart_number(filesclose,debug=False):
    # if some matches are found
    output = 'run_odd'
    maxpart = 1 # default max part number is 1, in case it's run_odd
    if filesclose:
        output = 'run_even'
        for f in filesclose:
            if f[1] % 2 == 0:
               # if one even match is found amongst the most recent files, both even and odd cycles must have been run. This assumes that at least two copies must exist in a batch job
               output = 'run_odd'
               break
        if output == 'run_even':
            maxpart = max( [ x[1] for x in filesclose ] )
    if debug:
        logprint(output,"maximum part number = ",maxpart+1)
    return (output,maxpart)

def run_scancommand(device_name,outputfile,width=None,height=None,mode=None,resolution=None,batch=False,batch_start='1',batch_increment='1',source=None,debug=False,logfile=None,dry_run=False):
    '''
    device_name and outputfile are required options.
    I've removed the batch option. It's always run in batch mode. So even if its just one file from the flatbed, it will scan it batch mode and name it <blah>-part-01.pnm
    '''

    print("Inside run_scancommand, about to run scanimage")
    # args = directory\|logdir\|prefix\|timenow\|device_name\|resolution\|height\|width\|mode\|source
    if debug:
        # -p prints progress
        scancommand = ['scanimage','-v','-v','-p']
    else:
        scancommand = ['scanimage','-v']

    # add outputfile option
    scancommand = scancommand + ['--batch='+outputfile]
    for op in ['device_name','batch_start','batch_increment','resolution','mode','source']:
        # if option is not False or None
        if eval(op):
            # this relies on the option variable name matching the scancommand option name
            scancommand = scancommand + ['--' + op.replace('_','-') , eval(op) ]

    if logfile == None:
        # could also be set in the default options in the function definition, but does not seem to work at the moment. not fully tested.
        logfile = open('/tmp/brscan.log','a')

    # debugging information 
    if debug:
        logprint('scancommand: ', scancommand)

    # run scancommand
    if not dry_run:
        run = subprocess.Popen(scancommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err = run.communicate()
        logprint('scancommand error:', err)
        if debug:
            # output tends to be quite long.
            logprint('scancommand output:', out)
        return out,err,run
    else:
        logprint('Dry run. Not running scancommand.')

    #except:
        #logprint('Error running scancommand')


    # old code, can be deleted. if not run in batch mode, scanimage output must be redirected to stdout.
    # runs scanimage in single page mode with its output going to stdout , which is then redirected to outputfile
    #outfile_handle = open(outputfile,'w')
    #run = subprocess.Popen(scancommand,stdout=outfile_handle,stderr=logfile)

def convert_to_pdf(filelist,wait=0,debug=False,logfile=None,compress=False,img2pdfopts=['--pagesize','Letter','--border','1in:1in']):
    """
    Requires img2pdf and convert from imagemagick

    Send files will full path name. Will convert to pdf using imagemagick convert and img2pdf. 
    
    Uses the default option img2pdf

        '--pagesize','Letter','--border','1in:1in'

    Has an unimplemented compress option. If true, I want convert to convert it to jpg before converting to pdf.

    Assumes file has an extension of the form file.xxx

    """

    logprint("Converting raw scanned files to pdf" )
    if debug:
        logprint('Received filelist to convert:',filelist)

    os.system('sleep ' + str(wait))
    #cmd = ['/home/arjun/bin/misc_scripts/convert-compress-delete','-t',"pdf",'-d',outputdir,'-y']
    #os.system('chown arjun:szhao ' + outputdir + '*')
    converted = []
    err = False
    try:
        for f in filelist:
            if os.path.exists(f):
                if compress:
                    # compress file to jpg
                    jpgf = re.sub(r'\....$',r'.jpg',f)
                    cmd = ['convert','-quality','90','-density','300',f,jpgf]
                    if debug:
                        print(cmd)
                    try:
                        run = subprocess.Popen(cmd,stdout=logfile,stderr=logfile)
                    except:
                        logprint('Error compressing to jpg using convert.')
                        err = True
                        if debug:
                            traceback.print_exc(file=sys.stdout)
                    f = jpgf

                pdff = re.sub(r'\....$',r'.pdf',f)
                cmd = ['img2pdf'] + img2pdfopts + ['-o',pdff,f]
                if debug:
                    print(cmd)

                try:
                    run = subprocess.Popen(cmd,stdout=logfile,stderr=logfile)
                except:
                    err = True
                    logprint('Error creating pdf using img2pdf')
                    if debug:
                        traceback.print_exc(file=sys.stdout)
                if debug:
                    logprint("conversion command: ", cmd)

                # add converted file to filelist
                converted = converted + [pdff]
                # wait for process to return
                run.wait()
    except:
        err = True
        if debug:
            traceback.print_exc(file=sys.stdout)
    if debug:
        logprint('Converted files',converted)

    return err,converted

def run_pdftk(filestopdftk,outputfile,debug=False,logfile=None):
    print("Compiling pdf file using pdftk")
    # files to pdftk is a list of strings
    if logfile==None:
        logfile = open('/tmp/brscan.log','a')
    pdftkcommand = ['pdftk'] + filestopdftk + ['cat','output',outputfile]
    if debug:
       logprint("output filename: ", outputfile)
    logprint("\npdftkcommand: " , pdftkcommand)
    run = subprocess.Popen(pdftkcommand,stdout=logfile,stderr=logfile)
    out,err = run.communicate()
    logprint("pdftkcommand errors: " ,err)

def run_chown(ownedby,outputfile,debug=False,logfile=None):
    if logfile==None:
        logfile = open('/tmp/brscan.log','a')
    if ownedby:
        run = subprocess.Popen(['chown',ownedby,outputfile])
        out,err = run.communicate()
        if debug:
            logprint("chown output,errors",out,err)
        else:
            logprint("ran chown")
    else:
        logprint("ownedby variable not set. not running chown.")
        




 
