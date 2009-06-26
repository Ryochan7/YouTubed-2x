from urllib2 import urlparse
from parsers import Parser_Helper
from other import WINDOWS
from videoitem import VideoItem


class ParserManager (object):
    def __init__ (self):
        self.parsers = {}
        self._register_app_parsers ()
        self._register_user_parsers ()


    def register (self, parser):
        if not issubclass (parser, Parser_Helper):
            raise TypeError ("A subclass of Parser_Helper was not passed")

        identifier = parser.host_str
        self.parsers.update ({identifier: parser})
#        print self.parsers[identifier]
#        print identifier


    def _register_app_parsers (self):
        import os, sys

        file_list = os.listdir (os.path.join (__package__, "parsers"))
        if "__init__.py" in file_list:
            file_list.remove ("__init__.py")

#        print file_list
        for file in file_list:
            if file.endswith (".py"):
                possible_module = file.rstrip (".py")
            # Useful for Py2exe build
            elif file.endswith (".pyo"):
                possible_module = file.rstrip (".pyo")
            else:
                possible_module = None

            if not possible_module:
                continue

#            print "DUDE parsers.%s" % possible_module

            try:
                exec ("import parsers.%s" % possible_module)
            except ImportError as exception:
                print >> sys.stderr, "File \"%s\" could not be imported" % possible_module
                continue

            parser_module = eval ("parsers.%s" % possible_module)
#            print parser_module

            module_contents = dir (parser_module)
            parser = None
            for item in module_contents:
                if item.endswith ("_Parser") and item.lower () == "%s_parser" % possible_module:
                    parser = getattr (parser_module, item)

            if parser and issubclass (parser, Parser_Helper):
                print parser
                self.register (parser)

#        print self.parsers


    def _register_user_parsers (self):
        import os, sys
        home_dir = os.path.expanduser ("~")
        if WINDOWS:
            config_dir = os.path.join (home_dir, "Application Data", "youtubed-2x")
        else:
            config_dir = os.path.join (home_dir, ".youtubed-2x")

        user_parser_dir = os.path.join (config_dir, "parsers")

        if not os.path.exists (config_dir):
            os.mkdir (config_dir)

        if not os.path.exists (user_parser_dir):
            os.mkdir (user_parser_dir)

        file_list = os.listdir (user_parser_dir)
        if "__init__.py" in file_list:
            file_list.remove ("__init__.py")

        sys.path.insert (1, user_parser_dir)

#        print sys.path
#        print file_list

        for file in file_list:
            if file.endswith (".py"):
                possible_module = file.rstrip (".py")
            # Useful for Py2exe build
            elif file.endswith (".pyo"):
                possible_module = file.rstrip (".pyo")
            else:
                possible_module = None

#            print possible_module

            if not possible_module:
                continue

            try:
                exec ("import %s" % possible_module)
            except ImportError as exception:
                print >> sys.stderr, "File \"%s\" could not be imported" % possible_module
                continue

            parser_module = eval (possible_module)
#            print parser_module

            module_contents = dir (parser_module)
            parser = None
            for item in module_contents:
                if item.endswith ("_Parser") and item.lower () == "%s_parser" % possible_module:
                    parser = getattr (parser_module, item)

            if parser and issubclass (parser, Parser_Helper):
                print parser
                self.register (parser)

        del sys.path[1]
#        print "HAM"

    
    def validateURL (self, full_url, video_item=True):
        """Make sure the url passed is in a valid form and return a video parser object"""
        if not isinstance (full_url, str):
            raise TypeError ("Argument must be a string")

#        print full_url
        youtube_video = None
        spliturl = urlparse.urlsplit (full_url)
        hostname = spliturl.hostname
        print len (self.parsers.keys ())

        if not hostname:
            return None
        elif hostname.startswith ("www."):
            hostname = hostname.lstrip ("www.")
#        hostname = hostname.split (".")[0]

#        print hostname
        if hostname not in self.parsers:
            return None

#        import time
#        start_time = time.time ()
        page_parser = self.parsers[hostname].checkURL (full_url)
        if page_parser:
            if video_item:
                youtube_video = VideoItem (page_parser)
            elif page_parser:
                youtube_video = page_parser
#        end_time = time.time ()
#        print "Time elapsed: %s" % (end_time - start_time)

        return youtube_video


parser_manager = ParserManager ()


