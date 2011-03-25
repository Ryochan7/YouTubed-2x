import logging
import os
import subprocess
import webbrowser
import gtk
import gobject
import pango

from youtubed2x_lib.ui.videoitemmenu import VideoItemMenu
from youtubed2x_lib.videoitem import VideoItem
from youtubed2x_lib.other import APP_NAME, VERSION, WINDOWS

class YouTubeDownloader (object):
    GTK_RIGHT_CLICK_BUTTON = 3

    def __init__ (self, gladefile, app_settings, thread_manager,
        parser_manager, prop_cont):
        self._video_bitrate_options = [384, 512, 768, 1024, 1536, 2000]
        self._log = logging.getLogger ("{0}.{1}".format (__name__,
            self.__class__.__name__))

        self.gladefile = gladefile
        self.window = gtk.glade.XML (self.gladefile)
        self.main_window = self.window.get_widget ('window1')
        self.about_window = self.window.get_widget ('aboutdialog1')
        self.about_window.set_comments ('Version %s' % VERSION)
        self.about_window.set_name (APP_NAME)
        self.mainbar1 = self.window.get_widget ('menubar1')
        self.entry1 = self.window.get_widget ('entry1')
        self.button1 = self.window.get_widget ('button1')
        self.button2 = self.window.get_widget ('button2')
        self.toolbutton1 = self.window.get_widget ('toolbutton1')
        self.toolbutton2 = self.window.get_widget ('toolbutton2')
        self.toolbutton3 = self.window.get_widget ('toolbutton3')
        self.toolbutton4 = self.window.get_widget ('toolbutton4')
        self.toolbutton5 = self.window.get_widget ('toolbutton5')
        self.video_bitrate_combobox = self.window.get_widget (
            "video_bitrate_combobox")
        self.audio_bitrate_combobox = self.window.get_widget (
            "audio_bitrate_combobox")

        bitrate_list = gtk.ListStore (gobject.TYPE_INT)
        self.video_bitrate_combobox.set_model (bitrate_list)
        for bitrate in self._video_bitrate_options:
            bitrate_list.append ([bitrate])
        if app_settings.vbitrate in self._video_bitrate_options:
            self.video_bitrate_combobox.set_active (
                self._video_bitrate_options.index (app_settings.vbitrate))
        else:
            self.video_bitrate_combobox.set_active (0)
            app_settings.vbitrate = self._video_bitrate_options[0]

        bitrate_list = gtk.ListStore (gobject.TYPE_INT)
        self.audio_bitrate_combobox.set_model (bitrate_list)
        for n in range (1,13):
            bitrate_list.append ([n*32])
        self.audio_bitrate_combobox.set_active ((app_settings.abitrate / 32)-1)

        self.combobox = self.window.get_widget ('combobox1')
        self.combobox.set_active (app_settings.format)
        self.checkbutton1 = self.window.get_widget ('checkbutton1')
        self.checkbutton2 = self.window.get_widget ('checkbutton2')
        self.checkbutton3 = self.window.get_widget ('checkbutton3')
        self.auto_download_check = self.window.get_widget (
            "auto_download_check")
        self.resolution_combobox = self.window.get_widget (
            "resolution_combobox")
        self.resolution_combobox.set_active (app_settings.output_res)

        if app_settings.format in VideoItem.VIDEO_FORMATS:
            self.resolution_combobox.set_sensitive (True)
            self.video_bitrate_combobox.set_sensitive (True)
            self.audio_bitrate_combobox.set_sensitive (True)
        else:
            self.resolution_combobox.set_sensitive (False)
            self.video_bitrate_combobox.set_sensitive (False)
            self.audio_bitrate_combobox.set_sensitive (True)

        if not app_settings.transcode:
            if not app_settings.keep_flv_files:
                app_settings.keep_flv_files = True
            self.checkbutton3.set_active (True)
            self.checkbutton3.set_sensitive (False)
            self.checkbutton1.set_active (False)
        if app_settings.overwrite:
            self.checkbutton2.set_active (True)
        if not app_settings.keep_flv_files:
            self.checkbutton3.set_active (False)

        self.auto_download_check.set_active (app_settings.auto_download)

        self.treeview1 = self.window.get_widget ("treeview1")
        self.column1 = gtk.TreeViewColumn ("URL", gtk.CellRendererText(),
            text=0)
        self.column1.set_sizing (gtk.TREE_VIEW_COLUMN_FIXED)
