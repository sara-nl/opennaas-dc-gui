<?php

include "settings.php";
include "layout.php";
include "rest_functions.php";



$VLANs = getVLANs();

write_html_head();
write_html_menu();

 ?>

<h1>VLANs</h1>

				<form name='resource_form' action='overview_vlan.php' method='get'>
				<table class="ui-nconf-table ui-nconf-max-width ui-widget ui-widget-content" id="example">
					<thead class="ui-widget-header"><tr>
							<th>Bridge Domain ID</th>
							<th>Vlan Description</th>
							<th>VLAN ID</th>
							<th>Configured on</th>
							<th>L3 network</th>
							<th>Routed by</th>
							<th>action</th>
						</tr>
					</thead>
					<tbody>					
<?php
	$i=0;
   	foreach ($VLANs as $vlan) {
		$color = ($i % 2) + 1;

		print "<tr class='color_list".$color." highlight'>";
		print "<td>".$vlan['domainName']."</td>";
		print "<td>".$vlan['description']."</td>";
		print "<td>".$vlan['vlanid']."</td>";
		print "<td>";
		foreach ($vlan['resources'] as $resource) print $resource." ";
		print "</td>";
		print "<td>"." "."</td>";
		print "<td>"." "."</td>";
		print "<td class='center'><input type='checkbox' name='checkbox_".$vlan['domainName']."'></td></tr>\n";
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
