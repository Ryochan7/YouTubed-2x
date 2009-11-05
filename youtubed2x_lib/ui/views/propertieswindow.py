import gtk.glade

class PropertiesWindow (object):
    def __init__ (self, glade_file, app_settings):
        self.gladefile = glade_file
        self.window = gtk.glade.XML (self.gladefile, "properties_win")
        self.main_window = self.window.get_widget ("properties_win")
        self.ffmpeg_chooser = self.window.get_widget ("ffmpeg_chooser")
        self.sitedirs_check = self.window.get_widget ("sitedirs")
        self.process_limit_spin = self.window.get_widget ("process_limit_spinbutton")

        self.proxy_server_text = self.window.get_widget ("proxy_server_text")
        self.proxy_port_spin = self.window.get_widget ("proxy_port_spin")

        self.proxy_server_label = self.window.get_widget ("proxy_server_label")
        self.proxy_port_label = self.window.get_widget ("proxy_port_label")
        self.use_proxy_checkbutton = self.window.get_widget ("use_proxy_checkbutton")

        self.setWidgetAttrib (app_settings)


    def setWidgetAttrib (self, app_settings):
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


    def show (self):
        self.main_window.show ()


    def hide (self):
        self.main_window.hide ()
        return True


