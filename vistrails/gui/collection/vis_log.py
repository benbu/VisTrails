############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
""" This modules builds a widget to visualize workflow execution logs """
from PyQt4 import QtCore, QtGui
from core.vistrail.pipeline import Pipeline
from core.log.module_exec import ModuleExec
from core.log.group_exec import GroupExec
from core.log.loop_exec import LoopExec
from core.log.workflow_exec import WorkflowExec
from gui.pipeline_view import QPipelineView
from gui.theme import CurrentTheme
from gui.vistrails_palette import QVistrailsPaletteInterface
from gui.collection.workspace import QWorkspaceWindow
from core import system, debug
import core.db.io


##############################################################################


class QExecutionItem(QtGui.QTreeWidgetItem):
    """
    QExecutionListWidget is a widget containing a list of workflow executions.
    
    """
    def __init__(self, execution, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent)
        self.execution = execution
        execution.item = self

        # find parent workflow or group
        if parent is not None:
            while parent.parent() is not None and \
                  type(parent.execution) != GroupExec:
                parent = parent.parent()
            self.wf_execution = parent.execution
        else:
            self.wf_execution = execution


        if type(execution) == WorkflowExec:
            if execution.db_name:
                self.setText(0, execution.db_name)
            else:
                self.setText(0, 'Version #%s' % execution.parent_version )
            for item_exec in execution.item_execs:
                QExecutionItem(item_exec, self)
        if type(execution) == ModuleExec:
            self.setText(0, '%s' % execution.module_name)
            for loop_exec in execution.loop_execs:
                QExecutionItem(loop_exec, self)
        if type(execution) == GroupExec:
            self.setText(0, 'Group')
            for item_exec in execution.item_execs:
                QExecutionItem(item_exec, self)
        if type(execution) == LoopExec:
            self.setText(0, 'Loop #%s' % execution.db_iteration)
            for item_exec in execution.item_execs:
                QExecutionItem(item_exec, self)
        self.setText(1, '%s' % execution.ts_start)
        self.setText(2, '%s' % execution.ts_end)
        self.setText(3, '%s' % {'0':'No', '1':'Yes'}.get(
                               str(execution.completed), 'Error'))

class QExecutionListWidget(QtGui.QTreeWidget):
    """
    QExecutionListWidget is a widget containing a list of workflow executions.
    
    """
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setColumnCount(4)
        self.setHeaderLabels(['Type', 'Start', 'End', 'Completed'])
        self.setSortingEnabled(True)

    def set_log(self, log=None):
        self.clear()
        if log is not None:
            for execution in log.workflow_execs:
                self.addTopLevelItem(QExecutionItem(execution))
    
class QLegendBox(QtGui.QFrame):
    """
    QLegendBox is just a rectangular box with a solid color
    
    """
    def __init__(self, brush, size, parent=None, f=QtCore.Qt.WindowFlags()):
        """ QLegendBox(color: QBrush, size: (int,int), parent: QWidget,
                      f: WindowFlags) -> QLegendBox
        Initialize the widget with a color and fixed size
        
        """
        QtGui.QFrame.__init__(self, parent, f)
        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        self.setAttribute(QtCore.Qt.WA_PaintOnScreen)
        self.setAutoFillBackground(True)
        palette = QtGui.QPalette(self.palette())
        palette.setBrush(QtGui.QPalette.Window, brush)
        self.setPalette(palette)
        self.setFixedSize(*size)
        if system.systemType in ['Darwin']:
            #the mac's nice looking messes up with the colors
            if QtCore.QT_VERSION < 0x40500:
                self.setAttribute(QtCore.Qt.WA_MacMetalStyle, False)
            else:
                self.setAttribute(QtCore.Qt.WA_MacBrushedMetal, False)
        

