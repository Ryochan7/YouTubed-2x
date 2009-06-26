import re
from youtubed2x_lib.parsers import Parser_Helper, getPage


class Veoh_Parser (Parser_Helper):
    """Parser for Veoh pages. Updated 06/07/2008"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?veoh\.com/videos/(\w+)')
    video_url_str = 'http://www.veoh.com/videos/%s'
    video_detail_url = 'http://www.veoh.com/rest/video/%s/details'
    video_title_re = re.compile (r'\ttitle="(.*)"')
    video_url_params_re = re.compile (r'fullPreviewHashPath="(\S+)"')
    extern_content_re = re.compile (r'<contentSource id=')
    forward_link_re = re.compile (r'aowPermalink="(\S+)"')
    is_portal = True
    parser_type = "Veoh"
    host_str = "veoh.com"


    def __init__ (self, video_id):
        Parser_Helper.__init__ (self, video_id)
        self.details_url = self.video_detail_url % video_id


    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.details_url)
        match = self.extern_content_re.search (page)
        if match:
            content_match = self.forward_link_re.search (page)
            page = ""
            newurl = content_match.group (1)
        return page, newurl

    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        secondary_url = commands[0]
        # Follow redirect
        page, real_url = getPage (secondary_url, read_page=False)
        return real_url


    @staticmethod
    def getImageData ():
        image_data = """\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe\xfe\xfe\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe\xfe\xfe\xff\xde\xee\xf2\xff~\xb6\xca\xff^\xa2\xc2\xff2\x8e\xb6\xff2\x8e\xb6\xff^\xa2\xc6\xff~\xb6\xce\xff\xde\xee\xf2\xff\xfe\xfe\xfe\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe\xfe\xfe\xff\xa6\xce\xda\xffN\x9a\xc2\xffb\xaa\xd6\xffb\xae\xda\xffb\xae\xde\xffb\xae\xde\xffb\xae\xda\xffb\xaa\xd6\xffF\x96\xc2\xff\xa6\xce\xda\xff\xfe\xfe\xfe\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe\xfe\xfe\xff\xa2\xca\xda\xffF\x96\xc2\xffV\xa6\xda\xffV\xae\xde\xffV\xb6\xde\xffV\xb6\xe2\xffV\xb6\xe2\xffV\xb6\xde\xffV\xae\xde\xffV\xa6\xda\xffF\x96\xca\xff\xa6\xca\xde\xff\xfe\xfe\xfe\xff\x00\x00\x00\x00\x00\x00\x00\x00\xde\xee\xf2\xff>\x92\xba\xffJ\x9e\xd6\xffJ\xae\xde\xffJ\xb2\xde\xffJ\xb6\xde\xffJ\xba\xe2\xffJ\xba\xe2\xffJ\xb6\xe2\xffJ\xb6\xde\xffJ\xae\xde\xffJ\xa2\xd6\xff>\x92\xc6\xff\xde\xee\xf2\xff\x00\x00\x00\x00\xfe\xfe\xfe\xffv\xb2\xca\xff>\x92\xce\xff>\xa6\xda\xff>\xae\xde\xff>\xb2\xde\xffn\xca\xea\xff\xd2\xee\xfa\xffJ\xbe\xe2\xff>\xb6\xe2\xff>\xb6\xe2\xff>\xb2\xde\xff>\xa6\xda\xff>\x96\xd2\xffv\xb2\xd2\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xffJ\x96\xbe\xff6\x96\xd2\xff6\xa6\xda\xff6\xae\xde\xff6\xb2\xde\xffj\xca\xea\xff\xfe\xfe\xfe\xff\xf2\xfa\xfe\xffj\xca\xea\xff6\xb6\xde\xff6\xb2\xde\xff6\xaa\xda\xff6\x9a\xd6\xffF\x96\xc6\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xff\x06r\xaa\xff\x16\x8a\xca\xff\x1e\xa2\xd6\xff\x1e\xaa\xda\xff"\xae\xda\xff^\xc6\xe6\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xffv\xce\xea\xff\x1e\xaa\xda\xff\x1e\xa2\xd6\xff\x16\x8e\xce\xff\x06r\xb6\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xff\nr\xae\xff\x0e\x8a\xca\xff\x0e\x9e\xd2\xff\x0e\xa6\xd6\xff\x0e\xaa\xda\xffN\xc2\xe2\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xffj\xca\xea\xff\x0e\xa6\xd6\xff\x0e\x9e\xd2\xff\x0e\x8e\xce\xff\nv\xb6\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xff:\x8e\xba\xff\x16\x8a\xca\xff\x16\x9e\xd2\xff\x16\xa6\xd6\xff\x16\xaa\xda\xffR\xc2\xe6\xff\xfe\xfe\xfe\xff\xf2\xfa\xfe\xffV\xc2\xe6\xff\x16\xae\xda\xff\x16\xaa\xda\xff\x16\xa2\xd6\xff\x16\x92\xce\xff:\x8e\xc6\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xffv\xb2\xca\xff"\x86\xc6\xff"\x9e\xd2\xff"\xaa\xd6\xff"\xae\xda\xffZ\xc6\xe6\xff\xca\xee\xf6\xff6\xb6\xde\xff&\xb2\xda\xff"\xae\xda\xff"\xaa\xd6\xff"\xa2\xd6\xff"\x8e\xca\xffv\xb2\xd2\xff\xfe\xfe\xfe\xff\x00\x00\x00\x00\xde\xee\xf2\xff.\x86\xba\xff.\x9a\xce\xff.\xaa\xd6\xff.\xb2\xda\xff.\xb2\xda\xff6\xb6\xde\xff6\xb6\xde\xff2\xb6\xda\xff.\xb2\xda\xff.\xaa\xd6\xff.\xa2\xd2\xff.\x8a\xc6\xff\xde\xee\xf2\xff\x007M\x05\x00\x00\x00\x00\xfe\xfe\xfe\xff\xa2\xca\xda\xff2\x8e\xc2\xff>\xaa\xd2\xff>\xb2\xda\xff>\xb6\xda\xff>\xba\xda\xff>\xba\xda\xff>\xba\xda\xff>\xb2\xda\xff>\xaa\xd2\xff2\x92\xc6\xff\xa2\xca\xe2\xff\xfe\xfe\xfe\xff\x00;T\x17\x00\x00\x00\x00\x00No\x19\xfe\xfe\xfe\xff\xa2\xca\xda\xffF\x9a\xc6\xffR\xae\xd2\xffR\xb6\xd6\xffR\xba\xd6\xffR\xba\xda\xffR\xba\xd6\xffR\xb2\xd6\xffF\x9e\xca\xff\xa6\xce\xe2\xff\xfe\xfe\xfe\xff\x00B]5\x00,>\r\x00\x00\x00\x00\x00\x00\x00\x00\x00Hg\x0e\xfe\xfe\xfe\xff\xde\xee\xf2\xff\x82\xba\xd2\xffb\xae\xca\xff>\x9e\xc2\xff>\x9e\xc2\xffb\xae\xce\xff\x82\xba\xd6\xff\xde\xee\xf2\xff\xfe\xfe\xfe\xff\x00=W&\x008O\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Fb\x07\x00Ea\x1e\xfe\xfe\xfe\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xff\xfe\xfe\xfe\xff\x00@Z.\x00;T\x18\x008O\x04\x00\x00\x00\x00\x00\x00\x00\x00"""

        return image_data
