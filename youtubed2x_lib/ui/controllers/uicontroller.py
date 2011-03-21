import os
import gtk
import webbrowser
import pango
import subprocess
from youtubed2x_lib.videoitem import VideoItem
from youtubed2x_lib.other import WINDOWS
from youtubed2x_lib.ui.models.videodownloadthread import VideoDownloadThread
from youtubed2x_lib.ui.views.videoitemmenu import VideoItemMenu
from videoitemmenucontroller import VideoItemMenuController


class UiController (object):
    GTK_RIGHT_CLICK_BUTTON = 3

    def __init__ (self, ui, app_settings, video_queue, parser_manager, prop_cont):
        self.ui = ui
        self.app_settings = app_settings
        self.video_queue = video_queue
        self.parser_manager = parser_manager
        self.prop_cont = prop_cont
        self._treeview_rightclick_event = None

        gtk.about_dialog_set_url_hook (self.open_site)
        self.ui.treeview1.connect ("button-press-event", self.treeview_right)
        self.ui.treeview1.connect ("cursor-changed", self.treeview_right2)

        dic = {"on_window1_delete_event": self.quit_app, "on_quit1_activate": self.quit_app, "on_preferences2_activate": self.show_preferences,
               "on_about1_activate": self.show_about_window, "on_aboutdialog1_response": self.hide_about_window, "on_aboutdialog1_delete_event": self.keep_about_window,
               "on_sites_activate": self.show_sites_window, "on_close_sites_clicked": self.hide_sites_window, "on_sites_dialog_delete_event": self.keep_sites_window,
               "on_sites_dialog_response": self.hide_sites_window, "on_checkbutton1_toggled": self.transcode_check, "on_checkbutton2_toggled": self.overwrite_check,
               "on_checkbutton3_toggled": self.keep_flvs_check, "on_auto_download_check_toggled": self.change_auto_download,
               "on_video_bitrate_changed": self.change_video_bitrate, "on_resolution_combobox_changed": self.resolution_change, "on_combobox1_changed": self.change_format,
               "on_toolbutton4_clicked": self.move_up, "on_toolbutton5_clicked": self.move_down, "on_treeview1_cursor_changed": self.select_item,
               "on_toolbutton3_clicked": self.clear_complete, "on_openfolderbutton_clicked": self.open_video_folder,
               "on_filechooserbutton1_current_folder_changed": self.change_video_folder, "on_pause_toolbutton_clicked": self.pause_download,
               "on_toolbutton2_clicked": self.remove, "on_button1_clicked": self.add_queue, "on_toolbutton1_clicked": self.startProcess,
               "on_entry1_activate": self.add_queue, "on_audio_bitrate_changed": self.change_audio_bitrate,
              }
        self.ui.window.signal_autoconnect (dic)

        self.video_queue.connect ("unblock-ui", self.unlock_partial_ui)
        self.video_queue.connect ("block-ui", self.block_partial_ui)
        self.video_queue.connect ("speed_progress_update", self.ui.update_speed_statusbar)
        self.video_queue.connect ("progress_update", self.ui.update_statusbar)

        # Populate sites_textview with hooks to controller methods when moving over text
        # and clicking on links
        self.ui.sites_textview.connect ("motion-notify-event", self.sites_textview_motion_notify_event)

        parser_list = self.parser_manager.get_official_parsers ()
        name_list = []
        tmp_dic = {}
        for parser in parser_list:
            name_list.append (parser.getType ())
            tmp_dic[parser.getType ()] = parser
        name_list.sort ()

        textbuffer = self.ui.sites_textview.get_buffer ()
        textbuffer.insert (textbuffer.get_end_iter (), "Supported Sites\n-----------------------\n\n")

        for i, name in enumerate (name_list):
            newtag = textbuffer.create_tag ("url-tag%i" % i)
            newtag.set_property ("underline", pango.UNDERLINE_SINGLE)
            newtag.set_property ("foreground", "#2750FF")
            newtag.connect ("event", self.sites_textview_link_button_press_event)
            newtag.set_data ("link", tmp_dic[name].domain_str)

            parser_version = tmp_dic[name].version
            textbuffer.insert (textbuffer.get_end_iter (), "* ")
            textbuffer.insert_with_tags_by_name (textbuffer.get_end_iter (), name, newtag.get_property ("name"))
