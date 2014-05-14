<?php

include "settings.php";
include "layout.php";
include "rest_functions.php";

write_html_head();
write_html_menu();
write_resource_menu($_GET['resourcename'], 3);

$context = getProtocolContext($_GET['resourcename']);

print "<br>";



	print "<table>\n";
	print "<th>Protocol Context</th>\n";
	print "<tr><td>authentication type</td><td>". $context->protocolSessionContext->sessionParameters->entry[0]->value . "</td></tr>\n"; 
	print "<tr><td>protocol</td><td>". $context->protocolSessionContext->sessionParameters->entry[1]->value . "</td></tr>\n"; 
	print "<tr><td>username</td><td>". $context->protocolSessionContext->sessionParameters->entry[3]->value . "</td></tr>\n"; 
	print "<tr><td>password</td><td>". $context->protocolSessionContext->sessionParameters->entry[2]->value . "</td></tr>\n"; 
	print "<tr><td>context uri</td><td>". $context->protocolSessionContext->sessionParameters->entry[4]->value . "</td></tr>\n"; 
	print "</table>";


write_html_foot(); 

?>
      