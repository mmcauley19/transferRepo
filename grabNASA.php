#!/usr/bin/php
<?php 
/*McAuley April 2021. Just a simple script to grab NASA snow sport stuff */

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

preg_match_all('/a href=\"(.*?)\">/',$content,$links,PREG_SET_ORDER,0);
$cmd = "wget ".$url.$links[5][1];
exec($cmd);
//var_dump($links);

exit()
/*
preg_match_all('/<tbody>(.*?)<\/tbody>/ms',$content,$tbody, PREG_SET_ORDER,0);
if (!empty($tbody))
 $tbody=$tbody[0][1];

//var_dump($tbody);


print(gettype($tbody));
$urlList = explode('<tr><td class="n"><a href="',$tbody);
print($urlList[3]);

foreach($urlList as $url){
 $url = 

$i=0;
//preg_match_all('<a href=(.*?)>/m',$tbody,$link,PREG_SET_ORDER,0);
//var_dump($link);
//foreach($tbody as $link){
// preg_match_all('<a href=(.*?)>/m',$link,$linkText,PREG_SET_ORDER,0);
// $i+=1;
 //print($i."\n");
//}


//var_dump($tbody);
 

?>

*/


?>
