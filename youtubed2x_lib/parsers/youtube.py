import re
import datetime
import urllib2
from youtubed2x_lib.parsers import Parser_Helper, getPage, PageNotFound


class YouTube_Parser (Parser_Helper):
    """Parser for YouTube pages. Updated 01/15/2010"""
    # URLs and RegExp statements from youtube-dl (some slightly modified)
    const_video_url_re = re.compile (r'^(?:http://)?(?:\w+\.)?youtube\.com/(?:v/|(?:watch(?:\.php)?)?\?(?:.+&)?v=)?([0-9A-Za-z_-]+)(?(1)[&/].*)?$')
    video_url_str = 'http://www.youtube.com/watch?v=%s'
    video_url_real_str = 'http://www.youtube.com/get_video?video_id=%s&t=%s'
    video_url_real_high_str = "%s&fmt=18" % video_url_real_str
    video_embed_info_url = "http://www.youtube.com/get_video_info?&video_id=%s&el=embedded"

    video_title_re = re.compile (r'<link rel="alternate" type="application/json\+oembed" href="(?:.*)" title="([^<]*)"(?:[ ]+)?/>')
    video_url_params_re = re.compile (r', "t": "([^"]+)"')
    login_required_re = re.compile (r"^http://www.youtube.com/verify_age\?(?:&)?next_url=/watch")
    video_embed_video_re = re.compile (r"status=ok&.*author=(?:[^&]+)&watermark=.*&token=([^&]+)&thumbnail_url")
    video_embed_title_re = re.compile (r"&title=(\S+)&ftoken=")

    parser_type = "YouTube"
    domain_str = "http://www.youtube.com/"
    host_str = "youtube.com"
    version = datetime.date (2010, 1, 15)


    def __init__ (self, video_id):
        super (YouTube_Parser, self).__init__ (video_id)
        self.has_high_version = False
        self.requires_login = False


    def getVideoPage (self, account="", password=""):
        if not isinstance (account, str) or not isinstance (password, str):
            raise TypeError ("Passed arguments must be strings")

        page, newurl = getPage (self.page_url)

        # If login information is required,
        # use the information used for the embed player
        if self.__class__.login_required_re.match (newurl):
            self.requires_login = True
            embed_info_url = self.__class__.video_embed_info_url % self.video_id
            page, newurl = getPage (embed_info_url)
            page = urllib2.unquote (page)

        return page, newurl


    def _parseTitle (self):
        if self.requires_login:
            match = self.__class__.video_embed_title_re.search (self.page_dump)
            if match:
                title = match.group (1)
                title = title.replace ("+", " ")
            else:
                raise self.__class__.UnknownTitle ("Could not find the title from embed information")

        else:
            match = self.__class__.video_title_re.search (self.page_dump)
            if not match:
                raise self.__class__.UnknownTitle ("Could not find the title from page")
            else:
                title = match.group (1)

        return title


    def _parsePlayerCommands (self):
        """Get the commands needed to get the video player"""
        if self.requires_login:
            newmatch = self.__class__.video_embed_video_re.search (self.page_dump)
#            print page_dump
            if newmatch:
