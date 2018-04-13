'''
GUI to create routing sheets for jobs on the shop floor

BY: Patrick Touchette
Start Date: 2018-03-04

to implement:
job image - done
part image - done
job checklist - done
part process templates - done
bulk parts list entry - done
bulk raw material list
gantt chart - done
add material to part process frame
bulk parts process entries
part check boxes
automatic cost calculations
profitability calculations
Part profit bar graph visualisation - done
estimated delivery date - done
job scheduling system
'''

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import pandas as pd
import os
from PIL import Image, ImageTk
import datetime

import numpy as np
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2TkAgg)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import pdf_reports

#Global constants
TITLE_FONT = ('Droid', 12, 'bold')
LABEL_FONT = ('Droid, 10')
LABEL_FONT_BOLD = ('Droid', 10, 'bold')
FRAME_PADDING = (5, 5)  #padx, pady
WIDGET_PADDING = (3, 2)  #padx, pady
COLOR1 = '#808180' #grey
COLOR2 = '#COD5EA' #light blue
COLOR3 = '#0F4563' #blue
COLOR4 = '#636361' #darker grey
COLOR5 = '#BCB2D2' #purple grey

class Main_Application(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, background='white')
        self.master.title('ERP Prototype')
        self.master.iconphoto(self.master, tk.PhotoImage(file='img\logo.png'))
        self.master.geometry('+25+5') #('1050x600+50+50')

        self.parts_list = []

        self.create_frames()
        configure_frames(self)  #Configures the frames in Main_Application, padding, relief, color, etc.
        configure_widgets(self) #Configures all widgets and their children with padding, color, font
        self.configure(background='lightgrey')



    def create_frames(self):
        self.title1 = Title_Frame(self, 'Built with tkinter')
        self.buttons_frame = Buttons_Frame(self)
        self.job_summary_frame = Job_Summary_Frame(self)
        self.job_image_frame = Image_Frame(self, 'img/assembly-REV-A.png')
        self.parts_list_frame = Parts_List_Frame(self)
        self.material_list_frame = Material_List_Frame(self)
        self.job_checklist_frame = Job_Checklist_Frame(self)
        self.graph = Bar_Graph(self)
        self.parts_frame = Parts_Frame(self)
        self.estimated_deliveries_frame = Estimated_Deliveries_Frame(self)

        #Column 0
        self.title1.grid(row=0, column=0, sticky=tk.NSEW, columnspan=2)
        self.buttons_frame.grid(row=1, column=0, sticky=tk.NSEW)
        self.job_summary_frame.grid(row=2, column=0, sticky=tk.NSEW)
        self.job_image_frame.grid(row=3, column=0, sticky=tk.NSEW)
        #Column1
        self.job_checklist_frame.grid(row=1, column=1, sticky=tk.NSEW, rowspan=2)
        self.estimated_deliveries_frame.grid(row=3, column=1, sticky=tk.NSEW)
        #Column2
        self.parts_list_frame.grid(row=0, column=2, sticky=tk.NSEW, rowspan=2)
        self.material_list_frame.grid(row=2, column=2, sticky=tk.NSEW)
        self.graph.grid(row=3, column=2, sticky=tk.NSEW)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)
        #column3
        self.parts_frame.grid(row=0, column=3, sticky=tk.NSEW, rowspan=5)
        self.parts_frame.rowconfigure(0, weight=0)


    def add_tooltips(self, children):
        '''recursive function to add a tooltip to all widgets'''
        for child in children:
            tooltip.create_ToolTip(child, child.winfo_name())
            if len(child.winfo_children()) > 0:
                self.add_tooltips(child.winfo_children())

    def add_part(self, part_title, event=None):
        self.part_router = Part_Router(self.parts_frame, part_title)
        self.parts_list.append(self.part_router)

    def open_part(self, item, event=None):
        if item != ():
            if len(self.parts_frame.grid_slaves()) > 1:
                self.parts_frame.grid_slaves()[0].grid_remove()
            self.parts_list[item[0]].grid(row=1, column=0, sticky=tk.N)
            self.parts_frame.focus_set()

class Title_Frame(tk.Frame):
    def __init__(self, master, title):
        tk.Frame.__init__(self, master)
        self.img = tk.PhotoImage(file='img/logo.png')
        self.img_label = ttk.Label(self, image=self.img)
        self.title = ttk.Label(self, text=title, font=TITLE_FONT)
        self.img_label.grid(row=0, column=0, sticky=tk.W)
        self.title.grid(row=0, column=1, sticky=tk.W)

