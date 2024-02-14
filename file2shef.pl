#!/usr/bin/perl
###########################################################################
# moves shef file from the LS1:/data/Incoming to shef dir on DS
###########################################################################
##$file = $ARGV[0];
##system "mv $file /awips/hydroapps/shefdecode/raw_data";

open (STDERR, ">>/data/logs/ldad/hydro_ldad.log");
$file = $ARGV[0];
print STDERR "$file \n";
##if ( $file =~ /hd/ ) {system "cp $file /home/data/hydro/ingest/observers"};
##if ( $file != /hd/ ) {system "cp $file /home/data/hydro/ingest/www"};

# can remove next line if above if statements work okay
system "cp $file /home/data/hydro/ingest/www";
system "/awips/hydroapps/local/datatools/www_rrmessage.LX.ksh $file";

# can comment out next line to use the SBN feed only
#system "mv $file /awips/hydroapps/shefdecode/raw_data";

exit;

###########################################################################
############################End of Program#################################
