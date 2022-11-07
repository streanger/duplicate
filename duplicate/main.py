"""
module for searching for files duplicates in gui view

useful:
    https://www.geeksforgeeks.org/python-group-first-elements-by-second-elements-in-tuple-list/
    https://stackoverflow.com/questions/6996603/how-do-i-delete-a-file-or-folder-in-python
    https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
    https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/labelframe.html
    https://pythonbasics.org/tkinter-checkbox/
    https://stackoverflow.com/questions/63468366/tkinter-mark-only-one-checkbox
    https://pypi.org/project/Send2Trash/
    https://www.geeksforgeeks.org/file-explorer-in-python-using-tkinter/
    https://stackoverflow.com/questions/3842155/is-there-a-way-to-make-the-tkinter-text-widget-read-only
    https://stackoverflow.com/questions/15995783/how-to-delete-all-children-elements
    https://rich.readthedocs.io/en/stable/logging.html
    https://www.tutorialspoint.com/how-to-align-checkbutton-in-ttk-to-the-left-side
    https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
    https://towardsdatascience.com/whats-init-for-me-d70a312da583
    https://python-notes.curiousefficiency.org/en/latest/python_concepts/import_traps.html#the-double-import-trap
    https://stackoverflow.com/questions/16745507/tkinter-how-to-use-threads-to-preventing-main-event-loop-from-freezing
    https://www.pythontutorial.net/tkinter/tkinter-thread/
    https://stackoverflow.com/questions/47008899/tkinter-dynamic-scrollbar-for-a-dynamic-gui-not-updating-with-gui
    https://stackoverflow.com/questions/42248376/stuck-using-fonts-on-tkinter-for-python-3-x
    https://stackoverflow.com/questions/68375136/what-is-the-default-font-of-tkinter-label
    https://github.com/arsenetar/dupeguru
    https://python-forum.io/thread-10689.html
    https://stackoverflow.com/questions/4998629/split-string-with-multiple-delimiters-in-python

structure tree:
    .
    ├── project
    │   ├── package
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   └── standalone.py
    │   └── setup.py

"""

import sys
import os
import re
import logging
import threading
import subprocess
from pathlib import Path
from tkinter import (
    Tk,
    Menu,
    Entry,
    Frame,
    Label,
    IntVar,
    LabelFrame,
    Checkbutton,
    filedialog,
    Button,
    font,
    YES,
    NO,
    TOP,
    END,
    BOTTOM,
    LEFT,
    BOTH,
    W,
)

from send2trash import send2trash
from rich.logging import RichHandler

# my modules
from duplicate.search_duplicates import search
from duplicate.scrolled_frame import VerticalScrolledFrame


