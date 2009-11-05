import os
import gtk
import gobject
import time
from threading import Lock, Semaphore
from videodownloadthread import VideoDownloadThread
from youtubed2x_lib.sessioninfo import SessionInfo, SessionItem
from youtubed2x_lib.ui.exceptions.inqueueexception import InQueueException


# TODO: NEED TO RENAME CLASS AND INSTANCE. NOT A QUEUE ANYMORE. W00T!
class QueueManager (object):
    COLUMN_NAMES = {0: "url", 1: "title", 2: "progress", 3: "status", 4: "speed", 5: "size", 6: "eta"}
    signals = ["progress-update", "info-changed", "block-ui", "unblock-ui"]
    UPDATE_INTERVAL = .5 # In seconds


    def __init__ (self, app_settings):
        self.observers = {}
        for signal in self.__class__.signals:
            self.observers[signal] = []
        self.dude = {}
        self.next_status_id = 0
        self._num_objects = 0
        self._running_items = 0
        if app_settings.process_limit < 0:
            raise Exception ("Process limit is less than zero. Passed: %s" % sem_limit)

        self._sem_limit = app_settings.process_limit
        self.app_settings = app_settings
        self.lock = Lock ()
        self.tree_model = gtk.ListStore (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.semaphore = Semaphore (self._sem_limit)
        self.sem_lock = Lock ()


    def register (self, signal, observer):
        if signal in self.observers:
            if observer not in self.observers[signal]:
                self.observers[signal].append (observer)
        else:
            raise Exception ("WTF")


    def unregister (self, signal, observer):
        if signal in self.observers:
            if observer in self.observers[signal]:
                self.observers[signal].remove (observer)
        else:
            raise Exception ("WTFA")


    def send (self, signal, *args):
        if signal in self.observers:
            for observer in self.observers[signal]:
                observer (*args)
        else:
            raise Exception ("WHO IS YOUR DADDY AND WHAT DOES HE DO?")


    def add_try (self, thread):
        self.lock.acquire ()
        # Check if video has already been added
        possible_id = self.getThreadId (thread.video.parser.page_url)
        if possible_id != None:
            self.lock.release ()
            raise InQueueException ("URL has already been added to queue.")

        id = self.next_status_id
        self.next_status_id += 1
        gtk.gdk.threads_enter ()
        self.dude[id] = {"iter": self.tree_model.append ([thread.video.parser.page_url, thread.video.parser.page_url, 0, "Getting Info", "", "", ""]), "thread": thread, "last_update": time.time ()}
#       self.tree_model.append (['http://www.youtube.com/watch?v=KZ1aZjTrh3I', 'http://www.youtube.com/watch?v=KZ1aZjTrh3I', 0, 'Waiting', "100 KB", "50 MB"]) # Replace 2nd URL with parsed title once page is parsed
        gtk.gdk.threads_leave ()
        self._num_objects += 1
        self.lock.release ()
        return id


    def acquire_sem (self):
        self.sem_lock.acquire ()
        if self._sem_limit == 0:
            self._running_items += 1
            self.sem_lock.release ()
            return True

        status = self.semaphore.acquire (False)
        if status:
            self._running_items += 1
        self.sem_lock.release ()
        return status


    def release_sem (self):
        self.sem_lock.acquire ()
        if self._running_items > 0:
            if self._running_items <= self._sem_limit and self._sem_limit != 0:
                self.semaphore.release ()
            self._running_items -= 1
        self.sem_lock.release ()


    def alter_sem (self, value):
        self.sem_lock.acquire ()
        if isinstance (value, int) and value >= 0:
            if value == 0:
                self.semaphore = Semaphore (value)
            elif value >= self._running_items:
                self.semaphore = Semaphore (value-self._running_items)

            self._sem_limit = value
        self.sem_lock.release ()


    def update_status (self, id, **kwargs):
        if not id in self.dude:
            return

        iter = self.dude[id]["iter"]
        if iter is None:
            return

        force_update = kwargs.get ("force_update", False)
        update_time = (time.time () - self.dude[id]["last_update"]) > self.__class__.UPDATE_INTERVAL
        # Return if it is not time to update
        if not update_time and not force_update:
            return

        self.lock.acquire ()
        gtk.gdk.threads_enter ()
        for column, key in self.__class__.COLUMN_NAMES.items ():
            if key in kwargs:
                self.tree_model.set (iter, column, kwargs[key])
        self.dude[id]["last_update"] = time.time ()
        gtk.gdk.threads_leave ()
        self.lock.release ()


    def startDownload (self, id):
        if not id in self.dude:
            return False

        thread = self.dude[id]["thread"]
        thread.setReady (True)


    def getVideoThread (self, id):
        if not id in self.dude:
            return None

        thread = self.dude[id]["thread"]
        return thread


    def getThreadId (self, url):
        for element in self.dude:
            thread = self.dude[element]["thread"]
            if thread and thread.video.parser.page_url == url:
                return element
        return None


    def removeDownload (self, id):
        if not id in self.dude:
            return

        iter = self.dude[id]["iter"]
        self.lock.acquire ()
        self._removeIter (iter)
        self.lock.release ()
        self.dude[id]["iter"] = None
        if self.dude[id]["thread"].status != VideoDownloadThread.DONE:
            self.dude[id]["thread"].cancel ()
        self._num_objects -= 1
        key_list = self.dude.keys ()
        key_list.sort ()
        # Removing last entry
        if id == key_list[-1]:
            if len (key_list) == 1:
                self.next_status_id = 0 # Reset Status ID (Removing only entry)
            else:
                self.next_status_id = key_list[-2]+1
        del self.dude[id]


    def finishDownload (self, id):
        if not id in self.dude:
            return

        iter = self.dude[id]["iter"]
        if self.dude[id]["thread"].status != VideoDownloadThread.DONE:
            self.dude[id]["thread"].cancel ()


    def _removeIter (self, iter):
        self.tree_model.remove (iter)


    def is_empty (self):
        return self._num_objects == 0


    def queue_length (self):
        return self._num_objects


    def swap_items (self, id_item1, id_item2):
        if id_item1 in self.dude and id_item2 in self.dude:
            self.tree_model.swap (self.dude[id_item1]["iter"], self.dude[id_item2]["iter"])


    def is_queue_active (self):
        for element in self.dude.keys ():
            thread = self.dude[element]["thread"]
            if thread and thread.isAlive ():
                if thread.status == VideoDownloadThread.READY or thread.status == VideoDownloadThread.PARSING:
                    return True

        return False


    def clear_complete (self):
        for element in self.dude.keys ():
            thread = self.dude[element]["thread"]
            if thread and not thread.isAlive ():
                self.removeDownload (element)


    def restore_session (self):
        restore_session = SessionInfo ()
        items = restore_session.read ()
#        print items
        for item in items:
            youtube_video = item.video
            self.send ("block-ui")
            VideoDownloadThread (self, self.app_settings, youtube_video, item.status).start ()


    def save_session (self):
        items = []

        def add_items (model, path, iter, item_list):
            url = model.get_value (iter, 0)
            thread_id = self.getThreadId (url)
            thread = self.getVideoThread (thread_id)
            if thread and (thread.status == thread.__class__.PAUSED or thread.status == thread.__class__.DONE or thread.status == thread.__class__.CANCELLED):
                 item_list.append (SessionItem (thread.video, thread.status))

        self.tree_model.foreach (add_items, items)

#        print items
        new_session = SessionInfo ()
        if items:
            for item in items:
                new_session.addItem (item)
            new_session.save ()
        else:
            new_session.delete ()


