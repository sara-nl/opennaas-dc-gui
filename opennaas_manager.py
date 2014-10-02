#!/usr/bin/python

# Copyright (c) 2014, Erik Ruiter, SURFsara BV, Amsterdam, The Netherlands
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions
# and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
# and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

import requests
from collections import defaultdict
import xml.etree.ElementTree as ET
import json, urllib, re
import settings

def etree_to_dict(t):
	"""Function which converts a ElementTree XML object to a python Dictionary."""

	d = {t.tag: {} if t.attrib else None}
	children = list(t)
	if children:
		dd = defaultdict(list)
		for dc in map(etree_to_dict, children):
			for k, v in dc.iteritems():
				dd[k].append(v)
		d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
	if t.attrib:
		d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())
	if t.text:
		text = t.text.strip()
		if children or t.attrib:
			if text:
				d[t.tag]['#text'] = text
		else:
			d[t.tag] = text
	return d

def getResourceName(resource_id, url, opennaas_user, opennaas_pwd):
	r = requests.get("%sresources/%s/name" % (url, resource_id), auth=(opennaas_user, opennaas_pwd))
	return r.text

def getResourceID(resource_name, url, opennaas_user, opennaas_pwd):
	r = requests.get("%sresources/type/router/name/%s" % (url, resource_name), auth=(opennaas_user, opennaas_pwd))
	return r.text

def getQueue(resource_name, url, opennaas_user, opennaas_pwd):
	r = requests.get("%srouter/%s/queue/getActionsId" % (url, resource_name), auth=(opennaas_user, opennaas_pwd))
	queue = r.text[1:-1].replace(" ","").split(",")
	return json.dumps(queue)

def executeQueue(resources, url, opennaas_user, opennaas_pwd):
	if isinstance(resources, list):
		for resource in resources:
			r = requests.post("%srouter/%s/queue/execute" % (url, resource), auth=(opennaas_user, opennaas_pwd))
	else:
		r = requests.post("%srouter/%s/queue/execute" % (url, resources), auth=(opennaas_user, opennaas_pwd))
	return json.dumps(r.text)

def clearQueue(resources, url, opennaas_user, opennaas_pwd):
	if isinstance(resources, list):
		for resource in resources:
			r = requests.post("%srouter/%s/queue/clear" % (url, resource), auth=(opennaas_user, opennaas_pwd))
	else:
		r = requests.post("%srouter/%s/queue/clear" % (url, resources), auth=(opennaas_user, opennaas_pwd))	
	return json.dumps(r.text)

def getContext(resource_name, url, opennaas_user, opennaas_pwd):
	context = dict()
	r = requests.get("%srouter/%s/protocolSessionManager/context" % (url, resource_name), auth=(opennaas_user, opennaas_pwd))
	data =  etree_to_dict( ET.fromstring(r.text) )	
	data = data['protocolSessionContexts']['protocolSessionContext']['sessionParameters']['entry']			
	for i in data:
		context.update( {i.get('key'): i.get('value').get('#text') })
	return json.dumps(context)

def removeQueueItems(resource_name, resources, url,opennaas_user,opennaas_pwd):
	"""
	<?xml version="1.0" encoding="UTF-8"?>
	<modifyParams>
    	<posAction>0</posAction>
    	<queueOper>REMOVE</queueOper>
	</modifyParams>
	"""
	return "ok"

def getResource(resource_id, url, opennaas_user, opennaas_pwd):
	if re.match('[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}',resource_id) == None:
		resource_id =  getResourceID(resource_id, url, opennaas_user, opennaas_pwd)
	
	r = requests.get("%sresources/%s" % (url, resource_id), auth=(opennaas_user, opennaas_pwd))
	data =  etree_to_dict( ET.fromstring(r.text) )				
			
	queue = getQueue(data['resourceInfo'].get('name'), url, opennaas_user, opennaas_pwd)
	data['resourceInfo'].update({'queue' : json.loads(queue)})
	
	return json.dumps(data['resourceInfo'])

