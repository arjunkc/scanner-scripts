# Apr 03 2017 Copyright Arjun Krishnan, distributed under GNU Public License
# Bunch of scanner utilities that allow double sided scanning from an auto
# To be imported as a module

import os,sys,re,time,datetime,subprocess

# define a function that takes in a list of files, and returns a list of files with timestamps that are within timeoffset 

def Usage(as_script):
    if as_script:
        sys.stdout.write("Usage:\n")
        sys.stdout.write("\t" + sys.argv[0] + "<directory name> <fileprefix=brscan> <time in seconds from epoch> <etc>\n")
        sys.stdout.flush()

def display(*s,logfile=None):
    # display string with the correct function.
    if logfile==None:
        logfile=open('/tmp/brscan.log','a')
    print(*s,file=logfile)
    logfile.flush()

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
        if debug and xtime!= None:
            display('xtime = ' + str(xtime) + '. part number = ' + str(partno) + '\n')
            #display('type xtime = ' + str(type(xtime)) + '. type timenow = ' + str(type(timenow)) + '. type timeoffset = ' + str(type(timeoffset)) + '\n')
        if xtime != None:
            if abs(xtime - timenow) <= timeoffset:
                if debug:
                    display('match = ' +str((xtime,partno,x) ) )
                matches.append((xtime,partno,x))

    if len(matches) > 0:
        # if any matches are found
        matches.sort(reverse=True) # will sort by first integer key, by default. it appears to work correctly
        # return list of most recent matches
        matches = [ x for x in matches if x[0] == matches[0][0] ]
    # matches is a 3-tuple containing, (filetime, part number, filename)
    return matches

def filelist(globbing_pattern,logfile=None):
    if logfile==None:
        logfile = open('/tmp/brscan.log','a')
    # logfile implementation untested
    run = subprocess.check_output(globbing_pattern,shell=True,stderr=logfile)
    return run.decode().split('\n')[0:-1]

def interleave_lists(l1,l2):
    # will interleave upto the shorter of the lengths of l1 and l2
    return [ val for pair in zip(l1,l2) for val in pair]

# parsing arguments, setting default ones

def parse_arguments(as_script,args):
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
    elif len(args) != 9:
        # check number of command line options
        display("need arguments for directory, prefix, timenow, device, resolution, height, width\n",logfile=lfile)
        display("arguments ",args,"\n",logfile=lfile)
        Usage(as_script)
        # return bad exit status
        sys.exit(1)
    else:
        # else take options from command line
        directory = args[1]
        prefix = args[2]
        timenow = int(args[3])
        device = args[4]
        resolution = args[5]
        height = args[6]
        width = args[7]
        mode = args[8]
    return [directory,prefix,timenow,device,resolution,height,width,mode]

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
        display(output,"maximum part number = ",maxpart+1)
    return (output,maxpart)

def run_scancommand(device,outputfile,width='215.88',height='279.4',mode='Black & White',resolution='300',batch=False,batchstart='1',batchincrement='1',debug=False,logfile=None):
    print("Running scanimage")
    if batch:
        scancommand=['scanimage','-v','-v','-p','--device-name',device,'--mode',mode,'--resolution',resolution,'-x',width,'-y',height,'--batch='+outputfile,'--batch-start',batchstart,'--batch-increment',batchincrement]
        run = subprocess.Popen(scancommand,stdout=logfile,stderr=logfile)
    else:
        scancommand=['scanimage','-v','-v','-p','--device-name',device,'--mode',mode,'--resolution',resolution,'-x',width,'-y',height]
        try:
            outfile_handle = open(outputfile,'w')
        except:
            display("Error opening outputfile",logfile=logfile)
        # when run without --batch, scanimage writes image date directly to
        # stdout. So we have to capture the stdout of a scancommand directly in
        # the outputfile handle
        run = subprocess.Popen(scancommand,stdout=outfile_handle,stderr=logfile)
    if debug:
        if logfile == None:
            logfile = open('/tmp/brscan.log','a')
        display('scancommand: ', scancommand,logfile=logfile)
    out,err = run.communicate()
    return out,err,run

def convert_to_pdf(directory='/home/arjun/brscan/documents/',outputtype='pdf',wait=10,debug=False,logfile=None):
    print("Converting raw scanned files to " + outputtype)
    os.system('sleep ' + str(wait))
    os.system('chown arjun:szhao ' + directory + '/*')
    cmd = ['/home/arjun/bin/misc_scripts/convert-compress-delete','-t',"pdf",'-d',directory,'-y']
    run = subprocess.Popen(cmd,stdout=logfile,stderr=logfile)
    if debug:
        out,err = run.communicate()
        display("conversion command: ", cmd,logfile=logfile)
        display(out,err,logfile=logfile)
    # wait for process to return
    run.wait()

def run_pdftk(filestopdftk,outputfile,debug=False,logfile=None):
    print("Compiling pdf file using pdftk")
    # files to pdftk is a list of strings
    if logfile==None:
        logfile = open('/tmp/brscan.log','a')
    pdftkcommand = ['pdftk'] + filestopdftk + ['cat','output',outputfile]
    if debug:
       display("output filename: ", outputfile,logfile=logfile)
    display("\npdftkcommand: " , pdftkcommand,logfile=logfile)
    run = subprocess.Popen(pdftkcommand,stdout=logfile,stderr=logfile)
    out,err = run.communicate()
    display("pdftkcommand errors: " ,err,logfile=logfile)



 
