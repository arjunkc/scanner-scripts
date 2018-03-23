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

1.      Have to fix the logfile inside single-sided-scan.py. Currently it writes to a fixed /home/arjun directory. I should make this write to $HOME or something.
1.	Have to allow a directory argument to `run_chown`. Currently its being called by `convert_to_pdf` as well.
1.	Have to fix single-sided-scan.py so that it accounts for permissions properly. 

# Notes

Mar 23 2018 Has a hack that allows you to set the directory you're scanning the files to. This is implemented by adding two new environment variables in 

    /opt/brother/scanner/brscan-skey/brscan-skey-0.2.4-0.cfg

called

    SAVETO
    LOGDIR

SAVETO sets the directory that the scanner saves files to. LOGDIR stores logs in that directory.
