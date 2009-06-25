import re
from youtubed2x_lib.parsers import Parser_Helper

class Guba_Parser (Parser_Helper):
    """Parser for Guba pages. Updated 06/17/2008"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?guba\.com/watch/(\d+)')
    video_url_str = 'http://www.guba.com/watch/%s'
    video_title_re = re.compile (r'var theName="([\S ]+)";')
    video_url_params_re = re.compile (r'"(\S+)" \);\r\n(?:[ ]{32})bfp.writeBlogFlashPlayer\(\);')
    parser_type = "Guba"

    def __init__ (self, video_id):
        super (Guba_Parser, self).__init__ (video_id)


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0]
        return real_url


