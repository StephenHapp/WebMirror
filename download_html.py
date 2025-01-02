import sys
import threading
import time
from opt_enums import *
from download import one_thread
from scan import scan_links
from rules import link_is_wanted
from urllib import parse

# Downloads html files specified by pre-verified options
# Returns the map of links downloaded: { layer_number : { original_link : local_file_path } }
def download_html(options):
    max_depth = options.get('max_depth')
    # Initialize map to store downloaded links
    linkmap = dict()
    i = 0
    while i <= max_depth:
        linkmap.update({i: {}})
        i += 1
    linkrules = options.get('link_rules')

    # a. Get list of 'layer-0' sites from user-supplied text file
    layer0_links_file = open(options.get('layer0_path'), 'r')
    layer0_links = linkmap.get(0)
    for line in layer0_links_file.readlines():
        line = line.strip()
        if line.startswith('http://'): line = line.split('http://', 1)[1]
        elif line.startswith('https://'): line = line.split('https://', 1)[1]
        layer0_links.update({line: None})
    
    layer0_links_file.close()
    if '' in layer0_links:
        layer0_links.pop('')
    # layer-0 site links stored in keys of linkmap.get(0)

    # b. Get user-specified desired options, including rules for which links to include

    # c. Repeat until all desired links are stored: (might be 0, in this case skip loop)
    print("Downloading HTML...", end="\033[K\n")
    for layer_num in range(len(linkmap) - 1):
        layer = linkmap.get(layer_num)
        # c.i. Download all pages on current layer
        download_layer(layer, layer_num, options)

        # c.ii. Scan each downloaded page on layer for links that match user-supplied rules
        # c.iii. Only store links to pages not yet downloaded (in any layer)
        # c.iv. Links stored in this iteration make up next layer
        next_layer = linkmap.get(layer_num + 1)
        layer_size = len(layer.items())
        current_item = 0
        for link, path in layer.items(): # for each page on this layer...
            current_item += 1
            page_links = scan_links(link, path) # Gets all <a> tag href links on page
            print("Scanning layer {}: [{}/{}]".format(layer_num, current_item, layer_size), end="\033[K\r")
            for href in page_links: # for each relevant link on this page...
                if link_in_map(href, linkmap): continue
                # Ensure link is desired by user
                if link_is_wanted(href, layer_num + 1, linkrules):
                    next_layer.update({href: None})
            # End for loop of page_links
        # End for loop of pages on this layer

        # All links on this layer added to next layer
    # End of for loop through linkmap

    # All <a> tag href links stored!

    # d. Download all HTML on final layer (all other layers downloaded by step 1c)
    layer_num = len(linkmap) - 1
    layer = linkmap.get(layer_num)
    download_layer(layer, layer_num, options)

    # e. Have the generated structure store the highest layer each link was found,
    #    along with the local path to where file was downloaded

    # g. Return the map of links downloaded: { layer_number : { original_link : local_file_path } }
    return linkmap

def link_in_map(link, map):
    for layer in map.values():
        if link in layer.keys(): return True
    return False

def download_layer(layer_map, layer_num, options):
    layer = layer_map
    # c.i. Download all pages on current layer

    # Send a bunch of threads to do the downloading
    max_threads = options.get('max_threads')
    max_requests = options.get('max_requests')
    requests_this_time_unit = 0
    copy_of_keys = set(layer.keys())
    for link in copy_of_keys:
        # This while loop means 'stay here until we're allowed to send a new thread'
        while True:
            _ = set(layer.values())
            _.discard(None) # Removes the value None from the set if it exists in there
            num_downloaded = len(_)
            print("Layer {}: [{}/{}]. Threads: [{}/{}]"
                .format(layer_num, num_downloaded, len(layer),
                        threading.active_count() - 1, max_threads),
                end='\033[K\r')
        
            if (max_requests != MaxRequests.NOLIMIT):
                time.sleep((max_requests[1])/(max_requests[0]))
            
            # At this point, we know we haven't reached the limit or requests per second
            if threading.active_count() - 1 >= max_threads:
                time.sleep(0.1)
                continue
            # All checks passed, we can exit the while loop
            break
        # End while loop

        # All checks passed, start a new thread
        t = threading.Thread(target=one_thread, args=(link, layer, options))
        t.start()
        requests_this_time_unit += 1 
    # End of for loop; all threads to download have been sent

    # Wait for all threads to finish
    while (threading.activeCount() > 1):
        _ = set(layer.values())
        _.discard(None) # Removes the value None from the set if it exists in there
        num_downloaded = len(_)
        print("Layer {}: [{}/{}]. Threads: [{}/{}]"
              .format(layer_num, num_downloaded, len(layer),
                      threading.active_count() - 1, max_threads),
              end='\033[K\r')
        time.sleep(0.1)
    _ = set(layer.values())
    _.discard(None) # Removes the value None from the set if it exists in there
    num_downloaded = len(_)
    print("Layer {}: [{}/{}]".format(layer_num, num_downloaded, len(layer)), end='\033[K\n')

