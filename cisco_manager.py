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


# rpc.py adjusted:
# line 183:
# - return
# + #return


import sys
from optparse import OptionParser
from collections import defaultdict
from ncclient import manager
from ncclient.xml_ import *
from ncclient import transport
from ncclient import operations
import xml.etree.ElementTree as ET
import logging
import time
from ciscoconfparse import CiscoConfParse
import json
import settings
# Parse and check arguments
def buildParser():
    """
    Prepare parsing of command line options
    """

    parser = OptionParser("usage: %prog [options] hostname")

    parser.add_option("-P", "--port", 
                  dest="port", 
              default='22',
                      help="NETconf port default = 22", 
              metavar="PORT")
    parser.add_option("-u", "--username", 
              dest="username", 
              default='',
                      help="ssh username", 
              metavar="USERNAME")
    parser.add_option("-p", "--password", 
              dest="password", 
              default='',
                      help="ssh password (can be ommited when using remote ssh key)", 
              metavar="password")
    return parser

# callback function to fake unknown host key reply when making ssh connection
def returnTrue(host, fingerprint):
    return True

def createManager(user,pwd,host):
    logging.basicConfig(filename=settings.ncclient_logfile, level=logging.DEBUG)
       
    # Try to connect to the remote host
    try:
        conn = manager.connect(host=host, port=22, username=user, password=pwd ,allow_agent=False, look_for_keys=False, unknown_host_cb=returnTrue) 

    except transport.AuthenticationError:
        print "unable to connect [" + host + "], wrong username or password?"
        sys.exit(3)
    except transport.SSHUnknownHostError:
        print "Unknown host key for [" + host + "]"
        sys.exit(3)
    except transport.SSHError:
        print "SSH unreachable for [" + host + "]"
        sys.exit(3) 
    
    conn.timeout = 30

    return conn

def getCiscoStatus(user,pwd,host):

    FILTER = """  
    <filter type='subtree'>
        <config-format-text-block>
            <text-filter-spec> | begin zzz </text-filter-spec>
        </config-format-text-block>
        <oper-data-format-text-block>
            <show>interfaces description</show>
            <show>mac address-table</show>
        </oper-data-format-text-block>
    </filter>
    """

    conn = createManager(user,pwd,host)

    try:
        result = str(conn.dispatch(rpc_command = 'get', filter =FILTER) )

    except operations.errors.TimeoutExpiredError:
        print "RPC timeout expired"
        conn.close_session()
        sys.exit(3)

    conn.close_session()   # dont forget to close, else ssh session will not be shut down
    
    jsonarray = buildJSONStatusInfo(result) 
    return jsonarray

def buildJSONStatusInfo(RPCdata):
    
    interfaceDict = defaultdict(dict)
    macDict = defaultdict(dict)
    begin = RPCdata.find('<item><show>interfaces description</show><response>\n')
    end = RPCdata.find('</response></item><item>')
    data = RPCdata[begin+51:end]
    data = data.split('\n')
    data.pop(0)
    data.pop(0)
    index = 0
    for line in data:

        interfaceDict[index].update({'interface': ""})
        interfaceDict[index].update({'interfacelong': ""})
        interfaceDict[index].update({'adminstatus': ""})
        interfaceDict[index].update({'protocolstatus': ""})
        interfaceDict[index].update({'description': ""})
        interfaceDict[index].update({'macaddresses': ""})

        interfacelong = line[0:30].strip()
        interfacelong = interfacelong.replace("Fa", "FastEthernet")
        interfacelong = interfacelong.replace("Gi", "GigabitEthernet")
        interfacelong = interfacelong.replace("Te", "TenGigabitEthernet")
        interfacelong = interfacelong.replace("Po", "Port-channel")
        interfacelong = interfacelong.replace("Vl", "Vlan")
        
        interfaceDict[index].update({'interface': line[0:30].strip() })
        interfaceDict[index].update({'interfacelong': interfacelong })
        interfaceDict[index].update({'adminstatus': line[30:45].strip() })
        interfaceDict[index].update({'protocolstatus': line[45:54].strip() })
        interfaceDict[index].update({'description': line[54:].strip() })
        
        index = index + 1
    
    begin = RPCdata.find('<item><show>mac address-table</show><response>\n')
    end = RPCdata.find('</response></item></cli-oper-data-block>')
    macdata = RPCdata[begin+51:end]
    macdata = macdata.split('\n')
    index = 0

    for line in macdata:
        macDict[index].update({'mac' : ""})
        macDict[index].update({'interface' : "" })
        macDict[index].update({'mac' : line[8:26].strip() })
        macDict[index].update({'interface' : line[38:].strip() })
        index = index + 1
    
    for intf in interfaceDict:
        for mac in macDict:
        
            if macDict[mac].get('interface') == interfaceDict[intf].get('interface'):
                
                tempmac = interfaceDict[intf].get('macaddress')
                if tempmac == None:
                    tempmac = ""
                    tempmac = tempmac + " " + macDict[mac].get('mac')
                    tempmac = tempmac.strip()
                    interfaceDict[intf].update({'macaddresses' : tempmac })
    
    jsonarray = json.dumps(interfaceDict)
    
    return jsonarray
    
