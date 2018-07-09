#!/usr/bin/python3

# Objectives: scan single sided files. convert to pdf. 

import os,sys,re,time,datetime,subprocess
import logging,traceback
from scanutils import *

# SETTINGS
part = 'part'
ownedby = 'arjun:szhao'
timeoffset = 5*60 # in seconds
as_script = False
debug = True 
default_logdir = '/tmp' + r'brscan/'
default_outdir = '/tmp' + r'brscan/'
waitlimit = 300 # a limit for waiting to fix errors
today = datetime.date.today().isoformat() 

def parse_arguments():
    global default_outdir,default_logdir

    # argument list
    parser = argparse.ArgumentParser(description='Process arguments for single and double sided scan')
    # else take options from command line
    parser.add_argument('--outputdir',nargs='?',action='store',default=default_outdir,const=default_outdir)
    parser.add_argument('--logdir',nargs='?',action='store',default=default_logdir,const=default_logdir)
    parser.add_argument('--prefix',nargs='?',action='store',default='brscan',const='brscan')
    parser.add_argument('--timenow',nargs='?',type=int,action='store',const=int(time.time()),default=int(time.time()))
    parser.add_argument('--device-name',nargs='?',action='store',const=None,default=None)
    #parser.add_argument('--device_name',nargs='?',action='store',const=1,default=1)
    parser.add_argument('--resolution',nargs='?',action='store',default='300',const='300')
    parser.add_argument('--height',nargs='?',action='store',default='290',const='290')
    parser.add_argument('--width',nargs='?',action='store',default='215.88',const='215.88')
    parser.add_argument('--mode',nargs='?',action='store',default=None,const=None)
    #parser.add_argument('--mode',action='store',default = 'Black & White')
    parser.add_argument('--source',nargs='?',action='store',default=None,const=None)
    # by default, its not in double mode.
    parser.add_argument('--duplex',nargs='?',action='store',default=None,const='manual')
    # requires exactly one argument, but this not set by nargs
    # duplextype takes auto and manual. 
    parser.add_argument('--duplextype',action='store',default='auto')
    # it's not a dry-run by default.
    parser.add_argument('--dry-run',action='store_true',default=False)
    args,unknown = parser.parse_known_args()

    # process options.
    if not args.device_name:
        if debug:
            logprint('No device name set. Trying to automatically find default device')
        args.device_name = get_default_device()

    # check logdir and outputdir, and then normalize the paths
    if not os.path.exists(args.logdir):
        if debug:
            logprint('Log directory ',args.logdir,' does not exist. Creating.')
        os.makedirs(args.logdir)
    # normalize name so that its easy to find
    args.logdir = os.path.normpath(args.logdir)

    if not os.path.exists(args.outputdir):
        if debug:
            logprint('Output directory ',args.outputdir,' does not exist. Creating.')
        os.makedirs(args.outputdir)
    # normalize name so that its easy to find
    args.outputdir = os.path.normpath(args.outputdir)

    # if args.duplex is passed, look at duplextype 
    # if duplextype is auto, then look for duplex source. If it's empty
    # choose something automatically from the driver. If it's set, use it.
    # if duplextype is manual, then again look for duplex source. If it's empty, leave it unset.
    # this is because if it's done manually, then the source does not really matter.
    if args.duplex:
        # command line option seen first
        if not args.source:
            if args.duplextype == 'auto':
                args.source = get_default_duplex_source()

    return args

# SCRIPT START
print("\n",today," Starting ", sys.argv[0]," at",time.time())

# see if run as a script. as_script needed to parse arguments correctly.
# I dont think this is needed anymore.
if not re.match(r'/usr/bin/.*python.*',sys.argv[0]):
    as_script = True

# read arguments 
args = parse_arguments()

# if debug, logprint parsed arguments
if debug:
    logprint('parsed arguments:',args)

