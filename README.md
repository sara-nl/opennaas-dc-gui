opennaas-dc-gui
===============

Example interface for operating the OpenNaaS REST interface.

This interface is written as an example to demonstrate the capabilities of OpenNaaS to function as a tool for administrating network elements in a datacenter.

Prerequisites
-------------

This applications uses Python and requires a working instance of OpenNaaS 0.28<br>
To download and install OpenNaaS, visit http://opennaas.org/downloads/ <br>
Or alternatively the github repository https://github.com/dana-i2cat/opennaas/ <br>
It can run as a standalone WSGI app.
It requires a number of packages:<br>

<pre>
sudo apt-get install python-paramiko
sudo apt-get install libxml2-dev
sudo apt-get install libxslt1-dev
sudo apt-get install python-pip python-dev build-essential 
sudo apt-get install python-pip
sudo pip install Flask
sudo pip install ncclient==0.3.2
sudo pip install ciscoconfparse
</pre>

Installation
------------

1. Clone the opennaas-dc-gui repository somewhere on your server.
2. adjust the settings.py file to match your environment
3. execute the app using ./opennaas_dc_gui.py

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
