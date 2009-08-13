import os, sys
import re
import subprocess
from other import WINDOWS


class VideoItem (object):
    command_dict = {'application': 'ffmpeg', 'vcodec': 'libxvid', 'vres': '320x240', 'bitrate': '%ik', 'acodec': 'copy', 'output_file': '%s', 'abitrate': '%ik'}
    resolution_re = re.compile (r"[ ]+Stream \#\d{1}\.\d{1}(?:\(und\))?: Video: \w+, \w+, (\d+)x(\d+).*")

    MAX_MP3_BITRATE = 384
    MIN_MP3_BITRATE = 32
    MAX_VID_BITRATE = 1024
    MIN_VID_BITRATE = 128

    MP4_AVI_FILE, AVI_FILE, MP3_FILE = range (0,3)
    VIDEO_FORMATS = [MP4_AVI_FILE, AVI_FILE]
    AUDIO_FORMATS = [MP3_FILE]
    _format_choices = list ()
    _format_choices.extend (VIDEO_FORMATS)
    _format_choices.extend (AUDIO_FORMATS)
    RES_320, RES_640 = range (0,2)

    def __init__ (self, site_parser):
#       print type (site_parser)
        self.title = ""
        self.real_url = ""
        self.flv_file = ""
        self.avi_file = ""
        self.file_format = self.__class__.AVI_FILE
        self.parser = site_parser
        self.output_res = self.__class__.RES_320
        self.input_file_size = -1


    def __str__ (self):
        return "<Video: %s>" % self.title


    def __repr__ (self):
        return "<Video: %s>" % self.title


    def getVideoInformation (self, account="", password=""):
        if not isinstance (account, str) or not isinstance (password, str):
            raise TypeError ("Username and password arguments must be strings")

        page = newurl = ""
        # VERY primitive video portal support
        if self.parser.is_portal:
            # Get initial video page
            if account or password:
                page, newurl = self.parser.getVideoPage (account, password)
            else:
                page, newurl = self.parser.getVideoPage ()

            # If no data was passed, assume that the portal is forwarding to a new site
            if not page:
                # Check if the portal forwarded to a site that is supported
                from parsermanager import ParserManager as parser_manager
                parser = parser_manager.validateURL (newurl, False)
                if not parser:
                    raise self.parser.InvalidPortal ("The portal forwarded to a site not supported by this application")
                # Check if the parser has changed by checking the page urls
                elif self.parser.page_url != parser.page_url:
                    self.parser = parser

                # Get real video page data
                if account or password:
                    page, newurl = self.parser.getVideoPage (account, password)
                else:
                    page, newurl = self.parser.getVideoPage ()


        elif account or password:
            page, newurl = self.parser.getVideoPage (account, password)
        else:
            page, newurl = self.parser.getVideoPage ()

        title, download_url, headers = self.parser.parseVideoPage (page)
        self.setTitle (title)
        self.real_url = download_url
        if headers.get ("Content-Length"):
            self.input_file_size = long (headers.get ("Content-Length"))

        return True



    def setTitle (self, newtitle):
        """Replace characters that cannot be used for the filename \
in a FAT32 filesystem. Incomplete"""
        if not isinstance (newtitle, str):
            raise TypeError ("Argument must be a string")

        has_pango = False
        try:
            import pango, gobject
            has_pango = True
        except ImportError:
            has_pango = False

        if has_pango:
            # parse_markup fails on unescaped markup. Common scenario would be unescaped ampersand.
            # It is bad practices but ignore an exception if raised.
            try:
                newtitle = pango.parse_markup (newtitle)[1]
            except gobject.GError:
                pass

        newtitle = newtitle.replace ('"', '')
        newtitle = newtitle.replace ('/', ' ')
        newtitle = newtitle.replace ('\\', ' ')
        newtitle = newtitle.replace ('|', '')
        newtitle = newtitle.replace ('?', '')
        newtitle = newtitle.replace (':', '')
        self.title = newtitle


    def setOutputRes (self, res_choice):
        if (res_choice == self.__class__.RES_320) or (res_choice == self.__class__.RES_640):
            self.output_res = res_choice
        else:
            raise Exception ("Invalid resolution was passed.")


    def setFileFormat (self, format_id):
        if format_id in self._format_choices:
            self.file_format = format_id


    def setFlvFile (self, path):
        self.flv_file = path


    def setOutputFile (self, path):
        self.avi_file = path


    def setRealUrl (self, url):
        self.real_url = url


    def setFileSize (self, size):
        if not isinstance (size, (int, long)):
            raise Exception ("File size must be a int or long")
        elif size < -1:
            raise Exception ("File size can be no lower than -1")
        else:
            self.input_file_size = size


    def getFileSize (self):
        return self.input_file_size


    def setFilePaths (self, directory):
        flv_file = os.path.join (directory, "%s.%s" % (self.title, self.parser.getEmbedExtension ()))
        self.setFlvFile (flv_file)
        avi_file = os.path.join (directory, self.getOutputFileName ())
        self.setOutputFile (avi_file)


    @staticmethod
    def setFFmpegLocation (path):
        VideoItem.command_dict.update ({"application": path})


    def getOutputFileName (self):
        if self.file_format in self.VIDEO_FORMATS:
            return "%s.avi" % self.title
        else:
            return "%s.mp3" % self.title


    def buildCommandList (self, bitrate, length=None, width=None):
        if not isinstance (bitrate, int):
            raise TypeError ("Bitrate must be an integer")
        elif length and not isinstance (length, int):
            raise TypeError ("Video length must be an integer")
        elif width and not isinstance (width, int):
            raise TypeError ("Video width must be an integer")

        ignore_mimetypes = ("audio/mpeg", "audio/mp3", "audio/ogg",)
        if self.parser.getEmbedType () in ignore_mimetypes:
            return []

        commands = list ()
        temp_commands = self.command_dict.copy ()
        temp_commands.update ({'input_file': self.flv_file})
        temp_commands.update ({'bitrate': '%ik' % bitrate})
        temp_commands.update ({'output_file': self.avi_file})


        if self.file_format == self.AVI_FILE or self.file_format == self.MP4_AVI_FILE:
            output_length = output_width = 0
            if self.output_res == self.__class__.RES_640:
                output_length = 640
                output_width = 480
                temp_commands.update ({"vres": "%ix%i" % (output_length, output_width)})
            else:
                output_length = 320
                output_width = 240
                

            # Add padding to video if needed. This method might be as
            # good as I can get it
            if length and width and (float (length)/width) != (float (output_length)/output_width):
                pad_left = pad_right = pad_top = pad_bottom = 0
                new_width = width
                new_length = length

                new_width = (width * output_length) / length
                if new_width % 2 != 0:
                    new_width -= 1

                if new_width <= output_width:
                    new_length = int (new_width * (float (length)/width))
                    # Continue to downscale until a valid resolution is found
                    while (new_length % 2 != 0 and new_width > 0):
                        new_width -= 2
                        new_length = int (new_width * (float (length)/width))
                elif new_width > output_width:
                    new_length = (output_width * length) / width
                    if new_length % 2 != 0:
                        new_length -= 1
                    new_width = int (new_length / (float (length)/width))
                    # Continue to downscale until a valid resolution is found
                    while (new_width % 2 != 0 and new_length > 0):
                        new_length -= 2
                        new_width = int (new_length / (float (length)/width))

                pad_top = pad_bottom = (output_width - new_width) / 2
                pad_left = pad_right = (output_length - new_length) / 2
                if pad_top % 2 != 0:
                    pad_top += 1
                    pad_bottom -= 1
                if pad_left % 2 != 0:
                    pad_left += 1
                    pad_right -= 1

                if pad_top: temp_commands.update ({"pad_top": "%i" % pad_top})
                if pad_bottom: temp_commands.update ({"pad_bottom": "%i" % pad_bottom})
                if pad_left: temp_commands.update ({"pad_left": "%i" % pad_left})
                if pad_right: temp_commands.update ({"pad_right": "%i" % pad_right})
                if new_length > 0 and new_width > 0: temp_commands.update ({"vres": "%ix%i" % (new_length, new_width)})
