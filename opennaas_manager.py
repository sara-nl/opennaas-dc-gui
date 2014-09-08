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

def executeQueue(resource_name, url, opennaas_user, opennaas_pwd):
	r = requests.post("%srouter/%s/queue/execute" % (url, resource_name), auth=(opennaas_user, opennaas_pwd))
	return json.dumps(r.text)

def clearQueue(resource_name, url, opennaas_user, opennaas_pwd):
	r = requests.post("%srouter/%s/queue/clear" % (url, resource_name), auth=(opennaas_user, opennaas_pwd))
	return json.dumps(r.text)

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
	
	resource = dict()
	resource.update({"id" : resource_id})
	capabilities = ""
	r = requests.get("%sresources/%s" % (url, resource_id), auth=(opennaas_user, opennaas_pwd))
	
	resourceInfoTree = ET.fromstring(r.text)
						
	for elem in resourceInfoTree.iter():	
				
		if elem.tag == "name": resource.update({'name' :elem.text})
		if elem.tag == "type": resource.update({'type' :elem.text})
		if elem.tag == "state": resource.update({'status' :elem.text})
		if elem.tag == "capability": capabilities = capabilities + " " + elem.text
	resource.update({'capabilities' :capabilities.strip()})
			
	queue = getQueue(resource.get('name'), url, opennaas_user, opennaas_pwd)
	resource.update({'queue' : json.loads(queue)})
	
	return json.dumps(resource)

def getResources(url, opennaas_user, opennaas_pwd):
	resources = defaultdict(dict)
	
	r = requests.get(url + "resources/", auth=(opennaas_user, opennaas_pwd))
	
	index = 0
	tree = ET.fromstring(r.text)
	for elem in tree.iter():
		if elem.tag == "resource":
			resources[index] = json.loads(getResource(elem.text, url, opennaas_user, opennaas_pwd))
			index = index + 1

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
	interfaces = defaultdict(dict)
	
	index = 0
	r = requests.get("%srouter/%s/chassis/interfaces" % (url, resourcename), auth=(opennaas_user, opennaas_pwd))
	tree = ET.fromstring(r.text)
	for elem in tree.iter():
		
		if elem.tag == "interface":
			ip= ""
			interfaces[index].update({'description': ""})
			interfaces[index].update({'ip': ""})
			ri = requests.get("%srouter/%s/chassis/interfaces/info?interfaceName=%s" % (url, resourcename, elem.text), auth=(opennaas_user, opennaas_pwd))
			ri_tree = ET.fromstring(ri.text)
			for ri_elem in ri_tree.iter():
				if ri_elem.tag == "name": interfaces[index].update({'name' : ri_elem.text})
				if ri_elem.tag == "description": interfaces[index].update({'description' : ri_elem.text})
				if ri_elem.tag == "state": interfaces[index].update({'state' : ri_elem.text})
			rip = requests.get("%srouter/%s/ip/interfaces/addresses?interface=%s" % (url, resourcename, elem.text), auth=(opennaas_user, opennaas_pwd))
			
			rip_tree = ET.fromstring(rip.text)
			for rip_elem in rip_tree.iter():
				if rip_elem.tag == "ipAddress": ip = ip + " " + rip_elem.text
				
			interfaces[index].update({'ip' :ip.strip()})
			index = index + 1
	
	return json.dumps(interfaces)

def getRouterVLANs(resourcename, url , opennaas_user, opennaas_pwd):
	interfaces = defaultdict(dict)
	vlanBridges = defaultdict(dict)
	vlaninterfaces = []
	
	# Build dictionary of all vlans with their attached interfaces
	index = 0
	r = requests.get("%srouter/%s/vlanbridge" % (url, resourcename), auth=(opennaas_user, opennaas_pwd))
	tree = ET.fromstring(r.text)
	for elem in tree.iter():
		if elem.tag == "domainName":
			vlanBridges[index].update({'domainName': elem.text})
			rv = requests.get("%srouter/%s/vlanbridge/%s" % (url, resourcename, elem.text), auth=(opennaas_user, opennaas_pwd))
			rv_tree = ET.fromstring(rv.text)
				
			for rv_elem in rv_tree.iter():
				if rv_elem.tag == "vlanid": vlanBridges[index].update({'vlanid': rv_elem.text})
				if rv_elem.tag == "description": vlanBridges[index].update({'description': rv_elem.text})
				if rv_elem.tag == "interfaceName": vlaninterfaces.append(rv_elem.text)
			vlanBridges[index].update({'interfaceName': vlaninterfaces})	
			vlaninterfaces = []
			index = index + 1

	index = 0
	r = requests.get("%srouter/%s/chassis/interfaces" % (url, resourcename), auth=(opennaas_user, opennaas_pwd))
	tree = ET.fromstring(r.text)
	for elem in tree.iter():
		if elem.tag == "interface": 
			interfaces[index].update({'name': elem.text})
			rv = requests.get("%srouter/%s/vlanbridge/vlanoptions?iface=%s" % (url, resourcename, elem.text), auth=(opennaas_user, opennaas_pwd))
			rv_tree = ET.fromstring(rv.text)
			for rv_elem in rv_tree.iter():
				print rv_elem.text
				if rv_elem.text == "native-vlan-id":
					print "bla"
			index = index + 1
	
	return json.dumps(interfaces)
	
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
	print ""

if __name__ == "__main__":
    main()

