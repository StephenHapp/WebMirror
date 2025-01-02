import time
import threading
from opt_enums import *
from scan import scan_media_links
from rules import link_is_wanted
from download import one_thread

# Downloads all media files linked within downloaded html documents
# as specified by pre-verified options
# Returns the map of files downloaded: { original_link : local_file_path }
def download_media(html_map, options):
    media_map = {}
    # a. Get user-supplied rules for which media types to download along with each
    #    page. User can specify different rules for different layers, in which case
    #    HTML pages are applied to the rule associated with the earliest layer they
    #    appeared
    rules = options.get('media_rules')


    # b. If media link is to be downloaded, check if it has already been downloaded
    #    first, If not downloaded yet, download and store key/value pair of
    #    download link with locally stored path
    #    of original link with location stored locally
    print("Scanning HTML for media...", end="\033[K\n")
    for layer_num, layer in html_map.items():
        layer_length = len(layer)
        num_scanned = 0 # Number of html pages scanned in this layer
        for html_link, path in layer.items():
            media_links = scan_media_links(html_link, path)

            for media_link in media_links:
                if media_link in media_map.keys(): continue
                # Ensure media link should be included
                if not link_is_wanted(media_link, layer_num, rules): continue
                media_map.update({media_link: None})
            # End for loop; all media links in html page saved
            num_scanned += 1
            print("Layer {}: Pages scanned: [{}/{}]"
                .format(layer_num, num_scanned, layer_length),
                end='\033[K\r')
        # End for loop; all html in this layer scanned
        print("Layer {}: Pages scanned: [{}/{}]"
            .format(layer_num, num_scanned, layer_length),
            end="\033[K\n")
    # End for loop; all html scanned

    # Download the media
    print("Downloading media...", end="\033[K\n")
    # Send a bunch of threads to do the downloading
    max_threads = options.get('max_threads')
    max_requests = options.get('max_requests')
    time_unit_start = time.time()
    requests_this_time_unit = 0
    copy_of_keys = set(media_map.keys())
    for media_link in copy_of_keys:
        # This while loop means 'stay here until we're allowed to send a new thread'
        while True:
            _ = set(media_map.values())
            _.discard(None) # Removes the value None from the set if it exists in there
            num_downloaded = len(_)
            print("Media downloaded: [{}/{}]. Threads: [{}/{}]"
                .format(num_downloaded, len(media_map),
                        threading.active_count() - 1, max_threads),
                end='\033[K\r')
        
            if (max_requests != MaxRequests.NOLIMIT):
                time.sleep(max_requests[1]/max_requests[0])
            
            # At this point, we know we haven't reached the limit or requests per second
            if threading.active_count() - 1 >= max_threads:
                time.sleep(0.1)
                continue
            # All checks passed, we can exit the while loop
            break
        # End while loop

        # All checks passed, start a new thread
        t = threading.Thread(target=one_thread, args=(media_link, media_map, options))
        t.start()
        requests_this_time_unit += 1 
    # End of for loop; all threads to download have been sent
    
    # Wait for all threads to finish
    while (threading.activeCount() > 1):
        _ = set(media_map.values())
        _.discard(None) # Removes the value None from the set if it exists in there
        num_downloaded = len(_)
        print("Media downloaded: [{}/{}]. Threads: [{}/{}]"
                .format(num_downloaded, len(media_map),
                        threading.active_count() - 1, max_threads),
                end='\033[K\r')
        time.sleep(0.1)
    _ = set(media_map.values())
    _.discard(None) # Removes the value None from the set if it exists in there
    num_downloaded = len(_)
    print("Media downloaded: [{}/{}]".format(num_downloaded, len(media_map)), end='\033[K\n')

    # c. Return the map of files downloaded: {original_link : local_file_path}
    return media_map