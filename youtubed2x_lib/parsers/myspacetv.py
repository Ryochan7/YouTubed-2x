import re
from youtubed2x_lib.parsers import Parser_Helper, getPage


class MySpaceTV_Parser (Parser_Helper):
    """Parser for MySpaceTV pages. Updated 06/16/2008"""
    const_video_url_re = re.compile (r'^(?:http://)?vids\.myspace\.com/index\.cfm\?fuseaction=vids\.individual&(?:v|V)ideo(?:id|ID)=(\d+)')
    video_url_str = 'http://vids.myspace.com/index.cfm?fuseaction=vids.individual&videoid=%s'
    video_details_str = "http://mediaservices.myspace.com/services/rss.ashx?videoID=%s&type=video"
    video_title_re = re.compile (r"<item>\r\n      <title>([^<]*)</title>")
    video_url_params_re = re.compile (r'<media:content url="(\S+)" type="video/x-flv"')
    parser_type = "MySpaceTV"

    def __init__ (self, video_id):
        super (MySpaceTV_Parser, self).__init__ (video_id)


    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.video_details_str % self.video_id)
        return page, newurl


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0]
        return real_url


