import re
from other import getPage, PageNotFound

class Parser_Helper (object):
    """Abstract parser class. Updated 05/28/2009"""
    is_portal = False
    embed_file_extensions = {"video/flv": "flv"} # Most supported sites only distribute flv files
    parser_type = "Generic"

    def __init__ (self, video_id):
        self.video_id = video_id
        self.page_url = self.video_url_str % video_id
        self.embed_file_type = "video/flv" # Normally assumed to be flv if parser does not raise an exception


    def __str__ (self):
        return "<%s: %s>" % (self.__class__.parser_type, self.page_url)

    def __repr__ (self):
        return "<%s: %s>" % (self.__class__.parser_type, self.page_url)


    @classmethod
    def getType (cls):
        return cls.parser_type

    def getEmbedType (self):
        return self.embed_file_type

    def getEmbedExtension (self):
        return self.__class__.embed_file_extensions.get (self.embed_file_type, "flv")

    def getImageString (self):
        return "%s.png" % self.__class__.parser_type


    class LoginRequired (Exception):
        pass

    class UnknownTitle (Exception):
        pass

    class InvalidCommands (Exception):
        pass

    class URLBuildFailed (Exception):
        pass

    class InvalidPortal (Exception):
        pass


    @classmethod
    def checkURL (cls, url):
        match = cls.const_video_url_re.match (url)
        if match:
            return cls (match.group (1))
        else:
            return None


    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.page_url)
        return page, newurl


    def parseVideoPage (self, page_dump):
        if not isinstance (page_dump, str):
            raise TypeError ("Argument must be a string representing the HTML code for a page")

        title = self._parseTitle (page_dump)
        commands = self._parsePlayerCommands (page_dump)
        download_url = self._parseRealURL (commands)
        return title, download_url


    def _parseTitle (self, page_dump):
        match = self.video_title_re.search (page_dump)
        if not match:
            raise self.__class__.UnknownTitle ("Could not find the title")
        else:
            title = match.group (1)
        return title


    def _parsePlayerCommands (self, page_dump):
        """Get the commands needed to get the video player"""
        match = self.video_url_params_re.search (page_dump)
        if not match:
            raise self.__class__.InvalidCommands ("Could not find flash player commands")
        else:
            commands = match.groups ()
        return commands


    def _parseRealURL (self, commands):
        """Abstract function that must be defined in all sub-classes."""
        raise NotImplementedError


class YouTube_Parser (Parser_Helper):
    """Parser for YouTube pages. Updated 03/21/2009"""
    # URLs and RegExp statements from youtube-dl (some slightly modified)
    const_video_url_re = re.compile (r'^(?:http://)?(?:\w+\.)?youtube\.com/(?:v/|(?:watch(?:\.php)?)?\?(?:.+&)?v=)?([0-9A-Za-z_-]+)(?(1)[&/].*)?$')
    video_url_str = 'http://www.youtube.com/watch?v=%s'
    video_url_real_str = 'http://www.youtube.com/get_video?video_id=%s&t=%s'
#    video_url_real_high_str = 'http://www.youtube.com/get_video?video_id=%s&t=%s&fmt=6' # Format seems to no longer exist
    video_url_real_high_str = 'http://www.youtube.com/get_video?video_id=%s&t=%s&fmt=18'
    video_title_re = re.compile (r'<title>YouTube - ([^<]*)</title>')
    video_url_params_re = re.compile (r', "t": "([^"]+)"')
