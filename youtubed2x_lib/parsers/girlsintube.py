import re
import datetime
from youtubed2x_lib.parsers import Parser_Helper, getPage


class GirlsInTube_Parser (Parser_Helper):
    """Parser for GirlsInTube pages. Updated 01/15/2010"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?girlsintube\.com/(\S+.\d+)')
    video_url_str = 'http://girlsintube.com/%s'
    video_url_age_post = {'year': '1929', 'month': '1', 'day': '1', 'prescreen_submit': 'Continue'}

    video_title_re = re.compile (r'<div class="player-comments"> <h1>([\S ]+)</h1> ')
    video_url_params_re = re.compile (r"{ 'clip': {'url': '(\S+)', ")

    parser_type = "GirlsInTube"
    domain_str = "http://www.girlsintube.com/"
    host_str = "girlsintube.com"
    version = datetime.date (2010, 1, 15)


    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.page_url)
        page, newurl = getPage (self.page_url, self.video_url_age_post)
        return page, newurl


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0]
        return real_url


    @staticmethod
    def getImageData ():
        image_data = """\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd90Y\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc5.K\xff\xcf6Z\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xad\x1f2\xff\xab#6\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe7r\x90\xff\xac%7\xff\xad\';\xff\xb74L\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc8AX\xff\xae%7\xff\xad\';\xff\xab(=\xff\xc2\'I\xff\xc2\'I\xff\xc0)J\xff\xbd)J\xff\xba*J\xff\xc0-L\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe5\x1dP\xff\xd3 F\xff\xb9"7\xff\xad#3\xff\xae%7\xff\xb0/B\xff\xd8\x9b\xa4\xff\xbdXj\xff\xaa*C\xff\xa9+G\xff\xa7,I\xff\xbe7V\xff\x00\x00\x00\x00\x00\x00\x00\x00\xe9%X\xff\xb0\x1f%\xff\xaf!(\xff\xb0#.\xff\xaf#0\xff\xae%5\xff\xc8my\xff\xccy\x85\xff\xa5\x16-\xff\xc2du\xff\xaa*C\xff\xa9+G\xff\xb54R\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe8<j\xff\xbc\x1c/\xff\xb0#.\xff\xaf#0\xff\xaa\x19*\xff\xd8\x97\xa0\xff\xad\';\xff\xb4<O\xff\xa9%>\xff\xaa*C\xff\xab*F\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd14T\xff\xac#/\xff\xcbr|\xff\xa9\x19+\xff\xad\';\xff\xef\xd7\xdb\xff\xb2:P\xff\xaa*C\xff\xcd?^\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcb)H\xff\xb9?M\xff\xd8\x97\xa0\xff\xc0Xh\xff\xa7\x1a1\xff\xdd\xa9\xb3\xff\xaa*C\xff\xc3Um\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc4(C\xff\xae%5\xff\xad\x1f2\xff\xad\';\xff\xab(=\xff\xaa(>\xff\xaa*C\xff\xa9(C\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xbe\x1e7\xff\xae%5\xff\xae%7\xff\xb8%@\xff\xcd$K\xff\xb2(B\xff\xa8*C\xff\xa8*E\xff\xcdCa\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xba 6\xff\xac$1\xff\xcf"I\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xce&L\xff\xc0)J\xff\xbf3R\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xbe 9\xff\xdc!P\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"""

        return image_data


