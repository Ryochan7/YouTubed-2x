import gtk
import gtk.glade

class VideoItemMenu (object):
    def __init__ (self, glade_file, treeview):
        self.gladefile = glade_file
        self.base = gtk.glade.XML (self.gladefile, "treeview_menu1")
        self.treeview_menu1 = self.base.get_widget ("treeview_menu1")
        if not isinstance (treeview, gtk.TreeView):
            raise Exception ("An instance of a gtk.TreeView object was not passed")
        self.treeview = treeview


    def get_children (self):
        return self.treeview_menu1.get_children ()


    def popup (self, *args):
        self.treeview_menu1.popup (*args)

