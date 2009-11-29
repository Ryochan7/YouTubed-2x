import re
import datetime
from youtubed2x_lib.parsers import Parser_Helper

class Guba_Parser (Parser_Helper):
    """Parser for Guba pages. Updated 07/04/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?guba\.com/watch/(\d+)')
    video_url_str = 'http://www.guba.com/watch/%s'
    video_title_re = re.compile (r'var theName="([\S ]+)";')
    video_url_params_re = re.compile (r'"(\S+)" \);\r\n(?:[ ]{32})bfp.writeBlogFlashPlayer\(\);')
    parser_type = "Guba"
    domain_str = "http://www.guba.com/"
    host_str = "guba.com"
    version = datetime.date (2009, 11, 28)


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0]
        return real_url


    @staticmethod
    def getImageData ():
        image_data = """\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa2\xaa\xaf2|\x87\x8e\x82\\jt\xc09JV\xc4Tcl\xcbt\x7f\x88\x9f\x8a\x94\x9bQ\xb8\xbe\xc2\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x8d\x97\x9dBcpz\xdf>OZ\xff3EQ\xff8IU\xffGWb\xff<MX\xff2DP\xff9JV\xffM\\f\xfft\x80\x88\xa8\xa3\xac\xb1\x17\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa5\xac\xb2\x86*=I\xff1CO\xff9JV\xff5FR\xff=NY\xffCS^\xffBR^\xff8IU\xff5GR\xff6GS\xff1CO\xffFVa\xff}\x88\x90\x97\x00\x00\x00\x00\xbd\xc3\xc7h 4A\xff@P[\xff1BN\xffEV`\xf8y\x84\x8c\x86\xab\xb2\xb7C\x86\x90\x97)\x83\x8e\x954\x83\x8e\x95efs|\xc9=MY\xff4ER\xff#6C\xff[is\xdd\xec\xee\xef\x10FVa\xf85FR\xff0BN\xffhu~\xda\xb9\xbf\xc3\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc5\xca\xce.fs|\xe0%8E\xff\xd9\xdc\xdf5\x9c\xa5\xabq%8E\xff7HT\xffWfo\xea\xff\xff\xff\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc9\xcd\xd0\x13\xd0\xd3\xd7S\x00\x00\x00\x00kw\x80\xbf/AN\xff,>J\xff\x9c\xa4\xaa\x81\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00DT_\xddCS_\xff<MX\xff\x97\x9f\xa5N\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|\x87\x8fI4FR\xa2EU`\x8aFVa\x8aDT_\x8a:JW\x8a#6C\x9bIXciEU`\xddCS^\xff?O[\xff\x8a\x95\x9bM\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00{\x86\x8e\x862EQ\xffCT_\xffCT_\xffCT_\xffEU`\xff=NZ\xffUdn\xc3ly\x82\xbf0AN\xff-?K\xff\x98\xa1\xa7|\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00{\x86\x8d\x862CP\xffCT_\xffBS^\xff>NZ\xffEU`\xff>NZ\xffUdn\xc3\x95\x9e\xa4q(;H\xff6HS\xff[js\xe5\xfc\xfd\xfc\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x91\x9a\xa1 VenFkx\x81>my\x82#\x82\x8d\x95EKZe\xff:KV\xffUdn\xc3\xd0\xd4\xd7\x10AR]\xf88IU\xff1CO\xffbpy\xd4\xb7\xbe\xc2\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa5\xac\xb2B?P[\xff;LW\xffTbl\xc3\x00\x00\x00\x00\xb8\xbe\xc2k\x1f3@\xff>NZ\xff3EQ\xffK[e\xf8z\x85\x8e\x8a}\x89\x8fA\xcb\xcf\xd3:\xac\xb3\xb9:u\x81\x89Wkx\x81\xbdCT_\xffCS^\xff1BO\xffEU`\xc3\x00\x00\x00\x00\x00\x00\x00\x00\x96\x9f\xa5\x8c,>J\xff0BN\xff:KW\xff4FR\xff@Q\\\xffAP\\\xffAQ]\xff;LX\xff6HT\xff;LW\xff);H\xffBS^\xff\xae\xb5\xbaX\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa7\xaf\xb4Q[ir\xec9JV\xff5FS\xff@P\\\xffBR]\xff@Q\\\xff8HU\xff5GS\xffDT_\xffu\x81\x8a\xb9\xcb\xd0\xd2\x19\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x91\x9a\xa1>u\x81\x89\x89O^h\xa7=NY\xa3IYc\xa8n{\x83\x9b\x81\x8c\x94`\x90\x9a\xa1\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"""

        return image_data


