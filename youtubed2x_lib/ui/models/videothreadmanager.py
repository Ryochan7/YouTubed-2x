import gtk
import logging
import gobject
import time
from threading import Lock, Semaphore
from videodownloadthread import VideoDownloadThread
from youtubed2x_lib.sessioninfo import SessionInfo, SessionItem
from youtubed2x_lib.ui.exceptions.inqueueexception import InQueueException
from youtubed2x_lib.download import FileDownloader

class VideoThreadManager (gobject.GObject):
    __gsignals__ = {
        "speed_progress_update": (gobject.SIGNAL_RUN_FIRST, None, (str,)),
        "progress_update": (gobject.SIGNAL_RUN_FIRST, None, (str,)),
        "info-changed": (gobject.SIGNAL_RUN_FIRST, None, ()),
        "block-ui": (gobject.SIGNAL_RUN_FIRST, None, ()),
        "unblock-ui": (gobject.SIGNAL_RUN_FIRST, None, ()),
    }

    COLUMN_NAMES = {
        0: "url",
        1: "title",
        2: "progress",
        3: "status",
        4: "speed",
        5: "size",
        6: "eta"
    }
    UPDATE_INTERVAL = 1 # In seconds
    DOWNLOAD_UPDATE_INTERVAL = 1 # In seconds
    BYTES_PER_KB = FileDownloader.BYTES_PER_KB
    TRANSFER_PER_BLOCK = FileDownloader.TRANSFER_PER_BLOCK

    def __init__ (self, app_settings):
        super (self.__class__, self).__init__ ()
        self._log = logging.getLogger ("{0}.{1}".format (__name__,
            self.__class__.__name__))

        if app_settings.process_limit < 0:
            raise Exception (
                "Process limit is less than zero. Passed: {0}".format (
                    app_settings.process_limit)
            )
    
        if app_settings.download_speed_limit < 0:
            raise Exception (
                "Download speed limit is less than zero. Passed: {0}".format (
                app_settings.download_speed_limit)
            )

        self.tree_items = {}
        self._num_objects = 0
        self._running_items = 0
        self._sem_limit = app_settings.process_limit
        self.semaphore = Semaphore (self._sem_limit)
        self.sem_lock = Lock ()
        self.app_settings = app_settings
        self.lock = Lock ()

        self.tree_model = gtk.ListStore (
            gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT,
            gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING,
            gobject.TYPE_STRING
        )
