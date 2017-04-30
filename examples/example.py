
from intra import IntraUI, introspect, iprint
from tkinter import *
from tkinter import ttk
import time

class Decoration:
    '''
    A decoration!
    '''
    def __init__(self):
        self.decorationtype = "paint"

class Weapon:
    '''
    A weapon!
    '''
    def __init__(self):
        self.weapon_damage = 3

    def hit(self, who):
        who.inflict(self.weapon_damage)

    def decorate(self):
        self.decoration = Decoration()

class Adventurer:
    '''
    An adventurer!
    '''
    def __init__(self):
        self.x = 3
        self.y = 10
        self.type = "Wizard"
        self.stats = (12, 13,)
        self.greetings = ['Ho there!', 'Hello!','Who goes there?']
        self.spells = dict(spell1="blinding light", spell2="fire", spell3="zap")
        self.iswizard = True
    
    def get_weapon(self, weapon):
        self.weapon = weapon
        print("Acquired weapon with {0} damage!".format(self.weapon.weapon_damage))

    def do_something(self):
        pass



ui = IntraUI()

# have some objects you want to analyze
gandalf = Adventurer()
white_staff = Weapon()

# perform the introspection. This gives you an IntrospectionResult which you can then view via command line or UI.
gandalf_inspected = introspect(gandalf)
white_staff_inspected = introspect(white_staff)

# lets view it using the UI. You can add multiple inspections to the same viewer.
viewer = ui.createViewer("Before Gandalf Had Weapon")
viewer.add(gandalf_inspected)
viewer.add(white_staff_inspected)

# lets modify the objects and reanalyze them
white_staff.decorate()
gandalf.get_weapon(white_staff)

# if you set the recurse flag to true, all sub-objects within the object being introspected will be traversed as well, recursively.
#     Arguments:
#    recurse -- whether to recurse through classes contained within the object. Good to use if there are no circular references within the object being analyzed.
gandalf_inspected_again = introspect(gandalf, recurse=True)

# View it using the UI. We'll create a new viewer here.
viewer2 = ui.createViewer("After Gandalf Had Weapon")
viewer2.add(gandalf_inspected_again)

# you can print the introspection if you're using a shell. Pass the inspection to iprint.
#    Arguments:
#    pretty_print -- Whether to wrap the output in a border for easier debugging
#    pretty_print_title -- What the wrapped output title will be

iprint(gandalf_inspected)
iprint(gandalf_inspected_again)

# To see what data the introspection actually stores, we can just introspect our introspections
inception = introspect(gandalf_inspected, recurse=True)
viewer2.add(inception)


#### ALTERNATIVE:



while True:
    print('hello!')
    time.sleep(5)
    pass