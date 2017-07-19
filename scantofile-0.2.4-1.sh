#! /bin/sh
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

#SCANOPTIONS="-v -v --device-name \"$device\" --mode 'Black & White' --resolution $resolution -y $height"
# -p means show progress, double -v -v makes it more verbose (the man page says it may be specified repeatedly).
# mode Gray appears to make things worse at this resolution. I have not tried True Gray.
# The scanoptions have to be escaped in some strange way like this so that everything is passed correctly to bash.

# echo the command to stdout. Then write it to logfile.
#echo "scanimage $SCANOPTIONS > $output_file"
#echo "scanimage $SCANOPTIONS > $output_file" >> $logfile 
#echo "scanimage $SCANOPTIONS > $output_file" 2>> $logfile | bash

#scanimage --verbose $SCANOPTIONS > $output_file 2>/dev/null

# if the file is zero size, run again.
#if [ ! -s $output_file ];then
  #if [ "`which usleep  2>/dev/null `" != '' ];then
    #usleep 1000000
  #else
    #sleep  1
  #fi
  #echo "Rerunning scanimage $SCANOPTIONS"
  #scanimage $SCANOPTIONS > $output_file 2>/dev/null
#
#fi

#compress_format="pdf"
#if [ -s $output_file ]; then
    #echo  $output_file is created.
    ## change ownership so arjun and szhao have access
    #chown arjun:szhao $output_file
#
    ## Should convert to jpg and delete duplicates
    #output_file_compressed=$(dirname $output_file)"/"$(basename $output_file .pnm)".$compress_format"
    #echo convert -quality 95 -density "$resolution" $output_file "$output_file_compressed" 
    #echo convert -quality 95 -density "$resolution" $output_file "$output_file_compressed" >> $logfile
    #echo convert -quality 95 -density "$resolution" "$output_file" "$output_file_compressed" | bash
    #chown arjun:szhao $output_file_compressed
#fi
