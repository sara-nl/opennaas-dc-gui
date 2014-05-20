<?php

include "settings.php";
include "layout.php";
include "rest_functions.php";


if (isset($_GET["modifyAction"])) $modifyAction = $_GET['modifyAction'];
else $modifyAction = "";
if (isset($_GET["modifyValue"])) 	$modifyValue = $_GET['modifyValue'];
else $modifyValue = "";
if (isset($_GET["newModifyValue"])) $newModifyValue = $_GET['newModifyValue'];
else $newModifyValue = "";
if (isset($_GET["resourceName"])) $resourceName = $_GET['resourceName'];
else $resourceName = "";
if (isset($_GET["interface"])) $interface = $_GET['interface'];
else $interface = "";
if (isset($_GET["formAction"])) $formAction = $_GET['formAction'];
else $formAction = "";
if ($formAction == 'update') updateResources();
if ($formAction == 'modify') modify($_GET);


function modify($GET) {
	global $REST_URL;
	if ($GET['modifyAction'] == "IPv4Address") {
		$xml = curl_POST($REST_URL."router/".$GET['resourceName']."/ip/interfaces/addresses/ipv4?interface=".$_GET['interface'],$GET['newModifyValue'] );
	}
	else if ($_GET['modifyAction'] == "IPv6Address") {
		$xml = curl_POST($REST_URL."router/".$GET['resourceName']."/ip/interfaces/addresses/ipv6?interface=".$_GET['interface'],$GET['newModifyValue'] );
	}
	else if ($_GET['modifyAction'] == "description") {
		$xml = curl_POST($REST_URL."router/".$GET['resourceName']."/ip/interfaces/description?interface=".$_GET['interface'],$GET['newModifyValue'] );
	}

    // close pop up window and reload main page
    ?>
    <html>
        <head>
            <script type="text/javascript" charset="utf-8">
                window.opener.location.reload();
                self.close();
            </script>
        </head>
        <body>
        </body>
    </html>
    <?php
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
			
			<title><?php echo $actionstring?> <?php echo $modifyAction?></title>
			<style type="text/css" title="currentStyle">
				@import "<?php echo $page_CSS_URL?>";
				@import "<?php echo $table_CSS_URL?>";
			</style>
		</head>
	<?php
	if ($modifyAction == "IPv4Address" | $modifyAction == "IPv6Address" | $modifyAction == "description" ) {
		?>
		<body id="dt_example">
			<form name='modify_form' action='modify_popup.php' method='get'>
				<h1><?php echo $actionstring?> <?php echo $modifyAction?></h1>
				<table>
					<tr><td>Current value:</td><td><?php echo $modifyValue?></td></tr>
					<tr><td>New value:</td><td><input type='text' width='100' name='newModifyValue'></td></tr>
				</table>
				<input type='hidden' name='formAction' value='modify'>
				<input type='hidden' name='modifyAction' value='<?php echo $modifyAction?>'>
				<input type='hidden' name='resourceName' value='<?php echo $resourceName?>'>
				<input type='hidden' name='interface' value='<?php echo $interface?>'>
				<input type='submit' value='Go'>

			</form>
		</body>
		<?php
	}
	if ($modifyAction == "aggregate" ) {
		$aggr = GetAggregatedInterface($resourceName, $interface);
		
		?>
		<body id="dt_example">
			<form name='modify_form' action='modify_popup.php' method='get'>
				<h1><?php echo $actionstring?> <?php echo $modifyAction?></h1>
				<table>
					<tr><td>Link ID:</td><td><?php echo $aggr['id']?></td></tr>
					<tr><td>Interfaces:</td><td><? print implode("<br>", $aggr['interfaces']); ?> </td></tr>
					<tr><td>link-speed:</td><td><?php echo $aggr['link-speed']?> </td></tr>
					<tr><td>Minimum interfaces:</td><td><?php echo $aggr['minimumIf']?></td></tr>
					<tr><td>Protocol:</td><td><?php echo $aggr['protocol']?> </td></tr>
					<tr><td>Mode:</td><td><?php echo $aggr['mode']?> </td></tr>
				</table>
				<input type='hidden' name='formAction' value='modify'>
				<input type='hidden' name='modifyAction' value='<?php echo $modifyAction?>'>
				<input type='hidden' name='resourceName' value='<?php echo $resourceName?>'>
				<input type='hidden' name='interface' value='<?php echo $interface?>'>
				<input type='submit' value='Go'>

			</form>
		</body>
		<?php
		}
		?>


	</html>

