from urllib2 import urlparse
import datetime
import parsers
from other import WINDOWS
from videoitem import VideoItem


class AlreadyRegistered (Exception):
    pass

class InvalidParser (Exception):
    pass


class ParserManager (object):
    def __init__ (self):
        self.parsers = {}
        self._app_parsers_list = []
        self._user_parsers_list = []
        self._register_app_parsers ()
        self._register_user_parsers ()
#        print self.parsers


    def register (self, parser):
        if not issubclass (parser, parsers.Parser_Helper):
            raise TypeError ("A subclass of Parser_Helper was not passed")

        host_str = getattr (parser, "host_str", "")
        version = getattr (parser, "version", "")
        if host_str and isinstance (host_str, str) and isinstance (version, datetime.date):
            identifier = host_str
            if identifier in self.parsers and self.parsers[identifier].version >= parser.version:
                # Override parser with newer version
                self.parsers.update ({identifier: parser})
            elif identifier not in self.parsers:
                # New parser being added
                self.parsers.update ({identifier: parser})
            else:
                # A newer parser is already registered
                raise AlreadyRegistered ()
        else:
            raise InvalidParser ()


    def _register_app_parsers (self):
        import os, sys

        # Importing modules from library.zip made with Py2exe
        if hasattr (parsers, "__loader__"):
            zipfiles = parsers.__loader__._files
            file_list = [zipfiles[file][0] for file in zipfiles.keys () if "youtubed2x_lib\\parsers\\" in file]
            file_list = [name.split ("\\")[-1] for name in file_list]
            if "__init__.pyo" in file_list:
                file_list.remove ("__init__.pyo")
            module_list = map (lambda file_list: file_list[:-4], file_list)
        else:
            file_list = os.listdir (os.path.join (os.path.dirname (__file__), "parsers"))
            module_list = filter (lambda file_list: file_list.endswith (".py"), file_list)
            module_list = map (lambda module_list: module_list[:-3], module_list)

        for possible_module in module_list:
            try:
               parser_module =  __import__ ("youtubed2x_lib.parsers.%s" % possible_module, {}, {}, ["parsers"])
            except ImportError as exception:
                print >> sys.stderr, "File \"%s\" could not be imported" % possible_module
                continue
            except Exception as exception:
                print >> sys.stderr, "%s" % exception
                continue

            module_contents = dir (parser_module)
            site_parser = None
            for item in module_contents:
                if item.endswith ("_Parser") and item.lower () == "%s_parser" % possible_module:
                    site_parser = getattr (parser_module, item)

            if site_parser and issubclass (site_parser, parsers.Parser_Helper):
                try:
                    self.register (site_parser)
                except AlreadyRegistered as exception:
                    print "A newer version of parser %s has already been registered" % possible_module
                except InvalidParser as exception:
                    print >> sys.stderr, "Parser %s is invalid." % possible_module
                else:
                    self._app_parsers_list.append (site_parser)
#                print site_parser


    def _register_user_parsers (self):
        import os, sys
        home_dir = os.path.expanduser ("~")
        if WINDOWS:
            # Useful for Windows Vista and Windows 7
            if "LOCALAPPDATA" in os.environ:
                config_dir = os.path.join (os.environ["LOCALAPPDATA"], "youtubed-2x")
            # Useful for Windows XP and below
            elif "APPDATA" in os.environ:
                config_dir = os.path.join (os.environ["APPDATA"], "youtubed-2x")
            else:
                raise Exception ("LOCALAPPDATA nor APPDATA specified. Should not be here")
        else:
            config_dir = os.path.join (home_dir, ".youtubed-2x")

        user_parser_dir = os.path.join (config_dir, "parsers")

        if not os.path.exists (config_dir):
            try:
                os.mkdir (config_dir)
            except OSError:
                print >> sys.stderr, "Could not create config directory \"%s\"" % config_dir

        if not os.path.exists (user_parser_dir):
            try:
                os.mkdir (user_parser_dir)
            except OSError:
                print >> sys.stderr, "Could not create unofficial parser directory \"%s\"." % user_parser_dir

        if not os.path.exists (user_parser_dir):
            print "User parser directory \"%s\" does not exist." % user_parser_dir
            return

        file_list = os.listdir (user_parser_dir)
        if "__init__.py" in file_list:
            file_list.remove ("__init__.py")

        # Add user directory to sys.path so
        # modules can be imported
        sys.path.insert (1, user_parser_dir)

        for file in file_list:
            if file.endswith (".py"):
                possible_module = file.rstrip (".py")
            else:
                possible_module = None

            if not possible_module:
                continue

            try:
                parser_module =  __import__ ("%s" % possible_module)
            except ImportError as exception:
                print >> sys.stderr, "File \"%s\" could not be imported" % possible_module
                continue
            except Exception as exception:
                print >> sys.stderr, "%s" % exception
                continue

            module_contents = dir (parser_module)
            site_parser = None
            for item in module_contents:
                if item.endswith ("_Parser") and item.lower () == "%s_parser" % possible_module:
                    site_parser = getattr (parser_module, item)

            if site_parser and issubclass (site_parser, parsers.Parser_Helper):
                try:
                    self.register (site_parser)
                except AlreadyRegistered as exception:
                    print "A newer version of parser %s has already been registered" % possible_module
                except InvalidParser as exception:
                    print >> sys.stderr, "Parser %s is invalid." % possible_module
                else:
                    self._user_parsers_list.append (site_parser)
#                print site_parser

        # Custom parsers loaded. Remove user_parser_dir
        # directory from sys.path
        del sys.path[1]

    
    def validateURL (self, full_url, video_item=True):
        """Make sure the url passed is in a valid form and return a video parser object"""
        if not isinstance (full_url, str):
            raise TypeError ("Argument must be a string")

        spliturl = urlparse.urlsplit (full_url)
        hostname = spliturl.hostname
#        print len (self.parsers.keys ())

        if not hostname:
            return None
        elif hostname.startswith ("www."):
            hostname = hostname.lstrip ("www.")

        if hostname not in self.parsers:
            return None

        page_parser = self.parsers[hostname].checkURL (full_url)
        if page_parser and video_item:
            youtube_video = VideoItem (page_parser)
        elif page_parser:
            youtube_video = page_parser
        else:
            youtube_video = None

        return youtube_video


    def get_official_parsers (self):
        parser_list = list (self._app_parsers_list)
        return parser_list


parser_manager = ParserManager ()


