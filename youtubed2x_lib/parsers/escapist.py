import re
import hashlib
from urllib2 import unquote
from youtubed2x_lib.parsers import Parser_Helper, getPage


class Escapist_Parser (Parser_Helper):
    """Parser for The Escapist pages. Updated 06/26/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?escapistmagazine\.com/videos/view/(\S+)')
    video_url_str = 'http://www.escapistmagazine.com/videos/view/%s'
    video_url_secondary_str = "http://www.themis-media.com/global/castfire/m4v/%s"
    video_title_re = re.compile (r'<div class=\'headline\'>([^<]*)</div>')
    video_url_params_re = re.compile (r'&quot;url&quot;:(\d+),&quot;')
    video_url_real_str_re = re.compile (r'^url=(\S+)?')
    post_vars = {"version": "ThemisMedia1.2", "format": ""}
    parser_type = "The Escapist"
    host_str = "escapistmagazine.com"


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        secondary_url = self.__class__.video_url_secondary_str % commands[0]
        video_hash = hashlib.md5 ("Video %s Hash" % commands[0]).hexdigest ()
        post_vars = self.__class__.post_vars.copy ()
        post_vars["format"] = video_hash
        # Attempt to get URL variable for flv video
        page, newurl = getPage (secondary_url, post_vars)
        match = self.__class__.video_url_real_str_re.match (page)
        if not match:
            raise self.__class__.URLBuildFailed ("Redirect from \"%s\" did not yield a video URL" % secondary_url)
        else:
            real_url = unquote (match.group (1))

        return real_url


    @staticmethod
    def getImageData ():
        image_data = """\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x80\x80\xff\x80\x80\x80\xff\x80\x80\x80\xff\x80\x80\x80\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x80\x80\xff\x00\x00\x00\xff\xc0\xc0\xc0\xff\x80\x80\x80\xff\x80\x80\x80\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\xc0\xc0\xff\x80\x80\x80\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\xc0\xc0\xff\x00\x00\x00\xff\x80\x80\x80\xff\x00\x00\x00\x00\x80\x80\x80\xff\xc0\xc0\xc0\xff\xc0\xc0\xc0\xff\x80\x80\x80\xff\x80\x80\x80\xff\x80\x80\x80\xff\x80\x80\x80\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x00\x00\x00\xff\xc0\xc0\xc0\xff\x80\x80\x80\xff\x00\x00\x00\xff\x80\x80\x80\xff\x80\x80\x80\xff\x80\x80\x80\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x80\x80\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x80\x80\x80\xff\xc0\xc0\xc0\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\xc0\xc0\xff\x80\x80\x80\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x80\x80\x80\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x80\x80\xff\x80\x80\x80\xff\x80\x80\x80\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\xc0\xc0\xff\x00\x00\x00\x00\x80\x80\x80\xff\x00\x00\x00\xff\x80\x80\x80\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x80\x80\xff\x00\x00\x00\xff\xc0\xc0\xc0\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x80\x80\xff\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x80\x80\xff\xc0\xc0\xc0\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x80\x80\xff\x80\x80\x80\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x80\x80\xff\x80\x80\x80\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x80\x80\xff\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00\x80\x80\x80\xff\x00\x00\x00\xff\x80\x80\x80\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x80\x80\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x80\x80\x80\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\xc0\xc0\xff\x00\x00\x00\xff\x00\x00\x00\xff\xc0\xc0\xc0\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"""

        return image_data

