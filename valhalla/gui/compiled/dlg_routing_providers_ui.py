# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'valhalla/resources/ui/dlg_routing_providers.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_RoutingProviders(object):
    def setupUi(self, RoutingProviders):
        RoutingProviders.setObjectName("RoutingProviders")
        RoutingProviders.resize(414, 88)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(RoutingProviders.sizePolicy().hasHeightForWidth())
        RoutingProviders.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(RoutingProviders)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(RoutingProviders)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 2, 1, 1)
        self.provider_add = QtWidgets.QPushButton(RoutingProviders)
        self.provider_add.setObjectName("provider_add")
        self.gridLayout.addWidget(self.provider_add, 1, 0, 1, 1)
        self.provider_remove = QtWidgets.QPushButton(RoutingProviders)
        self.provider_remove.setObjectName("provider_remove")
        self.gridLayout.addWidget(self.provider_remove, 1, 1, 1, 1)
        self.provider_layout = QtWidgets.QVBoxLayout()
        self.provider_layout.setObjectName("provider_layout")
        self.gridLayout.addLayout(self.provider_layout, 0, 0, 1, 3)

        self.retranslateUi(RoutingProviders)
        QtCore.QMetaObject.connectSlotsByName(RoutingProviders)

    def retranslateUi(self, RoutingProviders):
        _translate = QtCore.QCoreApplication.translate
        RoutingProviders.setWindowTitle(_translate("RoutingProviders", "Provider Settings"))
        self.provider_add.setText(_translate("RoutingProviders", "Add"))
        self.provider_remove.setText(_translate("RoutingProviders", "Remove"))
