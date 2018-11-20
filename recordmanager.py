# !/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Module for program-specific record management.

Contains one class, RecordManager

Usage:
>>> rm = RecordManager()
>>> record_dict = rm.create_dict()
"""


from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb

import dbmanager
import ndv_cypher
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


class RecordManager:
    """
    Class to manage all actions on records.

    Does not take any arguments.

    Instantiates DBManager in __init__().

    Functions:
    -write_encrypted(self, record_dict, preserve=False)
    -db_encryption(self, record_dict)
    -db_decryption(self)
    -add_new_record(self, site_entry, un_entry, pw_entry, new, record_dict)
    -change_record(self, new_site_text, new_un_text, new_pw_text, edit, record_dict, index)
    -delete_record(self, edit, record_dict, index)
    -create_dict(self)
    -search_dict(self, record_dict, searching_text, conditions)
    -clear_records(self, table, win, record_dict, clear_dict=True)
    -export_as_csv(self, menu, record_dict)
    -export_as_sql_db(self, menu, record_dict)
    -export_as_html(self, menu, record_dict)
    -export_as_json(self, menu, record_dict)
    -export_as_xml(self, menu, record_dict)
    -create_backup(self, menu, record_dict)
    -import_backup(self, menu, record_dict)

    Usage example:

    >>> manage_records = RecordManager()
    >>> manage_records.db_manager.create_databases()
    >>> records = manage_records.create_dict()

    """

    def __init__(self):
        self.db_manager = dbmanager.DBManager()
        self.unsaved_changes = False  # this value changes throughout runtime

    def write_encrypted(self, record_dict, preserve=False):
        """
        Writes encrypted records into the password database, and their
        respective keys into the key database. Set "preserve" to True
        to preserve the record dictionary when clearing the database.

        Args taken:
        -record_dict (dictionary)
        -preserve=False (boolean)

        Usage example:
        >>> manage_records = RecordManager()
        >>> manage_records.write_encrypted(record_dict)

        """
        encr_records, keys = self.record_encryption(record_dict)
        self.clear_records("both", False, record_dict, clear_dict=not preserve)  # all records are cleared from db
        for x in range(len(encr_records)):
            sitetext = encr_records[x][0]
            untext = encr_records[x][1]
            pwtext = encr_records[x][2]
            self.db_manager.write_to_main(sitetext, untext, pwtext)
            sitekey = keys[x][0]
            unkey = keys[x][1]
            pwkey = keys[x][2]
            self.db_manager.write_to_keys(sitekey, unkey, pwkey)

    def record_encryption(self, record_dict):
        """
        Encrypts records once extracted from a database, given that the
        conditions are met to avoid corruption. Returns encrypted
        records and their keys.

        Args taken:
        -record_dict (dictionary)

        Usage example:
        >>> manage_records = RecordManager()
        >>> manage_records.record_encryption(record_dict)

        """
        records = []
        keys = []
        if record_dict:  # only does it if there are values
            for record_id in record_dict:
                encr_list = []
                key_list = []
                record = record_dict[record_id]
                for x in record:  # one field of a record encrypted at a time
                    encr_record, key = ndv_cypher.VernamEncrypt.encrypt(str(x))
                    encr_list.append(encr_record)
                    key_list.append(str(key))
                encr_tuple = (str(encr_list[0]), str(encr_list[1]), str(encr_list[2]))  # tuple used to save space
                key_tuple = (key_list[0], key_list[1], key_list[2])
                # tuples appended to lists
                records.append(encr_tuple)
                keys.append(key_tuple)
        return records, keys

    def db_decryption(self):
        """
        Decrypts records once extracted from a database, given that the
        conditions are met to avoid corruption. Returns decrypted
        records.

        No args taken.

        Usage example:
        >>> manager = RecordManager()
        >>> manager.db_decryption()

        """
        records = []
        go_ahead, databox, keybox = self.db_manager.check_db()
        if go_ahead == 1:  # 1 = go ahead
            if len(databox) == len(keybox):
                for i in range(len(databox)):
                    decr_list = []
                    data_record = databox[i]
                    key_record = keybox[i]
                    for x in range(1, 4):
                        decrypted = ndv_cypher.VernamDecrypt.decrypt(str(data_record[x]), key_record[x])
                        decr_list.append(decrypted)
                    decr_tuple = (decr_list[0], decr_list[1], decr_list[2])
                    records.append(decr_tuple)
            elif len(databox) > len(keybox):
                mb.showerror("Error: More data than keys")
            elif len(databox) < len(keybox):
                mb.showerror("Error: More keys than data")
        elif go_ahead == 0:  # 0 = no records, encryption keys still there
            result = mb.askquestion(ERROR_BOX_TITLE,
                                    "Error: passw_table is empty, but key_table "
                                    "contains records. Clear 'key_table'?",
                                    icon="warning")
            if result == "yes":
                self.db_manager.clear_db("key_table")
                mb.showinfo(INFO_BOX_TITLE, "'key_table' cleared.")
            else:
                mb.showinfo(INFO_BOX_TITLE, "'key_table' not cleared. Program may not function correctly.",
                            icon="warning")
        else:  # if no keys, records are just returned as they are
            records = databox
        return records

    def add_new_record(self, site_entry, un_entry, pw_entry, new, record_dict):
        """
        Adds a new record to the program.

        Args taken:
        -site_entry (str)
        -un_entry (str)
        -pw_entry (str)
        -new (Tk window "new")
        -record_dict (dictionary)

        Usage example:
        >>> manage_records = RecordManager()
        >>> record_dict = manage_records.create_dict()
        >>> manage_records.add_new_record("Twitter", "@NDV_99", "nfn2334SDF/#'", new, record_dict)

        """
        result = mb.askquestion("Add record", "Are you sure?", icon="warning")  # checks before adding
        if result == "yes":
            sitetext = site_entry.get()
            untext = un_entry.get()
            pwtext = pw_entry.get()
            new_index = len(record_dict) + 1
            record = (sitetext, untext, pwtext)
            record_dict[new_index] = record  # new record inserted at end of dictionary
            site_entry.delete(0, END)
            un_entry.delete(0, END)
            pw_entry.delete(0, END)
            mb.showinfo(INFO_BOX_TITLE, "Record saved.", parent=new)
        else:
            mb.showinfo(INFO_BOX_TITLE, "Record not saved.", parent=new)

    def change_record(self, new_site_text, new_un_text, new_pw_text, edit, record_dict, index):
        """
        Changes a record in the program.

        Args taken:
        -new_site_text (str)
        -new_un_tetx (str)
        -new_pw_tetx (str)
        -edit (Tk window "edit")
        -record_dict (dictionary)
        -index (int - dictionary key)

        Usage example:
        >>> manage_records = RecordManager()
        >>> record_dict = manage_records.create_dict()
        >>> manage_records.change_record("Google", "n.devilliers1999", "aonc7rpqr3e", edit, record_dict, 32)
        """
        result = mb.askquestion("Change Record", "Change record?", icon="warning")  # checks before changing
        if result == 'yes':
            newsite = new_site_text.get()
            newun = new_un_text.get()
            newpw = new_pw_text.get()
            # old values shown in entry fields, no actual changes happen if unchanged by user
            record_dict[index] = (newsite, newun, newpw)
            self.unsaved_changes = True
            mb.showinfo(INFO_BOX_TITLE, "Record saved.")
            edit.destroy()
        else:
            mb.showinfo(INFO_BOX_TITLE, "Record preserved.", parent=edit)

    def delete_record(self, edit, record_dict, index):
        """
        Deletes a record in the program.

        Args taken:
        -edit (Tk window "edit")
        -record_dict (dictionary)
        -index (int - dictionary key)

        Usage example:
        >>> manage_records = RecordManager()
        >>> record_dict = manage_records.create_dict()
        >>> manage_records.delete_record(edit, record_dict, 73)
        >>>

        """
        result = mb.askquestion("Delete Record", "Delete record?", icon="warning")  # checks first
        if result == 'yes':
            del record_dict[index]  # record is deleted from dictionary
            self.unsaved_changes = True
            mb.showinfo(INFO_BOX_TITLE, "Record deleted.")
            edit.destroy()
        else:
            mb.showinfo(INFO_BOX_TITLE, "Record preserved.", parent=edit)

    def create_dict(self):
        """
        Creates a dictionary where decrypted records are kept in
        runtime.

        No args taken.

        Usage example:

        >>> manage_records = RecordManager()
        >>> record_dict = manage_records.create_dict()
        """
        records = self.db_decryption()
        record_dict = dict(enumerate(records, start=1))  # dictionary index starts at 1 to mirror database
        return record_dict

    def search_dict(self, record_dict, searching_text, conditions):
        """
        Searches the dictionary for records meeting given criteria.

        Args taken:
        -record_dict (dictionary)
        -searching_text (Tkinter stringvar)
        -conditions (list of Tkinter IntVars)

        Usage example:

        >>> manage_records = RecordManager()
        >>>record_dict = manage_records.create_dict()
        >>>box, indices = manage_records.search_dict(record_dict, searching_text, conditions)

        """
        box = []
        indices = []
        fields = []
        searched = []
        search_text = searching_text.get()
        search_site = conditions[0].get()
        search_un = conditions[1].get()
        search_pw = conditions[2].get()
        # fields to search are appended to list
        if search_site:
            fields.append(0)
            searched.append("Site")
        if search_un:
            fields.append(1)
            searched.append("Username")
        if search_pw:
            fields.append(2)
            searched.append("Passwords")
        if len(searched) != 0:
            if search_text != "":
                for record in record_dict:
                    # generator expression rather than list comprehension for faster evaluation of records
                    if any(search_text.lower() in x.lower() for x in map(record_dict[record].__getitem__, fields)):
                        box.append(record_dict[record])
                        indices.append(record)
            else:  # doesn't bother searching if no conditions, all records are just returned
                for record in record_dict:
                    box.append(record_dict[record])
                    indices.append(record)
        return box, indices, searched

    def clear_records(self, table, win, record_dict, clear_dict=True, everything=False):
        """
        Clears all records in the program.
        This involces clearing both the dictionary of records
        and the databases. "win" determines the actions that happen
        when the records are cleared. "clear_dict" can be set to False
        to preserve the dictionary, in cases such as autosaving or
        creating backups. "table" determines which table to clear.

        Args taken:
        -table (str)
        -win (str)
        -record_dict (dictionary)
        -clear_dict=True (boolean)

        Usage example:
        >>> manage_records = RecordManager()
        >>> manage_records.db_manager.clear_db("key_table", None, record_dict)

        """
        complete = False
        if not win:  # this bit is useful for easy implementation
            if table == "both":
                self.db_manager.clear_db("key_table")
                self.db_manager.clear_db("passw_table")
                if clear_dict:
                    record_dict.clear()
            else:
                self.db_manager.clear_db(table)  # can clear a specific table
                record_dict.clear()
        elif win == "dev":  # access from dev window allows admin to clear specific tables
            if table == "passw_table":
                result = mb.askquestion("Warning", "Clear 'passw_table'?")
                if result == "yes":
                    self.db_manager.clear_db(table)
                    record_dict.clear()
                    mb.showinfo(INFO_BOX_TITLE, "'passw_table' cleared. It is highly recommended to clear 'key_table' "
                                                "as well.")
                else:
                    mb.showinfo(INFO_BOX_TITLE, "'passw_table' not cleared.")
            elif table == "key_table":
                result = mb.askquestion("Warning", "Clear 'key_table'?")
                if result == "yes":
                    self.db_manager.clear_db(table)
                    mb.showinfo(INFO_BOX_TITLE, "'key_table' cleared.")
                else:
                    mb.showinfo(INFO_BOX_TITLE, "'key_table' not cleared.")
            elif table == "log_table":
                result = mb.askquestion("Warning", "Clear 'log_table'?")
                if result == "yes":
                    self.db_manager.clear_db(table)
                    mb.showinfo(INFO_BOX_TITLE, "'log_table' cleared.")
                else:
                    mb.showinfo(INFO_BOX_TITLE, "'log_table' not cleared.")
        elif win == "main":
            result = mb.askquestion("Warning", "Are you sure? These changes are irreversible.", icon='warning')
            if result == "yes":
                self.db_manager.clear_db("key_table")
                self.db_manager.clear_db("passw_table")
                record_dict.clear()
                if not everything:  # different messageboxes show depending on what's cleared
                    mb.showinfo(INFO_BOX_TITLE, "All records cleared.")
                else:
                    mb.showinfo(INFO_BOX_TITLE, 'All app data cleared.')
                complete = True
            else:
                if not everything:
                    mb.showinfo(INFO_BOX_TITLE, "Records not cleared.")
                else:
                    mb.showinfo(INFO_BOX_TITLE, 'App data preserved.')
        return complete

    def export_as_csv(self, menu, record_dict):  # all export functions have roughly the same layout
        """
        Exports the records to a CSV file (decrypted).

        Args taken:
        -menu (Tk window "menu")
        -record_dict (dictionary)

        Usage:
        >>> menu = Tk()
        >>> manage_records = RecordManager()
        >>> manage_records.export_as_csv(menu, record_dict)
        """
        menu.filename = fd.asksaveasfilename(initialdir="C:/", title="Save as...", filetypes=(("CSV Files", "*.csv"),
                                                                                              ("All files", "*.*")),
                                             initialfile="passwords.csv")  # 'Save as' menu
        # finicky thing where location is sometimes a tuple when cancelled (below)
        if menu.filename != "" and type(menu.filename) != tuple:
            self.write_encrypted(record_dict, preserve=True)
            csvfile = CSVFile(menu.filename)
            csvfile.write_file(["Site", "Username", "Password"], "UTF-8")  # file header
            for item in record_dict:
                csvfile.write_file(record_dict[item], "UTF-8")
            mb.showinfo(INFO_BOX_TITLE, "Data exported to %s." % menu.filename)

    def export_as_sql_db(self, menu, record_dict):
        """
        Exports the records to an SQL db file (decrypted).

        Args taken:
        -menu (Tk window "menu")
        -record_dict (dictionary)

        Usage:
        >>> menu = Tk()
        >>> manage_records = RecordManager()
        >>> manage_records.export_as_sql_db(menu, record_dict)
        """
        self.write_encrypted(record_dict, preserve=True)  # saves all records to database first
        menu.filename = fd.asksaveasfilename(initialdir="C:/", title="Save as...", filetypes=(("DB Files", "*.db"),
                                                                                              ("All files", "*.*")),
                                             initialfile="passwords.db")
        if menu.filename != "" and type(menu.filename) != tuple:
            self.db_manager.export_plain_db(record_dict, menu.filename)
            mb.showinfo(INFO_BOX_TITLE, "Data exported to %s." % menu.filename)

    def export_as_html(self, menu, record_dict):
        """
        Exports the records to an HTML file (decrypted).

        Args taken:
        -menu (Tk window "menu")
        -record_dict (dictionary)

        Usage:
        >>> menu = Tk()
        >>> manage_records = RecordManager()
        >>> manage_records.export_as_html(menu, record_dict)
        """
        mb.showinfo(INFO_BOX_TITLE, "File will be exported to a zip with stylesheet.")
        menu.filename = fd.asksaveasfilename(initialdir="C:/", title="Save as...", filetypes=(("ZIP Files", "*.zip"),
                                                                                              ("All files", "*.*")),
                                             initialfile="passwords.zip")
        if menu.filename != "" and type(menu.filename) != tuple:

            # code below basically writes an html file tag by tag
            records = []
            for record in record_dict:
                records.append(record_dict[record])
            html_file = HTMLFile("html/passwords.html")
            html_file.doct_type()
            html_file.html()
            html_file.head("Passwords")
            html_file.stylesheet()
            html_file.head_end()

            html_file.body()
            html_file.tag("h1", "Passwords")

            html_file.table()

            row = ["Site", "Username", "Password"]
            html_file.row(row)
            row.clear()

            for item in records:
                row.append(item[0])
                row.append(item[1])
                row.append(item[2])

                html_file.row(row)
                row.clear()

            html_file.table_end()
            html_file.body_end()
            html_file.html_end()
            html_file.write_file()
            html_zip = ZipFile(menu.filename)
            html_zip.write_file(("html/passwords.html", "html/stylesheet.css"), None)  # actual creation of file
            mb.showinfo(INFO_BOX_TITLE, "Data exported to %s. \nExtract stylesheet WITH HTML file." % menu.filename)

    def export_as_json(self, menu, record_dict):
        """
        Exports the records to a JSON file (decrypted).

        Args taken:
        -menu (Tk window "menu")
        -record_dict (dictionary)

        Usage:
        >>> menu = Tk()
        >>> manage_records = RecordManager()
        >>> manage_records.export_as_json(menu, record_dict)
        """
        menu.filename = fd.asksaveasfilename(initialdir="C:/", title="Save as...", filetypes=(("JSON Files", "*.json"),
                                                                                              ("All files", "*.*")),
                                             initialfile="passwords.json")
        if menu.filename != "" and type(menu.filename) != tuple:
            jf = JSONFile(menu.filename)
            jf.write_file(record_dict)
            mb.showinfo(INFO_BOX_TITLE, "Data exported to %s." % menu.filename)

    def export_as_xml(self, menu, record_dict):
        """
        Exports the records to an XML file (decrypted).

        Args taken:
        -menu (Tk window "menu")
        -record_dict (dictionary)

        Usage:
        >>> menu = Tk()
        >>> manage_records = RecordManager()
        >>> manage_records.export_as_xml(menu, record_dict)
        """
        menu.filename = fd.asksaveasfilename(initialdir="C:/", title="Save as...", filetypes=(("XML Files", "*.xml"),
                                                                                              ("All files", "*.*")),
                                             initialfile="passwords.xml")
        if menu.filename != "" and type(menu.filename) != tuple:
            xml = XMLFile(menu.filename)
            xml.write_file(record_dict)
            mb.showinfo(INFO_BOX_TITLE, "Data exported to %s." % menu.filename)

    def create_backup(self, menu, record_dict):
        """
        Creates a backup of password.db and keys.db in a zip file.

        Args taken:
        -menu (Tk window "menu")
        -record_dict (dictionary)

        Usage:
        >>> menu = Tk()
        >>> manage_records = RecordManager()
        >>> manage_records.create_backup(menu, record_dict)
        """
        menu.filename = fd.asksaveasfilename(initialdir="C:/", title="Save as...", filetypes=(("ZIP Files", "*.zip"),
                                                                                              ("All files", "*.*")),
                                             initialfile="backup.zip")
        if menu.filename != "" and type(menu.filename) != tuple:
            self.write_encrypted(record_dict, preserve=True)  # all data saved first
            backup_zip = ZipFile(menu.filename)
            backup_zip.write_file(("data/data.db", "data/settings.ini"), None)
            mb.showinfo(INFO_BOX_TITLE, "Backup created in %s." % backup_zip.filename, parent=menu)

    def import_backup(self, menu, record_dict):
        """
        Imports the databases from a zip file created by create_backup()

        Args taken:
        -menu (Tk window "menu")
        -record_dict (dictionary)

        Usage:
        >>> menu = Tk()
        >>> manage_records = RecordManager()
        >>> manage_records.import_backup(menu, record_dict)
        """
        imported = False
        menu.filename = fd.askopenfilename(initialdir="C:/", title="Open...", filetypes=(("Zip Files", "*.zip"),
                                                                                         ("All files", "*.*")))
        if menu.filename != "" and type(menu.filename) != tuple:
            self.clear_records("both", False, record_dict)  # records all cleared
            backup_zip = ZipFile(menu.filename)
            backup_zip.read_file()
            mb.showinfo(INFO_BOX_TITLE, "Backup imported. Restarting program...")
            imported = True
            menu.destroy()
        return imported
