__author__ = "@mehmetserifpasa"

import os
import time
import ujson
import threading
import subprocess
from tkinter import *
from tkinter import ttk
import tkinter.messagebox


class Window(Tk):

    def __init__(self):
        super().__init__()
        self.title('Monitor')
        self.width_screen = self.winfo_screenwidth()
        self.height_screen = self.winfo_screenheight()
        self.window_height = 700
        self.window_width = 900
        self.x_cordinate = int((self.width_screen / 2) - (self.window_width / 2))
        self.y_cordinate = int((self.height_screen / 2) - (self.window_height / 2))
        self.geometry("{}x{}+{}+{}".format(self.window_width, self.window_height, self.x_cordinate, self.y_cordinate))

        self.THEME = ttk.Style()
        self.THEME.theme_use('alt')

        self.SkipFirstValue = 0
        self.CPU_NULL = float(100.0)
        self.TOTAL_CPU = float(0.0)
        self.TOTAL_MEMORY = float(0.0)
        self.TOTAL_PROCESS_COUNT = 0
        self.OpenPathFileEvent = ""

        self.RefreshPeriodFile = open('settings.json', "r+")
        self.RefreshPeriodValue = ujson.loads(self.RefreshPeriodFile.read())['Refresh_Period']



    def Exit(self):
        c.destroy()
        sys.exit()



    def WriteEvent(self, data):
        """
        When we click on the process, it writes its information in the "Text" field.
        """
        self.EventFocus = self.TreeView.focus()
        self.EventFocusInfo = list(self.TreeView.item(self.EventFocus, 'values'))

        self.ProcessTextWrite.delete('1.0', END)
        self.ProcessTextWrite.insert(END,
                                "USER:  "    + str(self.EventFocusInfo[0]) + "\n" +
                                "PID:  "     + str(self.EventFocusInfo[1]) + "\n" +
                                "%CPU:  "     + str(self.EventFocusInfo[2]) + "\n" +
                                "%MEM:  "     + str(self.EventFocusInfo[3]) + "\n" +
                                "VSZ:  "     + str(self.EventFocusInfo[4]) + "\n" +
                                "RSS:  "     + str(self.EventFocusInfo[5]) + "\n" +
                                "Start:  "   + str(self.EventFocusInfo[6]) + "\n" +
                                "Time:  "    + str(self.EventFocusInfo[7]) + "\n" +
                                "Process Name:  " + str(self.EventFocusInfo[8]) + "\n"
                                )



    def OpenPathEvent(self, data):
        """
        When a process is clicked, it takes its directory address and opens the file path.
        """
        try:
            self.OpenPathEvents = self.TreeView.focus()
            self.OpenPathEventsInfo = list(self.TreeView.item(self.EventFocus, 'values'))
            self.OpenPathEventsCommandValue = self.OpenPathEventsInfo[8].split()[2]

            for i in self.OpenPathEventsCommandValue.split("/")[:-1]:
                self.OpenPathFileEvent += i + "/"

            os.system('open ' + str(self.OpenPathFileEvent))
            self.OpenPathFileEvent = ""

        except:
            tkinter.messagebox.showinfo("Information", "Directory could not be opened!")



    def MainWindow(self):
        self.tabs = ttk.Notebook(self)
        self.Target = Frame(self.tabs)
        self.tabs.add(self.Target, text="Process")

        self.tabs.pack(fill=BOTH, expand=1)

        self.TreeView = ttk.Treeview(self.Target, height=25)


        self.TreeView['columns'] = ('1', '2', '3',"4", "5", "6", "7", "8","9")
        self.TreeView['show'] = 'headings'

        self.TreeView.column('1', width=150)
        self.TreeView.heading('1', text="USER")

        self.TreeView.column('2', anchor=CENTER, width=70)
        self.TreeView.heading('2', text="PID", anchor="center")

        self.TreeView.column('3', anchor=CENTER, width=70)
        self.TreeView.heading('3', text="%CPU", anchor="center")

        self.TreeView.column('4', anchor=CENTER, width=70)
        self.TreeView.heading('4', text="%MEM", anchor="center")

        self.TreeView.column('5', anchor=CENTER, width=70)
        self.TreeView.heading('5', text="VSZ", anchor="center")

        self.TreeView.column('6', anchor=CENTER, width=70)
        self.TreeView.heading('6', text="RSS", anchor="center")

        self.TreeView.column('7',  width=70)
        self.TreeView.heading('7', text="START")

        self.TreeView.column('8',  width=90)
        self.TreeView.heading('8', text="TIME")

        self.TreeView.column('9', width=200)
        self.TreeView.heading('9', text="Process Name")

        self.TreeView.bind('<<TreeviewSelect>>', self.WriteEvent)
        self.TreeView.bind('<Double-Button-1>', self.OpenPathEvent)

        vbar = ttk.Scrollbar(self.TreeView, orient=VERTICAL, command=self.TreeView.yview)
        self.TreeView.configure(yscrollcommand=vbar.set)
        self.TreeView.grid(row=0, column=0, sticky=NSEW)

        self.TreeView.pack(fill=X)



        """ 
        self.TOTAL_INFO: Where processes calculate and write how much resources are used
        self.ProcessTextWrite: Where the information of the processes is written
        """
        self.TOTAL_INFO = Text(
            self.Target,
            font=('open sans', 15),
            bg="#F9F9F9",
            width=20,
            height=4,
        )
        self.TOTAL_INFO.pack(side=LEFT, fill=BOTH)

        self.ProcessTextWrite = Text(
            self.Target,
            font=('open sans', 13),
            bg="#F9F9F9",
            width=20,
            height=4,
        )
        self.ProcessTextWrite.pack(side=LEFT, fill=BOTH, expand=TRUE)


        #---------- THREAD START -----------------
        self.t1 = threading.Thread(target=c.ProcessInsert)
        self.t1.setDaemon(True)
        self.t1.start()



    def ProcessInsert(self):

        """
        The information received with "ps aux" is parsed here and written in the "Treeview" field.
        """

        while True:

            for i in self.TreeView.get_children():
                self.TreeView.delete(i)

            self.data = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).stdout.readlines()

            for i in self.data:

                if self.SkipFirstValue == 0:
                    self.SkipFirstValue += 1
                    pass

                else:
                    self.USER = i.decode("UTF-8").split()[0]
                    self.PID = i.decode("UTF-8").split()[1]
                    self.CPU = i.decode("UTF-8").split()[2]
                    self.MEM = i.decode("UTF-8").split()[3]
                    self.VSZ = i.decode("UTF-8").split()[4]
                    self.RSS = i.decode("UTF-8").split()[5]
                    self.STARTED = i.decode("UTF-8").split()[8]
                    self.TIME = i.decode("UTF-8").split()[9]
                    self.COMMAND = i.decode("UTF-8").split()[10].split("/")[-1] + "    ->  " +i.decode("UTF-8").split()[10]

                    self.TreeView.insert(
                        "",
                        END,
                        values=(
                            self.USER,
                            self.PID,
                            self.CPU,
                            self.MEM,
                            self.VSZ,
                            self.RSS,
                            self.STARTED,
                            self.TIME,
                            self.COMMAND,

                        )
                    )
                    self.SkipFirstValue = 0
                    self.TOTAL_PROCESS_COUNT += 1

                    try:
                        self.TOTAL_CPU_LEN = float(i.decode("UTF-8").split()[2])
                        self.TOTAL_CPU += self.TOTAL_CPU_LEN

                        self.TOTAL_MEM_LEN = float(i.decode("UTF-8").split()[3])
                        self.TOTAL_MEMORY += self.TOTAL_MEM_LEN

                    except:
                        pass

            self.TOTAL_INFO.delete("1.0", END)
            self.TOTAL_INFO.insert(
                END,
                "Usage CPU: %" + str(self.TOTAL_CPU)[0:5] + "\n"
                "Usage MEM: %" + str(self.TOTAL_MEMORY)[0:5] + "\n"
                "Total Process: " + str(self.TOTAL_PROCESS_COUNT) + "\n\n"
                "Empty CPU: %" + str(self.CPU_NULL - self.TOTAL_CPU)[0:5] + "\n"

            )

            self.TOTAL_CPU = float(0.0)
            self.TOTAL_MEMORY = float(0.0)
            self.TOTAL_PROCESS_COUNT = 0
            self.CPU_NULL = float(100.0)
            time.sleep(int(self.RefreshPeriodValue))





c = Window()
c.MainWindow()
c.protocol("WM_DELETE_WINDOW", c.Exit)
c.mainloop()