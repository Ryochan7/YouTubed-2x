#!/usr/bin/env python
#
# YouTubed-2x version 2009.03.12
# Get videos from YouTube and transcode them to GP2X compatible video files.
# Also works with Veoh, Google Video, Metacafe, Dailymotion, MyVideo, 6.cn, MySpaceTV, Guba, PornoTube, RedTube, YouPorn, Pornhub, and Tube8.
# needs: python, wget, ffmpeg
# USAGE: youtubed-2x.py [options] URL(s)
# EXAMPLE: youtubed-2x.py http://www.youtube.com/watch?v=EjI4e3QEoPQ

# YouTubed-2x - Convert YouTube videos to GP2X-compatible videos
# Copyright (C) 2007-2009 Travis Nickles <ryoohki7@yahoo.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import subprocess
import time
from optparse import OptionParser
from youtubed2x_lib.videoitem import VideoItem
from youtubed2x_lib.parsermanager import ParserManager as parser_manager
from youtubed2x_lib.other import VERSION, PageNotFound, APP_NAME, WINDOWS
from youtubed2x_lib.download import FileDownloader

# Grab the user's home directory
path = os.path.expanduser ("~")

# Create the command line options parser and parse command line.
command_usage = 'youtubed-2x.py [options] URL(s)\nExample: youtubed-2x.py http://www.youtube.com/watch?v=EjI4e3QEoPQ'
command_version = VERSION
command_parser = OptionParser (usage=command_usage, version=command_version, conflict_handler='resolve')
command_parser.add_option ('-d', '--delete', action='store_true', dest='delete', default=False, help="Delete the downloaded .flv files")
command_parser.add_option ('-D', '--download', action='store_true', dest='download', default=False, help="Only download the .flv files. Don't convert file")
command_parser.add_option ('-o', '--overwrite', action='store_true', dest='overwrite', default=False, help="Overwrite previously converted output")
command_parser.add_option ('-s', '--simulate', action='store_true', dest='simulate', default=False, help="Don't download or transcode videos. Useful for debugging parsers")
command_parser.add_option ('-f', '--format', action='store', dest='format', default='mpeg4', help="Choose the output file format: avi, mpeg4, or mp3 (default: mpeg4)")
command_parser.add_option ('-r', action='store', type='int', dest='resolution', default=VideoItem.RES_320, help="Set output video resolution. Options: 0 (320x240)[default], 1 (640x480)")
command_parser.add_option ('-b', action='store', type='int', dest='vbitrate', default=384, help="Set the video bitrate for the output in kbps (default: 384 video)")
command_parser.add_option ('-a', action='store', type='int', dest='abitrate', default=128, help="Set the audio bitrate for the output in kbps (default: 128)")
command_parser.add_option ('-h', '--help', action='help', help="Display help text and exit")
command_parser.add_option ('-v', '--version', action='version', help="Print version number and exit")
command_parser.add_option ('--sitedirs', action='store_true', dest='sitefolders', default=False, help="Group videos by web site origin")
(command_opts, command_args) = command_parser.parse_args ()


# Check if arguments were passed
if len (command_args) == 0:
    print >> sys.stderr, "You did not pass any urls to the program.\n"
    print >> sys.stderr, "YouTubed-2x version %s" % VERSION
    print >> sys.stderr, "Usage: youtubed-2x.py [options] URL(s)"
    print >> sys.stderr, "Example: youtubed-2x.py http://www.youtube.com/watch?v=EjI4e3QEoPQ"
    sys.exit (42)

# Check for improper options
if command_opts.delete and command_opts.download:
    print >> sys.stderr, "Cannot use the delete and download options together. Exiting."
    sys.exit (42)
#### Should not be a destructive option. Change later. ####
if command_opts.download and command_opts.overwrite:
    print >> sys.stderr, "Cannot use the download and overwrite options together. Exiting."
    sys.exit (42)
if command_opts.format != 'avi' and command_opts.format != 'mp3' and command_opts.format != "mpeg4":
    print >> sys.stderr, "You chose an improper output format. Exiting."
    print command_opts.format
    sys.exit (42)
if (command_opts.format == 'avi' or command_opts.format == "mpeg4") and (command_opts.vbitrate > 2000 or command_opts.vbitrate < 128 or (command_opts.vbitrate % 8 != 0)):
    print >> sys.stderr, "Invalid video bitrate. The video bitrate must be set between 128 kbps and 2000 kbps and be divisible by 8. Exiting."
    sys.exit (42)
elif command_opts.format == 'mp3' and (command_opts.abitrate > 384 or command_opts.abitrate < 32 or (command_opts.abitrate % 4 != 0)):
    print >> sys.stderr, "Invalid audio bitrate. The audio bitrate must be set between 32 kbps and 384 kbps and be divisible by 4. Exiting."
    sys.exit (42)
elif (command_opts.format == "avi" or command_opts.format == "mpeg4") and command_opts.resolution != VideoItem.RES_320 and command_opts.resolution != VideoItem.RES_640:
    print >> sys.stderr, "Video resolution choice is invalid. Exiting."
    sys.exit (42)


# Create the default videos directory if one does not exist
if WINDOWS:
    videos_dir = os.path.join (path, "My Documents", "My Videos")
else:
    videos_dir = os.path.join (path, "Videos")

if not os.path.isdir (videos_dir):
    try:
        os.mkdir (videos_dir)
    except OSError:
        print >> sys.stderr, "Could not make videos directory. Exiting."
        sys.exit (42)


