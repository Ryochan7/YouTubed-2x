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


class FileDownloader (object):
    BYTES_PER_KB = 1024 # 1 KB
    TRANSFER_PER_BLOCK = BYTES_PER_KB * 5 # 5 KB
    TMP_EXTENSION = ".tmp"

    def __init__ (self, url, output_file_path):
        self.url = url
        self.output_file_path = output_file_path
        self._output_file = None
        self._request = urllib2.Request (url)
        self._request.add_header ("User-Agent", USER_AGENT)
        self._handler = None
        self._bytes_downloaded = 0


    def setFileLocation (self, path):
        self.output_file_path = path


    def open (self):
        if self._handler is None:
            self._handler = urllib2.urlopen (self._request)
        else:
            raise ActiveSessionException ("Request is already open")

        if os.path.exists (self.output_file_path):
            raise FileExistException ("File already exists")
        else:
            self._output_file = open (self.output_file_path, 'wb')


    def readBlock (self):
        if self._handler is None:
            raise NoSessionException ("No open request initiated")

        data = self._handler.read (self.__class__.TRANSFER_PER_BLOCK)
        self._bytes_downloaded += len (data)
        self._output_file.write (data)
        return data


    def getFileSize (self):
        if self._handler:
            return long (self._handler.info ().get ("Content-Length", -1)) # Return -1 if content length is unknown
        else:
            raise NoSessionException ("No open request initiated")


    def getBytesDownloaded (self):
        return self._bytes_downloaded


    def downloadPercentage (self):
        file_size = self.getFileSize ()
        if file_size > 0:
            return long (self._bytes_downloaded / float (file_size) * 100)
        else:
            return -1


    def close (self):
        if self._handler:
            self._handler.close ()
            self._handler = None
            self._bytes_downloaded = 0
            self._output_file.close ()
            #shutil.move (self.output_file_path, self.output_file_path)
        else:
            raise NoSessionException ("No open request initiated")


    def humanizeSize (self, size):
        if size == 0:
            exponent = 0
        else:
            exponent = long (math.log (float (size), self.__class__.BYTES_PER_KB))

        suf_str = "BKMGTPEZY"
        if exponent < len (suf_str):
            suffix = suf_str[exponent]
        else:
            suffix = '?'

        remain = size / float (self.__class__.BYTES_PER_KB**exponent)
        if exponent == 0:
            size_str = "%.2f %s" % (remain, suffix)
        else:
            size_str = "%.2f %sB" % (remain, suffix)
        return size_str


    def cancel (self):
        self.close ()
        os.remove (self.output_file_path)


