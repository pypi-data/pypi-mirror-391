from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
from os import (
    path,
    rename,
)

from icalendar import Calendar
from icalendar import Event as IEvent


class Event:
    """
    Event class
    """

    def __init__(self, date, duration, summary, place="", tag=0,
                 url=None, caldav=None, colour=None):
        self._date = date                 # datetime.datetime()
        self._duration = int(duration)    # seconds
        self._summary = summary.strip()   # text
        self._place = place.strip()       # text
        self._tag = tag
        self._colour = colour  # default colour is tag; useful for caldav
        self._samehour = 0     # number of simultaneous events
        self._hlines = None    # horizontal lines of event
        self._vlines = None    # vertical lines of event
        # CalDAV
        self._url = url
        self._caldav = caldav

    @property
    def original(self) -> 'Event':
        return self

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, d):
        self._date = d

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, d):
        self._duration = d

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, s):
        self._summary = s

    @property
    def place(self):
        return self._place

    @place.setter
    def place(self, p):
        self._place = p

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, t):
        self._tag = t

    @property
    def samehour(self):
        return self._samehour

    @samehour.setter
    def samehour(self, samehour):
        self._samehour = samehour

    @property
    def hlines(self):
        return self._hlines

    @hlines.setter
    def hlines(self, hlines):
        self._hlines = hlines

    @property
    def vlines(self):
        return self._vlines

    @vlines.setter
    def vlines(self, vlines):
        self._vlines = vlines

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def caldav(self):
        return self._caldav

    @caldav.setter
    def caldav(self, caldav):
        self._caldav = caldav

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, colour):
        self._colour = colour

    def compute_vlines(self, ui):
        start_hour = self.date.hour
        start_min = self.date.minute
        early_start = 0
        late_end = 0
        end_time = start_hour * 3600 + start_min * 60 + self.duration
        # if starting hour doesn't fit, make it fit
        if start_hour < ui.hmin:
            start_hour = ui.hmin
            start_min = 0
            early_start = 1
        if end_time < start_hour * 3600:
            end_time = start_hour * 3600
        if end_time/3600 > ui.hmax:
            late_end = 1
        if start_hour >= ui.hmax:
            start_hour = ui.hmax
            start_min = 0
            late_end = 0  # already late
        # don't overflow
        end_time = min(ui.hmax * 3600, end_time)
        end_hour = int(end_time // 3600)
        end_min = int((end_time - end_hour * 3600) // 60)
        # time to lines
        # select the lines
        startline = start_hour - ui.hmin
        endline = end_hour - ui.hmin
        shline = ui.lines[1][startline] + 1  # 1st line after hour line
        ehline = ui.lines[1][endline] + 1    # same as start hour
        # lines to range of line
        if ui.hour_size == 1:
            # small terminals: starts on line event
            shline = shline - 1
            ehline = ehline - 1
        else:  # tall terminal, work between lines, deal with minutes
            minute_size = round(60 / (ui.hour_size - 1))
            if ui.hour_size > 2:
                # change start line only for wide hours
                shline += start_min // minute_size
            if end_min == 0:
                ehline -= 1  # stops before hour line
            else:
                ehline += end_min // minute_size
            # special case out of schedule
            if start_hour == ui.hmax:
                shline -= 1
        # overlaps the table when outside the limits
        shline -= early_start
        # failproof: never overlaps on dayname
        shline = max(shline, 3)
        # failproof: always a line
        if ehline <= shline:
            ehline = shline + 1
        ehline += late_end
        # finally define the range
        self.vlines = range(shline, ehline)

    def compute_hlines(self, ui, col, width, maxevents, table):
        start_vline = table[self.vlines[0]]
        e_width = width // maxevents
        left = 0
        while sum(start_vline[left:left + e_width]) != 0:
            left += 1  # width//maxevents
            # have we gone too far?
            if left + e_width > len(start_vline):
                # reduce event width
                e_width = len(start_vline) - left
        # first column picked from lines
        for v in self.vlines:
            for i in range(e_width):
                table[v][left+i] = 1
        # first column: right of vertical day line + offset of multievent
        first_col = ui.lines[0][col] + 1 + left
        # finally define the range
        self.hlines = range(first_col, first_col + e_width)
        # too many events or too small terminal
        if len(self.hlines) < 1:
            self.hlines = (ui.lines[0][col] + 1, width)

    def to_icalevent(self, categories=None):
        ie = IEvent()
        ie.add('dtstart', self.date)
        ie.add('duration', timedelta(seconds=self.duration))
        ie.add('summary', self.summary)
        if self.place:
            ie.add('location', self.place)
        if self.tag and type(self.tag) == int:
            if len(categories[self.tag]) > 1:
                ie.add('category', categories[self.tag][1])
            else:
                ie.add('category', self.tag)
        if self.url:
            ie.add('url', self.url)
        return ie

    def split_event(self):
        diffdayfirst = self.date.toordinal()
        last_day = self.date + timedelta(seconds=self.duration)
        diffdaylast = last_day.toordinal()
        if diffdayfirst == diffdaylast:
            return [self]
        else:
            # first subevent
            end_date = self.date.replace(hour=23, minute=59)
            e1 = SubEvent(self, self.date, (end_date-self.date).total_seconds())
            subevents = [e1]
            day_span = diffdaylast-diffdayfirst
            for i in range(1, day_span+1):
                if i != day_span:  # not last event
                    new_day = self.date.replace(hour=0, minute=0) + timedelta(days=i)
                    subevents.append(SubEvent(self, new_day, 86340))  # 23h59 in seconds
                else:
                    new_day = self.date.replace(hour=0, minute=0) + timedelta(days=i)
                    duration = (last_day.hour*60 + last_day.minute)*60
                    if duration > 0:  # avoids event finishing at midnight to spread
                       subevents.append(SubEvent(self, new_day, duration))
        return subevents


class SubEvent(Event):
    def __init__(self, event: Event, date, duration):
        self._orig_event = event
        super().__init__(
            date,
            duration,
            summary=event.summary,
            place=event.place,
            tag=event.tag,
            url=event.url,
            caldav=event.caldav,
            colour=event.colour,
        )

    @property
    def original(self) -> 'Event':
        return self._orig_event

class Agenda:
    """
    Agenda class
    """
    def __init__(self):
        self._events = []

    def add_event(self, e):
        self._events.append(e)

    def del_event(self, e):
        self._events.remove(e.original)

    @property
    def events(self):
        return self._events

    def sort(self):
        """sort by date and time."""
        maxdate = date(9999, 12, 31)
        self._events = sorted(self._events, key=lambda e: e.date if e.date else maxdate)

    @classmethod
    def from_calendar(cls, calendar, categories, default_tag, caldav=None):
        agenda = cls()
        for ie in calendar.walk('vevent'):
            sdate = ie['dtstart'].dt
            try:  # is there an end date?
                edate = ie['dtend'].dt
                # if so, compute duration
                dur = (edate - sdate).total_seconds()
            except KeyError:
                try:  # there is thus a duration
                    dur = ie['duration'].dt.total_seconds()
                except KeyError:  # no end date, no duration… Are you kidding me?
                    dur = 0  # it exists, that's all
            try:  # is there a summary?
                summ = ie['summary'].lstrip().replace('\n', "-")
            except KeyError:  # if none, NULL summary
                summ = " "
            try:  # is there a location?
                place = ie['location'].lstrip().replace('\n', "-")
            except KeyError:  # if none, NULL summary
                place = ""
            try:  # is there a category?
                cat = ie['category']
                tag = default_tag
                if type(cat) == list:  # several categories in a single event
                    for c in cat:
                        for t in range(1, 8):
                            if c.lstrip() in categories[t]:
                                # if category exists, tag it
                                tag = t
                else:  # single category
                    for t in range(1, 8):
                        if cat.lstrip() in categories[t]:
                            # if category exists, tag it
                            tag = t
            except KeyError:  # no category
                tag = default_tag
            # special case for events without hour:
            # set 1st hour to 0:00 and duration to 24h
            if type(sdate) == date:
                sdate = datetime.combine(sdate, time(0))
                dur = 24 * 60 * 60
            # check the potential timezone and put to local
            if sdate.tzinfo:
                sdate = sdate.astimezone()
                sdate = sdate.replace(tzinfo=None)
            if caldav:
                e = Event(sdate, dur, summ, place, tag, caldav=caldav)
            else:
                e = Event(sdate, dur, summ, place, tag)
            agenda.add_event(e)
        return agenda

    @classmethod
    def extract_week(cls, cal, culdav, day, ui, autosync=True):
        # create a list of subcals for each day of the week
        calweek = []
        for i in range(7):
            calweek.append(cls())
        # selects the events in caldavs, if required
        if autosync:
            culdav.sync()
        # first day of the current week; +1 for starting on monday in ordinal
        firstday = day.toordinal() - day.isoweekday() + 1
        for e in cal.events + culdav.events:
            diffdayfirst = e.date.toordinal() - firstday
            diffdaylast = (e.date + timedelta(seconds=e.duration)).toordinal() - firstday
            dayspan = set(range(diffdayfirst, diffdaylast+1))
            # if in the right week, we have
            #if 0 <= diffday <= 6:
            if dayspan.intersection(set(range(7))):  # if the event days interect the week
                if diffdayfirst == diffdaylast:
                    calweek[diffdayfirst].add_event(e)
                else:
                    for sub_e in e.split_event():
                        diffday = sub_e.date.toordinal() - firstday
                        if 0 <= diffday <= 6:
                            calweek[diffday].add_event(sub_e)
        for iday in range(ui.daynb):  # for all printed days
            calweek[iday].sort()
            for e in calweek[iday].events:
                # compute each vertical position for events
                e.compute_vlines(ui)
            # initialize no event on all lines
            nbevent = [0 for h in range(ui.ymax)]
            for e in calweek[iday].events:
                for i in e.vlines:
                    nbevent[i] += 1
            maxevent = max(nbevent)
            # if last idayumn, the day size is not ui.day_size
            if iday == ui.daynb - 1:
                width = ui.lines[0][-1] - ui.lines[0][-2] - 1
            else:
                width = ui.day_size - 1
            # day_size - 1: doesn't include vertical separating lines
            # table of position of events on day
            table = [[0 for d in range(width)] for y in range(ui.ymax)]
            for e in calweek[iday].events:
                maxevent = max([nbevent[i] for i in e.vlines])
                e.compute_hlines(ui, iday, width, maxevent, table)
        return calweek

    @classmethod
    def import_ical(cls, filename, categories, default_tag=0):
        with open(filename, "r") as f:
            calendar = Calendar.from_ical(f.read())
        return cls.from_calendar(calendar, categories, default_tag)

    @classmethod
    def import_calcurse(cls, filename, t=0):
        cal = cls()
        with open(filename) as f:
            for line in f:
                smon = int(line[0:2])
                sday = int(line[3:5])
                syea = int(line[6:10])
                shou = int(line[13:15])
                smin = int(line[16:18])
                emon = int(line[22:24])
                eday = int(line[25:27])
                eyea = int(line[28:32])
                ehou = int(line[35:37])
                emin = int(line[38:40])
                summ = line[42:-1]  # strips final \n
                sdate = datetime(syea, smon, sday, shou, smin)
                edate = datetime(eyea, emon, eday, ehou, emin)
                e = Event(sdate, (edate-sdate).total_seconds(), summ, tag=t)
                cal.add_event(e)
        return cal

    def export_ical(self, filename, categories):
        ical = Calendar()
        ical.add('prodid', '-//From Culendar')
        ical.add('version', '2.0')
        for e in self.events:
            ie = e.to_icalevent(categories)
            ical.add_component(ie)
        with open(filename, "wb") as f:
            f.write(ical.to_ical())

    def export_calcurse(self, filename):
        lines = ""
        for e in self.events:
            line = str(e.date.strftime('%m/%d/%Y @ %H:%M'))
            line += " -> "
            enddate = e.date + timedelta(seconds=e.duration)
            line += str(enddate.strftime('%m/%d/%Y @ %H:%M'))
            line += " |"
            line += e.summary
            if e.place:
                line += "@"
                line += e.place
            line += "\n"
            lines += line
        with open(filename, "w") as f:
            f.write(lines)

    @classmethod
    def load(cls, filename, todofilename):
        return cls.load_apts(filename), cls.load_todo(todofilename)

    @classmethod
    def load_apts(cls, filename, caldav=None):
        cal = cls()
        with open(filename) as f:
            for line in f:
                syea = int(line[0:4])
                smon = int(line[5:7])
                sday = int(line[8:10])
                shou = int(line[13:15])
                smin = int(line[16:18])
                eyea = int(line[22:26])
                emon = int(line[27:29])
                eday = int(line[30:32])
                ehou = int(line[35:37])
                emin = int(line[38:40])
                rema = line[42:-1]  # strips final \n
                # search for a tag
                try:
                    if "|" in rema:
                        tag = int(rema[rema.find("|") + 1:])
                        rema = rema[:rema.find("|")]
                    else:
                        tag = 0
                except ValueError:
                    tag = 0
                # search for a location delimiter
                if "@" in rema:
                    summ = rema[:rema.find("@")]
                    place = rema[rema.find("@") + 1:]
                else:
                    summ = rema
                    place = ""
                sdate = datetime(syea, smon, sday, shou, smin)
                edate = datetime(eyea, emon, eday, ehou, emin)
                e = Event(sdate, (edate-sdate).total_seconds(), summ, place, tag, caldav=caldav)
                cal.add_event(e)
        cal.sort()
        return cal

    @classmethod
    def load_todo(cls, todofilename):
        # Todo list: ugly hack, use Agenda
        # Todo item: Event with no duration and optional date
        todo = cls()
        with open(todofilename) as f:
            for line in f:
                try:  # if there is a date
                    syea = int(line[0:4])
                    smon = int(line[5:7])
                    sday = int(line[8:10])
                    sdate = date(syea, smon, sday)
                    rema = line[14:-1]  # strips final \n
                except ValueError:
                    rema = line[:-1]  # strips final \n
                    sdate = None
                try:
                    # if no |, empty tag and rema doesn't change
                    tag = int(rema[rema.find("|") + 1:])
                    summ = rema[:rema.find("|")]
                except ValueError:
                    tag = 0
                    summ = rema
                e = Event(sdate, None, summary=summ, tag=tag)
                todo.add_event(e)
        todo.sort()
        return todo

    def cal2txt(self, colour=None):
        lines = ""
        for e in self.events:
            line = str(e.date.strftime('%Y/%m/%d @ %H:%M'))
            line += " -> "
            enddate = e.date + timedelta(seconds=e.duration)
            line += str(enddate.strftime('%Y/%m/%d @ %H:%M'))
            line += " |"
            line += e.summary
            if e.place:
                line += "@"
                line += e.place
            if colour:
                line += "|"
                line += str(colour)
            elif e.tag:
                line += "|"
                line += str(e.tag)
            line += "\n"
            lines += line
        return lines

    def todo2txt(self):
        lines = ""
        for e in self.events:
            if e.date:
                line = str(e.date.strftime('%Y/%m/%d'))
                line += " -> "
            else:
                line = ""
            line += e.summary
            if e.tag:
                line += "|"
                line += str(e.tag)
            line += "\n"
            lines += line
        return lines

    def save_apts(self, conf, culdav=None):
        # main Agenda
        # backup current one
        if path.exists(conf.datafile):
            rename(conf.datafile, conf.datafile + '.old')
        with open(conf.datafile, "w") as f:
            f.write(self.cal2txt())
        if culdav:
            culdav.save_local()

    def save_todo(self, conf):
        # Todo file
        # backup current one
        if path.exists(conf.todofile):
            rename(conf.todofile, conf.todofile + '.old')
        with open(conf.todofile, "w") as f:
            f.write(self.todo2txt())