class Entry_Bar(tk.Frame):
    '''Basic label and entry bar, grided horizontally'''
    def __init__(self, master, text):
        tk.Frame.__init__(self, master)
        self.entry_label = ttk.Label(self, text=text, width=12)
        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(self, width=12, text=self.entry_var)

        self.entry_label.grid(row=0, column=0, sticky=tk.W)
        self.entry.grid(row=0, column=1, sticky=tk.W)

class Job_Summary_Frame(tk.Frame):
    '''This is where the basic information for the job goes'''
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.title = tk.Label(self, text='Job Summary', font=TITLE_FONT)
        self.title.grid(row=0, column=0, sticky=tk.W)
        self.entry_bars = []
        self.item_names = ['Job Number', 'Description', 'Client', 'Quantity',
                           'Cost', 'Delivery Date', 'Status']
        for item in self.item_names:
            self.entry_bars.append(Entry_Bar(self, item))

        for i, entry_bar in enumerate(self.entry_bars):
            entry_bar.grid(row=i+1, column=0, sticky=tk.W)

class Job_Checklist_Frame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.title = tk.Label(self, text='Checklist', font=TITLE_FONT)
        self.title.grid(row=0, column=0, sticky=tk.W)
        self.row = 1
        self.task_list = ['Confirmation', 'Material Requisition', 'Purchase',
                          'Job Released']
        self.task_objects = []

        self.create_tasks(self.task_list)

    def create_tasks(self, tasks):
        for task in tasks:
            self.task = Job_Checklist_Task(self, task)
            self.task_objects.append(self.task)
            self.task.grid(row=self.row, column=0, sticky=tk.NSEW)
            self.row += 1

class Job_Checklist_Task(tk.Frame):
    def __init__(self, master, text):
        tk.Frame.__init__(self, master)
        self.configure(relief=tk.GROOVE, bd=2)
        self.style = ttk.Style()
        self.style.configure('my.TCheckbutton', font=LABEL_FONT_BOLD)
        self.widget_width = 14
        self.var = tk.IntVar()
        self.check = ttk.Checkbutton(self, text=text, variable=self.var, command=self.on_select, width=self.widget_width, style='my.TCheckbutton')
        self.create_combobox()
        self.status_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.status_label = tk.Label(self, textvariable=self.status_var)
        self.date_label = tk.Label(self, textvariable=self.date_var)

        self.check.grid(row=0, column=0, sticky=tk.W)
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        self.combobox.grid(row=1, column=0, sticky=tk.W)
        self.date_label.grid(row=1, column=1, sticky=tk.W)

        self.on_select()


    def create_combobox(self):
        self.combobox_var = tk.StringVar()
        self.combobox = ttk.Combobox(self, width=self.widget_width, textvariable=self.combobox_var)
        self.combobox.configure(state='readonly')
        self.combobox['values'] = ['Paul tempsdniaser', 'Bob', 'Jacqueline', 'Chuck Norris']
        self.combobox.current(0)

    def on_select(self):
        if self.var.get() == 1:
            self.status_var.set('DONE')
            self.status_label.config(background='green')
            self.now = datetime.datetime.now()
            self.date_var.set('{}/{}/{}'.format(self.now.year, self.now.month, self.now.day))
        if self.var.get() == 0:
            self.status_var.set(' - ')
            self.status_label.config(background='white')
            self.now = None
            self.date_var.set('----/--/--')

class Image_Frame(tk.Frame):
    def __init__(self, master, imagefile):
        tk.Frame.__init__(self, master)
        self.title = tk.Label(self, text='Drawing', font=TITLE_FONT)
        self.title.grid(row=0, column=0, sticky=tk.W, columnspan=3)
        self.imagefile = imagefile
        self.img = Image.open(imagefile)
        maxsize = (150, 150)
        self.img = self.img.resize(maxsize)
        self.create_buttons()
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.img_label = tk.Label(self, image=self.tk_img)
        self.img_label.grid(row=2, column=0, sticky=tk.W, columnspan=3)
        self.filename_label = tk.Label(self, text=self.imagefile)
        self.filename_label.grid(row=3, column=0, sticky=tk.W, columnspan=3)

    def create_buttons(self):
        self.button_open = ttk.Button(self, text='Open', width=6, command=self.open_image)
        self.button_import = ttk.Button(self, text='Import', width=6, command=self.import_image)
        self.button_folder = ttk.Button(self, text='Folder', width=6, command=self.open_folder)

        self.button_open.grid(row=1, column=0, sticky=tk.W)
        self.button_import.grid(row=1, column=1, sticky=tk.W)
        self.button_folder.grid(row=1, column=2, sticky=tk.W)

    def open_image(self):
        dirname = os.path.dirname(__file__)
        filepath = os.path.join(dirname, self.imagefile)
        os.startfile(filepath)

    def import_image(self):
        pass

    def open_folder(self):
        dirname = os.path.dirname(__file__)
        os.startfile(dirname)

