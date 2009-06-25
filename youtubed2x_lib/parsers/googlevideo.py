import re
from youtubed2x_lib.parsers import Parser_Helper, getPage


class GoogleVideo_Parser (Parser_Helper):
    """Parser for GoogleVideo pages. Updated 05/28/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?video\.google\.com/videoplay\?docid=((?:-)?\d+)')
    video_url_str = 'http://video.google.com/videoplay?docid=%s'
    video_title_re = re.compile (r'<title>([^<]*)</title>')
    video_url_params_re = re.compile (r"<a href=(?:\")?(http://v(\d+)\.(\S+)\.googlevideo.com/videoplayback\?(\S+))(?:\")?>")
    forward_link_re = re.compile (r"document.getElementById\('external_page'\)\.src = \"(\S+)\";")
    embed_file_extensions = {"video/mp4": "mp4"}
    parser_type = "GoogleVideo"

    def __init__ (self, video_id):
        super (GoogleVideo_Parser, self).__init__ (video_id)
        self.embed_file_type = "video/mp4"


    # TODO: CHANGE TO REFLECT NO PORTAL SUPPORT
    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.page_url)
        match = self.forward_link_re.search (page)
        if match:
            page = ""
            newurl = match.group (1)
        return page, newurl


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        #from urllib2 import unquote
        #real_url = unquote (commands[0])
        real_url = commands[0]
        return real_url


