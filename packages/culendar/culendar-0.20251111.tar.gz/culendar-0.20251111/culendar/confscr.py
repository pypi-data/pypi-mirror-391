import curses
from collections import OrderedDict

from .i18n import _
from .inputs import Input


class Conf:
    def __init__(self, ui, conf, caldav):
        self.ui = ui
        self._screen = ui.screen
        self._caldav = caldav
        self._y, self._x = self._screen.getmaxyx()
        self._top = 0  # offset between screen and pad
        self._conf = conf
        self._general = OrderedDict()
        self._general["hmin"] = conf.hmin
        self._general["hmax"] = conf.hmax
        self._general["WE"] = conf.WE
        self._general["TODO"] = conf.todo  # noqa: T101
        self._general["autosave"] = conf.autosave
        self._general["colourset"] = conf.colourset
        self._general["autosync"] = conf.autosync
        self._general["mouse"] = conf.mouse
        self._tab = 0
        self._tabs = [
            self._general,
            self._conf.keys,
            self._conf.categories,
            self._conf.caldav,
        ]
        self._item = 0
        self._tabsnames = [
            _("General configuration"),
            _("Keybinding"),
            _("Categories"),
            _("CalDAV"),
        ]
        # to be independant from config.set_colours
        curses.init_pair(42, curses.COLOR_RED, -1)
        curses.init_pair(43, curses.COLOR_GREEN, -1)

