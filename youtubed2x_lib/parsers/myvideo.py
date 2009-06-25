import re
from youtubed2x_lib.parsers import Parser_Helper


class MyVideo_Parser (Parser_Helper):
    """Parser for MyVideo pages. Updated 01/08/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?myvideo\.de/watch/(\d+)(?:/\S+)?$')
    video_url_str = 'http://www.myvideo.de/watch/%s/'
    video_title_re = re.compile (r"<td class='globalHd'>([^<]*)</td>")
    video_url_params_re = re.compile (r"<link rel='image_src' href='(\S+)' />")
    parser_type = "MyVideo"

    def __init__ (self, video_id):
        super (MyVideo_Parser, self).__init__ (video_id)


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        partial_url = commands[0].split ("thumbs")[0]
        real_url = "%s%s.flv" % (partial_url, self.video_id)
        return real_url


