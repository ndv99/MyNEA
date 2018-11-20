# !/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Module for program-specific security operations.

Contains two classes:
-Security
-DeveloperOptions

Usage:
>>> secure = Security()
>>> startup_type = secure.startup()
"""

import datetime
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tkinter import messagebox as mb

from passlib.hash import bcrypt

import dbmanager
from filemanager import *

"""
This file is part of Tkinter Password Manager.

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

INFO_BOX_TITLE = "Information"
ERROR_BOX_TITLE = "Error"
WARNING_TITLE = "Warning"


class Security:
    """
    Class to manage data security when logging in.

    Does not take any arguments.

    Instantiates TextFile in __init__().

    Functions:
    -startup(self)
    -add_new_user(self, pass_entry, cpass_entry, un_entry, newu, email_entry)
    -change_details(self, new_un_entry, old_pw_entry, new_pw_entry, c_new_pw_entry, account, email_entry)
    -record_login(self, user, successful)
    -log_in(self, pass_entry, un_entry, login)
    -check_username(self, un_entry)
    -check_pass(self, pass_entry, admin)
    -server_setup(self)
    -send_key(self, un_entry, admin)
    -check_key(self, key_entry, key, login, admin)
    -keygen(self)
    -password_reset(self, new_pw_entry, c_new_pw_entry, win)
    -check_pass_strength(self, pass_entry, win)
    -pass_rules(self, pass_text, win)
    -generate_ascii_lists() [STATIC]
    -update_settings(self, log_time_entry, auto_time_entry, timeout_active, tools)

    Subclassed by DeveloperOptions.

    Usage example:

    >>> secure = Security
    >>> secure.startup()

    """

    def __init__(self):
        self.template_manage = TextFile('data/template.txt')

    def startup(self):
        """
        Handles the startup process of the program.

        No args taken.

        Usage example:
        >>> secure = Security()
        >>> secure.startup()

        """
        un_text = settings["User Details"]["username"]
        pw_text = settings["User Details"]["password"]
        email_text = settings["User Details"]["email"]
        if un_text == "" or pw_text == "" or email_text == "":  # starts as new user if there are missing credentials
            startup_type = "new"
        else:
            startup_type = "normal"
        return startup_type

    def add_new_user(self, pass_entry, cpass_entry, un_entry, newu, email_entry):
        """
        Creates a user profile for the program (username and password.)

        Args taken:
        -pass_entry (entry field in Tk window)
        -cpass_entry (entry field in Tk window)
        -un_entry (entry field in Tk window)
        -newu (Tk window "newu")
        -email_entry (entry field in Tk window)

        Usage example:
        >>> secure = Security()
        >>> secure.add_new_user("n£dfF23", "n£dfF23", "ndv99", newu, "noodles524@gmail.com")

        """
        added = False
        pass_text = pass_entry.get()
        cpass_text = cpass_entry.get()
        un_text = un_entry.get()
        email_text = email_entry.get()
        if pass_text == cpass_text:
            secure_pass = self.pass_rules(pass_text, newu)  # checks that password confirms to password rules
            if secure_pass:
                passw_hash = bcrypt.hash(pass_text)  # password is hashed so that it's never known by the program
                settings_file.write_file("User Details", "password", passw_hash)
                settings_file.write_file("User Details", "username", un_text)
                settings_file.write_file("User Details", "email", email_text)
                added = True
                mb.showinfo(INFO_BOX_TITLE, "User created.")
                newu.destroy()
        else:
            mb.showerror(ERROR_BOX_TITLE, "Passwords do not match.", parent=newu)
        return added

    def change_details(self, new_un_entry, old_pw_entry, new_pw_entry, c_new_pw_entry, account, email_entry):
        """
        Alters the user profile for the program (username and password).

        Args taken:
        -new_un_entry (entry field in Tk window)
        -old_pw_entry (entry field in Tk window)
        -new_pw_entry (entry field in Tk window)
        -c_new_pw_entry (entry field in Tk window)
        -account (Tk window "account")
        -email_entry(entry field in Tk window)

        Usage example:
        >>> secure = Security()
        >>> secure.change_details("ndv99", "Letmein", "n£dfF23", "n£dfF23", account, "example@email.com")

        """
        changed = False
        un_text = new_un_entry.get()
        email_text = email_entry.get()
        valid_old = self.check_pass(old_pw_entry, False)
        if valid_old:  # old password has to be valid before any changes are made
            new_pw_text = new_pw_entry.get()
            c_new_pw_text = c_new_pw_entry.get()
            if new_pw_text != "":  # only updates password if there's a new password there
                if new_pw_text == c_new_pw_text:
                    secure_pass = self.pass_rules(new_pw_text, account)  # checks new password conforms to rules
                    if secure_pass:
                        result = mb.askquestion("Confirm changes", "Change account details?", icon="warning")
                        if result == "yes":
                            if un_text:  # entry field contains old username, writes back if unchanged
                                settings_file.write_file("User Details", "username", un_text)
                            if email_text:  # entry field contains old email, writes back if unchanged
                                settings_file.write_file("User Details", "email", email_text)
                            new_hash = bcrypt.hash(new_pw_text)
                            settings_file.write_file("User Details", "password", new_hash)
                            mb.showinfo(INFO_BOX_TITLE, "Account details updated.")
                            changed = True
                        else:
                            mb.showinfo(INFO_BOX_TITLE, "Changes cancelled.", parent=account)
            elif new_pw_text == "":
                result = mb.askquestion("Confirm changes", "Change account details?", icon="warning")
                if result == "yes":
                    settings_file.write_file("User Details", "username", un_text)
                    settings_file.write_file("User Details", "email", email_text)
                    mb.showinfo(INFO_BOX_TITLE, "Account details updated.")
                    changed = True
                else:
                    mb.showinfo(INFO_BOX_TITLE, "Changes cancelled.", parent=account)
                    account.lift()
            else:
                mb.showerror(ERROR_BOX_TITLE, "Passwords do not match.", parent=account)
        else:
            mb.showerror(ERROR_BOX_TITLE, "Current password is incorrect.", parent=account)
        return changed

    def record_login(self, user, successful):
        """
        Records every login attempt (date, user, and success).

        Args taken:
        -user (str)
        -successful (str)

        Usage:
        >>> secure = Security()
        >>> secure.record_login("ndv99", "Successful")
        """
        now = datetime.datetime.now()  # current date and time
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")  # formats date and time as YYYY/MM/DD HH:MM:SS
        if successful:
            attempt = "Succesful"
        else:
            attempt = "Failed"
        dbm.write_to_log(timestamp, user, attempt)

    def log_in(self, pass_entry, un_entry, win):
        """
        Checks if the attempted login is valid.

        Args taken:
        -pass_entry (entry field in Tk window)
        -un_entry (entry field in Tk window)
        -login (Tk window "account")

        Usage example:
        >>> secure = Security()
        >>> secure.log_in("Letmein", "ndv99", win)

        """
        success = False
        admin = False
        user = un_entry.get()
        if user == "admin":
            valid_un = True
            admin = True
        else:
            valid_un = self.check_username(un_entry)
        if valid_un:
            valid_pw = self.check_pass(pass_entry, admin)
            if valid_pw:
                success = True
                pass_text = pass_entry.get()
                bcrypt.hash(pass_text)  # passsword is rehashed on a successful login for added security
            else:
                mb.showerror(ERROR_BOX_TITLE, "Incorrect password.", parent=win)
        else:
            mb.showerror(ERROR_BOX_TITLE, "Username not recognised.", parent=win)
        self.record_login(user, success)  # attempt is always recorded
        return success, admin

    def check_username(self, un_entry):
        """
        Checks if the entered username is the same as the stored one.

        Args taken:
        -un_entry (entry field in Tk window)

        Usage example:
        >>> secure = Security()
        >>> secure.check_username("ndv99")

        """
        valid_un = False
        un_text = settings["User Details"]["username"]
        try:  # contained exception handling within excpetion handler to handle excpetion given by exception handler
            try:
                un = un_entry.get()
                if un_text == un:
                    valid_un = True
            # interesting excpetion in Tkinter callback:
            # _tkinter.TclError: invalid command name ".140539365617560.140539360470072"
            # comes up when method is used during resetting password when username is checked
            # trying to use _tkinter.TclError does not work
            except _tkinter.TclError:
                mb.showerror("Error", "Internal program error. Please restart program.")
        except NameError:
            mb.showerror("Error", "Internal program error. Please restart program.")
        return valid_un

    def check_pass(self, pass_entry, admin):
        """
        Checks if the entered password is the same as the stored one.

        Args taken:
        -pass_entry (entry field in Tk window)
        -admin (boolean)

        Usage example:
        >>> secure = Security()
        >>> secure.check_pass("Letmein")

        """
        pass_text = pass_entry.get()
        if admin:
            passw = settings["Admin"]["password"]
        else:
            passw = settings["User Details"]["password"]
        valid = bcrypt.verify(pass_text, passw)  # hashes input with same salt as stored hash, compares values
        return valid

    def server_setup(self):
        """
        Sets up the SMTP server connection for password resets.

        No args taken.

        Usage:
        >>> secure = Security()
        >>> server, sender = secure.server_setup()

        """
        email_settings = settings["Email Settings"]
        host = email_settings["host"]
        port = email_settings["port"]
        address = email_settings["addresss"]
        password = email_settings["password"]
        server = smtplib.SMTP(host, port)
        server.starttls()  # starts SMTP server connection
        server.login(address, password)  # logs dev email account in
        return server, address

    def send_key(self, un_entry, admin):
        """
        Sends a reset key via email, or uses the admin password
        if in developer mode.

        Args taken:
        -un_entry (tkinter entry box)
        -admin (boolean)

        Usage:
        >>> secure = Security()
        >>> reset_key = secure.send_key("ndv99", False)

        """
        con_key = self.keygen()
        if admin:
            con_key = settings["Admin"]["password"]
        else:
            valid = self.check_username(un_entry)
            if valid:
                # variables
                username = settings["User Details"]["username"]
                client_address = settings["User Details"]["email"]
                email_template = ((self.template_manage.read_file(None)) % (username, con_key))
                # server
                server, my_address = self.server_setup()

                # setup
                message = MIMEMultipart()
                message['From'] = my_address
                message['To'] = client_address
                message['Subject'] = "Tkinter Password Manager - Key"
                message.attach(MIMEText(email_template, 'plain'))

                # add in exception handling for no connection
                server.send_message(message)
                mb.showinfo(INFO_BOX_TITLE, "Key sent.")
                del message
                server.quit()  # connection is closed
            else:
                mb.showerror(ERROR_BOX_TITLE, "Username is incorrect.")
        return con_key

    def check_key(self, key_entry, key, login, admin):
        """
        Checks the user's input of the reset key.

        Args taken:
        -key_entry (tkinter entry box)
        -key (key generated by program) (str)
        -login (tkinter window "login")
        -admin (boolean)

        Usage:
        >>> secure = Security()
        >>> secure.check_key("2 3 5 9 6 4", "2 3 5 9 6 4", login, False)

        """
        key_text = key_entry.get()
        correct = False
        if admin:
            valid = self.check_pass(key_entry, True)
            if valid:
                correct = True
            else:
                mb.showerror(ERROR_BOX_TITLE, "Incorrect key entered.", parent=login)
        else:
            if key_text == key:
                correct = True
            else:
                mb.showerror(ERROR_BOX_TITLE, "Incorrect key entered.", parent=login)
        return correct

    def keygen(self):
        """
        Generates 6 random integers as a password reset key (str).

        No args taken.

        Usage:
        >>> secure = Security()
        >>> key = secure.keygen()

        """
        key_list = []
        for x in range(6):
            digit = random.randint(0, 9)  # generates 6 random numbers
            key_list.append(str(digit))
        key = " ".join(key_list)
        return key

    def password_reset(self, new_pw_entry, c_new_pw_entry, win):
        """
        Resets the user's password if the correct reset key is entered.

        Args taken:
        -new_pw_entry (tkinter entry box)
        -c_new_pw_entry (tkinter entry box)
        -win (tkinter window)

        Usage:
        >>> secure = Security()
        >>> secure.password_reset("n£dfF23", "n£dfF23", win)

        """
        complete = False
        new_pw_text = new_pw_entry.get()
        c_new_pw_text = c_new_pw_entry.get()
        if new_pw_text == c_new_pw_text:
            secure_pass = self.pass_rules(new_pw_text, win)
            if secure_pass:
                newpass = bcrypt.hash(new_pw_text)
                mb.showinfo(INFO_BOX_TITLE, "Password changed.")
                settings_file.write_file("User Details", "password", newpass)
                complete = True
        else:
            mb.showerror(ERROR_BOX_TITLE, "Passwords do not match.", parent=win)
        return complete

    def check_pass_strength(self, pass_entry, win):
        """
        Checks the strength of an entered password.

        Args taken:
        -pass_entry (Tk entry field)
        -win (Tk window)

        Usage:
        >>> secure = Security()
        >>> secure.check_pass_strength(pass_entry, win)

        """
        passtext = pass_entry.get()
        score = 0
        special = False
        digits = False
        upper = False
        lower = False
        upper_list, lower_list, digits_list, special_list = self.generate_ascii_lists()
        strength = 0  # will be a value 1 to 5
        password_strength = ""
        if len(passtext) == 0:
            mb.showerror(ERROR_BOX_TITLE, "Please type in a password.", parent=win)
        else:
            if len(passtext) >= 8:
                strength += 2  # strength increased by two if length is more than 8
            else:
                strength += 1
            for character in passtext:  # iterates through characters and sets conditions to true if met
                if character in lower_list:
                    lower = True
                elif character in upper_list:
                    upper = True
                elif character in digits_list:
                    digits = True
                elif character in special_list:
                    special = True
            for condition in [special, lower, upper, digits]:
                if condition:
                    score += 1  # score is increased by one for each character type in password

            # below: the higher the score, the higher the strength
            if score == 2:
                strength += 1
            elif score == 3:
                strength += 2
            elif score == 4:
                strength += 3
            else:
                strength = 1

            # strength value corresponds to a strength from 'very weak' to 'very strong'
            if strength == 1:
                password_strength = "very weak"
            elif strength == 2:
                password_strength = "weak"
            elif strength == 3:
                password_strength = "medium"
            elif strength == 4:
                password_strength = "strong"
            elif strength == 5:
                password_strength = "very strong"
            mb.showinfo(INFO_BOX_TITLE, "Your password is %s." % password_strength, parent=win)

    def pass_rules(self, pass_text, win):
        """
        Checks if the user's password is of a secure strength.
        Used to enforce the following password rules:
        - >= 8 chars long
        - >= 1 lowercase char
        - >= 1 uppercase char
        - >= 1 numeric char
        - >= 1 special char ("!", "?")

        Args taken:
        -pass_text (str)
        -win (Tk window)

        Usage:
        >>> secure = Security()
        >>> secure.pass_rules(pass_text, win)
        """
        secure_pass = False
        # all conditions below must be met for password to be accepted, i.e:
        # -must have an uppercase char
        # -must have a lowercase char
        # -must have a digit
        # -must have a special char
        # -must be more than 8 chars long
        if len(pass_text) < 8:
            mb.showerror(ERROR_BOX_TITLE, "Your password must contain at least 8 characters.", parent=win)
        upper_list, lower_list, digits_list, special_list = self.generate_ascii_lists()
        upper = False
        lower = False
        digit = False
        special = False
        for character in pass_text:
            if character in upper_list:
                upper = True
            if character in lower_list:
                lower = True
            if character in digits_list:
                digit = True
            if character in special_list:
                special = True
        conditions = [upper, lower, digit, special]
        met = 0
        for condition in conditions:
            if not condition:
                mb.showerror(ERROR_BOX_TITLE, "Your password must contain at least one lower and upper-case character, "
                                              "one digit, and one special character.")
                win.lift()
                break
            else:
                met += 1
        if met == 4:
            secure_pass = True
        return secure_pass

    @staticmethod
    def generate_ascii_lists():
        """
        Generates four lists of ascii characters for
        checking passwords in the functions check_pass_strength
        and pass_rules

        No args taken.
        Static method.

        Usage:
        >>> upper_list, lower_list, digits_list, complete_special = Security.generate_ascii_lists()
        """
        lower_list = [chr(i) for i in range(97, 123)]
        upper_list = [chr(i) for i in range(65, 91)]
        digits_list = [chr(i) for i in range(48, 58)]
        special_list1 = (chr(i) for i in range(32, 48))
        special_list2 = (chr(i) for i in range(58, 65))
        special_list3 = (chr(i) for i in range(91, 97))
        special_list4 = (chr(i) for i in range(123, 127))

        # list for different char types is generated based on ascii values, quicker to do than storing as constants
        complete_special = []
        for x in special_list1:
            complete_special.append(x)
        for x in special_list2:
            complete_special.append(x)
        for x in special_list3:
            complete_special.append(x)
        for x in special_list4:
            complete_special.append(x)
        return upper_list, lower_list, digits_list, complete_special

    def update_settings(self, log_time_entry, auto_time_entry, timeout_active, records_shown_entry, logins_shown_entry,
                        win):
        """
        Updates autosave and auto-logout settings.

        Args taken:
        -log_time_entry (tkinter entry field)
        -auto_time_entry (tkinter entry field)
        -timeout_active (tkinter IntVar)
        -tools (tkinter window)

        Usage:
        >>> secure = Security()
        >>> secure.update_settings(log_time_entry, auto_time_entry, timeout_active, win)
        """
        result = mb.askquestion("Tools", "Save changes?", icon="warning", parent=win)
        if result == "yes":
            log_time = log_time_entry.get()
            auto_time = auto_time_entry.get()
            timeout = timeout_active.get()
            records_shown = records_shown_entry.get()
            logins_shown = logins_shown_entry.get()
            settings_file.write_file("Preferences", "autosave time", auto_time)
            settings_file.write_file("Preferences", "timeout", log_time)
            settings_file.write_file("Preferences", "records displayed", records_shown)
            settings_file.write_file("Preferences", "logins displayed", logins_shown)
            if timeout == 0:
                settings_file.write_file("Preferences", "timeout active", "")
            else:
                settings_file.write_file("Preferences", "timeout active", "True")
            mb.showinfo(INFO_BOX_TITLE, "Preferences saved. Restart to apply changes.")
        win.lift()


