from PyQt4 import QtCore
from core.modules.module_registry import get_module_registry
from packages.vtk.vtkcell import QVTKWidget
from packages.spreadsheet.basic_widgets import SpreadsheetCell, CellLocation
from packages.spreadsheet.spreadsheet_cell import QCellWidget

import paraview.simple as pvsp
import paraview.pvfilters
import vtk

# Needed for configuration
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui.modules.module_configure import StandardModuleConfigurationWidget

# Needed for port related stuff
from core.vistrail.port import PortEndPoint
import core.modules.basic_modules as basic_modules

# Needed to parse csv string into a list
import csv
import StringIO

# PVRepresentation
from pvrepresentationbase import *

from pvvariable import *

class PVIsoSurfaceCell(SpreadsheetCell):
    def __init__(self):
        SpreadsheetCell.__init__(self)
        self.cellWidget = None
        self.location = None
        self.representation = None

    def compute(self):
        """ compute() -> None
        Dispatch the vtkRenderer to the actual rendering widget
        """
        # Fetch input variable
        variables = self.forceGetInputListFromPort('variable')        

        # Fetch slice offset from input port
        if self.hasInputFromPort("location"):
            self.location = self.getInputFromPort("location")
        else:
            pass
        
        # Get representation from the input
        if self.hasInputFromPort("representation"):
            self.representation = self.getInputFromPort("representation")
        
        if self.representation is None:
          return;

        self.cellWidget = self.displayAndWait(QPVIsoSurfaceWidget, (self.location, variables, self.representation))

    def persistParameterList( self, parameter_list, **args ):
        print "Getting Something"

    def setSliceOffset(self, value):
        self.sliceOffset = value

    def getSliceOffset(self):
        return self.sliceOffset

class QPVIsoSurfaceWidget(QVTKWidget):

    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QVTKWidget.__init__(self, parent, f)
        self.view = None

    def updateContents(self, inputPorts):
        if self.view==None:
            self.view = pvsp.CreateRenderView()
            renWin = self.view.GetRenderWindow()
            self.SetRenderWindow(renWin)
            iren = renWin.GetInteractor()
            print type(iren)
            iren.SetNonInteractiveRenderDelay(0)
            iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

        del self.view.Representations[:]

        # Fetch variables from the input port
        (location, variables, representation) = inputPorts
        for var in variables:
            reader = var.get_reader()
            representation.setReader(reader)
            representation.setVariables(variables)
            representation.setView(self.view)            
            representation.execute()            
            
        # Set view specific properties
        self.view.CenterAxesVisibility = 0
        self.view.Background = [0.5, 0.5, 0.5]

        self.view.ResetCamera()
        self.view.StillRender()

        QCellWidget.updateContents(self, inputPorts)

    def saveToPNG(self, filename):
        """ saveToPNG(filename: str) -> filename or vtkUnsignedCharArray

        Save the current widget contents to an image file. If
        str==None, then it returns the vtkUnsignedCharArray containing
        the PNG image. Otherwise, the filename is returned.

        """
        image = self.view.CaptureWindow(1)
        image.UnRegister(None)

        writer = vtk.vtkPNGWriter()
        writer.SetInput(image)
        if filename!=None:
            writer.SetFileName(filename)
        else:
            writer.WriteToMemoryOn()
        writer.Write()
        if filename:
            return filename
        else:
            return writer.GetResult()

    def deleteLater(self):
        QCellWidget.deleteLater(self)


def registerSelf():
    registry = get_module_registry()
    # For now, we don't have configuration widget
    #registry.add_module(PVIsoSurfaceCell, configureWidgetType=PVClimateCellConfigurationWidget)
    registry.add_module(PVIsoSurfaceCell)
    registry.add_input_port(PVIsoSurfaceCell, "Location", CellLocation)
    registry.add_input_port(PVIsoSurfaceCell, "variable", PVVariable)    
    registry.add_input_port(PVIsoSurfaceCell, "representation", PVRepresentationBase)
    registry.add_output_port(PVIsoSurfaceCell, "self", PVIsoSurfaceCell)
