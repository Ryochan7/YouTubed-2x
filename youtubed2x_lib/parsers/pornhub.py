import re
from youtubed2x_lib.parsers import Parser_Helper, getPage


class Pornhub_Parser (Parser_Helper):
    """Parser for Pornhub pages. Updated 01/07/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?pornhub\.com/view_video.php\?viewkey=(\w+)$')
    domain_str = "http://www.pornhub.com/"
    video_url_str = 'http://www.pornhub.com/view_video.php?viewkey=%s'
    video_title_re = re.compile (r'<title>([^<]*) - Pornhub.com</title>')
    video_url_params_re = re.compile (r'to\.addVariable\("options", "(\S+)"\);')
    video_key_re = re.compile (r"<flv_url>(\S+)</flv_url>")
    parser_type = "Pornhub"

    def __init__ (self, video_id):
        super (Pornhub_Parser, self).__init__ (video_id)


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        from urllib2 import unquote
        video_config_url = unquote (commands[0])
        page, newurl = getPage (video_config_url)
        match = self.video_key_re.search (page)
        if not match:
            raise self.URLBuildFailed ("Could not find video url or position key")
        else:
            secondary_url = match.group (1)

        # Follow redirect
        page, real_url = getPage (secondary_url, read_page=False)
        return real_url


