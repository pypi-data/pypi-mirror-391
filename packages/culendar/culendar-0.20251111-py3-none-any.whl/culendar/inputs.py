from curses import curs_set
from datetime import (
    date,
    datetime,
    timedelta,
)

from .i18n import _


# TODO: deal with too long lines
class Input:
    def __init__(self, ui, text="", pwd=False):
        self.ui = ui
        self._screen = ui.screen
        self.screen_update()
        self.text = text
        # self._maxpos is cursor max position in x, defined by text setter
        self._pos = self._maxpos   # cursor position in text
        self._pwd = pwd

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, newtext):
        self._text = newtext
        self._maxpos = len(self._text)

    def screen_update(self):
        self._ymax, self._xmax = self._screen.getmaxyx()
        self._y = self._ymax - 1

    def reset_text(self):
        self.text = ""
        self._pos = 0

    def delete_char(self, offset):
        if self._pos == 0:
            offset = 0  # avoid backspacing -1 character
        deleted = self._pos + offset
        self.text = self.text[:deleted] + self.text[deleted + 1:]
        self._pos += offset
        # erase and redraw the new text
        self.delete_text()
        self.draw_text()

    def delete_part(self, begin, end):
        self.text = self.text[:begin] + self.text[end:]
        self._pos = max(0, self._pos - (end - begin))
        # erase and redraw the new text
        self.delete_text()
        self.draw_text()

    def add_char(self, key):
        self.text = self.text[:self._pos] + key + self.text[self._pos:]
        self._pos += 1
        self.draw_text()

    def draw_text(self):
        lentext = len(self._text)
        old_pos = None
        if lentext > self._xmax - 1:
            text = self._text[lentext - self._xmax + 1:]
            old_pos = self._pos
            self._pos = self._xmax - 1
        else:
            text = self._text
        if not self._pwd:
            self._screen.addstr(self._y, 0, text)
        else:  # obfuscate password
            self._screen.addstr(self._y, 0, "*" * len(text))
        self.draw_cursor()
        if old_pos:
            self._pos = old_pos

    def delete_text(self):
        self._screen.hline(self._y, 0, " ", self._xmax - 1)

    def draw_cursor(self):
        """put the cursor at the good position"""
        if self._pos > self._xmax - 1:
            self._screen.move(self._y, self._xmax - 1)
        else:
            self._screen.move(self._y, self._pos)

    def move_cursor(self, newpos):
        self._pos = newpos
        self.draw_cursor()

    def delete_from_cursor(self, direction):
        if direction == "left":
            self.text = self.text[self._pos:]
            self._pos = 0
        elif direction == "right":
            self.text = self.text[:self._pos]
            self._pos = self._maxpos
        # erase and redraw the new text
        self.delete_text()
        self.draw_text()

    def find_left_word(self):
        idx = -1
        for i, s in enumerate(self.text[:self._pos - 1]):
            if s == " ":
                idx = i + 1
        if idx > 0 and idx < self._pos:  # something has been found
            # second condition to prevent the search from slice [:-1]
            return idx
        else:
            return 0

    def move_left_word(self):
        self._pos = self.find_left_word()
        self.draw_cursor()

    def delete_left_word(self):
        goal = self.find_left_word()
        self.delete_part(goal, self._pos)

    def find_right_word(self):
        idx = self.text[self._pos + 1:].find(" ")
        if idx > 0:  # something has been found
            return self._pos + self.text[self._pos + 1:].find(" ") + 1
        else:
            return self._maxpos

    def move_right_word(self):
        self._pos = self.find_right_word()
        self.draw_cursor()

########################################################################
# get input and definition of keybindings
########################################################################

    def get_input(self):
        curs_set(1)  # start of input: redraw cursor
        key = 0  # integer that does nothing in the loop
        self.draw_text()
        while key not in ("\n", ""):
            if key in ["KEY_RESIZE"]:
                return -1
            elif key in ["KEY_DC", ""]:
                self.delete_char(0)
            elif key in ["KEY_IC"]:
                pass  # TODO
            elif key in ["KEY_BACKSPACE", ""]:
                self.delete_char(-1)
            elif key in ["KEY_HOME", "KEY_DOWN", ""]:
                self.move_cursor(0)
            elif key in ["KEY_END", "KEY_UP", ""]:
                self.move_cursor(self._maxpos)
            elif key in ["KEY_LEFT",  ""]:
                self.move_cursor(max(0, self._pos - 1))
            elif key in ["KEY_RIGHT", ""]:
                self.move_cursor(min(self._maxpos, self._pos + 1))
            elif key in [""]:
                self.delete_from_cursor("left")
            elif key in [""]:
                self.delete_from_cursor("right")
            elif key in ["KEY_SLEFT", "KEY_CLEFT"]:
                self.move_left_word()
            elif key in ["KEY_SRIGHT", "KEY_CRIGHT"]:
                self.move_right_word()
            elif key in [""]:
                self.delete_left_word()
            else:
                if type(key) == str:
                    self.add_char(key)
            key = self.ui.getkey()
        curs_set(0)  # end of input: remove cursor
        if key == "":  # escape key: cancel text
            return 1
        else:
            return 0

