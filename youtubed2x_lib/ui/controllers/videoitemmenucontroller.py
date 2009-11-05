import os
import gtk
import subprocess
from youtubed2x_lib.other import WINDOWS


class VideoItemMenuController (object):
    def __init__ (self, ui, video_queue):
        self.ui = ui
        self.video_queue = video_queue

        dic = {"on_copypageurl_menuitem_activate": self.copy_url_selection, "on_copyvidurl_menuitem_activate": self.copy_video_url_selection, "on_playvideo_menuitem_activate": self.playvideo_selection}
        self.ui.base.signal_autoconnect (dic)


    def copy_url_selection (self, widget):
        tree = self.ui.treeview.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        url = model.get_value (selection, 0)
        clipboard = gtk.Clipboard ()
        clipboard.set_text (url)


    def copy_video_url_selection (self, widget):
        tree = self.ui.treeview.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        url = model.get_value (selection, 0)
        thread_id = self.video_queue.getThreadId (url)
        thread = self.video_queue.getVideoThread (thread_id)
        clipboard = gtk.Clipboard ()
        clipboard.set_text (thread.video.real_url)


    def playvideo_selection (self, widget):
        tree = self.ui.treeview.get_selection ()
        model, selection = tree.get_selected ()
        if not selection:
            return

        url = model.get_value (selection, 0)
        thread_id = self.video_queue.getThreadId (url)
        thread = self.video_queue.getVideoThread (thread_id)
        if os.path.exists (thread.video.avi_file):
            video_file = thread.video.avi_file
        elif os.path.exists (thread.video.flv_file):
            video_file = thread.video.flv_file
        else:
            video_file = None

        if video_file:
            if WINDOWS:
                subprocess.Popen (["start", "", video_file], shell=True)
            else:
                subprocess.Popen (["xdg-open", video_file])


    def get_children (self):
        return self.ui.get_children ()


    def popup (self, *args):
        self.ui.treeview_menu1.popup (*args)


