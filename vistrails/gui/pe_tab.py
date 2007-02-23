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
""" The file describes the parameter exploration tab for VisTrails

QParameterExplorationTab
"""

from PyQt4 import QtCore, QtGui
from core.inspector import PipelineInspector
from gui.common_widgets import QDockContainer, QToolWindowInterface
from gui.pe_table import QParameterExplorationTable
from gui.virtual_cell import QVirtualCellWindow
from gui.param_view import QParameterView
from gui.pe_pipeline import QMarkPipelineView

################################################################################

class QParameterExplorationTab(QDockContainer, QToolWindowInterface):
    """
    QParameterExplorationTab is a tab containing different widgets
    related to parameter exploration
    
    """
    def __init__(self, parent=None):
        """ QParameterExplorationTab(parent: QWidget)
                                    -> QParameterExplorationTab
        Make it a main window with dockable area and a
        QParameterExplorationTable
        
        """
        QDockContainer.__init__(self, parent)
        self.setWindowTitle('Parameter Exploration')
        self.toolWindow().setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.toolWindow().hide()

        self.peTable = QParameterExplorationTable()
        self.setCentralWidget(self.peTable)
        
        self.paramView = QParameterView(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.paramView.toolWindow())
        
        self.markPipelineView = QMarkPipelineView(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.markPipelineView.toolWindow())
        
        self.virtualCell = QVirtualCellWindow(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.virtualCell.toolWindow())
        
        self.controller = None
        self.currentVersion = -1

    def setController(self, controller):
        """ setController(controller: VistrailController) -> None
        Assign a controller to the parameter exploration tab
        
        """
        self.controller = controller

    def showEvent(self, event):
        """ showEvent(event: QShowEvent) -> None
        Update the tab when it is shown
        
        """
        if self.currentVersion!=self.controller.currentVersion:
            self.currentVersion = self.controller.currentVersion
            if self.currentVersion!=-1:
                # First create an inspector for the pipeline
                inspector = PipelineInspector()

                # Now inspect the spreadsheet cells for the virtual
                # cell configuration
                inspector.inspectSpreadsheetCells(
                    self.controller.currentPipeline)
                cells = [self.controller.currentPipeline.modules[mId].name
                         for mId in inspector.spreadsheetCells]
                self.virtualCell.config.configVirtualCells(cells)

                # Now we need to inspect the parameter list
                self.paramView.treeWidget.updateFromPipeline(
                    self.controller.currentPipeline)