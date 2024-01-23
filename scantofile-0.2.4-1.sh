#! /bin/bash
set +o noclobber
#
#   $1 = scanner device
#   $2 = brother internal
#   
#       100,200,300,400,600
#
#   This is my batch scan. It scans single sided pages by default.
#   List devices with scanimage -L
#   Query device with scanimage -h to get allowed resolutions
#   To do:
#   ~~Apr 01 2016 To do, implement compression if possible.~~
#   ~~Dec 31 2016 to do, combine even and odd files into one big pdf file~~

function Usage() {
    echo -e "Usage:"
    echo -e "\t "$0" [option] <devicename>\n"
    echo -e "The devicename is optional. Set by default to ${default_device}"
    echo -e "Heights and width can be specified in the script."
    echo -e "\nOptions:"
    echo -e "\t -h \t Print this help"
}

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

# if SOURCE is not set
if [[ -z $SOURCE ]]; then
    SOURCE="Automatic Document Feeder(left aligned)"
fi

# parse one simple option. Allows you to get help
while getopts "h" opt; do
    case "$opt" in
        h)
            Usage
            exit 0
            # usually there will be shift here
            ;;
    esac
done

# see if scanners exists
default_device=$(scanimage -L | head -n 1 | sed "s/.*\`\(.*\)'.*/\1/")
if [[ -z "$default_device" ]]; then
    echo "No devices found" | tee "$logfile"
fi

if [ -z "$1" ]; then
    device="$default_device"
else
    device=$1
fi

# OPTIONS follow
resolution=300
# the width is default and i wont use it. It's in mm and equal to 8.5in
width=215.88
# the height has to be set. its now 11in = 279.4 and 11.4in = 290. Setting the height higher does not work on the ADF, but does work on the flatbet
height=279.4
# set color to Black and White by default
mode="Black & White"

epochnow=$(date '+%s')

# for debugging purposes, output arguments
echo "options after processing." >> ${logfile}
echo "$*" >> ${logfile}
# export environment to logfile
set >> ${logfile}
echo $LOGDIR >> ${logfile}

# BEGIN SCAN PROCEDURE
fileprefix='scantofile'
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
    --source "$SOURCE" "

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
    --source "$SOURCE" 
    #--dry-run \
