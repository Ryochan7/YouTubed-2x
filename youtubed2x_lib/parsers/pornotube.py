import re
import datetime
from youtubed2x_lib.parsers import Parser_Helper, getPage


class PornoTube_Parser (Parser_Helper):
    """Parser for PornoTube pages. Updated 07/04/2009"""
    # URLs and RegExp statements from pornotube-dl (some slightly modified)
    const_video_url_re = re.compile (r'(?:http://)?(?:www\.)?pornotube\.com/media\.php\?m=(\d+)')
    domain_str = "http://www.pornotube.com/"
    video_url_str = 'http://www.pornotube.com/media.php?m=%s'
    video_url_age_post = {'bMonth': '01', 'bDay': '1', 'bYear': '1986', 'verifyAge': 'true'}
    video_url_player_str = 'http://www.pornotube.com/player/player.php?%s'
    video_url_real_str = 'http://%s.pornotube.com/%s/%s.flv'
    video_url_id_re = re.compile (r'"player/v\.swf\?v=([^"]+)')
    video_title_re = re.compile (r'<span>Viewing Video: </span><span class="blue">([^<]*)</span>')
    video_url_mid_re = re.compile (r'&mediaId=(\d+)&')
    video_url_uid_re = re.compile (r'&userId=(\d+)&')
    video_url_mdomain_re = re.compile (r'&mediaDomain=([^&]+)&')
    parser_type = "PornoTube"
    domain_str = "http://www.pornotube.com/"
    host_str = "pornotube.com"
    version = datetime.date (2009, 11, 28)


    def getVideoPage (self):
        page, newurl = getPage (self.page_url, self.video_url_age_post)
        page, newurl = getPage (self.page_url)
        return page, newurl


    def _parsePlayerCommands (self, page_dump):
        """Get the commands needed to get the video player"""
        match = self.video_url_id_re.search (page_dump)
        if not match:
            raise self.InvalidCommands ("Could not find flash player commands")
        else:
            commands = match.groups ()
        return commands


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        video_url_player = self.video_url_player_str % commands
        page, newurl = getPage (video_url_player)

        match = self.video_url_mid_re.search (page)
        if not match:
            raise self.URLBuildFailed ("Could not find the mediaId")
        video_url_mid = match.group (1)
        match = self.video_url_uid_re.search (page)
        if not match:
            raise self.URLBuildFailed ("Could not find the userId")
        video_url_uid = match.group (1)
        match = self.video_url_mdomain_re.search (page)
        if not match:
            raise self.URLBuildFailed ("Could not find the mediaDomain")
        video_url_mdomain = match.group (1)

        real_url = self.video_url_real_str % (video_url_mdomain, video_url_uid, video_url_mid)
        return real_url


    @staticmethod
    def getImageData ():
        image_data = """\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x03\x04\x06\xff\x07\x01\x00\xff\x08\x00\x00\xff\x05Fx\xff\x06(G\xff\x05Dn\xff\x00\x01\x01\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x01\x02\xff\nEr\xff\x02&?\xff\x04/M\xff\x02\x00\x00\xff\x020R\xff\x01\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x01\xff\x03\x00\x01\xff\x04\x0b\x13\xff\x07\x07\n\xff\x07\x19+\xff\x00Fx\xff\x06\x19*\xff\x02\x00\x05\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x02\x01\x03\xff\x00\x00\x00\xff\x04>f\xff\x02Ft\xff\x04\x00\x00\xff\x02\x00\x03\xff\x00\x02\x02\xff\x00\x00\x00\xff\x00\x02\x02\xff\x00\x00\x02\xff\x00\x00\x01\xff\x00\x00\x02\xff\x00\x00\x00\xff\x00\x00\x01\xff\x00\x00\x03\xff\x01\x01\x00\xff\x00\x00\x03\xff\x03\x01\x01\xff\x03\'@\xff\x03":\xff\x04\x00\x01\xff\x00\x00\x03\xff\x04\x01\x04\xff\x02\x02\x03\xff\x02\x02\x05\xff\x84U\x02\xff\x84U\x02\xff\x84U\x01\xff\x85U\x01\xff\x86T\x02\xff\x84X\x01\xff\x0f\x08\x07\xffxR\x03\xff\x06\x04\x06\xff\x01\x01\x01\xff\x00\x01\x01\xff\x00\x00\x06\xffiE\x02\xff\x00\x00\x05\xff\x02\x01\x03\xff\x02\x02\x04\xff\xcd\x82\x02\xff\xd1\x82\x04\xff\xef\x90\x03\xff\xf0\x94\x03\xff\xd1\x7f\x04\xff\xd1\x85\x03\xff\x18\n\x06\xff\xdb\x90\x02\xff\x08\x06\x03\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x02\xff\xbf{\x02\xff\x00\x00\x01\xff\x18\x0f\x04\xff\x03\x00\x00\xff\x01\x01\x04\xff\x00\x00\x03\xff\xafo\x06\xff\xc9}\x03\xff\x00\x00\x02\xff\x00\x01\x03\xff\x00\x02\x00\xff\xdb\x92\x01\xff\x08\x07\x03\xff\x00\x00\x00\xff\x00\x01\x00\xff\x00\x00\x02\xff\xbe|\x02\xff\x00\x00\x01\xff\xb8t\x04\xff\x02\x03\x02\xff\x01\x00\x01\xff\x00\x00\x03\xff\xb2q\x01\xff\xca}\x01\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x03\xff\xdf\x90\x03\xff\x0b\x06\t\xff\x04\x04\x03\xff\x03\x03\x04\xff\x00\x00\x06\xff\xc0z\x00\xff\x00\x00\x03\xff\xe7\x8f\x02\xff\x01\x01\x01\xff\x02\x00\x03\xff\x00\x00\x02\xff\xb1q\x01\xff\xca}\x02\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x03\xff\xda\x92\x04\xff5GX\xff=Ra\xff=Qa\xff\'B\\\xff\xb8t\x00\xff\x00\x00\x01\xff\xe6\x8d\x00\xff\x02\x02\x00\xff\x01\x00\x00\xff\x00\x00\x03\xff\xb2p\x02\xff\xcb}\x02\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x01\xff\xdc\x93\x03\xff)t\xa7\xff/\x85\xbe\xff0\x84\xbe\xff\x1bs\xb5\xff\xbcp\x00\xff\x00\x00\x01\xff\xe7\x8e\x01\xff\x02\x02\x01\xff\x00\x01\x00\xff\x00\x00\x03\xff\xb2p\x02\xff\xca}\x02\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x01\xff\xde\x91\x01\xff\x0b\x85\xd0\xff\x03\x99\xfb\xff\x04\x98\xfa\xff\x00\x8a\xf0\xff\xbfm\x00\xff\x00\x00\x00\xff\xe7\x8e\x00\xff\x01\x00\x01\xff\x01\x00\x00\xff\x00\x00\x03\xff\xb1q\x01\xff\xcb|\x02\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x02\xff\xdb\x92\x02\xff\t\x83\xd1\xff\x00\x98\xfd\xff\x02\x98\xfc\xff\x00\x8e\xf3\xff\xc0l\x00\xff\x00\x00\x02\xff\xe8\x8f\x00\xff\x01\x01\x01\xff\x00\x00\x01\xff\x00\x00\x02\xff\xb0q\x01\xff\xcc|\x02\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x03\xff\xd5\x8a\x02\xff\x0b~\xc9\xff\x02\x99\xfe\xff\x02\x98\xfd\xff\x00\x7f\xe2\xff\xbes\x00\xff\x00\x00\x04\xff\xe7\x8e\x03\xff\x00\x00\x00\xff\x00\x00\x02\xff\x00\x00\x03\xff\xb3s\x03\xff\xcd~\x03\xff\x00\x00\x01\xff\x00\x00\x00\xff\x00\x00\x02\xffb8\x05\xffTC*\xff\x00\x8f\xec\xff\x00\x94\xf3\xff;Zc\xff\xaeu\x04\xff\x00\x00\x04\xff\xe9\x90\x03\xff\x00\x00\x00\xff\x00\x00\x01\xff\x01\x00\x03\xff^:\x02\xffi@\x04\xff\x00\x00\x02\xff\x00\x00\x00\xff\x01\x00\x00\xff\x01\x02\x07\xff\xa8k\x08\xff\xc6w\x00\xff\xbal\x00\xff\xc5\x7f\x05\xff\x00\x00\x05\xff\x02\x00\x03\xffvJ\x06\xff"""

        return image_data