#        self.column1.set_min_width (230)
        self.column1.set_resizable (True)
        self.column1.set_expand (True)
        self.column2 = gtk.TreeViewColumn ("Name")
        cell = gtk.CellRendererPixbuf ()
        self.column2.pack_start (cell, False)
        #self.column2.add_attribute (cell, "pixbuf", 6)
        cell2 = gtk.CellRendererText ()
        self.column2.pack_start (cell2, False)
        self.column2.set_cell_data_func (cell, self._cell_render_service)
        self.column2.set_attributes (cell2, text=1)
#        self.column2 = gtk.TreeViewColumn ("Name", gtk.CellRendererText(), text=1)
        self.column2.set_sizing (gtk.TREE_VIEW_COLUMN_FIXED)
        self.column2.set_min_width (175)
        self.column2.set_resizable (True)
        self.column2.set_expand (True)

        self.column5 = gtk.TreeViewColumn ("Speed",
            gtk.CellRendererText(), text=4)
        self.column5.set_sizing (gtk.TREE_VIEW_COLUMN_FIXED)
        self.column5.set_min_width (100)

        self.column6 = gtk.TreeViewColumn ("Size",
            gtk.CellRendererText (), text=5)
        self.column6.set_sizing (gtk.TREE_VIEW_COLUMN_FIXED)
        self.column6.set_min_width (100)

        self.column3 = gtk.TreeViewColumn ("Progress",
            gtk.CellRendererProgress(), value=2)
        self.column3.set_min_width (75)
        self.column4 = gtk.TreeViewColumn ("Status",
            gtk.CellRendererText(), text=3)
        self.column4.set_min_width (100)
        self.column4.set_sizing (gtk.TREE_VIEW_COLUMN_FIXED)
        self.column7 = gtk.TreeViewColumn ("Time Left",
            gtk.CellRendererText(), text=6)
        self.column7.set_min_width (110)
        self.column7.set_sizing (gtk.TREE_VIEW_COLUMN_FIXED)

        self.treeview1.append_column (self.column2)
        self.treeview1.append_column (self.column6)
        self.treeview1.append_column (self.column3)
        self.treeview1.append_column (self.column5)
        self.treeview1.append_column (self.column7)
        self.treeview1.append_column (self.column4)
        self.treeview1.set_model (thread_manager.tree_model)

        self.folder_chooser = self.window.get_widget ("filechooserbutton1")
        self.folder_chooser.set_current_folder (app_settings.output_dir)
        self.statusbar = self.window.get_widget ("statusbar1")
        self.speed_statusbar = self.window.get_widget ("statusbar2")
