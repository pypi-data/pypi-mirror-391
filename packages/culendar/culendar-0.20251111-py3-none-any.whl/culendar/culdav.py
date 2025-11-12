from datetime import datetime
from os import path
from urllib import request

from caldav import DAVClient
from caldav.lib.error import DAVError
from icalendar import Calendar

from .calendar import Agenda
from .i18n import _


class Culdav:
    """Culendar CalDav"""
    def __init__(self, caldav_dict, datapath, ui):
        self._list = caldav_dict
        self._datapath = datapath
        self.ui = ui
        # list of Icalendar, for each caldav
        # proper url if webcal; None if offline
        self._icals = []
        self._iscaldav = []     # list of True/False
        self._tags = []         # associated tags
        self._cal = Agenda()    # single list of all events
        self._cals = []         # list of event lists, by caldav

    @property
    def icals(self):
        return self._icals

    @property
    def events(self):
        return self._cal.events

    def initialize(self):
        for cdav_idx, cdav in enumerate(self._list):
            self.initialize_single(cdav, cdav_idx)

    def initialize_single(self, cdav, cdav_idx):
        try:
            if "@" in cdav["url"]:  # there is a password in the url
                head_user_password, tail = cdav["url"].split("@")
                head, user_password = head_user_password.split("://")
                user = user_password.split(":")[0]
                url = head + "://" + user + ":" + "*****" + "@" + tail
            else:
                url = cdav["url"]
            msg = _("Loading caldav ") + str(cdav_idx + 1) + _(": ") + url
            self.ui.inform(msg)
            if cdav["url"][:4] == "http":  # caldav
                flag = True  # it's a proper caldav
                dav_client = self.get_client(cdav)
                self.add_calendar(dav_client)
            if cdav["url"][:6] == "webcal":  # webcal
                flag = False  # it's a webcal
                if cdav["url"][:7] == "webcals":  # webcal
                    urlh = "https" + cdav["url"][7:]
                else:
                    urlh = "http" + cdav["url"][6:]
                self.read_webcal_url(urlh)
                self._icals.append(urlh)
            self._iscaldav.append(flag)
        except (Exception, KeyboardInterrupt) as e:
            err = _("Error: can't contact caldav ") + cdav["url"]
            if self.load_local(cdav["url"], cdav["username"], check=True):
                err += _(" -- using offline copy")
            err += _(" -- press any key to continue")
            self.ui.inform(err, str(e))
            self.ui.getkey()
            # append None to keep same size as _list
            self._icals.append(None)
            self._iscaldav.append(False)
        self.add_tag(cdav)

    def get_client(self, cdav):
        if len(cdav["username"]) != 0:
            client = DAVClient(cdav["url"], username=cdav["username"], password=cdav["password"])
        else:
            client = DAVClient(cdav["url"])
        return client

    def add_calendar(self, dav_client):
        principal = dav_client.principal()
        calendars = principal.calendars()
        if len(calendars) == 0:  # useful for my poor test of python-radicale
            cal = principal.make_calendar()
        else:
            try:
                cal = dav_client.calendar(url=dav_client.url)
            except DAVError:
                raise
            try:
                cal.get_supported_components()  # ensure calendar exist
            except (KeyError, DAVError) as e:
                # get first calendar from principal
                cal = calendars[0]
                try:
                    cal.get_supported_components()  # ensure calendar exist
                except (KeyError, DAVError):
                    # nothing left to be done, re-raise first error
                    raise e
        self._icals.append(cal)

    def add_tag(self, cdav):
        if cdav:
            self._tags.append(cdav["tag"])
        else:
            self._tags.append(None)

    def read_webcal_url(self, url):
        if "@" not in url:  # no password
            return request.urlopen(url).read().decode()
        else:
            # keep between http[s] *://* user:pwd *@* url
            user_and_password = url.split("@")[0].split("://")[1]
            user = user_and_password.split(":")[0]
            # if there are ":" in the password, join them again
            password = ":".join(user_and_password.split(":")[1:])
            # remove login and password from url
            url_clean = "".join(url.split(user + ":" + password + "@"))
            # create a password manager and an opener
            pwd_mgr = request.HTTPPasswordMgrWithDefaultRealm()
            pwd_mgr.add_password(None, url_clean, user, password)
            handler = request.HTTPBasicAuthHandler(pwd_mgr)
            opener = request.build_opener(handler)
            # finally read and decode the data
            return opener.open(url_clean).read().decode()

    def sync(self):
        # extracts all the events of the the ICalendar
        # set all events in a single culendar/Agenda class
        self.ui.inform(_("Synchronising caldavs…"))
        # resets the differents cals
        self._cals = []
        for ind, cal in enumerate(self._icals):
            tmpcal = Agenda()
            if self._iscaldav[ind]:
                ical = cal.events()
                for e in ical:  # a list of ical events, each one in a calendar
                    agendacul = Agenda.from_calendar(Calendar.from_ical(e.data), [], self._tags[ind], cal)
                    ecul = agendacul.events[0]  # a single event
                    ecul.url = e.canonical_url
                    ecul.colour = self._list[ind]["colour"]
                    tmpcal.add_event(ecul)
            else:
                try:
                    # if unreachable, cal was None and thus, error
                    cal = self.read_webcal_url(cal)
                except Exception:
                    pass
                # reached and a webcal
                if cal and cal[:15] == "BEGIN:VCALENDAR":
                    # in a webcal, _icals is url
                    # in a webcal, we get everything.
                    agendacul = Agenda.from_calendar(Calendar.from_ical(cal), [], self._tags[ind], "webcal")
                    for e in agendacul.events:
                        e.colour = self._list[ind]["colour"]
                        tmpcal.add_event(e)
                else:  # unreachable, use offline copy if any
                    url = self._list[ind]["url"]
                    username = self._list[ind]["username"]
                    tmpcal = self.load_local(url, username)
                    if cal:  # we got something, but not a wecal
                        warn = _("Warning: contacting ")
                        if len(url) > 20:
                            warn += url[:20] + "[…]"
                        else:
                            warn += url
                        warn += _(" gave a ")
                        warn += cal[:23]
                        warn += _(" -- using offline copy")
                        warn += _(" -- press any key to continue")
                        self.ui.inform(warn)
                        self.ui.getkey()
            if tmpcal:  # avoid None from loading offline apts
                tmpcal.sort()  # sort for better offline text copy
                self._cals.append(tmpcal)
        self._cal = Agenda()
        for cal in self._cals:
            for e in cal.events:
                self._cal.add_event(e)
        self.save_local()

    def del_caldav(self, list_idx):
        # _list already removed in confscreen
        # clean what is required:
        # from highest position to lowest to pop easily
        list_idx.sort(reverse=True)
        for idx in list_idx:
            _ = self._tags.pop(idx)
            self._icals.pop(idx)
            self._iscaldav.pop(idx)

    def update(self, oldconf):
        list_idx = []
        for idx, conf in enumerate(oldconf):
            if conf not in self._list:
                list_idx.append(idx)
        if list_idx:
            self.del_caldav(list_idx)
        idx = 0
        for conf in self._list:
            if conf not in oldconf:
                self.initialize_single(conf, idx)
                idx += 1
        self.sync()

    def save_local(self):
        # Caldav local saves - no backup, it's online
        if not self._icals:
            return
        for cdav_idx, cdav in enumerate(self._list):
            if self._icals[cdav_idx]:  # is there anything to save
                url = cdav["url"]
                suffix = url.replace("/", "-") + cdav["username"]
                fname = "apts." + suffix
                with open(self._datapath+"/"+fname, "w") as f:
                    f.write(self._cals[cdav_idx].cal2txt(cdav["colour"]))

    def load_local(self, url, username, check=False):
        suffix = url.replace("/", "-") + username
        filename = self._datapath + "/" + "apts." + suffix
        if path.exists(filename):
            if check:  # just check existence
                return True
            else:
                return Agenda.load_apts(filename, caldav="webcal")
        else:  # no local copy exists
            return False if check else None

    def add_event(self, event, cdav):
        event.caldav = cdav
        cal = Calendar()
        icalevent = event.to_icalevent()
        # caldav reguires a UID
        icalevent.add("uid", hash(datetime.now()))
        cal.add_component(icalevent)
        # https://caldav.readthedocs.io/en/latest/caldav/objects.html#caldav.objects.Calendar.add_event
        tmpevent = cdav.add_event(cal.to_ical().decode())
        event.url = tmpevent.canonical_url

    def del_event(self, event):
        # https://caldav.readthedocs.io/en/latest/caldav/objects.html#caldav.objects.Calendar.event_by_url
        event.caldav.event_by_url(event.url).delete()
        # delete from local cal in order to avoid syncing caldav to update events
        self._cal.del_event(event.original)