class Buttons_Frame(tk.Frame):
    '''Save, load, print, etc... buttons'''
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.button1 = ttk.Button(self, text='Save', width=12)
        #self.button2 = ttk.Button(self, text='Print', width=5)
        self.button3 = ttk.Button(self, text='Print', width=12, command=self.print_summary)
        self.button4 = ttk.Button(self, text='Soumission', width=12, command=self.price_quotation)
        self.button5 = ttk.Button(self, text='Confirmation', width=12, command=self.order_confirmation)

        self.button1.grid(row=0, column=0, sticky=tk.W)
        #self.button2.grid(row=0, column=1, sticky=tk.W)
        self.button3.grid(row=0, column=1, sticky=tk.W)
        self.button4.grid(row=1, column=0, sticky=tk.W)
        self.button5.grid(row=1, column=1, sticky=tk.W)

    def print_summary(self):
        '''prints the data contained in the job_summary_frame'''
        widget_list = self.master.job_summary_frame.entry_bars
        for widget in widget_list:
            widget_name = widget.entry_label['text']
            widget_entry = widget.entry.get()
            print(widget_name + ' ' + widget_entry)

    def price_quotation(self):
        pdf_file = 'Quote.pdf'
        order_confirmation = pdf_reports.Price_Quotation(pdf_file)

    def order_confirmation(self):
        pdf_file = 'Order Confirmation.pdf'
        order_confirmation = pdf_reports.Order_Confirmation(pdf_file)


class Parts_List_Frame(tk.Frame):
    '''This will display the parts list'''
    def __init__(self, master):
        tk.Frame.__init__(self, master, background=COLOR1)
        self.master = master
        self.title = tk.Label(self, text='Parts List', font=TITLE_FONT)
        self.button_frame = tk.Frame(self)
        self.listbox_frame = tk.Frame(self)

        self.title.grid(row=0, column=0, sticky=tk.W)
        self.button_frame.grid(row=1, column=0, sticky=tk.W)
        self.listbox_frame.grid(row=2, column=0, sticky=tk.NSEW)

        self.create_listbox()
        self.create_buttons()


    def create_listbox(self):
        self.scrollbar = tk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(self.listbox_frame, yscrollcommand=self.scrollbar.set) #, selectmode=EXTENTED)
        self.listbox.config(height=7)
        self.scrollbar.config(command=self.listbox.yview)


        self.listbox.grid(row=0, column=0, sticky=tk.NSEW)
        self.scrollbar.grid(row=0, column=1, sticky=tk.NS)

        self.listbox.bind("<<ListboxSelect>>", self.open_part)

    def create_buttons(self):
        self.button_new = ttk.Button(self.button_frame, text='New Part', width='8', command=self.insert_part)
        self.button_del = ttk.Button(self.button_frame, text='Delete', width='6', command=self.delete_part)
        self.button_bulk = ttk.Button(self.button_frame, text='Bulk Entry', width='9', command=self.bulk_entry)
        self.part_number = tk.StringVar()
        self.part_number_entry = tk.Entry(self.button_frame, textvariable=self.part_number)


        self.button_new.grid(row=0, column=0, sticky=tk.W)
        self.button_del.grid(row=0, column=1, sticky=tk.W)
        self.button_bulk.grid(row=0, column=2, sticky=tk.W)
        self.part_number_entry.grid(row=1, column=0, sticky=tk.W, columnspan=3)

        self.part_number_entry.bind('<Return>', self.insert_part)

    def insert_part(self, event=None):
        if len(self.part_number.get()) > 0:
            self.listbox.insert(tk.END, self.part_number.get())
        self.master.add_part(self.part_number.get())

    def delete_part(self):
        item = self.listbox.curselection()
        self.listbox.delete(item)
        self.listbox.select_set(0)
        self.master.parts_list[item[0]].destroy()
        del(self.master.parts_list[item[0]])

    def open_part(self, event=None):
        item = self.listbox.curselection()
        self.master.open_part(item)

    def bindings(self):
        '''Create all keyboard and mouse bindings here'''
        pass

    def bulk_entry(self):
        Parts_List_Bulk_Entry(self)

