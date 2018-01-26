# -*- coding: utf-8 -*-
# based on inara plugin
import json
import time
import urllib2
import sys
import Tkinter as tk
import tkMessageBox
import requests
import myNotebook as nb
import datetime
import os, sys
from config import config
from os import listdir
from os.path import join

this = sys.modules[__name__]
this.s = None
this.prep = {}
this.apiendpoint = "http://forum.thewingedhussars.com/apps/api/"
this.isCredentialsPassed = False
this.apikey = ''
this.username = ''
this.lastSystemDocked = ''
this.lastStationDocked = ''
this.lastStationFactionDocked = ''
this.isDocked = False
this.missions = {}
this.logsChecked = False
this.version = 1.11;
this.pluginname = 'TWH'

def plugin_start():
    this.username = tk.StringVar(value=config.get("TWHUsername"))
    this.apikey = tk.StringVar(value=config.get("TWHApiKey"))
    this.isCredentialsPassed = False
    if checkCredentials(this.username.get(), this.apikey.get()):
        this.isCredentialsPassed = True
    return this.pluginname

def plugin_autoupdate():
    this.s = requests.Session()
    url = this.apiendpoint + "plugins/twh/version.json"
    r = this.s.get(url)
    try:
        version = json.loads(r.text.encode('utf-8'))
        if version[u'version'] > this.version:
            if tkMessageBox.askyesno('Dostępna jest nowa wersja wtyczki %s v%0.2f' % (this.pluginname, version[u'version']), "Posiadasz starszą wersję wtyczki %s: v%0.2f. Dostępna jest aktualizacja do wersji v%0.2f. Czy chcesz pobrać i zainstalować nową wersję?" % (this.pluginname, this.version, version[u'version'])):
                url = this.apiendpoint + "plugins/twh/load.py"
                r = this.s.get(url)
                pluginContent = r.text.encode('utf-8')
                currentPluginPath = __file__
                file = open(currentPluginPath, 'w')
                file.write(pluginContent)
                file.close();
                tkMessageBox.showinfo('Wtyczka %s została zaktualizowana' % this.pluginname, 'Wtyczka %s została zaktualizowana do najnowszej wersji v%0.2f. Należy ponownie uruchomić program.' % (this.pluginname, version[u'version']))
    except:
        updateInfo("Nie udało się pobrać informacji o wersji wtyczki!")


def plugin_app(parent):
    this.parent = parent
    label = tk.Label(parent, text="%s v%0.2f:" % (this.pluginname, this.version))
    this.status = tk.Label(parent, text="Nie podłączony", anchor=tk.W)
    if (this.isCredentialsPassed):
        updateInfo("Online")
    elif this.username.get():
        updateInfo("Nieprawidłowe dane uwierzytelniające API!")

    plugin_autoupdate();
    return (label, this.status)


def plugin_prefs(parent):
    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)

    username_label = nb.Label(frame, text="Nazwa użytkownika na forum The Winged Hussars")
    username_label.grid(padx=10, row=10, sticky=tk.W)

    username_entry = nb.Entry(frame, textvariable=this.username)
    username_entry.grid(padx=10, row=10, column=1, sticky=tk.EW)

    pass_label = nb.Label(frame, text="Klucz API wygenerowany w profilu forum")
    pass_label.grid(padx=10, row=12, sticky=tk.W)

    pass_entry = nb.Entry(frame, textvariable=this.apikey)
    pass_entry.grid(padx=10, row=12, column=1, sticky=tk.EW)

    return frame


# check credentials
def checkCredentials(username, apikey):
    data = {
        "username": username,
        "key": apikey,
        "version": this.version
    }
    url = this.apiendpoint+"CheckCredentials/Check"
    this.s = requests.Session()
    r = this.s.post(url, data=data)
    retobject = json.loads(r.text);
    return retobject['meta']['status'] == 200


# settings
def prefs_changed():
    if this.username.get() != config.get("TWHUsername") or this.apikey.get() != config.get("TWHApiKey") or not this.isCredentialsPassed:
        config.set("TWHUsername", this.username.get())
        config.set("TWHApiKey", this.apikey.get())
        this.isCredentialsPassed = checkCredentials(this.username.get(), this.apikey.get())
        updateInfo(this.isCredentialsPassed and "Online" or "Nieprawidłowe dane uwierzytelniające API!")


