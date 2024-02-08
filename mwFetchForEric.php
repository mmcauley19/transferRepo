<?php
//edits for ft greely station 06/04/2023 MM starting line 74
date_default_timezone_set('UTC');
header("Content-Type:text/plain");
$today = date("Ymd")."000000";

//06/02/2023 MM- Fort Greely stations are getting reset at 1 am local? so need to change methodology
//for BAXA2 BKCA2 GEOA2 GRLA2 MISA2 OPTA2 PANA2 TEXA2 WSHA2 jjjj

//list of normal stations 
$lids = array("AFTA2","BAXA2","BKCA2","BOLA2","GEOA2","GRLA2","MAPA2","MGTA2","MISA2","NTTA2","OPFA2","OPOA2",
             "OPSA2","OPTA2","PANA2","SFDA2","TCOA2","TEXA2","WSHA2","BWSA2","LGCA2","TGCA2","ETBA2","MHPA2",
	      "ECEA2","TSLA2","DVCA2","HEAA2","PPSA2","JTMA2","WRTA2","HHKA2","HHWA2","COHA2","GOOA2", "EGNA2",
              "THTA2","THNA2","UHSA2"); // access via timeseries
//list of werid stations
$ftGreely = array("BAXA2","BKCA2","GEOA2","GRLA2","MISA2","OPTA2","PANA2","TEXA2","WSHA2","UHSA2");
$cwop = array("UHSA2"); 

//output variable is the SHEF encoded
$output = 'SRAK58 PACR '.date("dHi")."\nRR3ACR\n\n\n:APRFC ingest from mesowest\n";
//Get API token using API key. We use mesowest because that's what it used to be called (and still works)... feel free to replace 
//"mesowest" with "synopticdata" in URLs 
$apiToken = json_decode(file_get_contents("http://api.mesowest.net/v2/auth?apikey=f6f404875a5d4c8a953bc49bf3412bfb"));