########################################################################
# drawing functions
########################################################################

    def draw_conf_screen(self):
        self._screen.clear()
        self._y, self._x = self._screen.getmaxyx()
        # if ridiculously small terminal
        if self._x < 25 or self._y < 6:
            self._screen.clear()
            text = _(r"\_x< A dead duck. That's all such a small terminal deserves.")
            self._screen.addstr(0, 0, text[0:(self._x - 1) * (self._y - 1)])
            key = ""
            while key not in self._conf.keys["quit"] and key != "KEY_RESIZE":
                key = self.ui.getkey()
            if key in self._conf.keys["quit"]:
                exit()
            else:
                self.draw_conf_screen()
        # draw screen
        headleft = _("q: quit configuration")
        headcenter = _("Culendar configuration screen")
        self._screen.border()
        self._screen.hline(2, 1, curses.ACS_HLINE, self._x - 2)
        self._screen.addch(2, 0, curses.ACS_LTEE)
        self._screen.addch(2, self._x - 1, curses.ACS_RTEE)
        self._screen.addstr(1, 1, headleft, curses.A_BOLD)
        self._screen.addstr(1, (self._x - len(headcenter)) // 2 + 1, headcenter, curses.A_BOLD)
        # should be factorized with helpscr.py lines 83+
        # create full pad in case of terminal smaller than needed
        # counting lines for each tab, take max + 2 lines for tabnames
        self._padlines = 2 + max(len(d) for d in self._tabs)
        # pad columns: very hard to set a limit, one could add as many
        # keybinding as he wants… Set to 10×sizeX, to have lots of room
        # even for 80col terminals
        self._padcols = 10 * self._x
        self._pad = curses.newpad(self._padlines, self._padcols)
        self._pad.scrollok(True)
        self._screen.refresh()  # if not present, pad is ignored
        # the lines available for the pad
        self._padavail = self._y - 4
        # to have the bottom of the pad on the bottom of the screen
        self._maxtop = max(0, self._padlines - self._padavail)
        self.draw_tabs()

    def draw_tabs(self):
        # draw tabs
        colsize = round((self._x - 2) / len(self._tabs))
        self._pad.hline(1, 0, curses.ACS_HLINE, self._x - 1)
        for it, tname in enumerate(self._tabsnames):
            if it > 0:  # add previous separator
                self._pad.addch(0, it * colsize, curses.ACS_VLINE)
                self._pad.addch(1, it * colsize, curses.ACS_BTEE)
            if it == self._tab:
                OPT = curses.A_BOLD
            else:
                OPT = curses.A_NORMAL
            tabname = tname[0:colsize]  # to be sure to fit
            start = round((it + 1 / 2) * colsize - len(tabname) / 2)
            self._pad.addstr(0, start, tabname, OPT)
        if self._tab < 3:
            self.draw_dictionary()
        elif tname == "CalDAV":
            self.draw_caldav()
        self.draw_help()
        self._pad.refresh(self._top, 0, 3, 1, self._y - 2, self._x - 2)

    def draw_dictionary(self):
        if self._tab != 0:  # General is already an OrderDict
            stuff = sorted(self._tabs[self._tab].keys())
        else:
            stuff = self._tabs[self._tab].keys()
        for ik, k in enumerate(stuff):
            # key k is integer for some dict, gets str(.) when useful
            if ik == self._item:
                OPT = curses.A_BOLD
                # save the key to use it in edit_item()
                self._editing_key = k
            else:
                OPT = curses.A_NORMAL
            # if k is integer, it's the category number, rename it
            if type(k) == int:
                # add the associated color
                COL_OPT = self._conf.colours[k] + curses.A_REVERSE+OPT
                printme = _("Category ") + str(k)
                self._pad.addstr(2 + ik, 2, printme, COL_OPT)
                offset = len(printme)
            else:
                self._pad.addstr(2 + ik, 2, k, OPT)
                offset = len(k)
            if self._editing_key == k:
                # remember this offset for deleting item
                self._offset = offset
            self._pad.addstr(2 + ik, 2 + offset, " = ", OPT)
            if type(self._tabs[self._tab][k]) == bool:
                if self._tabs[self._tab][k]:
                    self._pad.addstr(2 + ik, 2 + offset + 3, _("On"), OPT + curses.color_pair(43))
                else:
                    self._pad.addstr(2 + ik, 2 + offset + 3, _("Off"), OPT + curses.color_pair(42))
            elif self._tab != 0:  # editing keys or categories
                listkeys = ""
                for ck in self._tabs[self._tab][k]:
                    # special case: keys (cf helpscr.py)
                    if ck == "\t":
                        listkeys += "TAB, "
                    elif ck == " ":
                        listkeys += "SPACE, "
                    else:
                        listkeys += ck + ", "
                listkeys = listkeys[:-2]  # erase final comma
                self._pad.addstr(2 + ik, 2 + offset + 3, listkeys, OPT)
            else:
                self._pad.addstr(2 + ik, 2 + offset + 3, str(self._tabs[self._tab][k]), OPT)
            if k == "colourset":  # special case, add an example of colourset
                example = _("Example")
                width = len(example) + 6
                colour = curses.A_REVERSE + curses.color_pair(42) + OPT
                normal = curses.A_REVERSE + OPT
                if self._tabs[self._tab][k] == 0:
                    self._pad.hline(2 + ik, 2 + offset + 3 + 3, " ", width, colour)
                    self._pad.addstr(2 + ik, 2 + offset + 3 + 6, example, colour)
                elif self._tabs[self._tab][k] == 1:
                    self._pad.addstr(2 + ik, 2 + offset + 3 + 3, " ", colour)
                    self._pad.addstr(2 + ik, 2 + offset + 3 + 3 + width - 1, " ", colour)
                    self._pad.hline(2 + ik, 2 + offset + 3 + 3 + 1, " ", width - 2, normal)
                    self._pad.addstr(2 + ik, 2 + offset + 3 + 6, example, normal)
                elif self._tabs[self._tab][k] == 2:
                    self._pad.hline(2 + ik, 2 + offset + 3 + 3, " ", width, normal)
                    self._pad.addstr(2 + ik, 2 + offset + 3 + 6, example, colour)
                else:
                    self._pad.hline(2 + ik, 2 + offset + 3 + 3, " ", width, normal)
                    self._pad.addstr(2 + ik, 2 + offset + 3 + 6, example, normal)

    def draw_caldav(self):
        tagcol = _("T")
        urlcol = _("URL")
        usernamecol = _("Username")
        passwordcol = _("Password")
        maxurl = len(urlcol)
        maxusr = len(usernamecol)
        for ik, cd in enumerate(self._conf.caldav):
            maxurl = max(maxurl, len(cd["url"]))
            maxusr = max(maxusr, len(cd["username"]))
        reflen = min(maxurl + maxusr + 9, self._x - 3)
        # y-position of the columns
        maxlen = self._x - 3
        xtag = 2
        xurl = xtag + 2
        if maxurl + maxusr + 11 > maxlen:
            # +11: to have place for colour and at least 4 first pwd characters
            # 4 for a minimal characters in pwd, 3 for space, split the rest
            halflen = (maxlen - xurl - 4 - 3) // 2
            # check if url or usr is smaller than this half length and optim
            if maxurl < halflen:
                maxusr = min(maxusr, maxlen - xurl - 7 - maxurl)
            elif maxusr < halflen:
                maxurl = min(maxurl, maxlen - xurl - 7 - maxusr)
            else:
                maxurl = maxusr = halflen
        xusr = xurl + 2 + maxurl
        xpwd = xusr + 2 + maxusr
        # print columns title
        self._pad.addstr(2, xtag, tagcol, curses.A_BOLD)
        self._pad.addstr(2, xurl, urlcol[:maxurl], curses.A_BOLD)
        self._pad.addstr(2, xusr, usernamecol[:maxusr], curses.A_BOLD)
        self._pad.addstr(2, xpwd, passwordcol, curses.A_BOLD)
        for ik, cd in enumerate(self._conf.caldav):
            if ik == self._item:
                OPT = curses.A_BOLD
                # save the key to use it in edit_item()
                self._editing_key = ik
            else:
                OPT = curses.A_NORMAL
            COL_OPT = self._conf.colours[cd["colour"]] + curses.A_REVERSE + OPT
            self._pad.addstr(4 + ik, xtag, cd["tag"], COL_OPT)
            if "@" in cd["url"]:  # there is a password to hide in a webcal
                head_user_password, tail = cd["url"].split("@")
                head, user_password = head_user_password.split("://")
                user = user_password.split(":")[0]
                # if there are ":" in the password, join them again
                password = ":".join(user_password.split(":")[1:])
                url = head + "://" + user + ":" + "*****" + "@" + tail
            else:
                url = cd["url"]
            self._pad.addstr(4+ik, xurl, url[:maxurl], OPT)
            if cd["url"][:4] == "http":
                self._pad.addstr(4 + ik, xusr, cd["username"][:maxusr], OPT)
                self._pad.addstr(4 + ik, xpwd, "*" * len(cd["password"]), OPT)

    def draw_help(self):
        self.oneline_footer()
        if self._tab == 0:  # general
            helpmsg = _("Enter/Space: edit value")
        elif self._tab == 1:  # keys
            helpmsg = _("a: add key    d: delete key")
        elif self._tab == 2:  # categories
            helpmsg = _("a: add name   d: delete name")
            helpmsg += _("    Enter/Space: change colour")
        elif self._tab == 3:  # caldav
            helpmsg = _("a: add caldav    d: delete caldav")
            helpmsg += _("    t: change tag    c: change colour")
            helpmsg += _("    u: edit url    n: edit username")
            helpmsg += _("    p: edit password")
        self._screen.addstr(self._y - 1, 0, helpmsg[:self._x - 1])

    def clear_tabs(self):
        self._pad.hline(0, 1, " ", self._padcols)
        self._pad.clrtobot()

    def redraw_tabs(self):
        self.clear_tabs()
        self.draw_tabs()

    def oneline_footer(self):
        self._screen.addch(self._y - 4, self._x - 1, curses.ACS_VLINE)
        self._screen.clrtobot()
        self._screen.addch(self._y - 3, 0, curses.ACS_VLINE)
        self._screen.addch(self._y - 3, self._x - 1, curses.ACS_VLINE)
        self._screen.hline(self._y - 2, 1, curses.ACS_HLINE, self._x - 2)
        self._screen.addch(self._y - 2, 0, curses.ACS_LLCORNER)
        self._screen.addch(self._y - 2, self._x - 1, curses.ACS_LRCORNER)

    def question_footer(self):
        self._screen.hline(self._y - 3, 1, curses.ACS_HLINE, self._x - 2)
        self._screen.addch(self._y - 3, 0, curses.ACS_LLCORNER)
        self._screen.addch(self._y - 3, self._x - 1, curses.ACS_LRCORNER)
        self._screen.clrtobot()

    def no_footer(self):
        self._screen.addch(self._y - 4, self._x - 1, " ")
        self._screen.clrtobot()
        self._screen.box()
        self._screen.refresh()

########################################################################
# editing functions
########################################################################

    def edit_item(self):
        if self._tab == 0:  # general
            if type(self._tabs[self._tab][self._editing_key]) == bool:
                self.edit_bool()
            elif self._editing_key == "colourset":
                # very specific case, toggle in different coloursets
                self.edit_colourset()
            elif type(self._tabs[self._tab][self._editing_key]) == int:
                self.edit_int_hour()
        elif self._tab == 2:  # change category colour
            self.edit_change_colour()

    def edit_bool(self):
        self._tabs[self._tab][self._editing_key] = not self._tabs[self._tab][self._editing_key]

    def edit_colourset(self):
        # 3 coloursets avalaible
        self._tabs[self._tab][self._editing_key] = (self._tabs[self._tab][self._editing_key] + 1) % 3

    def edit_generic(self, question, default="", pwd=False):
        self.question_footer()
        self._screen.addstr(self._y - 2, 0, question[:self._x])
        data = Input(self.ui, default, pwd)
        r = data.get_input()
        while r == -1:
            self.draw_conf_screen()  # we got a KEY_RESIZE while getting input
            self.question_footer()
            self._screen.addstr(self._y - 2, 0, question[:self._x])
            data.screen_update()
            r = data.get_input()
        if r == 0:
            return data
        else:  # cancel the question
            return "CUL_CANCEL"

    def edit_int_hour(self):
        question = _("Enter new value [hh] or [h]:")
        new_int = None
        while new_int is None:
            data = self.edit_generic(question)
            if data == "CUL_CANCEL":
                return
            new_int = data.check_inthour()
            if self.post_edit(new_int) == "CUL_CANCEL":
                return
        self._tabs[self._tab][self._editing_key] = new_int

    def edit_delete(self):
        if self._tab == 3:
            # pop the current caldav out of the list if any
            if len(self._tabs[self._tab]) != 0:
                self._tabs[self._tab].pop(self._editing_key)
            if self._editing_key == len(self._tabs[self._tab]):
                # last position
                self._item = len(self._tabs[self._tab]) - 1
        else:
            self.edit_delete_item()  # choose an item to delete

    def edit_delete_item(self):
        if len(self._tabs[self._tab][self._editing_key]) == 0:
            return
        elif len(self._tabs[self._tab][self._editing_key]) == 1:
            self._tabs[self._tab][self._editing_key].pop()
        else:
            self._item_idx = 0
            self.oneline_footer()
            helpmsg = _("Select item to delete, press Enter")
            self._screen.addstr(self._y - 1, 0, helpmsg[:self._x - 1])
            self.edit_delete_item_draw()
            key = self.ui.getkey()
            while key not in (["q", ""] + self._conf.keys["quit"]):
                if key == "KEY_RESIZE":
                    self.draw_conf_screen()
                    return
                elif key in (["\t", "KEY_RIGHT"] + self._conf.keys["nextday"]):
                    self._item_idx += 1
                    if self._item_idx > len(self._tabs[self._tab][self._editing_key]) - 1:
                        self._item_idx = 0
                elif key in (["KEY_BTAB", "KEY_LEFT"] + self._conf.keys["prevday"]):
                    self._item_idx -= 1
                    if self._item_idx < 0:
                        self._item_idx = len(self._tabs[self._tab][self._editing_key]) - 1
                elif key in ["d", "D", "\n"]:
                    self._tabs[self._tab][self._editing_key].pop(self._item_idx)
                    return
                self.edit_delete_item_draw()
                key = self.ui.getkey()

    def edit_delete_item_draw(self):
        # positioning the cursor just after the = sign
        self._pad.addstr(2 + self._item - self._top, 2 + self._offset + 2, " ")
        for i, item in enumerate(self._tabs[self._tab][self._editing_key]):
            if item == "\t":
                item = "TAB"
            elif item == " ":
                item = "SPACE"
            if i == self._item_idx:
                self._pad.addstr(item, curses.A_BOLD)
            else:
                self._pad.addstr(item)
            if i < len(self._tabs[self._tab][self._editing_key]) - 1:
                self._pad.addstr(", ")
        # may crash if very long categories / keys
        self._pad.refresh(self._top, 0, 3, 1, self._y - 2, self._x - 2)

    def edit_add_item(self):
        if self._tab == 1:
            self.edit_add_key()
        elif self._tab == 2:
            self.edit_add_category()
        elif self._tab == 3:
            self.edit_add_caldav()

    def edit_add_key(self):
        self.oneline_footer()
        question = _("Press the key to add (Escape to cancel)")
        self._screen.addstr(self._y - 1, 0, question[:self._x - 1])
        key = self.ui.getkey()
        if key == "KEY_RESIZE":
            self.draw_conf_screen()
        elif key != "":
            if key not in self._tabs[self._tab][self._editing_key]:
                # nothing to add, already here
                self._tabs[self._tab][self._editing_key].append(key)
            # check if added key is present elsewhere
            for k in self._tabs[self._tab].keys():
                # we don't care about the current edited key
                if k != self._editing_key:
                    if key in self._tabs[self._tab][k]:
                        # the new key was already in use: remove it
                        self._tabs[self._tab][k].pop(self._tabs[self._tab][k].index(key))
                        self.question_footer()
                        warning = (
                            _('Warning: key "')
                            + str(key)
                            + _('" was used for function "')
                            + str(k) + _('"'),
                        )
                        wait = _("Press any key to continue")
                        self._screen.addstr(self._y - 2, 0, warning[:self._x - 1])
                        self._screen.addstr(self._y - 1, 0, wait[:self._x - 1])
                        # pause; resize if necessary
                        if self.ui.getkey() == "KEY_RESIZE":
                            self.draw_conf_screen()

    def edit_add_category(self):
        question = _("Enter new category name:")
        new_cat = None
        while new_cat is None:
            data = self.edit_generic(question)
            if data == "CUL_CANCEL":
                return
            else:
                new_cat = data.text
        self._tabs[self._tab][self._editing_key].append(new_cat)

    def edit_add_caldav(self):
        new_url = self.enter_url()
        if not new_url:
            return
        question = _("Enter tag [a-z]:")
        self.question_footer()
        self._screen.addstr(self._y - 2, 0, question[:self._x])
        new_tag = self.ui.getkey()
        if not new_tag.isalpha():
            self.draw_conf_screen()  # if it is KEY_RESIZE, to be sure
            return
        new_colour = 0  # default colour
        if new_url[:4] == "http":  # caldav: require user/pwd
            new_user = self.enter_username()
            if not new_user:
                return
            new_pwd = self.enter_password()
            if not new_pwd:
                return
        else:
            new_user = ""
            new_pwd = ""
        # create the final dictionary
        cdav = {}
        cdav["url"] = new_url
        cdav["username"] = new_user
        cdav["password"] = new_pwd
        cdav["tag"] = new_tag
        cdav["colour"] = new_colour
        self._conf.caldav.append(cdav)
        self._item = len(self._conf.caldav) - 1

    def enter_url(self, url=""):
        question1 = _("Enter URL: (http(s)://[…] for a Caldav, ")
        question2 = _("webcal(s)://[user:password@][…] for a Webcal)")
        question = question1 + question2
        new_url = None
        while new_url is None:
            data = self.edit_generic(question, url)
            if data == "CUL_CANCEL":
                return
            else:
                new_url = data.text
        if new_url[:4] not in ("http", "webc"):
            err = _("Error: URL starts with http(s):// or webcal://")
            self._screen.addstr(self._y - 2, 0, " " * self._x)
            self._screen.addstr(self._y - 2, 0, err)
            self._screen.addstr(self._y - 1, 0, _("Press any key to continue"))
            key = self.ui.getkey()
            if key == "KEY_RESIZE":
                self.draw_conf_screen()
            return
        return new_url

    def enter_username(self, user=""):
        question = _("Enter username:")
        new_user = None
        while new_user is None:
            data = self.edit_generic(question, user)
            if data == "CUL_CANCEL":
                return
            else:
                new_user = data.text
        return new_user

    def enter_password(self, pwd=""):
        question = _("Enter password:")
        new_password = None
        while new_password is None:
            data = self.edit_generic(question, pwd, pwd=True)
            if data == "CUL_CANCEL":
                return
            else:
                new_password = data.text
        return new_password

    def edit_caldav_tag(self):
        cdav = self.cdav_copy(self._conf.caldav[self._editing_key])
        cur_tag = self._conf.caldav[self._editing_key]["tag"]
        question = _("Enter new tag [a-z]:")
        answer = _("(Current tag: ") + str(cur_tag) + ")"
        self.question_footer()
        self._screen.addstr(self._y - 2, 0, question[:self._x])
        self._screen.addstr(self._y - 1, 0, answer[:self._x])
        new_tag = self.ui.getkey()
        if not new_tag.isalpha():
            self.draw_conf_screen()  # if it is KEY_RESIZE, to be sure
            return
        cdav["tag"] = new_tag
        self._conf.caldav.pop(self._editing_key)
        self._conf.caldav.insert(self._editing_key, cdav)

    def edit_caldav_colour(self):
        cdav = self.cdav_copy(self._conf.caldav[self._editing_key])
        colour = (self._conf.caldav[self._editing_key]["colour"] + 1) % 8
        cdav["colour"] = colour
        self._conf.caldav.pop(self._editing_key)
        self._conf.caldav.insert(self._editing_key, cdav)

    def edit_caldav_url(self):
        cdav = self.cdav_copy(self._conf.caldav[self._editing_key])
        new_url = self.enter_url(cdav["url"])
        if not new_url:
            return
        cdav["url"] = new_url
        self._conf.caldav.pop(self._editing_key)
        self._conf.caldav.insert(self._editing_key, cdav)

    def edit_caldav_username(self):
        if self.iscaldav():
            cdav = self.cdav_copy(self._conf.caldav[self._editing_key])
            new_user = self.enter_username(cdav["username"])
            if not new_user:
                return
            cdav["username"] = new_user
            self._conf.caldav.pop(self._editing_key)
            self._conf.caldav.insert(self._editing_key, cdav)

    def edit_caldav_password(self):
        if self.iscaldav():
            cdav = self.cdav_copy(self._conf.caldav[self._editing_key])
            new_pwd = self.enter_password(cdav["password"])
            if not new_pwd:
                return
            cdav["password"] = new_pwd
            self._conf.caldav.pop(self._editing_key)
            self._conf.caldav.insert(self._editing_key, cdav)

    def edit_change_colour(self):
        indexes = self._conf.colours_idx
        indexes[self._editing_key] = (indexes[self._editing_key] + 1) % 8
        colours = self._conf.colours
        colours[self._editing_key] = curses.color_pair(indexes[self._editing_key])
        self._conf.colours = colours

    def post_edit(self, data):
        if (data == "KEY_RESIZE") or (data == "CUL_CANCEL"):
            # during error, resized or did nothing
            self.draw_conf_screen()
            return "CUL_CANCEL"
        else:
            # no error during input
            return data

########################################################################
# other functions
########################################################################

    def localconf_to_culconf(self):
        # due to the setter, if newhmin > oldhmax
        # hmin = oldhmax - 1
        self._conf.hmin = self._general["hmin"]
        self._conf.hmax = self._general["hmax"]
        # with the new hmax, use the setter for new hmin
        self._conf.hmin = self._general["hmin"]
        self._conf.WE = self._general["WE"]
        self._conf.todo = self._general["TODO"]  # noqa: T101
        self._conf.autosave = self._general["autosave"]
        self._conf.colourset = self._general["colourset"]
        self._conf.autosync = self._general["autosync"]
        self._conf.mouse = self._general["mouse"]

    def conf_screen(self):
        self.draw_conf_screen()
        key = self.ui.getkey()
        while True:
            if key in ["KEY_RESIZE"] + self._conf.keys["redraw"]:
                self.draw_conf_screen()
            if key in ["a", "A"] and self._tab > 0:  # key category caldav
                self.edit_add_item()
            if key in ["d", "D"] and self._tab > 0:  # key category caldav
                self.edit_delete()
            if key in ["t", "T"] and self._tab > 0:  # caldav tag
                if len(self._conf.caldav) > 0:  # at least a caldav to edit
                    self.edit_caldav_tag()
            if key in ["c", "C"] and self._tab > 0:  # caldav colour
                if len(self._conf.caldav) > 0:  # at least a caldav to edit
                    self.edit_caldav_colour()
            if key in ["u", "U"] and self._tab > 0:  # caldav url
                if len(self._conf.caldav) > 0:  # at least a caldav to edit
                    self.edit_caldav_url()
            if key in ["n", "N"] and self._tab > 0:  # caldav username
                if len(self._conf.caldav) > 0:  # at least a caldav to edit
                    self.edit_caldav_username()
            if key in ["p", "P"] and self._tab > 0:  # caldav password
                if len(self._conf.caldav) > 0:  # at least a caldav to edit
                    self.edit_caldav_password()
            if key in [" ", "\n"] + self._conf.keys["editevent"]:
                self.edit_item()
            if key in ["KEY_UP"] + self._conf.keys["prevweek"]:
                if self._item > 0:
                    self._item -= 1
                    if self._item < self._top:
                        self._top -= 1
                else:
                    self._item = len(self._tabs[self._tab]) - 1
                    self._top = max(0, self._item - (self._y - 9))
            if key in ["KEY_DOWN"] + self._conf.keys["nextweek"]:
                if self._item < len(self._tabs[self._tab]) - 1:
                    self._item += 1
                    # Are we on last on the last pad line?
                    if self._item - self._top == self._y - 8:
                        # scroll it
                        self._top += 1
                else:
                    self._item = 0
                    self._top = 0
            if key in ["\t", "KEY_RIGHT"] + self._conf.keys["nextday"]:
                self._tab = (self._tab + 1) % len(self._tabs)
                self._top = 0
                self._item = 0
            if key in ["KEY_BTAB", "KEY_LEFT"] + self._conf.keys["prevday"]:
                self._tab = (self._tab - 1) % len(self._tabs)
                self._top = 0
                self._item = 0
            if key in ["q"] + self._conf.keys["quit"]:
                self.localconf_to_culconf()
                self.oneline_footer()  # in case of message of caldav sync
                return self._conf
            self.redraw_tabs()
            key = self.ui.getkey()

    def iscaldav(self):
        if self._conf.caldav[self._editing_key]["url"][:6] == "webcal":
            self.oneline_footer()
            msg = _("Webcals do not require this parameter")
            self._screen.addstr(self._y - 1, 0, msg[:self.x])
            return False
        return True

    def debug(self, elt):
        self._screen.addstr(self._y - 2, 50, 'debug:   {}'.format(elt))
        self._screen.getch()  # just a pause
        self._screen.hline(self._y - 2, 50, " ", self._x - 51)

    def cdav_copy(self, cdav):
        new_cdav = {}
        new_cdav["url"] = cdav["url"]
        new_cdav["username"] = cdav["username"]
        new_cdav["password"] = cdav["password"]
        new_cdav["tag"] = cdav["tag"]
        new_cdav["colour"] = cdav["colour"]
        return new_cdav
