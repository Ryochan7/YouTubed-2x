import re
from youtubed2x_lib.parsers import Parser_Helper, getPage


class PacoPorn_Parser (Parser_Helper):
    """Parser for PacoPorn pages. Updated 06/03/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?pacoporn\.com/viewVideo\.php\?video_id=(\d+)(?:&title=(\S+))?')
    domain_str = "http://www.pacoporn.com/"
    video_url_str = 'http://www.pacoporn.com/viewVideo.php?video_id=%s'
    video_details_url_str = "http://www.pacoporn.com/videoConfigXmlCode.php?pg=video_%s_no_0"
    video_title_re = re.compile (r'TEXT Name=\"Header\" Value=\"([\S ]+)\" Enable=')
    video_url_params_re = re.compile (r'PLAYER_SETTINGS Name=\"FLVPath\" Value=\"(\S+)\"')
    parser_type = "PacoPorn"


    def __init__ (self, video_id):
        super (PacoPorn_Parser, self).__init__ (video_id)


    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.__class__.video_details_url_str % self.video_id)
        return page, newurl


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0]
        return real_url


