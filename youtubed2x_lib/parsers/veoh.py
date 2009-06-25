import re
from youtubed2x_lib.parsers import Parser_Helper, getPage


class Veoh_Parser (Parser_Helper):
    """Parser for Veoh pages. Updated 06/07/2008"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?veoh\.com/videos/(\w+)')
    video_url_str = 'http://www.veoh.com/videos/%s'
    video_detail_url = 'http://www.veoh.com/rest/video/%s/details'
    video_title_re = re.compile (r'\ttitle="(.*)"')
    video_url_params_re = re.compile (r'fullPreviewHashPath="(\S+)"')
    extern_content_re = re.compile (r'<contentSource id=')
    forward_link_re = re.compile (r'aowPermalink="(\S+)"')
    is_portal = True
    parser_type = "Veoh"


    def __init__ (self, video_id):
        Parser_Helper.__init__ (self, video_id)
        self.details_url = self.video_detail_url % video_id


    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.details_url)
        match = self.extern_content_re.search (page)
        if match:
            content_match = self.forward_link_re.search (page)
            page = ""
            newurl = content_match.group (1)
        return page, newurl

    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        secondary_url = commands[0]
        # Follow redirect
        page, real_url = getPage (secondary_url, read_page=False)
        return real_url


