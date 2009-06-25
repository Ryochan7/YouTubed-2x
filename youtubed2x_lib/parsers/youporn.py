import re
from youtubed2x_lib.parsers import Parser_Helper, getPage


class YouPorn_Parser (Parser_Helper):
    """Parser for YouPorn pages. Updated 01/07/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?youporn\.com/watch/(\d+)')
    video_url_str = 'http://www.youporn.com/watch/%s'
    video_url_real_str = 'http://download.youporn.com/download/%s/?%s'
    video_title_re = re.compile (r'<title>([^<]+) - Free Porn Videos - YouPorn.com Lite \(BETA\)</title>')
    video_url_params_re = re.compile (r'<a href="http://download.youporn.com/download/(\d+)/\?(\S+)">FLV - Flash Video format</a>')
    parser_type = "YouPorn"

    def __init__ (self, video_id):
        super (YouPorn_Parser, self).__init__ (video_id)
        self.video_enter_url = self.page_url + '?user_choice=Enter'


    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.video_enter_url)
        return page, newurl


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        page, newurl = getPage (self.video_url_real_str % commands, read_page=False)
        real_url = newurl
        return real_url

