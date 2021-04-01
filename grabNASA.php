#!/usr/bin/php
<?php 

function get_data($url){
 $ch = curl_init();
 $timeout = 5;
 curl_setopt($ch, CURLOPT_URL, $url);
 curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
 curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $timeout);
 curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/5.0 (Windows NT 6.1; rv:19.0) Gecko/20100101 Firefox/19.0");
 $data = curl_exec($ch);
 curl_close($ch);
 return $data;
}

$url="https://geo.nsstc.nasa.gov/SPoRT/outgoing/cbb/alaska_grib/";
$content = get_data($url);
preg_match_all('/<tbody>(.*?)<\/tbody>/m',$content,$tbody, PREG_SET_ORDER,0);
if (!empty($tbody))
 $tbody=$tbody[0][1];

print($tbody);
 

?>




?>
