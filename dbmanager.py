# !/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Module for managing program-specific database interactions.

Contains one class, DBManager.

Usage example:

>>> db = DBManager()
>>> db.create_databases()
"""

import sqlite3
from tkinter import *
from tkinter import messagebox as mb

import ndv_cypher

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


class DBManager:
    """
    Class to manage all sqlite3 database operations.

    Does not take any arguments.

    Functions:
    -create_databases(self)
    -count_records(self)
    -write_to_main(self, sitetext, untext, pwtext)
    -write_to_keys(self, sitetext, untext, pwtext)
    -write_to_log(self, date, user, success)
    -read_log(self)
    -clear_log(self, loginrec)
    -read_all_from_db(self)
    -clear_db(self, table, win)
    -check_db(self)
    -export_plain_db(self, record_dict, filename)
    -append_to_list(box, param) [STATIC]

    Usage example:

    >>> manage_db = DBManager()
    >>> manage_db.create_databases()
    >>> number_of_records = manage_db.count_records()
    >>> print (number_of_records)
    62

    """

    def __init__(self):
        self.conn = sqlite3.connect("data/data.db")
        self.cur = self.conn.cursor()

    def create_databases(self):
        """
        Creates password, key, and log databases if they don't already exist.

        No args taken.

        Usage example:
        >>> manage_db = DBManager()
        >>> manage_db.create_databases()

        """

        self.cur.execute("CREATE TABLE IF NOT EXISTS passw_table(personID INTEGER PRIMARY KEY AUTOINCREMENT, "
                         "site STR, username STR, password STR)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS key_table(personID INTEGER PRIMARY KEY AUTOINCREMENT, "
                         "sitekey STR, usernamekey STR, passwordkey STR, FOREIGN KEY (personID) "
                         "REFERENCES passw_table(personID))")  # primary keys are linked
        self.cur.execute("CREATE TABLE IF NOT EXISTS log_table(logID INTEGER PRIMARY KEY AUTOINCREMENT, "
                         "date STR, user STR, success STR)")

    def count_records(self):
        """
        Counts records in password database.

        No args taken.

        Usage example:
        >>> manage_db = DBManager()
        >>> number_of_records = manage_db.count_records()
        >>> print (number_of_records)
        62

        """
        num_of_records = 0
        self.cur.execute("SELECT * FROM passw_table")
        passwords = self.cur.fetchall()
        for x in passwords:
            num_of_records += 1
        return num_of_records

    def write_to_main(self, sitetext, untext, pwtext):
        """
        Writes records to password database.

        Args taken:
        -sitetext
        -untext
        -pwtext

        Usage example:
        >>> manage_db = DBManager()
        >>> sitetext = "Google"
        >>> untext = "johndoe1@gmail.com"
        >>> pwtext = "jhAS/123!"
        >>> manage_db.write_to_main(sitetext, untext, pwtext)

        """
        self.cur.execute("INSERT INTO passw_table (site, username, password) VALUES (?,?,?)", (sitetext, untext,
                                                                                               pwtext))
        self.conn.commit()

    def write_to_keys(self, sitetext, untext, pwtext):
        """
        Writes keys for encrypted records to key database.

        Args taken:
        -sitetext
        -untext
        -pwtext

        Usage example:
        >>> manage_db = DBManager()
        >>> sitetext, sitekey = ndv_cypher.VernamEncrypt.encrypt("Google")
        >>> untext, unkey = ndv_cypher.VernamEncrypt.encrypt("johndoe1@gmail.com")
        >>> pwtext, pwkey = ndv_cypher.VernamEncrypt.encrypt("jhAS/123!")
        >>> manage_db.write_to_keys(sitekey, unkey, pwkey)
        """
        self.cur.execute("INSERT INTO key_table (sitekey, usernamekey, passwordkey) VALUES (?,?,?)",
                         (sitetext, untext, pwtext))
        self.conn.commit()

    def write_to_log(self, date, user, success):
        """
        Writes login date/time, user, and success to log.

        Args taken:
        -date (str)
        -user (str)
        -success (str)

        Usage example:
        >>> manage_db = DBManager()
        >>> date = "2017-11-02 18:17:54"
        >>> user = "admin"
        >>> success = "Successful"
        >>> manage_db.write_to_log(date, user, success)

        """
        self.cur.execute("INSERT INTO log_table (date, user, success) VALUES (?,?,?)", (date, user, success))
        self.conn.commit()

    def read_log(self):
        """
        Reads all records from the login record database.

        No args taken.

        Usage example:
        >>> manage_db = DBManager()
        >>> manage_db.read_log()

        """
        box = []
        all_records = self.cur.execute("SELECT * FROM log_table ORDER BY date DESC")
        box = self.append_to_list(box, all_records)
        return box

    def clear_log(self, loginrec):
        """
        Clears login records.

         Args taken:
         -loginrec (tkinter window 'loginrec')

         Usage:
         >>> manager = DBManager()
         >>> loginrec = Tk()
         >>> manager.clear_log(loginrec)
        """
        result = mb.askquestion("Clear login records", "Are you sure?", icon='warning', parent=loginrec)
        if result == 'yes':
            self.clear_db('log_table')
            mb.showinfo(INFO_BOX_TITLE, 'Login records cleared.')
            loginrec.destroy()  # no point keeping window open when there are no records to show
        else:
            mb.showinfo(INFO_BOX_TITLE, 'Login records not cleared.', parent=loginrec)

    def read_all_from_db(self):
        """
        Reads all records from both databases.
        Returns records from each in two separate
        lists of tuples.

        No args taken.

        Usage example:
        >>> manage_db = DBManager()
        >>> manage_db.read_all_from_db()

        """
        databox = []
        keybox = []
        all_records = self.cur.execute("SELECT * FROM passw_table")
        databox = self.append_to_list(databox, all_records)
        all_keys = self.cur.execute("SELECT * FROM key_table")
        self.append_to_list(keybox, all_keys)
        if all_keys is None:
            keybox = []
        else:
            keybox = self.append_to_list(keybox, all_keys)
        return databox, keybox

    def clear_db(self, table):
        """
        Clears all records from a given databases. 'table' should be
        "key_table", "passw_table", or "log_table" for this program.

        Args taken:
        -table (str - sqlite3 table)

        Usage example:
        >>> manage_db = DBManager()
        >>> manage_db.clear_db("key_table")

        """
        if table == "passw_table":
            self.cur.execute("DELETE FROM passw_table")
            self.conn.commit()
            self.cur.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='passw_table'")
            # clears indexes so records always start from 1 (above)
            self.conn.commit()
        elif table == "key_table":
            self.cur.execute("DELETE FROM key_table")
            self.conn.commit()
            self.cur.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='key_table'")
            self.conn.commit()
        elif table == "log_table":
            self.cur.execute("DELETE FROM log_table")
            self.conn.commit()
            self.cur.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='log_table'")
            self.conn.commit()

    def check_db(self):
        """
        Checks the database before encryption/decryption. This will
        prevent either from happening if there is some kind of error.
        Also calls "read_all_from_db()" and returns data and keys.

        No args taken.

        Usage example:
        >>> manage_db = DBManager()
        >>> go_ahead, databox, keybox = manage_db.check_db()

        """
        databox, keybox = self.read_all_from_db()
        # each go_ahead value differs slightly in meaning across functions, but usually 1 is 'Go ahead'
        if databox == [] and keybox != []:
            go_ahead = 0
        elif databox != [] and keybox != []:
            go_ahead = 1
        else:
            go_ahead = 2
        return go_ahead, databox, keybox

    def export_plain_db(self, record_dict, filename):
        """
        Decrypts the password database and exports the
        records to a new database.

        Args taken:
        -record_dict
        -filename

        Usage:
        >>> db_manager = DBManager()
        >>> dictionary = {1: ("Google", "example@gmail.com", "password")}
        >>> db_manager.export_plain_db(dictionary, "output.db")
        """
        conn_export = sqlite3.connect(filename)  # new database is created
        cur_export = conn_export.cursor()
        cur_export.execute("CREATE TABLE IF NOT EXISTS passw_table(personID INTEGER PRIMARY KEY AUTOINCREMENT, "
                           "site STR, username STR, password STR)")
        for item in record_dict:
            site = record_dict[item][0]
            username = record_dict[item][1]
            password = record_dict[item][2]
            cur_export.execute("INSERT INTO passw_table (site, username, password) VALUES (?,?,?)", (site, username,
                                                                                                     password))
            conn_export.commit()

    @staticmethod
    def append_to_list(box, param):
        """
        Takes retrieved records from a database and appends them to a
        list, in multidimentional form.

        Args taken:
        -box
        -param

        Usage example:
        >>> manage_db = DBManager()
        >>> searchingtext = "Letmein123!"
        >>> p = manage_db.cur.execute("SELECT * FROM passw_table WHERE password Like (?)",
        >>>                                ('%'+searchingtext+'%',))
        >>> box = manage_db.append_to_list(box, p)

        """
        items = param.fetchall()  # param is the values retrieved from the database
        for item in items:
            if item not in box:
                box.append(item)
        return box  # box can be any list given to the function
