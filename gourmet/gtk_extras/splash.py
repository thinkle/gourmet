from pathlib import Path

from gettext import gettext as _
from gi.repository import Gtk

from gourmet.gglobals import imagedir


class Splash:

    def __init__(self):
        window = Gtk.Window()
        window.set_property('decorated', False)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_title(_('Gourmet Recipe Manager starting up...'))
        window.set_default_size(200, 200)

        path = Path(imagedir) / 'splash.png'
        image = Gtk.Image.new_from_file(str(path))
        window.add(image)

        label = Gtk.Label(label=_("Starting Gourmet..."))
        label.set_property('xalign', 0.5)
        label.set_property('yalign', 1)
        label.set_justify(Gtk.Justification.CENTER)
        label.set_line_wrap(True)
        label.show()
        window.add(label)

        self.label = label
        self.window = window

    def destroy(self):
        self.window.destroy()

    def show(self):
        # Show the splash screen without causing startup notification.
        Gtk.Window.set_auto_startup_notification(False)
        self.window.show_all()
        Gtk.Window.set_auto_startup_notification(True)

        # Ensure the splash is completely drawn before moving on
        while Gtk.events_pending():
            Gtk.main_iteration()

    def hide(self):
        self.window.hide()


if __name__ == '__main__':
    splash = Splash()
    splash.show()
    Gtk.main()
