#! /bin/bash
set +o noclobber
#
#   $1 = scanner device
#   $2 = brother internal
#   
#   This is my scantoimage. It's mostly the same as Brothers script, but it allows some more environment variables to be set using the cfg file so we don't have to edit the script directly.

function Usage() {
    echo -e "Usage:"
    echo -e "\t "$0" [option] <devicename>\n"
    echo -e "The devicename is optional. Set by default to ${default_device}"
    echo -e "Check the source for options. Will write a $compress_format file if the compress variable is set to True. The current value is $compress. If set to False, then the scan format is $scan_format"
    echo -e "Heights and width can be specified in the script. So can resolution."
    echo -e "\nOptions:"
    echo -e "\t -h \t Print this help"
}

# scan options
scan_format="pnm"
compress="True"
compress_format="jpg"
compress_quality="95"
autocrop="True"
#autocrop="False"
# set color to full color or 24 bit. 
mode='24Bit Color' #'Black & White'

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

#   List devices with scanimage -L
#   Query device with scanimage -h to get allowed resolutions
#   In color, resolution more than 300 slows things down on lower model printers 

if [[ -z "$IMAGEDPI" ]]; then
    resolution=600
else
    resolution="$IMAGEDPI"
fi

# height and width can be left empty to 
# be autodetected
if [[ -n "$IMAGEHEIGHT" ]]; then
    height="$IMAGEHEIGHT"
fi

if [[ -n "$IMAGEWIDTH" ]]; then
    width="$IMAGEWIDTH"
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


epochnow=$(date '+%Y-%m-%d-%H-%M-%S')

# for debugging purposes, output arguments
echo "options after processing." >> ${logfile}
echo "$*" >> ${logfile}
# export environment to logfile
set >> ${logfile}
echo $LOGDIR >> ${logfile}

# BEGIN SCAN PROCEDURE
if [ "`which usleep 2>/dev/null`" != '' ]; then
    usleep 100000
else
    sleep 0.1
fi

batch_prefix="$SAVETO/brscan_image_${epochnow}"
batch_pattern="${batch_prefix}-%03d.${scan_format}"

# build scanimage command as array to handle arguments with spaces safely
if [[ -z "$height" || -z "$width" ]]; then
    scancmd=(scanimage --batch="$batch_pattern" --mode "$mode" --device-name "$device" --resolution "$resolution" --format "$scan_format")
else
    scancmd=(scanimage --batch="$batch_pattern" --mode "$mode" --device-name "$device" --resolution "$resolution" -x "$width" -y "$height" --format "$scan_format")
fi

echo "${scancmd[@]}" | tee -a "$logfile"
"${scancmd[@]}" 2>> "$logfile"

# collect batch output files
output_files=("${batch_prefix}"-*.${scan_format})

# retry once if no files produced
if [ ${#output_files[@]} -eq 0 ] || [ ! -e "${output_files[0]}" ]; then
    if [ "`which usleep 2>/dev/null`" != '' ]; then
        usleep 1000000
    else
        sleep 1
    fi
    echo "Rerunning: ${scancmd[@]}" | tee -a "$logfile"
    "${scancmd[@]}" 2>> "$logfile"
    output_files=("${batch_prefix}"-*.${scan_format})
fi

# process each scanned file
for output_file in "${output_files[@]}"; do
    [ -e "$output_file" ] || continue

    if [ ! -s "$output_file" ]; then
        echo "Skipping empty file: $output_file" | tee -a "$logfile"
        continue
    fi
    echo "$output_file is created." | tee -a "$logfile"

    if [[ "True" == "$autocrop" ]]; then
        output_file_cropped="$(dirname "$output_file")/$(basename "$output_file" .${scan_format})-cropped.${scan_format}"
        image_info=$(convert "$output_file" -virtual-pixel edge -scale 25% -blur 0x5 -resize 400% -fuzz 10% -trim info:)
        off=$(echo "$image_info" | awk '{print $4}' | sed -e 's/[^+]*\(+[0-9]*+[0-9]*\)/\1/')
        crop=$(echo "$image_info" | awk '{print $3}')
        echo "convert $output_file -crop $crop$off $output_file_cropped" | tee -a "$logfile"
        if convert "$output_file" -crop "$crop$off" "$output_file_cropped"; then
            cp "$output_file_cropped" "$output_file"
            rm "$output_file_cropped"
        fi
    fi

    if [[ "True" == "$compress" ]]; then
        output_file_compressed="$(dirname "$output_file")/$(basename "$output_file" .${scan_format}).${compress_format}"
        echo "convert -quality $compress_quality -density $resolution $output_file $output_file_compressed" | tee -a "$logfile"
        convert -quality "$compress_quality" -density "$resolution" "$output_file" "$output_file_compressed" 2>> "$logfile"
    fi
done