#    video_high_quality_re = re.compile (r'onclick\="changeVideoQuality\(yt\.VideoQualityConstants\.HIGH\); urchinTracker\(\'/Events/VideoWatch/QualityChangeToHigh\'\); return false;">watch in high quality</a>')
    login_required_re = re.compile (r"^http://www.youtube.com/verify_age\?next_url=/watch")
    login_page = "http://www.youtube.com/signup"
    embed_file_extensions = {"video/flv": "flv", "video/mp4": "mp4"}
    parser_type = "YouTube"

    def __init__ (self, video_id):
        super (YouTube_Parser, self).__init__ (video_id)
        self.has_high_version = False


    def getVideoPage (self, account="", password=""):
        if not isinstance (account, str) or not isinstance (password, str):
            raise TypeError ("Passed arguments must be strings")

        if account and password:
            data = {"username": account, "password": password, "action_login": "Log In"}
            page, newurl = getPage (self.login_page, data)
            page, newurl = getPage (self.page_url)
            data = {"next_url": self.page_url, "action_confirm": "Confirm Birth Date"}
            page, newurl = getPage (newurl, data)
            return page, newurl
        elif account or password:
           raise TypeError ("When passing arguments, account name and password must be defined")

        page, newurl = getPage (self.page_url)
        if self.login_required_re.match (newurl):
            raise self.__class__.LoginRequired ("You must be logged in to access this video")
        return page, newurl

    def _parsePlayerCommands (self, page_dump):
        """Get the commands needed to get the video player"""
        match = self.video_url_params_re.search (page_dump)
        if not match:
            raise self.__class__.InvalidCommands ("Could not find flash player commands")

        commands = match.groups ()
        return commands

    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        # First, attempt to get a high quality version
        secondary_url = self.video_url_real_high_str % (self.video_id, commands[0])
        obtained_url = False
        content_type = self.embed_file_type
        try:
            page, real_url, content_type = getPage (secondary_url, read_page=False, get_content_type=True)
            obtained_url = True
        except PageNotFound, e:
            pass

        # Get standard quality if no high quality video exists
        if not obtained_url:
            secondary_url = self.video_url_real_str % (self.video_id, commands[0])
            page, real_url = getPage (secondary_url, read_page=False)

        # Test should not be necessary if it got this far
        if content_type not in ["video/flv", "video/mp4"]:
            raise self.__class__.URLBuildFailed ("An unexpected content type was found. Found: %s" % content_type)
        else:
            self.embed_file_type = content_type

        self.real_url = real_url
        return real_url


class PornoTube_Parser (Parser_Helper):
    """Parser for PornoTube pages. Updated 06/01/2008"""
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
        Parser_Helper.__init__ (self, video_id)


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