class DeveloperOptions(Security):
    """
    Class which holds all developer settings, accessible through the
    front end of the program.

    No args taken.

    Superclassed by Security.

    Methods:
    -get_email_settings(self)
    -set_email_settings(self, host_entry, port_entry, address_entry, password_entry, dev)
    -change_admin_pass(self, pass_entry, dev
    -admin_change_user_details(self, un_entry, email_entry, dev)
    -clear_user_details(self, dev)
    -clear_all(self, record_dict, dev)

    Usage:
    >>> dev = DeveloperOptions()
    >>> email_settings = dev.get_email_settings()
    """

    def __init__(self):
        super().__init__()

    def get_email_settings(self):
        """
        Fetches SMTP server settings.

        No args taken.

        Usage:
        >>> dev = DeveloperOptions()
        >>> server_settings = dev.get_email_settings()

        """
        email_settings = settings["Email Settings"]
        return email_settings

    def set_email_settings(self, host_entry, port_entry, address_entry, password_entry, dev):
        """
        Sets SMTP server settings.

        Args taken:
        -host_entry (tkinter entry box)
        -port_entry (tkinter entry box)
        -address_entry (tkinter entry box)
        -password_entry (tkinter entry box)
        -dev (tkinter window "dev")

        Usage:
        >>> devoptions = DeveloperOptions()
        >>> devoptions.set_email_settings("smtp@gmail.com", "255", "example@gmail.com", "password", dev)

        """
        host = host_entry.get()
        port = port_entry.get()
        address = address_entry.get()
        password = password_entry.get()
        settings_file.write_file("Email", "host", host)
        settings_file.write_file("Email", "port", port)
        settings_file.write_file("Email", "address", address)
        settings_file.write_file("Email", "password", password)
        mb.showinfo(INFO_BOX_TITLE, "Email settings updated.", parent=dev)

    def change_admin_pass(self, pass_entry, dev):
        """
        Changes admin password.

        Args taken:
        -pass_entry (tkinter entry box)
        -dev (tkinter window "dev")

        Usage:
        >>> devoptions = DeveloperOptions()
        >>> devoptions.change_admin_pass("password", dev))

        """
        # password strength is not checked, dev is expected to know how to set a secure password
        pass_text = pass_entry.get()
        result = mb.askquestion("Developer Options", "Change admin password?")
        if result == "yes":
            settings_file.write_file("Admin", "password", bcrypt.hash(pass_text))
            mb.showinfo(INFO_BOX_TITLE, "Admin password changed.", parent=dev)
        else:
            mb.showinfo(INFO_BOX_TITLE, "Admin password not changed.", parent=dev)

    def admin_change_user_details(self, un_entry, email_entry, dev):
        """
        Allows an admin to change the user's username and email.

        Args taken:
        -un_entry (tkinter entry box)
        -email_entry (tkinter entry box)
        -dev (tkinter window "dev")

        Usage:
        >>> devoptions = DeveloperOptions()
        >>> devoptions.admin_change_user_details("user1", "example@mail.com", dev)

        """
        # dev cannot change user's password or see user's password
        result = mb.askquestion("Developer Options", "Change user details?")
        if result == "yes":
            un_text = un_entry.get()
            email_text = email_entry.get()
            settings_file.write_file("User Details", "username", un_text)
            settings_file.write_file("User Details", "email", email_text)
            mb.showinfo(INFO_BOX_TITLE, "Details changed.", parent=dev)
        else:
            mb.showinfo(INFO_BOX_TITLE, "Details not changed.", parent=dev)

    def clear_user_details(self, dev):
        """
        Allows an admin to clear all user details.

        Args taken:
        -dev (tkinter window "dev")

        Usage:
        >>> devoptions = DeveloperOptions()
        >>> devoptions.clear_user_details(dev)
        """
        result = mb.askquestion("Clear user details", "Are you sure? This change is irreversible.")
        if result == "yes":
            settings_file.write_file("User Details", "password", "")
            settings_file.write_file("User Details", "username", "")
            settings_file.write_file("User Details", "email", "")
            mb.showinfo(INFO_BOX_TITLE, "User details cleared.", parent=dev)
        else:
            mb.showinfo(INFO_BOX_TITLE, "User details not cleared.", parent=dev)

    def clear_all(self, dev):
        """
        Clears all app data.

        Args taken:
        -record_dict (dictionary of records)
        -dev (Tk window "dev")

        Usage:
        >>> devoptions = DeveloperOptions()
        >>> devoptions.clear_all(dev)
        """
        settings_file.write_file("User Details", "password", "")
        settings_file.write_file("User Details", "username", "")
        settings_file.write_file("User Details", "email", "")
        mb.showinfo(INFO_BOX_TITLE, "All app data cleared.")
        dev.lift()


dbm = dbmanager.DBManager()
settings_file = INIFile('data/settings.ini')
settings = settings_file.read_file()