class Material_List_Frame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.title = tk.Label(self, text='Material', font=TITLE_FONT)
        self.title.grid(row=0, column=0, sticky=tk.W)
        self.row = 1

        self.create_buttons()
        self.create_labels()
        self.row1 = Material_Row(self, 'Steel 1010', 'part-01', 0)
        self.row2 = Material_Row(self, 'Washer 3/4', 'part-08', 1)
        self.row3 = Material_Row(self, 'Custom Screw', 'part-12', 2)
        self.row1.grid(row=self.row, column=0, sticky=tk.W, columnspan=3)
        self.row2.grid(row=self.row+1, column=0, sticky=tk.W, columnspan=3)
        self.row3.grid(row=self.row+2, column=0, sticky=tk.W, columnspan=3)

    def create_buttons(self):
        self.material_list_button = ttk.Button(self, text='Open List')

        self.material_list_button.grid(row=self.row, column=0, sticky=tk.W)
        self.row +=1

    def create_labels(self):
        self.label_missing_material = ttk.Label(self, text="What's Missing?", font=LABEL_FONT_BOLD)
        self.label_missing_material.grid(row=self.row, column=0, sticky=tk.W)
        self.row +=1

        self.label_part = ttk.Label(self, text='Part', font=LABEL_FONT, width=8, anchor=tk.W)
        self.label_material = ttk.Label(self, text='Material', font=LABEL_FONT, width=12, anchor=tk.W)
        self.label_status = ttk.Label(self, text='Status', font=LABEL_FONT, width=8, anchor=tk.W)

        self.label_part.grid(row=self.row, column=1, sticky=tk.W)
        self.label_material.grid(row=self.row, column=0, sticky=tk.W)
        self.label_status.grid(row=self.row, column=2, sticky=tk.W)
        self.row +=1

class Material_Row(tk.Frame):
    def __init__(self, master, material, part, status=0):
        tk.Frame.__init__(self, master)
        self.check_var = tk.IntVar()
        self.material_check = ttk.Checkbutton(self, text=material, variable=self.check_var, command=self.on_select, width=12)
        self.part_label = ttk.Label(self, text=part, font=LABEL_FONT, width=8, anchor=tk.W)
        self.status_combobox = ttk.Combobox(self, text=material, font=LABEL_FONT, width=8, state='readonly')
        self.status_combobox['values'] = ['Not Ordered', 'RFQ', 'Ordered', 'Received']
        self.status_combobox.current(status)
        self.status_combobox.unbind_class("TCombobox", "<MouseWheel>")


        self.material_check.grid(row=0, column=0, sticky=tk.W)
        self.part_label.grid(row=0, column=1, sticky=tk.W)
        self.status_combobox.grid(row=0, column=2, sticky=tk.W)

    def on_select(self):
        if self.check_var.get() == 1:
            self.destroy()

class Parts_Frame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, width=500, height=700)
        self.grid_propagate(0)  #Do not resize frame
        self.columnconfigure(0, weight=5)
        self.rowconfigure(0, weight=5)
        self.title = tk.Label(self, text='Part Process Sheet', font=TITLE_FONT)
        self.title.grid(row=0, column=0, sticky=tk.NW)

