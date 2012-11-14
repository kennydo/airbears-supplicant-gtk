import cookielib
import logging
import re
import socket
import time
import urllib
import urllib2
import urlparse

from airbears_supplicant_gtk import log
from airbears_supplicant_gtk.calnet.credentialstore import TestCredentialStore, GnomeCredentialStore
from gi.repository import GObject

logger = logging.getLogger(__name__)

AIRBEARS_CAS_URL = "https://auth.berkeley.edu/cas/login?service=https%3a%2f%2fwlan.berkeley.edu%2fcgi-bin%2flogin%2fcalnet.cgi%3fsubmit%3dCalNet%26url%3d"
AIRBEARS_LANDING_URL = "https://wlan.berkeley.edu/cgi-bin/login/calnet.cgi?url=&count=1"

class BaseAuthenticator(GObject.GObject):
    __gsignals__ = {
        'dns-wait-start': (GObject.SIGNAL_RUN_FIRST,
                           None,
                           ()),
        'dns-wait-failed': (GObject.SIGNAL_RUN_FIRST,
                            None,
                            ()),
        'dns-wait-succeeded': (GObject.SIGNAL_RUN_FIRST,
                               None,
                               ()),
        'incorrect-credentials': (GObject.SIGNAL_RUN_FIRST,
                                  None,
                                  ()),
        'successful-authntication': (GObject.SIGNAL_RUN_FIRST,
                                     None,
                                     ()),
    }

    def __init__(self, service):
        self.service = service
        self.cookies = cookielib.CookieJar()
        self.url_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
    
    def authenticate(self, username, password, cas_url=AIRBEARS_CAS_URL, landing_url=AIRBEARS_LANDING_URL):
        raise NotImplementedError()

class ResCompAuthenticator(BaseAuthenticator):
    def __init__(self, service):
        super(ResCompAuthenticator, self).__init__(service)

        # get the net-auth-#.housing.berkeley.edu host
        redirected = self.url_opener.open("http://www.google.com")
        host = urlparse.urlparse(redirected.url).netloc
        if not host.endswith("google.com"):
            self.net_auth_host = host
        else:
            self.net_auth_host = None
       
        logger.debug("Got net-auth-host: %s" % self.net_auth_host)

        self.cas_url = "https://auth.berkeley.edu/cas/login?%s" % urllib.urlencode({
            "service": redirected.url
        })
        self.landing_url = redirected.url

    def authenticate(self, username, password):
        if not self.net_auth_host:
            logger.debug("We are already logged into ResComp WiFi")
            return True

        logger.debug("Trying to authenticate")
        self.service.status_icon.notify("Awaiting DNS resolution")
        # looptry until DNS works
        cas_host = urlparse.urlparse(self.cas_url).netloc
        failed_dns_attempts = 0
        while failed_dns_attempts < 30:
            try:
                addr_info = socket.getaddrinfo(cas_host, 443)
                logger.debug("Successfully resolved DNS. Attempting authentication.")
                self.service.status_icon.notify("DNS is up!")
                break
            except Exception, e:
                # wait 2 seconds
                logger.debug("Attempt %s at resolving DNS failed, so sleeping" % failed_dns_attempts)
                logger.exception(e)
                time.sleep(2)
                failed_dns_attempts += 1
        if not addr_info:
            self.service.status_icon.notify("DNS resolution failed. Giving up.")
            return False
            
        calnet_content =  self.url_opener.open(self.cas_url).read()
        logger.debug(calnet_content)
        if "Login Successful" in calnet_content:
            logger.debug("We were already logged into CalNet")
            return True

        calnet_noop = re.findall(r'_cNoOpConversation.*?"', calnet_content)[0].replace('"', '')
        post_data = urllib.urlencode({
            "username": username,
            "password": password,
            "_eventId": "submit",
            "lt": calnet_noop,
        })
        
        login_result = self.url_opener.open(self.cas_url, post_data).read()
        logger.debug(self.cas_url)
        logger.debug(login_result)
        if "you provided are incorrect" in login_result:
            logger.debug("Authentication failed because of incorrect CalNet credentials")
            self.service.status_icon.notify("CalNet authentication failed because of incorrect credentials")
            return False
        
        if "is a required field" in login_result:
            logger.debug("Authentication failed because of empty username or password")
            self.service.status_icon.notify("CalNet authentication failed because of empty username or password")
            return False
       
        if "Login Successful" in login_result:
            logger.debug("Authentication completed without WLAN redirect")
            self.service.status_icon.notify("Successfully authenticated to CalNet")
            return True
        return False

class AirBearsAuthenticator(BaseAuthenticator):
    def __init__(self, service):
        super(AirBearsAuthenticator, self).__init__(service)

        self.cas_url = AIRBEARS_CAS_URL
        self.landing_url = AIRBEARS_LANDING_URL

    def authenticate(self, username, password):
        self.service.status_icon.notify("Awaiting DNS resolution")
        # looptry until DNS works
        cas_host = urlparse.urlparse(self.cas_url).netloc
        failed_dns_attempts = 0
        while failed_dns_attempts < 30:
            try:
                addr_info = socket.getaddrinfo(cas_host, 443)
                logger.debug("Successfully resolved DNS. Attempting authentication.")
                self.service.status_icon.notify("DNS is up!")
                break
            except Exception, e:
                # wait 2 seconds
                logger.debug("Attempt %s at resolving DNS failed, so sleeping" % failed_dns_attempts)
                logger.exception(e)
                time.sleep(2)
                failed_dns_attempts += 1
        if not addr_info:
            self.service.status_icon.notify("DNS resolution failed. Giving up.")
            return False
            
        calnet_content =  self.url_opener.open(cas_url).read()
        if "already logged in to" in calnet_content:
            logger.debug("CalNet was already logged in before attempting authentication")
            return True
        
        calnet_noop = re.findall(r'_cNoOpConversation.*?"', calnet_content)[0].replace('"', '')
        post_data = urllib.urlencode({
            "username": username,
            "password": password,
            "_eventId": "submit",
            "lt": calnet_noop,
        })
        
        login_result = self.url_opener.open(self.cas_url, post_data).read()
        if "you provided are incorrect" in login_result:
            logger.debug("Authentication failed because of incorrect CalNet credentials")
            self.service.status_icon.notify("CalNet authentication failed because of incorrect credentials")
            return False
        
        if "is a required field" in login_result:
            logger.debug("Authentication failed because of empty username or password")
            self.service.status_icon.notify("CalNet authentication failed because of empty username or password")
            return False
       
        if "successfully logged into" in login_result:
            logger.debug("Authentication completed without WLAN redirect")
            self.service.status_icon.notify("Successfully authenticated to CalNet")
            return True
        else:
            content = self.url_opener.open(self.landing_url).read()
            if "already logged in to" not in content:
                logger.debug("Redirect successfuly, and already logged into WiFi")
            else:
                logger.debug("Authentication completed")
            return True
        return False
