#!/bin/bash 
# From 
# https://forums.gentoo.org/viewtopic-t-166913-start-0.html
# 
# scan-pdf version 2 
# April 27, 2004 
# Copyright 2004 Zacchaeus Pearsall (zap4260 at yahoo.com) 
# Distributed under the terms of the GNU General Public License v2 

# to do
# 1. figure out how trap works

# Can set these flags to either scanonly or convert only to test individually
run_scan=True
run_convert=True

# DEBUG
DEBUG=True

DebugEcho () {
    if [[ ${DEBUG}=="True" ]]
    then
	echo "DebugEcho: " "$1"
    fi
}

# Set this to a value between 0 and 1 
# You may have to play with it some to get good scans 
# of colored paper 
THRESHOLD=0.55 

# Scan resolution 
RES=300

# Set these for the size paper you are scanning 
# defaults are X=212.5, Y=275; for US letter paper 
X=212.5 
# the height has to be set. its now 11in = 279.4 and 11.4in = 290. Setting the height higher does not work.
#Y=275 
Y=290

# Set this to the appropriate sane device for your scanner 
SCANDEVICE='brother4:net1;dev0'

# Leave this as Gray unless you have a scanner that has 
# a good useable 1-bit mode 
# cannot seem to get color to work.
SCANMODE="--mode 'Black & White'"
#SCANMODE='--mode "24bit Color"'

# If your scanner has a good 1-bit mode and you plan 
# to use it then uncomment this. I have no way to test this. 
# You may need to make some other modificatinos as well. 
#SCANNER_HAS_BW="yes" 

directory='/home/arjun/brscan/documents/'
fileprefix=${directory}'brscan'

# convert options
# Paper size for pdf output. See "man convert" for possibilites. currently unused
PAGESIZE="Letter" 
convert_opt="-density 300 -quality 95"
#convert_opt="-compress='jpeg' -quality 95"

if [[ "False" == $run_scan || -z ${1} ]]
    # if no scan (then autocreate file), or no first argument given
then 
    epochnow=$(date '+%s')
    dateiso=$(date -I)
    if [[ -e "${fileprefix}-${dateiso}.pdf" ]]; then
        PDFFILE=${fileprefix}-${dateiso}".pdf"
    else
        PDFFILE=${fileprefix}-${dateiso}-${epochnow}".pdf"
    fi 
else
    # if scan and not empty first argument
    if [ -e ${1} ] 
    then 
        echo "${1}: file exists" 
        echo "Press any key to continue, Ctrl-c to quit" 
        read -s -n 1 junk 
    fi 
    # if user didn't quit, overwrite file
    PDFFILE=${1}
fi 

TMPDIR=`/bin/mktemp -td scan-pdf.XXXXXXXXXX` 

# this creates a temporary directory that is deleted on exit. I don't know how trap works.
#trap "rm -fr ${TMPDIR}" 0 
#trap "exit 2" 1 2 3 15 

if [[ "$run_scan" == "True" ]]
then
    # Modify the scan command as needed to fit your scanner 
    SCANCMD="-x ${X} -y ${Y} --resolution ${RES}" 

    i=1 
    MORE_PAGES="y" 
    echo "To scan more sheets press space; press q when done" 
    while [ -z ${MORE_PAGES} ] || [ ${MORE_PAGES} != "q" ] 
    do 
        if [ ${i} -lt 10 ] 
        then 
            PG="pg0${i}" 
        else 
            PG="pg${i}" 
        fi 
        
        if [ ${SCANNER_HAS_BW} ] 
        then 
            "${SCANCMD}" > ${TMPDIR}/${PG}.pbm 
        else 
            #${SCANCMD} | pgmtopbm -threshold -value ${THRESHOLD} >\ 
        #${TMPDIR}/${PG}.pbm 
            DebugEcho "scanimage -d ${SCANDEVICE} ${SCANMODE} $SCANCMD > ${TMPDIR}/${PG}.pnm ${SCANCMD}"
            scanimage -d ${SCANDEVICE} --mode "Black & White" $SCANCMD > ${TMPDIR}/${PG}.pnm ${SCANCMD}
        fi 
        
        read -s -p "More (q to quit)?" -n 1 MORE_PAGES 
        echo  ' ' 
        let i++ 
    done 
else
    # if you do not run scan, expect TMPDIR on command line
    if [[ -n ${1} ]]
    then
        TMPDIR=${1}
    else
        echo "pass directory with scanned pnm files as argument"
        exit
    fi
fi

if [[ $run_convert == "True" ]]
then
    error_in_convert="False"
    for x in ${TMPDIR}/pg*.pnm
    do
        filename=$(basename $x .pnm)
        dirname=$(dirname $x)
        DebugEcho "convert ${convert_opt} $x ${dirname}/${filename}.png"
        if ! convert ${convert_opt} $x ${dirname}"/"${filename}".png"
        then
            error_in_convert="True"
        fi
    done
    if [[ ! "True" == ${error_in_convert} ]] 
    then
        img2pdf --pagesize Letter -o ${TMPDIR}/pgs.pdf ${TMPDIR}/pg*.png
        mv -i ${TMPDIR}/pgs.pdf ${PDFFILE}
    else
        mkdir -p /home/arjun/temp/scanscript
        mv ${TMPDIR} /home/arjun/temp/scanscript/
    fi

    # copy temporary files to friendly location
    if [[ "False" == ${DEBUG} ]]
    then
        #rm -rf ${TMPDIR}    
        :
    fi
fi
