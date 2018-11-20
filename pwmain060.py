# !/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Simple and comprehensive password management solution.

Classes:
-RecordManager
-Security
-DeveloperOptions
-WindowManager
-Windows

Usage example:
>>> wm = WindowManager()
>>> wm.startup()
"""

import platform
from threading import Lock
from tkinter import ttk

from ttkthemes import themed_tk as thk

from recordmanager import *
from security import *

"""
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Nicholas De Villiers"
__copyright__ = "Copyright (C) 2018 Nicholas De Villiers"
__license__ = "Public Domain"
__version__ = "0.6β"

# Changes from v0.5.2β:
# -New main screen (shows records straight away)
# -Ability to go between pages (main records and login records)
# -Ability to alter number of records shown per page
# -Added page number and records shown indicator
# -Added menu bar to main window
# -No more tools window (all tools available as menu bar options)
# -Added preferences window
# -Enhanced record adding/edting (changes are displayed immediately)
# -Ability to log out without closing program
# -Option to manually save changes
# -Prompt to save changes if autosave hasn't saved already when exiting
# -User given ability to clear all app data
# -All Tkinter windows converted to classes
# -Improved PEP8 conformity
# -Added window displaying copyright notices


INFO_BOX_TITLE = "Information"
ERROR_BOX_TITLE = "Error"
WARNING_TITLE = "Warning"


class WindowManager:
    """
    Class to manage window actions.

    Does not take any arguments.

    Functions:
    -edit_button_func(self, search, i, box, searching_text, record_dict, index)
    -close(self, win, record_dict)
    -feature_not_available(self)
    -auto_save_records(self, record_dict, menu)
    -stop_auto_save(self, menu)
    -timeout(self, record_dict, menu)
    -logout(self, menu, record_dict)
    -export(self, choice, subwin, menu, record_dict)

    Usage example:
    >>> manage_win = WindowManager()
    >>> record_dict = manage_records.create_dict()
    >>> menu = Tk()
    >>> menuwin = MainWindow(menuwin, True)
    >>> manage_win.auto_save_records(record_dict, menu)

    """

    def __init__(self):
        # most of these booleans are used for automation processes
        self.gui = GUI(master=None)
        self.stopped = False
        self.autosave_id = None
        self.timeout_id = None
        self.logout_id = None
        self.time_is_up = False
        self.auto_lock = Lock()

    def startup(self):
        """
        Handles the startup process of the program.

        No args taken.

        Usage:
        >>> wm.startup()
        """
        startup_type = secure.startup()
        # sets appropriate theme if run on linux. seen in all other window creations, will not comment those
        if self.gui.system == 'Linux':
            login = thk.ThemedTk()
            login.set_theme('radiance')
        else:
            login = Tk()
        LoginWindow(login, startup_type)
        login.mainloop()

    def log_in(self, password_entry, un_entry, win):
        """
        Handles the login process.

        Args taken:
        -password_entry (Tk entry field)
        -un_entry (Tk entry field)
        -win (Tk window)

        Usage:
        >>> login = Tk()
        >>> loginwin = LoginWindow(login)
        >>> login.mainloop()
        >>> wm.log_in(password_entry, un_entry, login)
        """
        success, admin = secure.log_in(password_entry, un_entry, win)
        if success:
            win.destroy()
            if self.gui.system == 'Linux':
                main = thk.ThemedTk()
                main.set_theme('radiance')
            else:
                main = Tk()
            mainwin = MainWindow(main, admin)
            mainwin.create_table()
            main.mainloop()

    def edit_button_func(self, main, i, box, index):
        """
        Creates the recurring edit button in the "search" window.

        Args taken:
        -search (Tk window "search")
        -box (list of records)
        -i (int - position of record in box)
        -searching_text (str)
        -record_dict (dictionary of records)
        -index (place in record_dict)

        Doesn't need calling outside of search window.
        """
        edit_button = ttk.Button(main.frame, text="Edit", command=lambda: main.edit_record(i, box, index))
        edit_button.grid(row=i + 2, column=0)

    def close(self, win, record_dict):
        """
        Ensures that all records are encrypted when the program is shut
        down. Re-encrypts primary password for added security.

        Args taken:
        -win (Main TK window in program ("new" in this case)

        Usage example:
        >>> manager = WindowManager()
        >>> menu = Tk()
        >>> menuwin = MainWindow(menu, True)
        >>> manager.close(menu, record_dict)

        """
        if manage_records.unsaved_changes:
            result = mb.askyesnocancel("Exit", "Save changes before exiting?", parent=win, icon='warning')
            if result:
                # aquires a process lock to finish saving records. avoids data corruption. will not comment after this
                self.auto_lock.acquire()
                self.stop_auto_save(win)
                manage_records.write_encrypted(record_dict)
                manage_records.db_manager.conn.close()
                win.destroy()
                self.auto_lock.release()
            elif result is False:
                self.auto_lock.acquire()
                self.stop_auto_save(win)
                manage_records.db_manager.conn.close()
                win.destroy()
                self.auto_lock.release()
        else:
            self.auto_lock.acquire()
            self.stop_auto_save(win)
            manage_records.db_manager.conn.close()
            win.destroy()
            self.auto_lock.release()

    def feature_not_available(self):
        """
        Dev function to show messagebox declaring a feature not available.

        Just set button command to this if you need to use it.
        """
        mb.showwarning("Password Manager", "Feature not available yet.")

    def auto_save_records(self, record_dict, menu):
        """
        Begins autosave process in background.

        Args taken:
        -record_dict (dictionary of records)
        -menu (Tk winow "menu")

        Usage:
        >>> winmanage = WindowManager()
        >>> menu = Tk()
        >>> menuwin = MainWindow(menu, True)
        >>> winmanage.auto_save_records(record_dict, menu)
        """
        self.auto_lock.acquire()
        if self.stopped:
            return
            # ends the function if the process is stopped
        manage_records.write_encrypted(record_dict, preserve=True)
        manage_records.unsaved_changes = False
        self.auto_lock.release()
        self.autosave_id = menu.after(int(settings["Preferences"]["autosave time"]) * 1000,
                                      lambda: self.auto_save_records(record_dict, menu))

    def stop_auto_save(self, menu):
        """
        Stops autosave process.

        Args taken:
        -menu (Tk window "menu")

        Usage:
        >>> wm = WindowManager()
        >>> record_dict = manage_records.create_dict()
        >>> menu = Tk()
        >>> menuwin = MainWindow(menu, True)
        >>> wm.auto_save_records(record_dict, menu)
        >>> wm.stop_auto_save(menu)

        """
        self.stopped = True
        # this boolean is used in the function above this. indicates program has stopped
        if self.autosave_id is not None:
            menu.after_cancel(self.autosave_id)

    def timeout(self, record_dict, menu):
        """
        Begins login timeout process in background.

        Args taken:
        -record_dict (dictionary of records)
        -menu (Tk winow "menu")

        Usage:
        >>> winmanage = WindowManager()
        >>> menu = Tk()
        >>> menuwin = MainWindow(menu, True)
        >>> winmanage.timeout(record_dict, menu)
        """
        if self.timeout_id is not None:
            timer = 20000  # time is in milliseconds
            self.logout_id = menu.after(timer, lambda: self.login_expired(menu, record_dict))
            result = mb.askquestion(WARNING_TITLE, "Are you still there?\nYou are being logged out in %d seconds." %
                                    (timer / 1000), icon="warning", parent=menu)
            if result == "yes":
                menu.after_cancel(self.logout_id)
            else:
                self.login_expired(menu, record_dict)
        # below: time is set in seconds in config file, multiplied by 1000 to comply with 'after' method.
        self.timeout_id = menu.after(int(settings["Preferences"]["timeout"]) * 1000,
                                     lambda: self.timeout(record_dict, menu))

    def login_expired(self, menu, record_dict):
        """
        Shuts down program if timeout has reached limit.

        Args taken:
        -menu (Tk winow "menu")
        -record_dict (dictionary of records)

        Usage:
        >>> winmanage = WindowManager()
        >>> menu = Tk()
        >>> menuwin = MainWindow(menu, True)
        >>> winmanage.login_expired(menu, record_dict)
        """
        self.time_is_up = True
        self.close(menu, record_dict)

    def export(self, choice, menu, record_dict):
        """
        Handles the export process for different filetypes.
        
        Args taken:
        -choice (str: 'CSV', 'SQL Database', 'JSON', 'XML', or 'HTML'
        -menu (tk window)
        -record_dict (dictionary)
        
        >>> menu = Tk()
        >>> mainmenu = MainWindow(menu, True)
        >>> wm = WindowManager()
        >>> wm.export('CSV', menu, mainmenu.record_dict)
        """
        option = choice.get()
        if option == "CSV":
            manage_records.export_as_csv(menu, record_dict)
        elif option == "SQL Database":
            manage_records.export_as_sql_db(menu, record_dict)
        elif option == "JSON":
            manage_records.export_as_json(menu, record_dict)
        elif option == "XML":
            manage_records.export_as_xml(menu, record_dict)
        elif option == "HTML":
            manage_records.export_as_html(menu, record_dict)
        else:
            mb.showerror(ERROR_BOX_TITLE, "Please select an option from the list.", parent=menu)

    @staticmethod
    def get_directory(filename):
        """
        Fetches the full system path to a program file.
        
        Args taken:
        -filename (str)
        
        Usage:
        >>> WindowManager.get_directory('data/favicon.png')
        """
        directory = sys.argv[0]
        directory = directory.split('/')
        directory.pop(-1)
        directory = '/'.join(directory)
        directory = directory + '/' + filename
        return directory


