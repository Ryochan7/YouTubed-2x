import re
from youtubed2x_lib.parsers import Parser_Helper


class Tube8_Parser (Parser_Helper):
    """Parser for Tube8 pages. Updated 07/26/2008"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?tube8\.com/(\S+/\S+/\d+)(?:/)?$')
    video_url_str = 'http://www.tube8.com/%s/'
    video_title_re = re.compile (r'">([\S ]+)</h1>')
    video_url_params_re = re.compile (r'param name="FlashVars" value="videoUrl=(\S+)&imageUrl=')
    parser_type = "Tube8"

    def __init__ (self, video_id):
        super (Tube8_Parser, self).__init__ (video_id)


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0]
        return real_url


