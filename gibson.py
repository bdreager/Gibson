#!/usr/bin/env python
# -*- coding: utf-8 -*-

__program__ = 'Gibson'
__version__ = '0.3.0'
__description__ = 'Hackers on steroids'

import os, curses, locale, random, string
from argconfparse import ArgConfParser
locale.setlocale(locale.LC_ALL, '') # for displaying the unicode characters using ncurses

def init_args():
    parser = ArgConfParser(prog=__program__, description=__description__)
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    return parser.parse_args()

class Gibson(object):

    def __init__(self, stdscr, args=None):
        self.stdscr = stdscr

        try: # needed for terminals with limited color support
            for i in range(256):
                curses.init_pair(i+1, i, -1)
                self.color_range = i
        except:
            pass

        self.windows = []
        self.to_remove = []

        self.stage_A = curses.color_pair(5) | curses.A_BOLD
        self.stage_B = curses.color_pair(4) | curses.A_BOLD
        self.stage_C = curses.color_pair(3) | curses.A_BOLD
        self.stage_D = curses.color_pair(2) | curses.A_BOLD

        self.verbose = False
        self.should_update = True
        self.view_resized()

    def update(self):
        self.activate_window()
        for window in self.active_windows: window.update()
        if (self.verbose): self.debug_output()
        self.stdscr.refresh()
        if (len(self.to_remove)): self.remove_windows()

    def activate_window(self):
        if self.should_update or len(self.active_windows) < self.max_active_windows:
            self.active_windows.append(self.inactive_windows.pop(0))
            self.should_update = False

    def set_remove(self, window):
        self.to_remove.append(window)

    def remove_windows(self):
        self.active_windows = [x for x in self.active_windows if x not in self.to_remove]
        self.inactive_windows.extend(self.to_remove)
        self.to_remove = []

    def debug_output(self):
        self.stdscr.addstr(0, 0, 'w:[{}], h:[{}] mw:[{}] w:[{}]'.format(self.width, self.height, self.max_active_windows, len(self.windows)))

    def view_resized(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.stdscr.clear()
        self.stdscr.refresh()
        self.max_active_windows = int(round(((self.height + self.width)/2) * 0.05))
        self.inactive_windows = [Window(self) for _ in range(self.max_active_windows*2)]
        self.active_windows = []
        self.should_update = True

class Window(object):
    X, A, B, C, D, E = (0, 1, 2, 3, 4, 5) #I know this is stupid
    kMIN_W = 10
    kMIN_H = 20
    kRATE = 4

    def __init__(self, parent):
        self.parent = parent
        self.win = curses.newwin(0,0,0,0)
        self.sub = None
        self.stage = self.X

    def setup(self):
        self.h, self.w, self.y, self.x = (1, 1, random.randint(self.kMIN_H, self.parent.height-self.kMIN_H), random.randint(self.kMIN_W, self.parent.width-self.kMIN_W))
        self.update_window()
        self.stage = self.A

    def update(self):
        #TODO cleanup this hot mess

        if self.stage == self.X:
            self.setup()

        elif self.stage == self.E:
            self.parent.set_remove(self)
            self.win.clear()
            self.stage = self.X

        elif self.stage == self.D:
            self.win.attrset(self.parent.stage_D)
            self.win.clear()
            self.win.refresh()
            self.w, self.x, at_min = self.shrink_1D(self.w, self.x, 3, self.kRATE)

            if at_min:
                self.stage = self.E
                self.win.border(curses.ACS_VLINE,1,1,1,1,1,1,1)
            else:
                self.update_window()
                self.win.box()

        elif self.stage == self.C:
            self.win.attrset(self.parent.stage_C)
            self.sub.update()

            if self.sub.lifespan <= 0 and random.randint(0, 10) == 0:
                self.stage = self.D
                self.parent.should_update = True

            self.win.box()

        elif self.stage == self.B:
            self.win.attrset(self.parent.stage_B)
            self.win.clear()

            self.h, self.y, at_max = self.expand_1D(self.h, self.y, self.parent.height, self.kRATE)
            self.update_window()

            self.win.box()

            if at_max or (self.h >= self.kMIN_H and random.randint(0, 50) == 0):
                self.stage = self.C
                self.sub = SubWindow(self)

        else:
            self.win.attrset(self.parent.stage_A)
            self.w, self.x, at_max = self.expand_1D(self.w, self.x, self.parent.width, self.kRATE)
            self.update_window()

            self.win.border(1,1,1,curses.ACS_HLINE,1,1,1,1)
            if at_max or (self.w >= self.kMIN_W and random.randint(0, 25) == 0): self.stage = self.B

        self.win.refresh()

    def update_window(self):
        self.win.resize(self.h, self.w)
        self.win.mvwin(self.y, self.x)

    def shrink_1D(self, size, pos, bounds, rate):
        new_size = size - rate
        new_pos = pos + rate/2
        return (size, pos, True) if new_pos < 0 or new_size <= bounds else (new_size, new_pos, False)

    def expand_1D(self, size, pos, bounds, rate):
        new_size = size + rate
        new_pos = pos - rate/2
        return (size, pos, True) if new_pos < 0 or new_pos + new_size > bounds else (new_size, new_pos, False)

class SubWindow(object):
    kTYPE_SCROLL, kTYPE_REPLACE = (1, 0)

    def __init__(self, parent):
        self.parent = parent
        self.h, self.w, self.y, self.x = (parent.h-2, parent.w-2, parent.y+1, parent.x+1)
        self.win = parent.win.subwin(self.h,self.w,self.y,self.x)
        self.full = self.alt = False
        self.set_type()

    def set_type(self):
        self.content = self.w * self.h * ('#' if random.randint(0, 5) == 0 else ' ' ) if random.randint(0, 2) == 0 else ''
        self.content_color = self.parent.parent.stage_B #curses.color_pair(random.randint(0, parent.parent.color_range)) | curses.A_BOLD
        self.main_set, self.alt_set = random.sample(['01', string.printable, string.ascii_letters+' '*50, string.hexdigits+' '*10], 2)
        self.full_type = random.choice([self.kTYPE_SCROLL, self.kTYPE_REPLACE])
        self.lifespan = random.randint(self.w,self.w*2) if self.full_type == self.kTYPE_SCROLL else random.randint(self.w*2, self.w*4)

    def update(self):
        #TODO cleanup this hot mess
        self.lifespan -= 1
        if self.full or self.alt:
            self.win.clear()

            if self.full_type == self.kTYPE_SCROLL:
                a = 1
                self.content = self.content[self.w:]
                self.content += self.random_line(self.main_set, range(random.randrange(1, self.w)))

            elif self.full_type == self.kTYPE_REPLACE:
                line = self.random_line(self.alt_set, range(self.w))
                target = random.randint(0, self.h) * self.w
                self.content = self.content[:target] + line + self.content[target+self.w:]

        else:
            self.content += self.random_line(self.main_set, range(random.randrange(1, self.w)))

        try: # if this fails, we know the view is full
            self.win.addstr(0,0,self.content, self.content_color)
            self.full = False
        except:
            self.full = True
            if self.full_type == self.kTYPE_REPLACE: # or random.randint(0, 10) == 0:
                self.alt = True
            pass

        if self.lifespan <= 0 and not self.full: self.lifespan = 1

        self.win.refresh()

    def random_line(self, char_set, range):
        line = ''
        for _ in range:
            line += random.choice(char_set)

        return line

class Driver(object):
    kKEY_ESC = '\x1b'

    def __init__(self, stdscr, args = None):
        self.stdscr = stdscr
        curses.curs_set(0)
        curses.use_default_colors()
        #curses.halfdelay(1)
        self.stdscr.nodelay(1)

        self.gibson = Gibson(stdscr, args)
        self.running = False

    def start(self):
        self.running = True
        self.run()

    def run(self):
        while self.running:
            self.gibson.update()
            self.update()
            self.stdscr.timeout(75)

    def update(self):
        try:
            key = self.stdscr.getkey()
        except curses.error as e:
            if str(e) == 'no input': return
            raise e

        lower = key.lower()
        if key == 'KEY_RESIZE': self.gibson.view_resized()
        elif key==self.kKEY_ESC or lower=='q': self.running = False

def main(stdscr=None, args=init_args()):
    if not stdscr:
        curses.wrapper(main, args=args)
    else:
        os.environ.setdefault('ESCDELAY', '25')
        Driver(stdscr, args).start()

if __name__ == '__main__': main()