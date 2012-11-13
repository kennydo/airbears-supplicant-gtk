import logging
import signal

from airbears_supplicant_gtk import log
from airbears_supplicant_gtk.calnet import GnomeCredentialStore, Authenticator
from airbears_supplicant_gtk.ui import CalNetAuthnDialog, StatusIcon
from gi.repository import Gtk

logger = logging.getLogger(__name__)

class Supplicant:
    def __init__(self, credential_store):
        self.credential_store = credential_store
        self.status_icon = StatusIcon(self)
        self.authenticator = Authenticator(self)
        
        self.status_icon.notify("Ready and waiting for AirBears WiFi")
        
    def start(self):
        logger.debug("Starting the AirBears Supplicant GTK service")    
    
    def stop(self):
        logger.debug("Shutting down the AirBears Supplicant GTK service")
        Gtk.main_quit()

def main(*args, **kwargs):
    credential_store = GnomeCredentialStore()
    supplicant = Supplicant(credential_store)
    supplicant.start()
    
    # so that Ctrl+C kills the Gtk loop
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()
