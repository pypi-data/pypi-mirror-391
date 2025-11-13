"""Tabbed GUI for starting/stopping/monitoring programs.
"""
__version__ = 'v2.2.0 2025-11-12'# Added: Restart.
#TODO: xdg_open does not launch if other editors not running. 

import sys, os, time, subprocess, argparse, threading, glob
from functools import partial
from importlib import import_module

from qtpy import QtWidgets as QW, QtGui, QtCore

from . import helpers as H
from . import detachable_tabs

#``````````````````Constants``````````````````````````````````````````````````
ManCmds =       ['Check', 'Start', 'Stop', 'Restart', 'Command']
AllManCmds = ['Check All','Start All','Stop All', 'Edit', 'Delete',
                'Condense', 'Uncondense']#, 'Exit All']
Col = {'Applications':0, '_status_':1, 'response':2}
FilePrefix = 'proc'
#``````````````````Helpers````````````````````````````````````````````````````
def select_files_interactively(directory, title=f'Select {FilePrefix}*.py files'):
    dialog = QW.QFileDialog()
    dialog.setFileMode( QW.QFileDialog.FileMode() )
    ffilter = f'procman ({FilePrefix}*.py)'
    files = dialog.getOpenFileNames( None, title, directory, ffilter)[0]
    return files

def create_folderMap():
    # create map of {folder1: [file1,...], folder2...} from pargs.files
    folders = {}
    if Window.pargs.configDir is None:
        files = [os.path.abspath(i) for i in Window.pargs.files]
    else:
        absfolder = os.path.abspath(Window.pargs.configDir)+'/'
        if Window.pargs.interactive:
            if len(Window.pargs.files) == 0:
                files = select_files_interactively(absfolder)
            else:
                files = [absfolder+i for i in Window.pargs.files]
        else:
            if len(Window.pargs.files) == 0:
                files = glob.glob(f'{absfolder}proc*.py')
            else:
                files = [absfolder+i for i in Window.pargs.files]
    for f in files:
        folder,tail = os.path.split(f)
        if not (tail.startswith(FilePrefix) and tail.endswith('.py')):
            H.printe(f'Config file should have prefix {FilePrefix} and suffix ".py"')
            sys.exit(1)
        if folder not in folders:
            folders[folder] = []
        folders[folder].append(tail)

    # sort the file lists
    for folder in folders:
        folders[folder].sort()
    return folders

def launch_default_editor(configFile):
    cmd = f'xdg-open {configFile}'
    H.printi(f'Launching editor: {cmd}')
    subprocess.call(cmd.split())

def is_process_running(cmdstart):
    try:
        subprocess.check_output(["pgrep", '-f', cmdstart])
        return True
    except subprocess.CalledProcessError:
        return False

def setButtonStyleSheet(parent):
    parent.setStyleSheet("QPushButton{"
            #"background-color: lightBlue;"
            "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,"
                "stop: 0 white, stop: 1 lightBlue);"
            #'border: 2px solid blue;'
            "border-style: solid;"
            "border-color: Grey;"
            "border-width: 2px;"
            f"font-size: {Window.pargs.rowHeight-5}px;"
            "border-radius: 10px;}"
            #"font-weight: bold;"# no effect
            'QPushButton::pressed{background-color:pink;}'
        )#{+ButtonStyleSheet)    

class myPushButton(QW.QPushButton):
    """Custom pushbutton""" 
    def __init__(self, text, manName='?', buttons=[]):
        super().__init__()
        self.setText(text)
        self.buttons = buttons
        self.manName = manName
        self.clicked.connect(self.buttonClicked)

    def buttonClicked(self):
        buttonText = self.text()
        if len(self.buttons) != 0:
            dlg = myDialog(self, self.manName, self.buttons)
            r = dlg.exec()
            return
        if self.manName == '':
            return
        #print(f'Executing manAction{self.manName, buttonText}')
        if self.manName == 'All':
            current_mytable().tableWideAction(buttonText)
        else:
             current_mytable().manAction(self.manName, buttonText)

class myDialog(QW.QDialog):
    def __init__(self, parent, title, buttons):
        super().__init__(parent)

        self.setWindowTitle(title)
        layout = QW.QVBoxLayout(self)
        for btnTxt in buttons:
            btn = myPushButton(btnTxt, title)
            btn.clicked.connect(self.accept)
            layout.addWidget(btn)
        self.setLayout(layout)
        