class Part_Router(tk.Frame):
    '''Part router containing the manufacturing steps, delays, material, processes,etc...'''
    def __init__(self, master, part_title):
        tk.Frame.__init__(self, master)
        self.title = tk.Label(self, text=part_title, font=TITLE_FONT)
        self.title.grid(row=0, column=0, sticky=tk.W)
        self.row = 1
        self.task_objects = []

        self.image = Image_Frame(self, 'img/part-REV-B-2018-03-18.jpg')
        self.image.grid(row=self.row, column=1)
        self.create_part_attributes()
        self.create_buttons()
        self.new_task()

    def create_part_attributes(self):
        self.attributes_frame = tk.Frame(self)
        self.attributes_frame.grid(row=self.row, column=0, sticky=tk.W)
        self.entry_bars = []
        self.item_names = ['Part Number', 'Description', 'Quantity', 'Material',
                           'Cost', 'Status', 'Hours', 'Dimension', ]
        for item in self.item_names:
            self.entry_bars.append(Entry_Bar(self.attributes_frame, item))

        for i, entry_bar in enumerate(self.entry_bars[0:4]):
            entry_bar.grid(row=i, column=0, sticky=tk.W)
        for i, entry_bar in enumerate(self.entry_bars[4:]):
                entry_bar.grid(row=i, column=1, sticky=tk.W)
        self.row +=1


    def create_buttons(self):
        self.buttons_frame = tk.Frame(self)
        self.button_new = ttk.Button(self.buttons_frame, text='New Task', command=self.new_task)
        self.button_del = ttk.Button(self.buttons_frame, text='Delete', command=self.delete_task)
        self.button_toggle_text = ttk.Button(self.buttons_frame, text='Hide Text', command=self.toggle_text)
        self.button_template1 = ttk.Button(self.buttons_frame, text='Template 1', command=self.process_template)

        self.buttons_frame.grid(row=self.row, column=0, sticky=tk.W)
        for i, button in enumerate(self.buttons_frame.winfo_children()):
            button.grid(row=self.row, column=i, sticky=tk.W)
        self.row +=1

    def new_task(self):
        self.task = Part_Task(self)
        self.task.grid(row=self.row, column=0, sticky=tk.W, padx=5, pady=5, columnspan=2)
        self.task_objects.append(self.task)
        self.row += 1

    def delete_task(self):
        self.grid_slaves()[0].destroy()
        self.task_objects.pop()

    def toggle_text(self):
        '''toggles the text box from the all instances of Part_Task.text'''
        if self.button_toggle_text['text'] == 'Hide Text':
            self.button_toggle_text.configure(text='Show Text')
            for task in self.task_objects:
                task.hide_text_box()

        elif self.button_toggle_text['text'] == 'Show Text':
            self.button_toggle_text.configure(text='Hide Text')
            for task in self.task_objects:
                task.show_text_box()

    def process_template(self):
        while len(self.task_objects) > 0:
            self.delete_task()
        self.load_task(0, 0, 0.5)
        self.load_task(0, 1, 3)
        self.load_task(1, 0, 5)
        self.load_task(3, 0, 1)
        self.load_task(4, 0, 1)


    def load_task(self, box1_index, box2_index, time):
        self.new_task()
        self.task.box1.current(box1_index)
        self.task.box_update()
        self.task.box2.current(box2_index)
        self.task.hours_spinbox.delete(0, "end")
        self.task.hours_spinbox.insert(0, time)

class Part_Task(tk.Frame):
    '''Creates a part task which contains the department, task name, and time'''
    def __init__(self, master):
        tk.Frame.__init__(self, master, class_='Part_Task')
        self.config(highlightbackground="black", highlightcolor="black", highlightthickness=1)
        #self.config(borderwidth=10, relief="flat", background='grey')
        self.tasks = {'Methods':['Planning', 'Programming'],
                      'Machining': ['Lathe', '5-axis mill', '3-axis mill'],
                      'Sub-contracting': ['JobShop', 'MechantMachinage', 'MachinMachine', 'ToolShop'],
                      'Surface Treatment': ['Black Oxyde', 'Hard Anodize'],
                      'Inspection': ['Manual Inspection', 'CMM Inspection']}
        self.create_task()
        self.create_spinbox()
        self.create_textbox()

    def create_combobox(self, combobox_values):
        self.combobox_var = tk.StringVar()
        self.combobox = ttk.Combobox(self, width=20, textvariable=self.combobox_var)
        self.combobox.configure(state='readonly')
        self.combobox['values'] = combobox_values
        self.combobox.current(0)
        return self.combobox, self.combobox_var

    def create_task(self):
        self.box1, self.box1_var = self.create_combobox(list(self.tasks))
        self.box2, self.box2_var = self.create_combobox(self.tasks[self.box1_var.get()])
        self.box1.bind("<<ComboboxSelected>>", self.box_update)
        self.box1.grid(row=0, column=0, sticky=tk.W)
        self.box2.grid(row=0, column=1, sticky=tk.W)

    def box_update(self, event=None):
        self.box2['values'] = self.tasks[self.box1_var.get()]
        self.box2.current(0)

    def create_spinbox(self):
        '''Enter task hours here'''
        self.hours = tk.Label(self, text='heures')
        self.hours_spinbox = tk.Spinbox(self, from_=0, to=100000, increment=.25, format='%.2f')
        self.hours_spinbox.config(width=6)
        self.hours_spinbox.selection_clear()
        self.hours.grid(row=0, column=2, sticky=tk.W)
        self.hours_spinbox.grid(row=0, column=3, sticky=tk.W)

    def create_textbox(self):
        self.text_state = 'SHOWN'
        self.text = ScrolledText(self, width=50, height=5)
        self.text.config(borderwidth=3, relief="sunken", background='lightgrey')
        self.text.grid(row=1, column=0, columnspan=4, sticky='nsew')
        self.toggle_button = ttk.Button(self, text='hide', command=self.toggle_text_box)
        self.toggle_button.grid(row=0, column=4, sticky=tk.W)

    def toggle_text_box(self):
        if self.text_state == 'SHOWN':
            self.text_state = 'HIDDEN'
            try:
                self.text.grid_remove()
            except:
                print('did not remove')
        elif self.text_state == 'HIDDEN':
            self.text_state = 'SHOWN'
            try: self.text.grid()
            except: print('Did not add grid')

    def hide_text_box(self):
        self.text.grid_remove()
        self.text_state = 'HIDDEN'

    def show_text_box(self):
        self.text.grid()
        self.text_state = 'SHOWN'

