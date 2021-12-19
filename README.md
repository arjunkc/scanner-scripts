# README

## Introduction

These are linux enhancement scripts to Brother's brscan-skey scripts. I have tested the scripts on the following consumer brother scanners:

    DCP-L2540DW (no automatic duplex)
    MFC-L2740DW (duplex automatic document feeder)

I have tested these on Archlinux and Debian.

Brother's linux drivers include two packages:

    brscan#
    brscan-skey

where `#` is a number (currently 4). The `brscan#` package contains the binary driver for the scanner and various ini files. The brscan-skey package contains a unix binary daemon that waits for the scanner to send it a message, and a bunch of bash/sh scripts that create scanned files on your PC.

Brother's scripts are very basic, and do not do many of the things I need to have an effective network or USB scanner for my work. In particular, they do not work too well with an (Automatic Document Feeder) ADF. 

**The most important feature for me is to be able to walk to the printer, throw a document in the ADF and hit scan. A pdf of this document should automatically be saved on my computer in a folder of my choice. This operation should support duplex scanning, whether or not the scanner supports automatic duplex scanning.**

This is what my enhanced scripts aim to do. They have the following features:

1.  Supports **duplex** scanning for Brother scanners, *whether or not they support duplex scanning*. That is, if you have a single sided scanning ADF, you feed the facing pages first, then flip the scanned pile over, and scan the reverse pages. The python scripts produce a single pdf document in the right order. The scripts also support scanners that do have duplex scanning ADFs.
1.  Written in python, accepts many options, should be extensible. 
1.  Can detect default devices automatically. 
1.  They are a drop in replacement for the brother scripts, and eventually, will require minimal configuration.

This package is definitely not user friendly, but it does come with an `./install.sh` script that I have done the bare minumum of testing with. Seems to work. *shrugs*.

## Requirements

1.  Requires the Debian Brother scanner driver downloaded from Brother's website ( [example](http://support.brother.com/g/s/id/linux/en/before.html?c=us&lang=en&prod=dcpl2540dw_us_as&redirect=on#ds620)). If installing on Archlinux, use the debtap (Debian to Arch package) program to get an installable Archlinux package.
1.  sane
1.  Python 3
1.  Imagemagick. For converting pnm files to jpg. 
1.  img2pdf seems to work best for embedding jpgs in pdfs. The default convert command distributed with imagemagick is "lossy". I just haven't bothered to figure it out.
1.  pdftk. For compiling the image files into one pdf. 
1.  bash. This is because I know bash better than sh.

## Installation

Download the scripts:

    git clone https://github.com/arjunkc/scanner-scripts

The default brother driver is installed to 

    /opt/brother/scanner/brscan-skey/

I assume that the basic scanner scripts distributed by Brother work for you. It is important to get the brscan-skey daemon working first.

Edit the `brscan-skey-0.2.4-0.cfg` and change default options as necessary. Then run

    cd scanner-scripts
    cp !(brscan-skey-0.2.4-0.cfg) /opt/brother/scanner/brscan-skey/script
    cp brscan-skey-0.2.4-0.cfg /opt/brother/scanner/brscan-skey/

Overwrite any files when prompted.

The two `cp` commands do the following: 

1.  Replace the files

        /opt/brother/scanner/brscan-skey/script/scantofile-0.2.4-1.sh
        /opt/brother/scanner/brscan-skey/script/scantoocr-0.2.4-1.sh
        /opt/brother/scanner/brscan-skey/script/scantoimage-0.2.4-1.sh
        /opt/brother/scanner/brscan-skey/script/scantoemail-0.2.4-1.sh

1.  Copy the files

        scanutils.py
        batchscan.py

    to

        /opt/brother/scanner/brscan-skey/script

    Copy the configuration files 

        brscan-skey-0.2.4-0.cfg

    to

        /opt/brother/scanner/brscan-skey/brscan-skey-0.2.4-0.cfg

## Configuration
This is mostly controlled using bash environment variables in 

    brscan-skey-<your version>.cfg

This is a file that is distributed with brscan-skey. The important variables are

SAVETO       | contains the directory scans are saved into. This is the important thing to set
LOGDIR       | self explanatory
DUPLEXTYPE   | can take two values, manual or automatic. manual implies you have a single sided scanner,and you must scan the odd pages, and the flip it around and scan the even pages.
SOURCE=""    | This is the paper source for the scanner. You can set this yourself by using scanimage -h. Needs sane and libsane to be installed, but you already knew that.
DUPLEXSOURCE | This is the paper source duplex scanning for the scanner. You can set this yourself by using scanimage -h. Needs scanutils.

## How it works

