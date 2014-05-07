opennaas-dc-gui
===============

Example interface for operating the OpenNaaS REST interface.

This interface is written as an example to demonstrate the capabilities of OpenNaaS to function as a tool for administrating network elements in a datacenter.

Prerequisites
-------------

This applications uses PHP and requires a working instance of OpenNaaS 0.28<br>
To download and install OpenNaaS, visit http://opennaas.org/downloads/ <br>
Or alternatively the github repository https://github.com/dana-i2cat/opennaas/ <br>

Installation
------------

1. Install the opennaas-dc-gui repository in your webservers document root.
2. adjust the settings.php file to have the $REST_URL and $BASE_URL reflect the location of your web and/or OpenNaaS servers.

Current functionality
---------------------

Overview page:
- Provides overview of all resources
- starting and stopping single / group of resources 
- Remove single / group of resources (works, but does not correctly show resources afterwards)

Overview VLAN page:
- List all VLANs found in all resources, list on which resources the vlans are configured

Queue overview:
- List all queue items of all resources

Resource Chassis page:
- Provides overview of all interfaces of a resource
- Add / Change interface description
- Add / Change interface IPv4 address
- Add / Change interface IPv6 address
- Bring interface / group of interfaces up / down (not working at the moment)
- Review Aggregated links information

Resource Queue page:
- lists all individual queue actions of a resource
- remove single / group of queue actions
- Clear /execute queue 

Resource info page:
- List Resource protocol context information

Note: Currently only Juniper EX and M series routers are supported using the router resource.