# set logdir. 
try:
    # debugging
    if debug:
        logprint('log directory: ',args.logdir)

    logfile_name = args.logdir + 'single-sided-scan.log'

    logfile = open(logfile_name,'a')
except:
    logprint("Error creating logdir")
    logging.exception("Error creating logdir")
    traceback.print_exc(file=sys.stdout)

# print parameters and arguments on debug
if debug:
    logprint('outputdir = ', args.outputdir + ' prefix = ' + args.prefix + '. timenow = ' + str(args.timenow) + '\n')
    logprint('arguments = ', sys.argv)

# set filename matchstring regular expressions
match_string_time = args.outputdir + '/' + args.prefix+'-([0-9]+)-'+part+r'-[0-9]+\..*'
match_string_part = args.outputdir + '/' + args.prefix+'-[0-9]+-'+part+r'-([0-9]+)\..*'

if debug:
    logprint('Look for scanned files of the following form (regex): ', match_string_part)

if args.duplex == 'manual':
    # then run complex double sided scanning routines.

    logprint('Running duplex mode = ', args.duplex)

    # find all files in directory
    try:
        cmd = 'ls ' + args.outputdir + '/' + args.prefix + '*-part-*.pdf'
        # filelist function ensures that a list is returned
        files = filelist(cmd)
    except:
        # ls might not find any files
        files = []
        logprint("\nNo close by files found\n")

    # find files close in creation time (specified by timeoffset) to other files in the directory
    # files close will contain a list of tuples containing (filetime, part number, filename)
    filesclose = files_within_timeoffset(files,match_string_time,match_string_part,args.timenow,timeoffset,debug=debug)
    if debug:
        logprint('files found = ',files,'filesclose = ',filesclose,'match_string_part = ',match_string_part)

    # determine whether to run odd or even; if even, also find the  max part number of the file. 
    (output,maxpart) = oddoreven_and_maxpart_number(filesclose,debug=debug)

    # run scanner command
    outputfile = args.outputdir + '/' + args.prefix + '-' + str(args.timenow) + '-part-%03d.pnm'
    if output == 'run_odd':
        logprint('Scanning odd pages')
        [out,err,processhandle] = run_scancommand(args.device_name,outputfile,width=args.width,height=args.height,logfile=logfile,debug=debug,mode=args.mode,resolution=args.resolution,batch=True,batch_start='1',batch_increment='2',source=args.source,dry_run=args.dry_run)
    else: # output == 'run_even'if
        # if no even files found within 5 minutes of each other
        # really these arguments to scancommand should not do type conversion for
        # the numerican arguments. to fix.
        logprint('Scanning even pages')

        [out,err,processhandle] = run_scancommand(args.device_name,outputfile,width=args.width,height=args.height,logfile=logfile,debug=debug,mode=args.mode,resolution=args.resolution,batch=True,batch_start=str(maxpart+1),batch_increment='-2',dry_run=args.dry_run)

    if not args.dry_run:
        # convert files to pdf
        # implement wait limit here. use subprocess.wait for a process to finish.
        # otherwise this thing crashes. run_scancommand should return a subprocess
        # handle so you can wait for it 
        processhandle.wait()
        cmd = 'ls ' + args.outputdir + '/' + args.prefix + '-' + str(args.timenow) + '-part-*.pnm'
        files = filelist(cmd)

        if debug:
            logprint('Scanned files: ', files)
        # find number of files by scanning the part number of the last file.
        # assumes that the list is sorted.
        if debug:
            logprint('Debugging file_part: ', files[-1],match_string_part)
        number_scanned = file_part(files[-1],match_string_part)

        if debug:
            logprint("number_scanned: " + str(number_scanned))

        # wait for a specified time before trying to convert each file.
        newfiles = convert_to_pdf(filelist,wait=0,debug=debug,logfile=logfile)

        # find newly converted files
        # newfiles = filelist('ls ' + args.outputdir +  '/' + args.prefix + '-' + str(args.timenow) + '-part-*.pdf')

        # make a filelist and output filename to pdftk
        if output == 'run_odd':
            # compile the odd pages into a single pdf
            compiled_pdf_filename = args.outputdir +  '/' + args.prefix + '-' + today + '-' + str(int(time.time())) + '-odd.pdf'
            filestopdftk = newfiles

            # write filelist to outputdir
            # to be used for new odd/even mechanism in the future.
            tf = open(args.outputdir + '/.scantoocr-odd-filelist','w')
            tf.write(str(newfiles))
        elif output == 'run_even':
           # if scanned even parts, and hence max part number is bigger than 1
           # even files are automatically numbered in reverse by the scancommand.
           oldfiles = [x[2] for x in filesclose]
           oldfiles.sort() #newfiles should be sorted already
           # new files have been ensured to be in sorted order.
           # interleave two lists, nested for loops
           allfiles = interleave_lists(oldfiles,newfiles)
           if debug:
               logprint('filelist: ' , allfiles)
           # ensures that the filename for compiled pdf is unique
           compiled_pdf_filename = args.outputdir +  '/' + args.prefix + '-' + today + '-' + str(int(time.time())) + '.pdf'
           filestopdftk = allfiles

        run_pdftk(filestopdftk,compiled_pdf_filename,debug=debug,logfile=logfile)

        # make the files owned by certain somebody
        if ownedby:
            subprocess.Popen(['chown',ownedby,compiled_pdf_filename])

    #close logfile
    logfile.close() 


