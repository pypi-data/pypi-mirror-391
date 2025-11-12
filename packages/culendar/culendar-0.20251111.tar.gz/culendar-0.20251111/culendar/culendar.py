from datetime import (
    date,
    timedelta,
)
from re import findall
from typing import (
    List,
    Optional,
)

from .calendar import (
    Agenda,
    Event,
    SubEvent
)
from .config import Config
from .confscr import Conf
from .culdav import Culdav
from .helpscr import Help
from .i18n import _
from .inputs import Input
from .ui import UI


class Culendar:
    WE_DAYS = (6, 7)  # Saturday, Sunday

    conf: Config
    ui: UI
    cal: Agenda
    todo: Agenda
    caldav: Culdav
    calweek: List[Agenda]
    count: int  # repetitions of the next command
    prevehl: int
    ehl: int  # highlighted event of current day
    todohl: int  # highlighted todo, if any, index starts at 1, 0 means focus on calendar
    _prevday: date
    _day: date

    def __init__(self, screen):
        self.conf = Config()
        self.ui = UI(self, self.conf, screen)
        self.cal, self.todo = Agenda.load(self.conf.datafile, self.conf.todofile)
        self.culdav = Culdav(self.conf.caldav, self.conf.datapath, self.ui)
        self.culdav.initialize()  # get cals and associated tags
        self.culdav.sync()  # update and redefine _events
        self.calweek = []
        self.count = 0
        self.prevehl = self.ehl = self.todohl = 0
        self.day = None  # current day
        self.ui.update()

    @property
    def day(self):
        return self._day

    @day.setter
    def day(self, day: Optional[date]):
        if day is None:
            self._prevday = date(1, 1, 1)
            self._day = date.today()
        else:
            self._prevday = self._day
            self.changehl(-self.ehl)  # resets highlight
            self._day = day
        self.avoid_WE(self.previous_day <= self.day)
        if not self.is_hl_same_week:
            # if it's a new week, recompute calweek
            self.update_calweek()

    @property
    def daynb(self):
        return self.ui.daynb

    @property
    def previous_day(self):
        return self._prevday

    def avoid_WE(self, forward=True):
        if self.conf.WE == 0:
            while self._day.isoweekday() in self.WE_DAYS:
                if forward:
                    self._day = date.fromordinal(self._day.toordinal() + 1)
                else:
                    self._day = date.fromordinal(self._day.toordinal() - 1)

    def update_calweek(self, autosync: Optional[bool] = None):
        """extraction of the agenda of all interesting days"""
        self.calweek = Agenda.extract_week(self.cal, self.culdav, self.day, self.ui, self.conf.autosync if autosync is None else autosync)

    def set_same_day(self):
        self._prevday = self._day

    @property
    def is_hl_same_day(self):
        return self.previous_day == self.day

    @property
    def is_hl_hidden_WE(self):
        iprevday = self.previous_day.isoweekday() - 1
        return iprevday >= self.daynb

    @property
    def is_hl_same_week(self):
        """same year and same isoweek"""
        return self.day.isocalendar()[:2] == self.previous_day.isocalendar()[:2]

    def toggle_WE(self):
        self.conf.WE = 1 - self.conf.WE
        self.avoid_WE(False)
        self.ui.update()

    def run_loop(self):
        key = ""
        while key not in self.conf.keys['quit']:
            key = self.ui.getkey()
            # repeat action at least 1, or the entered count value
            repetitions = max(1, self.count)
            # changing day or week or year
            if key in self.conf.keys['prevday']:
                self.addday(-repetitions)
            if key in self.conf.keys['nextday']:
                self.addday(+repetitions)
            if key in self.conf.keys['nextweek']:
                self.addday(+7 * repetitions)
            if key in self.conf.keys['prevweek']:
                self.addday(-7 * repetitions)
            if key in self.conf.keys['nextmonth']:
                self.addmonth(+repetitions)
            if key in self.conf.keys['prevmonth']:
                self.addmonth(-repetitions)
            if key in self.conf.keys['nextyear']:
                self.addyear(+repetitions)
            if key in self.conf.keys['prevyear']:
                self.addyear(-repetitions)
            if key in self.conf.keys['today']:
                self.changeday(date.today())
            if key in self.conf.keys['setday']:
                self.changeday()
            if key in self.conf.keys['startweek']:
                self.addday(-self.day.isoweekday() + 1)
            if key in self.conf.keys['endweek']:
                self.addday(-self.day.isoweekday() + self.daynb)
            # change highlighted event of current day
            if key in self.conf.keys['nextevent']:
                self.set_same_day()
                self.changehl(+repetitions)
                self.ui.draw_hl()
            if key in self.conf.keys['prevevent']:
                self.set_same_day()
                self.changehl(-repetitions)
                self.ui.draw_hl()
            # delete, edit, add (highlighted) event (if existing)
            if key in self.conf.keys['delevent']:
                self.del_event()
            if key in self.conf.keys['editevent']:
                self.edit_event()
            if key in self.conf.keys['addevent']:
                self.add_event()
            if key in self.conf.keys['tagevent']:
                self.tag_event()
            if key in self.conf.keys['copyevent']:
                self.copy_event(repetitions)
            if key in self.conf.keys['minusshifthour']:
                self.shift_event(-repetitions)
            if key in self.conf.keys['minusshiftday']:
                self.shift_event(-repetitions * 24)
            if key in self.conf.keys['shifthour']:
                self.shift_event(+repetitions)
            if key in self.conf.keys['shiftday']:
                self.shift_event(+repetitions * 24)
            # toggle week-end display
            if key in self.conf.keys['toggleWE']:
                self.toggle_WE()
            # toggle Todo bar focus (appear/disappear)
            if key in self.conf.keys['toggletodo']:
                self.toggle_TODO()
            if key in self.conf.keys['redraw']:
                self.ui.clear_cal()
                self.ui.draw_cal()
            if key in self.conf.keys['sync']:
                self.sync_caldav()
            if key in self.conf.keys['help']:
                self.ui.do_update_on_resize = False
                help = Help(self.ui, self.conf)
                help.help_screen()
                self.ui.update()
                self.ui.do_update_on_resize = True
            if key in self.conf.keys['save']:
                self.ui.inform(_("Saving configuration and calendar…"))
                self.conf.save()
                self.save()
                self.ui.inform(_("Configuration and calendar saved!"))
            if key in self.conf.keys['setconfig']:
                self.ui.do_update_on_resize = False
                conf = Conf(self.ui, self.conf, self.culdav)
                # real copy to keep a backup
                old_caldav_conf = [conf for conf in self.conf.caldav]
                # conf_screen returns a possibly modified conf
                self.conf = conf.conf_screen()
                self.ui.do_update_on_resize = True
                if old_caldav_conf != self.conf.caldav:
                    # FIXME should be updated with self.conf.caldav instead
                    self.culdav.update(old_caldav_conf)
                # redraw, works even in case of KEY_RESIZE inside help
                self.ui.update()
            if key in self.conf.keys['import']:
                self.importcal()
            if key in self.conf.keys['export']:
                self.exportcal()
            if key == "KEY_MOUSE":
                self.clicked()
            # define the buffer and the repetition of actions
            try:  # is the key an integer?
                # type 1 then 2, get 12
                self.count = self.count * 10 + int(key)
            except ValueError:  # not a number, back to zero
                self.count = 0
        # autosave on quit
        if self.conf.autosave:
            self.conf.save()
            self.save()

    def toggle_TODO(self):
        # if todohl > 1, Todo bar is in highlight mode, remove it
        if self.todohl > 0:
            self.conf.todo = False
            self.todohl = 0
            self.ui.update()  # recompute everything
        elif self.conf.todo:  # Todo bar is unhighlighted
            self.todohl = 1
            self.ui.draw_day()  # remove the day hl
            self.ui.draw_header()  # remove the week hl
            self.ui.draw_hl()  # hl the Todo item
        else:  # make appear the Todo bar
            self.conf.todo = True
            self.todohl = 1
            self.ui.update()  # recompute everything

    def addyear(self, shift):
        try:
            daytmp = self.day.replace(year=self.day.year + shift)
            delta = daytmp - self.day
            self.addday(delta.days)  # use the proper function
        except Exception:
            # we can't, that's a daytmp is out of range for month
            # ie, from 19 February to 31 February
            self.addday(shift * 365)  # fallback function

    def addmonth(self, shift):
        newmonth = (self.day.month - 1 + shift) % 12 + 1
        try:
            if abs(self.day.month - newmonth) != abs(shift):  # year changed
                self.addyear(int(shift / abs(shift)))  # sign(shift)
            daytmp = self.day.replace(month=newmonth)
            delta = daytmp - self.day
            self.addday(delta.days)  # use the proper function
        except Exception:
            # we can't, that's a day is out of range for month
            # ie, from 31 January to 31 February
            self.addday(shift * 30)  # fallback function

    def addday(self, shift):
        # change day: autoswitch from todo bar if any
        if self.todohl:
            self.todohl = 0
            self.ui.draw_header()  # hl the weekbar
            self.ui.draw_todo()  # un-hl the todo bar
        # set a new day
        self.day = self.day + timedelta(days=shift)
        # update the highlight, which remembers old values of day and ehl
        self.changehl(0)
        self.ui.draw_week()

    def changehl(self, inc):
        if self.todohl:  # Todo bar is highlighted
            maxhl = len(self.todo.events)
            self.todohl = (self.todohl + inc) % (maxhl + 1)
            if self.todohl == 0:
                self.todohl = 1  # todo hl starts at index 1
        else:
            self.prevehl = self.ehl
            iday = self.day.isoweekday() - 1
            maxhl = len(self.calweek[iday].events)
            if maxhl > 0:
                self.ehl = (self.ehl + inc) % maxhl
            else:
                self.ehl = 0

    def changeday(self, day=None):
        self.ui.clear_footer()
        if not day:
            day = self.ask_day()
            if day == "CUL_CANCEL":
                return  # cancel the change of day
        self.day = day
        self.avoid_WE(False)
        self.ui.draw_week()

    def sync_caldav(self):
        # update caldavs only
        self.culdav.sync()
        # redraw if something changed
        self.ui.clear_cal()
        self.ui.draw_cal()