class DuplicatesGUI(Frame):
    """class for checking files duplicates"""

    def __init__(self, master):
        super().__init__(master)
        # default setup
        self.directory = "."
        self.extensions = ("",)
        self.to_remove = []
        self.search_thread = None
        self.thread_works = False
        self.vertical_scrolled_frame = None
        self.main_frame = None
        self.info_label = None
        self.check_buttons = {}
        self.check_buttons_minus_last = []

        # style
        self.relief = "groove"
        self.original_color = self.master.cget("background")
        self.widgets_bg_color = self.original_color
        self.widgets_fg_color = "black"
        self.regular_font = font.nametofont("TkDefaultFont")
        self.overstrike_font = font.nametofont("TkDefaultFont").copy()
        self.overstrike_font.configure(overstrike=True)

        # window setup
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.geometry("{}x{}".format(650, 500))  # width x height
        self.master.resizable(width=True, height=True)
        self.master.wm_title("duplicate")

        # gui
        self.pack()
        self.run_gui()

    def spawn_thread(self):
        """spawn thread for search"""
        if self.thread_works:
            # DEBUG
            logging.info("thread already works, wait for finish")
            return None

        # remove previous widgets
        self.general_cleanup()

        # run thread for search
        self.search_thread = threading.Thread(target=self.search_and_update)
        self.search_thread.start()
        self.thread_works = True

        # DEBUG
        total_threads = threading.enumerate()
        logging.info("total_threads: {}".format(total_threads))
        return None

    def path_entry_callback(self, event):
        """entry widget event callback"""
        self.master.focus()  # unfocus from entry

        # read data from entry
        new_directory = self.path_entry.get().strip()
        logging.info(new_directory)

        # check if path is directory
        if Path(new_directory).is_dir():
            self.directory = new_directory
            # if ok set text to entry
            self.path_entry.delete(0, END)
            self.path_entry.insert(0, new_directory)
        else:
            # if not set previous text to entry
            self.path_entry.delete(0, END)
            self.path_entry.insert(0, self.directory)
        return None

    def extensions_entry_callback(self, event):
        """entry widget event callback"""
        self.master.focus()  # unfocus from entry

        # read and parse text
        text = self.extensions_entry.get().strip()
        extensions = [
            item.strip(" .") for item in re.split(",|;| ", text) if item.strip()
        ]
        extensions = tuple(sorted(set(extensions)))

        # update extensions
        if not extensions:
            extensions = ("",)  # to match all extensions
        extensions_text = ",".join(extensions)
        self.extensions = extensions
        self.info_label.config(text="extensions set to: {}".format(extensions))
        logging.info("extensions set to: {}".format(extensions))

        # update entry text
        self.extensions_entry.delete(0, END)
        self.extensions_entry.insert(0, extensions_text)
        return None

    def checkbox_command(self, path, status):
        """checkbox feedback"""
        status = status.get()
        logging.info("{} -> {}".format(path, status))
        if status:
            self.to_remove.append(path)
        else:
            try:
                self.to_remove.remove(path)
            except ValueError:
                pass
        logging.info(self.to_remove)
        return None

    def clear_to_remove_list(self):
        """clear items to be removed"""
        self.to_remove = []
        logging.info("to_remove cleared")
        return None

    def choose_and_set_directory(self):
        """choose directory to search"""
        directory = filedialog.askdirectory(initialdir=self.directory)
        if not directory:
            logging.info("choose directory cancelled")
            return False
        logging.info("directory: {}".format(directory))
        self.directory = directory
        self.path_entry.delete(0, END)
        self.path_entry.insert(0, self.directory)
        return True

    def search_and_update(self):
        """search for duplicates and update widgets
        https://stackoverflow.com/questions/15995783/how-to-delete-all-children-elements
        """
        # search for duplicates
        duplicates = search(self.directory, self.extensions)
        logging.info(duplicates)
        if duplicates:
            self.info_label.config(text="searching finished!")
        else:
            self.info_label.config(text="no duplicates found")

        # create new widgets
        for key, values in duplicates:
            row = Frame(self.main_frame, relief=self.relief, bg=self.widgets_bg_color)
            row.pack(expand=YES, fill=BOTH, side=TOP)
            labelframe = LabelFrame(row, text=key, labelanchor="n", bd=3, fg="green")
            labelframe.pack(expand=YES, fill=BOTH, side=TOP)

            items_number = len(values)
            for index, filepath in enumerate(values):
                box_status = IntVar()
                remove_box = Checkbutton(
                    labelframe,
                    text=filepath,
                    variable=box_status,
                    onvalue=1,
                    offvalue=0,
                    anchor=W,
                    command=lambda path=filepath, status=box_status: self.checkbox_command(
                        path, status
                    ),
                )
                remove_box.bind(
                    "<Button-3>",
                    lambda event, path=Path(filepath).parent: self.popup(event, path),
                )
                remove_box.pack(expand=YES, fill=BOTH, side=TOP)
                self.check_buttons[filepath] = remove_box
                if index < (items_number - 1):
                    self.check_buttons_minus_last.append(remove_box)

        # canvas, scrollregion reset
        # https://stackoverflow.com/questions/47008899/tkinter-dynamic-scrollbar-for-a-dynamic-gui-not-updating-with-gui
        self.vertical_scrolled_frame._on_frame_configure()
        self.thread_works = False
        logging.info("threaded target ended")
        return None

    def general_cleanup(self):
        """clear main frame widgets"""
        if self.thread_works:
            logging.info("can't clear because thread works")
            return False

        # clear to_remove
        self.clear_to_remove_list()

        # remove definitions
        self.check_buttons = {}
        self.check_buttons_minus_last = []

        # remove widgets
        for child in self.main_frame.winfo_children():
            logging.info(child)
            child.destroy()

        # update widgets
        self.master.update()
        return None

    def select_almost_all(self):
        """select n-1 of duplicated items"""
        for box in self.check_buttons_minus_last:
            box.invoke()
        return None

    def remove_selected_files(self):
        """move selected files to trash

        TODO: use queue for to_remove object
        """
        logging.info("files will be moved to trash")
        to_remove_local = self.to_remove.copy()
        for filepath in to_remove_local:
            try:
                send2trash(filepath)
                remove_box = self.check_buttons[filepath]
                remove_box.configure(font=self.overstrike_font)
                self.to_remove.remove(filepath)
                logging.info("box of file moved to trash: {}".format(remove_box))
            except Exception as err:
                logging.error(err)
        self.info_label.config(text="file(s) removed!")
        return None

    def run_gui(self):
        """create widgets & run gui"""
        # ************** define topbar frames **************
        topbar = Frame(self.master, relief=self.relief, bd=3)
        topbar.pack(expand=NO, fill=BOTH, side=TOP, ipady=2, pady=2)

        # entries text (button & label)
        entries_text_frame = Frame(topbar, relief=self.relief)
        entries_text_frame.pack(expand=YES, fill=BOTH, side=LEFT)
        directory_button = Button(
            entries_text_frame,
            relief=self.relief,
            text="path...",
            command=self.choose_and_set_directory,
        )
        directory_button.pack(expand=YES, fill=BOTH, side=TOP)
        extension_entry_label = Label(entries_text_frame, text="extensions")
        extension_entry_label.pack(expand=YES, fill=BOTH, side=TOP)

        # entries
        entries_frame = Frame(topbar, relief=self.relief)
        entries_frame.pack(expand=YES, fill=BOTH, side=LEFT)
        self.path_entry = Entry(entries_frame)
        self.path_entry.insert(END, self.directory)
        self.path_entry.bind("<Return>", self.path_entry_callback)
        self.path_entry.pack(expand=YES, fill=BOTH, side=TOP)
        self.extensions_entry = Entry(entries_frame)
        self.extensions_entry.bind("<Return>", self.extensions_entry_callback)
        self.extensions_entry.pack(expand=YES, fill=BOTH, side=TOP)

        # search button
        search_button = Button(
            topbar, relief=self.relief, text="search", command=self.spawn_thread
        )
        search_button.pack(expand=YES, fill=BOTH, side=LEFT)

        # clear button
        search_button = Button(
            topbar, relief=self.relief, text="clear", command=self.general_cleanup
        )
        search_button.pack(expand=YES, fill=BOTH, side=LEFT)

        # select n-1
        select_almost_all_button = Button(
            topbar,
            relief=self.relief,
            text="select\nn-1",
            command=self.select_almost_all,
        )
        select_almost_all_button.pack(expand=YES, fill=BOTH, side=LEFT)

        # remove-selected button
        remove_button = Button(
            topbar,
            relief=self.relief,
            text="remove\nselected",
            fg="red",
            activeforeground="red",
            command=self.remove_selected_files,
        )
        remove_button.pack(expand=YES, fill=BOTH, side=LEFT)

        # use wrapper
        self.vertical_scrolled_frame = VerticalScrolledFrame(
            self.master, relief=self.relief, bg=self.widgets_bg_color
        )
        self.vertical_scrolled_frame.pack(expand=YES, fill=BOTH, side=TOP)
        self.main_frame = Frame(self.vertical_scrolled_frame)
        self.main_frame.pack(expand=YES, fill=BOTH, side=TOP)

        # info label
        self.info_label = Label(self.master, text="", borderwidth=3, relief=self.relief)
        self.info_label.pack(expand=NO, fill=BOTH, side=BOTTOM)

        # *********** lift, get focus ***********
        self.master.update()
        self.master.attributes("-topmost", True)
        self.master.lift()  # move window to the top
        self.master.focus_force()
        return None

    def popup(self, event, path):
        """popup window for handling mouse rightclick
        https://stackoverflow.com/questions/12014210/tkinter-app-adding-a-right-click-context-menu
        https://www.askpython.com/python-modules/tkinter/menu-bar-and-menubutton
        """
        popup_menu = Menu(self, tearoff=0)
        popup_menu.add_command(
            label="open directory", command=lambda: open_directory(path)
        )
        try:
            popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            popup_menu.grab_release()
        return None

    def on_closing(self):
        """handle application closing"""
        self.master.destroy()
        self.master.quit()


def open_directory(directory):
    """open directory(file) - cross platform
    https://stackoverflow.com/questions/3022013/windows-cant-find-the-file-on-subprocess-call
    https://python-forum.io/thread-10689.html
    """
    logging.info("{}".format(directory))
    if sys.platform == "darwin":
        opener = "open"
    elif sys.platform == "win32":
        opener = "start"
        os.startfile(directory, "open")  # Windows only
        return True
    else:
        opener = "xdg-open"
    logging.info("{} -> {}".format(opener, directory))
    subprocess.call([opener, directory], shell=True)
    return None


def gui():
    """duplicates gui for entrypoint"""
    gui_object = DuplicatesGUI(master=Tk())
    gui_object.mainloop()
    return None


if __name__ == "__main__":
    FORMAT = "%(message)s"
    LEVEL = logging.INFO
    logging.basicConfig(format=FORMAT, level=LEVEL, handlers=[RichHandler()])

    # *********** main ***********
    gui()
