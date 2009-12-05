import os, sys
import mimetypes

class MimeVault (mimetypes.MimeTypes):
    def __init__ (self):
        mimetypes.MimeTypes.__init__ (self)
#        self.types_map = ({}, {}) # dict for (non-strict, strict)
#        self.types_map_inv = ({}, {})
        self.add_type ("video/flv", ".flv")
        self.add_type ("video/x-flv", ".flv")
        self.add_type ("video/mp4", ".mp4")
        self.add_type ("audio/mpeg", ".mp3")
        self.add_type ("video/quicktime", ".mov")
        #self.add_type ("text/plain", ".flv")
        #self.types_map_inv[True].update ({"text/plain": ".flv"})
        #print "IM HERE %s" % self.guess_all_extensions ("text/plain")


    def add_type(self, type, ext, strict=True):
        self.types_map[strict][ext] = type
        self.types_map_inv[strict].update ({type: [ext]})


