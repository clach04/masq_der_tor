#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
# debugserver_wsgi2.py - Dumps out client calling information
# Copyright (C) 2014  Chris Clark
"""Can be used to reverse engineer protocols with an existing client

Uses WSGI, see http://docs.python.org/library/wsgiref.html

Python 2 or Python 3

See twin - debugserver2_wsgi_class.py

TODO

  * doc/readme -e.g. environment variables (404 and port) and payload return/response (sample)
  * provide some samples using curl/wget with GET/POST/CUSTOM
"""

try:
    # py3
    from urllib.parse import parse_qs
except ImportError:
    # py2 (and <py3.8)
    from cgi import parse_qs
import os
try:
    import json
except ImportError:
    json = None
import logging
import mimetypes
from pprint import pprint

import socket
import struct
import sys
import time
from wsgiref.simple_server import make_server

try:
    import bjoern
except ImportError:
    bjoern = None

try:
    import meinheld  # https://github.com/mopemope/meinheld
except ImportError:
    meinheld = None


ALWAYS_RETURN_404 = True
DEFAULT_SERVER_PORT = 80  # Revisit for non-Windows


log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel(level=logging.DEBUG)


def to_bytes(in_str):
    # could choose to only encode for Python 3+
    return in_str.encode('utf-8')

def not_found(environ, start_response):
    """serves 404s."""
    #start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    #return ['Not Found']
    start_response('404 NOT FOUND', [('Content-Type', 'text/html')])
    return [to_bytes('''<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>404 Not Found</title>
</head><body>
<h1>Not Found</h1>
<p>The requested URL /??????? was not found on this server.</p>
</body></html>''')]


# Weekday and month names for HTTP date/time formatting; always English!
_weekdayname = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_monthname = [None, # Dummy so we can use 1-based month numbers
              "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def header_format_date_time(timestamp):
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    return "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
        _weekdayname[wd], day, _monthname[month], year, hh, mm, ss
    )

def current_timestamp_for_header():
    return header_format_date_time(time.time())


def determine_local_ipaddr():
    local_address = None

    # Most portable (for modern versions of Python)
    if hasattr(socket, 'gethostbyname_ex'):
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if not ip.startswith('127.'):
                local_address = ip
                break
    # may be none still (nokia) http://www.skweezer.com/s.aspx/-/pypi~python~org/pypi/netifaces/0~4 http://www.skweezer.com/s.aspx?q=http://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib has alonger one

    if sys.platform.startswith('linux'):
        import fcntl

        def get_ip_address(ifname):
            ifname = ifname.encode('latin1')
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15])
            )[20:24])

        if not local_address:
            for devname in os.listdir('/sys/class/net/'):
                try:
                    ip = get_ip_address(devname)
                    if not ip.startswith('127.'):
                        local_address = ip
                        break
                except IOError:
                    pass

    # Jython / Java approach
    if not local_address and InetAddress:
        addr = InetAddress.getLocalHost()
        hostname = addr.getHostName()
        for ip_addr in InetAddress.getAllByName(hostname):
            if not ip_addr.isLoopbackAddress():
                local_address = ip_addr.getHostAddress()
                break

    if not local_address:
        # really? Oh well lets connect to a remote socket (Google DNS server)
        # and see what IP we use them
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 53))
        ip = s.getsockname()[0]
        s.close()
        if not ip.startswith('127.'):
            local_address = ip

    return local_address