# events
def journal_entry(cmdr, is_beta, system, station, entry, state):
    events = ['FSDJump', 'Location', 'Rank', 'Progress', 'Materials', 'Loadout', 'Docked', 'MissionCompleted', 'RedeemVoucher', 'SellExplorationData', 'MarketSell']
    if not is_beta and this.isCredentialsPassed:
        if entry['event'] == 'Location' and entry['Docked']:
            this.lastSystemDocked = entry['StarSystem']
            this.lastStationDocked = entry['StationName']
        if entry['event'] == 'Docked':
            this.lastSystemDocked = entry['StarSystem']
            this.lastStationDocked = entry['StationName']
            this.lastStationFactionDocked = entry['StationFaction']
        if entry['event'] == 'MissionAccepted':
            entry['SourceSystem'] = this.lastSystemDocked
            entry['SourceStation'] = this.lastStationDocked
            entry['StationFaction'] = this.lastStationFactionDocked
            this.missions[entry['MissionID']] = entry
        if entry['event'] == 'RedeemVoucher' or entry['event'] == 'SellExplorationData' or entry['event'] == 'MarketSell':
            entry['SourceSystem'] = this.lastSystemDocked
            entry['SourceStation'] = this.lastStationDocked
            entry['StationFaction'] = this.lastStationFactionDocked
        if entry['event'] == 'MissionFailed' or entry['event'] == 'MissionAbandoned':
            if this.missions[entry['MissionID']]:
                del this.missions[entry['MissionID']]
        if entry['event'] == 'MissionCompleted':
            entry['StationFaction'] = this.lastStationFactionDocked
            if this.logsChecked:
                this.checkLogsForMission
            if this.missions[entry['MissionID']]:
                entry['source'] = this.missions[entry['MissionID']]
                del this.missions[entry['MissionID']]
        if entry['event'] in events:
            post = {
                "username": this.username.get(),
                "key": this.apikey.get(),
                "version": this.version,
                "data": json.dumps(entry)
            }
            url = this.apiendpoint + "CommandersLog/Import"
            r = this.s.post(url, data=post)
            updateInfo("Dziennik został zaktualizowany")

def checkLogsForMission():
    # Retrieve information about missions from last 10 logfiles
    currentdir = config.get('journaldir') or config.default_journal_dir
    try:
        logfiles = sorted([x for x in listdir(currentdir) if x.startswith('Journal') and x.endswith('.log')],
                          key=lambda x: x.split('.')[1:])
        logsLength = len(logfiles)
        if logsLength > 10:
            logsLength = 10
        if logsLength > 0:
            currentSystem = '';
            currentStation = '';
            currentStationFaction = '';
            for x in range(-logsLength, 0):
                logfile = logfiles and join(currentdir, logfiles[x]) or None
                if logfile != None:
                    with open(logfile, "r") as log:
                        for line in log:
                            try:
                                entry = json.loads(line)
                                if entry['event'] == 'Location' and entry['Docked']:
                                    currentSystem = entry['StarSystem']
                                    currentStation = entry['StationName']
                                if entry['event'] == 'Docked':
                                    currentSystem = entry['StarSystem']
                                    currentStation = entry['StationName']
                                    currentStationFaction = entry['StationFaction']
                                if entry['event'] == 'MissionAccepted':
                                    entry['SourceSystem'] = currentSystem
                                    entry['SourceStation'] = currentStation
                                    this.missions[entry['MissionID']] = entry
                                if entry['event'] == 'MissionFailed' or entry['event'] == 'MissionCompleted' or entry['event'] == 'MissionAbandoned':
                                    del this.missions[entry['MissionID']]
                            except:
                                """Nothing"""
            if len(this.lastSystemDocked) == 0:
                this.lastSystemDocked = currentSystem
                this.lastStationDocked = currentStation
                this.lastStationFactionDocked = currentStationFaction
            this.logsChecked = True
        return True
    except:
        return False

# commander data
def cmdr_data(data, is_beta):
    if not is_beta and this.isCredentialsPassed:
        if len(this.lastSystemDocked) == 0 and data['commander']['docked']:
            this.lastSystemDocked = data['lastSystem']['name']
            this.lastStationDocked = data['lastStarport']['name']
            this.lastStationFactionDocked = data['lastStarport']['minorfaction']
        if not this.logsChecked:
            this.checkLogsForMission()
        cmdr_data.last = data
        post = {
            "username": this.username.get(),
            "key": this.apikey.get(),
            "data": json.dumps(data)
        }
        url = this.apiendpoint + "CommandersData/Import"
        r = this.s.post(url, data=post)
        updateInfo("Dane komandora zostały zaktualizowane")

def updateInfo(msg):
    this.status['text'] = datetime.datetime.now().strftime("%H:%M") + " - " + msg
