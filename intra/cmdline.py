
import inspect
import itertools
import collections
from inspect import currentframe
import colorama
from .core import *



def colortext(text, color):
    '''
    Returns the string with a provided colorama color, with a reset afterwards
    Note this function should not be used externally. Used by internal classes only.
    __ prefix not possible.
    '''
    return color + text + colorama.Style.RESET_ALL

class TypeMap:
        color_map = {
            'class_method': colorama.Fore.YELLOW,          # https://docs.python.org/3/library/functions.html#callable
            'other_callable': colorama.Fore.RED,     # https://docs.python.org/3/library/functions.html#callable
            'sequence': colorama.Fore.MAGENTA,          # https://docs.python.org/3/library/stdtypes.html#sequence-types-list-tuple-range
            'string': colorama.Fore.BLUE,               # I dunno i sort of like strings being separate
            'numeric': colorama.Fore.WHITE,             # https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex
            'map': colorama.Fore.LIGHTBLUE_EX,          # https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
            'boolean': colorama.Fore.LIGHTGREEN_EX,     # https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not
            'class': colorama.Fore.CYAN,
            
        }

def __printstack(stack):
    #for item in reversed(stack.stack):
    for item in stack.stack:
        if isinstance(item, ClassStack):
            #print("{0}, {1}, {2}".format(item.name, item.value, item.valtype))
            print()
            printstring = colortext(item.strdata, TypeMap.color_map[item.valtype])
            print(printstring)
            __printstack(item)
            print()
            continue
        if isinstance(item, ClassItem):
            #print("{0}, {1}, {2}".format(item.name, item.value, item.valtype))
            printstring = colortext(item.strdata, TypeMap.color_map[item.valtype])
            print(printstring)
            continue
        print(item)

def iprint(introspectionresult, pretty_print=True, pretty_print_title=""):

    import colorama

    colorama.init()
    '''
    Prints the output of the introspection.
    Arguments:
    pretty_print -- Whether to wrap the output in a border for easier debugging
    pretty_print_title -- What the wrapped output title will become
    '''
    if pretty_print:
        print("==============================")
        print("[Introspection on line " + str(introspectionresult.line_no) + "] Instance of: " + introspectionresult.class_type)
        if (pretty_print_title != ""):
            print(pretty_print_title)
        print("==============================")
    __printstack(introspectionresult.class_stack)
    #for item in reversed(root_stack):
    #    print("{0}, {1}".format(item, type(item)))

    if pretty_print:
        print("==============================")

    print(colorama.Style.RESET_ALL)