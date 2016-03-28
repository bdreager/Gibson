#!/usr/bin/env python
# -*- coding: utf-8 -*-

__program__ = 'Gibson'
__version__ = '0.3.1'
__description__ = 'Hackers on steroids'

import os, curses, locale, string
from argparse import ArgumentParser
from random import randint, choice, sample, randrange
locale.setlocale(locale.LC_ALL, '') # for displaying the unicode characters using ncurses

def init_args():
    parser = ArgumentParser(prog=__program__, description=__description__)
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
        self.text_color = curses.color_pair(4)

        self.random_colors = False
        self.verbose = False
        self.should_update = True
        self.view_resized()

    def update(self):
        self.activate_window()
        for window in self.active_windows: window.update()
        if (self.verbose): self.debug_output()
        curses.doupdate()
        if (len(self.to_remove)): self.remove_windows()

    def activate_window(self):
        if self.should_update or len(self.active_windows) < self.max_active_windows:
            if len(self.inactive_windows) == 0: self.inactive_windows.append(Window(self))
            self.active_windows.append(self.inactive_windows.pop(0))
            self.should_update = False

    def set_remove(self, window):
        self.to_remove.append(window)

    def remove_windows(self):
        self.active_windows = [x for x in self.active_windows if x not in self.to_remove]
        self.inactive_windows.extend(self.to_remove)
        self.to_remove = []

    def debug_output(self):
        self.stdscr.addstr(0, 0, 'w:[{}], h:[{}] mawin:[{}] awin:[{}] iwin:[{}]'.format(self.width, self.height, self.max_active_windows, len(self.active_windows), len(self.inactive_windows)))

    def random_color(self):
        return curses.color_pair(randint(0, self.color_range))

    def view_resized(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.stdscr.clear()
        self.stdscr.refresh()
        self.max_active_windows = int(round(((self.height + self.width)/2) * 0.05))
        self.inactive_windows, self.active_windows = ([], [])
        self.should_update = True

class Window(object):
    kS_LIMBO, kS_EXPAND_W, kS_EXPAND_H, kS_PRINT, kS_SHRINK, kS_FINISH = (0, 1, 2, 3, 4, 5)
    kMIN_W, kMIN_H = (4, 4)
    kRATE = 2

    def __init__(self, parent):
        self.parent = parent
        self.win = curses.newwin(0,0,0,0)
        self.sub = None
        self.stage = self.kS_LIMBO

    def setup(self):
        self.h, self.w, self.y, self.x = (1, 1, randint(self.kMIN_H, self.parent.height-self.kMIN_H), randint(self.kMIN_W, self.parent.width-self.kMIN_W))
        self.update_window()
        self.stage = self.kS_EXPAND_W

    def update(self):
        #TODO cleanup this hot mess

        if self.stage == self.kS_LIMBO:
            self.setup()

        elif self.stage == self.kS_FINISH:
            self.parent.set_remove(self)
            self.win.erase()
            self.stage = self.kS_LIMBO

        elif self.stage == self.kS_SHRINK:
            self.win.attrset(self.parent.stage_D)
            self.win.erase()
            self.win.noutrefresh()
            self.w, self.x, at_min = self.shrink_1D(self.w, self.x, 3, self.kRATE)

            if at_min:
                self.stage = self.kS_FINISH
                self.win.border(curses.ACS_VLINE,1,1,1,1,1,1,1)
            else:
                self.update_window()
                self.win.box()

        elif self.stage == self.kS_PRINT:
            self.win.attrset(self.parent.stage_C)
            self.sub.update()

            if self.sub.lifespan <= 0 and randint(0, 10) == 0:
                self.stage = self.kS_SHRINK
                self.parent.should_update = True

            self.win.box()

        elif self.stage == self.kS_EXPAND_H:
            self.win.attrset(self.parent.stage_B)
            self.win.erase()

            self.h, self.y, at_max = self.expand_1D(self.h, self.y, self.parent.height, self.kRATE)
            self.update_window()

            self.win.box()

            if at_max or (self.h >= self.kMIN_H and randint(0, 20) == 0):
                self.stage = self.kS_PRINT
                self.sub = SubWindow(self)

        elif self.stage == self.kS_EXPAND_W:
            self.win.attrset(self.parent.stage_A)
            self.w, self.x, at_max = self.expand_1D(self.w, self.x, self.parent.width, self.kRATE)
            self.update_window()

            self.win.border(1,1,1,curses.ACS_HLINE,1,1,1,1)
            if at_max or (self.w >= self.kMIN_W and randint(0, 10) == 0): self.stage = self.kS_EXPAND_H

        self.win.noutrefresh()

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
        self.content = '' if randint(0, 3) == 0 else self.w * self.h * ('#' if randint(0, 5) == 0 else ' ' )
        self.content_color = curses.color_pair(randint(0, self.parent.parent.color_range)) if self.parent.parent.random_colors else self.parent.parent.text_color
        if randint(0, 4) == 0: self.content_color = self.content_color | curses.A_BOLD
        self.main_set, self.alt_set = sample(['01', string.printable, string.ascii_letters+' '*50, string.hexdigits+' '*10], 2)
        self.full_type = choice([self.kTYPE_SCROLL, self.kTYPE_REPLACE])
        self.lifespan = randint(self.w,self.w*2) if self.full_type == self.kTYPE_SCROLL else randint(self.w*2, self.w*4)

    def update(self):
        #TODO cleanup this hot mess
        self.lifespan -= 1
        if self.full or self.alt:
            self.win.erase()

            if self.full_type == self.kTYPE_SCROLL:
                a = 1
                self.content = self.content[self.w:]
                self.content += self.random_line(self.main_set, range(randrange(1, self.w)))

            elif self.full_type == self.kTYPE_REPLACE:
                line = self.random_line(self.alt_set, range(self.w))
                target = randint(0, self.h) * self.w
                self.content = self.content[:target] + line + self.content[target+self.w:]

        else:
            self.content += self.random_line(self.main_set, range(randrange(1, self.w)))

        try: # if this fails, we know the view is full
            self.win.addstr(0,0,self.content, self.content_color)
            self.full = False
        except:
            self.full = True
            if self.full_type == self.kTYPE_REPLACE:
                self.alt = True
            pass

        if self.lifespan <= 0 and not self.full: self.lifespan = 1

        self.win.noutrefresh()

    def random_line(self, char_set, range):
        line = ''
        for _ in range:
            line += choice(char_set)

        return line

class Driver(object):
    kKEY_ESC = '\x1b'
    kMIN_DELAY, kMAX_DELAY = (1, 100)

    def __init__(self, stdscr, args = None):
        self.stdscr = stdscr
        curses.curs_set(0)
        curses.use_default_colors()
        #curses.halfdelay(1)
        self.stdscr.nodelay(1)
        self.delay_ms = 25

        self.gibson = Gibson(stdscr, args)
        self.running, self.paused = (False, False)

    @property
    def delay_ms(self): return self._delay_ms
    @delay_ms.setter
    def delay_ms(self, value):
        self._delay_ms = max(min(value, self.kMAX_DELAY), self.kMIN_DELAY)

    def start(self):
        self.running = True
        self.run()

    def run(self):
        while self.running:
            if not self.paused: self.gibson.update()
            self.update()
            self.stdscr.timeout(self.delay_ms)

    def update(self):
        try:
            key = self.stdscr.getkey()
        except curses.error as e:
            if str(e) == 'no input': return
            raise e

        lower = key.lower()
        if key == 'KEY_RESIZE': self.gibson.view_resized()
        elif key==self.kKEY_ESC or lower=='q': self.running = False
        elif lower=='v': self.gibson.verbose = not self.gibson.verbose

        elif lower=='p': self.paused = not self.paused
        elif key=='c': self.gibson.random_colors = not self.gibson.random_colors
        elif key=='C': self.gibson.text_color = self.gibson.random_color()

        elif key=='-' or key=='_': self.delay_ms -= 5
        elif key=='=' or key=='+': self.delay_ms += 5

def main(stdscr=None, args=init_args()):
    if not stdscr:
        curses.wrapper(main, args=args)
    else:
        os.environ.setdefault('ESCDELAY', '25')
        Driver(stdscr, args).start()

if __name__ == '__main__': main()
