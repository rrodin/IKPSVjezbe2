<?php
require_once "nusoap.php";

function checkService($name){
	return "Hello ".$name.", your service is working fine!";
}

$server = new soap_server();
$server->configureWSDL("status", "urn:status");

$server->register("checkService",
    array("name" => "xsd:string"),
    array("return" => "xsd:string"),
    "urn:status",
    "urn:status#checkService",
    "rpc",
    "encoded",
    "Check if service is working by passing your name");

$server->service($HTTP_RAW_POST_DATA);
?>