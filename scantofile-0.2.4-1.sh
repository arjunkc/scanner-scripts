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
#   query device with scanimage -h to get allowed resolutions
#   Will scan from the 'brother4:net1;dev0' scanner by default.
#   To do:



resolution=300
logfile="/home/arjun/brscan/brscan-skey.log"
if [ -z "$1" ]; then
    device='brother4:net1;dev0'
else
    device=$1
fi

# the width is default and i wont use it. It's in mm and equal to 8.5in
width=215.88
# the height has to be set. its now 11in = 279.4 and 11.4in = 290. Setting the height higher does not work on the ADF, but does work on the flatbet
height=279.4
mode="Black & White"

mkdir -p /home/arjun/brscan/documents

epochnow=$(date '+%s')
directory='/home/arjun/brscan/documents/'
fileprefix='scantofile'
/opt/brother/scanner/brscan-skey/script/single-sided-scan.py \
    ${directory} \
    ${fileprefix} \
    ${epochnow} \
    ${device} \
    ${resolution} \
    $height \
    $width \
    "$mode" \
    >> $logfile 2>&1 

