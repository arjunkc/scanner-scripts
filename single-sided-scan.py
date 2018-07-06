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
default_logdir = os.environ.get('HOME') + r'brscan/'
default_outdir = os.environ.get('HOME') + r'brscan/'
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
    parser.add_argument('--duplex',action='store_true')
    # requires exactly one argument, but this not set by nargs
    # duplextype takes auto and manual. 
    parser.add_argument('--duplextype',action='store',default='auto')
    # it's not a dry-run by default.
    parser.add_argument('--dry-run',action='store_true',default=False)
    args,unknown = parser.parse_known_args()

    # process options.
    if not args.device_name:
        if debug:
            display('No device name set. Trying to automatically find default device')
        args.device_name = get_default_device()

    # check logdir and outputdir, and then normalize the paths
    if not os.path.exists(args.logdir):
        if debug:
            display('Log directory ',args.logdir,' does not exist. Creating.')
        os.makedirs(args.logdir)
        # normalize name so that its easy to find
        args.logdir = os.path.normpath(args.logdir)

    if not os.path.exists(args.outputdir):
        if debug:
            display('Output directory ',args.outputdir,' does not exist. Creating.')
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

# if debug, display parsed arguments
if debug:
    display('parsed arguments:',args)

# set logdir. 
try:
    # debugging
    if debug:
        display('log directory: ',args.logdir)

    logfile = args.logdir + 'single-sided-scan.log'

    logfile_handle = open(logfile,'a')
except:
    display("Error creating logdir")
    logging.exception("Error creating logdir")
    traceback.print_exc(file=sys.stdout)

# print parameters and arguments on debug
if debug:
    display('outputdir = ', args.outputdir + ' prefix = ' + args.prefix + '. timenow = ' + str(args.timenow) + '\n',logfile=logfile_handle)
    display('arguments = ', sys.argv,logfile=logfile_handle)

# set filename matchstring regular expressions
match_string_time = args.outputdir + '/' + args.prefix+'-([0-9]+)-'+part+r'-[0-9]+\..*'
match_string_part = args.outputdir + '/' + args.prefix+'-[0-9]+-'+part+r'-([0-9]+)\..*'

if debug:
    display('Look for scanned files of the following form (regex): ', match_string_part)

