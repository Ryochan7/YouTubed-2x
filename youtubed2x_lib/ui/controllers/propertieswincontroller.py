import sys
from youtubed2x_lib.videoitem import VideoItem
from youtubed2x_lib.other import set_proxy, remove_proxy


class PropertiesWinController (object):
    def __init__ (self, ui, app_settings, video_queue):
        self.ui = ui
        self.app_settings = app_settings
        self.video_queue = video_queue

        dic = {"on_ok_button_clicked": self.apply_changes, "on_properties_win_delete_event": self.cancel, "on_close_button_clicked": self.cancel, "on_use_proxy_checkbutton_toggled": self.toggle_proxy}
        self.ui.window.signal_autoconnect (dic)


    def toggle_proxy (self, widget):
        if widget.get_active ():
            self.ui.proxy_server_text.set_sensitive (True)
            self.ui.proxy_port_spin.set_sensitive (True)
            self.ui.proxy_server_label.set_sensitive (True)
            self.ui.proxy_port_label.set_sensitive (True)

        else:
            self.ui.proxy_server_text.set_sensitive (False)
            self.ui.proxy_port_spin.set_sensitive (False)
            self.ui.proxy_server_label.set_sensitive (False)
            self.ui.proxy_port_label.set_sensitive (False)



    def apply_changes (self, widget):
        temp = self.ui.ffmpeg_chooser.get_filename ()
        if temp:
            self.app_settings.ffmpeg_location = temp
            VideoItem.setFFmpegLocation (self.app_settings.ffmpeg_location)
        self.app_settings.sitedirs = self.ui.sitedirs_check.get_active ()

        temp_server = self.ui.proxy_server_text.get_text ()
        temp_port = self.ui.proxy_port_spin.get_value_as_int ()
        old_server = self.app_settings.proxy_server
        old_port = self.app_settings.proxy_port

        if temp_server != self.app_settings.proxy_server or temp_port != self.app_settings.proxy_port:
            self.app_settings.proxy_server = temp_server
            self.app_settings.proxy_port = temp_port

        if self.ui.use_proxy_checkbutton.get_active ():
            self.app_settings.use_proxy = True
            if temp_server and temp_port:
                try:
                    set_proxy (temp_server, temp_port)
                except Exception as exception:
                    print >> sys.stderr, "%s. Disabling proxy." % exception
                    self.app_settings.use_proxy = False
                    self.ui.use_proxy_checkbutton.set_active (self.app_settings.use_proxy)

        elif self.app_settings.use_proxy:
            self.app_settings.use_proxy = False
            remove_proxy ()

        temp = self.ui.process_limit_spin.get_value_as_int ()
        if temp != self.app_settings.process_limit:
            self.app_settings.process_limit = temp
            self.video_queue.alter_sem (self.app_settings.process_limit)

        #self.app_settings.download_speed_limit = self.ui.dlspeedlimit_spin.get_value_as_int ()
        #self.video_queue.setDownloadLimit (self.app_settings.download_speed_limit)

        self.ui.main_window.hide ()


    def show (self):
        self.ui.show ()


    def cancel (self, widget, data=None):
        self.ui.setWidgetAttrib (self.app_settings)
        self.ui.main_window.hide ()
        return True


    def hide (self, widget, data=None):
        self.ui.main_window.hide ()
        return True

