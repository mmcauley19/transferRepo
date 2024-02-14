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
#input_dir=/home/data/hydro/ingest/test
input_dir=/home/data/hydro/ingest/www
#archive_dir=/home/data/hydro/ingest/test.archive
archive_dir=/home/data/hydro/ingest/www.archive

fullfile=$1
file=`echo $fullfile | cut -d/ -f6`


##remove these 2 lines
##file=$fullfile


#for file in `ls $input_dir`
#do
echo "processing $input_dir/$file at $dte" >>$logfile
#cat $input_dir/$file | sed '1,4d' > $archive_dir/$file.tmp
cat $input_dir/$file | sed '1,4d' > $archive_dir/$file.tmp
#cp $input_dir/$file $archive_dir/$file.tmp

cp /dev/null $archive_dir/shef.tmp
cp /dev/null $archive_dir/shef.tmp2

# check to see if this is a slope site and create stage value.
# also change the slope letter to the shef number and add
# the stage value to the shef message

if [ "`grep HQIRV ${archive_dir}/${file}.tmp`" != "" ] ; then
 site=`awk '{print $2}' $archive_dir/$file.tmp`
 site=`echo $site | tr "[A-Z]" "[a-z]"`

  # Check to see if shef message also contains a slope
  #if [ "`grep HGIRV ${archive_dir}/${file}.tmp`" != "" ] ; then
   #num=`cut -d/ -f3 $archive_dir/$file.tmp | awk '{print $2}' | wc -c `
   #num=`expr $num - 1`
   #marker=`cut -d/ -f3 $archive_dir/$file.tmp | awk '{print $2}' | cut -c$num`
   #num2=`expr $num - 1`
   #slope=`cut -d/ -f3 $archive_dir/$file.tmp | awk '{print $2}' | cut -c1-$num2`
  #fi

 num=`cut -d/ -f2 $archive_dir/$file.tmp | awk '{print $2}' | wc -c `
echo "num=$num"
 num=`expr $num - 1`
echo "num=$num"
 marker=`cut -d/ -f2 $archive_dir/$file.tmp | awk '{print $2}' | cut -c$num`
 num2=`expr $num - 1`
echo "num2=$num2"
 slope=`cut -d/ -f2 $archive_dir/$file.tmp | awk '{print $2}' | cut -c1-$num2`
 slope2=`echo $slope \ / 1000 | bc -l | cut -c1-5`
echo "site=$site"
echo "slope=$slope"
echo "marker=$marker"
echo "Running /awips/hydroapps/local/utl/slope_stg_flw_alone/Hq2Hg_stnd_alone $site$marker $slope"
ssh ds -l oper /awips/hydroapps/local/utl/slope_stg_flw_alone/Hq2Hg_stnd_alone $site$marker $slope > $archive_dir/${site}.stg.tmp
#remsh ds -l oper /awips/hydroapps/local/utl/slope_stg_flw_alone/Hq2Hg_stnd_alone $site$marker $slope > $archive_dir/stg.tmp
echo "output = $archive_dir/${site}.stg.tmp"
echo "will cat output file"
cat $archive_dir/${site}.stg.tmp
 stage=`cut -c1-5 $archive_dir/${site}.stg.tmp`
 #stage=`cat $archive_dir/stg.tmp`
echo "stage=$stage"
  if [ "$marker" = "a" ] ; then
    marker2="1"
  elif [ "$marker" = "b" ] ; then
    marker2="2"
  elif [ "$marker" = "c" ] ; then
    marker2="3"
  elif [ "$marker" = "d" ] ; then
    marker2="4"
  elif [ "$marker" = "e" ] ; then
    marker2="5"
  elif [ "$marker" = "f" ] ; then
    marker2="6"
  elif [ "$marker" = "g" ] ; then
    marker2="7"
  elif [ "$marker" = "h" ] ; then
    marker2="8"
  elif [ "$marker" = "i" ] ; then
    marker2="9"
  elif [ "$marker" = "s" ] ; then
    marker2="19"
  else 
    marker2="1"
  fi
 #echo "slope=$slope"
 #echo "marker=$marker"
 #echo "stage=$stage"
 sed -n s/"\/HQIRV"/"\/HGIRV $stage\/HQIRV"/p $archive_dir/$file.tmp >> $archive_dir/shef.tmp
 sed -n s/"\/HQIRV $slope$marker"/"\/HQIRV $marker2$slope2"/p $archive_dir/shef.tmp >> $archive_dir/shef.tmp2 
 #print "SRAK58 PACR $dte" > $archive_dir/${file}.processed
 #print "ACRRR3ACR" >> $archive_dir/${file}.processed
 #print "&& WEBFORM DATA REPORT" >> $archive_dir/${file}.processed
 #print "" > $archive_dir/${file}.processed
 cat $archive_dir/shef.tmp2 > $archive_dir/${file}.processed
 cp $archive_dir/${file}.tmp /home/data/hydro/processed/${file}.tmp
else
 #print "SRAK58 PACR $dte" > $archive_dir/${file}.processed
 #print "ACRRR3ACR" >> $archive_dir/${file}.processed
 #print "&& WEBFORM DATA REPORT" >> $archive_dir/${file}.processed
#print "" > $archive_dir/${file}.processed
#cat "$archive_dir/${file}.tmp"
cat $archive_dir/${file}.tmp > $archive_dir/${file}.processed
cp $archive_dir/${file}.tmp /home/data/hydro/processed

fi
chmod 666 $archive_dir/${file}.processed

###sed -f /awips/hydroapps/local/datatools/www_ids.sed $archive_dir/${file}.processed > $archive_dir/${file}.tmp


/awips/fxa/bin/handleOUP.pl PACRRR3ACR $archive_dir/${file}.processed
echo "done transmitting via handleOUP, sending to autodecode now"

sleep 1


#sed 1d $archive_dir/${file}.tmp > $archive_dir/${file}.tmp2
/awips/hydroapps/local/decoders/AutoDecode_linux $archive_dir/${file}.tmp
#cp $archive_dir/${file}.tmp /home/data/hydro/processed

#print "SRAK58 PACR $dte" > $archive_dir/${file}.processed
#print "ACRRR3ACR" >> $archive_dir/${file}.processed
#print "&& WEBFORM DATA REPORT" >> $archive_dir/${file}.processed
#cat $archive_dir/${file}.tmp >> $archive_dir/${file}.processed
## send to netcdf processing
#/awips/hydroapps/local/decoders/AutoDecode $archive_dir/${file}.processed
#rm $archive_dir/${file}.tmp
mv $input_dir/${file} $archive_dir/${file}
rm -f $archive_dir/shef.tmp $archive_dir/shef.tmp2 $archive_dir/stg.tmp $archive_dir/${site}.stg.tmp

#done

) >> $logfile