foreach ($lids as $sid){
	echo $sid."\n";
	$datUrl = "http://api.mesowest.net/v2/stations/timeseries?&stid=".$sid."&recent=120&token=".$apiToken->TOKEN;
	echo $datUrl."\n";
	$datObj = json_decode(file_get_contents($datUrl));

	//Check for PP
        //Eric, hopefully this if block is all you need
    if (isset($datObj->STATION[0]->OBSERVATIONS->precip_accum_one_hour_set_1)){
        foreach($datObj->STATION[0]->OBSERVATIONS->precip_accum_one_hour_set_1 as $key => $ob){
            $dtg = preg_replace("/[^0-9,.]/", "", $datObj->STATION[0]->OBSERVATIONS->date_time[$key] );
            $ymd = substr($dtg, 0,8);
            $hm = substr($dtg,8,4);
            if (is_null($ob)){$pp = -9999;}else{
                    $pp = sprintf("%01.2f", $ob * 0.0393701); //convert mm to in
            }
            //shef encode
            $output .= ".AR ".$sid." ".$ymd." Z DH".$hm."/DC".$ymd.$hm."/PPIRZZ ".$pp."/\n";
        }
    }
	
	//Check for PC
	if (isset($datObj->STATION[0]->OBSERVATIONS->precip_accum_set_1)){
           //MM add on for difficult Ft Greely stations that we actually have to create our own PP because 
           //the accumulation resets at 1am (annoying) 6/4/2023
           //Eric- you can probably ignore this if and go straight to the else 
           if (in_array($sid,$ftGreely)){
           //do stuff
            $hourlyObs = array();
            foreach($datObj->STATION[0]->OBSERVATIONS->precip_accum_set_1 as $key => $ob){
             $dtg = preg_replace("/[^0-9,.]/", "", $datObj->STATION[0]->OBSERVATIONS->date_time[$key] );
             $ymd = substr($dtg, 0,8);
             $hm = substr($dtg,8,4);
             if (substr($hm,2,2) == "00"){ //we just want the even hour, not every 5 min
             //enter hourly ob into array
              if (is_null($ob)){ $ob = 0.0; }
               $hourlyObs[] = (object) array('time' => $ymd.$hm, 'value' => $ob);
             }
            }
            //now loop through and calculate the increment. Have to go backward since latest is last
            for ($i=count($hourlyObs)-1;$i>=1;$i--){
             $increment = $hourlyObs[$i]->value - $hourlyObs[$i-1]->value;
             #if ($increment <0){ $increment=0;}
	     if ($increment <0){ $increment=$hourlyObs[$i]->value;} #changed b/c if it was raining when the precip accum was reset, the value was set to 0 instead of the actual hourly value
             $ymd = substr($hourlyObs[$i]->time,0,8);
             $hm = substr($hourlyObs[$i]->time,8,4);
             $pp = sprintf("%01.2f", $increment * 0.0393701); //convert mm to in
             $output .= ".AR ".$sid." ".$ymd." Z DH".$hm."/DC".$ymd.$hm."/PPHR2Z ".$pp."/\n";
            }
           }
           else{
		foreach($datObj->STATION[0]->OBSERVATIONS->precip_accum_set_1 as $key => $ob){
			$dtg = preg_replace("/[^0-9,.]/", "", $datObj->STATION[0]->OBSERVATIONS->date_time[$key] );
			$ymd = substr($dtg, 0,8);
			$hm = substr($dtg,8,4);
			if (is_null($ob)){$pc = -9999;}else{
				$pc = sprintf("%01.2f", $ob * 0.0393701); //convert mm to in
			}
			$output .= ".AR ".$sid." ".$ymd." Z DH".$hm."/DC".$ymd.$hm."/PCIRZZ ".$pc."/\n";
		}
           }
	}
	//Check for TA
	if (isset($datObj->STATION[0]->OBSERVATIONS->air_temp_set_1)){
		foreach($datObj->STATION[0]->OBSERVATIONS->air_temp_set_1 as $key => $ob){
			$dtg = preg_replace("/[^0-9,.]/", "", $datObj->STATION[0]->OBSERVATIONS->date_time[$key] );
			$ymd = substr($dtg, 0,8);
			$hm = substr($dtg,8,4);
			if (is_null($ob)){$ta = -9999;}else{
				$ta = sprintf("%01.1f", ($ob * 1.8)+32); // convert C to F
			}
			$output .= ".AR ".$sid." ".$ymd." Z DH".$hm."/DC".$ymd.$hm."/TAIRZZ ".$ta."/\n";
		}
	}
	//Check for US
	if (isset($datObj->STATION[0]->OBSERVATIONS->wind_speed_set_1)){
		foreach($datObj->STATION[0]->OBSERVATIONS->wind_speed_set_1 as $key => $ob){
			$dtg = preg_replace("/[^0-9,.]/", "", $datObj->STATION[0]->OBSERVATIONS->date_time[$key] );
			$ymd = substr($dtg, 0,8);
			$hm = substr($dtg,8,4);
			if (is_null($ob)){$us = -9999;}else{
				$us = sprintf("%01.1f", $ob * 2.23693629); // convert m/s to mph
			}
			$output .= ".AR ".$sid." ".$ymd." Z DH".$hm."/DC".$ymd.$hm."/USIRZZ ".$us."/\n";
		}
	}
	//Check for UP
	if (isset($datObj->STATION[0]->OBSERVATIONS->wind_gust_set_1)){
		foreach($datObj->STATION[0]->OBSERVATIONS->wind_gust_set_1 as $key => $ob){
			$dtg = preg_replace("/[^0-9,.]/", "", $datObj->STATION[0]->OBSERVATIONS->date_time[$key] );
			$ymd = substr($dtg, 0,8);
			$hm = substr($dtg,8,4);
			if (is_null($ob)){$up = -9999;}else{
				$up = sprintf("%01.1f", $ob * 2.23693629); // convert m/s to mph
			}
			$output .= ".AR ".$sid." ".$ymd." Z DH".$hm."/DC".$ymd.$hm."/UPIRZZ ".$up."/\n";
		}
	}
	//Check for UD
	if (isset($datObj->STATION[0]->OBSERVATIONS->wind_direction_set_1)){
		foreach($datObj->STATION[0]->OBSERVATIONS->wind_direction_set_1 as $key => $ob){
			$dtg = preg_replace("/[^0-9,.]/", "", $datObj->STATION[0]->OBSERVATIONS->date_time[$key] );
			$ymd = substr($dtg, 0,8);
			$hm = substr($dtg,8,4);
			if (is_null($ob)){$ob = -9999;}
			$output .= ".AR ".$sid." ".$ymd." Z DH".$hm."/DC".$ymd.$hm."/UDIRZZ ".$ob."/\n";
		}
	}
	//Check for XR
	if (isset($datObj->STATION[0]->OBSERVATIONS->relative_humidity_set_1)){
		foreach($datObj->STATION[0]->OBSERVATIONS->relative_humidity_set_1 as $key => $ob){
			$dtg = preg_replace("/[^0-9,.]/", "", $datObj->STATION[0]->OBSERVATIONS->date_time[$key] );
			$ymd = substr($dtg, 0,8);
			$hm = substr($dtg,8,4);
			if (is_null($ob)){$ob = -9999;}
//			if (!isset($latestObs[$sid]['xr'])){
//            	$latestObs[$sid]['xr'] = array();
//            }
//            if(in_array($dtg,$latestObs[$sid]['xr'])){
//            	continue; //we already processed this ob
//            }else{
//            	$latestObs[$sid]['xr'][] = $dtg; //add it
//            }
			$output .= ".AR ".$sid." ".$ymd." Z DH".$hm."/DC".$ymd.$hm."/XRIRZZ ".$ob."/\n";
		}
	}
	//Check for SD
	if (isset($datObj->STATION[0]->OBSERVATIONS->snow_depth_set_1)){
		foreach($datObj->STATION[0]->OBSERVATIONS->snow_depth_set_1 as $key => $ob){
			$dtg = preg_replace("/[^0-9,.]/", "", $datObj->STATION[0]->OBSERVATIONS->date_time[$key] );
			$ymd = substr($dtg, 0,8);
			$hm = substr($dtg,8,4);
			if (is_null($ob)){$sd = -9999;}else{
				$sd = sprintf("%01.2f", $ob * 0.0393701); //convert mm to in
			}
//			if (!isset($latestObs[$sid]['sd'])){
//            	$latestObs[$sid]['sd'] = array();
//            }
//            if(in_array($dtg,$latestObs[$sid]['sd'])){
//            	continue; //we already processed this ob
//            }else{
//            	$latestObs[$sid]['sd'][] = $dtg; //add it
//            }
			$output .= ".AR ".$sid." ".$ymd." Z DH".$hm."/DC".$ymd.$hm."/SDIRZZ ".$sd."/\n";
		}
	}
	//Check for precip_accum_since_local_midnight   -> ONLY Needed for ETBA2 and MHPA2 and TSLA2 and ECEA2 as this is the only precip for these stations
	if (isset($datObj->STATION[0]->OBSERVATIONS->precip_accum_since_local_midnight_set_1) && ($sid == "ETBA2" || $sid == "ECEA2" || $sid == "MHPA2" || $sid == "TSLA2")){
		print $sid."\n";
		//find out what local midnight is in UTC for this time of the year
		//Changed local midnight to 0015 as that's when the gages reset except for TSLA2
		date_default_timezone_set('America/Anchorage');
		if ($sid == "TSLA2"){
			$localMidnight = date("Ymd")."0000";
		}else{
			$localMidnight = date("Ymd")."0015";
		}
		$utcMidnight = gmdate("YmdHi", strtotime($localMidnight));
		date_default_timezone_set('UTC');
		//print $utcMidnight."\n";
		//get datetime for latest ob and use it for '&end=' in this query
		$idxLast = count($datObj->STATION[0]->OBSERVATIONS->date_time)-1;
		$ppmDtg = preg_replace("/[^0-9,.]/", "", $datObj->STATION[0]->OBSERVATIONS->date_time[$idxLast] );
		$orig120MinObTime = preg_replace("/[^0-9,.]/", "", $datObj->STATION[0]->OBSERVATIONS->date_time[0] );
		$origDtg = substr($orig120MinObTime, 0,12);
		$ppmYmd = substr($ppmDtg, 0,8);
		$ppmHm = substr($ppmDtg,8,4);
		//print $ppmYmd.$ppmHm."\n";
		//new query
		$ppmUrl = "http://api.mesowest.net/v2/stations/timeseries?&vars=precip_accum_since_local_midnight&stid=".$sid."&start=".$utcMidnight."&end=".$ppmYmd.$ppmHm."&token=".$apiToken->TOKEN;
		$ppmObj = json_decode(file_get_contents($ppmUrl));
		//print_r($ppmObj);

		//VERIFY units  These had changed from inches to millimeters without notice so we will check each time
		try {
			$ppmUnit = $ppmObj->UNITS->precip_accum_since_local_midnight;
		} catch (exception $e) {
			echo "Caught exception: ", $e->getMessage(),"while querying ".$sid."\n";	
		}
		//These two stations are special cases where we obtain hourly pp from the accum_since_local_midnight by
		//saving the obs that occur near the top of the hour and subtracting the prior ob to get that hour's total
		//MHPA2 starts it's accumulation at 00:19 so it's initial value is truncated.
		$MHPA2_hourly_obs = array();
		$SAXA2_hourly_obs = array();
		// The $key matches the ob to the obtime
		foreach($ppmObj->STATION[0]->OBSERVATIONS->precip_accum_since_local_midnight_set_1 as $key => $ob){
		    //Get date-time data
			$dtg = preg_replace("/[^0-9,.]/", "", $ppmObj->STATION[0]->OBSERVATIONS->date_time[$key] );
			$ymd = substr($dtg, 0,8);
			$hm = substr($dtg,8,4);
			$minute = substr($dtg,10,2);
			
			#This conditional has '$key >= 1 &&' to ensure that there's a value to subtract from. Nothing has accumulated at key[0]...
			#$origDtg is used as the mark for when we start printing obs since we only want the last 2 hours worth.
			if ($key >= 1 && $ymd.$hm >= $origDtg){
				$currOb = $ppmObj->STATION[0]->OBSERVATIONS->precip_accum_since_local_midnight_set_1[$key];
				$lastOb = $ppmObj->STATION[0]->OBSERVATIONS->precip_accum_since_local_midnight_set_1[$key-1];
				$currObTime = $ppmObj->STATION[0]->OBSERVATIONS->date_time[$key];
				$lastObTime = $ppmObj->STATION[0]->OBSERVATIONS->date_time[$key-1];
				if (is_null($ob)){$ob = -9999;}
				
//				if ($netOb < 0){
//					print "Error: Negative value encountered\n";
//					print "Current Ob: ".$currOb." at ".$currObTime."\n";
//					print "Last Ob: ".$lastOb." at ".$lastObTime."\n";
//					exit;
//				}
				//Check units
				if ($ppmUnit == "Millimeters"){
					$ob = sprintf("%01.2f", $ob * 0.0393701);//convert mm to in
				}else{
					print "We have encountered an unexpected unit of measurement: ".$ppmUnit."\n";
					exit;
				}
//				if(in_array($dtg,$latestObs[$sid]['pp'])){
//		        	continue; //we already processed this ob
//		        }else{
//		        	$latestObs[$sid]['pp'][] = $dtg; //add it
//		        }
				$output .= ".AR ".$sid." ".$ymd." Z DH".$hm."/DC".$ymd.$hm."/PPIRZZ ".$ob."/\n";

			}
		}
	}
}
//file_put_contents("/ldad/localapps/mesowestFetch/latestObs.json",json_encode($latestObs));
$filename = "mesowestObs_".date("YmdHi").".sheffile";
file_put_contents($filename, $output);
echo "Wrote ".$filename." to disk.\n";
exec('find ./last24 -type f -mtime +1 -exec rm {} \;');
exec('cp '.$filename.' ./last24/');
exec('mv '.$filename.' /data/Incoming/');
?>
