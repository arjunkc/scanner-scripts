#!/usr/bin/python3

# Objectives: scan single sided files. convert to pdf. 

import os,sys,re,time,datetime,subprocess
import argparse,logging,traceback

import scanutils

# SETTINGS
part = 'part'
ownedby = 'arjun:szhao'
timeoffset = 5*60 # in seconds
as_script = False
debug = True 
scanutils.debug = debug
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
    # it's not a dry-run by default.
    parser.add_argument('--dry-run',action='store_true',default=False)
    args,unknown = parser.parse_known_args()

    # process options.
    if not args.device_name:
        if debug:
            scanutils.logprint('No device name set. Trying to automatically find default device')
        args.device_name = scanutils.get_default_device()

    # check logdir and outputdir, and then normalize the paths
    if not os.path.exists(args.logdir):
        if debug:
            scanutils.logprint('Log directory ',args.logdir,' does not exist. Creating.')
        os.makedirs(args.logdir)
    # normalize name so that its easy to find
    args.logdir = os.path.normpath(args.logdir)

    if not os.path.exists(args.outputdir):
        if debug:
            scanutils.logprint('Output directory ',args.outputdir,' does not exist. Creating.')
        os.makedirs(args.outputdir)
    # normalize name so that its easy to find
    args.outputdir = os.path.normpath(args.outputdir)

    # if args.duplex is auto, then look for duplex source. If it's empty
    # choose something automatically by running `scanimage -A`. If it's set, use it.
    if args.duplex == 'auto':
        if not args.source:
            args.source = scanutils.get_default_duplex_source()

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
    scanutils.logprint('parsed arguments:',args)

# set logdir. 
try:
    # debugging
    if debug:
        scanutils.logprint('log directory: ',args.logdir)

    logfile_name = args.logdir + '/single-sided-scan.log'

    logfile = open(logfile_name,'a')
    scanutils.logfile = logfile
except:
    scanutils.logprint("Error creating logdir")
    logging.exception("Error creating logdir")
    traceback.print_exc(file=sys.stdout)

# print parameters and arguments on debug
if debug:
    scanutils.logprint('outputdir = ', args.outputdir + ' prefix = ' + args.prefix + '. timenow = ' + str(args.timenow) + '\n')
    scanutils.logprint('arguments = ', sys.argv)

# set filename matchstring regular expressions
match_string_time = args.outputdir + '/' + args.prefix+'-([0-9]+)-'+part+r'-[0-9]+\..*'
match_string_part = args.outputdir + '/' + args.prefix+'-[0-9]+-'+part+r'-([0-9]+)\..*'

# list of odd files
odd_files_name = args.outputdir + '/' + '.' + args.prefix + '-odd-filelist'

if debug:
    scanutils.logprint('Look for scanned files of the following form (regex): ', match_string_part)

