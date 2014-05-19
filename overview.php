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
			if ($_GET['action'] == "remove") {
				$xml = curl_DELETE($REST_URL."resources/".$id,"info" );
			}
			
		}
	}
}
	
if (isset($_GET["formAction"])) {
	if ($_GET['formAction'] == 'update') updateResources();
}
	

$resources = getResources();

write_html_head();
write_html_menu();

 ?>

<h1>Resources</h1>

				<form name='resource_form' action='overview.php' method='get'>
				<table class="ui-nconf-table ui-nconf-max-width ui-widget ui-widget-content" id="example">
					<thead class="ui-widget-header"><tr>
							<th>Name</th>
							<th>resource type</th>
							<th>capabilities</th>
							<th>status</th>
							<th>action</th>
						</tr>
					</thead>
					<tbody>					
<?php
	$i=0;

   	foreach ($resources as $resource) {
   		
		$color = ($i % 2) + 1;
		if ($resource['status'] == "ACTIVE") $colorstring = "class='color_list".$color." highlight'";
		if ($resource['status'] == "INITIALIZED") $colorstring = "class='ui-state-error highlight'";
		if ($resource['queue'] == "HTTP_404") print "<tr ".$colorstring." id='".$i."'><td> <b>?</b>";
		else print "<tr ".$colorstring." id='".$i."'>"; 

		if ($resource['queue'] == "HTTP_404") print "<td> <b>?</b>"; 
		else if (strlen($resource['queue'][0]) > 2) print "<td> <img width=30 height=30 src='images/Icon-WIR-9.ashx' alt='".$resource['queue']."'>";
		else print "<td>";
		print "<a href='resource_".$resource['type'].".php?resourcename=".$resource['name']."'>".$resource['name']."</a></td><td>".$resource['type']."</td><td>". $resource['capabilities'] . "</td>";
		print "<td>".$resource['status']."</td>\n" ;
		print "<td class='center'><input type='checkbox' name='checkbox_".$resource['id']."'></td></tr>\n";
		$i = $i + 1;
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
					</select>
					<div style="text-align:right; padding-bottom:1em;">
						<button type="submit">Submit form</button>
					</div>
				</form>
			</div>
	        
<?php
write_html_foot();

?>