else: # if not (double sided and manual double scanning) simply run single sided scanning routine
    # in case we have args.duplex and args.duplextype = 'manual'
    # make outputfile

    logprint('Running in single side mode or --duplex="auto"')

    # run scan command
    outputfile = args.outputdir + '/' + args.prefix + '-' + str(int(args.timenow)) + '-part-%03d.pnm'
    [out,err,processhandle] = run_scancommand(args.device_name,outputfile,width=args.width,height=args.height,logfile=logfile,debug=debug,mode=args.mode,resolution=args.resolution,batch_start='1',batch_increment='1',source=args.source,dry_run=args.dry_run)

    # see if files have been created.
    if not args.dry_run:
        processhandle.wait()
        try:
            cmd = 'ls ' + args.outputdir + '/' + args.prefix + '-' + str(int(args.timenow)) + '-part-*.pnm'
            if debug:
                logprint('Command to find scanned files',cmd)
            files = filelist(cmd)

            if debug:
                logprint('Scanned files: ', files)
        except:
            logprint("error in ls; probably no scanned files found. check permissions and/or pathname.")

        # find number of files by scanning the part number of the last file.
        # assumes that the list is sorted.
        # why is len(files) not sufficient? To rewrite this section.
        try:
            if debug:
                logprint('Debugging file_part: ', files[-1],match_string_part)
            number_scanned = file_part(files[-1],match_string_part)
        except:
            number_scanned = 0
            logprint("Error determining number of files scanned")

        if debug:
            logprint("number_scanned: " + str(number_scanned))

        if number_scanned > 0:
            # wait for a time proportional to the number scanned
            # waiting is builtin to convert_to_pdf
            convertedfiles = convert_to_pdf(files,wait=0,debug=debug,logfile=logfile)

            # find newly converted files
            #convertedfiles = filelist('ls ' + args.outputdir + '/' + args.prefix + '-' + str(int(args.timenow)) + '-part-*.pdf')

            # make a filelist and output filename to pdftk
            compiled_pdf_filename = args.outputdir + '/' + args.prefix + '-' + today + '-' + str(int(time.time())) + '.pdf'

            run_pdftk(convertedfiles,compiled_pdf_filename,debug=debug,logfile=logfile)

        # make the files owned by a certain somebody
        if ownedby:
            subprocess.Popen(['chown',ownedby,compiled_pdf_filename])
