import os
import sys
import ConfigParser
from videoitem import VideoItem
from other import WINDOWS

class Settings (object):

    class InvalidConfig (Exception):
        pass


    def __init__ (self):
        self.setDefaults ()


    def readConfigFile (self):

        if not os.path.exists (self.config_file_location):
            print "Config file does not exist. Skipping."
            return

        string_keys = ("output_dir", "format", "ffmpeg_location", "proxy_server")
        int_keys = ("vbitrate", "abitrate", "output_res", "proxy_port", "process_limit")
        boolean_keys = ("keep_flv_files", "overwrite", "transcode", "sitedirs", "use_proxy", "auto_download")

        config = ConfigParser.ConfigParser ()
        try:
            config.read (self.config_file_location)
        except ConfigParser.MissingSectionHeaderError:
            raise self.InvalidConfig ("No header is defined")
        except IOError:
            raise self.InvalidConfig ("Could not read config file")

        if not config.has_section ("settings"):
            raise self.InvalidConfig ("Settings header is missing")

        for option in config.options ("settings"):
            if option in string_keys:
                setattr (self, option, config.get ("settings", option))
            elif option in int_keys:
                try:
                    setattr (self, option, config.getint ("settings", option))
                except ValueError:
                    raise self.InvalidConfig ("Attribute %s must be an integer" % option)
            elif option in boolean_keys:
                try:
                    setattr (self, option, config.getboolean ("settings", option))
                except ValueError:
                    raise self.InvalidConfig ("Attribute %s must be True or False" % option)

        if not os.path.isdir (self.output_dir):
            raise self.InvalidConfig ("Directory \"%s\" does not exist" % self.output_dir)

        if not os.path.exists (self.ffmpeg_location):
            raise self.InvalidConfig ("FFmpeg location \"%s\" is invalid" % self.ffmpeg_location)

        if isinstance (self.format, str):
            if self.format == "avi":
                self.format = VideoItem.AVI_FILE
            elif self.format == "mpeg4":
                self.format = VideoItem.MP4_AVI_FILE
            elif self.format == "mp3":
                self.format = VideoItem.MP3_FILE
            else:
                raise self.InvalidConfig ("Attribute format is invalid")

        if self.vbitrate > 2000 or self.vbitrate < 384: self.vbitrate = 384
        elif self.vbitrate % 8 != 0: self.vbitrate = 384
        if self.abitrate > 384 or self.abitrate < 32: self.abitrate = 128
        elif self.abitrate % 32: self.abitrate = 32

        if self.output_res != VideoItem.RES_320 and self.output_res != VideoItem.RES_640:
            raise self.InvalidConfig ("Attribute resolution is invalid")

        if self.process_limit < 0:
            raise self.InvalidConfig ("Process limit is invalid. Must be >= 0")

        return


    def writeConfigFile (self):

        if not os.path.isdir (self.config_dir):
            os.mkdir (self.config_dir)

        try:
            file = open (self.config_file_location, "w")
        except (IOError, OSError):
            print >> sys.stderr, "Could not write config file."
            return

        config = ConfigParser.ConfigParser ()
        config.add_section ("settings")
        config.set ("settings", "output_dir", self.output_dir)
        config.set ("settings", "keep_flv_files", self.keep_flv_files)
        if self.format == VideoItem.AVI_FILE:
            config.set ("settings", "format", "avi")
        elif self.format == VideoItem.MP4_AVI_FILE:
            config.set ("settings", "format", "mpeg4")
        elif self.format == VideoItem.MP3_FILE:
            config.set ("settings", "format", "mp3")

        config.set ("settings", "vbitrate", self.vbitrate)
        config.set ("settings", "abitrate", self.abitrate)
        config.set ("settings", "overwrite", self.overwrite)
        config.set ("settings", "transcode", self.transcode)
        config.set ("settings", "ffmpeg_location", self.ffmpeg_location)
        config.set ("settings", "sitedirs", self.sitedirs)
        config.set ("settings", "output_res", self.output_res)
        config.set ("settings", "use_proxy", self.use_proxy)
        if self.proxy_server and self.proxy_port:
            config.set ("settings", "proxy_server", self.proxy_server)
            config.set ("settings", "proxy_port", self.proxy_port)

        config.set ("settings", "process_limit", self.process_limit)
        config.set ("settings", "auto_download", self.auto_download)
        config.write (file)
        return


    def setDefaults (self):
        self.vbitrate = 384
        self.abitrate = 128
        self.format = VideoItem.MP4_AVI_FILE
        self.transcode = True
        self.overwrite = False
        self.keep_flv_files = True
        if WINDOWS:
            self.output_dir = os.path.join (os.path.expanduser ("~"), "My Documents", "My Videos")
        else:
            self.output_dir = os.path.join (os.path.expanduser ("~"), "Videos")
        self.ffmpeg_location = os.path.join (sys.prefix, "bin", "ffmpeg")
        self.sitedirs = False

        if not os.path.isdir (self.output_dir):
            os.mkdir (self.output_dir)

        if WINDOWS:
            self.config_dir = os.path.join (os.path.expanduser ("~"), "Application Data", "youtubed-2x")
        else:
            self.config_dir = os.path.join (os.path.expanduser ("~"), ".youtubed-2x")
        self.config_file_location = os.path.join (self.config_dir, "config.conf")

        possible_paths = (os.path.join (sys.prefix, "local", "bin"), os.path.join (sys.prefix, "bin"),)
        if not os.path.exists (self.ffmpeg_location):
            if not WINDOWS:
                for path in possible_paths:
                    if os.path.exists (os.path.join (path, "ffmpeg")):
                        self.ffmpeg_location = os.path.join (path, "ffmpeg")
                        break
            elif os.path.exists (os.path.join ("bin", "ffmpeg.exe")):
                self.ffmpeg_location = os.path.abspath (os.path.join ("bin", "ffmpeg.exe"))

        self.output_res = VideoItem.RES_320
        self.use_proxy = False
        self.proxy_server = ""
        self.proxy_port = 1
        self.process_limit = 4
        self.auto_download = True

        #print self.ffmpeg_location