class RedTube_Parser (Parser_Helper):
    """Parser for RedTube pages. Updated 06/14/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?redtube\.com/(\d+)$')
    domain_str = "http://www.redtube.com/"
    video_url_str = 'http://www.redtube.com/%s'
    video_url_real_str = 'http://dl.redtube.com/_videos_t4vn23s9jc5498tgj49icfj4678/%s/%s.flv'
    video_title_re = re.compile (r'<h1 class=\'videoTitle\'>([^<]*)</')
    # Mapped translation characters
    video_map_table = ['R', '1', '5', '3', '4', '2', 'O', '7', 'K', '9', 'H', 'B', 'C', 'D', 'X', 'F', 'G', 'A', 'I', 'J', '8', 'L', 'M', 'Z', '6', 'P', 'Q', '0', 'S', 'T', 'U', 'V', 'W', 'E', 'Y', 'N']
    parser_type = "RedTube"

    def __init__ (self, video_id):
        super (RedTube_Parser, self).__init__ (video_id)


    # TODO: Fix to use dynamic expires date
    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.page_url, additional_headers={"Cookie": r'pp="1"; expires="Fri, 16-Dec-2011 02:15:58 PM"; path="/"; domain=.redtube.com; secure=""'}) # Should use a dynamic date
        return page, newurl


    def _parsePlayerCommands (self, page_dump):
        """Get the parent folder index number and file index number for the download url"""
        # Weird ass algorithm used to help figure out the path for the .flv file.
        # Python interpretation of algorithm used for RedTube Downloader

        video_id = int (self.video_id) # Typecast from string (ex. 752)
        parent_index = "%.7d" % (video_id/1000) # 7-digit num. with quotient (int division) padded with 0s (ex. '0000000')
        subindex = "%.7d" % video_id # 7-digit id padded with 0s (ex. '0000752')

        # Add all the results from multiplying integer components of each subindex by i+1
        # and place the string representation in helper. Result is '79' in example
        temp = 0
        for i in range (7):
            temp += int (subindex[i]) * (i+1)
        helper = str (temp)

        # Add integer components of helper. Result is 16 in example
        temp = 0
        for i in helper:
            temp += int (i)

        # 2-digit string that holds the 2nd and 7th characters characters for the file id
        helper = "%.2d" % temp # (ex. '16')
        # Translate the original video id number into the proper file id code
        # Result of example is the string 'J6IA0L1UM'
        file_id = ''
        file_id += self.video_map_table[ord(subindex[3]) - 48 + temp + 3] # table[48-48+16+3] = table[19] = 'J'
        file_id += helper[1] # '6'
        file_id += self.video_map_table[ord(subindex[0]) - 48 + temp + 2] # table[48-48+16+2] = table[18] = 'I'
        file_id += self.video_map_table[ord(subindex[2]) - 48 + temp + 1] # table[48-48+16+1] = table[17] = 'A'
        file_id += self.video_map_table[ord(subindex[5]) - 48 + temp + 6] # table[53-48+16+6] = table[27] = '0'
        file_id += self.video_map_table[ord(subindex[1]) - 48 + temp + 5] # table[48-48+16+5] = table[21] = 'L'
        file_id += helper[0] # '1'
        file_id += self.video_map_table[ord(subindex[4]) - 48 + temp + 7] # table[55-48+16+7] = table[30] = 'U'
        file_id += self.video_map_table[ord(subindex[6]) - 48 + temp + 4] # table[50-48+16+4] = table[22] = 'M'
        commands = (parent_index, file_id)
        return commands


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = self.video_url_real_str % commands
        return real_url


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


class YouPorn_Parser (Parser_Helper):
    """Parser for YouPorn pages. Updated 01/07/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?youporn\.com/watch/(\d+)')
    video_url_str = 'http://www.youporn.com/watch/%s'
    video_url_real_str = 'http://download.youporn.com/download/%s/?%s'
    video_title_re = re.compile (r'<title>([^<]+) - Free Porn Videos - YouPorn.com Lite \(BETA\)</title>')
    video_url_params_re = re.compile (r'<a href="http://download.youporn.com/download/(\d+)/\?(\S+)">FLV - Flash Video format</a>')
    parser_type = "YouPorn"

    def __init__ (self, video_id):
        super (YouPorn_Parser, self).__init__ (video_id)
        self.video_enter_url = self.page_url + '?user_choice=Enter'


    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.video_enter_url)
        return page, newurl


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        page, newurl = getPage (self.video_url_real_str % commands, read_page=False)
        real_url = newurl
        return real_url


class GoogleVideo_Parser (Parser_Helper):
    """Parser for GoogleVideo pages. Updated 05/28/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?video\.google\.com/videoplay\?docid=((?:-)?\d+)')
    video_url_str = 'http://video.google.com/videoplay?docid=%s'
    video_title_re = re.compile (r'<title>([^<]*)</title>')
    video_url_params_re = re.compile (r"<a href=(?:\")?(http://v(\d+)\.(\S+)\.googlevideo.com/videoplayback\?(\S+))(?:\")?>")
    forward_link_re = re.compile (r"document.getElementById\('external_page'\)\.src = \"(\S+)\";")
    embed_file_extensions = {"video/mp4": "mp4"}
    parser_type = "GoogleVideo"

    def __init__ (self, video_id):
        super (GoogleVideo_Parser, self).__init__ (video_id)
        self.embed_file_type = "video/mp4"


    # TODO: CHANGE TO REFLECT NO PORTAL SUPPORT
    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.page_url)
        match = self.forward_link_re.search (page)
        if match:
            page = ""
            newurl = match.group (1)
        return page, newurl


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        #from urllib2 import unquote
        #real_url = unquote (commands[0])
        real_url = commands[0]
        return real_url


class Metacafe_Parser (Parser_Helper):
    """Parser for Metacafe pages. Updated 01/07/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?metacafe\.com/watch/(\S+)/(?:\w+)?')
    video_url_str = 'http://www.metacafe.com/watch/%s/'
    video_title_re = re.compile (r'<title>([^<]*) - Video</title>')
    video_url_params_re = re.compile (r"mediaURL=(\S+)&gdaKey=(\w+)&postRollContentURL=")
    parser_type = "Metacafe"

    def __init__ (self, video_id):
        super (Metacafe_Parser, self).__init__ (video_id)


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        from urllib2 import unquote
        real_url = "%s?__gda__=%s" % (unquote (commands[0]), commands[1])
        return real_url


