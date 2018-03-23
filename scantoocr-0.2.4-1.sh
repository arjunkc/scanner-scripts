#! /bin/bash
set +o noclobber
#
#   Edited by Arjun Krishnan Apr 03 2017
#
#   $1 = scanner device
#
#   
#       100,200,300,400,600

#   This is my batch scan. It scans by default to double sided pages.
#   Will scan from the 'brother4:net1;dev0' scanner by default.
#   To do:
#   ~~Apr 01 2016 To do, implement compression if possible.~~
#   ~~Dec 31 2016 to do, combine even and odd files into one big pdf file~~

resolution=300
if [ -z "$1" ]; then
    device='brother4:net1;dev0'
else
    device=$1
fi

# ugly hack that makes environment variables set available
source /opt/brother/scanner/brscan-skey/brscan-skey-*.cfg

# SAVETO DIRECTORY
if [[ -z $SAVETO ]];  then
    SAVETO=$HOME'/brscan/documents/'
else
    SAVETO=${SAVETO}'/brscan/documents/'
fi

mkdir -p $SAVETO

# LOGFILE
scriptname=$(basename "$0")
if [[ -z $LOGDIR ]]; then
    # $0 refers to the script name
    logfile=${HOME}"/brscan/$scriptname.log"
else
    logfile=${LOGDIR}"/$scriptname.log"
fi
mkdir -p $LOGDIR
touch ${logfile}

fileprefix='scantoocr'

# the width is default and i wont use it. It's in mm and equal to 8.5in
width=215.88
# the height has to be set. its now 11in = 279.4 and 11.4in = 290. Setting the height higher does not work on the ADF, but does work on the flatbet
height=279.4
mode="Black & White"

# makes output files that look like part-01.pnm and so on. Increase the %02d if
# you have more than 99 documents. In any case, the adf doesn't like to read
# more than 100 documents.

#date=$(date '+%F')
#hour=$(date '+%H')
#min=$(date '+%rM')
#easier to use epoch now
epochnow=$(date '+%s')
/opt/brother/scanner/brscan-skey/script/double-sided-scan.py \
    ${SAVETO} \
    ${fileprefix} \
    ${epochnow} \
    ${device} \
    ${resolution} \
    $height \
    $width \
    "$mode" \
    >> $logfile 2>&1 

