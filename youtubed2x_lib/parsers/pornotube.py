import re
from youtubed2x_lib.parsers import Parser_Helper, getPage


class PornoTube_Parser (Parser_Helper):
    """Parser for PornoTube pages. Updated 06/25/2009"""
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

    def __init__ (self, video_id):
        super (PornoTube_Parser, self).__init__ (video_id)


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


