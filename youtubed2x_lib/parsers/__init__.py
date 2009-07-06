import re
from youtubed2x_lib.other import getPage, PageNotFound

class Parser_Helper (object):
    """Abstract parser class. Updated 07/04/2009"""
    is_portal = False
    embed_file_extensions = {"video/flv": "flv"} # Most supported sites only distribute flv files
    parser_type = "Generic"
    host_str = None

    def __init__ (self, video_id):
        self.video_id = video_id
        self.page_url = self.video_url_str % video_id
        self.embed_file_type = "video/flv" # Normally assumed to be flv if parser does not raise an exception


    def __str__ (self):
        return "<%s: %s>" % (self.__class__.parser_type, self.page_url)

    def __repr__ (self):
        return "<%s: %s>" % (self.__class__.parser_type, self.page_url)


    @classmethod
    def getType (cls):
        return cls.parser_type

    def getEmbedType (self):
        return self.embed_file_type

    def getEmbedExtension (self):
        return self.__class__.embed_file_extensions.get (self.embed_file_type, "flv")

    def getImageString (self):
        return "%s.png" % self.__class__.parser_type


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
        return page, newurl


    def parseVideoPage (self, page_dump):
        if not isinstance (page_dump, str):
            raise TypeError ("Argument must be a string representing the HTML code for a page")

        title = self._parseTitle (page_dump)
        commands = self._parsePlayerCommands (page_dump)
        download_url = self._parseRealURL (commands)
        return title, download_url


    def _parseTitle (self, page_dump):
        match = self.video_title_re.search (page_dump)
        if not match:
            raise self.__class__.UnknownTitle ("Could not find the title")
        else:
            title = match.group (1)
        return title


    def _parsePlayerCommands (self, page_dump):
        """Get the commands needed to get the video player"""
        match = self.video_url_params_re.search (page_dump)
        if not match:
            raise self.__class__.InvalidCommands ("Could not find flash player commands")
        else:
            commands = match.groups ()
        return commands


    def _parseRealURL (self, commands):
        """Abstract function that must be defined in all sub-classes."""
        raise NotImplementedError


    @staticmethod
    def getImageData ():
        raise NotImplementedError


