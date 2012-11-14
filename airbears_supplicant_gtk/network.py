import dbus
import logging

from airbears_supplicant_gtk import log
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Gio, GObject, NMClient

logger = logging.getLogger(__name__)

class NetworkMonitor(GObject.GObject):
    __gsignals__ ={
        'wifi-connected': (GObject.SIGNAL_RUN_FIRST,
                           None,
                           (str,)),
    }

    def __init__(self):
        GObject.GObject.__init__(self)
    
    def register(self, wifi_callbacks):
        """
        Register with whatever system so that we receive notification of WiFi connections
        
        wifi_callbacks is a dict where the key is the SSID of a network, and the value
        is a 0-arity function to call when we connect to that network
        """
        raise NotImplementedError()
   
    def connected_networks(self):
        """
        Returns a list of SSIDs of connected WiFi networks
        """
        raise NotImplementedError()

def _byte_to_string(char):
    if 32 <= char < 127:
        return "%c" % char
    else:
        return urllib.quote(chr(char))

def _byte_array_to_string(bs):
    return ''.join([_byte_to_string(char) for char in bs])

class NetworkManagerMonitor(NetworkMonitor):
    NM_SERVICE = 'org.freedesktop.NetworkManager'
    NM_OBJECT = '/org/freedesktop/NetworkManager'
    NM_INTERFACE = 'org.freedesktop.NetworkManager'
    NM_WIRELESS_INTERFACE = 'org.freedesktop.NetworkManager.Device.Wireless'
    
    DBUS_PROPERTIES_INTERFACE = 'org.freedesktop.DBus.Properties'

    NM_DEVICE_STATE_ACTIVATED = 100
    
    def register(self):
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        try:
            bus.add_signal_receiver(self._handler,
                                    dbus_interface=self.NM_WIRELESS_INTERFACE,
                                    signal_name='PropertiesChanged')
            logger.debug("NetworkManagerMonitor is now listening to the PropertiesChanged signal of NetworkManager")
        except dbus.DBusException, e:
            logger.exception(e)
        self._check_networks()

    def _check_networks(self):
        connected_ssids = self.connected_networks()
        for ssid in connected_ssids:
            logger.debug("Emitting wifi-connected signal for SSID: %s" % ssid)
            self.emit('wifi-connected', ssid)
    
    def _handler(self, properties):
        if 'State' in properties:
            if properties['State'] == self.NM_DEVICE_STATE_ACTIVATED:
                logger.debug("NM state change was a device becoming active, so we should check our connected networks")
                self._check_networks()

    def _wifi_devices(self):
        nm_client = NMClient.Client()
        wifi_devices = [device for device in nm_client.get_devices() if isinstance(device, NMClient.DeviceWifi)]
        return wifi_devices

    def connected_networks(self):
        ssids = []
        for device in self._wifi_devices():
            active_ap = device.get_active_access_point()
            if active_ap:
                ssids.append(active_ap.get_ssid())
        logger.debug("connected_networks call returned: [%s]" % ",".join(ssids))
        return ssids