if args.duplex == 'manual':
    # then run complex double sided scanning routines.

    scanutils.logprint('Running duplex mode = ', args.duplex)

    # look for off files list
    if os.path.exists(odd_files_name):
        odd_files_list = eval(open(odd_files_name).read())
        scanutils.logprint('Found odd files list')
        if debug:
            scanutils.logprint('They are:',odd_files_list)

        # can be overridden below if checks are failed.
        run_mode = 'run_even'

        # look for file
        oddfiles = []
        for f in odd_files_list:
            if os.path.exists(f):
                oddfiles.append(f)
            else:
                # there is trouble; files missing. i won't do anything.
                scanutils.logprint('There are files missing in the odd files list. Missing file = ',f)
                # write filelist to logfile
                scanutils.logprint('Writing list of saved odd files to log.')
                scanutils.logprint(odd_files_list)
        if len(oddfiles) > 0:
            # the total number of files is of course twice the number of odd files
            maxpart = 2*len(oddfiles) 
        else:
            run_mode = 'run_odd'
            scanutils.logprint('No files exist in odd files list.')
            os.remove(odd_files_name)
         
    else:
        # if no odd filelist found, run in odd mode
        run_mode = 'run_odd'

    # run scanner command
    outputfile = args.outputdir + '/' + args.prefix + '-' + str(args.timenow) + '-part-%03d.pnm'
    if run_mode == 'run_odd':
        scanutils.logprint('Scanning odd pages')

        [out,err,processhandle] = scanutils.run_scancommand(\
                args.device_name,\
                outputfile,\
                width=args.width,\
                height=args.height,\
                logfile=logfile,\
                debug=debug,\
                mode=args.mode,\
                resolution=args.resolution,\
                batch=True,\
                batch_start='1',\
                batch_increment='2',\
                source=args.source,\
                dry_run=args.dry_run)
    else: # run_mode == 'run_even'
        scanutils.logprint('Scanning even pages')

        [out,err,processhandle] = scanutils.run_scancommand(\
                args.device_name,\
                outputfile,\
                width=args.width,\
                height=args.height,\
                logfile=logfile,\
                debug=debug,\
                mode=args.mode,\
                resolution=args.resolution,\
                batch=True,\
                batch_start=str(maxpart),\
                batch_increment='-2',\
                dry_run=args.dry_run)

    # convert files to pdf and concatenate them into one pdf
    if not args.dry_run:
        # convert files to pdf
        # implement wait limit here. use subprocess.wait for a process to finish.
        # otherwise this thing crashes. run_scancommand should return a subprocess
        # handle so you can wait for it 
        processhandle.wait()

        # find list of scanned files.
        cmd = 'ls ' + args.outputdir + '/' + args.prefix + '-' + str(args.timenow) + '-part-*.pnm'
        scanned_files = scanutils.filelist(cmd)

        if debug:
            scanutils.logprint('Scanned files: ', scanned_files)

        if debug:
            scanutils.logprint('Debugging file_part: ', scanned_files[-1],match_string_part)

        # find number of scanned files
        number_scanned = len(scanned_files)

        if debug:
            scanutils.logprint("number_scanned: " + str(number_scanned))

        # wait for a specified time before trying to convert each file.
        err,converted_files = scanutils.convert_to_pdf(scanned_files,wait=0,debug=debug,logfile=logfile)
        if not err and len(converted_files) == len(scanned_files):
            for f in scanned_files:
                os.remove(f)

        # make a filelist and output filename to pdftk
        if run_mode == 'run_odd':
            # compile the odd pages into a single pdf
            compiled_pdf_filename = args.outputdir +  '/' + args.prefix + '-' + today + '-' + str(int(time.time())) + '-odd.pdf'
            filestopdftk = converted_files

            # write filelist to outputdir
            # to be used for new odd/even mechanism in the future.
            tempf = open(odd_files_name,'w')
            tempf.write(str(converted_files))
            tempf.close()
        elif run_mode == 'run_even':
            # if scanned even parts, and hence max part number is bigger than 1
            # even files are automatically numbered in reverse by the scancommand.
            # new files have been ensured to be in sorted order.
            converted_files.sort() #newfiles should be sorted already

            # interleave two lists, nested for loops
            if len(oddfiles) == len(converted_files):
                allfiles = scanutils.interleave_lists(oddfiles,converted_files)
            else:
                logprint('Even files scanned not equal to odd files scanned. Compiling even files alone.')
                allfiles = converted_files

            if debug:
                scanutils.logprint('filelist: ' , allfiles)
            # ensures that the filename for compiled pdf is unique
            compiled_pdf_filename = args.outputdir +  '/' + args.prefix + '-' + today + '-' + str(int(time.time())) + '.pdf'
            filestopdftk = allfiles

            # finally delete even files list
            try:
                os.remove(odd_files_name)
            except:
                logprint('Error deleting odd files list!!! Must manually delete')
                if debug:
                    traceback.print_exc(file=sys.stdout)


        if len(filestopdftk) > 0:
            scanutils.run_pdftk(filestopdftk,compiled_pdf_filename,debug=debug,logfile=logfile)
        else:
            scanutils.logprint('No files to compile')

        # make the files owned by certain somebody
        if ownedby:
            subprocess.Popen(['chown',ownedby,compiled_pdf_filename])

    #close logfile
    logfile.close() 


else: # if not (double sided and manual double scanning) simply run single sided scanning routine
    # in case we have args.duplex and args.duplextype = 'manual'
    # make outputfile

    scanutils.logprint('Running in single side mode or --duplex="auto"')

    # run scan command
    outputfile = args.outputdir + '/' + args.prefix + '-' + str(int(args.timenow)) + '-part-%03d.pnm'
    [out,err,processhandle] = scanutils.run_scancommand(\
            args.device_name,\
            outputfile,\
            width=args.width,\
            height=args.height,\
            logfile=logfile,\
            debug=debug,\
            mode=args.mode,\
            resolution=args.resolution,\
            batch_start='1',\
            batch_increment='1',\
            source=args.source,\
            dry_run=args.dry_run)

    # see if files have been created.
    if not args.dry_run:
        processhandle.wait()
        try:
            cmd = 'ls ' + args.outputdir + '/' + args.prefix + '-' + str(int(args.timenow)) + '-part-*.pnm'
            if debug:
                scanutils.logprint('Command to find scanned files',cmd)
            files = scanutils.filelist(cmd)

            if debug:
                scanutils.logprint('Scanned files: ', files)
        except:
            scanutils.logprint("error in ls; probably no scanned files found. check permissions and/or pathname.")

        # find number of files by scanning the part number of the last file.
        # assumes that the list is sorted.
        # why is len(files) not sufficient? To rewrite this section.
        try:
            if debug:
                scanutils.logprint('Debugging file_part: ', files[-1],match_string_part)
            number_scanned = scanutils.file_part(files[-1],match_string_part)
        except:
            number_scanned = 0
            scanutils.logprint("Error determining number of files scanned")

        if debug:
            scanutils.logprint("number_scanned: " + str(number_scanned))

        if number_scanned > 0:
            # wait for a time proportional to the number scanned
            # waiting is builtin to convert_to_pdf
            err,convertedfiles = scanutils.convert_to_pdf(files,wait=0,debug=debug,logfile=logfile)

            # find newly converted files
            #convertedfiles = filelist('ls ' + args.outputdir + '/' + args.prefix + '-' + str(int(args.timenow)) + '-part-*.pdf')

            # make a filelist and output filename to pdftk
            compiled_pdf_filename = args.outputdir + '/' + args.prefix + '-' + today + '-' + str(int(time.time())) + '.pdf'

            scanutils.run_pdftk(convertedfiles,compiled_pdf_filename,debug=debug,logfile=logfile)

        # make the files owned by a certain somebody
        if ownedby:
            subprocess.Popen(['chown',ownedby,compiled_pdf_filename])