#            sites_str += "* %s    (%s/%s/%s)\n" % (name, parser_version.month, parser_version.day, parser_version.year)
            textbuffer.insert (textbuffer.get_end_iter (), "   (%s/%s/%s)\n" % (parser_version.month, parser_version.day, parser_version.year))


    def change_video_folder (self, widget):
        self.app_settings.output_dir = widget.get_filename ()

    def quit_app (self, widget, data=None):
        if self.video_queue.is_queue_active ():
            self.ui.show_caution_window ()
            return True

        gtk.main_quit ()

    def show_preferences (self, widget):
        self.prop_cont.show ()

    def show_about_window (self, widget):
        """Display non-modal about window"""
        self.ui.show_about_window ()

    def hide_about_window (self, widget, data):
        """Hide non-modal about window"""
        self.ui.hide_about_window ()

    def keep_about_window (self, widget, data):
        """Keep about window from being destroyed when close button
        is clicked. Window will be hidden later from the response handler"""
        return True

    def show_sites_window (self, widget):
        self.ui.sites_window.show ()

    def hide_sites_window (self, widget, data=None):
        """Hide non-modal sites dialog window"""
        self.ui.sites_window.hide ()

    def keep_sites_window (self, widget, data):
        """
        Keep supported sites window from being destroyed
        when close button is clicked. Window will be hidden later
        from the response handler
        """
        return True

    def open_site (self, widget, url):
        webbrowser.open (url)

    def transcode_check (self, widget):
        self.app_settings.transcode = not self.app_settings.transcode
        if not self.app_settings.transcode:
            self.ui.checkbutton3.set_active (True)
            self.ui.checkbutton3.set_sensitive (False)
        else:
            self.ui.checkbutton3.set_sensitive (True)

    def overwrite_check (self, widget):
        self.app_settings.overwrite = not self.app_settings.overwrite

    def keep_flvs_check (self, widget):
        self.app_settings.keep_flv_files = not self.app_settings.keep_flv_files

    def change_auto_download (self, widget):
        self.app_settings.auto_download = not self.app_settings.auto_download

    def change_video_bitrate (self, widget):
        index = widget.get_active ()
        self.app_settings.vbitrate = self.ui._video_bitrate_options[index]

    def change_audio_bitrate (self, widget):
        self.app_settings.abitrate = (widget.get_active ()*32)+32

    def resolution_change (self, widget):
        self.app_settings.output_res = widget.get_active ()


    def change_format (self, widget):
        format = widget.get_active ()
        if format in VideoItem.VIDEO_FORMATS:
            self.app_settings.format = format
            self.ui.resolution_combobox.set_sensitive (True)
            self.ui.video_bitrate_combobox.set_sensitive (True)
            self.ui.audio_bitrate_combobox.set_sensitive (True)
        else:
            self.app_settings.format = format
            self.ui.resolution_combobox.set_sensitive (False)
            self.ui.video_bitrate_combobox.set_sensitive (False)
            self.ui.audio_bitrate_combobox.set_sensitive (True)

    def move_up (self, widget):
        """Move Up"""
        tree = self.ui.treeview1.get_selection ()
        model, selection = tree.get_selected ()
        url = model.get_value (selection, 0)
        thread_id = self.video_queue.getThreadId (url)

        path = model.get_path (selection)
        index = path[0]
        previous = model.get_iter ((index-1),)
        dude_url = model.get_value (previous, 0)
        prev_thread_id = self.video_queue.getThreadId (dude_url)

        self.video_queue.swap_items (thread_id, prev_thread_id)
        tree.select_path (index-1)
        self.select_item ()

    def move_down (self, widget):
        """Move Down"""
        tree = self.ui.treeview1.get_selection ()
        model, selection = tree.get_selected ()
        url = model.get_value (selection, 0)
        thread_id = self.video_queue.getThreadId (url)

        path = model.get_path (selection)
        index = path[0]
        previous = model.get_iter ((index+1),)
        dude_url = model.get_value (previous, 0)
        prev_thread_id = self.video_queue.getThreadId (dude_url)

        self.video_queue.swap_items (thread_id, prev_thread_id)
        tree.select_path (index+1)
        self.select_item ()

    def select_item (self, widget=None):
        tree = self.ui.treeview1.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        url = model.get_value (selection, 0)
        thread_id = self.video_queue.getThreadId (url)
        thread = self.video_queue.getVideoThread (thread_id)

        if thread and thread.isAlive () and thread.status == thread.__class__.WAITING:
            self.ui.toolbutton1.set_sensitive (True)
            self.ui.toolbutton2.set_sensitive (True)
            self.ui.toolbutton2.set_label ("Remove")
            self.ui.pause_toolbutton.set_sensitive (False)
            self.ui.pause_toolbutton.set_label ("Pause")
        elif thread and thread.isAlive () and thread.status == thread.__class__.READY:
            self.ui.toolbutton1.set_sensitive (False)
            self.ui.toolbutton2.set_sensitive (True)
            self.ui.toolbutton2.set_label ("Cancel")
            if thread._downloader:
                self.ui.pause_toolbutton.set_sensitive (True)
            else:
                self.ui.pause_toolbutton.set_sensitive (False)
            self.ui.pause_toolbutton.set_label ("Pause")
        elif thread and thread.isAlive () and thread.status == thread.__class__.PARSING:
            self.ui.toolbutton1.set_sensitive (False)
            self.ui.toolbutton2.set_sensitive (False)
            self.ui.toolbutton2.set_label ("Remove")
            self.ui.pause_toolbutton.set_sensitive (False)
            self.ui.pause_toolbutton.set_label ("Pause")
        # Handle case of a cancelled download waiting to stop
        elif thread and thread.isAlive () and thread.status == thread.__class__.CANCELING:
            self.ui.toolbutton1.set_sensitive (False)
            self.ui.toolbutton2.set_sensitive (False)
            self.ui.toolbutton2.set_label ("Wait")
            self.ui.pause_toolbutton.set_sensitive (False)
            self.ui.pause_toolbutton.set_label ("Pause")
        elif thread and thread.isAlive () and thread.status == thread.__class__.PAUSED:
            self.ui.toolbutton1.set_sensitive (False)
            self.ui.toolbutton2.set_sensitive (True)
            self.ui.toolbutton2.set_label ("Cancel")
            self.ui.pause_toolbutton.set_sensitive (True)
            self.ui.pause_toolbutton.set_label ("Resume")
        elif thread:
            self.ui.toolbutton1.set_sensitive (False)
            self.ui.toolbutton2.set_sensitive (True)
            self.ui.toolbutton2.set_label ("Remove")
            self.ui.pause_toolbutton.set_sensitive (False)
            self.ui.pause_toolbutton.set_label ("Pause")

        path = model.get_path (selection)
        index = path[0]

        queue_length = self.video_queue.queue_length ()

        if queue_length >= 2:
            self.ui.toolbutton3.set_sensitive (True)
            if index == queue_length-1:
                self.ui.toolbutton4.set_sensitive (True)
                self.ui.toolbutton5.set_sensitive (False)
            elif index == 0:
                self.ui.toolbutton4.set_sensitive (False)
                self.ui.toolbutton5.set_sensitive (True)
            else:
                self.ui.toolbutton4.set_sensitive (True)
                self.ui.toolbutton5.set_sensitive (True)
        elif queue_length > 0:
            self.ui.toolbutton3.set_sensitive (True)

        return True

    def block_ui (self, widget=None):
        self.block_partial_ui ()
        self.ui.entry1.set_sensitive (False)
        self.ui.button1.set_sensitive (False)

    def block_partial_ui (self, widget=None):
        self.ui.toolbutton2.set_label ("Remove")
        self.ui.toolbutton1.set_sensitive (False)
        self.ui.toolbutton2.set_sensitive (False)
        self.ui.toolbutton3.set_sensitive (False)
        self.ui.toolbutton4.set_sensitive (False)
        self.ui.toolbutton5.set_sensitive (False)
        tree = self.ui.treeview1.get_selection ()
        model, selection = tree.get_selected ()
        if selection:
            index = model.get_path (selection)[0]
            tree.select_path (index)
            self.select_item ()

    def unlock_partial_ui (self, widget=None):
        self.ui.entry1.set_sensitive (True)
        self.ui.button1.set_sensitive (True)
        self.ui.entry1.set_text ("")
        tree = self.ui.treeview1.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            tree.select_path (self.video_queue.queue_length ()-1,)
        else:
            index = model.get_path (selection)[0]
            tree.select_path (index)

        self.select_item ()

    def clear_complete (self, widget):
        self.video_queue.clear_complete ()
        self.block_partial_ui ()

    def open_video_folder (self, widget):
        folder = self.ui.folder_chooser.get_filename ()
        if WINDOWS:
            subprocess.Popen (["start", "", folder], shell=True)
        else:
            subprocess.Popen (["xdg-open", folder])

    def pause_download (self, widget):
        tree = self.ui.treeview1.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        url = model.get_value (selection, 0)
        thread_id = self.video_queue.getThreadId (url)
        thread = self.video_queue.getVideoThread (thread_id)
        if thread.status == thread.__class__.READY and thread._downloader:
            thread.pause ()
        elif thread.status == thread.__class__.PAUSED:
            thread.setReady ()

        self.select_item ()

    def remove (self, widget):
        tree = self.ui.treeview1.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        url = model.get_value (selection, 0)
        thread_id = self.video_queue.getThreadId (url)
        thread = self.video_queue.getVideoThread (thread_id)

        if thread and thread.isAlive () and thread.status == thread.WAITING:
            self.video_queue.removeDownload (thread_id)
        elif thread and thread.isAlive () and thread.status == thread.__class__.READY:
            self.video_queue.finishDownload (thread_id)
        # Handle case of a cancelled download waiting to stop
        elif thread and thread.isAlive () and thread.status == thread.__class__.CANCELING:
            print "Already cancelled. Waiting. Don't do anything"
            return
        elif thread and thread.isAlive () and thread.status == thread.__class__.PAUSED:
            self.video_queue.finishDownload (thread_id)
        elif thread:
            self.video_queue.removeDownload (thread_id)

        self.block_partial_ui ()
        return True

    def treeview_right2 (self, widget):
        tree = widget.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        if self._treeview_rightclick_event != None:
            event = self._treeview_rightclick_event
            url = model.get_value (selection, 0)
            thread_id = self.video_queue.getThreadId (url)
            thread = self.video_queue.getVideoThread (thread_id)
            popup = VideoItemMenu (self.ui.gladefile, self.ui.treeview1)
            popup_cont = VideoItemMenuController (popup, self.video_queue)

            # Move this logic to VideoItemMenuController class
            if thread.status == thread.__class__.DONE:
                video_file_input = thread.video.flv_file
                video_file_output = thread.video.avi_file
                video_input_exists = os.path.exists (video_file_input)
                video_output_exists = os.path.exists (video_file_output)

                if video_input_exists:
                    popup_cont.get_children ()[0].set_sensitive (True)
                else:
                    popup_cont.get_children ()[0].set_sensitive (False)

                if video_output_exists:
                    popup_cont.get_children ()[1].set_sensitive (True)
                else:
                    popup_cont.get_children ()[1].set_sensitive (False)

                if video_input_exists or video_output_exists:
                    popup_cont.get_children ()[2].set_sensitive (True)
                else:
                    popup_cont.get_children ()[2].set_sensitive (False)
            else:
                popup_cont.get_children ()[0].set_sensitive (False)
                popup_cont.get_children ()[1].set_sensitive (False)
                popup_cont.get_children ()[2].set_sensitive (False)

            popup_cont.popup (None, None, None, event.button, event.time)

        self._treeview_rightclick_event = None

    def treeview_right (self, widget, event):
        # Check if a right click was performed on a video item.
        # The treeview_right2 will be called shortly after this
        # due to cursor-changed signal
        if event.button == self.__class__.GTK_RIGHT_CLICK_BUTTON:
            self._treeview_rightclick_event = event

    def add_queue (self, widget):
        newtext = self.ui.entry1.get_text ()
        if not newtext:
            return

        youtube_video = self.parser_manager.validateURL (newtext)
        if not youtube_video:
            self.ui.update_statusbar ("An invalid url was passed. Try again.", 2500)
            self.ui.entry1.set_text ('')
            return
        self.block_ui ()
        VideoDownloadThread (self.video_queue, self.app_settings, youtube_video).start ()

    def startProcess (self, widget):
        tree = self.ui.treeview1.get_selection ()
        model, selection = tree.get_selected ()

        url = model.get_value (selection, 0)
        thread_id = self.video_queue.getThreadId (url)

        if thread_id is not None:
            self.video_queue.startDownload (thread_id)

        self.select_item ()
        return True

    def sites_textview_link_button_press_event (self, tag, widget, event, gtkiter):
        if event.type == gtk.gdk.BUTTON_PRESS:
            link = tag.get_data ("link")
            webbrowser.open (link)

        return

    def sites_textview_motion_notify_event (self, widget, event):
        (x, y, state) = event.window.get_pointer ()
        (newx, newy) = widget.window_to_buffer_coords (widget.get_window_type (event.window), x, y)
        tag_list = widget.get_iter_at_location (newx, newy).get_tags ()
        #widget.window.get_pointer()
        cursor = gtk.gdk.Cursor (gtk.gdk.LEFT_PTR)

        for tag in tag_list:
            if tag.get_data ("link"):
                cursor = gtk.gdk.Cursor (gtk.gdk.HAND2)
                break

        event.window.set_cursor (cursor)

