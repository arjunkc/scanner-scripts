# README

Contains my scanning scripts for my Brother DCP-L2450DW scanner. It has an ADF
and a Flatbed, but the ADF does not support duplex scanning. My scan scripts
allow me to do the following

1.  `brscan-skey-0.2.4-0.cfg` This has to be copied to this precise directory:
    
    /opt/brother/scanner/brscan-skey/

    It tells the brscan-skey utility to call bash instead of sh. sh throws errors, and I don't really care enough to debug it.

1.  `scantofile.sh` A simple scanning utility. They're based on the scripts
    distributed by Brother and are called by the brscan-skey utility when it
    detects the scan button being pressed on the scanner. It scans a file,
    writes it to my directory, and converts it to a pdf.
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
1.  `double-sided-scan.py`. This is called by scantoocr.sh and has the weird
    timestamp checking stuff.
1.  `scanutils.py`. This is a python module that has a bunch of useful functions
    for `double-sided-scan.py`. 
1.  `scantoemail.sh`. This is the standard Brother scanner utility. I think I
    will turn this into a single sided scanning script from the ADF eventually.

# TODO

1.      Add argparse functionality. Working on this on Jul 03 2018
1.      Create a new thinkpad git branch. Then you can merge things if necessary.
1.      Install the newest version of brscan-skey and see if it passes along information about duplex scanning.
1.      Have to fix the logfile inside single-sided-scan.py. Currently it writes to a fixed /home/arjun directory. I should make this write to $HOME or something. I think it fails now if the logfile does not exist.
1.	Have to allow a directory argument to `run_chown`. Currently its being called by `convert_to_pdf` as well.
1.	Have to fix single-sided-scan.py so that it accounts for permissions properly. 

# Notes

Jul 03 2018 Made more progress on argparse. Have to test `get_default_scanner` and `parse_arguments`. You can do this in python.

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
