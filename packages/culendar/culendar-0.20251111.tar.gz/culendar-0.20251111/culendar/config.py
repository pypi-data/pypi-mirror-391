import curses
from os import (
    environ,
    getenv,
    mkdir,
    path,
)


class Config:
    def __init__(self):
        # Mouse activation
        self._mmask = curses.BUTTON1_CLICKED + curses.BUTTON1_DOUBLE_CLICKED + curses.BUTTON1_TRIPLE_CLICKED
        # invisible cursor
        curses.curs_set(0)
        # allow transparency
        curses.use_default_colors()
        # create default values
        self._hmin = 7   # 7 am
        self._hmax = 20  # 8 pm
        self._WE = bool(1)  # show week-ends
        self._todo = bool(0)      # doesn't show todo list
        self._todowidth = 0.2     # defaults 20% width
        self._autosave = bool(1)  # defaults to be less unusual
        self._colourset = 0       # defaults to flashy
        self._caldav = []         # empty list of caldavs
        self._autosync = False    # autoupdate all caldavs when changing day
        self._mouse = False       # disable mouse
        curses.mousemask(0)
        self._debug = bool(0)     # you want to see dead ducks
        self.checkdir()  # define paths
        self._configfile = self._configpath + '/culendar.conf'
        self._keysfile = self._configpath + '/keys.conf'
        self._coloursfile = self._configpath + '/colours.conf'
        self._categoriesfile = self._configpath + '/categories.conf'
        self._caldavfile = self._configpath + '/caldav.conf'
        self._datafile = self.datapath + '/apts'
        self._todofile = self.datapath + '/todo'
        # create blanks one if not existing
        if not path.exists(self._datafile):
            with open(self._datafile, "w") as f:
                f.write("")
        if not path.exists(self._todofile):
            with open(self._todofile, "w") as f:
                f.write("")
        self.readconf()         # overwrites default values
        self.readkeys()         # defines self._keys
        self.readcolours()      # defines self._colours_idx
        self.setcolours()       # defines self._colours
        self.readcategories()   # defines self._categories
        self.readcaldav()       # get the caldavs configurations

    @property
    def hmin(self):
        return self._hmin

    @hmin.setter
    def hmin(self, hmin):
        if hmin >= self._hmax:
            self._hmin = self._hmax - 1
        else:
            self._hmin = max(0, hmin)

    @property
    def hmax(self):
        return self._hmax

    @hmax.setter
    def hmax(self, hmax):
        if hmax <= self._hmin:
            self._hmax = self._hmin + 1
        else:
            self._hmax = min(24, hmax)

    @property
    def WE(self):
        return self._WE

    @WE.setter
    def WE(self, WE):
        self._WE = WE

    @property
    def todo(self):
        return self._todo

    @todo.setter
    def todo(self, T):
        self._todo = T

    @property
    def todowidth(self):
        return self._todowidth

    @property
    def autosave(self):
        return self._autosave

    @autosave.setter
    def autosave(self, autosave):
        self._autosave = autosave

    @property
    def keys(self):
        return self._keys

    @keys.setter
    def keys(self, keys):
        self._keys = keys

    @property
    def datapath(self):
        return self._datapath

    @property
    def datafile(self):
        return self._datafile

    @property
    def todofile(self):
        return self._todofile

    @property
    def colourset(self):
        return self._colourset

    @colourset.setter
    def colourset(self, cs):
        self._colourset = cs

    @property
    def colours_idx(self):
        return self._colours_idx

    @colours_idx.setter
    def colours_idx(self, idx):
        self._colours_idx = idx

    @property
    def colours(self):
        return self._colours

    @colours.setter
    def colours(self, colours):
        self._colours = colours

    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, categories):
        self._categories = categories

    @property
    def caldav(self):
        return self._caldav

    @caldav.setter
    def caldav(self, caldav):
        self._caldav = caldav

    @property
    def autosync(self):
        return self._autosync

    @autosync.setter
    def autosync(self, autosync):
        self._autosync = autosync

    @property
    def mouse(self):
        return self._mouse

    @mouse.setter
    def mouse(self, mouse):
        self._mouse = mouse
        if mouse:
            curses.mousemask(self._mmask)
        else:
            curses.mousemask(0)

    @property
    def debug(self):
        return self._debug

    def checkdir(self):
        # configuration stuff
        if 'XDG_CONFIG_HOME' in environ:
            self._configpath = getenv('XDG_DATA_HOME')
        else:
            self._configpath = getenv('HOME') + '/.config/culendar'
        if not path.exists(self._configpath):
            # implicitly suppose that $HOME/.config already exists
            mkdir(self._configpath)
        # data stuff
        if 'XDG_DATA_HOME' in environ:
            self._datapath = getenv('XDG_DATA_HOME')
        else:
            self._datapath = getenv('HOME') + '/.local/share/culendar'
        if not path.exists(self._datapath):
            # implicitly suppose that $HOME/.local/share already exists
            mkdir(self._datapath)

    def readconf(self):
        if not path.exists(self._configfile):
            # write the default conf
            self.writeconf()
        else:
            with open(self._configfile) as f:
                for line in f:
                    if line[0:7] == 'hmin = ':
                        # don't use the setter to have no limit on hmin
                        self._hmin = int(line[7:9])
                    if line[0:7] == 'hmax = ':
                        # use the setter to be sure to be higher than hmin
                        self.hmax = int(line[7:9])
                    if line[0:5] == 'WE = ':
                        self._WE = bool(int(line[5]))  # "0" to 0 to False
                    if line[0:11] == 'autosave = ':
                        self._autosave = bool(int(line[11]))
                    if line[0:12] == 'colourset = ':
                        self._colourset = int(line[12])
                    if line[0:11] == 'autosync = ':
                        self._autosync = bool(int(line[11]))
                    if line[0:8] == 'debug = ':
                        self._debug = bool(int(line[8]))
                    if line[0:7] == 'todo = ':
                        self._todo = bool(int(line[7]))
                    if line[0:12] == 'todowidth = ':
                        self._todowidth = float(line[12:])
                    if line[0:8] == 'mouse = ':
                        self.mouse = bool(int(line[8:]))
                # TODO: check if all is fine

    def writeconf(self):
        with open(self._configfile, "w") as f:
            f.write('hmin = ' + str(self._hmin) + '\n')
            f.write('hmax = ' + str(self._hmax) + '\n')
            f.write('WE = ' + str(int(self._WE)) + '\n')
            f.write('autosave = ' + str(int(self._autosave)) + '\n')
            f.write('colourset = ' + str(self._colourset) + '\n')
            f.write('autosync = ' + str(int(self._autosync)) + '\n')
            f.write('todo = ' + str(int(self._todo)) + '\n')
            f.write('todowidth = ' + str(self._todowidth) + '\n')
            f.write('mouse = ' + str(int(self._mouse)))
            if self._debug:  # if the debug is forced, write it
                f.write('\ndebug = ' + str(int(self._debug)))

    def readkeys(self):
        self._keys = {}
        if path.exists(self._keysfile):
            with open(self._keysfile) as f:
                for line in f:
                    # find separator between keyword and keys
                    ind = line.find(":")
                    keyword = line[:ind]
                    # +1 ignore :, -1 ignore final \n
                    keys = line[ind+1:-1].replace(" ", "").split(",")
                    if "SPACE" in keys:
                        keys.append(" ")
                        keys.remove("SPACE")
                    self._keys[keyword] = keys
        # check if all operations are defined, defaults if needed
        oldkeys = self._keys.copy()
        try:
            self._keys['quit']
        except KeyError:
            self._keys['quit'] = ['q', 'Q']
        try:
            self._keys['nextday']
        except KeyError:
            self._keys['nextday'] = ['KEY_RIGHT']
        try:
            self._keys['prevday']
        except KeyError:
            self._keys['prevday'] = ['KEY_LEFT']
        try:
            self._keys['nextweek']
        except KeyError:
            self._keys['nextweek'] = ['KEY_DOWN']
        try:
            self._keys['prevweek']
        except KeyError:
            self._keys['prevweek'] = ['KEY_UP']
        try:
            self._keys['nextmonth']
        except KeyError:
            self._keys['nextmonth'] = ['m']
        try:
            self._keys['prevmonth']
        except KeyError:
            self._keys['prevmonth'] = ['M']
        try:
            self._keys['nextyear']
        except KeyError:
            self._keys['nextyear'] = ['KEY_PPAGE', 'y']
        try:
            self._keys['prevyear']
        except KeyError:
            self._keys['prevyear'] = ['KEY_NPAGE', 'Y']
        try:
            self._keys['nextevent']
        except KeyError:
            self._keys['nextevent'] = ['KEY_END', '	']  # tab
        try:
            self._keys['prevevent']
        except KeyError:
            self._keys['prevevent'] = ['KEY_HOME', 'KEY_BTAB']
        try:
            self._keys['delevent']
        except KeyError:
            self._keys['delevent'] = ['d', 'D']
        try:
            self._keys['addevent']
        except KeyError:
            self._keys['addevent'] = ['a', 'A']
        try:
            self._keys['editevent']
        except KeyError:
            self._keys['editevent'] = ['e', 'E']
        try:
            self._keys['toggleWE']
        except KeyError:
            self._keys['toggleWE'] = ['w', 'W']
        try:
            self._keys['redraw']
        except KeyError:
            self._keys['redraw'] = ['', '']
        try:
            self._keys['sync']
        except KeyError:
            self._keys['sync'] = ['']
        try:
            self._keys['save']
        except KeyError:
            self._keys['save'] = ['s', 'S']
        try:
            self._keys['import']
        except KeyError:
            self._keys['import'] = ['i', 'I']
        try:
            self._keys['export']
        except KeyError:
            self._keys['export'] = ['x', 'X']
        try:
            self._keys['today']
        except KeyError:
            self._keys['today'] = ['']
        try:
            self._keys['setday']
        except KeyError:
            self._keys['setday'] = ['g', 'G']
        try:
            self._keys['startweek']
        except KeyError:
            self._keys['startweek'] = ['0']
        try:
            self._keys['endweek']
        except KeyError:
            self._keys['endweek'] = ['$']
        try:
            self._keys['help']
        except KeyError:
            self._keys['help'] = ['h', 'H']
        try:
            self._keys['tagevent']
        except KeyError:
            self._keys['tagevent'] = ['t', 'T', '|']
        try:
            self._keys['copyevent']
        except KeyError:
            self._keys['copyevent'] = ['p', 'P']
        try:
            self._keys['minusshifthour']
        except KeyError:
            self._keys['minusshifthour'] = ['-']
        try:
            self._keys['shifthour']
        except KeyError:
            self._keys['shifthour'] = ['+']
        try:
            self._keys['minusshiftday']
        except KeyError:
            self._keys['minusshiftday'] = ['/']
        try:
            self._keys['shiftday']
        except KeyError:
            self._keys['shiftday'] = ['*']
        try:
            self._keys['setconfig']
        except KeyError:
            self._keys['setconfig'] = ['c', 'C']
        try:
            self._keys['toggletodo']
        except KeyError:
            self._keys['toggletodo'] = ['']

        if len(self._keys) > len(oldkeys):
            # if a default configuration has been used
            self.writekeys()

    def writekeys(self):
        lines = ""
        # ordered list of items
        keywords = [
            'nextday', 'prevday', 'nextweek', 'prevweek',
            'nextmonth', 'prevmonth', 'nextyear', 'prevyear',
            'nextevent', 'prevevent', 'delevent', 'addevent',
            'editevent', 'toggleWE', 'quit', 'redraw', 'sync', 'save',
            'import', 'export', 'today', 'setday', 'startweek',
            'endweek', 'help', 'tagevent', 'copyevent',
            'minusshifthour', 'shifthour', 'minusshiftday', 'shiftday',
            'setconfig', 'toggletodo',
        ]
        for op in keywords:
            line = op + ": "
            for k in self._keys[op]:
                if k == " ":
                    k = "SPACE"
                line = line + k + ", "
            # replace last comma and space by a newline
            line = line[:-2] + "\n"
            lines += line
        with open(self._keysfile, "w") as f:
            f.write(lines)

    def readcolours(self):
        if not path.exists(self._coloursfile):
            # defaults and write file
            self._colours_idx = range(8)
            self.writecolours()
        else:
            self._colours_idx = []
            with open(self._coloursfile) as f:
                for line in f:
                    self._colours_idx.append(int(line))

    def writecolours(self):
        lines = ""
        for colour_idx in self._colours_idx:
            lines += str(colour_idx) + "\n"
        with open(self._coloursfile, "w") as f:
            f.write(lines)

    def setcolours(self):
        self._colours = []
        # define the eight colours
        for i in range(8):
            try:  # the terminal has a default background
                curses.init_pair(i, i, -1)
            except ValueError:  # defaults to black
                curses.init_pair(i, i, 0)
        for idx in self._colours_idx:
            self._colours.append(curses.color_pair(idx))

    def readcategories(self):
        self._categories = {}
        if not path.exists(self._categoriesfile):
            # defaults and write file
            for i in range(1, 8):
                self._categories[i] = [str(i)]
            self.writecategories()
        else:
            with open(self._categoriesfile) as f:
                for idx, line in enumerate(f):
                    cat = line[:-1].replace(", ", ",").split(",")
                    # -1 to ignore final \n
                    self._categories[idx + 1] = cat
                    # +1: category 0 is defaults

    def writecategories(self):
        lines = ""
        for tagnb in range(1, 8):
            line = ""
            for cat in self._categories[tagnb]:
                line = line + cat + ", "
            # replace last comma and space by a newline
            line = line[:-2] + "\n"
            lines += line
        with open(self._categoriesfile, "w") as f:
            f.write(lines)

    def readcaldav(self):
        if path.exists(self._caldavfile):
            with open(self._caldavfile) as f:
                for line in f:
                    cdav = {}  # initiate the dict
                    endurl = line.find(", username=")
                    endusername = line.find(", password=")
                    endpassword = line.find(", tag=")
                    endtag = line.find(", colour=")
                    # 5 to skip the starting  'url="'
                    url = line[5:endurl - 1]
                    # is there a password?
                    if endusername - endurl > 13:
                        username = line[endurl + 12:endusername - 1]
                        password = line[endusername + 12:endpassword - 1]
                    else:
                        username = ""
                        password = ""
                    tag = line[endpassword + 7:endtag - 1]
                    # line finish by 'colour="X"\n', get the X
                    colour = int(line[-3])
                    # fill up the caldav's dict
                    cdav["url"] = url
                    cdav["username"] = username
                    cdav["password"] = password
                    cdav["tag"] = tag
                    cdav["colour"] = colour
                    # stack it in the list
                    self._caldav.append(cdav)

    def writecaldav(self):
        lines = ""
        for cdav in self._caldav:
            line = ""
            line += 'url="' + cdav["url"]
            line += '", username="' + cdav["username"]
            line += '", password="' + cdav["password"]
            line += '", tag="' + cdav["tag"]
            line += '", colour="' + str(cdav["colour"]) + '"\n'
            lines += line
        with open(self._caldavfile, "w") as f:
            f.write(lines)

    def save(self):
        self.writeconf()
        self.writekeys()
        self.writecolours()
        self.writecategories()
        self.writecaldav()
