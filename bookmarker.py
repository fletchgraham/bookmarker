import os
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
import tkinter.ttk as ttk

import random

# SPEC
# show a list of bookmarks, last opened on top
# add bookmark
# remove bookmark
# edit bookmark
# open latest version of bookmarked file
# open bookmark location in explorer

# MODEL
# could be a deque of bookmarks
# can pickle itself

# BOOKMARK
# a dictionary of 
# name
# dir path
# file base name
# type

# VIEW
# treeview on right
# buttons on left

class Model():
    def __init__(self):
        self.bookmarks = []
        self.read()

    def read(self):
        self.bookmarks = []
        if os.path.exists('model.json'):
            with open('model.json', 'r') as infile:
                self.bookmarks = json.load(infile)

    def save(self):
        with open('model.json', 'w') as outfile:
            json.dump(self.bookmarks, outfile, indent=4)

    def delete_indicies(self, indicies_list):
        self.bookmarks = [
            x for i, x in enumerate(self.bookmarks)
            if not i in indicies_list
            ]
    
    def create(self, bm):
        self.bookmarks.append(bm)

def update_tree():
    tree.delete(*tree.get_children())

    for b in model.bookmarks:
        tree.insert('', 'end', text=b['name'])

def create():
    print('create')
    bm = {}
    bm['filepath'] = filedialog.askopenfilename()
    bm['name'] = simpledialog.askstring('Name the Bookmark','give a name')
    model.create(bm)
    model.save()
    update_tree()

def edit():
    print('edit')
    # open form, populate with highlighted bookmark's data
    # model updates bookmark at that index
    # pickle self
    # update tree

def delete():
    print('delete')
    indicies = [tree.index(x) for x in tree.selection()]
    model.delete_indicies(indicies)
    model.save()
    update_tree()

def open_file():
    print('open')
    # to do

def open_location():
    print('open location')
    for i in tree.selection():
        index = tree.index(i)
        fp = model.bookmarks[index].get('filepath')
        os.startfile(os.path.dirname(fp))
    # update last opened for that bookmark
    # pickle self
    # update the tree


model = Model()

window = tk.Tk()
window.title("Bookmarker")
window.rowconfigure(0, minsize=800, weight=1)
window.columnconfigure(1, minsize=800, weight=1)

tree = ttk.Treeview(window)
s = ttk.Style()
s.configure('Treeview', rowheight=40)
fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)

btn_open = tk.Button(fr_buttons, text="Open", command=open_file)
btn_open_loc = tk.Button(fr_buttons, text="Open Location", command=open_location)

btn_create = tk.Button(fr_buttons, text="Create", command=create)
btn_edit = tk.Button(fr_buttons, text="Edit", command=edit)
btn_delete = tk.Button(fr_buttons, text="Delete", command=delete)

btns = [
    btn_open,
    btn_open_loc,
    btn_create,
    btn_edit,
    btn_delete,
]

for btn in btns:
    btn.pack(fill=tk.X)

fr_buttons.grid(row=0, column=0, sticky="ns")
tree.grid(row=0, column=1, sticky="nsew")
update_tree()

window.mainloop()