parser_manager.importParsers ()
#### Iterate through the list of URLs and download  ####
#### and transcode any specified videos             ####
for full_url in command_args:
    print
    youtube_video = parser_manager.validateURL (full_url)
    if not youtube_video:
        print >> sys.stderr, "An invalid url (%s) was passed. Exiting." % full_url
        sys.exit (42)

    try:
        youtube_video.getVideoInformation ()
    except (youtube_video.parser.UnknownTitle, youtube_video.parser.InvalidCommands,
            PageNotFound, youtube_video.parser.URLBuildFailed, youtube_video.parser.InvalidPortal) as e:
        print >> sys.stderr, "%s. Exiting." % e.message
        sys.exit (42)
    except Exception as e:
        print >> sys.stderr, "%s. Exiting." % e.message
        sys.exit (42)
        

    print "%s video" % youtube_video.parser.getType ()
    print "Title: %s" % youtube_video.title

    if command_opts.format == 'avi':
        youtube_video.setFileFormat (youtube_video.AVI_FILE)
        youtube_video.setOutputRes (command_opts.resolution)
    elif command_opts.format == "mpeg4":
        youtube_video.setFileFormat (youtube_video.MP4_AVI_FILE)
        youtube_video.setOutputRes (command_opts.resolution)
    else:
        youtube_video.setFileFormat (youtube_video.MP3_FILE)

    print "Download URL: %s" % youtube_video.real_url
    print
    if command_opts.simulate:
        continue

    #### Download and Transcode file #####
    if command_opts.sitefolders:
        if not os.path.isdir (os.path.join (videos_dir, youtube_video.parser.getType ())):
            try:
                os.mkdir (os.path.join (videos_dir, youtube_video.parser.getType ()))
            except OSError:
                print >> sys.stderr, "Directory for site %s could not be made. Exiting."
                sys.exit (3)

        youtube_video.setFilePaths (os.path.join (videos_dir, youtube_video.parser.getType ()))
    else:
        youtube_video.setFilePaths (videos_dir)

    output_filename = youtube_video.getOutputFileName ()

    wget_file = ffmpeg_file = ""
    if WINDOWS:
        wget_file = os.path.join ("bin", "wget.exe")
        ffmpeg_file = os.path.join ("bin", "ffmpeg.exe")
    else:
        wget_file = os.path.join (sys.prefix, "bin", "wget")
        ffmpeg_file = os.path.join (sys.prefix, "bin", "ffmpeg")

    if not os.path.exists (youtube_video.flv_file):
        print 'Downloading "%s"' % os.path.basename (youtube_video.flv_file)
        print
        n00b = FileDownloader (youtube_video.real_url, youtube_video.flv_file)
        n00b.open ()
        start_update = time.time ()
        speeda = 0
        last_message_length = 0
        data = n00b.readBlock ()

        while data != "":
            speeda = n00b.getBytesDownloaded () / float ((time.time () - start_update))
            speed = "%s/s" % n00b.humanizeSize (speeda)

            progress = n00b.downloadPercentage ()
            if progress >= 0:
                progress_message = "%3s%%" % progress
            else:
                progress_message = "???%%"

            file_size = n00b.getFileSize ()
            if file_size > 0:
                file_size_message = n00b.humanizeSize (file_size)
            else:
                file_size_message = "Unknown"

            message = "%s     %s     %s" % (progress_message, file_size_message, speed)
            message_length = len (message)
            if (last_message_length - message_length) > 0:
                # Previous message longer than new message or same length
                diff_length = last_message_length - message_length
                sys.stdout.write (message + (" " * diff_length)  + "\r")
            else:
                sys.stdout.write (message + "\r")
            sys.stdout.flush ()
            last_message_length = len (message)

            data = n00b.readBlock ()

        n00b.close ()
        print
        print
    else:
        print "Already Downloaded. Continuing with transcoding."

    youtube_video.__class__.setFFmpegLocation (ffmpeg_file)
    if not os.path.exists (youtube_video.avi_file) and not command_opts.download:
        status = youtube_video.transcodeVideo (command_opts.abitrate, command_opts.vbitrate)
        if not status:
            print >> sys.stderr, "Transcoding failed. Exiting."
            if os.path.exists (youtube_video.avi_file):
                os.remove (youtube_video.avi_file)
            sys.exit (42)
    elif not os.path.exists (youtube_video.avi_file) and command_opts.download:
        print "Skipping transcoding."
    elif os.path.exists (youtube_video.avi_file) and command_opts.overwrite:
        print "Deleteing old '%s' file." % output_filename
        try:
            os.remove (youtube_video.avi_file)
        except OSError:
            print >> sys.stderr, "Could not delete '%s' for some reason. Continuing exit." % output_filename
            sys.exit (42)

        status = youtube_video.transcodeVideo (command_opts.abitrate, command_opts.vbitrate)
        if not status:
            print >> sys.stderr, "Transcoding failed. Exiting."
            if os.path.exists (youtube_video.avi_file):
                os.remove (youtube_video.avi_file)
            sys.exit (42)
    else:
        print "File already exists. Skipping transcoding."

    if command_opts.delete and os.path.exists (youtube_video.flv_file):
        try:
            os.remove (youtube_video.flv_file)
        except OSError:
            print >> sys.stderr, "Could not delete '%s' for some reason. Continuing exit." % filename
            sys.exit (42)


#### For loop has finished. ####
print "Done."

