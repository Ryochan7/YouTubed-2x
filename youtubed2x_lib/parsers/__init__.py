import re
import urllib2
from youtubed2x_lib.other import getPage, PageNotFound
import youtubed2x_lib.mimevault as mimevault

class Parser_Helper (object):
    """Abstract parser class. Updated 01/15/2010"""
    is_portal = False
    parser_type = "Generic"
    host_str = None
    mime_base = mimevault.MimeVault ()

    def __init__ (self, video_id):
        self.video_id = video_id
        self.page_url = self.video_url_str % video_id
        self.embed_file_type = "video/flv" # Normally assumed to be flv if parser does not raise an exception
        self.page_dump = ""


    def __str__ (self):
        return "<%s: %s>" % (self.__class__.parser_type, self.page_url)

    def __repr__ (self):
        return "<%s: %s>" % (self.__class__.parser_type, self.page_url)


    @classmethod
    def getType (cls):
        return cls.parser_type

    def getEmbedType (self):
        return self.embed_file_type


    def setEmbedType (self, embed_type):
        if self.__class__.mime_base.guess_extension (embed_type):
            self.embed_file_type = embed_type


    def getEmbedExtension (self):
        ext = self.__class__.mime_base.guess_extension (self.embed_file_type)
        if not ext:
            ext = ".flv"
        return ext


    class LoginRequired (Exception):
        pass

    class UnknownTitle (Exception):
        pass

    class InvalidCommands (Exception):
        pass

    class URLBuildFailed (Exception):
        pass

    class InvalidPortal (Exception):
        pass


    @classmethod
    def checkURL (cls, url):
        match = cls.const_video_url_re.match (url)
        if match:
            return cls (match.group (1))
        else:
            return None


    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.page_url)
        #self.page_dump = page
        return page, newurl


    def parseVideoPage (self, page_dump=""):
        if not isinstance (page_dump, str):
            raise TypeError ("Argument must be a string representing the HTML code for a page")
        

#        title = self._parseTitle (page_dump)
#        commands = self._parsePlayerCommands (page_dump)

        if not page_dump:
            page_dump, newurl = self.getVideoPage ()

        self.page_dump = page_dump

        title = self._parseTitle ()
        commands = self._parsePlayerCommands ()
        download_url = self._parseRealURL (commands)
        headers = self._getContentInformation (download_url)
        path = urllib2.urlparse.urlparse (download_url).path
        testmime = self.__class__.mime_base.guess_type (path)
        if testmime[0]:
            self.embed_file_type = testmime[0]
        else:
            self.embed_file_type = headers["Content-Type"]

        #print self.embed_file_type
        #print self.getEmbedExtension ()
        return title, download_url, headers


    def _parseTitle (self):
        match = self.video_title_re.search (self.page_dump)
        if not match:
            raise self.__class__.UnknownTitle ("Could not find the title")
        else:
            title = match.group (1)
        return title


    def _parsePlayerCommands (self):
        """Get the commands needed to get the video player"""
        match = self.video_url_params_re.search (self.page_dump)
        if not match:
            raise self.__class__.InvalidCommands ("Could not find flash player commands")
        else:
            commands = match.groups ()
        return commands


    def _getContentInformation (self, url):
        page, newurl, headers = getPage (url, read_page=False, get_headers=True)
        return headers


    def _parseRealURL (self, commands):
        """Abstract function that must be defined in all sub-classes."""
        raise NotImplementedError


    @staticmethod
    def getImageData ():
        raise NotImplementedError