#        self.download_semaphore = Semaphore (1)
        self.download_lock = Lock ()
        # Download limit in number of bytes (per second)
        #self.download_limit = 0
        self.download_limit = self.BYTES_PER_KB * 100# * self.app_settings.download_speed_limit
        # Used for bandwidth throttling
        self.download_update = time.time ()
        # Used for determining when to update download speed progress
        # text
        self.speed_status_update = time.time ()
        # Used to estimate how many bytes will be downloaded
        # to assist in bandwidth throttling
        self.download_speed_est = 0
        # Used to keep track of downloaded bytes across all downloads
        self.download_speed_total = 0
        # Limit the number of transcoding process
        self.transcode_semaphore = Semaphore (1)

    def create_video_thread (self, video, status=None):
        self.lock.acquire ()
        # Check if video has already been added
        possible_id = self.get_thread_id (video.parser.page_url)
        if possible_id:
            self.lock.release ()
            raise InQueueException ("URL has already been added to queue.")

        thread = None
        if status is None:
            thread = VideoDownloadThread (self, self.app_settings, video)
        else:
            thread = VideoDownloadThread (
                self, self.app_settings, video, status
            )
        
        # Using TreeIter hash as tree_item id
        item_iter = self.tree_model.append ([video.parser.page_url,
                video.parser.page_url, 0, "Getting Info", "", "", ""])
        self.tree_items[item_iter] = {
            "thread": thread,
            "last_update": time.time (),
            "speed_as_double": 0.0,
            "working": False
        }
        thread.download_id = item_iter

        #item_iter = self.tree_model.append (
        #    ['http://www.youtube.com/watch?v=KZ1aZjTrh3I',
        #   'http://www.youtube.com/watch?v=KZ1aZjTrh3I', 0, 'Waiting',
        #   "100 KB", "50 MB"]) # Replace 2nd URL with parsed title once page
        #    is parsed
        #thread.download_id = item_iter

        self._num_objects += 1
        thread.start ()
        self.lock.release ()
        return item_iter

    def acquire_sem (self, item_iter):
        self.sem_lock.acquire ()
        if not item_iter in self.tree_items or (
            self.tree_items[item_iter]["working"]):
            status = False
        elif self._sem_limit == 0:
            self._running_items += 1
            status = True
        else:
            status = self.semaphore.acquire (False)

        if status:
            self._running_items += 1
            self.lock.acquire ()
            self.tree_items[item_iter]["working"] = True
            self.lock.release ()
        
        self.sem_lock.release ()
        return status

    def release_sem (self, item_iter):
        self.sem_lock.acquire ()
        if not item_iter in self.tree_items:
            self.sem_lock.release ()
            return False

        if self._running_items > 0:
            if self._running_items <= self._sem_limit and self._sem_limit != 0:
                self.semaphore.release ()
            self._running_items -= 1
            self.lock.acquire ()
            self.tree_items[item_iter]["speed_as_double"] = 0.0
            self.tree_items[item_iter]["working"] = False
            self.lock.release ()

        # Run after _running_items is altered to check if no more running
        # items exist
        if self._running_items == 0:
            gtk.gdk.threads_enter ()
            self.emit ("speed_progress_update", "")
            self.emit ("progress_update", "")
            gtk.gdk.threads_leave ()
        self.sem_lock.release ()

    def alter_sem (self, widget, settings):
        self.sem_lock.acquire ()
        value = settings.process_limit
        if value >= 0:
            if value == 0:
                self.semaphore = Semaphore (value)
            elif value > 0 and value >= self._running_items:
                self.semaphore = Semaphore (value-self._running_items)

            self._sem_limit = value
        self.sem_lock.release ()

    def update_status (self, item_iter, **kwargs):
        self.lock.acquire ()
        if not item_iter in self.tree_items:
            self.lock.release ()
            return

        # Only update at certain intervals due to Windows GTK
        # runtime crashing when updating after each new message
        force_update = kwargs.get ("force_update", False)
        time_since_update = (
            time.time () - self.tree_items[item_iter]["last_update"]
        )
        update_time = time_since_update > self.UPDATE_INTERVAL
        # Return if it is not time to update item status
        if not update_time and not force_update:
            self.lock.release ()
            return

        gtk.gdk.threads_enter ()
        for column, key in self.COLUMN_NAMES.items ():
            if key in kwargs:
                self.tree_model.set (item_iter, column, kwargs[key])

        # Update download speed total message in statusbar
        #time_since_speed_update = time.time () - self.speed_status_update
        if (self.tree_items[item_iter]["thread"].status
            == VideoDownloadThread.READY):# and time_since_speed_update > self.__class__.UPDATE_INTERVAL:
            self.emit ("progress_update", "Active: %i of %i" % (self._running_items, self._num_objects))
            #self.download_lock.acquire ()
#            print "Try out"
            # Recalculate time_since_speed_update in case acquiring the download_lock
            # takes a while to do
            #time_since_speed_update = time.time () - self.speed_status_update
            #speed = 0.0
            #for thread_id in self._worker_threads_ids:
            #    temp_speed = self.tree_items[thread_id]["speed_as_double"]
            #    speed += temp_speed
            #print self._worker_threads_ids
            #print "TEST TOTAL SPEED: %s" % speed

            #speed = self.download_speed_total / time_since_speed_update
#            speed = self.download_speed_total / time_since_speed_update
            #self.send ("speed_progress_update", "DL Speed: %s/s" % (FileDownloader.humanizeSize (speed),))
            #self.send ("progress_update", "Active: %i of %i" % (self._running_items,self._num_objects))
            #self.download_speed_total = 0
            #self.speed_status_update = time.time ()
            #self.download_lock.release ()

        self.tree_items[item_iter]["last_update"] = time.time ()
        gtk.gdk.threads_leave ()
        self.lock.release ()

    def start_download (self, item_iter):
        if not item_iter in self.tree_items:
            return False

        thread = self.tree_items[item_iter]["thread"]
        thread.setReady (True)

    def get_video_thread (self, item_iter):
        if not item_iter in self.tree_items:
            return None

        thread = self.tree_items[item_iter]["thread"]
        return thread

    def get_thread_id (self, url):
        for element in self.tree_items:
            thread = self.tree_items[element]["thread"]
            if thread and thread.video.parser.page_url == url:
                return element
        return None

    def remove_download (self, item_iter):
        if not item_iter in self.tree_items:
            return

        self.lock.acquire ()
        self.tree_model.remove (item_iter)
        if self.tree_items[item_iter]["thread"].status != VideoDownloadThread.DONE:
            self.tree_items[item_iter]["thread"].cancel ()

        del self.tree_items[item_iter]
        self._num_objects -= 1
        self.lock.release ()

    def finish_download (self, item_iter):
        if not item_iter in self.tree_items:
            return

        if self.tree_items[item_iter]["thread"].status != VideoDownloadThread.DONE:
            self.tree_items[item_iter]["thread"].cancel ()

    def is_empty (self):
        return self._num_objects == 0

    def queue_length (self):
        return self._num_objects

    def swap_items (self, id_item1, id_item2):
        if id_item1 in self.tree_items and id_item2 in self.tree_items:
            self.tree_model.swap (self.tree_items[id_item1]["iter"],
                self.tree_items[id_item2]["iter"])

    def is_queue_active (self):
        for element in self.tree_items.keys ():
            thread = self.tree_items[element]["thread"]
            if thread and thread.isAlive () and (
                thread.status == VideoDownloadThread.READY or
                thread.status == VideoDownloadThread.PARSING):
                return True

        return False

    def clear_complete (self):
        for element in self.tree_items.keys ():
            thread = self.tree_items[element]["thread"]
            if thread and not thread.isAlive ():
                self.remove_download (element)

    def restore_session (self):
        restore_session = SessionInfo ()
        items = restore_session.read ()

        for item in items:
            self.emit ("block-ui")
            self.create_video_thread (item.video, item.status)

    def save_session (self):
        items = []

        def add_items (model, path, iter, item_list):
            url = model.get_value (iter, 0)
            thread_id = self.get_thread_id (url)
            thread = self.get_video_thread (thread_id)
            if thread and (
                thread.status == thread.PAUSED or thread.status == thread.DONE
                or thread.status == thread.CANCELLED
                or thread.status == thread.WAITING):
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

    def is_download_ready (self):
