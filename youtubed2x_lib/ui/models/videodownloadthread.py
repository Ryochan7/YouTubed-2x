import os
import sys
import subprocess
import signal
import re
import time
import gtk
import gobject
import logging
from threading import Thread
import youtubed2x_lib.download as downloader
from youtubed2x_lib.videoitem import VideoItem
from youtubed2x_lib.other import PageNotFound, WINDOWS
from youtubed2x_lib.ui.exceptions.inqueueexception import InQueueException

if WINDOWS:
    import win32process
    import win32api

class VideoDownloadThread (Thread):
    _STATUS_ITEMS = (WAITING, PARSING, READY, CANCELLED, DONE, PAUSED,
        CANCELING) = range (0,7)
    _STATUS_MESSAGES = (_("Queued"), _("Getting Info"), _("Downloading"),
        _("Cancelled"), _("Complete"), _("Paused"), _("Cancelling"))

    SLEEP_HOLD = 1 # In seconds
    SPEED_UPDATE_INTERVAL = .75 # In seconds
    WAIT_DOWNLOAD_INTERVAL = .25 # In seconds

    def __init__ (self, thread_manager, app_settings, video, status=WAITING):
        super (self.__class__, self).__init__ ()
        self._log = logging.getLogger ("{0}.{1}".format (__name__,
            self.__class__.__name__))

        self.setDaemon (True)
        self.video = video
        self.process_id = None
        self.download_id = None
        self._downloader = None
        self._has_sem = False
        self.thread_manager = thread_manager
        self.app_settings = app_settings

        if status in self._STATUS_ITEMS:
            self.status = status
        else:
            raise Exception ("'%s' is not a valid status" % status)

    def run (self):
        try:
            self.download_id = self.thread_manager.add_try (self)
        except InQueueException as exception:
            self._log.info ("Thread already in queue")
            gtk.gdk.threads_enter ()
            self.thread_manager.emit ("unblock-ui")
            gtk.gdk.threads_leave ()
            return

        if self.status == self.DONE:
            self.thread_manager.update_status (self.download_id,
                title=self.video.title, url=self.video.parser.page_url,
                force_update=True)
            self._finish_thread ()
            return
        elif self.status == self.CANCELLED:
            self.thread_manager.update_status (self.download_id,
                title=self.video.title, url=self.video.parser.page_url,
                force_update=True)
            self._finish_thread (_("Cancelling"), False)
            return

        if not self.video.title and not self.video.real_url:
            self.status = self.PARSING
            status, message = self._parsePage ()
            if not status:
                self.status = self.CANCELLED
                self._finish_thread (_("Parse Failed"), False)

                gtk.gdk.threads_enter ()
                self.thread_manager.emit ("unblock-ui")
                gtk.gdk.threads_leave ()
                return
            else:
                self.status = self.WAITING


        if self.video.getFileSize () > 0 and os.path.exists (self.video.flv_file):
            current_file_size = os.path.getsize (self.video.flv_file)
            current_percentage = min (100, current_file_size / float (self.video.getFileSize ()) * 100)
            self.status = self.PAUSED
            self.thread_manager.update_status (self.download_id, title=self.video.title, url=self.video.parser.page_url, progress=current_percentage, size=downloader.FileDownloader.humanizeSize (self.video.getFileSize ()), status=self._STATUS_MESSAGES[self.PAUSED], force_update=True)
        elif self.video.getFileSize () > 0:
            self.thread_manager.update_status (self.download_id, title=self.video.title, url=self.video.parser.page_url, progress=0, size=downloader.FileDownloader.humanizeSize (self.video.getFileSize ()), status=self._STATUS_MESSAGES[self.WAITING], force_update=True)
        else:
            self.thread_manager.update_status (self.download_id, title=self.video.title, url=self.video.parser.page_url, progress=0, size=_("Unknown"), status=self._STATUS_MESSAGES[self.WAITING], force_update=True)

        auto_download = self.app_settings.auto_download
        display_waiting = False
        if auto_download:
            self._has_sem = self.thread_manager.acquire_sem (self.download_id)
            if self._has_sem:
                self.status = self.READY
            else:
                self.thread_manager.update_status (self.download_id, status=_("Waiting"), force_update=True)
                display_waiting = True

        gtk.gdk.threads_enter ()
        self.thread_manager.emit ("unblock-ui")
        gtk.gdk.threads_leave ()

        while self.status != self.READY and self.status != self.CANCELING and not self._has_sem:
            time.sleep (self.SLEEP_HOLD)
            if auto_download:
                self._has_sem = self.thread_manager.acquire_sem (self.download_id)
                if self._has_sem:
                    self.status = self.READY

        # This loop will likely be entered when a user starts
        # a download manually. Make sure to obey process limit
        while not self._has_sem and self.status != self.CANCELING:
            if not display_waiting:
                self.thread_manager.update_status (self.download_id, status=_("Waiting"), force_update=True)
                display_waiting = True

            time.sleep (self.SLEEP_HOLD)
            self._has_sem = self.thread_manager.acquire_sem (self.download_id)


        if self.status == self.CANCELING:
            self.status = self.CANCELLED
            self._finish_thread (self._STATUS_MESSAGES[self.CANCELLED], False)
            if self._has_sem:
                self.thread_manager.release_sem (self.download_id)
            return

        # Refresh GUI for autodownloaded items
        gtk.gdk.threads_enter ()
        self.thread_manager.emit ("unblock-ui")
        gtk.gdk.threads_leave ()

        abitrate = self.app_settings.abitrate
        vbitrate = self.app_settings.vbitrate
        if self.app_settings.format in VideoItem.VIDEO_FORMATS:
            self.video.setOutputRes (self.app_settings.output_res)

        self.video.setFileFormat (self.app_settings.format)

        if self.app_settings.sitedirs:
            if not os.path.isdir (os.path.join (self.app_settings.output_dir, self.video.parser.getType ())):
                try:
                    os.mkdir (os.path.join (self.app_settings.output_dir, self.video.parser.getType ()))
                except OSError:
                    self.status = self.CANCELLED
                    self._finish_thread ("Dir Write Failed", False)
                    return

            self.video.setFilePaths (os.path.join (self.app_settings.output_dir, self.video.parser.getType ()))
        else:
            self.video.setFilePaths (self.app_settings.output_dir)

        transcode = self.app_settings.transcode
        keep_flv_files = self.app_settings.keep_flv_files

        # At this point, self._has_sem will definitely be True
        status = self._startDownload ()

        # Did download fail
        if not status and self.status == self.CANCELING:
            self.status = self.CANCELLED
            self._finish_thread (self._STATUS_MESSAGES[self.CANCELLED], False)
            self.thread_manager.release_sem (self.download_id)
            return
        elif not status:
            self.status = self.CANCELLED
            self._finish_thread (_("Download Failed"), False)
            self.thread_manager.release_sem (self.download_id)
            return

        if self.status == self.CANCELING:
            self.status = self.CANCELLED
            self._finish_thread (self._STATUS_MESSAGES[self.CANCELLED], False)
            self.thread_manager.release_sem (self.download_id)
            return

        # Refresh GUI (particularly for the pause button)
        gtk.gdk.threads_enter ()
        self.thread_manager.emit ("unblock-ui")
        gtk.gdk.threads_leave ()

        #self.thread_manager.release_sem (self.download_id)
        if not transcode:
            self._finish_thread ()
            self.thread_manager.release_sem (self.download_id)
            return

        #self.thread_manager.transcode_semaphore.acquire ()
        if os.path.exists (self.video.avi_file) and not self.app_settings.overwrite:
            self._log.debug ("Output file already exists. Skipping transcode.")
            self._finish_thread ()
            #self.thread_manager.transcode_semaphore.release ()
            self.thread_manager.release_sem (self.download_id)
            return
        elif os.path.exists (self.video.avi_file):
            self._log.debug ("Overwriting old avi file")
            os.remove (self.video.avi_file)

        status = self._startFFmpeg (abitrate, vbitrate)

        # Did ffmpeg fail
        if not status and self.status == self.CANCELING:
            self.status = self.CANCELLED
            self._finish_thread (self._STATUS_MESSAGES[self.CANCELLED], False)
            #self.thread_manager.transcode_semaphore.release ()
            self.thread_manager.release_sem (self.download_id)
            return
        elif not status:
            self.status = self.CANCELLED
            self._finish_thread (_("FFmpeg Failed"), False)
            #self.thread_manager.transcode_semaphore.release ()
            self.thread_manager.release_sem (self.download_id)
            return

        if not keep_flv_files:
            self._log.debug ("Flv video deleted")
            os.remove (self.video.flv_file)

        if self.status == self.CANCELING:
            self.status = self.CANCELLED
            #self.thread_manager.transcode_semaphore.release ()
            self.thread_manager.release_sem (self.download_id)
            return

        self._finish_thread ()
