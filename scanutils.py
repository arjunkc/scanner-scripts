# Apr 03 2017 Copyright Arjun Krishnan, distributed under GNU Public License
# Bunch of scanner utilities that allow double sided scanning from an auto
# To be imported as a module

import os,sys,re,time,datetime,subprocess

# define a function that takes in a list of files, and returns a list of files with timestamps that are within timeoffset 

def Usage(as_script):
    if as_script:
        sys.stdout.write("Usage:\n")
        sys.stdout.write("\tevenorodd.py <directory name> <fileprefix=brscan> <time in seconds from epoch>\n")
        sys.stdout.flush()

def display(*s,as_script=False,logfile=None):
    # display string with the correct function.
    if as_script:
        if logfile==None:
            logfile=open('/tmp/brscan.log','a')
        print(*s,file=logfile)
        logfile.flush()
    else:
        print(*s)

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
    if batch:
        scancommand=['scanimage','-v','-v','-p','--device-name',device,'--mode',mode,'--resolution',resolution,'-x',width,'-y',height,'--batch='+outputfile,'--batch-start',batchstart,'--batch-increment',batchincrement]
        run = subprocess.Popen(scancommand)
    else:
        scancommand=['scanimage','-v','-v','-p','--device-name',device,'--mode',mode,'--resolution',resolution,'-x',width,'-y',height]
        try:
            outfile_handle = open(outputfile,'w')
        except:
            display("Error opening outputfile",logfile=logfile)
        # when run this way, the outfile_handle contains the part- something. Can't be helped.
        run = subprocess.Popen(scancommand,stdout=outfile_handle)
    if debug:
        if logfile == None:
            logfile = open('/tmp/brscan.log','a')
        display('scancommand: ', scancommand,logfile=logfile)
    out,err = run.communicate()
    return out,err

def convert_to_pdf(directory='/home/arjun/brscan/documents/',outputtype='pdf',wait=10,debug=False):
    os.system('sleep ' + str(wait))
    os.system('chown arjun:szhao ' + directory + '/*')
    cmd = ['/home/arjun/bin/misc_scripts/convert-compress-delete','-t',"pdf",'-d',directory,'-y']
    run = subprocess.Popen(cmd)
    if debug:
        out,err = run.communicate()
        display("conversion command: ", cmd)
        display(out,err)
    # wait for process to return
    run.wait()


def run_pdftk(filestopdftk,outputfile,debug=False,logfile=None):
    # files to pdftk is a list of strings
    if logfile==None:
        logfile = open('/tmp/brscan.log','a')
    pdftkcommand = ['pdftk'] + filestopdftk + ['cat','output',outputfile]
    if debug:
       print("output filename: ", outputfile)
    display("\npdftkcommand: " , pdftkcommand,logfile=logfile)
    run = subprocess.Popen(pdftkcommand)
    out,err = run.communicate()
    display("pdftkcommand errors: " ,err,logfile=logfile)


 
