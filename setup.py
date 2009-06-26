import os
from distutils.core import setup
from youtubed2x_lib.other import VERSION, WINDOWS


stuff = {
    "name": "YouTubed-2x",
    "version": VERSION,
    "description": "Download and transcode flash video to GP2X video files",
    "author": "Travis Nickles",
    "url": "http://ryochan7.webfactional.com/",
    "scripts": ["youtubed-2x", "youtubed-2x_gui"],
    "packages": ["youtubed2x_lib", "youtubed2x_lib.parsers"],

    "data_files": [(os.path.join ("share", "youtubed-2x"), [os.path.join ("data", "youtubed-2x.glade")]),
                (os.path.join ("share", "applications"), [os.path.join ("data", "youtubed2x.desktop")]),

    "license": "GPL3",
}


if WINDOWS:
    import py2exe
    opts = {
        "py2exe": {
        #"includes": "atk,cairo,gobject,pango,pangocairo",
        "includes": "atk,cairo,pango,pangocairo",
        "optimize": 2,
        "dist_dir": "dist",
        }
    }
    stuff["data_files"].append (("bin", [os.path.join ("bin", "ffmpeg.exe")]))
    stuff["data_files"].append ((os.path.join ("etc", "gtk-2.0"), [os.path.join ("gtk-win", "etc", "gtk-2.0", file) for file in os.listdir (os.path.join ("gtk-win", "etc", "gtk-2.0"))]))
    stuff["data_files"].append ((os.path.join ("etc", "pango"), [os.path.join ("gtk-win", "etc", "pango", file) for file in os.listdir (os.path.join ("gtk-win", "etc", "pango"))]))
    stuff["data_files"].append ((os.path.join ("lib", "gtk-2.0", "2.10.0", "engines"), [os.path.join ("gtk-win", "lib", "gtk-2.0", "2.10.0", "engines", file) for file in os.listdir (os.path.join ("gtk-win", "lib", "gtk-2.0", "2.10.0", "engines"))]))
    stuff["data_files"].append ((os.path.join ("lib", "gtk-2.0", "2.10.0", "loaders"), [os.path.join ("gtk-win", "lib", "gtk-2.0", "2.10.0", "loaders", file) for file in os.listdir (os.path.join ("gtk-win", "lib", "gtk-2.0", "2.10.0", "loaders"))]))
    stuff["data_files"].append ((os.path.join ("lib", "pango", "1.6.0", "modules"), [os.path.join ("gtk-win", "lib", "pango", "1.6.0", "modules", file) for file in os.listdir (os.path.join ("gtk-win", "lib", "pango", "1.6.0", "modules"))]))
    stuff["data_files"].append ((os.path.join ("share", "themes", "Default", "gtk-2.0-key"), [os.path.join ("gtk-win", "share", "themes", "Default", "gtk-2.0-key", file) for file in os.listdir (os.path.join ("gtk-win", "share", "themes", "Default", "gtk-2.0-key"))]))
    stuff["data_files"].append ((os.path.join ("share", "themes", "MS-Windows", "gtk-2.0"), [os.path.join ("gtk-win", "share", "themes", "MS-Windows", "gtk-2.0", file) for file in os.listdir (os.path.join ("gtk-win", "share", "themes", "MS-Windows", "gtk-2.0"))]))
    #print stuff["data_files"]
    setup (options=opts, console=["youtubed-2x"], windows=["youtubed-2x_gui"], **stuff)
else:
    setup (**stuff)