###############################################################################
#       event functions
###############################################################################

    def del_event(self):
        if self.todohl > 0:
            self.del_todo()
            return
        inform = 0
        # select highlighted event if existing
        iday = self.day.isoweekday() - 1
        if len(self.calweek[iday].events) > self.ehl:
            event = self.calweek[iday].events[self.ehl]
            # clear the footer event
            self.ui.clear_footer()
            if event.caldav:
                if event.caldav == "webcal":
                    # webcals are read-only
                    msg = _("Error: can't delete webcal event or offline copy")
                    self.ui.text_in_footer(msg, _("Press any key to continue"))
                    self.ui.getkey()
                    self.ui.clear_footer()
                else:
                    # delete from local cal in order to avoid syncing caldav to update events
                    self.culdav.del_event(event)
            else:
                # delete it from the cal
                self.cal.del_event(event)
            self.update_calweek(False)
            # redraw day without the deleted event
            self.changehl(0)  # to update the highlighted event
            self.ui.draw_week()  # week instead of day for multidays event
            if inform:
                self.ui.inform(msg + event.url)

    def del_todo(self):
        # reminder: todo_hl starts at index 1
        self.todo.del_event(self.todo.events[self.todohl - 1])
        self.changehl(0)  # to update the highlighted event
        self.ui.clear_todo()
        self.ui.draw_todo()

    def edit_event(self):
        if self.todohl > 0:
            self.edit_todo()
            return
        # select highlighted event if existing
        iday = self.day.isoweekday() - 1
        if len(self.calweek[iday].events) > self.ehl:
            event = self.calweek[iday].events[self.ehl].original
            # we can't edit webcal events
            if event.caldav == "webcal":
                # webcals are read-only
                self.ui.clear_footer()
                msg = _("Error: can't delete webcal event")
                self.ui.text_in_footer(msg, _("Press any key to continue"))
                self.ui.getkey()
                self.ui.clear_footer()
                return  # exit here
            # the footer will be useful, clear it
            self.ui.clear_footer()
            # ask question
            label = _("Edit: (1) [s]tart time, (2) [e]nd time, (3) [d]escription, (4) [p]lace")
            keys = findall(r'\[(.)\]', label)
            self.ui.text_in_footer(label, '')
            s = self.ui.getkey()
            self.ui.clear_footer()
            if s in ('1', keys[0]):
                ed = event.date + timedelta(seconds=event.duration)
                sd = self.ask_starttime()
                if sd == "CUL_CANCEL":
                    return   # cancel edit event
                if sd > ed:  # shift the event to the new starting hour
                    d = event.duration
                else:  # keep the same end hour
                    # recompute duration
                    d = (ed - sd).total_seconds()
                event.date = sd
                event.duration = d
            elif s in ('2', keys[1]):
                ed = self.ask_endtime(event.date)
                if ed == "CUL_CANCEL":
                    return  # cancel edit event
                d = (ed - event.date).total_seconds()
                event.duration = d
            elif s in ('3', keys[2]):
                desc, place = self.ask_description(event)
                if desc == "CUL_CANCEL":
                    return  # canceled edition
                event.summary = desc
                if place:  # non empty
                    event.place = place
            elif s in ('4', keys[3]):
                place = self.ask_place(event)
                if place == "CUL_CANCEL":
                    return  # canceled edition
                event.place = place
            else:
                return
            # sort the events
            self.cal.sort()
            self.update_calweek(False)
            if event.caldav:  # update the corresponding caldav
                self.culdav.del_event(event)
                self.culdav.add_event(event, event.caldav)
            # redraw full week for multidays events
            self.ui.draw_week()

    def edit_todo(self):
        # the footer will be useful, clear it
        self.ui.clear_footer()
        if len(self.todo.events) < self.todohl - 1:
            return
        todo = self.todo.events[self.todohl - 1]
        question = _("Edit: (1) [i]tem, (2) [d]ate, (3) [r]emove date")
        keys = findall(r'\[(.)\]', question)
        self.ui.text_in_footer(question, '')
        s = self.getkey()
        if s == "KEY_RESIZE":
            self.update()
            return
        if s in ('1', keys[0]):
            item, day = self.ask_todo(todo)
            if day:
                todo.date = day
            todo.summary = item
        elif s in ('2', keys[1]):
            day = self.ask_day()
            if type(day) == date:
                todo.date = day
        elif s in ('3', keys[2]):
            todo.date = None
        else:
            self.draw_todo()
            return
        self.todo.sort()
        self.ui.clear_todo()
        self.ui.draw_todo()

    def add_event(self):
        # the footer will be useful, clear it
        self.ui.clear_footer()
        if self.todohl > 0:
            self.add_todo()
            return
        sd = self.ask_starttime()
        if sd == "CUL_CANCEL":
            return  # cancel add event
        ed = self.ask_endtime(sd)
        if ed == "CUL_CANCEL":
            return  # cancel add event
        duration = (ed - sd).total_seconds()
        desc, place = self.ask_description()
        if desc == "CUL_CANCEL":
            return  # cancel add event
        # create event
        e = Event(sd, duration, desc, place)
        self.cal.add_event(e)
        self.cal.sort()
        self.update_calweek(False)
        calday = self.calweek[self.day.isoweekday() - 1]
        # determine the ehl to set to hl this event
        self.prevehl = self.ehl
        try:
            self.ehl = calday.events.index(e)
            # it crashes if the event is split on several days
            # cause the full event doesn't exist anymore
        except ValueError:
           for ev in calday.events:
                if isinstance(ev, SubEvent) and ev.original == e:
                    self.ehl = calday.events.index(ev)
        self.ui.draw_week()  # redraw all week for multidays event

    def add_todo(self):
        summ, date = self.ask_todo()
        if summ == "CUL_CANCEL":
            return  # canceled new item
        item = Event(date, None, summary=summ, tag=0)
        self.todo.add_event(item)
        self.todo.sort()
        self.ui.clear_todo()
        self.ui.draw_todo()

    def clicked(self):
        x, y = self.ui.get_mouse_position()
        # the todo list has been clicked
        if self.conf.todo and x >= self.ui.xmax:
            if not self.todohl:
                self.toggle_TODO()
            if (y - 2) in range(len(self.todo.events)):
                # select a todo, starting on line 2, todohl starts at 1
                self.todohl = y - 2 + 1
                self.ui.draw_todo()
        elif x <= self.ui.XOFFSET:
            # clicked on the hour? Why?
            pass
        else:  # clicked on the main culendar
            if self.todohl:  # todo list is highlighted
                self.todohl = 0
                self.ui.draw_todo()  # not anymore
            # select the current day
            day_lines = self.ui.lines[0]
            iday = 0
            for i in range(len(day_lines)):
                if x > day_lines[i]:
                    iday += 1
            # Monday is 1
            cur_iday = self.day.isoweekday()
            self.addday(iday - cur_iday)
            # have we clicked on an event?
            calday = self.calweek[iday - 1]
            # Monday is 1, first value is 0
            for i, e in enumerate(calday.events):
                if y in e.vlines and x in e.hlines:
                    self.ehl = i
            self.ui.draw_day()

