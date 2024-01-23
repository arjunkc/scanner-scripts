#! /bin/bash
set +o noclobber
#
#   $1 = scanner device
#   $2 = brother internal
#   
#       100,200,300,400,600
#
#   List devices with scanimage -L
#   Query device with scanimage -h to get allowed resolutions
#   In color, resolution more than 300 slows things down

function Usage() {
    echo -e "Usage:"
    echo -e "\t "$0" [option] <devicename>\n"
    echo -e "The devicename is optional. Set by default to ${default_device}"
    echo -e "Check the source for options. Will write a png file in a default directory after scanning."
    echo -e "Heights and width can be specified in the script. So can compression format, resolution."
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
    SAVETO=${HOME}'/brscan/images'
else
    SAVETO=${SAVETO}'/images/'
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
# in scantofile the width and height are automatically set. Here, they're not.
# leave height and width uncommented to autodetect
#height=114
#width=160
# set color to full color or 24 bit. 
mode='"24Bit Color"' #other option is "Black & White"
compress_format="png"

epochnow=$(date '+%s')

# for debugging purposes, output arguments
echo "options after processing." >> ${logfile}
echo "$*" >> ${logfile}
# export environment to logfile
set >> ${logfile}
echo $LOGDIR >> ${logfile}

# BEGIN SCAN PROCEDURE
if [ "`which usleep  2>/dev/null `" != '' ];then
    usleep 100000
else
    sleep  0.1
fi
output_file="$SAVETO"/brscan_image_"`date +%Y-%m-%d-%H-%M-%S`".pnm

#echo "scan from $2($device) to $output_file"

# options
if [[ -z "$height" || -z "$width" ]]; then
    SCANOPTIONS="--mode $mode --device-name \"$device\" --resolution $resolution"
else
    SCANOPTIONS="--mode $mode --device-name \"$device\" --resolution $resolution -x $width -y $height"
fi

# echo the command to stdout. Then write it to logfile.
echo "scanimage $SCANOPTIONS > $output_file"
echo "scanimage $SCANOPTIONS > $output_file" >> $logfile 
echo "scanimage $SCANOPTIONS > $output_file" 2>> $logfile | bash

#scanimage --verbose $SCANOPTIONS > $output_file 2>/dev/null

# if the file is zero size, run again.
if [ ! -s $output_file ];then
  if [ "`which usleep  2>/dev/null `" != '' ];then
    usleep 1000000
  else
    sleep  1
  fi
  echo "Rerunning scanimage $SCANOPTIONS"
  scanimage $SCANOPTIONS > $output_file 2>/dev/null

fi
#echo gimp -n $output_file  2>/dev/null \;rm -f $output_file | sh & 

if [ -s $output_file ]; then
    echo  $output_file is created.

    # Should convert to jpg and delete duplicates
    output_file_compressed=$(dirname $output_file)"/"$(basename $output_file .pnm)".$compress_format"
    echo convert -trim -bordercolor White -border 20x10 +repage -quality 95 -density "$resolution" $output_file "$output_file_compressed" 
    echo convert -trim -quality 95 -density "$resolution" $output_file "$output_file_compressed" >> $logfile
    echo convert -trim -quality 95 -density "$resolution" "$output_file" "$output_file_compressed" | bash
fi
