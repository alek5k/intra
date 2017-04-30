
import inspect
import itertools
import colorama
import collections
from inspect import currentframe
import uuid
from tkinter import *
from tkinter import ttk
import threading




##################
### UI SECTION ###
##################


def quick_inspect(obj):
    ui = IntraUI()
    obj_inspected = introspect(obj)
    viewer = ui.createViewer("Object inspected")
    viewer.add(obj_inspected)

'''
A wrapper for the UI thread so the user doesnt have to call .start() directly.
usage:

ui = IntraUI()

# create viewers and add inspections to them here
'''
class IntraUI(threading.Thread): 
    def __init__(self):
        threading.Thread.__init__(self)
        self.start() # http://stackoverflow.com/questions/459083/how-do-you-run-your-own-code-alongside-tkinters-event-loop/4836121#4836121


    def callback(self):
        self.root.quit()

    def run(self):
        self.root=Tk()
        self.root.withdraw() # http://stackoverflow.com/questions/1406145/how-do-i-get-rid-of-python-tkinter-root-window
        self.root.mainloop()

    def createViewer(self, title):
        return Viewer(title)

### DEPRECATED ####

#class IntraUI_NoThread:
#    '''
#    A wrapper for the UI thread so the user doesnt have to call .start() directly.
#    usage:
#
#    ui = IntraUI()
#    
#    # create viewers and add inspections to them here
#    '''
#    def __init__(self):
#        self.startUI()
#
#        ### DEPRECATED ###
#        #if is_multithreaded:
#            #self.uithread = _UIThreaded(self.startUI)
#            #self.uithread.start() # http://stackoverflow.com/questions/459083/how-do-you-run-your-own-code-alongside-tkinters-event-loop/4836121#4836121
#        #else:
#            #self.uicontainer = _UINonThreaded(self.startUI)
#        
#    def startUI(self):
#        self.root=Tk()
#        self.root.withdraw() # http://stackoverflow.com/questions/1406145/how-do-i-get-rid-of-python-tkinter-root-window
#        self.root.mainloop()
#
#class _UINonThreaded:
#    def __init__(self, ui_init_method):
#        ui_init_method()##
#
#class _UIThreaded(threading.Thread):
#    '''
#    TK as a threaded UI, so the introspection doesnt interfere with async/await, observables, reactors, etc. that people have in their programs.
#    '''
#    def __init__(self, ui_init_method):
#        self.ui_init_method = ui_init_method
#        threading.Thread.__init__(self)
#        self.start() # http://stackoverflow.com/questions/459083/how-do-you-run-your-own-code-alongside-tkinters-event-loop/4836121#4836121##
#
#    def run(self):
#        self.ui_init_method()


