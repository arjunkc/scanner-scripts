#! /bin/bash
set +o noclobber
#
#   $1 = scanner device
## changed this   $2 = friendly name
#   $2 = email address 

#   
#       100,200,300,400,600
#

# JPG quality can be adjusted

SENDMAIL="`which sendmail   2> /dev/null`"
if [ "$SENDMAIL" = '' ];then
    SENDMAIL="/usr/sbin/sendmail"
fi
if [ ! -e  ];then
    echo "sendmail is not available."
fi

#-----------------------
debug_log='/var/log/brscan-skey.log'
scanimage_disable='no'
sendmail_disable='no'
sendmail_log='0'
#-----------------------
#log='1'
resolution=200
jpgquality='-quality 90 -density 200'

# set to arjun's default scanner if no argument 
if [ -z "$1" ]; then
    device='brother4:net1;dev0'
else
    device=$1
fi

mkdir -p ~/brscan
if [ "`which usleep  2>/dev/null `" != '' ];then
    usleep 100000
else
    sleep  0.1
fi

#echo "scan from $2($device)"

email_debug_option=''

if [ "$scanimage_disable" != 'yes' ];then
    tmpscnfile=`mktemp ~/brscan/brscan-tmp.XXXXXX`
    if [ "$device" = '' ];then
        # with my new code which sets a default device, this is not necessary
	scanimage --resolution $resolution  2>/dev/null > $tmpscnfile
    else
	scanimage --device-name "$device" --resolution $resolution 	    2>/dev/null  > $tmpscnfile
    fi

    if [ ! -s $tmpscnfile ];then
      if [ "`which usleep  2>/dev/null `" != '' ];then
        usleep 1000000
      else
        sleep  1
      fi
      if [ "$device" = '' ];then
	scanimage --resolution $resolution  2>/dev/null > $tmpscnfile
      else
	scanimage --device-name "$device" --resolution $resolution 	    2>/dev/null  > $tmpscnfile
      fi
    fi

    # convert if possible, then store a copy in brscan/documents 
    output_file=/home/arjun/brscan/documents/brscan_docs_"`date +%Y-%m-%d-%H-%M-%S`"
    if [ -e "`which convert 2>/dev/null `" ];then
        output_file=${output_file}".jpg"
        FILENAME="/home/arjun/brscan/brscan-skey.jpg"
        if convert $jpgquality $tmpscnfile $FILENAME; then
            # the code is inefficient, but makes it easier to modify
            # makes a hardlink, so no loss of space
            cp -al $FILENAME $output_file
            rm $tmpscnfile
        fi
    else 
        # Do no conversion. Store as pnm, but make an extra copy to email.
        output_file=${output_file}".pnm"
        FILENAME="/home/arjun/brscan/brscan-skey.pnm"
        # make hardlinks, no extra copies.
        cp -al $tmpscnfile $output_file
        mv $tmpscnfile $FILENAME
    fi

else
    echo DEBUG DATA :012345678901234567890123456789 > $output_file
fi

FLABEL='^FROM'
TLABEL='^TO'
CLABEL='^CC'
BLABEL='^BCC'
MLABEL='^MESSAGE'
SLABEL='^SUBJECT'

CONF=~/.brscan/'brscan_mail.config'
if [ ! -e $CONF ];then
  CONF=/opt/brother/scanner/brscan-skey//'brscan_mail.config'
fi

DEBUG="`grep 'DEBUG=1' $CONF`"
if [ "$DEBUG" != '' ];then
    sendmail_disable='silent'
fi

FADR="`grep $FLABEL=  $CONF | sed s/$FLABEL=//g`" 
TADR="`grep $TLABEL=  $CONF | sed s/$TLABEL=//g`" 
CADR="`grep $CLABEL=  $CONF | sed s/$CLABEL=//g`" 
BADR="`grep $BLABEL=  $CONF | sed s/$BLABEL=//g`" 

MSGT="`grep $MLABEL=  $CONF | sed s/$MLABEL=//g`" 
if [ "$MSGT" != '' ];then
    MESG=$MSGT
    if [ ! -e "$MESG" ];then
	MESG=~/.brscan/"$MSGT"
	if [ ! -e "$MESG" ];then
	    MESG=/opt/brother/scanner/brscan-skey/"$MSGT"
	fi
    fi
