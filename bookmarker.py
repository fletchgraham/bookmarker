import os
import json
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
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
        bm['last_opened'] = time.time()
        self.bookmarks.append(bm)

    def sort_bms(self, key=None, reverse=False):
        key = key or 'last_opened'
        self.bookmarks = sorted(
            self.bookmarks,
            key = lambda x: x.get(key) or 1,
            reverse=reverse
        )

def update_tree():
    tree.delete(*tree.get_children())

    for b in model.bookmarks:
        tree.insert('', 'end', text=b['name'])

def create():
    print('create')
    bm = {}
    bm['filepath'] = filedialog.askopenfilename()
    if not bm.get('filepath'):
        return 
    bm['name'] = simpledialog.askstring('Name the Bookmark','give a name')
    if not bm.get('name'):
        return
    model.create(bm)
    model.sort_bms(reverse=True)
    model.save()
    update_tree()

def edit(event=None):
    print('edit')
    try:
        selected_index = tree.index(tree.selection()[0])
    except:
        return

    bm = model.bookmarks[selected_index]

    answer = simpledialog.askstring(
        'Name the Bookmark',
        'give a name',
        initialvalue=bm['name']
    )

    if answer:
        bm['name'] = answer

    model.save()
    update_tree()

def delete():
    print('delete')
    indicies = [tree.index(x) for x in tree.selection()]
    answer = messagebox.askquestion("Delete", "Are You Sure?", icon='warning')

    if answer == 'yes':
        model.delete_indicies(indicies)

    model.save()
    update_tree()

def version_split(filename):
    """Return a tuple with version suffix
    (name, v_suffix, ext)
    """

    name, ext = os.path.splitext(filename)
    chars = ['v', '-', '_']
    name = name
    v_suffix = ''
    last_char = name[-1]
    saw_a_v = False
    while last_char.isdigit() and not saw_a_v or last_char.lower() in chars:
        if last_char.lower() == 'v':
            saw_a_v = True
        v_suffix = name[-1] + v_suffix
        name = name[:-1]
        last_char = name[-1]

    return name, v_suffix, ext

def v_suffix_to_int(v_string):
    """turn a version suffix into an integer"""
    digits = ''.join([x for x in v_string if x.isdigit()])
    return int(digits)

def get_latest_version(filepath):
    """Return path to the latest version of the provided filepath"""
    dirname = os.path.dirname(filepath)
    basename = os.path.basename(filepath)
    name, v_suffix, ext = version_split(basename)
    
    files = [
        f for f in os.listdir(dirname)
        if not os.path.isdir(f)
        and os.path.splitext(f)[1] == ext
        and name in f
    ]

    latest = sorted(
        files,
        key=lambda x: v_suffix_to_int(version_split(x)[1])
        )[-1]
    
    return os.path.join(dirname, latest)

def open_file(event=None):
    print('open')
    for i in tree.selection():
        index = tree.index(i)
        bm = model.bookmarks[index]
        fp = bm.get('filepath')
        try:
            latest_version = get_latest_version(fp)
        except:
            latest_version = fp
        os.startfile(latest_version)
        bm['last_opened'] = time.time()
    
    model.sort_bms(reverse=True)
    model.save()
    update_tree()

def open_location(event=None):
    print('open location')
    for i in tree.selection():
        index = tree.index(i)
        bm = model.bookmarks[index]
        fp = bm.get('filepath')
        os.startfile(os.path.dirname(fp))
        bm['last_opened'] = time.time()

    model.sort_bms(reverse=True)
    model.save()
    update_tree()

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

window.bind("<Return>", open_file)
window.bind("<Shift_L><Return>", open_location)
window.bind("<Shift_R><Return>", open_location)
window.bind("<F2>", edit)

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