if args.duplex and args.duplextype == 'manual':
    # then run complex double sided scanning routines.

    # find all files in directory
    try:
        files = filelist('ls ' + args.outputdir + '/' + args.prefix + '*-part-*.pdf')
    except:
        # ls might not find any files
        files = []
        if debug:
            display("\nNo close by files found\n",logfile=logfile_handle)

    # find files close in creation time (specified by timeoffset) to other files in the directory
    # files close will contain a list of tuples containing (filetime, part number, filename)
    filesclose = files_within_timeoffset(files,match_string_time,match_string_part,args.timenow,timeoffset,debug=debug)
    if debug:
        display(files,filesclose,logfile=logfile_handle)

    # determine whether to run odd or even; if even, also find the  max part number of the file. 
    (output,maxpart) = oddoreven_and_maxpart_number(filesclose,debug=debug)

    # run scanner command
    outputfile = args.outputdir + '/' + args.prefix + '-' + str(args.timenow) + '-part-%03d.pnm'
    if output == 'run_odd':
        [out,err,processhandle] = run_scancommand(args.device_name,outputfile,width=args.width,height=args.height,logfile=logfile_handle,debug=debug,mode=args.mode,resolution=args.resolution,batch=True,batch_start='1',batch_increment='2',source=args.source,dry_run=args.dry_run)
    else: # output == 'run_even'if
        # if no even files found within 5 minutes of each other
        # really these arguments to scancommand should not do type conversion for
        # the numerican arguments. to fix.
        [out,err,processhandle] = run_scancommand(args.device_name,outputfile,width=args.width,height=args.height,logfile=logfile_handle,debug=debug,mode=args.mode,resolution=args.resolution,batch=True,batch_start=str(maxpart+1),batch_increment='-2',dry_run=args.dry_run)

    if not args.dry_run:
        # convert files to pdf
        # implement wait limit here. use subprocess.wait for a process to finish.
        # otherwise this thing crashes. run_scancommand should return a subprocess
        # handle so you can wait for it 
        os.system('sleep 3')
        run = filelist('ls ' + args.outputdir + '/' + args.prefix + '-' + str(args.timenow) + '-part-*.pnm')
        # find number of files by scanning the part number of the last file.
        # assumes that the list is sorted.
        number_scanned = file_part(run[-1],match_string_part)
        if debug:
            display("number_scanned: " + str(number_scanned),logfile=logfile_handle)

        # wait for a time proportional to the number scanned
        convert_to_pdf(directory=args.outputdir,outputtype='pdf',wait=int(number_scanned/3.0),debug=debug,logfile=logfile_handle)

        # find newly converted files
        newfiles = filelist('ls ' + args.outputdir +  '/' + args.prefix + '-' + str(args.timenow) + '-part-*.pdf')

        # make a filelist and output filename to pdftk
        if output == 'run_odd':
            compiled_pdf_filename = args.outputdir +  '/' + args.prefix + '-' + today + '-' + str(int(time.time())) + '-odd.pdf'
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
           compiled_pdf_filename = args.outputdir +  '/' + args.prefix + '-' + today + '-' + str(int(time.time())) + '.pdf'
           filestopdftk = allfiles

        run_pdftk(filestopdftk,compiled_pdf_filename,debug=debug,logfile=logfile_handle)

        # make the files owned by certain somebody
        if not ownedby:
            subprocess.Popen(['chown',ownedby,compiled_pdf_filename])

    #close logfile
    logfile_handle.close() 


else: # simply run single sided scanning routine
    # in case we have args.duplex and args.duplextype = 'manual'
    # make outputfile
    outputfile = args.outputdir + '/' + args.prefix + '-' + str(int(args.timenow)) + '-part-%03d.pnm'

    # run scan command
    [out,err,processhandle] = run_scancommand(args.device_name,outputfile,width=args.width,height=args.height,logfile=logfile_handle,debug=debug,mode=args.mode,resolution=args.resolution,batch_start='1',batch_increment='1',source=args.source,dry_run=args.dry_run)

    # see if files have been created.
    if not args.dry_run:
        os.system('sleep 3')
        try:
            files = filelist('ls ' + args.outputdir + '/' + args.prefix + '-' + str(int(args.timenow)) + '-part-*.pnm')
            if debug:
                display('files scanned after 3 seconds: ',files)
        except:
            display("error in ls; probably no scanned files found. check permissions and/or pathname.")

        # find number of files by scanning the part number of the last file.
        # assumes that the list is sorted.
        if len(files) > 0:
            number_scanned = file_part(files[-1],match_string_part)
        else:
            number_scanned = 0

        if debug:
            display("number_scanned: " + str(number_scanned),logfile=logfile_handle)

        if number_scanned > 0:
            # wait for a time proportional to the number scanned
            convert_to_pdf(outputdir=args.outputdir,outputtype='pdf',wait=int(number_scanned/3.0),debug=debug,logfile=logfile_handle)

            # find newly converted files
            convertedfiles = filelist('ls ' + args.outputdir + '/' + args.prefix + '-' + str(int(args.timenow)) + '-part-*.pdf')

            # make a filelist and output filename to pdftk
            compiled_pdf_filename = args.outputdir + '/' + args.prefix + '-' + today + '-' + str(int(time.time())) + '.pdf'

            run_pdftk(convertedfiles,compiled_pdf_filename,debug=debug,logfile=logfile_handle)

            # make the files owned by a certain somebody
            run_chown(ownedby,compiled_pdf_filename,debug=debug,logfile=logfile_handle)
