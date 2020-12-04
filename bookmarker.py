import os
import json
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
import tkinter.ttk as ttk

import random

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

    def delete_by_names(self, names):
        self.bookmarks = [
            x for x in self.bookmarks
            if x.get('name') not in [n.replace('***', '') for n in names]
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

    def get_bm_by_name(self, name):
        for b in self.bookmarks:
            if name == b.get('name'):
                return b
        return None

def update_tree(*args):

    filter_by = search_field_var.get().lower()

    working_list = [
        b for b in model.bookmarks
        if not filter_by
        or filter_by in b.get('name').lower()
        ]

    tree.delete(*tree.get_children())
    tree.tag_configure('missing', background='red')

    for b in working_list:
        missing = ''
        if not os.path.exists(b['filepath']):
            print(f'{b["name"]} MISSING')
            missing = '***'
        tree.insert('', 'end', text=missing + b['name'])

    items_left = tree.get_children()
    if not items_left:
        return
    
    
    tree.selection_set(items_left[0])

def select_next(event):
    print('select next')

def select_prev(event):
    print('select previous')

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

    selected_items = tree.selection()
    if not selected_items:
        return
    
    selected_name = tree.item(selected_items[0])['text']

    bm = model.get_bm_by_name(selected_name)

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
    selected_items = tree.selection()
    if not selected_items:
        return

    names = [tree.item(x)['text'] for x in tree.selection()]
    answer = messagebox.askquestion("Delete", "Are You Sure?", icon='warning')

    if answer == 'yes':
        model.delete_by_names(names)

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
        name = tree.item(i)['text']
        bm = model.get_bm_by_name(name)
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
        name = tree.item(i)['text']
        bm = model.get_bm_by_name(name)
        fp = bm.get('filepath')
        os.startfile(os.path.dirname(fp))
        bm['last_opened'] = time.time()

    model.sort_bms(reverse=True)
    model.save()
    update_tree()

model = Model()
window = tk.Tk()
window.title("Bookmarker")
window.geometry('600x1200')

tree = ttk.Treeview(window)
s = ttk.Style()
s.configure('Treeview', rowheight=40)
fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)

btn_open = tk.Button(fr_buttons, text="Open", command=open_file)
btn_open_loc = tk.Button(fr_buttons, text="Open Location", command=open_location)

btn_create = tk.Button(fr_buttons, text="Create", command=create)
btn_edit = tk.Button(fr_buttons, text="Edit", command=edit)
btn_delete = tk.Button(fr_buttons, text="Delete", command=delete)

search_field_var = tk.StringVar()
search_field = tk.Entry(textvariable=search_field_var)
search_field_var.trace_add('write', update_tree)

window.bind("<Return>", open_file)
window.bind("<Shift_L><Return>", open_location)
window.bind("<Shift_R><Return>", open_location)
window.bind("<F2>", edit)

window.bind("<Up>", select_prev)
window.bind("<Right>", select_next)
window.bind("<Down>", select_next)
window.bind("<Left>", select_prev)

btns = [
    btn_open,
    btn_open_loc,
    btn_create,
    btn_edit,
    btn_delete,
]

for btn in btns:
    btn.pack(side=tk.LEFT)
fr_buttons.pack(fill=tk.X)

search_field.pack(fill=tk.X)

tree.pack(expand=True, fill=tk.BOTH)
update_tree()

window.mainloop()