# A relatively simple WSGI application. It's going to print out the
# environment dictionary after being updated by setup_testing_defaults
def simple_app(environ, start_response):
    print('')  # newline to seperate calls
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    result= []

    path_info = environ['PATH_INFO']

    # Returns a dictionary in which the values are lists
    if environ.get('QUERY_STRING'):
        get_dict = parse_qs(environ['QUERY_STRING'])
    else:
        get_dict = {}  # wonder if should make None to make clear its not there at all

    # dump out information about request
    #print(environ)
    #pprint(environ)
    print('PATH_INFO %r' % environ['PATH_INFO'])
    print('CONTENT_TYPE %r' % environ.get('CONTENT_TYPE'))  # missing under bjoern
    print('QUERY_STRING %r' % environ.get('QUERY_STRING'))  # missing under bjoern
    print('QUERY_STRING dict %r' % get_dict)
    print('REQUEST_METHOD %r' % environ['REQUEST_METHOD'])
    #print('environ %r' % environ) # DEBUG, potentially pretty print, but dumping this is non-default
    #print('environ:') # DEBUG, potentially pretty print, but dumping this is non-default
    #pprint(environ, indent=4)
    print('Filtered headers, HTTP*')
    for key in environ:
        if key.startswith('HTTP_'):  # TODO potentially startswith 'wsgi' as well
            # TODO remove leading 'HTTP_'?
            print('http header ' + key + ' = ' + repr(environ[key]))

    # TODO if not GET
    # POST values
    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    request_body = None

    read_body_payload = True
    if environ['REQUEST_METHOD'] != 'GET' and read_body_payload:
        # Read POST, etc. body
        if request_body_size:
            print('read with size %r' % request_body_size)
            request_body = environ['wsgi.input'].read(request_body_size)
        else:
            print('read with NO size')
            #import pdb ; pdb.set_trace()
            request_body = environ['wsgi.input'].read()  # everything, seen on linux where zero param would return no bytes
            print('read with NO size completed')

    # http://alteraction.com/cgi-bin/
    if path_info and path_info.startswith('/cgi-bin/'):  # '/cgi-bin/user.cgi' and (once?) '/cgi-bin/setup.cgi' request_body: b'app=g1&cgimethod=whichwebpages'
        log.debug('request_body: %r', request_body)
        # expecting; request_body: b'cgimethod=checkmessages&versionnumber=67&cgipassword=tempPass7x8E9&app=g1'
        # for now do NOT bother parsing
        # logic by negativespinner from https://www.reddit.com/r/abandonware/comments/pv1djv/comment/jl86w1j/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button
        if request_body.startswith(b'cgimethod=checkcontinue'):
            result = [to_bytes('["messageid": "success" ]')]  # yield to_bytes('...')
        else:  #  elif request_body.startswith(b'cgimethod=checkmessages'):
            game_state = {
                "messageid": "success",  # needed to continue to next episode
                "messagetext": {
                    "cost": "this is cost",
                    "more": "this is more",
                    "license": "this is license",
                    "emailtext": "this is emailtext",
                    "optionmessage": "this is option",
                    "firstendmessage": "firstend",
                    "nextendmessage": "nextend",
                    "return": "return",
                    "ZStartAgain2": "zstart",
                    "privacypolicy": "my privacy policy",
                    "emailrequired": "email required",
                    "messageid": "success",
                    "hijack": "hijack",
                    "flag": "flag",
                    "RegisterDriven": "RegisterDriven",
                    "VIPpassword": "VIPpassword",
                    "warnpages": "warnpages",
                    "episodemessage": "episodemessage",
                    "substract": "substract",  # this is the message shown after episode 4, just as 5 starts' Episode 5 of 5 ... substract
                    "substractmessage": "substractmessage"
                },
                # TODO make below variables
                "ticketsleft": 40,  # lives / ticket count from Nov 18, 2007 - https://lemmasoft.renai.us/forums/viewtopic.php?p=38537&sid=838be0e78a7ffcc6c7dc40c277d9cf87#p38537
                "userID": 1,
                #"userName":
            }
            #director_payload = '["messagetext": ["cost": "this is cost", "more": "this is more", "license": "this is license", "emailtext": "this is emailtext", "optionmessage": "this is option", "firstendmessage": "firstend", "nextendmessage": "nextend", "return": "return", "ZStartAgain2": "zstart", "privacypolicy": "my privacy policy", "emailrequired": "email required", "messageid": "success", "hijack": "hijack", "flag": "flag", "RegisterDriven": "RegisterDriven", "VIPpassword": "VIPpassword", "warnpages": "warnpages", "episodemessage": "episodemessage", "substract": "substract", "substractmessage": "substractmessage"]]'
            director_payload = json.dumps(game_state).replace('{', '[').replace('}', ']')
            #print(director_payload)
            result = [to_bytes(director_payload)]  # yield to_bytes('...')
    elif path_info and path_info.startswith('/auxiliars/help.htm'):  # http://www.alteraction.com/auxiliars/help.htm
        headers = [('Content-type', 'text/html')]
        result = [to_bytes('TODO help - nothing useful at https://web.archive.org/web/20080401000000*/http://www.alteraction.com/auxiliars/help.htm')]
    else:
        # return 404 by default
        return not_found(environ, start_response)

    start_response(status, headers)
    return result


def main(argv=None):
    print('Python %s on %s' % (sys.version, sys.platform))
    server_port = int(os.environ.get('PORT', DEFAULT_SERVER_PORT))

    print("Serving on port %d..." % server_port)
    print("ALWAYS_RETURN_404 = %r" % ALWAYS_RETURN_404)
    local_ip = os.environ.get('LISTEN_ADDRESS', determine_local_ipaddr())
    log.info('Starting server: %r', (local_ip, server_port))
    log.warning('NOTE this server assumes the client has been modified or running on a network that redirects alteraction.com to this server.')
    if bjoern:
        log.info('Using: bjoern')
        bjoern.run(simple_app, '', server_port)  # FIXME use local_ip?
    elif meinheld:
        # Untested, Segmentation fault when serving a file :-(
        meinheld.server.listen(('0.0.0.0', server_port))  # does not accept ''
        meinheld.server.run(simple_app)
    else:
        log.info('Using: wsgiref.simple_server')
        log.info('Issue CTRL-C to stop')
        httpd = make_server('', server_port, simple_app)  # FIXME use local_ip?
        httpd.serve_forever()

if __name__ == "__main__":
    sys.exit(main())
