# README

## Introduction

This is a work in progress, and does not work for anyone other than me. Should be ready in a few weeks though.

These are linux enhancement scripts to Brother's brscan-skey scripts. Consumer brother scanners like the 

    DCP-L2540DW
    MFC-L2740DW

Brother's linux drivers include two packages:

    brscan#
    brscan-skey

where `#` is a number (currently 4). The `brscan#` package contains the binary driver for the scanner and various ini files. The brscan-skey package contains a unix binary daemon that waits for the scanner to send it a message, and a bunch of bash/sh scripts that create scanned files on your PC.

These scripts are very basic, and do not do many of the things I need to have an effective network or USB scanner for my work. In particular, they do not work too well with an (Automatic Document Feeder) ADF.

My enhanced scripts have the following features:

1.  Support **duplex** scanning for Brother scanners, *whether or not they support duplex scanning*. That is, if you have a single sided scanning ADF, you feed the facing pages first, then flip the scanned pile over, and scan the reverse pages. The python scripts do the automated numbering and produce a single pdf document. The scripts also support scanners that do have duplex scanning ADFs.
1.  Written in python, accept many options. 
1.  Can detect default devices automatically. 
1.  They are a drop in replacement for the brother scripts, and eventually, will require minimal configuration.

## Requirements
I have tested it on python 3.5 and 3.6. Requires the debian brother package downloaded from the Brother website ( [example](http://support.brother.com/g/s/id/linux/en/before.html?c=us&lang=en&prod=dcpl2540dw_us_as&redirect=on#ds620)).

1.  sane
1.  Python 3
1.  Imagemagick. For converting pnm files to pdf.
1.  pdftk. For compiling the image files into one pdf.
1.  bash. This is because I know bash better than sh.

## Installation

Download the scripts:

    git clone https://github.com/arjunkc/scanner-scripts

The default brother driver is installed to 

    /opt/brother/scanner/brscan-skey/

I assume that the basic utilities distributed by Brother work for you.

Then run

    cp !(brscan-skey-0.2.4-0.cfg) /opt/brother/scanner/brscan-skey/script
    cp !(brscan-skey-0.2.4-0.cfg) /opt/brother/scanner/brscan-skey/

Edit the `brscan-skey-0.2.4-0.cfg` and change default options as necessary.

Replace the files

    /opt/brother/scanner/brscan-skey/script/scantofile-0.2.4-1.sh
    /opt/brother/scanner/brscan-skey/script/scantoocr-0.2.4-1.sh
    /opt/brother/scanner/brscan-skey/script/scantoimage-0.2.4-1.sh
    /opt/brother/scanner/brscan-skey/script/scantoemail-0.2.4-1.sh

Copy the files

    scanutils.py
    single-sided-scan.py

to

    /opt/brother/scanner/brscan-skey/script

and importantly

    brscan-skey-0.2.4-0.cfg

to

    /opt/brother/scanner/brscan-skey/brscan-skey-0.2.4-0.cfg



## How it works

When the "Scan" button on the Brother scanner is hit, the scanner sends out a message that is caught by the brscan-skey.

<!-- Contains my scanning scripts for my Brother DCP-L2540DW scanner. It has an ADF -->
<!-- and a Flatbed, but the ADF does not support duplex scanning. My scan scripts -->
<!-- allow me to do the following -->

1.  `brscan-skey-0.2.4-0.cfg` This has to be copied to this precise directory:
    
    /opt/brother/scanner/brscan-skey/

    It tells the brscan-skey utility to call bash instead of sh, and it also has a bunch of new environment variables that can be used to control duplex scanning. 

1.  `single-sided-scan.py`. This has the main python scripts that scan and convert to pdf. Called by `scantofile.sh`
1.  `double-sided-scan.py`. This is called by scantoocr.sh and has the weird
    timestamp checking stuff.
1.  `scanutils.py`. This is a python module that has a bunch of useful functions
    for `double-sided-scan.py`. 
1.  `scantofile.sh` A simple scanning utility. They're based on the scripts
    distributed by Brother and are called by the brscan-skey utility when it
    detects the scan button being pressed on the scanner. It scans a file,
    writes it to my directory, and converts it to a pdf. It is simply a wrapper for single-sided-scan.py with the appropriate options.
1.  `scantoocr.sh` A more elaborate scanning utility that allows me to first
    scan all the odd pages of a document using the ADF, and then scans all the
    even sides. It calls a python script double-sided-scan.py that can detects
    if a document is a single sided scan or a double sided scan using
    timestamps. If two scans are less than five minutes apart, and it a series
    of odd pages have been created within those five minutes, it assumes that
    the two scans are are related and the even sides are being scanned. It
    creates a single pdf file at the end using ImageMagick's convert.
    It does have the disadvantage that it cannot really be used for
    single sided scanning. 
1.  `scantoimage.sh` Same as `scantofile.sh` but it's set to scan in color. I
    find that Black & White at 300dpi works well enough for most documents for
    me.
1.  `batch-flatbed-scan.sh`. This is a *manual* batch scanner using the flatbed
    for unusual page sizes. It allows you to manually turn pages and hit a key
    to continue. I needed to create this since scanimage's `--batch-prompt`
    option does not appear to work correctly with Brother's scanners. It is
    related to this [bug report](http://lists.alioth.debian.org/pipermail/sane-devel/2016-May/034587.html).
1.  `scantoemail.sh`. This is the standard Brother scanner utility. I think I
    will turn this into a single sided scanning script from the ADF eventually.

# TODO

1.  To move to different mechanism for manual duplex scanning.
1.  To test `convert_to_pdf`. Seems to be working.
1.  Should change behaviour just a little bit. It should write a filelist of odd files to the directory. If it finds this file, then it should run the `run_even` routine, and then delete the filelist of oddfiles. As a backup, it should also save the `even` files as a separate file. So if you run scantoocr by mistake, you simply run it again, and it will delete the odd filelist, ensuring that you can rerun scantoocr right away. But the problem is that the `run_even` command will have the pages in reverse order. I suppose this can be fixed with a pdftk command manually. Perhaps to "clear the odd files scanned by mistake" you can have a check on the even side that does the following: if even files not equal to the number of odd files, then you delete the odd filelist, and don't create a compiled pdf output. 
1.  Perhaps it's ok to have the brscan daemon run by a normal user. In this case, you don't need to run chown. Then you can remove the chown script from your thingy. I don't think it will make it group writeable though, since the commands mgiht not respect the ACLs. So shirley might not be able to organize and delete the scans.
1.  Can you replace the `wait` statements by polling the subprocess handle, run.wait() or something? The wait quantities can then be limits. Maybe run.communicate() does the same thing.
1.  Remove my `convert-compress-delete` command, or simply add it to the scripts and run it for the time being.
1.  Change logdir option to logfile. Make logging a little bit better.
1.  Add an installation section to the README file.
1.  Move back to sh for more portability. Is this really necessary?
1.  Have to modify the chown mechanism. I can just add this functionality. The unix way is to not do this. But it's more convenient for me if it does, so I'm going to do it.
1.  ~~Have to fix the logfile inside single-sided-scan.py. Currently it writes to a fixed /home/arjun directory. I should make this write to $HOME or something. I think it fails now if the logfile does not exist.~~
1.  Have to allow a directory argument to `run_chown`. Currently its being called by `convert_to_pdf` as well.
1.  Have to fix single-sided-scan.py so that it accounts for permissions properly. 
1.  ~~Create a new thinkpad git branch. Then you can merge things if necessary.~~ decided not to have a new git branch. Should really use .gitattributes to run scripts that customize the configuration file.
1.  ~~Integrate double-sided-scan.py functionality into a single file. Has to check if device supports duplex mode. If it doesn't it will run the double-sided functionality that asks you to scan things twice.~~
1.  display should see if a global logfile variable has been set and its writeable. If not, it should just print to screen.
1.  ~~To test single-sided-scan.py after going through the code.~~ Jul 04 2018 Seems to be working, as far as I can tell from the command line. To test from scanner directly.
1.  ~~Add argparse functionality. Working on this on Jul 03 2018. Still working, updated `run_scancommand.`~~
1.  ~~Install the newest version of brscan-skey and see if it passes along information about duplex scanning.~~ There are scripts that automatically create the files. I would have to see it work, but I don't really see it working. You can only scan from the flatbed, it seems, and it only creates single files, no batch mode. I should add this to the main section of the readme. I tested the basic scripts from brother. The scantofile script is automatically generated, and it does not seem to capture the "double" sided option at all.

# Notes

Jul 06 2018 Works on thinkpad now. 

Jul 06 2018 Should change display mechanism. By default display should display to stdout, and the `--logdir` option should be changed to logfile. 

If the logfile is set, it should output to logfile. If not, it should make some temporary logfile, and it should send things there. 

If `--debug` is true, then display should output to stdout as well.

Jul 04 2018 It seems that the `--source` option you obtain using

    scanimage -A -d 'device'

will list Duplex scanning even if its not possible for the device! So I will have to setup an DUPLEXTYPE option in the cfg file. I will also setup a DUPLEXSOURCE option so you can set 'Automatic Document Feeder (centrally aligned,Duplex)' as a default option.

Jul 04 2018 Made `run_scancommand` a bit simpler so that it only runs in batch mode. I made the option names match the scancommand option names. I've tested `run_scancommand`, and it seems to work

Jul 03 2018 Even with the newer scripts, the brother automatic scan button does not seem to indicate that it can do duplex scans to brscan-skey.

Jul 03 2018 Made more progress on argparse. Have to test `get_default_scanner` and `parse_arguments`. You can do this in python. I have tested `get_default_scanner`. Still working on `parse_arguments`. Figuring out nargs, const and default.

Jul 03 2018 Working on argparse in scanutils. Almost done. Need to write a `get_default_scanner` script. Resume at line 115 on scanutils.py
when constructing the command to call, empty argument should be ignored. i considered arguments like `get_default_mode,` but I think if double is specified, it should look for a Duplex. If it's found, it should scan in this mode. 

options for mode, and source should probably be left alone. height and width are taken for letter, but these should also probably be left alone. The only thing that it should look for is the default device. It should also take the option --double, which will activate the double-sided-scan routines. What if you wanted to do double-sided scanning from the flatbed? This is easy to do, you just flip the paper over as. So if you have a --double option, then it will see if the ADF supports Duplex, and it will pick a default mode from the --source options obtained from

    scanimage -d <default device> -A

Otherwise it will run my manual double scanning routing from the ADF.

Jul 02 2018 I'm not sure scantoocr or double sided scan are needed for thinkpad. This is because the scanner automatically implements duplex scanning. Somehow, I'm not able to detect how the scanner is doing duplex. At the moment:

1.  File scans Duplex by setting the docsource environment variable inside scantofile-xxx.sh
1.  scantoocr is not used here. The easy way is to just use scantoocr when needed for duplex scanning.
1.  The right way to do things, of course, is to upgrade the thinkpad to the newest brscan-skey scripts, and then see if a new environment variable or shell variable is passed to the script indicating duplex scanning.

Right now, the scripts do dump the environment to the logfile. The logfile location has been hacked a bit. 

Jul 02 2018 I have a little `parse_arguments` hacky script. I really should use the parser mechanism. This is inside scanutils.py and is quite messy.

Jul 02 2018 At least the scan command ran this time with singlesidedscan

Jul 02 2018 Made a little more progress with the logging mechanism on thinkpad. I think I figured out how to pass environment variables to python. The single-sided-scan.py file now reads a logdir option. This defaults to '/var/log/brscan' or it writes to the $LOGDIR environment variable if set. I'm still testing it. I would like to set the arguments using the longform options

    --directory

and so on, for single-sided-scan.py. I have not tested this, but I think pythons `parse_arguments` module should implement this.

Apr 13 2018 Have to fix the logging mechanism using pythons logging module.

Mar 23 2018 Has a hack that allows you to set the directory you're scanning the files to. This is implemented by adding two new environment variables in 

    /opt/brother/scanner/brscan-skey/brscan-skey-0.2.4-0.cfg

called

    SAVETO
    LOGDIR

SAVETO sets the directory that the scanner saves files to. LOGDIR stores logs in that directory.