###############################################################################
#       ask questions
###############################################################################

    def ask_generic(self, question, default=""):
        self.ui.clear_footer()
        self.ui.text_in_footer(question[:self.ui.width], '')
        data = Input(self.ui, default)
        r = data.get_input()
        while r == -1:
            self.ui.update()  # we got a KEY_RESIZE while getting input
            self.ui.clear_footer()
            self.ui.text_in_footer(question[:self.ui.width], '')
            data.screen_update()
            r = data.get_input()
        self.ui.clear_footer()
        if r == 0:
            return data
        else:  # cancel the question
            return "CUL_CANCEL"

    def ask_starttime(self):
        question = _("Enter start time ([hh:mm], [hhmm], [hh] or [h]):")
        start_time = None
        while start_time is None:
            data = self.ask_generic(question)
            if data != "CUL_CANCEL":
                start_time = data.check_hour(self.day, start=True)
            else:
                data = "CUL_CANCEL"
                start_time = 0
        return self.post_check_input(data, start_time)

    def ask_endtime(self, start_date):
        # ask endtime, return duration of event
        question = _("Enter end time ([hh:mm], [hhmm], [hh] or [h]) or duration ([+xx[m|h|d]):")
        end_date = None
        while end_date is None:
            data = self.ask_generic(question)
            if data != "CUL_CANCEL":
                end_date = data.check_duration(self.day, start_date)
            else:
                data = "CUL_CANCEL"
                end_date = 0
        return self.post_check_input(data, end_date)

    def ask_description(self, event=None):
        question = _("Enter description[@location]:")
        if event:
            data = self.ask_generic(question, event.summary)
        else:
            data = self.ask_generic(question)
        try:
            desc = data.text
        except Exception:
            return "CUL_CANCEL", ""  # empty place
        # is there a location in the description?
        if "@" in desc:
            place = desc[desc.find("@") + 1:]
            desc = desc[:desc.find("@")]
        else:
            place = ""
        return desc, place

    def ask_place(self, event):
        question = _("Enter location:")
        data = self.ask_generic(question, event.place)
        try:
            return data.text
        except Exception:
            return "CUL_CANCEL"

    def ask_day(self):
        question = _("Enter day ([yyyy/]mm/dd] or [yyyy]mmdd, [Enter for today]):")
        new_day = None
        while new_day is None:
            data = self.ask_generic(question)
            if data != "CUL_CANCEL":
                new_day = data.check_day(self.day)
            else:
                data = "CUL_CANCEL"
                new_day = 0
        return self.post_check_input(data, new_day)

    def ask_filename(self, mode, question):
        filename = None
        while filename is None:
            data = self.ask_generic(question)
            if data != "CUL_CANCEL":
                filename = data.check_filename(mode)
            else:
                data = "CUL_CANCEL"
                filename = 0
        return self.post_check_input(data, filename)

    def tag_event(self):
        if self.todohl > 0:
            return  # we're in the todolist, nothing to do
        self.ui.clear_footer()
        # select highlighted event if existing
        iday = self.day.isoweekday() - 1
        if len(self.calweek[iday].events) > self.ehl:
            event = self.calweek[iday].events[self.ehl].original
            # the footer will be useful, clear it
            self.ui.clear_footer()
            # ask question
            self.ui.text_in_footer(
                _("Enter tag number [0-7] or [a-z]:"),
                _("(Current tag: ") + str(event.tag) + ")",
            )
            prekey = self.ui.getkey()
            key = prekey[0]
            if key.isdigit() and 0 <= int(key) <= 7:  # local event
                event.tag = int(key)
                self.ui.clear_footer()
            elif key.isalpha():  # caldav event
                if key in self.culdav._tags:
                    idx = self.culdav._tags.index(key)
                    if self.culdav._iscaldav[idx]:  # caldav
                        caldav = self.culdav._icals[idx]
                        try:  # remove from local events
                            self.cal.del_event(event)
                        except Exception:  # it's a switch from another caldav
                            # not a local event; duplicate
                            e = Event(event.date, event.duration,
                                      event.summary, event.place,
                                      event.tag, event.url,
                                      event.caldav, event.colour)
                            event = e
                        # switch from local to caldav local culendars
                        event.tag = key
                        event.colour = self.culdav._list[idx]["colour"]
                        self.culdav._cal.add_event(event)
                        # properly add to the extern caldav
                        self.culdav.add_event(event, caldav)
                        # inform the switch
                        msg = _("Event moved to ")
                        url = caldav.url.url_raw
                        self.ui.inform(msg + url)
                    else:  # it's a webcal, read-only
                        msg = _("Error: can't add an event to a webcal")
                        self.ui.text_in_footer(msg, _("Press any key to continue"))
                        key = self.ui.getkey()
                    self.ui.clear_footer()
                else:
                    errmsg = _(" is not an exisiting calDAV tag")
                    self.ui.inform(key + errmsg)
            else:
                self.ui.clear_footer()
                self.ui.inform(_("Incorrect tag"))
            # redraw with new colour
            self.update_calweek(False)
            self.ui.draw_week()  # week for multidays events

    def copy_event(self, repetitions=1):
        if self.todohl > 0:
            return  # we're in the todolist, nothing to do
        iday = self.day.isoweekday() - 1
        if len(self.calweek[iday].events) > self.ehl:
            # only if an event is selected
            if repetitions > 1:
                question = _("Copy to next [d]ays, [w]eeks, [m]onths or [y]ears?")
            else:
                question = _("Copy to next [d]ay, [w]eek, [m]onth or [y]ear?")
            self.ui.inform(question)
            key = self.ui.getkey()
            if key not in ["d", "D", "w", "W", "m", "M", "y", "Y"]:
                errmsg = _("Invalid answer -- canceled")
                self.ui.inform(errmsg)
                return
            event = self.calweek[iday].events[self.ehl].original
            date = event.date
            duration = event.duration
            summary = event.summary
            place = event.place
            tag = event.tag
            colour = event.colour
            for ind in range(repetitions):
                if key in ["d", "D"]:
                    new_date = date + timedelta(days=ind + 1)
                if key in ["w", "W"]:
                    new_date = date + timedelta(weeks=ind + 1)
                elif key in ["m", "M"]:
                    years = (date.month + ind) // 12
                    month = date.month + ind + 1 - 12 * years
                    try:
                        new_date = date.replace(year=date.year + years, month=month)
                    except Exception:
                        new_date = None
                elif key in ["y", "Y"]:
                    new_date = date.replace(year=date.year + ind + 1)
                if new_date:
                    e = Event(new_date, duration, summary, place, tag, colour=colour)
                    # deal with tags
                    if type(tag) == int:  # local event
                        self.cal.add_event(e)
                        msg = _("Event copied")
                    elif tag in self.culdav._tags:  # caldav event
                        idx = self.culdav._tags.index(tag)
                        caldav = self.culdav._icals[idx]
                        if self.culdav._iscaldav[idx]:  # caldav
                            self.culdav._cal.add_event(e)
                            # properly add to the extern caldav
                            self.culdav.add_event(e, caldav)
                            msg = _("Caldav event remotely copied")
                        else:  # webcal
                            self.cal.add_event(e)
                            msg = _("Webcal event locally copied")
            self.cal.sort()
            if key in ["d", "D"]:
                self.ui.draw_week()  # cause the current week changed
            self.ui.inform(msg)
        # no else: do nothing without an selected event

    def shift_event(self, hours):
        if self.todohl > 0:
            return  # we're in the todolist, nothing to do
        # select highlighted event if existing
        iday = self.day.isoweekday() - 1
        if len(self.calweek[iday].events) > self.ehl:
            event = self.calweek[iday].events[self.ehl].original
            # we can't edit webcal events
            if event.caldav == "webcal":
                # webcals are read-only
                # msg = _("Error: can't change webcal event")
                return  # exit here
            sd = event.date + timedelta(hours=hours)
            event.date = sd
            if event.caldav:  # update the corresponding caldav
                self.culdav.del_event(event)
                self.culdav.add_event(event, event.caldav)
            # give focus to moved event
            self.day = sd.date()
            self.update_calweek(False)
            # search for the event of the new day to highlight the moved one
            iday = self.day.isoweekday() - 1
            for i, e in enumerate(self.calweek[iday].events):
                if e.summary == event.summary and e.place == event.place:
                    self.ehl = i
            self.ui.draw_week()

    def ask_todo(self, todo=None):
        question = _("Enter Todo[@date] ([yyyy/]mm/dd] or [yyyy]mmdd):")
        if todo:
            data = self.ask_generic(question, todo.summary)
        else:
            data = self.ask_generic(question)
        if data == "CUL_CANCEL":
            return "CUL_CANCEL"
        try:
            desc = data.text
            day = None
        except Exception:
            return "CUL_CANCEL", None  # None date
        if "@" in desc:  # is there a date?
            date = desc[desc.find("@") + 1:]
            item = desc[:desc.find("@")]
            data.text = date
            day = data.check_day(self.day)
        else:
            item = desc
        if not type(day) == date:
            day = None
        return item, day

    def post_check_input(self, data, processed_data):
        if data == "KEY_RESIZE" or processed_data == "KEY_RESIZE":
            self.ui.update()
            return "CUL_CANCEL"
        if data == "CUL_CANCEL" or processed_data == "CUL_CANCEL":
            self.ui.clear_footer()
            return "CUL_CANCEL"
        else:
            return processed_data

