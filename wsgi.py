import sys
import settings
from cisco_manager import *
# getCiscoStatus, buildJSONStatusInfo, getCiscoConfig, getCiscoConfigFromFile, buildJSONConfigInfo, parseCiscoConfigChangeRPC, editCiscoConfig
from opennaas_manager import *
#getResources, updateResources, getResource, getRouterInterfaces, addToQueue, getQueue, executeQueue , clearQueue, removeQueueItems
from flask import Flask, request, render_template, Response, Blueprint
app = Flask(__name__)

wsgi_app = Blueprint('wsgi_app', __name__)

def get_localcredentials(devicename, local_hosts):
  for host in local_hosts:
    if host[0] == devicename:
		  return (host[1], host[2], host[3])
def get_local_resources(local_hosts):
  resources = []
  for resource in local_hosts:
    resources.append(resource[0])
  return resources

@wsgi_app.route('/')
def index():
  return render_template('index.html')

@wsgi_app.route('/local/', methods=['GET'])
def local_overview():
  return render_template('local.html', resources = get_local_resources(settings.local_hosts) ) 

@wsgi_app.route('/local/<name>/', methods=['GET'])
def local_resources(name = None):
  return render_template('local_resources.html', name = name)

@wsgi_app.route('/local/<name>/getstatus', methods=['GET'])
def local_getstatus(name = None):
  credentials = get_localcredentials(name, settings.local_hosts)
  return Response( getCiscoStatus(credentials[1],credentials[2],credentials[0] ), mimetype='application/json')

@wsgi_app.route('/local/<name>/getconfig', methods=['GET'])
def local_getconfig(name = None):
  credentials = get_localcredentials(name, settings.local_hosts)
  CiscoDict = getCiscoConfig(credentials[1],credentials[2],credentials[0])
  return Response( buildJSONConfigInfo(CiscoDict), mimetype='application/json')

@wsgi_app.route('/local/<name>/commit', methods=['POST'])
def local_commitconfig(name = None):
  jsonData = request.get_json(force = True)
  configString = parseCiscoConfigChangeRPC(jsonData)
  credentials = get_localcredentials(name, settings.local_hosts)
  editCiscoConfig(credentials[1],credentials[2],credentials[0],configString)
  return Response( '{"success": "true"}', mimetype='application/json')

@wsgi_app.route('/resources/')
def opennaas_resources():
  return render_template('opennaas_resources.html')

@wsgi_app.route('/resources/getresources')
def opennaas_getresources():
  resources = getResources(settings.opennaas_url, settings.opennaas_user, settings.opennaas_pwd)
  return Response( resources, mimetype='application/json')

@wsgi_app.route('/resources/getresource/<name>')
def opennaas_getresource(name = None):
  resources = getResource(name, settings.opennaas_url, settings.opennaas_user, settings.opennaas_pwd)
  return Response( resources, mimetype='application/json')

@wsgi_app.route('/resources/status/', methods=['POST'])
def opennaas_resources_action():
  resources = request.get_json(force = True)
  resources = updateResources(request.args.get('action'), resources, settings.opennaas_url, settings.opennaas_user, settings.opennaas_pwd)
  return Response( '{"success": "true"}', mimetype='application/json')

@wsgi_app.route('/router/<name>', methods=['POST', 'GET'])
def opennaas_resource_router(name = None):
  return render_template('opennaas_resource_router.html', name = name)
 
@wsgi_app.route('/router/<name>/getinterfaces', methods=['POST', 'GET'])
def opennaas_resource_router_getinterfaces(name = None):
  interfaces = getRouterInterfaces(name, settings.opennaas_url, settings.opennaas_user, settings.opennaas_pwd)
  return Response( interfaces, mimetype='application/json') 

@wsgi_app.route('/router/<name>/getcontext', methods=['POST', 'GET'])
def opennaas_resource_router_getcontext(name = None):
  data = getContext(name, settings.opennaas_url, settings.opennaas_user, settings.opennaas_pwd)
  return Response( data, mimetype='application/json') 

@wsgi_app.route('/router/<resource_name>/queue', methods=['GET', 'POST'])
def opennaas_resource_router_queue(resource_name = None):
  action = request.args.get('action')
  print request.args.get('interface')
  if request.method == "POST": resources = request.get_json(force = True)
  if action == "get": response = getQueue(resource_name, settings.opennaas_url, settings.opennaas_user, settings.opennaas_pwd)
  if action == "add": response = addToQueue(resource_name, request.args.get('interface'), request.args.get('type'), request.args.get('value'), settings.opennaas_url, settings.opennaas_user, settings.opennaas_pwd)
  if action == "execute": response = executeQueue(resource_name, settings.opennaas_url, settings.opennaas_user, settings.opennaas_pwd)
  if action == "remove": response = removeQueueItems(resource_name, resources, settings.opennaas_url, settings.opennaas_user, settings.opennaas_pwd)
  if action == "clear": response = clearQueue(resource_name, settings.opennaas_url, settings.opennaas_user, settings.opennaas_pwd)
  return Response( response, mimetype='application/json')

@wsgi_app.route('/queue/', methods=['GET'])
def opennaas_queue(action = None):
  if action == None: return render_template('opennaas_queue.html')

@wsgi_app.route('/queue/<action>', methods=['GET', 'POST'])
def opennaas_queueaction(action = None):
  if action == None: return render_template('opennaas_queue.html')
  if request.method == "POST": resources = request.get_json(force = True)
  if action == "execute": response = executeQueue(resources, settings.opennaas_url, settings.opennaas_user, settings.opennaas_pwd)
  if action == "clear": response = clearQueue(resources, settings.opennaas_url, settings.opennaas_user, settings.opennaas_pwd)
  return Response( response, mimetype='application/json')