class Dailymotion_Parser (Parser_Helper):
    """Parser for Dailymotion pages. Updated 04/19/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?dailymotion\.com/(?:\S+)?video/([\w-]+)')
    video_url_str = 'http://www.dailymotion.com/video/%s/'
    video_title_re = re.compile (r'vs_videotitle:"([\S ]+)",vs_user:')
    video_url_params_re = re.compile (r"addVariable\(\"video\", \"([\w\-%\.]+)%40%40spark%7C")
    video_url_real_str = "http://www.dailymotion.com%s"
    parser_type = "Dailymotion"

    def __init__ (self, video_id):
        super (Dailymotion_Parser, self).__init__ (video_id)


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        from urllib2 import unquote
        real_url = self.video_url_real_str % unquote (commands[0])
        return real_url


class Pornhub_Parser (Parser_Helper):
    """Parser for Pornhub pages. Updated 01/07/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?pornhub\.com/view_video.php\?viewkey=(\w+)$')
    domain_str = "http://www.pornhub.com/"
    video_url_str = 'http://www.pornhub.com/view_video.php?viewkey=%s'
    video_title_re = re.compile (r'<title>([^<]*) - Pornhub.com</title>')
    video_url_params_re = re.compile (r'to\.addVariable\("options", "(\S+)"\);')
    video_key_re = re.compile (r"<flv_url>(\S+)</flv_url>")
    parser_type = "Pornhub"

    def __init__ (self, video_id):
        super (Pornhub_Parser, self).__init__ (video_id)


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        from urllib2 import unquote
        video_config_url = unquote (commands[0])
        page, newurl = getPage (video_config_url)
        match = self.video_key_re.search (page)
        if not match:
            raise self.URLBuildFailed ("Could not find video url or position key")
        else:
            secondary_url = match.group (1)

        # Follow redirect
        page, real_url = getPage (secondary_url, read_page=False)
        return real_url


class Tube8_Parser (Parser_Helper):
    """Parser for Tube8 pages. Updated 07/26/2008"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?tube8\.com/(\S+/\S+/\d+)(?:/)?$')
    video_url_str = 'http://www.tube8.com/%s/'
    video_title_re = re.compile (r'">([\S ]+)</h1>')
    video_url_params_re = re.compile (r'param name="FlashVars" value="videoUrl=(\S+)&imageUrl=')
    parser_type = "Tube8"

    def __init__ (self, video_id):
        super (Tube8_Parser, self).__init__ (video_id)


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0]
        return real_url


class MyVideo_Parser (Parser_Helper):
    """Parser for MyVideo pages. Updated 01/08/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?myvideo\.de/watch/(\d+)(?:/\S+)?$')
    video_url_str = 'http://www.myvideo.de/watch/%s/'
    video_title_re = re.compile (r"<td class='globalHd'>([^<]*)</td>")
    video_url_params_re = re.compile (r"<link rel='image_src' href='(\S+)' />")
    parser_type = "MyVideo"

    def __init__ (self, video_id):
        super (MyVideo_Parser, self).__init__ (video_id)


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        partial_url = commands[0].split ("thumbs")[0]
        real_url = "%s%s.flv" % (partial_url, self.video_id)
        return real_url


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