#                print new_length
#                print new_width


        if self.file_format == self.AVI_FILE or self.file_format == self.MP4_AVI_FILE:
            commands.append (temp_commands['application'])
            commands.append ('-y')
            commands.append ('-i')
            commands.append (temp_commands['input_file'])
            commands.append ('-vcodec')
            if self.file_format == self.MP4_AVI_FILE:
                temp_commands.update ({"vcodec": "mpeg4"})
            elif self.file_format == self.AVI_FILE:
                temp_commands.update ({"vcodec": "libxvid"})
            commands.append (temp_commands['vcodec'])
            commands.append ('-s')
            commands.append (temp_commands['vres'])
            commands.append ('-b')
            commands.append (temp_commands['bitrate'])
            commands.append ('-acodec')
            # Check that the input file is an flv file
            # If it is, copy audio track. Else, re-encode audio track
            if self.parser.getEmbedType () == "video/flv":
                commands.append (temp_commands['acodec'])
            else:
                commands.append ("libmp3lame")
                commands.append ('-ab')
                commands.append ("%ik" % 128)

            # Add padding if needed
            if "pad_top" in temp_commands:
                commands.append ("-padtop")
                commands.append (temp_commands["pad_top"])
            if "pad_bottom" in temp_commands:
                commands.append ("-padbottom")
                commands.append (temp_commands["pad_bottom"])
            if "pad_left" in temp_commands:
                commands.append ("-padleft")
                commands.append (temp_commands["pad_left"])
            if "pad_right" in temp_commands:
                commands.append ("-padright")
                commands.append (temp_commands["pad_right"])

            # Set DIVX for FourCC tag when encoding to MP4
            # otherwise GP2X will not play the file
            if self.file_format == self.__class__.MP4_AVI_FILE:
                commands.append ("-vtag")
                commands.append ("DIVX")

            # Aspect ratio needs to be specified to encode xvid when using r13712 of ffmpeg
            # (0/1 ratio otherwise and fails).
            # Is not necessary when encoding to mpeg4 but it will be used anyway
            commands.append ("-aspect")
            commands.append ("4:3")

            commands.append (temp_commands['output_file'])

        elif self.file_format == self.MP3_FILE:
            temp_commands.update ({'acodec': 'libmp3lame'})
            commands.append (temp_commands['application'])
            commands.append ('-y')
            commands.append ('-i')
            commands.append (temp_commands['input_file'])
            commands.append ('-acodec')
            commands.append (temp_commands['acodec'])
            commands.append ('-ab')
            commands.append (temp_commands['bitrate'])
            commands.append (temp_commands['output_file'])

