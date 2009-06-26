import re
from youtubed2x_lib.parsers import Parser_Helper
from pornotube import PornoTube_Parser
from redtube import RedTube_Parser
from pornhub import Pornhub_Parser
from pacoporn import PacoPorn_Parser


class Porn2Pc_Parser (Parser_Helper):
    """Non-Parser for Porn2PC pages. Updated 06/03/2009"""
    const_video_url_re = re.compile (r'^((?:http://)?(?:www\.)?porn2pc\.com/)(\S+)')
    video_url_str = 'http://www.porn2pc.com/%s'
    parser_type = "Porn2Pc"
    host_str = "porn2pc.com"


    @classmethod
    def checkURL (cls, url):
        parsers = (PornoTube_Parser, RedTube_Parser, Pornhub_Parser, PacoPorn_Parser,)
        match = cls.const_video_url_re.match (url)
        if not match:
            return None

        page_id = match.group (2)

        for parser in parsers:
            test_url = "%s%s" % (parser.domain_str, page_id)
            page_parser = parser.checkURL (test_url)
            if page_parser:
                return page_parser

        return None


    def parseVideoPage (self, page_dump):
        raise NotImplementedError

    def getVideoPage (self, account="", password=""):
        raise NotImplementedError

    def _parseTitle (self, page_dump):
        raise NotImplementedError

    def _parsePlayerCommands (self, page_dump):
        raise NotImplementedError

    def _parseRealURL (self, commands):
        raise NotImplementedError


