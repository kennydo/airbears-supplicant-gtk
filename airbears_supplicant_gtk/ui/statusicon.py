import logging
import os

from airbears_supplicant_gtk import log
from gi.repository import Gtk

logger = logging.getLogger(__name__)

class StatusIcon:
    def __init__(self):
        self.icon = Gtk.StatusIcon()
        self.icon.connect("popup-menu", self.on_popup_menu)
        self.menu = StatusMenu(self)
        self.icon.set_from_file(self.icon_path())
        self.icon.set_title("AirBears Supplicant")
    
    def icon_path(self, icon_filename="tag_icon.png"):
        return os.path.join(os.path.dirname(__file__), 'assets', icon_filename)

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
        quit_item.connect("activate", Gtk.main_quit)

        self.menu.append(quit_item)
        self.menu.show_all()

    def popup(self, button, time):
        def pos(menu, icon):
            return (Gtk.StatusIcon.position_menu(menu, icon))
        self.menu.popup(None, None, pos, self.status_icon.icon, button, time)


if __name__ == "__main__":
    icon = StatusIcon()

    Gtk.main()
