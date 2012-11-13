import logging
import signal

from airbears_supplicant_gtk import log
from airbears_supplicant_gtk.calnet import GnomeCredentialStore, Authenticator
from airbears_supplicant_gtk.network import NetworkManagerMonitor
from airbears_supplicant_gtk.ui import CalNetAuthnDialog, StatusIcon
from gi.repository import Gtk

logger = logging.getLogger(__name__)

class Supplicant:
    def __init__(self, credential_store, network_monitor):
        self.credential_store = credential_store
        self.network_monitor = network_monitor
        self.status_icon = StatusIcon(self)
        self.authenticator = Authenticator(self)
        
        self._wifi_connected_signal = self.network_monitor.connect('wifi-connected',
                                                                    self.on_wifi_connected)
        
        self.status_icon.notify("Ready and waiting for AirBears WiFi")
        
    def start(self):
        logger.debug("Starting the AirBears Supplicant GTK service")
        logger.debug("Registering network monitor")
        self.network_monitor.register()
    
    def stop(self):
        logger.debug("Shutting down the AirBears Supplicant GTK service")
        Gtk.main_quit()
    
    def on_wifi_connected(self, network_monitor, ssid):
        logger.debug("Supplicant received signal we are connected to SSID: %s" % ssid)
        if ssid == "AirBears":
            self.status_icon.notify("Connected to AirBears. Attempting authentication.")
            logger.debug("Connected to AirBears!")

            credentials = self.credential_store.get_credentials()
            authentication = self.authenticator.authenticate(*credentials)
            logger.debug("Authentication returned: %s" % authentication)
        else:
            logger.debug("Connected to non-CalNet-authed network")

def main(*args, **kwargs):
    credential_store = GnomeCredentialStore()
    network_monitor = NetworkManagerMonitor()
    supplicant = Supplicant(credential_store, network_monitor)
    supplicant.start()
    
    # so that Ctrl+C kills the Gtk loop
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()
