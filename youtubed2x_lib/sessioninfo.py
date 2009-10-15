import os
import sys
import ConfigParser
from parsermanager import ParserManager as parser_manager
from other import UserDirectoryIndex


class SessionInfo (object):
    def __init__ (self):
        self.config_dir = UserDirectoryIndex.config_dir
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
                page_url = config.get (section, "page_url")
                youtube_video = parser_manager.validateURL (page_url)
                if not youtube_video:
                    continue

                title = config.get (section, "title")
                youtube_video.setTitle (title)
                real_url = config.get (section, "real_url")
                youtube_video.setRealUrl (real_url)
                flv_file = config.get (section, "flv_file")
                youtube_video.setFlvFile (flv_file)
                avi_file = config.get (section, "avi_file")
                youtube_video.setOutputFile (avi_file)
                file_format = config.getint (section, "file_format")
                youtube_video.setFileFormat (file_format)
                output_res = config.getint (section, "output_res")
                youtube_video.setOutputRes (output_res)
                embed_file_type = config.get (section, "embed_file_type")
                youtube_video.parser.setEmbedType (embed_file_type)
                file_size = config.getint (section, "file_size")
                youtube_video.setFileSize (file_size)
                status = config.getint (section, "status")                

                tempitems.append ([index, SessionItem (youtube_video, status)])
            except (ConfigParser.NoOptionError, TypeError) as exception:
                print >> sys.stderr, "%s: %s" % (exception.__class__.__name__, exception)
                continue
        tempitems.sort (lambda x, y: x[0]-y[0])

        items = []
        for item in tempitems:
            items.append (item[1])

        return items


    def addItem (self, item):
        if not isinstance (item, SessionItem):
            raise TypeError ("Passed item is invalid. Not a SessionItem object")

        self.item_list.append (item)


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
            item = listitem
            config.add_section ("session_video_%i" % i)
            config.set ("session_video_%i" % i, "title", item.video.title)
            config.set ("session_video_%i" % i, "page_url", item.video.parser.page_url)
            config.set ("session_video_%i" % i, "real_url", item.video.real_url)
            config.set ("session_video_%i" % i, "flv_file", item.video.flv_file)
            config.set ("session_video_%i" % i, "avi_file", item.video.avi_file)
            config.set ("session_video_%i" % i, "file_format", item.video.file_format)
            config.set ("session_video_%i" % i, "output_res", item.video.output_res)
            config.set ("session_video_%i" % i, "embed_file_type", item.video.parser.getEmbedType ())
            config.set ("session_video_%i" % i, "status", item.status)
            config.set ("session_video_%i" % i, "file_size", item.video.input_file_size)

        config.write (file)
        file.close ()


    def delete (self):
        if os.path.exists (self.session_file_location):
            os.remove (self.session_file_location)


class SessionItem (object):
    def __init__ (self, video, status):
        self.video = video
        self.status = status


