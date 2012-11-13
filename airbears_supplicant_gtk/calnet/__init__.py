import cookielib
import logging
import re
import time
import urllib
import urllib2
import urlparse

from airbears_supplicant_gtk import log
from airbears_supplicant_gtk.calnet.credentialstore import TestCredentialStore, GnomeCredentialStore

logger = logging.getLogger(__name__)

AIRBEARS_CAS_URL = "https://auth.berkeley.edu/cas/login?service=https%3a%2f%2fwlan.berkeley.edu%2fcgi-bin%2flogin%2fcalnet.cgi%3fsubmit%3dCalNet%26url%3d"
AIRBEARS_LANDING_URL = "https://wlan.berkeley.edu/cgi-bin/login/calnet.cgi?url=&count=1"

class Authenticator:
    def __init__(self, service):
        self.service = service
        self.cookies = cookielib.CookieJar()
        self.url_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
    
    def authenticate(self, username, password, cas_url=AIRBEARS_CAS_URL, landing_url=AIRBEARS_LANDING_URL):
        self.service.status_icon.notify("Awaiting DNS resolution")
        # looptry until DNS works
        cas_host = urlparse.urlparse(cas_url).netlog
        failed_dns_attempts = 0
        while failed_dns_attempts < 30:
            try:
                addr_info = socket.getaddrinfo(cas_host, 443)
                logger.debug("Successfully resolved DNS. Attempting authentication.")
                self.service.status_icon.notify("DNS is up!")
                break
            except:
                # wait 2 seconds
                logger.debug("Attempt %s at resolving DNS failed, so sleeping" % failed_dns_attempts)
                time.sleep(2)
                failed_dns_attempts += 1
        if not addr_info:
            self.service.status_icon.notify("DNS resolution failed. Giving up.")
            return False
            
        calnet_content =  self.url_opener(cas_url).read()
        if "already logged in to" in calnet_content:
            logger.debug("CalNet was already logged in before attempting authentication")
            return True
        
        calnet_noop = re.findall(r'_cNoOpConversation.*?"', first_calnet_login)[0].replace('"', '')
        post_data = urllib.urlencode({
            "username": username,
            "password": password,
            "_eventId": "submit",
            "lt": calnet_noop,
        })
        
        login_result = self.url_opener.open(cas_url, post_data).read()
        if "you provided are incorrect" in login_result:
            logger.debug("Authentication failed because of incorrect CalNet credentials")
            self.service.status_icon.notify("CalNet authentication failed because of incorrect credentials")
            return False
       
        if "successfully logged into" in login_result:
            logger.debug("Authentication completed without WLAN redirect")
            self.service.status_icon.notify("Successfully authenticated to CalNet")
            return True
        else:
            content = self.url_opener.open(landing_url).read()
            if "already logged in to" not in content:
                logger.debug("Redirect successfuly, and already logged into WiFi")
            else:
                logger.debug("Authentication completed")
            return True
        return True
