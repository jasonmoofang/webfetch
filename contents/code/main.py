# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4.kdeui import *
from PyKDE4.kdecore import *
 

# DON'T LOOK!!!!
# Code is very ugly atm :P This was my first Python project so....

class Fetch(plasmascript.Applet):
    def __init__(self,parent,args=None):
        plasmascript.Applet.__init__(self,parent)
 
    def init(self):
        self.http = QHttp()
        #self.resize(500,600)
        self.setHasConfigurationInterface(True)
        self.setAspectRatioMode(Plasma.Square)
        self.site = 'kde.org'
        self.get = '/'
        htm = self.config().readEntry("html")
        if htm.isEmpty():
            htm = QString("No content to display. Will attempt sync when internet is available!")
        url = self.config().readEntry("url")
        if not url.isEmpty():
            temp = QUrl()
            temp.setUrl(url)
            self.useUrl(temp)
        self.webview = Plasma.WebView(self.applet)
        self.webview.setHtml(htm, self.getUrl())
        self.label = Plasma.Label(self.applet)
        self.label.setText("Syncing...")
        syncButton = Plasma.PushButton(self.applet)
        stylesheet = "background-color:#000000;\n"
        stylesheet += "color:#ffffff;"
        syncButton.setStyleSheet(stylesheet)
        syncButton.setText("Sync Now")
        self.layout = QGraphicsLinearLayout(Qt.Vertical, self.applet)
        self.layout.addItem(self.label)
        self.layout.setStretchFactor(self.label, 1)
        self.layout.addItem(syncButton)
        self.layout.setStretchFactor(syncButton, 1)
        self.layout.addItem(self.webview)
        self.layout.setStretchFactor(self.webview, 15)
        self.setLayout(self.layout)
        self.sync()
        timer = QTimer(self.applet)
        timer.start(3600000)
        QObject.connect(self.http, SIGNAL("done(bool)"), self.update)
        QObject.connect(timer, SIGNAL("timeout()"), self.sync)
        QObject.connect(syncButton, SIGNAL("clicked()"), self.sync)

    def showConfigurationInterface(self):
        dialog = KDialog()
        dialog.resize(500,100)
        dialog.setButtons(KDialog.ButtonCode(KDialog.Ok | KDialog.Cancel))
        layout = QVBoxLayout()
        urlLabel = QLabel(dialog)
        urlLabel.setText("Url of Site to Cache:")
        self.url = QLineEdit(dialog)
        self.url.setText(self.getUrl().url())
        layout.addWidget(urlLabel)
        layout.addWidget(self.url)
        main = QWidget(dialog)
        main.setLayout(layout)
        dialog.setMainWidget(main)
        QObject.connect(dialog, SIGNAL("okClicked()"), self.configChanged)
        dialog.exec_()

    def configChanged(self):
        url = QUrl()
        url.setUrl(self.url.text())
        self.useUrl(url)
        self.sync()
        self.config().writeEntry("url", self.url.text())

    def useUrl(self, url):
        self.site = url.host()
        self.get = url.path()
        if url.hasQuery():
            self.get += "?" + url.encodedQuery()

    def sync(self):
        self.label.setText("Syncing...")
        self.http.setHost(self.site)
        self.http.get(self.get)

    def getUrl(self):
        return KUrl("http://" + self.site + self.get)

    def update(self, b):
        if not b:
            stuff = self.http.readAll();
            self.config().writeEntry("html", stuff)
            self.webview.setHtml(QString(stuff), self.getUrl())
            self.label.setText("Synced at "+QTime.currentTime().toString())
        else:
            self.label.setText("Unable to sync!")
            print self.http.errorString();
 
def CreateApplet(parent):
    return Fetch(parent) 
