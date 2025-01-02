#   View overview of system in plan.txt
import sys
from parse_options import parse_options
from download_html import download_html
from download_media import download_media
from stitch import stitch_site
from opt_enums import *
from make_index import make_index

# 0. User provides desired options for mirror download:
options = parse_options(sys.argv)

# 1. Download all HTML files (do not modify them at this step)
html_map = download_html(options)

# 2. Scan all HTML and download media links according to user-defined rules
media_map = download_media(html_map, options)

# 3. Use map(s) pairing original links to local paths to modify all links in
#    all downloaded HTML files.
stitch_site(html_map, media_map, options)

# And make the index.html file
make_index(html_map.get(0), options.get('dest_path'))