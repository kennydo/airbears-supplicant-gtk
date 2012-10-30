from gi.repository import Gtk

class CalNetAuthnDialog:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("glade/calnetauthn.glade")

        handlers = {
            "on_window_destroy": Gtk.main_quit,
            "on_clear_button_pressed": self.on_clear_button_pressed,

        }
        self.builder.connect_signals(handlers)

    def show(self):
        window = self.builder.get_object("window")
        window.show_all()

    def on_clear_button_pressed(self, button):
        username_entry = self.builder.get_object("username_entry")
        password_entry = self.builder.get_object("password_entry")

        username_entry.set_text("")
        password_entry.set_text("")


if __name__ == "__main__":
    test_window = CalNetAuthnDialog()
    test_window.show()

    Gtk.main()