else
    MESG="''"
fi
SUBJECT="`grep $SLABEL=  $CONF | sed s/$SLABEL=//g`"" Scanned on : "$(date +%Y-%m-%d-%H-%M-%S)

if [ "$2" != '' ];then
    # if second argument not empty
    TADR="`echo $3 | sed -e s/:.*$//`"
fi


if [ "$TADR" = '' ] || [ ${#TADR} -gt 256 ];then
    echo "E-mail Address Error:"
    echo "   E-mail address setting is not valid."
    echo "   E-mail address is not defined or the setting"
    echo "   might be larger than 256 characters."
    exit 0;
fi

if [ "$FADR" = '' ];then
    FADR="`whoami | sed s/\" .*$\"//g`"
fi
if [ "$FADR" = '' ];then
    FADR="''"
fi

# The if statement may be removed. It's useful to write the output_file in this way so that I don't later have to replace their code.
#if [ "$FILENAME" = '' ];then
#FILENAME=$output_file
#fi

command_line="$SENDMAIL -t $TADR"
command_flog="$SENDMAIL -t $TADR"

case "$sendmail_log" in
    "0") email_debug_option='';;
    "1") email_debug_option='--debug-mode L';command_line="cat";;
    "2") email_debug_option='--debug-mode M';command_line="cat";;
    "4") email_debug_option='--debug-mode H';command_line="cat";;
    "5") email_debug_option='--debug-mode l';command_line="cat";;
    "6") email_debug_option='--debug-mode m';command_line="cat";;
    "3") email_debug_option='--debug-mode h';command_line="cat";;
    *  ) email_debug_option='';;
esac

if [ $sendmail_disable = 'yes' ];then
    command_line="cat";
elif [ $sendmail_disable = 'silent' ];then
    command_line="head  -6";
fi

if [ -e "/opt/brother/scanner/brscan-skey/script/brscan_scantoemail"-"0.2.4-0" ];then
      touch "$debug_log"
      if [ -e "$debug_log" ];then
	echo -e "-----------------------------\n \
	/opt/brother/scanner/brscan-skey/script/brscan_scantoemail-"0.2.4-0" \n\
	    -t "$TADR" \n\
	    -r "$FADR" \n\
	    -c "$CADR" \
	    -b "$BADR" \
	    -f "$FILENAME" \
	    -M "$MESG" \
	    -S "$SUBJECT" \
	    $output_file  \|  $command_flog    \n\
	to  : $TADR    \n\
	from: $FADR    \n\
	cc  : $CC    \n\
	bcc : $BCC    \n\
	subject: $SUBJECT    \n\
	name: $FILENAME    \n\
	img : $output_file    \n\
	----------------------------- \n" >> $debug_log
     fi
     /opt/brother/scanner/brscan-skey/script/brscan_scantoemail-"0.2.4-0" \
	-t "$TADR" \
	-r "$FADR" \
	-c "$CADR" \
	-b "$BADR" \
	-f "$FILENAME" \
	-M "$MESG" \
	-S "$SUBJECT" \
        $email_debug_option \
	$output_file    |  $command_line

     # It seems that this is unnecessary. I'll comment it out.
     #if [ "$log" != '' ];then
	#touch $log
	#echo ''
	#echo ----------------------------- >> $log
	#echo to  : $TADR                  >> $log
	#echo from: $FADR                  >> $log
	#echo cc  : $CC                    >> $log
	#echo bcc : $BCC                   >> $log
	#echo subject: $SUBJECT            >> $log
	#echo name: $FILENAME              >> $log
	#echo mesg: $MESG                  >> $log
	#echo img : $output_file           >> $log
	#echo ----------------------------- >> $log
     #fi

else
    echo ERROR: /opt/brother/scanner/brscan-skey/script/brscan_scantoemail-"0.2.4-0" \
	-t $TADR \
	-r $FADR \
	-f $FILENAME \
	-M $MESG \
	$output_file  \| $command_flog
fi

# FILENAME was a temporary file with a short name making it easier to email. There is a copy saved.
rm -f $FILENAME

