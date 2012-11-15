import logging
import os

from airbears_supplicant_gtk import log
from airbears_supplicant_gtk.ui import CalNetAuthnDialog
from gi.repository import Gtk, GObject

logger = logging.getLogger(__name__)

class StatusIcon(GObject.GObject):
    __gsignals__ = {
        'popup-menu': (GObject.SIGNAL_RUN_FIRST,
                       None,
                       ()),
        'calnet-authn-window-opened': (GObject.SIGNAL_RUN_FIRST,
                                       None,
                                       (CalNetAuthnDialog,)),
    }

    def __init__(self, service):
        super(StatusIcon, self).__init__()
        self.service = service
        self.menu = StatusMenu(self.service, self)
        self._calnet_authn_window_opened_signal = self.menu.connect('calnet-authn-window-opened',
                                                                    self._on_calnet_authn_window_opened)

    def icon_path(self, icon_filename="tag_icon.png"):
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', icon_filename)
        logger.debug("StatusIcon looking for icon at: %s" % icon_path)
        return icon_path

    def show(self):
        self.icon = Gtk.StatusIcon()
        self.icon.connect("popup-menu", self.on_popup_menu)
        self.icon.set_from_file(self.icon_path())
        self.icon.set_title("AirBears Supplicant")

    def on_popup_menu(self, icon, button, time):
        self.emit('popup-menu')
        self.menu.popup(button, time)

    def _on_calnet_authn_window_opened(self, menu, window):
        self.emit('calnet-authn-window-opened', window)
 

class StatusMenu(GObject.GObject):
    __gsignals__ = {
        'calnet-authn-window-opened': (GObject.SIGNAL_RUN_FIRST,
                                      None,
                                      (CalNetAuthnDialog,)),
    }

    def __init__(self, service, status_icon):
        super(StatusMenu, self).__init__()
        self.menu = Gtk.Menu()
        self.service = service
        self.status_icon = status_icon

        quit_item = Gtk.MenuItem()
        quit_item.set_label("Quit")
        quit_item.connect("activate", self.on_quit_item_activate)
        
        
        credentials_item = Gtk.MenuItem()
        credentials_item.set_label("Update CalNet credentials")
        credentials_item.connect("activate", self.on_credentials_item_activate)
        
        self.menu.append(credentials_item)
        self.menu.append(quit_item)
        
        self.menu.show_all()

    def popup(self, button, time):
        def pos(menu, icon):
            return (Gtk.StatusIcon.position_menu(menu, icon))
        self.menu.popup(None, None, pos, self.status_icon.icon, button, time)
    
    def on_quit_item_activate(self, *args):
        self.status_icon.service.stop()
    
    def on_credentials_item_activate(self, *args):
        credentials_window = CalNetAuthnDialog(self.service.credential_store)
        credentials_window.show()
        self.emit('calnet-authn-window-opened', credentials_window)


if __name__ == "__main__":
    icon = StatusIcon()

    Gtk.main()
