############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
################################################################################
# This file contains classes working with cell helper widgets, i.e. toolbar,
# resizer, etc.:
#   QCellWidget
#   QCellToolBar
################################################################################
from PyQt4 import QtCore, QtGui
import datetime
import os
from core import system
import cell_rc
import spreadsheet_controller
import analogy_api

################################################################################

class QCellWidget(QtGui.QWidget):
    """
    QCellWidget is the base cell class. All types of spreadsheet cells
    should inherit from this.
    
    """

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        """ QCellWidget(parent: QWidget) -> QCellWidget
        Instantiate the cell and helper properties
        
        """
        QtGui.QWidget.__init__(self, parent, flags)
        self._historyImages = []
        self._player = QtGui.QLabel(self.parent())
        self._player.setAutoFillBackground(True)
        self._player.setFocusPolicy(QtCore.Qt.NoFocus)
        self._player.setScaledContents(True)
        self._playerTimer = QtCore.QTimer()        
        self._playerTimer.setSingleShot(True)
        self._currentFrame = 0
        self._playing = False
        self._capturingEnabled = False
        self.connect(self._playerTimer,
                     QtCore.SIGNAL('timeout()'),
                     self.playNextFrame)

    def setAnimationEnabled(self, enabled):
        """ setAnimationEnabled(enabled: bool) -> None
        
        """
        self._capturingEnabled = enabled
        if not enabled:
            self.clearHistory()
        
    def saveToPNG(self, filename):
        """ saveToPNG(filename: str) -> None        
        Abtract function for saving the current widget contents to an
        image file
        
        """
        print 'saveToPNG() is unimplemented by the inherited cell'

    def saveToHistory(self):
        """ saveToHistory() -> None
        Save the current contents to the history
        
        """
        # Generate filename
        current = datetime.datetime.now()
        tmpDir = system.temporary_directory()
        fn = (tmpDir + "hist_" +
              current.strftime("%Y_%m_%d__%H_%M_%S") +
              "_" + str(current.microsecond)+".png")
        if self.saveToPNG(fn):
            self._historyImages.append(fn)

    def clearHistory(self):
        """ clearHistory() -> None
        Clear all history files
        
        """
        for fn in self._historyImages:
            os.remove(fn)
        self._historyImages = []

    def deleteLater(self):
        """ deleteLater() -> None        
        Make sure to clear history and delete the widget
        
        """        
        self.clearHistory()
        QtGui.QWidget.deleteLater(self)

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple)
        Make sure to capture to history
        
        """
        # Capture window into history for playback
        if self._capturingEnabled:
            self.saveToHistory()

    def resizeEvent(self, e):
        """ resizeEvent(e: QEvent) -> None
        Re-adjust the player widget
        
        """
        QtGui.QWidget.resizeEvent(self, e)

        if self._player.isVisible():
            self._player.setGeometry(self.geometry())

    def setPlayerFrame(self, frame):
        """ setPlayerFrame(frame: int) -> None
        Set the player to display a particular frame number
        
        """
        if frame>=len(self._historyImages):
            frame = frame % len(self._historyImages)
        if frame>=len(self._historyImages):
            return
        self._player.setPixmap(QtGui.QPixmap(self._historyImages[frame]))

    def startPlayer(self):
        """ startPlayer() -> None
        Adjust the size of the player to the cell and show it
        
        """
        if not self._capturingEnabled:
            return
        self._player.setParent(self.parent())
        self._player.setGeometry(self.geometry())
        self._player.raise_()
        self._currentFrame = -1
        self.playNextFrame()
        self._player.show()
        self._playing = True
        
    def stopPlayer(self):
        """ startPlayer() -> None
        Adjust the size of the player to the cell and show it
        
        """
        if not self._capturingEnabled:
            return
        self._playerTimer.stop()
        self._player.hide()
        self._playing = False

    def showNextFrame(self):
        """ showNextFrame() -> None
        Display the next frame in the history
        
        """
        self._currentFrame += 1
        if self._currentFrame>=len(self._historyImages):
            self._currentFrame = 0
        self.setPlayerFrame(self._currentFrame)
        
    def playNextFrame(self):
        """ playNextFrame() -> None        
        Display the next frame in the history and start the timer for
        the frame after
        
        """
        self.showNextFrame()
        self._playerTimer.start(100)

    def grabWindowPixmap(self):
        """ grabWindowPixmap() -> QPixmap
        Widget special grabbing function
        
        """
        return QtGui.QPixmap.grabWidget(self)
        
################################################################################

class QCellToolBar(QtGui.QToolBar):
    """
    CellToolBar is inherited from QToolBar with some functionalities
    for interacting with CellHelpers
    
    """
    def __init__(self, sheet):
        """ CellToolBar(sheet: SpreadsheetSheet) -> CellToolBar        
        Initialize the cell toolbar by calling the user-defined
        toolbar construction function
        
        """
        QtGui.QToolBar.__init__(self,sheet)
        self.setAutoFillBackground(True)
        self.sheet = sheet
        self.row = -1
        self.col = -1
        self.createToolBar()

    def addAnimationButtons(self):
        """ addAnimationButtons() -> None
        
        """
        self.appendAction(QCellToolBarCaptureToHistory(self))
        self.appendAction(QCellToolBarPlayHistory(self))
        self.appendAction(QCellToolBarClearHistory(self))
            
    def createToolBar(self):
        """ createToolBar() -> None        
        A user-defined method for customizing the toolbar. This is
        going to be an empty method here for inherited classes to
        override.
        
        """
        pass

    def snapTo(self, row, col):
        """ snapTo(row, col) -> None
        Assign which row and column the toolbar should be snapped to
        
        """
        self.row = row
        self.col = col
        self.updateToolBar()

    def adjustPosition(self, rect):
        """ adjustPosition(rect: QRect) -> None
        Adjust the position of the toolbar to be top-left
        
        """
        self.adjustSize()
        p = self.parent().mapFromGlobal(rect.topLeft())
        self.move(p.x(), p.y())

    def updateToolBar(self):
        """ updateToolBar() -> None        
        This will get called when the toolbar widgets need to have
        their status updated. It sends out needUpdateStatus signal
        to let the widget have a change to update their own status
        
        """
        cellWidget = self.sheet.getCell(self.row, self.col)
        for action in self.actions():
            action.emit(QtCore.SIGNAL('needUpdateStatus'),
                        (self.sheet, self.row, self.col, cellWidget))

    def connectAction(self, action, widget):
        """ connectAction(action: QAction, widget: QWidget) -> None
        Connect actions to special slots of a widget
        
        """
        if hasattr(widget, 'updateStatus'):
            self.connect(action, QtCore.SIGNAL('needUpdateStatus'),
                         widget.updateStatus)
        if hasattr(widget, 'triggeredSlot'):
            self.connect(action, QtCore.SIGNAL('triggered()'),
                         widget.triggeredSlot)
        if hasattr(widget, 'toggledSlot'):
            self.connect(action, QtCore.SIGNAL('toggled(bool)'),
                         widget.toggledSlot)

    def appendAction(self, action):
        """ appendAction(action: QAction) -> QAction
        Setup and add action to the tool bar
        
        """
        action.toolBar = self
        self.addAction(action)
        self.connectAction(action, action)
        return action

    def appendWidget(self, widget):
        """ appendWidget(widget: QWidget) -> QAction
        Setup the widget as an action and add it to the tool bar

        """
        action = self.addWidget(widget)
        widget.toolBar = self
        action.toolBar = self
        self.connectAction(action, widget)
        return action

    def getSnappedWidget(self):
        """ getSnappedWidget() -> QWidget
        Return the widget being snapped by the toolbar
        
        """
        if self.row>=0 and self.col>=0:
            return self.sheet.getCell(self.row, self.col)
        else:
            return None

class QCellToolBarCaptureToHistory(QtGui.QAction):
    """
    QCellToolBarCaptureToHistory is the action to capture the
    underlying widget to history for play back. The cell type must
    support function saveToPNG(filename)
    
    """
    def __init__(self, parent=None):
        """ QCellToolBarCaptureToHistory(parent: QWidget)
                                         -> QCellToolBarCaptureToHistory
        Setup the image, status tip, etc. of the action
        
        """
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/camera_mount.png"),
                               "&Capture image to history",
                               parent)
        self.setStatusTip("Capture the cell contents to the history for "
                          "playback later")

    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        self.toolBar.hide()
        cellWidget.saveToHistory()
        self.toolBar.updateToolBar()
        self.toolBar.show()
        
################################################################################
        
class QCellToolBarPlayHistory(QtGui.QAction):
    """
    QCellToolBarPlayHistory is the action to play the history as an
    animation
    
    """
    def __init__(self, parent=None):
        """ QCellToolBarPlayHistory(parent: QWidget)
                                    -> QCellToolBarPlayHistory
        Setup the image, status tip, etc. of the action
        
        """
        self.icons = [QtGui.QIcon(":/images/player_play.png"),
                      QtGui.QIcon(":/images/player_pause.png")]
        self.toolTips = ["&Play the history",
                         "Pa&use the history playback"]
        self.statusTips = ["Playback all image files kept in the history",
                           "Pause the playback"]
        QtGui.QAction.__init__(self, self.icons[0], self.toolTips[0], parent)
        self.setStatusTip(self.statusTips[0])
        self.status = 0

    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        if self.status==0:            
            cellWidget.startPlayer()
        else:
            cellWidget.stopPlayer()
        self.toolBar.updateToolBar()

    def updateStatus(self, info):
        """ updateStatus(info: tuple) -> None
        Updates the status of the button based on the input info
        
        """
        (sheet, row, col, cellWidget) = info
        if cellWidget:
            newStatus = int(cellWidget._playing)
            if newStatus!=self.status:
                self.status = newStatus
                self.setIcon(self.icons[self.status])
                self.setToolTip(self.toolTips[self.status])
                self.setStatusTip(self.statusTips[self.status])
            self.setEnabled(len(cellWidget._historyImages)>0)                

################################################################################
            
class QCellToolBarClearHistory(QtGui.QAction):
    """
    QCellToolBarClearHistory is the action to reset cell history
    
    """
    def __init__(self, parent=None):
        """ QCellToolBarClearHistory(parent: QWidget)
                                     -> QCellToolBarClearHistory
        Setup the image, status tip, etc. of the action
        
        """
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/noatunloopsong.png"),
                               "&Clear this cell history",
                               parent)
        self.setStatusTip("Clear the cell history and its temporary "
                          "image files on disk")        
        
    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        cellWidget.clearHistory()
        self.toolBar.updateToolBar()
        
    def updateStatus(self, info):
        """ updateStatus(info: tuple) -> None
        Updates the status of the button based on the input info
        
        """
        (sheet, row, col, cellWidget) = info
        if cellWidget:
            self.setEnabled((len(cellWidget._historyImages)>0
                             and cellWidget._playing==False))

################################################################################

class QCellContainer(QtGui.QWidget):
    """ QCellContainer is a simple QWidget containing the actual cell
    widget as a child. This also acts as a sentinel protecting the
    actual cell widget from being destroyed by sheet widgets
    (e.g. QTableWidget) where they take control of the cell widget.
    
    """
    def __init__(self, widget=None, parent=None):
        """ QCellContainer(parent: QWidget) -> QCellContainer
        Create an empty container
        
        """
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        self.setLayout(layout)
        self.containedWidget = None
        self.setWidget(widget)
        self.toolBar = None

    def setWidget(self, widget):
        """ setWidget(widget: QWidget) -> None
        Set the contained widget of this container
        
        """
        if widget!=self.containedWidget:
            if self.containedWidget:
                self.layout().removeWidget(self.containedWidget)
                self.containedWidget.deleteLater()
                self.toolBar = None
            if widget:
                widget.setParent(self)
                self.layout().addWidget(widget)
                widget.show()
            self.containedWidget = widget

    def widget(self):
        """ widget() -> QWidget
        Return the contained widget
        
        """
        return self.containedWidget

    def takeWidget(self):
        """ widget() -> QWidget
        Take the contained widget out without deleting
        
        """
        widget = self.containedWidget
        if self.containedWidget:
            self.layout().removeWidget(self.containedWidget)
            self.containedWidget.setParent(None)
            self.containedWidget = None
        self.toolBar = None
        return widget

################################################################################

class QCellPresenter(QtGui.QLabel):
    """
    QCellPresenter represents a cell in the Editing Mode. It has an
    info bar on top and control dragable icons on the bottom
    
    """
    def __init__(self, parent=None):
        """ QCellPresenter(parent: QWidget) -> QCellPresenter
        Create the layout of the widget
        
        """        
        QtGui.QLabel.__init__(self, parent)        
        self.setAutoFillBackground(True)
        self.setScaledContents(True)
        self.setMargin(0)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.cellWidget = None

        layout = QtGui.QGridLayout(self)
        layout.setSpacing(2)
        layout.setMargin(self.margin())
        layout.setRowStretch(1, 1)
        self.setLayout(layout)
        
        self.info = QPipelineInfo()
        layout.addWidget(self.info, 0, 0, 1, 2)        

        self.manipulator = QCellManipulator()
        layout.addWidget(self.manipulator, 1, 0, 1, 2)

    def assignCellWidget(self, cellWidget):
        """ updateFromCellWidget(cellWidget: QWidget) -> None
        Assign a cell widget to this presenter
        
        """
        self.cellWidget = cellWidget
        if cellWidget:
            if hasattr(cellWidget, 'grabWindowPixmap'):
                bgPixmap = cellWidget.grabWindowPixmap()
            else:
                bgPixmap = QtGui.QPixmap.grabWidget(cellWidget)
            self.info.show()
        else:
            self.info.hide()
            bgPixmap = QtGui.QPixmap.grabWidget(self)
        painter = QtGui.QPainter(bgPixmap)
        painter.fillRect(bgPixmap.rect(),
                         QtGui.QBrush(QtGui.QColor(175, 198, 229, 196)))
        painter.end()
        self.setPixmap(bgPixmap)

    def assignCell(self, sheet, row, col):
        """ assignCell(sheet: Sheet, row: int, col: int) -> None
        Assign a sheet cell to the presenter
        
        """
        self.manipulator.assignCell(sheet, row, col)
        self.assignCellWidget(sheet.getCell(row, col))
        info = sheet.getCellPipelineInfo(row, col)
        self.info.updateInfo(info)
        
    def releaseCellWidget(self):
        """ releaseCellWidget() -> QWidget
        Return the ownership of self.cellWidget to the caller
        
        """
        cellWidget = self.cellWidget
        self.assignCellWidget(None)
        self.manipulator.assignCell(None, -1, -1)
        if cellWidget:
            cellWidget.setParent(None)
        return cellWidget

################################################################################

class QInfoLineEdit(QtGui.QLineEdit):
    """
    QInfoLineEdit is wrapper for a transparent, un-frame, read-only
    line edit
    
    """
    def __init__(self, parent=None):
        """ QInfoLineEdit(parent: QWidget) -> QInfoLineEdit
        Initialize the line edit
        
        """
        QtGui.QLineEdit.__init__(self, parent)
        self.setReadOnly(True)
        self.setFrame(False)
        pal = QtGui.QPalette(self.palette())
        pal.setBrush(QtGui.QPalette.Base,
                     QtGui.QBrush(QtCore.Qt.NoBrush))
        self.setPalette(pal)


class QInfoLabel(QtGui.QLabel):
    """
    QInfoLabel is wrapper for a transparent, bolded label
    
    """
    def __init__(self, text='', parent=None):
        """ QInfoLabel(text: str, parent: QWidget) -> QInfoLabel
        Initialize the line edit
        
        """
        QtGui.QLabel.__init__(self, text, parent)
        font = QtGui.QFont(self.font())
        font.setBold(True)
        self.setFont(font)

################################################################################
    
class QPipelineInfo(QtGui.QFrame):
    """
    QPipelineInfo displays information about the executed pipeline of
    a cell. It has 3 static lines: Vistrail name, (pipeline name,
    pipeline id) and the cell type
    
    """
    def __init__(self, parent=None):
        """ QPipelineInfo(parent: QWidget) -> None
        Create the 3 information lines
        
        """
        QtGui.QFrame.__init__(self, parent)
        self.setAutoFillBackground(True)
        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)

        pal = QtGui.QPalette(self.palette())
        color = QtGui.QColor(pal.brush(QtGui.QPalette.Base).color())
        color.setAlpha(196)
        pal.setBrush(QtGui.QPalette.Base, QtGui.QBrush(color))
        self.setPalette(pal)
        
        topLayout = QtGui.QVBoxLayout(self)
        topLayout.setSpacing(0)
        topLayout.setMargin(0)
        self.setLayout(topLayout)

        hLine = QtGui.QFrame()
        hLine.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Plain)
        hLine.setFixedHeight(1)
        topLayout.addWidget(hLine)

        layout = QtGui.QGridLayout()
        layout.setSpacing(2)
        layout.setMargin(2)
        topLayout.addLayout(layout)

        self.edits = []
        texts = ['Vistrail', 'Index', 'Created by']
        for i in range(len(texts)):
            label = QInfoLabel(texts[i])
            layout.addWidget(label, i, 0, 1, 1)
            edit = QInfoLineEdit()
            self.edits.append(edit)
            layout.addWidget(edit, i, 1, 1, 1)

        topLayout.addStretch()
        hLine = QtGui.QFrame()
        hLine.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Plain)
        hLine.setFixedHeight(1)
        topLayout.addWidget(hLine)

    def updateInfo(self, info):
        """ updateInfo(info: (dict, pid)) -> None
        Update the information of a pipeline info
        
        """
        if info:
            self.edits[0].setText(info[0]['vistrailName'])
            self.edits[1].setText('(Pipeline: %d, Module: %d)'
                                  % (info[0]['version'], info[0]['moduleId']))
            self.edits[2].setText(str(info[0]['reason']))
        else:
            for edit in self.edits:
                edit.setText('N/A')

################################################################################

class QCellManipulator(QtGui.QFrame):
    """
    QCellManipulator contains several dragable icons that allow users
    to move/copy or perform some operation from one cell to
    another. It also inclues a button for update the pipeline under
    the cell to be a new version on the pipeline. It is useful for the
    parameter exploration talks back to the builder
    
    """
    def __init__(self, parent=None):
        """ QPipelineInfo(parent: QWidget) -> None
        Create the 3 information lines
        
        """
        QtGui.QFrame.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        
        layout = QtGui.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setMargin(0)
        self.setLayout(layout)

        layout.addStretch()

        bLayout = QtGui.QHBoxLayout()
        layout.addLayout(bLayout)                

        bInfo = [(':/images/copy_cell.png',
                  'Drag to copy this cell to another place',
                  'copy', 'Copy'),
                 (':/images/move_cell.png',
                  'Drag to move this cell to another place',
                  'move', 'Move'),
                 (':/images/create_analogy.png',
                  'Drag to create an analogy between this cell and another one',
                  'create_analogy', 'Create\nAnalogy'),
                 (':/images/apply_analogy.png',
                  'Drag to apply the current analogy to this cell and put it '
                  'at another place', 'apply_analogy', 'Apply\nAnalogy')]
        
        self.buttons = []
        
        bLayout.addStretch()
        for b in bInfo:
            button = QCellDragLabel(QtGui.QPixmap(b[0]))
            button.setToolTip(b[1])
            button.setStatusTip(b[1])
            button.action = b[2]
            vLayout = QtGui.QVBoxLayout()
            vLayout.addWidget(button)
            label = QtGui.QLabel(b[3])
            label.setAlignment(QtCore.Qt.AlignCenter)
            vLayout.addWidget(label)
            bLayout.addLayout(vLayout)
            self.buttons.append(button)
            self.buttons.append(label)

        self.updateButton = QtGui.QToolButton()
        self.updateButton.setIconSize(QtCore.QSize(64, 64))
        self.updateButton.setIcon(QtGui.QIcon(QtGui.QPixmap(            
            ':/images/update.png')))
        self.updateButton.setAutoRaise(True)
        self.updateButton.setToolTip('Add this cell as a new version')
        self.updateButton.setStatusTip(self.updateButton.toolTip())
        self.updateButton.setText('Create Version')
        self.updateButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.connect(self.updateButton, QtCore.SIGNAL('clicked(bool)'),
                     self.updateVersion)
        self.buttons.append(self.updateButton)
        uLayout = QtGui.QHBoxLayout()
        uLayout.addStretch()
        uLayout.addWidget(self.updateButton)
        uLayout.addStretch()
        layout.addLayout(uLayout)
            
        bLayout.addStretch()

        layout.addStretch()

        self.innerRubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle,
                                                 self)
        
    def assignCell(self, sheet, row, col):
        """ assignCell(sheet: Sheet, row: int, col: int) -> None
        Assign a cell to the manipulator, so it knows where to drag
        and drop
        
        """
        self.cellInfo = (sheet, row, col)
        for b in self.buttons:
            if hasattr(b, 'updateCellInfo'):
                b.updateCellInfo(self.cellInfo)
            if sheet and sheet.getCell(row, col)!=None:
                widget = sheet.getCell(row, col)
                b.setVisible(type(widget)!=QCellPresenter or
                             widget.cellWidget!=None)
            else:
                b.setVisible(False)
        self.updateButton.setVisible(False)
        if sheet:
            info = sheet.getCellPipelineInfo(row, col)
            if info:
                self.updateButton.setVisible(len(info[0]['actions'])>0)

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Set to accept drops from the other cell info
        
        """
        mimeData = event.mimeData()
        if hasattr(mimeData, 'cellInfo'):
            if (mimeData.cellInfo==self.cellInfo or
                mimeData.cellInfo[0]==None or
                self.cellInfo[0]==None):
                event.ignore()
            else:
                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
                self.highlight()
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event):
        """ dragLeaveEvent(event: QDragLeaveEvent) -> None
        Unhighlight when the cursor leaves
        
        """
        self.highlight(False)
        
    def dropEvent(self, event):
        """ dragLeaveEvent(event: QDragLeaveEvent) -> None
        Unhighlight when the cursor leaves
        
        """
        self.highlight(False)
        mimeData = event.mimeData()
        action = mimeData.action
        cellInfo = mimeData.cellInfo
        manipulator = mimeData.manipulator
        if action in ['move', 'copy', 'create_analogy', 'apply_analogy']:
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
            
            if action=='move':
                self.cellInfo[0].swapCell(self.cellInfo[1], self.cellInfo[2],
                                          cellInfo[0], cellInfo[1], cellInfo[2])
                manipulator.assignCell(*self.cellInfo)
                self.assignCell(*cellInfo)
                
            if action=='copy':
                cellInfo[0].copyCell(cellInfo[1], cellInfo[2],
                                     self.cellInfo[0], self.cellInfo[1],
                                     self.cellInfo[2])
                
            if action=='create_analogy':
                p1Info = cellInfo[0].getPipelineInfo(cellInfo[1], cellInfo[2])
                p2Info = self.cellInfo[0].getPipelineInfo(self.cellInfo[1],
                                                          self.cellInfo[2])
                if p1Info!=None and p2Info!=None:
                    analogy = analogy_api.SpreadsheetAnalogy()
                    analogy.createAnalogy(p1Info, p2Info)

            if action=='apply_analogy':
                p1Info = cellInfo[0].getPipelineInfo(cellInfo[1], cellInfo[2])
                analogy = analogy_api.SpreadsheetAnalogy()
                newPipeline = analogy.applyAnalogy(p1Info)
                if newPipeline:
                    self.cellInfo[0].executePipelineToCell(newPipeline,
                                                           self.cellInfo[1],
                                                           self.cellInfo[2],
                                                           'Apply Analogy')

        else:
            event.ignore()
                    
        
    def highlight(self, on=True):
        """ highlight(on: bool) -> None
        Highlight the cell as if being selected
        
        """
        if on:
            self.innerRubberBand.setGeometry(self.rect())
            self.innerRubberBand.show()
        else:
            self.innerRubberBand.hide()

    def updateVersion(self):
        """ updateVersion() -> None        
        Use the performed action of this cell to add back a new
        version to the version tree
        
        """
        spreadsheetController = spreadsheet_controller.spreadsheetController
        builderWindow = spreadsheetController.getBuilderWindow()
        if builderWindow:
            info = self.cellInfo[0].getCellPipelineInfo(self.cellInfo[1],
                                                        self.cellInfo[2])
            if info:
                info = info[0]
                viewManager = builderWindow.viewManager
                view = viewManager.ensureVistrail(info['vistrailName'])
                if view:
                    controller = view.controller
                    controller.changeSelectedVersion(info['version'])
                    controller.performBulkActions(info['actions'])

