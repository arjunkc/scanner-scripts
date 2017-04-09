#! /bin/sh
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
#   Apr 01 2016 To do, implement compression if possible.
#   Dec 31 2016 to do, combine even and odd files into one big pdf file

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
# makes output files that look like part-01.pnm and so on. Increase the %02d if you have more than 99 documents.
# scantoocr should use epoch to make it easy

date=$(date '+%F')
hour=$(date '+%H')
min=$(date '+%rM')
epochnow=$(date '+%s')
directory='/home/arjun/brscan/documents/'
fileprefix=${directory}'brscan'
/opt/brother/scanner/brscan-skey/script/double-sided-scan.py ${directory} 'brscan' $epochnow $device $resolution $height $width "$mode" >> $logfile 2>&1

