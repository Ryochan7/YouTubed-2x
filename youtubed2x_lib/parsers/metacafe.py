import re
import datetime
from urllib2 import unquote
from youtubed2x_lib.parsers import Parser_Helper


class Metacafe_Parser (Parser_Helper):
    """Parser for Metacafe pages. Updated 07/04/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?metacafe\.com/watch/(\S+)/(?:\w+)?')
    video_url_str = 'http://www.metacafe.com/watch/%s/'
    video_title_re = re.compile (r'<title>([^<]*) - Video</title>')
    video_url_params_re = re.compile (r"mediaURL=(\S+)&postRollContentURL=")
    parser_type = "Metacafe"
    domain_str = "http://www.metacafe.com/"
    host_str = "metacafe.com"
    version = datetime.date (2009, 11, 28)


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = "%s" % unquote (commands[0])
        return real_url


    @staticmethod
    def getImageData ():
        image_data = """\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\x7f p\xf4\x7f \xdf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\x7f \xcf\xf4\x7f \xff\xf4\x7f 0\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\x7f  \xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \x80\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\x7f p\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xcf\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\x7f \xcf\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f  \x00\x00\x00\x00\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\x7f \x10\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f p\x00\x00\x00\x00\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\x7f `\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xef\xf4\x7f \xff\xf4\x7f \xcf\x00\x00\x00\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xf4\x7f \xbf\xf4\x7f \xff\xf4\x7f \xdf\xff\xff\xff\x00\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f  \xff\xff\xff\x00\xf4\x7f \xef\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xff\xff\xff\x00\xff\xff\xff\x00\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f p\xff\xff\xff\x00\xf4\x7f 0\xf4\x7f \xcf\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xff\xff\xff\x00\xefF#\xef\xff\xff\xff\x00\xf4\x7f \xff\xf4\x7f \xcf\xff\xff\xff\x00\x00\x00\x00\x00\xf4\x7f \x10\xf4\x7f \x8f\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xff\xff\xff\x00\xff\xff\xff\x00\xff\xff\xff\x00\xefF#\xdf\xefF#\xff\xefF#\xdf\xff\xff\xff\x00\xefF#p\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\x7f P\xf4\x7f \xef\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xcf\xff\xff\xff\x00\xefF#\xff\xefF#\xff\xefF#\xff\xefF#\xff\xefF#\xcf\xefF#0\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\x7f  \xf4\x7f \xbf\xf4\x7f \xff\xf4\x7f \xff\xf4\x7f \xff\xff\xff\xff\x00\xefF#\xff\xefF#\xff\xefF#\xef\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\x7f \x80\xf4\x7f \xff\xf4\x7f \xff\xff\xff\xff\x00\xefF#\xef\xefF#\xbf\xefF#\xff\xefF#0\x00\x00\x00\x00"""

        return image_data


