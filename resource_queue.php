<?php

include "settings.php";
include "layout.php";
include "rest_functions.php";


function updateResources() {
	global $REST_URL;
	$resources = getResources();

	foreach (array_keys($_GET) as $get) {
		if (strpos($get,"checkbox_") !== FALSE) {
			$id = str_replace("checkbox_", "", $get);
			$index = recursive_array_search($id);
			$type = $resources[$index]['type'];
			$name = $resources[$index]['name'];
			
			if ($_GET['action'] == "stop") {
				$xml = curl_PUT($REST_URL."resources/".$id."/status/stop","" );
			}
			if ($_GET['action'] == "forcestop") {
				$xml = curl_PUT($REST_URL."resources/".$id."/status/forceStop","" );
			}
			if ($_GET['action'] == "start") {
				$xml = curl_PUT($REST_URL."resources/".$id."/status/start","" );
			}
			if ($_GET['action'] == "queueexecute") {
				$xml = curl_POST($REST_URL.$type."/".$name."/queue/execute","" );
			}
			if ($_GET['action'] == "queueclear") {
				$xml = curl_POST($REST_URL.$type."/".$name."/queue/clear","" );
			}
			print $xml;
			
		}
	}
}
	
if ($_GET['formAction'] == 'update') updateResources();
	


if ($_GET['resourcename'] == "_all") {
	$routers = getResources();
}
else {
	$queue = getQueue($_GET['resourcename']);
}

write_html_head();
write_html_menu();
write_resource_menu($_GET['resourcename'], 1);
print "queue:" ; print_r($queue);
 ?>
		<div id="container">
			<div id="demo">
				<form name='resource_form' action='overview.php' method='get'>
				<table class="ui-nconf-table ui-nconf-max-width ui-widget ui-widget-content" id="example">
					<thead class="ui-widget-header"><tr>
						<tr>
							<th>Resource</th>
							<th>Queue ID</th>
							<th>Entry description</th>
							<th>Action</th>
						</tr>
					</thead>
					<tbody>					
<?	
	foreach ($routers as $router) {

	   	foreach ($router['queue'] as $key => $value) {
	   		if ($_GET['resourcename'] == "_all" & strlen($value) > 0) {
				print "<tr id='".$value."'>";
				print "<td>".$router['name']."</td>";
				print "<td>".$key."</td>";
				print "<td>".$value."</td>";
				print "<td class='center'><input type='checkbox' name='checkbox_".$router['id']."_".$value."'></td></tr>\n";
			}

		}
	}
?>		
					</tbody>		
					</table>
					<input type=hidden name=formAction value='update'>
					<select name='action'>
						<option value="">-- Choose Action --</option>
					  	<option value="start">start</option>
					  	<option value="stop">stop</option>
					  	<option value="forcestop">force stop</option>
					  	<option value="remove">remove</option>
					  	<option value="queueexecute">Execute queue</option>
					  	<option value="queueclear">Clear queue</option>
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
