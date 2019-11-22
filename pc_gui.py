import pc
import tkinter
import time
import random
import copy
import threading

DEFAULT_FONT = ('Helvetica', 20)
SLEEPF = 3
SLEEPE = 5


class Gui:
    def __init__(self, window, enroll):
        self.window = window
        self.enroll = enroll
        
        self.window.title('AutoEnroll')
        self.window.resizable(0,0)
        self.window.geometry('800x600')



    def run(self):
        run = tkinter.Button(master = self.window, text = 'Run', font = DEFAULT_FONT, command = self._start)
        run.grid(row = 0, column = 1, padx = 5, pady = 5)
        
        stop = tkinter.Button(master = self.window, text = 'Stop', font = DEFAULT_FONT, command = self._stop)
        stop.grid(row = 1, column = 1, padx = 5, pady = 5)

        self._get_user()
        
        self.window.rowconfigure(0, weight = 1)
        self.window.rowconfigure(1, weight = 1)
        self.window.rowconfigure(2, weight = 1)
        self.window.rowconfigure(3, weight = 7)
        self.window.columnconfigure(0, weight = 1)
        self.window.columnconfigure(1, weight = 1)
        self.window.mainloop()

    def _get_user(self):
        user = tkinter.Label(self.window, text = 'Ucinetid: ', font = ('Helvetica', 15))
        user.grid(row = 0, column = 0,padx = 20, sticky = tkinter.W)

        self.uinput = tkinter.Entry(self.window)
        self.uinput.grid(row = 0, column = 0, sticky = tkinter.E)

        password = tkinter.Label(self.window, text = 'Password: ', font = ('Helvetica', 15))
        password.grid(row = 1, column = 0, padx = 20, sticky = tkinter.W)

        self.pinput = tkinter.Entry(self.window)
        self.pinput.grid(row = 1, column = 0, sticky = tkinter.E)

    def _start(self):
        if not enroll.running:
            enroll.ucinetid = self.uinput.get()
            enroll.password = self.pinput.get()
            a = enroll.text.get('1.0','end')
            courses = set()
            for course in a.splitlines():
                courses.add(course)
            enroll.courses = courses
            enroll.times = 0
            enroll.attempt = 0
            enroll.running = True

    def _stop(self):
        enroll.done()


class Enroll:

    def __init__(self,window, ucinetid = None, password = None, courses = set()):
        self.window = window
        self.running = False
        self.ucinetid = ucinetid
        self.password = password
        self.cookie = None
        self.courses = courses
        self.enrollin = set()
        self.attempt = 0
        self.times = 0

        label = tkinter.Label(self.window, text = 'One Coursecode Each Line:', font = ('Helvetica', 15))
        label.grid(row = 2, column = 0)

        label2 = tkinter.Label(self.window, text = 'Output:', font = ('Helvetica', 15))
        label2.grid(row = 2, column = 1)

        self.text = tkinter.Text(self.window)
        self.text.grid(row = 3, column = 0, padx = 10, sticky = tkinter.N + tkinter.S + tkinter.E + tkinter.W)

        self.text2 = tkinter.Text(self.window)
        self.text2.grid(row = 3, column = 1, padx = 10, sticky = tkinter.N + tkinter.S + tkinter.E + tkinter.W)
        self.text2.config(state = tkinter.DISABLED)
        
    def login(self):
        pc.ucinetid = self.ucinetid
        pc.password = self.password
        while self.cookie == None and self.running:
            try:
                self.display_message(f'Try to log in {pc.ucinetid}.')
                self.cookie = pc.post()
                if not self.cookie:
                    assert False
            except:
                self.display_message('Log in fail.Try log in again...')
                time.sleep(random.randint(SLEEPF,SLEEPE))
            else:
                self.display_message('Log in success.')

    
    def enroll(self):
        courses = copy.deepcopy(self.courses)
        for course in courses:
            success = pc.enroll(self.cookie, course)
            if success:
                self.enrollin.add(course)
                self.courses.remove(course)
                self.display_message(f'Enroll {course} success.')
            else: 
                self.attempt += 1
                self.display_message(f'Enroll {course} fail. Attempt {self.attempt}.')
            time.sleep(random.randint(SLEEPF, SLEEPE))

    def log_off(self):
        if self.cookie:
            self.display_message(f'Log off {pc.ucinetid}.')
            pc.log_off(self.cookie)
            self.display_message(f'Log off successfully.')

    def done(self):
        self.running = False
        self.display_message(f'Success enroll in {self.enrollin}.\nFail enroll {self.courses}.\nTotal attempt {self.attempt}.')

    def display_message(self, message):
        self.text2.config(state = tkinter.NORMAL)
        if self.times > 25:
            self.text2.delete('1.0', '2.0')
        elif self.times == 0:
            self.text2.delete('1.0','end')
            self.times += 1
        else:
            self.times += 1
        self.text2.insert(tkinter.END, message + '\n')
        self.text2.config(state = tkinter.DISABLED)

def thread(enroll: Enroll):
    while True:
        if enroll.running:
            enroll.login()
            start = time.clock()
            while len(enroll.courses) > 0 and time.clock() - start < 500 and enroll.running:
                enroll.enroll()
            enroll.log_off()
            enroll.cookie = None
            if len(enroll.courses) == 0 and enroll.running:
                enroll.done()
        time.sleep(0.3)


if __name__ == '__main__':
    window = tkinter.Tk()
    enroll = Enroll(window = window)
    t = threading.Thread(target = thread, args = (enroll,))
    t.setDaemon(True)
    t.start()
    gui = Gui(window, enroll).run()
