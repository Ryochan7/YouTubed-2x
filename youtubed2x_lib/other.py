import os, sys
import urllib, urllib2
import cookielib
import socket
import gzip
import StringIO
import re
WINDOWS = (sys.platform == "win32")


class PageNotFound (Exception): pass


class UserDirectoryIndex (object):
    home_dir = data_dir = os.path.expanduser ("~")
    config_dir = ""

    if WINDOWS:
        # Useful for Windows Vista and Windows 7
        if "LOCALAPPDATA" in os.environ:
            data_dir = os.environ["LOCALAPPDATA"]
            config_dir = os.path.join (data_dir, "youtubed-2x")
        # Useful for Windows XP and below
        elif "APPDATA" in os.environ:
            data_dir = os.environ["APPDATA"]
            config_dir = os.path.join (data_dir, "youtubed-2x")
        else:
            raise Exception ("LOCALAPPDATA nor APPDATA specified. Should not be here")
    else:
        config_dir = os.path.join (data_dir, ".youtubed-2x")


def getPage (url, data=None, read_page=True, get_headers=False, additional_headers={}):
    """Generic function that makes requests for pages"""
    if data and not isinstance (data, dict):
        raise TypeError ("Data argument must be a dictionary")
    elif data:
        data = urllib.urlencode (data)
    if additional_headers and not isinstance (additional_headers, dict):
        raise TypeError ("Additional headers argument must be a dictionary")

    req = urllib2.Request (url, data)
    req.add_header ("User-Agent", USER_AGENT)
    req.add_header ("Accept-encoding", "gzip")

    for key, value in additional_headers.iteritems ():
        req.add_header (key, value)

    try:
        handle = urllib2.urlopen (req)
    except:
        raise PageNotFound ("Page \"%s\" could not be found" % url)

    if read_page:
        if handle.headers.get ("Content-Encoding") == "gzip":
            compressed_data = handle.read ()
            page = gzip.GzipFile (fileobj=StringIO.StringIO (compressed_data)).read ()
        else:
            page = handle.read ()
    else:
        page = None

    newurl = handle.geturl ()
    handle.close ()
    if get_headers:
        return page, newurl, handle.info ()

    return page, newurl

# Set user agent and cookie management
VERSION = "2009.11.26"
APP_NAME = "YouTubed-2x"
#USER_AGENT = {'User-agent' : '%s/%s' % (APP_NAME, VERSION)}
USER_AGENT = "%s/%s" % (APP_NAME, VERSION)
cj = cookielib.LWPCookieJar ()
#opener = urllib2.build_opener (urllib2.HTTPCookieProcessor(cj), urllib2.HTTPHandler(debuglevel=1))
opener = urllib2.build_opener (urllib2.HTTPCookieProcessor (cj), urllib2.ProxyHandler ())
urllib2.install_opener (opener)
#urllib2.install_opener (urllib2.build_opener (urllib2.ProxyHandler ()))

#print socket.getdefaulttimeout()
socket.setdefaulttimeout (15)
#socket.setdefaulttimeout (0)


def remove_proxy ():
    opener = urllib2.build_opener (urllib2.HTTPCookieProcessor (cj), urllib2.ProxyHandler ())
    urllib2.install_opener (opener)


def set_proxy (server, port):
    server = server.replace ("http://", "")
    temp_ip_re = re.compile (r"^\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}$")

    if temp_ip_re.match (server):
        proxy_handler = urllib2.ProxyHandler ({"http": "http://%s:%s" % (server, port)})

        opener = urllib2.build_opener (urllib2.HTTPCookieProcessor (cj), proxy_handler)
        urllib2.install_opener (opener)
    else:
        raise Exception ("Invalid server address passed")


