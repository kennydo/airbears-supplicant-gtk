import logging
import os

from airbears_supplicant_gtk import log
from airbears_supplicant_gtk.ui import CalNetAuthnDialog
from gi.repository import Gtk

logger = logging.getLogger(__name__)

class StatusIcon:
    def __init__(self, service):
        self.icon = Gtk.StatusIcon()
        self.icon.connect("popup-menu", self.on_popup_menu)
        self.menu = StatusMenu(self)
        self.icon.set_from_file(self.icon_path())
        self.icon.set_title("AirBears Supplicant")
        self.service = service
    
    def icon_path(self, icon_filename="tag_icon.png"):
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', icon_filename)
        logger.debug("StatusIcon looking for icon at: %s" % icon_path)
        return icon_path

    def show(self):
        self.icon.show_all()

    def on_popup_menu(self, icon, button, time):
        self.menu.popup(button, time)

class StatusMenu:
    def __init__(self, status_icon):
        self.menu = Gtk.Menu()
        self.status_icon = status_icon

        quit_item = Gtk.MenuItem()
        quit_item.set_label("Quit")
        quit_item.connect("activate", self.on_quit_item_activate)
        
        separator = Gtk.SeparatorMenuItem()
        
        credentials_item = Gtk.MenuItem()
        credentials_item.set_label("Update CalNet credentials")
        credentials_item.connect("activate", self.on_credentials_item_activate)
        
        self.menu.append(credentials_item)
        self.menu.append(separator)
        self.menu.append(quit_item)
        
        self.menu.show_all()

    def popup(self, button, time):
        def pos(menu, icon):
            return (Gtk.StatusIcon.position_menu(menu, icon))
        self.menu.popup(None, None, pos, self.status_icon.icon, button, time)
    
    def on_quit_item_activate(self, *args):
        self.status_icon.service.stop()
    
    def on_credentials_item_activate(self, *args):
        credentials_window = CalNetAuthnDialog(self.status_icon.service.credential_store)
        credentials_window.show()


if __name__ == "__main__":
    icon = StatusIcon()

    Gtk.main()
