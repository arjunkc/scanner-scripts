#! /bin/bash
set +o noclobber
#
#   Edited by Arjun Krishnan Apr 03 2017
#
#   $1 = scanner device
#   $2 = brother internal
#   
#       100,200,300,400,600
#
#   This is my batch scan. It scans double sided pages by default.
#   query device with scanimage -h to get allowed resolutions
#   Will scan from the 'brother4:net1;dev0' scanner by default.
#   To do:
#   ~~Apr 01 2016 To do, implement compression if possible.~~
#   ~~Dec 31 2016 to do, combine even and odd files into one big pdf file~~

resolution=300

if [ -n "$1" ]; then
    # if first argument is not empty
    device=$1
fi

# the width is default and i wont use it. It's in mm and equal to 8.5in
width=215.88
# the height has to be set. its now 11in = 279.4 and 11.4in = 290. Setting the height higher does not work on the ADF, but does work on the flatbet
height=279.4
mode="Black & White"

epochnow=$(date '+%s')

# LOGFILE
scriptname=$(basename "$0")
# $0 refers to the script name
basedir=$(readlink -f "$0" | xargs dirname)

# change to directory of script
cd ${basedir}
echo "basedir = $basedir" 

# ugly hack that makes environment variables set available
cfgfile=$(ls ../brscan-skey-*.cfg)
echo "cfgfile = $cfgfile"
if [[ -r "$cfgfile" ]]; then
    echo "Found cfgfile"
    source "$cfgfile"
    echo "environment after processing cfgfile"
    env
fi


# SAVETO DIRECTORY
if [[ -z "$SAVETO" ]];  then
    SAVETO=${HOME}'/brscan/documents'
else
    SAVETO=${SAVETO}'/documents/'
fi

mkdir -p $SAVETO

if [[ -z $LOGDIR ]]; then
    # if LOGDIR is not set, choose a default
    mkdir -p ${HOME}/brscan
    logfile=${HOME}"/brscan/$scriptname.log"
else
    mkdir -p $LOGDIR
    logfile=${LOGDIR}"/$scriptname.log"
fi
touch ${logfile}

# if DUPLEXTYPE is not set
if [[ -z $DUPLEXTYPE ]]; then
    DUPLEXTYPE='manual'
fi

# if DUPLEXSOURCE is not set
if [[ -z $DUPLEXSOURCE ]]; then
    DUPLEXSOURCE="Automatic Document Feeder(left aligned,Duplex)"
fi

# for debugging purposes, output arguments
echo "options after processing." >> ${logfile}
echo "$*" >> ${logfile}
# export environment to logfile
set >> ${logfile}
echo $LOGDIR >> ${logfile}

fileprefix='scantoocr'
echo "${basedir}/batchscan.py \
    --outputdir ${SAVETO} \
    --logdir ${LOGDIR} \
    --prefix ${fileprefix} \
    --timenow ${epochnow} \
    --device-name ${device} \
    --resolution ${resolution} \
    --height $height \
    --width $width \
    --mode "$mode" \
    --source "$DUPLEXSOURCE" \
    --duplex "$DUPLEXTYPE" " 

${basedir}/batchscan.py \
    --outputdir ${SAVETO} \
    --logdir ${LOGDIR} \
    --prefix ${fileprefix} \
    --timenow ${epochnow} \
    --device-name ${device} \
    --resolution ${resolution} \
    --height $height \
    --width $width \
    --mode "$mode" \
    --source "$DUPLEXSOURCE" \
    --duplex "$DUPLEXTYPE" 
    #--dry-run \

