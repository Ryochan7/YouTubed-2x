import os
import sys
import glob
from distutils.core import setup
from youtubed2x_lib.other import VERSION, WINDOWS
from utils import compile_po_messages


stuff = {
    "name": "YouTubed-2x",
    "version": VERSION,
    "description": "Download and transcode flash video to GP2X video files",
    "author": "Travis Nickles",
    "url": "http://www.ryochan7.com/",
    "scripts": ["youtubed-2x", "youtubed-2x_gui"],
    "packages": ["youtubed2x_lib", "youtubed2x_lib.parsers", "youtubed2x_lib.ui", "youtubed2x_lib.ui.controllers", "youtubed2x_lib.ui.exceptions", "youtubed2x_lib.ui.models", "youtubed2x_lib.ui.views"],

    "data_files": [(os.path.join ("share", "youtubed-2x"), [os.path.join ("data", "youtubed-2x.glade")]),
                (os.path.join ("share", "applications"), [os.path.join ("data", "youtubed2x.desktop")])],

    "license": "GPL3",
}

#if not WINDOWS:
#    compile_po_messages.make ()

trans_files = []
for mofile in glob.glob (os.path.join ("i18n", "*", "LC_MESSAGES", "youtubed-2x.mo")):
    locale_dir = os.path.basename (os.path.dirname (os.path.dirname (mofile)))
    trans_files.append ((os.path.join ("share", "locale", locale_dir, "LC_MESSAGES"), [mofile]))

if len (trans_files) > 0:
    stuff["data_files"].extend (trans_files)


if WINDOWS:
    import py2exe
    import youtubed2x_lib.parsers

    includes_list = ["atk", "cairo", "pango", "pangocairo"]
    # Used when freezing applications with Py2exe.
    # Parsers must be specified in includes otherwise Py2exe
    # will not bundle them
    if len (sys.argv) >= 2 and sys.argv[1] == "py2exe":
        file_list = os.listdir (os.path.join (os.path.dirname (__file__), "youtubed2x_lib", "parsers"))
        if "__init__.pyc" in file_list:
            file_list.remove ("__init__.pyc")
        if "__init__.py" in file_list:
            file_list.remove ("__init__.py")

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

            if site_parser and issubclass (site_parser, youtubed2x_lib.parsers.Parser_Helper):
                includes_list.append ("youtubed2x_lib.parsers.%s" % possible_module)


    opts = {
        "py2exe": {
        "includes": ",".join (includes_list),
        "optimize": 2,
        "dist_dir": "dist",
        }
    }
    stuff["data_files"].append (("bin", [os.path.join ("bin", "ffmpeg.exe")]))
    stuff["data_files"].append ((os.path.join ("etc", "gtk-2.0"), [os.path.join ("gtk-win", "etc", "gtk-2.0", file) for file in os.listdir (os.path.join ("gtk-win", "etc", "gtk-2.0")) if not file.startswith ('.')]))
    stuff["data_files"].append ((os.path.join ("etc", "pango"), [os.path.join ("gtk-win", "etc", "pango", file) for file in os.listdir (os.path.join ("gtk-win", "etc", "pango")) if not file.startswith ('.')]))
    stuff["data_files"].append ((os.path.join ("lib", "gtk-2.0", "2.10.0", "engines"), [os.path.join ("gtk-win", "lib", "gtk-2.0", "2.10.0", "engines", file) for file in os.listdir (os.path.join ("gtk-win", "lib", "gtk-2.0", "2.10.0", "engines")) if not file.startswith ('.')]))
    stuff["data_files"].append ((os.path.join ("lib", "gtk-2.0", "2.10.0", "loaders"), [os.path.join ("gtk-win", "lib", "gtk-2.0", "2.10.0", "loaders", file) for file in os.listdir (os.path.join ("gtk-win", "lib", "gtk-2.0", "2.10.0", "loaders")) if not file.startswith ('.')]))
    stuff["data_files"].append ((os.path.join ("lib", "pango", "1.6.0", "modules"), [os.path.join ("gtk-win", "lib", "pango", "1.6.0", "modules", file) for file in os.listdir (os.path.join ("gtk-win", "lib", "pango", "1.6.0", "modules")) if not file.startswith ('.')]))
    stuff["data_files"].append ((os.path.join ("share", "themes", "Default", "gtk-2.0-key"), [os.path.join ("gtk-win", "share", "themes", "Default", "gtk-2.0-key", file) for file in os.listdir (os.path.join ("gtk-win", "share", "themes", "Default", "gtk-2.0-key")) if not file.startswith ('.')]))
    stuff["data_files"].append ((os.path.join ("share", "themes", "MS-Windows", "gtk-2.0"), [os.path.join ("gtk-win", "share", "themes", "MS-Windows", "gtk-2.0", file) for file in os.listdir (os.path.join ("gtk-win", "share", "themes", "MS-Windows", "gtk-2.0")) if not file.startswith ('.')]))
    #print stuff["data_files"]
    setup (options=opts, console=["youtubed-2x"], windows=["youtubed-2x_gui"], **stuff)
else:
    setup (**stuff)

