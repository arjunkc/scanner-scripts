#! /bin/bash
set +o noclobber
#
#   $1 = scanner device
#   $2 = brother internal
#   
#       100,200,300,400,600
#
# query device with scanimage -h to get allowed resolutions
# in color resolution more than 300 slows things down
resolution=600
# leave height and width uncommented to autodetect
height=175
width=175
scan_format="pnm"
compress="True"
compress_format="jpg"
compress_quality="95"
autocrop="True"
# set color to full color or 24 bit. 
mode='"24Bit Color"' #"Black & White"'
#   List devices with scanimage -L
#   Query device with scanimage -h to get allowed resolutions
#   In color, resolution more than 300 slows things down

function Usage() {
    echo -e "Usage:"
    echo -e "\t "$0" [option] <devicename>\n"
    echo -e "The devicename is optional. Set by default to ${default_device}"
    echo -e "Check the source for options. Will write a $compress_format file if the compress variable is set to True. The current value is $compress. If set to False, then the scan format is $scan_format"
    echo -e "Heights and width can be specified in the script. So can resolution."
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
# this is currently unused in scantoimage
if [[ -z $SOURCE ]]; then
    SOURCE="FlatBed" #"Automatic Document Feeder(left aligned)"
fi

# parse one simple option. Allows you to get help
while getopts "h" opt; do
    case "$opt" in
        h)
            Usage
            exit 0
            # usually there will be shift here
            shift
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

# options
if [[ -z "$height" || -z "$width" ]]; then
    SCANOPTIONS="--mode $mode --device-name \"$device\" --resolution $resolution --format $scan_format"
else
    SCANOPTIONS="--mode $mode --device-name \"$device\" --resolution $resolution -x $width -y $height --format $scan_format"
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

if [ -s $output_file ]; then
    echo  $output_file is created. | tee -a "$logfile"

    output_file_cropped=$(dirname $output_file)"/"$(basename $output_file .pnm)"-cropped.pnm"
    if [[ "True" == "$autocrop" ]]; then
        # maybe better to use autocrop script, which seems better for trimming dirty scanned borders
        #echo convert -trim -fuzz 10% -bordercolor white -border 20x10 +repage "$resolution" $output_file "$output_file_cropped" | bash

        # get some autotrimming information about the image 
        image_info=$(convert $output_file -virtual-pixel edge -blur 0x20 -fuzz 10% -trim info:)
        # compute an offset
        off=$(echo $image_info | awk '{print $4 }' | sed -e 's/[^+]*\(+[0-9]*+[0-9]*\)/\1/') 
        # calculate crop
        crop=$(echo $image_info | awk '{print $3}')
        echo "convert $output_file -crop $crop$off $output_file_cropped" | tee -a "$logfile" 
        # run convert command
        if convert $output_file -crop $crop$off "$output_file_cropped"; then
            # if the convert command converts successfully
            #output_file="$output_file_cropped"
            cp "$output_file_cropped" "$output_file"
            rm "$output_file_cropped" 
        fi
    fi 

    # Should convert to jpg and delete duplicates
    output_file_compressed=$(dirname $output_file)"/"$(basename $output_file .pnm)".$compress_format"
    if [[ "True" == "$compress" ]]; then
        echo convert -quality $compress_quality -density "$resolution" $output_file "$output_file_compressed" | tee -a $logfile | bash
        # file ownership is best set through default acl for the destination directory
    fi
fi
