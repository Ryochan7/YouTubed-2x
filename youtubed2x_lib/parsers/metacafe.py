import re
from youtubed2x_lib.parsers import Parser_Helper


class Metacafe_Parser (Parser_Helper):
    """Parser for Metacafe pages. Updated 01/07/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?metacafe\.com/watch/(\S+)/(?:\w+)?')
    video_url_str = 'http://www.metacafe.com/watch/%s/'
    video_title_re = re.compile (r'<title>([^<]*) - Video</title>')
    video_url_params_re = re.compile (r"mediaURL=(\S+)&gdaKey=(\w+)&postRollContentURL=")
    parser_type = "Metacafe"

    def __init__ (self, video_id):
        super (Metacafe_Parser, self).__init__ (video_id)


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        from urllib2 import unquote
        real_url = "%s?__gda__=%s" % (unquote (commands[0]), commands[1])
        return real_url


