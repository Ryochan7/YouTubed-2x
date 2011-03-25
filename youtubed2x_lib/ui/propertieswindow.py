import gtk
import gobject
import logging
from youtubed2x_lib.videoitem import VideoItem
from youtubed2x_lib.other import set_proxy, remove_proxy


class PropertiesWindow (gobject.GObject):
    __gsignals__ = {
        "settings_updated": (gobject.SIGNAL_RUN_FIRST, None, (object,)),
    }

    def __init__ (self, glade_file, app_settings):
        super (self.__class__, self).__init__ ()
        self._log = logging.getLogger ("{0}.{1}".format (__name__,
            self.__class__.__name__))

        self.gladefile = glade_file
        self.window = gtk.glade.XML (self.gladefile, "properties_win")
        self.main_window = self.window.get_widget ("properties_win")
        self.ffmpeg_chooser = self.window.get_widget ("ffmpeg_chooser")
        self.sitedirs_check = self.window.get_widget ("sitedirs")
        self.process_limit_spin = self.window.get_widget ("process_limit_spinbutton")
        #self.dlspeedlimit_spin = self.window.get_widget ("dlspeedlimit_spinbutton")

        self.proxy_server_text = self.window.get_widget ("proxy_server_text")
        self.proxy_port_spin = self.window.get_widget ("proxy_port_spin")

        self.proxy_server_label = self.window.get_widget ("proxy_server_label")
        self.proxy_port_label = self.window.get_widget ("proxy_port_label")
        self.use_proxy_checkbutton = self.window.get_widget ("use_proxy_checkbutton")

        self.app_settings = app_settings

        connect_dict = {
            "on_ok_button_clicked": self.apply_changes,
            "on_properties_win_delete_event": self.cancel,
            "on_close_button_clicked": self.cancel,
            "on_use_proxy_checkbutton_toggled": self.toggle_proxy,
        }
        self.window.signal_autoconnect (connect_dict)
        self.set_widget_attrib (app_settings)

    def set_widget_attrib (self, app_settings):
        if app_settings.ffmpeg_location != self.ffmpeg_chooser.get_filename ():
            self.ffmpeg_chooser.set_filename (app_settings.ffmpeg_location)
        self.sitedirs_check.set_active (app_settings.sitedirs)

        self.use_proxy_checkbutton.set_active (app_settings.use_proxy)
        if app_settings.use_proxy:
            self.proxy_server_text.set_sensitive (True)
            self.proxy_port_spin.set_sensitive (True)
            self.proxy_server_label.set_sensitive (True)
            self.proxy_port_label.set_sensitive (True)

        self.proxy_server_text.set_text (app_settings.proxy_server)
        self.proxy_port_spin.set_value (app_settings.proxy_port)
        self.process_limit_spin.set_value (app_settings.process_limit)
        #self.dlspeedlimit_spin.set_value (app_settings.download_speed_limit)

    def toggle_proxy (self, widget):
        if widget.get_active ():
            self.proxy_server_text.set_sensitive (True)
            self.proxy_port_spin.set_sensitive (True)
            self.proxy_server_label.set_sensitive (True)
            self.proxy_port_label.set_sensitive (True)

        else:
            self.proxy_server_text.set_sensitive (False)
            self.proxy_port_spin.set_sensitive (False)
            self.proxy_server_label.set_sensitive (False)
            self.proxy_port_label.set_sensitive (False)

    def apply_changes (self, widget):
        temp = self.ffmpeg_chooser.get_filename ()
        if temp:
            self.app_settings.ffmpeg_location = temp
            VideoItem.setFFmpegLocation (self.app_settings.ffmpeg_location)
        self.app_settings.sitedirs = self.sitedirs_check.get_active ()

        temp_server = self.proxy_server_text.get_text ()
        temp_port = self.proxy_port_spin.get_value_as_int ()

        if temp_server != self.app_settings.proxy_server or temp_port != self.app_settings.proxy_port:
            self.app_settings.proxy_server = temp_server
            self.app_settings.proxy_port = temp_port

        if self.use_proxy_checkbutton.get_active ():
            self.app_settings.use_proxy = True
            if temp_server and temp_port:
                try:
                    set_proxy (temp_server, temp_port)
                except Exception:
                    self._log.exception ("Disabling proxy")
                    self.app_settings.use_proxy = False
                    self.use_proxy_checkbutton.set_active (self.app_settings.use_proxy)

        elif self.app_settings.use_proxy:
            self.app_settings.use_proxy = False
            remove_proxy ()

        temp = self.process_limit_spin.get_value_as_int ()
        if temp != self.app_settings.process_limit:
            self.app_settings.process_limit = temp

        self.emit ("settings_updated", self.app_settings)
        self.main_window.hide ()

    def cancel (self, widget, data=None):
        self.set_widget_attrib(self.app_settings)
        self.main_window.hide ()
        return True

    def show (self):
        self.main_window.show ()

    def hide (self):
        self.main_window.hide ()
        return True
