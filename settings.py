# WSGI settings in case of using standalone app instead of Apache mod_wsgi
WSGI_host = "yourhost"
WSGI_port = 8080

# OpenNaas URL + auth
opennaas_url = 'http://yourhost:8888/opennaas/'
opennaas_user = 'user'
opennaas_pwd = 'pass'

# Topology capability authentication string
topo_auth_string = 'pass'

### Settings for Cisco local resources

# logging for ncclient output
ncclient_logfile = "/tmp/ncclient.log"

# List of local resource tuples:
# Syntax is: ("id", "host", "username", "password")
local_hosts = [ ( "cisco1", "cisco1.yourdomain.com", "user", "pass" ),
( "cisco2", "cisco2.yourdomain.com", "user", "pass" ) ] 
