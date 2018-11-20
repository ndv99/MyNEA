from pwmain060 import *
import platform


__version__ = "0.6β"


class GUI:
    def __init__(self, master):
        # setting variables/constants for all windows
        self.DEFAULT_WIDTH = 308
        self.DEFAULT_HEIGHT = 280
        self.DEFAULT_PAD = 3
        icon_type = 'png'
        self.ICON_PATH = WindowManager.get_directory("data/favicon.%s" % icon_type)
        self.HEADER = "Helvetica 12 bold"
        self.MAIN_TITLE = "Password Manager %s" % __version__
        self.system = platform.system()
        if self.system == 'Linux':
            self.DEFAULT_HEIGHT += 10
            self.HEADER = "Ubuntu 12 bold"
            self.BGCOL = "#F6F4F2"
        self.dev_options = DeveloperOptions()
        self.wm = WindowManager()
        
        # window rendering applicable to all 
        self.master = master
        self.master.title(self.MAIN_TITLE)
        icon = PhotoImage(file=self.ICON_PATH)
        self.master.tk.call('wm', 'iconphoto', self.master._w, icon)


class MainWindow(GUI):
    def __init__(self, master, admin):
        super().__init__(master)
        self.record_dict = manage_records.create_dict()
        self.admin = admin
        self.menubar = Menu(master)
        self.load_menubar(True)
        self.frame = None
        if self.system == 'Linux':
            self.master.configure(background=self.BGCOL)

    def search_window_old(self, record_dict, searching_text, menu, conditions):
        """
        Sets up "search window", which displays records according to given conditions.

        Args taken:
        -searching_text (str)
        -record_dict (dictionary)
        -menu (tkinter window "menu")
        -conditions (list of tkinter IntVars)

        Usage example:

        >>> windows.search_window(record_dict, "Google")

        """
        box, indices, searched = manage_records.search_dict(record_dict, searching_text, conditions)
        search = Toplevel()
        if self.system == 'Linux':
            search.configure(background="#F6F4F2")
        icon = PhotoImage(file=self.ICON_PATH)
        # docs said to use private varialbe '_w'
        search.tk.call('wm', 'iconphoto', search._w, icon)
        ttk.Label(search, text="Fields searched:").grid(row=0, column=0, sticky=E)
        if len(searched) == 1:
            searched_str = searched[0]
        elif len(searched) == 2:
            searched_str = "%s, %s" % (searched[0], searched[1])
        elif len(searched) == 3:
            searched_str = "All"
        else:
            searched_str = "None"
        ttk.Label(search, text=searched_str).grid(row=0, column=1, sticky=W)
        if len(box) > 0:
            ttk.Label(search, text="%d records" % len(box)).grid(row=0, column=2, padx=self.DEFAULT_PAD, sticky=W)
            choice = StringVar(search, value="Select...")
            options = ["Select...", "CSV", "SQL Database", "XML", "HTML", "JSON"]
            export_options = ttk.OptionMenu(search, choice, *options)
            export_options.grid(row=0, column=3, padx=self.DEFAULT_PAD, sticky=W)
            ttk.Button(search, text="Export", command=lambda: self.wm.export(choice, search, menu, record_dict)
                       ).grid(row=0, column=2, padx=self.DEFAULT_PAD, sticky=E)
            ttk.Label(search, text="Site", font=self.HEADER).grid(row=1, column=1)
            ttk.Label(search, text="Username", font=self.HEADER).grid(row=1, column=2)
            ttk.Label(search, text="Password", font=self.HEADER).grid(row=1, column=3)
            for i in range(len(box)):
                record = box[i]
                index = indices[i]
                for x in range(1, 4):
                    if x % 3 == 0:
                        self.wm.edit_button_func(search, i, box, searching_text, record_dict, index, menu, conditions)
                    ttk.Label(search, text=record[x - 1]).grid(row=i + 2, column=x, padx=self.DEFAULT_PAD, sticky=W)
            close_button = ttk.Button(search, text='Close', command=search.destroy)
            close_button.grid(row=len(box) + 2, column=1, pady=self.DEFAULT_PAD)

            # clear records
            clear_button = ttk.Button(search, text="Clear all records",
                                      command=lambda: manage_records.clear_records("both", "menu", record_dict))
            clear_button.grid(row=1, column=0)
        else:
            search.geometry("%dx75" % self.DEFAULT_WIDTH)
            ttk.Label(search, text='No records found.').grid(row=1)
            close_button = ttk.Button(search, text='Close', command=search.destroy)
            close_button.grid(row=4, column=1, pady=self.DEFAULT_PAD)
        return search

    def create_table(self, searching_text, conditions):
        self.create_frame()
        box, indices, searched = manage_records.search_dict(self.record_dict, searching_text, conditions)
        ttk.Label(self.frame, text="Fields searched:").grid(row=0, column=0, sticky=E)
        if len(searched) == 1:
            searched_str = searched[0]
        elif len(searched) == 2:
            searched_str = "%s, %s" % (searched[0], searched[1])
        elif len(searched) == 3:
            searched_str = "All"
        else:
            searched_str = "None"
        ttk.Label(self.frame, text=searched_str).grid(row=0, column=1, sticky=W)
        if len(box) > 0:
            ttk.Label(self.frame, text="%d records" % len(box)).grid(row=0, column=2, padx=self.DEFAULT_PAD, sticky=W)
            choice = StringVar(self.frame, value="Select...")
            options = ["Select...", "CSV", "SQL Database", "XML", "HTML", "JSON"]
            export_options = ttk.OptionMenu(self.frame, choice, *options)
            export_options.grid(row=0, column=3, padx=self.DEFAULT_PAD, sticky=W)
            ttk.Button(self.frame, text="Export", command=lambda: self.wm.export(choice, self.master, self.master, self.record_dict)
                       ).grid(row=0, column=2, padx=self.DEFAULT_PAD, sticky=E)
            ttk.Label(self.frame, text="Site", font=self.HEADER).grid(row=1, column=1)
            ttk.Label(self.frame, text="Username", font=self.HEADER).grid(row=1, column=2)
            ttk.Label(self.frame, text="Password", font=self.HEADER).grid(row=1, column=3)
            for i in range(len(box)):
                record = box[i]
                index = indices[i]
                for x in range(1, 4):
                    if x % 3 == 0:
                        self.wm.edit_button_func(self.frame, i, box, searching_text, self.record_dict, index, self.master, conditions)
                    ttk.Label(self.frame, text=record[x - 1]).grid(row=i + 2, column=x, padx=self.DEFAULT_PAD, sticky=W)

            # clear records
            # clear_button = ttk.Button(self.master, text="Clear all records",
            #                           command=lambda: manage_records.clear_records("both", "menu", self.record_dict))
            # clear_button.grid(row=1, column=0)
            clear_button = ttk.Button(self.frame, text="Clear all records",
                                      command=self.clear_frame)
            clear_button.grid(row=1, column=0)
        else:
            self.master.geometry("%dx75" % self.DEFAULT_WIDTH)
            ttk.Label(self.frame, text='No records found.').grid(row=1)

    def create_frame(self):
        if self.system == 'Linux':
            self.frame = Frame(self.master, bg=self.BGCOL)
            self.frame.grid()
            self.master.configure(background=self.BGCOL)
        else:
            self.frame = Frame(self.master)
            self.frame.grid()

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        self.frame = None
        self.create_frame()

    def load_menubar(self, admin):
        # file menu
        file_menu = Menu(self.menubar, tearoff=0)
        export_menu = Menu(self.menubar, tearoff=0)
        export_menu.add_command(label="CSV")
        export_menu.add_command(label="HTML")
        export_menu.add_command(label="JSON")
        export_menu.add_command(label="XML")
        export_menu.add_command(label="SQL Database")
        file_menu.add_cascade(label='Export records', menu=export_menu)
        file_menu.add_command(label="Save")
        file_menu.add_command(label="Log out")
        file_menu.add_command(label="Exit")
        self.menubar.add_cascade(label="File", menu=file_menu)

        # records menu
        records_menu = Menu(self.menubar, tearoff=0)
        records_menu.add_command(label="Add record")
        records_menu.add_command(label="Clear all records")
        records_menu.add_command(label="Search records")
        self.menubar.add_cascade(label='Records', menu=records_menu)

        # account menu
        account_menu = Menu(self.menubar, tearoff=0)
        account_menu.add_command(label="Edit details")
        account_menu.add_command(label="Delete account")
        account_menu.add_command(label="View self.master records")
        self.menubar.add_cascade(label='Account', menu=account_menu)

        # tools menu
        tools_menu = Menu(self.menubar, tearoff=0)
        tools_menu.add_command(label="Password strength checker")
        tools_menu.add_command(label="Preferences")
        backup_menu = Menu(self.menubar, tearoff=0)
        backup_menu.add_command(label="Create backup")
        backup_menu.add_command(label="Import backup")
        tools_menu.add_cascade(label="Backup", menu=backup_menu)
        self.menubar.add_cascade(label='Tools', menu=tools_menu)
        if admin:
            tools_menu.add_separator()
            tools_menu.add_command(label="Developer options")

        self.master.config(menu=self.menubar)


