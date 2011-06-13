from string import Template
import re
from copy import copy
from PyQt4 import QtGui, QtCore
from datetime import time, timedelta, datetime

from dataobjs import PesterProfile, Mood, PesterHistory
from generic import PesterIcon, RightClickList, mysteryTime
from convo import PesterConvo, PesterInput, PesterText, PesterTabWindow
from parsetools import convertTags, addTimeInitial, timeProtocol, \
    lexMessage, colorBegin, colorEnd, mecmd, smiledict
from logviewer import PesterLogViewer


def delta2txt(d, format="pc"):
    if type(d) is mysteryTime:
        return "?"
    if format == "pc":
        sign = "+" if d >= timedelta(0) else "-"
    else:
        if d == timedelta(0):
            return "i"
        sign = "F" if d >= timedelta(0) else "P"
    d = abs(d)
    totalminutes = (d.days*86400 + d.seconds) // 60
    hours = totalminutes // 60
    leftovermins = totalminutes % 60
    if hours < 100:
        if format == "pc":
            return "%s%d:%02d" % (sign, hours, leftovermins)
        else:
            return "%s%02d:%02d" % (sign, hours, leftovermins)
    else:
        if format == "pc":
            return "%s%d" % (sign, hours)
        else:
            return "%s%02d:%02d" % (sign, hours, leftovermins)

def txt2delta(txt):
    sign = 1
    if txt[0] == '?':
        return mysteryTime()
    if txt[0] == '+':
        txt = txt[1:]
    elif txt[0] == '-':
        sign = -1
        txt = txt[1:]
    l = txt.split(":")
    try:
        h = int(l[0])
        m = 0
        if len(l) > 1:
            m = int(l[1])
        timed = timedelta(0, h*3600+m*60)
    except ValueError:
        timed = timedelta(0)
    except OverflowError:
        if sign < 0:
            return timedelta(min)
        else:
            return timedelta(max)
    return sign*timed

def pcfGrammar(td):
    if type(td) is mysteryTime:
        when = "???"
        temporal = "???"
        pcf = "?"
    elif td > timedelta(0):
        when = "FROM NOW"
        temporal = "FUTURE"
        pcf = "F"
    elif td < timedelta(0):
        when = "AGO"
        temporal = "PAST"
        pcf = "P"
    else:
        when = "RIGHT NOW"
        temporal = "CURRENT"
        pcf = "C"
    return (temporal, pcf, when)

class TimeGrammar(object):
    def __init__(self, temporal, pcf, when, number="0"):
        self.temporal = temporal
        self.pcf = pcf
        self.when = when
        if number == "0" or number == 0:
            self.number = ""
        else:
            self.number = str(number)

class TimeTracker(list):
    def __init__(self, time=None):
        self.timerecord = {"P": [], "F": []}
        self.open = {}
        if time is not None:
            self.append(time)
            self.current=0
            self.addRecord(time)
            self.open[time] = False
        else:
            self.current=-1
    def addTime(self, timed):
        try:
            i = self.index(timed)
            self.current = i
            return True
        except ValueError:
            self.current = len(self)
            self.append(timed)
            self.open[timed] = False
            self.addRecord(timed)
            return False
    def prevTime(self):
        i = self.current
        i = (i - 1) % len(self)
        return self[i]
    def nextTime(self):
        i = self.current
        i = (i + 1) % len(self)
        return self[i]
    def setCurrent(self, timed):
        self.current = self.index(timed)
    def addRecord(self, timed):
        try:
            (temporal, pcf, when) = pcfGrammar(timed - timedelta(0))
        except TypeError:
            (temporal, pcf, when) = pcfGrammar(mysteryTime())
        if pcf == "C" or pcf == "?":
            return
        if timed in self.timerecord[pcf]:
            return
        self.timerecord[pcf].append(timed)
    def getRecord(self, timed):
        try:
            (temporal, pcf, when) = pcfGrammar(timed - timedelta(0))
        except TypeError:
            (temporal, pcf, when) = pcfGrammar(mysteryTime())
        if pcf == "C" or pcf == "?":
            return 0
        if len(self.timerecord[pcf]) > 1:
            return self.timerecord[pcf].index(timed)+1
        else:
            return 0
    def removeTime(self, timed):
        try:
            self.pop(self.index(timed))
            self.current = len(self)-1
            del self.open[timed]
            return True
        except ValueError:
            return None
    def openTime(self, time):
        if self.open.has_key(time):
            self.open[time] = True
    def openCurrentTime(self):
        timed = self.getTime()
        self.openTime(timed)
    def isFirstTime(self):
        timed = self.getTime()
        return not self.open[timed]
    def getTime(self):
        if self.current >= 0:
            return self[self.current]
        else:
            return None
    def getGrammar(self):
        timed = self.getTime()
        return self.getGrammarTime(timed)
    def getGrammarTime(self, timed):
        mytime = timedelta(0)
        try:
            (temporal, pcf, when) = pcfGrammar(timed - mytime)
        except TypeError:
            (temporal, pcf, when) = pcfGrammar(mysteryTime())
        if timed == mytime:
            return TimeGrammar(temporal, pcf, when, 0)
        return TimeGrammar(temporal, pcf, when, self.getRecord(timed))

class TimeInput(QtGui.QLineEdit):
    def __init__(self, timeslider, parent):
        QtGui.QLineEdit.__init__(self, parent)
        self.timeslider = timeslider
        self.setText("+0:00")
        self.connect(self.timeslider, QtCore.SIGNAL('valueChanged(int)'),
                     self, QtCore.SLOT('setTime(int)'))
        self.connect(self, QtCore.SIGNAL('editingFinished()'),
                    self, QtCore.SLOT('setSlider()'))
    @QtCore.pyqtSlot(int)
    def setTime(self, sliderval):
        self.setText(self.timeslider.getTime())
    @QtCore.pyqtSlot()
    def setSlider(self):
        value = unicode(self.text())
        timed = txt2delta(value)
        if type(timed) is mysteryTime:
            self.timeslider.setValue(0)
            self.setText("?")
            return
        sign = 1 if timed >= timedelta(0) else -1
        abstimed = abs(txt2delta(value))
        index = 50
        for i, td in enumerate(timedlist):
            if abstimed < td:
                index = i-1
                break
        self.timeslider.setValue(sign*index)
        text = delta2txt(timed)
        self.setText(text)