#        self.lock.acquire ()
        self.download_lock.acquire ()
        ready = False
        update_time = (time.time () - self.download_update) > self.__class__.DOWNLOAD_UPDATE_INTERVAL
#        print self.download_limit
        if not update_time and self.download_limit == 0:
            ready = True
        elif not update_time and self.download_speed_total >= self.download_limit:
            ready = False
        elif not update_time and self.download_speed_total < self.download_limit:
            ready = True
        else:
            self.download_update = time.time ()
            self.download_speed_total = 0
            ready = True
        #print "UPDATE TIME: %s" % update_time
        #print "DOWNLOAD LIMIT EXCEED: %s" % self.download_speed_est >= self.download_limit
#        if self.download_limit == 0:
#        if not update_time and self.app_settings.download_speed_limit == 0:
#            ready = True
#        elif not update_time:
#            ready = False
#        elif not update_time and self.download_speed_est >= self.download_limit:
#            sleep_time = self.__class__.DOWNLOAD_UPDATE_INTERVAL - (time.time () - self.download_update)
#            if sleep_time > 0:
#                time.sleep (sleep_time)
#            ready = False
#        elif not update_time and self.download_speed_est > (self.download_limit - (self.__class__.TRANSFER_PER_BLOCK)):
#            sleep_time = self.__class__.DOWNLOAD_UPDATE_INTERVAL - (time.time () - self.download_update)
#            if sleep_time > 0:
#                time.sleep (sleep_time)
#            ready = False
#        elif not update_time and self.download_speed_est < self.download_limit:
#            self.download_speed_est += self.__class__.TRANSFER_PER_BLOCK
#            ready = True
#        else:
#            gtk.gdk.threads_enter ()
#            time_since_speed_update = time.time () - self.download_update
#            speed = self.download_speed_total / time_since_speed_update
#            self.send ("speed_progress_update", "DL Speed: %s/s" % (FileDownloader.humanizeSize (speed),))
            #self.send ("progress_update", "Active: %i of %i" % (self._running_items,self._num_objects))
#            self.download_speed_total = 0
#            gtk.gdk.threads_leave ()

#            self.download_limit = self.__class__.BYTES_PER_KB * self.app_settings.download_speed_limit
#            self.download_update = time.time ()
#            self.download_speed_est = self.__class__.TRANSFER_PER_BLOCK
#            ready = True

#        print "DOWNLOAD_EST: %s" % self.download_speed_est
        #if self.download_limit != 0 and self.download_speed_total > self.download_limit:
        #    print "THIS SHOULD NOT HAPPEN: %s" % self.download_speed_total

#        self.lock.release ()
        self.download_lock.release ()
        return ready

    def update_download_speed (self, block_in_bytes):
#        self.lock.acquire ()
        self.download_lock.acquire ()
#        if not self.download_limit == 0:
#            if block_in_bytes < (self.__class__.TRANSFER_PER_BLOCK):
#                self.download_speed_est -= (self.__class__.TRANSFER_PER_BLOCK) - block_in_bytes

        self.download_speed_total += block_in_bytes
        self.download_lock.release ()
#        self.lock.release ()

    def setDownloadLimit (self, new_limit=-1):
        self.lock.acquire ()
        self.download_lock.acquire ()
        if new_limit <= -1:
            self.download_limit = self.BYTES_PER_KB * self.app_settings.download_speed_limit
        else:
            self.download_limit = self.BYTES_PER_KB * new_limit
        self.download_lock.release ()
        self.lock.release ()
