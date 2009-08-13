import os
import sys
import ConfigParser
from videoitem import VideoItem
from other import WINDOWS, UserDirectoryIndex

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
            raise self.__class__.InvalidConfig ("No header is defined")
        except IOError:
            raise self.__class__.InvalidConfig ("Could not read config file")

        if not config.has_section ("settings"):
            raise self.__class__.InvalidConfig ("Settings header is missing")

        for option in config.options ("settings"):
            if option in string_keys:
                setattr (self, option, config.get ("settings", option))

            elif option in int_keys:
                try:
                    setattr (self, option, config.getint ("settings", option))
                except ValueError as exception:
                    raise self.__class__.InvalidConfig ("%s" % exception.args)
                except TypeError as exception:
                    raise self.__class__.InvalidConfig ("%s" % exception.args)

            elif option in boolean_keys:
                try:
                    setattr (self, option, config.getboolean ("settings", option))
                except ValueError as exception:
                    raise self.__class__.InvalidConfig ("%s" % exception.args)
                except TypeError as exception:
                    raise self.__class__.InvalidConfig ("%s" % exception.args)


        if not os.path.isdir (self.output_dir):
            raise self.__class__.InvalidConfig ("Directory \"%s\" does not exist" % self.output_dir)

        if not os.path.exists (self.ffmpeg_location):
            raise self.__class__.InvalidConfig ("FFmpeg location \"%s\" is invalid" % self.ffmpeg_location)

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
        file.close ()
        return


    def setDefaults (self):
        self.vbitrate = 384
        self.abitrate = 128
        self.format = VideoItem.MP4_AVI_FILE
        self.transcode = True
        self.overwrite = False
        self.keep_flv_files = True
        if WINDOWS:
            import ctypes
            dll = ctypes.windll.shell32
            buf = ctypes.create_string_buffer (300)
            # 0x000E corresponds to CSIDL_MYVIDEO environment variable
            dll.SHGetSpecialFolderPathA (None, buf, 0x000E, False)
            self.output_dir = buf.value
        else:
            self.output_dir = os.path.join (os.path.expanduser ("~"), "Videos")
        self.ffmpeg_location = os.path.join (sys.prefix, "bin", "ffmpeg")
        self.sitedirs = False

        if not os.path.isdir (self.output_dir):
            os.mkdir (self.output_dir)

        self.config_dir = UserDirectoryIndex.config_dir
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


    def _get_output_dir (self):
        return self._output_dir

    def _set_output_dir (self, value):
        if isinstance (value, str):
            self._output_dir = value
        else:
            raise TypeError ("output_dir value must be passed as a string")

    output_dir = property (_get_output_dir, _set_output_dir)


    def _get_vbitrate (self):
        return self._vbitrate

    def _set_vbitrate (self, value):
        if isinstance (value, int) and value <= 2000 and (value % 32) == 0:
            self._vbitrate = value
        elif isinstance (value, int) and value <= 2000:
            raise ValueError ("vbitrate value must be divisible by 8")
        elif is_int and (value % 8) == 0:
            raise ValueError ("vbitrate value passed greater than 2000")
        else:
            raise TypeError ("vbitrate must be an integer")

    vbitrate = property (_get_vbitrate, _set_vbitrate)


    def _get_abitrate (self):
        return self._abitrate

    def _set_abitrate (self, value):
        is_int = isinstance (value, int)
        if is_int and value <= 384 and (value % 32) == 0:
            self._abitrate = value
        elif is_int and value <= 384:
            raise ValueError ("abitrate must be divisible by 32")
        elif is_int and (value % 32) == 0:
            raise ValueError ("abitrate value passed greater than 384")
        else:
            raise TypeError ("abitrate must be an integer")

    abitrate = property (_get_abitrate, _set_abitrate)


    def _get_format (self):
        return self._format

    def _set_format (self, value):
        if isinstance (value, str):
            if value == "avi":
                self._format = VideoItem.AVI_FILE
            elif value == "mpeg4":
                self._format = VideoItem.MP4_AVI_FILE
            elif value == "mp3":
                self._format = VideoItem.MP3_FILE
            else:
                raise ValueError ("Invalid format string passed")
        elif isinstance (value, int):
            if value in VideoItem.VIDEO_FORMATS or value in VideoItem.AUDIO_FORMATS:
                self._format = value
            else:
                raise ValueError ("Invalid format integer passed")
        else:
            raise TypeError ("format attribute is invalid")

    format = property (_get_format, _set_format)


    def _get_transcode (self):
        return self._transcode

    def _set_transcode (self, value):
        if isinstance (value, bool):
            self._transcode = value
        else:
            raise TypeError ("transcode value must be a boolean")

    transcode = property (_get_transcode, _set_transcode)


    def _get_overwrite (self):
        return self._overwrite

    def _set_overwrite (self, value):
        if isinstance (value, bool):
            self._overwrite = value
        else:
            raise TypeError ("overwrite value must be a boolean")

    overwrite = property (_get_overwrite, _set_overwrite)


    def _get_keep_flv_files (self):
        return self._keep_flv_files

    def _set_keep_flv_files (self, value):
        if isinstance (value, bool):
            self._keep_flv_files = value
        else:
            raise TypeError ("keep_flv_files value must be a boolean")

    keep_flv_files = property (_get_keep_flv_files, _set_keep_flv_files)


    def _get_ffmpeg_location (self):
        return self._ffmpeg_location

    def _set_ffmpeg_location (self, value):
        if isinstance (value, str):
            self._ffmpeg_location = value
        else:
            raise TypeError ("ffmpeg location must be given as a string")

    ffmpeg_location = property (_get_ffmpeg_location, _set_ffmpeg_location)


    def _get_sitedirs (self):
        return self._sitedirs

    def _set_sitedirs (self, value):
        if isinstance (value, bool):
            self._sitedirs = value
        else:
            raise TypeError ("sitedirs value must be a boolean")

    sitedirs = property (_get_sitedirs, _set_sitedirs)


    def _get_config_dir (self):
        return self._config_dir

    def _set_config_dir (self, value):
        if isinstance (value, str):
            self._config_dir = value
        else:
            raise TypeError ("config_dir location must be given as a string")

    config_dir = property (_get_config_dir, _set_config_dir)


    def _get_config_file_location (self):
        return self._config_file_location

    def _set_config_file_location (self, value):
        if isinstance (value, str):
            self._config_file_location = value
        else:
            raise TypeError ("config_file_location location must be given as a string")

    config_file_location = property (_get_config_file_location, _set_config_file_location)


    def _get_output_res (self):
        return self._output_res

    def _set_output_res (self, value):
        is_int = isinstance (value, int)
        if is_int and (value == VideoItem.RES_320 or value == VideoItem.RES_640):
            self._output_res = value
        elif is_int:
            raise ValueError ("output_res is not a valid resolution")
        else:
            raise TypeError ("output_res must be an integer")


    output_res = property (_get_output_res, _set_output_res)


    def _get_use_proxy (self):
        return self._use_proxy

    def _set_use_proxy (self, value):
        if isinstance (value, bool):
            self._use_proxy = value
        else:
            raise TypeError ("use_proxy value must be a boolean")

    use_proxy = property (_get_use_proxy, _set_use_proxy)


    def _get_proxy_server (self):
        return self._proxy_server

    def _set_proxy_server (self, value):
        if isinstance (value, str):
            self._proxy_server = value
        else:
            raise TypeError ("proxy_server must be given as a string")

    proxy_server = property (_get_proxy_server, _set_proxy_server)


    def _get_proxy_port (self):
        return self._proxy_port

    def _set_proxy_port (self, value):
        if isinstance (value, int):
            self._proxy_port = value
        else:
            raise TypeError ("proxy_port must be an integer")

    proxy_port = property (_get_proxy_port, _set_proxy_port)


    def _get_process_limit (self):
        return self._process_limit

    def _set_process_limit (self, value):
        is_int = isinstance (value, int)
        if is_int and value >= 0:
            self._process_limit = value
        elif is_int:
            raise ValueError ("process_limit is invalid. Must be >= 0")
        else:
            raise TypeError ("process_limit must be an integer")

    process_limit = property (_get_process_limit, _set_process_limit)


    def _get_auto_download (self):
        return self._auto_download

    def _set_auto_download (self, value):
        if isinstance (value, bool):
            self._auto_download = value
        else:
            raise TypeError ("auto_download value must be a boolean")

    auto_download = property (_get_auto_download, _set_auto_download)