class Viewer:
    '''
    inspection1 = introspect(obj1)
    inspection2 = introspect(obj2)
    inspection3 = introspect(obj3)

    viewer = Viewer()
    viewer.add(inspection1)
    viewer.add(inspection2)
    
    viewer2 = Viewer()
    viewer2.add(inspection3)

    '''
    def __init__(self, custom_title="Introspection"):

        self.window = Toplevel()
        self.window.wm_title(custom_title)
        self.window.geometry('{}x{}'.format(900, 600))
        self.tree = ttk.Treeview(self.window)
        #http://knowpapa.com/ttk-treeview/
        self.tree["columns"] = ("type", "value", "docstring", "class_stack_symbol_string")
        self.tree["displaycolumns"]=("type", "value") # which columns to actually display http://stackoverflow.com/questions/33290969/hiding-treeview-columns-in-tkinter
        # self.tree["displaycolumns"]=("type", "value", "class_stack_symbol_string") # helpful for debugging
        self.tree.column("type", width=50)
        self.tree.column("value", width=300)
        self.tree.column("docstring", width=0) # this will be hidden
        self.tree.column("class_stack_symbol_string", width=300) # this will be hidden
        self.tree.heading("type", text="type")
        self.tree.heading("value", text="value")
        self.tree.heading("docstring", text="docstring") # this will be hidden
        self.tree.heading("class_stack_symbol_string", text="class_stack_symbol_string") # this will be hidden

        

        self.tree.bind("<Button-3>", self.popup) # right click context menu

        #self.menu = Menu(root, tearoff=0)
        self.menu = Menu(self.window, tearoff=0)
        self.menu.add_command(label="Show docstring", command=self.show_docstring)
        self.menu.add_command(label="Introspect", command=self.moar_introspect)
        #self.menu.add_command(label="Redo", command=self.hello)
        self.class_stack_inspections = [] # we store the class stacks from the introspection, so we can do further introspection later if need be

    def show_docstring(self):
        # print(self.tree.selection()) 
        iid = self.tree.selection()
        item_selected = self.tree.item(iid)
        #print(item_selected)
        if item_selected['values']:
            docstring = item_selected['values'][2]
            
            if docstring:
                self.docstringviewer = Toplevel()
                self.docstringviewer.wm_title("Docstring")
                label1 = Label(self.docstringviewer, text=docstring, justify=LEFT) # , height=20, width=100 (if you want to specify manually)
                label1.pack()
    
    def moar_introspect(self):
        # print(self.tree.selection()) 
        iid = self.tree.selection()
        item_selected = self.tree.item(iid)
        selected_class_stack = item_selected['values'][3] # note ttk treeview stores the values as strings, not objects.. which leads to a hack down here.

        # this was the previous way of doing it, when we were actually storing the introspections instead of just class-stacks. Leaving it here incase we ever need to go back.
        #class_stacks = [obj.class_stack.stack for obj in self.introspections]  # a list of lists at this point
        #class_stacks_extracted = [item for sublist in class_stacks for item in sublist] # flattening list
        #class_stacks_extracted = [item for item in class_stacks_extracted if isinstance(item, ClassStack)]
        #print(class_stacks_extracted)
        #print(selected_class_stack)

        # this is a bit of a hack... ttk treeview stores objects as strings, so we cant compare the item directly. We gotta compare the selected item in ttk (which is a string)
        # to the introspections we have performed...
        correct_class_stack = list(filter(lambda x: str(x) == selected_class_stack, self.class_stack_inspections))
        #print(correct_class_stack)

        if correct_class_stack:
            stack = correct_class_stack[0]
            if isinstance(stack, ClassStack):
                # the value parameter stores the actual object we want to then further introspect
                # print(stack)
                # print(stack.value)
                inspection = introspect(stack.value)

                viewer = Viewer("Expanded view of object instance '" + stack.name + "'")
                viewer.add(inspection)

        
    #http://stackoverflow.com/questions/12014210/python-tkinter-app-adding-a-right-click-context-menu
    def popup(self, event):
        """action in event of button 3 on tree view"""
        # select row under mouse
        iid = self.tree.identify_row(event.y)
        if iid:
            # mouse pointer over item
            self.tree.selection_set(iid)
            self.menu.post(event.x_root, event.y_root)
        else:
            pass # mouse pointer not over item , occurs when items do not fill frame, no action required
            
        
    def add(self, inspection):
        self.tree.insert("", 9999, inspection.result_id, text= "Line no. " + str(inspection.line_no) + " : " + inspection.class_type, values=(inspection.class_stack.valtype, '', inspection.class_stack.docstring, inspection.class_stack)) # note, we pass an empty string for value because we dont want to show anything in that column for these 'root' entries
        def enumeratetree(stack, parent):
            for item in stack:  
                if isinstance(item, ClassItem):
                    self.tree.insert(parent, 9999, text=item.name, values=(item.valtype, item.value, item.docstring, None))
                elif isinstance(item, ClassStack):
                    self.class_stack_inspections.append(item)
                    item_id = str(parent)+item.name # we add parent string (which is unique) to prevent conflicts, as tk complains about having a duplicate item id
                    self.tree.insert(parent, 9999, item_id, text=item.name, values=(item.valtype, item.value, item.docstring, item ))
                    enumeratetree(item.stack, item_id)

        enumeratetree(inspection.class_stack.stack, inspection.result_id)

        self.tree.pack(expand=YES, fill=BOTH)




#####################
### LOGIC SECTION ###
#####################

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
        strdata = indentation + "{: <20}{: <20}{: <20}".format(self.name, str(self.valtype), str(self.value))
        self.printstring = colortext(strdata, TypeMap.color_map[valtype])

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
        strdata = indentation + "{: <20}{: <20}{: <20}".format(self.name, str(self.valtype), str(self.value))
        self.printstring = colortext(strdata, TypeMap.color_map[valtype])






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
        
        color = colorama.Fore.RESET
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

def __printstack(stack):
    #for item in reversed(stack.stack):
    for item in stack.stack:
        if isinstance(item, ClassStack):
            #print("{0}, {1}, {2}".format(item.name, item.value, item.valtype))
            print()
            print(item.printstring)
            __printstack(item)
            print()
            continue
        if isinstance(item, ClassItem):
            #print("{0}, {1}, {2}".format(item.name, item.value, item.valtype))
            print(item.printstring)
            continue
        print(item)


def introspect(obj, recurse=False):
    '''
    Introspects the object and returns an IntrospectionResult.
    Arguments:
    recurse -- whether to recurse through classes contained within the object. Good to use if there are no circular references within the object being analyzed.
    ''' 
    cf = currentframe()
    line_no = cf.f_back.f_lineno

    colorama.init()
    root_stack = ClassStack("root", obj, inspect.getdoc(obj), 'class', 'ROOT>')
    __introspect_object(obj, recurse, root_stack)

    return IntrospectionResult(line_no=line_no, class_type=str(type(obj)), class_stack=root_stack)

def iprint(introspectionresult, pretty_print=True, pretty_print_title=""):
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
