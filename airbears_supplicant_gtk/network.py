import dbus
import logging

from airbears_supplicant_gtk import log
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GObject

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

    def connected_networks(self):
        ssids = []

        bus = dbus.SystemBus()
        nm_proxy = bus.get_object(self.NM_SERVICE, self.NM_OBJECT)
        nm_iface = dbus.Interface(nm_proxy, self.NM_INTERFACE)
        nm_props = dbus.Interface(nm_proxy, self.DBUS_PROPERTIES_INTERFACE)

        active_cons = nm_props.Get(self.NM_INTERFACE, "ActiveConnections")
        for active in active_cons:
            active_proxy = bus.get_object(self.NM_INTERFACE, active)
            active_props = dbus.Interface(active_proxy, self.DBUS_PROPERTIES_INTERFACE)

            con_path = active_props.Get("org.freedesktop.NetworkManager.Connection.Active", "Connection")
            con_proxy = bus.get_object(self.NM_INTERFACE, con_path)

            connection = dbus.Interface(con_proxy, "org.freedesktop.NetworkManager.Settings.Connection")
            settings = connection.GetSettings()
            if '802-11-wireless' in settings:
                ssids.append(_byte_array_to_string(settings['802-11-wireless']['ssid']))
        logger.debug("connected_networks call returned: [%s]" % ",".join(ssids))
        return ssids