#``````````````````Table Widget```````````````````````````````````````````````
def current_mytable():
    return Window.tabWidget.currentWidget()
class MyTable(QW.QTableWidget):
    def __init__(self, folder, fname, tabName):
        super().__init__()
        mname = fname[:-3]
        H.printv(f'importing {mname}')
        try:
            module = import_module(mname)
        except SyntaxError as e:
            H.printe(f'Syntax Error in {fname}: {e}')
            sys.exit(1)
        H.printv(f'imported {mname} {module.__version__}')
        self.startup = module.startup
        self.configFile = folder+'/'+fname
        self.setColumnCount(len(Col))
        self.setHorizontalHeaderLabels(Col.keys())
        self.verticalHeader().setMinimumSectionSize(Window.pargs.rowHeight)
        self.manRow = {}
        fontButton = QtGui.QFont('Arial', Window.pargs.rowHeight-10)
        self.setFont(fontButton)
        setButtonStyleSheet(self)

        try:    title = module.title
        except: title = 'Applications'

        # Wide button for for tab-wide commands
        rowPosition=0
        self._insertRow(rowPosition)
        self.setSpan(rowPosition,0,1,2)
        item = myPushButton(title, 'All', AllManCmds)
        item.setToolTip('Commands for all programs in this page')
        self.setCellWidget(rowPosition, Col['Applications'], item)

        # Set up all rows 
        for manName,props in self.startup.items():
            rowPosition = self.rowCount()
            self._insertRow(rowPosition)
            self.manRow[manName] = [rowPosition,'']# row, last command
            button = myPushButton(manName, manName, buttons=ManCmds)
            try:    button.setToolTip(props['help'])
            except: pass
            self.setCellWidget(rowPosition, Col['Applications'], button)
            itemStatus = QW.QTableWidgetItem('?')
            self.setItem(rowPosition, Col['_status_'], itemStatus)
            itemResponse = QW.QTableWidgetItem('')
            itemResponse.setFont(QtGui.QFont('Arial',10))
            self.setItem(rowPosition, Col['response'], itemResponse)

        # Set up headers
        self.resizeColumnsToContents()
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        if Window.pargs.condensed:
            self.set_headersVisibility(False)

    def _insertRow(self, rowPosition):
        self.insertRow(rowPosition)
        self.setRowHeight(rowPosition, 1)  

    def manAction(self, manName:str, cmd:str):
        # Execute action
        #print(f'manAction {manName,cmd}')
        rowPosition,lastCommand = self.manRow[manName]
        startup = self.startup
        cmdstart = startup[manName]['cmd']
        process = startup[manName].get('process', f'{cmdstart}')
        #print(f"pos: {rowPosition},{Col['response']}")

        if cmd == 'Check':
            H.printvv(f'checking process {process} ')
            status = ['stopped','started'][is_process_running(process)]
            item = self.item(rowPosition,Col['_status_'])
            prevStatus = item.text()
            if status != prevStatus:
                if prevStatus[:4] in ['stop','star','?']:
                    color = 'lightGreen' if 'started' in status else 'pink'
                    item.setBackground(QtGui.QColor(color))
                    item.setText(status)

        elif cmd == 'Start':
            self.item(rowPosition, Col['response']).setText('')
            if is_process_running(process):
                txt = f'Is already running: {manName}'
                self.item(rowPosition, Col['response']).setText(txt)
                return
            H.printv(f'starting {manName}')
            item = self.item(rowPosition, Col['_status_'])
            item.setText('starting...')
            item.setBackground(QtGui.QColor('lightYellow'))
            path = startup[manName].get('cd')
            H.printi('Executing commands:')
            if path:
                path = path.strip()
                expandedPath = os.path.expanduser(path)
                try:
                    os.chdir(expandedPath)
                except Exception as e:
                    txt = f'ERR: in chdir: {e}'
                    self.item(rowPosition, Col['response']).setText(txt)
                    return
                print(f'cd {os.getcwd()}')
            print(cmdstart)
            cmdlist = os.path.expanduser(cmdstart)
            shell = startup[manName].get('shell',False)
            if shell is False:
                cmdlist = cmdlist.split()
            H.printv(f'popen: {cmdlist}, shell:{shell}')
            try:
                process = subprocess.Popen(cmdlist, shell=shell, #close_fds=True,# env=my_env,
                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                time.sleep(0.1)
                if process.poll() is not None:
                    #print('process did not start in 0.1s')
                    item.setText('failed')
                    txt = f'Failed to execute {cmdstart}'
                    self.item(rowPosition, Col['response']).setText(txt)
                    return
            except Exception as e:
                H.printv(f'Exception: {e}') 
                self.item(rowPosition, Col['response']).setText(str(e))
                return

        elif cmd == 'Stop':
            status = self.item(rowPosition, Col['_status_']).text()
            if status != 'started':
                self.item(rowPosition, Col['response']).setText('not running')
                return
            self.item(rowPosition, Col['response']).setText('')
            H.printv(f'stopping {manName}')
            item = self.item(rowPosition, Col['_status_'])
            item.setText('stopping...')
            item.setBackground(QtGui.QColor('lightYellow'))
            cmdString = f'pkill -f "{process}"'
            H.printi(f'Executing:\n{cmdString}')
            os.system(cmdString)
            time.sleep(0.1)
            self.manAction(manName, ManCmds.index('Check'))

        elif cmd == 'Restart':
            self.manAction(manName, 'Stop')
            time.sleep(1.)
            self.manAction(manName, 'Start')

        elif cmd == 'Command':
            try:
                cd = startup[manName]['cd']
                cmdString = f'cd {cd}; {cmdstart}'
            except Exception as e:
                cmdString = cmdstart
            #print(f'Command in row {rowPosition}:\n{cmdString}')
            self.item(rowPosition, Col['response']).setText(cmdString)
        lastCommand = cmd

    def set_headersVisibility(self, visible:bool):
        #print(f'set_headersVisibility {visible}')
        self.horizontalHeader().setVisible(visible)
        self.verticalHeader().setVisible(visible)

    def tableWideAction(self, cmd:str):
        # Execute table-wide action
        if cmd == 'Edit':
            launch_default_editor(self.configFile)
        elif cmd == 'Delete':
            idx = Window.tabWidget.currentIndex()
            tabtext = Window.tabWidget.tabText(idx)
            H.printi(f'Deleting tab {idx,tabtext}')
            del Window.tableWidgets[tabtext]
            Window.tabWidget.removeTab(idx)
            self.deleteLater()# it is important to properly delete the associated widget
        elif cmd == 'Condense':
            self.set_headersVisibility(False)
        elif cmd == 'Uncondense':
            self.set_headersVisibility(True)
        elif cmd == 'Exit All':
            self.exit_all()
        else:# Delegate command to managers
            for manName in self.startup:
                cmd = cmd.split()[0]# use first word of the command
                self.manAction(manName, cmd)

#``````````````````Main Window````````````````````````````````````````````````
class Window(QW.QMainWindow):# it may sense to subclass it from QW.QMainWindow
    pargs = None
    tableWidgets = {}
    timer = QtCore.QTimer()

    def __init__(self):
        super().__init__()
        H.Verbose = Window.pargs.verbose
        folders = create_folderMap()
        if len(folders) == 0:
            sys.exit(1)
        H.printi(f'Configuration files: {folders}')
        self.setWindowTitle('procman')

        # Create tabWidget
        Window.tabWidget = detachable_tabs.DetachableTabWidget()
        Window.tabWidget.currentChanged.connect(periodicCheck)
        self.setCentralWidget(Window.tabWidget)
        H.printv(f'tabWidget created')

        # Add tables, configured from files, to tabs
        for folder,files in folders.items():
            sys.path.append(folder)
            for fname in files:
                tabName = fname[len(FilePrefix):-3]
                mytable = MyTable(folder, fname, tabName)
                Window.tableWidgets[tabName] = mytable
                #print(f'Adding tab: {fname}')
                Window.tabWidget.addTab(mytable, tabName)

        # Adjust window width to 2 columns of the current table
        ctable = current_mytable()
        w = [ctable.columnWidth(i) for i in range(2)]
        h = ctable.rowCount() * Window.pargs.rowHeight + 80
        self.resize(sum(w)+40, h)

        # Update tables and set up periodic check
        periodicCheck()
        if Window.pargs.interval != 0.:
            Window.timer.timeout.connect(periodicCheck)
            Window.timer.setInterval(int(Window.pargs.interval*1000.))
            Window.timer.start()

def periodicCheck():
    # execute tableWideAction on current tab
    current_mytable().tableWideAction('Check')
    # execute tableWideAction on all detached tabs
    for tabName,mytable in Window.tableWidgets.items():
        detached  = tabName in Window.tabWidget.detachedTabs
        #print(f'periodic for {tabName,detached}')
        if detached:
            mytable.tableWideAction('Check')