def getResources(url, opennaas_user, opennaas_pwd):
	resources = list()
	
	r = requests.get(url + "resources/", auth=(opennaas_user, opennaas_pwd))
	data =  etree_to_dict( ET.fromstring(r.text) )	
	for i in data['resources']['resource']:
		resources.append(json.loads(getResource(i, url, opennaas_user, opennaas_pwd)))
	return json.dumps(resources)

def updateResources(action, resources, url,opennaas_user,opennaas_pwd):
	for resource in resources:
		print "the resource:" + resource
		r = requests.put("%sresources/%s/status/%s" % ( url, resource, action), auth=(opennaas_user, opennaas_pwd))
		print r.text

def getResourceStatus(resourcename, url, opennaas_user, opennaas_pwd):
	id = getResourceID(resourcename , url, opennaas_user, opennaas_pwd)
	r = requests.get("%sresources/%s/status" % (url, id), auth=(opennaas_user, opennaas_pwd))
	return r.text

def getRouterInterfaces(resourcename, url , opennaas_user, opennaas_pwd):
	interfaces = list()

	r = requests.get("%srouter/%s/chassis/interfaces" % (url, resourcename), auth=(opennaas_user, opennaas_pwd))
	data = etree_to_dict( ET.fromstring(r.text) )	
	data = data['{opennaas.api}interfaces']['interface']
	
	for i in data:
		ri = requests.get("%srouter/%s/chassis/interfaces/info?interfaceName=%s" % (url, resourcename, i), auth=(opennaas_user, opennaas_pwd))
		ifInfo = etree_to_dict( ET.fromstring(ri.text) )	
		ifInfo = ifInfo['{opennaas.api}interfaceInfo']
		
		rip = requests.get("%srouter/%s/ip/interfaces/addresses?interface=%s" % (url, resourcename, i), auth=(opennaas_user, opennaas_pwd))
		ipInfo = etree_to_dict( ET.fromstring(rip.text) )
		if ipInfo['{opennaas.api}ipAddresses'] != None : ifInfo.update( ipInfo['{opennaas.api}ipAddresses'] )
		else: ifInfo.update( {'ipAddress' : ""} )
		
		if (ifInfo.get('description') == None): ifInfo['description'] = ''
		
		interfaces.append(ifInfo)

	return json.dumps(interfaces)

def getRouterAggregates(resourcename, url , opennaas_user, opennaas_pwd):
	r = requests.get("%srouter/%s/linkaggregation/" % (url, resourcename), auth=(opennaas_user, opennaas_pwd))
	tree = ET.fromstring(r.text)
	data = etree_to_dict(tree)

	return json.dumps(data)

def getRouterVLANs(resourcename, url , opennaas_user, opennaas_pwd):
	interfaces = defaultdict(dict)
	vlanBridges = defaultdict(dict)
	vlaninterfaces = []
	
	# Build dictionary of all vlans with their attached interfaces
	r = requests.get("%srouter/%s/vlanbridge" % (url, resourcename), auth=(opennaas_user, opennaas_pwd))
	vlans = etree_to_dict( ET.fromstring(r.text) )
	vlans = vlans['{opennaas.api}bridgeDomains']['domainName']
	for i in vlans :
		rv = requests.get("%srouter/%s/vlanbridge/%s" % (url, resourcename, i), auth=(opennaas_user, opennaas_pwd))
		vlanDetails = etree_to_dict( ET.fromstring(rv.text) )
		vlanBridges.update({ i : vlanDetails['{opennaas.api}bridgeDomain']})

	r = requests.get("%srouter/%s/chassis/interfaces" % (url, resourcename), auth=(opennaas_user, opennaas_pwd))
	ifdata = etree_to_dict( ET.fromstring(r.text) )
	ifdata = ifdata['{opennaas.api}interfaces']['interface']
	for i in ifdata:
		print i
		rv = requests.get("%srouter/%s/vlanbridge/vlanoptions?iface=%s" % (url, resourcename, i), auth=(opennaas_user, opennaas_pwd))
		vlanOptions = etree_to_dict( ET.fromstring(rv.text) )
		print vlanOptions
		"""rv_tree = ET.fromstring(rv.text)
		for rv_elem in rv_tree.iter():
			print rv_elem.text
			if rv_elem.text == "native-vlan-id":
				print "bla"
		index = index + 1
		"""