################################################################################

class QCellDragLabel(QtGui.QLabel):
    """
    QCellDragLabel is a pixmap label allowing users to drag it to
    another cell manipulator
    
    """
    def __init__(self, pixmap, parent=None):
        """ QCellDragLabel(pixmap: QPixmap, parent: QWidget) -> QCellDragLabel
        Construct the pixmap label
        
        """
        QtGui.QLabel.__init__(self, parent)
        self.setMargin(0)
        self.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        self.setFixedSize(64, 64)
        self.cursorPixmap = pixmap.scaled(self.size())

        self.startPos = None
        self.cellInfo = (None, -1, -1)
        self.action = None
        
    def updateCellInfo(self, cellInfo):
        """ updateCellInfo(cellInfo: tuple) -> None
        Update cellInfo for mime data while dragging
        
        """
        self.cellInfo = cellInfo

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Store the start position for drag event
        
        """
        self.startPos = QtCore.QPoint(event.pos())
        QtGui.QLabel.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        """ mouseMoveEvent(event: QMouseEvent) -> None
        Prepare to drag
        
        """
        p = event.pos() - self.startPos
        if p.manhattanLength()>=QtGui.QApplication.startDragDistance():
            drag = QtGui.QDrag(self)
            data = QtCore.QMimeData()
            data.cellInfo = self.cellInfo
            data.action = self.action
            data.manipulator = self.parent()
            drag.setMimeData(data)
            drag.setHotSpot(self.cursorPixmap.rect().center())
            drag.setPixmap(self.cursorPixmap)            
            drag.start(QtCore.Qt.MoveAction)