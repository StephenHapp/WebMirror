import requests
import mimetypes
import os
from urllib import parse
from opt_enums import *
from random_name import random_name
from time import sleep

valid_extensions = ('.aac', '.abw', '.arc', '.avif', '.avi', '.azw', '.bin', '.bmp', '.bz', '.bz2', '.cda', '.csh', '.css', '.csv', '.doc', '.docx', '.eot', '.epub', '.gz', '.gif', '.htm', '.html', '.ico', '.ics', '.jar', '.jpeg', '.jpg', '.js', '.json', '.jsonld', '.mid', '.midi', '.mjs', '.mp3', '.mp4', '.mpeg', '.mpkg', '.odp', '.ods', '.odt', '.oga', '.ogg', '.ogv', '.ogx', '.opus', '.otf', '.png', '.pdf', '.php', '.ppt', '.pptx', '.rar', '.rtf', '.sh', '.svg', '.tar', '.tif', '.tiff', '.ts', '.ttf', '.txt', '.vsd', '.wav', '.weba', '.webm', '.webp', '.woff', '.woff2', '.xhtml', '.xls', '.xlsx', '.xml', '.xul', '.zip', '.3gp', '.3g2', '.7z')
windows_forbidden_characters = ('<', '>', ':', '"', '\\', '|', '?', '*', '^')
windows_forbidden_names = ('CON', 'PRN', 'AUX', 'NUL', 'COM0', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT0', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9')

headers = {
    'User-Agent': 'WebMirror (python script using requests library)',
    'Accept-Encoding': 'gzip'
}

# Returns the absolute path to the downloaded file, or None on failure
def download(download_link, destination_dir, longnames_opt,
             namechars_opt, reservednames_opt, structure_opt):
    download_link # Link on web to get and download
    destination_dir # Directory to store downloaded file
    longnames_opt # Indicates how to fix long file names
    namechars_opt # Indicates how to fix unsupported characters in file names
    reservednames_opt # Indicates how to fix unsupported file names
    structure_opt # Indicates where to store file in destination_dir
    
    try:
        response = requests.get('https://' + download_link, headers=headers)
        # Sometimes response takes a lil bit
        sleep(0.2)
    except:
        response = None
    
    

    if (response == None) or (not response.ok):
        # Might need to try encoding the URL
        encoded_link = parse.quote(download_link)
        try:
            response = requests.get('https://' + encoded_link, headers=headers)
            # Sometimes response takes a lil bit
            sleep(0.2)
        except:
            response = None

    if (response == None) or (not response.ok):
        return None

    # Determine file extension
    file_extension = get_file_extension(response.headers.get('content-type'), download_link)

    # Determine name to save as
    filename = download_link.removesuffix(file_extension) # Does nothing if file extensions don't match, that's OK
    filename = filename.split('/')[-1] # Isolate path from file name

    # Modifies filename if necessary
    filename = shorten(filename, longnames_opt)
    filename = fixchars(filename, namechars_opt)
    filename = fixname(filename, reservednames_opt)
    # filename ready

    # Determine location to store
    directory = get_directory(download_link, destination_dir, structure_opt, namechars_opt, file_extension)
    
    # Put it all together
    local_path = os.path.normpath(os.path.join(directory, filename + file_extension))

    # Save the file at a new location without overwriting preexisting files
    local_path = save_new(response, local_path, file_extension)

    # File saved, return location of file
    response.close()
    return local_path


# Returns a file extension based on the MIME type
def get_file_extension(mime_type, url):
    mime_type = mime_type.split(';', 1)[0] # Isolates the part that determines file extension
    result = mimetypes.guess_extension(mime_type, False)
    if result == None:
        # Try again manually
        result = os.path.splitext(url)[1].split('?', 1)[0]
        if result not in valid_extensions:
            print('Warning: could not determine file type: ' + url, end="\033[K\n")
            return ''
    return result

# Returns a shortened filename according to the passed in option
def shorten(filename, option):
    if option == LongNames.NOFIX: return filename

    # Option is either LongNames.RANDOM or LongNames.TRUNCATE
    # Only need to shorten if longer than desired
    if len(filename) <= option[1]: return filename

    # It's time to shorten
    if option[0] == LongNames.TRUNCATE:
        filename = filename[0:option[1]]
    elif option[0] == LongNames.RANDOM:
        filename = random_name()
    return filename

# Returns filename with characters replaced according to passed in option
def fixchars(filename, option):
    if option == NameChars.NOFIX: return filename
    elif option == NameChars.WINDOWS:
        result = ''
        for character in filename:
            if character in windows_forbidden_characters: result += '_'
            else: result += character
    else: # option is the set of allowed characters
        result = ''
        for (character) in filename:
            if character in option: result += character
            else: result += '_'
    return result

# Returns filename that meets desired restrictions on allowed file names
def fixname(filename, option):
    if option == ReservedNames.NOFIX: return filename
    elif option == ReservedNames.WINDOWS:
        if filename.upper() in windows_forbidden_names:
            filename = random_name()
    return filename

# Returns the absolute path to the directory where file should be stored
def get_directory(link, home_dir, structure_option, chars_option, extension):
    match structure_option:
        case Structure.ONEDIR:
            return os.path.join(home_dir, "files")
        case Structure.TWODIR:
            if (extension.upper() == '.HTML') or (extension.upper() == '.HTM'):
                return os.path.join(home_dir, 'html')
            else:
                return os.path.join(home_dir, 'media')
        case Structure.EXTENSION:
            extension = extension.lstrip('.')
            if len(extension) == 0:
                extension = '_'
            return os.path.join(home_dir, extension)
        case Structure.SITE:
            # Isolate the file's location on the web from link
            webdir = os.path.dirname(link)
            # Need to fix webdir to match allowed chars
            webdir = fixchars(webdir, chars_option)
            return os.path.join(home_dir, webdir)

def save_new(response, destination, extension):
    if os.path.isfile(destination):
        # Find a destination that isn't taken
        destination = destination.removesuffix(extension)
        count = 1
        while os.path.isfile(destination + '(' + str(count) + ')' + extension):
            count += 1
        destination = (destination + '(' + str(count) + ')' + extension)
    # Destination is safe to save to
    os.makedirs(os.path.dirname(destination), mode=700, exist_ok=True)
    file = open(destination, 'wb')
    file.write(response.content)
    file.close()
    return destination

def one_thread(link, layer_map, options):
    localpath = download(
        link,
        options.get('dest_path'),
        options.get('long_names'),
        options.get('name_chars'),
        options.get('reserved_named'),
        options.get('structure')
    )
    # Might be None if there was an error
    if localpath == None:
        print("Error: failed to download " + link, end="\033[K\n")
        layer_map.pop(link)
    else:
        layer_map.update({link: localpath})
        