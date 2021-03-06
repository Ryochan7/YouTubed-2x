import re
import datetime
from youtubed2x_lib.parsers import Parser_Helper, getPage


class SpankWire_Parser (Parser_Helper):
    """Parser for SpankWire pages. Updated 01/15/2010"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?spankwire\.com/((\S+)/video(\d+))(?:\?(.*))?')
    video_url_str = 'http://www.spankwire.com/%s/'

    video_title_re = re.compile (r'<title>([^<]+)</title>')
    video_details_xml_url = "http://www.spankwire.com/Player/VideoXML.aspx?id=%s"
    video_url_params_re = re.compile (r'<url type="string">(\S+)</url>')

    parser_type = "SpankWire"
    domain_str = "http://www.spankwire.com/"
    host_str = "spankwire.com"
    version = datetime.date (2010, 1, 15)


    def _parsePlayerCommands (self):
        """Get the commands needed to get the video player"""
        page, newurl = getPage (self.__class__.video_details_xml_url % self.video_id.rsplit ("/video", 1)[1])

        match = self.video_url_params_re.search (page)
        if not match:
            raise self.__class__.InvalidCommands ("Could not find flash player commands")
        else:
            commands = match.groups ()
        return commands
    

    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0].replace ("&amp;", "&")
        return real_url


    @staticmethod
    def getImageData ():
        image_data = """\xfe}\xda?\xffs\xc8\x7f\xfft\xc9\x7f\xfft\xc9\x7f\xfft\xc9\x7f\xfft\xc9\x7f\xfft\xc9\x7f\xfft\xc9\x7f\xffs\xc9\x7f\xfft\xca\x7f\xffs\xc9\x7f\xfft\xc9\x7f\xfft\xc9\x7f\xfft\xc9\x7f\xfft\xc9\x7f\xffw\xd0\x7f\xffs\xc8\x7f\xf5j\xb8\xff\xf6j\xb9\xff\xf6j\xb9\xff\xf6j\xb9\xff\xf6j\xb9\xff\xf6e\xb6\xff\xf6d\xb6\xff\xf6i\xb8\xff\xf6e\xb6\xff\xf6h\xb8\xff\xf6j\xb9\xff\xf6j\xb9\xff\xf6j\xb9\xff\xf6j\xb9\xff\xfan\xbf\xff\xfft\xc9\x7f\xf6j\xb9\xff\xf7k\xba\xff\xf7k\xba\xff\xf7k\xba\xff\xf6c\xb6\xff\xfc\xcf\xe8\xff\xfc\xd6\xeb\xff\xf7y\xc0\xff\xff\xff\xff\xff\xf7w\xc0\xff\xf6b\xb6\xff\xf7k\xba\xff\xf7j\xba\xff\xf7k\xba\xff\xfbn\xc0\xff\xfft\xc9\x7f\xf6j\xb9\xff\xf7k\xba\xff\xf7k\xba\xff\xf7k\xba\xff\xf6d\xb6\xff\xfc\xcc\xe7\xff\xfc\xc5\xe4\xff\xf9\xa2\xd3\xff\xfe\xfb\xfd\xff\xf8\x81\xc3\xff\xfd\xdf\xf0\xff\xf6e\xb7\xff\xf7k\xba\xff\xf7k\xba\xff\xfbn\xc0\xff\xfft\xc9\x7f\xf6j\xb9\xff\xf6f\xb7\xff\xf6g\xb8\xff\xf7k\xba\xff\xf6e\xb7\xff\xfb\xc4\xe3\xff\xfa\xad\xd9\xff\xfc\xd1\xe9\xff\xf9\x9c\xd1\xff\xfd\xe1\xf1\xff\xfc\xd3\xea\xff\xf6d\xb6\xff\xf7k\xba\xff\xf7j\xb9\xff\xfbn\xc0\xff\xfft\xc9\x7f\xf6f\xb7\xff\xfa\xb1\xdb\xff\xfa\xa8\xd6\xff\xf6g\xb8\xff\xf6g\xb8\xff\xfb\xb7\xdd\xff\xf8\x81\xc4\xff\xfe\xeb\xf6\xff\xf9\xa6\xd6\xff\xff\xff\xff\xff\xf8{\xc1\xff\xf6j\xb9\xff\xf6h\xb8\xff\xf6j\xb9\xff\xfbn\xc0\xff\xfft\xc9\x7f\xf6`\xb4\xff\xfd\xea\xf5\xff\xfd\xe6\xf3\xff\xf6b\xb6\xff\xf6f\xb7\xff\xfb\xcc\xe7\xff\xfe\xf1\xf9\xff\xfc\xd1\xe9\xff\xf8\x8d\xc9\xff\xfc\xd1\xea\xff\xf6e\xb7\xff\xf8w\xc0\xff\xff\xff\xff\xff\xf7o\xbc\xff\xfbn\xc0\xff\xfft\xc9\x7f\xf6i\xb8\xff\xf8\x86\xc6\xff\xf9\x9f\xd2\xff\xf6h\xb8\xff\xf6_\xb4\xff\xfd\xef\xf7\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf6f\xb8\xff\xf6_\xb4\xff\xfd\xe6\xf3\xff\xfb\xc6\xe4\xff\xf6g\xb8\xff\xfbn\xc0\xff\xfft\xc9\x7f\xf6j\xb9\xff\xf7i\xb9\xff\xf7i\xb8\xff\xf6c\xb6\xff\xfb\xc0\xe2\xff\xfe\xf4\xf9\xff\xfa\xb8\xde\xff\xfc\xd0\xe8\xff\xfd\xdf\xf0\xff\xfd\xe2\xf1\xff\xfc\xd8\xec\xff\xfa\xab\xd7\xff\xf6b\xb6\xff\xf7k\xba\xff\xfbn\xc0\xff\xfft\xc9\x7f\xf6j\xb9\xff\xf6h\xb8\xff\xfa\xaa\xd7\xff\xfe\xf7\xfb\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf7v\xbf\xff\xf6X\xb1\xff\xfd\xe0\xf0\xff\xff\xff\xff\xff\xfa\xad\xd9\xff\xf6d\xb7\xff\xf7k\xba\xff\xf7k\xba\xff\xfbn\xc0\xff\xfft\xc9\x7f\xf6j\xb9\xff\xf7k\xba\xff\xf8\x80\xc4\xff\xff\xff\xff\xff\xff\xfc\xfd\xff\xff\xff\xff\xff\xf6`\xb5\xff\xf9\x98\xcf\xff\xfe\xfc\xfd\xff\xfe\xef\xf8\xff\xf7u\xbf\xff\xf7k\xba\xff\xf7k\xba\xff\xf7k\xba\xff\xfbn\xc0\xff\xfft\xc9\x7f\xf6j\xb9\xff\xf7k\xba\xff\xf6e\xb7\xff\xfd\xe6\xf3\xff\xfe\xfe\xff\xff\xff\xfe\xfe\xff\xfd\xe6\xf3\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf7u\xbe\xff\xf7j\xba\xff\xf7j\xb9\xff\xf7k\xba\xff\xf7k\xba\xff\xfbn\xc0\xff\xfft\xc9\x7f\xf6j\xb9\xff\xf7k\xba\xff\xf7k\xba\xff\xf7k\xba\xff\xfd\xdc\xee\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf7m\xba\xff\xf6k\xba\xff\xf7k\xba\xff\xf7k\xba\xff\xf7k\xba\xff\xfbn\xc0\xff\xfft\xc9\x7f\xf6j\xb9\xff\xf7k\xba\xff\xf7j\xb9\xff\xf7k\xba\xff\xf6d\xb7\xff\xf7w\xc0\xff\xfb\xc6\xe5\xff\xff\xfc\xfe\xff\xfb\xb9\xde\xff\xf6e\xb7\xff\xf7k\xb9\xff\xf7k\xba\xff\xf7k\xba\xff\xf7k\xba\xff\xfbn\xc0\xff\xfft\xc9\x7f\xf6j\xb9\xff\xf7k\xba\xff\xf7k\xba\xff\xf7k\xba\xff\xf6k\xba\xff\xf7k\xba\xff\xf6e\xb7\xff\xf6a\xb5\xff\xf6f\xb7\xff\xf7k\xba\xff\xf7k\xba\xff\xf7k\xba\xff\xf7k\xba\xff\xf7k\xba\xff\xfbn\xc0\xff\xffx\xd0\x80\xfam\xbf\xff\xfbn\xc0\xff\xfbn\xc0\xff\xfbn\xc0\xff\xfbn\xc0\xff\xfbn\xc0\xff\xfbn\xc0\xff\xfbn\xc0\xff\xfbn\xc0\xff\xfbn\xc0\xff\xfbn\xc0\xff\xfbn\xc0\xff\xfbn\xc0\xff\xfbn\xc0\xff\xfdr\xc7\xff"""

        return image_data


