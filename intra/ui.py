from .core import *
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