class TimeSlider(QtGui.QSlider):
    def __init__(self, orientation, parent):
        QtGui.QSlider.__init__(self, orientation, parent)
        self.setTracking(True)
        self.setMinimum(-50)
        self.setMaximum(50)
        self.setValue(0)
        self.setPageStep(1)
    def getTime(self):
        time = timelist[abs(self.value())]
        sign = "+" if self.value() >= 0 else "-"
        return sign+time
    def mouseDoubleClickEvent(self, event):
        self.setValue(0)

class MemoTabWindow(PesterTabWindow):
    def __init__(self, mainwindow, parent=None):
        PesterTabWindow.__init__(self, mainwindow, parent, "memos")
    def addChat(self, convo):
        self.convos[convo.channel] = convo
        # either addTab or setCurrentIndex will trigger changed()
        newindex = self.tabs.addTab(convo.channel)
        self.tabIndices[convo.channel] = newindex
        self.tabs.setCurrentIndex(newindex)
        self.tabs.setTabIcon(newindex, PesterIcon(self.mainwindow.theme["memos/memoicon"]))
    def updateBlocked(self):
        pass
    def updateMood(self):
        pass

_ctag_begin = re.compile(r'<c=(.*?)>')

class MemoText(PesterText):
    def __init__(self, theme, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        if hasattr(self.parent(), 'mainwindow'):
            self.mainwindow = self.parent().mainwindow
        else:
            self.mainwindow = self.parent()
        self.initTheme(theme)
        self.setReadOnly(True)
        self.setMouseTracking(True)
        self.textSelected = False
        self.connect(self, QtCore.SIGNAL('copyAvailable(bool)'),
                     self, QtCore.SLOT('textReady(bool)'))
        self.urls = {}
        for k in smiledict:
            self.addAnimation(QtCore.QUrl("smilies/%s" % (smiledict[k])), "smilies/%s" % (smiledict[k]));

    def initTheme(self, theme):
        if theme.has_key("memos/scrollbar"):
            self.setStyleSheet("QTextEdit { %s } QScrollBar:vertical { %s } QScrollBar::handle:vertical { %s } QScrollBar::add-line:vertical { %s } QScrollBar::sub-line:vertical { %s } QScrollBar:up-arrow:vertical { %s } QScrollBar:down-arrow:vertical { %s }" % (theme["memos/textarea/style"], theme["memos/scrollbar/style"], theme["memos/scrollbar/handle"], theme["memos/scrollbar/downarrow"], theme["memos/scrollbar/uparrow"], theme["memos/scrollbar/uarrowstyle"], theme["memos/scrollbar/darrowstyle"] ))
        else:
            self.setStyleSheet("QTextEdit { %s }" % theme["memos/textarea/style"])

    def addMessage(self, msg, chum):
        if type(msg) in [str, unicode]:
            lexmsg = lexMessage(msg)
        else:
            lexmsg = msg
        parent = self.parent()
        window = parent.mainwindow
        me = window.profile()
        chumdb = window.chumdb
        if chum is not me: # SO MUCH WH1T3SP4C3 >:]
            if type(lexmsg[0]) is colorBegin: # get color tag
                colortag = lexmsg[0]
                try:
                    color = QtGui.QColor(*[int(c) for c in colortag.color.split(",")])
                except ValueError:
                    color = QtGui.QColor("black")
                else:
                    chumdb.setColor(chum.handle, color)
                    parent.updateColor(chum.handle, color)
            else:
                color = chumdb.getColor(chum.handle)
        else:
            color = me.color

        chum.color = color
        systemColor = QtGui.QColor(window.theme["memos/systemMsgColor"])
        if chum is not me:
            if parent.times.has_key(chum.handle):
                time = parent.times[chum.handle]
                if time.getTime() is None:
                    # MY WAY OR THE HIGHWAY
                    time.addTime(timedelta(0))
            else:
                # new chum! time current
                newtime = timedelta(0)
                time = TimeTracker(newtime)
                parent.times[handle] = time
        else:
            time = parent.time

        if time.isFirstTime():
            grammar = time.getGrammar()
            joinmsg = chum.memojoinmsg(systemColor, time.getTime(), grammar, window.theme["convo/text/joinmemo"])
            self.append(convertTags(joinmsg))
            parent.mainwindow.chatlog.log(parent.channel, joinmsg)
            time.openCurrentTime()

        def makeSafe(msg):
            if msg.count("<c") > msg.count("</c>"):
                for i in range(msg.count("<c") - msg.count("</c>")):
                    msg = msg + "</c>"
            return msg
        if type(lexmsg[0]) is mecmd:
            memsg = chum.memsg(systemColor, lexmsg, time=time.getGrammar())
            window.chatlog.log(parent.channel, memsg)
            self.append(convertTags(memsg))
        else:
            self.append(makeSafe(convertTags(lexmsg)))
            window.chatlog.log(parent.channel, lexmsg)

    def changeTheme(self, theme):
        self.initTheme(theme)
    def submitLogTitle(self):
        return "[%s]" % (self.parent().title())

class MemoInput(PesterInput):
    def __init__(self, theme, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.setStyleSheet(theme["memos/input/style"])
    def changeTheme(self, theme):
        self.setStyleSheet(theme["memos/input/style"])

class PesterMemo(PesterConvo):
    def __init__(self, channel, timestr, mainwindow, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
        self.channel = channel
        self.setObjectName(self.channel)
        self.mainwindow = mainwindow
        self.time = TimeTracker(txt2delta(timestr))
        self.setWindowTitle(channel)
        self.channelLabel = QtGui.QLabel(self)
        self.channelLabel.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding))

        self.textArea = MemoText(self.mainwindow.theme, self)
        self.textInput = MemoInput(self.mainwindow.theme, self)
        self.textInput.setFocus()

        self.userlist = RightClickList(self)
        self.userlist.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding))
        self.userlist.optionsMenu = QtGui.QMenu(self)
        self.addchumAction = QtGui.QAction(self.mainwindow.theme["main/menus/rclickchumlist/addchum"], self)
        self.connect(self.addchumAction, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('addChumSlot()'))
        self.banuserAction = QtGui.QAction(self.mainwindow.theme["main/menus/rclickchumlist/banuser"], self)
        self.connect(self.banuserAction, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('banSelectedUser()'))
        self.opAction = QtGui.QAction(self.mainwindow.theme["main/menus/rclickchumlist/opuser"], self)
        self.connect(self.opAction, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('opSelectedUser()'))
        self.voiceAction = QtGui.QAction(self.mainwindow.theme["main/menus/rclickchumlist/voiceuser"], self)
        self.connect(self.voiceAction, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('voiceSelectedUser()'))
        self.userlist.optionsMenu.addAction(self.addchumAction)
        # ban & op list added if we are op

        self.optionsMenu = QtGui.QMenu(self)
        self.quirksOff = QtGui.QAction(self.mainwindow.theme["main/menus/rclickchumlist/quirksoff"], self)
        self.quirksOff.setCheckable(True)
        self.connect(self.quirksOff, QtCore.SIGNAL('toggled(bool)'),
                     self, QtCore.SLOT('toggleQuirks(bool)'))
        self.logchum = QtGui.QAction(self.mainwindow.theme["main/menus/rclickchumlist/viewlog"], self)
        self.connect(self.logchum, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('openChumLogs()'))
        self.invitechum = QtGui.QAction(self.mainwindow.theme["main/menus/rclickchumlist/invitechum"], self)
        self.connect(self.invitechum, QtCore.SIGNAL('triggered()'),
                     self, QtCore.SLOT('inviteChums()'))
        self.optionsMenu.addAction(self.quirksOff)
        self.optionsMenu.addAction(self.logchum)
        self.optionsMenu.addAction(self.invitechum)

        self.chanModeMenu = QtGui.QMenu("Memo Settings", self)
        self.chanHide = QtGui.QAction("Hidden", self)
        self.chanHide.setCheckable(True)
        self.connect(self.chanHide, QtCore.SIGNAL('toggled(bool)'),
                     self, QtCore.SLOT('hideChan(bool)'))
        self.chanInvite = QtGui.QAction("Invite-Only", self)
        self.chanInvite.setCheckable(True)
        self.connect(self.chanInvite, QtCore.SIGNAL('toggled(bool)'),
                     self, QtCore.SLOT('inviteChan(bool)'))
        self.chanMod = QtGui.QAction("Mute", self)
        self.chanMod.setCheckable(True)
        self.connect(self.chanMod, QtCore.SIGNAL('toggled(bool)'),
                     self, QtCore.SLOT('modChan(bool)'))
        self.chanModeMenu.addAction(self.chanHide)
        self.chanModeMenu.addAction(self.chanInvite)
        self.chanModeMenu.addAction(self.chanMod)

        self.timeslider = TimeSlider(QtCore.Qt.Horizontal, self)
        self.timeinput = TimeInput(self.timeslider, self)
        self.timeinput.setText(timestr)
        self.timeinput.setSlider()
        self.timetravel = QtGui.QPushButton("GO", self)
        self.timeclose = QtGui.QPushButton("CLOSE", self)
        self.timeswitchl = QtGui.QPushButton(self)
        self.timeswitchr = QtGui.QPushButton(self)

        self.connect(self.timetravel, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('sendtime()'))
        self.connect(self.timeclose, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('smashclock()'))
        self.connect(self.timeswitchl, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('prevtime()'))
        self.connect(self.timeswitchr, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('nexttime()'))

        self.times = {}

        self.initTheme(self.mainwindow.theme)

        # connect
        self.connect(self.textInput, QtCore.SIGNAL('returnPressed()'),
                     self, QtCore.SLOT('sentMessage()'))

        layout_0 = QtGui.QVBoxLayout()
        layout_0.addWidget(self.textArea)
        layout_0.addWidget(self.textInput)

        layout_1 = QtGui.QHBoxLayout()
        layout_1.addLayout(layout_0)
        layout_1.addWidget(self.userlist)