def getNetworkOverview(url , opennaas_user, opennaas_pwd):
	domains = defaultdict();
	routers = json.loads(getResources(url, opennaas_user, opennaas_pwd))

	for router in routers:
		if router['type'] == 'router':
			print "%srouter/%s/vlanbridge" % (url, router['name'])
			r = requests.get("%srouter/%s/vlanbridge" % (url, router['name']), auth=(opennaas_user, opennaas_pwd))
			vlans = etree_to_dict( ET.fromstring(r.text) )
			#print vlans
			vlans = vlans['{opennaas.api}bridgeDomains']['domainName']
			
			for vlan in vlans:
				print "%srouter/%s/vlanbridge/%s" % (url, router['name'],vlan)
				r = requests.get("%srouter/%s/vlanbridge/%s" % (url, router['name'],vlan), auth=(opennaas_user, opennaas_pwd))
				domain = etree_to_dict( ET.fromstring(r.text) )
				print domain
				domain = domain['{opennaas.api}bridgeDomain']
				domain.update( { 'resources' : [router['name']]})

				if vlan not in domains.keys():
					domains.update( { vlan : domain })
				else:
					resources = domains[vlan]['resources']
					resources.append(router['name'])
					domains[vlan].update({ 'resources' : resources })
		
	return json.dumps(domains)

def getTopology(resourcename , url, topo_auth_string):
	r = requests.get("%snetwork/%s/topology" % (url, resourcename), headers = {'Accept' : 'application/xml', 'Authorization' : 'Basic ' + topo_auth_string })
	topo = etree_to_dict( ET.fromstring(r.text) )
	return json.dumps(topo)

def createLinkAggregation(resourcename, interface, type, value, url,opennaas_user,opennaas_pwd):
	payload = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ns2:aggregatedInterface xmlns:ns2="opennaas.api">
  <id>ae2</id>
  <interfaces>
    <interface>ge-0/0/3</interface>
    <interface>ge-0/0/4</interface>
  </interfaces>
  <aggregationOptions>
    <entry>
      <key>link-speed</key>
      <value>1g</value>
    </entry>
    <entry>
      <key>minimum-links</key>
      <value>1</value>
    </entry>
  </aggregationOptions>
</ns2:aggregatedInterface>"""
	r = requests.post("%srouter/%s/linkaggregation" % (url, resourcename),  headers = {'Content-Type': 'application/xml'} ,  data = payload, auth=(opennaas_user, opennaas_pwd))
	print r.status_code
	print r.headers
	print r.text
	return vlanBridges
	
def addToQueue(resourcename, interface, type, value, url,opennaas_user,opennaas_pwd):

	print interface,type,value
	if type == "description": url = "%srouter/%s/ip/interfaces/description?interface=%s" % (url, resourcename, interface)
	if type == "ipv4address": url = "%srouter/%s/ip/interfaces/addresses/ipv4?interface=%s" % (url, resourcename, interface)
	if type == "ipv6address": url = "%srouter/%s/ip/interfaces/addresses/ipv6?interface=%s" % (url, resourcename, interface)
	if type == "status": url = "%srouter/%s/chassis/interfaces/status/%s?ifaceName=%s" % (url, resourcename, value, interface)

	if type == "status":
		r = requests.put(url, auth=(opennaas_user, opennaas_pwd), headers = {"content-type":"application/xml"})
	else:	
		r = requests.post(url, data = value, auth=(opennaas_user, opennaas_pwd), headers = {"content-type":"application/xml"})
	print r
	return json.dumps(r.text)

def main(): 
	#print getRouterInterfaces('switch1',settings.opennaas_url,settings.opennaas_user, settings.opennaas_pwd)
	#print getTopology("fakeNet",settings.opennaas_url,settings.topo_auth_string)
	print ""
	
if __name__ == "__main__":
    main()

