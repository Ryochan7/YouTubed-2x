import urllib2
import os
import math
#import shutil
from other import USER_AGENT

class FileExistException (Exception):
    pass

class NoSessionException (Exception):
    pass

class ActiveSessionException (Exception):
    pass

class ResumeFail (Exception):
    pass


class FileDownloader (object):
    BYTES_PER_KB = 1024 # 1 KB
    TRANSFER_PER_BLOCK = BYTES_PER_KB * 5 # 5 KB
    TMP_EXTENSION = ".tmp"
    SECONDS_PER_MINUTE = 60
    SECONDS_PER_HOUR = SECONDS_PER_MINUTE**2
    UNKNOWN_FILESIZE = -1

    def __init__ (self, url, output_file_path):
        self.url = url
        self.output_file_path = output_file_path
        self._output_file = None
        self._request = urllib2.Request (url)
        self._request.add_header ("User-Agent", USER_AGENT)
        self._handler = None
        self._bytes_downloaded = 0
        self._filesize = self.__class__.UNKNOWN_FILESIZE # Use -1 when file size is unknown


    def setFileLocation (self, path):
        self.output_file_path = path


    def open (self):
        if self._handler is not None:
            raise ActiveSessionException ("Request is already open")

        if os.path.exists (self.output_file_path):
            file_size = os.path.getsize (self.output_file_path)
            self._request.add_header ("Range", "bytes=%s-" % (file_size))
            try:
                self._handler = urllib2.urlopen (self._request)
            except urllib2.HTTPError as exception:
                if exception.code == 416:
                    raise FileExistException ("File already exists and assumed fully downloaded")
                else:
                    raise exception

            content_range = self._handler.info ().get ("Content-Range", None)
            if content_range:
                self._filesize = long (content_range.split ('/')[1])
            else:
                self._filesize = long (self._handler.info ().get ("Content-Length", self.__class__.UNKNOWN_FILESIZE))

            if content_range and self._filesize == file_size:
                self._handler.close ()
                self._handler = None
                raise FileExistException ("File already exists")
            elif content_range:
                self._output_file = open (self.output_file_path, 'ab')
                self._bytes_downloaded = file_size
            elif self._filesize == file_size:
                self._handler.close ()
                self._handler = None
                raise FileExistException ("File already exists")
            else:
                self._handler.close ()
                self._handler = None
                raise ResumeFail ("Could not resume file download")
                
        else:
            self._handler = urllib2.urlopen (self._request)
            self._output_file = open (self.output_file_path, 'wb')
            self._filesize = long (self._handler.info ().get ("Content-Length", self.__class__.UNKNOWN_FILESIZE))


    def readBlock (self):
        if self._handler is None:
            raise NoSessionException ("No open request initiated")

        data = self._handler.read (self.__class__.TRANSFER_PER_BLOCK)
        self._bytes_downloaded += len (data)
        self._output_file.write (data)
        return data


    def getFileSize (self):
        if self._handler:
            return self._filesize # Return -1 if content length is unknown
        else:
            raise NoSessionException ("No open request initiated")


    def getBytesDownloaded (self):
        return self._bytes_downloaded


    def downloadPercentage (self):
        file_size = self.getFileSize ()
        if file_size > 0:
            return long (self._bytes_downloaded / float (file_size) * 100)
        else:
            return self.__class__.UNKNOWN_FILESIZE


    def close (self):
        if self._handler:
            self._handler.close ()
            self._handler = None
            self._bytes_downloaded = 0
            self._output_file.close ()
            self._filesize = self.__class__.UNKNOWN_FILESIZE
            #shutil.move (self.output_file_path, self.output_file_path)
        else:
            raise NoSessionException ("No open request initiated")


    @classmethod
    def humanizeSize (cls, size):
        if size == 0:
            exponent = 0
        else:
            exponent = long (math.log (float (size), cls.BYTES_PER_KB))

        suf_str = "BKMGTPEZY"
        if exponent < len (suf_str):
            suffix = suf_str[exponent]
        else:
            suffix = '?'

        remain = size / float (cls.BYTES_PER_KB**exponent)
        if exponent == 0:
            size_str = "%.2f %s" % (remain, suffix)
        else:
            size_str = "%.2f %sB" % (remain, suffix)
        return size_str


    def humanizeTime (self, speed):
        if speed <= 0:
            raise Exception ("Speed must be greater than zero")
        file_size = self.getFileSize ()
        if file_size < 0:
            return "? h ? m ? s"

        time_in_seconds = (file_size - self.getBytesDownloaded ()) / speed
        (remain_hour, tmp_min) = divmod (time_in_seconds, self.__class__.SECONDS_PER_HOUR)
        if remain_hour > 99:
            remain_hour = 99
            remain_min = remain_sec = 59
        else:
            (remain_min, remain_sec) = divmod (tmp_min, self.__class__.SECONDS_PER_MINUTE)
        remain_string = "%02d h %02d m %02d s" % (remain_hour, remain_min, remain_sec)
        return remain_string


    def cancel (self):
        self.close ()
        os.remove (self.output_file_path)


