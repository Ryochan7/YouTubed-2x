import os
import sys
import re
import subprocess

class FfmpegController (object):
    command_dict = {'application': 'ffmpeg', 'vcodec': 'libxvid', 'vres': '320x240', 'bitrate': '%ik', 'acodec': 'copy', 'output_file': '%s', 'abitrate': '%ik'}
    resolution_re = re.compile (r"[ ]+Stream \#\d{1}\.\d{1}(?:\(und\))?: Video: \w+, \w+, (\d+)x(\d+).*")

    def __init__ (self, video_file):
        self.video_file = video_file


    def addPadding (self, temp_commands, length, width, output_length, output_width):
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
#           print new_length
#           print new_width


