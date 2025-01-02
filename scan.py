import os
from bs4 import BeautifulSoup
from urllib import parse
from requests import head

# Returns a set of all href links found in <a> tags from passed in html file
def scan_links(original_link, path):
    file = open(path, 'rb')
    content = BeautifulSoup(file, 'html.parser')
    file.close()
    link_tags = content.find_all('a', recursive=True)
    links = set()
    for tag in link_tags:
        link = tag.get('href')
        if link != None:
            links.add(str(link))

    # Still need to modify links to their full path (without http/https)
    result = set()
    for link in links:
        if len(link) < 1:
            continue
        if link[0] == '#': # These are links to other areas of the same page, don't need to track these
            continue
        
        link = parse.unquote(link, encoding="utf-8", errors="ignore")
        converted_link = convert_to_url(original_link, link)
        if converted_link == None: continue
        else: result.add(converted_link)

    return result

# Returns a set of all media links found in passed in html file
# This means all links in <link> href attributes and all links in src attributes
def scan_media_links(original_link, path):
    file = open(path, 'rb')
    content = BeautifulSoup(file, 'html.parser')
    file.close()

    links = set()

    link_tags = content.find_all(name='link', recursive=True)
    for tag in link_tags:
        link = tag.get('href')
        if (link != None):
            links.add(link)

    all_tags = content.find_all()
    for tag in all_tags:
        link = tag.get('src')
        if link != None:
            links.add(link)
    
    # Still need to modify links to their full path (without http/https)
    result = set()
    for link in links:
        if len(link) < 1:
            continue
        if link[0] == '#': # These are links to other areas of the same page, don't need to track these
            continue
        
        link = parse.unquote(link, encoding="utf-8", errors="ignore")
        converted_link = convert_to_url(original_link, link)
        if converted_link == None: continue
        else: result.add(converted_link)

    return result

# Takes in a potentially local path from a source link and combines them into
# a global URL
def convert_to_url(source, path):
    source = source.removeprefix('http://')
    source = source.removeprefix('https://')
    source = source.removesuffix('/')

    if '/' in source:
        domain = source.split('/', 1)[0]
    else:
        domain = source
    
    path = path.removeprefix('http://')
    path = path.removeprefix('https://')

    if path.startswith('//'): # These are global links
        return path.removeprefix('//')
    elif path.startswith('/'): # These need to be modified to include their full path from domain
        return domain + path
    elif path.startswith('./'): # These need to be modified to include their full path
        path = path[1:]
        return source + path
    elif path.startswith('../'):
        while path.startswith('../'):
            # If we cannot go up source anymore,
            # that's the web dev's fault,
            # so continue to next link
            if '/' not in source: break
            source = source.rsplit('/', 1)[0]
            path = path.removeprefix('../')
        if path.startswith('../'): return None
        else: return source + '/' + path
    elif '.' not in path: # Means it's local for certain
        return source + '/' + path
    else:
        # It's still possible that the link is relative to the page
        # rather than global to the web, but it's trickier to know which
        # I might implement more intelligent checking later, but for now,
        # Silently assume global link
        return path


# Might use this at some point, but for now it's a small edge case that takes
# too long to check for
def test_locality():
    # Test to see if a local page is available
        local_link = domain + '/' + link
        response = None
        try:
            response = head('https://' + local_link, headers={
                'User-Agent': 'Python 3 script, using requests package'
            })
        except:
            response = None

        if not response.ok:
            # Might need to try encoding the URL
            encoded_link = parse.quote(local_link)
            try:
                response = head('https://' + encoded_link, headers={
                    'User-Agent': 'Python 3 script, using requests package'
                })
            except:
                response = None
        
        if response.ok:
            # Local link worked, that's probably the intended route
            result.add(domain + '/' + link)
            print('Warning: assuming ' + link + ' is local link:' + (domain + '/' + link), end="\033[K\n")
        else:
            # Local link didn't work, so it's probably a global link
            result.add(link)
            print('Warning: assuming ' + link + ' is global and not this local link:' + (domain + '/' + link), end="\033[K\n")