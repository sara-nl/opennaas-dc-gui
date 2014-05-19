<?php 

include "settings.php";

function print_rr($content, $return=false) {
    $output = '<div style="border: 1px solid; height: 100px; resize: both; overflow: auto;"><pre>' 
        . print_r($content, true) . '</pre></div>';
 
    if ($return) {
        return $output;
    } else {
        echo $output;
    }
} 

function curl_query($query, $returntype="") {
	
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_URL, $query);
	curl_setopt($ch, CURLOPT_HTTPGET , 1);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

	$output = curl_exec($ch);
	$info = curl_getinfo($ch);
	curl_close($ch); 

	if ($info['http_code'] == '404') return 'HTTP_404';
	if ($returntype == "xml") return simplexml_load_string($output);
	if ($returntype == "info") return $info;
	return $output;
}

function curl_PUT($query, $data, $returntype="") {
	
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "PUT");
	curl_setopt($ch, CURLOPT_POSTFIELDS,"");
	curl_setopt($ch, CURLOPT_URL, $query);


	$output = curl_exec($ch);
	$info = curl_getinfo($ch);
	curl_close($ch);  

	if ($info['http_code'] == '404') return 'HTTP_404';
	if ($returntype == "xml") return simplexml_load_string($output);
	if ($returntype == "info") return $info;
	else return $output;
}

function curl_DELETE($query, $data, $returntype="") {
	
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "DELETE");
	curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/xml'));
	curl_setopt($ch, CURLOPT_POSTFIELDS,"");
	curl_setopt($ch, CURLOPT_URL, $query);


	$output = curl_exec($ch);
	$info = curl_getinfo($ch);
	
	if ($info['http_code'] == '404') return 'HTTP_404';
	if ($returntype == "xml") return simplexml_load_string($output);
	if ($returntype == "info") return $info;
	else return $output;
}

function curl_POST($query, $data, $returntype="") {
	
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
	curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/xml'));
	curl_setopt($ch, CURLOPT_POSTFIELDS,$data);
	curl_setopt($ch, CURLOPT_URL, $query);


	$output = curl_exec($ch);
	$info = curl_getinfo($ch);
	curl_close($ch);  

	if ($info['http_code'] == '404') return 'HTTP_404';
	if ($returntype == "xml") return simplexml_load_string($output);
	if ($returntype == "info") return $info;

	return $output;
}


function listRESTfunctions($resourcename, $capability) {
	global $REST_URL;
	
	$xml = curl_query($REST_URL."router/".$resourcename."/".$capability."?_wadl","xml");
	print_r($xml);
	print $xml->resources->attributes->base;
	return 1;
}

function recursive_array_search($needle,$haystack) {
    foreach($haystack as $key=>$value) {
        $current_key=$key;
        if($needle===$value OR (is_array($value) && recursive_array_search($needle,$value))) {
        	
            return $current_key;
        }
    }
    return false;
}

function getResources() {
	global $REST_URL;
	$capabilities ="";
	$xml = (array)curl_query($REST_URL."resources/","xml");
	
	if (!is_array($xml['resource'])) $xml['resource'] = array($xml['resource']);   // required if there is only one resource, because foreach requires an array
	
	foreach ($xml['resource'] as $resource) {

    	$descriptor_xml = curl_query($REST_URL."resources/".$resource."/descriptor","xml");
    
    	foreach ($descriptor_xml->capabilityDescriptors as $i) 	$capabilities = $capabilities. (string)$i->information->type. " ";
		
		$status = curl_query($REST_URL."resources/".$resource."/status");
    	$queuedata = curl_query($REST_URL.(string)$descriptor_xml->information->type."/".(string)$descriptor_xml->information->name."/queue/getActionsId");
    	$queuestring = str_replace(array('[',']'),'',$queuedata);
		$queue = split(',',$queuestring );
   
		$routers[]= array(	'name' => (string)$descriptor_xml->information->name , 
						    'type' => (string)$descriptor_xml->information->type, 
						    'id' => $resource, 
						    'capabilities' => $capabilities,
						    'status' => $status,
						    'queue' => $queue );
   	}

	return $routers;
}

function getQueue($resourcename) {
	$routers = getResources();
	$queue = " ";
	foreach ($routers as $router) {
		if ($router['name'] == $resourcename) {
			$queue = $router['queue'];
		}
	}
	return $queue;
}