When the "Scan" button on the scanner is hit, the scanner sends out a message that is caught by the brscan-skey daemon. There are 4 or 5 commands that it usually invokes, depending on whether you chose

    File,OCR,Image,Email

Some newer models also have an FTP option. Then the brscan-skey daemon invokes the appropriate script after reading the configuration file `brscan-skey-*.cfg`. It usually finds in `/opt/brother/scanner/brscan-skey` directory (generally, the directory in which the brscan-skey script is installed ?). The script that is invoked can be changed in the configuration file. For example, my `brscan-skey-*.cfg` has the following variable set

    FILE="/bash  /opt/brother/scanner/brscan-skey/script/scantofile-0.2.4-1.sh"
    
So if the File option is chosen on the scanner, brscan-skey will call 

    bash /opt/brother/scanner/brscan-skey/script/scantoocr-0.2.4-1.sh <device name>

where `<device name>` is something like

    'brother4:net1;dev0'

Brother's basic scripts are rudimentary and simply invoke the scanimage command. When the OCR button is pressed, Brother's script also attempts to run an optical character recognition software. This is not such a useful feature for me.

My scripts replace Brother's scripts and are wrappers for the python script `batchscan.py`. `batchscan.py` scans in scanimage's batch mode, which allows you to scan a bunch of automatically named individual files from the ADF. The most important difference is that when the OCR option is chosen on the scanner, `batchscan.py` no longer attempts to run optical character recognition software. **Instead, it runs batchscan.py in duplex mode**. The `--duplex` option to batchscan.py takes two values: auto or manual. When run in manual mode, it assumes that the ADF is not capable of automatic duplex scanning. In this case, you have to scan all the odd pages, manually flip the paper stack over and put it back in the ADF, and hit the OCR scan button again on the scanner to scan the even. The script then produces a compiled pdf file with the pages in the right order. The way the script detects whether or not it is scanning the odd pages or the even pages is via a file in the output directory called `.scantoocr-odd-filelist`. When scanning odd pages, it stores the names of the scanned pages in this file. So if the file exists, it knows that it is scanning the even pages next. Once it is done scanning the even pages, it deletes `.scantoocr-odd-filelist`. 

Of course, this hidden file .scantoocr-odd-filelist is a source of pain from time-to-time. For example, if you walk away from the scanner after scanning the the next sides and forget about it, it will quite nicely mess up your next few duplex scans. The solution here is to delete this .scantoocr-odd-filelist manually. I could put in a timer that detects whether or not `.scantoocr-odd-filelist` is "too old" or "stale", and performs a new duplex scan. Maybe I will do this at some point; it's trivial to implement. 

`batchscan.py` also converts the scanned `pnm` files to `jpg` and then embeds it into a pdf. This is a fairly space efficient option, and typically converts scans that are several megabytes in size to a few kilobytes.

### Files

1.  `brscan-skey-0.2.4-0.cfg` This has to be copied to this precise directory:
    
    /opt/brother/scanner/brscan-skey/

    It tells the brscan-skey utility to call bash instead of sh, and it also has a bunch of new environment variables that can be used to control duplex scanning. 

1.  `batchscan.py`. This is the main python script that is invoked by `scantofile`, `scantoocr` and so on. This is a standalone command that has a bunch of optional commands. The most important option is `--duplex` which takes two values: auto and manual. The full list of options include

    a.  --outputdir. Where to store the scanned files.
    a.  --logdir The directory to write the log file in. 
    a.  --prefix This the prefix for the names of the scanned files. Ex: --prefix='myfiles' will create files named 'myfiles-part-01.pdf'.
    a.  --timenow Writes the current time to the file. Can be safely ignored for the most part.
    a.  --device-name If empty, it tries to automatically detect a working scanner.
    a.  --resolution Scan resolution.
    a.  --height Scan page height.
    a.  --width Scan page width.
    a.  --mode The scan mode. Ex: "Black & White"
    a.  --source Source of the documents. Ex: 'Automatic Document Feeder(left aligned,Duplex)'
    a.  --duplex 'auto' or 'manual'. Leave blank for single sided mode.
    a.  --dry-run If set, does not actually run scanimage, but outputs the command that it will run. Useful for testing.