#        layout_1 = QtGui.QGridLayout()
#        layout_1.addWidget(self.timeslider, 0, 1, QtCore.Qt.AlignHCenter)
#        layout_1.addWidget(self.timeinput, 1, 0, 1, 3)
        layout_2 = QtGui.QHBoxLayout()
        layout_2.addWidget(self.timeslider)
        layout_2.addWidget(self.timeinput)
        layout_2.addWidget(self.timetravel)
        layout_2.addWidget(self.timeclose)
        layout_2.addWidget(self.timeswitchl)
        layout_2.addWidget(self.timeswitchr)
        self.layout = QtGui.QVBoxLayout()

        self.layout.addWidget(self.channelLabel)
        self.layout.addLayout(layout_1)
        self.layout.addLayout(layout_2)
        self.layout.setSpacing(0)
        margins = self.mainwindow.theme["memos/margins"]
        self.layout.setContentsMargins(margins["left"], margins["top"],
                                  margins["right"], margins["bottom"])

        self.setLayout(self.layout)

        if parent:
            parent.addChat(self)

        p = self.mainwindow.profile()
        timeGrammar = self.time.getGrammar()
        systemColor = QtGui.QColor(self.mainwindow.theme["memos/systemMsgColor"])
        msg = p.memoopenmsg(systemColor, self.time.getTime(), timeGrammar, self.mainwindow.theme["convo/text/openmemo"], self.channel)
        self.time.openCurrentTime()
        self.textArea.append(convertTags(msg))
        self.mainwindow.chatlog.log(self.channel, msg)

        self.op = False
        self.newmessage = False
        self.history = PesterHistory()
        self.applyquirks = True

    def title(self):
        return self.channel
    def icon(self):
        return PesterIcon(self.mainwindow.theme["memos/memoicon"])

    def sendTimeInfo(self, newChum=False):
        if newChum:
            self.messageSent.emit("PESTERCHUM:TIME>%s" % (delta2txt(self.time.getTime(), "server")+"i"),
                                  self.title())
        else:
            self.messageSent.emit("PESTERCHUM:TIME>%s" % (delta2txt(self.time.getTime(), "server")),
                                  self.title())

    def updateMood(self):
        pass
    def updateBlocked(self):
        pass
    def updateColor(self, handle, color):
        chums = self.userlist.findItems(handle, QtCore.Qt.MatchFlags(0))
        for c in chums:
            c.setTextColor(color)
    def addMessage(self, text, handle):
        if type(handle) is bool:
            chum = self.mainwindow.profile()
        else:
            chum = PesterProfile(handle)
            self.notifyNewMessage()
        self.textArea.addMessage(text, chum)

    def initTheme(self, theme):
        self.resize(*theme["memos/size"])
        self.setStyleSheet("QFrame#%s { %s }" % (self.channel, theme["memos/style"]))
        self.setWindowIcon(PesterIcon(theme["memos/memoicon"]))

        t = Template(theme["memos/label/text"])
        self.channelLabel.setText(t.safe_substitute(channel=self.channel))
        self.channelLabel.setStyleSheet(theme["memos/label/style"])
        self.channelLabel.setAlignment(self.aligndict["h"][theme["memos/label/align/h"]] | self.aligndict["v"][theme["memos/label/align/v"]])
        self.channelLabel.setMaximumHeight(theme["memos/label/maxheight"])
        self.channelLabel.setMinimumHeight(theme["memos/label/minheight"])

        self.userlist.optionsMenu.setStyleSheet(theme["main/defaultwindow/style"])
        scrolls = "width: 12px; height: 12px; border: 0; padding: 0;"
        if theme.has_key("main/chums/scrollbar"):
            self.userlist.setStyleSheet("QListWidget { %s } QScrollBar { %s } QScrollBar::handle { %s } QScrollBar::add-line { %s } QScrollBar::sub-line { %s } QScrollBar:up-arrow { %s } QScrollBar:down-arrow { %s }" % (theme["memos/userlist/style"], theme["main/chums/scrollbar/style"] + scrolls, theme["main/chums/scrollbar/handle"], theme["main/chums/scrollbar/downarrow"], theme["main/chums/scrollbar/uparrow"], theme["main/chums/scrollbar/uarrowstyle"], theme["main/chums/scrollbar/darrowstyle"] ))
        elif theme.has_key("convo/scrollbar"):
            self.userlist.setStyleSheet("QListWidget { %s } QScrollBar { %s } QScrollBar::handle { %s } QScrollBar::add-line { %s } QScrollBar::sub-line { %s } QScrollBar:up-arrow { %s } QScrollBar:down-arrow { %s }" % (theme["memos/userlist/style"], theme["convo/scrollbar/style"] + scrolls, theme["convo/scrollbar/handle"], "display:none;", "display:none;", "display:none;", "display:none;" ))
        else:
            self.userlist.setStyleSheet("QListWidget { %s } QScrollBar { %s } QScrollBar::handle { %s }" % (theme["memos/userlist/style"], scrolls, "background-color: black;"))
        self.userlist.setFixedWidth(theme["memos/userlist/width"])
        self.addchumAction.setText(theme["main/menus/rclickchumlist/addchum"])
        self.banuserAction.setText(theme["main/menus/rclickchumlist/banuser"])
        self.opAction.setText(theme["main/menus/rclickchumlist/opuser"])
        self.voiceAction.setText(theme["main/menus/rclickchumlist/voiceuser"])
        self.quirksOff.setText(theme["main/menus/rclickchumlist/quirksoff"])
        self.logchum.setText(theme["main/menus/rclickchumlist/viewlog"])

        self.timeinput.setFixedWidth(theme["memos/time/text/width"])
        self.timeinput.setStyleSheet(theme["memos/time/text/style"])
        slidercss = "QSlider { %s } QSlider::groove { %s } QSlider::handle { %s }" % (theme["memos/time/slider/style"], theme["memos/time/slider/groove"], theme["memos/time/slider/handle"])
        self.timeslider.setStyleSheet(slidercss)

        larrow = PesterIcon(self.mainwindow.theme["memos/time/arrows/left"])
        self.timeswitchl.setIcon(larrow)
        self.timeswitchl.setIconSize(larrow.realsize())
        self.timeswitchl.setStyleSheet(self.mainwindow.theme["memos/time/arrows/style"])
        self.timetravel.setStyleSheet(self.mainwindow.theme["memos/time/buttons/style"])
        self.timeclose.setStyleSheet(self.mainwindow.theme["memos/time/buttons/style"])

        rarrow = PesterIcon(self.mainwindow.theme["memos/time/arrows/right"])
        self.timeswitchr.setIcon(rarrow)
        self.timeswitchr.setIconSize(rarrow.realsize())
        self.timeswitchr.setStyleSheet(self.mainwindow.theme["memos/time/arrows/style"])


    def changeTheme(self, theme):
        self.initTheme(theme)
        self.textArea.changeTheme(theme)
        self.textInput.changeTheme(theme)
        margins = theme["memos/margins"]
        self.layout.setContentsMargins(margins["left"], margins["top"],
                                  margins["right"], margins["bottom"])
        for item in [self.userlist.item(i) for i in range(0,self.userlist.count())]:
            if item.op:
                icon = PesterIcon(self.mainwindow.theme["memos/op/icon"])
                item.setIcon(icon)
            elif item.voice:
                icon = PesterIcon(self.mainwindow.theme["memos/voice/icon"])
                item.setIcon(icon)

    def addUser(self, handle):
        chumdb = self.mainwindow.chumdb
        defaultcolor = QtGui.QColor("black")
        op = False
        voice = False
        if handle[0] == '@':
            op = True
            handle = handle[1:]
            if handle == self.mainwindow.profile().handle:
                self.userlist.optionsMenu.addAction(self.opAction)
                self.userlist.optionsMenu.addAction(self.banuserAction)
                self.optionsMenu.addMenu(self.chanModeMenu)
                self.op = True
        elif handle[0] == '+':
            voice = True
            handle = handle[1:]
        item = QtGui.QListWidgetItem(handle)
        if handle == self.mainwindow.profile().handle:
            color = self.mainwindow.profile().color
        else:
            color = chumdb.getColor(handle, defaultcolor)
        item.setTextColor(color)
        item.op = op
        item.voice = voice
        if op:
            icon = PesterIcon(self.mainwindow.theme["memos/op/icon"])
            item.setIcon(icon)
        elif voice:
            icon = PesterIcon(self.mainwindow.theme["memos/voice/icon"])
            item.setIcon(icon)
        self.userlist.addItem(item)
        self.sortUsers()

    def sortUsers(self):
        users = []
        listing = self.userlist.item(0)
        while listing is not None:
            users.append(self.userlist.takeItem(0))
            listing = self.userlist.item(0)
        users.sort(key=lambda x: ((0 if x.op else 1), (0 if x.voice else 1), x.text()))
        for u in users:
            self.userlist.addItem(u)

    def updateChanModes(self, modes):
        if not hasattr(self, 'modes'): self.modes = ""
        chanmodes = list(str(self.modes))
        if chanmodes and chanmodes[0] == "+": chanmodes = chanmodes[1:]
        modes = str(modes)
        if modes[0] == "+":
            chanmodes.extend(modes[1:])
            if modes.find("s") >= 0: self.chanHide.setChecked(True)
            if modes.find("i") >= 0: self.chanInvite.setChecked(True)
            if modes.find("m") >= 0: self.chanMod.setChecked(True)
        elif modes[0] == "-":
            for i in modes[1:]:
                try:
                    chanmodes.remove(i)
                except ValueError:
                    pass
            if modes.find("s") >= 0: self.chanHide.setChecked(False)
            if modes.find("i") >= 0: self.chanInvite.setChecked(False)
            if modes.find("m") >= 0: self.chanMod.setChecked(False)
        chanmodes.sort()
        self.modes = "+" + "".join(chanmodes)
        if self.mainwindow.advanced:
            t = Template(self.mainwindow.theme["memos/label/text"])
            self.channelLabel.setText(t.safe_substitute(channel=self.channel) + "(%s)" % (self.modes))

    def timeUpdate(self, handle, cmd):
        window = self.mainwindow
        chum = PesterProfile(handle)
        systemColor = QtGui.QColor(window.theme["memos/systemMsgColor"])
        close = None
        # old TC command?
        try:
            secs = int(cmd)
            time = datetime.fromtimestamp(secs)
            timed = time - datetime.now()
            s = (timed.seconds // 60)*60
            timed = timedelta(timed.days, s)
        except ValueError:
            if cmd == "i":
                timed = timedelta(0)
            else:
                if cmd[len(cmd)-1] == 'c':
                    close = timeProtocol(cmd)
                    timed = None
                else:
                    timed = timeProtocol(cmd)

        if self.times.has_key(handle):
            if close is not None:
                if close in self.times[handle]:
                    self.times[handle].setCurrent(close)
                    grammar = self.times[handle].getGrammar()
                    self.times[handle].removeTime(close)
                    msg = chum.memoclosemsg(systemColor, grammar, window.theme["convo/text/closememo"])
                    self.textArea.append(convertTags(msg))
                    self.mainwindow.chatlog.log(self.channel, msg)
            elif timed not in self.times[handle]:
                self.times[handle].addTime(timed)
            else:
                self.times[handle].setCurrent(timed)
        else:
            if timed is not None:
                ttracker = TimeTracker(timed)
                self.times[handle] = ttracker

    @QtCore.pyqtSlot()
    def sentMessage(self):
        text = unicode(self.textInput.text())
        if text == "" or text[0:11] == "PESTERCHUM:":
            return
        self.history.add(text)
        if self.time.getTime() == None:
            self.sendtime()
        grammar = self.time.getGrammar()
        quirks = self.mainwindow.userprofile.quirks
        lexmsg = lexMessage(text)
        if type(lexmsg[0]) is not mecmd:
            if self.applyquirks:
                lexmsg = quirks.apply(lexmsg)
            initials = self.mainwindow.profile().initials()
            colorcmd = self.mainwindow.profile().colorcmd()
            clientMsg = [colorBegin("<c=%s>" % (colorcmd), colorcmd),
                         "%s%s%s: " % (grammar.pcf, initials, grammar.number)] + lexmsg + [colorEnd("</c>")]
            # account for TC's parsing error
            serverMsg = [colorBegin("<c=%s>" % (colorcmd), colorcmd),
                         "%s: " % (initials)] + lexmsg + [colorEnd("</c>"), " "]
        else:
            clientMsg = copy(lexmsg)
            serverMsg = copy(lexmsg)

        self.addMessage(clientMsg, True)
        serverText = convertTags(serverMsg, "ctag")
        self.messageSent.emit(serverText, self.title())

        self.textInput.setText("")
    @QtCore.pyqtSlot()
    def namesUpdated(self):
        # get namesdb
        namesdb = self.mainwindow.namesdb
        # reload names
        self.userlist.clear()
        for n in self.mainwindow.namesdb[self.channel]:
            self.addUser(n)
    @QtCore.pyqtSlot(QtCore.QString, QtCore.QString)
    def modesUpdated(self, channel, modes):
        c = unicode(channel)
        if c == self.channel:
            self.updateChanModes(modes)

    @QtCore.pyqtSlot(QtCore.QString)
    def closeInviteOnly(self, channel):
        c = unicode(channel)
        if c == self.channel:
            self.disconnect(self.mainwindow, QtCore.SIGNAL('inviteOnlyChan(QString)'),
                     self, QtCore.SLOT('closeInviteOnly(QString)'))
            if self.parent():
                print self.channel
                i = self.parent().tabIndices[self.channel]
                self.parent().tabClose(i)
            else:
                self.close()
            msgbox = QtGui.QMessageBox()
            msgbox.setText("%s: Invites only!" % (c))
            msgbox.setInformativeText("This channel is invite-only. You must get an invitation from someone on the inside before entering.")
            msgbox.setStandardButtons(QtGui.QMessageBox.Ok)
            ret = msgbox.exec_()

    @QtCore.pyqtSlot(QtCore.QString, QtCore.QString, QtCore.QString)
    def userPresentChange(self, handle, channel, update):
        h = unicode(handle)
        c = unicode(channel)
        update = unicode(update)
        if update[0:4] == "kick": # yeah, i'm lazy.
            l = update.split(":")
            update = l[0]
            op = l[1]
            reason = l[2]
        if update == "nick":
            l = h.split(":")
            oldnick = l[0]
            newnick = l[1]
            h = oldnick
        if update[0:1] in ["+", "-"]:
            l = update.split(":")
            update = l[0]
            op = l[1]
        if (update in ["join","left", "kick", "+o", "-o", "+v", "-v"]) \
                and channel != self.channel:
            return
        chums = self.userlist.findItems(h, QtCore.Qt.MatchFlags(0))
        systemColor = QtGui.QColor(self.mainwindow.theme["memos/systemMsgColor"])
        # print exit
        if update == "quit" or update == "left" or update == "nick":
            for c in chums:
                chum = PesterProfile(h)
                self.userlist.takeItem(self.userlist.row(c))
                if not self.times.has_key(h):
                    self.times[h] = TimeTracker(timedelta(0))
                while self.times[h].getTime() is not None:
                    t = self.times[h]
                    grammar = t.getGrammar()
                    msg = chum.memoclosemsg(systemColor, grammar, self.mainwindow.theme["convo/text/closememo"])
                    self.textArea.append(convertTags(msg))
                    self.mainwindow.chatlog.log(self.channel, msg)
                    self.times[h].removeTime(t.getTime())
                if update == "nick":
                    self.addUser(newnick)
                    newchums = self.userlist.findItems(newnick, QtCore.Qt.MatchFlags(0))
                    for nc in newchums:
                        for c in chums:
                            if c.op:
                                nc.op = True
                                icon = PesterIcon(self.mainwindow.theme["memos/op/icon"])
                                nc.setIcon(icon)
                            if c.voice:
                                nc.voice = True
                                icon = PesterIcon(self.mainwindow.theme["memos/voice/icon"])
                                nc.setIcon(icon)
                    self.sortUsers()
        elif update == "kick":
            if len(chums) == 0:
                return
            c = chums[0]
            chum = PesterProfile(h)
            if h == self.mainwindow.profile().handle:
                chum = self.mainwindow.profile()
                ttracker = self.time
                curtime = self.time.getTime()
            elif self.times.has_key(h):
                ttracker = self.times[h]
            else:
                ttracker = TimeTracker(timedelta(0))
            while ttracker.getTime() is not None:
                grammar = ttracker.getGrammar()
                opchum = PesterProfile(op)
                if self.times.has_key(op):
                    opgrammar = self.times[op].getGrammar()
                elif op == self.mainwindow.profile().handle:
                    opgrammar = self.time.getGrammar()
                else:
                    opgrammar = TimeGrammar("CURRENT", "C", "RIGHT NOW")
                msg = chum.memobanmsg(opchum, opgrammar, systemColor, grammar, reason)
                self.textArea.append(convertTags(msg))
                self.mainwindow.chatlog.log(self.channel, msg)
                ttracker.removeTime(ttracker.getTime())

            if chum is self.mainwindow.profile():
                # are you next?
                msgbox = QtGui.QMessageBox()
                msgbox.setText(self.mainwindow.theme["convo/text/kickedmemo"])
                msgbox.setInformativeText("press 0k to rec0nnect or cancel to absc0nd")
                msgbox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
                ret = msgbox.exec_()
                if ret == QtGui.QMessageBox.Ok:
                    self.userlist.clear()
                    self.time = TimeTracker(curtime)
                    self.resetSlider(curtime)
                    self.mainwindow.joinChannel.emit(self.channel)
                    me = self.mainwindow.profile()
                    self.time.openCurrentTime()
                    msg = me.memoopenmsg(systemColor, self.time.getTime(), self.time.getGrammar(), self.mainwindow.theme["convo/text/openmemo"], self.channel)
                    self.textArea.append(convertTags(msg))
                    self.mainwindow.chatlog.log(self.channel, msg)
                elif ret == QtGui.QMessageBox.Cancel:
                    if self.parent():
                        i = self.parent().tabIndices[self.channel]
                        self.parent().tabClose(i)
                    else:
                        self.close()
            else:
                # i warned you about those stairs bro
                self.userlist.takeItem(self.userlist.row(c))
        elif update == "join":
            self.addUser(h)
            time = self.time.getTime()
            serverText = "PESTERCHUM:TIME>"+delta2txt(time, "server")
            self.messageSent.emit(serverText, self.title())
        elif update == "+o":
            if self.mainwindow.config.opvoiceMessages():
                chum = PesterProfile(h)
                if h == self.mainwindow.profile().handle:
                    chum = self.mainwindow.profile()
                    ttracker = self.time
                    curtime = self.time.getTime()
                elif self.times.has_key(h):
                    ttracker = self.times[h]
                else:
                    ttracker = TimeTracker(timedelta(0))
                opchum = PesterProfile(op)
                if self.times.has_key(op):
                    opgrammar = self.times[op].getGrammar()
                elif op == self.mainwindow.profile().handle:
                    opgrammar = self.time.getGrammar()
                else:
                    opgrammar = TimeGrammar("CURRENT", "C", "RIGHT NOW")
                msg = chum.memoopmsg(opchum, opgrammar, systemColor)
                self.textArea.append(convertTags(msg))
                self.mainwindow.chatlog.log(self.channel, msg)
            for c in chums:
                c.op = True
                icon = PesterIcon(self.mainwindow.theme["memos/op/icon"])
                c.setIcon(icon)
                if unicode(c.text()) == self.mainwindow.profile().handle:
                    self.userlist.optionsMenu.addAction(self.opAction)
                    self.userlist.optionsMenu.addAction(self.voiceAction)
                    self.userlist.optionsMenu.addAction(self.banuserAction)
                    self.optionsMenu.addMenu(self.chanModeMenu)
            self.sortUsers()
        elif update == "-o":
            self.mainwindow.channelNames.emit(self.channel)
            if self.mainwindow.config.opvoiceMessages():
                chum = PesterProfile(h)
                if h == self.mainwindow.profile().handle:
                    chum = self.mainwindow.profile()
                    ttracker = self.time
                    curtime = self.time.getTime()
                elif self.times.has_key(h):
                    ttracker = self.times[h]
                else:
                    ttracker = TimeTracker(timedelta(0))
                opchum = PesterProfile(op)
                if self.times.has_key(op):
                    opgrammar = self.times[op].getGrammar()
                elif op == self.mainwindow.profile().handle:
                    opgrammar = self.time.getGrammar()
                else:
                    opgrammar = TimeGrammar("CURRENT", "C", "RIGHT NOW")
                msg = chum.memodeopmsg(opchum, opgrammar, systemColor)
                self.textArea.append(convertTags(msg))
                self.mainwindow.chatlog.log(self.channel, msg)
            for c in chums:
                c.op = False
                if c.voice:
                    icon = PesterIcon(self.mainwindow.theme["memos/voice/icon"])
                    c.setIcon(icon)
                else:
                    icon = QtGui.QIcon()
                    c.setIcon(icon)
                if unicode(c.text()) == self.mainwindow.profile().handle:
                    self.userlist.optionsMenu.removeAction(self.opAction)
                    self.userlist.optionsMenu.removeAction(self.voiceAction)
                    self.userlist.optionsMenu.removeAction(self.banuserAction)
                    self.optionsMenu.removeAction(self.chanModeMenu.menuAction())
            self.sortUsers()
        elif update == "+v":
            if self.mainwindow.config.opvoiceMessages():
                chum = PesterProfile(h)
                if h == self.mainwindow.profile().handle:
                    chum = self.mainwindow.profile()
                    ttracker = self.time
                    curtime = self.time.getTime()
                elif self.times.has_key(h):
                    ttracker = self.times[h]
                else:
                    ttracker = TimeTracker(timedelta(0))
                opchum = PesterProfile(op)
                if self.times.has_key(op):
                    opgrammar = self.times[op].getGrammar()
                elif op == self.mainwindow.profile().handle:
                    opgrammar = self.time.getGrammar()
                else:
                    opgrammar = TimeGrammar("CURRENT", "C", "RIGHT NOW")
                msg = chum.memovoicemsg(opchum, opgrammar, systemColor)
                self.textArea.append(convertTags(msg))
                self.mainwindow.chatlog.log(self.channel, msg)
            for c in chums:
                c.voice = True
                if not c.op:
                    icon = PesterIcon(self.mainwindow.theme["memos/voice/icon"])
                    c.setIcon(icon)
            self.sortUsers()
        elif update == "-v":
            if self.mainwindow.config.opvoiceMessages():
                chum = PesterProfile(h)
                if h == self.mainwindow.profile().handle:
                    chum = self.mainwindow.profile()
                    ttracker = self.time
                    curtime = self.time.getTime()
                elif self.times.has_key(h):
                    ttracker = self.times[h]
                else:
                    ttracker = TimeTracker(timedelta(0))
                opchum = PesterProfile(op)
                if self.times.has_key(op):
                    opgrammar = self.times[op].getGrammar()
                elif op == self.mainwindow.profile().handle:
                    opgrammar = self.time.getGrammar()
                else:
                    opgrammar = TimeGrammar("CURRENT", "C", "RIGHT NOW")
                msg = chum.memodevoicemsg(opchum, opgrammar, systemColor)
                self.textArea.append(convertTags(msg))
                self.mainwindow.chatlog.log(self.channel, msg)
            for c in chums:
                c.voice = False
                if c.op:
                    icon = PesterIcon(self.mainwindow.theme["memos/op/icon"])
                    c.setIcon(icon)
                else:
                    icon = QtGui.QIcon()
                    c.setIcon(icon)
            self.sortUsers()
        elif c == self.channel and h == "" and update[0] in ["+","-"]:
            self.updateChanModes(update)

    @QtCore.pyqtSlot()
    def addChumSlot(self):
        if not self.userlist.currentItem():
            return
        currentChum = PesterProfile(unicode(self.userlist.currentItem().text()))
        self.mainwindow.addChum(currentChum)
    @QtCore.pyqtSlot()
    def banSelectedUser(self):
        if not self.userlist.currentItem():
            return
        currentHandle = unicode(self.userlist.currentItem().text())
        (reason, ok) = QtGui.QInputDialog.getText(self, "Ban User", "Enter the reason you are banning this user (optional):")
        if ok:
            self.mainwindow.kickUser.emit("%s:%s" % (currentHandle, reason), self.channel)
    @QtCore.pyqtSlot()
    def opSelectedUser(self):
        if not self.userlist.currentItem():
            return
        currentHandle = unicode(self.userlist.currentItem().text())
        self.mainwindow.setChannelMode.emit(self.channel, "+o", currentHandle)
    @QtCore.pyqtSlot()
    def voiceSelectedUser(self):
        if not self.userlist.currentItem():
            return
        currentHandle = unicode(self.userlist.currentItem().text())
        self.mainwindow.setChannelMode.emit(self.channel, "+v", currentHandle)
    def resetSlider(self, time, send=True):
        self.timeinput.setText(delta2txt(time))
        self.timeinput.setSlider()
        if send:
            self.sendtime()

    @QtCore.pyqtSlot()
    def openChumLogs(self):
        currentChum = self.channel
        self.mainwindow.chumList.pesterlogviewer = PesterLogViewer(currentChum, self.mainwindow.config, self.mainwindow.theme, self.mainwindow)
        self.connect(self.mainwindow.chumList.pesterlogviewer, QtCore.SIGNAL('rejected()'),
                     self.mainwindow.chumList, QtCore.SLOT('closeActiveLog()'))
        self.mainwindow.chumList.pesterlogviewer.show()
        self.mainwindow.chumList.pesterlogviewer.raise_()
        self.mainwindow.chumList.pesterlogviewer.activateWindow()

    @QtCore.pyqtSlot()
    def inviteChums(self):
        if not hasattr(self, 'invitechums'):
            self.invitechums = None
        if not self.invitechums:
            (chum, ok) = QtGui.QInputDialog.getText(self, "Invite to Chat", "Enter the chumhandle of the user you'd like to invite:")
            if ok:
                chum = unicode(chum)
                self.mainwindow.inviteChum.emit(chum, self.channel)
            self.invitechums = None

    @QtCore.pyqtSlot(bool)
    def hideChan(self, on):
        x = ["-","+"][on]
        self.mainwindow.setChannelMode.emit(self.channel, x+"s", "")
    @QtCore.pyqtSlot(bool)
    def inviteChan(self, on):
        x = ["-","+"][on]
        self.mainwindow.setChannelMode.emit(self.channel, x+"i", "")
    @QtCore.pyqtSlot(bool)
    def modChan(self, on):
        x = ["-","+"][on]
        self.mainwindow.setChannelMode.emit(self.channel, x+"m", "")

    @QtCore.pyqtSlot()
    def sendtime(self):
        me = self.mainwindow.profile()
        systemColor = QtGui.QColor(self.mainwindow.theme["memos/systemMsgColor"])
        time = txt2delta(self.timeinput.text())
        present = self.time.addTime(time)

        serverText = "PESTERCHUM:TIME>"+delta2txt(time, "server")
        self.messageSent.emit(serverText, self.title())
    @QtCore.pyqtSlot()
    def smashclock(self):
        me = self.mainwindow.profile()
        time = txt2delta(self.timeinput.text())
        removed = self.time.removeTime(time)
        if removed:
            grammar = self.time.getGrammarTime(time)
            systemColor = QtGui.QColor(self.mainwindow.theme["memos/systemMsgColor"])
            msg = me.memoclosemsg(systemColor, grammar, self.mainwindow.theme["convo/text/closememo"])
            self.textArea.append(convertTags(msg))
            self.mainwindow.chatlog.log(self.channel, msg)

        newtime = self.time.getTime()
        if newtime is None:
            newtime = timedelta(0)
            self.resetSlider(newtime, send=False)
        else:
            self.resetSlider(newtime)
    @QtCore.pyqtSlot()
    def prevtime(self):
        time = self.time.prevTime()
        self.time.setCurrent(time)
        self.resetSlider(time)
        self.textInput.setFocus()
    @QtCore.pyqtSlot()
    def nexttime(self):
        time = self.time.nextTime()
        self.time.setCurrent(time)
        self.resetSlider(time)
        self.textInput.setFocus()
    def closeEvent(self, event):
        self.mainwindow.waitingMessages.messageAnswered(self.channel)
        self.windowClosed.emit(self.title())

    windowClosed = QtCore.pyqtSignal(QtCore.QString)


timelist = ["0:00", "0:01", "0:02", "0:04", "0:06", "0:10", "0:14", "0:22", "0:30", "0:41", "1:00", "1:34", "2:16", "3:14", "4:13", "4:20", "5:25", "6:12", "7:30", "8:44", "10:25", "11:34", "14:13", "16:12", "17:44", "22:22", "25:10", "33:33", "42:00", "43:14", "50:00", "62:12", "75:00", "88:44", "100", "133", "143", "188", "200", "222", "250", "314", "333", "413", "420", "500", "600", "612", "888", "1000", "1025"]

timedlist = [timedelta(0), timedelta(0, 60), timedelta(0, 120), timedelta(0, 240), timedelta(0, 360), timedelta(0, 600), timedelta(0, 840), timedelta(0, 1320), timedelta(0, 1800), timedelta(0, 2460), timedelta(0, 3600), timedelta(0, 5640), timedelta(0, 8160), timedelta(0, 11640), timedelta(0, 15180), timedelta(0, 15600), timedelta(0, 19500), timedelta(0, 22320), timedelta(0, 27000), timedelta(0, 31440), timedelta(0, 37500), timedelta(0, 41640), timedelta(0, 51180), timedelta(0, 58320), timedelta(0, 63840), timedelta(0, 80520), timedelta(1, 4200), timedelta(1, 34380), timedelta(1, 64800), timedelta(1, 69240), timedelta(2, 7200), timedelta(2, 51120), timedelta(3, 10800), timedelta(3, 60240), timedelta(4, 14400), timedelta(5, 46800), timedelta(5, 82800), timedelta(7, 72000), timedelta(8, 28800), timedelta(9, 21600), timedelta(10, 36000), timedelta(13, 7200), timedelta(13, 75600), timedelta(17, 18000), timedelta(17, 43200), timedelta(20, 72000), timedelta(25), timedelta(25, 43200), timedelta(37), timedelta(41, 57600), timedelta(42, 61200)]
