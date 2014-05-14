<?php
require_once "settings.php";

function write_html_head() {
	global $jQuery_URL1, $jQuery_URL2,  $jQuery_URL3, $page_CSS_URL, $table_CSS_URL, $BASE_URL;
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
	<head>
		<meta http-equiv="content-type" content="text/html; charset=utf-8" />
		<link rel="shortcut icon" type="image/ico" href="https://www.surfsara.nl/sites/all/themes/st_sara/favicon.ico" />
		
		<title>SURFsara OpenNaaS GUI</title>
		
		<link rel="stylesheet" type="text/css" href="css/main.css">
		<link rel="stylesheet" type="text/css" href="css/new.css">
		<link rel="stylesheet" type="text/css" href="css/jquery-ui.custom.css">
		<link rel="stylesheet" type="text/css" href="css/jquery.table.css">
		<link rel="stylesheet" type="text/css" href="css/nconf-widget.css">

		<script type="text/javascript" language="javascript" src="<?=$jQuery_URL1?>"></script>
		<script type="text/javascript" language="javascript" src="<?=$jQuery_URL2?>"></script>
		<script type="text/javascript" language="javascript" src="<?=$jQuery_URL3?>"></script>

      <script src="js/jquery.nconf_ajax_debug.js" type="text/javascript"></script>
      <script src="js/jquery.nconf_help_admin.js" type="text/javascript"></script>
      <script src="js/jquery.nconf_tooltip.js" type="text/javascript"></script>
      <script src="js/jquery.nconf_accordion_list.js" type="text/javascript"></script>
      <script src="js/jquery.nconf_head.js" type="text/javascript"></script>

		<script type="text/javascript" charset="utf-8">
		var oTable;
		 
		$(document).ready(function() {
		   
		     
		    oTable = $('#example').dataTable( {
                "iDisplayLength": 25
               } );


		} );
		</script>
	</head>
<body>
    <div id="switcher" style="position: absolute; right: 0"></div>
<div id="title">
    <center>
        <div id="logo"></div>
    </center>
</div>
<div id="titlesub">
    <center>
        <div>
            <table>
                <tr>
                                  </tr>
            </table>
        </div>
    </center>
</div>
<div id="mainwindow">
<?php
}

function write_html_menu() {
?>

<div id="navigation">
 <div class="left_navigation">
  <div class="ui-widget">
    <h2 class="ui-widget-header header"><span><a href="index.php" >Home</a></span></h2>
 <h2 class="ui-widget-header header"><span>Basic Items</span></h2>
    <div class="ui-widget-content box_content"><table border=0 width=188>
    	<div class="link_with_tag"><a href="overview.php" >Show Resources</a></div>
    	<div class="link_with_tag"><a href="resource_queue.php?resourcename=_all" >Show Queue</a></div>
        <div class="link_with_tag"><a href="overview_vlan.php" >Show VLANs</a></div>
    	</table></div>

    <h2 class="ui-widget-header header"><span>Additional Items</span></h2>
    <div class="ui-widget-content box_content">
                
</div>
    
   </div> <!-- END OF DIV "accordion" -->
 </div>     <!-- END OF DIV "left_navigation" -->
</div>         <!-- END OF DIV "navigation" -->

<div id="mainspace" style="float: left; width: 22px; height: 100px"> </div>
<div id="maincontent">

<?php
}

function write_html_foot() {
?>
	</body>
</html>
<?php
}


function write_resource_menu($resourcename, $active) {
	
	if ($active == 0) print "<b>Chassis</b> |";
	else   print "<a href='resource_router.php?resourcename=".$resourcename."'>Chassis</a> | ";
	if ($active == 1) print "<b>Queue</b> |";
	else print "<a href='resource_queue.php?resourcename=".$resourcename."'>Queue</a> |";
 	if ($active == 2) print "<b>VLANs</b> |";
	else print "<a href='resource_vlanbridge.php?resourcename=".$resourcename."'>VLANs</a> |";
	if ($active == 3) print "<b>Resource Info</b>\n";
	else print "<a href='resource_info.php?resourcename=".$resourcename."'>Resource Info</a>";
	print "<h1>".$resourcename;
	$queue = getQueue($resourcename);
	if (strlen($queue[0]) > 2) print " -- ". count($queue)." Actions Queued --";
	print "</h1>\n";
}
?>