#        self.thread_manager.transcode_semaphore.release ()
        self.thread_manager.release_sem (self.download_id)

    def _finish_thread (self, print_status="Complete", done=True):
        if done:
            self.status = self.DONE

        self.thread_manager.update_status (self.download_id, progress=100, status=print_status, speed="", size="", eta="", force_update=True)

        gtk.gdk.threads_enter ()
        self.thread_manager.emit ("block-ui")
        gtk.gdk.threads_leave ()

    def setReady (self, ready=True):
        if isinstance (ready, bool) and ready:
            self.status = self.READY

    def pause (self):
        if self._downloader:
            self.status = self.PAUSED

    def cancel (self):
        if self._downloader or not self._has_sem:
            self.status = self.CANCELING

        # Process is currently running. Kill process and cancel thread
        elif self.process_id and self.status == self.READY:
            if not WINDOWS:
                os.kill (self.process_id, signal.SIGKILL)
            else:
                handle = win32api.OpenProcess (1, 0, self.process_id)
                win32api.TerminateProcess (handle, 0)

            self.status = self.CANCELING
            self.process_id = None
        # Thread is active but likely transitioning to ffmpeg.
        # Wait and try to cancel
        elif self.status == self.READY:
            gobject.timeout_add (500, self.cancel)
        # Thread should be in a save spot to just set the flag
        else:
            self.status = self.CANCELING


    def _startFFmpeg (self, abitrate, vbitrate):
        testre = re.compile (r'time=(\d+).(\d+)')
        durationre = re.compile (r'Duration: (\d{2}):(\d{2}):(\d{2}).(\d{2})')
        command = None
        process = None

        # Get flv video file information (resolution, framerate)
        try:
            if not WINDOWS:
                process = subprocess.Popen ([self.video.command_dict["application"], "-i", self.video.flv_file], stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            else:
                process = subprocess.Popen ([self.video.command_dict["application"], "-i", self.video.flv_file], stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE, creationflags=win32process.CREATE_NO_WINDOW)
                process.stdout.close ()
                process.stdin.close ()
            process.wait ()
        except OSError:
            return False

        match = VideoItem.resolution_re.search (process.stderr.read ())
        if match:
            vid_length, vid_width = match.groups ()
            #print match.group (0)
            vid_length, vid_width = int (vid_length), int (vid_width)
            command = self.video.buildCommandList (abitrate, vbitrate, vid_length, vid_width)
        else:
            command = self.video.buildCommandList (abitrate, vbitrate)

        if not command:
            return True

        #print command

        duration = None
        percentage = 0

        self.thread_manager.update_status (self.download_id, progress=percentage, status=_("Transcoding"), force_update=True)
        try:
            if not WINDOWS:
                process = subprocess.Popen (command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, close_fds=True)
            else:
                process = subprocess.Popen (command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, creationflags=win32process.CREATE_NO_WINDOW)
                process.stdin.close ()
        except OSError:
            return False

        start_update = time.time ()
        (stdout, stderr) = (process.stdout, process.stderr)
        self.process_id = process.pid
#       print process.poll ()
        message = "Transcoding %s" % self.video.title
        if len (message) > 41:
            message = "%s..." % message[0:38]

        while process.poll () == None:
            msg = stderr.readline ()
#            print msg
            msg = msg.strip ()
            if msg:
                #print msg
                if not duration:
                    match = durationre.match (msg)
                    if match:
                        duration = (int (match.group (1)) * 3600) + (int (match.group (2)) * 60) + (int (match.group (3)))
                        duration = float (duration) + (float (match.group (4)) * .01)
                    continue
                match = testre.search (msg)
                if match:
                    percentage = float (match.group (1))
                    percentage = percentage + (float (match.group (2)) * .01)
                    percentage = int (percentage*100/duration)
                    if percentage > 100:
                        percentage = 100

                    transcode_time = float (match.group (1))
                    transcode_time = transcode_time + (float (match.group (2)) * .01)
                    ffmpeg_eta = (transcode_time) / float (time.time ()-start_update)
                    ffmpeg_eta = (duration - transcode_time) / float (ffmpeg_eta)

                    (remain_hour, tmp_min) = divmod (ffmpeg_eta, 60**2)
                    if remain_hour > 99:
                        remain_hour = 99
                        remain_min = remain_sec = 59
                    else:
                        (remain_min, remain_sec) = divmod (tmp_min, 60)
                    remain_string = "%02d h %02d m %02d s" % (remain_hour, remain_min, remain_sec)

                    self.thread_manager.update_status (self.download_id, progress=percentage, eta=remain_string)

#       print process.poll ()
        self.process_id = None

        if process.poll () == 0 and not WINDOWS:
            self.thread_manager.update_status (self.download_id, progress=100, status=self._STATUS_MESSAGES[self.DONE], eta="", force_update=True)
        elif process.poll () == 0 and self.status != self.CANCELLED:
            self.thread_manager.update_status (self.download_id, progress=100, status=self._STATUS_MESSAGES[self.DONE], eta="", force_update=True)
        else:
            if os.path.exists (self.video.avi_file):
                os.remove (self.video.avi_file)
            return False
        return True

    def _startDownload (self):
        n00b = downloader.FileDownloader (self.video.real_url,
            self.video.flv_file)
        try:
            n00b.open ()
        except downloader.FileExistException as exception:
            self._log.info ("File already exists. Skipping Download")
            return True
        except Exception as exception:
            self._log.exception ("Downloading failed")
            return False

        self._downloader = n00b

        file_size = n00b.getFileSize ()
        initial_size = n00b.getBytesDownloaded ()
        self.video.setFileSize (file_size)

        if file_size > 0:
            self.thread_manager.update_status (self.download_id, size="%s" % n00b.humanizeSize (n00b.getFileSize ()), status=_("Downloading"), force_update=True)
        else:
            # Returned file_size is -1. Unknown file size. Proceed with
            # download but stats can't be updated
            self.thread_manager.update_status (self.download_id, size=_("Unknown"), status=_("Downloading"), force_update=True)

#        self.thread_manager.download_semaphore.acquire ()
#        while not self.thread_manager.is_download_ready ():
#            continue

        last_update = time.time ()
        try:
            data = n00b.readBlock ()
#            self.thread_manager.update_download_speed (len (data))
#            self.thread_manager.download_semaphore.release ()
        except Exception as exception:
            #print >> sys.stderr, "%s" % exception
            sys.stderr.write (exception)
#            self.thread_manager.download_semaphore.release ()
            return False

        # Refresh GUI (particularly for the pause button)
        gtk.gdk.threads_enter ()
        self.thread_manager.emit ("unblock-ui")
        #self.thread_manager.send ("unblock-ui")
        gtk.gdk.threads_leave ()

        total_time = 0
        while self.status == self.PAUSED or (data != "" and self.status == self.READY):
            if self.status == self.PAUSED:
                if n00b:
                    # Pausing download. Have to close current session
                    total_time += (time.time () - last_update)
                    n00b.close ()
                    n00b = None
                    self.thread_manager.update_status (self.download_id, speed="", eta="", status=_("Paused"), force_update=True)
                time.sleep (self.SLEEP_HOLD)
                continue
            # Have to re-open file downloader. Downloader will timeout
            # when resumed after a few seconds,
            # for some reason, if the same session is used.
            elif not n00b:
                try:
                    n00b = self._downloader
                    n00b.open ()
                    self.thread_manager.update_status (self.download_id, speed="", eta="", status=_("Downloading"), force_update=True)
                except downloader.FileExistException as exception:
                    self._log.info ("File already exists. Skipping Download")
                    return True
                except downloader.ResumeFail as exception:
                    self._log.exception ("Resume of download failed")
                    if os.path.exists (self.video.flv_file):
                        try:
                            os.remove (self.video.flv_file)
                        except OSError, IOError:
                            pass
                    return False
                except Exception as exception:
                    self._log.exception ("Download failed")
                    return False

                last_update = time.time ()
                #self.thread_manager.download_semaphore.acquire ()
                #while not self.thread_manager.is_download_ready ():
                #    continue
                try:
                    data = n00b.readBlock ()
                    #self.thread_manager.update_download_speed (len (data))
                    #self.thread_manager.download_semaphore.release ()
                except Exception as exception:
                    self._log.exception ("Could not read block")
                    #self.thread_manager.download_semaphore.release ()
                    return False

            total_time += (time.time () - last_update)
            #print "time.time (): %s" % time.time ()
            #print "last_update: %s" % last_update
            #print "TOTAL TIME: %s" % total_time
            speeda = (n00b.getBytesDownloaded () - initial_size) / total_time
#            speeda = n00b.getBytesDownloaded () / total_time
            percentage = n00b.downloadPercentage ()

            if percentage >= 0:
                self.thread_manager.update_status (self.download_id, progress=n00b.downloadPercentage (), speed="%s/s" % n00b.humanizeSize (speeda), eta=n00b.humanizeTime (speeda))
            else:
                # File size is not known. Update speed only
                self.thread_manager.update_status (self.download_id, progress=0, speed="%s/s" % n00b.humanizeSize (speeda), eta=n00b.humanizeTime (speeda))

            last_update = time.time ()
            #self.thread_manager.download_semaphore.acquire ()
            #while not self.thread_manager.is_download_ready ():
            #    continue

            #self.thread_manager.is_download_ready ()
            try:
                #print "Your mom is a ho"
                data = n00b.readBlock ()
                #self.thread_manager.update_download_speed (len (data))
                #self.thread_manager.download_semaphore.release ()
            except Exception as exception:
                print "%s" % exception
                #self.thread_manager.download_semaphore.release ()
                return False

            #speeda2 = (len (data) / (time.time () - last_update))
            #print "SPEED 2: %s" % speeda2

        self._downloader = None

        if self.status == self.READY and n00b.getBytesDownloaded () == file_size:
            n00b.close ()
        elif self.status == self.READY and file_size == -1:
            n00b.close () # Can only assume file completely downloaded
        elif self.status == self.CANCELING and n00b:
            n00b.cancel () # Download was cancelled while downloading
            self.thread_manager.update_status (self.download_id, speed="", size="", eta="", force_update=True)
            return False
        elif self.status == self.PAUSED and n00b and n00b.getBytesDownloaded () == file_size:
            n00b.close () # Download was paused after file finished downloading
            self.status = self.READY
        elif self.status == self.PAUSED and file_size == -1:
            n00b.close () # Download was paused after file finished
                          # downloading. Can only assume file
                          # completely downloaded
            self.status = self.READY
        else:
            self._log.debug ("Something")
            # Download was cancelled after being paused
            if os.path.exists (self.video.flv_file):
                try:
                    os.remove (self.video.flv_file)
                except OSError, IOError:
                    pass
            self.thread_manager.update_status (self.download_id, speed="", size="", eta="", force_update=True)
            return False

        self.thread_manager.update_status (self.download_id, progress=100, speed="", size="", eta="", force_update=True)
        return True

    def _parsePage (self):
        parser_class = self.video.parser.__class__
        try:
            self.video.getVideoInformation ()
        except (parser_class.UnknownTitle, parser_class.InvalidCommands,
            parser_class.URLBuildFailed, parser_class.InvalidPortal,
            parser_class.LoginRequired) as exception:
            self._log.exception ("Parsing of page failed")
            return False, exception.args
        except PageNotFound as exception:
            self._log.exception ("Page could not be found")
            return False, exception.args
        except Exception as exception:
            self._log.exception ("Unexpected exception while parsing page")
            return False, exception.args

        return True, ""