1.  `scanutils.py`. This is a python module that has a bunch of useful functions. It's imported by `batchscan.py`
1.  `scantofile-*.sh` It is simply a wrapper for batchscan.py in single sided mode. It scans a bunch of files from the ADF, converts them to pdf, and compiles a single pdf file. It also deletes the raw `pnm` files produced by the scanner if the conversion to pdf was successful.
1.  `scantoocr-*.sh` This is a wrapper for batchscan.py run in double sided mode. The double sided mode can be 'auto' or 'manual' (set in the configuration file). 
1.  `scantoimage-*.sh` Same as the brother script, but it tries to scan in color, and converts to png. I haven't tested this as much.
1.  `batch-flatbed-scan.sh`. This is a *manual* batch scanner using the flatbed
    for unusual page sizes. It allows you to manually turn pages and hit a key
    to continue. I needed to create this since scanimage's `--batch-prompt`
    option does not appear to work correctly with Brother's scanners. It is
    related to this [bug report](http://lists.alioth.debian.org/pipermail/sane-devel/2016-May/034587.html). 
1.  `scantoemail.sh`. This is the standard Brother scanner utility. 

# TODO

1.  Test the single sided scanning stuff. ~~In particular, delete the pnm files.~~ Still working, the filelist function is a bit problematic. Also debugging output is not going in.
1.  Clean up the code.
1.  Change logdir option to logfile. 
1.  Have to fix single-sided-scan.py so that it accounts for permissions properly. 
1.  Implement `dry_run` routines for `convert_to_pdf` and `run_pdftk`
1.  ~~Deal with permissions errors on the logfile.~~ alleviated a little bit by logging to a tempfile
1.  ~~Add an installation section to the README file.~~
1.  ~~Have to modify the chown mechanism. I can just add this functionality. The unix way is to not do this. But it's more convenient for me if it does, so I'm going to do it. Perhaps it's ok to have the brscan daemon run by a normal user. In this case, you don't need to run chown. Then you can remove the chown script from your thingy. I don't think it will make it group writeable though, since the commands mgiht not respect the ACLs. So my wife might not be able to organize and delete the scans on a shared folder. I guess this is a personal problem.~~ I think that it does work, but I haven't tested it on mediaserver.
1.  ~~Move back to sh for more portability. Is this really necessary?~~ decided that since we have so many requirements, requiring bash is not too much to ask.
1.  ~~To move to different mechanism for manual duplex scanning. Should change behaviour just a little bit. It should write a filelist of odd files to the directory. If it finds this file, then it should run the `run_even` routine, and then delete the filelist of oddfiles. As a backup, it should also save the `even` files as a separate file. So if you run scantoocr by mistake, you simply run it again, and it will delete the odd filelist, ensuring that you can rerun scantoocr right away. But the problem is that the `run_even` command will have the pages in reverse order. I suppose this can be fixed with a pdftk command manually. Perhaps to "clear the odd files scanned by mistake" you can have a check on the even side that does the following: if even files not equal to the number of odd files, then you delete the odd filelist, and don't create a compiled pdf output.~~
1.  ~~Can you replace the `wait` statements by polling the subprocess handle, run.wait() or something? The wait quantities can then be limits. Maybe run.communicate() does the same thing.~~
1.  ~~Remove my `convert-compress-delete` command, or simply add it to the scripts and run it for the time being.~~
1.  ~~To test `convert_to_pdf`. Seems to be working.~~
1.  ~~Have to fix the logfile inside single-sided-scan.py. Currently it writes to a fixed /home/arjun directory. I should make this write to $HOME or something. I think it fails now if the logfile does not exist.~~
1.  ~~Create a new thinkpad git branch. Then you can merge things if necessary.~~ decided not to have a new git branch. Should really use .gitattributes to run scripts that customize the configuration file.
1.  ~~Integrate double-sided-scan.py functionality into a single file. Has to check if device supports duplex mode. If it doesn't it will run the double-sided functionality that asks you to scan things twice.~~
1.  display should see if a global logfile variable has been set and its writeable. If not, it should just print to screen.
1.  ~~To test single-sided-scan.py after going through the code.~~ Jul 04 2018 Seems to be working, as far as I can tell from the command line. To test from scanner directly.
1.  ~~Add argparse functionality. Working on this on Jul 03 2018. Still working, updated `run_scancommand.`~~
1.  ~~Install the newest version of brscan-skey and see if it passes along information about duplex scanning.~~ There are scripts that automatically create the files. I would have to see it work, but I don't really see it working. You can only scan from the flatbed, it seems, and it only creates single files, no batch mode. I should add this to the main section of the readme. I tested the basic scripts from brother. The scantofile script is automatically generated, and it does not seem to capture the "double" sided option at all.

# Notes
Jul 13 2018 Fixed the filelist function. the code is still pretty messy. Now works when run as normal user arjun. Removed chown commands.

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

### License 

batchscan.py adds batchscanning functionality brscan-skey
Copyright © 2018 Arjun Krishnan

Do whatever you want. 
