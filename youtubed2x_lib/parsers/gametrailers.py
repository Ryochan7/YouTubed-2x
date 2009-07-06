import re
import datetime
from youtubed2x_lib.parsers import Parser_Helper


class GameTrailers_Parser (Parser_Helper):
    """Parser for GameTrailers pages. Updated 07/04/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?gametrailers\.com/video/(\S+)')
    video_url_str = 'http://www.gametrailers.com/video/%s'
    video_title_re = re.compile (r'<span class="MovieTitle">([^<]*)</span>')
    video_url_params_re = re.compile (r'<span class="Downloads">(?:\s+)<a href="(\S+)">Quicktime')
    embed_file_extensions = {"video/quicktime": "mov"}
    parser_type = "GameTrailers"
    host_str = "gametrailers.com"
    version = datetime.date (2009, 7, 4)


    def __init__ (self, video_id):
        super (GameTrailers_Parser, self).__init__ (video_id)
        self.embed_file_type = "video/quicktime"


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0]
        return real_url


    @staticmethod
    def getImageData ():
        image_data = """\x17I\x8b\xff\x16\\\x90\xff5`\xa7\xff5`\xa7\xff4_\xa7\xffGn\xa7\xffCl\xa9\xffBk\xa9\xffBj\xa9\xffL\x7f\xa9\xffU\x8b\xa8\xffZz\xa7\xffAh\xa9\xff\x10T\x98\xff\x00Jp\xff\x00El\xff\x16[\x8e\xffd\x86\xff\xff\x86\xa1\xff\xff\x8c\xb1\xff\xff\x87\xaf\xff\xff\xaa\xb9\xd4\xff\xc5\xcd\xd2\xff\xd9\xd8\xd2\xff\xd9\xd8\xd2\xff\xd2\xcf\xcc\xff\xcc\xcf\xd2\xff\xbe\xe6\xec\xff\x8b\xb8\xff\xffM\x81\xe3\xff3l\xc8\xff\x00Hn\xff2c\xb0\xff\x96\xb6\xfe\xff\xc5\xfc\xff\xff\xae\xb6\xb5\xff\x8a\x88\x85\xff\xcb\xcb\xcd\xff\xf2\xf2\xf2\xff\xf3\xf3\xf3\xff\xf3\xf3\xf3\xff\xf2\xf2\xf2\xff\xd5\xd5\xd5\xff\x89\x8a\x8b\xff\x9e\xb0\xab\xff\x9a\xbd\xff\xffO\x82\xe3\xff\x00U\x80\xffNw\xb0\xff\xdb\xff\xff\xff\xa8\xa5\xa6\xffFFE\xff\xd3\xd3\xd3\xff\xe9\xe9\xe9\xff\xf2\xf2\xf2\xff\xf2\xf2\xf2\xff\xf2\xf2\xf2\xff\xf2\xf2\xf2\xff\xe8\xe8\xe8\xff\xde\xde\xde\xff```\xff\x80\x86\x8b\xff\x84\xab\xff\xff.^\xb2\xffM\x85\xb0\xff\xd4\xe2\xe2\xff;;;\xff\xb2\xb2\xb2\xff\xd5\xd5\xd5\xff\xef\xef\xef\xff\xf4\xf4\xf4\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf7\xf7\xf7\xff\xef\xef\xef\xff\xd7\xd7\xd7\xff\xb8\xb8\xb8\xff@@@\xff\xa4\xc5\xd3\xffGr\xaf\xff3d\xb4\xff]s{\xff||}\xff\xa9\xa9\xa9\xff\x81\x81\x81\xff\x8d\x8d\x8d\xff\x90\x90\x90\xff\x8f\x8f\x8f\xffnnn\xfflll\xff\x8d\x8d\x8d\xff\x87\x87\x87\xff\x92\x92\x92\xffppp\xff\\XS\xffL}\xb2\xff1a\xb7\xff\x0eBW\xff\x99\x99\x9b\xff\x8b\x8b\x8b\xff\xff\xff\xff\xffjjj\xffHHH\xffJJJ\xffOOO\xffUUU\xff\x8f\x8f\x8f\xff\xff\xff\xff\xff000\xff<<<\xff0)$\xffU\x96\xbc\xffCt\xbc\xff72+\xff\x94\x94\x94\xff\xa5\xa5\xa5\xff\xff\xff\xff\xffvvv\xff\xb6\xb6\xb6\xff\xb7\xb7\xb7\xffvvv\xffvvv\xff\xe3\xe3\xe3\xff\xd5\xd5\xd5\xff666\xff\x81~{\xff\x00"E\xffZ\x90\xbb\xffCt\xbc\xff(12\xffdba\xff\xd1\xd1\xd2\xff\xc9\xc9\xc9\xff???\xffggg\xff\xf6\xf6\xf6\xffaaa\xff}}}\xff\xe7\xe7\xe7\xff\x92\x92\x92\xff888\xffeee\xff(13\xffY\x84\xbb\xff0b\xbd\xff\x0e=Q\xffIFD\xff\xeb\xeb\xeb\xff\x9b\x9b\x9b\xffIIH\xff\xc7\xc7\xc8\xff\xf7\xf7\xf7\xff\'\'\'\xff}}}\xff\xf5\xf5\xf5\xffWWW\xff===\xffQNL\xff\x193>\xffAs\xbc\xff\x00V\x83\xff\x0cJi\xff+8?\xffuuu\xff\x88\x88\x88\xff\x8c\x8c\x8c\xffwww\xffwww\xff%%%\xffUUU\xff\x89\x89\x89\xff$$$\xffOOO\xffSNK\xff2JM\xff*`\xba\xff\x19Z\x91\xffJ\x81\xf6\xff\x17/:\xffUTS\xffPPP\xffPPP\xffWWW\xffVVV\xff^^^\xffkkk\xffSSS\xffSSS\xffbbb\xff\x1f7F\xffPv\xbe\xff/`\xb3\xff*]\xb0\xff\x93\xb0\xff\xffp\x83\x8f\xff4AH\xff{yx\xff\x81\x81\x81\xff\x85\x85\x85\xff\x86\x86\x86\xff\x87\x87\x87\xff\x83\x83\x83\xff\x81\x81\x81\xff|||\xff9CI\xff,]\x89\xffV{\xff\xff\x0eR\x92\xff*]\xb0\xff\x86\xa3\xfe\xff\xac\xdd\xff\xffr\x81\x8f\xff\x151B\xffXdl\xff\x8f\x8c\x8a\xff\x9c\x99\x97\xff\x9c\x99\x97\xff\x8f\x8c\x8a\xff[fl\xff!;K\xff+V}\xff\x88\xa7\xff\xff%u\xce\xff\x14T\x98\xff._\xb3\xffu\x97\xfe\xff\x87\xa2\xfe\xff\x82\xc1\xff\xff\xab\xbb\xcb\xffYbe\xff\x1a3<\xff\x00&A\xff\x00\'@\xff\x0b,A\xff\x00<b\xff(Z\x95\xff@\x80\xfa\xff[\x80\xff\xffUz\xc2\xff\x0fS\x9a\xff\x00Gj\xff#\\\xbc\xff\x1f[\xb9\xff(b\xb9\xffDw\xb8\xff\\\x8d\xbf\xff@w\xc4\xff2j\xc3\xff+c\xc7\xff\x00X\x87\xff\x00Iq\xff\x00Gm\xff\x00Mv\xff\x00S}\xff\x00S\x82\xff\x00Hn\xff"""

        return image_data


