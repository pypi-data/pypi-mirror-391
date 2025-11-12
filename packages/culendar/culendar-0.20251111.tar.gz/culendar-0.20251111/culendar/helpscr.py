import curses

from .i18n import _


class Help:
    def __init__(self, ui, conf):
        self.ui = ui
        self._screen = ui.screen
        self._conf = conf
        # help categories
        self._moving = [
            'nextday', 'prevday', 'nextweek', 'prevweek',
            'nextmonth', 'prevmonth', 'nextyear', 'prevyear',
            'today', 'startweek', 'endweek', 'setday',
        ]
        self._events = [
            'nextevent', 'prevevent', 'addevent',
            'delevent',  'editevent', 'tagevent', 'copyevent',
            'minusshifthour', 'shifthour', 'minusshiftday',
            'shiftday',
        ]
        self._io = ['save', 'import', 'export']
        self._misc = ['toggleWE', 'redraw', 'sync', 'setconfig', 'help', 'quit']
        self._categories = [
            [self._moving, _("Choosing date:")],
            [self._events, _("Dealing with events:")],
            [self._io, _("Reading and writing files:")],
            [self._misc, _("Miscellaneous:")],
        ]
        # descriptions of all possibilities
        self._desc = {}
        self._desc['nextday'] = _('Select next day')
        self._desc['prevday'] = _('Select previous day')
        self._desc['nextweek'] = _('Go to next week')
        self._desc['prevweek'] = _('Go to previous week')
        self._desc['nextmonth'] = _('Go to next month')
        self._desc['prevmonth'] = _('Go to previous month')
        self._desc['nextyear'] = _('Go to next year')
        self._desc['prevyear'] = _('Go to previous year')
        self._desc['today'] = _('Go to today')
        self._desc['startweek'] = _('Go to first day of current week')
        self._desc['endweek'] = _('Go to last day of current week')
        self._desc['setday'] = _('Enter the day to go')
        desc = _('Select next event of current day or next todo')
        self._desc['nextevent'] = desc
        desc = _('Select previous event of current day or previous todo')
        self._desc['prevevent'] = desc
        self._desc['addevent'] = _('Add an event or todo')
        self._desc['delevent'] = _('Delete selected event or todo (if any)')
        self._desc['editevent'] = _('Edit selected event todo (if any)')
        desc = _('Set a numerical [0-7] tag to selected event')
        self._desc['tagevent'] = desc
        self._desc['tagevent2'] = _(' Alphabetic tag puts event on CalDAV')
        desc = _('Copy selected event to next day, week, month or year')
        self._desc['copyevent'] = desc
        desc = _("Shift selected event one hour earlier")
        self._desc['minusshifthour'] = desc
        self._desc['shifthour'] = _("Shift selected event one hour later")
        desc = _("Shift selected event one day earlier")
        self._desc['minusshiftday'] = desc
        self._desc['shiftday'] = _("Shift selected event one day later")
        self._desc['save'] = _('Save calendar and configuration')
        desc = _('Import a calendar (from iCalendar or calcurse)')
        self._desc['import'] = desc
        self._desc['export'] = _('Export calendar (to iCalendar or calcurse)')
        self._desc['toggleWE'] = _('Toggle presence of week-end')
        self._desc['toggletodo'] = _('Toggle presence of Todo list')
        self._desc['redraw'] = _('Redraw screen')
        self._desc['sync'] = _('Synchronize Caldavs and Webcals')
        self._desc['setconfig'] = _('Configure Culendar')
        self._desc['help'] = _('Get this help')
        self._desc['quit'] = _('Quit Culendar')

    def draw_help_screen(self):
        self._screen.clear()
        self._y, self._x = self._screen.getmaxyx()
        # if ridiculously small terminal
        if self._x < 25 or self._y < 5:
            self._screen.clear()
            text = _(r"\_x< A dead duck. That's all such a small terminal deserves.")
            self._screen.addstr(0, 0, text[0:(self._x-1)*(self._y-1)])
            key = ""
            while key not in self._conf.keys['quit'] and key != 'KEY_RESIZE':
                key = self.ui.getkey()
                if key in self._conf.keys['quit']:
                    exit()
                else:
                    self.draw_help_screen()
        # draw screen
        headleft = _("q: quit help")
        headcenter = _("Culendar help screen")
        headcenter += " 0.20251111"
        self._screen.border()
        self._screen.hline(2, 1, curses.ACS_HLINE, self._x - 2)
        self._screen.addch(2, 0, curses.ACS_LTEE)
        self._screen.addch(2, self._x - 1, curses.ACS_RTEE)
        self._screen.addstr(1, 1, headleft, curses.A_BOLD)
        self._screen.addstr(1, (self._x - len(headcenter)) // 2 + 1, headcenter, curses.A_BOLD)
        # create full pad for self._screenolling help
        # counting lines for each category
        padlines = (
            3
            + len(self._moving) + 4 + len(self._events) + 4
            + len(self._io) + 4 + len(self._misc) + 4
        )
        colsize = round((self._x - 2) / 4)
        # pad columns: starting description + maximum description
        padcols = 2 * colsize + max(len(v) for v in self._desc.values())
        self._pad = curses.newpad(padlines, padcols)
        self._pad.scrollok(True)
        self._screen.refresh()  # if not present, pad is ignored
        self._pad.addstr(0, 0, _("Key(s)"))
        self._pad.addstr(0, colsize, _("Function name"))
        self._pad.addstr(0, 2 * colsize, _("Function description"))
        shift = 2
        for category in self._categories:
            # print category as subtitle
            self._pad.addstr(shift, 0, category[1], curses.A_BOLD)
            shift += 2
            if category[1] == _("Miscellaneous:"):
                # Repetition is not really a command
                # treat it separately
                self._pad.addstr(shift, 0, _("number n>0"))
                # second column: small name
                self._pad.addstr(shift, colsize, "repetition")
                # third column: description
                desc = _("Repeat following command n times (when reasonable)")
                self._pad.addstr(shift, 2*colsize, desc)
                shift += 1
            for i, k in enumerate(category[0]):
                # first column: keys
                listkeys = ""
                for ck in self._conf.keys[k]:
                    if ck == "\t":
                        listkeys += "TAB, "
                    elif ck == " ":
                        listkeys += "SPACE, "
                    else:
                        listkeys += ck+", "
                listkeys = listkeys[:-2]  # erase final comma
                self._pad.addstr(i + shift, 0, listkeys)
                # second column: small name
                self._pad.addstr(i + shift, colsize, k)
                # third column: description
                self._pad.addstr(i + shift, 2 * colsize, self._desc[k])
                if k == "tagevent":
                    shift += 1
                    self._pad.addstr(i + shift, 2 * colsize, self._desc["tagevent2"])
            shift += len(category[0]) + 2
        self._top = 0
        # the lines available for the pad
        self._padavail = self._y - 4
        # to have the bottom of the pad on the bottom of the screen
        self._maxtop = max(0, padlines - self._padavail)

    def help_screen(self):
        self.draw_help_screen()
        self._pad.refresh(self._top, 0, 3, 1, self._y - 2, self._x - 2)
        key = self.ui.getkey()
        while True:
            if key == 'KEY_RESIZE':
                self.draw_help_screen()
            if key == 'KEY_UP':
                self._top = max(0, self._top - 1)
            if key == 'KEY_DOWN':
                self._top = min(self._maxtop, self._top + 1)
            if key == 'KEY_PPAGE':
                self._top = max(0, self._top - self._padavail)
            if key == 'KEY_NPAGE':
                self._top = min(self._maxtop, self._top + self._padavail)
            if key in self._conf.keys['quit']:
                return
            self._pad.refresh(self._top, 0, 3, 1, self._y - 2, self._x - 2)
            key = self.ui.getkey()