class Guba_Parser (Parser_Helper):
    """Parser for Guba pages. Updated 06/17/2008"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?guba\.com/watch/(\d+)')
    video_url_str = 'http://www.guba.com/watch/%s'
    video_title_re = re.compile (r'var theName="([\S ]+)";')
    video_url_params_re = re.compile (r'"(\S+)" \);\r\n(?:[ ]{32})bfp.writeBlogFlashPlayer\(\);')
    parser_type = "Guba"

    def __init__ (self, video_id):
        super (Guba_Parser, self).__init__ (video_id)


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0]
        return real_url


class GiantBomb_Parser (Parser_Helper):
    """Parser for GiantBomb pages. Updated 02/02/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?giantbomb\.com/(\S+)')
    video_url_str = 'http://www.giantbomb.com/%s'
    video_details_url = 'http://www.giantbomb.com/video/params/%s/'
    video_title_re = re.compile (r'<title><!\[CDATA\[([^\[]*)]]></title>')
    video_embed_code_re = re.compile (r'flashvars="paramsURI=http%3A//www.giantbomb.com/video/params/(\d+)/(?:\?w=1)?"')
    video_url_params_re = re.compile (r'<URI bitRate="700">(\S+)</URI>')
    parser_type = "GiantBomb"

    def __init__ (self, video_id):
        super (GiantBomb_Parser, self).__init__ (video_id)


    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.page_url)
        match = self.video_embed_code_re.search (page)
        if match:
            newurl = self.video_details_url % match.group (1)
            page, newurl = getPage (newurl)
        return page, newurl


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0]
        return real_url


class GirlsInTube_Parser (Parser_Helper):
    """Parser for GirlsInTube pages. Updated 02/22/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?girlsintube\.com/(\S+.\d+)')
    video_url_str = 'http://girlsintube.com/%s'
    video_url_age_post = {'year': '1929', 'month': '1', 'day': '1', 'prescreen_submit': 'Continue'}
    video_title_re = re.compile (r'<div class="player-comments"> <h1>([\S ]+)</h1> ')
    video_url_params_re = re.compile (r"{ 'clip': {'url': '(\S+)', ")
    parser_type = "GirlsInTube"

    def __init__ (self, video_id):
        super (GirlsInTube_Parser, self).__init__ (video_id)


    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.page_url)
        page, newurl = getPage (self.page_url, self.video_url_age_post)
        return page, newurl


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0]
        return real_url


class PacoPorn_Parser (Parser_Helper):
    """Parser for PacoPorn pages. Updated 06/03/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?pacoporn\.com/viewVideo\.php\?video_id=(\d+)(?:&title=(\S+))?')
    domain_str = "http://www.pacoporn.com/"
    video_url_str = 'http://www.pacoporn.com/viewVideo.php?video_id=%s'
    video_details_url_str = "http://www.pacoporn.com/videoConfigXmlCode.php?pg=video_%s_no_0"
    video_title_re = re.compile (r'TEXT Name=\"Header\" Value=\"([\S ]+)\" Enable=')
    video_url_params_re = re.compile (r'PLAYER_SETTINGS Name=\"FLVPath\" Value=\"(\S+)\"')
    parser_type = "PacoPorn"


    def __init__ (self, video_id):
        super (PacoPorn_Parser, self).__init__ (video_id)


    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.__class__.video_details_url_str % self.video_id)
        return page, newurl


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = commands[0]
        return real_url


class Porn2Pc_Parser (Parser_Helper):
    """Non-Parser for Porn2PC pages. Updated 06/03/2009"""
    const_video_url_re = re.compile (r'^((?:http://)?(?:www\.)?porn2pc\.com/)(\S+)')
    video_url_str = 'http://www.porn2pc.com/%s'
    parser_type = "Porn2Pc"


    def __init__ (self, video_id):
        super (Porn2pc_Parser, self).__init__ (video_id)


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



