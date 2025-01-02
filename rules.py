#   File that handles parsing and understanding user-supplied rules for links
#   
#   Example file:
#   
#   - "en\.wikipedia\.org.*"    
#   + "en\.wikipedia\.org/Wikipedia/Vital_articles/Level/5.*"
#   LAYERS 3 4
#   - ".*"
#   + "en\.wikipedia\.org/wiki.*" !".*#.*"
#   
#   Inclusion/Exclusion:
#   
#   +       Include the link if the rule matches, but continue checking following rules
#   
#   -       Exclude the link if the rule matches, but continue checking following rules
#   
#   ++      IMMEDIATELY include the link if the rule matches, skipping all following
#           rules
#   --      IMMEDIATELY exclude the link if the rule matches, skipping all following
#           rules
#   
#   Regular expresssions:
#   
#   ""      Strings inside double quotes are evaluated as a regular expression using
#           Python's built-in library (re)
#   
#   !       NOT. Flips the result of the immediately following regular expression
#   
#           List multiple regular expressions in a line to require that all expressions
#           apply to the link for the rule to take effect.
#   
#   LAYER   Indicate which layers the following rules should apply to. Both
#   LAYERS  LAYER and LAYERS behave identically. The positive integers following
#           the word are the layers the rules apply to.
#   
#   #       Comments. Lines that begin with # are skipped immediately
from enum import Enum
import re

class Actions(Enum):
    INCLUDE = 1
    EXCLUDE = 2
    INCLUDENOW = 3
    EXCLUDENOW = 4
    SETLAYERS = 5

# Returns an array representing the same rules expressed in the file
def compile(filepath):
    file = open(filepath, "r")
    lines = file.readlines()
    file.close()

    result = []

    for linenum in range(len(lines)):
        line = lines[linenum]
        tokens = line.split()
        # Check for case of empty line
        if len(tokens) == 0: continue

        rule = []
        match tokens[0]:
            case '#': continue
            case '++': rule.append(Actions.INCLUDENOW)
            case '--': rule.append(Actions.EXCLUDENOW)
            case '+': rule.append(Actions.INCLUDE)
            case '-': rule.append(Actions.EXCLUDE)
            case 'LAYER' | 'LAYERS':
                rule.append(Actions.SETLAYERS)
            case _: raise Exception('Could not parse line {} of {}:\n{}'. format(linenum + 1, filepath, line))

        # Add the rest of the tokens to the rule, ensuring they are all valid
        if (rule[0] == Actions.SETLAYERS):
            # Just need to ensure the rest of the numbers are valid
            if len(tokens) == 1: raise Exception('Could not parse line {} of {}:\n{}'. format(linenum + 1, filepath, line))
            nums = set()
            for token in tokens[1:]: 
                try: num = int(token)
                except: raise Exception('Could not parse line {} of {}:\n{}'. format(linenum + 1, filepath, line))
                nums.add(num)
            rule.append(nums)
        else:
            # Ensure each expression is valid
            if len(tokens) == 1: raise Exception('Could not parse line {} of {}:\n{}'. format(linenum + 1, filepath, line))
            for token in tokens[1:]:
                expression = [False, None]
                if token[0] == '!':
                    expression[0] = True # Indicates to apply NOT to result of match
                pureToken = token.lstrip('!')
                if len(pureToken) < 2:
                    raise Exception('Could not parse line {} of {}:\n{}'. format(linenum + 1, filepath, line))
                if (pureToken[0] != '"') or (pureToken[-1] != '"'):
                    raise Exception('Could not parse line {} of {}:\n{}'. format(linenum + 1, filepath, line))
                pureToken = pureToken.strip('"')

                try: 
                    regex = re.compile(pureToken)
                except: 
                    raise Exception('Could not parse line {} of {}:\n{}'. format(linenum + 1, filepath, line))
                expression[1] = regex
                rule.append(expression)
            # End for loop
        # End if/else

        # Rule for this line has been finished
        result.append(rule)
    # End for loop
    # All rules have been compiled into the result array
    return result

# Checks the rules, returns True if link should be included, false otherwise
def link_is_wanted(link, link_layer, rules):
    layers = None # Indicates what layers the rules currently apply to. None indicates all layers
    result = True # Initially starts by assuming link should be included

    for rule in rules:
        if len(rule) <= 1: continue

        if rule[0] == Actions.SETLAYERS:
            layers = rules[1]
            continue
        if (layers != None): 
            if (link_layer not in layers): continue
        
        action = rule[0]
        # Check each expression in this line, and if all expressions pass, apply the action
        for expression in rule[1:]:
            flip = expression[0]
            regex = expression[1]
            expression_passes = flip ^ (re.search(pattern=regex, string=link) != None)
            if (not expression_passes):
                # Link doesn't pass all expressions, so action isn't applied
                action = None
                break
            # Link passed this expression, check the rest
        # End of for loop
        # Line completely checked, action now says the action to perform
        match action:
            case None: continue # Apply no action
            case Actions.INCLUDE: result = True
            case Actions.EXCLUDE: result = False
            case Actions.INCLUDENOW:
                result = True
                break
            case Actions.EXCLUDENOW:
                result = False
                break
    # End for loop

    # Result now tells if link should be included or not
    return result