class GUI:
    """
    Base class for all windows.

    Subclassed by:
    -MainWindow
    -LoginWindow
    -ForgotPasswordWindow
    -AddRecordWindow
    -EditRecordWindow
    -AccountWindow
    -LoginRecords
    -PassChecker
    -Preferences
    -DevOptionsWindow

    Methods:
    -set_up_window(self)

    Args taken:
    -master (Tkinter Tk or Toplevel)

    Usage:
    >>> root = Tk()
    >>> mygui = GUI(root)
    >>> mygui.set_up_window()
    >>> root.title("My GUI")
    """

    def __init__(self, master):
        # setting variables/constants for all windows
        self.DEFAULT_WIDTH = 308
        self.DEFAULT_HEIGHT = 280
        self.DEFAULT_PAD = 3
        icon_type = 'png'
        self.ICON_PATH = WindowManager.get_directory("data/favicon.%s" % icon_type)
        self.HEADER = "Helvetica 12 bold"
        self.MAIN_TITLE = "Password Manager v%s" % __version__
        self.system = platform.system()
        if self.system == 'Linux':
            self.DEFAULT_HEIGHT += 10
            self.HEADER = "Ubuntu 12 bold"
            self.BGCOL = "#F6F4F2"
        self.dev_options = DeveloperOptions()

        # window rendering applicable to all
        self.master = master

    def set_up_window(self):
        """
        Sets up a window with the default title and icon.

        No args taken.

        Usage:
        >>> root = Tk()
        >>> mygui = GUI(root)
        >>> mygui.set_up_window()
        """
        self.master.title(self.MAIN_TITLE)
        icon = PhotoImage(file=self.ICON_PATH)
        self.master.tk.call('wm', 'iconphoto', self.master, icon)


