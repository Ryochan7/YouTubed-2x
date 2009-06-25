import re
from youtubed2x_lib.parsers import Parser_Helper, getPage


class GirlsInTube_Parser (Parser_Helper):
    """Parser for GirlsInTube pages. Updated 02/22/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?girlsintube\.com/(\S+.\d+)')
    video_url_str = 'http://girlsintube.com/%s'
    video_url_age_post = {'year': '1929', 'month': '1', 'day': '1', 'prescreen_submit': 'Continue'}
    video_title_re = re.compile (r'<div class="player-comments"> <h1>([\S ]+)</h1> ')
    video_url_params_re = re.compile (r"{ 'clip': {'url': '(\S+)', ")
    parser_type = "GirlsInTube"

    def __init__ (self, video_id):
        super (GirlsInTube_Parser, self).__init__ (video_id)


    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.page_url)
        page, newurl = getPage (self.page_url, self.video_url_age_post)
        return page, newurl


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0]
        return real_url