########################################################################
# Check input validity
########################################################################
    def error(self, errmsg):
        self._screen.hline(self._ymax - 2, 0, " ", self._xmax)
        self._screen.hline(self._ymax - 1, 0, " ", self._xmax)
        self._screen.addstr(self._ymax - 2, 0, errmsg)
        self._screen.addstr(self._ymax - 1, 0, _("Press [Enter] to continue"))
        k = self.ui.getkey()
        if k in ['q', 'Q', '']:
            return "CUL_CANCEL"
        elif k == 'KEY_RESIZE':
            return k
        else:
            return None

    def check_hour(self, day, start=False):
        try:  # to create a time
            if len(self.text) == 0 and start:  # default value
                h = 0
                m = 0
            elif len(self.text) == 0 and not start:  # default value
                h = 24
                m = 0
            elif ":" in self.text:
                h = int(self.text[:self.text.find(":")])
                m = int(self.text[self.text.find(":") + 1:])
            elif len(self.text) < 3:
                h = int(self.text)
                m = 0
            else:
                m = int(self.text[-2:])
                h = int(self.text[:-2])
            if h == 24:
                if start:
                    h = 23
                    m = 59
                    tmpday = day
                else:
                    h = 0
                    # add hour and minute to day by using datetime
                    tmpday = datetime.fromordinal(day.toordinal() + 1)
            else:  # idem
                tmpday = datetime.fromordinal(day.toordinal())
            d = tmpday.replace(hour=h, minute=m)
            return d
        except ValueError:
            errmsg = _("You entered an invalid time")
            return self.error(errmsg)

    def check_duration(self, day, start_date):
        if "+" in self.text:
            end_date = self.check_add_time(start_date)
        else:
            end_date = self.check_hour(day)
        if end_date not in (None, "CUL_CANCEL", "KEY_RESIZE"):
            if end_date < start_date:
                st = (str(start_date.hour) + ":"
                      + ("0"+str(start_date.minute))[-2:])
                errmsg = _("Ending time should be greater than ")+st
                return self.error(errmsg)
        return end_date

    def check_add_time(self, start_date):
        multiplier = 1  # minutes, default
        if self.text[-1] in ["m", "h", "d"]:
            if self.text[-1] == "h":
                multiplier = 60
            if self.text[-1] == "d":
                multiplier = 24*60
            self.text=self.text[:-1]  # remove now useless letter
        try:
            duration = int(self.text[1:]) * multiplier*60  # in seconds
            end_date = start_date + timedelta(seconds=duration)
            return end_date
        except:
            errmsg = _("You entered an invalid duration")
            return self.error(errmsg)

    def check_day(self, day):
        if not self.text:  # empty day: set to today
            return date.today()
        else:
            try:
                if '/' in self.text:
                    if len(self.text) > 5:
                        y = int(self.text[0:4])
                        dec = 5
                    else:
                        y = day.year
                        dec = 0
                    m = int(self.text[dec:dec + 2])
                    d = int(self.text[dec + 3:])
                else:
                    if len(self.text) > 4:
                        y = int(self.text[0:4])
                        dec = 4
                    else:
                        y = day.year
                        dec = 0
                    m = int(self.text[dec:dec + 2])
                    d = int(self.text[dec + 2:])
                return date(y, m, d)
            except ValueError:
                errmsg = _("Error: could not understand date")
                return self.error(errmsg)

    def check_filename(self, mode):
        try:
            if self.text[-2] == " " and (self.text[-1] in [str(i) for i in range(8)]):
                # special case: hidden final tag
                f = open(self.text[:-2], mode)
                f.close()
            else:
                f = open(self.text, mode)
                f.close()
            return self.text
        except OSError:
            if mode == "rb":
                errmsg = _("Error: unable to read the file ")
            elif mode == "wb":
                errmsg = _("Error: unable to write the file ")
            return self.error(errmsg + self.text)

    def check_inthour(self):
        try:
            if int(self.text) < 0:
                errmsg = _("Error: should be higher than 0")
                return self.error(errmsg)
            if int(self.text) > 24:
                errmsg = _("Error: should be lower than 24")
                return self.error(errmsg)
            return int(self.text)
        except ValueError:
            errmsg = _("Error: must be an integer")
            return self.error(errmsg)
