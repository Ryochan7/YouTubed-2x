import os
import subprocess

in_directory = os.path.abspath (os.path.dirname (__file__))
base_directory = os.path.dirname (in_directory)
po_directory = os.path.join (base_directory, "i18n")

def make ():
    for file in os.listdir (po_directory):
        if file.endswith (".po"):
            #print file
            file_location = os.path.join (po_directory, file)
            locale_string = file.rsplit (".po", 1)[0]
            locale_directory = os.path.join (po_directory, locale_string)
            messages_directory = os.path.join (locale_directory, "LC_MESSAGES")
            #print file_location
            #print locale_string
            #print locale_directory
            #print messages_directory

            output_location = os.path.join (messages_directory, "youtubed-2x.mo")
            if not os.path.exists (locale_directory):
                os.mkdir (locale_directory)

            if not os.path.exists (messages_directory):
                os.mkdir (messages_directory)

            comp_process = subprocess.Popen (["msgfmt", file_location, "-o", output_location])
            comp_process.wait ()


if __name__ == "__main__":
    make ()

