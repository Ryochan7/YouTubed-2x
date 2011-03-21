import os
import subprocess

in_directory = os.path.abspath (os.path.dirname (__file__))
base_directory = os.path.dirname (in_directory)
os.chdir (base_directory)

def extract_glade_strings (file_location):
    current_process = subprocess.Popen (["intltool-extract", "--type=gettext/glade", file_location])
    current_process.wait ()
    output_file_location = "%s.h" % file_location
    return output_file_location


potincludes = os.path.join (base_directory, "i18n", "POTFILES.inc")
print potincludes
file = open (potincludes)

files = []
#print file.readline ()
for line in file.readlines ():
    line = line.strip ()
    if line:
        print line
        file_location = line
        if file_location.endswith (".glade"):
            print "Extracting glade strings"
            file_location = extract_glade_strings (file_location)

        if os.path.exists (file_location):
            files.append (file_location)

file.close ()

print files

command_list = ["xgettext", "--language=Python", "--keyword=_", "--keyword=N_", "--output=messages.pot"]
command_list.extend (files)

print command_list

#current_process = subprocess.Popen (["pygettext", files_string])
current_process = subprocess.Popen (command_list)
current_process.wait ()

