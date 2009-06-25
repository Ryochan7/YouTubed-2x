import re
from youtubed2x_lib.parsers import Parser_Helper, getPage, PageNotFound


class YouTube_Parser (Parser_Helper):
    """Parser for YouTube pages. Updated 03/21/2009"""
    # URLs and RegExp statements from youtube-dl (some slightly modified)
    const_video_url_re = re.compile (r'^(?:http://)?(?:\w+\.)?youtube\.com/(?:v/|(?:watch(?:\.php)?)?\?(?:.+&)?v=)?([0-9A-Za-z_-]+)(?(1)[&/].*)?$')
    video_url_str = 'http://www.youtube.com/watch?v=%s'
    video_url_real_str = 'http://www.youtube.com/get_video?video_id=%s&t=%s'
#    video_url_real_high_str = 'http://www.youtube.com/get_video?video_id=%s&t=%s&fmt=6' # Format seems to no longer exist
    video_url_real_high_str = 'http://www.youtube.com/get_video?video_id=%s&t=%s&fmt=18'
    video_title_re = re.compile (r'<title>YouTube - ([^<]*)</title>')
    video_url_params_re = re.compile (r', "t": "([^"]+)"')
#    video_high_quality_re = re.compile (r'onclick\="changeVideoQuality\(yt\.VideoQualityConstants\.HIGH\); urchinTracker\(\'/Events/VideoWatch/QualityChangeToHigh\'\); return false;">watch in high quality</a>')
    login_required_re = re.compile (r"^http://www.youtube.com/verify_age\?next_url=/watch")
    login_page = "http://www.youtube.com/signup"
    embed_file_extensions = {"video/flv": "flv", "video/mp4": "mp4"}
    parser_type = "YouTube"

    def __init__ (self, video_id):
        super (YouTube_Parser, self).__init__ (video_id)
        self.has_high_version = False


    def getVideoPage (self, account="", password=""):
        if not isinstance (account, str) or not isinstance (password, str):
            raise TypeError ("Passed arguments must be strings")

        if account and password:
            data = {"username": account, "password": password, "action_login": "Log In"}
            page, newurl = getPage (self.login_page, data)
            page, newurl = getPage (self.page_url)
            data = {"next_url": self.page_url, "action_confirm": "Confirm Birth Date"}
            page, newurl = getPage (newurl, data)
            return page, newurl
        elif account or password:
           raise TypeError ("When passing arguments, account name and password must be defined")

        page, newurl = getPage (self.page_url)
        if self.login_required_re.match (newurl):
            raise self.__class__.LoginRequired ("You must be logged in to access this video")
        return page, newurl

    def _parsePlayerCommands (self, page_dump):
        """Get the commands needed to get the video player"""
        match = self.video_url_params_re.search (page_dump)
        if not match:
            raise self.__class__.InvalidCommands ("Could not find flash player commands")

        commands = match.groups ()
        return commands

    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        # First, attempt to get a high quality version
        secondary_url = self.video_url_real_high_str % (self.video_id, commands[0])
        obtained_url = False
        content_type = self.embed_file_type
        try:
            page, real_url, content_type = getPage (secondary_url, read_page=False, get_content_type=True)
            obtained_url = True
        except PageNotFound, e:
            pass

        # Get standard quality if no high quality video exists
        if not obtained_url:
            secondary_url = self.video_url_real_str % (self.video_id, commands[0])
            page, real_url = getPage (secondary_url, read_page=False)

        # Test should not be necessary if it got this far
        if content_type not in ["video/flv", "video/mp4"]:
            raise self.__class__.URLBuildFailed ("An unexpected content type was found. Found: %s" % content_type)
        else:
            self.embed_file_type = content_type

        self.real_url = real_url
        return real_url

