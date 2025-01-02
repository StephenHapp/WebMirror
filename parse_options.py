import sys
import os
from rules import link_is_wanted, compile
from opt_enums import *

# Returns a dictionary of the options parsed from array of command line arguments
def parse_options(argv):
    # Stores options requested by the user
    result = { 
        # These first ones require user to provide values
        "dest_path": None,
        "layer0_path": None,
        # The rest are set to default values
        "max_depth": 0,
        "link_rules": compile(os.path.abspath("./default/linkrules.txt")),
        "media_rules": compile(os.path.abspath("./default/mediarules.txt")),
        "make_external_page": True,
        "include_queries": False,
        "long_names": [LongNames.TRUNCATE, 64],
        "name_chars": NameChars.WINDOWS,
        "reserved_names": ReservedNames.WINDOWS,
        "structure": Structure.SITE,
        "max_threads": 50,
        "max_requests": MaxRequests.NOLIMIT
    }

    for arg in argv[1:]:
        option_split = arg.split(':')

        match option_split[0]:
            case 'dest':
                path = os.path.abspath(option_split[1])
                result.update({'dest_path': path})
            case 'layer0':
                path = os.path.abspath(option_split[1])
                if not os.path.isfile(path):
                    raise Exception("Could not find layer-0 links file: " + str(path))
                result.update({'layer0_path': path})
            case 'depth':
                num = None
                try:
                    num = int(option_split[1]) # This should be the number of layers to mirror
                except ValueError:
                    raise Exception('Invalid depth: ' + option_split[1] + '. Depth must be non-negative integer')
                if num < 0:
                    raise Exception('Invalid depth: ' + str(num) + '. Depth must be non-negative integer')
                result.update({'max_depth': num})
            case 'linkrules':
                path = os.path.abspath(option_split[1])
                if not os.path.isfile(path):
                    raise Exception("Could not find path to linkrules file: " + str(path))
                result.update({'link_rules': compile(path)})
            case 'mediarules':
                path = os.path.abspath(option_split[1])
                if not os.path.isfile(path):
                    raise Exception("Could not find path to mediarules file: " + str(path))
                result.update({'media_rules': compile(path)})
            case 'externalpage':
                match (option_split[1]):
                    case 'true': result.update({'make_external_page': True})
                    case 'false': result.update({'make_external_page': False})
                    case _: raise Exception("Invalid value for externalpage option: " + option_split[1])
            case 'queries':
                match (option_split[1]):
                    case 'true': result.update({'include_queries': True})
                    case 'false': result.update({'include_queries': False})
                    case _: raise Exception("Invalid value for queries option: " + option_split[1])
            case 'longnames':
                match (option_split[1]):
                    case 'nofix': result.update({'long_names': LongNames.NOFIX})
                    case 'trunc': # option_split[2] should have max file name length
                        num = None
                        try:
                            num = int(option_split[2])
                        except ValueError:
                            raise Exception('Invalid value: ' + option_split[1] + '. File name length must be a positive integer')
                        if num < 1:
                            raise Exception('Invalid value: ' + str(num) + '. File name length must be a positive integer')
                        result.update({'long_names': (LongNames.TRUNCATE, num)})
                    case 'rand': # option_split[2] should have max file name length
                        num = None
                        try:
                            num = int(option_split[2])
                        except ValueError:
                            raise Exception('Invalid value: ' + option_split[1] + '. File name length must be a positive integer')
                        if num < 1:
                            raise Exception('Invalid value: ' + str(num) + '. File name length must be a positive integer')
                        result.update({'long_names': (LongNames.RANDOM, num)})
                    case _: raise Exception("Invalid value for longnames option: " + option_split[1])
            case 'namechars':
                match (option_split[1]):
                    case 'nofix':
                        result.update({'name_chars': NameChars.NOFIX})
                    case 'windows':
                        result.update({'name_chars': NameChars.WINDOWS})
                    case _: # Must be a path to a file
                        path = os.path.abspath(option_split[1])
                        if not os.path.isfile(path):
                            raise Exception("Could not find file for accepted file name characters: " + str(path))
                        file = open(path, 'r')
                        result.update({'name_chars': set(str(file.read()))})
                        file.close()
            case 'reservednames':
                match (option_split[1]):
                    case 'nofix': result.update({'reserved_names': ReservedNames.NOFIX})
                    case 'windows': result.update({'reserved_names': ReservedNames.WINDOWS})
                    case _:
                        raise Exception("Invalid value for reservednames option: " + option_split[1])
            case 'structure':
                match (option_split[1]):
                    case 'site': result.update({'structure': Structure.SITE})
                    case 'extension': result.update({'structure': Structure.EXTENSION})
                    case 'twodir': result.update({'structure': Structure.TWODIR})
                    case 'onedir': result.update({'structure': Structure.ONEDIR})
                    case _:
                        raise Exception("Invalid value for structure option: " + option_split[1])
            case 'maxthreads':
                num = None
                try:
                    num = int(option_split[1])
                except ValueError:
                    raise Exception('Invalid value for maxthreads option: ' + option_split[1] + '. Must be positive integer')
                if num < 1:
                    raise Exception('Invalid value for maxthreads option: ' + str(num) + '. Must be positive integer')
                result.update({'max_threads': num})
            case 'maxrequests':
                if option_split[1] == 'nolimit':
                    result.update({'max_requests': MaxRequests.NOLIMIT})
                else:
                    num1 = None
                    num2 = None
                    try:
                        num1 = int(option_split[1])
                        num2 = int(option_split[2])
                    except ValueError:
                        raise Exception('Invalid value for maxrequests option: ' + option_split[1] + ' ' + option_split[2])
                    if (num1 < 1) or (num2 < 1):
                        raise Exception('Invalid value for maxrequests option: ' + option_split[1] + ' ' + option_split[2] + '. Both numbers must be positive integers')
                    result.update({'max_requests': [num1, num2]})
            case _:
                raise Exception('Invalid option: ' + option_split[0])
        # End of match statement
    # End of for loop

    # Ensure that required values were provided
    if (result.get('dest_path') == None):
        raise Exception('Required option not provided: dest:<path>')
    if (result.get('layer0_path') == None):
        raise Exception('Required option not provided: layer0:<path>')

    return result