class MainWindow(GUI):
    """
    Class containing main user interface and management methods.

    Superclassed by GUI.

    Methods:
    -create_table(self)
    -refresh_table(self)
    -create_frame(self)
    -clear_frame(self)
    -load_menubar(self, admin)
    -add_record(self)
    -edit_record(self, i, box, index)
    -search_records_window(self)
    -about_window(self)
    -search_records(self, conditions_list, searching_text, search)
    -show_all(self)
    -save_records(self)
    -clear_records(self)
    -change_account_details(self)
    -view_login_records(self)
    -strength_checker(self)
    -pref_window(self)
    -dev_options_window(self)
    -log_out(self)

    Usage:
    >>> main = Tk()
    >>> maincontent = MainWindow(main, True)
    >>> maincontent.create_table()
    """

    def __init__(self, master, admin):
        super().__init__(master)
        self.set_up_window()
        self.searching_text = StringVar(value="")
        # boolean conditions stored as integer 1 or 0 (below)
        self.conditions = [IntVar(value=1), IntVar(value=1), IntVar(value=1)]
        self.record_dict = manage_records.create_dict()
        self.max_records_shown = int(settings['Preferences']['records displayed'])
        self.lower_bound = 0
        self.upper_bound = self.max_records_shown
        self.page = 1
        # below: default value is 1. will be recalculated if more pages are required.
        self.no_of_pages = 1
        self.admin = admin
        self.dev = DeveloperOptions()
        # below: two different functions needed to create menubar. first one creates bar, second one fills it
        self.menubar = Menu(master)
        self.load_menubar(admin)
        self.frame = None
        if self.system == 'Linux':
            self.master.configure(background=self.BGCOL)
        self.master.protocol('WM_DELETE_WINDOW', lambda: wm.close(self.master, self.record_dict))
        wm.auto_save_records(self.record_dict, self.master)
        if bool(settings["Preferences"]["timeout active"]):
            wm.timeout(self.record_dict, self.master)

    def create_table(self):
        """
        Creates table inside of frame in main window.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow(main, True)
        >>> maincontent.create_table()

        """
        self.create_frame()
        records_shown = []
        box, indices, searched = manage_records.search_dict(self.record_dict, self.searching_text, self.conditions)
        ttk.Label(self.frame, text="Fields searched:").grid(row=0, column=0, sticky=E)
        if len(searched) == 1:
            # fields searched are stored in a list
            searched_str = searched[0]
        elif len(searched) == 2:
            searched_str = "%s, %s" % (searched[0], searched[1])
        elif len(searched) == 3:
            searched_str = "All"
        else:
            searched_str = "None"
        # shows typed search, if applicable
        ttk.Label(self.frame, text=searched_str).grid(row=0, column=1, sticky=W)
        if len(box) > 0:
            # tells user which range of records is being shown
            ttk.Label(self.frame, text='Showing records').grid(row=0, column=2, sticky=E)
            if len(box) >= self.upper_bound:
                highest = self.upper_bound
            else:
                highest = len(box)
            ttk.Label(self.frame, text='%d - %d of %d' % (self.lower_bound + 1, highest, len(box))).grid(row=0,
                                                                                                         column=3,
                                                                                                         sticky=W)
            # field headers
            ttk.Label(self.frame, text="Site", font=self.HEADER).grid(row=1, column=1)
            ttk.Label(self.frame, text="Username", font=self.HEADER).grid(row=1, column=2)
            ttk.Label(self.frame, text="Password", font=self.HEADER).grid(row=1, column=3)

            # if amount of records is less than or equal to the page limit
            if len(box) <= self.max_records_shown:
                for i in range(len(box)):
                    # got index errors from time to time, used this block to break loop if occurred. seems to work
                    try:
                        record = box[i]
                    except IndexError:
                        break
                    index = indices[i]
                    for x in range(1, 4):
                        if x % 3 == 0:
                            wm.edit_button_func(self, i, box, index)
                            # edit button always shown to left of record
                        ttk.Label(self.frame, text=record[x - 1]).grid(row=i + 2, column=x, padx=self.DEFAULT_PAD,
                                                                       sticky=W)
            # if amount of records exceeds page limit
            else:
                for i in range(self.lower_bound, self.upper_bound):
                    # got index errors from time to time, used this block to break loop if occurred. seems to work
                    try:
                        record = box[i]
                    except IndexError:
                        break
                    # list is kept of which records are on display
                    records_shown.append(record)
                    index = indices[i]
                    for x in range(1, 4):
                        if x % 3 == 0:
                            wm.edit_button_func(self, i, box, index)
                            # edit button always shown to left of record
                        ttk.Label(self.frame, text=record[x - 1]).grid(row=i + 2, column=x, padx=self.DEFAULT_PAD,
                                                                       sticky=W)
                # below: buttons for changing pages, and label displaying page number
                # buttons are only shown if there are pages after/before current page. one or both maybe shown
                if self.upper_bound < len(box):
                    ttk.Button(self.frame, text='Next', command=lambda:self.next_page(box)).grid(row=self.upper_bound + 2, column=3)
                if self.page != 1:
                    ttk.Button(self.frame, text='Back', command=self.previous_page).grid(row=self.upper_bound + 2,
                                                                                         column=0)
                if self.max_records_shown < len(box):
                    ttk.Label(self.frame, text='Page').grid(row=self.upper_bound + 2, column=1, sticky=E)
                    self.calculate_page_numbers(box)
                    ttk.Label(self.frame, text=str("%d/%d" % (self.page, self.no_of_pages))).grid(
                        row=self.upper_bound + 2, column=2, sticky=W)
        else:
            # what to do if there are no records
            self.master.geometry("%dx75" % self.DEFAULT_WIDTH)
            ttk.Label(self.frame, text='No records found.').grid(row=1)

    def refresh_table(self):
        """
        Refreshes table in main window.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow(main, True)
        >>> maincontent.create_table()
        >>> maincontent.refresh_table()
        """
        self.clear_frame()
        self.create_table()

    def create_frame(self):
        """
        Draws frame inside main window.

        No args taken

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow(main, True)
        >>> maincontent.create_frame()
        """
        if self.system == 'Linux':
            self.frame = Frame(self.master, bg=self.BGCOL)
            self.frame.grid()
            self.master.configure(background=self.BGCOL)
        else:
            self.frame = Frame(self.master)
            self.frame.grid()

    def clear_frame(self):
        """
        Clears frame in main window.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow(main, True)
        >>> maincontent.create_table()
        >>> maincontent.clear_frame()
        """
        # below: each widget is iterated through one by one and destroyed
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        self.frame = None

    def calculate_page_numbers(self, box):
        """
        Calculates the number of the page currently shown in the main window.

        Args taken:
        -box (list of records)

        Usage handled internally by class.
        """
        self.no_of_pages = (len(box) // self.max_records_shown)
        if (len(box) % self.max_records_shown) > 0:
            self.no_of_pages += 1
            # this bit is needed when records do not perfectly fit onto all pages

    def load_menubar(self, admin):
        """
        Loads the menu bar in the main window.

        Args taken:
        -admin (bool)

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow(main, True)
        >>> maincontent.load_menubar(True)
        """
        # file menu
        file_menu = Menu(self.menubar, tearoff=0)
        export_menu = Menu(self.menubar, tearoff=0)
        export_menu.add_command(label="CSV", command=lambda: wm.export(StringVar(value="CSV"), self.master,
                                                                       self.record_dict))
        export_menu.add_command(label="HTML", command=lambda: wm.export(StringVar(value="HTML"), self.master,
                                                                        self.record_dict))
        export_menu.add_command(label="JSON", command=lambda: wm.export(StringVar(value="JSON"), self.master,
                                                                        self.record_dict))
        export_menu.add_command(label="XML", command=lambda: wm.export(StringVar(value="XML"), self.master,
                                                                       self.record_dict))
        export_menu.add_command(label="SQL Database", command=lambda: wm.export(StringVar(value="SQL Database"),
                                                                                self.master, self.record_dict))
        file_menu.add_cascade(label='Export records', menu=export_menu)
        file_menu.add_command(label="Save", command=self.save_records)
        file_menu.add_command(label="Log out", command=self.log_out)
        file_menu.add_command(label="Exit", command=lambda: wm.close(self.master, self.record_dict))
        file_menu.add_separator()
        file_menu.add_command(label="About...", command=self.about_window)
        self.menubar.add_cascade(label="File", menu=file_menu)

        # records menu
        records_menu = Menu(self.menubar, tearoff=0)
        records_menu.add_command(label="Add record", command=self.add_record)
        records_menu.add_command(label="Clear all records", command=self.clear_records)
        records_menu.add_command(label="Search records", command=self.search_records_window)
        records_menu.add_command(label='Show all', command=self.show_all)
        self.menubar.add_cascade(label='Records', menu=records_menu)

        # account menu
        account_menu = Menu(self.menubar, tearoff=0)
        account_menu.add_command(label="Edit details", command=self.change_account_details)
        account_menu.add_command(label="Delete account", command=self.clear_all_details)
        account_menu.add_command(label="View login records", command=self.view_login_records)
        self.menubar.add_cascade(label='Account', menu=account_menu)

        # tools menu
        tools_menu = Menu(self.menubar, tearoff=0)
        tools_menu.add_command(label="Password strength checker", command=self.strength_checker)
        tools_menu.add_command(label="Preferences", command=self.pref_window)
        backup_menu = Menu(self.menubar, tearoff=0)
        backup_menu.add_command(label="Create backup", command=lambda: manage_records.create_backup(self.master,
                                                                                                    self.record_dict))
        backup_menu.add_command(label="Import backup", command=lambda: manage_records.import_backup(self.master,
                                                                                                    self.record_dict))
        tools_menu.add_cascade(label="Backup", menu=backup_menu)
        if admin:
            # ensures dev options are only shown if user is admin
            tools_menu.add_separator()
            tools_menu.add_command(label="Developer options", command=self.dev_options_window)

        self.menubar.add_cascade(label='Tools', menu=tools_menu)
        self.master.config(menu=self.menubar)

    def add_record(self):
        """
        Handles GUI for adding records.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow(main, True)
        >>> maincontent.create_table()
        >>> maincontent.add_record()
        """
        new = Toplevel()
        AddRecordWindow(new, self.record_dict)
        self.master.wait_window(new)  # interaction with main window disabled until this window is close
        box, indices, searched = manage_records.search_dict(self.record_dict, self.searching_text, self.conditions)
        self.add_more_pages(box)
        self.refresh_table()

    def add_more_pages(self, records):
        # if records have been added
        if self.upper_bound < len(records):
            # if user on last page
            print(self.page, self.no_of_pages)
            if self.page == self.no_of_pages:
                # if more pages are needed
                if self.no_of_pages < len(records) / self.max_records_shown:
                    self.calculate_page_numbers(records)
                else:
                    self.upper_bound = len(records)
            else:
                # if more pages are needed
                if self.no_of_pages < len(records) / self.max_records_shown:
                    self.calculate_page_numbers(records)

    def edit_record(self, i, box, index):
        """
        Handles GUI for editing a record.

        Args taken:
        -i (int)
        -box (list)
        -index (int)

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow(main, True)
        >>> maincontent.create_table()
        >>> maincontent.edit_record(i, box, index)
        """
        edit = Toplevel()
        EditRecordWindow(edit, i, box, self.record_dict, index)
        self.master.wait_window(edit)
        box, indicies, searched = manage_records.search_dict(self.record_dict, self.searching_text, self.conditions)
        self.remove_pages(box)
        self.refresh_table()

    def remove_pages(self, records):
        # if user on the last page
        if self.page == self.no_of_pages:
            # if a page needs to be removed
            print(len(records), self.lower_bound)
            if len(records) <= self.lower_bound:
                self.calculate_page_numbers(records)
                self.page = self.no_of_pages
                self.upper_bound = len(records)
                self.lower_bound = self.max_records_shown * (self.no_of_pages - 1)
        else:
            self.calculate_page_numbers(records)

    def search_records_window(self):
        """
        Creates a Toplevel window to search records.
        
        No args taken.
        
        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow(main, True)
        >>> maincontent.search_records_window()
        """
        search = Toplevel()
        s_width = self.DEFAULT_WIDTH
        s_height = self.DEFAULT_HEIGHT
        search.geometry('%dx%d' % (s_width, s_height))
        if self.system == 'Linux':
            search.configure(background=self.BGCOL)
        ttk.Label(search).pack()
        ttk.Label(search, text="Search Records", font=self.HEADER).pack()

        # search box
        searching_text = StringVar(search, value="")
        search_entry = ttk.Entry(search, textvariable=searching_text)
        search_entry.pack()

        # checkboxes for searching site, username, and password fields
        search_site = IntVar(search)
        search_site.set(1)
        search_site_check = ttk.Checkbutton(search, text="Search site names", variable=search_site)
        search_site_check.pack()

        search_un = IntVar(search)
        search_un.set(1)
        search_un_check = ttk.Checkbutton(search, text="Search usernames", variable=search_un)
        search_un_check.pack()

        search_pw = IntVar(search)
        search_pw.set(1)
        search_pw_check = ttk.Checkbutton(search, text="Search passwords", variable=search_pw)
        search_pw_check.pack()

        # packs checkboxes into a list when parsed to search function
        conditions = [search_site, search_un, search_pw]

        search_button = ttk.Button(search, text='Search', command=lambda: self.search_records(conditions,
                                                                                              searching_text, search))
        search_button.pack()

    def about_window(self):
        """
        Method to show window displaying copyright information.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> maingui = MainWindow(main, False)
        >>> main.mainloop()
        >>> maingui.about_window()
        """
        # Window automatically sizes to text
        about = Toplevel()
        if self.system == 'Linux':
            about.configure(background=self.BGCOL)
        ttk.Label(about, text="Tkinter Password Manager version %s" % __version__, font=self.HEADER,
                  padx=self.DEFAULT_PAD, pady=self.DEFAULT_PAD).pack()
        copyright_file = TextFile("data/copyright.txt")
        copyright_info = copyright_file.read_file(None)
        ttk.Label(about, text=copyright_info).pack()
        ttk.Label(about, text="%s. %s." % (__copyright__, __license__)).pack()

    def search_records(self, conditions_list, searching_text, search):
        """
        Sets new search terms and conditions and refreshes the GUI table.

        Args taken:
        -conditions_list (list of Tk IntVars)
        -searching_text (Tk StringVar)
        -search (Tk Toplevel window)

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow(main)
        >>> maincontent.search_records(conditions_list, StringVar(value="Google"))
        """
        # updating instance variables
        self.conditions = conditions_list
        self.searching_text = searching_text
        search.destroy()
        self.refresh_table()  # table is updated according to search terms/conditions

    def show_all(self):
        """
        Sets the search terms and conditions to defaults and refreshes GUI table.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow(main)
        >>> maincontent.show_all()
        """
        self.searching_text = StringVar(value="")
        self.conditions = [IntVar(value=1), IntVar(value=1), IntVar(value=1)]
        self.refresh_table()

    def next_page(self, box):
        """
        Moves onto the next page of records by changing the upper and lower bounds.

        No args taken.

        Usage handled internally by class.
        """
        self.page += 1
        self.lower_bound = self.upper_bound  # new lower bound will be same as old upper bound
        # condition to see if all spaces for records are needed
        if not (self.upper_bound + self.max_records_shown > len(self.record_dict)):
            self.upper_bound += self.max_records_shown
        else:
            # upper bound is set to length of records if on last page
            self.upper_bound = len(box)
        self.refresh_table()

    def previous_page(self):
        """
        Moves back to the previous page of records by changing the upper and lower bounds.

        No args taken.

        Usage handled internally by class.
        """
        self.upper_bound = self.lower_bound  # new upper bound is old lower bound if on last page
        self.page -= 1
        self.lower_bound -= self.max_records_shown  # lower bound decreases by maximum records shown
        self.refresh_table()

    def save_records(self):
        """
        Saves all records to database.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow(main)
        >>> maincontent.save_records()
        """
        manage_records.write_encrypted(self.record_dict, preserve=True)
        mb.showinfo(INFO_BOX_TITLE, "Records saved.", parent=self.master)

    def clear_records(self):
        """
        Clears all records from the database and refreshes the GUI table.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow(main)
        >>> maincontent.clear_records()
        """
        manage_records.clear_records("both", "main", self.record_dict)
        self.refresh_table()

    def change_account_details(self):
        """
        Open the account settings window.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow(main)
        >>> maincontent.change_account_details()
        """
        account = Toplevel()
        AccountWindow(account)

    def clear_all_details(self):
        """
        Handles the clearing of all records using the GUI.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> mainwin = MainWindow(main, True)
        >>> mainwin.clear_all_details()
        """
        complete = manage_records.clear_records('both', 'main', self.record_dict, everything=True)
        if complete:
            self.dev.clear_all(self.master)

    def view_login_records(self):
        """
        Opens the login records window.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow(main)
        >>> maincontent.view_login_records()
        """
        loginrec = Toplevel()
        LoginRecords(loginrec)

    def strength_checker(self):
        """
        Opens the password strength checker tool.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow()
        >>> maincontent.strength_checker()
        """
        passc = Toplevel()
        PassChecker(passc)

    def pref_window(self):
        """
        Opens the preferences window.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow()
        >>> maincontent.pref_window()
        """
        pref = Toplevel()
        Preferences(pref)

    def dev_options_window(self):
        """
        Opens the dev options window.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow()
        >>> maincontent.dev_options_window()
        """
        dev = Toplevel()
        DevOptionsWindow(dev, self.record_dict)

    def import_backup(self):
        """
        Handles importing of a backup.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> maingui = MainWindow(main, False)
        >>> main.mainloop()
        >>> maingui.import_backup()
        """
        imported = manage_records.import_backup(self.master, self.record_dict)
        if imported:
            wm.startup()

    def log_out(self):
        """
        Logs out the user and returns them to the login window.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> maincontent = MainWindow(main)
        >>> maincontent.log_out()
        """
        result = mb.askyesnocancel("Save records", "Save records before logging out?", parent=self.master,
                                   icon='warning')
        if result:
            wm.auto_lock.acquire()
            wm.stop_auto_save(self.master)
            self.master.destroy()
            wm.auto_lock.release()
            wm.startup()
        elif not result:
            wm.auto_lock.acquire()
            wm.stop_auto_save(self.master)
            self.master.destroy()
            wm.auto_lock.release()
            wm.startup()
        # mb.askyesnocancel is a bit finicky, hence above structure not including 'else'


class LoginWindow(GUI):
    """
    Class containing user interface for logging into main program.

    Superclassed by GUI.

    Args taken:
    -master (Tk window)
    -login_type (str - "new" or "normal")

    Methods:
    -draw_normal_login(self)
    -draw_new_user_win(self)
    -forgot_password(self)

    Usage:
    >>> login = Tk()
    >>> loginwin = LoginWindow(login, "normal")
    """

    def __init__(self, master, login_type):
        super().__init__(master)
        self.set_up_window()
        if self.system == 'Linux':
            self.master.configure(background=self.BGCOL)
        self.width = self.DEFAULT_WIDTH
        if login_type == "new":
            self.height = self.DEFAULT_HEIGHT + 65
        else:
            self.height = self.DEFAULT_HEIGHT + 20
            self.draw_normal_login()
        self.master.geometry("%dx%d" % (self.width, self.height))

    def draw_normal_login(self):
        """
        Draws the content of the login window for standard logins.

        No args taken.

        Usage handled by class __init__.
        """
        ttk.Label(self.master, text="Welcome", font=self.HEADER).pack()
        ttk.Label(self.master).pack()

        # labels and entry
        ttk.Label(self.master, text="Username").pack()
        un_text = StringVar(self.master, value="")
        un_entry = ttk.Entry(self.master, text=un_text)
        un_entry.pack()

        ttk.Label(self.master, text="Password").pack()
        password_text = StringVar(self.master, value="")
        password_entry = ttk.Entry(self.master, textvariable=password_text, show="*")
        password_entry.pack()
        ttk.Label(self.master).pack()

        # buttons
        ttk.Button(self.master, text="Login", command=lambda: wm.log_in(password_entry, un_entry, self.master)
                   ).pack()
        ttk.Button(self.master, text="Forgot Password?",
                   command=self.forgot_password).pack()
        ttk.Label(self.master).pack()
        ttk.Button(self.master, text="Exit", command=self.master.destroy).pack()

    def draw_new_user_win(self):
        """
        Draws the content of the login window for new logins.

        No args taken.

        Usage handled by class __init__.
        """
        ttk.Label(self.master, text="Welcome", font=self.HEADER).pack()
        ttk.Label(self.master).pack()
        ttk.Label(self.master, text="Please enter a username and password.")
        ttk.Label(self.master).pack()

        # labels and entry
        ttk.Label(self.master, text="Username").pack()
        un_text = StringVar(self.master, value="")
        un_entry = ttk.Entry(self.master, text=un_text)
        un_entry.pack()

        ttk.Label(self.master, text="Password").pack()
        password_text = StringVar(self.master, value="")
        con_password_text = StringVar(self.master, value="")
        password_entry = ttk.Entry(self.master, text=password_text, show="*")
        password_entry.pack()

        ttk.Label(self.master, text="Confirm Password").pack()
        con_password_entry = ttk.Entry(self.master, text=con_password_text, show="*")
        con_password_entry.pack()
        ttk.Label(self.master).pack()

        ttk.Label(self.master, text="Email Address").pack()
        email_text = StringVar(self.master, value="")
        email_entry = ttk.Entry(self.master, text=email_text)
        email_entry.pack()
        ttk.Label(self.master).pack()

        # Buttons
        ttk.Button(self.master, text="Create account",
                   command=lambda: self.add_new_user(password_entry, con_password_entry, un_entry, email_entry)).pack()
        ttk.Button(self.master, text="Close", command=self.master.destroy).pack()

    def forgot_password(self):
        """
        Creates the forgot password window.
        
        No args taken.
        
        Usage:
        >>> login = Tk()
        >>> loginwin = LoginWindow(login, "normal")
        >>> loginwin.forgot_password()
        """
        wm.feature_not_available()  # feature not currently available due to tkinter bug
        # forgot = Toplevel()
        # ForgotPasswordWindow(forgot, self.master)
        # self.master.wait_window(forgot)

    def add_new_user(self, password_entry, con_password_entry, un_entry, email_entry):
        """
        Handles adding of a new user.

        Args taken:
        -password_entry (tk entry field)
        -con_password_entry (tk entry field)
        -un_entry (tk entry field)
        -email_entry (tk entry field)

        Usage handled by GUI.
        """
        added = secure.add_new_user(password_entry, con_password_entry, un_entry, self.master, email_entry)
        if added:
            wm.startup()


class ForgotPasswordWindow(GUI):
    """
    Class containing all GUI information for the password reset process.
    
    Superclassed by GUI.
    
    Args taken:
    -master (tk window)
    -login (tk window 'login')
    
    Methods:
    -enter_key_window(self, admin, un_entry)
    -new_password_window(self)
    -clear_widgets(self)
    -check_key(self, key_entry, con_key, admin)
    -reset_password(self, new_pw_entry, c_new_pw_entry)
    
    Usage:
    >>> login = Tk()
    >>> loginwin = LoginWindow(login)
    >>> forgot = Toplevel()
    >>> forgotpwwin = ForgotPasswordWindow(forgot, login)
    """

    def __init__(self, master, login):
        super().__init__(master)
        self.set_up_window()
        self.login = login
        self.width = self.DEFAULT_HEIGHT - 28
        self.height = self.DEFAULT_HEIGHT - 100
        if self.system == 'Linux':
            self.height += 10
            self.master.configure(background=self.BGCOL)
        self.master.geometry('%dx%d' % (self.width, self.height))
        ttk.Label(self.master, text="Password Reset", font=self.HEADER).pack()
        ttk.Label(self.master).pack()

        ttk.Label(self.master, text="Username").pack()
        username = StringVar(self.master, value="")
        username_entry = ttk.Entry(self.master, textvariable=username)
        username_entry.pack()

        ttk.Button(self.master, text="Send reset key", command=lambda: self.enter_key_window(False, username_entry
                                                                                             )).pack()
        ttk.Button(self.master, text="Admin reset...", command=lambda: self.enter_key_window(True, username_entry
                                                                                             )).pack()
        ttk.Button(self.master, text="Close", command=self.master.destroy).pack()

    def enter_key_window(self, admin, un_entry):
        """
        Changes GUI to the key entry window.
        
        Args taken:
        -admin (bool)
        -un_entry (tk entry field)

        Usage:
        >>> login = Tk()
        >>> loginwin = LoginWindow(login)
        >>> forgot = Toplevel()
        >>> forgotwin = ForgotPasswordWindow(forgot, login)
        >>> forgotwin.enter_key_window()
        """
        self.clear_widgets()
        con_key = self.dev_options.send_key(un_entry, admin)  # key is generated and parsed here
        ttk.Label(self.master).pack()
        ttk.Label(self.master, text="Enter key").pack()
        key_text = StringVar(self.master, value="")
        if admin:
            key_entry = ttk.Entry(self.master, textvariable=key_text, show="*")  # ensures admin password is hidden
        else:
            key_entry = ttk.Entry(self.master, textvariable=key_text)
        key_entry.pack()
        ttk.Button(self.master, text="Confirm", command=lambda: self.check_key(key_entry, con_key, admin)
                   ).pack()
        ttk.Button(self.master, text="Cancel", command=self.master.destroy).pack()

    def new_password_window(self):
        """
        Changes GUI to the password reset window.

        No args taken.

        Usage:
        >>> login = Tk()
        >>> loginwin = LoginWindow(login)
        >>> forgot = Toplevel()
        >>> forgotwin = ForgotPasswordWindow(forgot, login)
        >>> forgotwin.new_password_window()
        """
        self.clear_widgets()
        ttk.Label(self.master, text="Password Reset", font=self.HEADER).pack()
        ttk.Label(self.master).pack()

        # Labels and entry

        ttk.Label(self.master, text="Enter New Password").pack()
        new_password = StringVar(self.master, value="")
        new_pw_entry = ttk.Entry(self.master, text=new_password, show="*")
        new_pw_entry.pack()

        ttk.Label(self.master, text="Confirm New Password").pack()
        c_new_password = StringVar(self.master, value="")
        c_new_pw_entry = ttk.Entry(self.master, text=c_new_password, show="*")
        c_new_pw_entry.pack()

        # ttk.Buttons
        ttk.Label(self.master).pack()
        confirm = ttk.Button(self.master, text="Confirm changes",
                             command=lambda: self.reset_password(new_pw_entry, c_new_pw_entry))
        confirm.pack()

    def clear_widgets(self):
        """
        Clears widgets from window.

        No args taken.

        Usage:
        >>> login = Tk()
        >>> loginwin = LoginWindow(login)
        >>> forgot = Toplevel()
        >>> forgotwin = ForgotPasswordWindow(forgot, login)
        >>> forgotwin.clear_widgets()
        """
        for widget in self.master.winfo_children():
            widget.destroy()

    def check_key(self, key_entry, con_key, admin):
        """
        Changes GUI to the key entry window.

        Args taken:
        -key_entry (tk entry field)
        -con_key (str)
        -admin (bool)

        Usage handled by GUI.
        """
        correct = secure.check_key(key_entry, con_key, self.login, admin)
        if correct:
            self.new_password_window()

    def reset_password(self, new_pw_entry, c_new_pw_entry):
        """
        Resets the user's password and restarts the program.

        Args taken:
        -new_pw_entry (tk entry field)
        -c_new_pw_entry (tk entry field)

        Usage handled by GUI.
        """
        complete = secure.password_reset(new_pw_entry, c_new_pw_entry, self.login)
        if complete:
            self.login.destroy()
            wm.startup()


class AddRecordWindow(GUI):
    """
    Class containg GUI for adding records.

    Superclassed by GUI.

    Args taken:
    -master (tk window)
    -record_dict (dictionary)

    No methods.

    Usage:
    >>> add = Tk()
    >>> addwin = AddRecordWindow(add, record_dict=manage_records.create_dict())
    """

    def __init__(self, master, record_dict):
        super().__init__(master)
        self.set_up_window()
        if self.system == 'Linux':
            self.master.configure(background=self.BGCOL)
        self.width = self.DEFAULT_WIDTH
        self.height = self.DEFAULT_HEIGHT + 15
        self.master.geometry('%dx%d' % (self.width, self.height))
        ttk.Label(self.master, text="New Record", font=self.HEADER).pack()
        ttk.Label(self.master).pack()

        # site entry
        site_text = StringVar(self.master, value="")
        ttk.Label(self.master, text="Site").pack()
        site_entry = ttk.Entry(self.master, textvariable=site_text)
        site_entry.pack()
        ttk.Label(self.master).pack()

        # username entry
        un_text = StringVar(self.master, value="")
        ttk.Label(self.master, text="Username").pack()
        un_entry = ttk.Entry(self.master, textvariable=un_text)
        un_entry.pack()
        ttk.Label(self.master).pack()

        # password entry
        pw_text = StringVar(self.master, value="")
        ttk.Label(self.master, text="Password").pack()
        pw_entry = ttk.Entry(self.master, textvariable=pw_text)
        pw_entry.pack()
        ttk.Label(self.master).pack()

        # buttons
        ttk.Button(self.master, text="Add",
                   command=lambda: manage_records.add_new_record(site_entry, un_entry, pw_entry, self.master,
                                                                 record_dict)).pack()
        ttk.Button(self.master, text="Close", command=self.master.destroy).pack()


class EditRecordWindow(GUI):
    """
    Class containg GUI for editing records.

    Superclassed by GUI.

    Args taken:
    -master (tk window)
    -i (int)
    -box (list)
    -record_dict (dictionary)
    -index (int)

    No methods.

    Usage handled by main GUI, information required is generated then.
    """

    def __init__(self, master, i, box, record_dict, index):
        super().__init__(master)
        self.set_up_window()
        self.width = self.DEFAULT_WIDTH
        self.height = 315
        if self.system == 'Linux':
            self.height += 15
            self.master.configure(background=self.BGCOL)
        self.master.geometry('%dx%d' % (self.width, self.height))
        ttk.Label(self.master, text="Edit Record", font=self.HEADER).pack()
        ttk.Label(self.master).pack()

        # site entry
        new_site_text = StringVar(self.master, value=box[i][0])
        ttk.Label(self.master, text="Site").pack()
        new_site_entry = ttk.Entry(self.master, textvariable=new_site_text)
        new_site_entry.pack()
        ttk.Label(self.master).pack()

        # username entry
        new_un_text = StringVar(self.master, value=box[i][1])
        ttk.Label(self.master, text="Username").pack()
        new_un_entry = ttk.Entry(self.master, textvariable=new_un_text)
        new_un_entry.pack()
        ttk.Label(self.master).pack()

        # password entry
        new_pw_text = StringVar(self.master, value=box[i][2])
        ttk.Label(self.master, text="Password").pack()
        new_pw_entry = ttk.Entry(self.master, textvariable=new_pw_text)
        new_pw_entry.pack()
        ttk.Label(self.master).pack()

        # buttons
        ttk.Button(self.master, text="Confirm",
                   command=lambda: manage_records.change_record(new_site_text, new_un_text, new_pw_text, self.master,
                                                                record_dict, index)).pack()
        ttk.Button(self.master, text="Delete",
                   command=lambda: manage_records.delete_record(self.master, record_dict, index)
                   ).pack()
        ttk.Button(self.master, text="Close", command=self.master.destroy).pack()


class AccountWindow(GUI):
    """
    Class containg GUI for editing account settings.

    Superclassed by GUI.

    Args taken:
    -master (tk window)

    Methods:
    -change_details(self, un_entry, old_pw_entry, new_pw_entry, c_new_pw_entry, email_entry)

    Usage:
    >>> account = Tk()
    >>> accountwin = AccountWindow(account)
    """

    def __init__(self, master):
        super().__init__(master)
        self.set_up_window()
        self.width = self.DEFAULT_WIDTH
        self.height = 340
        if self.system == 'Linux':
            self.master.configure(background=self.BGCOL)
            self.height += 10
        self.master.geometry("%dx%d" % (self.width, self.height))
        ttk.Label(self.master, text="Edit Account Details", font=self.HEADER).pack()
        ttk.Label(self.master).pack()

        # labels and entry
        ttk.Label(self.master, text="Username").pack()
        un_text = settings["User Details"]["username"]
        username = StringVar(self.master, value=un_text)
        un_entry = ttk.Entry(self.master, text=username)
        un_entry.pack()

        ttk.Label(self.master, text="Old Password").pack()
        old_password = StringVar(self.master, value="")
        old_pw_entry = ttk.Entry(self.master, text=old_password, show="*")
        old_pw_entry.pack()

        ttk.Label(self.master, text="New Password").pack()
        new_password = StringVar(self.master, value="")
        new_pw_entry = ttk.Entry(self.master, text=new_password, show="*")
        new_pw_entry.pack()

        ttk.Label(self.master, text="Confirm New Password").pack()  # user is required to enter their new password twice
        c_new_password = StringVar(self.master, value="")
        c_new_pw_entry = ttk.Entry(self.master, text=c_new_password, show="*")
        c_new_pw_entry.pack()

        ttk.Label(self.master, text="Email Address").pack()
        adr = settings["User Details"]["email"]
        email_text = StringVar(self.master, value=adr)
        email_entry = ttk.Entry(self.master, text=email_text)
        email_entry.pack()

        # ttk.Buttons
        ttk.Label(self.master).pack()
        confirm = ttk.Button(self.master, text="Confirm changes",
                             command=lambda: self.change_details(un_entry, old_pw_entry, new_pw_entry, c_new_pw_entry,
                                                                 email_entry))
        confirm.pack()
        ttk.Button(self.master, text="Close", command=self.master.destroy).pack()

        self.master.mainloop()

    def change_details(self, un_entry, old_pw_entry, new_pw_entry, c_new_pw_entry, email_entry):
        """
        Changes the users account details.
        
        Args taken:
        -un_entry (tk entry field)
        -old_pw_entry (tk entry field)
        -new_pw_entry (tk entry field)
        -c_new_pw_entry (tk entry field)
        -email_entry (tk entry field)
        
        Usage handled by GUI.
        """
        changed = secure.change_details(un_entry, old_pw_entry, new_pw_entry, c_new_pw_entry, self.master,
                                        email_entry)
        if changed:
            self.master.destroy()


class LoginRecords(GUI):
    """
    Class containing GUI to show login records.
    
    Superclassed by GUI.
    
    Args taken:
    -master (Tk window)
    
    No methods.
    
    
    Usage:
    >>> loginrec = Tk()
    >>> loginrecwin = LoginRecords(loginrec)
    """

    def __init__(self, master):
        super().__init__(master)
        # some similarities to main window
        self.set_up_window()
        self.frame = None
        self.login_records = manage_records.db_manager.read_log()
        self.max_records_shown = int(settings['Preferences']['logins displayed'])
        self.lower_bound = 0
        self.upper_bound = self.max_records_shown
        self.page = 1
        self.no_of_pages = 1
        if self.system == 'Linux':
            self.master.configure(background=self.BGCOL)
        self.create_table()

    # functions below are shared with main window, will not comment

    def create_frame(self):
        """
        Draws frame inside login record window.

        No args taken

        Usage:
        >>> loginrec = Tk()
        >>> loginrec_content = LoginRecords(loginrec)
        >>> loginrec_content.create_frame()
        """
        if self.system == 'Linux':
            self.frame = Frame(self.master, bg=self.BGCOL)
            self.frame.grid()
            self.master.configure(background=self.BGCOL)
        else:
            self.frame = Frame(self.master)
            self.frame.grid()

    def clear_frame(self):
        """
        Clears frame in login record window.

        No args taken.

        Usage:
        >>> loginrec = Tk()
        >>> loginrec_content = LoginRecords(loginrec)
        >>> loginrec_content.create_table()
        >>> loginrec_content.clear_frame()
        """
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        self.frame = None

    def create_table(self):
        """
        Creates table inside of frame in login record window.

        No args taken.

        Usage:
        >>> loginrec = Tk()
        >>> loginrec_content = LoginRecords(loginrec)
        >>> loginrec_content.create_table()

        """
        self.create_frame()
        if len(self.login_records) > 0:
            ttk.Label(self.frame, text="Date/Time", font=self.HEADER).grid(row=0, column=0, padx=self.DEFAULT_PAD + 5)
            ttk.Label(self.frame, text="User", font=self.HEADER).grid(row=0, column=1, padx=self.DEFAULT_PAD + 5)
            ttk.Label(self.frame, text="Success", font=self.HEADER).grid(row=0, column=2, padx=self.DEFAULT_PAD + 5)
            if len(self.login_records) <= self.max_records_shown:
                for i in range(len(self.login_records)):
                    record = self.login_records[i]
                    for x in range(1, 4):
                        ttk.Label(self.frame, text=record[x], anchor=W).grid(row=i + 1, column=x - 1)
            else:
                for i in range(self.lower_bound, self.upper_bound):
                    record = self.login_records[i]
                    for x in range(1, 4):
                        ttk.Label(self.frame, text=record[x], anchor=W).grid(row=i + 1, column=x - 1)
                if self.upper_bound < len(self.login_records):
                    ttk.Button(self.frame, text='Next', command=self.next_page).grid(row=self.upper_bound + 2, column=3)
                if self.page != 1:
                    ttk.Button(self.frame, text='Back', command=self.previous_page).grid(row=self.upper_bound + 2,
                                                                                         column=0)
                if self.max_records_shown < len(self.login_records):
                    ttk.Label(self.frame, text='Page').grid(row=self.upper_bound + 2, column=1, sticky=E)
                    self.calculate_page_numbers(self.login_records)
                    ttk.Label(self.frame, text=str("%d/%d" % (self.page, self.no_of_pages))).grid(
                        row=self.upper_bound + 2, column=2, sticky=W)
            clear_button = ttk.Button(self.frame, text="Clear login records",
                                      command=lambda: manage_records.db_manager.clear_log(self.frame))
            clear_button.grid(row=0, column=3)
        else:
            self.master.geometry("%dx45" % self.DEFAULT_WIDTH)
            ttk.Label(self.frame, text='No previous logins.').grid(row=1)

    def refresh_table(self):
        """
        Refreshes table in login record window.

        No args taken.

        Usage:
        >>> loginrec = Tk()
        >>> loginrec_content = LoginRecords(loginrec)
        >>> loginrec_content.create_table()
        >>> loginrec_content.refresh_table()
        """
        self.clear_frame()
        self.create_table()

    def next_page(self):
        """
        Moves onto the next page of records by changing the upper and lower bounds.

        No args taken.

        Usage handled internally by class.
        """
        self.page += 1
        self.lower_bound = self.upper_bound
        if not (self.upper_bound + self.max_records_shown > len(self.login_records)):
            self.upper_bound += self.max_records_shown
        else:
            self.upper_bound = len(self.login_records)
        self.refresh_table()

    def previous_page(self):
        """
        Moves back to the previous page of records by changing the upper and lower bounds.

        No args taken.

        Usgae handled internally by class.
        """
        self.upper_bound = self.lower_bound
        self.lower_bound -= self.max_records_shown
        self.page -= 1
        self.refresh_table()

    def calculate_page_numbers(self, box):
        """
        Calculates the number of the page currently shown in the login record window..

        Args taken:
        -box (list of records)

        Usage handled internally by class.
        """
        self.no_of_pages = (len(box) / self.max_records_shown)
        if (len(box) % self.max_records_shown) > 0:
            self.no_of_pages += 1


class PassChecker(GUI):
    """
    Class containing GUI for the password strength checker tool.
    
    Superclassed by GUI.
    
    Args taken:
    -master (tk window)
    
    No methods.
    
    Usage:
    >>> passc = Tk()
    >>> passcheckerwin = PassChecker(passc)
    """

    def __init__(self, master):
        super().__init__(master)
        self.set_up_window()
        self.width = self.DEFAULT_WIDTH
        self.height = self.DEFAULT_HEIGHT
        self.master.geometry('%dx%d' % (self.width, self.height))
        if self.system == 'Linux':
            self.master.configure(background=self.BGCOL)
        ttk.Label(self.master, text="Password Strength Checker", font=self.HEADER).pack()
        ttk.Label(self.master).pack()
        pw_text = StringVar(self.master, value="")
        pw_entry = ttk.Entry(self.master, textvariable=pw_text, show="*")
        pw_entry.pack()
        ttk.Button(self.master, text="Check password strength",
                   command=lambda: secure.check_pass_strength(pw_entry, self.master)).pack()


class Preferences(GUI):
    """
    Class containg GUI for preferences window
    
    Superclassed by GUI.
    
    Args taken:
    -master (tk window)
    
    No methods..
    
    Usage:
    >>> pref = Tk()
    >>> prefwin = Preferences(pref)
    """

    def __init__(self, master):
        super().__init__(master)
        self.set_up_window()
        self.width = self.DEFAULT_WIDTH
        self.height = self.DEFAULT_HEIGHT
        if self.system == 'Linux':
            self.master.config(background=self.BGCOL)
            self.height += 20
        self.master.geometry('%dx%d' % (self.width, self.height))
        ttk.Label(self.master, text='Preferences', font=self.HEADER).pack()
        ttk.Label(self.master).pack()
        timeout_active = IntVar()
        if settings["Preferences"]["timeout active"] != "":  # empty value in ini file indicates "False"
            timeout_active.set(1)  # value of 1 means timeout is active
        else:
            timeout_active.set(0)
        timeout_button = ttk.Checkbutton(self.master, text="Auto logout", variable=timeout_active)
        timeout_button.pack()

        ttk.Label(self.master, text="Auto logout time (s)").pack()
        log_time = StringVar(self.master, value=settings["Preferences"]["timeout"])
        log_time_entry = ttk.Entry(self.master, textvariable=log_time)
        log_time_entry.pack()

        ttk.Label(self.master, text="Autosave time (s)").pack()
        auto_time = StringVar(self.master, value=settings["Preferences"]["autosave time"])
        auto_time_entry = ttk.Entry(self.master, textvariable=auto_time)
        auto_time_entry.pack()

        ttk.Label(self.master, text="Passwords per page").pack()
        passwords_shown = StringVar(self.master, value=settings['Preferences']['records displayed'])
        passwords_shown_entry = ttk.Entry(self.master, textvariable=passwords_shown)
        passwords_shown_entry.pack()

        ttk.Label(self.master, text="Login records per page").pack()
        logins_shown = StringVar(self.master, value=settings['Preferences']['logins displayed'])
        logins_shown_entry = ttk.Entry(self.master, textvariable=logins_shown)
        logins_shown_entry.pack()

        ttk.Button(self.master, text="Save changes",
                   command=lambda: secure.update_settings(log_time_entry, auto_time_entry, timeout_active,
                                                          passwords_shown_entry, logins_shown_entry, self.master)
                   ).pack()
        ttk.Button(self.master, text="Close", command=self.master.destroy).pack()
        self.master.mainloop()


class DevOptionsWindow(GUI):
    """
    Class containing GUI for developer options.
    
    Superclassed by GUI.
    
    Args taken:
    -master (tk window)
    -record_dict(dictionary)
    
    No methods.
    
    Usage:
    >>> dev = Tk()
    >>> devoptionswin = DevOptionsWindow(dev,record_dict=manage_records.create_dict())
    """

    def __init__(self, master, record_dict):
        super().__init__(master)
        self.set_up_window()
        self.record_dict = record_dict
        if self.system == 'Linux':
            self.master.configure(background=self.BGCOL)
        self.master.title("%s Developer Options" % self.MAIN_TITLE)

        # db management
        ttk.Label(self.master, text="Database options", font=self.HEADER).grid(row=0, column=0, padx=self.DEFAULT_PAD)
        ttk.Button(self.master, text="Clear 'passw_table'",
                   command=lambda: manage_records.clear_records("passw_table", "main",
                                                                self.record_dict)).grid(row=1, column=0)
        ttk.Button(self.master, text="Clear 'key_table'",
                   command=lambda: manage_records.clear_records("key_table", "main",
                                                                self.record_dict)).grid(
            row=2, column=0, padx=self.DEFAULT_PAD)
        ttk.Button(self.master, text="Clear 'log_table'",
                   command=lambda: manage_records.clear_records("log_table", "main", self.record_dict)
                   ).grid(row=3, column=0, padx=self.DEFAULT_PAD)

        # admin account settings
        # ttk.Label(self.master).grid(row=4, column=0)
        ttk.Label(self.master, text="Admin account settings", font=self.HEADER).grid(row=5, column=0,
                                                                                     padx=self.DEFAULT_PAD)
        ttk.Label(self.master, text="New admin password").grid(row=6, column=0, padx=self.DEFAULT_PAD)
        pass_text = StringVar(self.master, value="")
        pass_entry = ttk.Entry(self.master, textvariable=pass_text, show='*')
        pass_entry.grid(row=7, column=0, padx=self.DEFAULT_PAD)
        ttk.Button(self.master, text="Change admin password",
                   command=lambda: self.dev_options.change_admin_pass(pass_entry, self.master)
                   ).grid(row=8, column=0, padx=self.DEFAULT_PAD)

        # user settings
        ttk.Label(self.master, text="User details", font=self.HEADER).grid(row=0, column=2, padx=self.DEFAULT_PAD)
        ttk.Label(self.master, text="Username").grid(row=1, column=2, padx=self.DEFAULT_PAD)
        details = settings["User Details"]
        un_text = StringVar(self.master, value=details["username"])
        un_entry = ttk.Entry(self.master, textvariable=un_text)
        un_entry.grid(row=2, column=2, padx=self.DEFAULT_PAD)
        ttk.Label(self.master, text="Email address").grid(row=3, column=2, padx=self.DEFAULT_PAD)
        email_text = StringVar(self.master, value=details['email'])
        email_entry = ttk.Entry(self.master, textvariable=email_text)
        email_entry.grid(row=4, column=2, padx=self.DEFAULT_PAD)
        ttk.Button(self.master, text="Update user details",
                   command=lambda: self.dev_options.admin_change_user_details(un_entry, email_entry, self.master)
                   ).grid(row=5, column=2, padx=self.DEFAULT_PAD)
        ttk.Button(self.master, text="Clear user details",
                   command=lambda: self.dev_options.clear_user_details(self.master)
                   ).grid(row=6, column=2, padx=self.DEFAULT_PAD)

        # email settings
        ttk.Label(self.master, text="Email settings", font=self.HEADER).grid(row=0, column=1, padx=self.DEFAULT_PAD)
        email_settings = self.dev_options.get_email_settings()
        host_text = StringVar(self.master, value=email_settings['host'])
        port_text = StringVar(self.master, value=email_settings['port'])
        addr_text = StringVar(self.master, value=email_settings['address'])
        pass_text = StringVar(self.master, value=email_settings['password'])
        ttk.Label(self.master, text="Host").grid(row=1, column=1, padx=self.DEFAULT_PAD)
        ttk.Label(self.master, text="Port").grid(row=3, column=1)
        ttk.Label(self.master, text="Address").grid(row=5, column=1, padx=self.DEFAULT_PAD)
        ttk.Label(self.master, text="Password").grid(row=7, column=1, padx=self.DEFAULT_PAD)
        host_entry = ttk.Entry(self.master, textvariable=host_text)
        port_entry = ttk.Entry(self.master, textvariable=port_text)
        addr_entry = ttk.Entry(self.master, textvariable=addr_text)
        pass_entry = ttk.Entry(self.master, textvariable=pass_text, show="*")
        host_entry.grid(row=2, column=1, padx=self.DEFAULT_PAD)
        port_entry.grid(row=4, column=1, padx=self.DEFAULT_PAD)
        addr_entry.grid(row=6, column=1, padx=self.DEFAULT_PAD)
        pass_entry.grid(row=8, column=1, padx=self.DEFAULT_PAD)
        ttk.Button(self.master, text="Update Email Settings",
                   command=lambda: self.dev_options.set_email_settings(host_entry,
                                                                       port_entry,
                                                                       addr_entry,
                                                                       pass_entry,
                                                                       self.master)
                   ).grid(row=9, column=1)

        # other
        ttk.Button(self.master, text="Clear app data", command=self.clear_all_details).grid(row=8, column=2)
        ttk.Button(self.master, text="Close", command=self.master.destroy).grid(row=9, column=2, pady=self.DEFAULT_PAD)
        self.master.mainloop()

    def clear_all_details(self):
        """
        Handles the clearing of all records using the GUI.

        No args taken.

        Usage:
        >>> main = Tk()
        >>> mainwin = MainWindow(main, True)
        >>> mainwin.clear_all_details()
        """
        complete = manage_records.clear_records('both', 'main', self.record_dict, everything=True)
        if complete:
            self.dev_options.clear_all(self.master)


# instantiation of necessary classes and calling of functions
secure = Security()
manage_records = RecordManager()
wm = WindowManager()
settings_file = INIFile('data/settings.ini')
settings = settings_file.read_file()
manage_records.db_manager.create_databases()

if __name__ == '__main__':
    wm.startup()
