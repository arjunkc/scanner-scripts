#! /bin/bash
set +o noclobber
#
#   $1 = scanner device
#   $2 = friendly name
#

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

function Usage() {
    echo -e "Usage:"
    echo -e "\t scantoimage.sh <devicename>\n"
    echo -e "The devicename is optional."
    echo -e "Check the source for options. Will write a png file in a default directory after scanning."
    echo -e "Heights and width can be specified in the script. So can compression format, resolution."
}

# parse one simple option. Allows you to get help
while getopts "h" opt; do
    case "$opt" in
        h)
            Usage
            exit 0
            ;;
    esac
done

# set color to full color or 24 bit. 
mode='"24Bit Color"'
#mode='"Black & White"'

logfile="/home/arjun/brscan/brscan-skey.log"
if [ -z "$1" ]; then
    device='brother4:net1;dev0'
else
    device=$1
fi

# in scantofile the widht and height are automatically set. Here, they're not.

mkdir -p ~/brscan/photos
if [ "`which usleep  2>/dev/null `" != '' ];then
    usleep 100000
else
    sleep  0.1
fi
output_file=/home/arjun/brscan/photos/brscan_photo_"`date +%Y-%m-%d-%H-%M-%S`".pnm

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
    echo  $output_file is created.
    # change ownership so arjun and szhao have access

    output_file_cropped=$(dirname $output_file)"/"$(basename $output_file .pnm)"-cropped.pnm"
    if [[ "True" == "$autocrop" ]]; then
        # maybe better to use autocrop script, which seems better for trimming dirty scanned borders
        #echo convert -trim -fuzz 10% -bordercolor white -border 20x10 +repage "$resolution" $output_file "$output_file_cropped" | bash

        # get some autotrimming information about the image 
        image_info=$(convert $output_file -virtual-pixel edge -blur 0x20 -fuzz 25% -trim info:)
        # compute an offset
        off=$(echo $image_info | awk '{print $4 }' | sed -e 's/[^+]*\(+[0-9]*+[0-9]*\)/\1/') 
        # calculate crop
        crop=$(echo $image_info | awk '{print $3}')
        echo "convert $output_file -crop $crop$off $output_file_cropped" >> "$logfile" 
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
        echo convert -trim -quality $compress_quality -density "$resolution" $output_file "$output_file_compressed" >> $logfile
        echo convert -trim -quality $compress_quality -density "$resolution" "$output_file" "$output_file_compressed" | bash
        # file ownership is best set through default acl for the destination directory
    fi
fi
