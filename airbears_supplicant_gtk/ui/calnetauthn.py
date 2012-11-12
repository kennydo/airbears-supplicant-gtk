import logging
import os

from airbears_supplicant_gtk import log
from gi.repository import Gtk

logger = logging.getLogger(__name__)

class CalNetAuthnDialog:
    def __init__(self, credential_store):
        self.credential_store = credential_store

        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.glade_file_path())

        handlers = {
            "on_window_delete_event": Gtk.main_quit,
            "on_clear_button_pressed": self.on_clear_button_pressed,
            "on_save_button_pressed": self.on_save_button_pressed,
        }
        self.builder.connect_signals(handlers)

        self.username_entry = self.builder.get_object("username_entry")
        self.password_entry = self.builder.get_object("password_entry")

    def glade_file_path(self):
        return os.path.join(os.path.dirname(__file__), 'assets', 'calnetauthn.glade')

    def show(self):
        window = self.builder.get_object("window")
        window.show_all()

    def on_clear_button_pressed(self, button):
        logger.debug("Pressed the Clear button")
        self.username_entry.set_text("")
        self.password_entry.set_text("")

    def on_save_button_pressed(self, button):
        username = self.username_entry.get_text()
        password = self.password_entry.get_text()

        logger.debug("Save buton pressed with username %s" % username)

        self.credential_store.save(username, password)

if __name__ == "__main__":
    from airbears_supplicant_gtk.calnet.credentialstore import TestCredentialStore

    cred_store = TestCredentialStore()

    test_window = CalNetAuthnDialog(cred_store)
    test_window.show()

    Gtk.main()
