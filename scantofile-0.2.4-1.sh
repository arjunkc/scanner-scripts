#! /bin/bash
set +o noclobber
#
#   Edited by Arjun Krishnan Apr 03 2017
#
#   $1 = scanner device
#
#   
#       100,200,300,400,600
#
#   This is my batch scan. It scans by default to single sided pages.
#   query device with scanimage -h to get allowed resolutions
#   Will scan from the 'brother4:net1;dev0' scanner by default.
#   To do:
#   ~~Apr 01 2016 To do, implement compression if possible.~~
#   ~~Dec 31 2016 to do, combine even and odd files into one big pdf file~~

resolution=300

if [ -z "$1" ]; then
    device='brother4:bus3;dev7'
else
    device=$1
fi

# the width is default and i wont use it. It's in mm and equal to 8.5in
width=215.88
# the height has to be set. its now 11in = 279.4 and 11.4in = 290. Setting the height higher does not work on the ADF, but does work on the flatbet
height=279.4
mode="Black & White"
docsource="Automatic Document Feeder(left aligned)"

epochnow=$(date '+%s')

# ugly hack that makes environment variables set available
source /opt/brother/scanner/brscan-skey/brscan-skey-*.cfg

# SAVETO DIRECTORY
if [[ -z "$SAVETO" ]];  then
    SAVETO=${HOME}'/brscan/documents'
else
    SAVETO=${SAVETO}'/documents/'
fi

mkdir -p $SAVETO

# LOGFILE
scriptname=$(basename "$0")
basedir=$(dirname "$0")
if [[ -z $LOGDIR ]]; then
    # $0 refers to the script name
    logfile=${HOME}"/brscan/$scriptname.log"
else
    logfile=${LOGDIR}"/$scriptname.log"
fi
mkdir -p $LOGDIR
touch ${logfile}

# for debugging purposes, output arguments
echo $* >> ${logfile}
# export environment to logfile
set >> ${logfile}
echo $LOGDIR >> ${logfile}

fileprefix='scantofile'
${basedir}/single-sided-scan.py \
    --outputdir ${SAVETO} \
    --logdir ${LOGDIR} \
    --prefix ${fileprefix} \
    --timenow ${epochnow} \
    --device-name ${device} \
    --resolution ${resolution} \
    --height $height \
    --width $width \
    --mode "$mode" \
    --source "$docsource" \
    >> $logfile 2>&1 

