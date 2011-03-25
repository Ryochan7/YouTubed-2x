#!/usr/bin/env python

import os
import sys
import pygtk
if not sys.platform == "win32":
    pygtk.require ("2.0")
import gtk
import gtk.glade
import logging
import gettext
import locale

def add_translation ():
    lc, enc = locale.getdefaultlocale ()

    if os.path.exists (os.path.join (os.path.dirname (sys.argv[0]), "i18n")):
        # Running locally
        logging.debug ("Running local")
        gettext.bindtextdomain ("youtubed-2x", "i18n")
        lc, enc = locale.getdefaultlocale ()
        lang = gettext.translation ("youtubed-2x", "i18n", languages=[lc], fallback=True)
        logging.debug (lang)

        lang.install ()
        #gettext.install ("youtubed-2x", "i18n")
        gtk.glade.bindtextdomain ("youtubed-2x", "i18n")
    elif gettext.find ("youtubed-2x"):
        # Installed. .mo file is in default locale location
        logging.debug ("Found default locale")
        gettext.install ("youtubed-2x")
        gtk.glade.bindtextdomain ("youtubed-2x")
    elif WINDOWS and os.path.exists (os.path.join (sys.prefix, "share", "locale")):
        # Windows when using build made with Py2exe
        logging.debug ("Py2exe build")
        locale_dir = os.path.join (sys.prefix, "share", "locale")
        gettext.bindtextdomain ("youtubed-2x", locale_dir)
        lang = gettext.translation("youtubed-2x", locale_dir, languages=[lc], fallback=True)
        logging.debug (lang)
        lang.install ()
        #gettext.install ("youtubed-2x", "i18n")
        gtk.glade.bindtextdomain ("youtubed-2x", locale_dir)
    else:
        # Installed. Try to discover locale location
        logging.debug ("Installed")
        locale_dir = None
        if "XDG_DATA_DIRS" in os.environ:
            data_dirs = os.environ["XDG_DATA_DIRS"].split (":")
            for data_dir in data_dirs:
                mofile = gettext.find ("youtubed-2x",
                    os.path.join (data_dir, "locale"))

                logging.debug (mofile)
                if mofile:
                    locale_dir = os.path.join (data_dir, "locale")
                    break

        logging.debug (locale_dir)
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
    logging.debug (_)

if __name__ == '__main__':
    from youtubed2x_lib.other import WINDOWS
    # Set up logging
    logging_level = logging.NOTSET
    if WINDOWS:
        logging.basicConfig (filename="log.txt", level=logging_level)
    else:
        logging.basicConfig (level=logging_level)

    log = logging.getLogger ()
    log.debug ("This is a test")

    # Must call add_translation before imports that use _
    add_translation ()
    from youtubed2x_lib.videoitem import VideoItem
    from youtubed2x_lib import settings
    from youtubed2x_lib.parsermanager import ParserManager as parser_manager
    from youtubed2x_lib.ui.propertieswindow import PropertiesWindow
    from youtubed2x_lib.ui.models.videothreadmanager import VideoThreadManager
    from youtubed2x_lib.ui.mainwindow import YouTubeDownloader

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
        logging.critical ("Glade file \"%s\" could not be found. Exiting.",
            filename)
        sys.exit (1)

    thread_manager = VideoThreadManager (app_settings)
    prop_win = PropertiesWindow (gladefile, app_settings)
    prop_win.connect ("settings_updated", thread_manager.alter_sem)
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