#                print newmatch.groups ()
                commands = newmatch.groups ()
            else:
                raise self.__class__.InvalidCommands ("Could not find token from embed player")
        else:
            match = self.__class__.video_url_params_re.search (self.page_dump)
            if not match:
                raise self.__class__.InvalidCommands ("Could not find flash player commands")

            commands = match.groups ()
        return commands


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        token = commands[0]
        # First, attempt to get a high quality version
        secondary_url = self.__class__.video_url_real_high_str % (self.video_id, token)
        obtained_url = False
        content_type = self.embed_file_type

        try:
            page, real_url, headers = getPage (secondary_url, read_page=False, get_headers=True)
            obtained_url = True
        except PageNotFound, e:
            pass

        # Get standard quality if no high quality video exists
        if not obtained_url:
            secondary_url = self.__class__.video_url_real_str % (self.video_id, token)
            page, real_url, headers = getPage (secondary_url, read_page=False, get_headers=True)

        # Test should not be necessary if it got this far
        if headers["Content-Type"] not in ["video/flv", "video/x-flv", "video/mp4"]:
            raise self.__class__.URLBuildFailed ("An unexpected content type was found. Found: %s" % headers["Content-Type"])
        else:
            self.embed_file_type = headers["Content-Type"]

        self.real_url = secondary_url
        return secondary_url


    @staticmethod
    def getImageData ():
        image_data = "\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\x00\x01\x00\xff\xfd\xfe\xfb\xff\x00\x01\x00\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xda\xd4\xd1\xff\x00\x01\x00\xff\xa0\xa2\x9f\xff\x00\x01\x00\xff\xda\xd4\xd1\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xffSUR\xff\x00\x01\x00\xffSUR\xff\xfd\xfe\xfb\xff!# \xff\x00\x01\x00\xff!# \xff\xfd\xfe\xfb\xff\x00\x01\x00\xff\xda\xd4\xd1\xff\x10\x12\x0f\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\x00\x01\x00\xff\xda\xd4\xd1\xff\xfd\xfe\xfb\xff!# \xff\xfd\xfe\xfb\xff\x10\x12\x0f\xff\xa0\xa2\x9f\xff\x00\x01\x00\xff\xda\xd4\xd1\xff\x00\x01\x00\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\x00\x01\x00\xff\xda\xd4\xd1\xff\xfd\xfe\xfb\xff!# \xff\xda\xd4\xd1\xff!# \xff\xda\xd4\xd1\xff\x00\x01\x00\xff\xa0\xa2\x9f\xff\x00\x01\x00\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\x00\x01\x00\xff\xda\xd4\xd1\xff\xfd\xfe\xfb\xff!# \xff\x00\x01\x00\xff!# \xff\xfd\xfe\xfb\xff!# \xff\x00\x01\x00\xff\x00\x01\x00\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xff\xad\xad\xff\xff-0\xff\xff\n\x0f\xff\xff-0\xff\xff-0\xff\xff-0\xff\xff-0\xff\xff\n\x0f\xff\xff-0\xff\xffPO\xff\xff||\xff\xff\xd0\xd0\xff\xff\xd0\xd0\xff\xff\xad\xad\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xff\n\x0f\xff\xff\xd0\xd0\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xff-0\xff\xff\n\x0f\xff\xff\n\x0f\xff\xfd\xfe\xfb\xff\xff-0\xff\xff\n\x0f\xff\xff\n\x0f\xff\xff-0\xff\xff\xad\xad\xff\xff||\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xff-0\xff\xff\n\x0f\xff\xfd\xfe\xfb\xff\xffPO\xff\xffPO\xff\xffPO\xff\xff-0\xff\xff\xe2\xe0\xff\xff\xad\xad\xff\xff-0\xff\xff\n\x0f\xff\xff\xad\xad\xff\xff-0\xff\xff-0\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xff-0\xff\xff\n\x0f\xff\xfd\xfe\xfb\xff\xff\n\x0f\xff\xff\xe2\xe0\xff\xff\xad\xad\xff\xff\xad\xad\xff\xff\xad\xad\xff\xfd\xfe\xfb\xff\xff\xad\xad\xff\xff\xad\xad\xff\xff\xd0\xd0\xff\xff\xe2\xe0\xff\xff\n\x0f\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xff-0\xff\xff\n\x0f\xff\xfd\xfe\xfb\xff\xff-0\xff\xff\xd0\xd0\xff\xff||\xff\xff\xad\xad\xff\xff\xad\xad\xff\xffde\xff\xff\xad\xad\xff\xff\xad\xad\xff\xff\xe2\xe0\xff\xff\xe2\xe0\xff\xff\n\x0f\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xff-0\xff\xff\n\x0f\xff\xfd\xfe\xfb\xff\xff-0\xff\xff\xd0\xd0\xff\xffde\xff\xff\xad\xad\xff\xff\xad\xad\xff\xffde\xff\xff\xad\xad\xff\xff\xd0\xd0\xff\xffPO\xff\xff||\xff\xff\n\x0f\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xff-0\xff\xff\n\x0f\xff\xfd\xfe\xfb\xff\xff-0\xff\xff\xd0\xd0\xff\xfd\xfe\xfb\xff\xff\xad\xad\xff\xff\xad\xad\xff\xfd\xfe\xfb\xff\xff\xad\xad\xff\xff||\xff\xfd\xfe\xfb\xff\xff\xe2\xe0\xff\xff\n\x0f\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xffde\xff\xff-0\xff\xffPO\xff\xff-0\xff\xff-0\xff\xffPO\xff\xff-0\xff\xff-0\xff\xffPO\xff\xff-0\xff\xff\n\x0f\xff\xffde\xff\xff-0\xff\xffPO\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff\xff||\xff\xffde\xff\xffde\xff\xffde\xff\xffde\xff\xffPO\xff\xffde\xff\xffPO\xff\xffde\xff\xff||\xff\xffde\xff\xff||\xff\xfd\xfe\xfb\xff\xfd\xfe\xfb\xff"

        return image_data


