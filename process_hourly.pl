#!/usr/bin/perl

##############################################################################################################
##############################################################################################################
## process_hourly.pl
##
## A perl program to process the output files of "run_build_hourly", create a suitable SHEF product
## and post it to the database via shefdecode
##############################################################################################################
##############################################################################################################
$version   = '1.00';
$input_dir = '/awips2/edex/data/share/hydroapps/precip_proc/local/data/gpp_input';
$shef_dir  = '/awips2/edex/data/share/hydroapps/shefdecode/input/';
$log_dir   = '/awips2/edex/data/share/hydroapps/precip_proc/local/data/log/gage_pp';
$send_dir  = '/awips/hydroapps/lx/rfc/data/send';

#$save_dir  = '/awips/hydroapps/lx/rfc/data/sbnprods';	# save additional hard copy
$save_dir  = $log_dir;	# to save additional hard copy of the SHEF file, change this to whatever dir you want

$log_stamp = `date -u +%m%d`;
$log_file  = "$log_dir/Process_hourlyLOG.$log_stamp";

@shef_data = ();
$item_count = 0;

$send_shef = 1;		# set to zero to suspend shef sending, >0 for send
#$send_shef = 0;		# set to zero to suspend shef sending, >0 for send


unless(open(LOG, ">>$log_file")) {				# open log file
   print "Cannot open log file:  $log_file\n";
   }


chomp($current_hour = `date -u +%H`);				# get current hour
chomp($date_for_comparison = `date -u "+%Y-%m-%d %H:00:00"`);

chomp($cur = `date -u`);
chomp($host =`hostname`);

$input_name = &get_latest_file();			 # find the latest BUILDHORLY file
$input_file = "$input_dir/$input_name";			 # create full filename with path

#print LOG "process_hourly suspended\n";
#exit();


print LOG "\nStarting process_hourly\n";
print LOG "time:  $date_for_comparison\n";
print LOG "use input file:  $input_name\n";
print LOG "host is: $host\ntime is:  $cur\n";

						 	# open the file to parse it
unless(open(INPUT, "<$input_file")) {
   print LOG "Cannot open log file:  $input_file\n";
   die("Cannot open log file:  $input_file\n");
   }

print LOG "Reading input file $input_name\n";

while(<INPUT>) { 
   s/\|/\,/g;			# replace pipe character with comma; perl doesn't like to split on the pipe | 
   
   ($lid, $pe, $dur, $pg, $z, $valid_time, $amount) = split /,/ ;
   					# value in file is to 3 places, lets get it to two places
   $value = sprintf "%0.2f", $amount;
   					# seeing some bogus reports, so eliminating any too high amounts
   if ($value > 8) {
      print LOG "Invalid amount for $lid : $value\n";
      next;
      }
						# get date, hour, etc in formats we can use
   ($date, $hour) = split / /, $valid_time;
   $full_date = "$date $hour";
   ($year, $month, $day) = split /-/, $date;
   $hour =~ s/(\d\d)\:\d\d\:\d\d/$1/;
   $print_hour = sprintf "%02d", $hour;
   $print_hour .= '00';
   $pg =~ s/^P/R/;
   						# OK, now create the shef line
                                          
#   my $shef_line = ".AR $lid $month$day DH$print_hour\/PPH $value";
   my $shef_line = ".AR $lid $month$day DH$print_hour\/PPH$pg $value";
     if ($lid =~ /FIEM7/) { print LOG "FIEM7 found $shef_line\n"; }   
   
   						# skip current hour because is usually is not complete, ie
						# not all peices of the data are in yet. buildhourly allows it
						# if 75% of data are in, but that may not be enought for 15 min
						# data in heavy rain, so delay it an hour
#   if ($full_date ge $date_for_comparison) {
#      print LOG "Too early for:  $shef_line\n";
#      next;
#      } 
   if ($full_date gt $date_for_comparison) {
      print LOG "Too early for:  $shef_line\n";
      next;
      } 
#   print LOG "compared: $full_date to $date_for_comparison\n";
#   print LOG ".AR $lid $month$day DH$print_hour\/PPH $value\n";
   						# push the SHEF line to an array
   push(@shefdata, $shef_line);
   $item_count++;
   }

						# now create the SHEF file all at once using the array we made
&make_shef_file();

print LOG "Created SHEF file with $item_count entries\n";
print LOG "Done\n.";

##############################################################################################################
##############################################################################################################
### sub make _shef_file
### This subroutine will just create the shef file.  We are creating it in the "send" directory
### could be modified to create a WMO style header or create the file elsewhere and copy to SHEF decode.
### Modify Headers to create desired prduct.
##############################################################################################################
sub make_shef_file {
my ($line, $date_string, $shef_file, $ddhhmm);

chomp($date_string = `date -u +%m%d.%H%M%S`);
chomp($ddhhmm = `date -u +%d%H%M`);

#$send_dir = '/var/tmp';
#$shef_file = "$save_dir/MKCWRKRR7.$date_string";
$shef_file = "$save_dir/MKCHOURLY.$date_string";

unless (open(SHEF, ">$shef_file") ) {
   print LOG "Cannot open shef file for writing:  $shef_file\n";
   die( "Cannot open shef file for writing:\n");
   }

print SHEF "MKCWRKRR7\n";
print SHEF "TTAA00 KKRF $ddhhmm\n";
print SHEF "MKCWRKRR7\n\n";
print SHEF ":Hourly Data built from the sub hourly reports\n\n";

foreach $line (sort(@shefdata)) {
  print SHEF "$line\n";
  }
print SHEF "\nNNNN\n";

close SHEF;

my $cp_command = "cp $shef_file $shef_dir";

if ($send_shef < 1) {
   print LOG "Not sending\n";
   return()
   }

$temp = system($cp_command);
if ( $temp) {
   print LOG "ERROR:  Could not copy file to shef directory!\n";
   }

# Fieldgen runs immediately after this, sleep a few seconds to ensure shef file has been processed

sleep(15);
   
}
##############################################################################################################
##############################################################################################################
### sub get_latest_file
### This subroutine gets a list of files with BUILD in the name, sorts the list and then grabs the top one
## which would be the latest due to date stamp.  Return that file name
##############################################################################################################
sub get_latest_file {
my(@file_list, @sorted_list);

unless ( opendir(PRODDIR, $input_dir) ) {
  print LOG "Failed to open product dir:  $input_dir\n";
  print "\nCouldn't open $input_dir to read files!\n";
  }

@file_list = grep /BUILD/, readdir(PRODDIR);
@sorted_list = sort(@file_list);

my $found_latest = pop(@sorted_list);
print LOG "Latest input file is:  $found_latest\n";

return($found_latest)
}
