import gtk
import gtk.glade
import os
import subprocess
from youtubed2x_lib.other import WINDOWS


class VideoItemMenu (object):
    def __init__ (self, glade_file, treeview, thread_manager):
        self.gladefile = glade_file
        self.base = gtk.glade.XML (self.gladefile, "treeview_menu1")
        self.treeview_menu1 = self.base.get_widget ("treeview_menu1")
        if not isinstance (treeview, gtk.TreeView):
            raise Exception ("An instance of a gtk.TreeView object was not passed")
        self.treeview = treeview
        self.thread_manager = thread_manager

        connect_dict = {
            "on_copypageurl_menuitem_activate": self.copy_page_url_selection,
            "on_copyvidurl_menuitem_activate": self.copy_video_url_selection,
            "on_playvideo_menuitem_activate": self.playvideo_selection,
            "on_playvideoout_menuitem_activate": self.playoutput_selection,
            "on_dir_menuitem_activate": self.open_output_directory,
        }
        self.base.signal_autoconnect (connect_dict)

    def copy_page_url_selection (self, widget):
        tree = self.treeview.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        url = model.get_value (selection, 0)
        clipboard = gtk.Clipboard ()
        clipboard.set_text (url)

    def copy_video_url_selection (self, widget):
        tree = self.treeview.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        url = model.get_value (selection, 0)
        thread_id = self.thread_manager.get_thread_id (url)
        thread = self.thread_manager.get_video_thread (thread_id)
        clipboard = gtk.Clipboard ()
        clipboard.set_text (thread.video.real_url)

    def playvideo_selection (self, widget):
        tree = self.treeview.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        url = model.get_value (selection, 0)
        thread_id = self.thread_manager.get_thread_id (url)
        thread = self.thread_manager.get_video_thread (thread_id)

        if os.path.exists (thread.video.flv_file):
            video_file = thread.video.flv_file
        else:
            video_file = None

        if video_file:
            if WINDOWS:
                subprocess.Popen (["start", "", video_file], shell=True)
            else:
                subprocess.Popen (["xdg-open", video_file])

    def playoutput_selection (self, widget):
        tree = self.treeview.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        url = model.get_value (selection, 0)
        thread_id = self.thread_manager.get_thread_id (url)
        thread = self.thread_manager.get_video_thread (thread_id)
        if os.path.exists (thread.video.avi_file):
            video_file = thread.video.avi_file
        else:
            video_file = None

        if video_file:
            if WINDOWS:
                subprocess.Popen (["start", "", video_file], shell=True)
            else:
                subprocess.Popen (["xdg-open", video_file])

    def open_output_directory (self, widget):
        tree = self.treeview.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        url = model.get_value (selection, 0)
        thread_id = self.thread_manager.get_thread_id (url)
        thread = self.thread_manager.get_video_thread (thread_id)
        if os.path.exists (thread.video.flv_file):
            video_file = thread.video.flv_file
        elif os.path.exists (thread.video.avi_file):
            video_file = thread.video.avi_file
        else:
            video_file = None

        if video_file:
            directory = video_file.rsplit (os.sep, 1)[0]
            if WINDOWS:
                subprocess.Popen (["start", "", directory], shell=True)
            else:
                subprocess.Popen (["xdg-open", directory])

    def get_children (self):
        return self.treeview_menu1.get_children ()

    def popup (self, *args):
        self.treeview_menu1.popup (*args)
