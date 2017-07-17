#!/usr/bin/python3

# Objectives: scan single sided files. convert to pdf. 

import os,sys,re,time,datetime,subprocess

from scanutils import *

# SETTINGS
part = 'part'
timeoffset = 5*60 # in seconds
as_script = False
debug = True 
logfile = '/home/arjun/brscan/double-sided-scan.log'
lfile = open(logfile,'a')
waitlimit = 300 # a limit for waiting to fix errors

# SCRIPT START
# read arguments 
# see if run as a script

if not re.match(r'/usr/bin/.*python.*',sys.argv[0]):
    as_script = True

args = sys.argv
[directory,prefix,timenow,device,resolution,height,width,mode] \
        = parse_arguments(as_script,args)

