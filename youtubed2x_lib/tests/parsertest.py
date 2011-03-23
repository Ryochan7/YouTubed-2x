import unittest
from youtubed2x_lib.parsermanager import ParserManager as parser_manager
import youtubed2x_lib.other as other

test_dict = {
    "youtube": "http://www.youtube.com/watch?v=EjI4e3QEoPQ",
    "pornotube": "http://pornotube.com/media.php?m=1610782",
    "redtube": "http://www.redtube.com/9035",
    "veoh": "http://www.veoh.com/videos/v1113892Awt5sqew",
    "veoh_portal": "http://www.veoh.com/videos/v157834969D2enpjt",
    "youporn": "http://www.youporn.com/watch/263247/little-hottie-decides-to-go-all-the-way-23/",
    "google_video": "http://video.google.com/videoplay?docid=-6375437977488723034&ei=pV4RSaeKEZnc-AHktpyMCQ&q=ghost+opera",
    "metacafe": "http://www.metacafe.com/watch/186757/ayumi_hamasaki/",
    "pornhub": "http://www.pornhub.com/view_video.php?viewkey=825c2be0a2800b5ae50f",
    "tube8": "http://www.tube8.com/hardcore/amazing-hentai-lesbian-scene/23954/",
    "myvideo": "http://www.myvideo.de/watch/3026730/Ayumi_Hamasaki_Voyage",
    "myspacetv": "http://vids.myspace.com/index.cfm?fuseaction=vids.individual&videoid=19941883&searchid=a8a1777e-b225-4199-9787-e51cd8f2df2c",
    "guba": "http://www.guba.com/watch/3000017203",
    "dailymotion": "http://www.dailymotion.com/relevance/search/kanon%2B2006/video/x2myny_amv-kanon_school",
    "giantbomb": "http://www.giantbomb.com/final-fantasy-xiii-gameplay-trailer/17-190/",
    "screwattack": "http://screwattack.com/videos/AVGN-Odyssey",
    "gametrailers": "http://www.gametrailers.com/video/angry-video-screwattack/37368",
    "escapistmagazine": "http://www.escapistmagazine.com/videos/view/zero-punctuation/789-Prototype",
    "yahoovideo": "http://video.yahoo.com/watch/125292/",
}

class ParserTest (unittest.TestCase):
    parser_manager.importParsers ()

    def test_page_download (self):
        """Test the page downloader function. Attempt to download the
           page for a YouTube video"""
        page, newurl = other.getPage (test_dict["youtube"])
        self.assert_ (page)

    def _get_information (self, url):
        video = parser_manager.validateURL (url)
        self.assert_ (video, "The URL {0} tested was invalid".format (url))
        video.getVideoInformation ()

    def test_youtube_parser (self):
        url = test_dict["youtube"]
        self._get_information(url)
        
    def test_pornotube_parser (self):
        url = test_dict["pornotube"]
        self._get_information(url)

    def test_redtube_parser (self):
        url = test_dict["redtube"]
        self._get_information(url)

    def test_veoh_parser (self):
        url = test_dict["veoh"]
        self._get_information(url)

    def test_veoh_portal_parser (self):
        url = test_dict["veoh_portal"]
        self._get_information(url)

    def test_youporn_parser (self):
        url = test_dict["youporn"]
        self._get_information(url)

    def test_google_video_parser (self):
        url = test_dict["google_video"]
        self._get_information(url)

    def test_metacafe_parser (self):
        url = test_dict["metacafe"]
        self._get_information(url)

    def test_pornhub_parser (self):
        url = test_dict["pornhub"]
        self._get_information(url)

    def test_tube8_parser (self):
        url = test_dict["tube8"]
        self._get_information(url)

    def test_myvideo_parser (self):
        url = test_dict["myvideo"]
        self._get_information(url)

    def test_myspacetv_parser (self):
        url = test_dict["myspacetv"]
        self._get_information(url)

    def test_guba_parser (self):
        url = test_dict["guba"]
        self._get_information(url)

    def test_dailymotion_parser (self):
        url = test_dict["dailymotion"]
        self._get_information(url)

    def test_giantbomb_parser (self):
        url = test_dict["giantbomb"]
        self._get_information(url)

    def test_screwattack_parser (self):
        url = test_dict["screwattack"]
        self._get_information(url)

    def test_gametrailers_parser (self):
        url = test_dict["gametrailers"]
        self._get_information(url)

    def test_escapistmagazine_parser (self):
        url = test_dict["escapistmagazine"]
        self._get_information(url)

    def test_yahoovideo_parser (self):
        url = test_dict["yahoovideo"]
        self._get_information(url)

    def test_padding (self):
        """Test that proper padding is done in the VideoItem.buildCommandList method"""
        youtube_video = parser_manager.validateURL (test_dict["youtube"])
        youtube_video.title = "Tester"
        youtube_video.setFilePaths (".")
        #youtube_video.setOutputRes (youtube_video.RES_640)

        # Testing against http://www.youtube.com/watch?v=_leYvPpmJGg specs
        command_list = youtube_video.buildCommandList (96, 384, 320, 180)
        padtop = padbottom = None
        for i, value in enumerate (command_list):
            if value == "-padtop": padtop = command_list[i+1]
            elif value == "-padbottom": padbottom = command_list[i+1]

        self.assertEqual (padtop, "30")
        self.assertEqual (padbottom, "30")

        # Testing against http://www.giantbomb.com/50-cent-blood-on-the-sand-video-review/17-289/ specs
        command_list = youtube_video.buildCommandList (96, 384, 640, 368)
        padtop = padbottom = None
        for i, value in enumerate (command_list):
            if value == "-padtop": padtop = command_list[i+1]
            elif value == "-padbottom": padbottom = command_list[i+1]

        self.assertEqual (padtop, "28")
        self.assertEqual (padbottom, "28")


        # Testing against http://video.google.com/videoplay?docid=-8378365891276905720
        # specs
        command_list = youtube_video.buildCommandList (96, 384, 200, 240)
        padleft = padright = None
        for i, value in enumerate (command_list):
            if value == "-padleft": padleft = command_list[i+1]
            elif value == "-padright": padright = command_list[i+1]

        self.assertEqual (padleft, "60")
        self.assertEqual (padright, "60")

if __name__ == '__main__':
    unittest.main()