class LoginWindow(GUI):
    def __init__(self, master, login_type):
        super().__init__(master)
        width = self.DEFAULT_WIDTH
        if login_type == "new":
            height = self.DEFAULT_HEIGHT + 65
            self.draw_new_user_win()
        else:
            height = self.DEFAULT_HEIGHT + 20
            self.draw_normal_login()
        self.master.geometry("%dx%d" % (width, height))

    def draw_normal_login(self):
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
        ttk.Button(self.master, text="Login", command=lambda: secure.log_in(password_entry, un_entry, self.master)
                   ).pack()
        ttk.Button(self.master, text="Forgot Password?", command=lambda: self.forgot_password_window(self.master)).pack()
        ttk.Label(self.master).pack()
        ttk.Button(self.master, text="Exit", command=self.master.destroy).pack()
    
    def draw_new_user_win(self):
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

        # ttk.Buttons
        ttk.Button(self.master, text="Create account", command=lambda: secure.add_new_user(password_entry,
                                                                                           con_password_entry,
                                                                                           un_entry, self.master,
                                                                                           email_entry)).pack()
        ttk.Button(self.master, text="Close", command=self.master.destroy).pack()


if __name__ == "__main__":
    gui = GUI(master=None)
    if gui.system == 'Linux':
        root = thk.ThemedTk()
        root.set_theme("radiance")
    else:
        root = Tk()
    main = MainWindow(root, True)
    main.create_table(StringVar(value=""), [IntVar(value=1), IntVar(value=1), IntVar(value=1)])
    root.mainloop()
