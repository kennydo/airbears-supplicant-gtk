import logging
import signal

from airbears_supplicant_gtk import log
from airbears_supplicant_gtk.calnet import GnomeCredentialStore, AirBearsAuthenticator, ResCompAuthenticator
from airbears_supplicant_gtk.network import NetworkManagerMonitor
from airbears_supplicant_gtk.ui import CalNetAuthnDialog, StatusIcon
from gi.repository import Gtk, Notify

logger = logging.getLogger(__name__)

class Supplicant:
    def __init__(self, credential_store, network_monitor):
        self._last_notification = None
        self.credential_store = credential_store
        self.network_monitor = network_monitor
        self.status_icon = StatusIcon(self)
        
        self._wifi_connected_signal = self.network_monitor.connect('wifi-connected',
                                                                    self.on_wifi_connected)
        
        self.notify("Ready and waiting for AirBears WiFi")
        
    def start(self):
        logger.debug("Starting the AirBears Supplicant GTK service")
        logger.debug("Registering network monitor")
        self.network_monitor.register()
    
    def stop(self):
        logger.debug("Shutting down the AirBears Supplicant GTK service")
        Gtk.main_quit()

    def notify(self, body):
        if self._last_notification:
            self._last_notification.close()
        n = Notify.Notification.new("AirBears Supplicant", body, self.status_icon.icon_path())
        n.show()
        self._last_notification = n
    
    def on_wifi_connected(self, network_monitor, ssid):
        logger.debug("Supplicant received signal we are connected to SSID: %s" % ssid)
        if ssid == "AirBears":
            self.notify("Connected to AirBears. Attempting authentication.")
            logger.debug("Connected to AirBears!")
            self.authenticator = AirBearsAuthenticator(self)

            credentials = self.credential_store.get_credentials()
            if credentials:
                authentication = self.authenticator.authenticate(*credentials)

            logger.debug("Authentication to AirBeras returned: %s" % authentication)
        elif ssid == "RESCOMP":
            self.notify("Connected to ResComp WiFi. Attempting authentication.")
            self.authenticator = ResCompAuthenticator(self)
            credentials = self.credential_store.get_credentials()
            if credentials:
                authentication = self.authenticator.authenticate(*credentials)
            logger.debug("Authenticaton to ResComp returned: %s" % authentication)
        else:
            logger.debug("Connected to non-CalNet-authed network")

def main(*args, **kwargs):
    Notify.init("AirBears Supplicant")
    credential_store = GnomeCredentialStore()
    network_monitor = NetworkManagerMonitor()
    supplicant = Supplicant(credential_store, network_monitor)
    supplicant.start()
    
    # so that Ctrl+C kills the Gtk loop
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()
