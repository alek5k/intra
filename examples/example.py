
from intra.core import introspect
from intra.ui import IntraUI
from intra.cmdline import iprint
import time

class AnotherObject:
    '''
    Another object
    '''
    def __init__(self):
        self.anotherstring = "paint"
        self.anotherbool = True
        self.anothernumber = 55

class SomeObject:
    '''
    An object with a description
    '''
    def __init__(self):
        self.intattrib = 3
        self.stringattrib = "objtype"
        self.tupleattrib = (12, 13,)
        self.listattrib = ['Ho there!', 'Hello!','Who goes there?']
        self.dictattrib = dict(id1="aaa", id2="bbb", id3="ccc")
        self.boolattrib = True
    
    def add_nested_object(self, nestedobj):
        self.nestedobj = nestedobj

    def some_other_method(self):
        pass



if __name__ == "__main__":

    ui = IntraUI()

    # have some objects you want to analyze
    my_obj = SomeObject()
    another_obj = AnotherObject()

    # perform the introspection. This gives you an IntrospectionResult which you can then view via command line or UI.
    inspection1 = introspect(my_obj)
    inspection2 = introspect(another_obj)

    # lets view it using the UI. You can add multiple inspections to the same viewer.
    viewer = ui.createViewer("My Viewer Title")
    viewer.add(inspection1)
    viewer.add(inspection2)

    # lets modify the objects and reanalyze them
    my_obj.add_nested_object(another_obj)

    # if you set the recurse flag to true, all sub-objects within the object being introspected will be traversed as well, recursively.
    #     Arguments:
    #    recurse -- whether to recurse through classes contained within the object. Good to use if there are no circular references within the object being analyzed.
    reinspected = introspect(my_obj, recurse=True)

    # View it using the UI. We'll create a new viewer here.
    viewer2 = ui.createViewer("After adding a nested object")
    viewer2.add(reinspected)

    # you can print the introspection if you're using a shell. Pass the inspection to iprint.
    #    Arguments:
    #    pretty_print -- Whether to wrap the output in a border for easier debugging
    #    pretty_print_title -- What the wrapped output title will be

    print("\n\nTwo separate objects:\n\n")
    iprint(inspection1)
    iprint(inspection2)

    print("\n\nNested object:\n\n")
    iprint(reinspected)

    # To see what data the introspection actually stores, we can just introspect our introspections
    inception = introspect(my_obj, recurse=True)
    viewer2.add(inception)

    print('you can run your own blocking code while introspections are occurring on a separate thread.')
    while True:
        time.sleep(5)
        pass