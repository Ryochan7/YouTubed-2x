import unittest
from youtubed2x_lib.parsermanager import parser_manager
import youtubed2x_lib.other as other

testURLs = ("http://www.youtube.com/watch?v=EjI4e3QEoPQ",
"http://pornotube.com/media.php?m=1610782",
"http://www.redtube.com/9035",
"http://www.veoh.com/videos/v1113892Awt5sqew", # Check Veoh native support
"http://www.veoh.com/videos/v157834969D2enpjt", # Check Veoh portal support
"http://www.youporn.com/watch/263247/little-hottie-decides-to-go-all-the-way-23/",
"http://video.google.com/videoplay?docid=-6375437977488723034&ei=pV4RSaeKEZnc-AHktpyMCQ&q=ghost+opera",
"http://www.metacafe.com/watch/186757/ayumi_hamasaki/",
"http://www.pornhub.com/view_video.php?viewkey=825c2be0a2800b5ae50f",
"http://www.tube8.com/hardcore/amazing-hentai-lesbian-scene/23954/",
"http://www.myvideo.de/watch/3026730/Ayumi_Hamasaki_Voyage",
"http://vids.myspace.com/index.cfm?fuseaction=vids.individual&videoid=19941883&searchid=a8a1777e-b225-4199-9787-e51cd8f2df2c",
"http://www.guba.com/watch/3000017203?duration_step=0&fields=23&filter_tiny=0&pp=40&query=kanon%202006&sb=10&set=-1&sf=0&size_step=0&o=1&sample=1225875586:e1ebff36f1214e71528291dcb086a919a88ca379",
"http://www.dailymotion.com/relevance/search/kanon%2B2006/video/x2myny_amv-kanon_school",
"http://www.giantbomb.com/news/ogle-the-final-fantasy-xiii-trailer-repeatedly/872/",
"http://www.porn2pc.com/9035", # Example points to RedTube-style URL
)


class ParseTest (unittest.TestCase):

    def testUrlValidation (self):
        """Test the regular expressions for each parser"""
        for URL in testURLs:
            youtube_video = parser_manager.validateURL (URL)
            self.assert_ (youtube_video, "The URL (%s) tested was invalid" % URL)


    def testPageDownload (self):
        """Test the page downloader function. Attempt to download the
           page for a YouTube video
        """
        page, newurl = other.getPage (testURLs[0])
        self.assert_ (page)


    def testVideoUrlParse (self):
        """ Test each parser and get the information for a video """
        print ""
        for URL in testURLs:
            youtube_video = parser_manager.validateURL (URL)
            self.assert_ (youtube_video, "The URL (%s) tested was invalid" % URL)
            print "Testing parser type: %s" % youtube_video.parser.getType ()
            youtube_video.getVideoInformation ()


    def testPadding (self):
        """Test that proper padding is done in the VideoItem.buildCommandList method"""
        youtube_video = parser_manager.validateURL (testURLs[0])
        youtube_video.title = "Tester"
        youtube_video.setFilePaths (".")
        #youtube_video.setOutputRes (youtube_video.__class__.RES_640)
        
        # Testing against http://www.youtube.com/watch?v=_leYvPpmJGg specs
        command_list = youtube_video.buildCommandList (384, 320, 180)
        padtop = padbottom = None
        for i, value in enumerate (command_list):
            if value == "-padtop": padtop = command_list[i+1]
            elif value == "-padbottom": padbottom = command_list[i+1]

        self.assertEqual (padtop, "30")
        self.assertEqual (padbottom, "30")

        # Testing against http://www.giantbomb.com/50-cent-blood-on-the-sand-video-review/17-289/ specs
        command_list = youtube_video.buildCommandList (384, 640, 368)
        padtop = padbottom = None
        for i, value in enumerate (command_list):
            if value == "-padtop": padtop = command_list[i+1]
            elif value == "-padbottom": padbottom = command_list[i+1]

        self.assertEqual (padtop, "28")
        self.assertEqual (padbottom, "28")


        # Testing against http://video.google.com/videoplay?docid=-8378365891276905720 
        # specs
        command_list = youtube_video.buildCommandList (384, 200, 240)
        padleft = padright = None
        for i, value in enumerate (command_list):
            if value == "-padleft": padleft = command_list[i+1]
            elif value == "-padright": padright = command_list[i+1]

        self.assertEqual (padleft, "60")
        self.assertEqual (padright, "60")


if __name__ == "__main__":
    unittest.main ()