#        print commands
        return commands


    def transcodeVideo (self, bitrate):
        """Transcodes the input .flv file into a GP2X-compatible media file"""
        if not isinstance (bitrate, int):
            raise TypeError ("Bitrate must be an integer")

        print "Transcoding '%s'" % os.path.basename (self.flv_file)
        print
        status = 90

        if self.file_format == self.AVI_FILE or self.file_format == self.MP4_AVI_FILE:
            if bitrate > self.__class__.MAX_VID_BITRATE or bitrate < self.__class__.MIN_VID_BITRATE or (bitrate % 8 != 0):
                print >> sys.stderr, "You specified an invalid video bitrate for transcoding."
                return False
            else:
                process = subprocess.Popen ([self.command_dict["application"], "-i", self.flv_file], stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                status = process.wait ()
                match = self.__class__.resolution_re.search (process.stderr.read ())

                if match:
                    vid_length, vid_width = match.groups ()
                    vid_length, vid_width = int (vid_length), int (vid_width)
                    command = self.buildCommandList (bitrate, vid_length, vid_width)
                else:
                    command = self.buildCommandList (bitrate)

                if not WINDOWS:
                    process = subprocess.Popen (command, universal_newlines=True, close_fds=True)
                else:
                    process = subprocess.Popen (command, universal_newlines=True)
                status = process.wait ()
        elif self.file_format == self.MP3_FILE:
            if bitrate > self.__class__.MAX_MP3_BITRATE or bitrate < self.__class__.MIN_MP3_BITRATE or (bitrate % 4 != 0):
                print >> sys.stderr, "You specified an invalid audio bitrate for transcoding."
                return False
            else:
                command = self.buildCommandList (bitrate)
                if not WINDOWS:
                    process = subprocess.Popen (command, universal_newlines=True, close_fds=True)
                else:
                    process = subprocess.Popen (command, universal_newlines=True)

                status = process.wait ()
        print
        if status:
            return False
        return True


