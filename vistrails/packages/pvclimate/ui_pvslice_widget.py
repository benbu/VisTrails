# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pvslice_widget.ui'
#
# Created: Tue Dec 18 11:06:51 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PVSliceWidget(object):
    def setupUi(self, PVSliceWidget):
        PVSliceWidget.setObjectName(_fromUtf8("PVSliceWidget"))
        PVSliceWidget.resize(577, 366)
        self.gridLayout = QtGui.QGridLayout(PVSliceWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_8 = QtGui.QVBoxLayout()
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.groupBox = QtGui.QGroupBox(PVSliceWidget)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.sliceNormalXLineEdit = QtGui.QLineEdit(self.groupBox)
        self.sliceNormalXLineEdit.setObjectName(_fromUtf8("sliceNormalXLineEdit"))
        self.horizontalLayout_2.addWidget(self.sliceNormalXLineEdit)
        self.sliceNormalYLineEdit = QtGui.QLineEdit(self.groupBox)
        self.sliceNormalYLineEdit.setObjectName(_fromUtf8("sliceNormalYLineEdit"))
        self.horizontalLayout_2.addWidget(self.sliceNormalYLineEdit)
        self.sliceNormalZLineEdit = QtGui.QLineEdit(self.groupBox)
        self.sliceNormalZLineEdit.setObjectName(_fromUtf8("sliceNormalZLineEdit"))
        self.horizontalLayout_2.addWidget(self.sliceNormalZLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.sliceOriginXLineEdit = QtGui.QLineEdit(self.groupBox)
        self.sliceOriginXLineEdit.setObjectName(_fromUtf8("sliceOriginXLineEdit"))
        self.horizontalLayout.addWidget(self.sliceOriginXLineEdit)
        self.sliceOriginYLineEdit = QtGui.QLineEdit(self.groupBox)
        self.sliceOriginYLineEdit.setObjectName(_fromUtf8("sliceOriginYLineEdit"))
        self.horizontalLayout.addWidget(self.sliceOriginYLineEdit)
        self.sliceOriginZLineEdit = QtGui.QLineEdit(self.groupBox)
        self.sliceOriginZLineEdit.setObjectName(_fromUtf8("sliceOriginZLineEdit"))
        self.horizontalLayout.addWidget(self.sliceOriginZLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        self.verticalLayout_7.addLayout(self.horizontalLayout_4)
        self.verticalLayout_8.addWidget(self.groupBox)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.groupBox_2 = QtGui.QGroupBox(PVSliceWidget)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.verticalLayout_6 = QtGui.QVBoxLayout()
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.verticalLayout_5.addLayout(self.verticalLayout_6)
        self.sliceOffsetListWidget = QtGui.QListWidget(self.groupBox_2)
        self.sliceOffsetListWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.sliceOffsetListWidget.setObjectName(_fromUtf8("sliceOffsetListWidget"))
        self.verticalLayout_5.addWidget(self.sliceOffsetListWidget)
        self.horizontalLayout_3.addWidget(self.groupBox_2)
        self.inputGroupBox = QtGui.QGroupBox(PVSliceWidget)
        self.inputGroupBox.setObjectName(_fromUtf8("inputGroupBox"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.inputGroupBox)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_3 = QtGui.QLabel(self.inputGroupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_3.addWidget(self.label_3)
        self.csvLineEdit = QtGui.QLineEdit(self.inputGroupBox)
        self.csvLineEdit.setObjectName(_fromUtf8("csvLineEdit"))
        self.verticalLayout_3.addWidget(self.csvLineEdit)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.horizontalLayout_3.addWidget(self.inputGroupBox)
        self.verticalLayout_8.addLayout(self.horizontalLayout_3)
        self.gridLayout.addLayout(self.verticalLayout_8, 0, 0, 3, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 152, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 0, 1, 1, 1)
        self.applyButton = QtGui.QPushButton(PVSliceWidget)
        self.applyButton.setObjectName(_fromUtf8("applyButton"))
        self.gridLayout.addWidget(self.applyButton, 1, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 152, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 2, 1, 1, 1)

        self.retranslateUi(PVSliceWidget)
        QtCore.QMetaObject.connectSlotsByName(PVSliceWidget)

    def retranslateUi(self, PVSliceWidget):
        PVSliceWidget.setWindowTitle(QtGui.QApplication.translate("PVSliceWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("PVSliceWidget", "Slice Base Parameters", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("PVSliceWidget", "Normal", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("PVSliceWidget", "Origin", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("PVSliceWidget", "Slice Offset Values", None, QtGui.QApplication.UnicodeUTF8))
        self.inputGroupBox.setTitle(QtGui.QApplication.translate("PVSliceWidget", "Input", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("PVSliceWidget", "Comma Separated Values", None, QtGui.QApplication.UnicodeUTF8))
        self.applyButton.setText(QtGui.QApplication.translate("PVSliceWidget", "Apply", None, QtGui.QApplication.UnicodeUTF8))