class Parts_List_Bulk_Entry(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.title('Parts List Bulk Entry')
        self.title_label = tk.Label(self, text='Parts List Bulk Entry', font=TITLE_FONT)
        self.buttons_frame = tk.Frame(self)
        self.auto_entry_frame = tk.Frame(self)
        self.header_row = Bulk_Entry_Row(self)
        self.entries_frame = Scrollable_Frame(self)

        self.title_label.grid(row=0, column=0, sticky=tk.W)
        self.buttons_frame.grid(row=1, column=0, sticky=tk.W)
        self.auto_entry_frame.grid(row=2, column=0, sticky=tk.W)
        self.header_row.grid(row=3, column=0, sticky=tk.W)
        self.entries_frame.grid(row=4, column=0, sticky=tk.W)

        self.row_objects = []
        self.row = 0

        self.create_buttons()
        self.create_auto_entries()
        self.header_row.create_column_titles()

    def create_buttons(self):
        self.button = ttk.Button(self.buttons_frame, text="Exit", command=self.destroy)
        self.button_new_row = ttk.Button(self.buttons_frame, text="New Row", command=self.new_row)
        self.button_delete_row = ttk.Button(self.buttons_frame, text="Delete", command=self.delete_row)
        self.button_paste = ttk.Button(self.buttons_frame, text="Paste", command=self.paste_from_clipboard)


        self.button.grid(row=0, column=0, sticky=tk.W)
        self.button_new_row.grid(row=0, column=1, sticky=tk.W)
        self.button_delete_row.grid(row=0, column=2, sticky=tk.W)
        self.button_paste.grid(row=0, column=3, sticky=tk.W)

    def create_auto_entries(self):
        '''This will create the interface to enter the data to generate a bunch of parts'''
        self.part_number_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.drawing_number_var = tk.StringVar()

        self.part_number_label = tk.Label(self.auto_entry_frame, text='Part Number')
        self.part_number = tk.Entry(self.auto_entry_frame, textvariable=self.part_number_var)
        self.quantity_label = tk.Label(self.auto_entry_frame, text='Quantity')
        self.quantity = tk.Entry(self.auto_entry_frame, textvariable=self.quantity_var)
        self.drawing_number_label = tk.Label(self.auto_entry_frame, text='Drawing Number')
        self.drawing_number = tk.Entry(self.auto_entry_frame, textvariable=self.drawing_number_var)

        self.generate_button = ttk.Button(self.auto_entry_frame, text='Generate', command=self.generate_parts)


        grid_all_widgets(self.auto_entry_frame)



    def new_row(self):
        self.entry_row = Bulk_Entry_Row(self.entries_frame.frame)
        self.entry_row.grid(row=self.row, column=0, sticky=tk.W)
        self.entry_row.create_entries()
        self.entries_frame.bind_mouse_wheel(self.entry_row) #Bind widgets to enable scrolling
        self.row +=1

    def delete_row(self):
        self.entries_frame.frame.winfo_children()[-1].destroy()
        self.row -=1

    def generate_parts(self):
        part_number = self.part_number_var.get()
        qty = int(self.quantity_var.get())
        drawing = self.drawing_number_var.get()

        for i in range(qty):
            self.new_row()
            self.entry_row.entry1_var.set(part_number + '-'+str(i+1))
            self.entry_row.entry5_var.set(drawing)

    def paste_from_clipboard(self):
        self.part_number_var.set('170888')
        self.quantity_var.set('30')
        self.drawing_number_var.set('878A234FFGT')

        part_number = self.part_number_var.get()
        qty = int(self.quantity_var.get())
        drawing = self.drawing_number_var.get()

        for i in range(qty):
            self.new_row()
            self.entry_row.entry1_var.set(part_number + '-'+str(i+1))
            self.entry_row.entry2_var.set('Part ' + str(i+1))
            self.entry_row.entry3_var.set('1')
            self.entry_row.entry4_var.set('Acier 1020')
            self.entry_row.entry5_var.set(drawing)

class Scrollable_Frame(tk.Frame):
    # https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter/3092341#3092341
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.canvas = tk.Canvas(self, borderwidth=0, background="#e6e6e6") #ffffff
        self.canvas.configure(width=1000, height=500)
        self.frame = tk.Frame(self.canvas, background="#e6e6e6")
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.grid(row=0, column=1, sticky=tk.NS)
        self.canvas.grid(row=0, column=0, sticky=tk.W)
        self.canvas.create_window(0, 0, window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        #up-down key scrolling
        self.canvas.bind("<Up>",    lambda event: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Down>",  lambda event: self.canvas.yview_scroll( 1, "units"))
        self.bind_mouse_wheel(self.canvas) #mousewheel scrolling

        self.canvas.focus_set()


    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def mouse_wheel(self, event):
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            self.canvas.yview_scroll(1, "units")
        if event.num == 4 or event.delta == 120:
            self.canvas.yview_scroll(-1, "units")

    def bind_mouse_wheel(self, widget):
        '''Bind all widgets and their children inside the frame to allow scrolling'''
        try:
            widget.bind("<MouseWheel>", self.mouse_wheel) #Windows
            widget.bind("<Button-4>", self.mouse_wheel) # Linux, OS
            widget.bind("<Button-5>", self.mouse_wheel) # Linux, OS
            if len(widget.winfo_children()) > 0:
                for child in widget.winfo_children():
                    self.bind_mouse_wheel(child)

        except:
            pass

class Bulk_Entry_Row(tk.Frame):
    # https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter/3092341#3092341
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.titles = ['Part Number', 'Description', 'Quantity', 'Material', 'Drawing']
        self.width= 15

    def create_entries(self):
        self.entry1_var = tk.StringVar()
        self.entry2_var = tk.StringVar()
        self.entry3_var = tk.StringVar()
        self.entry4_var = tk.StringVar()
        self.entry5_var = tk.StringVar()
        self.entry1 = tk.Entry(self, textvariable=self.entry1_var, width=self.width, font=LABEL_FONT)
        self.entry2 = tk.Entry(self, textvariable=self.entry2_var, width=self.width, font=LABEL_FONT)
        self.entry3 = tk.Entry(self, textvariable=self.entry3_var, width=self.width, font=LABEL_FONT)
        self.entry4 = tk.Entry(self, textvariable=self.entry4_var, width=self.width, font=LABEL_FONT)
        self.entry5 = tk.Entry(self, textvariable=self.entry5_var, width=self.width, font=LABEL_FONT)
        grid_all_widgets(self)
        configure_widgets(self)

    def create_column_titles(self):
        '''Part Number, description, quantity, material, drawing'''
        self.size = 24
        self.label1 = tk.Label(self, text='Part Number', width=self.width, anchor=tk.W, font=TITLE_FONT)
        self.label2 = tk.Label(self, text='Description', width=self.width, anchor=tk.W, font=('Droid', self.size))
        self.label3 = tk.Label(self, text='Quantity', width=self.width, anchor=tk.W, font=('Droid', self.size))
        self.label4 = tk.Label(self, text='Material', width=self.width, anchor=tk.W, font=('Droid', self.size))
        self.label5 = tk.Label(self, text='Drawing', width=self.width, anchor=tk.W, font=('Droid', self.size))
        grid_all_widgets(self)
        configure_widgets(self)

class Bar_Graph(tk.Frame):
    def __init__(self, master, ):
        tk.Frame.__init__(self, master)
        self.title = tk.Label(self, text='Job Profitability', font=TITLE_FONT)
        self.title.grid(row=0, column=0, sticky=tk.W)
        self.row = 1
        self.create_buttons()
        self.create_chart()

    def create_buttons(self):
        self.button1 = ttk.Button(self, text='Details', width=10, command=self.details)
        self.button2 = ttk.Button(self, text='Report', width=10, command=self.report)


        self.button1.grid(row=self.row, column=0, sticky=tk.W)
        self.button2.grid(row=self.row, column=1, sticky=tk.W)
        self.row += 1

    def create_chart(self):
        self.objects = ['Part-01', 'Part-02', 'Part-03', 'Part-04', 'Part-05', 'Part-06']
        self.y_pos = np.arange(len(self.objects))
        self.profit = [65,110,25,88,92,100]

        self.fig = Figure(figsize=(2,2), facecolor='white', dpi=100)
        self.axis = self.fig.add_subplot(111) #1 row, 1 column

        self.axis.barh(self.y_pos, self.profit, .8, align='center', alpha=0.5, )
        self.axis.set_yticks(self.y_pos)
        self.axis.set_yticklabels(self.objects)
        self.axis.set_xlabel('Profit')
        #self.axis.set_title('Job Profitability')

        for i, percent in enumerate(self.profit):
            self.axis.text(1,i,s=str(percent)+'%', horizontalalignment='left', verticalalignment='center',
                           color='blue',weight='bold', clip_on=True)
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=self.row, column=0, sticky=tk.NSEW, columnspan=2)
        self.row +=1

    def details(self):
        pass

    def report(self):
        pass

class Estimated_Deliveries_Frame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.title = tk.Label(self, text='Estimated Delivery Dates', font=TITLE_FONT)
        self.title.grid(row=0, column=0, sticky=tk.W, columnspan=3)
        self.row = 1
        self.delivery_date = datetime.date(2018,4,21)
        self.parts_list = { 'Part-01': datetime.date(2018,4,18),
                            'Part-02':datetime.date(2018,4,17),
                            'Part-03':datetime.date(2018,4,22),
                            'Part-04':datetime.date(2018,4,28),
                            'Part-05':datetime.date(2018,4,17),
                            'Part-06':datetime.date(2018,4,21)
                            }

        self.create_buttons()
        self.create_part_estimated_delivery('Project', datetime.date(2018,4,28), font=('Droid', 12, 'bold'))
        for part, date in self.parts_list.items():
            self.create_part_estimated_delivery(part, date)

    def create_buttons(self):
        self.button1 = ttk.Button(self, text='Gantt Chart', width=10, command=self.gantt_chart)
        self.button2 = ttk.Button(self, text='Report', width=10, command=self.report)


        self.button1.grid(row=self.row, column=0, sticky=tk.W)
        self.button2.grid(row=self.row, column=1, sticky=tk.W)
        self.row += 1

    def create_part_estimated_delivery(self, partname, date, font=LABEL_FONT):
        self.day_count = (date - self.delivery_date).days
        if date <= self.delivery_date:
            self.status = 'green'
        else:
            self.status = 'red'

        self.label1 = tk.Label(self, text=partname, font=font, fg='blue')
        self.delivery_label = tk.Label(self, text=date, font=font)
        self.status_label = tk.Label(self, text=str(self.day_count) + ' days', font=font, fg=self.status)

        self.label1.grid(row=self.row, column=0, sticky=tk.W)
        self.delivery_label.grid(row=self.row, column=1, sticky=tk.W)
        self.status_label.grid(row=self.row, column=2, sticky=tk.W)

        self.row += 1

    def status_check(self):
        pass

    def gantt_chart(self):
        os.startfile('gantt-chart.html')

    def report(self):
        pass



def grid_all_widgets(frame, horizontal=1, vertical=0):
    '''1 or nothing for horizontal'''
    if horizontal == 1:
        for i, widget in enumerate(frame.winfo_children()):
            widget.grid(row=0, column=i, sticky=tk.W, padx=10)
            try: widget.config(justify=tk.LEFT, font=LABEL_FONT)
            except: pass

    else:
        for i, widget in enumerate(frame.winfo_children()):
            widget.grid(row=i, column=0, sticky=tk.W)

def add_padding(frame):
    '''DO NOT USE, use configure_widgets instead
    recursive funtion to loop through all the layers of frames and widgets'''
    slaves = frame.winfo_children()
    for slave in slaves:
        print(slave.widgetName)
        if slave.widgetName == 'frame':
            slave.configure(highlightbackground="black", highlightcolor="black", highlightthickness=1) #For testing
            slave.grid_configure(padx=FRAME_PADDING[0], pady=FRAME_PADDING[1])
        else:
            slave.grid_configure(padx=WIDGET_PADDING[0], pady=WIDGET_PADDING[1])

        if len(slave.winfo_children()) > 0:
            frame.add_padding(slave)

def configure_frames(mainframe):
    '''Configure the frames only. Padding and relief style, as well as color'''
    frames = mainframe.winfo_children()
    for frame in frames:
        if frame.widgetName == 'frame':
            #frame.configure(highlightbackground="black", highlightcolor="black", highlightthickness=1) #For testing
            frame.configure(bd=2, relief=tk.RAISED)
            frame.grid_configure(padx=FRAME_PADDING[0], pady=FRAME_PADDING[1])


def configure_widgets(widget):
    '''Configure all widgets and their children. Adds styles, colors, padding, etc...'''
    try:
        widget.grid_configure(padx=WIDGET_PADDING[0], pady=WIDGET_PADDING[1])
        widget.configure(background='white')

        #if widget.widgetName == 'frame': widget.configure(bd=1, relief=tk.SOLID) #For testing

        if len(widget.winfo_children()) > 0:
            for child in widget.winfo_children():
                configure_widgets(child)

    except:
        pass


if __name__ == '__main__':
    root = tk.Tk()
    app = Main_Application(root)
    app.grid(row=0, column=0, sticky=tk.W)
    root.mainloop()
