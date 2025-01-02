import os
from bs4 import BeautifulSoup
from scan import convert_to_url
from urllib import parse

def stitch_site(html_map, media_map, options):
    # a. For links that were downloaded, replace link in HTML with relative path
    #    to downloaded file.
    # b. If 'external.html' option was enabled, replace links to files not downloaded
    #    with the relative path to external.html?link=<original link>.
    # c. If 'external.html' option wasn't enabled, do not modify links to files
    #    not downloaded.
    make_external_page = options.get('make_external_page')
    root = options.get('dest_path')

    print("Linking pages...", end="\033[K\n")

    if make_external_page:
        file = open('./default/external.html', 'r')
        contents = file.read()
        file.close()

        file = open(os.path.join(root, 'external.html'), 'w')
        file.write(contents)
        file.close()

    # Make an unlayered dict of html_map
    unlayered_html_map = dict()
    for layer in html_map.values():
        unlayered_html_map.update(layer)
    
    length = len(unlayered_html_map)
    i = 0
    for original_link, path in unlayered_html_map.items():
        # Fix this html document
        file = open(path, 'rb')
        soup = BeautifulSoup(file, 'html.parser')
        file.close()

        # Fix all hrefs in <a> tags
        link_tags = soup.find_all('a', recursive=True)
        for tag in link_tags:
            if tag.get('href') == None: continue
            if tag.get('href').startswith('#'): continue

            # First convert the href to the url
            _ = parse.unquote(tag.get('href'), encoding="utf-8", errors="ignore")
            url = convert_to_url(original_link, _)

            if unlayered_html_map.get(url) == None:
                if make_external_page:
                    # Convert the href link to an external link
                    loc = os.path.join(root, 'external.html')
                    dir = os.path.dirname(path)
                    rel_path = os.path.relpath(loc, start=dir)
                    tag['href'] = rel_path + '?link=' + url
            else:

                # Convert the href link to local path to file
                rel_path = os.path.relpath(
                    path=unlayered_html_map.get(url),
                    start = os.path.dirname(path)
                )
                tag['href'] = rel_path
            # href fixed
        # End for loop, all links to pages fixed

        # Fix all hrefs in <link> tags and src attributes in all tags
        link_tags = soup.find_all('link', recursive=True)
        for tag in link_tags:
            if tag.get('href') == None: continue
            if tag.get('href').startswith('#'): continue

            # First convert the href to the url
            _ = parse.unquote(tag.get('href'), encoding="utf-8", errors="ignore")
            url = convert_to_url(original_link, _)

            if media_map.get(url) == None:
                if make_external_page:
                    # Convert the href link to an external link
                    loc = os.path.join(root, 'external.html')
                    dir = os.path.dirname(path)
                    rel_path = os.path.relpath(loc, start=dir)
                    tag['href'] = rel_path + '?link=' + url
            else:

                # Convert the href link to local path to file
                rel_path = os.path.relpath(
                    media_map.get(url),
                    start = os.path.dirname(path)
                )
                tag['href'] = rel_path
            # href fixed
        # End for loop, all hrefs fixed

        all_tags = soup.find_all(recursive=True)
        for tag in all_tags:
            if tag.get('src') == None: continue
            if tag.get('src').startswith('#'): continue
            # First convert the src to the url
            _ = parse.unquote(tag.get('src'), encoding="utf-8", errors="ignore")
            url = convert_to_url(original_link, _)

            if media_map.get(url) == None:
                if make_external_page:
                    # Convert the src link to an external link
                    loc = os.path.join(root, 'external.html')
                    dir = os.path.dirname(path)
                    rel_path = os.path.relpath(loc, start=dir)
                    tag['src'] = rel_path + '?link=' + url
            else:
                # Convert the src link to local path to file
                rel_path = os.path.relpath(
                    path=media_map.get(url),
                    start = os.path.dirname(path)
                )
                tag['src'] = rel_path
            # src fixed
        # End for loop, All srcs fixed

        # All tags fixed in this page, still need to write to file
        file = open(path, 'wb')
        file.write(soup.encode(encoding='utf-8'))
        file.close()
        print("Pages fixed: [{}/{}]".format(i, length), end="\033[K\r")
        i += 1
    # All html documents fixed
    print("Pages fixed: [{}/{}]".format(i, length), end="\033[K\n")
