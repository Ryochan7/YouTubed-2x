import re
from youtubed2x_lib.parsers import Parser_Helper, getPage


class GiantBomb_Parser (Parser_Helper):
    """Parser for GiantBomb pages. Updated 02/02/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?giantbomb\.com/(\S+)')
    video_url_str = 'http://www.giantbomb.com/%s'
    video_details_url = 'http://www.giantbomb.com/video/params/%s/'
    video_title_re = re.compile (r'<title><!\[CDATA\[([^\[]*)]]></title>')
    video_embed_code_re = re.compile (r'flashvars="paramsURI=http%3A//www.giantbomb.com/video/params/(\d+)/(?:\?w=1)?"')
    video_url_params_re = re.compile (r'<URI bitRate="700">(\S+)</URI>')
    parser_type = "GiantBomb"

    def __init__ (self, video_id):
        super (GiantBomb_Parser, self).__init__ (video_id)


    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.page_url)
        match = self.video_embed_code_re.search (page)
        if match:
            newurl = self.video_details_url % match.group (1)
            page, newurl = getPage (newurl)
        return page, newurl


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0]
        return real_url


