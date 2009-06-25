import re
from youtubed2x_lib.parsers import Parser_Helper, getPage


class RedTube_Parser (Parser_Helper):
    """Parser for RedTube pages. Updated 06/14/2009"""
    const_video_url_re = re.compile (r'^(?:http://)?(?:www\.)?redtube\.com/(\d+)$')
    domain_str = "http://www.redtube.com/"
    video_url_str = 'http://www.redtube.com/%s'
    video_url_real_str = 'http://dl.redtube.com/_videos_t4vn23s9jc5498tgj49icfj4678/%s/%s.flv'
    video_title_re = re.compile (r'<h1 class=\'videoTitle\'>([^<]*)</')
    # Mapped translation characters
    video_map_table = ['R', '1', '5', '3', '4', '2', 'O', '7', 'K', '9', 'H', 'B', 'C', 'D', 'X', 'F', 'G', 'A', 'I', 'J', '8', 'L', 'M', 'Z', '6', 'P', 'Q', '0', 'S', 'T', 'U', 'V', 'W', 'E', 'Y', 'N']
    parser_type = "RedTube"

    def __init__ (self, video_id):
        super (RedTube_Parser, self).__init__ (video_id)


    # TODO: Fix to use dynamic expires date
    def getVideoPage (self, account="", password=""):
        page, newurl = getPage (self.page_url, additional_headers={"Cookie": r'pp="1"; expires="Fri, 16-Dec-2011 02:15:58 PM"; path="/"; domain=.redtube.com; secure=""'}) # Should use a dynamic date
        return page, newurl


    def _parsePlayerCommands (self, page_dump):
        """Get the parent folder index number and file index number for the download url"""
        # Weird ass algorithm used to help figure out the path for the .flv file.
        # Python interpretation of algorithm used for RedTube Downloader

        video_id = int (self.video_id) # Typecast from string (ex. 752)
        parent_index = "%.7d" % (video_id/1000) # 7-digit num. with quotient (int division) padded with 0s (ex. '0000000')
        subindex = "%.7d" % video_id # 7-digit id padded with 0s (ex. '0000752')

        # Add all the results from multiplying integer components of each subindex by i+1
        # and place the string representation in helper. Result is '79' in example
        temp = 0
        for i in range (7):
            temp += int (subindex[i]) * (i+1)
        helper = str (temp)

        # Add integer components of helper. Result is 16 in example
        temp = 0
        for i in helper:
            temp += int (i)

        # 2-digit string that holds the 2nd and 7th characters characters for the file id
        helper = "%.2d" % temp # (ex. '16')
        # Translate the original video id number into the proper file id code
        # Result of example is the string 'J6IA0L1UM'
        file_id = ''
        file_id += self.video_map_table[ord(subindex[3]) - 48 + temp + 3] # table[48-48+16+3] = table[19] = 'J'
        file_id += helper[1] # '6'
        file_id += self.video_map_table[ord(subindex[0]) - 48 + temp + 2] # table[48-48+16+2] = table[18] = 'I'
        file_id += self.video_map_table[ord(subindex[2]) - 48 + temp + 1] # table[48-48+16+1] = table[17] = 'A'
        file_id += self.video_map_table[ord(subindex[5]) - 48 + temp + 6] # table[53-48+16+6] = table[27] = '0'
        file_id += self.video_map_table[ord(subindex[1]) - 48 + temp + 5] # table[48-48+16+5] = table[21] = 'L'
        file_id += helper[0] # '1'
        file_id += self.video_map_table[ord(subindex[4]) - 48 + temp + 7] # table[55-48+16+7] = table[30] = 'U'
        file_id += self.video_map_table[ord(subindex[6]) - 48 + temp + 4] # table[50-48+16+4] = table[22] = 'M'
        commands = (parent_index, file_id)
        return commands


    def _parseRealURL (self, commands):
        """Get the real url for the video"""
        real_url = self.video_url_real_str % commands
        return real_url


