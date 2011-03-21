#!/usr/bin/env python

import os
import sys
import pygtk
if not sys.platform == "win32":
    pygtk.require ("2.0")
import gtk
import gtk.glade
import logging
from youtubed2x_lib.other import WINDOWS

# Translation stuff
import gettext
import locale

lc, enc = locale.getdefaultlocale ()

if os.path.exists (os.path.join (os.path.dirname (sys.argv[0]), "i18n")):
    # Running locally
    #print "Running local"
    gettext.bindtextdomain ("youtubed-2x", "i18n")
    lc, enc = locale.getdefaultlocale ()
    lang = gettext.translation ("youtubed-2x", "i18n", languages=[lc], fallback=True)
    #print lang
    lang.install ()
    #gettext.install ("youtubed-2x", "i18n")
    gtk.glade.bindtextdomain ("youtubed-2x", "i18n")
elif gettext.find ("youtubed-2x"):
    # Installed. .mo file is in default locale location
    #print "Found default locale"
    gettext.install ("youtubed-2x")
    gtk.glade.bindtextdomain ("youtubed-2x")
elif WINDOWS and os.path.exists (os.path.join (sys.prefix, "share", "locale")):
    # Windows when using build made with Py2exe
    #print "Py2exe build"
    locale_dir = os.path.join (sys.prefix, "share", "locale")
    gettext.bindtextdomain ("youtubed-2x", locale_dir)
    lang = gettext.translation("youtubed-2x", locale_dir, languages=[lc], fallback=True)
    #print lang
    lang.install ()
    #gettext.install ("youtubed-2x", "i18n")
    gtk.glade.bindtextdomain ("youtubed-2x", locale_dir)
else:
    # Installed. Try to discover locale location
    #print "Installed"
    locale_dir = None
    if "XDG_DATA_DIRS" in os.environ:
        data_dirs = os.environ["XDG_DATA_DIRS"].split (":")
        for data_dir in data_dirs:
            mofile = gettext.find ("youtubed-2x",
                os.path.join (data_dir, "locale"))
#            #print mofile
            if mofile:
                locale_dir = os.path.join (data_dir, "locale")
                break

    #print locale_dir
    if locale_dir:
        gettext.install ("youtubed-2x", locale_dir)
        gtk.glade.bindtextdomain ("youtubed-2x", locale_dir)
    else:
        # If .mo file could not be found, ignore the issue.
        # Non-translated strings will be used. Install _()
        # to global namespace
        gettext.install ("youtubed-2x")
        gtk.glade.bindtextdomain ("youtubed-2x")

#gettext.install ("youtubed-2x")
gtk.glade.textdomain ("youtubed-2x")
#print _

from youtubed2x_lib.videoitem import VideoItem
from youtubed2x_lib import settings
from youtubed2x_lib.parsermanager import ParserManager as parser_manager
from youtubed2x_lib.ui.propertieswindow import PropertiesWindow
from youtubed2x_lib.ui.models.videothreadmanager import VideoThreadManager
from youtubed2x_lib.ui.mainwindow import YouTubeDownloader

if __name__ == '__main__':
    # If running on Windows, write output and error messages to text files.
    # Needed due to Py2exe
    if WINDOWS:
        sys.stdout = open ("log.txt", "w")
        sys.stderr = open ("errors.log", "w")

    logging.basicConfig (level=logging.NOTSET)
    log = logging.getLogger ()
    log.debug ("This is a test")

    media_paths = [
        # Can't use __file__ here. Py2exe does not like it
        os.path.join (os.path.dirname (sys.argv[0]), "data"), # Running locally
    ]
    # Check for system data directories. Append any found
    # directories to media_paths
    if "XDG_DATA_DIRS" in os.environ:
        data_dirs = os.environ["XDG_DATA_DIRS"].split (":")
        for data_dir in data_dirs:
            media_paths.append (os.path.join (data_dir, "youtubed-2x"))
    elif WINDOWS:
        media_paths.append (os.path.join (sys.prefix, "share", "youtubed-2x"))

    app_settings = settings.Settings ()
    try:
        app_settings.readConfigFile ()
    except app_settings.InvalidConfig as exception:
        logging.exception("Invalid configuration file")
        logging.info ("Reverting to default settings")
        app_settings.setDefaults ()

    parser_manager.importParsers ()

    gladefile = None
    filename = "youtubed-2x.glade"
    for path in media_paths:
        glade_file = os.path.join (path, filename)
        if os.path.exists (glade_file):
            gladefile = glade_file
            break

    if not gladefile:
        logging.critical ("Glade file \"%s\" could not be found. Exiting.", filename)
        sys.exit (1)

    thread_manager = VideoThreadManager (app_settings)
    prop_win = PropertiesWindow (gladefile, app_settings, thread_manager)
    main_ui = YouTubeDownloader (gladefile, app_settings, thread_manager,
        parser_manager, prop_win)
    VideoItem.setFFmpegLocation (app_settings.ffmpeg_location)

    thread_manager.restore_session ()
    gtk.gdk.threads_init ()
    gtk.gdk.threads_enter ()
    gtk.main ()
    gtk.gdk.threads_leave ()
    app_settings.writeConfigFile ()
    thread_manager.save_session ()