class QLegendWidget(QtGui.QWidget):
    """
    QLegendWindow contains a list of QLegendBox and its description
    
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setMargin(10)
        self.gridLayout.setSpacing(10)
        self.setFont(CurrentTheme.VISUAL_DIFF_LEGEND_FONT)
        
        data = [[0, 0, "Successful",      CurrentTheme.SUCCESS_MODULE_BRUSH],
                [0, 1, "Error",             CurrentTheme.ERROR_MODULE_BRUSH],
                [1, 0, "Not executed", CurrentTheme.PERSISTENT_MODULE_BRUSH],
                [1, 1, "Cached",     CurrentTheme.NOT_EXECUTED_MODULE_BRUSH]]

        for x, y, text, brush in data:         
            self.gridLayout.addWidget(
                QLegendBox(brush, CurrentTheme.VISUAL_DIFF_LEGEND_SIZE, self),
                x*2, y*2)
            self.gridLayout.addWidget(QtGui.QLabel(text, self), x*2, y*2+1)

class QLogDetails(QtGui.QWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.execution = None
        self.parentExecution = None
        self.set_title("Log Details")
        self.legend = QLegendWidget()
        self.executionList = QExecutionListWidget()
        self.executionList.setExpandsOnDoubleClick(False)
        self.isDoubling = False
        layout = QtGui.QVBoxLayout()

        self.backButton = QtGui.QPushButton('Go back')
        self.backButton.setToolTip("Go back to parent workflow")
        layout.addWidget(self.backButton)
        self.backButton.hide()

        layout.addWidget(self.legend)
        layout.addWidget(self.executionList)
        self.detailsWidget = QtGui.QTextEdit()
        layout.addWidget(self.detailsWidget)
        self.setLayout(layout)
#        self.connect(self.executionList, 
#                     QtCore.SIGNAL("itemSelectionChanged()"),
#                     self.execution_changed)
        self.connect(self.backButton,
                     QtCore.SIGNAL('clicked()'),
                     self.goBack)
        self.connect(self.executionList, QtCore.SIGNAL(
         "itemClicked(QTreeWidgetItem *, int)"),
         self.singleClick)
        self.connect(self.executionList, QtCore.SIGNAL(
         "itemDoubleClicked(QTreeWidgetItem *, int)"),
         self.doubleClick)

    def execution_changed(self):
        item = self.executionList.selectedItems()[0]
        if self.execution != item.execution:
            self.execution = item.execution
            from gui.vistrails_window import _app
            _app.notify("execution_changed", item.wf_execution, item.execution)
        
    def set_controller(self, controller):
        print '@@@@ QLogDetails calling set_controller'
        # self.log = controller.vistrail.get_log()
        self.log = controller.read_log()
        print "read log", self.log
        # set workflow tag names
        for execution in self.log.workflow_execs:
            wf_id = execution.parent_version
            tagMap = controller.vistrail.get_tagMap()
            if execution.parent_version in tagMap:
                execution.db_name = tagMap[execution.parent_version]
        if self.log is not None:
            print "  @@ len(workflow_execs):", len(self.log.workflow_execs)
        self.executionList.set_log(self.log)

    def set_execution(self, wf_execution, execution):
        print "setting execution details for", execution
        if not execution:
            return
        self.execution = execution
        self.parentExecution = wf_execution
        if hasattr(execution, 'item') and \
           not execution.item == self.executionList.currentItem():
            self.executionList.setCurrentItem(execution.item)
        text = ''
        text += '%s\n' % execution.item.text(0)
        text += 'Start: %s\n' % execution.ts_start
        text += 'End: %s\n' % execution.ts_end
        if hasattr(execution, 'user'):
            text += 'User: %s\n' % execution.user
        if hasattr(execution, 'cached'):
            text += 'Cached: %s\n' % ("Yes" if execution.cached else 'No')
        text += 'Completed: %s\n' % {'0':'No', '1':'Yes'}.get(
                                    str(execution.completed), 'Error')
        if hasattr(execution, 'error') and execution.error:
            text += 'Error: %s\n' % execution.error
        annotations = execution.db_annotations \
                      if hasattr(execution, 'db_annotations') else []
        if len(annotations):
            text += '\n\nAnnotations:'
            for annotation in annotations:
                text += "\n  %s: %s" % (annotation.key, annotation.value)
        self.detailsWidget.setText(text)
        
    def singleClick(self, item, col):
        print "singleClick"
        if self.isDoubling:
            self.isDoubling = False
            return
        if type(item.wf_execution) == GroupExec:
            self.backButton.show()
        else:
            self.backButton.hide()
        from gui.vistrails_window import _app
        _app.notify("execution_changed", item.wf_execution, item.execution)

    def doubleClick(self, item, col):
        print "doubleClick"
        # only difference here is that we should show contents of GroupExecs 
        self.isDoubling = True
        if type(item.wf_execution) == GroupExec:
            self.backButton.show()
        else:
            self.backButton.hide()
        from gui.vistrails_window import _app
        if type(item.execution) == GroupExec:
            # use itself as the workflow
            _app.notify("execution_changed", item.execution, item.execution)
        else:
            _app.notify("execution_changed", item.wf_execution, item.execution)

    def goBack(self):
        print "goBack"
        if type(self.parentExecution) != GroupExec:
            self.backButton.hide()
        from gui.vistrails_window import _app
        _app.notify("execution_changed",
                    self.parentExecution.item.wf_execution,
                    self.parentExecution)

class QLogView(QPipelineView):
    def __init__(self, parent=None):
        QPipelineView.__init__(self, parent)
        self.set_title("Provenance")
        self.log = None
        self.execution = None
        self.parentExecution = None
        # self.exec_to_wf_map = {}
        # self.workflow_execs = []
        # Hook shape selecting functions
        self.connect(self.scene(), QtCore.SIGNAL("moduleSelected"),
                     self.moduleSelected)

    def set_default_layout(self):
        self.layout = \
            {QtCore.Qt.LeftDockWidgetArea: QWorkspaceWindow,
             QtCore.Qt.RightDockWidgetArea: QLogDetails,
             }
            
    def set_action_links(self):
        self.action_links = { }

    def set_controller(self, controller):
        QPipelineView.set_controller(self, controller)
        print "@@@ set_controller called", id(self.controller), len(self.controller.vistrail.actions)

    def set_to_current(self):
        # change to normal controller hacks
        print "AAAAA doing set_to_current"
        if self.controller.current_pipeline_view is not None:
            self.disconnect(self.controller,
                            QtCore.SIGNAL('versionWasChanged'),
                            self.controller.current_pipeline_view.parent().version_changed)
        self.controller.current_pipeline_view = self.scene()
        self.set_log(self.controller.log)
        self.connect(self.controller,
                     QtCore.SIGNAL('versionWasChanged'),
                     self.version_changed)

    def version_changed(self):
        pass

    def moduleSelected(self, id, selectedItems):
        """ moduleSelected(id: int, selectedItems: [QGraphicsItem]) -> None
        """
        from gui.vistrails_window import _app
        if len(selectedItems)!=1 or id==-1:
            if self.execution != self.parentExecution:
                _app.notify("execution_changed", self.parentExecution, self.parentExecution)
#            self.moduleUnselected()
            return

        item = selectedItems[0]
        if hasattr(item,'execution') and item.execution:
            if self.execution != item.execution:
                item = self.scene().selectedItems()[0]
                _app.notify("execution_changed", self.parentExecution, item.execution)
        else:
            if self.execution != self.parentExecution:
                _app.notify("execution_changed", self.parentExecution, self.parentExecution)

    def set_log(self, log):
        self.log = log
        # self.exec_to_wf_map = {}
        # for workflow_exec in self.log.workflow_execs:
        #     next_level = workflow_exec.item_execs
        #     while len(next_level) > 0:
        #         new_next_level = []
        #         for item_exec in next_level:
        #             self.exec_to_wf_map[item_exec.id] = workflow_exec.id
        #             if item_exec.vtType == ModuleExec.vtType:
        #                 new_next_level += item_exec.loop_execs
        #             else:
        #                 new_next_level += item_exec.item_execs
        #         next_level = new_next_level

    def set_exec_by_id(self, exec_id):
        workflow_execs = [e for e in self.log.workflow_execs 
                          if e.id == int(exec_id)]
        if len(workflow_execs):
            self.set_execution(workflow_execs[0], workflow_execs[0])
            return True
        return False

    def set_exec_by_date(self, exec_date):
        workflow_execs = [e for e in self.log.workflow_execs
                          if str(e.ts_start) == str(exec_date)]
        if len(workflow_execs):
            self.set_execution(workflow_execs[0], workflow_execs[0])
            return True
        return False

    def get_execution_pipeline(self, execution):
        """ Recursively finds pipeline through layers of groupExecs """
        if type(execution) == WorkflowExec:
            version = execution.parent_version
            return self.controller.vistrail.getPipeline(version)
        if type(execution) == GroupExec:
            parent = execution.item.wf_execution
            parent_pipeline = self.get_execution_pipeline(parent)
            return parent_pipeline.db_get_module_by_id(
                                   execution.db_module_id).pipeline

    def set_execution(self, wf_execution, execution):
        print "set_execution:", wf_execution, execution
        self.execution = execution
        if self.parentExecution != wf_execution:
            self.parentExecution = wf_execution
            self.pipeline = self.get_execution_pipeline(wf_execution)
            self.update_pipeline()
        self.update_selection()

        # if idx < len(self.workflow_execs) and idx >= 0:
        #     self.execution = self.workflow_execs[idx]
        # else:
        #     self.execution = None

        # self.currentItem = self.workflow_execs[idx]
        # self.execution = item.execution
        # self.workflowExecution = item
        # while self.workflowExecution.parent():
        #     self.workflowExecution = self.workflowExecution.parent()
        # self.workflowExecution = self.workflowExecution.execution
        # self.parentExecution = item
        # while self.parentExecution.execution.__class__ not in \
        #         [WorkflowExec, LoopExec, GroupExec]:
        #     self.parentExecution = self.parentExecution.parent()
        # self.parentExecution = self.parentExecution.execution
        # self.showExecution()

    def update_pipeline(self):
        print "ACTIONS!"
        print "#### controller", id(self.controller)
        scene = self.scene()
        scene.clearItems()
        self.pipeline.validate(False)
        
        module_execs = dict([(e.module_id, e) 
                             for e in self.parentExecution.item_execs])
        # controller = DummyController(self.pipeline)
        scene.controller = self.controller
        self.moduleItems = {}
        for m_id in self.pipeline.modules:
            module = self.pipeline.modules[m_id]
            brush = CurrentTheme.PERSISTENT_MODULE_BRUSH
            if m_id in module_execs:
                e = module_execs[m_id]
                if e.completed:
                    if e.error:
                        brush = CurrentTheme.ERROR_MODULE_BRUSH
                    elif e.cached:
                        brush = CurrentTheme.NOT_EXECUTED_MODULE_BRUSH
                    else:
                        brush = CurrentTheme.SUCCESS_MODULE_BRUSH
                else:
                    brush = CurrentTheme.ERROR_MODULE_BRUSH
            module.is_valid = True
            item = scene.addModule(module, brush)
            item.controller = self.controller
            self.moduleItems[m_id] = item
            if m_id in module_execs:
                e = module_execs[m_id]
                item.execution = e
                e.module = item
            else:
                item.execution = None
        connectionItems = []
        for c in self.pipeline.connections.values():
            connectionItems.append(scene.addConnection(c))

        # Color Code connections
        for c in connectionItems:
            pen = QtGui.QPen(CurrentTheme.CONNECTION_PEN)
            pen.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 128+64)))
            c.connectionPen = pen

        scene.updateSceneBoundingRect()
        scene.fitToView(self, True)

    def update_selection(self):
        for item in self.scene().selectedItems():
            item.setSelected(False)
        if type(self.execution) == ModuleExec:
            if hasattr(self.execution, 'item'):
                self.execution.item.setSelected(True)
            if hasattr(self.execution, 'module'):
                self.execution.module.setSelected(True)
        if type(self.execution) == GroupExec and self.execution == self.parentExecution:
            # viewing group as a module
            self.execution.item.setSelected(True)
            self.execution.module.setSelected(True)
