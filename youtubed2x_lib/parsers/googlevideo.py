import re
import datetime
from youtubed2x_lib.parsers import Parser_Helper, getPage


class GoogleVideo_Parser (Parser_Helper):
    """Parser for GoogleVideo pages. Updated 07/06/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?video\.google\.com/videoplay\?docid=((?:-)?\d+)')
    video_url_str = 'http://video.google.com/videoplay?docid=%s'
    video_title_re = re.compile (r'<title>([^<]*)</title>')
    video_url_params_re = re.compile (r"<a href=(?:\")?(http://v(\d+)\.(\S+)\.googlevideo.com/videoplayback\?(\S+))(?:\")?>")
    embed_file_extensions = {"video/mp4": "mp4"}
    parser_type = "GoogleVideo"
    domain_str = "http://video.google.com/"
    host_str = "video.google.com"
    version = datetime.date (2009, 11, 28)


    def __init__ (self, video_id):
        super (GoogleVideo_Parser, self).__init__ (video_id)
        self.embed_file_type = "video/mp4"


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0]
        return real_url


    @staticmethod
    def getImageData ():
        image_data = """\x00\x00\x00\x00\xfb\xfc\xff\xff\xcc\xdb\xe2\xff _\xa6\xff\x04L\xa1\xff\x86\xac\xd1\xff\xfd\xff\xfc\xff\xf9\xf1\xef\xff\xc3?:\xff\xd5\x01\x00\xff\xfa\x02\x02\xff\xfd\x00\x00\xff\xfd\x00\x02\xff\xf6\x01\x00\xff\xee\x00\x00\xff\x00\x00\x00\x00\xfc\xfb\xff\xff\xfe\xff\xff\xffP\x83\xb8\xff\x00W\xb9\xff\x02c\xcc\xff\x0eb\xbc\xff\xdc\xe6\xf2\xff\xff\xfe\xfc\xff\xf6\xd4\xd5\xff\xe7\x0c\n\xff\xfd\x00\x00\xff\xfe\x01\x03\xff\xfd\x01\x00\xff\xf6\x01\x00\xff\xec\x00\x04\xff\xe0\x02\x00\xff\xff\xff\xff\xff\xfb\xfb\xfb\xff$l\xb6\xff\x00c\xc8\xff\x00f\xcf\xff\x00Y\xc1\xff\x83\xaf\xd2\xff\xff\xfe\xff\xff\xfe\xfc\xff\xff\xe0FF\xff\xf9\x00\x01\xff\xfc\x03\x00\xff\xf9\x01\x01\xff\xf0\x00\x03\xff\xeb\x01\x00\xff\xdf\x00\x00\xff\xfe\xfd\xff\xff\xff\xfc\xff\xff;|\xbe\xff\x02]\xc6\xff\x02f\xc8\xff\x02Z\xc4\xffW\x8e\xce\xff\xff\xff\xfb\xff\xff\xff\xff\xff\xddSP\xff\xf4\x00\x04\xff\xff\x01\x00\xff\xfd\x00\x03\xff\xf3\x01\x00\xff\xe5\x00\x00\xff\xda\x02\x03\xff\xff\xff\xfd\xff\xff\xff\xfd\xff\x82\xa9\xd2\xff\x00S\xb9\xff\x04d\xca\xff\x02X\xbd\xffY\x90\xc8\xff\xfd\xff\xfe\xff\xff\xf8\xff\xff\xc7)(\xff\xc2\x19\x06\xff\xb1&\x11\xff\xb6 \x11\xff\xcc\x10\x05\xff\xe1\x02\x00\xff\xd5\x01\x00\xff\xdb\xe1\xed\xff\xfe\xff\xff\xff\xe8\xf1\xf6\xff(l\xb5\xff\x00T\xbb\xff\x0e]\xb9\xff\xb9\xcf\xe4\xff\xfe\xff\xff\xff\x99\xb1\x9b\xff\x1dp \xff\x00\x957\xff\x03\x96=\xff\x00\x93;\xff\t\x896\xff:e-\xff\x8a+\x0f\xff\'^\x9f\xff\xac\xbe\xd6\xff\xff\xfd\xfe\xff\xef\xf2\xf9\xff\xa0\xbf\xde\xff\xda\xe2\xed\xff\xfd\xff\xfe\xff\x85\xb8\x99\xff\x00\x82,\xff\x03\x9a;\xff\x03\x98:\xff\x00\x967\xff\x00\x969\xff\x01\x91:\xff\x00\x93?\xff\x01\x87B\xff\x15V\xa8\xff\x10O\x9c\xffBo\xa6\xff\x84\xa2\xbe\xff\xff\xfe\xfc\xff\xff\xff\xfb\xff\xbf\xda\xc9\xff\x02w\x1f\xff\x00\x9b5\xff\x00\x997\xff\x00\x9a7\xff\x01\x94<\xff\x01\x94<\xff\x00\x8f8\xff\x01\x8b=\xff\x01\x87>\xff\'Y\xa2\xff\x1cU\xa4\xff\x08J\x9e\xff\x11H\x98\xff\xdf\xe8\xf1\xff\xfe\xfe\xfe\xff\xe1\xec\xe4\xff&\x9aQ\xff\x00\x94-\xff\x02\x979\xff\x02\x97;\xff\x00\x948\xff\x02\x92;\xff\x01\x8f=\xff\x02\x8b=\xff\x00\x898\xff"I\x8e\xff8^\x9d\xffV~\xb2\xffn\x90\xc0\xff\xcf\xda\xee\xff\xfd\xff\xfe\xff\xfe\xff\xfd\xff\xeb\xf2\xeb\xffF\xa8k\xff\x01\x8d-\xff\x00\x96<\xff\x00\x93;\xff\x00\x93;\xff\x00\x8f=\xff\x00\x8a=\xff\x00\x84=\xff\xa6\xbb\xd0\xff\xeb\xee\xfd\xff\xfe\xff\xff\xff\xfa\xf0\xd5\xff\xe8\xdd\xb0\xff\xde\xcf\x96\xff\xf7\xf3\xea\xff\xff\xff\xff\xff\xfa\xfc\xfb\xffI\xa6m\xff\x01\x8d*\xff\x00\x938\xff\x00\x90;\xff\x02\x8b9\xff\x00\x88<\xff\x00\x85<\xff\xff\xfd\xff\xff\xf3\xe9\xd0\xff\xce\xb08\xff\xdf\xb0\n\xff\xe3\xb5\x00\xff\xe2\xae\x02\xff\xd6\xa9*\xff\xf1\xec\xd9\xff\xff\xfe\xfc\xff\xd7\xe8\xe0\xff\r\x86?\xff\x00\x909\xff\x03\x8c<\xff\x02\x89=\xff\x00\x85>\xff\x00\x81>\xff\xf8\xfb\xf4\xff\xcc\xa67\xff\xef\xb4\x00\xff\xfe\xc5\x02\xff\xfb\xc3\n\xff\xf6\xbe\t\xff\xea\xaa\x00\xff\xdb\xb0J\xff\xfe\xfe\xfe\xff\xfe\xfc\xff\xff%\x91U\xff\x00\x894\xff\x00\x8d;\xff\x00\x86=\xff\x05\x81C\xff\x01}>\xff\xf2\xec\xde\xff\xd8\xa2\x1b\xff\xf7\xb9\x10\xff\xf1\xb9\x0c\xff\xf2\xb5\x0f\xff\xf0\xb2\x0f\xff\xf4\xb3\x1b\xff\xe7\xab/\xff\xff\xf9\xf3\xff\xf6\xfb\xfe\xff\x1d\x85J\xff\x00\x869\xff\x02\x85A\xff\x00\x86<\xff\x02\x80@\xff\x00{=\xff\xfb\xfc\xfe\xff\xdf\xb7_\xff\xec\xa7\x0c\xff\xf0\xb1\x16\xff\xf1\xb2\x15\xff\xf4\xb3\x1b\xff\xf1\xaa\x1e\xff\xee\xc4|\xff\xfe\xff\xff\xff\xa9\xca\xb7\xff\x03v1\xff\x01\x83;\xff\x03\x82?\xff\x00}>\xff\x00z>\xff\x00yC\xff\x00\x00\x00\x00\xfb\xf4\xec\xff\xeb\xc5|\xff\xef\xb6O\xff\xf1\xb1E\xff\xef\xb6M\xff\xf6\xce\x93\xff\xf9\xfb\xf6\xff\xd1\xe1\xde\xff\x1cxI\xff\x00z4\xff\x02|?\xff\x00|@\xff\x00{<\xff\x00zA\xff\x00\x00\x00\x00"""

        return image_data