def getCiscoConfig(user,pwd,host):

    conn = createManager(user,pwd,host)

    try:
        result = str(conn.get_config(source='running'))

    except operations.errors.TimeoutExpiredError:
        print "RPC timeout expired"
        conn.close_session()
        sys.exit(3)

    conn.close_session()   # dont forget to close, else ssh session will not be shut down

    configTree = ET.fromstring(result)
    for elem in configTree.iter():
        if elem.tag.find("cli-config-data-block") != -1:
            config = elem.text.split('\n')
            parse = CiscoConfParse(config)
    
    return parse


def editCiscoConfig(user,pwd,host,configString):

    conn = createManager(user,pwd,host)

    try:
        result = str(conn.edit_config(target='running', config=configString))

    except operations.errors.TimeoutExpiredError:
        print "RPC timeout expired"
        conn.close_session()
        sys.exit(3)

    conn.close_session()


def getCiscoConfigFromFile(filename):
    f = open(filename, 'r')
    config = f.readlines()
    f.close()
    parse = CiscoConfParse(config)
    return parse

def buildJSONConfigInfo(config):
    ConfigDict = defaultdict(dict)
    VLANDict = defaultdict(dict)
    interfaceDict = defaultdict(dict)
    all_intfs = config.find_objects(r"^interface")
    index=0   
    for obj in all_intfs:
        #print obj.text
        children = obj.children
        
        interfaceDict[index].update({'vlan': 0})
        interfaceDict[index].update({'description': ""})
        interfaceDict[index].update({'adminstate': "enabled"})
        interfaceDict[index].update({'ifname': obj.text.replace("interface ","").strip()})
        for child in children:
 
            if child.text.find("switchport access vlan") != -1:
                interfaceDict[index].update({'vlan': int(child.text.replace('switchport access vlan ','').strip())})
            if child.text.find("description") != -1:
                interfaceDict[index].update({'description': child.text.replace('description ','').strip()})
            if child.text.find("shutdown") != -1:
                interfaceDict[index].update({'adminstate': child.text.strip()})

        index = index + 1

    all_vlans = config.find_objects(r"^vlan [0-9]")
    index=0  
    for obj in all_vlans:
        children = obj.children

        VLANDict[index].update({'name': 0})
        VLANDict[index].update({'vlan_id': int(obj.text.replace("vlan ","").strip())})
        for child in children:
            if child.text.find("name ") != -1:
                VLANDict[index].update({'name': child.text.replace('name ','').strip()})
        index = index + 1

    ConfigDict['interfaces'].update(interfaceDict)
    ConfigDict['vlans'].update(VLANDict)

    jsonarray = json.dumps(ConfigDict)
    
    return jsonarray

def parseCiscoConfigChangeRPC(ConfigArray):

    configString="<config>\n<cli-config-data-block>\n"
    for configItem in ConfigArray:
        
        configString = configString + "interface %s\n" % configItem[0]
        if configItem[1] == 'adminstate':
            if configItem[2] == 'enabled':
                configString = configString + "no shutdown\n"
            if configItem[2] == 'shutdown':
                configString = configString + "shutdown\n"
        if configItem[1] == 'vlan':
            configString = configString + "switchport mode access\nswitchport access vlan %s\n" % configItem[2]
        if configItem[1] == 'description':
            configString = configString + "description %s\n" % configItem[2]            
    
    configString = configString + "</cli-config-data-block>\n</config>"

    return configString

def main(): 
    start = int(round(time.time() * 1000))          # start execution timer

    parser = buildParser()
    (options, args) = parser.parse_args()

    if len(args) == 0:
        print "No hostname specified --exiting"
        quit()

    CiscoDict = getCiscoConfig(options.username,options.password,args[0])
    buildJSONConfigInfo(CiscoDict)
    end = int(round(time.time() * 1000))
    print "Execution time: {0}".format((end-start)/1000.0)

if __name__ == "__main__":
    main()