#        self.speed_label = self.window.get_widget ("speedlabel")
        self.statusbar_context_id = self.statusbar.get_context_id ("Statusbar")
        self.pause_toolbutton = self.window.get_widget ("pause_toolbutton")
        self.sites_window = self.window.get_widget ("sites_dialog")
        self.sites_textview = self.window.get_widget ("sites_textview")

        self.app_settings = app_settings
        self.thread_manager = thread_manager
        self.parser_manager = parser_manager
        self.prop_cont = prop_cont
        self._treeview_rightclick_event = None

        gtk.about_dialog_set_url_hook (self.open_site)
        self.treeview1.connect ("button-press-event", self.treeview_right)
        self.treeview1.connect ("cursor-changed", self.treeview_right2)

        connect_dict = {
            "on_window1_delete_event": self.quit_app,
            "on_quit1_activate": self.quit_app,
            "on_preferences2_activate": self.show_preferences,
            "on_about1_activate": self.show_about_window,
            "on_aboutdialog1_response": self.hide_about_window,
            "on_aboutdialog1_delete_event": self.keep_about_window,
            "on_sites_activate": self.show_sites_window,
            "on_close_sites_clicked": self.hide_sites_window,
            "on_sites_dialog_delete_event": self.keep_sites_window,
            "on_sites_dialog_response": self.hide_sites_window,
            "on_checkbutton1_toggled": self.transcode_check,
            "on_checkbutton2_toggled": self.overwrite_check,
            "on_checkbutton3_toggled": self.keep_flvs_check,
            "on_auto_download_check_toggled": self.change_auto_download,
            "on_video_bitrate_changed": self.change_video_bitrate,
            "on_resolution_combobox_changed": self.resolution_change,
            "on_combobox1_changed": self.change_format,
            "on_toolbutton4_clicked": self.move_up,
            "on_toolbutton5_clicked": self.move_down,
            "on_treeview1_cursor_changed": self.select_item,
            "on_toolbutton3_clicked": self.clear_complete,
            "on_openfolderbutton_clicked": self.open_video_folder,
            "on_filechooserbutton1_current_folder_changed":
                self.change_video_folder,
            "on_pause_toolbutton_clicked": self.pause_download,
            "on_toolbutton2_clicked": self.remove,
            "on_button1_clicked": self.add_video_from_url,
            "on_toolbutton1_clicked": self.start_process,
            "on_entry1_activate": self.add_video_from_url,
            "on_audio_bitrate_changed": self.change_audio_bitrate,
        }
        self.window.signal_autoconnect (connect_dict)

        self.thread_manager.connect ("unblock-ui", self.unlock_partial_ui)
        self.thread_manager.connect ("block-ui", self.block_partial_ui)
        self.thread_manager.connect ("speed_progress_update",
            self.update_speed_statusbar)
        self.thread_manager.connect ("progress_update", self.update_statusbar)

        # Populate sites_textview with hooks to controller methods when
        # moving over text and clicking on links
        self.sites_textview.connect ("motion-notify-event",
            self.sites_textview_motion_notify_event)

        parser_list = self.parser_manager.get_official_parsers ()
        name_list = []
        tmp_dic = {}
        for parser in parser_list:
            name_list.append (parser.getType ())
            tmp_dic[parser.getType ()] = parser
        name_list.sort ()

        textbuffer = self.sites_textview.get_buffer ()
        textbuffer.insert (textbuffer.get_end_iter (),
            "Supported Sites\n-----------------------\n\n")

        for i, name in enumerate (name_list):
            newtag = textbuffer.create_tag ("url-tag%i" % i)
            newtag.set_property ("underline", pango.UNDERLINE_SINGLE)
            newtag.set_property ("foreground", "#2750FF")
            newtag.connect ("event",
                self.sites_textview_link_button_press_event)
            newtag.set_data ("link", tmp_dic[name].domain_str)

            parser_version = tmp_dic[name].version
            textbuffer.insert (textbuffer.get_end_iter (), "* ")
            textbuffer.insert_with_tags_by_name (textbuffer.get_end_iter (),
                name, newtag.get_property ("name"))

            textbuffer.insert (textbuffer.get_end_iter (),
                "   ({0}/{1}/{2})\n".format (parser_version.month,
                parser_version.day, parser_version.year))

    def update_statusbar (self, widget=None, message=None, interval=0):
        if message == None:
            self.statusbar.pop (self.statusbar_context_id)
        else:
            self.statusbar.pop (self.statusbar_context_id)
            self.statusbar.push (self.statusbar_context_id, message)
        if interval:
            gobject.timeout_add (interval, self.update_statusbar)

    def update_speed_statusbar (self, widget=None, message=None):
        if message == None:
            self.speed_statusbar.pop (self.statusbar_context_id)
        else:
            self.speed_statusbar.pop (self.statusbar_context_id)
            self.speed_statusbar.push (self.statusbar_context_id, message)

    def show_about_window (self, widget):
        """Display non-modal about window"""
        self.about_window.show ()

    def hide_about_window (self, widget, data=None):
        """Hide non-modal about window"""
        self.about_window.hide ()

    def show_caution_window (self):
        temp_wtree = gtk.glade.XML (self.gladefile, 'dialog1')
        caution_window = temp_wtree.get_widget ('dialog1')
        caution_window.run ()
        caution_window.destroy ()

    def _cell_render_service (self, column, cell, model, iter):
        url = model.get_value (iter, 0)
        thread_id = self.thread_manager.get_thread_id (url)
        thread = self.thread_manager.get_video_thread (thread_id)

        if not hasattr (thread.video.parser.__class__, "getImageData") and (
            not callable (thread.video.parser.__class__.getImageData)):
            return

        image_data = thread.video.parser.getImageData ()
        image = gtk.gdk.pixbuf_new_from_data (image_data,
            gtk.gdk.COLORSPACE_RGB, True, 8, 16, 16, 16*4)
        cell.set_property ('pixbuf', image)
        return

    def change_video_folder (self, widget):
        self.app_settings.output_dir = widget.get_filename ()

    def quit_app (self, widget, data=None):
        if self.thread_manager.is_queue_active ():
            self.show_caution_window ()
            return True

        gtk.main_quit ()

    def show_preferences (self, widget):
        self.prop_cont.show ()

    def keep_about_window (self, widget, data):
        """Keep about window from being destroyed when close button
        is clicked. Window will be hidden later from the response handler"""
        return True

    def show_sites_window (self, widget):
        self.sites_window.show ()

    def hide_sites_window (self, widget, data=None):
        """Hide non-modal sites dialog window"""
        self.sites_window.hide ()

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
            self.checkbutton3.set_active (True)
            self.checkbutton3.set_sensitive (False)
        else:
            self.checkbutton3.set_sensitive (True)

    def overwrite_check (self, widget):
        self.app_settings.overwrite = not self.app_settings.overwrite

    def keep_flvs_check (self, widget):
        self.app_settings.keep_flv_files = not self.app_settings.keep_flv_files

    def change_auto_download (self, widget):
        self.app_settings.auto_download = not self.app_settings.auto_download

    def change_video_bitrate (self, widget):
        index = widget.get_active ()
        self.app_settings.vbitrate = self._video_bitrate_options[index]

    def change_audio_bitrate (self, widget):
        self.app_settings.abitrate = (widget.get_active ()*32)+32

    def resolution_change (self, widget):
        self.app_settings.output_res = widget.get_active ()

    def change_format (self, widget):
        format = widget.get_active ()
        if format in VideoItem.VIDEO_FORMATS:
            self.app_settings.format = format
            self.resolution_combobox.set_sensitive (True)
            self.video_bitrate_combobox.set_sensitive (True)
            self.audio_bitrate_combobox.set_sensitive (True)
        else:
            self.app_settings.format = format
            self.resolution_combobox.set_sensitive (False)
            self.video_bitrate_combobox.set_sensitive (False)
            self.audio_bitrate_combobox.set_sensitive (True)

    def move_up (self, widget):
        """Move Up"""
        tree = self.treeview1.get_selection ()
        model, selection = tree.get_selected ()
        url = model.get_value (selection, 0)
        thread_id = self.thread_manager.get_thread_id (url)

        path = model.get_path (selection)
        index = path[0]
        previous = model.get_iter ((index-1),)
        dude_url = model.get_value (previous, 0)
        prev_thread_id = self.thread_manager.get_thread_id (dude_url)

        self.thread_manager.swap_items (thread_id, prev_thread_id)
        tree.select_path (index-1)
        self.select_item ()

    def move_down (self, widget):
        """Move Down"""
        tree = self.treeview1.get_selection ()
        model, selection = tree.get_selected ()
        url = model.get_value (selection, 0)
        thread_id = self.thread_manager.get_thread_id (url)

        path = model.get_path (selection)
        index = path[0]
        previous = model.get_iter ((index+1),)
        dude_url = model.get_value (previous, 0)
        prev_thread_id = self.thread_manager.get_thread_id (dude_url)

        self.thread_manager.swap_items (thread_id, prev_thread_id)
        tree.select_path (index+1)
        self.select_item ()

    def select_item (self, widget=None):
        tree = self.treeview1.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        url = model.get_value (selection, 0)
        thread_id = self.thread_manager.get_thread_id (url)
        thread = self.thread_manager.get_video_thread (thread_id)

        if thread and thread.isAlive () and thread.status == thread.WAITING:
            self.toolbutton1.set_sensitive (True)
            self.toolbutton2.set_sensitive (True)
            self.toolbutton2.set_label ("Remove")
            self.pause_toolbutton.set_sensitive (False)
            self.pause_toolbutton.set_label ("Pause")
        elif thread and thread.isAlive () and thread.status == thread.READY:
            self.toolbutton1.set_sensitive (False)
            self.toolbutton2.set_sensitive (True)
            self.toolbutton2.set_label ("Cancel")
            if thread._downloader:
                self.pause_toolbutton.set_sensitive (True)
            else:
                self.pause_toolbutton.set_sensitive (False)
            self.pause_toolbutton.set_label ("Pause")
        elif thread and thread.isAlive () and thread.status == thread.PARSING:
            self.toolbutton1.set_sensitive (False)
            self.toolbutton2.set_sensitive (False)
            self.toolbutton2.set_label ("Remove")
            self.pause_toolbutton.set_sensitive (False)
            self.pause_toolbutton.set_label ("Pause")
        # Handle case of a cancelled download waiting to stop
        elif thread and thread.isAlive () and thread.status == thread.CANCELING:
            self.toolbutton1.set_sensitive (False)
            self.toolbutton2.set_sensitive (False)
            self.toolbutton2.set_label ("Wait")
            self.pause_toolbutton.set_sensitive (False)
            self.pause_toolbutton.set_label ("Pause")
        elif thread and thread.isAlive () and thread.status == thread.PAUSED:
            self.toolbutton1.set_sensitive (False)
            self.toolbutton2.set_sensitive (True)
            self.toolbutton2.set_label ("Cancel")
            self.pause_toolbutton.set_sensitive (True)
            self.pause_toolbutton.set_label ("Resume")
        elif thread:
            self.toolbutton1.set_sensitive (False)
            self.toolbutton2.set_sensitive (True)
            self.toolbutton2.set_label ("Remove")
            self.pause_toolbutton.set_sensitive (False)
            self.pause_toolbutton.set_label ("Pause")

        path = model.get_path (selection)
        index = path[0]

        queue_length = self.thread_manager.queue_length ()

        if queue_length >= 2:
            self.toolbutton3.set_sensitive (True)
            if index == queue_length-1:
                self.toolbutton4.set_sensitive (True)
                self.toolbutton5.set_sensitive (False)
            elif index == 0:
                self.toolbutton4.set_sensitive (False)
                self.toolbutton5.set_sensitive (True)
            else:
                self.toolbutton4.set_sensitive (True)
                self.toolbutton5.set_sensitive (True)
        elif queue_length > 0:
            self.toolbutton3.set_sensitive (True)

        return True

    def block_ui (self, widget=None):
        self.block_partial_ui ()
        self.entry1.set_sensitive (False)
        self.button1.set_sensitive (False)

    def block_partial_ui (self, widget=None):
        self.toolbutton2.set_label ("Remove")
        self.toolbutton1.set_sensitive (False)
        self.toolbutton2.set_sensitive (False)
        self.toolbutton3.set_sensitive (False)
        self.toolbutton4.set_sensitive (False)
        self.toolbutton5.set_sensitive (False)
        tree = self.treeview1.get_selection ()
        model, selection = tree.get_selected ()
        if selection:
            index = model.get_path (selection)[0]
            tree.select_path (index)
            self.select_item ()

    def unlock_partial_ui (self, widget=None):
        self.entry1.set_sensitive (True)
        self.button1.set_sensitive (True)
        self.entry1.set_text ("")
        tree = self.treeview1.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            num_threads = self.thread_manager.queue_length ()
            path = (num_threads - 1) if num_threads > 0 else 0
            tree.select_path (path)
        else:
            index = model.get_path (selection)[0]
            tree.select_path (index)

        self.select_item ()

    def clear_complete (self, widget):
        self.thread_manager.clear_complete ()
        self.block_partial_ui ()

    def open_video_folder (self, widget):
        folder = self.folder_chooser.get_filename ()
        if WINDOWS:
            subprocess.Popen (["start", "", folder], shell=True)
        else:
            subprocess.Popen (["xdg-open", folder])

    def pause_download (self, widget):
        tree = self.treeview1.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        url = model.get_value (selection, 0)
        thread_id = self.thread_manager.get_thread_id (url)
        thread = self.thread_manager.get_video_thread (thread_id)
        if thread.status == thread.READY and thread._downloader:
            thread.pause ()
        elif thread.status == thread.PAUSED:
            thread.setReady ()

        self.select_item ()

    def remove (self, widget):
        tree = self.treeview1.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        url = model.get_value (selection, 0)
        thread_id = self.thread_manager.get_thread_id (url)
        thread = self.thread_manager.get_video_thread (thread_id)

        if thread and thread.isAlive () and thread.status == thread.WAITING:
            self.thread_manager.remove_download (thread_id)
        elif thread and thread.isAlive () and thread.status == thread.READY:
            self.thread_manager.finish_download (thread_id)
        # Handle case of a cancelled download waiting to stop
        elif thread and thread.isAlive () and thread.status == thread.CANCELING:
            print "Already cancelled. Waiting. Don't do anything"
            return
        elif thread and thread.isAlive () and thread.status == thread.PAUSED:
            self.thread_manager.finish_download (thread_id)
        elif thread:
            self.thread_manager.remove_download (thread_id)

        self.block_partial_ui ()
        return True

    def treeview_right2 (self, widget):
        tree = widget.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        if self._treeview_rightclick_event:
            event = self._treeview_rightclick_event
            url = model.get_value (selection, 0)
            thread_id = self.thread_manager.get_thread_id (url)
            thread = self.thread_manager.get_video_thread (thread_id)
            popup = VideoItemMenu (self.gladefile, self.treeview1,
                self.thread_manager)

            # Move this logic to VideoItemMenuController class
            if thread.status == thread.DONE:
                video_file_input = thread.video.flv_file
                video_file_output = thread.video.avi_file
                video_input_exists = os.path.exists (video_file_input)
                video_output_exists = os.path.exists (video_file_output)

                if video_input_exists:
                    popup.get_children ()[0].set_sensitive (True)
                else:
                    popup.get_children ()[0].set_sensitive (False)

                if video_output_exists:
                    popup.get_children ()[1].set_sensitive (True)
                else:
                    popup.get_children ()[1].set_sensitive (False)

                if video_input_exists or video_output_exists:
                    popup.get_children ()[2].set_sensitive (True)
                else:
                    popup.get_children ()[2].set_sensitive (False)
            else:
                popup.get_children ()[0].set_sensitive (False)
                popup.get_children ()[1].set_sensitive (False)
                popup.get_children ()[2].set_sensitive (False)

            popup.popup (None, None, None, event.button, event.time)

        self._treeview_rightclick_event = None

    def treeview_right (self, widget, event):
        # Check if a right click was performed on a video item.
        # The treeview_right2 will be called shortly after this
        # due to cursor-changed signal
        if event.button == self.GTK_RIGHT_CLICK_BUTTON:
            self._treeview_rightclick_event = event

    def add_video_from_url (self, widget):
        newtext = self.entry1.get_text ()
        if not newtext:
            return

        video = self.parser_manager.validateURL (newtext)
        if not video:
            self.update_statusbar (
                message="An invalid url was passed. Try again.", interval=2500
            )
            self.entry1.set_text ('')
            return
        self.block_ui ()
        
        self.thread_manager.create_video_thread (video)

    def start_process (self, widget):
        tree = self.treeview1.get_selection ()
        model, selection = tree.get_selected ()

        url = model.get_value (selection, 0)
        thread_id = self.thread_manager.get_thread_id (url)

        if thread_id is not None:
            self.thread_manager.start_download (thread_id)

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