###############################################################################
# save/import/export
###############################################################################

    def save(self):
        self.cal.save_apts(self.conf, self.culdav)
        self.todo.save_todo(self.conf)

    def importcal(self):
        question = _("Enter the file name to import (ical or calcurse): (filename [tag])")
        filename = self.ask_filename("rb", question)
        tag = 0  # default value
        if filename == "CUL_CANCEL":
            return
        if filename[-2] == " " and filename[-1] in [str(i) for i in range(8)]:
            tag = int(filename[-1])
            filename = filename[:-2]
        try:  # is it an ical?
            cal = Agenda.import_ical(filename, self.conf.categories, tag)
        except Exception:
            try:  # is it from calcurse?
                cal = Agenda.import_calcurse(filename, tag)
            except Exception:
                self.ui.text_in_footer(_("Unable to load file"), _("Press any key to continue"))
                self.ui.getkey()
                self.ui.clear_footer()
                return
        # check for already present event
        # 1) create simple list from self.cal
        existingevents = []
        for se in self.cal.events:
            existingevents.append(se.date.strftime('%Y%m%d%H%M') + str(se.duration) + se.summary.replace(' ', ''))
        for e in cal.events:
            currentevent = (e.date.strftime('%Y%m%d%H%M') + str(e.duration) + e.summary.replace(' ', ''))
            if currentevent not in existingevents:
                self.cal.add_event(e)
        self.cal.sort()
        self.ui.draw_cal()
        self.ui.inform(_("New events imported!"))

    def exportcal(self):
        # returns 1 if successful
        self.ui.clear_footer()
        key = ""
        while key not in ["i", "I", "c", "C", "q", "Q", ""]:
            self.ui.text_in_footer(_("Export to [i]cal or to [c]alcurse?"), "[i/c]")
            key = self.ui.getkey()
            if key in ["q", "Q", ""]:
                self.ui.clear_footer()
                return
        question = _("Enter the file name to export:")
        filename = self.ask_filename("wb", question)
        if filename == "CUL_CANCEL":
            return
        if key in ["c", "C"]:
            self.cal.export_calcurse(filename)
        else:
            self.cal.export_ical(filename, self.conf.categories)
        self.ui.inform(_("Calendar exported!"))
