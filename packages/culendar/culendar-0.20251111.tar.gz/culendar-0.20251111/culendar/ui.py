import curses
from datetime import (
    date,
    timedelta,
)

from .i18n import _


class UI:
    X_MAX_WITH_MOUSE = 223  # limit to clickable without bug
    XOFFSET = 6  # left offset to draw hours
    YOFFSETTOP = 3  # top offset to draw the header
    YOFFSETBOT = 4  # bottom offset to draw the footer

    def __init__(self, culendar, conf, screen):
        self.ctrl = culendar
        self.conf = conf
        self.screen = screen
        self.xmax = 0
        self.ymax = 0
        self.day_size = 0
        self.todocol = 0
        self.width = 0
        self.hour_size = 0
        self.lines = [[], []]
        self.do_update_on_resize = True
        self.update_screen_props()

    @property
    def hmin(self):
        return self.conf.hmin

    @property
    def hmax(self):
        return self.conf.hmax

    @property
    def daynb(self):
        return 7 if self.conf.WE else 5

    def update(self):
        self.update_screen_props()
        try:
        # everything changes, clear screen and redraw stuff
            self.clear_cal()
            self.draw_cal()
        # FIXME only catch proper exception or test for minimal terminal size instead
        except Exception as e:
            # culendar couldn't draw it: it's ridiculously small terminal
            self.dead_duck(e)

    def update_screen_props(self):
        self.ymax, self.xmax = self.screen.getmaxyx()
        if self.conf.mouse:
            self.xmax = min(self.xmax, self.X_MAX_WITH_MOUSE)
        if self.conf.todo:  # keep space for a todo
            xmax = self.xmax - round(self.xmax * self.conf.todowidth)
            self.day_size = (xmax - self.XOFFSET) // self.daynb
            # update xmax to be hour place + a multiple of day_size
            xmax = 7 + self.day_size * self.daynb
            self.todocol = self.xmax - xmax
            self.xmax = xmax
        else:
            self.day_size = (self.xmax - self.XOFFSET) // self.daynb
            self.todocol = 0
        self.width = self.xmax + self.todocol
        self.hour_size = (self.ymax - self.YOFFSETTOP - self.YOFFSETBOT) // (self.hmax - self.hmin)
        self.linepos()

    def linepos(self):
        # locations of [day lines, hour lines]
        self.lines = [[], []]
        self.lines[0].append(self.XOFFSET)
        for id in range(self.daynb - 1):
            self.lines[0].append(self.lines[0][id] + self.day_size)
        # the last one is in the last position
        self.lines[0].append(self.xmax - 1)
        self.lines[1].append(self.YOFFSETTOP)
        for ih in range(self.hmax - self.hmin):
            self.lines[1].append(self.lines[1][ih] + self.hour_size)

    def clear_cal(self):
        self.screen.clear()

    def draw_cal(self):
        if self.conf.mouse:
            self.draw_mousedeath()
        self.draw_table()
        self.draw_hours()
        self.draw_week()
        if self.conf.todo:
            self.draw_todo()

    def draw_mousedeath(self):
        ymax, real_xmax = self.screen.getmaxyx()
        if self.conf.todo:
            xmax = self.xmax + self.todocol
        else:
            xmax = self.xmax
        if real_xmax > xmax:
            msg = _(" ☠ DON'T CLICK HERE ☠ ")
            nbmsg = (real_xmax - xmax) // len(msg)
            remain = (real_xmax - xmax) - len(msg) * nbmsg
            msg = msg * nbmsg + msg[:remain]
            for y in range(self.ymax - 1):
                self.screen.addstr(y, xmax, msg, curses.A_REVERSE)
            self.screen.addstr(self.ymax - 1, xmax, msg[:-1], curses.A_REVERSE)

    def draw_table(self):
        # draw vertical lines to bottom point
        bottom = self.lines[1][-1] - 2
        self.screen.vline(2, 0, curses.ACS_VLINE, bottom)
        for ld in self.lines[0]:
            self.screen.vline(2, ld, curses.ACS_VLINE, bottom)
        # draw horizontal lines up to the end
        self.screen.hline(1, 1, curses.ACS_HLINE, self.xmax - 2)
        for lh in self.lines[1]:
            self.screen.hline(lh, 1, curses.ACS_HLINE, self.xmax - 2)
        for lh in self.lines[1]:
            for ld in self.lines[0]:
                # draw crosses
                self.screen.addch(lh, ld, curses.ACS_PLUS)
            # draw left and right tees
            self.screen.addch(lh, 0, curses.ACS_LTEE)
            self.screen.addch(lh, self.lines[0][-1], curses.ACS_RTEE)
        for ld in self.lines[0]:
            # draw top and bottom tees
            self.screen.addch(1, ld, curses.ACS_TTEE)
            self.screen.addch(self.lines[1][-1], ld, curses.ACS_BTEE)
        # draw corners
        self.screen.addch(1, 0, curses.ACS_ULCORNER)
        self.screen.addch(1, self.lines[0][-1], curses.ACS_URCORNER)
        self.screen.addch(self.lines[1][-1], 0, curses.ACS_LLCORNER)
        self.screen.addch(self.lines[1][-1], self.lines[0][-1], curses.ACS_LRCORNER)

    def draw_hours(self):
        self.screen.addstr(2, 1, _('hours'))
        for i, h in enumerate(range(self.hmin, self.hmax)):
            if h < 10:
                self.screen.addstr(self.lines[1][i], 3, f'{h}h')
            else:
                self.screen.addstr(self.lines[1][i], 2, f'{h}h')

    def draw_week(self):
        self.ctrl.update_calweek(False)
        self.draw_header()
        self.draw_daynames()  # redraw day names
        if self.conf.debug:
            for iday in range(self.daynb):
                self.draw_day(iday)
            self.draw_hl()
        else:
            try:
                for iday in range(self.daynb):
                    self.draw_day(iday)
                self.draw_hl()
            # FIXME only catch proper exception or test for minimal terminal size instead
            except Exception as e:  # couldn't draw it: too small terminal
                self.dead_duck(e)

    def draw_header(self):
        # erase previous header
        self.screen.hline(0, 0, " ", self.xmax - 1)
        if self.ctrl.todohl:
            style = curses.A_NORMAL
        else:
            style = curses.A_BOLD
        w = (
            _(' Week ') + str(self.ctrl.day.isocalendar()[1]) + ', '
            + self.ctrl.day.strftime("%B") + ' ' + str(self.ctrl.day.isocalendar()[0])
        )
        self.screen.addstr(0, (self.xmax - len(w)) // 2 + 1, w, style)
        self.screen.addstr(0, 0, str(self.conf.keys['help'][0]), curses.A_BOLD)
        self.screen.addstr(0, 1, _(": help"), curses.A_BOLD)

    def draw_daynames(self):
        # first day is monday = 1
        curday = date.fromordinal(self.ctrl.day.toordinal() - self.ctrl.day.isoweekday() + 1)
        for id in range(self.daynb):
            d = curday.strftime("%a %d/%m")
            pos = self.lines[0][id] + (self.day_size - len(d)) // 2 + 1
            if curday == self.ctrl.day:
                self.screen.addstr(2, pos, d, curses.A_BOLD)
            else:
                self.screen.addstr(2, pos, d)
            # increment day
            curday = date.fromordinal(curday.toordinal() + 1)

    def draw_day(self, iday=-1, hl=0):
        self.clear_day(iday)
        if iday == -1:  # defaults to current day
            iday = self.ctrl.day.isoweekday() - 1
            hl = 1  # not in draw_week, we'll draw the highlight
        calday = self.ctrl.calweek[iday]
        for e in calday.events:
            self.draw_event(e, curses.A_NORMAL)
        if hl:
            self.draw_hl()

    def clear_day(self, iday=-1):
        if iday == -1:  # defaults to current day
            iday = self.ctrl.day.isoweekday() - 1
        if iday == self.daynb - 1:
            width = self.lines[0][-1] - self.lines[0][-2] - 1
        else:
            width = self.day_size - 1
        # day_size - 1: doesn't include vertical separating lines
        for v in range(self.lines[1][0], self.lines[1][-1] + 1):
            # +1 to be sure to include last line
            self.screen.hline(v, self.lines[0][iday] + 1, " ", width)
            if v in self.lines[1]:
                # if it's a horizontal line, redraw it
                self.screen.hline(v, self.lines[0][iday] + 1, curses.ACS_HLINE, width)

    def draw_event(self, e, flag):
        # flag is bold if highlighted, normal if not
        try:
            colour = self.conf.colours[e.tag] + curses.A_REVERSE + flag
        except Exception:  # alphabetic tag, that's a caldav, use e.color
            colour = self.conf.colours[e.colour] + curses.A_REVERSE + flag
        normal = curses.A_REVERSE + flag
        if type(e.hlines) == tuple:  # cf calendary.py compute_hlines()
            dduck = [
                _(r"\_x<  too   >x_/")[0:e.hlines[1]],
                _(r"\_x<  many  >x_/")[0:e.hlines[1]],
                _(r"\_x< events >x_/")[0:e.hlines[1]],
            ]
            for iv, v in enumerate(e.vlines):
                self.screen.addstr(v, e.hlines[0], dduck[iv % 3])
            return
        width = len(e.hlines)
        # draw background
        for v in e.vlines:
            if self.conf.colourset == 0:
                self.screen.hline(v, e.hlines[0], " ", width, colour)
            elif self.conf.colourset == 1:
                self.screen.addstr(v, e.hlines[0], " ", colour)
                self.screen.addstr(v, e.hlines[0] + width - 1, " ", colour)
                self.screen.hline(v, e.hlines[0] + 1, " ", width - 2, normal)
            elif self.conf.colourset == 2:
                self.screen.hline(v, e.hlines[0], " ", width, normal)
            else:
                self.screen.hline(v, e.hlines[0], " ", width, normal)
        # prepare the text
        t = e.summary
        if len(t) > width:
            t = t[0:width]
        # draw text for all cases, bold for highlighted event
        posx = e.hlines[0] + (width - len(t)) // 2
        posy = e.vlines[0] + (e.vlines[-1] - e.vlines[0]) // 2
        if self.conf.colourset == 0:
            self.screen.addstr(posy, posx, t, colour)
        elif self.conf.colourset == 1:
            self.screen.addstr(posy, posx, t, normal)
            if len(t) == width:
                self.screen.addstr(posy, posx, t[0], colour)
                self.screen.addstr(posy, posx + width - 1, t[-1], colour)
        elif self.conf.colourset == 2:
            self.screen.addstr(posy, posx, t, colour)
        else:
            self.screen.addstr(posy, posx, t, normal)
        # if there is a location, add it if it's a two lines event
        if e.place != "" and e.vlines[-1] > e.vlines[0]:
            # prepare the text
            p = e.place
            if len(p) > width:
                p = p[0:width]
            posx = e.hlines[0] + (width - len(p)) // 2
            if self.conf.colourset == 0:
                self.screen.addstr(posy + 1, posx, p, colour)
            elif self.conf.colourset == 1:
                self.screen.addstr(posy + 1, posx, p, normal)
                if len(p) == width:
                    self.screen.addstr(posy + 1, posx, p[0], colour)
                    self.screen.addstr(posy + 1, posx + width - 1, p[-1], colour)
            elif self.conf.colourset == 2:
                self.screen.addstr(posy + 1, posx, p, colour)
            else:
                self.screen.addstr(posy + 1, posx, p, normal)

    def draw_hl(self):
        if self.conf.todo and self.ctrl.todohl > 0:
            self.draw_todo()  # erase previous hl, draw new one
            return
        # else: normal event hl
        self.clear_hl()
        self.draw_daynames()
        iday = self.ctrl.day.isoweekday() - 1
        maxhl = len(self.ctrl.calweek[iday].events)
        # is there anything to highlight?
        if self.ctrl.ehl < maxhl and maxhl > 0:
            self.draw_event(self.ctrl.calweek[iday].events[self.ctrl.ehl], curses.A_BOLD)
            self.draw_footer(self.ctrl.calweek[iday].events[self.ctrl.ehl])

    def clear_hl(self):
        self.clear_footer()
        # we toggled the WE off; nothing to do
        if self.ctrl.is_hl_hidden_WE:
            pass
        # if we change the hl of current day
        elif self.ctrl.is_hl_same_day:
            # just redraw in normal font
            iday = self.ctrl.day.isoweekday() - 1
            maxhl = len(self.ctrl.calweek[iday].events)
            # is there anything to highlight?
            if self.ctrl.prevehl < maxhl and maxhl > 0:
                self.draw_event(self.ctrl.calweek[iday].events[self.ctrl.prevehl], curses.A_NORMAL)
        # if we change from less than a week
        elif self.ctrl.is_hl_same_week:
            # redraw previous day
            calday = self.ctrl.calweek[self.ctrl.previous_day.isoweekday() - 1]
            for e in calday.events:
                self.draw_event(e, curses.A_NORMAL)
        # else: nothing to do, new week clears everything

    def clear_footer(self):
        for y in range(max(0, self.ymax - 3), self.ymax):
            self.screen.hline(y, 0, " ", self.width)

    def text_in_footer(self, *messages: list[str]):
        if len(messages) > 3:
            raise ValueError("footer text can only takes up to 3 message lines")
        for i, msg in enumerate(messages[::-1], 1):
            self.screen.addstr(self.ymax - i, 0, msg)

    def draw_footer(self, e):
        enddate = e.original.date + timedelta(seconds=e.original.duration)
        if e.place:
            desc = e.summary + " @ " + e.place
        else:
            desc = e.summary
        text = _('Summary: ') + desc
        self.text_in_footer(
            _('Begin date: {}').format(e.original.date),
            _('End date:   {}').format(enddate),
            text[:self.width - 1],
        )

    def draw_todo(self):
        if self.ctrl.todohl:
            style = curses.A_BOLD
        else:
            style = curses.A_NORMAL
        title = _("TODO")  # noqa: T101
        xpos = self.xmax + (self.todocol - len(title)) // 2
        self.screen.addch(0, self.xmax - 1, curses.ACS_VLINE)
        self.screen.addch(1, self.xmax - 1, curses.ACS_PLUS)
        self.screen.addch(self.lines[1][-1], self.xmax - 1, curses.ACS_RTEE)
        self.screen.vline(self.lines[1][-1] + 1, self.xmax - 1, curses.ACS_VLINE, self.ymax - self.lines[1][-1] - 4)
        self.screen.hline(1, self.xmax, curses.ACS_HLINE, self.todocol)
        self.screen.addstr(0, xpos, title, style)
        for idx, item in enumerate(self.ctrl.todo.events):
            if idx + 1 == self.ctrl.todohl:
                style = curses.A_BOLD
            else:
                style = curses.A_NORMAL
            if item.date:
                date = item.date.strftime("%d/%m")
                self.screen.addstr(2 + idx, self.xmax + self.todocol - len(date), date, style)
            if len(item.summary) < self.todocol:
                # + " " to ensure a space before the date
                text = item.summary + " "
            else:
                text = item.summary[:self.todocol - 1]
            self.screen.addstr(2 + idx, self.xmax + 1, text, style)
        if self.ctrl.todohl > 0 and len(self.ctrl.todo.events) > 0:
            self.draw_todohl()

    def draw_todohl(self):
        """draw highlighted todo in the footer"""
        self.clear_footer()
        if len(self.ctrl.todo.events) + 1 > self.ctrl.todohl:
            item = self.ctrl.todo.events[self.ctrl.todohl - 1]
            date = ""
            if item.date:
                date = (
                    " -- " + str(item.date.day)
                    + "/" + str(item.date.month)
                    + "/" + str(item.date.year)
                )
            text = item.summary + date
            self.text_in_footer(text[:self.width - 1])

    def clear_todo(self):
        for y in range(2, self.ymax):
            self.screen.hline(y, self.xmax, " ", self.todocol)

    def dead_duck(self, exception: Exception):
        text = _(r"\_x< A dead duck. That's all such a small terminal deserves.")
        if self.conf.debug:
            curses.endwin()
            print(text)
        else:
            self.clear_cal()
            self.screen.addstr(0, 0, text[0:(self.width - 1) * (self.ymax - 1)])
            key = ""
            while key not in self.conf.keys['quit'] and key != 'KEY_RESIZE':
                key = self.getkey()
            if key in self.conf.keys['quit']:
                if self.conf.debug:
                    print(exception)
                exit()
            else:
                self.update()

    def getkey(self):
        """
        function to deal properly with all kind of typed key
        get_wch() returns a str for standard keys;
        for functions keys, sometimes string names, sometimes escaped sequences,
        sometimes ordinal integers.
        stupid function that translates different possibilities into strings
        for the fun, it's terminal-dependant

        roughly tested with urvxt, screen, xterm terminals
        probably doesn't work with yours
        """
        key = self.screen.get_wch()
        if key == "":
            # half delay mode of 1/10s: no input key raises an error
            # assumption: no humain being type ESC + real keys so fast
            curses.halfdelay(1)
            try:
                # get the false keys and stack it
                while 1:
                    key += str(self.screen.get_wch())
            except Exception:
                # the bundle of special keys stopped:
                # back to normal mode
                curses.cbreak()
                if key in ["[b", "[1;2B"]:
                    key = "kDN"  # shift down
                elif key in ["[a", "[1;2A"]:
                    key = "kUP"  # shift right
                elif key in ["[d", "[1;2D"]:
                    key = "KEY_SLEFT"
                elif key in ["[c", "[1;2C"]:
                    key = "KEY_SRIGHT"
                # non curses character: control+key
                elif key in ["Ob", "[1;5B"]:
                    key = "KEY_CDOWN"
                elif key in ["Oa", "[1;5A"]:
                    key = "KEY_CUP"
                elif key in ["Od", "[1;5D"]:
                    key = "KEY_CLEFT"
                elif key in ["Oc", "[1;5C"]:
                    key = "KEY_CRIGHT"
                elif key in ["OP"]:
                    key = "KEY_F(1)"
                elif key in ["OQ"]:
                    key = "KEY_F(2)"
                elif key in ["OR"]:
                    key = "KEY_F(3)"
                elif key in ["OS"]:
                    key = "KEY_F(4)"
                elif key in ["[1~", "OH", "[H"]:
                    key = "KEY_HOME"
                elif key in ["[4~", "OF", "[F"]:
                    key = "KEY_END"
                else:
                    if not self.conf.debug and len(key) > 1:
                        key = ""
        if type(key) == int:
            if key in [410]:
                key = "KEY_RESIZE"
            elif key in [258]:
                key = "KEY_DOWN"
            elif key in [259]:
                key = "KEY_UP"
            elif key in [260]:
                key = "KEY_LEFT"
            elif key in [261]:
                key = "KEY_RIGHT"
            elif key in [262, 362]:
                key = "KEY_HOME"
            elif key in [360, 385]:
                key = "KEY_END"
            elif key in [263]:
                key = "KEY_BACKSPACE"
            elif key in [265]:
                key = "KEY_F(1)"
            elif key in [266]:
                key = "KEY_F(2)"
            elif key in [267]:
                key = "KEY_F(3)"
            elif key in [268]:
                key = "KEY_F(4)"
            elif key in [269]:
                key = "KEY_F(5)"
            elif key in [270]:
                key = "KEY_F(6)"
            elif key in [271]:
                key = "KEY_F(7)"
            elif key in [272]:
                key = "KEY_F(8)"
            elif key in [273]:
                key = "KEY_F(9)"
            elif key in [274]:
                key = "KEY_F(10)"
            elif key in [275]:
                key = "KEY_F(11)"
            elif key in [276]:
                key = "KEY_F(12)"
            elif key in [330]:
                key = "KEY_DC"
            elif key in [331]:
                key = "KEY_IC"
            elif key in [338]:
                key = "KEY_NPAGE"
            elif key in [339]:
                key = "KEY_PPAGE"
            elif key in [353]:
                key = "KEY_BTAB"
            elif key in [513, 336]:
                key = "kDN"
            elif key in [529, 337]:
                key = "kUP"
            elif key in [393]:
                key = "KEY_SLEFT"
            elif key in [402]:
                key = "KEY_SRIGHT"
            # non curses character: control+key
            elif key in [514, 525]:
                key = "KEY_CDOWN"
            elif key in [530, 566]:
                key = "KEY_CUP"
            elif key in [523, 545]:
                key = "KEY_CLEFT"
            elif key in [528, 560]:
                key = "KEY_CRIGHT"
            elif key in [409]:
                key = "KEY_MOUSE"
            else:
                if not self.conf.debug:
                    key = ""
                else:
                    key = str(key)
        if key == "KEY_RESIZE" and self.do_update_on_resize:
            self.update()
        return key

    def get_mouse_position(self):
        try:
            _, x, y, _, _ = curses.getmouse()
        except Exception:
            x = -1
            y = -1
        return x, y

    def inform(self, *messages: list[str]):
        """use footer to give feedback"""
        self.clear_footer()
        self.text_in_footer(*[
            msg[0:self.width - 1] for msg in messages
        ])
        self.screen.refresh()

    def debug(self, elt):
        self.screen.addstr(self.ymax - 2, 50, 'debug:   {}'.format(elt))
        self.screen.getch()  # just a pause
        self.screen.hline(self.ymax - 2, 1, " ", self.width - 2)
