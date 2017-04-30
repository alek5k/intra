
import inspect
import itertools
import collections
from inspect import currentframe
import uuid


class IntrospectionResult:
    '''
    class_type: The type of object the introspection result is
    class_stack: The stack is a container of property/method metadata
    '''
    def __init__(self, line_no, class_type, class_stack):
        self.result_id = uuid.uuid4()
        self.line_no = line_no
        self.class_type = class_type
        self.class_stack = class_stack



class ClassStack:
    '''
    A container for the metadata of the properties/methods in the object.
    '''
    def __init__(self, name, value, docstring, valtype, indentation):
        self.stack = list()
        self.name = name
        self.value = value
        self.docstring = docstring
        self.valtype = valtype
        self.strdata = indentation + "{: <20}{: <20}{: <20}".format(self.name, str(self.valtype), str(self.value))

    def append(self, data):
        self.stack.append(data)
    

class ClassItem:
    '''
    A property/method of an object.
    '''
    def __init__(self, name, value, docstring, valtype, indentation):
        self.name = name
        self.value = value
        self.docstring = docstring
        self.valtype = valtype
        self.strdata = indentation + "{: <20}{: <20}{: <20}".format(self.name, str(self.valtype), str(self.value))



def __isbound(m):
    '''
    Checks if the method is bound, i.e. a user-defined method.
    Also see: http://stackoverflow.com/questions/53225/how-do-you-check-whether-a-python-method-is-bound-or-not
    '''
    return hasattr(m, '__self__')


def __issequence(obj):
    '''
    Checks if an object is a python sequence (such as a list or a tuple)
    Also see:   [1] https://docs.python.org/2/library/stdtypes.html#sequence-types-str-unicode-list-tuple-bytearray-buffer-xrange
                [2] http://stackoverflow.com/questions/2937114/python-check-if-an-object-is-a-sequence
    '''
    if isinstance(obj, str):
        return False
    return isinstance(obj, collections.Sequence)
    

def __introspect_object(obj, recurse, stack, spacing=''):
    '''
    Introspects the object, and pushes the output to the stack.
    While traversing the object, if it finds another object, this method will call itself recursively.
    Arguments:
    obj -- the object to traverse
    recurse -- whether to recurse through classes contained within the object. Good to use if there are no circular refs anywhere.
    stack -- the stack to push the result to, for printing later
    spacing -- the spacing to use before the string gets put into the stack. Done so as to create a better tree structure
    '''
    elems = inspect.getmembers(obj)

    for x in elems:
        
        
        valtype = 'class'
        
        if (x[0].startswith("__") and x[0].endswith("__")):
            continue

        if callable(x[1]):
            if __isbound(x[1]):
                valtype = 'class_method'
            else:
                valtype = 'other_callable'

        if __issequence(x[1]):
            valtype = 'sequence'

        if isinstance(x[1], str):
            valtype = 'string'
        
        if isinstance(x[1], (int, float, complex,)):
            valtype = 'numeric'

        if isinstance(x[1], dict):
            valtype = 'map'
        
        if isinstance(x[1], bool):
            valtype = 'boolean'

        if valtype == 'class':
            newstack = ClassStack(x[0], x[1], inspect.getdoc(x[1]), valtype, spacing)
            if recurse:
                __introspect_object(x[1], recurse, newstack, spacing + '   ')
            stack.append(newstack)
            continue

        stack.append(ClassItem(x[0], x[1], inspect.getdoc(x[1]), valtype, spacing))



def introspect(obj, recurse=False):
    '''
    Introspects the object and returns an IntrospectionResult.
    Arguments:
    recurse -- whether to recurse through classes contained within the object. Good to use if there are no circular references within the object being analyzed.
    ''' 
    cf = currentframe()
    line_no = cf.f_back.f_lineno

    root_stack = ClassStack("root", obj, inspect.getdoc(obj), 'class', 'ROOT>')
    __introspect_object(obj, recurse, root_stack)

    return IntrospectionResult(line_no=line_no, class_type=str(type(obj)), class_stack=root_stack)
