# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'valhalla/resources/ui/dlg_plugin_settings.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PluginSettingsDialog(object):
    def setupUi(self, PluginSettingsDialog):
        PluginSettingsDialog.setObjectName("PluginSettingsDialog")
        PluginSettingsDialog.setWindowModality(QtCore.Qt.WindowModal)
        PluginSettingsDialog.resize(693, 525)
        PluginSettingsDialog.setWindowTitle("Valhalla - Settings")
        self.gridLayout = QtWidgets.QGridLayout(PluginSettingsDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.menu_widget = QtWidgets.QListWidget(PluginSettingsDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.menu_widget.sizePolicy().hasHeightForWidth())
        self.menu_widget.setSizePolicy(sizePolicy)
        self.menu_widget.setMinimumSize(QtCore.QSize(100, 200))
        self.menu_widget.setMaximumSize(QtCore.QSize(153, 16777215))
        self.menu_widget.setStyleSheet("QListWidget{\n"
"    background-color: rgb(69, 69, 69, 220);\n"
"    outline: 0;\n"
"}\n"
"QListWidget::item {\n"
"    color: white;\n"
"    padding: 3px;\n"
"}\n"
"QListWidget::item::selected {\n"
"    color: black;\n"
"    background-color:palette(Window);\n"
"    padding-right: 0px;\n"
"}")
        self.menu_widget.setFrameShape(QtWidgets.QFrame.Box)
        self.menu_widget.setLineWidth(0)
        self.menu_widget.setIconSize(QtCore.QSize(32, 32))
        self.menu_widget.setUniformItemSizes(False)
        self.menu_widget.setObjectName("menu_widget")
        item = QtWidgets.QListWidgetItem()
        self.menu_widget.addItem(item)
        self.gridLayout.addWidget(self.menu_widget, 0, 0, 1, 1)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setObjectName("main_layout")
        self.ui_stacked_panels = QtWidgets.QStackedWidget(PluginSettingsDialog)
        self.ui_stacked_panels.setObjectName("ui_stacked_panels")
        self.general_page = QtWidgets.QWidget()
        self.general_page.setObjectName("general_page")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.general_page)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ui_deps_group = QtWidgets.QGroupBox(self.general_page)
        self.ui_deps_group.setObjectName("ui_deps_group")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.ui_deps_group)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.ui_deps_table = QtWidgets.QTableWidget(self.ui_deps_group)
        self.ui_deps_table.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ui_deps_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ui_deps_table.setProperty("showDropIndicator", False)
        self.ui_deps_table.setDragDropOverwriteMode(False)
        self.ui_deps_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.ui_deps_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui_deps_table.setShowGrid(False)
        self.ui_deps_table.setObjectName("ui_deps_table")
        self.ui_deps_table.setColumnCount(4)
        self.ui_deps_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.ui_deps_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.ui_deps_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.ui_deps_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.ui_deps_table.setHorizontalHeaderItem(3, item)
        self.verticalLayout_3.addWidget(self.ui_deps_table)
        self.verticalLayout.addWidget(self.ui_deps_group)
        self.ui_url_group = QtWidgets.QGroupBox(self.general_page)
        self.ui_url_group.setObjectName("ui_url_group")
        self.formLayout_2 = QtWidgets.QFormLayout(self.ui_url_group)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label = QtWidgets.QLabel(self.ui_url_group)
        self.label.setObjectName("label")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.ui_debug = QtWidgets.QCheckBox(self.ui_url_group)
        self.ui_debug.setText("")
        self.ui_debug.setObjectName("ui_debug")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.ui_debug)
        self.verticalLayout.addWidget(self.ui_url_group)
        self.ui_stacked_panels.addWidget(self.general_page)
        self.main_layout.addWidget(self.ui_stacked_panels)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.main_layout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_9 = QtWidgets.QLabel(PluginSettingsDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout.addWidget(self.label_9)
        self.toolButton_2 = QtWidgets.QToolButton(PluginSettingsDialog)
        icon = QtGui.QIcon.fromTheme(":images/themes/default/mActionHelpContents.svg")
        self.toolButton_2.setIcon(icon)
        self.toolButton_2.setIconSize(QtCore.QSize(32, 32))
        self.toolButton_2.setObjectName("toolButton_2")
        self.horizontalLayout.addWidget(self.toolButton_2)
        self.main_layout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.main_layout, 0, 1, 1, 1)

        self.retranslateUi(PluginSettingsDialog)
        self.menu_widget.setCurrentRow(-1)
        self.ui_stacked_panels.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(PluginSettingsDialog)

    def retranslateUi(self, PluginSettingsDialog):
        _translate = QtCore.QCoreApplication.translate
        __sortingEnabled = self.menu_widget.isSortingEnabled()
        self.menu_widget.setSortingEnabled(False)
        item = self.menu_widget.item(0)
        item.setText(_translate("PluginSettingsDialog", "General"))
        self.menu_widget.setSortingEnabled(__sortingEnabled)
        self.ui_deps_group.setTitle(_translate("PluginSettingsDialog", "Dependencies"))
        item = self.ui_deps_table.horizontalHeaderItem(0)
        item.setText(_translate("PluginSettingsDialog", "Package"))
        item = self.ui_deps_table.horizontalHeaderItem(1)
        item.setText(_translate("PluginSettingsDialog", "Installed"))
        item = self.ui_deps_table.horizontalHeaderItem(2)
        item.setText(_translate("PluginSettingsDialog", "Available"))
        self.ui_url_group.setTitle(_translate("PluginSettingsDialog", "Misc"))
        self.label.setText(_translate("PluginSettingsDialog", "Debug"))
        self.label_9.setText(_translate("PluginSettingsDialog", "With :heart: from GIS-OPS UG"))
        self.toolButton_2.setText(_translate("PluginSettingsDialog", "Help"))
