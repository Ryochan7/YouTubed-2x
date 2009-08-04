import os
import sys
import ConfigParser
from videoitem import VideoItem
from other import WINDOWS


class SessionInfo (object):
    def __init__ (self):
        self.config_dir = ""
        if WINDOWS:
            # Used with Windows Vista and Windows 7
            if "LOCALAPPDATA" in os.environ:
                self.config_dir = os.path.join (os.environ["LOCALAPPDATA"], "youtubed-2x")
            # Useful for Windows XP and below
            elif "APPDATA" in os.environ:
                self.config_dir = os.path.join (os.environ["APPDATA"], "youtubed-2x")
            else:
                raise Exception ("LOCALAPPDATA nor APPDATA specified. Should not be here.")
        else:
            self.config_dir = os.path.join (os.path.expanduser ("~"), ".youtubed-2x")

        self.session_file_location = os.path.join (self.config_dir, "session_info.conf")
        self.item_list = []


    def read (self):
        if not os.path.exists (self.session_file_location):
            return []

        tempitems = []
        config = ConfigParser.ConfigParser ()
        config.read (self.session_file_location)
        section_list = config.sections ()
        for section in section_list:
            try:
                index = int (section.strip ("session_video_"))
            except ValueError as exception:
                print >> sys.stderr, "Session \"%s\" has invalid identifier" % section
                continue

            try:
                title = config.get (section, "title")
                page_url = config.get (section, "page_url")
                real_url = config.get (section, "real_url")
                flv_file = config.get (section, "flv_file")
                avi_file = config.get (section, "avi_file")
                file_format = config.getint (section, "file_format")
                output_res = config.getint (section, "output_res")
                embed_file_type = config.get (section, "embed_file_type")
                status = config.getint (section, "status")
                file_size = config.getint (section, "file_size")

                tempitems.append ([index, title, page_url, real_url, flv_file, avi_file, file_format, output_res, embed_file_type, file_size, status])
            except (ConfigParser.NoOptionError, TypeError) as exception:
                print >> sys.stderr, "%s: %s" % (exception.__class__.__name__, exception)
                continue
        tempitems.sort (lambda x, y: x[0]-y[0])

        items = []
        for item in tempitems:
            del item[0]
            items.append (item)

        return items


    def addItem (self, item, status):
        if not isinstance (item, VideoItem):
            raise TypeError ("Passed item is invalid. Not a VideoItem object")

        if not isinstance (status, (int, long)):
            raise TypeError ("Passed done value is invalid. Must be a boolean.")
        self.item_list.append ([item, status])


    def save (self):
        if not os.path.isdir (self.config_dir):
            os.mkdir (self.config_dir)

        try:
            file = open (self.session_file_location, "w")
        except (IOError, OSError):
            print >> sys.stderr, "Could not write session file."
            return


        file = open (self.session_file_location, 'w')
        config = ConfigParser.ConfigParser ()
        
        for i, listitem in enumerate (self.item_list):
            status = listitem[1]
            item = listitem[0]
            config.add_section ("session_video_%i" % i)
            config.set ("session_video_%i" % i, "title", item.title)
            config.set ("session_video_%i" % i, "page_url", item.parser.page_url)
            config.set ("session_video_%i" % i, "real_url", item.real_url)
            config.set ("session_video_%i" % i, "flv_file", item.flv_file)
            config.set ("session_video_%i" % i, "avi_file", item.avi_file)
            config.set ("session_video_%i" % i, "file_format", item.file_format)
            config.set ("session_video_%i" % i, "output_res", item.output_res)
            config.set ("session_video_%i" % i, "embed_file_type", item.parser.getEmbedType ())
            config.set ("session_video_%i" % i, "status", status)
            config.set ("session_video_%i" % i, "file_size", item.input_file_size)

        config.write (file)
        file.close ()


    def delete (self):
        if os.path.exists (self.session_file_location):
            os.remove (self.session_file_location)