function getResourceStatus($resourcename) {
	$routers = getResources();
	foreach ($routers as $router) {
		if ($router['name'] == $resourcename) {
			$status = $router['status'];
		}
	}
	return $status;
}

function getRouterInterfaces($resourcename) {	 
	global $REST_URL;
	$int_xml = (array) curl_query($REST_URL."router/".$resourcename."/chassis/interfaces","xml");
	
	foreach ($int_xml['interface'] as $i) {  
		$ipAddress="";   
		$ipinfo = (array) curl_query($REST_URL."router/".$resourcename."/ip/interfaces/addresses?interface=".$i,"xml");

		if (isset($ipinfo['ipAddress'])) $ipAddress = $ipinfo['ipAddress'];

		$intinfo_xml = curl_query($REST_URL."router/".$resourcename."/chassis/interfaces/info?interfaceName=".$i,"xml");			
			$interfaces[]= array(	'name' => (string)$intinfo_xml->name , 
						    		'state' => (string)$intinfo_xml->state,
									'description' => (string)$intinfo_xml->description,
									'ip' => $ipAddress); 
	}
	return $interfaces;
}

function GetAggregatedInterfaces($resourcename) {	 
	global $REST_URL;
	$xml = (array) curl_query($REST_URL."router/".$resourcename."/linkaggregation/","xml");
	
	if (!isset($xml['interface'])) return array();
	else return (array)$xml['interface'];
}

function GetAggregatedInterface($resourcename, $interfacename) {	 
	global $REST_URL;
	$xml = (array) curl_query($REST_URL."router/".$resourcename."/linkaggregation/".$interfacename,"xml");
	foreach ($xml['interfaces'] as $if) {
		$interfaces[]= (string)$if;
	}
	$aggr = array(	'id' => $xml['id'],
					'interfaces' => $interfaces,
					'link-speed' => "1g",			// FAKED!!!
					'minimumIf' => "1", 			// FAKED!!!
					'protocol' => (string)$xml['aggregationOptions']->entry->key,
					'mode' => (string)$xml['aggregationOptions']->entry->value
					);			    	
	return $aggr;
}


function getVLANs() {
	global $REST_URL;

	$routers = getResources();
	foreach ($routers as $router) {
		
		$xml = (array)curl_query($REST_URL."router/".$router['name']."/vlanbridge/","xml");
		
		foreach ($xml['domainName'] as $domain) {
			$domainxml = (array)curl_query($REST_URL."router/".$router['name']."/vlanbridge/".$domain,"xml");
			
			if (strlen(recursive_array_search($domain,$domains)) === 0) { 
				
				$domains[$domain] = array( 'domainName' => $domainxml['domainName'],
									   'vlanid' => $domainxml['vlanid'],
									   'description' => $domainxml['description'],
									   'resources' => (array)$router['name']);
			}
			else $domains[$domain]['resources'][] = $router['name'];

		}

	}
	
	//	print_rr($domains);
	/*foreach ($xml['resource'] as $resource) {

    	$descriptor_xml = curl_query($REST_URL."resources/".$resource."/descriptor","xml");
	global $REST_URL;
	$capabilities ="";
	$xml = (array)curl_query($REST_URL."vlanbridge/","xml");
	print_r($xml);*/
	/*foreach ($xml['resource'] as $resource) {

    	$descriptor_xml = curl_query($REST_URL."resources/".$resource."/descriptor","xml");
    
    	foreach ($descriptor_xml->capabilityDescriptors as $i) 	$capabilities = $capabilities. (string)$i->information->type. " ";
		
		$status = curl_query($REST_URL."resources/".$resource."/status");
    	$queuedata = curl_query($REST_URL.(string)$descriptor_xml->information->type."/".(string)$descriptor_xml->information->name."/queue/getActionsId");
    	$queuestring = str_replace(array('[',']'),'',$queuedata);
		$queue = split(',',$queuestring );
   
		$routers[]= array(	'name' => (string)$descriptor_xml->information->name , 
						    'type' => (string)$descriptor_xml->information->type, 
						    'id' => $resource, 
						    'capabilities' => $capabilities,
						    'status' => $status,
						    'queue' => $queue );
   	}*/

	return $domains;
}

function getProtocolContext($resourcename) {
	global $REST_URL;
	
	$context = curl_query($REST_URL."router/".$resourcename."/protocolSessionManager/context/","xml");
 
	return $context;
}


?>