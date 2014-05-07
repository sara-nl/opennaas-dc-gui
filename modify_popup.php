<?php

include "settings.php";
include "layout.php";
include "rest_functions.php";

$modifyAction = $_GET['modifyAction'];
$modifyValue = $_GET['modifyValue'];
$newModifyValue = $_GET['newModifyValue'];
$resourceName = $_GET['resourceName'];
$interface = $_GET['interface'];

if ($_GET['formAction'] == 'modify') { 
	modify($_GET);
}


function modify($GET) {
	global $REST_URL;
	if ($GET['modifyAction'] == "IPv4Address") {
		$xml = curl_POST($REST_URL."router/".$GET['resourceName']."/ip/interfaces/addresses/ipv4?interface=".$_GET['interface'],$GET['newModifyValue'] );
	}
	if ($_GET['modifyAction'] == "IPv6Address") {
		$xml = curl_POST($REST_URL."router/".$GET['resourceName']."/ip/interfaces/addresses/ipv6?interface=".$_GET['interface'],$GET['newModifyValue'] );
	}
	if ($_GET['modifyAction'] == "description") {
		$xml = curl_POST($REST_URL."router/".$GET['resourceName']."/ip/interfaces/description?interface=".$_GET['interface'],$GET['newModifyValue'] );
	}
	//closeCurrentWindow();

	
}



	global $page_CSS_URL, $table_CSS_URL;
	if (strlen($modifyValue) === 0) $actionstring = "Add";
	else $actionstring = "Modify";

	?>
	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
	<html>
		<head>
			<meta http-equiv="content-type" content="text/html; charset=utf-8" />
			<link rel="shortcut icon" type="image/ico" href="https://www.surfsara.nl/sites/all/themes/st_sara/favicon.ico" />
			
			<title><?=$actionstring?> <?=$modifyAction?></title>
			<style type="text/css" title="currentStyle">
				@import "<?=$page_CSS_URL?>";
				@import "<?=$table_CSS_URL?>";
			</style>
		</head>
	<?
	if ($modifyAction == "IPv4Address" | $modifyAction == "IPv6Address" | $modifyAction == "description" ) {
		?>
		<body id="dt_example">
			<form name='modify_form' action='modify_popup.php' onSubmit='self.close(); window.opener.location.reload();' method='get'>
				<h1><?=$actionstring?> <?=$modifyAction?></h1>
				<table>
					<tr><td>Current value:</td><td><?=$modifyValue?></td></tr>
					<tr><td>New value:</td><td><input type='text' width='100' name='newModifyValue'></td></tr>
				</table>
				<input type='hidden' name='formAction' value='modify'>
				<input type='hidden' name='modifyAction' value='<?=$modifyAction?>'>
				<input type='hidden' name='resourceName' value='<?=$resourceName?>'>
				<input type='hidden' name='interface' value='<?=$interface?>'>
				<input type='submit' value='Go'>

			</form>
		</body>
		<?
	}
	if ($modifyAction == "aggregate" ) {
		$aggr = GetAggregatedInterface($resourceName, $interface);
		
		?>
		<body id="dt_example">
			<form name='modify_form' action='modify_popup.php' onSubmit='self.close(); window.opener.location.reload();' method='get'>
				<h1><?=$actionstring?> <?=$modifyAction?></h1>
				<table>
					<tr><td>Link ID:</td><td><?=$aggr['id']?></td></tr>
					<tr><td>Interfaces:</td><td><? print implode("<br>", $aggr['interfaces']); ?> </td></tr>
					<tr><td>link-speed:</td><td><?=$aggr['link-speed']?> </td></tr>
					<tr><td>Minimum interfaces:</td><td><?=$aggr['minimumIf']?></td></tr>
					<tr><td>Protocol:</td><td><?=$aggr['protocol']?> </td></tr>
					<tr><td>Mode:</td><td><?=$aggr['mode']?> </td></tr>
				</table>
				<input type='hidden' name='formAction' value='modify'>
				<input type='hidden' name='modifyAction' value='<?=$modifyAction?>'>
				<input type='hidden' name='resourceName' value='<?=$resourceName?>'>
				<input type='hidden' name='interface' value='<?=$interface?>'>
				<input type='submit' value='Go'>

			</form>
		</body>
		<?	
		}
		?>


	</html>

