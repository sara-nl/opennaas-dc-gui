<?php
include "settings.php";
include "rest_functions.php";
include "layout.php";

if (isset($argv)) {
    $resourcename = $argv[1];   
}
else {
	$resourcename = $_GET['resourcename'];
}

function updateInterfaces() {
		
	global $REST_URL;
	
	foreach (array_keys($_GET) as $get) {
		if (strpos($get,"checkbox_") !== FALSE) {
			$tempname = str_replace("checkbox_", "", $get);
			$name = str_replace("_", ".", $tempname);
			$name = "ge-0/0/10.0";
			if ($_GET['action'] == "up") {
				$if = substr($name, 0, -2); 
				
				$xml = curl_PUT($REST_URL."router/".$_GET['resourcename']."/chassis/interfaces/status/up?ifaceName=".$if,"xml" );
			}
			if ($_GET['action'] == "down") {
				$if = substr($name, 0, -2); 
				
				$xml = curl_PUT($REST_URL."router/".$_GET['resourcename']."/chassis/interfaces/status/down?ifaceName=".$if,"xml" );
			}
		}
	}
	
	if ($_GET['action'] == "queueexecute") {
		$xml = curl_POST($REST_URL."router/".$_GET['resourcename']."/queue/execute","" );
	}
}
	
if ($_GET['formAction'] == 'update') updateInterfaces();

$interfaces = getRouterInterfaces($resourcename);
$aggregates = GetAggregatedInterfaces($resourcename);

write_html_head();
write_html_menu();
write_resource_menu($_GET['resourcename'], 0);

?>
		
				<form name='router_resource_form' action='resource_router.php' method='get'>
				<table class="ui-nconf-table ui-nconf-max-width ui-widget ui-widget-content" id="example">
					<thead class="ui-widget-header"><tr>
				
						<tr>
							<th>Interface name</th>
							<th>Interface description</th>
							<th>IPv4</th>
							<th>IPv6</th>
							<th>Status</th>
							<th>Action</th>
						</tr>
					</thead>
					<tbody>
					
<?	
	$i=0;
	//print_r($interfaces);
   	foreach ($interfaces as $interface) {
   		$isAggr = FALSE;
   		// Interface name
   		
   		foreach ($aggregates as $aggr) {
   			if (strpos($interface['name'] , $aggr) !== FALSE) $isAggr = TRUE;
   			$modifyValue = $aggr;
   		}
		if ($isAggr == TRUE) {
		?>
		<tr><td><b><a href='#' onClick="MyWindow=window.open('modify_popup.php?modifyAction=aggregate&resourceName=<?=$resourcename?>&interface=<?=$modifyValue?>&modifyValue=<?=$interface['name']?>','MyWindow','toolbar=no,location=no,directories=no,status=no, menubar=no,scrollbars=no,resizable=no,width=600,height=300'); return false;"><?=$interface['name']?></a></b></td>
		<?
		} else print "<tr><td>".$interface['name']."</td>";
		
		// Interface description
		if  (strlen($interface['description']) == 0) {
		?>
		<td align='left'><a href='#' onClick="MyWindow=window.open('modify_popup.php?modifyAction=description&resourceName=<?=$resourcename?>&interface=<?=$interface['name']?>&modifyValue=<?=$interface['description']?>','MyWindow','toolbar=no,location=no,directories=no,status=no, menubar=no,scrollbars=no,resizable=no,width=600,height=300'); return false;">...</a></td>
		<? }
		else {
		?>
	    <td><a href='#' onClick="MyWindow=window.open('modify_popup.php?modifyAction=description&resourceName=<?=$resourcename?>&interface=<?=$interface['name']?>&modifyValue=<?=$interface['description']?>','MyWindow','toolbar=no,location=no,directories=no,status=no, menubar=no,scrollbars=no,resizable=no,width=600,height=300'); return false;"><?=$interface['description']?></a></td>
		<? }


		// IPv4
		$ipv4count = 0;
		foreach ((array)$interface['ip'] as $ip) {
			if (stripos($ip, ".")) {
				$ipv4count = $ipv4count + 1;

				?>
				<td><a href='#' onClick="MyWindow=window.open('modify_popup.php?modifyAction=IPv4Address&resourceName=<?=$resourcename?>&interface=<?=$interface['name']?>&modifyValue=<?=$ip?>','MyWindow','toolbar=no,location=no,directories=no,status=no, menubar=no,scrollbars=no,resizable=no,width=600,height=300'); return false;"><?=$ip?></a></td>
				<?
			}
		}
		if ($ipv4count == 0) {
			?>
			<td align='left'><a href='#' onClick="MyWindow=window.open('modify_popup.php?modifyAction=IPv4Address&resourceName=<?=$resourcename?>&interface=<?=$interface['name']?>&modifyValue=<?=$ip?>','MyWindow','toolbar=no,location=no,directories=no,status=no, menubar=no,scrollbars=no,resizable=no,width=600,height=300'); return false;">...</a></td>
			<?
		}
		
		// IPv6
		$ipv6count = 0;
		foreach ((array)$interface['ip'] as $ip) {
			if (stripos($ip, ":")) {
				$ipv6count = $ipv6count + 1;
				?>
				<td><a href='#' onClick="MyWindow=window.open('modify_popup.php?modifyAction=IPv6Address&resourceName=<?=$resourcename?>&interface=<?=$interface['name']?>&modifyValue=<?=$ip?>','MyWindow','toolbar=no,location=no,directories=no,status=no, menubar=no,scrollbars=no,resizable=no,width=600,height=300'); return false;"><?=$ip?></a></td>
				<?
			}
		}
		if ($ipv6count == 0) {
			?>
			<td align='left'><a href='#' onClick="MyWindow=window.open('modify_popup.php?modifyAction=IPv6Address&resourceName=<?=$resourcename?>&interface=<?=$interface['name']?>&modifyValue=<?=$ip?>','MyWindow','toolbar=no,location=no,directories=no,status=no, menubar=no,scrollbars=no,resizable=no,width=600,height=300'); return false;">...</a></td>
			<?
		}	

		// Status
		print "<td class='center'>".$interface['state']."</td>";

		// Action
		print "<td class='center'><input type='checkbox' name='checkbox_".urlencode($interface['name'])."'></td></tr>\n";
		$i = $i+ 1;
	}
	?>		
			</tbody>		
			</table>
			<input type=hidden name='formAction' value='update'>
			<input type=hidden name='resourcename' value='<?=$resourcename?>'>
			<select name='action'>
						<option value="">-- Choose Action --</option>
					  	<option value="up">Bring interface up</option>
					  	<option value="down">Bring interface down</option>
					  	<option value="queueexecute">Execute queue for <?=$resourcename?></option>
					</select>
			<div style="text-align:right; padding-bottom:1em;">
						<button type="submit">Submit form</button>
					</div>
			</form>
		</div>
	</div>
<?
write_html_foot();    
?>
