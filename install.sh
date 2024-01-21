#!/bin/bash
# based on version brscan-skey version 0.2.4-1
# needs changes if brother scripts change

shopt -s extglob
#DEFAULT_BRSCAN_DIR="/opt/brother/scanner/brscan-skey"
DEFAULT_BRSCAN_DIR="/tmp/brscan-skey"

if [ -e "$DEFAULT_BRSCAN_DIR" ]; then

    # VERSION is used for all other scripts
    # BINVERSION is used for the scantoemail script and cfg file

    VERSION=$(ls "$DEFAULT_BRSCAN_DIR"/brscan-skey*.sh | sed 's/^.*brscan-skey-//g' | sed s/"\.sh"// ) 
    eval $(grep "^BINVERSION=" "$DEFAULT_BRSCAN_DIR"/brscan-skey*.sh)
    
    echo "Detected brscan-skey version: $VERSION"
    echo "Detected brscan-skey BINVERSION: $BINVERSION"

    if [ -e "$DEFAULT_BRSCAN_DIR"/script ]; then
        #cp "!(brscan-skey-0.2.4-0.cfg)" "$DEFAULT_BRSCAN_DIR"/script -v
        /bin/cp !(brscan-skey-${BINVERSION}.cfg) $DEFAULT_BRSCAN_DIR/script -v -i
    else
        echo "script directory not found. Bad installation or incompatible version"
    fi

    echo cp brscan-skey-"$BINVERSION".cfg "$DEFAULT_BRSCAN_DIR" -v
    echo "Here are the package default options"
    echo "You may edit them at $DEFAULT_BRSCAN_DIR/brscan-skey-$BINVERSION.cfg\n"
    cat brscan-skey-"$BINVERSION".cfg
else
    echo "Default Brother brscan-skey directory does not exist at $DEFAULT_BRSCAN_DIR.\n Install and test brother drivers first."
fi


