# !/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Module for handling interaction with several filetypes.

Classes:
-FileManager
-TextFile
-CSVFile
-ZIPFile
-INIFile
-JSONFile
-XMLFile
-HTMLFile

Usage example:
>>> txtfile = TextFile("test.txt")
>>> txtfile.write_file("test", None)
"""

import abc
import configparser
import csv
import json
import zipfile
from xml.dom.minidom import parseString

import dicttoxml

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


class FileManager:
    """
    Class to manage interaction with files.

    Takes one argument:
    -filename (name of txt file)

    Subclassed by:
    -TextFile
    -CSVFile
    -ZipFile
    -INIFile
    -JSONFile
    -XMLFile
    -HTMLFile

    Functions:
    -read_file(self, encoding)
    -write_file(self, content)

    Methods are abstract, not intended for direct use.

    """

    def __init__(self, filename):
        self.filename = filename

    @abc.abstractmethod
    def read_file(self, *args):
        """
        Reads data from a file.

        Args taken:
        *args

        Abstract method - not intended for direct use.
        """
        pass

    @abc.abstractmethod
    def write_file(self, *args):
        """
        Writes to a file.

        Args taken:
        *args

        Abstract method - not intended for direct use.
        """
        pass


class TextFile(FileManager):
    """
    Class to manage interaction with text files.

    Superclassed by FileManager

    Takes one argument:
    -filename (name of txt file)

    Functions:
    -read_file(self, encoding)
    -write_file(self, content)

    Usage:

    >>> text_file = TextFile("testfile.txt")
    >>> text_file.write_file("Hello, world!", None)

    """

    def __init__(self, filename):
        super().__init__(filename)

    def read_file(self, encoding):
        """
        Reads data from a text file.

        Args taken:
        -encoding (str)

        Usage example:
        >>> file = TextFile("un.txt")
        >>> text = file.read_file("utf-8")
        """
        with open(self.filename, 'r', encoding=encoding) as file:
            text = file.read()
            file.close()
        return text

    def write_file(self, content, encoding):
        """
        Writes to text file.

        Args taken:
        -content (str)
        -encoding (str)

        Usage example:
        >>>file = TextFile("un.txt")
        >>>file.write_file("ndv99", None)
        """
        with open(self.filename, "w") as file:
            file.write(content)
            file.close()


class CSVFile(FileManager):
    """
    Class to manage interaction with csv files.

    Superclassed by FileManager

    Takes one argument:
    -filename (name of txt file)

    Functions:
    -read_file(self, encoding)
    -write_file(self, content, encoding)
    -clear_file(self)

    Usage:

    >>> csv_file = TextFile("testfile.csv")
    >>> csv_file.write_file("Hello, world!", None)

    """

    def __init__(self, filename):
        super().__init__(filename)

    def read_file(self, encoding):
        """
        Reads data from a CSV file.

        Args taken:
        -encoding (str)

        Usage example:
        >>>file = CSVFile("log.csv")
        >>>content = file.read_file("utf-8")
        """
        with open(self.filename, 'r') as file:
            csvreader = csv.reader(file, delimiter=",", quotechar='|', quoting=csv.QUOTE_MINIMAL)
            records = []
            for row in csvreader:
                if row:
                    record = (row[0], row[1], row[2])
                    if record != ("", "", ""):
                        records.append(record)  # only appends record if not empty
            file.close()
        return records
        # this method is never actually used in the program, not sure why I made it


    def write_file(self, content, encoding):
        """
        Writes to a CSV file.

        Args taken:
        -content (str)
        -encoding (str)

        Usage example:
        >>>file = CSVFile("log.csv")
        >>>file.write_file(["2014-09-23 16:45:32", "Successful"], None)
        """
        with open(self.filename, 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=",", quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(content)
            csvfile.close()

    def clear_file(self):
        """
        Clears a CSV file.

        No args taken.

        Usage example:
        >>>file = CSVFile("log.csv")
        >>>file.clear_file()
        """
        with open(self.filename, "w+") as file:
            file.truncate()  # 'truncate' is the command to clear all file data
            file.close()


class ZipFile(FileManager):
    """
    Class to manage interaction with zip files.

    Superclassed by FileManager

    Takes one argument:
    -filename (name of txt file)

    Functions:
    -read_file(self, encoding)
    -write_file(self, content, encoding)

    Usage:

    >>>backupzip = ZipFile("testfile.zip")
    >>>backupzip.write_file(("test1.txt", "test2.txt"), None)

    """

    def __init__(self, filename):
        super().__init__(filename)

    def read_file(self):
        """
        Extracts files from a zip file.

        No args taken.

        Usage:
        >>>imported = ZipFile("backup.zip")
        >>>imported.read_file()
        """
        with zipfile.ZipFile(self.filename, "r") as file:
            file.extractall()  # automatically extracts to program directory
            file.close()

    def write_file(self, files: tuple, encoding):
        """
        Compresses given files into a zip file.

        Args taken:
        -content: tuple (tuple of strings of file names)
        -encoding

        Usage:

        >>>backupzip = ZipFile("testfile.zip")
        >>>backupzip.write_file(("test1.txt", "test2.txt"), None)
        """
        with zipfile.ZipFile(self.filename, "w") as file:
            for item in files:
                file.write(item)
            file.close()


class INIFile(FileManager):
    """
    Class to manage interaction with INI files.

    Superclassed by FileManager

    Takes one argument:
    -filename (name of txt file)

    Functions:
    -read_file(self)
    -write_file(self, section, key, content)

    Usage:

    >>> settings_file = INIFile("data/settings.ini")
    >>> settings_file.write_file('Email', 'host', '234')

    """

    def __init__(self, filename):
        super().__init__(filename)
        self.config = configparser.ConfigParser()

    def read_file(self):
        """
        Reads data from an INI file.

        No args taken.

        Usage example:
        >>>file = TextFile("un.txt")
        >>>text = file.read_file()
        """
        self.config.read(self.filename)
        return self.config

    def write_file(self, section, key, content):
        """
        Writes to an INI file.

        Args taken:
        -section (str)
        -key (str)
        -content (str)

        Usage:

        >>>settings_file = TextFile("data/settings.ini")
        >>>settings_file.write_file('Email', 'host', '234')
        """
        self.config.set(section, key, content)
        with open(self.filename, "w") as config_file:
            self.config.write(config_file)


class JSONFile(FileManager):
    """
    Class to manage interaction with JSON files.

    Superclassed by FileManager

    Takes one argument:
    -filename (name of txt file)

    Functions:
    -read_file(self) [NO FUNCTIONALITY]
    -write_file(self, content: dict)

    Usage:

    >>> json_file = JSONFile("passwords.json")
    >>> dictionary = {1: ("Google", "example@gmail.com", "password")}
    >>> json_file.write_file(dictionary)

    """

    def __init__(self, filename):
        super().__init__(filename)

    def read_file(self, *args):
        pass  # read file method is not needed, JSON is only used as an export

    def write_file(self, content: dict):
        """
        Writes a dictionary to a JSON file.

        Args taken:
        -content (dictionary)

        Usage example:
        >>>file = JSONFile("log.json")
        >>>file.write_file({"2014-09-23 16:45:32": "Successful"})
        """
        json_string = json.dumps(content)  # converts all records into a json string
        with open(self.filename, "w") as file:
            json.dump(json_string, file)  # dumps string into json file
            file.close()


class XMLFile(FileManager):
    """
    Class to manage interaction with XML files.

    Superclassed by FileManager

    Takes one argument:
    -filename (name of txt file)

    Functions:
    -read_file(self) [NO FUNCTIONALITY]
    -write_file(self, content: dict)

    Usage:

    >>> xml_file = XMLFile("passwords.xml")
    >>> dictionary = {1: ("Google", "example@gmail.com", "password")}
    >>> xml_file.write_file(dictionary)

    """

    def __init__(self, filename):
        super().__init__(filename)

    def write_file(self, content: dict):
        """
        Writes dictionary to an XML file.

        Args taken:
        -content (dictionary)

        Usage example:
        >>>file = JSONFile("log.xml")
        >>>file.write_file({"2014-09-23 16:45:32": "Successful"})
        """
        content = {str(k): v for k, v in content.items()}
        # above: k is a string as library 'dicttoxml' contains bug with int keys.
        xml = dicttoxml.dicttoxml(content)
        with open(self.filename, "w") as file:
            file.write(parseString(xml).toprettyxml())  # 'toprettyxml' makes the file look neater
            file.close()

    def read_file(self, *args):
        pass  # read method not needed


class HTMLFile(FileManager):
    """
    Class for generating an HTML page.

    Functions:
    -doc_type(self,doctype="<!DOCTYPE html>")
    -html(self)
    -html_end(self)
    -head(self,title,meta="<meta charset='UTF-8'>")
    -headEnd(self)
    -stylesheet(self,stylesheet="stylesheet.css")
    -body(self)
    -bodyEnd(self)
    -tag(self, tag, text)
    -table(self)
    -tableEnd(self)
    -row(self, row)
    -write_file(self)
    -read_file(self) [NO FUNCTIONALITY]

    Args tkaen:
    -filename (str)

    Usage example:
    >>> html_file = HTMLFile("html/passwords.html")
    >>> html_file.doct_type()
    >>> html_file.html()
    >>> html_file.head("Passwords")
    >>> html_file.stylesheet()
    >>> html_file.head_end()
    >>> html_file.write_file()
    """

    # class basically works by creating HTML tags and appending them to a list, then writing list to html file

    def __init__(self, filename):
        super().__init__(filename)
        self.page = []

    def doct_type(self, doctype="<!DOCTYPE html>"):
        """
        Adds doctype tag to page.

        Args taken:
        -doctype="<!DOCTYPE html>") (str)

        Usage example:
        >>> html_file = HTMLFile("testfile.html")
        >>> html_file.doct_type()
        """
        self.page.append(doctype)

    def html(self):
        """
        Adds html tag to page.

        No args taken.

        >>> html_file = HTMLFile("testfile.html")
        >>> html_file.html()
        """
        self.page.append("<html>")

    def html_end(self):
        """
        Adds html end tag to page.

        No args taken.

        Usage:
        >>> html_file = HTMLFile("testfile.html")
        >>> html_file.html_end()
        """
        self.page.append("</html>")

    def head(self, title, meta="<meta charset='UTF-8'>"):
        """
        Adds head tag to page.

        Args taken:
        -title (str)
        -meta="<meta charset='UTF-8'>" (str)

        Usage:
        >>> html_file = HTMLFile("testfile.html")
        >>> html_file.head("Test File")
        """
        self.page.append("<head>")
        self.page.append(meta)
        self.page.append("<title>" + title + "</title>")

    def head_end(self):
        """
        Adds head end tag to page.

        No args taken.

        Usage:
        >>> html_file = HTMLFile("testfile.html")
        >>> html_file.head_end()
        """
        self.page.append("</head>")

    def stylesheet(self, stylesheet="stylesheet.css"):
        """
        Adds stylesheet tag to page.

        Args taken:
        -stylesheet="stylesheet.css" (str)

        Usage:
        >>> html_file = HTMLFile("testfile.html")
        >>> html_file.stylesheet()
        """
        self.page.append("<link rel='stylesheet' type='text/css' href='" + stylesheet + "'>")

    def body(self):
        """
        Adds body tag to page.

        No args taken.

        Usage:
        >>> html_file = HTMLFile("testfile.html")
        >>> html_file.body()
        """
        self.page.append("<body>")

    def body_end(self):
        """"
        Adds body end tag to page.

        No args taken.

        Usage:
        >>> html_file = HTMLFile("testfile.html")
        >>> html_file.body_end()
        """
        self.page.append("</body>")

    def tag(self, tag, text):
        """
        Adds custom tag to page.

        Args taken:
        -tag (str)
        -text (str)

        Usage:
        >>> html_file = HTMLFile("testfile.html")
        >>> html_file.tag("a", "https://www.google.co.uk/")
        """
        self.page.append("<" + tag + ">" + text + "</" + tag + ">")

    def table(self):
        """
        Adds table tag to page.

        No args taken.
        Usage:
        >>> html_file = HTMLFile("testfile.html")
        >>> html_file.table()
        """
        self.page.append("<table border='1' cellspacing='4' cellpadding='4'>")

    def table_end(self):
        """
        Adds table end tag to page.

        No args taken.

        Usage:
        >>> html_file = HTMLFile("testfile.html")
        >>> html_file.table_end()
        """
        self.page.append("</table>")

    def row(self, row: list):
        """
        Adds row into a table.

        Args taken:
        -row (list)

        Usage:
        >>> html_file = HTMLFile("testfile.html")
        >>> html_file.row(['Column 1', "Column 2", "Column 3"])
        """
        self.page.append("<tr>")
        for column in row:
            self.page.append("<td>" + str(column) + "</td>")
        self.page.append("</tr>")

    def write_file(self):
        """
        Outputs final html file.

        No args taken.

        Usage:
        >>> html_file = HTMLFile("testfile.html")
        >>> html_file.write_file()
        """
        html_file = open(self.filename, 'w')
        for line in self.page:
            html_file.write(line)
        html_file.close()

    def read_file(self, *args):
        pass  # read method not needed
