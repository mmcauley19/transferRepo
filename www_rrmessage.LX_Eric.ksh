#!/usr/bin/ksh
# Gets raw www_obs file in /home/data/hydro/ingest/www.archive
# Processed file is put in /home/data/hydro/ingest/www.archive/*.processed
# HandleOUP runs sending file out SBN and acq_patterns.txt file gets 
# file and sends file to shef_decoder

#set -xv
logfile=/data/logs/ldad/wwwshef.log
(
echo "STARTING WWW SHEF DECODE at `date`" >> $logfile
APPS_DEFAULTS=/awips/hydroapps/.Apps_defaults
APPS_DEFAULTS_USER=/home/oper/.Apps_defaults
export APPS_DEFAULTS
export APPS_DEFAULTS_USER
PATH=$PATH:/home/public/bin
export PATH

dte=`date -u +%d%H%M`
input_dir=/home/data/hydro/ingest/www
archive_dir=/home/data/hydro/ingest/www.archive

fullfile=$1
file=`echo $fullfile | cut -d/ -f6`

echo "processing $input_dir/$file at $dte" >>$logfile
cat $input_dir/$file | sed '1,4d' > $archive_dir/$file.tmp


cat $archive_dir/${file}.tmp > $archive_dir/${file}.processed
cp $archive_dir/${file}.tmp /home/data/hydro/processed
chmod 666 $archive_dir/${file}.processed



#ERIC - you'll need to change "PACRRR3ACR" to something else, I'm guessing PHFORR3HFO
/awips/fxa/bin/handleOUP.pl PACRRR3ACR $archive_dir/${file}.processed
echo "done transmitting via handleOUP, sending to autodecode now"

sleep 1


mv $input_dir/${file} $archive_dir/${file}


) >> $logfile
